"""usage: curves.py LABEL=DIAG_DIR ... -- ice_diag runs (seed*_L6.json.gz), pooled per tree over the steps after 300 Myr:
(1) the ice against dT: per 1 C bin of dT, the share of steps in an icehouse (ice sea level <= -20 m), deep
(<= -150 m) and the mean ice sea level; (2) the parts of dT: drift, CO2 term, ice albedo term, and the CO2 stock's
split ln(source) - ln(sink) with the sink's parts (ice-free area, supply per area, plant factor, temperature factor),
each against the seed's own 300 Myr reference, mean over the pooled steps and in the deep steps; (3) the CO2 answer:
the pooled regression of the CO2 term on dT and of ln sink on dT."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

T0 = 300.0
BINS = np.arange(-8, 9, 1.0)


def load(d):
    runs = {}
    for p in sorted(Path(d).glob("seed*_L6.json.gz")):
        r = json.load(gzip.open(p))
        st = [s for s in r["steps"] if "dT" in s]
        runs[p.name.split("_")[0]] = st
    return runs


def arr(st, k):
    return np.array([np.nan if s.get(k) is None else s[k] for s in st], float)


for arg in sys.argv[1:]:
    label, d = arg.split("=", 1)
    runs = load(d)
    pooled = {k: [] for k in ("dT", "sea_ice", "drift", "co2_term", "albedo_term", "lsrc", "lsink", "area", "supa",
                              "plant", "temp", "co2")}
    for name, st in runs.items():
        t = arr(st, "t")
        m = t >= T0
        ref = np.argmin(np.abs(t - T0))  # (the references are frozen at 300 Myr: the parts against their value there)
        area, sup, plant, temp = (arr(st, k) for k in ("w_area", "w_supply", "w_plant", "w_temp"))
        pooled["dT"].append(arr(st, "dT")[m])
        pooled["sea_ice"].append(arr(st, "sea_ice")[m])
        for k in ("drift", "co2_term", "albedo_term", "co2"):
            pooled[k].append(arr(st, k)[m])
        pooled["lsrc"].append(np.log(arr(st, "src"))[m])
        pooled["lsink"].append(np.log(arr(st, "sink"))[m])
        pooled["area"].append(np.log(area / area[ref])[m])
        pooled["supa"].append(np.log((sup / area) / (sup[ref] / area[ref]))[m])
        pooled["plant"].append(np.log(plant / plant[ref])[m])
        pooled["temp"].append(np.log(temp / temp[ref])[m])
    P = {k: np.concatenate(v) for k, v in pooled.items()}
    dT, si = P["dT"], P["sea_ice"]
    print(f"== {label}: {len(runs)} seeds, {len(dT)} steps after {T0:g} Myr; icehouse {100 * (si <= -20).mean():.0f}%, "
          f"deep {100 * (si <= -150).mean():.1f}%, mean dT {np.nanmean(dT):+.2f}, median {np.nanmedian(dT):+.2f}")
    print("  dT bin | steps | icehouse % | deep % | mean ice SL m")
    for lo in BINS[:-1]:
        b = (dT >= lo) & (dT < lo + 1)
        if b.sum() >= 20:
            print(f"  {lo:+.0f}..{lo + 1:+.0f} | {b.sum()} | {100 * (si[b] <= -20).mean():.0f} | {100 * (si[b] <= -150).mean():.0f} | "
                  f"{si[b].mean():.0f}")
    deep = si <= -150
    for tag, sel in (("all", np.ones_like(deep)), ("deep", deep), ("ice-free (> -20 m)", si > -20)):
        if sel.sum() == 0:
            continue
        f = {k: np.nanmean(P[k][sel]) for k in P}
        print(f"  {tag} ({sel.sum()} steps): dT {f['dT']:+.2f} = drift {f['drift']:+.2f} + CO2 {f['co2_term']:+.2f} + "
              f"albedo {f['albedo_term']:+.2f}; co2 {f['co2']:+.3f} e-folds: ln src {f['lsrc']:+.3f}, ln sink {f['lsink']:+.3f} "
              f"(area {f['area']:+.3f}, supply/area {f['supa']:+.3f}, plants {f['plant']:+.3f}, temp {f['temp']:+.3f}; vs 300 Myr)")
    ok = np.isfinite(dT) & np.isfinite(P["co2_term"]) & np.isfinite(P["lsink"])
    b_co2 = np.polyfit(dT[ok], P["co2_term"][ok], 1)[0]
    b_sink = np.polyfit(dT[ok], P["lsink"][ok], 1)[0]
    print(f"  regressions on dT (pooled, trends in): CO2 term {b_co2:+.2f} C/C, ln sink {b_sink:+.4f} per C")
