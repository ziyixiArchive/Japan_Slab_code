from slurmpy import Slurm

# paths and constant values
nproc_old = 336  # number of processors used in bin files
old_mesh_dir = "/work/05880/tg851791/stampede2/model/FWEA18_ref"  # the mesh files
old_model_dir = "/work/05880/tg851791/stampede2/model/FWEA18_smooth"  # the model files
model_tags = "vpv,vph,vsv,vsh,eta,qmu,rho"  # vlues to generate
output_file = "/work/05880/tg851791/stampede2/model/FWEA18_ppm"  # output directory
# region as lon1/lat1/lon2/lat2/dep1/dep2 (eg: if lon1=30, lon2=20, get points like 30, 29, ...)
region = "90/10/150/60/0/805.232"
npts = "201/241/119"  # number of poins, including the edge points.
# use 18*18 cores, can be set anyway you like. (two directions, divide subregions)
nproc = "18/18"

command = "date;"
# check if ../../specfem_gll.jl/src/program/get_ppm_model.jl is actually the path of get_ppm_model.jl
command += f"ibrun julia ../../specfem_gll.jl/src/program/get_ppm_model.jl --nproc_old {nproc_old} --old_mesh_dir {old_mesh_dir} --old_model_dir {old_model_dir} --model_tags {model_tags} --output_file {output_file} --region {region} --npts {npts} --nproc {nproc};"
command += "date;"

# run 2h18min for my region, 60d*60d, 336*336NEX 21*21 proc. It's safe to set a longer time.
s = Slurm("interp", {"partition": "skx-normal",
                     "nodes": 10, "ntasks": 324, "time": "03:00:00", "account": "TG-EAR130011"})

s.run(command)
