from scipy import pi
import scipy.constants as cts
from scipy.special import jv
from sympy import abc, sin
import sympy
import mpmath
import numpy as np
from sympy.utilities.lambdify import lambdify
import matplotlib.pyplot as plt

class Monopole:
    e_o = cts.epsilon_0
    co = cts.c

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

    def Zint(self):
        rou2 = self.rou(self.wp,self.v_col,self.f)
        k1 = self.kp(rou2,self.f)
        return ((rou2*k1)/(2*pi*self.ro))*((self.besselFunc(0,k1*self.ro))/(self.besselFunc(1,k1*self.ro)))

    def leff(self):
        return ((2*sin((self.w*self.l)/(2*self.co))**2)/((((self.w)/(self.co)))*sin((self.w*self.l)/(self.co))))

    def besselFunc(self, n, x):
        # print("bessel: ",n,x)
        if type(x) == type(0) or type(x) == type(1.0) or type(x) == type(1.0+1.0j):
            mpmath.mp.dps = 15; mpmath.mp.pretty = True
            return mpmath.besselj(n,x)
        else:
            return sympy.besselj(n,x)
