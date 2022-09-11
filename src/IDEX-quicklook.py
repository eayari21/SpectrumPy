#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A graphical interface for viewing and saving scope data
__author__      = Ethan Ayari,
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust

Works with Python 3.8.10
"""

# %%DEPENDENCIES
import sys
import os
import matplotlib
import datetime
import numpy as np
import qtawesome as qta

from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg,
                                               NavigationToolbar2QT as
                                               NavigationToolbar)

from readTrc import Trc
from ImpactSQLConnector import SQLWindow
from PyQt6.QtCore import QSize  # , Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QFileDialog,
    QVBoxLayout,
    QListWidget,
    QInputDialog,
    QMessageBox,
    QWidget,
    QLabel,
    QCheckBox,
    QPushButton,
)

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# %%PRETTY PLOTS
matplotlib.use('Agg')
plt.style.use('seaborn-pastel')

# %%INITIALIZE (AND/OR DECLARE) GLOBAL VARIABLES
global traceNumber
global traceList
global times
global amps
global metas
global nChannels
global channelNames
global numDisplay
global displayDex
global mass
global velocity
times = []
amps = []
metas = []
traceList = []
mass = []
velocity = []

# %%DO OUR BEST TO SET THE BASE DIRECTORY
abspath = os.path.abspath(sys.argv[0])
dname = os.path.dirname(abspath)
try:
    os.chdir(dname)
except FileNotFoundError:
    pass
if getattr(sys, 'frozen', False):
    try:
        Current_Path = os.path.dirname(sys.executable)
    except FileNotFoundError:
        pass
else:
    try:
        Current_Path = str(os.path.dirname(__file__))
    except FileNotFoundError:
        pass

try:
    os.chdir("../traces/")
except FileNotFoundError:
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.chdir("../traces/")
    except FileNotFoundError:
        pass

# %%SPECIFY WINDOWS ENVIRONMENT
try:
    from ctypes import windll # Only accessible on Windows OS
    myappid = "IMPACT.SpectrumPy.0.1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

except ImportError:
    pass

# %%SET UP INTERACTIVE PLOT
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=15, height=8, dpi=100):
        """A class to set up the interactive matplotlib plot. Uses the global
        traceNumber and channelNames variables to decide which data to display.

        Args:
           width (float):  The width of the figure.
           height (float):  The height of the figure.
           dpi (float):  Controls the quality of the interactive plot. Stands
           for "dots per inch".

        Kwargs:
           parent (FigureCanvasQTAgg): The parent canvas of the current plot.
           This is useful for opening new windows

        Returns:
           None

        Raises:
           None
           """

        global traceNumber
        global channelNames
        global numDisplay
        global displayDex
        global mass
        global velocity
        traceNumber = 1
        self.numDisplay = numDisplay
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.fig.suptitle("Trace Number " + str(traceNumber)   + ": {} kg Particle @ {} km/s".format(mass[traceNumber],
                             round(velocity[traceNumber], 2)),
                          fontsize=20)

        if(self.numDisplay == 1):
            self.ax = self.fig.add_subplot(111)
            self.ax.set_xlabel("Time [s]", fontsize=16, labelpad=40)
            self.ax.set_ylabel("Voltage [V]", fontsize=12, labelpad=70)
            self.ax.grid(True)

            self.ax.set_ylabel(str(channelNames[displayDex[0]]), labelpad=4)

        elif(self.numDisplay == 2):
            self.ax = self.fig.add_subplot(111)
            self.ax1 = self.fig.add_subplot(211)
            self.ax2 = self.fig.add_subplot(212, sharex=self.ax1)

            self.ax.spines['top'].set_color('none')
            self.ax.spines['bottom'].set_color('none')
            self.ax.spines['left'].set_color('none')
            self.ax.spines['right'].set_color('none')
            self.ax.tick_params(labelcolor='white', top=False,
                                bottom=False, left=False, right=False)
            self.ax.xaxis.set_ticklabels([])
            self.ax.yaxis.set_ticklabels([])
            self.ax.set_xlabel("Time [s]", fontsize=16, labelpad=40)
            self.ax.set_ylabel("Voltage [V]", fontsize=12, labelpad=70)
            self.ax1.grid(True)
            self.ax2.grid(True)

            self.ax1.set_ylabel(str(channelNames[displayDex[0]]), labelpad=4)
            self.ax2.set_ylabel(str(channelNames[displayDex[1]]), labelpad=4)

        elif(self.numDisplay == 3):
            self.ax = self.fig.add_subplot(111)
            self.ax1 = self.fig.add_subplot(311)
            self.ax2 = self.fig.add_subplot(312, sharex=self.ax1)
            self.ax3 = self.fig.add_subplot(313, sharex=self.ax1)

            self.ax.spines['top'].set_color('none')
            self.ax.spines['bottom'].set_color('none')
            self.ax.spines['left'].set_color('none')
            self.ax.spines['right'].set_color('none')
            self.ax.tick_params(labelcolor='white', top=False, bottom=False,
                                left=False, right=False)
            self.ax.xaxis.set_ticklabels([])
            self.ax.yaxis.set_ticklabels([])
            self.ax.set_xlabel("Time [s]", fontsize=16, labelpad=40)
            self.ax.set_ylabel("Voltage [V]", fontsize=12, labelpad=70)
            self.ax1.grid(True)
            self.ax2.grid(True)
            self.ax3.grid(True)

            self.ax1.set_ylabel(str(channelNames[displayDex[0]]), labelpad=4)
            self.ax2.set_ylabel(str(channelNames[displayDex[1]]), labelpad=4)
            self.ax3.set_ylabel(str(channelNames[displayDex[2]]), labelpad=4)

        elif(self.numDisplay == 4):
            self.ax = self.fig.add_subplot(111)
            self.ax1 = self.fig.add_subplot(411)
            self.ax2 = self.fig.add_subplot(412, sharex=self.ax1)
            self.ax3 = self.fig.add_subplot(413, sharex=self.ax1)
            self.ax4 = self.fig.add_subplot(414, sharex=self.ax1)

            self.ax.spines['top'].set_color('none')
            self.ax.spines['bottom'].set_color('none')
            self.ax.spines['left'].set_color('none')
            self.ax.spines['right'].set_color('none')
            self.ax.tick_params(labelcolor='white', top=False, bottom=False,
                                left=False, right=False)
            self.ax.xaxis.set_ticklabels([])
            self.ax.yaxis.set_ticklabels([])
            self.ax.set_xlabel("Time [s]", fontsize=16, labelpad=20)
            self.ax.set_ylabel("Voltage [V]", fontsize=12, labelpad=70)
            self.ax1.grid(True)
            self.ax2.grid(True)
            self.ax3.grid(True)
            self.ax4.grid(True)

            self.ax1.set_ylabel(str(channelNames[displayDex[0]]), labelpad=4)
            self.ax2.set_ylabel(str(channelNames[displayDex[1]]), labelpad=4)
            self.ax3.set_ylabel(str(channelNames[displayDex[2]]), labelpad=4)
            self.ax4.set_ylabel(str(channelNames[displayDex[3]]), labelpad=4)
        else:
            print("Invalid number of channels to display, must be 1, 2, 3, or",
                  "4.")

        super().__init__(self.fig)


# %%SET UP QT WINDOW OBJECT
# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        """A class to set up the main pyQT user interface.

        Args:
           None

        Kwargs:
           None

        Returns:
           None

        Raises:
           None
           """
        super(MainWindow, self).__init__(parent)

        global channelNames
        global nChannels
        global times
        global amps
        global metas
        global traceList
        global traceNumber
        global numDisplay
        global displayDex
        global mass
        global velocity

        self.renderPlot = False
        self.setWindowTitle("SpectrumPY Beta Main Window")
        trcdir = QFileDialog.getExistingDirectory(self, ''''Please Select A
                                                  Folder Containing Trace
                                                  Files''')
        times, amps, metas = generalReadTRC(trcdir)


        self.timeStamps = []

        for k in range(len(metas)-1):

            timeArr = metas[k][0]['TRIGGER_TIME']
            # print(timeArr)
            date_time = 1000 * \
                datetime.datetime.timestamp(datetime.datetime(*timeArr))

            # print(time)
            # this is in yyyymmddhhmmss.ms format
            self.timeStamps.append(int(date_time))
        self.sql_win = SQLWindow(self.timeStamps)


        # Associate all SQL quantities, remember:
        # ||"Estimate Quality",
        # ||"Time",
        # ||"Velocity (km/s)",
        # ||"Mass (kg)",
        # ||"Charge (C)",
        # ||"Radius (m)"
        self.Mass = self.sql_win.df["Mass (kg)"]
        self.Velocity = self.sql_win.df["Velocity (km/s)"]
        self.Charge = self.sql_win.df["Charge (C)"]
        self.Size = self.sql_win.df["Radius (m)"]
        mass = self.sql_win.df["Mass (kg)"]
        velocity = self.sql_win.df["Velocity (km/s)"]

        channelNames = []

        # Check to see if the channels are predefined
        if(os.path.exists(trcdir + "/settings.txt")):
            settingsFile = open(trcdir + '/settings.txt', 'r')
            Lines = settingsFile.readlines()

            for line in Lines:
                channelNames.append(str(line))
        else:
            # If there is no settings file, prompt the user to enter
            # the channel name(s)
            prompter = ("No settings.txt file found. {}"
                        " channels detected, ").format(str(nChannels))
            #            "please enter the name of "
            #            "Channel 1".format(str(nChannels)))
            for chan in range(int(nChannels)):
                le, done = QInputDialog.getText(self, 'Input Dialog',
                                                      (prompter +
                                                       "please enter the name"
                                                       " of Channel {}"
                                                       ).format(str(chan+1)))
                if done:
                    channelNames.append(le)

            dlg = QMessageBox(self)
            dlg.setWindowTitle("Save channel settings")
            dlg.setText(("Would you like to save these channel names for"
                        " future use?"))
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes |
                                   QMessageBox.StandardButton.No)
            dlg.setIcon(QMessageBox.Icon.Question)
            button = dlg.exec()

            if button == QMessageBox.StandardButton.Yes:
                # writing user-provided settings to a file
                settingsFile = open(trcdir+'/settings.txt', 'w')
                for name in channelNames:
                    settingsFile.write("%s\n" % str(name))
                settingsFile.close()

        # Call channel choosing window
        numDisplay = 4
        displayDex = [0, 1, 2, 3]
        # print("numDisplay: ", numDisplay)
        self.tracelist_widget = QListWidget()

        for trace in traceList:
            self.tracelist_widget.insertItem(int(trace), str(trace))

        self.v_layout = QVBoxLayout()
        self.tracelist_widget.clicked.connect(self.updatePlot)

        self._createMenuBar()
        self._createActions()

        # print(self.renderPlot)

        # if(self.channelWin.complete):
        self.sc = MplCanvas(self, width=16, height=12, dpi=100)
        displayTRC(times[traceNumber], amps[traceNumber], self.sc)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.setCentralWidget(self.sc)
        self.v_layout.addStretch()
        self.v_layout.addWidget(self.toolbar)
        self.sc.setLayout(self.v_layout)


        self.show()

        # %%HANDLER FUNCTION TO PROMPT USER TO SAVE AND EXIT SAFELY
    def closeEvent(self, event):
 
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Close window")
        dlg.setText(("Are you sure you want to quit SpectrumPY?"))
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes |
                               QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            global times
            global amps
            global traceNumber
            import pandas as pd
            a = times[traceNumber]
            b = amps[traceNumber]
            df = pd.DataFrame({"Time (s)": a, "Amplitude": b})
            df.to_csv("Specoutput.csv", index=False)
            event.accept()

        else:
            pass

# %%CREATE MENU BAR AND FILE DROP DOWN OPTIONS
    def _createMenuBar(self):
        """This function sets up the toolbar options located above the
        interactive plot. For now, these options echo the menu options (file,
        edit, view, etc.)

        Args:
           None

        Kwargs:
           None

        Returns:
           None

        Raises:
           None
           """
        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        button_action = QAction(QIcon("bug.png"), "&Import Scope Data (.trc)",
                                self)
        button_action.setStatusTip("This is your button")
        button_action.triggered.connect(self.importScopeData)
        button_action.setCheckable(True)
        toolbar.addAction(button_action)

        toolbar.addSeparator()

        button_action2 = QAction(QIcon("bug.png"), "&Export to .csv", self)
        button_action2.setStatusTip("This is your button2")
        button_action2.triggered.connect(self.exportScopeData)
        button_action2.setCheckable(True)
        toolbar.addAction(button_action2)

        traceIcon = qta.icon("fa5s.list-ol")
        listTraces = QAction(traceIcon, "&Choose Trace", self)
        listTraces.triggered.connect(self.chooseTrace)

        helpIcon = qta.icon("mdi.help-circle-outline")
        getHelp = QAction(helpIcon, "&Read the Docs", self)
        getHelp.triggered.connect(self.helpPage)

        channelChangeIcon = qta.icon("fa5s.digital-tachograph")
        changeChannels = QAction(channelChangeIcon, "&Change Channels", self)
        changeChannels.triggered.connect(self.changeChannel)

        QDIcon = qta.icon("mdi.speedometer")
        fitQD = QAction(QDIcon, "&Fit QD Waveform", self)
        fitQD.triggered.connect(self.fitQD)

        SQLIcon = qta.icon("fa.database")
        viewSQL = QAction(SQLIcon, "&View SQL Data", self)
        viewSQL.triggered.connect(self.viewSQLWindow)

        self.setStatusBar(QStatusBar(self))

        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        # file_menu.addAction(button_action)
        import_submenu = file_menu.addMenu("Import Data")
        import_submenu.addAction(button_action)
        file_menu.addSeparator()
        # file_menu.addAction(button_action2)
        export_submenu = file_menu.addMenu("Export Data")
        export_submenu.addAction(button_action2)

        view_menu = menu.addMenu("&View")
        view_menu.addAction(listTraces)
        view_menu.addAction(changeChannels)

        run_menu = menu.addMenu("&Run")
        run_menu.addAction(fitQD)
        run_menu.addAction(viewSQL)

        help_menu = menu.addMenu("&Help")
        help_menu.addAction(getHelp)

# %%CREATE TOOLBAR ACTIONS
    def _createActions(self):
        """Initializes the actions associated with the toolbar options.

        Args:
           None

        Kwargs:
           None

        Returns:
           None

        Raises:
           None
           """
        # Creating action using the first constructor
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        # Creating actions using the second constructor
        self.openAction = QAction("&Open...", self)
        self.saveAction = QAction("&Save", self)
        self.exitAction = QAction("&Exit", self)
        self.copyAction = QAction("&Copy", self)
        self.pasteAction = QAction("&Paste", self)
        self.cutAction = QAction("C&ut", self)
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)

# %%WRITE TIMES AND AMPS TO CSV
    def exportScopeData(self, s):
        """Action associated with the "export data" option. Pandas is imported
        alone here since it can be time consuming. It takes the time and
        amplitude arrays from the current trace shot being viewed and writes
        them both as a two column csv.

        Args:
           None

        Kwargs:
           s (str): The destination filename for the csv data.

        Returns:
           None

        Raises:
           None
           """
        global times
        global amps
        global traceNumber
        global displayDex
        import pandas as pd
        # dec = 1  # The factor of decimation (Makes plotting faster)
        dec = 312  # for low rate ADC's  (1/sampling rate)
        # dec = 38 for high rate ADC's
        i = dec*np.array(range(int(len(times[int(traceNumber)][displayDex[0]])/dec)))
        print(i)
        ionTime = times[int(traceNumber)][displayDex[0]][i]
        ionAmp = amps[int(traceNumber)][displayDex[0]][i]
        targetAmp = amps[int(traceNumber)][displayDex[1]][i]
        # ionTime = times[displayDex[0]][int(traceNumber)][i]
        # ionAmp = amps[displayDex[0]][int(traceNumber)][i]
        # targetAmp = amps[displayDex[1]][int(traceNumber)][i]

        df = pd.DataFrame({"Time (s)": ionTime, "Ion Grid Amplitude (V)": ionAmp, "Target Amplitude (V)": targetAmp})
        df.to_csv("Specoutput.csv", index=False)

# %%CHANGE SHOT BEING VIEWED
    def chooseTrace(self, s):
        """A helper function that adds the trace chooser to the QT main window.

        Args:
           None

        Kwargs:
           s (str): The choice of trace provided by the user.

        Returns:
           None

        Raises:
           None
           """
        self.v_layout.addWidget(self.tracelist_widget)

# %%CHANGE SHOT BEING VIEWED
    def changeChannel(self, s):
        """A helper function that adds the trace chooser to the QT main window.

        Args:
           None

        Kwargs:
           s (str): The choice of trace provided by the user.

        Returns:
           None

        Raises:
           None
           """
        self.channelWin = ChannelChoosingWindow(self)
        self.channelWin.show()

# %%BRING UP HTML DOCS
    def helpPage(self, s):
        """A helper function that gets help from the QT main window.

        Args:
           None

        Kwargs:
           s (str): The choice of trace provided by the user.

        Returns:
           None

        Raises:
           None
           """
        import webbrowser
        filename = dname + '../_build/index.html'
        webbrowser.open('file://' + os.path.realpath(filename))
        # webbrowser.open_new_tab("../_build/index.html")

# %%FIT EXISTING QD WAVEFORMS
    def fitQD(self, s):
        """A function to obtain the charge and speed of an impactor using the QD waveform.

        Args:
           None

        Kwargs:
           s (str): The choice of trace provided by the user.

        Returns:
           None

        Raises:
           None
           """
        print("Fitting QD Waveforms")

# %%BRING UP MATCHED SQL DATA
    def viewSQLWindow(self, s):
        """A function to view the accelerator metadata in an interactive window.

        Args:
           None

        Kwargs:
           s (str): The choice of trace provided by the user.

        Returns:
           None

        Raises:
           None
           """
        print("Viewing SQL Data")
        # self.sqlwindow = SQLWindow(self.timeStamps)
        # self.sqlWindow.show()
        self.sql_win.show()


# %%UPDATE PLOT WITH CHOICE OF TRACE FILE
    def updatePlot(self, s):
        """Update the matplotlib canvas with the user-provided choice of trace.

        Args:
           None

        Kwargs:
           s (str): The user's choice of trace.

        Returns:
           None

        Raises:
           None
           """
        global traceNumber
        global displayDex
        global times
        global amps
        global metas
        global mass
        global velocity
    

        if(displayDex == []):
            displayDex = [0, 1, 2, 3]
        print("Updating Plot...")
        content = str(self.tracelist_widget.currentItem().text())
        # print(content)
        traceNumber = int(content)

        # self.sc = MplCanvas(self, width=16, height=12, dpi=100)
        self.sc.fig.suptitle("Trace Number " + str(traceNumber) + ": {} kg Particle @ {} km/s".format(mass[traceNumber],
                             round(velocity[traceNumber], 2)),
                             fontsize=20)
        # Clear all axes
        # self.sc.ax.cla()
        if(self.sc.numDisplay == 1):
            self.sc.ax.cla()
        if hasattr(self.sc, 'ax1'):
            self.sc.ax1.cla()
            self.sc.ax1.grid(True)
            self.sc.ax1.set_ylabel(str(channelNames[displayDex[0]]),
                                   labelpad=4)

        if hasattr(self.sc, 'ax2'):
            self.sc.ax2.cla()
            self.sc.ax2.grid(True)
            self.sc.ax2.set_ylabel(str(channelNames[displayDex[1]]),
                                   labelpad=4)

        if hasattr(self.sc, 'ax3'):
            self.sc.ax3.cla()
            self.sc.ax3.grid(True)
            self.sc.ax3.set_ylabel(str(channelNames[displayDex[2]]),
                                   labelpad=4)

        if hasattr(self.sc, 'ax4'):
            self.sc.ax4.cla()
            self.sc.ax4.grid(True)
            self.sc.ax4.set_xticks([])
            self.sc.ax4.set_ylabel(str(channelNames[displayDex[3]]),
                                   labelpad=4)

        self.setCentralWidget(self.sc)
        self.v_layout.addStretch()
        self.v_layout.addWidget(self.toolbar)
        self.sc.setLayout(self.v_layout)

        # Load new data into the interactive plot.
        displayTRC(times[int(content)], amps[int(content)], self.sc)

        # Get rid of the trace choosing widget
        self.tracelist_widget.setParent(None)
        self.tracelist_widget.setParent(self)
        self.sc.draw()
        self.show()

# %%OPEN A FILE DIALOG TO IMPORT SCOPE DATA
    def importScopeData(self, s):
        """Update the matplotlib canvas with the user-provided choice of trace.

        Args:
           None

        Kwargs:
           s (str): The user's choice of trace.

        Returns:
           None

        Raises:
           None
           """
        global channelNames
        global traceList
        global times
        global amps
        global metas
        trcdir = QFileDialog.getExistingDirectory(self, ''''Please select a
                                                 folder containing trace
                                                 files.''')
        times = None
        amps = None
        metas = None
        channelNames = []
        times, amps, metas = generalReadTRC(trcdir)

        self.timeStamps = []

        for k in range(len(metas)-1):

            timeArr = metas[k][0]['TRIGGER_TIME']

            date_time = 1000 * \
                datetime.datetime.timestamp(datetime.datetime(*timeArr))


            # this is in yyyymmddhhmmss.ms format
            self.timeStamps.append(int(date_time))

        channelNames = []
        # Check to see if the channels are predefined
        if(os.path.exists(trcdir + "/settings.txt")):
            settingsFile = open(trcdir + '/settings.txt', 'r')
            Lines = settingsFile.readlines()

            for line in Lines:
                channelNames.append(str(line))
        else:
            # If there is no settings file, prompt the user to enter
            # the channel name(s)
            prompter = ("No settings.txt file found. {}"
                        " channels detected, ").format(str(nChannels))
            #            "please enter the name of "
            #            "Channel 1".format(str(nChannels)))
            for chan in range(int(nChannels)):
                le, done = QInputDialog.getText(self, 'Input Dialog',
                                                      (prompter +
                                                       "please enter the name"
                                                       " of Channel {}"
                                                       ).format(str(chan+1)))
                if done:
                    channelNames.append(le)

            dlg = QMessageBox(self)
            dlg.setWindowTitle("Save channel settings")
            dlg.setText(("Would you like to save these channel names for"
                        " future use?"))
            dlg.setStandardButtons(QMessageBox.StandardButton.Yes |
                                   QMessageBox.StandardButton.No)
            dlg.setIcon(QMessageBox.Icon.Question)
            button = dlg.exec()

            if button == QMessageBox.StandardButton.Yes:
                # writing user-provided settings to a file
                settingsFile = open(trcdir+'/settings.txt', 'w')
                for name in channelNames:
                    settingsFile.write("%s\n" % str(name))
                settingsFile.close()

        # Call channel choosing window
        # self.show_new_window()

        self.tracelist_widget = QListWidget()

        for trace in traceList:
            self.tracelist_widget.insertItem(int(trace), str(trace))
        self.tracelist_widget.clicked.connect(self.updatePlot)
        self.updatePlot


# %%SET UP QT POPUP WINDOW OBJECT
class ChannelChoosingWindow(QWidget):
    """
    This "window" is a child. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self, MainWindow):
        super(ChannelChoosingWindow, self).__init__()
        global channelNames
        global numDisplay
        global displayDex
        displayDex = []
        self.displayChannels = []
        numDisplay = 0
        # super(ChannelChoosingWindow, self).__init__(parent)
        self.complete = False
        self.parent = MainWindow
        self.setWindowTitle(("SpectrumPY Beta Channel Choosing Window"))

        # Set the label text for the user
        lb = QLabel("Please choose the channels you would like to display:",
                    self)
        lb.setGeometry(20, 20, 350, 20)
        lb.move(20, 20)

        self.label = QLabel('Nothing Selected')
        self.label.move(20, 55)

        self.submitButton = QPushButton("Plot Chosen Data")
        self.submitButton.clicked.connect(self.Submit_Plot)

        # Set the vertical Qt Layout
        vbox = QVBoxLayout()
        vbox.addWidget(lb)
        vbox.addWidget(self.label)
        # Create as many checkboxes as channels
        ySpacing = 100
        cB = {}
        for name in channelNames:
            cB[name] = QCheckBox('{}'.format(name), self)
            cB[name].move(20, ySpacing)
            cB[name].toggled.connect(self.Selected_Value)
            ySpacing += 20
            vbox.addWidget(cB[name])

        vbox.addWidget(self.submitButton)
        self.submitButton.setGeometry(500, 700, 60, 20)
        self.setLayout(vbox)
        self.setGeometry(60, 60, 700, 700)
        self.lblText = ''

        self.show()

    # %%DEFINE FUNCTION TO READ THE USER'S INPUT
    def Selected_Value(self):
        global numDisplay
        global displayDex
        global channelNames

        # print("Selected: ", self.sender().isChecked(),
        #      "  Name: ", self.sender().text())

        if(self.sender().isChecked()):
            self.lblText += self.sender().text()
            numDisplay += 1
            # self.displayChannels.append(self.sender().text())
            displayDex.append(channelNames.index(self.sender().text()))
        else:
            self.lblText.replace(self.sender().text(), '')
            numDisplay -= 1
            displayDex.remove(channelNames.index(self.sender().text()))
            # self.displayChannels.remove(self.sender().text())
        # print("Number of displays: ", numDisplay)
        # super().numDisplay = numDisplay
        self.label.setText('You have selected \n' + self.lblText)
        # for disp in self.displayChannels:
        #    displayDex.append(channelNames.index(disp))
        # self.parent.updatePlot
        # print(self.parent.__dict__)
        # self.parent.updatePlot

