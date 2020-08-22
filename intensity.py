# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 08:38:22 2020

@author: rljones
"""

import numpy as np

def Intensity2D(Qx):
    """
    """

    Iq = 100 * np.ones_like(Qx)
    dIq = np.sqrt(Iq)
    return Iq, dIq
