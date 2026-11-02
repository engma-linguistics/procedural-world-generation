"""Lane 135: how big are the spin-up's transients? Over tools/ice_diag.py outputs (seed*_L6.json.gz, 1 Gyr).
usage: spinup.py GLOB...   (e.g. "<judge>/main_r*/seed*_L6.json.gz")
Per draw and window (0-100, 100-200, 200-300, 300-500, 500-700, 700-1000 Myr): the mean of the CO2 source and the
weathering sink (raw, as counted), land %, the star's forcing, dT and ln CO2, each against the draw's 300-1000 Myr
mean (ratios for source/sink, differences for the rest); medians and the 10-90% range over the draws. Also: when the
plants arrive (first step with w_plant > 1, bare = 1), the step change of ln sink there, and the references' mismatch with the
300-1000 Myr means (ln src_ref/source, ln sink_ref/sink-at-the-balance is not recorded, so only the raw ratio)."""
import glob
import gzip
import json
import sys

import numpy as np

W = ((0, 100), (100, 200), (200, 300), (300, 500), (500, 700), (700, 1000))
files = sorted({f for g in sys.argv[1:] for f in glob.glob(g)})
acc = {}
plants, jump, srcref, sinkref, late_imb = [], [], [], [], []
for f in files:
    st = json.load(gzip.open(f))["steps"]
    t = np.array([s["t"] for s in st])
    col = {k: np.array([np.nan if s.get(k) is None else s[k] for s in st], float)
           for k in ("source_raw", "sink_raw", "land", "star", "dT", "co2", "src", "sink")}
    late = (t > 300) & (t <= 1000)
    for k in ("source_raw", "sink_raw", "land", "star", "dT", "co2"):
        ref = np.nanmean(col[k][late])
        for w in W:
            m = (t > w[0]) & (t <= w[1])
            v = np.nanmean(col[k][m])
            acc.setdefault((k, w), []).append(v / ref if k in ("source_raw", "sink_raw") else v - ref)
    pl = [s["t"] for s in st if (s.get("w_plant") or 0) > 1.01]  # (1.0: bare ground)
    if pl:
        plants.append(pl[0])
        i = int(np.searchsorted(t, pl[0]))
        if 3 <= i < len(t) - 3:
            jump.append(np.log(np.nanmean(col["sink_raw"][i:i + 3]) / np.nanmean(col["sink_raw"][i - 3:i])))
    # the kept references against the planet's later rates (src = source / src_ref, so ln src_ref/source = -ln src)
    srcref.append(-np.log(np.nanmean(col["src"][late])))
    sinkref.append(-np.log(np.nanmean(col["sink"][late])))
    late_imb.append(np.nanmean(np.log(col["src"][late]) - np.log(col["sink"][late])))
print(f"{len(files)} draws")
for k in ("source_raw", "sink_raw", "land", "star", "dT", "co2"):
    cells = []
    for w in W:
        v = np.array(acc[(k, w)])
        cells.append(f"{np.nanmedian(v):.2f} [{np.nanpercentile(v, 10):.2f}, {np.nanpercentile(v, 90):.2f}]")
    print(f"{k:11s} | " + " | ".join(cells))
if plants:
    print(f"plants arrive: median {np.median(plants):.0f} Myr ({min(plants):.0f}-{max(plants):.0f}); "
          f"ln sink step there: median {np.median(jump):+.2f} [{np.percentile(jump, 10):+.2f}, {np.percentile(jump, 90):+.2f}]")
for name, v in (("ln src_ref / late source (mean index)", srcref), ("ln sink_ref / late sink (mean index)", sinkref),
                ("late imbalance ln src - ln sink", late_imb)):
    v = np.array(v)
    print(f"{name}: median {np.median(v):+.2f}, 10-90% [{np.percentile(v, 10):+.2f}, {np.percentile(v, 90):+.2f}], sd {v.std():.2f}")
