"""Lane 150 (PW-1411, PW-1413): one Earth L6 climate, three reads.
1. heatcross (lane 142): the inflow's heat above its sinking water across latitudes (RAPID 26.5 N 1.33 PW, Johns et
   al. 2011; OSNAP 0.45 PW, Lozier et al. 2019);
2. the Greenland-Scotland ridge (nordmap.py's line): sinking by basin, the inflow across it and its heat above the
   water sinking north of it (Tsubouchi et al. 2021: 305 +- 26 TW);
3. seabox (lane 142): the sea against OISST v2 1991-2020 by box (annual, coldest month, winter half-swing).
Usage: screen.py OISST.nc [k=v ...] (TUNE overrides)"""
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
for a in sys.argv[2:]:
    k, v = a.split("=")
    climate.TUNE[k] = float(v)
rec = {}
orig_ov, orig_route, orig_along, orig_wh = ocean.overturning, ocean._route, ocean._along, ocean.winter_half


def spy_ov(cg, sea, *a, **k):
    out = orig_ov(cg, sea, *a, **k)
    rec.update(cg=cg, sea=sea, out=out)
    return out


def spy_route(order, par, sink):
    T = orig_route(order, par, sink)
    rec["par"], rec["Tr"] = par.copy(), T.copy()
    return T


def spy_along(order, par, Q, tgt, x0, rate, dil):
    x = orig_along(order, par, Q, tgt, x0, rate, dil)
    if not dil.any():
        rec["t_in"], rec["Q"] = x.copy(), Q.copy()
    return x


def spy_wh(sea_half_w, share, tune):
    out = orig_wh(sea_half_w, share, tune)
    if len(share) > 50000:  # (the fine grid's call)
        rec["share"], rec["half_w0"], rec["half_w"] = share, sea_half_w, out
    return out


ocean.overturning, ocean._route, ocean._along, ocean.winter_half = spy_ov, spy_route, spy_along, spy_wh
g = build_grid(6)
d = earth_data.earth_on_grid(g)
c = climate.compute(g, d["elev"].astype(float), 0.0, 23.4, d["ice"].astype(float))
cg, o = rec["cg"], rec["out"]
lat, lon = cg.lat, cg.lon
par, Q, t, sk, Tr = rec["par"], rec["Q"], rec["t_in"], o["sinking"], rec["Tr"]
atl = (lon > -100) & (lon < 60)
sink_cells = (sk > 1e-3) & atl & (lat > 0)
T_s = float((sk * t)[sink_cells].sum() / sk[sink_cells].sum())
print(f"N Atlantic sinking {sk[sink_cells].sum():.2f} Sv, its water {T_s:.2f} C")
i = np.flatnonzero((par >= 0) & atl)
p = par[i]
row = []
for L in (26.5, 45, 55, 60, 65, 70):
    cr = (lat[p] < L) & (lat[i] >= L)
    pw = float((Q[i][cr] * climate.RHO_C_SEA * (t[i][cr] - T_s)).sum() / 1e15)
    tm = float((Q[i][cr] * t[i][cr]).sum() / max(Q[i][cr].sum(), 1e-9))
    row.append(f"{L} N {pw:.2f} PW ({tm:.1f} C)")
print("heat above the sinking water: " + "; ".join(row))
sea = rec["sea"]
atlN = sea & atl & (lat > 40)
nord = atlN & (((lat >= 66) & (lon > -40)) | ((lat >= 63.5) & (lon > -14)) | ((lat >= 62) & (lon > -8)))
print("sinking Sv: Labrador %.2f, Irminger/Iceland basin %.2f, Nordic/Barents/Arctic %.2f" % (
    sk[atlN & ~nord & (lon < -45)].sum(), sk[atlN & ~nord & (lon >= -45)].sum(), sk[nord].sum()))
T_n = float((sk * t)[nord].sum() / max(sk[nord].sum(), 1e-9))
j = np.flatnonzero(nord & (par >= 0))
j = j[~nord[par[j]]]
Qx = Tr[j]
print(f"across the ridge: {Qx.sum():.2f} Sv at {(Qx * t[j]).sum() / max(Qx.sum(), 1e-9):.2f} C; sinking north of it "
      f"at {T_n:.2f} C -> {(Qx * 1e6 * climate.RHO_C_SEA * (t[j] - T_n)).sum() / 1e12:.0f} TW")
# the sea against OISST
seaf = ~earth_data.land_of(d)
w = earth_data.cell_areas(g)
iy = np.abs(olat[None, :] - g.lat[:, None]).argmin(1)
ix = np.abs(((olon[None, :] - g.lon[:, None] % 360) + 180) % 360 - 180).argmin(1)
obs = osst[:, iy, ix]
ok = np.isfinite(obs).all(0)
o_ann, o_min = obs.mean(0), obs.min(0)
BOX = [("N Atl 40-60N 60-10W", 40, 60, -60, -10), ("NW 50-60N 60-35W", 50, 60, -60, -35),
       ("NE 50-60N 35-10W", 50, 60, -35, -10), ("Nordic 60-72N 20W-15E", 60, 72, -20, 15),
       ("N Pac 40-60N", 40, 60, 145, -130)]
print("box | SST ann model/OISST | cold month model/OISST | winter half-swing model/OISST | air cold model/NCEP")
cold = np.minimum(c["sst_jul"], c["sst_jan"])
for name, a, b, lo, hi in BOX:
    m = box_mask(g, seaf, a, b, lo, hi, "sea") & ok
    f = lambda x: float((x * w)[m].sum() / w[m].sum())
    print(f"{name} | {f(c['sst']):.1f} / {f(o_ann):.1f} | {f(cold):.1f} / {f(o_min):.1f} | "
          f"{f(c['sst'] - cold):.2f} / {f(o_ann - o_min):.2f} | "
          f"{f(np.minimum(c['t_warm'], c['t_cold'])):.1f} / {f(np.minimum(d['obs_t_warm'], d['obs_t_cold'])):.1f}")
for a, b in ((40, 50), (50, 60), (60, 70)):
    m = seaf & ok & (g.lat >= a) & (g.lat < b)
    f = lambda x: float((x * w)[m].sum() / w[m].sum())
    print(f"band {a}-{b}N sea SST {f(c['sst']):.2f} / OISST {f(o_ann):.2f}")
