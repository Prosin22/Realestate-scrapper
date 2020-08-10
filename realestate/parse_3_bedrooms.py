# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 15:00:12 2020

@author: pierr
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize

ROOT = "C:/Users/pierr/PycharmProjects/real_estate_scraper/realestate/"

with open(ROOT + "condo.json") as json_file:
    houses = json.load(json_file)


amf = [45.506538, -73.569397]
my01 = [45.500544, -73.562157]

def compute_distance(pt1,pt2):
    dist = (pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2
    return dist

keep_house = []
long_list = []
lat_list = []

max_dist = 1
    
for house in houses:
    keep = True
    try:

        price = int(house["price"].replace("$","").replace(",","").replace(" / monthly",""))
                
        if int(house["principal_characteristics"][0]["Size (sqft)"]) < 1000:
            keep = False
        
        if price > 500000:
            keep = False
        
        point = [float(house["latitude"]),float(house["longitude"])]
        print(compute_distance(point,amf))
        if not (compute_distance(point,amf)<max_dist and compute_distance(point,my01)<max_dist):
            keep = False
            
    except:
        keep = False
        
    

    if keep:
        long_list.append(float(house["longitude"]))
        lat_list.append(float(house["latitude"]))
        
        keep_house.append(house)
        
    

long_min = -73.7217 
long_max = -73.4951

lat_min = 45.4395
lat_max = 45.5436

BBox = ((long_min,   long_max,      
         lat_min, lat_max))
    
fig, ax = plt.subplots(figsize = (8,5))

ax.scatter(long_list, lat_list, zorder=1, c='black', s=10)
ax.set_title('Plotting House Data on Mtl Map')
ax.set_xlim(BBox[0],BBox[1])
ax.set_ylim(BBox[2],BBox[3])
ax.imshow(mtl_map, zorder=0, extent = BBox, aspect= 'equal')
print(keep_house)
