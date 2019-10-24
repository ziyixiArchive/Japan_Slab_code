from glob import glob
from os.path import join, basename
import subprocess

pkl_dir = "/mnt/scratch/xiziyi/validation/data_time"
data_dir = "/mnt/scratch/xiziyi/validation/data_simple"

all_data_paths = glob(join(data_dir, "*h5"))
for each_data_path in all_data_paths:
    thebasename = basename(each_data_path)
    gcmtid = thebasename.split(".")[0].split("_")[-1]
    ref_path = join(pkl_dir, f"{gcmtid}.pkl")
    command = f"python ../../process/update_auxiliary_from_file.py --obs_path {each_data_path} --pkl_path {ref_path}"
    subprocess.call(command, shell=True)
