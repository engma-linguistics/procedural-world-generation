"""Regress the finish T on the forcing parts: ln src, ln supply (vs 250-300), geography (w_temp), plants, over windows."""
import gzip, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from an import DRAWS, J, H  # noqa
arm = sys.argv[1]
W = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
X, Y, names = [], [], []
for tag, seed in DRAWS:
    raw = json.load(gzip.open(J / f"{arm}_r0.0005_{tag}" / f"seed{seed}_L6.json.gz")); st = [r for r in raw["steps"] if r["t"] > 0]
    t = np.array([r["t"] for r in st]); g = lambda k: np.array([r.get(k) if r.get(k) is not None else np.nan for r in st], float)
    end = t[-1]; i0 = (t >= 250) & (t < 300); i1 = t >= end - W
    sup = g("w_supply"); rate = g("w_rate"); area = g("w_area")
    row = [np.nanmean(np.log(g("src"))[i1]), np.log(np.nanmean(sup[i1]) / np.nanmean(sup[i0])),
           np.log(np.nanmean(rate[i1]) / np.nanmean(rate[i0])), np.log(np.nanmean(area[i1]) / np.nanmean(area[i0])),
           np.nanmean(g("albedo_term")[i1]), np.nanmean(g("drift")[i1])]
    X.append(row); Y.append(st[-1]["true_temp_c"] - H.PREIND_T); names.append(f"{tag} {seed}")
X, Y = np.array(X), np.array(Y)
print("cols: lnsrc lnsup lnrate lnarea alb drift")
print("corr(lnsrc, lnsup) across draws:", round(np.corrcoef(X[:, 0], X[:, 1])[0, 1], 2), " corr(lnrate,lnsup)", round(np.corrcoef(X[:, 2], X[:, 1])[0, 1], 2))
F = X[:, 0] - X[:, 1]
print(f"F = lnsrc - lnsup: median {np.median(F):+.2f} sd {F.std():.2f}; src sd {X[:,0].std():.2f}, sup sd {X[:,1].std():.2f}")
for cols, lab in (([0], "src"), ([1], "sup"), ([0, 1], "src+sup"), ([0, 1, 4], "src+sup+alb")):
    A = np.c_[X[:, cols], np.ones(len(Y))]
    c, res, *_ = np.linalg.lstsq(A, Y, rcond=None)
    pred = A @ c; r2 = 1 - ((Y - pred) ** 2).sum() / ((Y - Y.mean()) ** 2).sum()
    print(f"{lab:12} coef {np.round(c, 2)} R2 {r2:.2f}")
A = np.c_[F, np.ones(len(Y))]; c, *_ = np.linalg.lstsq(A, Y, rcond=None); r2 = 1 - ((Y - A @ c) ** 2).sum() / ((Y - Y.mean()) ** 2).sum()
print(f"F alone coef {np.round(c, 2)} R2 {r2:.2f}")
for n, x, y in sorted(zip(names, X, Y), key=lambda z: z[2]):
    print(f"{n:14} endT {y:+5.1f} lnsrc {x[0]:+.2f} lnsup {x[1]:+.2f} (rate {x[2]:+.2f} area {x[3]:+.2f}) F {x[0]-x[1]:+.2f} alb {x[4]:+.1f}")
