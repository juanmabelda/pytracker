# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 08:35:21 2017

@author: juanma
"""

from numpy import *
import cv2

class videofile():
    '''Allows interaction with an OpenCV VideoCapture object in a more
    pythonic way'''
    def __init__(self, filename):
        self.video = cv2.VideoCapture(filename)
        
    def __iter__(self):
        return self
        
    def next(self):
        try:
            ret, img = self.video.read()
        except:
            raise StopIteration
            
        if ret == False:
            raise StopIteration
            
        return img
        
    def goto(self, frame_number):
        '''Move to a specified frame'''
        
        if frame_number < 0:
            raise IndexError
        elif frame_number > len(self):
            raise IndexError
            
        self.video.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, frame_number)
        
        
    def __len__(self):
        self_len = self.video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        return int(self_len)