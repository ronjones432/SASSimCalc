# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 11:45:13 2020

@author: rljones
"""

from components import Source, VelocitySelector, Attenuator
from components import Aperture, Guide, Sample, BeamStop, Detector
from instrument import Instrument

def build_10m():
    src = Source(loc=-800, flux=100000)
    velsel = VelocitySelector(loc=-600, wavelen=5, spread=0.14)
    atten = Attenuator(loc=-510, number=0, factor=0)
    srcap = Aperture(loc=-500, shape='circle', dims=[2.54, 2.54])
    samap = Aperture(loc=0, shape='circle', dims=[0.635, 0.635])
    guides = Guide(loc=-500, number=0, dims=[5,5], parms=[2,2])
    sam = Sample(loc=5, label='Cylinders in d2O', dims=[2.54, 2.54, 0.254], model='cylinder')
    bs = BeamStop(loc=495, coords=[0.2, 5.3], bsnum=2, bsdims=[5.08, 5.08], A=20.1, B=2.0477)
    det = Detector(loc=500, dpix=[0.508, 0.508], npix=[128,128], beam_cntr=[64.1, 65.2])
    
    sans = Instrument(src, velsel, atten, srcap, samap, guides, sam, bs, det)
    
    return sans