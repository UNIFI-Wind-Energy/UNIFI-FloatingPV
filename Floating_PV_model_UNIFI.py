
"""
Citation notice:

If you use this model, please cite:
F. Superchi, R. Travaglini and A. Bianchini, Renewable Energy, vol. 260, p. 125194, 2026.
"Critical issues for the deployment of floating offshore hybrid energy systems comprising wind and solar: a case study analysis for the Mediterranean Sea"
https://doi.org/10.1016/j.renene.2026.125194
"""

import pvlib
from pvlib import location
from pvlib import irradiance
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np


#%%

'user defined parameters'
tilt = 30                  # [°] change according to tilt of panels
surface_azimuth = 180      # [°] change according to surface orientation

tz = 'CET'         # time zone
lat = xx.xxxx      # latitude of installation in [°]
lon = xx.xxxx      # longitude of installation in [°]

# monofacial open structure free standing from https://doi.org/10.1016/j.apenergy.2020.116084
u_c = 31.9           # heat coeff. 1
u_v = 1.5            # heat coeff. 2

T_stc = 25           # °C temperature at STC
gamma = 0.004        # gamma coefficient linking temperature variation to efficiency variation https://doi.org/10.1016/j.heliyon.2022.e11896
eta_stc = 0.1649     # efficiency at STC of the panels https://doi.org/10.1016/j.apenergy.2020.116084

WIL = 1 - 10/100   # wave induced losses: 10%   from https://doi.org/10.1016/j.solener.2025.113439
HL = 1 - 6.6/100   # humidity losses: 6.6%      from 10.5455/jjee.204-1667584023

#%%
"""
USER INPUT REQUIRED: solar time series

download the solar timeseries from the NSRDB: National Solar Radiation Database
https://nsrdb.nrel.gov/data-viewer

suggested: TMY containing all attributes (DHI, DNI, GHI, wind speed at 2m, etc.)

"""

df_NREL = pd.read_csv('xxx.csv', skiprows=2)    #replace xxx with the name of the csv file

date = pd.date_range(start = 'xx-xx-xxxx', end = 'xx-xx-xxxx', freq='1h') #replace the xx with start and end date

#%%
'GHI, DNI and DHI comparison'
fig,ax = plt.subplots(figsize = (8,5))

ax.plot(df_NREL['GHI'], label = 'GHI', color = 'orange')
ax.plot(df_NREL['DNI'], label = 'DNI', color = 'skyblue')
ax.plot(df_NREL['DHI'], label = 'DHI', color = 'grey')

ax.set_xlabel('Time [h]')
ax.set_ylabel('Irradiance [W/$m^{2}$]')
ax.grid(alpha = 0.3)

ax.legend(ncol = 3, loc = 'upper center')

x_start = 1992
x_end = x_start + 24*14

ax.set_xlim(x_start, x_end)

#%%
'solar posizion'

site_location = location.Location(lat, lon, tz=tz)

df_years = df_NREL.loc[(df_NREL['Day'] == 1) & (df_NREL['Hour'] == 0)]
years = df_years['Year'].tolist()

months = df_years['Month'].tolist()

solar_position_avgy = pd.DataFrame()

for i in range(len(months)):
    if months[i] != 12:
        start = str(months[i]) + '-01-'+ str(years[i])
        end = str(months[i]+1) + '-01-'+ str(years[i])
        
    else:
        start = str(months[i]) + '-01-'+ str(years[i])
        end = '01-01-'+ str(years[i]+1)
    
    times = pd.date_range(start = start, end = end, inclusive = 'left', freq='1h', tz=site_location.tz)
        
    solar_position = site_location.get_solarposition(times=times)
    
    solar_position_avgy = pd.concat([solar_position_avgy, solar_position], axis = 0)
    
df_NREL['apparent_zenith'] = solar_position_avgy['apparent_zenith'].reset_index(drop=True)
df_NREL['azimuth'] = solar_position_avgy['azimuth'].reset_index(drop=True)

#%%
'solar angles plot'
fig,ax = plt.subplots(figsize = (8,5))

ax.plot(df_NREL['apparent_zenith'], label = 'Apparent zenith', color = 'black')
ax.plot(df_NREL['azimuth'], label = 'Azimuth', color = 'red')

ax.set_xlabel('Time [h]')
ax.set_ylabel('Angle [°]')
ax.grid(alpha = 0.3)

ax.legend(ncol = 3, loc = 'upper center')

