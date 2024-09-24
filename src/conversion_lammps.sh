#!/bin/bash

# Define the Boltzmann constant (kcal/(mol·K))
boltzmann_constant=0.0019872041

# Get input temperature in Kelvin from the user
read -p "Enter Energy in Kelvin: " temperature_in_K

# Calculate the energy in kcal/mol
energy_in_kcal_per_mol=$(echo "scale=6; $temperature_in_K * $boltzmann_constant" | bc)

#echo "Temperature in Kelvin: $temperature_in_K K"
echo "Energy in kcal/mol: $energy_in_kcal_per_mol kcal/mol"