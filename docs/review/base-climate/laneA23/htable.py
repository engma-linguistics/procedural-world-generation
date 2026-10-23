"""usage: htable.py LABEL=report.md[:frames.json.gz] ... -- lane A23's health comparison (PW-646).

Per sweep: the per-seed columns that carry the ice finding (dT range, % of keyframes with ice sea level below
-150 m, the old and new ice bars, icehouse %), the counts, and, where the sweep's frames are given, the run's CO2
as ppm (climate.pco2: 350 x e^co2) at 5/50/95% and the share of keyframes below 124 ppm (where the plants' CO2
responses are held, vegetation.CO2_RANGE) and below 150 ppm."""
import gzip
import json
import sys

import numpy as np


def table(path):
    rows = {}
    for line in open(path):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) == 15 and c[0].isdigit():
            rows[int(c[0])] = dict(dT=c[6], deep=float(c[10]), old=c[12], new="ok" if c[13] == "ok" else "F",
                                   why=c[13], ice=float(c[14]))
    return rows


def ppm(frames):
    d = json.load(gzip.open(frames))
    v = [f["co2"] for run in d.values() for f in run if isinstance(f, dict) and f.get("co2") is not None]
    p = 350.0 * np.exp(np.array(v))
    return (f"ppm 5/50/95% {np.percentile(p, 5):.0f}/{np.percentile(p, 50):.0f}/{np.percentile(p, 95):.0f}; "
            f"<124 ppm {100 * np.mean(p < 124):.1f}% <150 ppm {100 * np.mean(p < 150):.1f}% of {len(p)} keyframes")


for arg in sys.argv[1:]:
    label, rest = arg.split("=", 1)
    rep, _, fr = rest.partition(":")
    t = table(rep)
    deep = [s for s, r in t.items() if r["deep"] > 10]
    print(f"## {label} ({rep})")
    print("seed | dT range | ice SL<-150 m % | old bar | new bar | icehouse %")
    for s, r in sorted(t.items()):
        print(f"{s} | {r['dT']} | {r['deep']:.1f} | {r['old']} | {r['new']} | {r['ice']:.1f}")
    print(f"seeds with >10% of keyframes below -150 m: {len(deep)} {deep}; old bar F {sum(r['old'] != 'ok' for r in t.values())};"
          f" new bar F {sum(r['new'] != 'ok' for r in t.values())}; median icehouse "
          f"{np.median([r['ice'] for r in t.values()]):.1f}%")
    if fr:
        print(ppm(fr))
    print()
