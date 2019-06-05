
import os, sys
sys.path.insert(0, os.path.expanduser('~/dv'))

import numpy as np

from PyChop import PyChop2

yamlpath = os.path.expanduser('~/dv/resolution/ARCS/PyChop/arcs-opt.yaml')


def res_vs_E(E, chopper='ARCS-100-1.5-SMI', chopper_freq=600., Ei=100.):
    instrument = PyChop2(yamlpath, chopper, chopper_freq)
    res, flux = instrument.getResFlux(Etrans=E, Ei_in=Ei)
    return res


def main():
    E = np.arange(0., 100., 5.)
    res = res_vs_E(E)
    print(res)
    return

if __name__ == '__main__': main()














