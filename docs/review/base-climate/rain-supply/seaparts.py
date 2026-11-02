"""Lane 134 (PW-1362): the parts of the annual sea temperature in the NH subtropical sea boxes (Earth L6).
t_sea (the latitude's), the land air's chill (compute's), the upwelling, what the currents add (raw0 - t_sea + chill
+ upwelling, before the band mean is restored), the overturning (moc_heat), the shelf air; against NCEP's annual
2 m air. Also each box's half-swings (_sea_half: own, the land's share) against NCEP's."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import numpy as np
from planet import climate
from planet.grid import build_grid
from tools import earth_data
from tools.moisture_regions import SEA_BOXES, box_mask

g = build_grid(int(sys.argv[1]) if len(sys.argv) > 1 else 6)
d = earth_data.earth_on_grid(g)
elev, ice = d["elev"].astype(float), d["ice"].astype(float)
rec = {}
orig_sh = climate._sea_half
def spy_sh(*a, **k):
    out = orig_sh(*a, **k)
    rec["half"] = out
    rec["land_air"] = a[3]
    return out
climate._sea_half = spy_sh
orig_ss = climate.sea_surface
def spy_ss(*a, **k):
    out = orig_ss(*a, **k)
    if k.get("share") is None and k.get("chill") is not None:
        rec["raw0"] = out[0]
        rec["chill"] = k["chill"]
        rec["t_sea"] = a[2]
    return out
climate.sea_surface = spy_ss
c = climate.compute(g, elev, 0.0, 23.4, ice)
sea = ~earth_data.land_of(d)
w = earth_data.cell_areas(g)
tune = climate.TUNE
hk = tune["hk"]
om, ow, oc = d["obs_temp"], d["obs_t_warm"], d["obs_t_cold"]
up = c["upwelling"]
sea_half, sea_half_w = rec["half"]
own = climate._sea_half(g.lat, 23.4, climate.season_strength(g, 23.4), np.zeros(g.n), tune, rec["t_sea"])[0]
print("box | t_sea | chill | upwelling | currents | moc | shelf | final SST | NCEP air ann | final air ann | "
      "half-swing own / land-summer / land-winter | final air half | NCEP air half")
for name, a, b, lo, hi, _k in SEA_BOXES:
    if name not in ("Gulf of Mexico", "W Atlantic subtropics", "E Atlantic subtropics", "NW Pacific subtropics",
                    "N Atlantic storm track", "N Pacific storm track"):
        continue
    m = box_mask(g, sea, a, b, lo, hi, "sea")
    f = lambda x: float((x * w)[m].sum() / w[m].sum())
    cur = rec["raw0"] - rec["t_sea"] + rec["chill"] + up
    shelf = c["sst"] - (rec["raw0"] + c["moc_heat"])
    print(f"{name} | {f(rec['t_sea']):.1f} | {-f(rec['chill']):.2f} | {-f(up):.2f} | {f(cur):+.2f} | "
          f"{f(c['moc_heat']):+.2f} | {f(np.maximum(shelf, -50)):+.2f} | {f(c['sst']):.1f} | {f(om):.1f} | "
          f"{f(c['temp']):.1f} | {f(own):.2f} / {f(sea_half - own):.2f} / {f(sea_half_w - own):.2f} | "
          f"{f(0.5 * (c['t_warm'] - c['t_cold'])):.2f} | {f(0.5 * (ow - oc)):.2f}")
