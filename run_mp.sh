#!/bin/bash

folder="CO2_TRAPPE"
src="src"
specie="CO2"
temperature=("300") # in Kelvin
pressure=("120" "140" "160" "180" "200")
block=1
sim=1


module load 2022
module load OpenMPI/4.1.4-GCC-11.3.0

export I_MPI_PMI_LIBRARY=/cm/shared/apps/slurm/current/lib64/libpmi2.so

for T in ${temperature[@]}
do
    for P in ${pressure[@]}
    do
        for ((i=1; i<=block; i++))
        do
            for ((j=1; j<=sim; j++))
            do

                fold="$folder/T_${T}_P_${P}/block_${i}/sim_${j}"

                cp src/mp.in ${fold}/.

            done
        done
    done
done