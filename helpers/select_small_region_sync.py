from os.path import join,basename
from glob import glob
import subprocess
from glob import glob

sync_dir="/scratch/05880/tg851791/asdf_sync_small_region/output/OUTPUT_FILES"
output_dir="/scratch/05880/tg851791/sac_files_for_small_region/sync_small"

all_event_paths=glob(join(sync_dir,"*"))
all_gcmtids=[basename(item) for item in all_event_paths]

for each_gcmtid in glob(all_gcmtids):
    command=f"mkdir -p {output_dir}/{each_gcmtid}"
    subprocess.call(command,shell=True)
    command=f"mv {sync_dir}/{each_gcmtid}/*sem.sac {output_dir}/{each_gcmtid}"
    subprocess.call(command,shell=True)