from glob import glob
from os.path import join, basename
import subprocess

data_dir = "/mnt/scratch/xiziyi/validation/data_simple"
pkl_dir = "/mnt/scratch/xiziyi/validation/data_time"

all_data_paths = glob(join(data_dir, "*.preprocessed_10s_to_120s.h5"))

for each_data_path in all_data_paths:
    thebasename = basename(each_data_path)
    gcmtid = thebasename.split(".")[0].split("_")[-1]
    to_path = join(pkl_dir, f"{gcmtid}.pkl")
    command = f"mpirun -np 36 python ../../process/write_auxiliary_info2file.py --obs_path {each_data_path} --ref_path {each_data_path} --pkl_path {to_path}"
    subprocess.call(command, shell=True)
