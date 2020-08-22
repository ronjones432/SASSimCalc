# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 08:30:34 2020

@author: rljones
"""

import numpy as np
import math
from sasmodels import data
from sasmodels.core import load_model
from sasmodels.direct_model import DirectModel
from sasmodels.direct_model import call_kernel
from sasmodels.data import Data2D
from resolution import *

class Instrument():
    """
    An object composed of component objects where a component is a physical beam control device
    in a scattering beamline. Currently, the parameters of each component are user defined, however
    the number and types of objects are generally hard coded. Expanding to a user defined set of components
    will require some more flexible forms of the calculations, which inherently assume a set of
    components.
    
    The object has methods to calculate instrumental resolution and simulate the intensity as a function
    of q in 2-D and 1-D. The q-dependent scattering is calculated in 2-D, the 1-D data is derived from an 
    average from the 2-D calculation.
    """
    def __init__(self, src, velsel, atten, guides, srcap, samap, sam, bs, det):
        
        self.src = src
        self.velsel = velsel
        self.atten = atten
        self.guides = guides
        self.srcap = srcap
        self.samap = samap
        self.sam = sam
        self.bs = bs
        self.det = det
        
        #set self.bsloc
        self.BStoAnode()
        
        #create pixel based detector axes and flattened real space coord arrays
        self.calc_qxqy()
        
        #calculate resolution functin of the instrument
        self.det.sig2_d = var_pix(self.det.dpix) 
        self.det.sig2_w = var_wave(self.velsel.spread)
        wavelen = self.velsel.wavelen
        samaploc = self.samap.loc
        srcaploc = selr.srcap.loc
        detloc = self.det.loc
        _,sig2_wy = sig2_w
        self.det.sig2_g = var_grav(wavelen, samaploc, srcaploc, sig2_wy)
        self.det.sig2_c = var_coll(samaploc, srcaploc, detloc)


    def BStoAnode(self):
        """Calculate distance from beamstop to detector anode plane"""
        # In IGOR, empirical formula based on radius Dist=20.1 + 1.61*Radius, in cm.
        # But the radius is not the actual parameter. Rather, beamstop number is the
        # parameter, and BS radius scales with bs number on 30m instruments (num 1 = 1" diam, etc). 
        # Here, we are fixing that issue and implementing the functionality on
        # BS number, which will allow us to use the 10m SANS 1.5" beamstop (BS num = 4)
        #  
        # To get there, Dist = 20.1 + 1.61*radius = 20.1 + 1.61*(bsnum*2.54)/2
        self.bsloc = self.det.loc - (self.bs.A + self.bs.B*self.bs.num)
    
    def calc_qxqy(self):
        """Create flattened arrays of q from nominal r values"""
        detloc = self.det.loc
        wavelen = self.velsel.wavelen
        samloc = self.sam.loc
        
        sdd = detloc - samloc
        kmag = 4*math.pi/wavelen
        qx_1d = kmag * np.arctan(self.det.ax_x/sdd)
        qy_1d = kmag * np.arctan(self.det.ax_y/sdd)
        Qx, Qy = np.meshgrid(qx_1d, qy_1d)
        self.Qx, self.Qy = Qx.flatten(), Qy.flatten()
        self.Qnom = np.sqrt(Qx**2 + Qy**2)
    
