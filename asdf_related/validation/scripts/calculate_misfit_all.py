from glob import glob
from os.path import join, basename
import subprocess

all_models = ["crust1_stw105_processed",
              "EARA2014_nosmooth_crust2.0_processed",
              "EARA2014_nosmooth_processed",
              "EARA2014_smooth_crust2.0_processed",
              "EARA2014_smooth_processed",
              "FWEA18_nosmooth_processed",
              "FWEA18_smooth_processed",
              "hybrid_processed",
              "s362ani_processed"]

data_dir = "/mnt/scratch/xiziyi/validation/data_simple"
sync_dir = "/mnt/scratch/xiziyi/validation/sync"
win_dir = "/mnt/scratch/xiziyi/validation/win"
output_dir = "/mnt/scratch/xiziyi/validation/misfit"

process_flags = ["preprocessed_20s_to_120s"]


all_win_paths = glob(join(win_dir, "*"))
all_gcmtids = [basename(item).split(".")[0] for item in all_win_paths]


def kernel(each_gcmtid):
    for each_model in all_models:
        for each_process_flag in process_flags:
            data_fname = join(
                data_dir, f"raw_{each_gcmtid}.{each_process_flag}.h5")
            sync_fname = join(sync_dir, each_model,
                              f"{each_gcmtid}.{each_process_flag}.h5")
            win_fname = join(win_dir, f"{each_gcmtid}.txt")
            output_fname = join(output_dir, each_model,
                                f"{each_gcmtid}.{each_process_flag}.pkl")
            command = f"python ../get_misfit_from_windowpicker.py --data_fname {data_fname} --sync_fname {sync_fname} --win_fname {win_fname} --output_fname {output_fname}"
            subprocess.call(command, shell=True)


def main(each_gcmtid):
    for each_model in all_models:
        command = f"mkdir -p {join(output_dir,each_model)}"
    kernel(each_gcmtid)


if __name__ == "__main__":
    main("201201010527A")
