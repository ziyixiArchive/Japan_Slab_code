import MPI
MPI.Init()

comm = MPI.COMM_WORLD
rank=MPI.Comm_rank(comm)

a=zeros(2)
a.=rank

result=MPI.Gather(a,0,comm)

if rank==0
    @info result
end

MPI.Finalize()