#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 13:53:04 2021

@author: ethanayari
"""

import h5py
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

#Put the path to your hdf5
filename = "Anthracene_iron_7_13_2021_10kms_plus.h5"

def decay(t,b,c):
    # A = initial amount
    # B = decay constant
    # t = time
    # C = additive constant
    x0 = 100
    return x0 * np.exp(-b * t) + c



def read_hdf5(path):


    keys = []
    f =  h5py.File(path, 'r') # open file
    
    f.visit(keys.append) # append all keys to list
    for key in keys:
        print(f[key].name)

    #change this to whatever you want to extract
    mass = f["/Spectra/Spectrum  17/Mass"]
    amp = f["/Spectra/Spectrum  17/AmplitudeDenoised"]
    return mass[()], amp[()]

#Read in mass and amplitude from the hdf5 export
m_17, amp_17 = read_hdf5("Anthracene_iron_7_13_2021_10kms_plus.h5")
print(type(m_17),type(amp_17))
deriv = np.diff(amp_17)/np.diff(m_17)
#deriv = np.gradient(amp_17, m_17)

#print(m_17)
#print(amp_17)

mpl.rcParams['agg.path.chunksize'] = 10000
#fig = plt.figure(dpi = 2000)
plt.plot(m_17,amp_17, 'y')
#plt.plot(m_17[:-1],deriv, 'r')
#plt.ylim(10e-5,1.0)

#Plot in log to look like Spectrum
plt.yscale('log')
plt.xlabel("Mass (u)")
plt.ylabel("Amplitude")
plt.title("Anthracene #17")
plt.show()




    
