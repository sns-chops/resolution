import os, sys
here = os.path.abspath(os.path.dirname(__file__))

import numpy as np

from PyChop import PyChop2

yamlpath = os.path.join(here, '../../CNCS/PyChop/cncs-06082019.yaml')

scale_flux = 600

freqs = {
    'High Resolution': 180.,
    'Intermediate': 240.,
    'High Flux': 300.,
}

def res_vs_E(E, chopper, Ei=100.):
    instrument = PyChop2(yamlpath)
    instrument.setChopper(chopper)
    res, flux = instrument.getResFlux(Etrans=E, Ei_in=Ei, frequency=freqs[chopper])
    return res

def elastic_res_flux(chopper, Ei=100.):
    instrument = PyChop2(yamlpath)
    instrument.setChopper(chopper)
    res, flux = instrument.getResFlux(Etrans=0., Ei_in=Ei, frequency=freqs[chopper])
    return res[0], flux[0]*scale_flux

def main():
    E = np.arange(0., 100., 5.)
    res = res_vs_E(E, 'Intermediate')
    print(res)
    return

if __name__ == '__main__': main()














