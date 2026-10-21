"""Dump a fine zoom's land/sea (and lakes) as a PNG, optionally a crop: coast_view.py <id> <out.png> [r0 c0 size]."""
import sys

import numpy as np
from planet.images import write_png

from planet import zoom as Z

meta, lay = Z.load(sys.argv[1])
n = meta["nx"]
w = np.asarray(lay["water"]).reshape(n, n)
e = np.asarray(Z.load(sys.argv[1], decode=True)[1]["elevation"]).reshape(n, n)
img = np.zeros((n, n, 3), np.uint8)
land = np.clip(80 + e / 4, 80, 255)
img[..., 0] = np.where(w == 0, land * 0.8, 20)
img[..., 1] = np.where(w == 0, land, np.where(w == 2, 120, 60))
img[..., 2] = np.where(w == 0, land * 0.5, np.where(w == 1, 150, 200))
if len(sys.argv) > 3:
    r0, c0, s = map(int, sys.argv[3:6])
    img = img[r0:r0 + s, c0:c0 + s]
f = max(1, 800 // img.shape[0])
img = np.repeat(np.repeat(img, f, 0), f, 1)
write_png(sys.argv[2], img)
print(np.bincount(w.ravel(), minlength=3), e.min(), e.max())
