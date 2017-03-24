#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 15:19:29 2017

@author: juanma
"""

import cv2
from numpy import *
from matplotlib.pyplot import *
from video_proc import *
from scipy.linalg import norm


#%% Creamos matrices de distorsion y de transformacion

mtx = eye(3)
dist = zeros([1,5])


#%%
# arrange points for cv2
def _arrange_points(points):
    '''Arrange an array of points to the way OpenCV likes'''
    
    tam = list(shape(points))
    
    tam.append(1)
    
    output_matrix = zeros(tam)
    
    for o, p in enumerate(points):
        col = reshape(p, [tam[1], 1])
        output_matrix[o,:,:] = col
        
    return output_matrix



#%% El objeto en 3D

objp = array([[-0.5, -0.5, 0.],
              [ 0.5, -0.5, 0.],
              [ 0.5,  0.5, 0.],
              [-0.5,  0.5, 0.]])

plot(objp[:,0,0], objp[:,1,0])    
objp = _arrange_points(objp)
print objp


#%% La imagen 2D del objeto
cntr = array([[-0.5, -0.5],
              [ 0.5, -0.5],
              [ 0.5,  0.5],
              [-0.5,  0.5]])
    
cntr = _arrange_points(cntr)
print cntr

#%% Calculamos la posicion del objeto 3D
ret, rvecs, tvecs = cv2.solvePnP(objp, cntr, mtx, dist)

print (180./pi)*norm(rvecs), "\n", rvecs

#%% La imagen del objeto 3D girada 90º
cntr = array([[ 0.5, -0.5],
              [ 0.5,  0.5],
              [-0.5,  0.5],
              [-0.5, -0.5]])
    
#cntr += 2
    
cntr = _arrange_points(cntr)
print cntr

#%% La imagen del objeto 3D girada 90º
cntr = array([[ 0.5,  0.5],
              [-0.5,  0.5],
              [-0.5, -0.5],
              [ 0.5, -0.5]])
    
#cntr += 2
    
cntr = _arrange_points(cntr)
print cntr

