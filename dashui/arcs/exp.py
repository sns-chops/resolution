import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import numpy as np, pandas as pd, scipy as sp
import plotly, plotly.plotly as py, plotly.figure_factory as ff, plotly.graph_objs as go

# data
import resolution_plot

class ExpData(resolution_plot.ExpData):
    
    def __init__(self, datafile):
        # read data
        print( "reading data. please wait...")
        vdata = self.vdata = pd.read_csv(datafile, delimiter=' ')
        # vtable = ff.create_table(vdata)
        print("  done")
        self.choppers = choppers = np.array(vdata.Chopper, dtype=int)
        self.chopper_freqs = np.array([getattr(vdata, "Chopper%d"%c)[i] for i, c in enumerate(choppers)])
        self.intensity = vdata.Height * vdata.Sigma * np.sqrt(2.*np.pi)
        self.resolution = resolution = vdata.Sigma
        self.FWHM = resolution * 2.355
        self.FWHM_percentages = self.FWHM/vdata.Energy * 100.
        self.Ei_list = list(vdata.Energy.unique())
        return

fc1data = ExpData(os.path.join(here, '../../ARCS//V_Cali_Int_Res_FC1_2018_v2.dat'))
fc2data = ExpData(os.path.join(here, '../../ARCS/V_Cali_Int_Res_FC2_2018_v2.dat'))
fc1_highres_data = ExpData(os.path.join(here, '../../ARCS/V_Cali_Int_Res_FC1_HighRes_2018_v2.dat'))
vscatt_scale = 2.6e4
vscatt_scale *=60./1.4
vscatt_scale *= 1.5/2
fc1data.intensity *= vscatt_scale
fc2data.intensity *= vscatt_scale
fc1_highres_data.intensity *= vscatt_scale

data = {
    'ARCS-700-1.5-AST': fc1data,
    'ARCS-100-1.5-AST': fc2data,
    'ARCS-700-0.5-AST': fc1_highres_data,
}