# %%DEFINE FUNCTION TO READ THE USER'S INPUT
    def Submit_Plot(self):
        global traceNumber
        global times
        global amps
        global metas
        global mass
        global velocity

        self.parent.sc = MplCanvas(self.parent, width=16, height=12, dpi=100)
        self.parent.toolbar.setParent(None)
        self.parent.setCentralWidget(self.parent.sc)
        self.parent.v_layout.addStretch()
        self.parent.toolbar = NavigationToolbar(self.parent.sc, self.parent)
        self.parent.v_layout.addWidget(self.parent.toolbar)
        self.parent.sc.setLayout(self.parent.v_layout)

        traceNumber = 2
        displayTRC(times[int(traceNumber)], amps[int(traceNumber)],
                   self.parent.sc)
        self.fig.suptitle("Trace Number " +str(traceNumber)   + ": {} kg Particle @ {} km/s".format(mass[traceNumber],
                             round(velocity[traceNumber], 2)),
                          fontsize=20)
        self.parent.updatePlot
        self.parent.sc.draw()

    # %%HANDLER FUNCTION TO TRIGGER MAIN WINDOW UPON CLOSE
    def closeEvent(self, event):
        global numDisplay
        global displayDex

        if(numDisplay <= 0 or numDisplay > 4):
            numDisplay = 4
        if(displayDex == []):
            displayDex = [0, 1, 2, 3]
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Close window")
        dlg.setText(("Are you sure you want to close the channel window?"))
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes |
                               QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()

        if button == QMessageBox.StandardButton.Yes:
            event.accept()
            self.parent.renderPlot = True
            self.parent.updatePlot
            self.complete = True
            # print("Status before: ", self.parent().renderPlot)
            # self.parent().renderPlot = True

            # print("Status before: ", self.parent().renderPlot)
            # print('Window closed')
        else:
            event.ignore()


