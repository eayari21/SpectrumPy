#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for postprocessing spectrum exports.

__author__      = Ethan Ayari,
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust
"""

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# import matplotlib as mpl
from scipy.fft import fft, fftfreq
from scipy.optimize import curve_fit
from statsmodels.graphics import tsaplots
from math import factorial

import warnings
warnings.filterwarnings('ignore')

# Improve figure resolution
plt.rcParams['figure.figsize'] = [10, 6]
plt.rcParams.update({'font.size': 18})
plt.style.use('seaborn')
plt.rcParams['agg.path.chunksize'] = 10000

verbose = False


# %% Gaussian function to be fit
def gaussian(x, mean, amplitude, standard_deviation):
    return amplitude * np.exp(- (x - mean)**2 / (2*standard_deviation ** 2))


# %% Fit the Gaussian
def gauss_fit(bin_heights, bin_borders, Plot=False):
    bin_centers = bin_borders[:-1] + np.diff(bin_borders) / 2
    popt, _ = curve_fit(gaussian, bin_centers, bin_heights, p0=[1., 0., 1.])
    if(Plot):
        x_interval_for_fit = np.linspace(bin_borders[0], bin_borders[-1],
                                         10000)
        plt.plot(x_interval_for_fit, gaussian(x_interval_for_fit, *popt), 'r',
                 label=r'$\mu = ${:.2f}, A = {:.2f}, $\sigma$ = {:.2f}'.format(*popt), lw=3)
        plt.legend()


# %% Simplest function to define ringing
def Ringingdecay(t, A, B, w, p):
    # A = initial amount
    # B = decay constant
    # w = angular frequency
    # p = phase shift
    # t = time

    return float(A)*np.exp(-1*float(B)*t)*np.cos(float(w)*t - float(p))


# %%
def decay(t, A, B):
    # A = initial amount
    # B = decay constant
    # t = time

    return A * np.exp(-B * t)


# %%
def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size-1)//2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window,
                                                           half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs(y[1:half_window+1][::-1] - y[0])
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve(m[::-1], y, mode='valid')


# %%
def read_hdf5(path):

    keys = []
    f = h5py.File(path, 'r')  # open file

    f.visit(keys.append)   # append all keys to list
    for key in keys:
        print(f[key].name)
        pass

    # change this to whatever you want to extract
    mass = f["/Spectra/47: 9CE8F380-E65A-4A40-9BA1-BC5E21778DF5/Time"]
    amp = f["/Spectra/47: 9CE8F380-E65A-4A40-9BA1-BC5E21778DF5/AmplitudeDenoised"]
    return mass[()], amp[()]


# %%APPEND ALL OF THE PERIDOT SPECTRA INTO MASS AND AMPLITUDE LISTS
def read_all_hdf5(path):
    amps = []
    masses = []
    times = []
    keys = []
    f = h5py.File(path, 'r')  # open file

    f.visit(keys.append)   # append all keys to list
    for key in keys:
        # print(f[key].name)
        if(str(f[key].name).endswith('Mass')):
            masses.append(f[key][()])
        if(str(f[key].name).endswith('Amplitude')):
            amps.append(f[key][()])
        if(str(f[key].name).endswith('Time')):
            times.append(f[key][()])
        pass

    return times, masses, amps


# %%
def compute_power_spectrum(fft, freq, n, ax=None, plot=False):
    psd = np.real(fft * np.conj(fft))/n  # Compute power spectrum

    if(plot):
        ax.plot(freq, psd, 'r', label="Spectral Power Density")
        ax.plot(freq, filter_psd(psd), 'g', label='Filtered SPD')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel(r"$\frac{ion numer^{2}}{Hz}$")
        # plt.yscale('log')
        plt.legend()
        plt.title("Power Spectrum", fontweight='bold', fontsize=20)
        plt.show()
    return psd


# %%
def compute_amplitude_spectrum(fft, freq, delta, n, plot=False):
    fftamps = np.sqrt(2)*np.sqrt(np.real(fft)**2 + np.imag(fft)**2)/n
    if(plot):
        plt.plot(freq, fftamps, 'b', label="Fourier Amplitude Spectrum")
        plt.xlabel('Frequency (MHz)')
        plt.ylabel("Amplitude")
        plt.yscale('log')
        plt.title("Amplitude Spectrum", fontweight='bold', fontsize=20)
        plt.show()
    return fftamps


# %%
def compute_phase_spectrum(fft, freq, plot=False):
    fftphase = (180/np.pi)*np.arctan2(np.imag(fhat), np.real(fhat))
    if(plot):
        plt.plot(freq, fftphase, 'g', label="Fourier Phase Spectrum")
        plt.xlabel('Frequency (MHz)')
        plt.ylabel("Amplitude")
        plt.yscale('log')
        plt.title("Phase Spectrum", fontweight='bold', fontsize=20)
        plt.show()
    return fftphase


# %%
def filter_psd(psd):
    return savitzky_golay(psd, 15, 4)


# %%
def reconstruct_time_series(psd, n, delta, ax=None, plot=False):

    # bigfreq = freq[np.where(psd == max(psd))]

    altpsd = np.zeros(n)  # Empty array that will be assigned our random phases
    idxs_half = np.arange(1, np.floor(n/2), dtype=int)  # first half
    psd_real = np.abs(psd[idxs_half])  # amplitude for first half
    idxs_half = np.delete(idxs_half, np.argwhere(psd_real >= .4))  # Domain too
    psd_real = psd_real[psd_real < .4]  # Delete zero frequency value

    if(plot):
        if(ax is not None):
            ax[0].plot(idxs_half, psd_real)
        else:
            plt.plot(idxs_half, psd_real)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel(r"$\frac{ion numer^{2}}{Hz}$")
        plt.title("Half of Filtered PSD", fontweight='bold', fontsize=20)
        plt.xscale('log')
        plt.show()
    for k in range(len(psd_real)):
        ak = np.random.uniform(0, 2*np.pi)
        # tmp[k] = np.exp(-1*1j*2*np.pi*(k**2)/n)
        altpsd[k] = np.sqrt(psd_real[k]/(2*n*delta))*np.exp(1j*ak)  # *tmp[k]

    reco2 = np.fft.ifft(altpsd)  # Transfer back to time domain
    dom = np.linspace(0, len(reco2)-1, len(reco2))

    if(plot):
        if(ax[1] is not None):
            ax.plot(dom, reco2)
        else:
            plt.plot(dom, reco2)
        plt.xlabel(r'Time ($\mu s$)')
        plt.ylabel("ion number")
        plt.title("Reconstructed Time Series", fontweight='bold', fontsize=20)
        plt.show()
    return reco2.real


# %%
def generate_noise(axs=None, Plot=False):
    # times, mass, amps = read_all_hdf5("/Users/ethanayari/Desktop/
    # Peridot_Jan_'21/run580(11-10).h5")
    times, mass, amps = read_all_hdf5("run580(11-10).h5")
    slices = []
    for amp in amps:
        slices.append(amp)
    delta = float(times[0][1] - times[0][0])  # Time scale value
    noise = np.concatenate(slices, axis=0)  # Array of all amplitudes
    n = len(noise)  # Sample size
    fhat = np.fft.fft(noise)  # computes the fft
    fft_fre = np.fft.fftfreq(n=noise.size, d=delta)
    if(axs is not None):
        psd = compute_power_spectrum(fhat, fft_fre, n, axs[1], plot=Plot)
        reco = reconstruct_time_series(psd, n, delta, axs[2], plot=Plot)
    else:
        psd = compute_power_spectrum(fhat, fft_fre, n, plot=Plot)
        reco = reconstruct_time_series(psd, n, delta, plot=Plot)
    return reco


# %%
def end_to_end_amps(amps, recon):
    hist, bins = np.histogram(recon, bins=1000)
    heights, borders, _ = plt.hist(recon, bins, label='Amplitude Histogram')
    plt.xlabel('Amplitude (ion number)')
    plt.ylabel('Number of Occurences')
    plt.title('Reconstructed Noise Amplitudes', fontsize=20, fontweight='bold')
    gauss_fit(heights, borders, True)
    plt.show()

    hist, bins = np.histogram(recon, bins=15)
    heights, borders, _ = plt.hist(amps, bins, label='Amplitude Histogram')
    plt.xlabel('Amplitude (ion number)')
    plt.ylabel('Number of Occurences')
    plt.title('Original Noise Amplitudes', fontsize=20, fontweight='bold')
    gauss_fit(heights, borders, True)
    plt.show()


# %%
def end_to_end_psd(freq, psd, reco, plot=False):
    delta = float(times[0][1] - times[0][0])  # Time scale value
    n = len(reco)  # Sample size
    fhat = np.fft.fft(reco)  # computes the fft
    fft_fre = np.fft.fftfreq(n=reco.size, d=delta)
    idxs_half = np.arange(1, np.floor(n/2), dtype=int)  # first half
    recondex = np.arange(1, np.floor(n/2), dtype=int)  # first half
    psd_recon = compute_power_spectrum(fhat, fft_fre, n, plot=False)
    psd_real = np.abs(psd[idxs_half])  # amplitude for first half
    recon_psd_real = np.abs(psd_recon[recondex])  # amplitude for first half
    idxs_half = np.delete(idxs_half, np.argwhere(psd_real >= .4))  # Domain too
    recon_idxs_half = np.delete(recondex, np.argwhere(recon_psd_real >=
                                                      .4*10**(-4)))
    psd_real = psd_real[psd_real < .4]  # Delete zero frequency value
    recon_psd_real = recon_psd_real[recon_psd_real < .4*10**(-4)]  # Del zero f

    if(plot):
        plt.plot(recon_idxs_half, recon_psd_real*10**4, 'r',
                 label="Reconstructed Spectral Power Density", lw=3)
        plt.plot(idxs_half, psd_real, 'cyan', label='Original SPD', lw=.5)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel(r"$\frac{ion numer^{2}}{Hz}$", fontsize=16)
        plt.xscale('log')
        plt.legend()
        plt.title("Power Spectrum Comparison", fontweight='bold', fontsize=20)
        plt.show()


# %%
def take_autocorr(timeseries, name):
    # plot autocorrelation function
    tsaplots.plot_acf(timeseries, lags=1000)
    plt.xlabel(r'Number of Lags (5ns steps)')
    plt.ylabel("Correlation")
    plt.title(name, fontweight='bold', fontsize=20)
    plt.show()


# %%
def main():
    # Read in mass and amplitude from the hdf5 export
    m_17, amp_17 = read_hdf5("run580(11-10).h5")
    # print(type(m_17),type(amp_17))
    # deriv = np.diff(amp_17)/np.diff(m_17)

    # Take a slice where we don't have lines for noise extraction
    ampslice = np.zeros(len(m_17))
    # slicedex = np.where((m_17 >= 80) & (m_17 <= 190))
    slicedex = np.where(np.logical_and(m_17 >= 6.96, m_17 <= 8.1))
    ampslice[slicedex] = amp_17[slicedex]

    lowampdex = np.where(amp_17 < max(amp_17)/4)
    ampslice = amp_17[lowampdex]

    y = fft(ampslice)
    PSD = y * np.conj(y)/len(y)
    xf = fftfreq(len(m_17), (len(m_17))/500)[:len(m_17)//2]
    x2 = np.arange(1, np.floor(len(xf / 2)), dtype='int')

    xslice = m_17[slicedex]
    yslice = 100*amp_17[slicedex]
    fitslice = xslice - xslice[0]

    parameters, covariance = curve_fit(Ringingdecay, fitslice, yslice,
                                       p0=[4.98, 6.94, 2*np.pi, (1/2)*np.pi],
                                       maxfev=100_000)
    # p0=[.015, 1.25, 2*np.pi, (1/2)*np.pi]
    # print("Parameters for fit: ", parameters)
    RingFit = Ringingdecay(fitslice, parameters[0], parameters[1],
                           parameters[2], parameters[3])
    # print("Ringing values: ", RingFit)

    # mpl.rcParams['agg.path.chunksize'] = 10000
    # fig = plt.figure(dpi=2000)
    fig = plt.figure()
    # plt.plot(m_17, amp_17, 'y')
    # print(yslice)
    plt.plot(xslice, yslice, 'r', lw=3, label="Ringing Line")
    # plt.plot(xslice, RingFit, color='g', lw=3, label="Ringing Fit")

    plt.axhline(y=0.0, color='b', linestyle='dashdot', label="baseline")

    # plt.yscale('log')
    plt.xlabel("Mass (u)")
    plt.ylabel("Amplitude")
    plt.title("$^{7} Li$ Line for Peridot Spectra 20", fontweight="bold")
    plt.show()

    df = pd.DataFrame({"Mass": xslice, "Amplitude": yslice})
    df.to_csv("Li-spec32.csv", index=False)
    # plt.hist(ampslice)
    # plt.show()

    plt.plot(xf,
             y, 'r', lw=.08)

    # print(y)
    # plt.plot(m_17[:-1],deriv, 'r')
    # plt.ylim(10e-5,1.0)

    # Plot in log to look like Spectrum
    # plt.yscale('log')
    plt.xlabel("frequency")
    plt.ylabel("Amplitude")
    plt.title("Peridot White Noise", fontweight='bold')
    plt.show()
    plt.plot(xf[x2], PSD[x2], 'r', lw=2.0)

    # print(y)
    # plt.plot(m_17[:-1],deriv, 'r')
    # plt.ylim(10e-5,1.0)

    # Plot in log to look like Spectrum
    plt.yscale('log')
    plt.xlabel("Frequency")
    plt.ylabel("Power Spectrum")
    plt.title("Peridot White Noise", fontweight='bold')
    plt.show()
    np.savetxt("Powerspectrum.txt", np.real(PSD[x2]))
    np.savetxt("Frequencies.txt", np.real(xf[x2]))

    # plot autocorrelation function
    tsaplots.plot_acf(ampslice, lags=100)
    plt.show()


# %%
if __name__ == '__main__':
    # main()
    """
    times, mass, amps = read_all_hdf5("run580(11-10).h5")

    timearr = []
    for time in times:
        timearr.append(time)
    timearr = np.concatenate(np.array(timearr), axis=0)
    if(verbose):
        print("Masses: ", mass)
        print("Amplitudes: ", amps)

    slices = []
    for amp in amps:
        slices.append(amp)

    delta = float(times[0][1] - times[0][0])  # Time scale value
    noise = np.concatenate(slices, axis=0)  # Array of all amplitudes
    n = len(noise)  # Sample size
    fhat = np.fft.fft(noise)  # computes the fft
    fft_fre = np.fft.fftfreq(n=noise.size, d=delta)

    psd = compute_power_spectrum(fhat, fft_fre, n, plot=False)
    phase = compute_phase_spectrum(fhat, fft_fre, plot=False)
    fftamps = compute_amplitude_spectrum(fhat, fft_fre, delta, n, plot=False)
    psd = filter_psd(psd)
    reco = reconstruct_time_series(psd, n, delta, plot=True)
    end_to_end_amps(noise, reco)
    end_to_end_psd(fft_fre, psd, reco, plot=True)

    take_autocorr(reco, "Reconstructed Time Series")
    take_autocorr(noise, "Original Time Series")

    # freq = (1/(delta*n)) * np.arange(n)  # frequency array
    # Take one half of the power spectrum, assum the square root of the
    # integral is the RMS value of the random noise
"""
    times, amps = read_hdf5("run580(11-10).h5")
    timearr = []
    for time in times:
        # print(time)
        timearr.append(time)
    # timearr = np.concatenate(np.array([timearr]), axis=0)

    amparr = []
    for amp in amps:
        amparr.append(amp)
    # amparr = np.concatenate(np.array(amparr), axis=0)
    plt.plot(timearr, amparr)
    SpecFrame = pd.DataFrame({r"Time seconds": timearr,
                              "Amplitude (ion number)": amparr})
    SpecFrame.to_csv("AmpvsMass.csv", sep=",")
