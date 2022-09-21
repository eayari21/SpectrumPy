#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ion grid and target waveform analysis
__author__      = Ethan Ayari, Jamey Szalay
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust

Works with Python 3.9
"""

# %%DEPENDENCIES
from decimal import DivisionByZero
from scipy.optimize import curve_fit
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %%DEPENDENCIES
plt.style.use('seaborn-white')

# plt.rcParams['font.family'] = 'DejaVuSerif-BoldItalic'
# plt.rcParams['font.serif'] = 'DejaVuSerif-BoldItalic'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 12
plt.rcParams['agg.path.chunksize'] = 10_000

# %%ALTERNATE ION GRID FUNCTION DEFINITON
def AlterIDEXIonGrid(x, P0, P1, P2, P3, P4, P5, P6):
    return P1 - np.heaviside(P0-x, 0) * P2 * np.exp(-(((x-P0)**2.0)/P3**2.0) ) + np.heaviside(x-P0, 0) * ( P4 * (1.0 - np.exp(-(x-P0)/P5)) * np.exp( -(x-P0)/P6) - P2)

# %%ALTERNATE ION GRID FUNCTION DEFINITON
def IDEXTarget(x, P0, P1, P2, P3, P4, P5, P6):
    P2 = 0.0
    print(P1)
    return P1 - np.heaviside(P0-x, 0) * P2 * np.exp(-(((x-P0)**2.0)/P3**2.0) ) + np.heaviside(x-P0, 0) * ( P4 * (1.0 - np.exp(-(x-P0)/P5)) * np.exp( -(x-P0)/P6) - P2)


# %%SET UP INTERACTIVE PLOT
class ImpactEvent:

    # %%
    def __init__(self, ionGridTime, ionGridAmp, traceNum = ""):
        """A class to hold every data source and
        derived quantities for each impact event.

        Args:
           ionGridTime (float): The time domain of the ion grid signal
           ionGridAmp (float): The amplitude array
           ionGridUnits (str): Unit of the ion grid amplitude (V,dN, ...)


        Kwargs:
           None

        Returns:
           A catalog of impact event information

        Raises:
           None
           """
        self.x, self.y = ionGridTime, ionGridAmp
        self.traceNum = int(traceNum)
        self.pre = -3.0e-5  # Before image charge
        self.yBaseline = self.y.where(self.x < self.pre)
        self.yImage = self.y[(self.x.values >= self.pre) & (self.x.values < 0.0)]
        self.ionError = self.yBaseline.std()
        self.ionErrorVector = pd.DataFrame([np.nan] * len(self.yBaseline))
        self.ionMean = self.yBaseline.mean()
        self.yBaseline -= self.ionMean
        self.parameters = []

    # %%
    def fitIonSignal(self):

        # %% Initial Guess for the parameters of the ion grid signal
        t0 = 0.0                         # P[0] time of impact
        c = 0.                           # P[1] Constant offset
        b = np.abs(min(self.yImage))     # P[2] Image amplitude
        # b = .01
        s = 4.e-6                        # P[3] Image pulse width
        A  = np.abs(min(self.y) - max(self.y))     # P[4] amplitude (v)
        # A = .05
        t1 = 4.3e-5                      # P[5] rise  time (s)
        t2 = 4.3e-4                      # P[6] discharge time (s)
        c = 0


        ionTime = np.array(self.x.apply(lambda x: float(x)))
        ionAmp = np.array(self.y.apply(lambda x: float(x)))

        param, param_cov = curve_fit(AlterIDEXIonGrid, ionTime, ionAmp, p0=[t0, c, b, s, A, t1, t2])
        self.parameters = param
        self.IonAmp = param[4]
        self.IontRise = param[5]
        self.IontDecay = param[6]
        # param = [t0, c, b, s, A, t1, t2]
        self.result = AlterIDEXIonGrid(ionTime, param[0], param[1], param[2], param[3], param[4], param[5], param[6])

    # %%
    def fitTargetSignal(self):

        # %% Initial Guess for the parameters of the target signal
        t0 = 0.0                          # P[0] time of impact
        c = self.yBaseline + self.ionMean # P[1] Constant offset
        b = np.abs(min(self.yImage))      # P[2] Image amplitude
        # b = .01
        s = 4.e-6                         # P[3] Image pulse width
        A  = np.abs(min(self.y) - max(self.y))      # P[4] amplitude (v)
        # A = .05
        t1 = 4.3e-5                       # P[5] rise  time (s)
        t2 = 4.3e-4                       # P[6] discharge time (s)
        c = 0

        try:
            if(b/self.ionError < 2.0):
                b = 0.0
        except DivisionByZero:
            if(b <= .0001):
                b = 0.0



        ionTime = np.array(self.x.apply(lambda x: float(x)))
        ionAmp = np.array(self.y.apply(lambda x: float(x)))

        param, param_cov = curve_fit(IDEXTarget, ionTime, ionAmp, p0=[t0, c, b, s, A, t1, t2])
        self.parameters = param

        self.TargetAmp = param[4]
        self.TargettRise = param[5]
        self.TargettDecay = param[6]
        # param = [t0, c, b, s, A, t1, t2]
        self.result = IDEXTarget(ionTime, param[0], param[1], param[2], param[3], param[4], param[5], param[6])

    # %%
    def plotIonSignalFit(self):
        # plt.plot(wave_6["Time (s)"].head(len(self.yBaseline)), self.yBaseline, label="Ion Baseline")
        # plt.plot(wave_6["Time (s)"].head(len(self.yBaseline)), targetBaseline, label="Target Baseline")
        # plt.plot(wave_6["Time (s)"], AlterIDEXIonGrid(ionTime, t0, c, b, s, A, t1, t2), label="First Guess")
        # plt.plot(timeSlice, ampSlice)
        plt.style.use('seaborn-pastel')
        # fig = plt.figure(dpi=2000)
        plt.cla()
        plt.clf()
        plt.xlabel("Time (s)", fontsize=15)
        plt.ylabel("Voltage (V)", fontsize=15)
        plt.plot(self.x, self.y, label="Ion Grid (V)")
        plt.plot(self.x, self.result, label = "Fit (V)")
        plt.figtext(0.5, 0.2,
            r"Amplitude: %.2e V, $\tau_{Rise}$: %.2e s, $\tau_{Discharge}$: %.2e s"%(self.IonAmp, self.IontRise, self.IontDecay),
            horizontalalignment ="center", 
            verticalalignment ="center", 
            wrap = True, fontsize = 14, 
            color ="orange")
        plt.title("Ion Grid Signal Fit number {}".format(str(self.traceNum+1)), fontweight='bold', fontsize=20)
        plt.legend(loc='best')
        plt.savefig("IonGrid{}.png".format(str(self.traceNum+1)))
        print(self.parameters)
        with open("IonFitResults.txt", "a") as f1:
            f1.write("Trace {}: t0={} s, c={} V, b={} V, s={} s, A={} V, t1={} s, t2={} s \n".format(str(self.traceNum+1), self.parameters[0], self.parameters[1], self.parameters[2], self.parameters[3], self.parameters[4], self.parameters[5], self.parameters[6]))
            f1.write('\n')

    # %%
    def plotTargetSignalFit(self):
        # plt.plot(wave_6["Time (s)"].head(len(self.yBaseline)), self.yBaseline, label="Ion Baseline")
        # plt.plot(wave_6["Time (s)"].head(len(self.yBaseline)), targetBaseline, label="Target Baseline")
        # plt.plot(wave_6["Time (s)"], AlterIDEXIonGrid(ionTime, t0, c, b, s, A, t1, t2), label="First Guess")
        # plt.plot(timeSlice, ampSlice)

        plt.xlabel("Time (s)", fontsize=15)
        plt.ylabel("Voltage (V)", fontsize=15)
        plt.plot(self.x, self.y, label="Target (V)")
        plt.plot(self.x, self.result, label = "Fit (V)")
        plt.legend()
        plt.title("Target Grid Signal Fit{}".format(str(self.traceNum)), fontsize=20)
        plt.show()


# %%EXECUTABLE CODE BELOW
if __name__ == "__main__":

    """
     # %%
    wave_6 = pd.read_csv("SUDAIonTarget6.csv")
    wave_10 = pd.read_csv("SUDAIonTarget10.csv")
    wave_11 = pd.read_csv("SUDAIonTarget11.csv")
    wave_12 = pd.read_csv("SUDAIonTarget12.csv")

