from glob import glob
from os.path import join, basename
import subprocess


cmt_dir = "/mnt/research/seismolab2/japan_slab/cmts/130_used_events"
data_dir = "/mnt/scratch/xiziyi/process_data/asdf_all_484_processed_simple"
out_dir = "/mnt/scratch/xiziyi/process_data/asdf_all_130_processed_simple"

# get gcmtids
all_cmt_files = glob(join(cmt_dir, "*"))
all_gcmtids = [basename(item) for item in all_cmt_files]
