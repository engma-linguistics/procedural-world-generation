"""compare.py MAIN_DIR LANE_DIR: the paired PW-1024 sweep tables (probe.py OUT.json + --save dirs), per arm and paired by run."""
import json
import sys
from collections import defaultdict
from pathlib import Path
import numpy as np

EST = 0.12
DR = ("red", "blue", "green", "black", "white", "gold", "silver", "bronze", "copper", "brass")
A, B = Path(sys.argv[1]), Path(sys.argv[2])
runs = sorted(set(p.stem for p in A.glob("*.json")) & set(p.stem for p in B.glob("*.json")))
print(f"paired runs: {len(runs)}: {', '.join(runs)}")


def rich_occ(d, run, e):
    f = d / run / "ERAS.npz"
    if not f.exists():
        return None
    z = np.load(f)
    land = z["land_" + e]; allp = sum(z[f"people_{c}_{e}"] for c in ("foragers", "herders", "farmers", "others"))
    m = land & (allp < 0.02) & (z["prey_" + e] >= 3)
    mr = land & (z["prey_" + e] >= 3)
    d_ = z["dragons_" + e]
    return (float((d_[m] > 1e-9).mean()) if m.any() else float("nan"), int(m.sum()), float((d_[mr] > 1e-9).mean()))


def arm(d):
    out = {}
    for run in runs:
        r = json.loads((d / f"{run}.json").read_text())
        z = np.load(d / run / "RUN.npz", allow_pickle=False)
        pres = json.loads(str(z["pres"]))
        mf = pres.get("megafauna", {})
        by_country = defaultdict(int)
        for lid, x in mf.items():
            if lid.endswith("_dragon"):
                for p in x["pocket_list"]:
                    by_country[p["country"]] += p["count"]
        ids = [str(x) for x in z["ids"]]
        cells = {lid: int((z["P"][ids.index(lid)] >= EST).sum()) for lid in ids if lid.endswith("_dragon") or lid.endswith("_giant")}
        out[run] = {"peoples": r["peoples"], "count": r["mf_count"], "cov": r["mf_cov"], "by_country": dict(by_country), "cells": cells,
                    "occ0": rich_occ(d, run, "0"), "occ25": rich_occ(d, run, "25"), "present": r["present"]}
    return out


M, L = arm(A), arm(B)
for nm, X in (("main", M), ("lane", L)):
    cells = [c for r in X.values() for c in r["peoples"].values()]
    print(f"\n== {nm}: per-people pass {sum(c >= 300 for c in cells)}/{len(cells)} = {np.mean([c >= 300 for c in cells]):.1%}; "
          f"remnants (<100) {sum(c < 100 for c in cells)} (absent {sum(c == 0 for c in cells)})")
    print(f"   dragons per run {np.mean([r['present']['dragons'] for r in X.values()]):,.0f}; giants per run {np.mean([r['present']['giants'] for r in X.values()]):,.0f}")
    o0 = [r["occ0"] for r in X.values() if r["occ0"]]; o25 = [r["occ25"] for r in X.values() if r["occ25"]]
    print(f"   rich empty land occupied (any dragon), now {np.nanmean([o[0] for o in o0]):.2f} (mean {np.mean([o[1] for o in o0]):.0f} cells), "
          f"25 kyr {np.nanmean([o[0] for o in o25]):.2f}; all rich land occupied now {np.mean([o[2] for o in o0]):.2f}, 25 kyr {np.mean([o[2] for o in o25]):.2f}")
print("\n== dragons by kind (count per run; cells held per run; target share of its country reached), main -> lane")
for k in DR:
    lid = k + "_dragon"
    f = lambda X, key: np.mean([X[r][key].get(lid, 0) or 0 for r in runs])
    g = lambda X: np.mean([(X[r]["cov"].get(lid) or 0) for r in runs])
    absent = lambda X: sum((X[r]["count"].get(lid, 0) or 0) == 0 for r in runs)
    print(f"  {lid:>14}: {f(M, 'count'):8,.0f} -> {f(L, 'count'):8,.0f}   cells {f(M, 'cells'):7,.0f} -> {f(L, 'cells'):7,.0f}   "
          f"target {g(M):.2f} -> {g(L):.2f}   runs without {absent(M)} -> {absent(L)}")
print("\n== giants by kind (count per run; cells)")
gl = sorted({lid for X in (M, L) for r in X.values() for lid in r["count"] if lid.endswith("giant")})
for lid in gl:
    f = lambda X, key: np.mean([X[r][key].get(lid, 0) or 0 for r in runs])
    print(f"  {lid:>14}: {f(M, 'count'):8,.0f} -> {f(L, 'count'):8,.0f}   cells {f(M, 'cells'):7,.0f} -> {f(L, 'cells'):7,.0f}")
print("\n== dragons by country (per run)")
cs = sorted({c for X in (M, L) for r in X.values() for c in r["by_country"]}, key=lambda c: -np.mean([M[r]["by_country"].get(c, 0) for r in runs]))
for c in cs:
    a, b = (np.mean([X[r]["by_country"].get(c, 0) for r in runs]) for X in (M, L))
    print(f"  {c:>16}: {a:8,.0f} -> {b:8,.0f}")
print("\n== paired per run: dragons, rich empty occupancy, per-people pass")
for r in runs:
    pm = np.mean([c >= 300 for c in M[r]["peoples"].values()]); pl = np.mean([c >= 300 for c in L[r]["peoples"].values()])
    om, ol = (X[r]["occ0"][0] if X[r]["occ0"] else float("nan") for X in (M, L))
    print(f"  {r}: dragons {M[r]['present']['dragons']:7,} -> {L[r]['present']['dragons']:7,}; occ {om:.2f} -> {ol:.2f}; pass {pm:.0%} -> {pl:.0%}")
peo = sorted({lid for X in (M, L) for r in X.values() for lid in X[r]["peoples"]} if False else {lid for r in runs for lid in M[r]["peoples"]})
print("\n== per-people pass by people, main -> lane (runs passing of", len(runs), ")")
diff = []
for lid in peo:
    a = sum(M[r]["peoples"].get(lid, 0) >= 300 for r in runs); b = sum(L[r]["peoples"].get(lid, 0) >= 300 for r in runs)
    if a != b:
        diff.append(f"{lid} {a}->{b}")
print("  changed: " + (", ".join(diff) or "none"))
