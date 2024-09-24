#!/bin/bash

folder="CO2_TRAPPE"
src="src"
specie="CO2"
temperature=("300")
pressure=("120" "140" "160" "180" "200")
size=("2000")
iter=1
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
                seed=$(( $iter * 1000))
                fold="$folder/T_${T}_P_${P}/block_${i}/sim_${j}"

                if [ -d "$folder/T_${T}_P_${P}/block_${i}/sim_${j}" ]; then
                    rm -r ${fold}
                fi

                mkdir -p ${fold}
                mkdir ${fold}/init

                cp src/simulation.in                       ./
                cp src/Running_Density.py                  ./

                sed -i "s/T_VAL/${T}/g"                     simulation.in  
                sed -i "s/P_VAL/${P}/g"                     simulation.in  
                sed -i "s/R_VAL/${seed}/g"                  simulation.in 

                sed -i "s/T_VAL/${T}/g"                     Running_Density.py
                sed -i "s/P_VAL/${P}/g"                     Running_Density.py
                sed -i "s/MOLECULE_DEF/${specie}/g"         Running_Density.py

                mv simulation.in                            ${fold}
                mv Running_Density.py                       ${fold}

                cp src/CO2.xyz                              ${fold}/init
                cp src/params.ff                            ${fold}/init

                Density_RP=$(python REFPROP_input.py ${T} ${P} "${specie}") 
                wait
            
                echo "The density calculated by REFPROP is: $Density_RP"
                cd ${fold}/init

                ~/Software/fftool/fftool ${size} ${specie}.xyz -r $Density_RP    > /dev/null
                ~/Software/packmol-20.14.2/packmol < pack.inp > packmol.out
                ~/Software/fftool/fftool ${size} ${specie}.xyz -r $Density_RP -l > /dev/null

                sed -i '13,25d'                             ./data.lmp
                cp data.lmp ..

                cd -

                cd ${fold}
                rm -r init
                cd - 

                iter=$((iter+1))
            done
        done
    done
done