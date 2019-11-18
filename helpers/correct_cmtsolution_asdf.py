"""
Correct cmtsolution for the asdf files.
"""
import obspy
import pyasdf
from glob import glob
from os.path import join, basename
import tqdm

cmt_dir = "/mnt/research/seismolab2/japan_slab/cmts/Japan_slab_from_used_EARA2014"


@click.command()
@click.option('--work_dir', required=True, type=str)
def main(work_dir):
    all_asdf_paths = glob(join(work_dir, "*h5"))
    for each_asdf_path in tqdm.tqdm(all_asdf_paths):
        each_fname = basename(each_asdf_path)
        each_gcmtid = each_fname.split(".")[0]
        gcmt_event = obspy.read_events(join(cmt_dir, each_gcmtid))
        used_event = obspy.read_events(gcmt_event)

        with pyasdf.ASDFDataSet(each_asdf_path) as data:
            data.events = used_event


if __name__ == "__main__":
    main()
