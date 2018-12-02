#!/usr/bin/env python

import numpy as np

class Instrument:

    IE_params = None
    def I_E(self, E):
        c, R1, T1, R2, T2, R3, T3, a, b, Ecut, s, delta, g, I = self.IE_params
        return I_E(E, c, R1, T1, R2, T2, R3, T3, a, b, Ecut, s, delta, g, I)

    def IC_atE(self, E):
        "E: unit eV"
        A,B,R,to = self.computeICParams(E)
        def _(t):
            return IC(t, A,B,R,to)
        return _

    L_MF = 11.61 # mod-fc distance. meter.
    def time_distrib_thru_fc(self, t, t0, E, fc):
        return time_distrib_thru_fc(
            t, t0, E, self.L_MF, fc.delta_t(), self.I_E, self.IC_atE)

    def plot_IC_atE(self, E):
        params = self.computeICParams(E)
        t = np.arange(0, 1000., 1)
        I = IC(t, *params)
        from matplotlib import pyplot as plt
        plt.figure()
        plt.plot(t,I)
        plt.show()
        plt.close()
        return

    def check_IC_sumrule(self, E):
        params = self.computeICParams(E)
        t0 = params[-1]
        # print t0
        t = np.arange(0, 100., 0.1)
        I = IC(t, *params)
        dt = t[1]-t[0]
        assert np.isclose(I.sum()*dt, 1, rtol=2e-2)
        return

    It_params = None
    def computeICParams(self, E):
        "compute parameters in Ikeda Carpenter function for given E (eV)"
        funcs = map(build_func, self.It_params)
        return [func(E) for func in funcs]


def IC(t, A, B, R, to):
    """t: microsecond"""
    from numpy import exp
    r = (1.-R)*A/2.*(A*(t-to))**2 * exp(-A*(t-to)) \
        +R*B*(A/(A-B))**3 *(
            exp(-B*(t-to)) 
            - exp(-A*(t-to))*(1+(A-B)*(t-to)
                                 +0.5*(A-B)**2*(t-to)**2)
        )
    r[t<to] = 0
    return r

def time_distrib_thru_fc(t, t0, E, L, dt_fc, I_E, f_t_E):
    """
    t: microsecond
    t0: microsecond
    E: eV
    L: meter
    dt_fc: microsecond
    t: microsecond
    """
    from mcni.utils import conversion as Conv
    v = Conv.e2v(E*1000)
    t_fc = L/v + t0/1e6
    t_travel = t_fc - t/1e6 # second
    v1 = L/t_travel # m/s
    E1 = Conv.VS2E * v1*v1 # in meV
    E1 /= 1000 # in eV
    res = I_E(E1) * 2*E1*dt_fc*1.e-6/t_travel*f_t_E(E1)(t)
    res[t_travel<0] = 0
    return res

def I_E(E, c, R1, T1, R2, T2, R3, T3, a, b, Ecut, s, delta, g, I):
    from numpy import exp, sqrt, power
    k = 8.617e-5 # eV/K
    B = 7.36e-3 # eV
    D = lambda E: 1/(1+(Ecut/E)**s)
    x = g*(E-2*B)
    x[E<2*B] = 0
    rho = 1 + delta*exp(-x)*(1 + x +0.5*x**2)
    # impl copied from SNS_source_analytic component
    arg1 = I*1.0e12 * exp(-c/sqrt(E));
    arg2 = R1*E/power(k*T1,2) *exp(-E/(k*T1));
    arg3 = R2*E/power(k*T2,2) *exp(-E/(k*T2));
    arg4 = R3*E/power(k*T3,2) *exp(-power(E/(k*T3),b));
    arg5 = D(E)*rho/power(E,1-a);
    arg6 =(arg1 * ( arg2 + arg3 + arg4 + arg5 ));
    return arg6
            
# fitfit function
def f(x, a,b,c,d,f,g,h,i,j,k):
    return a*x**b*(1+c*x+d*x**2+(x/f)**g)/(1+h*x+i*x**2+(x/j)**k)

# this is only used by computeICParams
def build_func(param_str):
    params = map(float, param_str.split())
    return lambda x: f(x, *params)
