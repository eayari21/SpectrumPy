#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a python rendition of Jon Hillier's synthetic spectra IDL script
__author__ = Ethan Ayari,
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust

Works with Python 3.8.10
"""

import re
# import sys
import random

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# from subprocess import call
from decimal import *
from scipy.stats import exponnorm
from RSF_test import line_appear
from utils import create_fracs
from peakdecayscript import generate_noise

# Improve figure resolution
# plt.rcParams["figure.figsize"] = [10.0, 5.0]
# plt.rcParams["figure.autolayout"] = True
plt.style.use("seaborn-pastel")

# sys.path.insert(0, "/Users/ethanayari/Desktop/Peridot_Jan_'21")


# %%WRAPPER FOR EVERY SPECTRA
class Spectra():
    # %%INITIALIZE TOF OR MASS SPECTRA
    def __init__(self, rockarray, percentarray, vel, stretch=1800.0,
                 shift=0.0):
        """Creates a synthetic TOF of Mass Spectra. for a user-provided sample.

        Args:
           rockarray (str array): A user-provided list of what minerals are
           contained in the sample. Example: [Ferrosilite, Peridot]

            percentarray (float array): The relative abundance of each mineral
            in the sample. Example: [50.0, 50.0]

            vel (float): The impact velocity of the sample. Example: 15.6

        Kwargs:
           None

        Returns:
           None

        Raises:
           Exceptions will be raised for an invalid format of input parameters.
           """

        # Check that each mineral has a specified abundance
        if(len(rockarray) != len(percentarray)):
            raise Exception('ERROR - NUMBER OF ROCKS MUST MATCH PERCENTAGES')
            return None

        # Make sure these abundances sum to 100
        if(np.sum(percentarray) != 100):
            raise Exception('ERROR - TOTAL PERCENTAGES MUST BE 100')
            return None

        rockarray_s = np.sort(rockarray)
        percentarray_s = np.sort(percentarray)

        # Make sure each mineral is only entered once
        if(len(np.unique(rockarray)) != len(rockarray)):
            raise Exception('ERROR - PLEASE ONLY USE EACH MINERAL ONCE!')
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
        spectrum_t = np.zeros(10_000)
        self.iso_mass = np.array(self.iso_mass).flatten().transpose()
        # iso_mass MUST be a 1-D Numpy array

        peak_times = []
        for lp in range(len(self.iso_mass)):
            peak_times.append((stretch*np.sqrt(self.iso_mass[lp] +
                                               shift)).astype(float))
            # in nanoseconds
        peak_times = np.array(peak_times)

        # Find indices of time peaks and normalize them by the sampling rate
        self.peak_positions = []
        for lp in range(len(peak_times)):
            self.peak_positions.append(np.floor(peak_times[lp]/srate))
        self.peak_positions = np.array(self.peak_positions)

        # Put arrival times into the peak positions
        for lp in range(len(lama_abund)):
            spectrum_t[self.peak_positions[lp].astype(int)] = lama_abund[lp]

        spectrum_t = [i+i*random.uniform(-1,1)/np.sqrt(2) for i in spectrum_t]
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

        # Create TOF Spectrum
        real_spectrum_t = np.convolve(spectrum_t, gx) + 2.0
        self.time_spectrum = (real_spectrum_t/max(real_spectrum_t))[:-62]
        self.time_spectrum = self.time_spectrum - min(self.time_spectrum)

        timeBase = np.arange(10_000)*2
        tmpCalc = [Decimal(x.item()) for x in timeBase]
        domain = [((a - Decimal(shift))/Decimal(stretch))**Decimal(2.0) for a
                  in tmpCalc]
        spec_max = max(real_spectrum_t)
        real_spectrum_t = real_spectrum_t/spec_max
        real_spectrum_t = real_spectrum_t[:-62]
        real_spectrum_t = real_spectrum_t - min(real_spectrum_t)

        self.domain, self.mass_spectrum = domain, real_spectrum_t

# %%PROCESS MINERAL CSV
    def unwrap_mins(self, rocks, elems_present, percentarray_s, rockarray_s):
        """Create elemental abundances from the user-provided list of minerals.

        Args:
            rocks (series): The output of
            :func:'object_spectra.Spectra.fetch_rocks'. This is a
            database of known minerals and their elemental abundances.

            elems_present (float array): The relative abundance of each element
            in the sample, calculated in the :mod:'Spectra' initialization.

            percentarray_s (float array): A sorted array of mineral abundances
            in the sample.

            rockarray_s (str array): The names of minerals in the sample
            ordered alphabetically.

        Kwargs:
           None

        Returns:
           None

        Raises:
           None
           """
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

# %%PROCESS ISOTOPE DATA
    def sort_isotopes(self, isotope_data):
        """Format the isotope labels and abundances properly for further
        analysis.

        Args:
           isotope_data (float array): An array of isotopic ratios and labels,
           the output of :func:'object_spectra.Spectra.fetch_abundances'

        Kwargs:
           None

        Returns:
           None

        Raises:
           None
           """
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

# %%CREATE A HASH OF NAMES AND MASS INDICES
    def create_isotope_pairs(self, Plot=False, Verbose=False):
        """Create a list of tuples (dictionary-style key: value pairs) to be
        used for mass line labels.
        Args:
           None

        Kwargs:
           Plot (bool): A boolean indicating whether or not the user wants to
           see a demonstration of the labels.

           Verbose (bool): A boolean representing the user's choice of whether
           or not they want real-time print statements of all relevant
           quantities.

        Returns:
           None

        Raises:
           None
           """
        # Let's get the target material in the spectrum
        if 'Ag' not in self.iso_names:
            if Verbose:
                print("Target material not detected in spectra, adding label.",
                      '\n')
            self.iso_names.append('Ag')
            self.iso_names.append('Ag')
        # Strip zeros from isotopic masses
        # self.iso_mass = [i for i in self.iso_mass if i != 0]
        self.iso_dict = [(i, j) for i, j in zip(self.iso_names,
                                                self.iso_mass)]

        if Verbose:
            print("Isotopes present in the spectra: \n", self.iso_names)
            print("Isotopic masses: \n", self.iso_mass, '\n')
            print("Generated dictionary: \n", self.iso_dict, '\n')

# %%SPLIT A SIGNAL INTO HIGH, MIDDLE & LOW CHANNELS
    def split_into_gstages(self, Plot=False, Verbose=False):
        """Split the amplitudes of the TOF signal into low, middle and high
        gain stages.

        Args:
           None

        Kwargs:
           Plot (bool): A boolean indicating whether or not the user wants to
           see a demonstration of the labels.

           Verbose (bool): A boolean representing the user's choice of whether
           or not they want real-time print statements of all relevant
           quantities.

        Returns:
           None

        Raises:
           None
           """
        low = self.mass_spectrum
        mid = self.mass_spectrum
        high = self.mass_spectrum
        maxspec = max(high)

        if(maxspec != 1.0):
            high = self.mass_spectrum/maxspec

        midcut = np.where(high <= 0.25)
        highremain = np.where(high > 0.25)
        lowcut = np.where(high <= 0.15)
        midremain = np.where(high > 0.15)

        if(Verbose):
            print("Midcut = ", midcut)
            print("Lowcut = ", lowcut)

        mid[midcut] = high[midcut]
        mid[highremain] = .25
        low[lowcut] = high[lowcut]
        low[midremain] = .15

        if(Plot):
            # Display the spectrum with high-resolution
            # plt.style.use('dark_background')
            fig = plt.figure(dpi=2000)
            fig = plt.figure()
            ax = fig.add_subplot()
            # Display spectrum in log
            # ax.set_yscale('log')
            ax.set_xlabel("Mass(u)", fontsize=15)
            ax.set_ylabel("Amplitude", fontsize=15)
            ax.set_title("Split TOF",
                         font="Times New Roman", fontweight="bold",
                         fontsize=20)
            ax.set_facecolor("white")
            plt.plot(self.domain, low, color='green', lw=1,
                     label="Low channel")
            plt.plot(self.domain, mid, color='blue', lw=1,
                     label="Middle channel")
            plt.plot(self.domain, high, color='red', lw=3,
                     label="High channel")
            plt.grid(b=None)
            plt.legend(loc="upper right")
        return low, mid, high


# %%AVOID DIVISION BY ZERO
def safe_div(x, y):
    # Function to handle division by zero "Pythonically"
    try:
        return x/y
    except ZeroDivisionError:
        return 0


# %%FETCH ISOTOPIC ABUNDANCES
def fetch_abundances():
    """
    Parameters
    ----------
    Returns
    -------
    A database of isotopic ratios.
    """
    # Get full list of all isotopes and their corresponding
    # symbols, masses and abundances
    eleabund = pd.read_csv("elementabundances.csv", header=0)
    return eleabund


# %%FETCH RELATIVE SENSITIVITY FACTORS
def fetch_rsfs():
    """
    Parameters
    ----------
    Returns
    -------
    A database of TOF_SIMS relative sensitivity factors.
    """
    # Retreve Hillier Relative Sensitivity Factors (Taken from TOF-SIMS)
    rsfs = pd.read_csv("rel_sens_fac.csv")
    rsfs.columns = ['Name', 'Sensitivity Factor']
    return rsfs


# %%FETCH MINERAL ELEMENTAL ABUNDNCES
def fetch_rocks():
    """
    Parameters
    ----------
    Returns
    -------
    A database of minerals and their added abundances.
    """
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
    """
    Parameters
    ----------
    signal : Float64 Array
        An initial numerical spectra free from noise.
    Returns
    -------
    The RMS average value of the input signal.
    """
    rms = np.sqrt(np.mean(signal**2))
    return rms


# %%ADD REALISTIC NOISE TO A SIGNAL
def add_real_noise(signal, SNR):
    """
    Parameters
    ----------
    signal : Float64 Array
        An initial numerical spectra free from noise.
    SNR : Float64
        A perscribed sigal-to-noise ratio for the added nosie
    Returns
    -------
    A synthetic TOF or mass spectra with  background noise added
    throughout. This noise has the same frequency and amplitude
    space as the instrument electronics.
    This bakcground noise was derived via fourier analysis of Peridot impact
    spectra on the Hyperdust instrument.
    """
    noise = generate_noise().astype(float)
    # scaling = np.abs(rms_val(signal)/rms_val(noise))/(SNR**2)
    scaling = np.abs(max(signal)/max(noise))/(SNR)
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
    12. Diopside
    13. Bronzite
    14. Ferrocene
    ==========================================================================
    """

    N_spectra = 500
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
                              'Silica',
                              'Diopside',
                              'Bronzite',
                              'Ferrocene'])

    # x,y = Spectra(['Albite','Anorthite'],[200/3,100/3])

    # ForSpec = Spectra(['Forsterite','Anorthite'],[200/3,100/3])

    velarr = []
    SNRarr = []
    stretchArr = []
    SNRchoice = [.1, .3, 1, 3, 10.0]
    min_name = ""
    for k in range(N_spectra):
        if(k <= 49):
            min_name = mineral_names[0]
            if(k <= 24):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]
        elif(k <= 99):
            min_name = mineral_names[1]

            if(k <= 74):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]

        elif(k <= 149):
            min_name = mineral_names[2]

            if(k <= 124):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]

        elif(k <= 199):
            min_name = mineral_names[3]

            if(k <= 174):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]

        elif(k <= 249):
            min_name = mineral_names[4]

            if(k <= 224):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]

        elif(k <= 299):
            min_name = mineral_names[5]

            if(k <= 274):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]

        elif(k <= 349):
            min_name = mineral_names[6]

            if(k <= 324):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]

        elif(k <= 399):
            min_name = mineral_names[7]

            if(k <= 374):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]

        elif(k <= 449):
            min_name = mineral_names[8]

            if(k <= 424):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]
        elif(k <= 499):
            min_name = mineral_names[9]

            if(k <= 474):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]
        elif(k <= 549):
            min_name = mineral_names[10]

            if(k <= 524):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]
        elif(k <= 599):
            min_name = mineral_names[11]

            if(k <= 574):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]
        elif(k <= 649):
            min_name = mineral_names[12]

            if(k <= 624):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]
        elif(k <= 699):
            min_name = mineral_names[13]

            if(k <= 674):
                SNR_tmp = SNRchoice[0]
            else:
                SNR_tmp = SNRchoice[0]
        # min_name = "Fayalite-Spinel"
        # min_name = "Peridot"
        # min_name = str(min_name)
        # print(min_name)
        # vel = 18*random.uniform(0, 1)+7
        vel = 20.0
        velarr.append(vel)
        # print(vel)

        # Define shift with experimental deviation
        # stretchTmp = 1350.00 + random.uniform(-5.0, 5.0)
        # stretchArr.append(stretchTmp)
        # print("Stretch parameter $\alpha = $", stretchTmp)
        # Render spectrum object
        ForSpec = Spectra([min_name], [100], 20.0)
        # ForSpec = Spectra(["Fayalite", "Spinel"], [50.0, 50.0], vel)
        # ForSpec = Spectra(["Fayalite"],[100.0], 22.0)

        # One spectra object attribute is a suitable domain for plotting
        x = ForSpec.domain
        # print("Domain (amu) = ", x)
        # The spectrum is another accesible attribute
        y = ForSpec.mass_spectrum
        # print("Mass Spectrum: \n", len(y), '\n', "TOF Spectrum\n",
        #      len(ForSpec.time_spectrum))
        # print(ForSpec.pres_min)

        # SNR_tmp = np.random.choice(SNRchoice, size=1)
        # SNR_tmp = .9
        SNRarr.append(SNR_tmp)
        y = add_real_noise(y, SNR_tmp)

        # Display the spectrum with high-resolution
        # plt.style.use('dark_background')
        # fig = plt.figure(dpi=20_000)
        fig = plt.figure()
        ax = fig.add_subplot()
        # Display spectrum in log
        ax.set_yscale('log')
        # plt.xlim(15.5, 60)
        # plt.ylim(1.0e-5, 1.0)
        ax.set_xlabel("Mass(u)", fontsize=15)
        ax.set_ylabel("Log Amplitude", fontsize=15)
        ax.set_title(r"{} at {} ".format(min_name,
                                         str(vel)) + r"$\frac{km}{s}$",
                     pad=10.0,
                     font="Times New Roman", fontweight="bold",
                     fontsize=20)
        ax.set_facecolor("white")
        ax.plot(x, y, lw=.25, c='black')
        plt.fill_between(x, y, color='gray')

        ForSpec.create_isotope_pairs(Verbose=False)
        xmin, xmax = ax.get_xlim()
        for val in ForSpec.iso_dict:
            if(xmin <= val[1] and xmax >= val[1]):
                if(val[1] != 0):
                    plt.axvline(val[1]+.35, color='green', lw=1.0, ls=':')
                    title = r"$^{{{}}}${}".format(str(round(val[1])),
                                                  str(val[0]))
                    # print(title)
                    plt.text(val[1]-.25, 1.75, title, color='green',
                             fontsize=18, rotation=90.0)

        # plt.grid(b=None)
        plt.grid(color='gray', linewidth=.5)
        fig.patch.set_facecolor('#ECECEC')
        plt.show()

        # Plot TOF Spectrum if desired
        # plt.plot(2*np.arange(10_000), ForSpec.time_spectrum)
        # plt.xlabel(r"TOF ($\mu s$)")
        # plt.ylabel("Amplitude")
        # plt.yscale('log')
        # plt.show()
        # plt.savefig(min_name+str(k+1)+".eps", dpi=1200)

        # low, mid, high = ForSpec.split_into_gstages(Plot=True)

        x = np.array(x)  # .transpose()
        y = np.array(y)  # .transpose()

        # print("x= ", x, "y= ", y)
        # Save Spectra as a csv as well
        SpecDict = {"Mass": x, "Amplitude": y}
        SpecFrame = pd.DataFrame({"Mass (amu)": x, r"Time (microseconds)":
                                  2*np.arange(10_000),
                                  "Amplitude": y})

        spec_save = str(k+1) + ".csv"
        SpecFrame.to_csv(spec_save, sep=",")

velarr = np.array(velarr)
np.savetxt("Velocities.txt", velarr)
SNRarr = np.array(SNRarr)
np.savetxt("SignaltoNoise.txt", SNRarr)
stretchArr = np.array(stretchArr)
np.savetxt("Stretch Parameter Values", stretchArr)

# Copy every file with a spectra number in its name
# call(['cp', '/Users/ethanayari/Documents/GitHub/SpectrumPy
# copy/python_dev/*{1..450}*', '/Users/ethanayari/Dropbox/IDEX
# Pipeline/python/Training_Sets/trainingset4'])