#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 22 15:07:07 2022

@author: ethanayari
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import exponnorm

plt.style.use('seaborn-poster')
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
        
#Canonical line shape
amp = 3.7*exponnorm.pdf(x-4, 1.5)

ring = float(5.0)*np.exp(-1*float(3.0)*x)*np.sin(float(5)*x + 3.14)
A = 1
B = 1
w = 1
p = 1

t = np.array_split(ring,5)
ringnext=np.concatenate((t[1],t[2],t[3],t[4],t[0]))
test2= amp + 1.2*ringnext*amp

sinc=np.sin(2*x)/x
sinc[0] = 1.0
sinc = sinc/max(sinc)
sinc[0] = 1.0
x2 = np.linspace(0,10, 5*len(x))
amp2 = 3.7*exponnorm.pdf(x2-4, 1.5)
t2 = np.array_split(amp2,5)
test = t2[4]*sinc
h = np.concatenate((t2[0], t2[1], t2[2], t2[3], test))

plt.plot(x, gx, c='r', label="Gaussian")

plt.plot(x2, h,c='g', lw = 4, label="Ringing Shape")
# plt.plot(x, amp, c='b', label="EMG")
plt.xlabel("Time of Flight $( \mu s)$")
plt.ylabel("Amplitude (ion number)")
plt.title("Available Line Shapes", fontweight="bold", fontsize = 20)
plt.grid(False)
plt.legend()