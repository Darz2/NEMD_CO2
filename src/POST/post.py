#!/usr/bin/env python

################### import packages ################

import os
import numpy as np
import pandas as pd
import subprocess
import openpyxl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
plt.style.use('fivethirtyeight')
from sklearn.metrics import r2_score

################# julia preprocessing ###############

julia_run = "julia clean_data.jl"
subprocess.run(julia_run, shell=True, check=True)

##### Function to reshape and convet it to desired dataframe ######

def reshape_conv(array, samp_sets, layers):
    """
    Reshapes an array and converts it to a pandas DataFrame with column headings based on the number of layers.
    
    Parameters:
    - array: numpy array to be reshaped and converted.
    - samp_sets: number of sample sets (rows) in the reshaped array.
    - layers: number of layers (columns) in the reshaped array.
    
    Returns:
    - DataFrame: a pandas DataFrame with the reshaped data.
    """
    reshape_array = np.reshape(array, (int(samp_sets), int(layers)))
    columns = [str(i+1) for i in range(int(layers))]
    df = pd.DataFrame(reshape_array, columns=columns)
    return df

############ Function for linear fit ####################

def linear_fit(x, m, c):
  return m * x + c

############# Function for marker face color #############

def fade(color, alpha):
    rgba = mcolors.to_rgba(color)
    return (rgba[0], rgba[1], rgba[2], alpha)

####################### MAIN CODE ########################
################### MODIFICATION SPACE ################### 

layers  = 20
samp_interval = int(4000)
n = 2000

thermal_data = pd.read_csv("thermal.csv", delimiter=",")
massdens_data = pd.read_csv("massdens.csv", delimiter=",")
numdens_data = pd.read_csv("numdens.csv", delimiter=",")
MP_data = pd.read_table("../Muller_Plathe.out", delim_whitespace=True)

x_length = MP_data.iloc[0,-4]       # Angstrom
y_length = MP_data.iloc[0,-3]       # Angstrom
z_length = MP_data.iloc[0,-2]       # Angstrom

z_interval = np.linspace(0.025, 0.975, 20)
z_spacings = z_interval * z_length

# print(MP_data.shape)
# print(MP_data.columns)
# print(MP_data['#'])
time_step = MP_data["Step"].to_numpy()
# print(time_step)
heat_flux_array = MP_data["KE_diff"].to_numpy()

temp_layers = thermal_data['Column3'].to_numpy()
numdens_layers = numdens_data['Column2'].to_numpy()
massdens_layers = massdens_data['Column2'].to_numpy()
num_particles = thermal_data['Column2'].to_numpy()

total_time = int((len(temp_layers))/layers)*samp_interval
samp_sets = int(total_time/samp_interval)

print("Total time in fs = ", total_time)
print("Number of sample sets = ", samp_sets)

################### Reshaped dataframes ################################

temperature = reshape_conv(temp_layers,samp_sets,layers)
particles_layers = reshape_conv(num_particles,samp_sets,layers)
number_density = reshape_conv(numdens_layers,samp_sets,layers)
mass_density = reshape_conv(massdens_layers,samp_sets,layers)

################### To write all the data into a single excel file (comment it out if not necessary) ################################

# with pd.ExcelWriter('MP_post.xlsx') as writer:
#     temperature.to_excel(writer, sheet_name='Temperature', index=False)
#     particles_layers.to_excel(writer, sheet_name='Particles_Layers', index=False)
#     number_density.to_excel(writer, sheet_name='Number_Density', index=False)
#     mass_density.to_excel(writer, sheet_name='Mass_Density', index=False)

################### To Remove the processed csv files ################################

remove = "rm *.csv"
subprocess.run(remove, shell=True, check=True)

################## Plotting script to plot KE-Transfers #############################

plt.plot(time_step*1e-6, heat_flux_array,label='RNEMD with $W$ = $200 \; fs$')
plt.xlabel('Time [ns]')
plt.ylabel('KE [Kcal mol$^{-1}$]')
# plt.title('KE - Transfer')
plt.legend(loc="upper left")
plt.savefig('heat_flux_plot.png', dpi=300, bbox_inches='tight')
plt.cla()

################## TEMPERATURE GRADIENT calculation #############################

temperature = temperature.to_numpy()
nrows = temperature.shape[0]
ave_temp = temperature[0:nrows-1,0:20].mean(axis =0)
ave_temp_slope = ave_temp[1:10,]
z_slope = z_spacings[1:10,]    # multiplying by 0.1 to convert from Angstrom to nm
# print("Gradient_points-y :", ave_temp_slope)
# print("Gradient_points-x :", z_slope)

