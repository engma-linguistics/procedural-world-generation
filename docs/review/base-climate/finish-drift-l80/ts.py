"""Bin time series across draws: median and sd of ln src, ln supply/ref(250-300), land, T, iced land; plus per-draw last-60 Myr."""
import gzip, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from an import DRAWS, J, H  # noqa
arm = sys.argv[1]
show = sys.argv[2:]  # draws to print in detail, "tag:seed"
bins = list(range(300, 1001, 50))
tab = {k: [] for k in ("src", "sup", "land", "T", "ice", "pl")}
for tag, seed in DRAWS:
    raw = json.load(gzip.open(J / f"{arm}_r0.0005_{tag}" / f"seed{seed}_L6.json.gz")); st = [r for r in raw["steps"] if r["t"] > 0]
    t = np.array([r["t"] for r in st]); g = lambda k: np.array([r.get(k) if r.get(k) is not None else np.nan for r in st], float)
    sup = g("w_supply"); s0 = np.nanmean(sup[(t >= 250) & (t < 300)])
    ser = dict(src=np.log(g("src")), sup=np.log(sup / s0), land=g("land"), T=g("true_temp_c") - H.PREIND_T, ice=g("iced_land"),
               pl=np.log(g("w_plant")))
    for k, v in ser.items():
        tab[k].append([np.nanmean(v[(t >= a) & (t < a + 50)]) for a in bins[:-1]])
    if f"{tag}:{seed}" in show:
        print(f"--- {tag} {seed}")
        for a in range(int(t[-1]) - 80, int(t[-1]) + 1, 4):
            i = (t >= a) & (t < a + 4)
            if i.any():
                r = st[np.where(i)[0][-1]]
                print(f"{r['t']:7.1f} T {r['true_temp_c']-H.PREIND_T:+5.1f} lnsrc {np.log(r['src']):+.2f} lnsink {np.log(r['sink']):+.2f} lnsup {np.log(r['w_supply']/s0):+.2f} "
                      f"co2 {r['co2']:+.2f} co2t {r['co2_term']:+.1f} alb {r['albedo_term']:+.1f} drift {r['drift']:+.2f} ice {r['iced_land'] or 0:.2f} wT {r.get('w_T') or 0:.1f} land {r['land']:.3f}")
print("bin start  " + " ".join(f"{a:6d}" for a in bins[:-1]))
for k, v in tab.items():
    v = np.array(v)
    print(f"{k:5} med  " + " ".join(f"{x:+6.2f}" for x in np.nanmedian(v, 0)))
    print(f"{k:5} sd   " + " ".join(f"{x:6.2f}" for x in np.nanstd(v, 0)))
