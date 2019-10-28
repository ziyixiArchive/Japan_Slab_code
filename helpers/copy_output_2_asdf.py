from glob import glob
from os.path import join, basename
import subprocess

data_dir = "/scratch/05880/tg851791/asdf_sync_small_region/output/OUTPUT_FILES"
output_dir = "/scratch/05880/tg851791/asdf_sync_small_region/asdf"

all_sync_files = glob(join(data_dir, "*", "synthetic.h5"))

for each_file in all_sync_files:
    gcmtid = each_file.split("/")[-2]
    to_path = join(output_dir, f"{gcmtid}.h5")
    command = f"cp {each_file} {to_path}"
    subprocess.call(command, shell=True)