# %%GENERAL TRACE READER
def generalReadTRC(dataDir, verbose=False):
    """A function to read in the binary trace files from the oscilloscopes. It
    is general for different instruments and scope configurations. The number
    of channels and shots is automatically detected and sorted.

        Args:
           dataDir (str): The folder containing the trace files. It doesn't
           matter if there are other files in that directory. If you are
           manually entering a path and encounter issues, try os.listdir() to
           ensure things look right.'

        Kwargs:
           verbose (bool): A boolean representing the user's choice of whether
           or not they want real-time print statements of all relevant
           quantities.

        Returns:
           times (list): A 2 dimensional list containing the time arrays for
           each shot.

           amps (list): A 2 dimensional list containing the amplitude arrays
           for each shot.

           metas (list): A 2 dimensional list containing the metadata arrays
           for each shot. **TODO** Figure out this format and make it a dict.

        Exceptions:
           FileNotFoundError: The cue to stop parsing the user-provuded
           directory for any more trace files.

            ZeroDivisionError: This will be reaised if there are no files
            detected at all.
           """
    # __author__= Ethan Ayari
    # Iterate through all files in the folder and attempt to sort them
    parse = True

    global times
    global amps
    global metas
    global nChannels
    global traceList
    times = []
    amps = []
    metas = []
    shotKey = "00000"
    nChannels = 0
    while parse:
        # Shot number must be given as a 5 digit number
        # Initialize empty scope object
        trc = Trc()
        tmpTime = []
        tmpAmp = []
        tmpMeta = []
        # Iterate through all files in passed directory
        parsetwo = False
        # for filename in os.scandir(dataDir):
        directoryList = sorted(os.scandir(dataDir), key=lambda e: e.name)
        for filename in directoryList:
            # print(str(filename))
            # Gather all channels for shotKey
            if(str(filename).find(shotKey) != -1):
                parsetwo = True
                if verbose:
                    print(str(filename.path))
                try:
                    t, y, meta = trc.open(str(filename.path))
                    # t, y, meta = trc.open(str(filename))
                    tmpTime.append(t)
                    tmpAmp.append(y)
                    tmpMeta.append(meta)
                    nChannels += 1
                except FileNotFoundError:
                    # We've found everything
                    parse = False
        if not parsetwo:
            parse = False

        times.append(tmpTime)
        amps.append(tmpAmp)
        metas.append(tmpMeta)
        i = int(shotKey) + 1
        shotKey = f'{i:05d}'
    shotKey = int(shotKey)-1  # Get rid of extra shot count
    try:
        nChannels = int(int(nChannels) / int(shotKey))
    except ZeroDivisionError:
        print("No data was detected.")

    traceList = list(range(1, len(times)-1))
    if verbose:
        print(r"{} channels detected.".format(nChannels))
        print(r"{} shots detected per each channel.".format(int(shotKey)))
    return times, amps, metas


