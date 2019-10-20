"""
remove stations with no data after processing.
"""
import pyasdf
import subprocess
from loguru import logger
import click
import obspy


def remove_stations(ds):
    waveform_list = ds.waveforms.list()
    for item in waveform_list:
        wg = ds.waveforms[item]
        data_tags = wg.get_waveform_tags()
        if(len(data_tags) == 0):
            inv = wg["StationXML"]
            logger.info(f"remove {inv.get_contents()['stations'][0]}")
            del ds.waveforms[item]
        else:
            # see if there are only three traces
            tag = data_tags[0]
            st = wg[tag]
            # after procesing the data, the only possible is the case of mul locs
            if(len(st) == 3):
                continue
            else:
                loc_set = set()
                for trace in st:
                    net, sta, loc, cha = trace.id.split(".")
                    loc_set.add(loc)
                if("" in loc_set):
                    reference_loc = ""
                else:
                    reference_loc = sorted(loc_set)[0]

                for trace in st:
                    net, sta, loc, cha = trace.id.split(".")
                    if(loc != reference_loc):
                        st.remove(trace)

                inv = wg["StationXML"]
                discard_locs = sorted(loc_set-set([reference_loc]))
                logger.info(
                    f"{inv.get_contents()['stations'][0]} keeps the loc {reference_loc}, discard {discard_locs}")


def work(asdf_file, logfile, output_file):
    command = f"cp {asdf_file} {output_file}"
    subprocess.call(command, shell=True)

    # ds = pyasdf.ASDFDataSet(output_file)
    with pyasdf.ASDFDataSet(output_file) as ds:
        logger.add(logfile, format="{time} {level} {message}", level="INFO")
        logger.info(f"start to process {output_file}")

        remove_stations(ds)
        logger.success("finish removing missing stations")
    # del ds


@click.command()
@click.option('--asdf_file', required=True, type=str, help="the data asdf file")
@click.option('--logfile', required=True, type=str, help="the log file")
@click.option('--output_file', required=True, type=str, help="the output file")
def main(asdf_file, logfile, output_file):
    work(asdf_file, logfile, output_file)


if __name__ == "__main__":
    main()
