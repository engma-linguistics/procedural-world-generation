"""Lane 132: the model's sea air vs SST by sea box and half-year (Earth L6): what a marine layer's air would be."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa
import numpy as np
from planet import climate, vegetation
from planet.grid import build_grid
from tools import earth_data
from tools.moisture_regions import SEA_BOXES, box_mask

rec = []
orig = climate._season_inputs
def spy(grid, elev, t_air, sst, *a, **k):
    rec.append((np.array(t_air), np.array(sst)))
    return orig(grid, elev, t_air, sst, *a, **k)
climate._season_inputs = spy
g = build_grid(int(sys.argv[1]) if len(sys.argv) > 1 else 6)
d = earth_data.earth_on_grid(g)
elev, ice = d["elev"].astype(float), d["ice"].astype(float)
c, _ = vegetation.coupled_climate(g, elev, 0.0, 23.4, ice)
sea = ~earth_data.land_of(d)
w = earth_data.cell_areas(g)
(ta_j, ss_j), (ta_n, ss_n) = rec[-2], rec[-1]
qk = climate.TUNE["q_k"]
hk = climate.TUNE["hk"]
om, ow, oc = d["obs_temp"], d["obs_t_warm"], d["obs_t_cold"]
nh = g.lat > 0
o_j = np.where(nh, om + hk * (ow - om), om - hk * (om - oc))  # NCEP 2 m air, half-year means
o_n = np.where(nh, om - hk * (om - oc), om + hk * (ow - om))
for name, a, b, lo, hi, _k in SEA_BOXES:
    m = box_mask(g, sea, a, b, lo, hi, "sea")
    f = lambda x: float((x * w)[m].sum() / w[m].sum())
    nj = a > 0
    for lab, ta, ss, ob in (("Jul", ta_j, ss_j, o_j), ("Jan", ta_n, ss_n, o_n)):
        fin = c["t_warm"] if (lab == "Jul") == (a > 0) else c["t_cold"]
        fin = c["temp"] + hk * (fin - c["temp"])
        print(f"{name:24s} {lab}: SST {f(ss):5.1f}  air {f(ta):5.1f}  final air {f(fin):5.1f}  NCEP air {f(ob):5.1f}  "
              f"qsat(air)/qsat(SST) {f(np.exp(qk*(ta-ss))):.2f}")
