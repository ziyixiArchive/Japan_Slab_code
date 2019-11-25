from os.path import join, basename
from glob import glob
import subprocess

sync_dir = "/mnt/scratch/xiziyi/process_sync_small/processed"
data_dir = "/mnt/scratch/xiziyi/process_data_small/asdf_all_484_processed_simple"
sync_out_dir = "/mnt/scratch/xiziyi/asdf_small/sync"
data_out_dir = "/mnt/scratch/xiziyi/asdf_small/data"

all_sync_fpath = glob(join(sync_dir, "*h5"))
all_sync_fname = [basename(item) for item in all_sync_fpath]
for each_fname in all_sync_fname:
    # data
    data_from = join(data_dir, each_fname)
    data_to = join(data_out_dir, each_fname)
    command = f"cp {data_from} {data_to}"
    subprocess.call(command, shell=True)
    # sync
    sync_from = join(sync_dir, each_fname)
    sync_to = join(sync_out_dir, each_fname)
    command = f"cp {sync_from} {sync_to}"
    subprocess.call(command, shell=True)
