"""Finish-window bias check: per draw, ln src / ln sink / T / co2 in the window (last 10 Myr) against the 20 Myr
before it, and step lengths there."""
import gzip, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from an import DRAWS, J, H  # noqa
arm = sys.argv[1]
D = {k: [] for k in ("src", "sink", "T", "co2", "sup", "srcmean")}
for tag, seed in DRAWS:
    raw = json.load(gzip.open(J / f"{arm}_r0.0005_{tag}" / f"seed{seed}_L6.json.gz")); st = [r for r in raw["steps"] if r["t"] > 0]
    t = np.array([r["t"] for r in st]); end = t[-1]
    win = t > end - 10 + 1e-6; pre = (t > end - 30) & (t <= end - 10 + 1e-6); pre2 = (t > end - 50) & (t <= end - 30)
    g = lambda k: np.array([r[k] for r in st], float)
    dts = np.diff(t)
    for k, v in (("src", np.log(g("src"))), ("sink", np.log(g("sink"))), ("T", g("true_temp_c")), ("co2", g("co2")), ("sup", np.log(g("w_supply")))):
        D[k].append((v[win].mean() - v[pre].mean(), v[pre].mean() - v[pre2].mean()))
    D["srcmean"].append((np.log(g("src")[win].mean()) - np.log(g("src")[pre].mean()), 0))
    if tag == "l6fix" and seed == 957317:
        print("steps in window:", np.round(dts[-25:], 2), " n window", win.sum(), " n pre", pre.sum())
        print("src last 30 values:", np.round(g("src")[-30:], 2))
for k, v in D.items():
    v = np.array(v)
    print(f"{k:7} window-minus-prev20 median {np.median(v[:,0]):+.3f} mean {v[:,0].mean():+.3f} sd {v[:,0].std():.3f} | control (prev20 - the 20 before) median {np.median(v[:,1]):+.3f} mean {v[:,1].mean():+.3f}")
