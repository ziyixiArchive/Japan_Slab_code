"""
Check if the asdf files have been broken.
"""
from glob import glob
import pyasdf
import numpy as np
import click
from os.path import join
import tqdm
import multiprocessing


def get_all_files(main_dir):
    return glob(join(main_dir, "*h5"))


def check(fname):
    try:
        with pyasdf.ASDFDataSet(fname) as ds:
            for item in ds.waveforms.list():
                maxvalue = np.max(ds.waveforms[item].sync[0].data)
        return True
    except:
        print(fname)
        return False


@click.command()
@click.option('--main_dir', required=True, type=str, help="working directory")
def main(main_dir):
    all_files = get_all_files(main_dir)
    with multiprocessing.Pool(processes=30) as pool:
        r = list(tqdm.tqdm(pool.imap(check, all_files)))


if __name__ == "__main__":
    main()
