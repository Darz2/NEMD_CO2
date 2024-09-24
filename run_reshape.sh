#!/bin/bash

folder="CO2_TRAPPE_F"
src="src"
specie="CO2"
temperature=("300") # in Kelvin
pressure=("38" "50" "61" "83" "107" "233")  # in bar
size=("1000")
block=5
sim=2

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

                cp src/reshape.in           ./

                sed -i "s/T_VAL/${T}/g"      reshape.in  
                sed -i "s/P_VAL/${P}/g"      reshape.in  

                mv reshape.in                ${fold}

            done
        done
    done
done