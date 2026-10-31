"""The supply step at the plants' arrival: per draw, ln supply and ln erosion rate 40 Myr before vs after the first
w_plant > 1.05 step, and ln src over the same (control)."""
import gzip, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from an import DRAWS, J  # noqa
arm = sys.argv[1]
out = []
for tag, seed in DRAWS:
    raw = json.load(gzip.open(J / f"{arm}_r0.0005_{tag}" / f"seed{seed}_L6.json.gz")); st = [r for r in raw["steps"] if r["t"] > 0]
    t = np.array([r["t"] for r in st]); g = lambda k: np.array([r.get(k) if r.get(k) is not None else np.nan for r in st], float)
    pl = g("w_plant"); t0 = t[np.argmax(pl > 1.05)]
    b, a = (t >= t0 - 40) & (t < t0), (t >= t0 + 10) & (t < t0 + 50)
    r = [np.log(np.nanmean(g(k)[a]) / np.nanmean(g(k)[b])) for k in ("w_supply", "w_rate", "w_area")] + [np.nanmean(np.log(g("src"))[a]) - np.nanmean(np.log(g("src"))[b])]
    out.append(r); print(f"{tag} {seed}: plants at {t0:.0f}; dln supply {r[0]:+.2f} rate {r[1]:+.2f} area {r[2]:+.2f} | src {r[3]:+.2f}")
o = np.array(out); print("median", np.round(np.median(o, 0), 3), "mean", np.round(o.mean(0), 3), "sd", np.round(o.std(0), 3))
