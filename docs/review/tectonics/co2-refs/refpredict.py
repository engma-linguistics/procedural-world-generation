"""Lane 135 (PW-1316): offline, how well does each way of learning the source's reference over the spin-up predict the
source the planet goes on to have? Over tools/ice_diag.py outputs (1 Gyr). usage: refpredict.py GLOB...
Predictors from the spin-up's raw source (source_raw, per step; the drift's noise included, as in both arms):
  efold   main's: follow with b = 1 - exp(-dt / min(100, 10 + t)) until 300 Myr
  all     PW-1316 B: the mean over 0-300 Myr
  late200 the mean over 100-300 Myr (the ticket's first wording)
Targets: the mean source over 300-400, 300-500 and 300-1000 Myr. Printed: the median and sd over draws of
ln(predictor / target): the sd is how far the kept reference is off, draw to draw."""
import glob
import gzip
import json
import sys

import numpy as np

files = sorted({f for g in sys.argv[1:] for f in glob.glob(g)})
err = {}
for f in files:
    st = json.load(gzip.open(f))["steps"]
    t = np.array([s["t"] for s in st])
    x = np.array([s["source_raw"] for s in st], float)
    spin = (t <= 300) & (x > 0)
    ref, tp = None, 0.0
    for ti, xi in zip(t[spin], x[spin]):
        dt = ti - tp
        tp = ti
        ref = xi if ref is None else ref + (1 - np.exp(-dt / min(100.0, 10.0 + ti))) * (xi - ref)
    pred = {"efold": ref, "all": x[spin].mean(), "late200": x[spin & (t > 100)].mean()}
    for lo, hi in ((300, 400), (300, 500), (300, 1000)):
        tgt = x[(t > lo) & (t <= hi)].mean()
        for k, v in pred.items():
            err.setdefault((k, hi), []).append(np.log(v / tgt))
print(f"{len(files)} draws; ln(reference / later mean source): median, sd")
for k in ("efold", "all", "late200"):
    print(f"{k:8s} " + "  ".join(f"300-{hi}: {np.median(err[(k, hi)]):+.3f}, sd {np.std(err[(k, hi)]):.3f}"
                                  for hi in (400, 500, 1000)))
