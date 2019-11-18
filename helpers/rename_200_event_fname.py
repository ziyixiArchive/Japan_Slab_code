from glob import glob
from os.path import join, basename
import subprocess
import click


@click.command()
@click.option('--work_dir', required=True, type=str)
def main(work_dir):
    all_asdf_files = glob(join(work_dir, "*h5"))
    for each_asdf in all_asdf_files:
        thebase = basename(each_asdf)
        thebase_dot_split = thebase.split(".")
        thebase_dot_split[0] = thebase_dot_split[0].split("_")[-1]
        newbase = ".".join(thebase_dot_split)
        newpath = join(work_dir, newbase)
        command = f"mv {each_asdf} {newpath}"
        subprocess.call(command, shell=True)


if __name__ == "__main__":
    main()
