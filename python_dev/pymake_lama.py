#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a python rendition of Jon Hillier's synthetic spectra IDL script

__author__      = Ethan Ayari, Institute for Modeling Plasmas, Atmospheres and Cosmic Dust
"""


import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

#Improve figure resolution
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

#%%
def safe_div(x,y):
#Function to handle division by zero "Pythonically"
    try:
        return x/y
    except ZeroDivisionError:
        return 0
    
    
#%%
def fetch_abundances():
#Get full list of all elements and their corresponding symbols, masses and abundances
    eleabund = pd.read_csv("elementabundances.csv",header = 0)
    return eleabund


#%%
def fetch_rsfs():
#Retreve Hillier Relative Sensitivity Factors (Taken from TOF-SIMS)
    rsfs = pd.read_csv("rel_sens_fac.csv")
    rsfs.columns = ['Name','Sensitivity Factor']
    return rsfs


#%%
def fetch_rocks():
#Retrieve the available elements from the heidelberg experiment and their compositions (up to 8 elements)
    rocks = pd.read_csv("rocks.csv", header = 0,)
    rocks.columns = ['Mineral','Element1','abundance1','Element2','abundance2','Element3','abundance3','Element4','abundance4','Element5','abundance5','Element6','abundance6','Element7','abundance7','Element8','abundance8']
    return rocks


#%%
def add_noise(signal):

    """
    

    Parameters
    ----------
    signal : Float64 Array
        An initial numerical spectra free from noise

    Returns
    -------
    A synthetic TOF or mass spectra with gaussian "white" noise added throughout. This whitenoise was derived via fourier analysis of Peridot impact ionization spectra on the Hyperdust instrument.

    """

#Based on a specified signal to noise ratio (SNR), select values from a gaussian sample whose mean corresponds to the ratio. 

    # Set a target SNR
    target_snr_db = 5
    peak_sig = np.where(signal[signal>2.7*10e-4])
    # Calculate signal power and convert to dB 
    sig_avg_watts = np.mean(signal)
    sig_avg_db = 10 * np.log10(sig_avg_watts)
    # Calculate noise according to [2] then convert to watts
    noise_avg_db = sig_avg_db - target_snr_db
    noise_avg_watts = 10 ** (noise_avg_db / 10)
    # Generate an sample of white noise
    mean_noise = 0
    noise_volts = .01*np.random.normal(mean_noise, np.sqrt(noise_avg_watts), len(y))
    
    noise_volts[peak_sig] = 0
    # Noise up the original signal
    y_volts = signal - noise_volts
    return y_volts


#%%   
def make_lama(rockarray, percentarray):
   
    """
    

    Parameters
    ----------
    rockarray : String Array
        A list of what minerals are contained in the sample
    percentarray : Float Array
        The relative abundance of each mineral in the sample

    Returns
    -------
    A synthetic TOF or mass spectra

    """
    
    
#Check that each mineral has a specified abundance
    if(len(rockarray)!=len(percentarray)):
       print('ERROR - NUMBER OF ROCKS MUST MATCH PERCENTAGES')
       return None

#Make sure these abundances sum to 100
    if(np.sum(percentarray)!=100):
       print('ERROR - TOTAL PERCENTAGES MUST BE 100')
       return None

    rockarray_s = np.sort(rockarray)
    percentarray_s = np.sort(percentarray)

#Make sure each mineral is only entered once
    if(len(np.unique(rockarray))!=len(rockarray)):
       print('ERROR - PLEASE ONLY USE EACH MINERAL ONCE!')
       return None


    rocks = fetch_rocks()
#Convert mineral abundances to to fractions 
    rocks['abundance1'] =  rocks['abundance1'].astype(float)/100
    rocks['abundance2'] =  rocks['abundance2'].astype(float)/100
    rocks['abundance3'] =  rocks['abundance3'].astype(float)/100
    rocks['abundance4'] =  rocks['abundance4'].astype(float)/100
    rocks['abundance5'] =  rocks['abundance5'].astype(float)/100
    rocks['abundance6'] =  rocks['abundance6'].astype(float)/100
    rocks['abundance7'] =  rocks['abundance7'].astype(float)/100
    rocks['abundance8'] =  rocks['abundance8'].astype(float)/100
    percentarray_s = percentarray_s/100.0
    
    elems_present = []
    pres_abunds = []

#Unwrap mineral data
    for i in range(len(rockarray)):
#Find what mineral(s) are present
       min_pres = rocks.loc[rocks['Mineral']==rockarray_s[i]]  
#Go throguh and add the elements and their respective abundances for each mineral detected in the sample
       if not (min_pres['Element1'].empty):
          elems_present.append(str(min_pres['Element1']))
       if not (min_pres['abundance1'].empty):
          pres_abunds.append(float(min_pres['abundance1'] + (percentarray_s[i]*min_pres['abundance1'])))
       if not (min_pres['Element2'].empty):
          elems_present.append(str(min_pres['Element2']))
       if not (min_pres['abundance2'].empty):
          pres_abunds.append(float(min_pres['abundance2'] + (percentarray_s[i]*min_pres['abundance2'])))
       if not (min_pres['Element3'].empty):
          elems_present.append(str(min_pres['Element3']))
       if not (min_pres['abundance3'].empty):
          pres_abunds.append(float(min_pres['abundance3'] + (percentarray_s[i]*min_pres['abundance3'])))
       if not (min_pres['Element4'].empty):
          elems_present.append(str(min_pres['Element4']))
       if not (min_pres['abundance4'].empty):
          pres_abunds.append(float(min_pres['abundance4'] + (percentarray_s[i]*min_pres['abundance4'])))
       if not (min_pres['Element5'].empty):
          elems_present.append(str(min_pres['Element5']))
       if not (min_pres['abundance5'].empty):
          pres_abunds.append(float(min_pres['abundance5'] + (percentarray_s[i]*min_pres['abundance5'])))
       if not (min_pres['Element6'].empty):
          elems_present.append(str(min_pres['Element6']))
       if not (min_pres['abundance6'].empty):
          pres_abunds.append(float(min_pres['abundance6'] + (percentarray_s[i]*min_pres['abundance6'])))
       if not (min_pres['Element7'].empty):
          elems_present.append(str(min_pres['Element7']))
       if not (min_pres['abundance7'].empty):
          pres_abunds.append(float(min_pres['abundance7'] + (percentarray_s[i]*min_pres['abundance7'])))
       if not (min_pres['Element8'].empty):
          elems_present.append(str(min_pres['Element8']))
       if not (min_pres['abundance8'].empty):
          pres_abunds.append(float(min_pres['abundance8'] + (percentarray_s[i]*min_pres['abundance8'])))

    #print("Elements present:", elems_present)
    #print("Present abundances:", pres_abunds)
    
    newels = []
    #Remove nonsense characters from element names and add them to a list
    for i in range(len(elems_present)):
        tmp1 = elems_present[i].replace('\nName: Element'+str(i+1)+', dtype: object', '')
        tmp2 = re.sub(r'^.*?    ', "", tmp1)
        newels.append(tmp2)
    
    #print("newels: ", newels)
    iso_abun = []
    iso_mass = []
    iso_syms = []
    isotope_data = fetch_abundances()


    for i in range(len(newels)):
        
       #Find what isoptopes are present in the elements and their relative abundances
       iso_pres = isotope_data.loc[isotope_data["Symbol"] == newels[i]]

       #Check for all 8 possible abbundances and add them to a list, along with their corresponding masses
       if not (iso_pres['Abundance1(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance1(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass1(u)'].empty):
           iso_mass.append(iso_pres['Mass1(u)'].astype(float))
       
       if not (iso_pres['Abundance2(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance2(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass2(u)'].empty):
           iso_mass.append(iso_pres['Mass2(u)'].astype(float))
       
       if not (iso_pres['Abundance3(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance3(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass3(u)'].empty):
           iso_mass.append(iso_pres['Mass3(u)'].astype(float))
       
       if not (iso_pres['Abundance4(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance4(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass4(u)'].empty):
           iso_mass.append(iso_pres['Mass4(u)'].astype(float))
       
       if not (iso_pres['Abundance5(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance5(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass5(u)'].empty):
           iso_mass.append(iso_pres['Mass5(u)'].astype(float))
       
       if not (iso_pres['Abundance6(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance6(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass6(u)'].empty):
           iso_mass.append(iso_pres['Mass6(u)'].astype(float))
       
       if not (iso_pres['Abundance7(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance7(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass7(u)'].empty):
           iso_mass.append(iso_pres['Mass7(u)'].astype(float))
      
       if not (iso_pres['Abundance8(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance8(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass8(u)'].empty):
           iso_mass.append(iso_pres['Mass8(u)'].astype(float))
       
       if not (iso_pres['Abundance9(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance9(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass9(u)'].empty):
           iso_mass.append(iso_pres['Mass9(u)'].astype(float))
       
       if not (iso_pres['Abundance10(%)'].empty):
           iso_syms.append(iso_pres['Symbol'])
           iso_abun.append((iso_pres['Abundance10(%)'].astype(float)/100.0)*pres_abunds[i])
       if not (iso_pres['Mass10(u)'].empty):
           iso_mass.append(iso_pres['Mass10(u)'].astype(float))

#Clean isotopic mass values
    for lp in range(len(iso_mass)):
        if(len(iso_mass[lp] != 0)):
           newsym = re.sub(r'^.*?    ', "", str(iso_mass[lp]))
           #print(newsym)
           twosym = newsym.split("\n",1)[0]
           newsym = re.sub(r'^.*?   ', "", twosym)
           if not(str(newsym)=="NaN"):
               iso_mass[lp] = float(newsym)
           else:
               iso_mass[lp] = 0 
#Clean isotopic abundance values              
    for lp in range(len(iso_abun)):
        if(len(iso_abun[lp] != 0)):
           newsym = re.sub(r'^.*?    ', "", str(iso_abun[lp]))
           #print(newsym)
           twosym = newsym.split("\n",1)[0]
           newsym = re.sub(r'^.*?   ', "", twosym)
           if not(str(newsym)=="NaN"):
               iso_abun[lp] = float(newsym)
           else:
               iso_abun[lp] = 0           
    
#Scale isotopic abundances by 100  
    new_abun = []
    for item in iso_abun:
        new_abun.append(item*100.0)
        
#Molar concentration is given by dividing the isotopic abundances by the masses
    molar_conc = [safe_div(i,j) for i, j in zip(new_abun, iso_mass)]
    totalconc = 0.0
    
#Calculate total concentration to normalize
    for i in range(len(molar_conc)):
        if not (molar_conc[i]==0):
            totalconc += float(molar_conc[i])

    molar_conc_norm = []
    
    for item in molar_conc:
        molar_conc_norm.append(item/totalconc)    

#Time to add the Relative Sensitivity Factors
    rsfs = fetch_rsfs()
    
#extract Oxygen sensitivity factor for later normalization
    oxrow = rsfs[rsfs['Name'] == "O"]
    oxsens = oxrow["Sensitivity Factor"]
    oxsens = oxsens.to_numpy()[0]

    
    sens_names= []
    
#Clean Relative Sensitivity Factor names
    for lp in rsfs["Name"]:
        newsym = re.sub(r'^.*?     ', "", str(lp))
        sens_names.append(newsym)
        #print(len(newsym))
    rsfs['Name'] = [sens_names[i] for i in rsfs.index]
    

#Iterate through all pesent isotopes and scale their normalized molar concentrates by their corresponding sensitivity factor
    new_isosyms = []
    for lp in iso_syms:
       newsym = re.sub(r'^.*?    ', "", str(lp))
       twosym = newsym.split("\n",1)[0]
       new_isosyms.append(twosym)

    rsf_pres = []
    rsf_names = []
    for lp in range(len(new_isosyms)):
       pres_rsf = rsfs.loc[rsfs['Name'] == new_isosyms[lp]]

       rsf_pres.append(pres_rsf["Sensitivity Factor"].astype(float))
       rsf_names.append(pres_rsf["Name"].astype(str))



    
#Clean rsf values
    n_rsf_vals = []
    for lp in range(len(rsf_pres)):
       newsym = re.sub(r'^.*?    ', "", str(rsf_pres[lp]))
       twosym = newsym.split("\n",1)[0]

       if("Series" in twosym):
           n_rsf_vals.append(0)
       else:
           n_rsf_vals.append(float(twosym)/oxsens)
    
#clean rsf names, annoying "Series" string persists during Pandas to Numpy conversion
    n_rsf_names = []
    for lp in range(len(rsf_names)):
       newsym = re.sub(r'^.*?    ', "", str(rsf_names[lp]))
       twosym = newsym.split("\n",1)[0]

       if("Series" in twosym):
           n_rsf_names.append("")
       else:
           n_rsf_names.append(twosym)

    
    n_isosyms = []
    for lp in range(len(iso_syms)):
       newsym = re.sub(r'^.*?    ', "", str(iso_syms[lp]))
       twosym = newsym.split("\n",1)[0]
       #print(len(twosym))
       if("Series" in twosym):
           n_isosyms.append("")
       else:
           n_isosyms.append(twosym)
   
#Find the hydrogen index (if it exists) to later disregard
    try:
        hydrodex = n_isosyms.index('H')
    except ValueError:
        hydrodex = -1
   
    for lp in range(len(n_rsf_names)):
                molar_conc_norm[lp] = molar_conc_norm[lp]*float(n_rsf_vals[lp])
 

#calculate silver (Ag) target reference peaks
    lama_abund = np.array(molar_conc_norm).flatten().transpose()
    max_abund = max(lama_abund)
    ag_index = isotope_data.loc[isotope_data['Name']=='Silver']
    ag107_index = ag_index[ag_index['Mass1(u)'] == 107]
    ag109_index = ag_index[ag_index['Mass2(u)'] == 109]
    ag107_amp = (max_abund*ag_index['Abundance1(%)'])/100.0
    ag109_amp = (max_abund*ag_index['Abundance2(%)'])/100.0
    
#append ag refernece values to isotope mass and abundance arrays
    iso_mass.append(107)
    iso_mass.append(109)
 
    lama_abund = np.append(lama_abund,ag107_amp)
    lama_abund = np.append(lama_abund,ag109_amp)
#lama_abund is now an array of arrival times

#Use the stretch and shift parameters of the instrument to convert isotopic abundance array to a TOF then mass spectra
    stretch = 1800.00 #units of ns per sqrt(mass)
    shift = 0.0 #What does this correspond to physically?
    srate = 2.0 #Sampling rate in ns
    
#Create TOF
    spectrum_t = np.zeros(10000)
    iso_mass = np.array(iso_mass).flatten().transpose() #MUST be a 1-D Numpy array

    peak_times = []
    for lp in range(len(iso_mass)):
        peak_times.append((stretch*np.sqrt(iso_mass[lp]+shift)).astype(float)) #in nanoseconds
    peak_times = np.array(peak_times)
    
    
#Find indexes of time peaks and normalize them by the sampling rate
    peak_positions = []
    for lp in range(len(peak_times)):
       peak_positions.append(np.floor(peak_times[lp]/srate))
    peak_positions = np.array(peak_positions)

#Put arrival times into the peak positions    
    for lp in range(len(lama_abund)):
          spectrum_t[peak_positions[lp].astype(int)] = lama_abund[lp]
          
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

#Convove each peak with the Gaussian sample for more realistic shapes
    real_spectrum_t = np.convolve(spectrum_t,gx) + 2.0
    domain = (((np.arange(10000)*2)-shift)/stretch)**2.0
    spec_max = max(real_spectrum_t)
    real_spectrum_t = real_spectrum_t/spec_max

    return domain, real_spectrum_t




if __name__ == "__main__":
    
    min_name = 'Anorthite'
    
    #x,y = make_lama(['Albite','Anorthite'],[200/3,100/3])
    x,y = make_lama([min_name],[100])
    y = y[:-62]
    
    #y = add_noise(y)
    
    plt.style.use('dark_background')
    fig = plt.figure(dpi = 2000)
    fig = plt.figure()
    ax  = fig.add_subplot()
    ax.set_yscale('log')
    ax.set_xlabel("Mass(u)")
    ax.set_ylabel("Amplitude")
    ax.set_title("100% " + min_name)
    
    ax.plot(x,y,lw=.5,c = 'y')
    
    plt.savefig("Forsterite100.eps", dpi=1200)

