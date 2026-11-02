"""Lane 125: which cloud kinds make the warm semi-arid / wet land's cover (climate.clouds), by rain band.

    PYTHONPATH=. [PLANET_DATA=<root>] uv run python docs/review/base-climate/tropical-cloud/components.py earth|WORLDID

Re-solves the climate (vegetation.coupled_climate, as docs/review/base-climate/summer-heat/diag.py and
world_bands.py --resolve do), records the last call's inputs to climate.clouds, then re-calls it with one cloud
kind's knob zeroed (cloud_deep, cloud_cu, cloud_storm, cloud_rh+cloud_polar, cloud_clear, cloud_sc) and prints the
mean sky cover and shade of warm land by rain band. Nothing is written.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate, vegetation  # noqa: E402

who = sys.argv[1]
rec = {}
orig = climate.clouds


def spy(*a, **k):
    rec["args"], rec["kw"] = a, k
    return orig(*a, **k)


climate.clouds = spy
if who == "earth":
    from tools import earth_data
    from planet.grid import build_grid
    g = build_grid(7)
    d = earth_data.earth_on_grid(g)
    elev, ice, dT = d["elev"].astype(float), d["ice"].astype(float), 0.0
    land = earth_data.land_of(d) & (ice <= 0)
else:
    from planet import store as S, world as W
    from planet.geo import is_land
    wd = W.load(S.find_world(who))
    g, L = wd["grid"], wd["layers"]
    elev, ice = np.asarray(L["elevation"], float), np.asarray(L.get("ice", np.zeros(g.n)), float)
    dT = float(wd["meta"].get("dT", 0.0))
    land = is_land(elev, ice) & (ice <= 0)
c, _ = vegetation.coupled_climate(g, elev, dT, 23.4, ice)
a, kw = rec["args"], rec["kw"]
tune = dict(a[5])
warm = land & (c["temp"] > 18) & (np.abs(g.lat) < 35)
P = c["precip"]
north = g.lat >= 0


def run(over, label):
    t = {**tune, **over}
    out = orig(*a[:5], t, *a[6:], **kw)
    sky = 0.5 * (out[0][0] + out[1][0])
    sh = 0.5 * (climate.shade(out[0][1]) + climate.shade(out[1][1]))
    cells = []
    for p0, p1 in ((400, 900), (900, 1500), (1500, 6000)):
        m = warm & (P >= p0) & (P < p1)
        cells.append(f"{sky[m].mean():.2f}/{sh[m].mean():.2f}")
    print(f"{label:34}", "  ".join(cells))


print(who, "sky/shade of warm land, rain 400-900 | 900-1500 | >1500, n =",
      [int((warm & (P >= p0) & (P < p1)).sum()) for p0, p1 in ((400, 900), (900, 1500), (1500, 6000))])
run({}, "all kinds")
run({"cloud_deep": 0.0}, "no deep (rain-belt towers)")
run({"cloud_cu": 0.0}, "no fair-weather cumulus")
run({"cloud_storm": 0.0}, "no storm-track layer cloud")
run({"cloud_rh": 0.0, "cloud_polar": 0.0}, "no humidity layer cloud")
run({"cloud_clear": 0.0}, "no subtropical clearing")
run({"cloud_deep": 0.0, "cloud_cu": 0.0}, "no convective (deep+cu)")
run({"cloud_sun_conv": 1.0}, "convective counted whole (conv=1)")
