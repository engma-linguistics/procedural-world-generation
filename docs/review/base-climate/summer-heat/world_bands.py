"""Lane 121: a saved world's warm month by latitude band and continentality (read-only).

    PYTHONPATH=. uv run python docs/review/base-climate/summer-heat/world_bands.py worlds/<id>.json [--resolve]

--resolve re-runs the world's climate (vegetation.coupled_climate on its elevation and ice at its dT) with
planet/climate.py::_summer_split recorded, and with the split set to 0, to split the warm month into the split's
part and the rest (the stored world is a finished time-zoom frame: orbit and ice differ a little).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate, vegetation, world  # noqa: E402
from tools.earth_data import cell_areas  # noqa: E402

w = world.load(sys.argv[1])
L, g = w["layers"], w["grid"]
print(sorted(L))
lat = g.lat
alat = np.abs(lat)
elev = L["elevation"].astype(float)
ice = L.get("ice", np.zeros(g.n)).astype(float)
land = (elev > 0) | (ice > 0)
open_land = land & (ice <= 0)
area = cell_areas(g)
cont = np.clip(climate.smooth(g, land.astype(float), 1000.0), 0, 1)


def wm(x, m):
    return float((x * area)[m].sum() / area[m].sum()) if m.any() else float("nan")


def table(tw, tm, tag):
    print(tag, f">=30 {100 * wm((tw >= 30) * 1.0, open_land):.1f}% >=35 {100 * wm((tw >= 35) * 1.0, open_land):.1f}%")
    for lo, hi in ((0, 10), (10, 20), (0, 20), (20, 40), (40, 60)):
        b = open_land & (alat >= lo) & (alat < hi)
        print(f"  {lo}-{hi}: warm {wm(tw, b):.1f} ann {wm(tm, b):.1f} land share {area[b].sum() / area[open_land].sum():.3f}"
              f" cont {wm(cont, b):.2f}")


table(L["warm_month"], L["temperature"], "stored")
for lo, hi in ((0, 0.4), (0.4, 0.7), (0.7, 0.9), (0.9, 1.01)):
    for blo, bhi in ((0, 20), (20, 40)):
        b = open_land & (cont >= lo) & (cont < hi) & (alat >= blo) & (alat < bhi)
        print(f"  {blo}-{bhi} cont {lo}-{hi}: warm {wm(L['warm_month'], b):.1f} ann {wm(L['temperature'], b):.1f} "
              f"area {area[b].sum() / area[open_land].sum():.3f}")
if "--resolve" in sys.argv:
    dT = float(w["meta"].get("dT", sys.argv[sys.argv.index("--resolve") + 1] if len(sys.argv) > 3 else 0.0))
    rec = {}
    orig = climate._summer_split

    def split(*a):
        out = orig(*a)
        rec["d"] = out
        return out * rec.get("scale", 1.0)

    climate._summer_split = split
    for scale in (1.0, 0.0):
        rec["scale"] = scale
        c, _ = vegetation.coupled_climate(g, elev, dT, 23.4, ice)
        table(c["t_warm"], c["temp"], f"resolve dT={dT:.2f} split x{scale}")
        for lo, hi in ((0, 20), (20, 40)):
            b = open_land & (alat >= lo) & (alat < hi)
            print(f"    d_sum {lo}-{hi}: {wm(rec['d'], b):+.2f}  P {wm(c['precip'], b):.0f}")
if "--orbit" in sys.argv:  # the finished frame's orbit anomaly (planet/finish.py::orbit_dt), 'run' vs 'seasons' response
    from planet import icemass
    from planet import timezoom as TZ
    obl, ecc, peri = (float(x) for x in sys.argv[sys.argv.index("--orbit") + 1].split(","))
    dT = float(sys.argv[sys.argv.index("--orbit") + 2])
    _, fb = vegetation.coupled_climate(g, elev, dT, 23.4, ice)
    gw, gc, _ = climate.compute(g, elev, dT, 23.4, ice)["ground"]
    own = icemass.seasonal_k(g.lat, gw, gc, 23.4)
    for resp in ("run", "seasons"):
        p = TZ.TZParams(orbit_resp=resp)
        d = TZ.orbit_anomaly(g, (obl, ecc, peri), 23.4, p, land, ice, own, earth=False)
        c = climate.compute(g, elev, dT, 23.4, ice, veg=fb, orbit_dt=d)
        table(c["t_warm"], c["temp"], f"orbit {resp} k(land 0-20) {wm(d[:, 3].__abs__(), open_land & (alat < 20)):.2f} C |jul|")
