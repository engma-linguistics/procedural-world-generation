"""Lane 142 (PW-1381): the model's sea against an observed SST climatology, Earth L6.
OISST v2 (Reynolds et al. 2002; NOAA PSL sst.ltm.1991-2020.nc, fetched to scratch, see get_sst.py's URL dir),
sampled at each cell's nearest 1-deg pixel. Per box: annual SST, the warmest / coldest month, the half-swings,
the overturning's share of the annual SST, the inflow's share of the surface water, and NCEP's 2 m air.
Usage: seabox.py OISST.nc [level] [tune overrides as k=v ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import numpy as np
from planet import climate, ocean
from planet.grid import build_grid
from tools import earth_data
from tools.h5_reader import read_variable
from tools.tiff_reader import BytesSource
from tools.moisture_regions import box_mask

src = BytesSource(Path(sys.argv[1]).read_bytes())
osst = read_variable(src, "sst").astype(float)
olat, olon = read_variable(src, "lat"), read_variable(src, "lon")
osst[(osst < -5) | (osst > 45)] = np.nan
level = int(sys.argv[2]) if len(sys.argv) > 2 and "=" not in sys.argv[2] else 6
tune = {}
for a in sys.argv[2:]:
    if "=" in a:
        k, v = a.split("=")
        tune[k] = float(v)
climate.TUNE.update(tune)
g = build_grid(level)
d = earth_data.earth_on_grid(g)
elev, ice = d["elev"].astype(float), d["ice"].astype(float)
rec = {}
orig_wh = ocean.winter_half
def spy_wh(sea_half_w, share, tune):
    rec["share"], rec["half_w0"] = share, sea_half_w
    out = orig_wh(sea_half_w, share, tune)
    rec["half_w"] = out
    return out
ocean.winter_half = spy_wh
c = climate.compute(g, elev, 0.0, 23.4, ice)
sea = ~earth_data.land_of(d)
w = earth_data.cell_areas(g)
iy = np.abs(olat[None, :] - g.lat[:, None]).argmin(1)
ix = np.abs(((olon[None, :] - g.lon[:, None] % 360) + 180) % 360 - 180).argmin(1)
obs = osst[:, iy, ix]  # (12, n)
ok = np.isfinite(obs).all(0)
o_ann, o_max, o_min = obs.mean(0), obs.max(0), obs.min(0)
om, ow, oc = d["obs_temp"], d["obs_t_warm"], d["obs_t_cold"]
BOX = [("N Atl storm track", 40, 60, -60, -10), ("  NW 50-60N 60-35W", 50, 60, -60, -35),
       ("  NE 50-60N 35-10W", 50, 60, -35, -10), ("  SW 40-50N 60-35W", 40, 50, -60, -35),
       ("  SE 40-50N 35-10W", 40, 50, -35, -10), ("N Pac storm track", 40, 60, 145, -130),
       ("Nordic seas", 60, 72, -20, 15), ("NE Atl 30-40N", 30, 40, -40, -10)]
print("box | SST ann model/OISST | warm month model/OISST | cold month model/OISST | moc_heat | share | "
      "half own->winter | air ann model/NCEP | air cold model/NCEP")
for name, a, b, lo, hi in BOX:
    m = box_mask(g, sea, a, b, lo, hi, "sea") & ok
    f = lambda x: float((x * w)[m].sum() / w[m].sum())
    print(f"{name} | {f(c['sst']):.1f} / {f(o_ann):.1f} | {f(np.maximum(c['sst_jul'], c['sst_jan'])):.1f} / "
          f"{f(o_max):.1f} | {f(np.minimum(c['sst_jul'], c['sst_jan'])):.1f} / {f(o_min):.1f} | "
          f"{f(c['moc_heat']):+.2f} | {f(rec['share']):.2f} | {f(rec['half_w0']):.2f}->{f(rec['half_w']):.2f} | "
          f"{f(c['temp']):.1f} / {f(om):.1f} | {f(np.minimum(c['t_warm'], c['t_cold'])):.1f} / "
          f"{f(np.minimum(ow, oc)):.1f}")
# the sea between 40 and 60 N, all longitudes: does the zonal take-off balance?
for a, b in ((30, 40), (40, 50), (50, 60), (60, 70)):
    m = sea & ok & (g.lat >= a) & (g.lat < b)
    f = lambda x: float((x * w)[m].sum() / w[m].sum())
    print(f"band {a}-{b}N sea: SST {f(c['sst']):.2f} / OISST {f(o_ann):.2f}; moc_heat {f(c['moc_heat']):+.2f}")
for s_ in c["moc_sites"]:
    print("site", s_)
