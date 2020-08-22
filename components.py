# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 08:44:22 2020

@author: rljones
"""
import numpy as np
from sasmodels.core import load_model


class Source(object):
    """
    Defines the beam flux at the start of the instrument.
    Parameters:
    
    *loc*: arbitrary, but be consistent with the other loc values

    *flux*: neutrons/sec just prior to the first instrument component
    """
    def __init__(self, loc, flux):
        self.loc = loc
        self.flux = flux

class VelocitySelector(object):
    """Define parameters of a velocity selector
    
    *loc*: a number specifying the location of the selector (in cm)
    
    *wavelen*: wavelength of the beam (in Angstroms)
    
    *spread*: FWHM of wavelength distribution (delta wavelength/wavelength) 
    """
    def __init__(self, loc, wavelen, spread):
        self.loc = loc
        self.wavelen = wavelen
        self.spread = spread
        
        
    def calc_wavelen(self, velocity, A, B):
        """
        Return the wavelength and spread from selector parameters
        
        Parameters:
        *velocity*: velocity (in rpm) of the selector
        
        *A, B*: Selector constants
        """
        self.velsel_A = A
        self.velsel_B = B
        
        self.wavelen = (1/velocity)*self.velsel_B + self.velsel_A
            

class Attenuator(object):
    """Define parameters of the attenuator"""
    def __init__(self, loc, number, factor):

        self.loc = loc
        self.number = number
        self.factor = factor


class Aperture(object):
    """
    Define an aperture component by its dimensions and shape
    
    Parameters:
    *loc*: location along beampath
    *shape*: string, either circle or rectangle
    *dims*: dimensions of (width, height) or (diam, diam)
    """
    def __init__(self, loc, shape, dims):    
        self.loc = loc
        self.shape = shape

        self.pf_list = {'circle': 4, 'rectangle': 12}
        self.calc_moment(dims)
        
    def calc_moment(self, dims):
        """Calculate the moment of the aperture shape"""
        self.dims = dims        
        dim1, dim2 = self.dims
        if self.shape in self.pf_list: 
            pf = self.pf_list[self.shape]
            self.moment = (1/pf*((dim1/2)**2), 1/pf*((dim2/2)**2))
        else: 
            self.moment = None
            print(f'Invalid Shape = {self.shape}')
        

class Guide(object):
    """Create a guide component object that modifies intensity"""
    def __init__(self, loc, number, dims, parms):
        self.loc = loc
        self.num = number
        self.dims = dims
        self.parms = parms


class Sample(object):
    """Create a 2D sasmodels kernal representing the sample"""
    def __init__(self, loc, label, dims, model):
        self.loc = loc
        self.label = label
        self.dims = dims
        self.load_sasmodel(model)
        
    def load_sasmodel(self, model):
        self.model = model
        try:
            self.kernel = load_model(model)
        except ValueError:
            print(f'Invalid model specification: {self.model}')


class BeamStop(object):
    """Create an object that describes the beamstop shape and location"""
    def __init__(self, loc, coords, bsnum, bsdims, A, B):
        """
        Parameters:
        *loc*: location along the beam path
        
        *coords*: location of beamstop in plane parallel to detector (x, y)
            
        *bsnum*: number of the beamstop
    
        *bsdims*: dimensions of beamstop (width, height) or (diam, diam)

        *A, B*: Distance to detector = A + B*bsnum    
        """
        self.loc = loc
        self.coords = coords
        self.num = bsnum
        self.bsdims = bsdims
        self.A = A
        self.B = B        
        
class Detector(object):
    """Create a 2-D detector array"""
    def __init__(self, loc, dpix, npix, beam_cntr):
        """
        Parameters:
        *loc*: location of detector on beamline coordinates
        
        *dpix*: tuple of pixel (width, height)
    
        *npix*: number of pixels along each axis (horiz, vert)
    
        *beam_cntr*: center of beam in pixel coords (horiz, vert)
        """    
        self.loc = loc
        self.dpix = dpix
        self.npix = npix
        self.bm_cntr = beam_cntr
        self.axes()
        self.r_nominal()
                    
    def axes(self):
        """Create 1-D arrays (x, y) with real space distances from beam center"""
        ## Fill 1-D numpy arrays with real space distances (in cm) from the beam center
        ## and nominal q magnitudes (limit of perfect resolutions) for each detector row (column).
        ## Pixels start from (1,1) and ending at (pix_x,pix_y).
        ## These will represent the pixel coordinates along each axis.
        
        dpix_x, dpix_y = self.dpix
        npix_x, npix_y = self.npix
        cen_x, cen_y = self.bm_cntr

        self.ax_x = dpix_x*(np.arange(1,npix_x+1,1)-cen_x)
        self.ax_y = dpix_y*(np.arange(1,npix_y+1,1)-cen_y)
        
    def r_nominal(self):
        """Create flattened arrays of distances to each pixel"""
        Rx, Ry = np.meshgrid(self.ax_x, self.ax_y)
        self.Rx, self.Ry = Rx.flatten(), Ry.flatten()
        self.Rnom = np.sqrt(Rx**2 + Ry**2)
    