#Least-square fit
m, c = np.linalg.lstsq(np.vstack([z_slope, np.ones(len(z_slope))]).T, ave_temp_slope, rcond=None)[0]
r_squared = r2_score(ave_temp_slope, linear_fit(z_slope, m, c))
dT_dz = m

#Linear fit
z_slope_fit = np.linspace(min(z_slope), max(z_slope), 100)
ave_temp_fit = linear_fit(z_slope_fit, m, c)

######## Total Number, Number Density, Mass Density calculation #########

# Number of Particles
particles = particles_layers.to_numpy()
ave_particles = particles[0:nrows-1,0:20].mean(axis =0)

# Number Density
num_dens = number_density.to_numpy()
ave_num_dens = num_dens[0:nrows-1,0:20].mean(axis =0)

# Mass Density
mass_dens = mass_density.to_numpy()
ave_mass_dens = mass_dens[0:nrows-1,0:20].mean(axis =0)
Density = np.mean(ave_mass_dens)

################## Plotting script for TEMPERATURE GRADIENT #########################

fig,ax = plt.subplots()
ax.plot(z_spacings*0.1, ave_temp,'s',color='#00ff01', markeredgecolor='g', markeredgewidth=1.5, lw = 2,label='$W$ = $200 \; fs$')
ax.plot(z_slope_fit*0.1, ave_temp_fit,'-',color='#00ff01', lw = 2, label=f'Linear Fit ($r^{2}$ = {r_squared:.2f})')
ax.plot()
plt.xlabel('Z / [nm]')
plt.ylabel('$T$ / [K]')
# plt.title('Temperature - Gradient')
plt.legend(loc="lower center")
 
with open('temp_gradient.dat', 'w') as file:
    file.write('z_spacings ave_temp z_slope_fit ave_temp_fit\n')
    for z, temp, z_fit, temp_fit in zip(z_spacings, ave_temp, z_slope_fit, ave_temp_fit):
        file.write(f'{z:.2f} {temp:.2f} {z_fit:.2f} {temp_fit:.2f}\n')
         
tick_positions = []
for i in z_spacings:
    tick_positions.append(i*0.1)
    ax.axvline(i*0.1, color='k', lw=2, alpha=0.2)
    
ax.axvline(z_spacings[0]*0.1, color='b', lw=2, alpha=1)
ax.axvline(z_spacings[1]*0.1, color='b', lw=2, alpha=1)

ax.axvline(z_spacings[9]*0.1, color='r', lw=2, alpha=1)
ax.axvline(z_spacings[10]*0.1, color='r', lw=2, alpha=1)

cold = z_spacings * 0.1
mask = (cold >= z_spacings[0]*0.1) & (cold <= z_spacings[1]*0.1)
ax.fill_between(cold, min(ave_temp)-100, max(ave_temp)+100 ,where=mask, color='blue', alpha=0.25)

hot = z_spacings * 0.1
mask = (hot >= z_spacings[9]*0.1) & (hot <= z_spacings[10]*0.1)
ax.fill_between(hot, min(ave_temp)-100, max(ave_temp)+100 ,where=mask, color='red', alpha=0.25)

for spine in ax.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(1.75)  

secax = ax.secondary_xaxis('top')
secax.set_xticks(z_spacings * 0.1)
secax.set_xticklabels([f'{x*0.1:.1f}' for x in z_spacings], fontsize=8, rotation=70)
    
ax.tick_params(axis='both', colors='black' , size=10)
ax.xaxis.set_tick_params(width=2)
ax.yaxis.set_tick_params(width=2)
secax.xaxis.set_tick_params(width=2)

ax.set_ylim([min(ave_temp)-100, max(ave_temp) + 100])

legend = ax.legend(frameon=True, loc="upper right", edgecolor='black')
frame = legend.get_frame()
frame.set_linewidth(2)
legend_texts = legend.get_texts()
for text in legend_texts:
  text.set_fontsize(12)
ax.grid(False)

plt.savefig('temp_gradient.png', dpi=300, bbox_inches='tight')
plt.cla()

################## THERMAL CONDUCTIVITY CALCULATION #########################

avagadro_number = 6.02214076e23         # mol-1
dt = total_time                         # fs
dt_s = dt*1e-15                         # s
area = (x_length*x_length)*1e-20        # m^2
KE = heat_flux_array[-1]                # kcal/mol
KE_j = (KE*4184)/avagadro_number        # jolue
heat_flux = KE_j/(2*area*dt_s)          # in W/m2
dT_dz = dT_dz/1e-10                     # K/m
kappa = heat_flux/dT_dz
print("Density in kg/m3 = {:.4f}".format(Density*1e3))
print("Heat-Flux in W/m2 = {:.4e}".format(heat_flux))
print("dT/dz in K/m = {:.4e}".format(dT_dz))
print("R2 = {:.4f}".format(r_squared))
print("Thermal conductivity in mW/mK = {:.4f}".format(kappa*1e3))
freq = 160 # in fs

