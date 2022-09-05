#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 17:20:34 2022

A graphical interface for the IMPACT acclerator server

@author: ethanayari
"""
import sys

import pandas as pd

from sqlalchemy import create_engine
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt


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


class SQLWindow(QtWidgets.QMainWindow):
    def __init__(self, timebase):
        super().__init__()
        self.setWindowTitle("SpectrumPY Beta Accelerator Window")

        self.table = QtWidgets.QTableView()
        db_connection_str = 'mysql+pymysql://root:Loucet59@localhost/impact081622'
        db_connection = create_engine(db_connection_str)

        self.df = pd.DataFrame()

        for time in timebase:
                time = str(time)

        self.df = pd.read_sql(('select estimate_quality, integer_timestamp, velocity, mass, charge, radius'
                      ' from dust_event where mass != -1 order by '
                      'abs(integer_timestamp-{}) limit {};'.format(time, str(len(timebase)))),
                 con=db_connection)
        self.df.columns=["Estimate Quality", "Timestep", "Velocity (km/s)", "Mass (kg)", "Charge (C)", "Radius (m)"] 
        self.df["Velocity (km/s)"] /= 1000.0
        data = self.df
        self.model = TableModel(data)
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)
        self.setGeometry(600, 100, 400, 200)


app = QtWidgets.QApplication(sys.argv)
app.setStyle("Fusion")
timebase = [1610582973656.163, 1610585338509.92, 1610585953564.734, 1610585988674.428, 1610585996455.589, 1610585997151.357, 1610586251250.198, 1610586629076.907]
window = SQLWindow(timebase)
window.show()
app.exec()
