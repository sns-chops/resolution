import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import numpy as np, pandas as pd
import plotly.graph_objs as go

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
                                                                                                                   
alldata = ExpData(os.path.join(here, '../../SEQUOIA/V_Cali_Int_Res_All-IPTS_22666.dat'))

# scale factor from https://jupyter.sns.gov/user/lj7/notebooks/dv/sns-chops/resolution/SEQUOIA/plotly-plot-2.ipynb
alldata.intensity *= 580000

# unique Eis
unique_nominal_Eis = set( list(alldata.Ei_list) )
unique_nominal_Eis = sorted(list(unique_nominal_Eis))

# find Ei that has more than one data points
Eis = []
for n_Ei in unique_nominal_Eis:
    good = False
    for chopper_index in range(2):
        condition = (alldata.vdata.chopper_choice==chopper_index)&(alldata.vdata.Energy==n_Ei)
        if condition.sum() > 1:
            good = True; break
    if not good: continue
    Eis.append(n_Ei)
    continue
good_Eis = Eis; del Eis