file_path = '../../thermal_conductivity.dat'
if not os.path.exists(file_path):
    with open(file_path, 'w') as file:
        file.write('Frequency-[fs] Density-[Kg/m3] Heat_flux-[W/m2] dT/dz-[K/m] R2 Kappa\n')

with open(file_path, 'a') as file:
    file.write(f'{freq:.2f} {Density*1e3:.2f} {heat_flux:.2f} {dT_dz:.2f} {r_squared:.2f} {kappa*1e3:.4f}\n')


################## Plotting script for number of particles #########################

fig,ax = plt.subplots()
c='#272727'
ax.plot(z_spacings*0.1, ave_particles, marker='o', linestyle='-', markeredgecolor=c, markerfacecolor=fade(c, 0.6),
 color = c, markeredgewidth=1.5, lw = 2,label=fr'$W$ = ${n} \; fs$')

with open('number_layers.dat', 'w') as file:
    file.write('z_spacings ave_particles\n')
    for z, i in zip(z_spacings, ave_particles):
        file.write(f'{z:.2f} {i:.2f}\n')

ax.plot()
plt.xlabel('Z / [nm]')
plt.ylabel('Number of Molecules / [-]')
plt.legend(loc="lower center")
  
tick_positions = []
for i in z_spacings:
    tick_positions.append(i*0.1)
    ax.axvline(i*0.1, color='k', lw=2, alpha=0.2)
    
ax.axvline(z_spacings[0]*0.1, color='b', lw=2, alpha=1)
ax.axvline(z_spacings[1]*0.1, color='b', lw=2, alpha=1)

ax.axvline(z_spacings[9]*0.1, color='r', lw=2, alpha=1)
ax.axvline(z_spacings[10]*0.1, color='r', lw=2, alpha=1)

cold = z_spacings * 0.1
mask = (cold >= z_spacings[0]*0.1) & (cold <= z_spacings[1]*0.1)
ax.fill_between(cold, min(ave_particles)-10, max(ave_particles)+10 ,where=mask, color='blue', alpha=0.25)

hot = z_spacings * 0.1
mask = (hot >= z_spacings[9]*0.1) & (hot <= z_spacings[10]*0.1)
ax.fill_between(hot, min(ave_particles)-10, max(ave_particles)+10 ,where=mask, color='red', alpha=0.25)

for spine in ax.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(1.75)  

secax = ax.secondary_xaxis('top')
secax.set_xticks(z_spacings * 0.1)
secax.set_xticklabels([f'{x*0.1:.1f}' for x in z_spacings], fontsize=8, rotation=70)
    
ax.tick_params(axis='both', colors='black' , size=10)
ax.xaxis.set_tick_params(width=2)
ax.yaxis.set_tick_params(width=2)
secax.xaxis.set_tick_params(width=2)

ax.set_ylim([min(ave_particles)-10, max(ave_particles) + 10])

legend = ax.legend(frameon=True, loc="upper right", edgecolor='black')
frame = legend.get_frame()
frame.set_linewidth(2)
legend_texts = legend.get_texts()
for text in legend_texts:
  text.set_fontsize(12)
ax.grid(False)

plt.savefig('number_layers.png', dpi=300, bbox_inches='tight')
plt.cla()

################## Plotting script for Number-density #########################

fig,ax = plt.subplots()
c='#272727'
ax.plot(z_spacings*0.1, ave_num_dens, marker='o', linestyle='-', markeredgecolor=c, markerfacecolor=fade(c, 0.6),
 color = c, markeredgewidth=1.5, lw = 2,label='$W$ = $200 \; fs$')

with open('num_density.dat', 'w') as file:
    file.write('z_spacings ave_num_dens\n')
    for z, i in zip(z_spacings, ave_num_dens):
        file.write(f'{z:.8f} {i:.8f}\n')
        
ax.plot()
plt.xlabel('Z / [nm]')
plt.ylabel('Number density / [m$^{-3}$]')
plt.legend(loc="lower center")
  
tick_positions = []
for i in z_spacings:
    tick_positions.append(i*0.1)
    ax.axvline(i*0.1, color='k', lw=2, alpha=0.2)
    
ax.axvline(z_spacings[0]*0.1, color='b', lw=2, alpha=1)
ax.axvline(z_spacings[1]*0.1, color='b', lw=2, alpha=1)

