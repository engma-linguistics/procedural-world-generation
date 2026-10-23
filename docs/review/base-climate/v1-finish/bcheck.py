import sys, time, hashlib, numpy as np
from planet.grid import build_grid
from planet.tectonics import mantle
for L in map(int, sys.argv[1:]):
    g = build_grid(L); t=time.time()
    Y, d = mantle._build_basis(g); t=time.time()-t
    G = Y.T @ Y
    # analytic check: deviation of raw harmonics from GS'd ones
    print(L, g.n, f"{t:.2f}s", hashlib.md5(Y.tobytes()).hexdigest()[:12], "orth err", np.abs(G-np.eye(len(d))).max(), "mean", np.abs(Y.sum(0)).max())
