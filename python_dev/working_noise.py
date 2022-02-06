#!/usr/bin/env python

"""
This is a python rendition of Jon Hillier's synthetic spectra IDL script

__author__      = Ethan Ayari, Institute for Modeling Plasmas, Atmospheres and Cosmic Dust
"""


import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


def safe_div(x,y):
    try:
        return x/y
    except ZeroDivisionError:
        return 0
    
#Get full list of all elements and their corresponding symbols, masses and abundances
def fetch_abundances():
    eleabund = pd.read_csv("elementabundances.csv",header = 0)
    #eleabund = pd.read_csv("elementabundances.txt",sep='\t',header = None,skiprows=0)
    #eleabund = df.iloc[:, 0:4]
    #eleabund.columns = ['Name','Symbol','Mass1(u)','Abundance1(%)','Mass2(u)','Abundance2(%)','Mass3(u)','Abundance3(%)','Mass4(u)','Abundance4(%)','Mass5(u)','Abundance5(%)','Mass6(u)','Abundance6(%)','Mass7(u)','Abundance7(%)','Mass8(u)','Abundance8(%)','Mass9(u)','Abundance9(%)','Mass10(u)','Abundance10(%)']
    #eleabund.to_csv("elementabundances.csv", sep = '\t',encoding='utf-8',index = False)
    #eleabund.to_csv("elementabundances.csv", sep = '\t',encoding='utf-8',index = False)
    return eleabund
#Retreve Hillier Relative Sensitivity Factors
def fetch_rsfs():
    rsfs = pd.read_csv("rel_sens_fac.csv")
    rsfs.columns = ['Name','Sensitivity Factor']
    #rsfs.to_csv("rel_sens_fac.csv", '\t', encoding='utf-8',index = False)
    return rsfs
#Retrieve the available elements from the heidelberg experiment and their compositions (up to 8 elements)
def fetch_rocks():
    rocks = pd.read_csv("rocks.csv", header = 0,)
    rocks.columns = ['Mineral','Element1','abundance1','Element2','abundance2','Element3','abundance3','Element4','abundance4','Element5','abundance5','Element6','abundance6','Element7','abundance7','Element8','abundance8']
    #rocks.to_csv("rocks.csv", sep = '\t',encoding='utf-8',index = False)
    return rocks

def add_noise(signal):
    # Set a target SNR
    target_snr_db = 5
    # Calculate signal power and convert to dB 
    sig_avg_watts = np.mean(signal)
    sig_avg_db = 10 * np.log10(sig_avg_watts)
    # Calculate noise according to [2] then convert to watts
    noise_avg_db = sig_avg_db - target_snr_db
    noise_avg_watts = 10 ** (noise_avg_db / 10)
    # Generate an sample of white noise
    mean_noise = 0
    noise_volts = .01*np.random.normal(mean_noise, np.sqrt(noise_avg_watts), len(y))
    # Noise up the original signal
    y_volts = signal - noise_volts
    return y_volts

    
def make_lama(rockarray, percentarray):
#Check for improper data
    if(len(rockarray)!=len(percentarray)):
       print('ERROR - NUMBER OF ROCKS MUST MATCH PERCENTAGES')
       return None

    if(np.sum(percentarray)!=100):
       print('ERROR - TOTAL PERCENTAGES MUST BE 100')
       return None

    rockarray_s = np.sort(rockarray)
    percentarray_s = np.sort(percentarray)
    #print(rockarray_s,percentarray_s)

    if(len(np.unique(rockarray))!=len(rockarray)):
       print('ERROR - PLEASE ONLY USE EACH MINERAL ONCE!')
       return None


    rocks = fetch_rocks()
