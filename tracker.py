#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 15:05:14 2017

@author: juanma
"""

import matplotlib
import json
import pandas as pd
#import cv2
matplotlib.use('TkAgg')

from numpy import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.pyplot import get_cmap
from tkFileDialog   import askopenfilename, askdirectory, asksaveasfilename
from ttk import Treeview, Scrollbar
import tkMessageBox

# The video management system
from video_proc import *


from matplotlib.figure import Figure

import sys
if sys.version_info[0] < 3:
    from Tkinter import *
else:
    from tkinter import *


from tkSimpleDialog import Dialog


class WndCal(Frame):
    
    def __init__(self, parent):
        self._parent = parent
        
        # Title of the window
        parent.title("Python Tracker")
        
        # The content of the video
        self._video = None
        
        # We're performing callibration
        self._onTrack = False
        
        # The definition of the cheess
        self._chess = { "shape" : (8, 6),
                        "size"  : 0.03}
        
        # Basic image process
        self._image = {"Brightness": 0,
                       "Contrast"  : 0,
                       "Threshold" : 126}
        
        # The results
        self._results = pd.DataFrame()
        
        # The camera callibration
        self._callibration = dict()
        
        # By default marker
        self._marker = {"marker" : [[1, 1, 1, 0, 0],
                                    [1, 0, 0, 1, 0],
                                    [1, 1, 1, 0, 0],
                                    [1, 0, 0, 1, 0],
                                    [1, 0, 0, 0, 1]],
                        "size"   : 0.03}
        
        # The menu
        menu = Menu(parent)
        
        parent.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open video",
                             command=self.open_video)
        
        filemenu.add_command(label="Open callibration",
                             command=self.open_callibration)
        
        filemenu.add_separator()

        filemenu.add_command(label="Export csv",
                             command=self.export_csv)

        
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.go_exit)
        
        markermenu = Menu(menu)
        menu.add_cascade(label="Marker", menu=markermenu)
        markermenu.add_command(label="Load marker", command=self.load_marker)
        
        # The main frame to hold the main figure the AR marker figure and
        # the treeview
        frm_main = Frame(self._parent)
        frm_main.pack(side=TOP,fill=BOTH, expand=1)
        
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
        canvas = FigureCanvasTkAgg(self._figure, master=frm_main)
        self._canvas = canvas
        #from numpy.random import rand
        canvas.show()
        canvas.get_tk_widget().pack(side=LEFT, fill=BOTH, expand=1)
        
        # Another figure for the AR marker
        self._figure2 = Figure(figsize=(1,1), dpi=100)
        axes2 = self._figure2.add_subplot(111)
        # Removing the uwanted things of the axes
        axes2.tick_params(axis="both",
                         which="both",
                         top="off",
                         bottom="off",
                         left="off",
                         right="off",
                         labelbottom="off",
                         labelleft="off")
        
        self._axes2 = axes2
        
        
        #from numpy.random import rand
        axes2.imshow(array(self._marker["marker"])*255)
        
        #......................................................
        # Another frame to hold AR and marker
        frm_submain = Frame(frm_main)
        frm_submain.pack(side=LEFT)

        # Packing the figure
        canvas2 = FigureCanvasTkAgg(self._figure2, master=frm_submain)
        self._canvas2 = canvas2
        canvas2.show()
        canvas2.get_tk_widget().pack(side=TOP)#, fill=BOTH)

        #..................................................
        # This is other frame to hold the treeview and the scroll bar
        frm_tree = Frame(frm_submain)
        frm_tree.pack(side=BOTTOM, fill=BOTH, expand=1)

        # Los scrollers
        ysb = Scrollbar(frm_tree, orient='vertical')
        xsb = Scrollbar(frm_tree, orient='horizontal')
        
        self._table = Treeview(frm_tree,
                               yscrollcommand=ysb.set,
                               xscrollcommand=xsb.set)

        ysb.config(command=self._table.yview)
        xsb.config(command=self._table.xview)
        #self._table.grid(row=0,column=0)
        #ysb.grid(row=0,column=1)
        #xsb.grid(row=1,column=0)

        ysb.pack(side=RIGHT,fill=Y,expand=1)
        xsb.pack(side=BOTTOM,fill=X,expand=1)
        self._table.pack(side=LEFT, fill=BOTH, expand=1)
        

        
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
        # Brightness
        bright_frame = Frame(self._parent)
        br_lab = Label(bright_frame, text= "Brightness")
        self._sc_br = Scale(bright_frame,
                            orient=HORIZONTAL,
                            from_ = 0,
                            to = 255,
                            command=self._brightness_change)
        
        bright_frame.pack(fill=X)
        br_lab.pack(side=LEFT)
        self._sc_br.pack(side=LEFT,fill=X, expand=1)
        self._sc_br.set(128)

        #............................................................
        # Contrast
        contrast_frame = Frame(self._parent)
        ct_lab = Label(contrast_frame, text= "Contrast")
        self._sc_ct = Scale(contrast_frame,
                            orient=HORIZONTAL,
                            from_ = 0,
                            to = 255,
                            command=self._contrast_change)
        
        contrast_frame.pack(fill=X)
        ct_lab.pack(side=LEFT)
        self._sc_ct.pack(side=LEFT,fill=X, expand=1)
        self._sc_ct.set(128)

        #............................................................
        # Threshold
        threshold_frame = Frame(self._parent)
        th_lab = Label(threshold_frame, text= "Threshold")
        self._sc_th = Scale(threshold_frame,
                            orient=HORIZONTAL,
                            from_ = 0,
                            to = 255,
                            command=self._threshold_change)
        
        threshold_frame.pack(fill=X)
        th_lab.pack(side=LEFT)
        self._sc_th.pack(side=LEFT,fill=X, expand=1)
        self._sc_th.set(126)
        
        
        #............................................................
        # The button for the calculations
        clc_frame = Frame(self._parent)
        btn_calc = Button(clc_frame, text= "Track marker", command=self.track)
        clc_frame.pack(fill=X)
        btn_calc.pack(anchor=CENTER)
        
    def _brightness_change(self, value):
        self._image["brightness"] = int(value)
        
        if self._video == None: return
        
        image = self._video.frame()

        marc_gris = brightness_contrast(image,
                                        self._image["brightness"],
                                        self._image["contrast"])
        
        self.do_draw(marc_gris, gray=True)

        
    
    def _contrast_change(self, value):
        self._image["contrast"] = int(value)

        if self._video == None: return
        
        image = self._video.frame()

        marc_gris = brightness_contrast(image,
                                        self._image["brightness"],
                                        self._image["contrast"])
        
        self.do_draw(marc_gris, gray=True)
        
    
    def _threshold_change(self, value):
        self._image["threshold"] = int(value)

        if self._video == None: return
        
        image = self._video.frame()

        marc_gris = brightness_contrast(image,
                                        self._image["brightness"],
                                        self._image["contrast"])
        
        marc_gris = threshold(marc_gris, self._image["threshold"])
        
        
        self.do_draw(marc_gris, gray=True)
        

    def _ruler_change(self, value):
        if self._video == None: return
        
        
        if not(self._onTrack):
            value = int(value)
            img = self._video.goto(value)

            self.do_draw(img, ruler=True)
        #self._axes.clear()
        #self._axes.imshow(img)
        #self._canvas.show()
        
    def load_marker(self):
        options = {"filetypes"   : [("marker files","*.mrk")]}
        
        #filename = asksaveasfilename(**options)
        filename = askopenfilename(**options)
        if filename=="":
            return
        
        
        with open(filename, 'r') as outfile:
            content = outfile.read()
            self._marker = json.loads(content)
            
        self.draw_marker()
            
        
#        cols = ("M1VX", "M1VY", "M1VZ")
#        self._table["columns"] = cols
#        
#        for c in cols:
#            self._table.column(c, width=60, anchor='c')
#            self._table.heading(c, text=c)
#        
#        self._table["show"] = "headings"

        
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

    
    def open_callibration(self):
        options = {"filetypes"   : [("calibration files","*.ccb")],
                   "initialfile" : "camera_calibrated.ccb"}
        #filename = asksaveasfilename(**options)
        filename = askopenfilename(**options)
        if filename=="":
            return
        
        
        callib = {}
        with open(filename, 'r') as outfile:
            content = outfile.read()
            callib = json.loads(content)
            
        for k in callib:
            self._callibration[k] = array(callib[k])
            
        #print self._callibration
        
    def export_csv(self):
        options = {"filetypes"   : [("text files","*.csv")],
                   "initialfile" : "results.csv"}
        filename = asksaveasfilename(**options)
        if filename=="":
            return
        
        self._results.to_csv(filename, sep="\t")
            
    def go_exit(self):
        self._parent.destroy()
        
    def do_draw(self, img, ruler=False, gray=False):
        if not(ruler):
            self._ruler.set(self._video._ind)

        self._axes.clear()
        
        if gray:
            self._axes.imshow(img, cmap=get_cmap("gray"))
        else:
            self._axes.imshow(img)
            
        self._canvas.show()
        self._canvas.flush_events()
        
    def draw_marker(self):
        self._axes2.clear()
        self._axes2.imshow(array(self._marker["marker"])*255)
        self._canvas2.show()
    
    def track(self):        
        self._onTrack=True
        
        ind = (len(self._results.keys())/6)+1
        
        mapping = {"X" : 0, "Y" : 1 , "Z" : 2}
        
        res = dict()
        index = []
        
        # Creating an new variable to hold the analysis
        for k in mapping:
            res["M"+str(ind)+"P"+k] = []
            res["M"+str(ind)+"R"+k] = []
        
        # El angulo rotado
        res["M"+str(ind)+"a"] = []
            
        # The size of the marker
        sizes = (self._marker["size"], self._marker["size"])
        
        
        # Iterating every frame
        for frame in self._video:
            
            # Brightness and contrast analysis
            marc_gris = brightness_contrast(frame,
                                            self._image["brightness"],
                                            self._image["contrast"])
            
            marc_bw = threshold(marc_gris, self._image["threshold"])
            
            try:
            
                cnt, dist_Exo, angle, ret = find_marker_in_image(marc_bw,
                                                             marc_gris,
                                                             frame,
                                                             self._marker["marker"],
                                                             crnr_dist = 50,
                                                             draw_fn=self.do_draw)
            except Exception:
                ret = False
                
            
            try:
                ret, rvecs, tvecs = get_pose(cnt,
                                         self._callibration["matrix"],
                                         self._callibration["distortion"],
                                         angle=0.,#angle,
                                         sizes=sizes)
            except Exception:
                ret = False
            
            if ret:
                index.append(self._video._ind)
                for k in mapping:
                    res["M"+str(ind)+"P"+k].append(float(tvecs[mapping[k]]))
                    res["M"+str(ind)+"R"+k].append(float(rvecs[mapping[k]]))
                    
                res["M"+str(ind)+"a"].append(angle)

            
        these_res = pd.DataFrame(res, index=index)
        self._results = pd.concat([self._results, these_res], axis=1)
        print self._results
            
        self.onTrack=False
            
            
#
#        ret,mtx,dist,rvecs,tvecs = callibration(self._video,
#                                                self._chess["shape"],
#                                                self.do_draw,
#                                                the_size=self._chess["size"])
#        self._onTrack=False
#        
#        self._callibration["matrix"] = mtx.tolist()
#        self._callibration["distortion"] = dist.tolist()
#        
#        
#        if ret:
#            tkMessageBox.showinfo("Result", "Callibration sucessful")
#        else:
#            tkMessageBox.showinfo("Result", "Callibration unsucessful")
            
        


def main():
    root = Tk()
    #root.geometry("500x400+300+300")
    app = WndCal(root)
    root.mainloop()
    
    
if __name__ == '__main__':
    main()
