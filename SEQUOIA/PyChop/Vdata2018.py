# coding: utf-8

# Vanadium calibration data for resolution and flux from 2018

import os, numpy as np
datadir = os.path.expanduser('~/dv/sns-chops/resolution/SEQUOIA')


import pandas as pd
import numpy as np
import scipy as sp
import plotly, plotly.plotly as py, plotly.figure_factory as ff, plotly.graph_objs as go



class ExpData:
    
    def __init__(self, datafile=os.path.join(datadir, './V_Cali_Int_Res_FC1_2018.dat')):
        # read data
        print "reading data. please wait..."
        vdata = self.vdata = pd.read_csv(datafile, delimiter=' ')
        print "  done"
        self.choppers = choppers = np.array(vdata.chopper_choice, dtype=int)
        # the chopper index was a custom index of the name list ['highres', 'highflux']. 
        # See generate-resolution-data-from-V-experiments-Alltogether-2.ipynb
        # Mapping it to Chopper? tag in the mantid nexus file: 0->2, 1->1.
        self.chopper_freqs = np.array([getattr(vdata, "Chopper%d"%(2-c,))[i] for i, c in enumerate(choppers)])
        self.intensity = vdata.Height * vdata.Sigma * np.sqrt(2.*np.pi)
        self.resolution = resolution = vdata.Sigma
        self.FWHM = resolution * 2.355
        self.Ei_list = list(vdata.Energy.unique())
        return
    
    
    def getDataArr(self, name):
        if hasattr(self, name): return getattr(self, name)
        return getattr(self.vdata, name)


    def createPlotXY_on_condition(self, condition, x, y, extra_info={}, mode='markers'):
        # print x,y
        labels = [''] * int(condition.sum())
        for attr_name, (attr_label, format_str) in extra_info.iteritems():
            fmt = '%s='+format_str
            for i,v in enumerate(self.getDataArr(attr_name)[condition]):
                labels[i] += fmt % (attr_label, v) + '\n'
                continue
            continue
        trace = go.Scatter(
            x = self.getDataArr(x)[condition],
            y = self.getDataArr(y)[condition],
            mode = mode, # 'markers+text',
            text = labels,
            textposition='top center',
            hoverinfo = 'x + y + text'
        )
        return trace