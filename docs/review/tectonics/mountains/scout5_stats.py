"""PW-1446 (b) scout 194: the two-tier bar's continuous parts for a paired judge, per set and pooled.
usage: scout5_stats.py ROOT[:ROLL,ROLL] [ROOT[:ROLL,...] ...] -> arms `main` and `cap` under each root (paired.sh layout),
only the listed rolls of each root (default all). Per set and pooled: late dT (judge.py's measure, mean dT 600-1000 Myr)
range and sd between draws for each arm, the paired cap - main mean with a bootstrap 95% CI (4000 resamples of draws),
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
    a, b = J.arm(root, "main", rolls), J.arm(root, "cap", rolls)
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
    for arm, v in (("main", a), ("cap", b)):
        print(f"  {arm:4s} late dT range {v.min():+.2f}..{v.max():+.2f} (inside -6..+5: {'yes' if v.min() >= -6 and v.max() <= 5 else 'NO'}), "
              f"sd {v.std(ddof=1):.2f}, mean {v.mean():+.2f}, median {np.median(v):+.2f}; <0: {(v < 0).sum()}, >+3: {(v > 3).sum()}")
    print(f"  paired cap - main late dT: mean {d.mean():+.2f} C (95% CI {lo:+.2f}..{hi:+.2f}), median {np.median(d):+.2f}, "
          f"up/down {(d > 0).sum()}/{(d < 0).sum()}")
    print(f"  soft pass main {pa}/{len(d)}, cap {pb}/{len(d)}; main only {ao}, cap only {bo}; McNemar exact p {mc:.3f}")
    print(f"  frozen over at the end main {fz[0]}, cap {fz[1]}; hellhouse main {hl[0]}, cap {hl[1]}")
    # Levene-type check of the spread (Brown-Forsythe on |x - median|), paired draws treated as two samples
    za, zb = np.abs(a - np.median(a)), np.abs(b - np.median(b))
    obs = zb.mean() - za.mean()
    pool = np.concatenate([za, zb]); n = len(za); cnt = 0
    for _ in range(4000):
        s = rng.permutation(pool)
        cnt += abs(s[n:].mean() - s[:n].mean()) >= abs(obs)
    print(f"  spread: mean |dev from median| main {za.mean():.2f}, cap {zb.mean():.2f}; permutation p {cnt / 4000:.3f}")


sets = [load_set(s) for s in sys.argv[1:]]
for s, spec in zip(sets, sys.argv[1:]):
    report(spec, s)
if len(sets) > 1:
    allp = {}
    for s in sets:
        allp.update(s)
    report("pooled", allp)