#convert to fractions 
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


    for i in range(len(rockarray)):
       #print("Desired mineral", type(rockarray[i]))
       #print("Rock list: ", rocks['Mineral'])
       min_pres = rocks.loc[rocks['Mineral']==rockarray[i]]  
       #print(min_pres)                 
       if not (min_pres['Element1'].empty):
          elems_present.append(str(min_pres['Element1']))
       if not (min_pres['abundance1'].empty):
          pres_abunds.append(float(min_pres['abundance1']))
       if not (min_pres['Element2'].empty):
          elems_present.append(str(min_pres['Element2']))
       if not (min_pres['abundance2'].empty):
          pres_abunds.append(float(min_pres['abundance2']))
       if not (min_pres['Element3'].empty):
          elems_present.append(str(min_pres['Element3']))
       if not (min_pres['abundance3'].empty):
          pres_abunds.append(float(min_pres['abundance3']))
       if not (min_pres['Element4'].empty):
          elems_present.append(str(min_pres['Element4']))
       if not (min_pres['abundance4'].empty):
          pres_abunds.append(float(min_pres['abundance4']))
       if not (min_pres['Element5'].empty):
          elems_present.append(str(min_pres['Element5']))
       if not (min_pres['abundance5'].empty):
          pres_abunds.append(float(min_pres['abundance5']))
       if not (min_pres['Element6'].empty):
          elems_present.append(str(min_pres['Element6']))
       if not (min_pres['abundance6'].empty):
          pres_abunds.append(float(min_pres['abundance6']))
       if not (min_pres['Element7'].empty):
          elems_present.append(str(min_pres['Element7']))
       if not (min_pres['abundance7'].empty):
          pres_abunds.append(float(min_pres['abundance7']))
       if not (min_pres['Element8'].empty):
          elems_present.append(str(min_pres['Element8']))
       if not (min_pres['abundance8'].empty):
          pres_abunds.append(float(min_pres['abundance8']))

    #print("Elements present:", elems_present)
    #print("Present abundances:", pres_abunds)
    
    newels = []
    #Remove nonsense characters from element names
    for i in range(len(elems_present)):
        tmp1 = elems_present[i].replace('\nName: Element'+str(i+1)+', dtype: object', '')
        tmp2 = tmp1.replace('7    ','')
        newels.append(tmp2)
    
    print("newels: ", newels)
    iso_abun = []
    iso_mass = []
    iso_syms = []
    isotope_data = fetch_abundances()
    #print(isotope_data.loc[51]["Symbol"])
    #print(isotope_data)


    for i in range(len(newels)):
       iso_pres = isotope_data.loc[isotope_data["Symbol"] == newels[i]]
       #print(iso_pres['Symbol'])
       
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
    

    print(iso_mass)
    print(iso_abun)
    print(iso_syms)
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
    
    #print(iso_syms)
    #print(iso_mass)
    #print(np.count_nonzero(iso_abun))     
    new_abun = []
    for item in iso_abun:
        new_abun.append(item*100.0)
    """    
    print("Newels:", newels)    
    print("Newabunds:", new_abun)
    """
    #print("Abundances: ", new_abun)
    #print("Masses: ", iso_mass)
    molar_conc = [safe_div(i,j) for i, j in zip(new_abun, iso_mass)]
    #print(molar_conc)
    #molar_conc = float(iso_abun)/float(iso_mass)
    totalconc = 0.0
    
    for i in range(len(molar_conc)):
        #print(float(molar_conc[i]))
        if not (molar_conc[i]==0):
            totalconc += float(molar_conc[i])

    molar_conc_norm = []
    
    for item in molar_conc:
        molar_conc_norm.append(item/totalconc)    
    #print(molar_conc_norm)
#Time to add the Relative Sensitivity Factors
    rsfs = fetch_rsfs()
    
#extract Oxygen sensitivity factor for later normalization
    oxrow = rsfs[rsfs['Name'] == "O"]
    oxsens = oxrow["Sensitivity Factor"]
    oxsens = oxsens.to_numpy()[0]
    #print(rsfs["Name"])
    #print("Isotope symbols \n")
    #print(iso_syms[0])
    #print(iso_syms)
    
    sens_names= []
    
    for lp in rsfs["Name"]:
        newsym = re.sub(r'^.*?     ', "", str(lp))
        sens_names.append(newsym)
        #print(len(newsym))
    rsfs['Name'] = [sens_names[i] for i in rsfs.index]
    
    #print(rsfs["Name"])