# %%TRACE READER
def readTRC(dataDir):
    # Alex Doner's Multi-channel viewer

    trcName1 = '/C1Fe'
    trcName2 = '/C2Fe'
    trcName3 = '/C3Fe'
    trcName4 = '/C4Fe'  # Look at the name of the files (Before the num)
    number = -1  # Starts on this number +1
    trcS = '.trc'
    global times
    global amps
    global metas
    times = []
    amps = []
    metas = []

    parse = True
    while parse:
        trc = Trc()
        number += 1
        # print(number)
        strNum = '{:05}'.format(number)
        # title = 'Trace Number: ' + strNum
        fileName1 = dataDir + trcName1 + strNum + trcS
        fileName2 = dataDir + trcName2 + strNum + trcS
        fileName3 = dataDir + trcName3 + strNum + trcS
        fileName4 = dataDir + trcName4 + strNum + trcS

        try:
            t1, y1, meta1 = trc.open(fileName1)
            t2, y2, meta2 = trc.open(fileName2)
            t3, y3, meta3 = trc.open(fileName3)
            t4, y4, meta4 = trc.open(fileName4)

            times.append([t1, t2, t3, t4])
            amps.append([y1, y2, y3, y4])
            metas.append([meta1, meta2, meta3, meta4])

        except FileNotFoundError:
            parse = False

    # Update trace list
    global traceList
    traceList = list(range(1, len(times)+1))
    return times, amps, metas


