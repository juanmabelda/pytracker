# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 08:35:21 2017

@author: juanma
"""

from numpy import *
import glob
import cv2

#% ffmpeg -i calibracion.mp4 ./callibration/cal%00d.png

class videofile():
    '''Allows interaction with an OpenCV VideoCapture object in a more
    pythonic way'''
    def __init__(self, filename):
        #self.video = cv2.VideoCapture(filename)
        self.video = glob.glob(filename+"/*.png")
        self.video.sort()
        
        # Current frame
        self._ind = 0
        
        # Range of analysis
        self._from = 0
        self._to = len(self.video)-1
        
        
    def __iter__(self):
        return self
        
    def __next__(self):
        if self._ind >= self._to:
            raise StopIteration
        
        
        try:
            frame = cv2.imread(self.video[self._ind])
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            raise StopIteration
            
        self._ind += 1
        return frame
#        try:
#            ret, img = self.video.read()
#        except:
#            raise StopIteration
#            
#        if ret == False:
#            raise StopIteration
#            
#        return img

    def range_def(self, from_f , to_f):
        '''Defines a range for analysis'''
        self._from = from_f
        self._to = to_f
        
        if self._ind < self._from:
            self._ind = self._from
            
    def mark_start(self, from_f):
        if (from_f >= 0) & (from_f < self._to):
            self._from = from_f
            
    def mark_end(self, to_f):
        if (to_f < len(self)) & (to_f > self._from):
            self._to = to_f
    
    def goto_start(self):
        self.goto(self._from)
        return self.frame()
    
    def goto_end(self):
        self.goto(self._to)
        return self.frame()
        
    def goto_prev(self):
        if self._ind > self._from:
            self._ind -= 1
            
        return self.frame()
    
    def goto_next(self):
        if self._ind < (self._to-1):
            self._ind += 1
            
        return self.frame()
        
    def frame(self):
        frame = cv2.imread(self.video[self._ind])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame
        
    def goto(self, frame_number):
        '''Move to a specified frame'''
        
        self._ind = frame_number
        return self.frame()
        
#        if frame_number < 0:
#            raise IndexError
#        elif frame_number > len(self):
#            raise IndexError
#            
#        self.video.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame_number)
        
        
    def __len__(self):
        return len(self.video)
#        self_len = self.video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
#        return int(self_len)