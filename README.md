# SpectrumPy

A Python library dedicated to generating numerical dust impact ionization time-of-flight mass spectra. This is an adaptation of Jon Hillier's IDL script: 

Jon K. Hillier, K. Fiege, M. Trieloff, R. Srama, Numerical modelling of mineral impact ionisation spectra, Plane-tary and Space Science,Volume 89, 2013, Pages 159-166, ISSN 0032-0633,

Author: Ethan Ayari, Institute for Modeling Plasma, Atmosphere and Cosmic Dust

Look at /html/index.html for the associated wiki page, or visit file:///Users/ethanayari/Dropbox/Mac/Documents/GitHub/SpectrumPy/python_dev/html/classobject__spectra_1_1_spectra.html to go directly to the class list.

To use this script, you will only need to edit the part of "/python_dev/object_spectra.py" below the line

if __name__ == "__main__":

To create a spectrum object, you will use a command like below:

# Sample of 50% Fayalite and 50% Spinel impacting at velocity "vel"
ForSpec = Spectra(["Fayalite", "Spinel"], [50.0, 50.0], vel)

Here, the Spectra object is a class containing the time of flight & mass spectra, present elements & isotopes, as well as other attributes of the sample. In order for this script to work, first the minerals in the sample must be given as a string array (And exist in the database). Then, the percent abundance of those minerals in the sample must be given as a float array. Finally, the velocity of the impactor is given as a float.

To access attributes of the spectrum object, use syntax similar to the below commands:
        # One spectra object attribute is a suitable domain for plotting
        x = ForSpec.domain

        # The spectrum is another accesible attribute
        y = ForSpec.mass_spectrum
        
Realistic line shapes are convolved with the stoichiometric amplitudes to give realistic line contents. Then, noise effects of the same frequencies and amplitudes as laboratory spectra are implemented to recreate what is seen at dust accelerators or in mission data. The probability of a given mass line appearing is dependent on the velocity of the impactor, as described in

K. Fiege, M. Trieloff, J.K. Hillier, M. Guglielmino, F. Postberg, R. Srama, S. Kempf, J. Blum Calibration of relative sensitivity factors for impact ionization detectors with high-velocity silicate micropar-ticles, Icarus, 241 (2014), pp. 336-345.


For any questions relating to the code, reach out to ethan.ayari@lasp.colorado.edu
