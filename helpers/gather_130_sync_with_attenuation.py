from glob import glob
from os.path import join, basename
import subprocess

base_dir = "/mnt/research/seismolab2/japan_slab/sync/with_attenuation_130_sync/OUTPUT_FILES"
output_dir = "/mnt/research/seismolab2/japan_slab/sync/with_attenuation_130_sync"

all_sync_fpaths = glob(join(base_dir, "*", "synthetic.h5"))
all_gcmtids = [item.split("/")[-2] for item in all_sync_fpaths]

# move files
for sync_fpath, gcmtid in zip(all_sync_fpaths, all_gcmtids):
    output_fpath = join(output_dir, f"{gcmtid}.h5")
    command = f"mv {sync_fpath} {output_fpath}"
    subprocess.call(command, shell=True)
