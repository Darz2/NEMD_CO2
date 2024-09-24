#!/usr/bin/env python

import sys
import CoolProp.CoolProp as CP
import numpy as np
from molmass import Formula
    
CP.set_config_string(CP.ALTERNATIVE_REFPROP_PATH, f'~/Software/REFPROP/REFPROP-cmake/build')

Temperature = int(sys.argv[1])
Pressure = int(sys.argv[2])
specie = sys.argv[3]

formula = Formula(specie)
molar_mass = formula.mass
# Temperature = 300
# Pressure = 200
# specie = 'CO2'

# print(Temperature)
# print(Pressure)
# print(specie)
# print(type(Temperature))
# print(type(Pressure))
# print(type(specie))

Density_RP = CP.PropsSI('D', 'T',Temperature, 'P', Pressure*1e5, specie)
Density_RP = Density_RP/molar_mass  # in mol/L
print(f"{Density_RP:.0f}")
