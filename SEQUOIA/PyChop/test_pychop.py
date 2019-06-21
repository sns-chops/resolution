import os, sys, glob, numpy as np

sys.path.insert(0, "/SNS/users/lj7/dv")

from PyChop import PyChop2
instrument = PyChop2('cncs.yaml')
instrument.moderator.mod_pars = [0, 0, 0]
instrument.setChopper('High Resolution')
print instrument.getResFlux(Etrans=0, Ei_in=80)
