# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 13:00:05 2023

@author: Amanda Ojasalo
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import cm
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

"""
This script plots GSL, LST, urban land cover or DLT along the urban-rural gradient 
based on the GSL gradient pattern classification.

"""

# variable to plot
var = 'GSL_mean' # 'MAT_2017.2021', 'urban_fabric_1', 'broadleaved_percentage'

# reading the cities, defining data path
gradient_patterns = pd.read_csv('C:/Users/amand/Documents/GRADU/Europe_capitals.csv', sep=';') # file containing list of the cities & GSL gradient patterns
path = 'C:/Users/amand/Documents/GRADU/Data/results/combined-buffer-results/'

# gradient shapes
shapes = ['linear increase', 'linear decrease', 'quadratic up', 
          'quadratic down', 'random', 'high increase']

# iterating over the shapes   
for shape in shapes:
    # selecting cities whith correct shape
    cities = gradient_patterns.loc[gradient_patterns['zonal-shape'] == shape]
    cities = cities['City'].tolist()

    fig, ax = plt.subplots(1,1, figsize=(18, 10))
    
    # create cmap
    cmap = ListedColormap(["tab:blue", "tab:brown", "k", "tab:orange", "tab:purple",
                           "darkgreen", "m", "grey", "tab:cyan", "tab:olive", "khaki"])
    color = iter(cmap(np.linspace(0, 1, 11)))
    
    for city in cities: # plot the cities
        c = next(color) # adjust the color
        data = pd.read_csv(path + city + '-buffer-results.csv')
        ax.scatter(y=data[var], x=data.index, s=130, label=city, color=c)
        data[var].plot(ax=ax, label='_nolegend_', color=c)
    
    # ax properties
    ax.set_ylabel(var, size=26)
    ax.set_xlabel('Distance from urban area (km)', size=26)
    ax.set_title('Cities classified as ' + shape, size=28)
    ax.tick_params(axis='both', which='major', labelsize=24)
    ax.autoscale(enable=True, axis='x', tight=True)
    ax.set_xticks(np.arange(0,11,1))
    ax.set_xticklabels(['0','0-2','2-4','4-6','6-8','8-10','10-12','12-14','14-16','16-18','18-20'])

    #ax.set_ylim([-1,85])
    ax.grid()
    ax.legend(loc='upper right', bbox_to_anchor=(1.21, 1.02), fontsize=20, frameon=False)
