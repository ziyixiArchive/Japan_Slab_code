from glob import glob
from os.path import join, basename
import subprocess

from_dir = "/mnt/scratch/xiziyi/process_data/asdf_all_284_processed"
to_dir = "/mnt/scratch/xiziyi/validation/data"
win_dir = "/mnt/scratch/xiziyi/validation/win"

all_win_paths = glob(join("/mnt/scratch/xiziyi/validation/win", "*"))
all_win_fnames = [basename(item) for item in all_win_paths]
all_gcmt_ids = [item.split(".")[0] for item in all_win_fnames]
all_from_paths = [join(from_dir, f"raw_{item}*") for item in all_gcmt_ids]

for from_path in all_from_paths:
    command = f"cp {from_path} {to_dir}/"
    subprocess.call(command)
