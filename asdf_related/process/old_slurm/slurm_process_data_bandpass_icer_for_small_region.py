import sys
from glob import glob
from os.path import join

from slurmpy import Slurm

# some resources information
N_cores = 100
N_node = 5
N_cores_each_node = 20

# the base sync directory storing asdf files
N_files = 71
N_iters = 15

# some configuration
PY = "/mnt/home/xiziyi/anaconda3/envs/seismology/bin/python"
min_periods = "6,10,20,40"
max_periods = "100,100,100,100"
waveform_length = 1200
sampling_rate = 10
logfile = "/mnt/scratch/xiziyi/process_data_small/process_data_284.log"
RAW_DIR_HEAD = "/mnt/scratch/xiziyi/process_data_small/asdf_all_284_sub"
PROCESSED_DIR = "/mnt/scratch/xiziyi/process_data_small/asdf_all_284_processed"
cea_correction_file = "./cmpaz_segment.txt"
sub_number = 4


def get_files(base_dir):
    return glob(join(base_dir, "*h5"))


def get_scripts(run_files):
    result = ""
    result += "module purge;"
    result += "module load GCC/8.2.0-2.31.1;"
    result += "module load OpenMPI/3.1.3;"
    # run iters
    for iiter in range(N_iters):
        result += f"echo 'start iteration {iiter}'; "
        for ieach in range(N_node):
            # run N_node files at the same iter
            offset = iiter*N_node+ieach
            if(offset >= N_files):
                continue
            filename = run_files[offset]
            result += f"srun -n {N_cores_each_node} --exclusive {PY} ./process_data_bandpass.py --min_periods {min_periods} --max_periods {max_periods} --asdf_filename {filename} --waveform_length {waveform_length} --sampling_rate {sampling_rate} --output_directory {PROCESSED_DIR} --logfile {logfile} --correct_cea --cea_correction_file {cea_correction_file} &"
        result += f"wait; "
        result += f"echo 'end iteration {iiter}'; "

    return result


def submit_job(thecommand):
    s = Slurm("process_data", {"nodes": N_node, "ntasks": N_cores,
                               "time": "24:00:00", "cpus-per-task": 1, "mem-per-cpu": "4G"})
    s.run(thecommand)


if __name__ == "__main__":
    for index in range(sub_number):
        RAW_DIR=RAW_DIR_HEAD+str(index+1)
        run_files = get_files(RAW_DIR)
        thecommand = get_scripts(run_files)
        submit_job(thecommand)
