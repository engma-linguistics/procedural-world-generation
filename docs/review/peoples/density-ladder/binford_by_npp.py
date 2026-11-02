"""Lane 130 (PW-1275): Binford 2001 forager densities (D-PLACE dplace-dataset-binford, cldf/data.csv, var B008) against NPP.

NPP per society: the Miami model (Lieth 1975, as standardised in Adams, White & Lenton 2004, Ecol Model 177:353, App. A.1 and
Table B.3): 0.45 x min(3000/(1+exp(1.315-0.119T)), 3000(1-exp(-0.000664P))) g C/m2/yr, on D-PLACE ecoClimate mean temperature and
precipitation (dplace-data datasets/ecoClimate, baseline 1900-1949; ml/m2/month x 12 / 1000 = mm/yr). Usage:
python binford_by_npp.py DIR, DIR holding data.csv, societies.csv (dplace-dataset-binford cldf/) and eco_data.csv
(dplace-data datasets/ecoClimate/data.csv). A review tool, not part of the model.
"""
import csv, math, sys
import numpy as np
D = sys.argv[1]
vals = {}
for r in csv.DictReader(open(f"{D}/data.csv")):
    vals.setdefault(r["Soc_ID"], {})[r["Var_ID"]] = (r["Value"], r["Code_ID"])
eco = {}
for r in csv.DictReader(open(f"{D}/eco_data.csv")):
    if r["soc_id"].startswith("B"):
        eco.setdefault(r["soc_id"], {})[r["var_id"]] = float(r["code"])
soc = {r["ID"]: r for r in csv.DictReader(open(f"{D}/societies.csv"))}

def npp(T, Pmm):
    f1 = 3000 / (1 + math.exp(1.315 - 0.119 * T))
    f2 = 3000 * (1 - math.exp(-0.000664 * Pmm))
    return 0.45 * min(f1, f2)

rows = []
for s, v in vals.items():
    if "B008" not in v:
        continue
    try:
        d = float(v["B008"][0])
    except ValueError:
        continue
    dom = v.get("B004", ("", ""))[0]
    norm = v.get("B005", ("", ""))[0]
    mob = v.get("B009", ("", ""))[0]
    fish = float(v["B003"][0]) if "B003" in v and v["B003"][0] not in ("", "NA") else float("nan")
    e = eco.get(s)
    n = npp(e["AnnualMeanTemperature"], e["MonthlyMeanPrecipitation"] * 12 / 1000) if e else float("nan")
    lat = float(soc[s]["Latitude"]) if s in soc and soc[s]["Latitude"] else float("nan")
    rows.append((s, d, dom, norm, mob, fish, n, lat))
print("n with density", len(rows), "with npp", sum(not math.isnan(r[6]) for r in rows))
def q(xs, label):
    xs = np.array(xs)
    if len(xs) == 0:
        return
    print(f"{label:<44} n={len(xs):3d} p10={np.percentile(xs,10):.3f} p25={np.percentile(xs,25):.3f} med={np.median(xs):.3f} p75={np.percentile(xs,75):.3f} p90={np.percentile(xs,90):.3f} max={xs.max():.2f}")
q([r[1] for r in rows], "all")
print("B004 values", set(r[2] for r in rows), "B005", set(r[3] for r in rows), "B009", set(r[4] for r in rows))
for k in sorted(set(r[2] for r in rows)):
    q([r[1] for r in rows if r[2] == k], f"dominant={k}")
for k in sorted(set(r[4] for r in rows)):
    q([r[1] for r in rows if r[4] == k], f"mobility={k}")
for k in sorted(set(r[3] for r in rows)):
    q([r[1] for r in rows if r[3] == k], f"B005={k}")
q([r[1] for r in rows if r[5] >= 50], "fishing >=50%")
q([r[1] for r in rows if r[5] >= 50 and r[4] == "2"], "fishing >=50% and sedentary")
q([r[1] for r in rows if abs(r[7]) >= 55], "|lat|>=55")
# by NPP bins, terrestrial (fishing < 30%)
terr = [r for r in rows if not math.isnan(r[6]) and (math.isnan(r[5]) or r[5] < 30)]
for lo, hi in [(0, 150), (150, 300), (300, 450), (450, 600), (600, 1400)]:
    q([r[1] for r in terr if lo <= r[6] < hi], f"terrestrial, NPP {lo}-{hi} gC/m2/yr")
x = np.log10([r[6] for r in terr if r[6] > 0 and r[1] > 0]); y = np.log10([r[1] for r in terr if r[6] > 0 and r[1] > 0])
b, a = np.polyfit(x, y, 1); rr = np.corrcoef(x, y)[0, 1]
print(f"terrestrial log10 dens = {a:.3f} + {b:.3f} log10 NPP  (r={rr:.2f}, n={len(x)})")
for N in (100, 200, 330, 500, 800):
    print(f"  fit at NPP {N}: {10**(a + b*math.log10(N)):.3f}")
# quantile regression-ish: upper quartile per bin already above
allf = [r for r in rows if not math.isnan(r[6]) and r[1] > 0 and r[6] > 0]
x = np.log10([r[6] for r in allf]); y = np.log10([r[1] for r in allf])
b, a = np.polyfit(x, y, 1); print(f"all log10 dens = {a:.3f} + {b:.3f} log10 NPP (r={np.corrcoef(x,y)[0,1]:.2f}, n={len(x)})")
