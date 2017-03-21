# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 15:00:37 2017

@author: juanma
"""

from numpy import *
from matplotlib.pyplot import *
import cv2
from videofile_mgn import videofile

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

def callibration(video, chessboard, draw_func=None, the_size = 0.03):
    '''Perform a callibration on a chessboard of given dimensions'''

    tablero = tuple(chessboard)
    
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = zeros((tablero[1]*tablero[0],3), float32)
    objp[:,:2] = mgrid[0:tablero[0],0:tablero[1]].T.reshape(-1,2)*the_size
    
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    
    #images = videofile(filename)    
    
    for img in  video:
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, tablero,None)
    
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
    
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            if type(corners2) == type(None):
                corners2 = corners
            
            imgpoints.append(corners2)
    
            # Draw and display the corners
            if draw_func != None:
                cv2.drawChessboardCorners(img, tablero, corners2,ret)
                draw_func(img)
                #cv2.imshow('img',img)
                #cv2.waitKey(50)
                
        print video._ind, ret
            
    
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints,
                                                       imgpoints,
                                                       gray.shape[::-1],
                                                       None,
                                                       None)
    
    return ret, mtx, dist, rvecs, tvecs

#
import sys    
def main(argv=None):
    if len(sys.argv)==2:
        cal = callibration(sys.argv[1], (8,6), draw=True)
    elif len(sys.argv)==3:
        hor, vert = sys.argv[2].split("x")
        tam = (int(hor), int(vert))
        cal = callibration(sys.argv[1], tam, draw=True)
    else:
        return
        
    print cal
    
if __name__=="__main__":    
    sys.exit(main(sys.argv))