#Iterate through all pesent isotopes and scale their normalized molar concentrates by their corresponding sensitivity factor
    new_isosyms = []
    for lp in iso_syms:
       newsym = re.sub(r'^.*?    ', "", str(lp))
       twosym = newsym.split("\n",1)[0]
       new_isosyms.append(twosym)

       #print(newsym)
       #pres_rsf = rocks.loc[rsfs['Name']==iso_syms[lp]]
    #print(rsfs["Name"])
    """
    for i in range(len(new_isosyms)):
       if(len(new_isosyms[i])==39):
          new_isosyms[i] = 'Nan'
   """
    rsf_pres = []
    rsf_names = []
    for lp in range(len(new_isosyms)):
       pres_rsf = rsfs.loc[rsfs['Name'] == new_isosyms[lp]]
       #print(pres_rsf['Sensitivity Factor'])
       rsf_pres.append(pres_rsf["Sensitivity Factor"].astype(float))
       rsf_names.append(pres_rsf["Name"].astype(str))


    #print(rsf_pres[0])
    
    #Clean rsf values
    n_rsf_vals = []
    for lp in range(len(rsf_pres)):
       newsym = re.sub(r'^.*?    ', "", str(rsf_pres[lp]))
       twosym = newsym.split("\n",1)[0]
       #print(len(twosym))
       if("Series" in twosym):
           n_rsf_vals.append(0)
       else:
           n_rsf_vals.append(float(twosym)/oxsens)
    
    #clean rsf names
    n_rsf_names = []
    for lp in range(len(rsf_names)):
       newsym = re.sub(r'^.*?    ', "", str(rsf_names[lp]))
       twosym = newsym.split("\n",1)[0]
       #print(len(twosym))
       if("Series" in twosym):
           n_rsf_names.append("")
       else:
           n_rsf_names.append(twosym)
    #print(n_rsf_names)
    
    n_isosyms = []
    for lp in range(len(iso_syms)):
       newsym = re.sub(r'^.*?    ', "", str(iso_syms[lp]))
       twosym = newsym.split("\n",1)[0]
       #print(len(twosym))
       if("Series" in twosym):
           n_isosyms.append("")
       else:
           n_isosyms.append(twosym)
   
    try:
        hydrodex = n_isosyms.index('H')
    except ValueError:
        hydrodex = -1
    """
    print(len(n_rsf_names))
    print(len(n_isosyms))
    print(len(n_rsf_vals))
    print(len(molar_conc_norm))
    """
    #print(rsf_names)
    #print(np.array(new_isosyms))
    #print(molar_conc_norm)
    #increm = 0
    for lp in range(len(n_rsf_names)):
                molar_conc_norm[lp] = molar_conc_norm[lp]*float(n_rsf_vals[lp])
 
    #print(molar_conc_norm)
#calculate silver reference peaks
    lama_abund = np.array(molar_conc_norm).flatten().transpose()
    #print(lama_abund)
    max_abund = max(lama_abund)

    ag_index = isotope_data.loc[isotope_data['Name']=='Silver']
    ag107_index = ag_index[ag_index['Mass1(u)'] == 107]
    ag109_index = ag_index[ag_index['Mass2(u)'] == 109]
    ag107_amp = (max_abund*ag_index['Abundance1(%)'])/100.0
    ag109_amp = (max_abund*ag_index['Abundance2(%)'])/100.0
    #print(ag109_amp,ag107_amp)
#append ag refernece values to isotope mass and abundance arrays
    iso_mass.append(107)
    iso_mass.append(109)
    #lama_abund.append(ag107_amp)
    #lama_abund.append(ag109_amp)
    lama_abund = np.append(lama_abund,ag107_amp)
    lama_abund = np.append(lama_abund,ag109_amp)
    #print(lama_abund)

#Use the stretch and shift parameters of the instrument to convert isotopic abundance array to a TOF then mass spectra
    stretch = 1800.00 #units of ns per sqrt(mass)
    shift = 0.0 #What does this correspond to physically?
    srate = 2.0 #Sample rate in ns
    spectrum_t = np.zeros(10000)
    
#Create TOF
    iso_mass = np.array(iso_mass).flatten().transpose()
    #print(iso_mass[iso_mass != 0])
    
    peak_times = []
    for lp in range(len(iso_mass)):
        peak_times.append((stretch*np.sqrt(iso_mass[lp]+shift)).astype(float)) #in nanoseconds
    peak_times = np.array(peak_times)
    
    peak_positions = []
    for lp in range(len(peak_times)):
       peak_positions.append(np.floor(peak_times[lp]/srate))
    peak_positions = np.array(peak_positions)
    
    for lp in range(len(lama_abund)):
          spectrum_t[peak_positions[lp].astype(int)] = lama_abund[lp]
#Gaussian sample (taken from IDL's gaussian_function)
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

    real_spectrum_t = np.convolve(spectrum_t,gx) + 2.0
    domain = (((np.arange(10000)*2)-shift)/stretch)**2.0
    spec_max = max(real_spectrum_t)
    real_spectrum_t = real_spectrum_t/spec_max

    return domain, real_spectrum_t

x,y = make_lama(['Ferrohornblende'],[100.0])
"""
print(x)
print(y)
"""


y = y[:-62]
y = add_noise(y)



#plt.plot(x,noise_volts)

plt.style.use('dark_background')
fig = plt.figure(dpi = 2000)
fig = plt.figure()
ax  = fig.add_subplot()
ax.set_yscale('log')
ax.set_xlabel("Mass(u)")
ax.set_ylabel("Amplitude")
ax.set_title("100% Ferrohornblende")
ax.plot(x,y,lw=.5,c = 'y')
#ax.fill_between(x, 0, y_volts, alpha=0.2)
#ax.grid()
"""
majorLocator   = MultipleLocator(1)
ax.xaxis.set_major_locator(majorLocator)
"""

