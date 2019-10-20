import subprocess
from os.path import join, basename
from glob import glob

cmt_dir = "/mnt/research/seismolab2/japan_slab/cmts/Japan_slab_validation"
asdf_all_284_dir = "/mnt/scratch/xiziyi/process_data/asdf_all_284"
target_dir = "/mnt/scratch/xiziyi/process_data/asdf_validation_from_284"

all_gcmtid_paths = glob(join(cmt_dir, "*"))
all_gcmtids = [basename(item) for item in all_gcmtid_paths]

for gcmtid in all_gcmtids:
    from_path = join(asdf_all_284_dir, f"raw_{gcmtid}.h5")
    to_path = join(target_dir, f"raw_{gcmtid}.h5")
    try:
        command = f"cp {from_path} {to_path}"
        subprocess.call(command, shell=True)
    except:
        pass
