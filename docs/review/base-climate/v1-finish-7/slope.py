"""usage: slope.py DIR... : within-run regression over 300-1000 Myr (steps) of ln w_temp (the weathering's
temperature factor, supply- and plant-weighted) and w_T (supply-weighted local temperature) on the global dT: the
thermostat's realised temperature coefficient per C of global warming (nominal WEATHER_K 0.09 per C of local)."""
import gzip
import json
import sys
from pathlib import Path

import numpy as np

for d in sys.argv[1:]:
    a, b, c = [], [], []
    for f in sorted(Path(d).rglob("seed*_L6.json.gz")):
        st = json.load(gzip.open(f))["steps"]
        ok = [s for s in st if s["t"] >= 300 and s.get("w_temp") and s.get("w_T") is not None]
        if len(ok) < 20:
            continue
        dT = np.array([s["dT"] for s in ok])
        lw = np.log([s["w_temp"] for s in ok])
        wT = np.array([s["w_T"] for s in ok])
        sl = np.array([s["sink"] for s in ok]) if ok[0].get("sink") is not None else None
        a.append(np.polyfit(dT, lw, 1)[0])
        b.append(np.polyfit(dT, wT, 1)[0])
        if sl is not None:
            c.append(np.polyfit(dT, np.log(sl), 1)[0])
    print(f"{Path(d).name}: n={len(a)} dlnw/ddT {np.median(a):.3f} [{np.percentile(a, 25):.3f}, {np.percentile(a, 75):.3f}]"
          f" dwT/ddT {np.median(b):.2f} dln(sink/ref)/ddT {np.median(c) if c else float('nan'):.3f}")
