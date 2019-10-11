"""
process sync file. 
"""
import obspy
import numpy as np
from mpi4py import MPI
import pyasdf
from obspy.signal.util import _npts2nfft
from os.path import join
from loguru import logger

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
isroot = (rank == 0)


def sync_remove_response(pre_filt, st):
    """
    mimic obspy.remove_response, but only do the frequency taper
    """
    obspy.core.util.misc.limit_numpy_fft_cache()
    for trace in st:
        data = trace.data.astype(np.float64)
        npts = len(data)
        nfft = _npts2nfft(npts)
        data = np.fft.rfft(data, n=nfft)
        t_samp = trace.stats.delta
        fy = 1 / (t_samp * 2.0)
        freqs = np.linspace(0, fy, nfft // 2 + 1).astype(np.float64)
        freq_domain_taper = obspy.signal.invsim.cosine_sac_taper(
            freqs, flimit=pre_filt)
        data *= freq_domain_taper
        data = np.fft.irfft(data)[0:npts]
        trace.data = data

    return st


def process_single_event(min_periods, max_periods, asdf_filename, waveform_length, sampling_rate, output_directory, logfile):
    # with pyasdf.ASDFDataSet(asdf_filename) as ds:
    ds = pyasdf.ASDFDataSet(asdf_filename, mode="r")

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

        f2 = 1.0 / max_period
        f3 = 1.0 / min_period
        f1 = 0.8 * f2
        f4 = 1.2 * f3
        pre_filt = (f1, f2, f3, f4)
        # log
        if(isroot):
            logger.success(
                f"[{rank}/{size}] {asdf_filename} is filtered with {f1} {f2} {f3} {f4}")

        # inv will be None if no inv provided
        def process_function(st, inv):
            # log, since all the sac files are 3 component, no need to do some checking
            logger.info(
                f"[{rank}/{size}] processing {'.'.join(st[0].id.split('.')[:2])}")

            status_code = check_time(st, event_time, waveform_length, inv)
            if(status_code == 0):
                pass
            elif(status_code == -1):
                logger.error(
                    f"[{rank}/{size}] {'.'.join(st[0].id.split('.')[:2])} error in cutting data")
                return
            else:
                raise Exception("unknown status code")
            st.trim(event_time, event_time+waveform_length)

            st.detrend("demean")
            st.detrend("linear")
            st.taper(max_percentage=0.05, type="hann")

            sync_remove_response(pre_filt, st)

            st.interpolate(sampling_rate=sampling_rate)

            # Convert to single precision to save space.
            for tr in st:
                tr.data = np.require(tr.data, dtype="float32")

            return st
        tag_name = "preprocessed_%is_to_%is" % (
            int(min_period), int(max_period))
        tag_map = {
            "sync": tag_name
        }

        output_name_head = asdf_filename.split("/")[-1].split(".")[0]
        ds.process(process_function, join(
            output_directory, output_name_head+"."+tag_name + ".h5"), tag_map=tag_map)
        logger.success(
            f"[{rank}/{size}] success in processing {asdf_filename} from {min_period}s to {max_period}s")


def check_time(st, event_time, waveform_length, inv):
    for trace in st:
        starttime = trace.stats.starttime
        endtime = trace.stats.endtime
        if(starttime > event_time):
            logger.error(
                f"[{rank}/{size}] {'.'.join(st[0].id.split('.')[:2])} starttime:{str(starttime)} > event_time:{str(event_time)}")
            return -1
        if(endtime < event_time+waveform_length):
            logger.error(
                f"[{rank}/{size}] {'.'.join(st[0].id.split('.')[:2])} endtime:{str(endtime)} < cut_time:{str(event_time+waveform_length)}")
            return -1
    return 0


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--min_periods', required=True, type=str, help="min periods in seconds, eg: 10,40")
    @click.option('--max_periods', required=True, type=str, help="max periods in seconds, eg: 120,120")
    @click.option('--asdf_filename', required=True, type=str, help="asdf raw data file name")
    @click.option('--waveform_length', required=True, type=float, help="waveform length to cut (from event start time)")
    @click.option('--sampling_rate', required=True, type=int, help="sampling rate in HZ")
    @click.option('--output_directory', required=True, type=str, help="output directory")
    @click.option('--logfile', required=True, type=str, help="the logging file")
    def main(min_periods, max_periods, asdf_filename, waveform_length, sampling_rate, output_directory, logfile):
        min_periods = [float(item) for item in min_periods.split(",")]
        max_periods = [float(item) for item in max_periods.split(",")]
        process_single_event(min_periods, max_periods, asdf_filename,
                             waveform_length, sampling_rate, output_directory, logfile)

    main()
