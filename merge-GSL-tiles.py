# -*- coding: utf-8 -*-
"""
Created on Mon May 22 11:06:52 2023

@author: Amanda Ojasalo
"""

import rasterio as rio
import pandas as pd
from rasterio.merge import merge
from pathlib import Path

"""
This script merges the Copernicus HR-VPP GSL data tiles into image mosaic for each European capital city.

"""

path = 'C:/Users/amand/Documents/GRADU/Data/' # path for the GSL files
cities = pd.read_csv('C:/Users/amand/Documents/GRADU/Europe_capitals.csv', sep=';') # country list
cities = cities['City'].tolist()

# define years, seasons and empty list for files
years = ['2017', '2018', '2019', '2020', '2021']
seasons = ['s1', 's2']
raster_mosaic = []

# iterate all cities
for city in cities:
    fp = Path(path + city + '/') # define city-specific fp
    
    raster_files = list(fp.iterdir()) # list files in folder
    
    if len(raster_files) > 10: # if there's more than 10 files in the folder, mosaic needs to be done 
        Path(str(fp) + '/mosaic_output').mkdir(parents=True, exist_ok=True) # create mosaic folder
        
        for year in years: # iterate years
            for season in seasons: # iterate seasons
                
                # select only the files where season and year is same
                selected_files = [r for r in raster_files if year in str(r) and season in str(r)]
                
                # open selected rasters and append to mosaic list
                for s in selected_files:
                    raster = rio.open(s)
                    raster_mosaic.append(raster)
                
                # merge selected files
                mosaic, output = merge(raster_mosaic)
                
                # assign metadata
                output_meta = raster.meta.copy()
                output_meta.update({"driver": "GTiff",
                                    "height": mosaic.shape[1],
                                    "width": mosaic.shape[2],
                                    "transform": output})
                
                # write the mosaic into folder
                with rio.open(str(fp) + '/mosaic_output/' + 'GSL_mosaic_' + city + '_' + year + '_' + season, "w", **output_meta) as m:
                    m.write(mosaic)
                    
                print(city, year, season, 'done') # print progress
                
                raster_mosaic = [] # empty the mosaic list
                                    