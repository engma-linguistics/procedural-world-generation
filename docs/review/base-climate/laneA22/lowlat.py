"""usage (from a tree root): lowlat.py [level] [dT] [co2_index]

Why the time zoom's plants green the low latitudes under glacial cooling (PW-644), on Earth
(timezoom.source_earth). The plants (vegetation.model, the full model, as Plants.grow at the start) are grown
on the start's climate and on a cooled one (climate.compute at dT, the default -4 C as the forest test), with
the CO2 index (default -1/3: the forest test's CO2 term of -1 C over co2_sensitivity 3), and on the swaps that
take the change apart:
  - ref:     the start's climate, CO2 index 0
  - all:     the cooled climate and the CO2 index
  - cool:    the cooled climate, CO2 0 (the temperature and rain together)
  - temp:    the cooled temperatures with the start's rain (and clouds)
  - rain:    the start's temperatures with the cooled rain
  - co2:     the start's climate with the CO2 index
Per latitude belt (|lat| 0-15, 15-30, 30-40, 40+; ice-free land) it prints the rain, PET (Oudin), the
moisture index P/PET, tree area (Mkm2), tree / herb / bare shares, the coarse biomes' area (forest, savanna and
grassland, desert), and the darkening term (W/m2 over the planet: -veg_toa x the snow-free albedo change x
the annual sun x (1 - snow cover), as plants.measure)."""
import sys

import planet  # noqa: F401  (before numpy)
import numpy as np

from planet import climate
from planet import timezoom as Z
from planet import vegetation as V
from planet.timezoom.geometry import geometry

level = int(sys.argv[1]) if len(sys.argv) > 1 else 4
dT = float(sys.argv[2]) if len(sys.argv) > 2 else -4.0
co2 = float(sys.argv[3]) if len(sys.argv) > 3 else -1.0 / 3.0

src = Z.source_earth(level)
g, tilt = src["grid"], src["tilt"]
elev, H = src["elev"], np.maximum(src["ice"], 0.0)
grounded = (H > 1) & (elev > 0)
surf = np.where(grounded, elev + H, elev)
area = geometry(g)["area"]
A = float(area.sum())
land = (surf > 0) & ~grounded
al = np.abs(g.lat)
sun = climate.insolation(g.lat, tilt) * 1e6 / 86400.0
t = climate.TUNE
TOA = Z.TZParams().veg_toa

c0 = climate.compute(g, surf, 0.0, tilt, ice=np.where(grounded, H, 0))
c4 = climate.compute(g, surf, dT, tilt, ice=np.where(grounded, H, 0))
TK, PK = ("temp", "t_warm", "t_cold"), ("p_jul", "p_jan", "cloud_jul", "cloud_jan")


def mix(ct, cp):
    return {**{k: ct[k] for k in TK}, **{k: cp[k] for k in PK}}


def grow(c, co2i):
    v = V.model(g, surf, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"], tilt, c["cloud_jul"],
                c["cloud_jan"], ice=np.where(grounded, H, 0), co2=co2i)
    v["fb"] = V.feedback(v["eq"]["nu"], v["pot"]["lai"])
    v["c"] = c
    return v


cases = {"ref": (c0, 0.0), "all": (c4, co2), "cool": (c4, 0.0), "temp": (mix(c4, c0), 0.0),
         "rain": (mix(c0, c4), 0.0), "co2": (c0, co2)}
V_ = {k: grow(*v) for k, v in cases.items()}
BELTS = ((0, 15), (15, 30), (30, 40), (40, 90))
FOREST = {6, 9, 10, 13, 14}
OPEN = {8, 12}  # temperate grassland, savanna
DESERT = {7, 11}
ref = V_["ref"]
print(f"Earth L{level}, dT {dT}, CO2 index {co2:+.3f}")
for name, v in V_.items():
    c = v["c"]
    s = v["s"]
    biome = V.biome_of(v["types"], 0)
    sc = climate.snow_cover(g.lat, tilt, c["temp"], c["t_warm"], c["t_cold"], c["p_jul"], c["p_jan"], t)
    da = (1 - sc) * (v["fb"]["albedo"] - ref["fb"]["albedo"])[None, :]
    dF = np.where(land, -TOA * (da * sun).mean(0), 0.0)
    rows = []
    for a, b in BELTS:
        m = land & (al >= a) & (al < b)
        w = area[m]
        P = float((s["precip"][m] * w).sum() / w.sum())
        pet = float((s["pet_y"][m] * w).sum() / w.sum())
        tree = float((v["sm"]["tree"][m] * w).sum() / 1e12)
        herb = float((v["sm"]["herb"][m] * w).sum() / w.sum())
        bare = float(((1 - v["sm"]["cover"][m]) * w).sum() / w.sum())
        f = float(w[np.isin(biome[m], list(FOREST))].sum() / 1e12)
        o = float(w[np.isin(biome[m], list(OPEN))].sum() / 1e12)
        d = float(w[np.isin(biome[m], list(DESERT))].sum() / 1e12)
        F = float((dF * area)[m].sum() / A)
        rows.append(f"{a:>2}-{b:<2} P {P:5.0f} PET {pet:5.0f} mi {P / pet:4.2f} tree {tree:5.2f} herb {herb:.2f} "
                    f"bare {bare:.2f} | forest {f:5.2f} sav+grass {o:5.2f} desert {d:5.2f} Mkm2 | F {F:+.3f}")
    Flo = float((dF * area)[land & (al < 40)].sum() / A)
    print(f"[{name}] F below 40: {Flo:+.3f} W/m2, all land: {float((dF * area).sum() / A):+.3f}")
    for r in rows:
        print("   " + r)
