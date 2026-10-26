"""usage: eqsun.py [WORLD] -> PW-808's first check: on the Earth world's model climate, the wet equatorial land's
(< 10 deg, > 2000 mm) cloud cover and sunshine share (climate.sunshine of it) against the observed: ICOADS/NCEP
cloud and CRU sunshine (tools/earth_data.earth_clouds). Also the subtropical and mid-latitude land for contrast.
Harness only."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from planet import climate, store as S, world as W  # noqa: E402
from tools.earth_data import earth_clouds  # noqa: E402

if len(sys.argv) > 1:
    path = S.find_world(sys.argv[1])
else:
    path = [p for p, e in S.items("world") if e.get("method") == "earth"][0]
w = W.load(path)
g, L = w["grid"], w["layers"]
obs = earth_clouds(g)
lat = np.asarray(g.lat)
land = L["elevation"] > 0 if "elevation" in L else L["land"].astype(bool)
rain = L["precipitation"]
print(f"world {path.name}; layers with cloud: {[k for k in L if 'cloud' in k or 'sun' in k]}")
for name, m in [("wet equatorial land (<10 deg, >2000 mm)", land & (np.abs(lat) < 10) & (rain > 2000)),
                ("all equatorial land (<10 deg)", land & (np.abs(lat) < 10)),
                ("subtropical land (20-35 deg)", land & (np.abs(lat) > 20) & (np.abs(lat) < 35)),
                ("mid-latitude land (40-60 deg)", land & (np.abs(lat) > 40) & (np.abs(lat) < 60))]:
    row = [f"{name}: {m.sum()} cells"]
    for h in ["jul", "jan"]:
        c = L[f"cloud_{h}"][m] / 100.0
        so = obs[f"obs_sun_{h}"][m]
        cn = obs[f"obs_cloud_ncep_{h}"][m]
        row.append(f"{h}: model cloud {np.nanmean(c):.2f} -> sunshine {np.nanmean(climate.sunshine(c)):.2f}; "
                   f"NCEP cloud {np.nanmean(cn):.2f}; CRU sunshine {np.nanmean(so):.2f} "
                   f"(sunshine() of NCEP cloud {np.nanmean(climate.sunshine(cn)):.2f})")
    print("\n  ".join(row))
