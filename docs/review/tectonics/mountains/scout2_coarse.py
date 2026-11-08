"""Coarse-world hypsometry, top cells and their crust (PW-1446 scout 188). usage: coarse.py WORLD_ID..."""
import os, sys
import numpy as np

ROOT = '/home/daniel/personal/repos/procedural-world-generation'
sys.path.insert(0, os.getcwd())
from planet import world as W, summit

for wid in sys.argv[1:]:
    w = W.load(f'{ROOT}/worlds/{wid}.json')
    g, L, m = w['grid'], w['layers'], w['meta']
    E = np.asarray(L['elevation'], float)
    ice = np.asarray(L.get('ice', np.zeros(g.n)), float)
    land = E > 0
    free = land & (ice <= 10)
    rock = np.asarray(L['rock']).astype(int)
    print(f'== world {wid} run {m.get("source_run")} t {m.get("t_myr")} Myr; layers: {sorted(L)[:80]}')
    for k in (1000, 2000, 3000, 4000):
        print(f'  ice-free land > {k} m: {100 * (free & (E > k)).sum() / free.sum():.2f}%')
    hi = land & (E > 4000)
    print(f'  rock of land > 4 km: ' + ', '.join(f'{r}:{100*(rock[hi]==r).mean():.0f}%' for r in np.unique(rock[hi])))
    print(f'  craton share of all land: {100*(rock[land]==5).mean():.0f}%')
    smt = summit.summit_m(g, E)
    top = np.argsort(-E)[:8]
    ck = next((k for k in ('crust_thickness', 'crust_km') if k in L), None)
    print(f'  highest cell {E.max():.0f} m; summit_m max {smt.max():.0f}; crust layer {ck}')
    for c in top:
        cr = f'{float(L[ck][c]):.1f} km' if ck else '-'
        print(f'    cell {c}: {E[c]:.0f} m rock {rock[c]} crust {cr} summit {smt[c]:.0f}')
    for k in (5000, 6000, 7000):
        print(f'  cells > {k} m: {(E > k).sum()}')
    off = g.nbr_off
    nbmean = np.add.reduceat(E[g.nbr_idx], off[:-1]) / np.diff(off)
    cr = np.asarray(L[ck], float)
    airy = 250 + 150 * (np.clip(cr, 35, 80) - 35)
    for c in top:
        print(f'    cell {c}: {E[c]:.0f} m, nbr mean {nbmean[c]:.0f} m, crust {cr[c]:.1f} km, Airy {airy[c]:.0f} m, excess {E[c]-airy[c]:+.0f}')
    s = E > 6000
    if s.any():
        print(f'  cells > 6 km: crust median {np.median(cr[s]):.1f} km; elev-Airy median {np.median((E-airy)[s]):+.0f}; rock '
              + ', '.join(f'{r}:{(rock[s]==r).sum()}' for r in np.unique(rock[s])))
