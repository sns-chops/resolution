# coding: utf-8

import os, numpy as np
# datadir = os.path.expanduser('~/notebooks/ARCS')
datadir = os.path.expanduser('~/dv/sns-chops/resolution/ARCS')


import pandas as pd
import numpy as np
import scipy as sp
import plotly, plotly.plotly as py, plotly.figure_factory as ff, plotly.graph_objs as go

from ipywidgets import widgets
from IPython.display import display, clear_output, Image
from plotly.widgets import GraphWidget


# initialize plotly
plotly.tools.set_credentials_file(username='mcvine', api_key='xPhu0GyBCi4iiEI3unYE')


class ExpData:
    
    def __init__(self, datafile=os.path.join(datadir, './V_Cali_Int_Res_FC1_2018.dat')):
        # read data
        print "reading data. please wait..."
        vdata = self.vdata = pd.read_csv(datafile, delimiter=' ')
        vtable = ff.create_table(vdata)
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


    def createPlotXY(self, Ei, x, y, extra_info={}):
        # print x,y
        condition = np.isclose(self.vdata.Energy, Ei)
        labels = [''] * condition.sum()
        for attr_name, (attr_label, format_str) in extra_info.iteritems():
            fmt = '%s='+format_str
            for i,v in enumerate(self.getDataArr(attr_name)[condition]):
                labels[i] += fmt % (attr_label, v) + '\n'
                continue
            continue
        trace = go.Scatter(
            x = self.getDataArr(x)[condition],
            y = self.getDataArr(y)[condition],
            mode = 'markers', # 'markers+text',
            text = labels,
            textposition='top center',
            hoverinfo = 'x + y + text'
        )
        return trace



