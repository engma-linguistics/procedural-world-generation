"""split.py JUDGE : late (600-1000 Myr) dT of cand - main split into the target's parts, plus the ice and rain."""
import gzip, json, sys, glob
import numpy as np
J = sys.argv[1]
K = ["dT", "target", "co2", "co2_term", "albedo_term", "ghg", "ice_frac", "sea_ice", "w_T"]
U = ["temp", "precip", "land_precip", "precip_ice", "snow_land", "acc", "melt", "sea", "arid_pct"]
def load(p):
    d = json.load(gzip.open(p))
    late = [r for r in d["steps"] if 600 <= r["t"] < 1000 and abs(r["t"] - round(r["t"])) < 1e-9]
    ups = [u for u in d["updates"] if 600 <= u["t"] < 1000 and "budget" in u]
    for u in ups:
        u.update(u["budget"])
    s = {k: float(np.mean([r[k] for r in late if r.get(k) is not None])) for k in K}
    s.update({k: float(np.mean([u[k] for u in ups])) for k in U})
    s["iced%"] = 100 * float(np.mean([r["sea_ice"] < -20 for r in late]))
    return s
KK = K + U + ["iced%"]
rows = []
for f in sorted(glob.glob(f"{J}/main_*/*.json.gz")):
    g = f.replace("/main_", "/cand_")
    try:
        a, b = load(f), load(g)
    except FileNotFoundError:
        continue
    print(f.split("/")[-2][5:], f.split("/")[-1][:12])
    print("   " + " ".join(f"{k[:9]:>9}" for k in KK))
    for n, x in (("A", a), ("B", b)):
        print(f"{n:>3}" + " ".join(f"{x[k]:9.3f}" for k in KK))
    print("B-A" + " ".join(f"{b[k]-a[k]:+9.3f}" for k in KK))
