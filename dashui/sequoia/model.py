import os, sys
here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here+'/../..')
import numpy as np
from PyChop import PyChop2

yamlpath = os.path.join(here, '../../SEQUOIA/PyChop/sequoia-06212019.yaml')

def res_vs_E(E, chopper='', chopper_freq=600., Ei=100.):
    instrument = PyChop2(yamlpath, chopper, chopper_freq)
    res, flux = instrument.getResFlux(Etrans=E, Ei_in=Ei)
    return res

def elastic_res_flux(chopper='SEQUOIA-100-1.5-SMI', chopper_freq=600., Ei=100.):
    instrument = _getModel(yamlpath, chopper, chopper_freq)
    res, flux = instrument.getResFlux(Etrans=0., Ei_in=Ei)
    return res[0], flux[0]*3*deteff(Ei)*absorption(Ei)*Ei

def elastic_resolution(chopper='SEQUOIA-100-1.5-SMI', chopper_freq=600., Ei=100.):
    instrument = _getModel(yamlpath, chopper, chopper_freq)
    try:
        return instrument.getResolution(Etrans=0., Ei_in=Ei)[0]
    except:
        return 0.

model_cache = {}
def _getModel(path, chopper, chopper_freq):
    key = path, chopper, chopper_freq
    if key not in model_cache:
        model = PyChop2(path, chopper, chopper_freq)
        model_cache[key] = model
    else:
        model = model_cache[key]
    return model

#https://jupyter.sns.gov/user/lj7/notebooks/dv/sns-chops/resolution/SEQUOIA/PyChop/pychop%20-%20Intensity%20and%20VRes_vs_Ei.ipynb
#
v =  8.314*(300.)/(10*101325)/6.022e23 * 1e30  # AA^3
# print 1/v
xs = 5333. # barn
v/xs  # cm
mu_He3 = xs/v
import unit_conversion as Conv
pixelsize = 2.54 * .7
def deteff(E):
    v = Conv.e2v(E)
    return 1.-np.exp(-2200./v*mu_He3*pixelsize)
a = 3.03 # AA
xs = 5 # barn
mu_V = xs/a**3  # 1./cm
V_thickness = .9 #cm
def absorption(E):
    v = Conv.e2v(E)
    return np.exp(-2200./v*V_thickness*mu_V)

