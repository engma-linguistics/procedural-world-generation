"""Lane 148 (PW-1365): per-draw climate summary of the eccentricity screen's runs (read-only).

    uv run python docs/review/climate/eccentricity/runs_summary.py ROOT ARM...

ROOT/<ARM>/m_r0_l6/seed*_L6.json.gz (tools/ice_diag.py output). Per draw, after 300 Myr: the median and max of the
global dT (C against the model's pre-industrial), the median and min pCO2 (ppm), the median and max share of the land
under ice (%), and the share of steps in an icehouse (land ice holding >= 20 m of sea level). For the hard bars run
tools/hard_bar.py ROOT/<ARM> 6.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from planet import climate  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

root = Path(sys.argv[1])
print(f"{'arm':>5} {'seed':>7} {'dTmed':>6} {'dTmax':>6} {'pCO2med':>7} {'pCO2min':>7} {'iceMed%':>7} {'iceMax%':>7} {'icehouse%':>9}")
for arm in sys.argv[2:]:
    for p in sorted((root / arm).glob("m_r*/seed*_L6.json.gz")):
        raw = C.load(str(p))
        s = C.series(raw)
        late = [r for r in raw["steps"] if r["t"] >= 300]
        pc = climate.PCO2_BALANCE * np.exp(np.array([r["co2"] for r in late]))
        m = s["t"] >= 300
        dT, il, sl = s["dT"][m], 100 * s["iced_land"][m], s["sea_ice"][m]
        print(f"{arm:>5} {p.name.split('_')[0][4:]:>7} {np.median(dT):+6.1f} {dT.max():+6.1f} {np.median(pc):7.0f} "
              f"{pc.min():7.0f} {np.median(il):7.1f} {il.max():7.1f} {100 * np.mean(sl <= -20):9.0f}")
