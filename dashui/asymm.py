"""
The idea is that the functional form of the PSF function can be nearly universal.
We use those from Ei=130meV of ARCS as the general form for all ARCS data as a
first approximation.
"""


import numpy as np

def linear(a0, a1):
    return lambda E: a0 + a1*E

def parabolic(a0, a1, a2):
    return lambda E: a0 + a1*E + a2*E*E

# data from Ei=130meV
a0_a = 0.220735832594
a1_a = -0.0012356210013
a2_a = -4.86453189362e-06
a0_b = 0.0476677481103
a1_b = -0.000415707214915
a2_b = 1.92210604173e-07
from numpy import array
x_t0 = array([   0.,   10.,   20.,   30.,   40.,   50.,   60.,   70.,   80.,
                 90.,  100.,  110.,  120., 130.])
y_t0 = array([   5.74030747,    6.17078063,    6.60218515,    7.19238872,
                 7.91124324,    9.02569315,   10.53174808,   12.61032027,
                 15.78117089,   21.19391277,   30.7701625 ,   56.60375125,  100. , 300      ])

x_sigma = array([   0.,   10.,   20.,   30.,   40.,   50.,   60.,   70.,   80.,
                    90.,  100.,  110.,  120., 130.])
y_sigma = array([  2.56952213,   2.62595814,   2.74551247,   2.86743246,
                   3.02381235,   3.16348315,   3.32458451,   3.65308239,
                   3.84840911,   4.49697484,   5.80173869,   8.62287841,  20.  , 100    ])

def positive(f):
    def _(x):
        t = f(x)
        try:
            t[t<0] = 0
            return t
        except:
            if t<0: t = 0
            return t
    return _

interped_funcs = dict(
    a = positive(parabolic(a0_a, a1_a, a2_a)),
    b = positive(parabolic(a0_b, a1_b, a2_b)),
    t0 = lambda E: np.interp(E, x_t0, y_t0),
    sigma = lambda E: np.interp(E, x_sigma, y_sigma),
    R = lambda E: 0*E+ 0.3,
)

fwhm_interp_a = array([-3.25775146e-07,  1.25946371e-04, -4.47017439e-02,  5.32418042e+00])
fwhm_interp_order = 3
def interped_fwhm(x):
    a = fwhm_interp_a
    order = fwhm_interp_order
    return sum( a[i]*x**(order-i) for i in range(order+1) )

from dgsres import icg
geom = icg.Geom(l1=11.6, l2=2.0, l3=3.)

def psf(x, E_over_Ei, fwhm):
    Emax = 107. # over this value the resolution function using interpolated params got broader.
    E0 = E_over_Ei*Emax
    params = dict()
    for name in interped_funcs.keys():
        params[name] = interped_funcs[name](E0)
    res = icg.resolution(x/fwhm*interped_fwhm(E0)+E0, Ei=130., E0=E0, geom=geom, **params)
    return res/res.sum()
