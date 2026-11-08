"""PW-1331 scout 210b (copied from scout 194's scout5_stats.py, arms renamed): the two-tier bar's continuous parts for a
paired judge, per set and pooled, plus late cover read-outs (wet equatorial lowland trees, savanna/steppe trees).
usage: scout2b_stats.py ROOT[:ROLL,ROLL] [ROOT[:ROLL,...] ...] -> arms `main` and `cand` under each root (paired.sh layout),
only the listed rolls of each root (default all). Per set and pooled: late dT (judge.py's measure, mean dT 600-1000 Myr)
range and sd between draws for each arm, the paired cand - main mean with a bootstrap 95% CI (4000 resamples of draws),
pass counts and McNemar. Hard failures come from tools/hard_bar.py."""
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools import judge as J  # noqa: E402


def load_set(spec):
    root, _, rolls = spec.partition(":")
    rolls = rolls.split(",") if rolls else None
    a, b = J.arm(root, "main", rolls), J.arm(root, "cand", rolls)
    keys = sorted(set(a) & set(b))
    return {(root,) + k: (a[k], b[k]) for k in keys}


def report(name, pairs):
    a = np.array([p[0]["m"]["late dT"] for p in pairs.values()])
    b = np.array([p[1]["m"]["late dT"] for p in pairs.values()])
    d = b - a
    rng = np.random.default_rng(0)
    bm = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(4000)]
    lo, hi = np.percentile(bm, [2.5, 97.5])
    pa, pb = sum(p[0]["ok"] for p in pairs.values()), sum(p[1]["ok"] for p in pairs.values())
    ao = sum(p[0]["ok"] and not p[1]["ok"] for p in pairs.values())
    bo = sum(p[1]["ok"] and not p[0]["ok"] for p in pairs.values())
    nd = ao + bo
    mc = min(1.0, 2 * sum(math.comb(nd, i) for i in range(min(ao, bo) + 1)) / 2**nd) if nd else 1.0
    fz = [sum(p[i]["frozen"] for p in pairs.values()) for i in (0, 1)]
    hl = [sum(p[i]["hell"] for p in pairs.values()) for i in (0, 1)]
    print(f"== {name}: {len(d)} paired draws")
    for arm, v in (("main", a), ("cand", b)):
        print(f"  {arm:4s} late dT range {v.min():+.2f}..{v.max():+.2f} (inside -6..+5: {'yes' if v.min() >= -6 and v.max() <= 5 else 'NO'}), "
              f"sd {v.std(ddof=1):.2f}, mean {v.mean():+.2f}, median {np.median(v):+.2f}; <0: {(v < 0).sum()}, >+3: {(v > 3).sum()}")
    print(f"  paired cand - main late dT: mean {d.mean():+.2f} C (95% CI {lo:+.2f}..{hi:+.2f}), median {np.median(d):+.2f}, "
          f"up/down {(d > 0).sum()}/{(d < 0).sum()}")
    print(f"  soft pass main {pa}/{len(d)}, cand {pb}/{len(d)}; main only {ao}, cand only {bo}; McNemar exact p {mc:.3f}")
    print(f"  frozen over at the end main {fz[0]}, cand {fz[1]}; hellhouse main {hl[0]}, cand {hl[1]}")
    for key in ("wet_eq_trees", "savanna_trees", "steppe_trees", "trees", "bwh_pct", "arid_pct", "land_precip", "grass"):
        xa = np.array([J._mean(p[0]["ups"], key) for p in pairs.values()])
        xb = np.array([J._mean(p[1]["ups"], key) for p in pairs.values()])
        dd = xb - xa
        ok = ~np.isnan(dd)
        if not ok.any():
            continue
        clo, chi = J.boot_ci(dd[ok])
        print(f"  late {key}: main median {np.nanmedian(xa):.2f}, cand {np.nanmedian(xb):.2f}; paired median {np.median(dd[ok]):+.2f} "
              f"[{clo:+.2f}, {chi:+.2f}], mean {dd[ok].mean():+.2f}, up/down {(dd[ok] > 0).sum()}/{(dd[ok] < 0).sum()}, sign p {J.sign_p(list(dd[ok])):.3f}")
    # Levene-type check of the spread (Brown-Forsythe on |x - median|), paired draws treated as two samples
    za, zb = np.abs(a - np.median(a)), np.abs(b - np.median(b))
    obs = zb.mean() - za.mean()
    pool = np.concatenate([za, zb]); n = len(za); cnt = 0
    for _ in range(4000):
        s = rng.permutation(pool)
        cnt += abs(s[n:].mean() - s[:n].mean()) >= abs(obs)
    print(f"  spread: mean |dev from median| main {za.mean():.2f}, cand {zb.mean():.2f}; permutation p {cnt / 4000:.3f}")


sets = [load_set(s) for s in sys.argv[1:]]
for s, spec in zip(sets, sys.argv[1:]):
    report(spec, s)
if len(sets) > 1:
    allp = {}
    for s in sets:
        allp.update(s)
    report("pooled", allp)
