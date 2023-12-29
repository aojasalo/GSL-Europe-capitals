# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 10:29:43 2023

@author: Amanda Ojasalo
"""

import pandas as pd

"""

This script calculates the proportions of broadleaved dominated pixels, conifer dominated pixels and
non-classified GSL pixels along the urban-rural gradient from DLT-urban-rural-count QGIS model outputs.

"""

# reading the city list
data = pd.read_csv('C:/Users/amand/Documents/GRADU/dokumentit/Europe_capitals.csv', sep=';')
cities = data['City'].tolist()

# defining path for the data
data_path = 'C:/Users/amand/Documents/GRADU/Data/results/DLT-results/' 

# iterating over the cities            
for city in cities:    
        # open the DLT count data
        dlt = pd.read_csv(data_path + city + '-DLT-zonal-count.csv', sep=';', encoding = 'unicode_escape')
        dlt = dlt[['ringId', 'count_1', 'count_2']]
        dlt = dlt.fillna(0).sort_values('ringId').reset_index(drop=True)
        
        # open the GSL count data
        gsl = pd.read_csv(data_path + city + '-GSL-zonal-count.csv', sep=';', encoding = 'unicode_escape') #, encoding = 'unicode_escape')
        gsl = gsl[['ringId', 'count_5']]
        gsl = gsl.fillna(0).sort_values('ringId').reset_index(drop=True)
     
        # merge dataframes and rename cols
        dlt_data = pd.merge(dlt,gsl,how='left')        
        dlt_data = dlt_data.rename(columns={'count_1':'count_broadleaved','count_2':'count_conifer','count_5':'count_all_GSL'})
        
        # calculate proportion of other vegetation and percentages of each class
        dlt_data['count_other_veg'] = dlt_data['count_all_GSL'] - dlt_data['count_broadleaved'] - dlt_data['count_conifer']
        dlt_data['broadleaved_percentage'] = dlt_data['count_broadleaved'] / dlt_data['count_all_GSL'] * 100
        dlt_data['conifer_percentage'] = dlt_data['count_conifer'] / dlt_data['count_all_GSL'] * 100
        dlt_data['other_veg_percentage'] = dlt_data['count_other_veg'] / dlt_data['count_all_GSL'] * 100

        #print(dlt_data)        
        # save to file
        dlt_data.to_csv('C:/Users/amand/Documents/GRADU/Data/results/DLT-results/' + city + '-DLT-results.csv')
