#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A graphical interface for viewing and saving scope data
__author__      = Ethan Ayari,
Institute for Modeling Plasmas, Atmospheres and Cosmic Dust

Works with Python 3.8.10
"""

import sys


from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QCheckBox,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QFileDialog,
    QVBoxLayout,
    QListWidget,
)

import matplotlib
from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg,
                                               NavigationToolbar2QT as
                                               NavigationToolbar)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

plt.style.use('dark_background')
matplotlib.use('qtagg')

global traceNumber
global traceList
global times
global amps
global metas
times = []
amps = []
metas = []
traceList = []


# %%SET UP INTERACTIVE PLOT
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=15, height=8, dpi=100):
        global traceNumber
        traceNumber = 1
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.suptitle("Hyperdust Scope Trace #" + str(traceNumber),
                          fontsize=20)

        self.ax = self.fig.add_subplot(111)
        self.ax1 = self.fig.add_subplot(411)
        self.ax2 = self.fig.add_subplot(412, sharex=self.ax1)
        self.ax3 = self.fig.add_subplot(413, sharex=self.ax1)
        self.ax4 = self.fig.add_subplot(414, sharex=self.ax1)

        self.ax.spines['top'].set_color('none')
        self.ax.spines['bottom'].set_color('none')
        self.ax.spines['left'].set_color('none')
        self.ax.spines['right'].set_color('none')
        self.ax.tick_params(labelcolor='black', top=False, bottom=False,
                            left=False, right=False)
        self.ax.set_xlabel("Time [s]", labelpad=30)
        self.ax.set_ylabel("Voltage [V]", labelpad=30)
        self.ax1.grid(True)
        self.ax2.grid(True)
        self.ax3.grid(True)
        self.ax4.grid(True)

        self.ax1.set_ylabel('QD 2')
        self.ax2.set_ylabel('QD 1')
        self.ax3.set_ylabel('TOF Low')
        self.ax4.set_ylabel('TOF High')

        super().__init__(self.fig)


# %%SET UP QT WINDOW OBJECT
# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SpectrumPY Beta")

        self.sc = MplCanvas(self, width=15, height=8, dpi=100)
        # sc.axes.plot([0, 1, 2, 3, 4], [10, 1, 20, 3, 40])
        trcdir = 'Anthracene_iron_7_13_2021_10kms_plus'
        global times
        global amps
        global metas
        global traceList
        global traceNumber
        times, amps, metas = readTRC(trcdir)
        self.tracelist_widget = QListWidget()
        print(len(metas))
        for trace in traceList:
            self.tracelist_widget.insertItem(int(trace), str(trace))
        self.v_layout = QVBoxLayout()
        self.tracelist_widget.clicked.connect(self.updatePlot)
        displayTRC(times[traceNumber], amps[traceNumber], self.sc)
        self.toolbar = NavigationToolbar(self.sc, self)
        self._createMenuBar()
        self._createActions()
        self.setCentralWidget(self.sc)
        self.v_layout.addStretch()
        # self.v_layout.addSpacing()
        self.v_layout.addWidget(self.toolbar)
        self.sc.setLayout(self.v_layout)
        self.show()

# %%CREATE MENU BAR AND FILE DROP DOWN OPTIONS
    def _createMenuBar(self):
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

        listTraces = QAction(QIcon("bug.png"), "&Choose Trace", self)
        listTraces.triggered.connect(self.chooseTrace)
        # toolbar.addWidget(QLabel("Hello"))
        # toolbar.addWidget(QCheckBox())

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

# %%CREATE TOOLBAR OPTIONS
    def _createActions(self):
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
        global times
        global amps
        global traceNumber
        import pandas as pd
        a = times[traceNumber]
        b = amps[traceNumber]
        df = pd.DataFrame({"Time (s)": a, "Amplitude": b})
        df.to_csv("Specoutput.csv", index=False)

# %%CHANGE SHOT BEING VIEWED
    def chooseTrace(self, s):
        global traceList
        global times
        global amps
        global metas
        global traceNumber
        # traceNumber = str(self.tracelist_widget.currentItem().text())

        self.v_layout.addWidget(self.tracelist_widget)

# %%UPDATE PLOT WITH CHOICE OF TRACE FILE
    def updatePlot(self, s):
        """
        self.tracelist_widget = QListWidget(self)
        for trace in traceList:
            self.tracelist_widget.insertItem(int(trace), str(trace))
        self.v_layout = QVBoxLayout()
        """
        global traceNumber
        content = str(self.tracelist_widget.currentItem().text())  # .text()
        print(content)
        traceNumber = int(content)

        self.sc.fig.suptitle("Hyperdust Scope Trace #" + str(traceNumber),
                             fontsize=20)
        self.sc.ax.cla()
        self.sc.ax1.cla()
        self.sc.ax2.cla()
        self.sc.ax3.cla()
        self.sc.ax4.cla()
        self.sc.ax1.set_yticks([])
        self.sc.ax2.set_yticks([])
        self.sc.ax3.set_yticks([])
        self.sc.ax4.set_yticks([])

        self.sc.ax = self.sc.fig.add_subplot(111)
        self.sc.ax1 = self.sc.fig.add_subplot(411)
        self.sc.ax2 = self.sc.fig.add_subplot(412, sharex=self.sc.ax1)
        self.sc.ax3 = self.sc.fig.add_subplot(413, sharex=self.sc.ax1)
        self.sc.ax4 = self.sc.fig.add_subplot(414, sharex=self.sc.ax1)

        self.sc.ax.spines['top'].set_color('none')
        self.sc.ax.spines['bottom'].set_color('none')
        self.sc.ax.spines['left'].set_color('none')
        self.sc.ax.spines['right'].set_color('none')
        self.sc.ax.tick_params(labelcolor='black', top=False, bottom=False,
                               left=False, right=False)
        self.sc.ax.set_xlabel("Time [s]", labelpad=30)
        self.sc.ax.set_ylabel("Voltage [V]", labelpad=30)

        self.sc.ax1.set_ylabel('QD 2')
        self.sc.ax1.set_ylabel('Time [s]')
        self.sc.ax2.set_ylabel('QD 1')
        self.sc.ax3.set_ylabel('TOF Low')
        self.sc.ax4.set_ylabel('TOF High')
        displayTRC(times[int(content)], amps[int(content)], self.sc)
        self.tracelist_widget.setParent(None)
        self.tracelist_widget.setParent(self)
        self.sc.draw()

# %%OPEN A FILE DIALOG TO IMPORT SCOPE DATA
    def importScopeData(self, s):
        """
        fname = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "${HOME}",
            "All Files (*);; Trace Files(*.trc)",
        )
        """
        fname = QFileDialog.getExistingDirectory(self, 'Select Folder')
        times, amps, metas = readTRC(fname)


# %%GENERAL TRACE READER
def generalReadTRC(dataDir):
    pass


# %%TRACE READER
def readTRC(dataDir):
    # Alex Doner's Multi-channel viewer

    from readTrcDoner import Trc

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
        # plt.waitforbuttonpress(0)
        # plt.close(fig)
    # Update trace list
    global traceList
    traceList = list(range(1, len(times)+1))
    return times, amps, metas


# %%TRACE FILE DISPLAY
def displayTRC(times, amps, sc):
    import numpy as np

    print("Displaying oscilloscope output")
    dec = 1  # The factor of decimation (Makes plotting faster)
    i = dec*np.array(range(int(len(times[1])/dec)))

    amps[2] = -1*amps[2]
    amps[3] = -1*amps[3]

    for k in range(len(amps[2])):
        if(amps[2][k] <= 10**-4):
            amps[2][k] = 10**-4
        if(amps[3][k] <= 10**-4):
            amps[3][k] = 10**-4

    # ONE AXIS FOR REACH CHANNEL
    sc.ax1.plot(times[0][i], amps[0][i], markersize=1.0)
    sc.ax2.plot(times[1][i], amps[1][i], markersize=1.0)
    sc.ax3.plot(times[2][i], amps[2][i], markersize=1.0)
    sc.ax4.plot(times[3][i], amps[3][i], markersize=1.0)
    # plt.grid()
    sc.show()


# %%EXECUTABLE CODE BELOW
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
