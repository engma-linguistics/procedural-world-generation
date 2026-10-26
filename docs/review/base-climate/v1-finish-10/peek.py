"""usage: peek.py DIAG.json.gz [EVERY] -- a run's climate updates every EVERY-th: t, dT, true mean T, pCO2,
land ice (m of sea level), tree cover over land and over the wet equatorial lowland (%)."""
import gzip
import json
import sys

d = json.load(gzip.open(sys.argv[1]))
k = int(sys.argv[2]) if len(sys.argv) > 2 else 25
print("t dT meanT pco2 sea_ice trees wet_eq")
for r in d["updates"][::k] + d["updates"][-1:]:
    print(r["t"], r["dT"], r["temp"], r.get("pco2"), r["sea_ice"], r.get("trees"), r.get("wet_eq_trees"))
