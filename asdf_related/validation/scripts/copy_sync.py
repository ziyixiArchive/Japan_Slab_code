from glob import glob
from os.path import join, basename
import subprocess

mapper = {
    "201104291312484": "201104291312A",
    "201105101526088": "201105101526A",
    "201105221642234": "201105221642A",
    "201106222150572": "201106222150A",
    "201108011458146": "201108011458A",
    "201110210802390": "201110210802A",
    "201111241025376": "201111241025A",
    "201201010528014": "201201010527A",
    "201202260617243": "201202260617A",
    "201203121232496": "201203121232A",
    "201206092100193": "201206092100A",
    "201206240759355": "201206240759A",
    "201207091925080": "201207091925A",
    "201208080711021": "201208080711A",
    "201303290501115": "201303290501A",
    "201311222204260": "201311222204A",
    "201504150739292": "201504150739A",
    "201507030643244": "201507030643A",
    "201510160638285": "201510160638A",
    "201601201713146": "201601201713A",
    "201605030000537": "201605030000A",
    "201605110115497": "201605110115A",
    "201607251511575": "201607251511A",
    "201608041624382": "201608041624A",
    "201608241034583": "201608241034A",
    "201609121132570": "201609121132A",
    "201712091514280": "201712091514A",
    "201802112314201": "201802112314A",
    "201805101802310": "201805101802A",
    "201806172258378": "201806172258A"
}

all_models = ["crust1_stw105_processed",
              "EARA2014_nosmooth_crust2.0_processed",
              "EARA2014_nosmooth_processed",
              "EARA2014_smooth_crust2.0_processed",
              "EARA2014_smooth_processed",
              "FWEA18_nosmooth_processed",
              "FWEA18_smooth_processed",
              "hybrid_processed",
              "s362ani_processed"]

from_dir = "/mnt/scratch/xiziyi/process_sync_validation"
to_dir = "/mnt/scratch/xiziyi/validation/sync"
process_flags = ["preprocessed_10s_to_120s",
                 "preprocessed_20s_to_120s", "preprocessed_40s_to_120s"]

for each_model in all_models:
    command = f"mkdir -p {join(to_dir,each_model)}"
    subprocess.call(command, shell=True)
    for raw_key in mapper:
        gcmtid = mapper[raw_key]
        for each_process_flag in process_flags:
            from_path = join(from_dir, each_model,
                             f"{raw_key}.{each_process_flag}.h5")
            to_path = join(to_dir, each_model,
                           f"{gcmtid}.{each_process_flag}.h5")
            command = f"cp {from_path} {to_path}"
            subprocess.call(command, shell=True)
