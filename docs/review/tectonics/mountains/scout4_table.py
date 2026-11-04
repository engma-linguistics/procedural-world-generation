"""PW-1446 scout 193: per-draw late-window carbon-cycle table of two judge arms (read-only on the ice_diag records).

    uv run python docs/review/tectonics/mountains/scout4_table.py JUDGE_DIR [--a main --b cap] [--out table.json]

JUDGE_DIR holds <arm>_r<roll>_<group>/seed<N>_L6.json.gz. Per draw, over the late window (600-1000 Myr), the means of
dT and of the carbon cycle's parts: the balance is sink_raw co2_law(X) = source_raw exp(-YARDSTICK), and sink_raw =
w_supply w_plant w_temp (erosion supply x plant factor x climate factor), so ln(source_raw / w_supply) is the
tectonic forcing the thermostat answers. Writes one JSON row per draw and arm.
"""
import argparse
import glob
import gzip
import json
import math
import os

import numpy as np

LATE = (600.0, 1000.0)


def late(rows, key, log=False):
    v = [r.get(key) for r in rows]
    v = [x for x in v if x is not None and (x > 0 or not log)]
    if log:
        v = [math.log(x) for x in v]
    return float(np.mean(v)) if v else None


def one(path):
    d = json.load(gzip.open(path))
    st = [s for s in d["steps"] if LATE[0] <= s["t"] <= LATE[1]]
    out = {"t_end": d["steps"][-1]["t"]}
    for k in ("dT", "co2", "co2_term", "albedo_term", "star", "ghg", "drift", "land", "w_area", "w_rate", "w_T",
              "w_q", "w_bare", "w_a", "iced_land", "src", "sink", "plume_src"):
        out[k] = late(st, k)
    for k in ("source_raw", "sink_raw", "w_supply", "w_plant", "w_temp", "src", "sink"):
        out["ln_" + k] = late(st, k, log=True)
    ok = [s for s in st if s.get("w_temp") and s.get("w_supply")]
    out["sd_dT"] = float(np.std([s["dT"] for s in st]))
    out["sd_ln_supply"] = float(np.std([math.log(s["w_supply"]) for s in ok]))
    out["sd_co2"] = float(np.std([s["co2"] for s in st]))
    # within-run sensitivities to dT over the late window (slope of ln factor on dT)
    x = np.array([s["dT"] for s in ok])
    for k in ("w_temp", "w_supply", "w_plant"):
        y = np.array([math.log(s[k]) for s in ok])
        out["b_" + k] = float(np.polyfit(x, y, 1)[0]) if len(x) > 5 and x.std() > 0 else None
    ok2 = [s for s in ok if s.get("w_T") is not None and s.get("w_q")]
    x2 = np.array([s["dT"] for s in ok2])
    if len(x2) > 5 and x2.std() > 0:
        out["b_w_T"] = float(np.polyfit(x2, [s["w_T"] for s in ok2], 1)[0])  # C of supply-weighted T per C of dT
        out["b_w_q"] = float(np.polyfit(x2, [math.log(s["w_q"]) for s in ok2], 1)[0])
        out["b_w_area"] = float(np.polyfit(x2, [math.log(s["w_area"]) for s in ok2], 1)[0])
        out["b_w_rate"] = float(np.polyfit(x2, [math.log(s["w_rate"]) for s in ok2], 1)[0])
    # within-run co-movement of the outgassing and the erosion supply (10-step means, to skip step noise)
    if len(ok) >= 40:
        n = len(ok) // 10 * 10
        ls = np.array([math.log(s["source_raw"]) for s in ok[:n]]).reshape(-1, 10).mean(1)
        lw = np.array([math.log(s["w_supply"]) for s in ok[:n]]).reshape(-1, 10).mean(1)
        out["r_src_sup_time"] = float(np.corrcoef(ls, lw)[0, 1])
    h = [r for r in d.get("hyps", []) if LATE[0] <= r["t"] <= LATE[1]]
    if h:
        for k in ("p2", "p3", "p4", "n5", "n6", "max", "thick_max"):
            out["h_" + k] = float(np.mean([r[k] for r in h]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--a", default="main")
    ap.add_argument("--b", default="cap")
    ap.add_argument("--out")
    a = ap.parse_args()
    rows = []
    for arm in (a.a, a.b):
        for p in sorted(glob.glob(os.path.join(a.dir, f"{arm}_r*", "seed*_L6.json.gz"))):
            grp = os.path.basename(os.path.dirname(p))[len(arm) + 1:]
            seed = int(os.path.basename(p)[4:].split("_")[0])
            r = one(p)
            r.update(arm=arm, draw=f"{grp}:{seed}")
            rows.append(r)
    if a.out:
        with open(a.out, "w") as f:
            json.dump(rows, f, indent=0)
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
