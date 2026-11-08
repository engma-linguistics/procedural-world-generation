"""PW-1446 scout 193: exact covariance split of the late carbon balance across draws, per arm, with a paired bootstrap.

    uv run python docs/review/tectonics/mountains/scout4_decomp.py table.json

net = ln source_raw - ln w_supply - ln w_plant - ln w_temp (= ln co2_law(X) + YARDSTICK each step, so its spread is
what the CO2 must absorb). var(net) = sum_i cov(net, part_i): each part's share of the spread. Likewise var(dT) over
co2_term, albedo_term, ghg and the rest. The bootstrap resamples draws (paired: the same draws in both arms) for the
cap - main difference of each share, of corr(ln source, ln supply), and of the late-dT sd.
"""
import json
import sys

import numpy as np

rows = [r for r in json.load(open(sys.argv[1])) if r["draw"].split("_")[0] in ("r0.0005", "r0.001")]
A = {r["draw"]: r for r in rows if r["arm"] == "main"}
B = {r["draw"]: r for r in rows if r["arm"] == "cap"}
ds = sorted(set(A) & set(B))


def parts(D, i):
    def g(k):
        return np.array([D[ds[j]][k] for j in i])

    def cv(x, y):
        return float(np.cov(x, y)[0, 1])

    src, sup, pl, tm = g("ln_source_raw"), g("ln_w_supply"), g("ln_w_plant"), g("ln_w_temp")
    net = src - sup - pl - tm
    out = {"sd net": float(net.std(ddof=1)), "net<-src": cv(net, src), "net<-sup": cv(net, -sup),
           "net<-plant": cv(net, -pl), "net<-temp": cv(net, -tm), "r(src,sup)": float(np.corrcoef(src, sup)[0, 1]),
           "sd src-sup": float((src - sup).std(ddof=1))}
    dT = g("dT")
    rest = dT - g("co2_term") - g("albedo_term") - g("ghg")
    out.update({"sd dT": float(dT.std(ddof=1)), "dT<-co2": cv(dT, g("co2_term")), "dT<-albedo": cv(dT, g("albedo_term")),
                "dT<-ghg": cv(dT, g("ghg")), "dT<-rest": cv(dT, rest),
                "slope temp/dT": float(np.polyfit(dT, tm, 1)[0]), "slope co2/net": float(np.polyfit(net, g("co2"), 1)[0]),
                "slope alb/dT": float(np.polyfit(dT, g("albedo_term"), 1)[0])})
    return out


full = np.arange(len(ds))
a, b = parts(A, full), parts(B, full)
rng = np.random.default_rng(1)
boot = []
for _ in range(4000):
    i = rng.integers(0, len(ds), len(ds))
    pa, pb = parts(A, i), parts(B, i)
    boot.append({k: pb[k] - pa[k] for k in a})
print(f"{len(ds)} paired draws\n{'':16s} {'main':>9s} {'cap':>9s} {'cap-main':>9s}  95% paired bootstrap")
for k in a:
    v = np.array([x[k] for x in boot])
    lo, hi = np.percentile(v, [2.5, 97.5])
    print(f"{k:16s} {a[k]:9.4f} {b[k]:9.4f} {b[k] - a[k]:9.4f}  [{lo:.4f}, {hi:.4f}]")
