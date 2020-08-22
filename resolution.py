# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 08:33:20 2020

@author: rljones

Note: We should somehow cache or more smartly calculate resolution.
For example, if varying wavelength, do not need to keep recalculating
variance in collimation.
"""

import numpy as np
import math
from scipy import special as sp

def calc_Resolution2D(object):
    """Calculate the 2-D resolution function"""
        


def shadow(detloc, bsloc, samaploc, bs_diam, sig2_d, Rnom):
    """
    Calculate the distortion of the beam due to the beamstop.
    
    This distortion is represented by a "shadow factor"
    that serves to correct the probability distribution of <q>.
    All dimensions are in cm, sig2_d is in cm^2
    
    *detloc*: beamline coordinate of the detector component
    *bsloc*: beamline coordinate of the beamstop
    *samaploc*: beamline coordinate of the sample aperture
    *bs_diam*: 2-D dimensions of the beamstop [x, y]
    *sig2_d*: 2-D variance due to pixel size [x, y]
    """

    sqrt2 = math.sqrt(2)

    sig2_d = sig2_d
    L_bs = detloc - bsloc
    L_2 = detloc - samaploc    
    r_bs = bs_diam/2.0
    rbs_proj = r_bs + (r_bs*L_bs)/(L_2 - L_bs)
    shadow = 0.5*(1.0 + sp.erf((Rnom - rbs_proj)/(sqrt2*sig2_d)))
    return shadow
        
def var_wave(spread):
    """Return the 2-D variance due to wavelength distribution (spread)"""
    sig2_w = (spread**2)/6
    return [sig2_w, sig2_w]
    
def var_coll(samaploc, srcaploc, detloc):
    """Return the 2-D variance due to collimation""" 
          
    L1 = samaploc - srcaploc
    L2 = detloc - samaploc
    m_x1, m_y1 = self.srcap.moment
    m_x2, m_y2 = self.samap.moment
    sig2_cx = ((m_x1*L2/L1)**2)/4 + ((m_x2 * (L1+L2)/L2)**2)/4
    sig2_cy = ((m_y1*L2/L1)**2)/4 + ((m_y2 * (L1+L2)/L2)**2)/4
    return [sig2_cx, sig2_cy]
        
def var_grav(wavelen, samaploc, srcaploc, sig2_wy):
    """Calculate sig2_g, variance due to gravity.
    
    Parameters:
        *wavelen*: wavelength (Angstroms)
        *samaploc*: location of sample aperture along beampath
        *srcaploc*: location of source aperture along beampath
        *sig2_wy* = y-axis variance due to wavelength (dl/l) which is unitless
    """
    g_grav = 981.0 ##cm/s^2
    h_m = 395600.0 ##cm/s
    L1 = self.samap.loc - self.srcap.loc ##cm
    L2 = self.det.loc - self.samap.loc #cm
    y_g = ((g_grav*wavelen**2)/(2*h_m**2))*L2*(L1+L2)
    sig2_g = 4.0 * y_g**2 * sig2_wy
    return [0, sig2_g]
        
def var_pix(dpix):
    ## Calculate sig2_d, variance due to pixel size. Variance due to pixel
    ## blur is calculated in 
    pix_dx, pix_dy = dpix
    sig2_dx = (pix_dx/(2*math.sqrt(2*math.log(2))))**2
    sig2_dy = (pix_dx/(2*math.sqrt(2*math.log(2))))**2
    return [sig2_dx, sig2_dy]