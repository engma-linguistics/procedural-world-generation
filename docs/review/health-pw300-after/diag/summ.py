"""python summ.py <health dir> [...]: lake and inland summary over 8 L6 seeds, frames after 50 Myr."""
import gzip
import json
import re
import sys

for D in sys.argv[1:]:
    sw = json.load(open(D + "/sweep.json"))
    fr = json.load(gzip.open(D + "/frames.json.gz"))
    runs = [[x for x in fr[r["id"]] if x["t"] > 50] for r in sw["results"][:8]]
    F = [x for f in runs for x in f]
    n = len(F)
    lm = lambda x: x["lake_max_mkm2"] or 0
    g = sum(lm(x) > 1 for x in F)
    gi = sum(lm(x) > 1 and (x["sea_ice_m"] or 0) < -60 for x in F)
    g2 = sum(lm(x) > 2 for x in F)
    lp = sorted(x["lake_pct"] or 0 for x in F)
    inl = sorted(x["inland_pct"] for x in F if x["inland_pct"] is not None)
    pr = [100 * sum(lm(x) > 1 for x in f) / len(f) for f in runs]
    sp = re.search(r"of (\d+) spells", open(D + "/report.md").read())
    print(f"{D.rstrip('/').split('/')[-1]:22s} giant {100 * g / n:.1f}% ({g}; ice-age {gi}) >2: {g2}  runs>5%: "
          f"{sum(p > 5 for p in pr)} {[round(p) for p in pr]}  mean big {sum(map(lm, F)) / n:.2f}  lake_pct med "
          f"{lp[n // 2]:.2f} <0.2: {100 * sum(v < 0.2 for v in lp) / n:.0f}%  inland med {inl[len(inl) // 2]:.1f} "
          f"p90 {inl[int(.9 * len(inl))]:.1f} max {inl[-1]:.1f} >30: {sum(v > 30 for v in inl)}  spells {sp.group(1)}")
