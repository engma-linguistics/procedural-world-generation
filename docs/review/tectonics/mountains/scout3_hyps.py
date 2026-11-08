"""PW-1446 (b) scout 190: paired hypsometry of two ice_diag arms (the `hyps` records, every 10 Myr).
usage: scout3_hyps.py JUDGE_ROOT ARM_A ARM_B [T0 T1] -> per draw, medians over T0..T1 Myr (default 100..1000)"""
import glob, gzip, json, os, sys
import numpy as np

root, A, B = sys.argv[1:4]
t0, t1 = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (100.0, 1000.0)
K = ("p2", "p3", "p4", "n5", "n6", "n7", "max", "thick_max")


def rows(path):
    d = json.load(gzip.open(path))
    return [h for h in d.get("hyps", []) if t0 <= h["t"] <= t1]


out = {A: [], B: []}
print(f"medians over {t0:g}-{t1:g} Myr; 'f>7' = share of samples whose highest cell is above 7 km")
print(f"{'draw':32s} {'arm':5s} " + " ".join(f"{k:>8s}" for k in K) + "      f>7    f>6")
for pa in sorted(glob.glob(f"{root}/{A}_r*/seed*_L6.json.gz")):
    pb = pa.replace(f"/{A}_r", f"/{B}_r")
    if not os.path.exists(pb):
        continue
    tag = pa.split(f"/{A}_")[1].replace(".json.gz", "")
    for arm, p in ((A, pa), (B, pb)):
        r = rows(p)
        if not r:
            continue
        med = {k: float(np.median([h[k] for h in r])) for k in K}
        f7 = float(np.mean([h["max"] > 7000 for h in r])); f6 = float(np.mean([h["max"] > 6000 for h in r]))
        out[arm].append({**med, "f7": f7, "f6": f6, "top": max(h["max"] for h in r)})
        print(f"{tag:32s} {arm:5s} " + " ".join(f"{med[k]:8.2f}" for k in K) + f"  {f7:6.2f} {f6:6.2f}  top {out[arm][-1]['top']}")
for arm in (A, B):
    if out[arm]:
        print(f"== {arm} over {len(out[arm])} draws, median of draw medians: "
              + ", ".join(f"{k} {np.median([o[k] for o in out[arm]]):.2f}" for k in K + ("f7", "f6", "top")))
