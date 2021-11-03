"""
main.py
"""
from animation import Animation
import tkinter as tk
import numpy as np
from matplotlib.backends import backend_tkagg
from functions import Functionx, multiplies_var
import matplotlib.pyplot as plt
from locate_mouse import in_bounds, locate_mouse

from scipy import pi
from scipy.special import jv
from monopole import Monopole
from sympy.utilities.lambdify import lambdify
from sympy import abc
import sympy


def change_array(x_arr: np.ndarray, y_arr: np.ndarray,
                 x: float, y: float) -> np.ndarray:
    """
    Given a location x that maps to a value y,
    and an array x_arr which maps to array y_arr, find the closest
    element in x_arr to x. Then, change its corresponding
    element in y_arr with y.
    """

    if (x < x_arr[0]) or (x > x_arr[-1]):
        return y_arr

    closest_index = np.argmin(np.abs(x_arr - x))
    y_arr[closest_index] = y

    return y_arr


class Main(Animation):
    """
    The main part of the program.
    """
    def __init__(self) -> None:
        """
        The constructor.
        """

        # Make all of the matplotlib objects
        Animation.__init__(self)

        self.f0 = Functionx("8.8541878128e-12*(wp**2)/(v_col+(x*2*3.14159265359))")
        self.figuration()
        # Tkinter main window
        self.window = tk.Tk()

        colour = self.window.cget('bg')
        if colour == 'SystemButtonFace':
            colour = "#F0F0F0"

        self.figure.patch.set_facecolor(colour)

        self.window.title("Plot")
        self.window.configure()

        # Canvas
        self.canvas = \
            backend_tkagg.FigureCanvasTkAgg(
                self.figure,
                master=self.window
            )
        self.canvas.get_tk_widget().grid(
            row=0,
            column=0,
            rowspan=19,
            columnspan=2
        )
        self.enter_function_button = tk.Button(self.window,
                                               text="DEFAULT VALUES",
                                               command=
                                               self.update_function_by_entry)
        self.enter_function_button.grid(
            row=2,
            column=3,
            columnspan=2,
            sticky=tk.W + tk.E + tk.N,
            padx=(10, 10)
        )
        self.slider_frequency = tk.Scale(
                    self.window,
                    label="Change Frequency [MHz]",
                    from_=30, 
                    to=300,
                    resolution=1,
                    orient=tk.HORIZONTAL,
                    length=200,
                    command=self.slider_frequency_update
                )
        self.slider_frequency.set(152)
        self.slider_frequency.grid(
            row=15,
            column=3,
            columnspan=2,
            sticky=tk.W + tk.E + tk.N,
            padx=(10, 10)
        )
        self.inductanceLabel = tk.Label(self.window)
        self.inductanceLabel.grid(
                row=16,
                column=3,
                columnspan=1,
                sticky=tk.W + tk.E + tk.S,
                padx=(10, 10)
        )
        self.function_range = {
            "Rs" : {
                "v_col": {
                    "default": 500,
                    "from": 1,
                    "to": 1000,
                    "resolution": 10,
    
                },
                "wp": {
                    "default": 61.779,
                    "from": 6,
                    "to": 100,
                    "resolution": 0.1,
                },
                "l": {
                    "default": 450e-3,
                    "from": 100e-3,
                    "to": 2000e-3,
                    "resolution": .50e-3,
                },
                "r": {
                    "default": 12e-3,
                    "from": 5e-3,
                    "to": 30e-3,
                    "resolution": 1e-3,
                },
            },
        }
        self.function_menu_string = tk.StringVar(self.window)
        self.current_function = "Rs"
        self.function_menu_string.set(self.current_function)
        self.sliderslist = []
        print("HOLA 2")
        self.set_sliders()

    def figuration(self):
        self.ax = self.figure.subplots(nrows=1, ncols=1)
        #self.figure.subplots_adjust(wspace=0.75, hspace=0.75)
        # self.figure.tight_layout()

        self.zint = self.monopoleImpedance(500e6,61.779e9,450e-3,12e-3)
        self.leff = self.monopoleEffectivLength(500e6,61.779e9,450e-3,12e-3)

        self.x1 = np.linspace(30e6,300e6,100000)
        self.y1 = self.zint(self.x1).real*self.leff(self.x1).real

        self.x2 = self.x1
        self.y2 = self.zint(self.x1).imag*self.leff(self.x1).real

        self.freq = 152e6
        self.reactance = self.zint(self.freq).imag*self.leff(self.freq).real

        line, = self.ax.plot(self.x1, self.y1, label="Resistance")
        line2, = self.ax.plot(self.x2, self.y2, label="Reactance")
        line3, = self.ax.plot(self.freq, self.reactance, "or")

        self.ax.set_xlim(self.x1[0], self.x1[-1])
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("freq")
        self.ax.set_ylabel("Impedance")
        self.ax.set_title("Impedance(freq)")
        self.ax.grid(True,which="both")
        self.ax.axvline(x=152e6, ls=':', c='g', label="Reference of 152MHz")
        self.ax.axvline(x=141e6, ls=':', c='y', label="Reference of 141MHz")
        self.ax.set_xscale("log")

        leg = self.ax.legend(loc='upper left')

        self.line = line
        self.line2 = line2
        self.line3 = line3
    

        # xbounds = self.ax.get_xlim()
        # ybounds = self.ax.get_ylim()
        # s = (-xbounds[0] + xbounds[1])/600 + xbounds[0]
        # y = (ybounds[1] - ybounds[0])*0.9 + ybounds[0]

        # self.text = self.ax.text(s, y, "f(x) = mash")
        # self.text.set_bbox({"facecolor": "white", "alpha": 1.0})
        self.autoaddartists = True
    
    def monopoleImpedance(self, v_col, wp, l, ro):
            print("wp=",wp," v_col=",v_col," l=",l,"ro=",ro)
            a = Monopole(wp,v_col,abc.x,ro,l)
            c = a.Zint(a.kp(a.rou(wp,v_col,abc.x),abc.x),a.rou(wp,v_col,abc.x),ro)
            # b = a.leff(2*pi*abc.x,l)
            bessel = {'besselj': jv}
            libraries = [bessel, "numpy"]  
            return lambdify(abc.x, c, modules=libraries)

    def monopoleEffectivLength(self, v_col, wp, l, ro):
            print("wp=",wp," v_col=",v_col," l=",l,"ro=",ro)
            a = Monopole(wp,v_col,abc.x,ro,l)
            b = a.leff(2*pi*abc.x,a.l)
            # b = a.leff(2*pi*abc.x,l)
            bessel = {'besselj': jv}
            libraries = [bessel, "numpy"]  
            return lambdify(abc.x, b, modules=libraries)

    def _update_appearance(self) -> None:
        """
        Helper function that updates the appearance of the function.
        """
        # print("MASSSSH:",type(self.y1))
        # print(self.y1)
        # print(self.y2)
        print("Lint = {:.4e}".format(self.reactance/(2*pi*self.freq)),"Hy")
        print("XLint = {:.4e}".format(self.reactance),"\u03A9")
        #print("Rint = {:.4e}".format(self.reactance),"\u03A9")
        indText = "Inductance ={: .2e}".format(self.reactance/(2*pi*self.freq))+" Hy"
        self.inductanceLabel.configure(text=indText)

        self.line.set_ydata(self.y1)
        self.line2.set_ydata(self.y2)
        self.line3.set_ydata(self.reactance)
        self.line3.set_xdata(self.freq)

    def _update_function(self, str_args: str) -> None:
        """
        Helper function for update_function_by_entry and
        update_function_by_preset.
        """
        self.f = Functionx(str_args)
        self.set_sliders()
        self.slider_update()
        self._update_appearance()
        self.text.set_text("f(x) =")

    def update_function_by_entry(self, *event: tk.Event) -> None:
        """
        Update the function.
        """
        self.sliderslist[0].set(self.default_vals['v_col'])
        self.sliderslist[1].set(self.default_vals['wp'])
        self.sliderslist[2].set(self.default_vals['l'])
        self.sliderslist[3].set(self.default_vals['r'])

        print(self.default_vals)
        self.zint = self.monopoleImpedance(
            self.default_vals['v_col']*1e6,
            self.default_vals['wp']*1e9,
            self.default_vals['l'],
            self.default_vals['r']
            )
        self.leff = self.monopoleEffectivLength(
            self.default_vals['v_col']*1e6,
            self.default_vals['wp']*1e9,
            self.default_vals['l'],
            self.default_vals['r']
            )

        print("EQUAL1: ", self.zint(self.x1).real*self.leff(self.x1).real == self.y1)
        print("EQUAL2: ", self.zint(self.x1).imag*self.leff(self.x1).real == self.y2)
        
        self.y1 = self.zint(self.x1).real*self.leff(self.x1).real
        self.y2 = self.zint(self.x1).imag*self.leff(self.x1).real
        self.reactance = self.zint(self.freq).imag*self.leff(self.freq).real

        self._update_appearance()

    def slider_frequency_update(self, *event: tk.Event) -> None:
        self.freq = self.slider_frequency.get()*1e6
        print("HOLA FREQUENCY", self.freq)

        self.reactance = self.zint(self.freq).imag*self.leff(self.freq).real
        self._update_appearance()


    def slider_update(self, *event: tk.Event) -> None:
        """
        Update the functions given input from the slider.
        """
        print("Slider_update ->")

        tmplist = []
        for i in range(len(self.sliderslist)):
            tmplist.append(self.sliderslist[i].get())
            print(i,": ",self.sliderslist[i].get())
        #print(tmplist)
        
        self.zint = self.monopoleImpedance(tmplist[0]*1e6, tmplist[1]*1e9, tmplist[2], tmplist[3])
        self.leff = self.monopoleEffectivLength(tmplist[0]*1e6, tmplist[1]*1e9, tmplist[2], tmplist[3])

        print("EQUAL1: ", self.zint(self.x1).real*self.leff (self.x1).real == self.y1)
        print("EQUAL2: ", self.zint(self.x1).imag*self.leff (self.x1).real == self.y2)
        
        self.y1 = self.zint(self.x1).real*self.leff (self.x1).real
        self.y2 = self.zint(self.x1).imag*self.leff (self.x1).real
        self.reactance = self.zint(self.freq).imag*self.leff (self.freq).real
        self._update_appearance()

    def update_function_by_mouse(self, event: tk.Event) -> None:
        """
        Update the function by mouse.
        """
        bounds = list(self.ax[0].get_xlim())
        bounds.extend(self.ax[0].get_ylim())
        pixel_bounds = [120, 430, 494, 530, 865, 632]
        bounds_ft = list(self.ax[1].get_xlim())
        bounds_ft.extend(self.ax[1].get_ylim())
        pixel_ft_bounds = [120, 78, 493, 180, 863, 279] 
        height = self.canvas.get_tk_widget().winfo_height()
        if in_bounds(event, pixel_bounds, height):
            x, y = locate_mouse(event, bounds, height, pixel_bounds)
            change_array(self.x1, self.y1, x, y)
            self._update_appearance()
        elif in_bounds(event, pixel_ft_bounds, height):
            x, y = locate_mouse(event, bounds_ft, height, pixel_ft_bounds)
            # y = -y if (int(x/(self.freq[1] - self.freq[0]))) % 2 else y
            change_array(self.freq, self.fourier_amps, x, y)
            change_array(self.freq, self.fourier_amps, -x, y)
            self.line.set_ydata(self.y1)
            self.line2.set_ydata(self.y2)

    def set_sliders(self) -> None:
        """
        Create and set sliders.
        """

        for slider in self.sliderslist:
            slider.destroy()
        self.sliderslist = []
        self.default_vals = dict()
        for key in self.function_range[str(self.current_function)]:
            a = {key: self.function_range[str(self.current_function)][key]['default']}
            self.default_vals.update(a)

        for i, symbol in enumerate(self.function_range[str(self.current_function)]):
            self.sliderslist.append(tk.Scale(
                    self.window,
                    label="change " + str(symbol) + ":",
                    from_=self.function_range[str(self.current_function)][str(symbol)]["from"], 
                    to=self.function_range[str(self.current_function)][str(symbol)]["to"],
                    resolution=self.function_range[str(self.current_function)][str(symbol)]["resolution"],
                    orient=tk.HORIZONTAL,
                    length=200,
                    command=self.slider_update
                )
            )
            self.sliderslist[i].grid(row=i + 4, column=3,
                                     padx=(10, 10), pady=(0, 0))
            self.sliderslist[i].set(self.default_vals[symbol])

    def update(self, delta_t: float) -> None:
        # print_to_terminal("fps: %d" % (int(1.0/delta_t)))
        pass


if __name__ == "__main__":
    run = Main()
    run.animation_loop()
    tk.mainloop()
