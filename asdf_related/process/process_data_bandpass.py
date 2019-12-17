"""
process asdf data file.
"""

from os.path import join

import numpy as np
import obspy
import pyasdf
from loguru import logger
from obspy.geodetics.base import gps2dist_azimuth
from pyasdf import ASDFDataSet
import pandas as pd
from mpi4py import MPI
import io
from obspy.signal.invsim import simulate_seismometer

# fix a bug in intel
import mpi4py
mpi4py.rc.recv_mprobe = False

# TODO problems may be in "water level" somewhere

# global parameters
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
isroot = (rank == 0)


# CEA_NETWORKS
CEA_NETWORKS = ["AH", "BJ", "BU", "CQ", "FJ", "GD", "GS", "GX", "GZ", "HA", "HB", "HE", "HI", "HL", "HN",
                "JL", "JS", "JX", "LN", "NM", "NX", "QH", "SC", "SD", "SH", "SN", "SX", "TJ", "XJ", "XZ", "YN", "ZJ"]


def process_single_event(min_periods, max_periods, taper_tmin_tmax, asdf_filename, waveform_length, sampling_rate, output_directory, logfile, correct_cea, cea_correction_file):
    # with pyasdf.ASDFDataSet(asdf_filename) as ds:
    tmin, tmax = map(float, taper_tmin_tmax.split(","))
    with pyasdf.ASDFDataSet(asdf_filename, mode="r") as ds:

        # load cea correction file
        if(correct_cea):
            correction_data = pd.read_csv(cea_correction_file, sep="|", comment="#", names=[
                "network", "station", "eventno", "mean", "std", "median", "mad", "starttime", "endtime"])
            correction_data["starttime"] = correction_data["starttime"].apply(
                modify_time)
            correction_data["endtime"] = correction_data["endtime"].apply(
                modify_time)

        # add logger information
        logger.add(logfile, format="{time} {level} {message}", level="INFO")

        # some parameters
        event = ds.events[0]
        origin = event.preferred_origin() or event.origins[0]
        event_time = origin.time
        event_latitude = origin.latitude
        event_longitude = origin.longitude

        for min_period, max_period in zip(min_periods, max_periods):
            # log
            if(isroot):
                logger.success(
                    f"[{rank}/{size}] start to process {asdf_filename} from {min_period}s to {max_period}s")
                if(correct_cea):
                    logger.success(
                        f"[{rank}/{size}] will correct cea dataset according to the cea station orientation information")

            f2 = 1.0 / tmax
            f3 = 1.0 / tmin
            f1 = 0.5 * f2
            f4 = 2.0 * f3
            pre_filt = (f1, f2, f3, f4)

            # log
            if(isroot):
                logger.success(
                    f"[{rank}/{size}] {asdf_filename} is filtered with {f1} {f2} {f3} {f4}")

            def process_function(st, inv):
                # log
                logger.info(
                    f"[{rank}/{size}] processing {inv.get_contents()['stations'][0]}")

                # there are possibility that some stations has multiple loc codes or use HH stations. (should avoid in the future)
                st = filter_st(st, inv)

                # overlap the previous trace
                status_code = check_st_numberlap(st, inv)
                if(status_code == -1):
                    return
                elif(status_code == 0):
                    pass
                elif(status_code == 1):
                    # merge may have roblem (samplign rate is not equal)
                    try:
                        st.merge(method=1, fill_value=0,
                                 interpolation_samples=0)
                    except:
                        logger.error(
                            f"[{rank}/{size}] {inv.get_contents()['stations'][0]} error in merging")
                        return
                else:
                    raise Exception("unknown status code")

                status_code = check_time(st, event_time, waveform_length, inv)
                if(status_code == 0):
                    pass
                elif(status_code == -1):
                    logger.error(
                        f"[{rank}/{size}] {inv.get_contents()['stations'][0]} error in cutting data")
                    return
                else:
                    raise Exception("unknown status code")
                # trim will automatically use starttime if starttime>eventtime
                st.trim(event_time, event_time+waveform_length)

                st.detrend("demean")
                st.detrend("linear")
                st.taper(max_percentage=0.05, type="hann")

                # st.remove_response(output="DISP", pre_filt=pre_filt, zero_mean=False,
                #                    taper=False, inventory=inv, water_level=None)
                # here we should use PZ files to remove the response.
                st = remove_response(st, pre_filt=pre_filt, inv=inv)

                # the same of removing response with sac
                st.detrend("demean")
                st.detrend("linear")

                st.interpolate(sampling_rate=sampling_rate)

                # ! have problem here (all value is zero)
                station_latitude = inv[0][0].latitude
                station_longitude = inv[0][0].longitude

                # baz is calculated using station and event's location
                # for cea stations, we can directly add an angle to it
                _, baz, _ = gps2dist_azimuth(station_latitude, station_longitude,
                                             event_latitude, event_longitude)

                network = inv.get_contents()['networks'][0]
                if(correct_cea and (network in CEA_NETWORKS)):
                    baz = func_correct_cea(
                        baz, inv, event_time, correction_data)
                if(baz == None):
                    logger.error(
                        f"[{rank}/{size}] {inv.get_contents()['stations'][0]} error in correcting orientation")
                    return

                # we have to limit baz to be in [0,360)
                baz = np.mod(baz, 360)

                components = [tr.stats.channel[-1] for tr in st]
                if "N" in components and "E" in components:
                    # there may be some problem in rotating (time span is not equal for three channels)
                    try:
                        st.rotate(method="NE->RT", back_azimuth=baz)
                    except:
                        logger.error(
                            f"[{rank}/{size}] {inv.get_contents()['stations'][0]} error in rotating")
                        return
                else:
                    logger.error(
                        f"[{rank}/{size}] {inv.get_contents()['stations'][0]} doesn't have both N and E")
                    return

                # bandpass filter
                st.filter("bandpass", freqmin=1.0/max_period,
                          freqmax=1.0/min_period, corners=2, zerophase=True)

                # Convert to single precision to save space.
                for tr in st:
                    tr.data = np.require(tr.data, dtype="float32")

                return st

            tag_name = "preprocessed_%is_to_%is" % (
                int(min_period), int(max_period))
            tag_map = {
                "raw": tag_name
            }
            output_name_head = asdf_filename.split("/")[-1].split(".")[0]
            ds.process(process_function, join(
                output_directory, output_name_head+"."+tag_name + ".h5"), tag_map=tag_map)

            if(rank == 0):
                logger.success(
                    f"[{rank}/{size}] success in processing {asdf_filename} from {min_period}s to {max_period}s")


