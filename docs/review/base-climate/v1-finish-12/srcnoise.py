"""usage: srcnoise.py DIAG_FILE [...] -> how jumpy the carbon source is after 300 Myr: the tectonic outgassing
(source_raw without the drift's factor) per step, its step-to-step scatter, and its spread over running means of
2 (one step), 10, 20 and 50 Myr; and the same for ln pCO2. Harness only."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from planet.tectonics import Params  # noqa: E402
from planet.tectonics.earth import drift_source  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

p = Params()
for f in sys.argv[1:]:
    raw = C.load(f)
    st = [r for r in raw["steps"] if r["t"] >= 300]
    dt = st[1]["t"] - st[0]["t"]
    tect = np.array([r["source_raw"] / drift_source(p, r["drift"]) for r in st])
    noise = np.array([drift_source(p, r["drift"]) for r in st])
    co2 = np.array([r["co2"] for r in st])
    lt = np.log(tect)
    jump = np.std(np.diff(lt))
    out = [f"{Path(f).name.split('_')[0]:>11} dt {dt:.0f}: ln tect step-diff sd {jump:.2f}, lag-1 r "
           f"{np.corrcoef(lt[1:], lt[:-1])[0, 1]:+.2f}"]
    for w in [1, 5, 10, 25]:
        sm = np.convolve(lt, np.ones(w) / w, mode="valid")
        out.append(f"sd(ln tect, {w * dt:.0f} Myr mean) {np.std(sm):.2f}")
    out.append(f"sd ln drift factor {np.std(np.log(noise)):.2f}; sd ln pCO2 {np.std(co2):.2f}, step-diff "
               f"{np.std(np.diff(co2)):.2f}")
    print("; ".join(out))
