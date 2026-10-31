"""How much of ln src variance is fast: cross-draw sd of the last-W mean for several W; within-run sd after
removing running means; and the ridge/arc/plume parts if derivable (plume_src)."""
import gzip, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from an import DRAWS, J, H  # noqa
arm = sys.argv[1]
Ws = (4, 10, 20, 50, 100)
last = {w: [] for w in Ws}; lastT = []; fast = {w: [] for w in (10, 30, 60)}; lag1 = []; plume = []
for tag, seed in DRAWS:
    raw = json.load(gzip.open(J / f"{arm}_r0.0005_{tag}" / f"seed{seed}_L6.json.gz")); st = [r for r in raw["steps"] if r["t"] > 0]
    t = np.array([r["t"] for r in st]); s = np.log(np.array([r["src"] for r in st])); end = t[-1]
    T = np.array([r["true_temp_c"] for r in st])
    for w in Ws:
        last[w].append(s[t >= end - w].mean())
    # regular 2 Myr grid 520-980
    tg = np.arange(520, 980, 2.0); sg = np.interp(tg, t, s); Tg = np.interp(tg, t, T)
    for w in fast:
        k = int(w / 2); rm = np.convolve(sg, np.ones(k) / k, mode="same")
        fast[w].append(np.std((sg - rm)[k:-k]))
    lag1.append([np.corrcoef(sg[:-L], sg[L:])[0, 1] for L in (1, 2, 5, 10, 25)])
    plume.append(np.mean([r["plume_src"] / max(r["source_raw"], 1e-9) for r in st if r["t"] > 520]))
for w in Ws:
    print(f"last {w:3d} Myr mean ln src: cross-draw sd {np.std(last[w]):.3f} median {np.median(last[w]):+.3f}")
for w in fast:
    print(f"within-run sd of ln src about its {w} Myr running mean: median {np.median(fast[w]):.3f}")
print("autocorr at lag 2,4,10,20,50 Myr (median):", np.round(np.median(lag1, 0), 2))
print("plume share of source (median):", round(float(np.median(plume)), 3))
