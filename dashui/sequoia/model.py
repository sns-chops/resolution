
import os, sys
# sys.path.insert(0, os.path.expanduser('~/dv'))
here = os.path.abspath(os.path.dirname(__file__))

import numpy as np

from PyChop import PyChop2

yamlpath = os.path.join(here, '../../SEQUOIA/PyChop/sequoia-06212019.yaml')

scale_flux = 600

def res_vs_E(E, chopper='', chopper_freq=600., Ei=100.):
    instrument = PyChop2(yamlpath, chopper, chopper_freq)
    res, flux = instrument.getResFlux(Etrans=E, Ei_in=Ei)
    return res

def elastic_res_flux(chopper='SEQUOIA-100-1.5-SMI', chopper_freq=600., Ei=100.):
    instrument = PyChop2(yamlpath, chopper, chopper_freq)
    res, flux = instrument.getResFlux(Etrans=0., Ei_in=Ei)
    return res[0], flux[0]*scale_flux