x_start = 1992
x_end = x_start + 24*14

ax.set_xlim(x_start, x_end)


#%%

'Plane of Array (POA) calculation'
# Generate clearsky data using the Ineichen model, which is the default
# The get_clearsky method returns a dataframe with values for GHI, DNI, and DHI

# GHI and POA comparison similar to https://pvlib-python.readthedocs.io/en/latest/gallery/irradiance-transposition/plot_ghi_transposition.html#sphx-glr-gallery-irradiance-transposition-plot-ghi-transposition-py

clearsky = site_location.get_clearsky(times)


POA_irradiance_NREL = irradiance.get_total_irradiance(
                                                        surface_tilt=tilt,
                                                        surface_azimuth=surface_azimuth,
                                                
                                                        dni=df_NREL['DNI'],
                                                        ghi=df_NREL['GHI'],
                                                        dhi=df_NREL['DHI'],
                                                        
                                                        solar_zenith=df_NREL['apparent_zenith'],
                                                        solar_azimuth=df_NREL['azimuth']
                                                        )

POA_irradiance_NREL['temp_air'] = df_NREL['Temperature']
POA_irradiance_NREL['wind_speed'] = df_NREL['Wind Speed']

#%%
'POA global, POA direct and POA diffuse comparison'
fig,ax = plt.subplots(figsize = (8,5))

ax.plot(POA_irradiance_NREL['poa_global'], label = 'POA global', color = 'orange')
ax.plot(POA_irradiance_NREL['poa_direct'], label = 'POA direct', color = 'skyblue')
ax.plot(POA_irradiance_NREL['poa_diffuse'], label = 'POA diffuse', color = 'grey')

ax.set_xlabel('Time [h]')
ax.set_ylabel('Irradiance [W/$m^{2}$]')
ax.grid(alpha = 0.3)

ax.legend(ncol = 3, loc = 'upper center')

x_start = 1992
x_end = x_start + 24*14

ax.set_xlim(x_start, x_end)


#%%
'cell temperature T cell variation'

T_cell = pvlib.temperature.pvsyst_cell(
    poa_global=POA_irradiance_NREL['poa_global'],
    temp_air=POA_irradiance_NREL['temp_air'],
    wind_speed=POA_irradiance_NREL['wind_speed'],
    u_c = u_c,
    u_v = u_v
)

POA_irradiance_NREL['T cell'] = T_cell

#%%
'plots'
fig,ax = plt.subplots(figsize = (8,5))

ax.plot(T_cell, label = 'Cell temperature')
ax.plot(POA_irradiance_NREL['temp_air'], label = 'Air temperature')
ax.set_xlabel('Time [h]')
ax.set_ylabel('Temperature [°C]')
ax.grid(alpha = 0.3)

ax.legend(loc = 'lower left')

ax2 = ax.twinx()
ax2.plot(POA_irradiance_NREL['wind_speed'], label = 'wind speed', color = 'blue')
ax2.set_ylabel('Wind Speed [m/s]')
ax2.legend(loc = 'upper right')

x_start = 1992
x_end = x_start + 24*14

ax.set_xlim(x_start, x_end)

#%%
'temperatures'
fig, ax = plt.subplots(4,1, figsize = (8,6))

ax = plt.subplot2grid((4, 1), (0, 0), rowspan=2)
ax.plot(T_cell, label = 'Cell temperature')
ax.plot(POA_irradiance_NREL['temp_air'], label = 'Air temperature')
ax.set_xlabel('Time [h]')
ax.set_ylabel('Temperature [°C]')
ax.grid(alpha = 0.3)
ax.legend(ncol = 2, loc = 'upper right')

'wind speed'
ax2 = plt.subplot2grid((4, 1), (2, 0), rowspan=1)
ax2.plot(POA_irradiance_NREL['wind_speed'], label = 'wind speed', color = 'blue')
ax2.grid(alpha = 0.3)
ax2.set_ylabel('Wind Speed [m/s]')

'error normalized to the nominal power'
ax3 = plt.subplot2grid((4, 1), (3, 0), rowspan=1)
ax3.plot(POA_irradiance_NREL['poa_global'], label = 'wind speed', color = 'orange')
ax3.grid(alpha = 0.3)
ax3.set_ylabel('Irradiance [W/$m^{2}$]')

x_start = 1992
x_end = x_start + 24*14
ax.set_xlim(x_start, x_end)
ax2.set_xlim(x_start, x_end)
ax3.set_xlim(x_start, x_end)

