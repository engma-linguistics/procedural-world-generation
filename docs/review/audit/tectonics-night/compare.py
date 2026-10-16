"""Before/after table of health sweeps (tools/health.py --quick outputs).

    uv run python docs/review/audit/tectonics-night/compare.py <health dir> [<health dir> ...]

Per sweep: per-seed values (frames after 50 Myr), then the mean over seeds.
"""
import gzip
import json
import sys
from pathlib import Path

import numpy as np


def spells(vals, thr=-50.0, gap=5):
    n, last = 0, -10**9
    for i, v in enumerate(vals):
        if v is not None and v < thr:
            if i - last > gap:
                n += 1
            last = i
    return n


def summary(d: Path):
    sw = json.load(open(d / "sweep.json"))
    fr = json.load(gzip.open(d / "frames.json.gz"))
    rows = []
    for r in sw["results"]:
        f = [x for x in fr[r["id"]] if x["t"] > 50]
        med = lambda k: float(np.median([x[k] for x in f if x[k] is not None]))  # noqa: E731
        rows.append(dict(
            seed=r["seed"], vol=r["checks"]["volume_ratio"], land=med("land_pct"), cont=med("cont_pct"),
            km=med("cont_km"), peak=max(x["max_elev_km"] for x in f), peak_frames=r["checks"]["peak_frames"],
            inland=med("inland_pct"), lakes=med("lake_pct"), giant=r["checks"]["giant_lake_frames"],
            sea=med("sea_level"), age=med("ocean_age"), plates=med("plates"),
            ice_spells=spells([x["sea_ice_m"] for x in fr[r["id"]]])))
    return rows


KEYS = ["vol", "land", "cont", "km", "peak", "peak_frames", "inland", "lakes", "giant", "sea", "age", "plates",
        "ice_spells"]
for p in sys.argv[1:]:
    rows = summary(Path(p))
    print(f"## {p}")
    print("| seed | " + " | ".join(KEYS) + " |")
    for r in rows:
        print(f"| {r['seed']} | " + " | ".join(f"{r[k]:.3g}" for k in KEYS) + " |")
    mean = {k: np.mean([r[k] for r in rows]) for k in KEYS}
    mean["peak_max"] = max(r["peak"] for r in rows)
    mean["vol_range"] = (min(r["vol"] for r in rows), max(r["vol"] for r in rows))
    mean["ice_spells"] = sum(r["ice_spells"] for r in rows)
    print("| mean | " + " | ".join(f"{mean[k]:.3g}" for k in KEYS) + " |")
    print(f"peak max {mean['peak_max']:.2f} km, volume range {mean['vol_range']}, icehouse spells total "
          f"{mean['ice_spells']}")
    print()
