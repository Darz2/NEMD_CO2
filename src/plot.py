#!/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
plt.style.use('fivethirtyeight')

############ Function for linear fit ####################

def linear_regression(x, y):
  model = LinearRegression()
  model.fit(x.reshape(-1, 1), y)
  r_squared = model.score(x.reshape(-1, 1), y)
  slope = model.coef_[0]
  return slope, r_squared, model

MP_data = pd.read_table("Muller_Plathe_pr.out", delim_whitespace=True)
x_length = MP_data.iloc[0,-3]       # Angstrom
z_length = MP_data.iloc[0,-2]       # Angstrom

print(x_length)
print(z_length)
# x_length = 23.996905
# z_length = 159.97936
timestep = 0.5
z_interval = np.linspace(0.025, 0.975, 60)
z_spacings = z_interval * z_length

heat_flux_array = MP_data["Total_Heat_Flux"].to_numpy()
KE = heat_flux_array[-1]
avagadro_number = 6.02214076e23         # mol-1
KE_j = (KE*4184)/avagadro_number        # jolue
total_time = MP_data["Step"].to_numpy()
dt = total_time[-1]*timestep
print(dt)
dt_s = dt*1e-15                         # s
avagadro_number = 6.02214076e23         # mol-1
area = (x_length*x_length)*1e-20        # m^2
heat_flux = KE_j/(2*area*dt_s)          # in W/m2

data = pd.read_csv('thermal_pr.csv', delimiter=',', header=None)
temperature = data.to_numpy()
nrows = temperature.shape[0]
ncolumns = temperature.shape[1]
# print(ncolumns)
# print(nrows)
# print(temperature[1:nrows,0:ncolumns])
ave_temp = temperature[1:nrows,0:ncolumns].mean(axis =0)
# print(ave_temp)
# print(ave_temp[1:30,])
ave_temp_slope = ave_temp[1:int(ncolumns/2),]
z_slope = z_spacings[1:int(ncolumns/2),]
# ave_temp_slope = ave_temp[int((ncolumns/2)+2):ncolumns,]
# z_slope = z_spacings[int((ncolumns/2)+2):ncolumns,]
# print(ave_temp_slope)
# print(z_slope)

slope, r_squared, model = linear_regression(z_slope, ave_temp_slope)
dT_dz = slope/1e-10                     # K/m
# print(dT_dz)

kappa = heat_flux/dT_dz
print("Heat-Flux in W/m2 = {:.4e}".format(heat_flux))
print("dT/dz in K/m = {:.4e}".format(dT_dz))
print("R2 = {:.4f}".format(r_squared))
print("Thermal conductivity in mW/mK = {:.4f}".format(kappa*1e3)) 
# # print(temperature[1])
plt.scatter(z_spacings*0.1,ave_temp)
plt.plot(z_slope*0.1,  model.predict(z_slope.reshape(-1, 1)),'-',color='red', lw = 2, label=f'Fitted line ($R^{2}$ = {r_squared:.2f})')
# # x_tick = np.arange(1,21,1)
# # plt.xticks(x_tick)
plt.legend()
plt.ylabel("Temperature / [Kelvin]")
plt.xlabel("z / [nm]")
plt.tight_layout()
plt.savefig('temperature_gradient.png')
# plt.show()
