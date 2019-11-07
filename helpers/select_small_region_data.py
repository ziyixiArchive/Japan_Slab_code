import numpy as np 
from os.path import join,basename
import subprocess
from glob import glob
from tqdm import tqdm

station_path="/scratch/05880/tg851791/asdf_sync_small_region/ref/DATA/STATIONS"
data_dir="/scratch/05880/tg851791/sac_files_for_small_region/data"
output_dir="/scratch/05880/tg851791/sac_files_for_small_region/data_small"


# read station file
station=np.loadtxt(station_path,dtype=np.str)
pairs=[f"{row[1]}.{row[0]}" for row in station]

# get all event names
all_events_path=glob(join(data_dir,"*"))
all_gcmtids=[basename(item) for item in all_events_path]

# loop through all gcmtids
for each_gcmtid in tqdm(all_gcmtids):
    # mkdir
    command=f"mkdir -p {output_dir}/{each_gcmtid}"
    subprocess.call(command,shell=True)
    # mv sac files
    all_sac_files=glob(join(data_dir,each_gcmtid,"*"))
    for each_file in all_sac_files:
        thebase=basename(each_file)
        fname_spliter=thebase.split(".")
        try:
            thekey=".".join([fname_spliter[0],fname_spliter[1]])
        except:
            thekey=None
        if(thekey in pairs):
            out_path=join(output_dir,each_gcmtid,thebase)
            command=f"mv {each_file} {out_path}"
            subprocess.call(command,shell=True)
    # mv PZ files
    command=f"mkdir -p {output_dir}/{each_gcmtid}/PZ"
    subprocess.call(command,shell=True)
    all_pz_files=glob(join(data_dir,each_gcmtid,"PZ","*"))
    for each_file in all_pz_files:
        thebase=basename(each_file)
        fname_spliter=thebase.split(".")
        try:
            thekey=".".join([fname_spliter[0],fname_spliter[1]])
        except:
            thekey=None
        if(thekey in pairs):
            out_path=join(output_dir,each_gcmtid,"PZ",thebase)
            command=f"mv {each_file} {out_path}"
            subprocess.call(command,shell=True)
    # mv extra files
    command=f"mkdir -p {output_dir}/{each_gcmtid}/extra"
    subprocess.call(command,shell=True)
    all_pz_files=glob(join(data_dir,each_gcmtid,"extra","*"))
    for each_file in all_pz_files:
        thebase=basename(each_file)
        fname_spliter=thebase.split(".")
        try:
            thekey=".".join([fname_spliter[0],fname_spliter[1]])
        except:
            thekey=None
        if(thekey in pairs):
            out_path=join(output_dir,each_gcmtid,"extra",thebase)
            command=f"mv {each_file} {out_path}"
            subprocess.call(command,shell=True)
