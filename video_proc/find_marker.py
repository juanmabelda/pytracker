# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 09:31:04 2017

@author: juanma
"""

import cv2
from numpy import *
from matplotlib.pyplot import *
from scipy.linalg import norm


# La distancia de hamming
def _hamming_distance(a, b):
    '''Helper function para calcular la distancia de hamming'''
    a = array(a)
    b = array(b)
    return len(a[a!=b])


def brightness_contrast(img, brightness, contrast):
    '''Changes brightness and contrast of the image'''

    brillo = brightness - 128
    #contraste = contrast/255.
    contraste = 259.*(contrast + 255.)/(255. * (259. - contrast))
        
    marc2 = img.copy()
        
    marc2 = uint8(clip(marc2*contraste + brillo, 0, 255))
    marc_gris = cv2.cvtColor(marc2, cv2.COLOR_BGR2GRAY)
    
    return marc_gris

def threshold(img, threshold):
    '''Thresholds an image'''
    
    th, marc_bw = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    
    return marc_bw

            
#
def find_marker_in_image(img, marc_gris, frame, marker, thr_len=50, crnr_dist=50, draw_fn=None):
    '''Finds an AR marker defined by marker in a binary image'''

    # Tamaño del patrone
    marker_size = shape(marker)
    # The size of the matriz for averaging
    mt_size = tuple((m+2)*25 for m in marker_size)
    
    #draw_fn(img, gray="True")

    # Búsqueda de contornos
    bw_c, cont, _ = cv2.findContours(img,
                                  cv2.RETR_TREE,
                                  cv2.CHAIN_APPROX_SIMPLE)
    
    #imshow(marc_gris,cmap=get_cmap("gray")); show()    
    
    # Los contornos que pueden ser marcadores
    cntrn = []
    for cnt in cont:
        if cv2.arcLength(cnt, True) > thr_len:
            cntrn.append(cnt)
        cntrn.append(cnt)
            
    # Buscamos los contornos de cuatro puntos porque los marcadores son cuadrados
    cnt4p = []
    for cnt in cntrn:
        epsilon = 0.1*cv2.arcLength(cnt,True)
        crv = cv2.approxPolyDP(cnt, epsilon,True)
    
        # Si no tienen cuatro puntos, pasamos de ellos    
        if len(crv) != 4: continue
    
        # Si no son convexos lo descarvamos
        if not(cv2.isContourConvex(crv)): continue
    
          
        # Si dos esquinas consecutivas están muy cerca, pasamos de ellas
        lcrv = [[float(x[0][0]), float(x[0][1])] for x in crv]
        min_dist = 1e6
    
        for x, y in zip(lcrv, lcrv[1:]+lcrv[:1]):
            dist = sqrt( (x[0]-y[0])**2 +  (x[1]-y[1])**2)
            if dist < min_dist: min_dist = dist
        #for x, y in zip(lcrv, lcrv[1:]+lcrv[:1]):
               
        #print min_dist            
        if min_dist < crnr_dist: continue
                
        cnt4p.append(cnt)
    #for cnt in cntrn:
    
        
    
    # Buscamos el patron en los contornos
    for cnt in cnt4p:
        #print shape(cnt)
            
        # Cojemos el ajuste poligonal
        epsilon = 0.1*cv2.arcLength(cnt,True)
        crv = cv2.approxPolyDP(cnt, epsilon, True)
        lcrv = [[float32(x[0][0]), float32(x[0][1])] for x in crv]
        acrv = array(lcrv)
        
        # El destino
#        dst = array([[0         , 0],
#                     [0         , mt_size[1]],
#                     [mt_size[0], mt_size[1]],
#                     [mt_size[0], 0        ]],
#                     float32)
        dst = array([[0         , 0],
                     [mt_size[0], 0        ],
                     [mt_size[0], mt_size[1]],
                     [0         , mt_size[1]]],
                     float32)

            
        #print acrv, dst
            
        # Obtenemos la transformación
        trf = cv2.getPerspectiveTransform(acrv, dst)
    
        
         # Transformamos la imagen
        mrk = cv2.warpPerspective(marc_gris,trf,mt_size)
        #mrk = cv2.warpPerspective(img,trf,mt_size)
            
        _, bin_mrk = cv2.threshold(mrk, 125, 255,
                                   cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        #print bin_mrk
            
        #cv2.imshow("pers",bin_mrk); cv2.waitKey(1500)
        #bin_mrk = mrk.copy()
        #imshow(bin_mrk, cmap=get_cmap("gray")); show()
        
            
        # Vectores para la binarizacion
        marc = zeros([marker_size[0]+2,marker_size[1]+2])
        for r in range(marker_size[0]+2):
            for c in range(marker_size[1]+2):
                celda = bin_mrk[ r*25:(r+1)*25,c*25:(c+1)*25]
                nivel = count_nonzero(celda)
                if nivel > 312:
                     marc[r,c] = 1
                    
        # Distancias de hamming del marcador encontrado a los patrones
        dist_Exo = marker_size[0]*marker_size[1]
            
        # Calculamos la distancia al patrón
        # print m["name"]
        the_marc = marc[1:marker_size[0]+1,1:marker_size[0]+1]
        the_marc = array(the_marc, dtype=int)
        #print "="*12
        for c in range(4):
            dist_e = _hamming_distance(the_marc, marker)
            if dist_e < dist_Exo:
                dist_Exo = dist_e
                angle = -c*pi/2
                the_cnt = cnt
                                
            the_marc = rot90(the_marc)
            
            #print "."*12
            #print the_marc
            
        if dist_Exo == 0:
            if draw_fn != None:
                cv2.drawContours(frame, cnt, -1, (0,255,0), 5)
                cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                draw_fn(frame)
            return cnt, dist_Exo, angle, True
    
    
    return the_cnt, dist_Exo, angle, False

def get_pose(cont, mtx, dist, angle = 0., sizes=(1.,1.)):
    '''Returns the position and the orientation of the AR marker
       =========================================================
       
       Parameters
       ----------
       
       * cont : Contour of the marker
       * mtx  : Transformation matrix
       * dist : Distortion coefficients
       * sizes: Size (in metric units) heigth of rows x width of columns
    '''
    
    # Formula de Rodrigues
    # T1 [+] T2 = (T1 + T2 - cross(T1, T2))/(1 - dot(T1,T2))
    
    # Vector de Rodrigues de la orientacion del marcador
    rodr = array([0., 0., tan(angle/2.)])
    
    
    # Buscamos las esquinas
    epsilon = 0.1*cv2.arcLength(cont,True)                                                 
    crv = cv2.approxPolyDP(cont, epsilon,True)
    lcrv = [[float32(x[0][0]), float32(x[0][1])] for x in crv]
    acrv = array(lcrv)    
    
#    corners = zeros([4,2,1])
#    for c in range(4):
#        corners[c,:,:] = reshape(acrv[c,:],[2,1])
    corners = _arrange_points(acrv)
        
#    objp = zeros([4,3,1])
#    objp[0] = array([[0.],[0.],[0.]])
#    objp[1] = array([[0.],[1.],[0.]])
#    objp[2] = array([[1.],[1.],[0.]])
#    objp[3] = array([[1.],[0.],[0.]])

    hs0 = float(sizes[0])/2.
    hs1 = float(sizes[1])/2.
        
#    objp = _arrange_points(array([[0.      , 0.      , 0.],
#                                  [0.      , sizes[1], 0.],
#                                  [sizes[0], sizes[1], 0.],
#                                  [sizes[0], 0.      , 0.]]))

    objp = _arrange_points(array([[-hs0    , -hs1    , 0.],
                                  [-hs0    ,  hs1    , 0.],
                                  [ hs0    ,  hs1    , 0.],
                                  [ hs0    , -hs1    , 0.]]))

        
    ret, rvecs, tvecs = cv2.solvePnP(objp, corners, mtx, dist)
    
    
    rvecs = vang2rodr(rvecs.reshape(3))
    #rvec_tr = (rodr + rvecs - cross(rodr, rvecs))/(1 - dot(rodr, rvecs))
    rvec_tr = rodrigues(rodr, rvecs)
    #tvec_tr = tvecs
    #print tvecs
    
    return ret, rvec_tr, tvecs

# La composicion de movimientos segun Rodriges
def rodrigues(Omega1, Omega2):
    '''Composition of rotations using Rodrigues vectors'''
    res = (Omega1 + Omega2 - cross(Omega1, Omega2))/(1 - dot(Omega1, Omega2))
    
    return res

# Rotacion de un vector respecto de un vector de Rodrigues
def rodr_rot(Omega, v):
    '''Rotation of a vector through a Rodrigues vector'''
    
    vt = v + (2/(1 + dot(Omega, Omega))) * \
         (cross(Omega, v) + cross(Omega, cross(Omega, v)))
    
    return vt


def vang2rodr(vang):
    '''Transforms an angle vector array to a rodrigues vector array'''
    
    if len(shape(vang))==1:
        ang = norm(vang)
        unit  = array(vang)/ang
        rodr = tan(ang/2)*unit
    else:    
        # The norm of the vector is the turning angle
        ang = norm(vang, axis=1)      
        # The direction of rotation (unitary vector)
        unit = array( [v/a for v, a in zip(vang,ang)])        
        # Rodrigues vector
        rodr = array([u*tan(a/2) for u, a in zip(unit, ang)])   
    
    return rodr
    
    
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
