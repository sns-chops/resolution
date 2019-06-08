import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import numpy as np, pandas as pd, scipy as sp
import plotly, plotly.plotly as py, plotly.figure_factory as ff, plotly.graph_objs as go

# data
import resolution_plot
class ExpData(resolution_plot.ExpData):
    def __init__(self, datafile):
        # read data
        print("reading data. please wait...")
        vdata = self.vdata = pd.read_csv(datafile, delimiter=' ')
        print("  done")
        self.choppers = choppers = np.array(vdata.chopper_choice, dtype=int)
        # the chopper index was a custom index of the name list ['highres', 'highflux'].
        # See generate-resolution-data-from-V-experiments-Alltogether-2.ipynb
        # Mapping it to Chopper? tag in the mantid nexus file: 0->2, 1->1.
        self.chopper_freqs = np.array([getattr(vdata, "Chopper%d"%(2-c,))[i] for i, c in enumerate(choppers)])
        self.intensity = vdata.Height * vdata.Sigma * np.sqrt(2.*np.pi)
        self.resolution = resolution = vdata.Sigma
        self.FWHM = resolution * 2.355
        self.FWHM_percentages = self.FWHM/vdata.Energy * 100.
        self.Ei_list = list(vdata.Energy.unique())
        return
                                                                                                                   
#expdata_highres = Vdata2018.ExpData(os.path.join(Vdata2018.datadir, './V_Cali_Int_Res_HighRes.dat'))
#expdata_interm = Vdata2018.ExpData(os.path.join(Vdata2018.datadir, './V_Cali_Int_Res_Intermediate.dat'))
#expdata_highflux = Vdata2018.ExpData(os.path.join(Vdata2018.datadir, './V_Cali_Int_Res_HighFlux.dat'))

