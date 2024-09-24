#!/bin/bash
#SBATCH --job-name=NEMD_T_300_P_200
#SBATCH -p parallel-12
#SBATCH -n 2
#SBATCH --mem-per-cpu=2G
#SBATCH -t 6-00:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=d.raju.tudelft.nl

lmp=~/Software/lammps/src/
srun $lmp/lmp_mpi < simulation.in

wait