# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 12:07:09 2023

@author: Amanda Ojasalo
"""

import xarray as xr

"""

This script calculates multi-year mean annual LST from MODIS MOD11A2.061 data 2017-2021.

"""

# open data (the whole study area in one file)
d = xr.open_dataset('C:/Users/amand/Documents/GRADU/Data/temperature/MOD11A2.061_1km_aid0001.nc')

# resample the 8-day averages into monthly averages
d_monthly = d.resample(time='1M').mean('time', skipna=True)
print(d_monthly)

# resample the monthly averages into annual averages
d_annual = d_monthly.resample(time='1Y').mean('time', skipna=True)
print(d_annual)

# drop year 2016 as its there for some reason
d_annual = d_annual.sel(time=slice('2017-01-01', '2022-01-01'))
print(d_annual)

# resample to 2017-2021 average
d_final = d_annual.mean('time', skipna=True)
print(d_final)

# kelvin to celsius
d_final = d_final.LST_Day_1km - 273.15

# save
d_final.to_netcdf('C:/Users/amand/Documents/GRADU/Data/temperature/MODIS-LST-avg-2017-2021.nc')
