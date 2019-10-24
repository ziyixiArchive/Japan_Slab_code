import subprocess
from glob import glob
from os.path import join, basename

raw_dir = "/Users/ziyixi/work/Datas/windows_picker/20s-logs"
simplified_dir = "/Users/ziyixi/work/Datas/windows_picker/20s-logs-simplified"

all_raw_paths = glob(join(raw_dir, "*"))
all_raw_basenames = [basename(item) for item in all_raw_paths]
all_output_paths = [join(simplified_dir, item) for item in all_raw_basenames]

for raw_path, output_path in zip(all_raw_paths, all_output_paths):
    command = f"python ../extract_windows_info.py --windows_path {raw_path} --output_path {output_path}"
    subprocess.call(command, shell=True)
