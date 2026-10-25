"""usage: terms.py DIAG.json.gz [...] -- per 100 Myr: the means of dT, the star's forcing, the CO2 term, the ice
albedo term, the drift, the source and sink against their references, the plant factor, the supply and pCO2."""
import gzip
import json
import sys

import numpy as np

for f in sys.argv[1:]:
    st = json.load(gzip.open(f))["steps"]
    end = max(r["t"] for r in st)
    print(f)
    for a in range(0, int(end), 100):
        w = [r for r in st if a <= r["t"] < a + 100]

        def m(k):
            return float(np.mean([r.get(k, 0.0) or 0.0 for r in w]))
        print(f"  {a:>4}: dT {m('dT'):+5.1f} star {m('star'):+5.1f} co2t {m('co2_term'):+5.1f} alb {m('albedo_term'):+5.1f}"
              f" drift {m('drift'):+4.1f} src {m('src'):.2f} sink {m('sink'):.2f} plant {m('w_plant'):.2f}"
              f" supply {m('w_supply'):.3g} bare {m('w_bare'):.2f} a {m('w_a'):.2f} pot {m('w_pot'):.2f}"
              f" pco2 {500 * np.exp(m('co2')):.0f}")
