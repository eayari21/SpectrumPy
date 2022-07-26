#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 10:57:12 2022

@author: ethanayari
"""

import PyInstaller.__main__
import shutil

PyInstaller.__main__.run([
    'qt-trial.py',
    '--icon=impact.ico',
    '--name=IDEXCalQuicklook',
    '--windowed',
    '--onefile',
    '--noconsole',
], )

shutil.copytree('/Users/ethanayari/Dropbox/Mac/Documents/GitHub/SpectrumPy copy/python_dev/Anthracene_iron_7_13_2021_10kms_plus',
                'dist/Anthracene_iron_7_13_2021_10kms_plus')
