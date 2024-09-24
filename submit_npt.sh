#!/bin/bash

#SBATCH -J NPT_CO2-RIGID
#SBATCH -t 5-00:00:00
#SBATCH -p genoa
#SBATCH -N 3
#SBATCH --ntasks=576
#SBATCH --mem=336G
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=d.raju@tudelft.nl

module load 2022
module load OpenMPI/4.1.4-GCC-11.3.0

export I_MPI_PMI_LIBRARY=/cm/shared/apps/slurm/current/lib64/libpmi2.so

folder="CO2_TRAPPE_F"
src="src"
specie="CO2"
lmp=~/Software/lammps/src/
directory=$(pwd)
temperature=("300") # in Kelvin
pressure=("83" "107" "233")  # in bar


for T in ${temperature[@]}
do  
    # echo "1st loop"
    for P in ${pressure[@]}
    do	
        # echo "2st loop"
        if [ $P -eq 233 ]; then
            block=4
            sim=2
        else    
            block=5
            sim=2
        fi
        for ((i=1; i<=block; i++))
        do  
            echo "$T"
            echo "$P"
            echo "$block"
            for ((j=1; j<=sim; j++))
            do
                fold="$folder/T_${T}_P_${P}/block_${i}/sim_${j}"
                if [ -d "${fold}" ]; then
                    cd ${fold}
                    srun --ntasks=12 --nodes=1 --cpus-per-task=1 --mem-per-cpu=2000 $lmp/lmp_mpi < simulation.in > slurm.out &
                    cd -
                else
                    echo "Directory ${fold} does not exist!"
                fi
            done
        done
    done
done
wait