# %%TRACE FILE DISPLAY
def displayTRC(times, amps, sc):
    """Update the matplotlib canvas with the user-provided choice of trace.

        Args:
           times (list): The 2D list that gets returned from
           :func:'IDEX-quicklook.generalReadTrc'

           amps (list): The 2D list that gets returned from
           :func:'IDEX-quicklook.generalReadTrc'

           sc (FigureCanvasQTAgg): An instance of the :class:'MplCanvas' class
           defined above.

        Kwargs:
           None

        Returns:
           None

        Raises:
           None
           """
    global channelNames
    global nChannels
    global numDisplay
    global displayDex
    # print("amps: ", len(amps))
    # print(displayDex)
    # print("Displaying oscilloscope output")
    if(displayDex == []):
        displayDex = [0, 1, 2, 3]
    dec = 312  # The factor of decimation (Makes plotting faster)
    i = dec*np.array(range(int(len(times[displayDex[0]])/dec)))

    # Format the channel properly if it is a TOF channel
    for name in range(len(channelNames)):
        if('Low' in channelNames[name] or 'High' in channelNames[name]):
            amps[name] = -1*amps[name]
            for k in range(len(amps[name])):
                if(amps[name][k] <= 10**-4):
                    amps[name][k] = 10**-4

    # ONE AXIS FOR REACH CHANNEL
    if(numDisplay == 1):
        sc.ax.plot(times[displayDex[0]][i], amps[displayDex[0]][i],
                   markersize=.5, lw=.5)

    if(numDisplay == 2):
        sc.ax1.plot(times[displayDex[0]][i], amps[displayDex[0]][i],
                    markersize=.5, lw=.5)
        sc.ax2.plot(times[displayDex[1]][i], amps[displayDex[1]][i],
                    markersize=.5, lw=.5)

    if(numDisplay == 3):
        sc.ax1.plot(times[displayDex[0]][i], amps[displayDex[0]][i],
                    markersize=.5, lw=.5)
        sc.ax2.plot(times[displayDex[1]][i], amps[displayDex[1]][i],
                    markersize=.5, lw=.5)
        sc.ax3.plot(times[displayDex[2]][i], amps[displayDex[2]][i],
                    markersize=.5, lw=.5)

    if(numDisplay == 4):
        sc.ax1.plot(times[displayDex[0]][i], amps[displayDex[0]][i],
                    markersize=.5, lw=.5)
        sc.ax2.plot(times[displayDex[1]][i], amps[displayDex[1]][i],
                    markersize=.5, lw=.5)
        sc.ax3.plot(times[displayDex[2]][i], amps[displayDex[2]][i],
                    markersize=.5, lw=.5)
        sc.ax4.plot(times[displayDex[3]][i], amps[displayDex[3]][i],
                    markersize=.5, lw=.5)
    sc.draw()


# %%NECESSARY WAITING FUNCION
def is_ready(something):
    if something:
        return True
    return False


# %%EXECUTABLE CODE BELOW
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = MainWindow()
    w.show()
    app.exec()
