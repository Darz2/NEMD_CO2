#!/bin/bash
#SBATCH --job-name=EPM2_F1_NPT_T_TEMP_P_PRESS_B_BLOCK_S_SIM
#SBATCH -p parallel-12
#SBATCH -n 12
#SBATCH --mem-per-cpu=2G
#SBATCH -t 7-00:00:00
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=d.raju.tudelft.nl

lmp=~/Software/lammps/src/
srun $lmp/lmp_mpi < simulation.in

wait