#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 17:20:34 2022

@author: ethanayari
"""

import pyodbc
# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port
server = '192.168.1.102,3306'
database = 'CCLDAS_PRODUCTION'
username = 'smallacc'
password = 'get dusty'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER=' + server
                      + ';DATABASE=' + database+';UID=' + username+';PWD=' +
                      password)
print("Connection Successful!")
cursor = cnxn.cursor()
cursor.execute("""SELECT * FROM sys.Tables""")
row = cursor.fetchone()
while row:
    print(row[0])
    row = cursor.fetchone()
