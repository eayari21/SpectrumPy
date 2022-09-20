#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 17:20:34 2022

A graphical interface for the IMPACT acclerator server

@author: ethanayari
"""
import sys
import matplotlib
import pandas as pd

from sqlalchemy import create_engine
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg,
                                               NavigationToolbar2QT as
                                               NavigationToolbar)

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

matplotlib.use('Agg')
plt.style.use('seaborn-pastel')

# %%SET UP INTERACTIVE PLOT
class SQLMplCanvas(FigureCanvasQTAgg):

    def __init__(self, data, parent=None, width=15, height=8, dpi=100):
        """A class to set up an interactive matplotlib plot for the SQL data.

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
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.suptitle("Accelerator Data Calibration Curve")
        self.ax = self.fig.add_subplot((111), position=[0.15, 0.15, 0.75, 0.75])
        self.ax.set_xlabel("Velocity [km/s]", fontsize=16, labelpad=40)
        self.ax.set_ylabel(r"$\frac{Q_{i}}{m} [C/kg]$", fontsize=12, labelpad=70)
        self.ax.grid(True)
        
        super().__init__(self.fig)


# %%SET UP SQL TABLE
class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return(str(value))
        if role == Qt.ItemDataRole.BackgroundRole:
            qualVal = self._data.iloc[[index.row()]]["Estimate Quality"]
            qualVal = int(qualVal.astype(int))
            # return (str(value))
            COLORS = ['#FE433C', '#EC8282',  '#D2D6CF', '#7BBFD0', '#0095EF']
            return QtGui.QColor(COLORS[qualVal-1])

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return(self._data.columns[section])
        if orientation == Qt.Orientation.Vertical:
            return str(self._data.index[section])

# %%SET UP SQL WINDOW
class SQLWindow(QtWidgets.QMainWindow):
    def __init__(self, timebase):
        super().__init__()
        self.setWindowTitle("SpectrumPY Beta Accelerator Window")

        self.table = QtWidgets.QTableView()
        db_connection_str = 'mysql+pymysql://root:Loucet59@localhost/impact091322'
        db_connection = create_engine(db_connection_str)

        self.df = pd.DataFrame()

        for time in timebase:
                time = str(time)

        self.df = pd.read_sql(('select estimate_quality, integer_timestamp, velocity, mass, charge, radius'
                      ' from dust_event where mass != -1 order by '
                      'abs(integer_timestamp-{}) limit {};'.format(time, str(len(timebase)))),
                 con=db_connection)
        self.df.columns=["Estimate Quality", "Time", "Velocity (km/s)", "Mass (kg)", "Charge (C)", "Radius (m)"] 
        self.df["Velocity (km/s)"] /= 1000.0
        self.df["Time"] = pd.to_datetime(self.df['Time'], unit='ms')
        self.df['Trace Number'] = range(1, len(self.df) + 1)
        data = self.df

        self.w = None  # Create empty window object
        self.plotButton = QtWidgets.QPushButton("View Accelerator Plot")
        self.plotButton.clicked.connect(self.show_sql_plot)
        self.plotButton.resize(200, 100)
    
        self.model = TableModel(data)
        self.table.setModel(self.model)
    
        self.v_layout = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        self.v_layout.addWidget(self.plotButton)
        # self.v_layout.addStretch()
        self.v_layout.addWidget(self.table)
        self.table.move(300, 200)

        widget.setLayout(self.v_layout)

        self.setGeometry(50, 50, 800, 600)
        self.show()

    # %%TRIGGER PLOT WINDOW
    def show_sql_plot(self, checked):
        if self.w is None:
            self.w = SQLPlot(self.df)
            self.w.show()


# %%SET UP SQL WINDOW
class SQLPlot(QtWidgets.QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.df = data
        self.setWindowTitle("SpectrumPY Beta Accelerator Plot")
        self.sc = SQLMplCanvas(data=self.df, parent=self, width=4, height=4, dpi=100)
        im1 = self.sc.ax.scatter(data["Velocity (km/s)"], data["Charge (C)"]/data["Mass (kg)"], c=data["Radius (m)"], cmap='RdYlBu')  # , size=data["Radius (m)"])
        divider = make_axes_locatable(self.sc.ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        cbar = self.sc.fig.colorbar(im1, cax=cax, orientation='vertical')
        cbar.ax.get_yaxis().labelpad = 15
        cbar.ax.set_ylabel('Radius (m)', rotation=270)

        self.toolbar = NavigationToolbar(self.sc, self)

        self.v_layout = QtWidgets.QVBoxLayout()

        self.v_layout.addWidget(self.toolbar)
        self.v_layout.addWidget(self.sc)

        dummyWidget = QtWidgets.QWidget()
        dummyWidget.setLayout(self.v_layout)
        self.setCentralWidget(dummyWidget)

        self.sc.figure.canvas.draw()
        self.show()


"""
app = QtWidgets.QApplication(sys.argv)
app.setStyle("Fusion")

timebase = [1626223747962, 1626223758587, 1626223765555, 1626223774395, 1626223774950, 1626223797395, 1626223817939, 1626223822550, 1626223827865, 1626224158588, 1626224163526, 1626224182681, 1626224198761, 1626224235666, 1626224264699, 1626224264828, 1626224269871, 1626224286902, 1626224294542, 1626224313738, 1626224327959, 1626224385928, 1626224388957, 1626224425955, 1626224472756, 1626224566617, 1626224577492, 1626224592304, 1626224605569, 1626224622585, 1626224663925, 1626224669571, 1626224720584, 1626224741685, 1626224855358, 1626224860514, 1626224865762, 1626224888357, 1626225005728, 1626225006851, 1626225007536, 1626225007887, 1626225048525, 1626225056993, 1626225130576, 1626225148743, 1626225163476, 1626225171709, 1626225190304, 1626225229410, 1626225278599, 1626225316893, 1626225347523, 1626225349601, 1626225355507, 1626225399914, 1626225561977, 1626225698486, 1626225766916, 1626225784977, 1626225801415, 1626225817801, 1626225821847, 1626225841894, 1626225845894, 1626225863893, 1626225867682, 1626225870789, 1626225886931, 1626225930457, 1626225968674, 1626226005538, 1626226027428, 1626226153334, 1626226194860, 1626226281446, 1626226308939, 1626226317644, 1626226325894, 1626226342859, 1626226344797, 1626226373976, 1626226387837, 1626226391868, 1626226403757, 1626226483783, 1626226533608, 1626226604948, 1626226635775, 1626226658901, 1626226778812, 1626226785841, 1626226795796, 1626226805999, 1626226807858, 1626226813827, 1626226860593, 1626226939809]


# timebase = [1610582973656.163, 1610585338509.92, 1610585953564.734, 1610585988674.428, 1610585996455.589, # 1610585997151.357, 1610586251250.198, 1610586629076.907]

window = SQLWindow(timebase)
window.show()
app.exec()

"""