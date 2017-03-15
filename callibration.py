#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 15:05:14 2017

@author: juanma
"""

import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler


from matplotlib.figure import Figure

import sys
if sys.version_info[0] < 3:
    from Tkinter import *
else:
    from tkinter import *

class WndCal(Frame):
    
    def __init__(self, parent):
        self._parent = parent
        
        # Title of the window
        parent.title("Callibration")
        
        # The matplotilb figure
        self._figure = Figure(figsize=(5,4), dpi=100)        
        axes = self._figure.add_subplot(111)
        
        # Removing the uwanted things of the axes
        axes.tick_params(axis="both",
                         which="both",
                         top="off",
                         bottom="off",
                         left="off",
                         right="off",
                         labelbottom="off",
                         labelleft="off")       
        
        # Packing the figure
        canvas = FigureCanvasTkAgg(self._figure, master=parent)
        canvas.show()
        canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)
        
        
    def go_exit(self):
        self._parent.destroy()
    
    


def main():
    root = Tk()
    #root.geometry("500x400+300+300")
    app = WndCal(root)
    root.mainloop()
    
    
if __name__ == '__main__':
    main()