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
from tkFileDialog   import askopenfilename, askdirectory
import tkMessageBox

# The video management system
from video_proc import *


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
        
        # The content of the video
        self._video = None
        
        # We're performing callibration
        self._onCallibrate = False
        
        # The menu
        menu = Menu(parent)
        
        parent.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open video", command=self.open_video)
        filemenu.add_command(label="Save callibration", command=self.save_callibration)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.go_exit)
        
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
        
        self._axes = axes
        #self._axes.hold(False) # To provide some cleaning
        
        # Packing the figure
        canvas = FigureCanvasTkAgg(self._figure, master=parent)
        self._canvas = canvas
        #from numpy.random import rand
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        
        # Frame for play / stop buttons
        btn_frame = Frame(self._parent)
        
        # Placing the buttons
        st = Button(btn_frame, text= "<<", command=self.go_start)
        ed = Button(btn_frame, text= ">>", command=self.go_end)
        pr = Button(btn_frame, text= "<|", command=self.go_prev)
        nx = Button(btn_frame, text= "|>", command=self.go_next)
        pl = Button(btn_frame, text= ">",  command=self.go_play)
        
        
        #btn_frame.pack(side=BOTTOM, fill=Y)
        btn_frame.pack(fill=X)
        st.pack(side=LEFT)
        pr.pack(side=LEFT)
        pl.pack(side=LEFT)
        nx.pack(side=LEFT)
        ed.pack(side=LEFT)
        
        #............................................................
        # Placing the ruler
        rlr_frame = Frame(self._parent)
        mk_st = Button(rlr_frame, text= "V", command=self.mark_start)
        mk_nd = Button(rlr_frame, text= "V", command=self.mark_end)
        
        self._ruler = Scale(rlr_frame,orient=HORIZONTAL, command=self._ruler_change)
        
        rlr_frame.pack(fill=X)
        mk_st.pack(side=LEFT)
        self._ruler.pack(side=LEFT,fill=X, expand=1)
        mk_nd.pack(side=LEFT)
        
        #............................................................
        # The button for the calculations
        clc_frame = Frame(self._parent)
        btn_calc = Button(clc_frame, text= "Callibrate", command=self.callibrate)
        clc_frame.pack(fill=X)
        btn_calc.pack(anchor=CENTER)
        

    def _ruler_change(self, value):
        if self._video == None: return
        
        
        if not(self._onCallibrate):
            value = int(value)
            img = self._video.goto(value)

            self.do_draw(img, ruler=True)
        #self._axes.clear()
        #self._axes.imshow(img)
        #self._canvas.show()
        
    def go_start(self):
        
        # If there is no video, we move out
        if self._video == None: return
        
        img = self._video.goto_start()
        self.do_draw(img)
        
        
                    
    def go_end(self):
        # If there is no video, we move out
        if self._video == None: return

        img = self._video.goto_end()
        self.do_draw(img)

    
    def go_prev(self):
        # If there is no video, we move out
        if self._video == None: return

        img = self._video.goto_prev()
        self.do_draw(img)

    
    def go_next(self):
        # If there is no video, we move out
        if self._video == None: return

        img = self._video.goto_next()
        self.do_draw(img)


    
    def go_play(self):
        # If there is no video, we move out
        if self._video == None: return
        
        for img in self._video:
            self.do_draw(img)
        
    def open_video(self):
        #name = askopenfilename()
        name = askdirectory()
        
        self._video = videofile(name)
        self._ruler.config(to=len(self._video)-1)
        img = self._video.frame()
        self.do_draw(img)

        
        
    def mark_start(self):
        valor = int(self._ruler.get())
        self._video.mark_start(valor)
        
    def mark_end(self):
        valor = int(self._ruler.get())
        self._video.mark_end(valor)

    
    def save_callibration(self):
        pass
        
        
    def go_exit(self):
        self._parent.destroy()
        
    def do_draw(self, img, ruler=False):
        if not(ruler):
            self._ruler.set(self._video._ind)

        self._axes.clear()
        self._axes.imshow(img)
        self._canvas.show()
        self._canvas.flush_events()
    
    def callibrate(self):
        self._onCallibrate=True

        ret, mtx, dist, rvecs, tvecs = callibration(self._video, (7,6), self.do_draw)
        
        
        if ret:
            tkMessageBox.showinfo("Result", "Callibration sucessful")
        else:
            tkMessageBox.showinfo("Result", "Callibration unsucessful")
            
        self._onCallibrate=False
        


def main():
    root = Tk()
    #root.geometry("500x400+300+300")
    app = WndCal(root)
    root.mainloop()
    
    
if __name__ == '__main__':
    main()