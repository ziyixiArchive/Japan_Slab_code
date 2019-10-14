"""
write the auxiliary info for an data asdf file to a file.
"""
import click
import numpy as np
import obspy
import pyasdf
from mpi4py import MPI
from obspy.geodetics.base import gps2dist_azimuth, locations2degrees
from obspy.taup import TauPyModel
import pickle
import tempfile

model = TauPyModel(model='ak135')
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
isroot = (rank == 0)


def get_property_times(stla, stlo, evla, evlo, evdp):
    property_times = {
        "p": None,  # either p or P
        "s": None,
        "rayleigh": None,
        "love": None,
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
        if(property_times["rayleigh"] == None):
            if(item.name == "3.5kmps"):
                property_times["rayleigh"] = item.time
        if(property_times["love"] == None):
            if(item.name == "4.0kmps"):
                property_times["love"] = item.time

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


@click.command()
@click.option('--obs_path', required=True, type=str, help="the obs hdf5 file path")
@click.option('--ref_path', required=True, type=str, help="the ref hdf5 file path (not necessary, but have to provide one)")
@click.option('--pkl_path', required=True, type=str, help="the pickle file to store the auxiliary info")
def main(obs_path, ref_path, pkl_path):
    results = None
    with pyasdf.ASDFDataSet(obs_path, mode="a") as obs_ds:
        with pyasdf.ASDFDataSet(ref_path, mode="r") as ref_ds:
            event = obs_ds.events[0]
            origin = event.preferred_origin() or event.origins[0]
            evla = origin.latitude
            evlo = origin.longitude
            evdp = origin.depth/1000

            # kernel function
            def process(sg_obs, sg_ref):
                waveform_tags = sg_obs.get_waveform_tags()
                inv_obs = sg_obs["StationXML"]
                station_info = {inv_obs.get_contents()['stations'][0]}

                # should have only one tag, after we have simplify the asdf file
                tag_obs = waveform_tags[0]
                st_obs = sg_obs[tag_obs]

                # property times
                stla = inv_obs[0][0].latitude
                stlo = inv_obs[0][0].longitude
                property_times = get_property_times(
                    stla, stlo, evla, evlo, evdp)

                return property_times
            results = obs_ds.process_two_files_without_parallel_output(
                ref_ds, process)

            if(isroot):
                with open(pkl_path, 'wb') as handle:
                    pickle.dump(results, handle)


if __name__ == "__main__":
    main()
