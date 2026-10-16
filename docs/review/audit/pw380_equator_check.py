"""PW-380: July/January on equatorial land of world bcd6c8's terrain, recomputed with its frame's orbit."""
import sys
import numpy as np
sys.path.insert(0, ".")
from planet import climate, world, timezoom as TZ

w = world.load("/data/personal/repos/procedural-world-generation/worlds/bcd6c8.json")
g, L = w["grid"], w["layers"]
elev, ice = np.asarray(L["elevation"], float), np.asarray(L["ice"], float)
land = elev > 0
d = TZ.orbit_anomaly(g, (24.589, 0.0409, 236.8), 23.4, TZ.TZParams(), land, ice)
for tag, od in (("no orbit", None), ("orbit", d)):
    c = climate.compute(g, elev, -8.95, 23.4, np.where(land, ice, 0.0), orbit_dt=od)
    s = world.seasons(g, c)
    jul, jan = s["temperature_jul"], s["temperature_jan"]
    out = [tag]
    for lo, hi in ((0, 1), (-1, 0), (5, 10), (-10, -5)):
        m = land & (g.lat >= lo) & (g.lat < hi)
        out.append("%g..%g jul %.1f jan %.1f" % (lo, hi, np.median(jul[m]), np.median(jan[m])))
    bins = np.floor(g.lon / 2.0).astype(int)
    st = []
    for b in np.unique(bins):
        mn, ms = land & (bins == b) & (g.lat >= 0) & (g.lat < 1), land & (bins == b) & (g.lat < 0) & (g.lat > -1)
        if mn.any() and ms.any():
            st.append(abs(jul[mn].mean() - jul[ms].mean()))
    out.append("jul step med %.1f p90 %.1f max %.1f" % (np.median(st), np.percentile(st, 90), np.max(st)))
    print(" | ".join(out), flush=True)
