from glob import glob
from os.path import join, basename
import subprocess

work_dir = "/mnt/scratch/xiziyi/validation/data"
output_dir = "/mnt/scratch/xiziyi/validation/data_simple"

all_paths = glob(work_dir, "*")

for each_path in all_paths:
    thebasename = basename(each_path)
    to_path = join(output_dir, thebasename)
    command = f"python ../../process/simplify_data_after_process.py --asdf_file {each_path} --logfile ./simple_all.log --output_file {to_path}"
    subprocess.call(command, shell=True)
