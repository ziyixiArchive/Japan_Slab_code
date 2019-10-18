"""
Get windows in TaoKai's style, and calculate snr, delta t and cc.
"""
from obspy.signal.cross_correlation import correlate, xcorr_max
from obspy.geodetics.base import gps2dist_azimuth, locations2degrees
from obspy.taup import TauPyModel
import numpy as np
import pyasdf

model = TauPyModel(model='ak135')


class Window(object):
    """
    The window object is adapted form pyflex.Window, but will have different parameters.
    """

    def __init__(self, left, right, min_period, channel_id):
        self.left = left
        self.right = right
        self.min_period = min_period
        self.channel_id = channel_id

        # values to be updated
        self.similarity = None
        self.max_cc = None
        self.deltat = None
        self.snr = None

    def update_cc_related(self, obs, syn):
        """
        Use the trace info to update similarity, max_cc and deltat. Always use data as the reference.
        """
        # firstly, we have tp make obs and syn comparable, assume their deltas are the same.
        obs = obs.copy()
        syn = syn.copy()
        # after having processed, the starttime should be the same
        syn.stats.starttime = obs.stats.starttime

        win_obs = obs.slice(self.left, self.right)
        win_syn = syn.slice(self.left, self.right)

        cc = correlate(win_obs, win_syn, None, demean=True)
        shift, value = xcorr_max(cc, abs_max=False)

        self.similarity = cc[len(cc)//2]
        self.deltat = shift*win_obs.stats.delta
        self.max_cc = value

    def update_snr(self, snr):
        self.snr = snr


def get_travel_times(stla, stlo, evla, evlo, evdp):
    property_times = {
        "p": None,  # either p or P
        "s": None,
        "surf_start": None,
        "surf_end": None,
        "ss": None,
        "pp": None,
        "sp": None,
        "scs": None,
        "gcarc": None,
        "azimuth": None,
        "stla": stla,
        "stlo": stlo,
    }

    # sphere gcircle distance, since taup use sphere
    gcarc = locations2degrees(stla, stlo, evla, evlo)
    property_times["gcarc"] = gcarc

    # calculate first arrivals
    arrivals = model.get_travel_times(source_depth_in_km=evdp,
                                      distance_in_degree=gcarc,
                                      phase_list=["p", "P", "s", "S", "3.5kmps", "4.0kmps", "sS", "SS", "pP", "PP", "sP", "SP", "ScS"])

    for item in arrivals:
        # find p
        if(property_times["p"] == None):
            if(item.name == "p" or item.name == "P"):
                property_times["p"] = item.time

        # find s
        if(property_times["s"] == None):
            if(item.name == "s" or item.name == "S"):
                property_times["s"] = item.time

        # find surface wave
        if(property_times["surf_start"] == None):
            if(item.name == "4.6kmps"):
                property_times["surf_start"] = item.time
        if(property_times["surf_end"] == None):
            if(item.name == "3.3kmps"):
                property_times["surf_end"] = item.time

        # find pp,ss,sp
        if(property_times["pp"] == None):
            if(item.name == "pP" or item.name == "PP"):
                property_times["pp"] = item.time
        if(property_times["ss"] == None):
            if(item.name == "sS" or item.name == "SS"):
                property_times["ss"] = item.time
        if(property_times["sp"] == None):
            if(item.name == "sP" or item.name == "SP"):
                property_times["sp"] = item.time

        # find scs
        if(property_times["scs"] == None):
            if(item.name == "ScS"):
                property_times["scs"] = item.time

    # get azimuth, from the source to the stations
    _, property_times["azimuth"], _ = gps2dist_azimuth(evla, evlo, stla, stlo)

    # always could success
    return property_times


def get_windows_for_single_trace(travel_times, component, obs, syn, min_period):
    """
    Find body wave windows and combine overlap windows. (don't combine surface wave windows)
    """
    body_windows = []
    surf_windows = []
    result = []

    # get the max starttime and the min endtime
    opt_starttime = max(obs.stats.starttime, syn.stats.starttime)
    opt_endtime = min(obs.stats.endtime, syn.stats.endtime)

    search_list_body = ["ss", "s"]
    if(component == "z"):
        search_list_body += ["p", "pp", "sp"]
    elif(component == "r"):
        search_list_body += ["p", "pp", "sp"]
    elif(component == "t"):
        search_list_body += ["scs"]

    # for all the phases in the search list, if its time is not None, add its window in result
    for phase in search_list_body:
        phase_time = travel_times[phase]+obs.stats.starttime
        # left, right, min_period, channel_id
        left = phase_time-20
        if(left < opt_starttime):
            left = opt_starttime
        right = phase_time+50
        if(right > opt_endtime):
            right = opt_endtime
        channel_id = obs.id
        result.append(Window(left, right, min_period, channel_id))

    # sort the windows according to their first arrival(get bigger)
    result = sorted(result, key=lambda item_window: item_window.left)

    # combine the overlap windows
    merge_ids = []
    current_merge_id = 0
    for index in range(len(result)):
        if(index == 0):
            merge_ids.append(current_merge_id)
        else:
            if(result[index].left < result[index-1].right):
                # overlap with the left window
                merge_ids.append(current_merge_id)
            else:
                current_merge_id += 1
                merge_ids.append(current_merge_id)
    # merge all the windows with the same merge id
    merge_ids = np.array(merge_ids)
    result = np.array(result)
    updated_result = []
    for merge_id in range(current_merge_id+1):
        win_selected = result[np.where(merge_ids == merge_id)]
        min_period = win_selected[0].min_period
        channel_id = win_selected[0].channel_id
        all_left = [item.left for item in win_selected]
        all_right = [item.right for item in win_selected]
        updated_result.append(
            Window(min(all_left), max(all_right), min_period, channel_id))

    return updated_result


def main(obs_path, syn_path):
    # init
    with pyasdf.ASDFDataSet(obs_path, mode="r") as obs_
