#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test code for velocity-dependent mass line appearance.

__author__ = Ethan Ayari,
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust

"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


plt.style.use('seaborn-darkgrid')

# Improve figure resolution
plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True


# %%ARCTAN APPROXIMATION TO FERMI DISTRIBUTION FOR FITTING
def atan_approx(E, a, b, c):

    # Canonical function to fit is y = (1/3)*(np.arctan(x - 10) + 1.5)
    # This best defines a PDF that resembles the curves in Fiege et. al

    return (1/3)*(np.arctan(E - b) + c)


"""
#%%
def prob_appear(E, fermi, T):
    fermi = 1.0
    T = 300
    kB = 8.6173303e-5
    fout = []

    gout = 1 - (1 / (1 + (np.exp(E / (kB * T)))))


    for i in range(len(E)):
        if(E[i] < fermi):
            bound =  1 + -1 / (1 + np.exp((E[i] - fermi) / (kB * T)))
            fout.append(bound)
            #print('y')
        else:
            ubound = 1 - np.exp(-(E[i] - fermi) / (kB * T)) / (1 +
                                        np.exp(-(E[i] - fermi) / (kB * T)))
            fout.append(ubound)
            #print('n')



    fout = np.array(fout)
    return fout
"""


# %%MONTE CARLO NUMBER
def mcnumber():
    return np.random.random(1)[0]


# %%FIND NEAREST INDEX TO A VALUE IN AN ARRAY
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).nanargmin()
    return array[idx]


# %%FUNCTION TO FIND THE INDEX AND VALUE OF NEAREST ITEM IN AN ARRAY
def nearest_idx(array, value):

    idx = (np.abs(array - value)).argmin()

    return idx


# %%MONTE CARLO WEIGHTING
def line_appear(elem_name, vel):

    if(vel >= 20):
        return 1.0

    # print(elem_name, vel)

    # Create a samle velocity domain and find the nearest
    # index to passed velocity
    vel_domain = np.linspace(0, 20, 1000)
    v_indx = nearest_idx(vel_domain, vel)

    # Define a simple database to reference everything
    elements = {
        'Element Names': ['H', 'C', 'O', 'Mg', 'Al', 'Si', 'Ca', 'Fe'],
        '50% Velocity (km/s)': [8.9, 9.8, 14.4, 5.5, 5.7, 8.5, 4.6, 8.4],
        'Ionization Energy (eV)': [13.6, 11.26, 13.6, 7.64, 5.99, 8.15, 6.11,
                                   7.9],
        'Ionization Efficiency (eV)': [13.6, 11.26, 13.6, 7.64, 5.99,
                                       8.15, 6.11, 7.9],
        '10% Velocity (km/s)': [6.6, 6.9, 12.2, 4.1, 4.1, 6.2, 3.9, 6.7],
        '90% Velocity (km/s)': [12.0, 12.7, 17.0, 7.4, 7.8, 11.6, 5.5, 10.6]
    }

    # Is the provided elemnt in the database?
    if(elem_name in elements['Element Names']):

        elem_index = elements['Element Names'].index(elem_name)
        # print(elem_index)

        # Fetch velocities for 10, 50 and 90 percent
        # Fiege et. al. probabilities from the database
        tval = elements['10% Velocity (km/s)'][elem_index]
        fval = elements['50% Velocity (km/s)'][elem_index]
        nval = elements['90% Velocity (km/s)'][elem_index]

        vel_vals = np.array([tval, fval, nval])
        prob_vals = np.array([.1, .5, .9])

        # Fit coefficients of arctan functions by passing in the function,
        # the x data, the y data, and finally an initial
        # Estimate for the parameters, I use [(1/3), 10, 1.5]
        parameters, covariance = curve_fit(atan_approx, vel_vals, prob_vals,
                                           p0=[(1/3), 10, 1.5])

        # Estimate probability using above PDF and given velocity
        g = atan_approx(vel_domain, parameters[0], parameters[1],
                        parameters[2])

        # print("Probability of Mass Line Appearance: ", g[v_indx])
        # Compare to a uniform random number
        rand = mcnumber()
        if(rand <= .5 + g[v_indx]):
            # print(elem_name, " mass line appears.")

            # If this is true the line appears, scale the
            # amplitude by the TOF-SIMS-like ionization efficiency
            # SIMS-like efficiencies given in
            # Table 2 of Hornung and Kissel (1994)
            sims = np.array(elements['Ionization Efficiency (eV)'])
            weight = float((1.5)*sims[elem_index]/max(sims))

            return weight

        else:
            # Mass line no longer appears
            # print(elem_name, " mass line does not appear.")
            return 0


# %%LINE APPEARANCE TEST CODE
if __name__ == "__main__":

    vel = np.linspace(0, 20, 1000)
    # y = prob_appear(vel, 15, 293)
    y = atan_approx(vel, (1/3), 10, 1.5)

    # Define a simple database to reference everything
    elements = {
        'Element Names': ['H', 'C', 'O', 'Mg', 'Al', 'Si', 'Ca', 'Fe'],
        '50% Velocity (km/s)': [8.9, 9.8, 14.4, 5.5, 5.7, 8.5, 4.6, 8.4],
        'Ionization Energy (eV)': [13.6, 11.26, 13.6, 7.64, 5.99, 8.15,
                                   6.11, 7.9],
        'Ionization Efficiency (eV)': [13.6, 11.26, 13.6, 7.64, 5.99, 8.15,
                                       6.11, 7.9],
        '10% Velocity (km/s)': [6.6, 6.9, 12.2, 4.1, 4.1, 6.2, 3.9, 6.7],
        '90% Velocity (km/s)': [12.0, 12.7, 17.0, 7.4, 7.8, 11.6, 5.5, 10.6]
    }

    vel_vals = np.array([elements['10% Velocity (km/s)'][0],
                         elements['50% Velocity (km/s)'][0],
                         elements['90% Velocity (km/s)'][0]])
    prob_vals = np.array([.1, .5, .9])

    # Fit coefficients of arctan functions by passing in the function,
    # the x data, the y data, and finally an initial
    # estimate for the parameters, I use [(1/3), 10, 1.5]
    parameters, covariance = curve_fit(atan_approx, vel_vals,
                                       prob_vals, p0=[(1/3), 10, 1.5])

    g = atan_approx(vel, parameters[0], parameters[1], parameters[2])

    fig = plt.figure(dpi=2000)
    ax = fig.add_subplot()
    ax.set_xlabel("Velocity (km/s)")
    ax.set_ylabel("Line Appearance Probability (%)")
    ax.set_title("Hydrogen Appearance Probability vs. Velocity",
                 fontweight='bold')

    plt.scatter(vel_vals, prob_vals, c='r', s=20, label="Fitted data")

    plt.plot(vel, g, label="Fitted Fermi")

    plt.plot(vel, y, label="Original Fermi")

    plt.legend(loc='best')
