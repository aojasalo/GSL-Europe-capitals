# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 11:23:39 2023

@author: Amanda Ojasalo
"""

import pandas as pd

"""

This script cleans and combines the urban-rural gradient results from QGIS models. 

"""

# reading the city list
data = pd.read_csv('C:/Users/amand/Documents/GRADU/dokumentit/Europe_capitals.csv', sep=';')
cities = data['City'].tolist()

# defining paths for the data
dlt_path = 'C:/Users/amand/Documents/GRADU/Data/results/DLT-results/' 
gsl_path = 'C:/Users/amand/Documents/GRADU/Data/results/GSL-buffer-results/' 
temp_path = 'C:/Users/amand/Documents/GRADU/Data/results/temperature-results/'
lc_path = 'C:/Users/amand/Documents/GRADU/Data/results/land-cover-results/'

# iterating over the cities            
for city in cities:    
        # open all files
        dlt = pd.read_csv(dlt_path + city + '-DLT-results.csv', encoding = 'unicode_escape')
        gsl = pd.read_csv(gsl_path + city + '-GSL-results.csv') #, encoding = 'unicode_escape')
        temp = pd.read_csv(temp_path + city + '-LST-results.csv')
        lc = pd.read_csv(lc_path + city + '-landcover-results.csv', encoding = 'unicode_escape')
        
        # select only necessary cols
        gsl = gsl[['ringId', '_mean', '_median', '_stdev', '_min', '_max']]
        temp = temp[['ringId', '_mean']]
        lc = lc[['Landuse-class','area_percent','buffer1area_percent',
                 'buffer2area_percent','buffer3area_percent','buffer4area_percent',
                 'buffer5area_percent','buffer6area_percent','buffer7area_percent',
                 'buffer8area_percent','buffer9area_percent','buffer10area_percent']]
        
        # fill nan with 0 (urban area rind id)
        gsl = gsl.fillna(0).sort_values('ringId').reset_index(drop=True)
        temp = temp.fillna(0).sort_values('ringId').reset_index(drop=True)
        
        # rename cols
        gsl = gsl.rename(columns={'_mean': 'GSL_mean','_median': 'GSL_median','_min': 'GSL_min','_max': 'GSL_max','_stdev': 'GSL_stdev',})
        temp = temp.rename(columns={'_mean': 'MAT_2017-2021'})
        
        # transpose the lc dataframe (it's in the wrong form) and rename cols
        lc = lc.transpose()
        lc.columns = lc.iloc[0]
        lc = lc.drop(lc.index[0])
        lc = lc.rename(columns={2:'urban_fabric_2',1:'urban_fabric_1',5:'other',3:'agricultural',4:'natural_vegetation'})
        lc['ringId'] = [0,1,2,3,4,5,6,7,8,9,10]

        # all dataframe
        d = pd.merge(gsl, dlt, how='left') # gsl and dlt
        d = pd.merge(d, temp, how='left') # result and temp
        d = pd.merge(d, lc, how='left') # result and lc
               
        # drop unnecessary cols
        d = d.drop(['Unnamed: 0'], axis=1)
        #print(d)
        
        # save to file
        d.to_csv('C:/Users/amand/Documents/GRADU/Data/results/combined-buffer-results/' + city + '-buffer-results.csv')
