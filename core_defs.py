# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 08:44:22 2020

@author: rljones
"""
import numpy as np
from matplotlib import pyplot as plt
import math
from scipy import special as sp
from sasmodels import data
from sasmodels.core import load_model
from sasmodels.direct_model import DirectModel
from sasmodels.direct_model import call_kernel
from sasmodels.data import Data2D

class Source(object):
    """
    Object defines the beam flux at the start of the instrument.
    The location is required in the form of the parameter loc, but
    the value is arbitrary and not used at this time other. It is
    anticipated that eventually the code will make a graphical 
    representation of the instrument, and it will be useful there.
    
    *loc* - arbitrary number, but be consistent with the other loc values
    
    *flux* - neutrons/sec just prior to the first instrument component
    """
    def __init__(self, loc, flux):
        
        self.loc = loc
        self.flux = flux

class VelocitySelector(object):
    """
    Object defines parameters of a velocity selector, namely the wavelength
    and FWHM spread of the wavelength distribution. A method is included
    to convert, if desired, from velocity selector rotation speed and two
    selector constants. This method allows one to iterate velocity (which
    can be checked for physical limits) rather than wavelength.                                                                
    
    *loc*: a number specifying the location of the selector (in cm)
    *wavelen*: wavelength of the beam (in Angstroms)
    *spread*: FWHM of wavelength distribution (delta wavelength/wavelength) 
    """
    def __init__(self, loc, wavelen, spread):
        
        
        self.loc = loc #cm
        if mode == 'wavelength':
            self.wavelen = parm1
            self.spread = parm2
        elif mode == 'velocity':
            self.vel, self.tilt = self.set_velocity(parm1, parm2) # in rpm
        else:
            print('Note: mode can only be "wavelength" or "velocity"')
        
    def set_velocity(self, velocity, A, B):
        ## TODO: Add limits to velocity.
        ## velocity is the speed of the velocity selector in rpm
        ## A and B are selector constants that incorporate the tilt effects

        self.velsel_A = A
        self.velsel_B = B
        
        self.wavelen, self.spread = (1/velocity)*self.velsel_B + self.velsel_A
        return self.wavelen, self.spread
            

class Attenuator(object):
    """
    """
    def __init__(self, loc, number, factor):

        self.loc = loc
        self.number = number
        self.factor = factor


class Aperture(object):
    """
    """
    def __init__(self, loc, shape, dims):
    
        self.loc = loc
        self.shape = shape
        self.dims = dims
        self.pf_list = {'circle': 4, 'rectangle': 12}
        self.calc_moment()
        
    def calc_moment(self):
        ## Calculate the moment of the aperture shape
        dim1, dim2 = self.dims
        if self.shape in self.pf_list: 
            pf = self.pf_list[self.shape]
        else: 
            print(f'Shape = {self.shape}')
        self.moment = (1/pf*((dim1/2)**2), 1/pf*((dim2/2)**2))
        

class Guide(object):
    """
    """
    def __init__(self, loc, number, dims, parms):

        self.loc = loc
        self.num = number
        self.dims = dims
        self.parms = parms


class Sample(object):
    """
    A class that defines the sample dimensions and form. Form is defined ultimately by
    a model from the SASModels package (https://github.com/SasView/sasmodels). The model
    is used to generate the spatial dependence of scattering for calculation in the 
    detector class.
    """
    def __init__(self, loc, label, dims, model):
        self.loc = loc
        self.label = label
        self.dims = dims
        self.model = model
        
    def load_sasmodel(self, model):
        self.kernel = load_model(model)


class BeamStop(object):
    """
    """
    def __init__(self, loc, )
class Detector(object):
    """
    A detector object used to create a 2-D detector image and a 1-D averaged version of the data
    
    *samdd* = sample to detector distance in cm
    
    *sapdd* = sample aperture to detector distance in cm
    
    *pix*: tuple of pixel widths in cm (width, height)
    
    *npix*: tuple of number of pixels along each axis (width, height)
    
    *bm_cntr*: tuple of pixel coordinates for center of beam (horizontal, vertical)
    
    *bs_num*: number of the beamstop (used to calculate the distance from the anode plane)
    
    *bs_dia*: diameter, in cm, of the beamstop
    
    *bs_loc*: coordinates of the beamstop.
    """    
    def __init__(self, loc, dpix, npix, beam_cntr, beamstop):
        self.loc = loc
        self.dpix = dpix
        self.npix = npix
        self.bm_cntr = beam_cntr
        self.axes()
        
        if beamstop is not None:
            self.bs = beamstop['number']
            self.bs_diam = beamstop['dims']
            self.bsloc = beamstop['loc']
            self.BStoAnode()
            print('Beamstop!')

                    
    def axes(self):
        ## Fill 1-D numpy arrays with real space distances (in cm) from the beam center
        ## and nominal q magnitudes (limit of perfect resolutions) for each detector row (column).
        ## Pixels start from (1,1) and ending at (pix_x,pix_y).
        ## These will represent the pixel coordinates along each axis.
        
        dpix_x, dpix_y = self.dpix
        npix_x, npix_y = self.npix
        cen_x, cen_y = self.bm_cntr

        self.ax_x = dpix_x*(np.arange(1,npix_x+1,1)-cen_x)
        self.ax_y = dpix_y*(np.arange(1,npix_y+1,1)-cen_y)
    
    def BStoAnode(self):
        # In IGOR, empirical formula based on radius Dist=20.1 + 1.61*Radius, in cm.
        # But the radius is not the actual parameter. Rather, beamstop number is the
        # parameter, and BS radius scales with bs number on 30m instruments (num 1 = 1" diam, etc). 
        # Here, we are fixing that issue and implementing the functionality on
        # BS number, which will allow us to use the 10m SANS 1.5" beamstop (BS num = 4)
        #  
        # To get there, Dist = 20.1 + 1.61*radius = 20.1 + 1.61*(bsnum*2.54)/2
        self.bsloc = self.loc - (20.1 + 2.0477*self.bs)
