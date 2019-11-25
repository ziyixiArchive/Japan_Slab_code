"""
Simplify stations for all asdf files in a directory.
"""

from glob import glob
import click
import subprocess
from os.path import join, basename
from simplify_data_after_process import work
import multiprocessing

# PY = "/mnt/home/xiziyi/anaconda3/envs/seismology/bin/python"


def run_single(asdf_file, logfile, output_file):
    # command = f"{PY} ./simplify_stations_after_process_data.py --asdf_file {asdf_file} --logfile {logfile} --output_file {output_file}"
    # subprocess.call(command, shell=True)
    work(asdf_file, logfile, output_file)


def kernel(info):
    asdf_file, log_file, output_file = info
    run_single(asdf_file, log_file, output_file)


def run_all(base_dir, log_file, output_dir):
    allfiles = glob(join(base_dir, "*h5"))
    allfnames = [basename(item) for item in allfiles]
    alloutputs = [join(output_dir, fname) for fname in allfnames]

    # for asdf_file, output_file in zip(allfiles, alloutputs):
    #     print(asdf_file)
    #     run_single(asdf_file, log_file, output_file)

    # build the iterable list
    info_list = []
    for asdf_file, output_file in zip(allfiles, alloutputs):
        info_list.append((asdf_file, log_file, output_file))
    with multiprocessing.Pool(processes=30) as pool:
        pool.map(kernel, info_list)


@click.command()
@click.option('--base_dir', required=True, type=str, help="the asdf directory")
@click.option('--log_file', required=True, type=str, help="the log file")
@click.option('--output_dir', required=True, type=str, help="the output directory")
def main(base_dir, log_file, output_dir):
    run_all(base_dir, log_file, output_dir)


if __name__ == "__main__":
    main()
