import argparse
import sys
from glob import glob
from os.path import join

import numpy as np
import sh
import tqdm


def get_args(args=None):
    parser = argparse.ArgumentParser(
        description='A python script to init the structure of the specfem forward simulation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--base',
                        help='the directory to place all the specefem directories',
                        required=True)

    parser.add_argument('--cmtfiles',
                        help='cmt files, each named as the id of the event',
                        required=True)

    parser.add_argument('--ref',
                        help='reference specfem directories',
                        required=True)

    parser.add_argument('--output',
                        help='directory to place DATABASES_MPI and OUTPUT_FILES',
                        required=True)

    results = parser.parse_args(args)
    # return results["base"], results["cmtfiles"], results["ref"], results["output"]
    return results.base, results.cmtfiles, results.ref, results.output


def init_structure(base, cmtfiles, ref, output):
    # base dir
    sh.mkdir("-p", base)
    sh.cp("-r", ref, join(base, "ref"))
    sh.mkdir("-p", join(base, "work"))

    # refine the structure in ref
    sh.rm("-rf", join(base, "ref", "DATABASES_MPI"))
    sh.rm("-rf", join(base, "ref", "EXAMPLES"))
    sh.rm("-rf", join(base, "ref", "OUTPUT_FILES"))
    sh.rm("-rf", join(base, "ref", "doc"))
    sh.rm("-rf", join(base, "ref", "tests"))

    # mv DATA and utils to upper level
    sh.mv(join(base, "ref", "DATA"), base)
    sh.mv(join(base, "ref", "utils"), base)

    # get work directories' list
    dirs_raw = glob(join(cmtfiles, "*"))
    dirs = [i.split("/")[-1] for i in dirs_raw]

    # cp to work directories
    for dir in tqdm.tqdm(dirs):
        sh.cp("-r", join(base, "ref"), join(base, "work", dir))

    # mv DATA and utils back to ref
    sh.mv(join(base, "DATA"), join(base, "ref", "DATA"))
    sh.mv(join(base, "utils"), join(base, "ref", "utils"))

    # mkdir DATA in work directory
    for dir in dirs:
        sh.mkdir(join(base, "work", dir, "DATA"))

    # cp and ln files in DATA
    toln = ["cemRequest", "crust1.0", "crust2.0",
            "crustmap", "epcrust", "eucrust-07", "GLL", "heterogen", "Lebedev_sea99", "Montagner_model", "old", "PPM", "QRFSI12", "s20rts", "s362ani", "s40rts", "Simons_model", "topo_bathy", "Zhao_JP_model"]
    for dir in tqdm.tqdm(dirs):
        sh.cp(join(cmtfiles, dir), join(
            base, "work", dir, "DATA", "CMTSOLUTION"))
        sh.cp(join(base, "ref", "DATA", "Par_file"),
              join(base, "work", dir, "DATA", "Par_file"))
        sh.cp(join(base, "ref", "DATA", "STATIONS"),
              join(base, "work", dir, "DATA", "STATIONS"))
        for lnfile in toln:
            sh.ln("-s", join(base, "ref", "DATA", lnfile),
                  join(base, "work", dir, "DATA", lnfile))

        # ln in workfiles
        toln_work = ["utils"]
        for lnfile in toln_work:
            sh.ln("-s", join(base, "ref", lnfile),
                  join(base, "work", dir, lnfile))

    # mkdir and ln DATABASES_MPI and OUTPUT_FILES
    sh.mkdir("-p", output)
    sh.mkdir("-p", join(output, "DATABASES_MPI"))
    sh.mkdir("-p", join(output, "OUTPUT_FILES"))
    for dir in tqdm.tqdm(dirs):
        sh.mkdir("-p", join(output, "DATABASES_MPI", dir))
        sh.mkdir("-p", join(output, "OUTPUT_FILES", dir))
        sh.ln("-s", join(output, "DATABASES_MPI", dir),
              join(base, "work", dir, "DATABASES_MPI"))
        sh.ln("-s", join(output, "OUTPUT_FILES", dir),
              join(base, "work", dir, "OUTPUT_FILES"))


if __name__ == "__main__":
    base, cmtfiles, ref, output = get_args(sys.argv[1:])
    init_structure(base, cmtfiles, ref, output)
