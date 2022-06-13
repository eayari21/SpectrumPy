#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a python rendition of Jon Hillier's synthetic spectra IDL script
__author__      = Ethan Ayari,
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust
"""

import re
# import sys
# import random

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# from subprocess import call
from scipy.stats import exponnorm
from RSF_test import line_appear
from utils import create_fracs
from peakdecayscript import generate_noise

# Improve figure resolution
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True
plt.style.use("seaborn-bright")

# sys.path.insert(0, "/Users/ethanayari/Desktop/Peridot_Jan_'21")


# %%WRAPPER FOR EVERY SPECTRA
class Spectra():
    # %%INITIALIZE TOF OR MASS SPECTRA
    def __init__(self, rockarray, percentarray, vel):
        """
    Parameters
    ----------
    rockarray : String Array
        A list of what minerals are contained in the sample
    percentarray : Float Array
        The relative abundance of each mineral in the sample
    Returns
    -------
    A synthetic TOF or Mass spectra"""

        # Check that each mineral has a specified abundance
        if(len(rockarray) != len(percentarray)):
            print('ERROR - NUMBER OF ROCKS MUST MATCH PERCENTAGES')
            return None

        # Make sure these abundances sum to 100
        if(np.sum(percentarray) != 100):
            print('ERROR - TOTAL PERCENTAGES MUST BE 100')
            return None

        rockarray_s = np.sort(rockarray)
        percentarray_s = np.sort(percentarray)

        # Make sure each mineral is only entered once
        if(len(np.unique(rockarray)) != len(rockarray)):
            print('ERROR - PLEASE ONLY USE EACH MINERAL ONCE!')
            return None

        rocks = fetch_rocks()
        # Convert mineral abundances to to fractions
        percentarray_s = create_fracs(percentarray_s, rocks)

        self.pres_min = []
        elems_present = []
        self.pres_abunds = []

        # Organize mineral data into element lists
        self.unwrap_mins(rocks, elems_present, percentarray_s, rockarray_s)

        # Uncomment out following lines to ensure elements are organized right
        # print("Elements present:", elems_present)
        # print("Present abundances:", self.pres_abunds)

        # Use the appearance curves to alter the spectra
        # This functionality is taken from RSF_test

        for j in range(len(self.els)):
            new_amp_weight = line_appear(self.els[j], vel)
            if new_amp_weight is not None:
                # print("Weight = ", new_amp_weight)
                # print("Abundance = ", self.pres_abunds[j])
                self.pres_abunds[j] = new_amp_weight * self.pres_abunds[j]

        # print("self.els: ", self.els)
        isotope_data = fetch_abundances()

        self.sort_isotopes(isotope_data)

        # Molar concentration is given by
        # dividing the isotopic abundances by the masses
        molar_conc = [safe_div(i, j) for i, j in
                      zip(self.new_abun, self.iso_mass)]
        totalconc = 0.0

        # Calculate total concentration to normalize
        for i in range(len(molar_conc)):
            if not (molar_conc[i] == 0):
                totalconc += float(molar_conc[i])

        molar_conc_norm = []

        for item in molar_conc:
            # molar_conc = safe_div(item, totalconc)
            if(totalconc == 0):
                molar_conc_norm.append(0)
            else:
                molar_conc_norm.append(item/totalconc)

        # Time to add the Relative Sensitivity Factors
        rsfs = fetch_rsfs()

        # extract Oxygen sensitivity factor for later normalization
        oxrow = rsfs[rsfs['Name'] == "O"]
        oxsens = oxrow["Sensitivity Factor"]
        oxsens = oxsens.to_numpy()[0]

        sens_names = []

        # Clean Relative Sensitivity Factor names
        for lp in rsfs["Name"]:
            newsym = re.sub(r'^.*?     ', "", str(lp))
            sens_names.append(newsym)
            # print(len(newsym))
        rsfs['Name'] = [sens_names[i] for i in rsfs.index]

        # Iterate through all pesent isotopes and scale their normalized molar
        # concentrations by their corresponding sensitivity factor
        new_isosyms = []
        for lp in self.iso_syms:
            newsym = re.sub(r'^.*?    ', "", str(lp))
            twosym = newsym.split("\n", 1)[0]
            new_isosyms.append(twosym)

        rsf_pres = []
        rsf_names = []
        for lp in range(len(new_isosyms)):
            pres_rsf = rsfs.loc[rsfs['Name'] == new_isosyms[lp]]

            rsf_pres.append(pres_rsf["Sensitivity Factor"].astype(float))
            rsf_names.append(pres_rsf["Name"].astype(str))

        # Clean rsf values
        self.rsf_vals = []
        for lp in range(len(rsf_pres)):
            newsym = re.sub(r'^.*?    ', "", str(rsf_pres[lp]))
            twosym = newsym.split("\n", 1)[0]

            if("Series" in twosym):
                self.rsf_vals.append(0)
            else:
                self.rsf_vals.append(float(twosym)/oxsens)

        # clean rsf names, annoying "Series" string persists during
        # Pandas to Numpy conversion
        self.rsf_names = []
        for lp in range(len(rsf_names)):
            newsym = re.sub(r'^.*?    ', "", str(rsf_names[lp]))
            twosym = newsym.split("\n", 1)[0]

            if("Series" in twosym):
                self.rsf_names.append("")
            else:
                self.rsf_names.append(twosym)

        # Find the hydrogen index (if it exists) to later disregard
        try:
            hydrodex = self.iso_names.index('H')
        except ValueError:
            hydrodex = -1

        for lp in range(len(self.rsf_names)):
            molar_conc_norm[lp] = molar_conc_norm[lp]*float(self.rsf_vals[lp])

        # calculate silver (Ag) target reference peaks
        lama_abund = np.array(molar_conc_norm).flatten().transpose()
        max_abund = max(lama_abund)
        ag_index = isotope_data.loc[isotope_data['Name'] == 'Silver']
        ag107_index = ag_index[ag_index['Mass1(u)'] == 107]
        ag109_index = ag_index[ag_index['Mass2(u)'] == 109]
        ag107_amp = (max_abund*ag_index['Abundance1(%)'])/100.0
        ag109_amp = (max_abund*ag_index['Abundance2(%)'])/100.0

        # append ag reference values to isotope mass and abundance arrays
        self.iso_mass.append(107)
        self.iso_mass.append(109)

        lama_abund = np.append(lama_abund, ag107_amp)
        lama_abund = np.append(lama_abund, ag109_amp)
        # lama_abund is now an array of arrival times
        # Use the stretch and shift parameters of the instrument to convert
        # isotopic abundance array to a TOF then mass spectra
        stretch = 1800.00  # units of ns per sqrt(mass)
        shift = 0.0
        srate = 2.0  # Sampling rate in ns

        # Create TOF
        spectrum_t = np.zeros(10000)
        self.iso_mass = np.array(self.iso_mass).flatten().transpose()
        # iso_mass MUST be a 1-D Numpy array

        peak_times = []
        for lp in range(len(self.iso_mass)):
            peak_times.append((stretch*np.sqrt(self.iso_mass[lp]+shift)).astype(float))
            # in nanoseconds
        peak_times = np.array(peak_times)

        # Find indices of time peaks and normalize them by the sampling rate
        peak_positions = []
        for lp in range(len(peak_times)):
            peak_positions.append(np.floor(peak_times[lp]/srate))
        peak_positions = np.array(peak_positions)

        # Put arrival times into the peak positions
        for lp in range(len(lama_abund)):
            spectrum_t[peak_positions[lp].astype(int)] = lama_abund[lp]

        # Regular Gaussian sample (taken from IDL's gaussian_function)
        gx = np.array([0.0081887, 0.011109, 0.0149208, 0.0198411, 0.0261214,
                       0.0340475, 0.0439369, 0.0561348, 0.0710054, 0.0889216,
                       0.110251, 0.135335, 0.164474, 0.197899, 0.235746,
                       0.278037, 0.324652, 0.375311, 0.429557, 0.486752,
                       0.546074, 0.606531, 0.666977, 0.726149, 0.782705,
                       0.83527, 0.882497, 0.923116, 0.955997, 0.980199,
                       0.995012, 1., 0.995012, 0.980199, 0.955997, 0.923116,
                       0.882497, 0.83527, 0.782705, 0.726149, 0.666977, 0.6065,
                       0.546074, 0.486752, 0.429557, 0.375311, 0.324652, 0.278,
                       0.235746, 0.197899, 0.164474, 0.135335, 0.110251, 0.088,
                       0.0710054, 0.0561348, 0.0439369, 0.0340475, 0.0261214,
                       0.0198411, 0.0149208, 0.011109, 0.0081887])

        x = np.linspace(0, 10, len(gx))

        # Canonical line shape
        amp = 3.7*exponnorm.pdf(x-4, 1.5)

        # Convove each peak with the Gaussian sample for more realistic shapes
        ring = float(5.0)*np.exp(-1*float(3.0)*x)*np.sin(float(5)*x + 3.14)
        t = np.array_split(ring, 5)
        ringnext = np.concatenate((t[1], t[2], t[3], t[4], t[0]))
        tot = amp + .5*ringnext*amp
        real_spectrum_t = np.convolve(spectrum_t, tot) + 2.0

        # x2 = np.linspace(0, 10, 5*len(x))
        # amp2 = 3.7*exponnorm.pdf(x2-4, 1.5)
        t2 = np.array_split(amp, 5)
        x_l = np.linspace(0, 10, len(t2[4]))

        np.seterr(divide='ignore', invalid='ignore')
        sinc = np.sin(2*x_l)/x_l
        sinc[0] = 1.0
        sinc = sinc/max(sinc)
        sinc[0] = 1.0
        # test = t2[4]*sinc
        #  h = np.concatenate((t2[0], t2[1], t2[2], t2[3], test))
        real_spectrum_t = np.convolve(spectrum_t, gx) + 2.0

        domain = (((np.arange(10000)*2)-shift)/stretch)**2.0
        spec_max = max(real_spectrum_t)
        real_spectrum_t = real_spectrum_t/spec_max

        self.domain, self.mass_spectrum = domain, real_spectrum_t

# %%PROCESS MINERAL CSV
    def unwrap_mins(self, rocks, elems_present, percentarray_s, rockarray_s):
        # Unwrap mineral data
        for i in range(len(rockarray_s)):
            # Find what mineral(s) are present
            min_pres = rocks.loc[rocks['Mineral'] == rockarray_s[i]]

            # Add it to the object list
            self.pres_min.append(min_pres)

            # Go throguh and add the elements and their respective abundances
            # for each mineral detected in the sample
            for j in range(7):
                t = j+1
                if not (min_pres['Element{}'.format(str(t))].empty):
                    elems_present.append(min_pres['Element{}'.format(str(t))].to_string())
                if not (min_pres['abundance{}'.format(str(t))].empty):
                    self.pres_abunds.append(float(min_pres['abundance{}'.format(str(t))]
                                                  + (percentarray_s[i]*min_pres['abundance{}'.format(str(t))])))

        self.els = []

        # Remove nonsense characters from element names and add them to a list
        for i in range(len(elems_present)):
            tmp1 = elems_present[i].replace('\nName: Element'+str(i+1) +
                                            ', dtype: object', '')
            tmp2 = re.sub(r'^.*?    ', "", tmp1)
            self.els.append(tmp2)

        # print(self.els)
        """
        elstemp = pd.Series(elems_present)
        for val in elstemp:
            self.els.append(val)
        print(self.els)
        """

# %%PROCESS ISOTOPE DATA
    def sort_isotopes(self, isotope_data):

        self.iso_abun = []
        self.iso_mass = []
        self.iso_syms = []

        for i in range(len(self.els)):

            # Find what isotopes are present in the
            # elements and their relativeabundances
            iso_pres = isotope_data.loc[isotope_data["Symbol"] == self.els[i]]

            # Check for all 8 possible abundances and add them to a list,
            # along with their corresponding masses
            for k in range(9):
                t = k+1
                if not (iso_pres['Abundance{}(%)'.format(str(t))].empty):
                    self.iso_syms.append(iso_pres['Symbol'])
                    self.iso_abun.append((iso_pres['Abundance{}(%)'.format(str(t))].astype(float)/100.0)*self.pres_abunds[i])
                if not (iso_pres['Mass{}(u)'.format(str(t))].empty):
                    self.iso_mass.append(iso_pres['Mass{}(u)'.format(str(t))].astype(float))

        # Clean isotopic mass values
        for lp in range(len(self.iso_mass)):
            if(len(self.iso_mass[lp] != 0)):
                newsym = re.sub(r'^.*?    ', "", str(self.iso_mass[lp]))

                twosym = newsym.split("\n", 1)[0]
                newsym = re.sub(r'^.*?   ', "", twosym)
                if not(str(newsym) == "NaN"):
                    self.iso_mass[lp] = float(newsym)
                else:
                    self.iso_mass[lp] = 0

        # Clean isotopic abundance values
        for lp in range(len(self.iso_abun)):
            if(len(self.iso_abun[lp] != 0)):
                newsym = re.sub(r'^.*?    ', "", str(self.iso_abun[lp]))

                twosym = newsym.split("\n", 1)[0]
                newsym = re.sub(r'^.*?   ', "", twosym)
                if not(str(newsym) == "NaN"):
                    self.iso_abun[lp] = float(newsym)
                else:
                    self.iso_abun[lp] = 0

        # Scale isotopic abundances by 100
        self.new_abun = []
        for item in self.iso_abun:
            self.new_abun.append(item*100.0)

        # Clean isotope names
        self.iso_names = []
        for lp in range(len(self.iso_syms)):
            newsym = re.sub(r'^.*?    ', "", str(self.iso_syms[lp]))
            twosym = newsym.split("\n", 1)[0]

            if("Series" in twosym):
                self.iso_names.append("")
            else:
                self.iso_names.append(twosym)


# %%AVOID DIVISION BY ZERO
def safe_div(x, y):
    # Function to handle division by zero "Pythonically"
    try:
        return x/y
    except ZeroDivisionError:
        return 0


# %%FETCH ISOTOPIC ABUNDANCES
def fetch_abundances():
    # Get full list of all elements and their corresponding
    # symbols, masses and abundances
    eleabund = pd.read_csv("elementabundances.csv", header=0)
    return eleabund


# %%FETCH RELATIVE SENSITIVITY FACTORS
def fetch_rsfs():
    # Retreve Hillier Relative Sensitivity Factors (Taken from TOF-SIMS)
    rsfs = pd.read_csv("rel_sens_fac.csv")
    rsfs.columns = ['Name', 'Sensitivity Factor']
    return rsfs


# %%FETCH MINERAL ELEMENTAL ABUNDNCES
def fetch_rocks():
    # Retrieve the available elements from the heidelberg experiment and
    # their compositions (up to 8 elements)
    rocks = pd.read_csv("rocks.csv", header=0)
    rocks.columns = ['Mineral', 'Element1', 'abundance1', 'Element2',
                     'abundance2', 'Element3', 'abundance3', 'Element4',
                     'abundance4', 'Element5', 'abundance5', 'Element6',
                     'abundance6', 'Element7', 'abundance7', 'Element8',
                     'abundance8']
    return rocks


# %%FETCH MINERAL ELEMENTAL ABUNDNCES
def rms_val(signal):
    rms = np.sqrt(np.mean(signal**2))
    return rms


# %%ADD REALISTIC NOISE TO A SIGNAL
def add_real_noise(signal, SNR):
    noise = generate_noise().astype(float)
    scaling = np.abs(rms_val(signal)/rms_val(noise))/(SNR**2)
    for k in range(len(signal)):
        if(signal[k] < .2):
            signal[k] += np.random.choice(noise*scaling, size=1)
    return signal


# %%ADD GAUSSIAN (WHITE) NOISE TO A SIGNAL
def add_gaussian_noise(signal):
    """
    Parameters
    ----------
    signal : Float64 Array
        An initial numerical spectra free from noise.
    Returns
    -------
    A synthetic TOF or mass spectra with  optional gaussian "white"
    noise added throughout.
    This white noise was derived via fourier analysis of Peridot impact
    spectra on the Hyperdust instrument.
    """
    # Based on a specified signal to noise ratio (SNR), select values
    # from a gaussian sample whose mean corresponds to the ratio.

    # Set a target SNR
    target_snr_db = 5
    peak_sig = np.where(signal[signal > 2.7*10e-1])
    # Calculate signal power and convert to dB
    sig_avg_watts = np.mean(signal)
    sig_avg_db = 10 * np.log10(sig_avg_watts)
    # Calculate noise according to [2] then convert to watts
    noise_avg_db = sig_avg_db - target_snr_db
    noise_avg_watts = 10 ** (noise_avg_db / 10)
    # Generate an sample of white noise
    mean_noise = 0
    noise_volts = .1*np.random.normal(mean_noise,
                                      np.sqrt(noise_avg_watts), len(signal))

    noise_volts[peak_sig] = 0
    # Noise up the original signal
    y_volts = signal - noise_volts
    return y_volts


# %%
if __name__ == "__main__":
    """
    ==========================================================================
    Test code: Enter the mineral you want to you want to see the spectra of.
    **NOTE: Minerals must be written just as they are below
    in order to set the "min_name" variable properly**
    Currently available minerals include:
    1. Ferrosilite
    2. Enstatite
    3. Fayalite
    4. Forsterite
    5. Anorthite
    6. Albite
    7. Magnesiohornblende
    8. Ferrohornblende
    9. Spinel
    10. Peridot
    11. Silica
    ==========================================================================
    """
"""
    N_spectra = 200
    mineral_names = np.array(['Albite',
                              'Anorthite',
                              'Enstatite',
                              'Fayalite',
                              'Ferrohornblende',
                              'Ferrosilite',
                              'Forsterite',
                              'Magnesiohornblende',
                              'Spinel',
                              'Peridot',
                              'Silica'])

    # x,y = Spectra(['Albite','Anorthite'],[200/3,100/3])

    # ForSpec = Spectra(['Forsterite','Anorthite'],[200/3,100/3])
    velarr = []
    SNRarr = []
    # SNRchoice = [2, 50, 100, 200]
    min_name = ""
    for k in range(N_spectra):
        if(k <= 49):
            min_name = mineral_names[9]
        elif(k <= 99):
            min_name = mineral_names[9]
        elif(k <= 149):
            min_name = mineral_names[10]
        elif(k <= 199):
            min_name = mineral_names[10]
        elif(k <= 249):
            min_name = mineral_names[4]
        elif(k <= 299):
            min_name = mineral_names[5]
        elif(k <= 349):
            min_name = mineral_names[6]
        elif(k <= 399):
            min_name = mineral_names[7]
        elif(k <= 449):
            min_name = mineral_names[8]
        # min_name = "Fayalite-Spinel"
        # min_name = "Peridot"
        # min_name = str(min_name)
        # print(min_name)
        # vel = 18*random.uniform(0, 1)+7
        vel = 20.0
        velarr.append(vel)
        # print(vel)

        # Render spectrum object
        ForSpec = Spectra([min_name], [100], 20.0)
        # ForSpec = Spectra(["Fayalite", "Spinel"], [50.0, 50.0], vel)
        # ForSpec = Spectra(["Fayalite"],[100.0], 22.0)

        # One spectra object attribute is a suitable domain for plotting
        x = ForSpec.domain

        # The spectrum is another accesible attribute
        y = ForSpec.mass_spectrum
        y = y[:-62]
        y = y - min(y)

        # print(ForSpec.pres_min)

        # SNR_tmp = np.random.choice(SNRchoice, size=1)
        SNR_tmp = 40.0
        SNRarr.append(SNR_tmp)
        y = add_real_noise(y, SNR_tmp)
        # noise = np.random.normal(0, 10e-20, len(y))

        # for k in range(len(y)):
        #    if(k % 15 == 0):
        #        y[k] = y[k]+noise[k]

        # Display the spectrum with high-resolution
        # plt.style.use('dark_background')
        fig = plt.figure(dpi=2000)
        fig = plt.figure()
        ax = fig.add_subplot()
        # Display spectrum in log
        ax.set_yscale('log')
        ax.set_xlabel("Mass(u)", fontsize=15)
        ax.set_ylabel("Amplitude", fontsize=15)
        ax.set_title(min_name,
                     font="Times New Roman", fontweight="bold",
                     fontsize=20)
        ax.set_facecolor("white")
        ax.plot(x, y, lw=1, c='r')
        plt.grid(b=None)
        plt.savefig(min_name+str(k+1)+".eps", dpi=1200)

        x = np.array(x)  # .transpose()
        y = np.array(y)  # .transpose()

        # print("x= ", x, "y= ", y)
        # Save Spectra as a csv as well
        SpecDict = {"Mass": x, "Amplitude": y}
        SpecFrame = pd.DataFrame({"Mass": x, "Amplitude": y})

        spec_save = str(k+1) + ".csv"
        SpecFrame.to_csv(spec_save, sep=",")

velarr = np.array(velarr)
np.savetxt("Velocities.txt", velarr)
SNRarr = np.array(SNRarr)
np.savetxt("SignaltoNoise.txt", SNRarr)

# Copy every file with a spectra number in its name
# call(['cp', '/Users/ethanayari/Documents/GitHub/SpectrumPy
# copy/python_dev/*{1..450}*', '/Users/ethanayari/Dropbox/IDEX
# Pipeline/python/Training_Sets/trainingset4'])
"""