fig.tight_layout()

#%%
'temperature effect on efficiency'

eta_list = []

for T in T_cell:
    eta = eta_stc * (1-gamma*(T-T_stc))
    eta_list.append(eta)

POA_irradiance_NREL['eta'] = eta_list
    
#%%
'Example of Power calculation'

P_installed = 1000   #kW

P_nom = 320  #Wp                monofacial PV module specifics from https://doi.org/10.1016/j.apenergy.2020.116084
A_nom = 1.983*0.994 #m2 
P_spec = P_nom / A_nom / 1000   # kW/m2   almost equal to efficiency

A = P_installed / P_spec #m2

G_list = POA_irradiance_NREL['poa_global'].to_list()    #W/m2

P_list = []
i = 0
for eta in eta_list:
    P = A * eta * G_list[i] / 1000   #kW
    i = i+1
    P_list.append(P)

POA_irradiance_NREL['power'] = P_list


#%%
'dataframe save'
POA_irradiance_NREL.to_csv('POA_irradiance_NREL.csv',sep = ';' )

#%%
'example plots'

fig_x = 10
fig_y = 2
x_start = 1992
x_end = x_start + 24*14

'irradiance plots'
fig,ax = plt.subplots(figsize = (fig_x,fig_y))

ax.plot(POA_irradiance_NREL['poa_global'], label = 'POA global', color = 'orange')
ax.plot(df_NREL['GHI'], label = 'GHI', color = 'grey')

ax.legend()

ax.set_xlabel('Time [h]')
ax.set_ylabel('Irradiance [W/$m^{2}$]')
ax.grid(alpha = 0.3)

ax.set_xlim(x_start, x_end)

'temperature plots'
fig,ax = plt.subplots(figsize = (fig_x,fig_y))

ax.plot(POA_irradiance_NREL['T cell'], label = 'Cell temperature', color = 'red')
ax.plot(POA_irradiance_NREL['temp_air'], label = 'Air temperature', color = 'skyblue')

ax.set_xlabel('Time [h]')
ax.set_ylabel('Temperature [°C]')
ax.grid(alpha = 0.3)
ax.legend()

ax.set_xlim(x_start, x_end)

'wind speed plots'
fig,ax = plt.subplots(figsize = (fig_x,fig_y))

ax.plot(POA_irradiance_NREL['wind_speed'], label = 'wind speed', color = 'blue')

ax.set_xlabel('Time [h]')
ax.set_ylabel('Wind speed [m/s]')
ax.grid(alpha = 0.3)
ax.set_xlim(x_start, x_end)

'efficiency plots'
fig,ax = plt.subplots(figsize = (fig_x,fig_y))

ax.plot(POA_irradiance_NREL['eta']*100, color = 'black') #, label = 'label')

ax.set_xlabel('Time [h]')
ax.set_ylabel('Efficiency [%]')
ax.grid(alpha = 0.3)

ax.set_ylim(15,17.5)
ax.set_xlim(x_start, x_end)


'power plots'
fig,ax = plt.subplots(figsize = (fig_x,fig_y))

ax.plot(POA_irradiance_NREL['power'], color = 'slateblue') #, label = 'label')

ax.set_xlabel('Time [h]')
ax.set_ylabel('Power [kW]')
ax.grid(alpha = 0.3)

ax.set_xlim(x_start, x_end)


#%%
'different power ratings computation'

df_out = pd.DataFrame()

df_out['Year']  = df_NREL['Year']
df_out['Month'] = df_NREL['Month']
df_out['Day']   = df_NREL['Day']
df_out['Hour']  = df_NREL['Hour']

G_list = POA_irradiance_NREL['poa_global'].to_list()    #W/m2

P_list_spec = []

P_list_WIL = []
P_list_HL = []

i = 0
for eta in eta_list:
    P_spec =  eta * G_list[i] / 1000   #kW/m2
    P_WIL = P_spec * WIL
    P_HL = P_WIL * HL
    i = i+1
    P_list_spec.append(P_spec)
    P_list_WIL.append(P_WIL)
    P_list_HL.append(P_HL)

df_out['P_spec'] = P_list_spec    #kW/m2
df_out['P_WIL'] = P_list_WIL    #kW/m2
df_out['P_WIL_HL'] = P_list_HL    #kW/m2


df_out.to_csv('df_PV_p_spec_WIL_HL.csv', sep = ';')





















