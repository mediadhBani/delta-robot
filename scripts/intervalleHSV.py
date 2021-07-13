# -*- coding: utf-8 -*-
"""
@brief Programme pour déterminer la couleur moyenne et l'écart-type d'une image.
"""

import numpy as np
import re
import sys

if len(sys.argv) == 1:
    print("intervalleHSV.py fichier_histogramme\nRenvoie la couleur moyenne et",
          "l'écart-type d'une image.")
    exit(1)

def isfloat(x):
    return x.replace('.', '', 1).isdigit()


pattern = re.compile('\d+(?:\.\d+)?(?:\s+[+-]?\d+(?:\.\d+)?){0,2}')
hist, w = [], []

with open(sys.argv[1], 'r') as fichier:
    for line in fichier:
        occ, hue, sat, val, *_ = re.findall(pattern, line)
        hist.append([hue, sat, val])
        w.append(occ)
    
    hist.pop(0)
    w.pop(0)

    hist, w = np.array(hist, dtype=float), np.array(w, dtype=float)
    avg = np.average(hist, weights=w, axis=0)
    std = np.sqrt(np.average((hist-avg)**2, weights=w, axis=0))

    inf = (avg - std) * [.5, 2.55, 2.55]
    sup = (avg + std) * [.5, 2.55, 2.55]


print(sys.argv[1], f"{avg}\n {inf}, {sup}")