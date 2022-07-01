#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a GUI wrapper for SpectrumPY
__author__      = Ethan Ayari,
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust
"""

# import re
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
import peakdecayscript as pds

from PIL import ImageTk, Image
from object_spectra import Spectra, add_real_noise
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
min_w = 50  # Minimum width of the frame
max_w = 200  # Maximum width of the frame
cur_width = min_w  # Increasing width of the frame
expanded = False  # Check if it is completely exanded


# %%GUI MASTER CLASS
class SpectrumPYApp():
    def __init__(self):
        super().__init__()
        # %%SET GLOBAL PLOT VARIABLES
        self.window = tk.Tk()

        self.window.geometry('')

        # Define the icons to be shown and resize it
        self.home = ImageTk.PhotoImage(Image.open('home.png').resize((30, 30),
                                                                     Image.ANTIALIAS))
        self.settings = ImageTk.PhotoImage(Image.open('settings.png').resize((30, 30),
                                                                     Image.ANTIALIAS))
        self.ring = ImageTk.PhotoImage(Image.open('ring.png').resize((30, 30),
                                                                     Image.ANTIALIAS))

        menubar = tk.Menu(self.window)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Project", command=self.donothing)
        filemenu.add_command(label="Open Scope File", command=self.donothing)
        filemenu.add_command(label="Save Plot", command=self.donothing)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=self.donothing)
        helpmenu.add_command(label="About...", command=self.donothing)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.window.config(menu=menubar)

        self.window.attributes('-fullscreen', False)

        img = tk.Image("photo", file="impact.png")
        self.window.call("wm", "iconphoto", self.window._w, img)

        iconfile = os.getcwd() + "/impact.ico"
        self.window.iconbitmap(iconfile)

        self.window.title("SpectrumPY GUI")
        self.window.configure(background='#00008B')
        # self.window.conself.figure(background='black')

        impimage = Image.open("impact.png")
        logo = ImageTk.PhotoImage(impimage)

        laspimage = Image.open("lasplogo.png")
        lasplogo = ImageTk.PhotoImage(laspimage)

        imapimage = Image.open("IMAPlogo.png")
        imaplogo = ImageTk.PhotoImage(imapimage)

        self.logolabel = tk.Label(image=logo)
        self.logolabel.image = logo

        self.lasplogolabel = tk.Label(image=lasplogo)
        self.lasplogolabel.image = lasplogo

        self.imaplogolabel = tk.Label(image=imaplogo)
        self.imaplogolabel.image = imaplogo

        self.quit_button = tk.Button(self.window, text='Quit App',
                                     command=self.window.destroy,
                                     font=('calibre', 20, 'bold'), fg="black",
                                     bg="orange")

        # creating a label for
        # name using widget Label
        self.name_one_label = tk.Label(self.window, text='Mineral One Name',
                                       font=('calibre', 20, 'bold'),
                                       fg="black",
                                       bg="orange")
        self.name_two_label = tk.Label(self.window, text='Mineral Two Name',
                                       font=('calibre', 20, 'bold'),
                                       fg="black",
                                       bg="orange")
        # creating a entry for input
        # name using widget Entry
        mineral_names = ['Albite',
                         'Anorthite',
                         'Enstatite',
                         'Fayalite',
                         'Ferrohornblende',
                         'Ferrosilite',
                         'Forsterite',
                         'Magnesiohornblende',
                         'Spinel',
                         'Peridot',
                         'Silica']

        self.min_one_name = tk.StringVar()
        self.min_two_name = tk.StringVar()

        self.snr_val = tk.StringVar()
        self.vel_val = tk.StringVar()
        self.vel_val.set("20.0")

        self.noise_present = tk.BooleanVar()
        self.noise_present.set(False)

        self.split_gains = tk.BooleanVar()
        self.split_gains.set(False)

        self.min_one_abundance = tk.Scale(self.window, label="Abundance One",
                                          from_=0, to=100)
        self.min_one_abundance.set(50)

        self.min_two_abundance = tk.Scale(self.window, label="Abundance Two",
                                          from_=0, to=100)
        self.min_two_abundance.set(50)

        self.name_one_entry = tk.OptionMenu(self.window, self.min_one_name,
                                            *mineral_names)

        self.name_two_entry = tk.OptionMenu(self.window, self.min_two_name,
                                            *mineral_names)

        # creating a button using the widget
        # Button that will call the generate_spectra function
        self.sub_btn = tk.Button(self.window, text='Generate Spectra',
                                 command=self.generate_spectra, font=(
                                     'calibre', 20, 'bold'),
                                 fg="blue",
                                 bg="red")

        self.fft_btn = tk.Button(self.window, text='Noise Panel',
                                 command=self.analyze_noise, font=(
                                     'calibre', 20, 'bold'),
                                 fg="blue",
                                 bg="red")

        self.noise_btn = tk.Checkbutton(self.window, text='Generate Noise',
                                        variable=self.noise_present,
                                        command=self.noise_switch,
                                        onvalue=True,
                                        offvalue=False, font=('calibre', 20,
                                                              'bold'),
                                        fg="blue", bg="red")
        self.noise_present.set(False)

        self.gainsplit_btn = tk.Checkbutton(self.window,
                                            text='Split Over Gain Stages',
                                            variable=self.split_gains,
                                            command=self.divide_into_gains,
                                            onvalue=True,
                                            offvalue=False, font=('calibre',
                                                                  20,
                                                                  'bold'),
                                            fg="blue",
                                            bg="red")
        self.split_gains.set(False)

        # creating a label for
        # snr using widget Label
        self.snr_label = tk.Label(self.window, text='Signal to Noise Ratio',
                                  font=('calibre', 20, 'bold'), fg="black",
                                  bg="orange")

        self.snr_entry = tk.Entry(self.window, textvariable=self.snr_val,
                                  validate="focusout",
                                  # validatecommand=self.generate_spectra,
                                  font=('calibre', 20, 'normal'), fg="blue",
                                  bg="orange")

        self.vel_label = tk.Label(self.window, text='Impact Velocity (km/s)',
                                  font=('calibre', 20, 'bold'), fg="black",
                                  bg="orange")

        self.vel_entry = tk.Entry(self.window, textvariable=self.vel_val,
                                  validate="focusout",
                                  # validatecommand=self.generate_spectra,
                                  font=('calibre', 20, 'normal'), fg="blue",
                                  bg="orange")

        # img = ImageTk.PhotoImage(Image.open("impact_logo.jpeg"))
        # PIL solution
        # self.window.iconphoto(False, img)

        self.fig = plt.figure(figsize=(10, 6))
        self.ax = plt.axes()

        # Display spectrum in log
        self.ax.set_yscale('log')
        self.ax.set_xlabel("Mass(u)", fontsize=15)
        self.ax.set_ylabel("Amplitude", fontsize=15)
        self.ax.set_facecolor("white")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky="W")

        # navigation self.toolbar
        self.toolbarFrame = tk.Frame(master=self.window)
        # self.toolbarFrame.grid(row=2, column=1)
        self.toolbar = NavigationToolbar2Tk(self.canvas,
                                            self.toolbarFrame)
        self.basic_gui()

        # %%RENDER NOISE ANALYSIS PANE
    def analyze_noise(self):
        win = tk.Toplevel()
        win.wm_title("SpectrumPY Noise Manager")
        fig, axs = plt.subplots(2)
        fig.suptitle('Vertically stacked subplots')

        # Display spectrum in log
        # ax.set_yscale('log')
        # ax.set_xlabel("Mass(u)", fontsize=15)
        # ax.set_ylabel("Amplitude", fontsize=15)
        # ax.set_facecolor("white")
        pds.generate_noise(True)
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.get_tk_widget().grid(row=0, column=1, sticky="W")

        # navigation self.toolbar
        toolbarFrame = tk.Frame(master=win)
        toolbarFrame.grid(row=1, column=1)
        toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

        b = tk.Button(win, text="Close and return to main menu",
                      command=win.destroy)
        b.grid(row=2, column=0)
        canvas.draw()

        # placing the self.canvas on the Tkinter self.window
        canvas.get_tk_widget().grid(row=0, column=1)
        toolbar.update()

    # %%PLACEHOLDER FUCNTION
    def donothing(self):
        pass

        # %%UPDATE INTERACTIVE PLOT
    def generate_spectra(self):
        try:
            self.canvas.get_tk_widget().grid_forget()
        except AttributeError:
            pass
        one_name = self.min_one_name.get()
        two_name = self.min_two_name.get()
        one_abun = self.min_one_abundance.get()
        two_abun = self.min_two_abundance.get()

        # print("Mineral one : " + one_name, one_abun, "%")
        # print("Mineral two : " + two_name, two_abun, "%")

        min_name = np.array([one_name, two_name])
        pres_abunds = np.array([float(one_abun), float(two_abun)])

        print(float(self.vel_val.get()))

        spectra = Spectra(min_name, pres_abunds, float(self.vel_val.get()))

        # One spectra object attribute is a suitable domain for plotting
        x = spectra.domain

        # The spectrum is another accesible attribute
        y = spectra.mass_spectrum

        if(self.noise_present.get()):
            print("Adding Noise")
            y = add_real_noise(y, float(self.snr_val.get()))

        if(self.split_gains.get()):
            self.ax.clear()
            lo, mid, hi = spectra.split_into_gstages()
            self.ax.plot(x, hi, lw=1, c='g', label="High Channel")
            self.ax.plot(x, mid, lw=1, c='r', label="Middle Channel")
            self.ax.plot(x, hi, lw=1, c='b', label="Low Channel")
            plt.legend(loc="best")

        self.ax.set_title("{} % {} and {}% {}".format(str(one_abun), one_name,
                                                      str(two_abun), two_name),
                          font="Times New Roman", fontweight="bold",
                          fontsize=20)

        if not(self.split_gains.get()):
            self.ax.plot(x, y, lw=1, c='r')
        plt.grid(b=None)
        # creating the Tkinter self.canvas
        # containing the Matplotlib self.figure

        self.canvas.draw()

        # placing the self.canvas on the Tkinter self.window
        self.canvas.get_tk_widget().grid(row=0, column=1)
        self.toolbar.update()

        # %%COMMAND TO ADD NOISE
    def noise_switch(self):

        if(self.noise_present.get()):
            print("Noise has been turned on")
        else:
            print("Noise has been turned off")
            self.ax.clear()
            self.ax.set_yscale('log')

        self.generate_spectra()

    # %%COMMAND TO ADD NOISE
    def divide_into_gains(self):

        if(self.split_gains.get()):
            print("Splitting signal over 3 gain stages")
        else:
            print("Recombining 3 gain stages")
            self.ax.clear()
            self.ax.set_yscale('log')

        self.generate_spectra()

    # %%GENERATE BASIC GUI
    def basic_gui(self):
        # placing the label and entry in position using grid method
        # self.logolabel.grid(row=0, column=3, sticky="NE")
        # self.lasplogolabel.grid(row=0, column=2, sticky="EW")
        # self.imaplogolabel.grid(row=0, column=1, sticky="EW")

        self.vel_label.grid(row=1, column=1, sticky="news")
        self.vel_entry.grid(row=1, column=2, sticky="news")

        self.name_one_label.grid(row=2, column=1)
        self.name_one_entry.grid(row=2, column=2)
        self.name_two_label.grid(row=3, column=1)
        self.name_two_entry.grid(row=3, column=2)

        self.min_one_abundance.grid(row=2, column=3, sticky="news")
        self.min_two_abundance.grid(row=3, column=3, sticky="news")

        # self.name_two_entry.pack(side="right")
        # self.name_two_label.pack(side="right")

        # self.snr_label.pack(side="top", anchor="e")
        # self.snr_entry.pack(side="top", anchor="e")
        self.snr_label.grid(row=4, column=1, sticky="news")
        self.snr_entry.grid(row=4, column=2, sticky="news")

        # self.sub_btn.pack(side="bottom", anchor="n", fill="both")
        # self.min_one_abundance.pack(side="left")
        self.sub_btn.grid(row=6, column=1, sticky="news")
        self.fft_btn.grid(row=6, column=2, sticky="news")
        self.noise_btn.grid(row=4, column=3, sticky="news")

        self.gainsplit_btn.grid(row=0, column=3, sticky="news")

        # self.quit_button.pack(side="bottom", anchor="s", fill="both")
        # self.noise_btn.pack(side="top", anchor="w")
        self.quit_button.grid(row=7, column=1, sticky="news")
        # self.window.update()  # For the width to get updated
        self.frame = tk.Frame(self.window, bg='orange', width=40,
                              height=self.window.winfo_height())
        self.frame.grid(row=0, column=0)

        # Make the buttons with the icons to be shown
        self.home_b = tk.Button(self.frame, image=self.home, bg='orange',
                                relief='flat')
        self.set_b = tk.Button(self.frame, image=self.settings, bg='orange',
                               relief='flat')
        self.ring_b = tk.Button(self.frame, image=self.ring, bg='orange',
                                relief='flat')

        # Put them on the frame
        self.home_b.grid(row=0, column=0, pady=10, sticky='E')
        self.set_b.grid(row=1, column=0, pady=40, sticky='E')
        self.ring_b.grid(row=2, column=0, sticky='E')

        # Bind to the frame, if entered or left
        self.frame.bind('<Enter>', lambda e: self.expand())
        self.frame.bind('<Leave>', lambda e: self.contract())

        # So that it does not depend on the widgets inside the frame
        self.frame.grid_propagate(True)
        self.window.mainloop()

    # %%EXPAND SIDEBAR
    def expand(self):
        global cur_width, expanded
        cur_width += 10  # Increase the width by 10
        rep = self.window.after(1, self.expand)  # Repeat this func every ms
        self.frame.config(width=cur_width)  # Change the width
        if cur_width >= max_w:  # If width is greater than maximum width
            expanded = True  # Frame is expended
            self.window.after_cancel(rep)  # Stop repeating the func
            self.fill()

    # %%CONTRACT SIDEBAR
    def contract(self):
        global cur_width, expanded
        cur_width -= 10  # Reduce the width by 10
        rep = self.window.after(5, self.contract)  # Call this func every 5 ms
        self.frame.config(width=cur_width)  # Reduce width
        if cur_width <= min_w:  # If it is back to normal width
            expanded = False  # Frame is not expanded
            self.window.after_cancel(rep)  # Stop repeating the func
            self.fill()

    # %%FILL SIDEBAR
    def fill(self):
        if expanded:  # If the frame is exanded
            # Show a text, and remove the image
            self.home_b.config(text='Home', image='', font=(0, 21))
            self.set_b.config(text='Settings', image='', font=(0, 21))
            self.ring_b.config(text='Bell Icon', image='', font=(0, 21))
        else:
            # Bring the image back
            self.home_b.config(image=self.home, font=(0, 21))
            self.set_b.config(image=self.settings, font=(0, 21))
            self.ring_b.config(image=self.ring, font=(0, 21))


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
    bGUI = SpectrumPYApp()
