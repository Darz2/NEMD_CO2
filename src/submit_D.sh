#!/bin/bash
#SBATCH --job-name=EPM2_F1_NPT_T_TEMP_P_PRESS_B_BLOCK_S_SIM
#SBATCH -n 4
#SBATCH -t 5-00:00:00
#SBATCH --mem-per-cpu=1G
#SBATCH --mail-type=ALL
#SBATCH --mail-user=d.raju.tudelft.nl
#SBATCH --account=research-me-pe

module load 2023r1-gcc11
module load openmpi/4.1.4

lmp=~/Software/LAMMPS/mylammps/src/
srun $lmp/lmp_mpi < in.ALL
wait
