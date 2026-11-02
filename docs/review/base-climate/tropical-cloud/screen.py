"""Lane 126: Earth L7 screen for the land humidity-layer cloud gate (PW-1334), the summer split's sunshine reading
(PW-1327) and its candidates. Runs vegetation.coupled_climate on the worktree's private data/earth copy with TUNE
overrides, records climate.clouds' inputs, and prints:
- warm land (obs T > 18, |lat| < 35) sky / sun / shade in the three rain bands, same cells (model and GPCC rain both
  in band), against CRU sunshine (as tropical-cloud/bands.py);
- land cloud regions (earth_check CLOUD_REGIONS land rows + Pacific NW), annual sky cover % and sunshine vs CRU;
- warmest month by band (0-20, 20-40, 40-60) vs NCEP, land >= 30 / >= 35 C share, regional warm-month biases;
- with --prox, the stability proxies of the layer cloud by region and season.

    PYTHONPATH=. uv run python docs/review/base-climate/tropical-cloud/screen.py [--tune k=v,k=v] [--prox] [--save F]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate, vegetation  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools import earth_data  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--tune", default="")
ap.add_argument("--prox", action="store_true")
ap.add_argument("--save", default="")
ap.add_argument("--recall", default="", help="';'-separated TUNE override sets to re-call clouds() with (no re-solve)")
A = ap.parse_args()
for kv in A.tune.split(","):
    if kv:
        k, v = kv.split("=")
        assert k in climate.TUNE, k
        climate.TUNE[k] = type(climate.TUNE[k])(float(v)) if not isinstance(climate.TUNE[k], tuple) else \
            tuple(float(x) for x in v.split(":"))
        print("TUNE", k, "=", climate.TUNE[k], flush=True)

rec = {}
orig = climate.clouds


def spy(*a, **k):
    rec["args"] = a
    return orig(*a, **k)


climate.clouds = spy
g = build_grid(7)
d = earth_data.earth_on_grid(g)
cl = earth_data.earth_clouds(g)
elev, ice = d["elev"].astype(float), d["ice"].astype(float)
c, _ = vegetation.coupled_climate(g, elev, 0.0, 23.4, ice)
lat, lon, w = g.lat, g.lon, earth_data.cell_areas(g)
land = earth_data.land_of(d) & (ice <= 0)
dh = climate.day_hours(lat, 23.4)
m_sun = 0.5 * (c["sun_jul"] / np.maximum(dh[0], 1e-6) + c["sun_jan"] / np.maximum(dh[1], 1e-6))
m_sky = 0.5 * (c["cloud_jul"] + c["cloud_jan"])
m_sh = 0.5 * (c["shade_jul"] + c["shade_jan"])
o_sun = 0.5 * (cl["obs_sun_jul"] + cl["obs_sun_jan"])
o_sh = 0.5 * (climate.shade(cl["obs_sun_jul"]) + climate.shade(cl["obs_sun_jan"]))
P, oP, oT = c["precip"], d["obs_precip"], d["obs_temp"]


def wm(x, m):
    m = m & np.isfinite(x)
    return float((x * w)[m].sum() / w[m].sum()) if m.sum() else float("nan")


def box(a, b, lo, hi):
    return (lat >= a) & (lat <= b) & (lon >= lo) & (lon <= hi)


print("\n== warm land, same cells: sky / sun / shade  model | obs(CRU)")
warm = land & (oT > 18) & (np.abs(lat) < 35)
for p0, p1 in ((400, 900), (900, 1500), (1500, 6000)):
    m = warm & (P >= p0) & (P < p1) & (oP >= p0) & (oP < p1)
    print(f"  {p0}-{p1}: n={int(m.sum()):5d}  {wm(m_sky, m):.2f}/{wm(m_sun, m):.2f}/{wm(m_sh, m):.2f}"
          f"  | {wm(o_sun, m):.2f}/{wm(o_sh, m):.2f}")
print("\n== land cloud regions: sky % (target), sun model / CRU")
from tools.earth_check import CLOUD_REGIONS  # noqa: E402
regs = [r for r in CLOUD_REGIONS if r[5] == "land"] + [("Pacific NW", 42, 50, -125, -120, "land", (60, 75))]
for name, a, b, lo, hi, surf, tgt in regs:
    m = land & box(a, b, lo, hi)
    print(f"  {name:20} sky {100 * wm(m_sky, m):5.1f} ({tgt[0]}-{tgt[1]})  jul {100 * wm(c['cloud_jul'], m):4.0f}"
          f" jan {100 * wm(c['cloud_jan'], m):4.0f}  sun {wm(m_sun, m):.2f} / {wm(o_sun, m):.2f}")

print("\n== warmest month vs NCEP (ice-free land north of 60S)")
tw, otw = c["t_warm"], d["obs_t_warm"]
L = land & (lat > -60)
for a, b in ((0, 20), (20, 40), (40, 60)):
    m = L & (np.abs(lat) >= a) & (np.abs(lat) < b)
    print(f"  {a}-{b}: {wm(tw, m):5.1f} vs {wm(otw, m):5.1f} ({wm(tw - otw, m):+.1f})   d_sum n/a")
nth = lat >= 0
m_ss = np.where(nth, c["sun_jul"] / np.maximum(dh[0], 1e-6), c["sun_jan"] / np.maximum(dh[1], 1e-6))
o_ss = np.where(nth, cl["obs_sun_jul"], cl["obs_sun_jan"])
for a_, b_ in ((0, 10), (10, 20), (20, 40), (40, 60), (20, 60)):
    m = L & (np.abs(lat) >= a_) & (np.abs(lat) < b_)
    print(f"  summer sunshine share {a_}-{b_}: model {wm(m_ss, m):.3f}  CRU {wm(o_ss, m):.3f}")
for thr in (30, 35):
    print(f"  land >= {thr} C: {100 * wm((tw >= thr).astype(float), L):.1f}%  NCEP {100 * wm((otw >= thr).astype(float), L):.1f}%")
REG = [("Sahara", 18, 30, -10, 30), ("Arabia", 17, 28, 40, 55), ("India", 10, 28, 72, 88),
       ("US Southwest", 31, 37, -115, -105), ("Mexico N", 24, 31, -110, -100), ("Sahel", 10, 16, -15, 30),
       ("W Africa coast", 4, 9, -10, 5), ("SE USA", 29, 36, -92, -78), ("Pacific NW", 42, 50, -125, -120),
       ("W Europe", 43, 55, -5, 15), ("Siberia", 55, 70, 65, 140), ("Amazon", -10, 2, -70, -50)]
print("  region warm month model / NCEP (bias)   annual model / obs")
for name, a, b, lo, hi in REG:
    m = L & box(a, b, lo, hi)
    print(f"  {name:16} {wm(tw, m):5.1f} / {wm(otw, m):5.1f} ({wm(tw - otw, m):+.1f})   "
          f"{wm(c['temp'], m):5.1f} / {wm(oT, m):5.1f}   summer sun {wm(m_ss, m):.2f} / {wm(o_ss, m):.2f}")

print("\n== lake evaporation mm/yr: shade (as run) | sky cover (the old reading)")
old = climate.open_water_evap(lat, c["temp"], c["t_warm"], c["t_cold"], c["rh_jul"], c["rh_jan"], c["cloud_jul"],
                              c["cloud_jan"], 23.4)
for name, a_, b_, lo, hi in (("Lake Victoria", -3, 0.5, 31.5, 34.5), ("Amazon floodplain", -4, -2, -65, -55),
                             ("Lake Chad", 12, 14.5, 13, 15.5), ("Caspian", 37, 47, 47, 54), ("Great Basin", 38, 42, -120, -112),
                             ("Lake Eyre", -30, -27, 136, 139)):
    m = land & box(a_, b_, lo, hi)
    print(f"  {name:18} {wm(c['lake_evap'], m):6.0f} | {wm(old, m):6.0f}")
if A.prox:
    s_in = rec["args"][2]
    vap = rec["args"][3]
    print("\n== layer-cloud stability proxies (land): lts = t_ref - (t_air + height) [C], -inst [C], t_sl, rh")
    for si, q, tag in zip(s_in, vap, ("jul", "jan")):
        rh = np.clip(q / np.maximum(si["qs"], 1e-12), 0, 1)
        inst = si["mse_t"] + climate.LQ * q - si["mse_thr"]
        lts = si["t_ref"] - si["mse_t"]
        for name, a, b, lo, hi in [("warm 400-900", None, None, None, None), ("warm >1500", None, None, None, None)] + \
                [("W Europe", 43, 55, -5, 15), ("Pacific NW", 42, 50, -125, -120), ("Siberia", 55, 70, 65, 140),
                 ("Amazon", -10, 2, -70, -50), ("Sahel", 10, 16, -15, 30), ("S Africa sav", -25, -10, 15, 35),
                 ("China E", 25, 35, 105, 120), ("Canada", 50, 65, -120, -80)]:
            if a is None:
                m = warm & ((oP >= 400) & (oP < 900) if "900" in name else (oP >= 1500))
            else:
                m = land & box(a, b, lo, hi)
            print(f"  {tag} {name:14} lts {wm(lts, m):6.1f}  -inst {wm(-inst, m):6.1f}  t_sl {wm(si['t_sl'], m):5.1f}"
                  f"  rh {wm(rh, m):.2f}  rh^1.5*0.55 {wm(0.55 * rh ** 1.5, m):.2f}")
if A.save:
    np.savez_compressed(A.save, tw=tw, temp=c["temp"], sky=m_sky, sun=m_sun, koppen=c["koppen"], P=P)

if A.recall:
    a = rec["args"]
    s_in = a[2]
    print("\n== re-call clouds (no re-solve). shade 400-900/900-1500/>1500 same cells (obs 0.27/0.41/0.53) | summer sun"
          " 0-10,10-20,20-40,40-60 (CRU .46 .57 .67 .55) | annual sky % WEur PNW Sib Amaz Congo (60-75,-,60-70,65-80,70-80)"
          " | summer sun WEur PNW India MexN SEUSA (CRU .45 .62 .49 .61 .64)")
    gates = {"lts": lambda si, t: climate._layer_gate(si, t),
             "temp": lambda si, t: np.clip((t["g_t1"] - si["t_sl"]) / t["g_dt"], t["g_f"], 1)}
    for spec in [""] + A.recall.split(";"):
        t = dict(a[5])
        gate = "lts"
        for kv in spec.split(","):
            if kv:
                k, v = kv.split("=")
                if k == "gate":
                    gate = v
                    continue
                t[k] = tuple(float(x) for x in v.split(":")) if ":" in v else float(v)
        keep = climate._layer_gate
        climate._layer_gate = lambda si, tt, g=gates[gate], kk=keep: g(si, tt) if gate != "lts" else kk(si, tt)
        out = orig(*a[:5], t, *a[6:])
        climate._layer_gate = keep
        sky = 0.5 * (out[0][0] + out[1][0])
        sh = 0.5 * (climate.shade(out[0][1]) + climate.shade(out[1][1]))
        ss = np.where(nth, out[0][1], out[1][1])
        bands = []
        for p0, p1 in ((400, 900), (900, 1500), (1500, 6000)):
            m = warm & (P >= p0) & (P < p1) & (oP >= p0) & (oP < p1)
            bands.append(f"{wm(sh, m):.2f}")
        sb = [wm(ss, L & (np.abs(lat) >= a_) & (np.abs(lat) < b_)) for a_, b_ in ((0, 10), (10, 20), (20, 40), (40, 60))]
        rs = [100 * wm(sky, land & box(*r)) for r in ((43, 55, -5, 15), (42, 50, -125, -120), (55, 70, 65, 140),
                                                       (-10, 2, -70, -50), (-5, 5, 12, 30))]
        sr = [wm(ss, land & box(*r)) for r in ((43, 55, -5, 15), (42, 50, -125, -120), (10, 28, 72, 88),
                                               (24, 31, -110, -100), (29, 36, -92, -78))]
        print(f"  {spec or 'as run':40} {'/'.join(bands)} | " + " ".join(f"{x:.2f}" for x in sb) + " | "
              + " ".join(f"{x:3.0f}" for x in rs) + " | " + " ".join(f"{x:.2f}" for x in sr), flush=True)
