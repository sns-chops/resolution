"""
We are applying corrections to PyChop model to match the experimental data.
However, we should actually apply the correction to the experimental data to match 
model.
"""


import os, sys
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here+'/../..')
import numpy as np

from PyChop import PyChop2

yamlpath = os.path.join(here, '../../CNCS/PyChop/cncs-06082019.yaml')

scale_flux = 3e2 * 0.00980989028558523 # https://jupyter.sns.gov/user/lj7/notebooks/dv/sns-chops/resolution/CNCS/PyChop/pychop%20-%20Intensity%20and%20VRes_vs_Ei.ipynb

freqs = {
    'High Resolution': 180.,
    'Intermediate': 240.,
    'High Flux': 300.,
}

def res_vs_E(E, chopper, Ei=100.):
    instrument = _getModel(yamlpath, chopper)
    res, flux = instrument.getResFlux(Etrans=E, Ei_in=Ei, frequency=freqs[chopper])
    return res

def elastic_res_flux(chopper, Ei=100.):
    instrument = _getModel(yamlpath, chopper)
    res, flux = instrument.getResFlux(Etrans=0., Ei_in=Ei, frequency=freqs[chopper])
    return res[0], flux[0]*scale_flux*deteff(Ei)*absorption(Ei)

model_cache = {}
def _getModel(path, chopper):
    key = path, chopper
    if key not in model_cache:
        model = PyChop2(path)
        model.setChopper(chopper)
        model_cache[key] = model
    else:
        model = model_cache[key]
    return model

def main():
    E = np.arange(0., 100., 5.)
    res = res_vs_E(E, 'Intermediate')
    print(res)
    return

# corrections for flux
import unit_conversion as Conv
# He3
v =  8.314*(300.)/(10*101325)/6.022e23 * 1e30  # AA^3
xs = 5333. # barn
mu_He3 = xs/v
pixelsize = 2.54 * .7
def deteff(E):
    v = Conv.e2v(E)
    return 1.-np.exp(-2200./v*mu_He3*pixelsize)
# V
a = 3.03 # AA
xs = 5 # barn
mu_V = xs/a**3  # 1./cm
V_thickness = .9 #cm
def absorption(E):
    v = Conv.e2v(E)
    return np.exp(-2200./v*V_thickness*mu_V)

if __name__ == '__main__': main()