ax.axvline(z_spacings[9]*0.1, color='r', lw=2, alpha=1)
ax.axvline(z_spacings[10]*0.1, color='r', lw=2, alpha=1)

cold = z_spacings * 0.1
mask = (cold >= z_spacings[0]*0.1) & (cold <= z_spacings[1]*0.1)
ax.fill_between(cold, min(ave_num_dens)-10*1e-3, max(ave_num_dens)+10*1e-3 ,where=mask, color='blue', alpha=0.25)

hot = z_spacings * 0.1
mask = (hot >= z_spacings[9]*0.1) & (hot <= z_spacings[10]*0.1)
ax.fill_between(hot, min(ave_num_dens)-10*1e-3, max(ave_num_dens)+10*1e-3 ,where=mask, color='red', alpha=0.25)

for spine in ax.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(1.75)  

secax = ax.secondary_xaxis('top')
secax.set_xticks(z_spacings * 0.1)
secax.set_xticklabels([f'{x*0.1:.1f}' for x in z_spacings], fontsize=8, rotation=70)
    
ax.tick_params(axis='both', colors='black' , size=10)
ax.xaxis.set_tick_params(width=2)
ax.yaxis.set_tick_params(width=2)
secax.xaxis.set_tick_params(width=2)

ax.set_ylim([min(ave_num_dens)-10*1e-3, max(ave_num_dens) + 10*1e-3])

legend = ax.legend(frameon=True, loc="upper right", edgecolor='black')
frame = legend.get_frame()
frame.set_linewidth(2)
legend_texts = legend.get_texts()
for text in legend_texts:
  text.set_fontsize(12)
ax.grid(False)

plt.savefig('number_density.png', dpi=300, bbox_inches='tight')
plt.cla()

################## Plotting script for mass-density #########################

fig,ax = plt.subplots()
c='#272727'
ax.plot(z_spacings*0.1, ave_mass_dens, marker='o', linestyle='-', markeredgecolor=c, markerfacecolor=fade(c, 0.6),
 color = c, markeredgewidth=1.5, lw = 2,label='$W$ = $200 \; fs$')

with open('mass_density.dat', 'w') as file:
    file.write('z_spacings ave_mass_dens\n')
    for z, i in zip(z_spacings, ave_mass_dens):
        file.write(f'{z:.4f} {i:.4f}\n')
        
ax.plot()
plt.xlabel('Z / [nm]')
plt.ylabel('mass density / [g cm$^{-3}$]')
plt.legend(loc="lower center")
  
tick_positions = []
for i in z_spacings:
    tick_positions.append(i*0.1)
    ax.axvline(i*0.1, color='k', lw=2, alpha=0.2)
    
ax.axvline(z_spacings[0]*0.1, color='b', lw=2, alpha=1)
ax.axvline(z_spacings[1]*0.1, color='b', lw=2, alpha=1)

ax.axvline(z_spacings[9]*0.1, color='r', lw=2, alpha=1)
ax.axvline(z_spacings[10]*0.1, color='r', lw=2, alpha=1)

cold = z_spacings * 0.1
mask = (cold >= z_spacings[0]*0.1) & (cold <= z_spacings[1]*0.1)
ax.fill_between(cold, min(ave_mass_dens)-0.1, max(ave_mass_dens)+0.1 ,where=mask, color='blue', alpha=0.25)

hot = z_spacings * 0.1
mask = (hot >= z_spacings[9]*0.1) & (hot <= z_spacings[10]*0.1)
ax.fill_between(hot, min(ave_mass_dens)-0.1, max(ave_mass_dens)+0.1 ,where=mask, color='red', alpha=0.25)

for spine in ax.spines.values():
    spine.set_edgecolor('black')
    spine.set_linewidth(1.75)  

secax = ax.secondary_xaxis('top')
secax.set_xticks(z_spacings * 0.1)
secax.set_xticklabels([f'{x*0.1:.1f}' for x in z_spacings], fontsize=8, rotation=70)
    
ax.tick_params(axis='both', colors='black' , size=10)
ax.xaxis.set_tick_params(width=2)
ax.yaxis.set_tick_params(width=2)
secax.xaxis.set_tick_params(width=2)

ax.set_ylim([min(ave_mass_dens)-0.1, max(ave_mass_dens) + 0.1])

legend = ax.legend(frameon=True, loc="upper right", edgecolor='black')
frame = legend.get_frame()
frame.set_linewidth(2)
legend_texts = legend.get_texts()
for text in legend_texts:
  text.set_fontsize(12)
ax.grid(False)

plt.savefig('mass_density.png', dpi=300, bbox_inches='tight')
plt.cla()