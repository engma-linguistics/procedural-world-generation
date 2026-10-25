"""usage: endterms.py DIAG_FILE [...] -> the carbon balance's parts near the run's end, per seed-draw: what sets the
end pCO2 (source, the sink's weathering parts: supply, temperature, plants, area, rate) and the temperature's parts
(drift, CO2 term, albedo, star). Means over the windows given (Myr before the end). Harness only."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from planet import climate  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

KEYS = ["co2", "dT", "drift", "co2_term", "albedo_term", "star", "star_ctl", "src", "sink", "source_raw", "sink_raw",
        "w_supply", "w_temp", "w_plant", "w_area", "w_rate", "w_bare", "w_a", "w_q", "w_T", "land"]
print(f"{'seed':>11} {'win':>8} " + " ".join(f"{k[:9]:>9}" for k in KEYS) + "   pCO2")
for f in sys.argv[1:]:
    raw = C.load(f)
    steps = [r for r in raw["steps"] if r["t"] > 0]
    t = np.array([r["t"] for r in steps])
    end = t.max()
    for a, b in [(300, 400), (500, 600), (700, 800), (end - 100, end - 30), (end - 30, end + 1)]:
        w = (t >= a) & (t < b)
        vals = []
        for k in KEYS:
            v = np.array([r.get(k, np.nan) if r.get(k) is not None else np.nan for r in np.array(steps)[w]], float)
            vals.append(np.nanmean(v) if len(v) else np.nan)
        pc = climate.PCO2_BALANCE * np.exp(vals[0])
        print(f"{Path(f).name.split('_')[0]:>11} {a:>4.0f}-{b:<4.0f}" + " ".join(f"{v:9.3f}" for v in vals) + f" {pc:6.0f}")
