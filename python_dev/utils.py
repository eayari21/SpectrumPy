#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 10:49:22 2021

@author: ethanayari
"""

from scipy.stats import exponnorm
import numpy as np
import matplotlib.pyplot as plt


plt.style.use('seaborn-darkgrid')

#Improve figure resolution
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True


#%%
def create_fracs(percent_arr, rocks):
    percentarray_s = percent_arr
    
    #Convert mineral abundances to to fractions 
    rocks['abundance1'] =  rocks['abundance1'].astype(float)/100
    rocks['abundance2'] =  rocks['abundance2'].astype(float)/100
    rocks['abundance3'] =  rocks['abundance3'].astype(float)/100
    rocks['abundance4'] =  rocks['abundance4'].astype(float)/100
    rocks['abundance5'] =  rocks['abundance5'].astype(float)/100
    rocks['abundance6'] =  rocks['abundance6'].astype(float)/100
    rocks['abundance7'] =  rocks['abundance7'].astype(float)/100
    rocks['abundance8'] =  rocks['abundance8'].astype(float)/100
    frac_array = percentarray_s/100.0
    
    return frac_array

#%%
if __name__ == "__main__":
              
#Code to display the different line shapes
#So far this only includes the Gaussian and EMG models
              
    #Regular Gaussian sample (taken from IDL's gaussian_function)
    gx = np.array([0.0081887, 0.011109 , 0.0149208, 0.0198411, 0.0261214, 0.0340475,
           0.0439369, 0.0561348, 0.0710054, 0.0889216, 0.110251 , 0.135335 ,
           0.164474 , 0.197899 , 0.235746 , 0.278037 , 0.324652 , 0.375311 ,
           0.429557 , 0.486752 , 0.546074 , 0.606531 , 0.666977 , 0.726149 ,
           0.782705 , 0.83527  , 0.882497 , 0.923116 , 0.955997 , 0.980199 ,
           0.995012 , 1.       , 0.995012 , 0.980199 , 0.955997 , 0.923116 ,
           0.882497 , 0.83527  , 0.782705 , 0.726149 , 0.666977 , 0.606531 ,
           0.546074 , 0.486752 , 0.429557 , 0.375311 , 0.324652 , 0.278037 ,
           0.235746 , 0.197899 , 0.164474 , 0.135335 , 0.110251 , 0.0889216,
           0.0710054, 0.0561348, 0.0439369, 0.0340475, 0.0261214, 0.0198411,
           0.0149208, 0.011109 , 0.0081887])
        
    x = np.linspace(0,10,len(gx))
        
    amp = 3.7*exponnorm.pdf(x-4, 1.5)
    
    plt.plot(x,gx, 'c', lw = 4, label = "Regular Gaussian")
    plt.plot(x,amp, 'r', lw = 4, label = "Exponentially Modified Gaussian")
    plt.xlabel("Mass/Time (Arbitrary)")
    plt.ylabel("Amplitude")
    plt.title("Line Shapes Available", fontweight = 'bold', fontsize = 20)
    plt.legend(loc = 'upper right')
    plt.grid()
    plt.show()
    
    