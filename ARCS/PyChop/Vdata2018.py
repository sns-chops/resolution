# coding: utf-8

# Vanadium calibration data for resolution and flux from 2018

import os, numpy as np
# datadir = os.path.expanduser('~/notebooks/ARCS')
datadir = os.path.expanduser('~/dv/sns-chops/resolution/ARCS')


import pandas as pd
import numpy as np
import scipy as sp


class ExpData:
    
    def __init__(self, datafile=os.path.join(datadir, './V_Cali_Int_Res_FC1_2018.dat')):
        # read data
        print "reading data. please wait..."
        vdata = self.vdata = pd.read_csv(datafile, delimiter=' ')
        print "  done"
        self.choppers = choppers = np.array(vdata.Chopper, dtype=int)
        self.chopper_freqs = np.array([getattr(vdata, "Chopper%d"%c)[i] for i, c in enumerate(choppers)])
        self.intensity = vdata.Height * vdata.Sigma * np.sqrt(2.*np.pi)
        self.resolution = resolution = vdata.Sigma
        self.FWHM = resolution * 2.355
        self.Ei_list = list(vdata.Energy.unique())
        return
    
    
    def getDataArr(self, name):
        if hasattr(self, name): return getattr(self, name)
        return getattr(self.vdata, name)


