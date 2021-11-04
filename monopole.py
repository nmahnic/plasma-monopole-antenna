from scipy import pi
from scipy.special import jv
from sympy import abc, sin
import sympy
import mpmath
import numpy as np
from sympy.utilities.lambdify import lambdify
import matplotlib.pyplot as plt

class Monopole:
    e_o = 8.85e-12

    def __init__(self, wp, v_col, f, ro, l):
        self.wp = wp
        self.v_col = v_col
        self.f = f
        self.w = 2*pi*f
        self.ro = ro
        self.l = l


    def rou(self, wp, v_col,w):
        return (((wp**2)/((2*pi*w)**2+(v_col)**2))*v_col*self.e_o)**-1

    def kp(self, rou1, f):
        return ((1-1j)/((2*rou1)/(2*pi*f*4*pi*1e-7))**0.5)

    def Zint(self, k1, rou2, ro):
        return ((rou2*k1)/(2*pi*ro))*((self.besselFunc(0,k1*ro))/(self.besselFunc(1,k1*ro)))

    def leff(self, w, l):
        return ((2*sin((w*l)/(6e8))**2)/((((w)/(3e8)))*sin((w*l)/(3e8))))

    def leff_f(self, f, l):
        return ((2*sin((l*f*2*pi)/(6e8))**2)/((((f*2*pi)/(3e8)))*sin((f*2*pi*l)/(3e8))))

    def besselFunc(self, n, x):
        # print("bessel: ",n,x)
        if type(x) == type(0) or type(x) == type(1.0) or type(x) == type(1.0+1.0j):
            mpmath.mp.dps = 15; mpmath.mp.pretty = True
            return mpmath.besselj(n,x)
        else:
            return sympy.besselj(n,x)
