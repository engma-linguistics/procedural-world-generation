"""usage: jointco2.py DIAG_FILE [...] -> offline, per logged step: the CO2 stock that balances the step's source and
sink when the sink's temperature leg sees the climate that CO2 gives (GEOCARB's joint solve), against the stock the
run carried (the sink at the lagged dT). Same source, sink at X = 1, bare share, target; the sink's climate law is
climate_coef() per C. Indicative only: the trajectory itself would change. Harness only."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from planet import climate  # noqa: E402
from planet.tectonics import Params  # noqa: E402
from planet.tectonics.earth import climate_coef, co2_law, co2_term  # noqa: E402
from tools import ice_criteria as C  # noqa: E402

p = Params()
cc = climate_coef()


def solve(s, w, bare, dT, rest):
    """ln X with w co2_law(X) exp(cc (co2_term(X) + rest - dT)) = s (f increases in ln X)."""
    lo, hi = -12.0, 12.0
    for _ in range(60):
        m = 0.5 * (lo + hi)
        f = np.log(w * co2_law(np.exp(m), bare)) + cc * (co2_term(p, m) + rest - dT) - np.log(s)
        lo, hi = (m, hi) if f < 0 else (lo, m)
    return 0.5 * (lo + hi)


for f in sys.argv[1:]:
    st = [r for r in C.load(f)["steps"] if r["t"] >= 300]
    run, joint = [], []
    for r in st:
        rest = r["target"] - r["co2_term"]  # albedo, star, control, offset: held within the step
        run.append(r["co2"])
        joint.append(solve(r["src"], r["sink"], r["w_bare"], r["dT"], rest))
    run, joint = np.array(run), np.array(joint)
    pb = climate.PCO2_BALANCE
    print(f"{Path(f).name.split('_')[0]:>11}: ln X sd run {run.std():.2f} joint {joint.std():.2f}; step-diff sd run "
          f"{np.diff(run).std():.2f} joint {np.diff(joint).std():.2f}; 10-90% ppm run "
          f"{pb * np.exp(np.percentile(run, 10)):.0f}-{pb * np.exp(np.percentile(run, 90)):.0f} joint "
          f"{pb * np.exp(np.percentile(joint, 10)):.0f}-{pb * np.exp(np.percentile(joint, 90)):.0f}; end ppm run "
          f"{pb * np.exp(run[-1]):.0f} joint {pb * np.exp(joint[-1]):.0f}")
