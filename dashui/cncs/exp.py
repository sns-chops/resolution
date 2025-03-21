import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import pandas as pd
import numpy as np

# data
exp_int_to_flux = 0.00980989028558523 # https://jupyter.sns.gov/user/lj7/notebooks/dv/sns-chops/resolution/CNCS/PyChop/pychop%20-%20Intensity%20and%20VRes_vs_Ei.ipynb

import resolution_plot
class ExpData(resolution_plot.ExpData):
    def __init__(self, datafile):
        # read data
        print("reading data. please wait...")
        vdata = self.vdata = pd.read_csv(datafile, delimiter=' ')
        print("  done")
        self.intensity = vdata.Height * vdata.Sigma * np.sqrt(2.*np.pi)
        self.flux = vdata.counts * exp_int_to_flux
        self.resolution = resolution = vdata.Sigma
        self.FWHM = resolution * 2.355
        self.FWHM_percentages = self.FWHM/vdata.Energy * 100.
        self.Ei_list = list(vdata.Energy.unique())
        return
    

datadir = os.path.join(here, '../../CNCS/')
expdata_highres = ExpData(os.path.join(datadir, './V_Cali_Int_Res_HighRes_E500bins.dat'))
expdata_interm = ExpData(os.path.join(datadir, './V_Cali_Int_Res_Intermediate.dat'))
expdata_highflux = ExpData(os.path.join(datadir, './V_Cali_Int_Res_HighFlux.dat'))

data = {
    'High Resolution': expdata_highres,
    'Intermediate': expdata_interm,
    'High Flux': expdata_highflux,
}
