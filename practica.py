# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 11:54:47 2017

@author: juanma
"""

import cv2
from numpy import *
from matplotlib.pyplot import *
from video_proc import *
#%%            
marc = cv2.imread("./samples/measurement/mes0001.png")
imshow(marc)


#%% Brillo y contraste
marc2 = marc.copy() # Copiamos la imagen para no machacar la original
contraste = 1.
brillo = 163
marc2 = uint8(clip(marc2*contraste + brillo, 0, 255))
imshow(marc2)

#%% Convertimos a escala de grises
marc_gris = cv2.cvtColor(marc2, cv2.COLOR_BGR2GRAY)
imshow(marc_gris, cmap=get_cmap("gray"))

#%% Binarizamos la imagen
th, marc_bw = cv2.threshold(marc_gris, 213, 255, cv2.THRESH_BINARY)
imshow(marc_bw, "gray")


#%% Busamos el marcador
patrones = {"marcador1":
            [[1,1,1,0,0],
             [1,0,0,1,0],
             [1,1,1,0,0],
             [1,0,0,1,0],
             [1,0,0,0,1]],
            "marcador2": 
            [[1,0,0,0,0],
             [1,0,0,0,0],
             [1,0,0,0,0],
             [1,0,0,0,0],
             [1,1,1,0,0]]}
            

cnt, dist_Exo, angle, ret = find_marker_in_image(marc_bw,
                                                 marc_gris,
                                                 patrones["marcador1"],
                                                 crnr_dist = 50)

print ret, dist_Exo, angle

#%% Dibujamos el hallazgo
cv2.drawContours(marc, cnt, -1, (0,255,0), 5)
imshow(marc)
show()

#%% Cogemos la calibración del espacion
ret, mtx, dist, rvecs, tvecs = callibration("./samples/VID_20170313_103754.mp4"
                                            ,(7,4),
                                            draw=True)

#%% Leemos la calibracion
import json
callib = {}
with open("./camera_calibrated.ccb", 'r') as outfile:
    content = outfile.read()
    callib = json.loads(content)
    
for k in callib:
    callib[k] = array(callib[k])



#%% Calculamos la posición y la orientación
ret, rvecs, tvecs = get_pose(cnt, mtx, dist)

print rvecs
print tvecs