def check_st_numberlap(st, inv):
    """
    detect overlapping
    """
    if(len(st) == 0):
        logger.error(
            f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has only 0 traces")
        return -1
    elif(len(st) < 3):
        logger.error(
            f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has less than 3 traces")
        return -1
    elif(len(st) == 3):
        channel_set = set()
        for item in st:
            channel_set.add(item.id[-1])
        if(len(channel_set) == 3):
            return 0
        else:
            logger.error(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has less than 3 channels")
            return -1
    else:
        channel_set = set()
        for item in st:
            channel_set.add(item.id[-1])
        if(len(channel_set) == 3):
            logger.warning(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has {len(st)} traces, need to merge")
            return 1
        elif(len(channel_set) < 3):
            logger.error(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has less than 3 channels")
            return -1
        else:
            logger.error(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has {len(channel_set)} channels, error!")
            return -1


def remove_response(st, pre_filt=None, inv=None):
    for index, item in enumerate(st):
        pz_vir_file = io.StringIO()
        inv_tr = inv.select(channel=item.stats.channel)
        inv_tr.write(pz_vir_file, format="SACPZ")
        pz_vir_file.seek(0)
        obspy.io.sac.sacpz.attach_paz(item, pz_vir_file)
        data = simulate_seismometer(
            item.data, item.stats.sampling_rate, paz_remove=item.stats.paz, water_level=6e9, zero_mean=False, taper=False, pre_filt=pre_filt, sacsim=True)
        st[index].data = data
    return st


def modify_time(time_str):
    if(type(time_str) != str):
        return obspy.UTCDateTime("2099-09-01")
    else:
        return obspy.UTCDateTime(time_str)


def func_correct_cea(baz, inv, event_time, correction_data):
    network, station = inv.get_contents()["channels"][0].split(".")[:2]

    # after 2013-09-01T11:52:00Z, all the stations have been corrected
    trunc_datetime = obspy.UTCDateTime("2013-09-01T11:52:00Z")
    if(event_time > trunc_datetime):
        logger.info(
            f"[{rank}/{size}] {inv.get_contents()['stations'][0]} is later than 2013-09-01T11:52:00Z")
        return baz
    else:
        info_for_this_station = correction_data.loc[(
            correction_data.network == network) & (correction_data.station == station) & (correction_data.starttime <= event_time) & (correction_data.endtime >= event_time)]
        if(len(info_for_this_station) == 0):
            logger.error(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has no correcting orientation's information!")
            return None
        elif(len(info_for_this_station) == 1):
            median_value = info_for_this_station["median"].values[0]
            if(np.isnan(median_value)):
                if_has_been_corrected = (
                    info_for_this_station["endtime"].values[0] == obspy.UTCDateTime("2099-09-01"))
                if(if_has_been_corrected):
                    logger.info(
                        f"[{rank}/{size}] {inv.get_contents()['stations'][0]} is later than {str(info_for_this_station['starttime'].values[0])}")
                    return baz
                else:
                    logger.error(
                        f"[{rank}/{size}] {inv.get_contents()['stations'][0]} median value is nan")
                    return None
            logger.info(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} ({baz},{median_value})->({baz-median_value})")
            return baz-median_value
        else:
            logger.error(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} has more than one row of orientation information")
            return None


def check_time(st, event_time, waveform_length, inv):
    for trace in st:
        starttime = trace.stats.starttime
        endtime = trace.stats.endtime
        # add some tolerance here (1 min)
        if(starttime-60 > event_time):
            logger.error(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} starttime:{str(starttime)} > event_time:{str(event_time)}")
            return -1
        if(endtime < event_time+waveform_length):
            logger.error(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} endtime:{str(endtime)} < cut_time:{str(event_time+waveform_length)}")
            return -1
    return 0


def filter_st(st, inv):
    # we should assure only to add one type of data, as the order of HH,BH,SH (we don't consider the case like
    # only 2 HH but 3 BH.)
    newst = obspy.Stream()
    # get band code status
    band_code = None
    band_code_list = []
    for trace in st:
        theid = trace.id
        net, sta, loc, cha = theid.split(".")
        band_code_list.append(cha[:2])
    if(len(band_code_list) == 0):
        return newst
    else:
        if("HH" in band_code_list):
            band_code = "HH"
        elif("BH" in band_code_list):
            band_code = "BH"
        elif("SH" in band_code_list):
            band_code = "SH"
        else:
            return newst
    for trace in st:
        theid = trace.id
        net, sta, loc, cha = theid.split(".")

        con1 = ((loc == "") or (loc == "00"))
        con2 = (cha[:2] == band_code)
        if(con1 and con2):
            newst += trace
        else:
            logger.warning(
                f"[{rank}/{size}] {inv.get_contents()['stations'][0]} remove id: {theid}")
    return newst


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--min_periods', required=True, type=str, help="min periods in seconds, eg: 10,40")
    @click.option('--max_periods', required=True, type=str, help="max periods in seconds, eg: 120,120")
    @click.option('--taper_tmin_tmax', required=True, type=str, help="frequency taper tmin(f3) and tmax(f2), eg: 1,400")
    @click.option('--asdf_filename', required=True, type=str, help="asdf raw data file name")
    @click.option('--waveform_length', required=True, type=float, help="waveform length to cut (from event start time)")
    @click.option('--sampling_rate', required=True, type=int, help="sampling rate in HZ")
    @click.option('--output_directory', required=True, type=str, help="output directory")
    @click.option('--logfile', required=True, type=str, help="the logging file")
    @click.option('--correct_cea/--no-correct_cea', default=False, help="if handling cea dataset")
    @click.option('--cea_correction_file', required=False, type=str, help="the cea correction file")
    def main(min_periods, max_periods, taper_tmin_tmax, asdf_filename, waveform_length, sampling_rate, output_directory, logfile, correct_cea, cea_correction_file):
        min_periods = [float(item) for item in min_periods.split(",")]
        max_periods = [float(item) for item in max_periods.split(",")]
        process_single_event(min_periods, max_periods, taper_tmin_tmax, asdf_filename,
                             waveform_length, sampling_rate, output_directory, logfile, correct_cea, cea_correction_file)

    main()
