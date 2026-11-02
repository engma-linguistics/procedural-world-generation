"""earthw.py CODE_DIR : Earth L6 climate.compute water / energy bookkeeping (read-only on the owner's L6.npz)."""
import sys
sys.path.insert(0, sys.argv[1])
import numpy as np
from planet import climate
from planet.grid import build_grid
g = build_grid(6)
z = np.load("/home/daniel/personal/repos/procedural-world-generation/data/earth/L6.npz")
elev, ice = z["elev"].astype(float), z["ice"].astype(float)
calls = []
orig = climate.rain
def spy(*a, **k):
    out = orig(*a, **k); calls.append(out); return out
climate.rain = spy
c = climate.compute(g, elev, 0.0, 23.4, ice)
land = climate.is_land(elev, ice, g); ocean = ~land
lat = g.lat
w = np.cos(np.radians(lat)) if np.abs(lat).max() > 3.2 else np.cos(lat)
latd = np.degrees(lat) if np.abs(lat).max() <= 3.2 else lat
m = lambda x, k=slice(None): float((x * w)[k].sum() / w[k].sum())
print("rain passes", len(calls))
for i, ((rj, ra), (ej, ea), _q, _s) in enumerate(calls):
    print(f" pass {i+1}: kernel P {m(0.5*(rj+ra)):.1f}  kernel E {m(0.5*(ej+ea)):.1f} (sea E {m(np.where(ocean,0.5*(ej+ea),0))/m(ocean*1.0):.1f})")
P = c["precip"]; E = np.where(ocean, c["sea_evap"], c["aet"])
print(f"final: P {m(P):.1f} sea_evap+aet {m(E):.1f}  land P {m(P, land):.1f} land aet {m(c['aet'], land):.1f} runoff {m(c['runoff'], land):.1f}")
print(f"global T {m(c['temp']):.2f}  sea T {m(c['temp'], ocean):.2f} land T {m(c['temp'], land):.2f}")
for lo, hi in ((-90, -60), (-60, -30), (-30, 0), (0, 30), (30, 45), (45, 60), (60, 75), (75, 90)):
    k = (latd >= lo) & (latd < hi); kl = k & land; ko = k & ocean
    cl = 0.5 * (c["cloud_jul"] + c["cloud_jan"])
    print(f"{lo:4d}..{hi:3d} T {m(c['temp'], k):6.2f} landT {m(c['temp'], kl) if kl.any() else np.nan:6.2f} "
          f"landTwarm {m(c['t_warm'], kl) if kl.any() else np.nan:6.2f} landP {m(P, kl) if kl.any() else np.nan:6.0f} "
          f"seaP {m(P, ko) if ko.any() else np.nan:6.0f} cloud {m(cl, k):.3f} landcloud {m(cl, kl) if kl.any() else np.nan:.3f}")
