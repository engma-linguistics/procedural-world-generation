"""Earth L6, SH summer (the 'jan' half-year), first-guess land-sea winds: per box, the first-guess t_sl,
its zonal mean, the anomaly, the 900 km and the big warmth, and the east / north parts (m/s) of the
belts, the 900 km land-sea part and the big part (the final, front-shifted call)."""
import sys, os
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, WT)
import numpy as np
from planet import climate, vegetation
from planet.grid import build_grid
from tools import earth_data
from tools.earth_data import cell_areas
grid = build_grid(6); d = earth_data.earth_on_grid(grid); w = cell_areas(grid)
lat, lon = grid.lat, grid.lon; land = earth_data.land_of(d)
cap = []
_om = climate.monsoon_wind
def spy(g, t_sl, shift, *a, **kw):
    if g.n == grid.n: cap.append((t_sl.copy(), shift, list(a) + [None] * 6))
    return _om(g, t_sl, shift, *a, **kw)
climate.monsoon_wind = spy
c = vegetation.coupled_climate(grid, d["elev"].astype(np.float64), 0.0, 23.4, d["ice"].astype(np.float64))[0]
t, sh, a = cap[-1]  # the final jan call
G = climate._geom(grid); U = climate.U_REF
zm = climate.zonal_mean(grid, t)
col = a[5]
anom = (t - zm) * (1 if col is None else col)
w9 = climate.smooth(grid, anom, 900.0); wb = a[1] * climate.smooth_big(grid, anom, a[2])
belts = climate.wind(grid, sh, a[3], 1.0 if a[4] is None else a[4])
p9 = _om(grid, t, sh, a[0], 0.0, a[2], a[3], 1.0 if a[4] is None else a[4], col)[0] - belts
pall = _om(grid, t, sh, a[0], a[1], a[2], a[3], 1.0 if a[4] is None else a[4], col)[0] - belts
def en(v, m):
    e = (v * G["east"]).sum(1) * U; n = (v * G["north"]).sum(1) * U
    return f"E {np.average(e[m], weights=w[m]):+4.1f} N {np.average(n[m], weights=w[m]):+4.1f}"
B = {"Patagonia land": (-52, -40, -76, -65, True), "S Atl off Pat": (-52, -40, -64, -56, False),
     "SE Pac off Chile": (-52, -38, -85, -76, False), "Tasmania land": (-44, -40, 144, 149, True),
     "Tasman": (-45, -35, 150, 165, False), "NZ land": (-47, -34, 166, 179, True), "Agulhas": (-40, -30, 15, 35, False)}
for k, (a0, a1, l0, l1, L) in B.items():
    m = (land == L) & (lat >= a0) & (lat < a1) & (lon >= l0) & (lon < l1)
    print(f"{k:>16}: t_sl {np.average(t[m], weights=w[m]):5.1f} zm {np.average(zm[m], weights=w[m]):5.1f} "
          f"anom {np.average(anom[m], weights=w[m]):+5.1f} w900 {np.average(w9[m], weights=w[m]):+5.1f} "
          f"big {np.average(wb[m], weights=w[m]):+5.1f} | belts {en(belts, m)} | 900 {en(p9, m)} | +big {en(pall, m)}"
          f" | model Tw {np.average(c['t_warm'][m], weights=w[m]):5.1f} obs {np.nanmean(d['obs_t_warm'][m]):5.1f}")