# Logic for if there's an image charge or not, and 
# 
# logic for ion vs. target grid
#
# Plot the rise time (calculate from line 32 of LDEX_fit_iev.pro)
#
# Find 10% and 90% of amplitude of fit, ∆t between those two points
    y = -1*wave_12["Target Amplitude (V)"]
    x = wave_12["Time (s)"]
    impact6 = ImpactEvent(x, y)
    impact6.fitTargetSignal()
    impact6.plotTargetSignalFit()

    y = -1*wave_11["Target Amplitude (V)"]
    x = wave_11["Time (s)"]
    impact6 = ImpactEvent(x, y)
    impact6.fitTargetSignal()
    impact6.plotTargetSignalFit() 
"""


"""
y = ( p[0] + p[1]*[x] + p[2]*[x**2] + p[3]*sqrt(x) +
		 p[4]*log(x))
   fa = {'x':x, 'y':y, 'err':err}
   m = mpfit('myfunct', p0, functkw=fa)
   print 'status = ', m.status
   if (m.status <= 0): print 'error message = ', m.errmsg
   print 'parameters = ', m.params"""


# %%
"""
parinfo = [{'value':0., 'fixed':0, 'limited':[0,0], 'limits':[0.,0.]} 
 												for i in range(7)]

parinfo[4]['limited'][0] = 1
parinfo[4]['limits'][0]  = 0.
values = [t0, c, b, s, A, t1, t2]
for i in range(7): parinfo[i]['value']=values[i]

 # Place constraints on t0
parinfo[0]['limited'] = [1, 1]
parinfo[0]['limits]'] = [10e-5, 18.e-5]

# Make time constants positive
parinfo[3].limited = 1
parinfo[3].limits = [0.,30.e-5]
parinfo[5].limited = 1
parinfo[5].limits = [0.,50.e-5]
parinfo[6].limited = 1 
parinfo[6].limits = [0.,1000.e-5]    
"""