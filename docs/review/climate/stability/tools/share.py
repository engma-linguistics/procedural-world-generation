"""Lane 158: which terms carry the forked nulls' dT difference? Paired differences (fn, fn2 minus fm; 6 draws each,
lane 144), 10 Myr means over 400-1000 Myr. The climate's target is co2_term - albedo + ghg + star (star the same
in both arms). Share of var(d target) from each term: cov(d term, d target) / var(d target) (they add to 1).
co2_term's part is split by the carbon balance, ln X ~ (ln src - ln sink@X=1) / a, with ln sink@X=1 = ln supply +
ln plant + ln temp-factor: cov of each with d co2_term over var(d target), times the sign it enters with."""
import gzip, json
import numpy as np
from decomp import L, six, rec

K = {"co2_term": lambda x: x["co2_term"], "albedo": lambda x: x["albedo_term"], "ghg": lambda x: x["ghg"],
     "target": lambda x: x["co2_term"] + x["albedo_term"] + x["ghg"],
     "ln src": lambda x: np.log(x["src"]), "-ln supply": lambda x: -np.log(x["w_supply"]),
     "-ln plant": lambda x: -np.log(x["w_plant"]), "-ln temp": lambda x: -np.log(x["w_temp"]),
     "dT": lambda x: x["dT"], "ice": lambda x: x["iced_land_pct"]}
D = {k: [] for k in K}
for arm in ("n", "n2"):
    for r, tag, s in six:
        A, B = rec(arm, r, tag, s), rec("m", r, tag, s)
        for a in range(400, 1000, 10):
            ts = [t for t in A if a < t <= a + 10 and t in B]
            for k, f in K.items():
                D[k].append(np.mean([f(A[t]) - f(B[t]) for t in ts]))
D = {k: np.array(v) for k, v in D.items()}
v = D["target"].var()
print(f"n = {len(D['target'])} paired 10 Myr means; sd d target {np.sqrt(v):.2f} C, sd d dT {D['dT'].std():.2f} C")
for k in ("co2_term", "albedo", "ghg"):
    print(f"  share of var(d target) from {k:>9}: {np.cov(D[k], D['target'])[0, 1] / v:+.2f}")
# the carbon balance's drivers, as their projection on d target (each through co2_term: d lnX ~ d(ln src - ln sink)/a)
tot = D["ln src"] + D["-ln supply"] + D["-ln plant"] + D["-ln temp"]
print(f"  corr(d(ln src - ln sink@1), d co2_term) = {np.corrcoef(tot, D['co2_term'])[0, 1]:.2f}; sd of the parts:")
for k in ("ln src", "-ln supply", "-ln plant", "-ln temp"):
    print(f"    {k:>10}: sd {D[k].std():.3f}, share of var(d(ln src - ln sink@1)) {np.cov(D[k], tot)[0, 1] / tot.var():+.2f}")
print(f"  corr(d ln src, d dT) {np.corrcoef(D['ln src'], D['dT'])[0, 1]:.2f}; corr(d ice, d dT) {np.corrcoef(D['ice'], D['dT'])[0, 1]:.2f}")
b = np.polyfit(D["ln src"], D["dT"], 1)[0]
print(f"  d dT per unit d ln src (OLS): {b:.1f} C; d ice per C of d dT: {np.polyfit(D['dT'], D['ice'], 1)[0]:.2f} pts")
