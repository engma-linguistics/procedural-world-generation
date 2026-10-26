"""usage: vegsun.py WORLD PCO2[:SHIFT] ... -> offline vegetation (vegetation.model, rain held; v1-finish-9's diag.py
method) on a stored world's climate, twice: the light from the raw cloud cover (as the plants get it now:
climate.months' sunshine(cloud)) and from the climate's own sunshine (climate.clouds' convective-aware
sunshine, the stored sunshine_* layers, given to the plants as the cloud sunshine() maps onto it). Harness only."""
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from planet import climate, store as S, vegetation as V  # noqa: E402
from planet.grid import build_grid  # noqa: E402

d = json.load(open(S.find_world(sys.argv[1])))
L = d["layers"]
g = build_grid(d["meta"]["level"])
A = lambda k: np.asarray(L[k], float)  # noqa: E731
el, tj, ta = A("elevation"), A("temperature_jul"), A("temperature_jan")
tw, tc = np.maximum(tj, ta), np.minimum(tj, ta)
ice, P = A("ice"), A("precipitation")
lat = np.abs(np.asarray(g.lat))
hj, ha = climate.day_hours(g.lat)
raw = (A("cloud_jul") / 100, A("cloud_jan") / 100)
sun = ((climate.SUN_CLEAR - A("sunshine_jul") / hj) / climate.SUN_CLOUD,
       (climate.SUN_CLEAR - A("sunshine_jan") / ha) / climate.SUN_CLOUD)
land0 = (el > 0) & (ice <= 0)
wq0 = land0 & (lat < 10) & (P > 2000)
print(f"{sys.argv[1]}: stored tree {A('tree_cover')[land0].mean():.1f}, wet-eq {A('tree_cover')[wq0].mean():.1f} "
      f"({wq0.sum()} cells); wet-eq sunshine share raw-cloud {climate.sunshine(raw[0][wq0]).mean():.2f} climate's "
      f"{climate.sunshine(sun[0][wq0]).mean():.2f}", flush=True)
for arg in sys.argv[2:]:
    pc, sh = (float(x) for x in (arg.split(":") + ["0"])[:2])
    for name, (cj, ca) in [("raw cloud", raw), ("climate sunshine", sun)]:
        t0 = time.time()
        m = V.model(g, el, A("temperature") + sh, tw + sh, tc + sh, A("precipitation_jul"), A("precipitation_jan"),
                    23.4, cj, ca, ice=ice, pco2=pc, cheap=False)
        tr = V.tree_cover(m["pot"], m["eq"]["nu"])
        la = m["land"]
        wq = la & (lat < 10) & (P > 2000)
        npp = m["sm"]["npp"] if "sm" in m else None
        print(f"  pco2 {pc:4.0f} dT {sh:+.0f} {name:>16}: tree {100 * tr[la].mean():5.1f}%  wet-eq {100 * tr[wq].mean():5.1f}%"
              + (f"  wet-eq npp {npp[wq].mean():5.0f}" if npp is not None else "") + f"  ({time.time() - t0:.0f}s)",
              flush=True)
