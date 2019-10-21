import argparse
import sys
from glob import glob
from os.path import join

from slurmpy import Slurm

N_total = 192
N_each = 12
N_iter = 16
nproc = 324


def get_args(args=None):
    parser = argparse.ArgumentParser(
        description='A python script to submit jobs in one sbatch job',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--base',
                        help='the directory to place all the specefem directories',
                        required=True)
    results = parser.parse_args(args)
    return results.base


def get_dirs(base):
    return glob(join(base, "*"))


def get_scripts(thedirs):
    result = "date; "
    result += "module load boost/1.68; "
    result += "module load phdf5/1.8.16; "
    # for xmeshfem3D
    result += f"echo 'start xmeshfem3D'; "
    for iiter in range(N_iter):
        result += f"echo 'start iteration {iiter}'; "
        for ieach in range(N_each):
            # ievent
            ievent = iiter*N_each+ieach
            ievent_dir = thedirs[ievent]
            # cd
            result += f"cd {ievent_dir}; "
            # if N_each-1
            if(ieach == N_each-1):
                inc = ieach*nproc
                result += f"ibrun -n {nproc} -o {inc} ./bin/xmeshfem3D; "
            else:
                inc = ieach*nproc
                result += f"ibrun -n {nproc} -o {inc} ./bin/xmeshfem3D & "
        result += f"wait; "
        result += f"echo 'end iteration {iiter}'; "
        result += f"date; "

    # for xspecfem3D
    result += f"echo 'start xspecfem3D'; "
    for iiter in range(N_iter):
        result += f"echo 'start iteration {iiter}'; "
        for ieach in range(N_each):
            # ievent
            ievent = iiter*N_each+ieach
            ievent_dir = thedirs[ievent]
            # cd
            result += f"cd {ievent_dir}; "
            # if N_each-1
            if(ieach == N_each-1):
                inc = ieach*nproc
                result += f"ibrun -n {nproc} -o {inc} ./bin/xspecfem3D; "
            else:
                inc = ieach*nproc
                result += f"ibrun -n {nproc} -o {inc} ./bin/xspecfem3D & "
        result += f"wait; "
        result += f"echo 'end iteration {iiter}'; "
        result += f"date; "

    return result


def submit_job(thecommand):
    s = Slurm("sync", {"nodes": 81, "ntasks": 3888,
                       "partition": 'skx-normal', "time": "20:00:00", "account": "TG-EAR140030"})
    s.run(thecommand)


if __name__ == "__main__":
    base = get_args(sys.argv[1:])
    thedirs = get_dirs(base)
    thecommand = get_scripts(thedirs)
    submit_job(thecommand)
