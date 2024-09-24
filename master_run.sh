#!/bin/bash

#SBATCH -J CO2_TraPPE_Flexible_NPT
#SBATCH -t 5-00:00:00
#SBATCH -p genoa
#SBATCH -N 1
#SBATCH --ntasks=192
##SBATCH --mem=336G
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=d.raju@tudelft.nl

module load 2022
module load OpenMPI/4.1.4-GCC-11.3.0

export I_MPI_PMI_LIBRARY=/cm/shared/apps/slurm/current/lib64/libpmi2.so

folder="CO2_TRAPPE"
src="src"
specie="CO2"
lmp=~/Software/lammps/src/
directory=$(pwd)
temperature=("300") 
pressure=("120" "140" "160" "180" "200")
block=1
sim=1

for T in ${temperature[@]}
do  
    for P in ${pressure[@]}
    do	
        for ((i=1; i<=block; i++))
        do  
            for ((j=1; j<=sim; j++))
            do
                fold="$folder/T_${T}_P_${P}/block_${i}/sim_${j}"
                if [ -d "${fold}" ]; then
                    cd ${fold}
                    srun --ntasks=36 --nodes=1 --cpus-per-task=1 --mem-per-cpu=2000 $lmp/lmp_mpi < simulation.in > slurm.out &
                    echo ${SLURM_STEPID}
                    cd -
                else
                    echo "Directory ${fold} does not exist!"
                fi
            done
        done
    done
done
wait
