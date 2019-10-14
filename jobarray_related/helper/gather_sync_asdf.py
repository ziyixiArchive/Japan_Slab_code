"""
Gather sync asdf files in a working directory
"""
from glob import glob
from os.path import join
import subprocess
import click


def get_asdf_paths(work_dir):
    all_sync_paths = glob(join(work_dir, "*", "OUTPUT_FILES", "synthetic.h5"))
    return all_sync_paths


def move_sync_files(all_sync_paths, output_dir):
    for each_sync_path in all_sync_paths:
        gcmtid = each_sync_path.split("/")[-3]
        target_path = join(output_dir, f"{gcmtid}.h5")
        command = f"mv {each_sync_path} {target_path}"
        subprocess.call(command, shell=True)


@click.command()
@click.option('--work_dir', required=True, type=str)
@click.option('--output_dir', required=True, type=str)
def main(work_dir, output_dir):
    all_sync_paths = get_asdf_paths(work_dir)
    move_sync_files(all_sync_paths, output_dir)


if __name__ == "__main__":
    main()
