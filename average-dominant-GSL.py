# -*- coding: utf-8 -*-
"""
Created on Mon May 29 12:02:28 2023

@author: Amanda Ojasalo
"""

import gc
import xarray as xr
import pandas as pd

"""

This script selects the longer season from the two potential seasons from the Copernicus HR-VPP GSL data
and calculates the average GSL for 2017-2021 for each European capital city.

"""

cities = pd.read_csv('C:/Users/amand/Documents/GRADU/Europe_capitals.csv', sep=';') # city list
cities = cities['City'].tolist()

# iterate every city
for city in cities:
    fp = 'C:/Users/amand/Documents/GRADU/Data/GSL_data/' + city + '/mosaic_output/' # GSL mosaic fp
    
    array_list = [] # list where to append annual files 
    index = ['2017','2018','2019','2020','2021'] # years
        
    # open the annual files, both seasons for each year
    for i in index:
        s1 = xr.open_dataarray(fp + '/GSL_mosaic_' + city + '_' + i + '_s1', engine='rasterio', chunks='auto') # read in chunks
        s2 = xr.open_dataarray(fp + '/GSL_mosaic_' + city + '_' + i + '_s2', engine='rasterio', chunks='auto') # read in chunks
        
        # fill nan with 0 to select the dominant season (if nan, there's no second season)
        s1 = s1.fillna(0)
        s2 = s2.fillna(0)

        #print(s1.compute(), s2.compute())
        
        # select the dominant season
        s12 = xr.where(s1 >= s2, s1, s2)
        s12 = s12.where(s12 != 0) # convert 0 back to nan
        
        # delete stuff for memory increace
        del s1, s2
        
        array_list.append(s12) # append to array list
           
    # create a dict and a xarray dataset from the arrays
    datadict = {index[i]: array_list[i] for i in range(len(index))}
    dataset = xr.Dataset(data_vars=datadict)
    #print(dataset)
    
    del s12
    del array_list
    del datadict
    gc.collect()
    
    # compute the mean of the years
    mean = dataset.to_array(dim='mean').mean('mean')
    mean_values = mean.compute() # compute from chunks

    # save the mean for each capital
    mean_values.rio.to_raster('C:/Users/amand/Documents/GRADU/Data/GSL_data/GSL_dominant_average_2017-2021_' + city + '.tif')

    del mean
    del mean_values
    del dataset
    gc.collect()
    
    print(city, 'done')

    