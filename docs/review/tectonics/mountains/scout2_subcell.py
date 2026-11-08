"""Per coarse cell: the zoom's highest pixel and mean vs the world's cell mean (PW-1446 scout 188).

usage: subcell.py ZOOM_ID [ZOOM_ID...]   (all from one world)
Prints: per cell-mean bin, median / p90 / max of (zoom max - cell mean), and the zoom's own cell means vs world.
"""
import json, os, sys
import numpy as np

ROOT = os.environ.get('ZROOT', '/home/daniel/personal/repos/procedural-world-generation')
sys.path.insert(0, os.getcwd())
from planet import world as W, summit
from planet.zoom import regional as RG

BINS = [(0, 500), (500, 1000), (1000, 2000), (2000, 3000), (3000, 4000), (4000, 5000), (5000, 7000), (7000, 12000)]
EARTH = {(0, 500): (105, 549), (500, 1000): (389, 1085), (1000, 2000): (622, 1408), (2000, 3000): (617, 1762),
         (3000, 4000): (1143, 2008), (4000, 5000): (941, 1732), (5000, 7000): (816, 1276)}
_worlds = {}


def world(wid):
    if wid not in _worlds:
        w = W.load(f'{ROOT}/worlds/{wid}.json')
        _worlds[wid] = w
    return _worlds[wid]


for zid in sys.argv[1:]:
    zd = f'{ROOT}/zooms/{zid}'
    d = json.load(open(zd + '/zoom.json'))
    wid = d['source_world']['id']
    w = world(wid)
    g, L = w['grid'], w['layers']
    E = np.asarray(L['elevation'], float)
    rock = np.asarray(L['rock']).astype(int)
    nx, ny, res = d['nx'], d['ny'], d['res_km']
    sp = d['layers']['elevation']
    e = np.fromfile(os.path.join(zd, sp['file']), dtype=sp['dtype']).reshape(sp['shape']).astype(float).ravel()
    wat = np.fromfile(os.path.join(zd, 'layers/water.bin'), dtype='u1').ravel()
    fr = RG.frame_of(d['center'])
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    own = g.locate(fr.to_sphere(X.ravel(), Y.ravel()))
    land = wat == 0
    cells, inv, cnt = np.unique(own, return_inverse=True, return_counts=True)
    zmax = np.full(len(cells), -1e9)
    np.maximum.at(zmax, inv[land], e[land])
    zmean = np.bincount(inv, e, len(cells)) / cnt
    full = cnt >= 0.6 * cnt.max()  # cells wholly inside the zoom
    em = E[cells]
    ok = full & (em > 0) & (zmax > -1e8)
    dz = zmax - em
    smt = summit.summit_m(g, E)[cells]
    print(f'== zoom {zid} ({res} km/px) of world {wid}; {ok.sum()} full land cells; '
          f'world cell max {em[ok].max():.0f} m; zoom max {zmax[ok].max():.0f} m; world summit_m max {smt[ok].max():.0f}')
    print(f'  zoom cell-mean - world cell-mean on these cells: median {np.median(zmean[ok]-em[ok]):+.0f}, '
          f'|p90| {np.percentile(np.abs(zmean[ok]-em[ok]), 90):.0f} m')
    print('  bin(km)      n   med(max-mean)  p90   max  | Earth med p90 | world summit-mean med')
    for b in BINS:
        s = ok & (em >= b[0]) & (em < b[1])
        if s.sum() == 0:
            continue
        ea = EARTH.get(b, ('-', '-'))
        print(f'  {b[0]/1e3:.1f}-{b[1]/1e3:.1f}  {s.sum():5d}  {np.median(dz[s]):7.0f}  {np.percentile(dz[s],90):7.0f}'
              f' {dz[s].max():6.0f}  | {ea[0]:>5} {ea[1]:>5} | {np.median(smt[s]-em[s]):6.0f}')
    lr = summit.local_relief(g, E)[cells]
    print('  by local relief (3x3 max-min of world means, the summit.py fit): zoom p75(max-mean) vs Earth p75 (RELIEF_KNOTS)')
    edges = [0, 300, 700, 1200, 2000, 3000, 6000]
    for a, b in zip(edges[:-1], edges[1:]):
        s = ok & (lr >= a) & (lr < b)
        if s.sum() < 3:
            continue
        print(f'    relief {a:5d}-{b:5d} m  n {s.sum():5d}  zoom p75 {np.percentile(dz[s], 75):6.0f}  max {dz[s].max():6.0f}'
              f'  Earth p75 {summit.sub_cell_relief(np.median(lr[s])):6.0f}  (cell mean median {np.median(em[s]):.0f})')
    top = np.argsort(-np.where(ok, zmax, -1e9))[:6]
    print('  top cells: cell  world_mean  zoom_max  dz  rock  world_summit')
    for k in top:
        print(f'    {cells[k]:7d} {em[k]:7.0f} {zmax[k]:7.0f} {dz[k]:6.0f} {rock[cells[k]]:3d} {smt[k]:7.0f}')
