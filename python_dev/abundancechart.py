#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a GUI wrapper for SpectrumPY
__author__      = Ethan Ayari,
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust
"""

# import re

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk

from object_spectra import Spectra, add_real_noise
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

# %%SET GLOBAL PLOT VARIABLES
window = tk.Tk()
window.attributes('-fullscreen', True)

min_one_name = tk.StringVar()
min_two_name = tk.StringVar()
snr_val = tk.StringVar()
noise_present = tk.BooleanVar()
noise_present.set(False)

min_one_abundance = tk.Scale(window, label="Abundance One",
                             from_=0, to=100)
min_one_abundance.set(50)

min_two_abundance = tk.Scale(window, label="Abundance Two",
                             from_=0, to=100)
min_two_abundance.set(50)

fig = plt.figure(figsize=(8, 4))
ax = plt.axes()
# ax = plt.axes()
# Display spectrum in log
ax.set_yscale('log')
ax.set_xlabel("Mass(u)", fontsize=15)
ax.set_ylabel("Amplitude", fontsize=15)
ax.set_facecolor("white")

canvas = FigureCanvasTkAgg(fig, master=window)
# creating the Matplotlib toolbar
toolbar = NavigationToolbar2Tk(canvas, window)


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


# %%DISPLAY ELEMENTAL ABUNDANCES
def display_els(ForSpec):
    min_name = "Enstatite"
    pres_abunds = ForSpec.pres_abunds
    x = np.arange(1, len(pres_abunds)+1)
    # print(x)
    ax1 = plt.subplot()
    ax1.set_xticks(x)

    y = pres_abunds

    # plot bar chart

    plt.bar(x, y)

    # Define tick labels

    ax1.set_xticklabels(str(ForSpec.els))
    plt.xlabel("Element Name")
    plt.ylabel(r"Abundance $(\%)$")
    plt.title(min_name, fontsize=20, fontweight='bold')

    # Display graph

    plt.show()


# %%COMMAND TO ADD NOISE
def noise_switch():
    if(noise_present):
        print("Noise has been turned on")
    else:
        print("Noise has been turned off")
    # noise_present.set(True)
    generate_spectra()


# %%UPDATE INTERACTIVE PLOT
def generate_spectra():
    try:
        canvas.get_tk_widget().pack_forget()
    except AttributeError:
        pass
    one_name = min_one_name.get()
    two_name = min_two_name.get()
    one_abun = min_one_abundance.get()
    two_abun = min_two_abundance.get()

    # print("Mineral one : " + one_name, one_abun, "%")
    # print("Mineral two : " + two_name, two_abun, "%")

    min_name = np.array([one_name, two_name])
    pres_abunds = np.array([float(one_abun), float(two_abun)])

    spectra = Spectra(min_name, pres_abunds, 20.0)

    # One spectra object attribute is a suitable domain for plotting
    x = spectra.domain

    # The spectrum is another accesible attribute
    y = spectra.mass_spectrum
    y = y[:-62]
    y = y - min(y)

    if(noise_present.get()):
        print("Adding Noise")
        y = add_real_noise(y, float(snr_val.get()))

    ax.set_title("{} % {} and {}% {}".format(str(one_abun), one_name,
                                             str(two_abun), two_name),
                 font="Times New Roman", fontweight="bold", fontsize=20)

    ax.plot(x, y, lw=1, c='r')
    plt.grid(b=None)
    # creating the Tkinter canvas
    # containing the Matplotlib figure

    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()
    toolbar.update()

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()


# %%GENERATE BASIC GUI
def basic_gui():
    # window = tk.Tk()
    window.title("SpectrumPY GUI")
    window.configure(background='#00008B')

    quit_button = tk.Button(window, text='Quit App',
                            command=window.destroy,
                            font=('calibre', 20, 'bold'), fg="black",
                            bg="orange")

    # creating a label for
    # name using widget Label
    name_one_label = tk.Label(window, text='Mineral One Name',
                              font=('calibre', 20, 'bold'), fg="black",
                              bg="orange")

    # creating a entry for input
    # name using widget Entry
    name_one_entry = tk.Entry(window, textvariable=min_one_name,
                              font=('calibre', 20, 'normal'), fg="blue",
                              bg="orange")

    # creating a label for password
    name_two_label = tk.Label(window, text='Mineral Two Name',
                              font=('calibre', 20, 'bold'), fg="black",
                              bg="orange")

    # creating a entry for password
    name_two_entry = tk.Entry(window, textvariable=min_two_name,
                              font=('calibre', 20, 'normal'), fg="blue",
                              bg="orange")

    # creating a button using the widget
    # Button that will call the generate_spectra function
    sub_btn = tk.Button(window, text='Generate Spectra',
                        command=generate_spectra, font=('calibre', 20,
                                                        'bold'), fg="blue",
                        bg="red")

    noise_btn = tk.Checkbutton(window, text='Generate Noise',
                               variable=noise_present,
                               command=noise_switch, onvalue=True,
                               offvalue=False, font=('calibre', 20, 'bold'),
                               fg="blue", bg="red")
    noise_present.set(False)

    # creating a label for
    # snr using widget Label
    snr_label = tk.Label(window, text='Signal to Noise Ratio',
                         font=('calibre', 20, 'bold'), fg="black",
                         bg="orange")

    snr_entry = tk.Entry(window, textvariable=snr_val,
                         font=('calibre', 20, 'normal'), fg="blue",
                         bg="orange")
    # placing the label and entry in the required position using grid method
    # name_one_label.grid(row=0, column=0)
    # name_one_entry.grid(row=0, column=1)
    # name_two_label.grid(row=1, column=0)
    # name_two_entry.grid(row=1, column=1)
    # sub_btn.grid(row=2, column=1)

    name_one_label.pack(side="left")
    name_one_entry.pack(side="left")
    min_two_abundance.pack(side="right")

    name_two_entry.pack(side="right")
    name_two_label.pack(side="right")

    snr_label.pack(side="top", anchor="e")
    snr_entry.pack(side="top", anchor="e")

    sub_btn.pack(side="bottom", anchor="n", fill="both")
    min_one_abundance.pack(side="left")

    quit_button.pack(side="bottom", anchor="s", fill="both")
    noise_btn.pack(side="top", anchor="w")

    window.mainloop()


"""
# %%GENERATE INTERACTIVE PLOT
def spectrumGUI():
    min_names = ["Ferrosilite", "Enstatite", "Fayalite", "Forsterite",
                 "Anorthite", "Albite", "Magnesiohornblende",
                 "Ferrohornblende", "Spinel"]
    # Create two bounded text boxes for the mineral abundances
    mineral_one_abundance = widgets.BoundedFloatText(
        value=50.0,
        min=0.0,
        max=100.0,
        step=1.0,
        description=r'Mineral 1 Abundance $(%)$',
        disabled=False,
        color='black'
    )
    mineral_two_abundance = widgets.BoundedFloatText(
        value=100.0 - float(mineral_one_abundance.value),
        min=0.0,
        max=100.0,
        step=1.0,
        description=r'Mineral 1 Abundance $(%)$',
        disabled=False,
        color='black'
    )

    # Make a dropdown to select the Area, or "All"
    min_one_name = widgets.Dropdown(
        options=min_names,
        value=min_names[2],
        description='Mineral one:',
    )
    # Make a dropdown to select the Area, or "All"
    min_two_name = widgets.Dropdown(
        options=min_names,
        value=min_names[0],
        description='Mineral two:',
    )

    vel = widgets.BoundedFloatText(
        value=20.0,
        min=0.0,
        max=100.0,
        step=0.1,
        description='Impact Velocity (km/s)',
        disabled=False,
        color='black'
    )
    ForSpec = Spectra([min_one_name.value, min_two_name.value],
                      [mineral_one_abundance.value,
                       mineral_two_abundance.value], vel.value)

    # One spectra object attribute is a suitable domain for plotting
    x = ForSpec.domain

    # The spectrum is another accesible attribute
    y = ForSpec.mass_spectrum
    y = y[:-62]
    y = y - min(y)
    # Display the spectrum with high-resolution
    # plt.style.use('dark_background')

    # Display spectrum in log
    ax.set_yscale('log')
    ax.set_xlabel("Mass(u)", fontsize=15)
    ax.set_ylabel("Amplitude", fontsize=15)
    # ax.set_title("{:.2f}%/{:.2f}% Fayalite-Spinel Mixture".format(fay_abun,
    #              spin_abun),
    #             font="Times New Roman", fontweight="bold", fontsize=20)
    ax.set_title("Tester", font="Times New Roman", fontweight="bold",
                 fontsize=20)
    ax.set_facecolor("white")
    plt.plot(x, y, lw=1, c='r')
    plt.grid(b=None)
    fig.tight_layout()
    fig.subplots_adjust(left=0.05, bottom=0.07, right=0.95,
                        top=0.95, wspace=0, hspace=0)

    # mng = plt.get_current_fig_manager()
    # mng.full_screen_toggle()
    canvas_frame.pack(side=TOP, expand=True)

    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

    toolbar.update()
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
    button = tkinter.Button(master=window, text="Quit", command=_quit)
    button.pack(side=tkinter.BOTTOM)

    tkinter.mainloop()

def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)


def _quit():
    window.quit()     # stops mainloop
    window.destroy()  # this is necessary on Windows to prevent
"""


# %%GENERATE ABUNDANCE CHARTS
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
    ==========================================================================
"""
    # spectrumGUI()
    basic_gui()
