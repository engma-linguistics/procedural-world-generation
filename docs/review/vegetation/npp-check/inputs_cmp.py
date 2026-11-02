"""Lane 123: the climate inputs of warm 550-900 mm land, worlds against Earth's observed African savanna."""
import sys

sys.path.insert(0, "/data/personal/repos/procedural-world-generation/.claude/worktrees/agent-aefe19dd8197a7ce6")
import planet  # noqa: F401
import numpy as np
from planet import store as S, world as W, climate
from planet.geo import is_land
from tools.earth_data import earth_on_grid, earth_clouds


def stats(tag, lat, T, tw, tc, pj, pa, cj, ca, m, extra=""):
    P = 0.5 * (pj + pa)
    north = lat >= 0
    ps, pw = np.where(north, pj, pa), np.where(north, pa, pj)
    mo = climate.months(lat[m], T[m], tw[m], tc[m], pj[m], pa[m], 23.4, cj[m], ca[m])
    pet = mo["pet"].sum(0)
    par = mo["par"].sum(0)
    print(f"{tag:10} n={m.sum():5d} P={P[m].mean():5.0f} summer share={np.mean(ps[m] / np.maximum(ps[m] + pw[m], 1e-9)):.2f} "
          f"MAT={T[m].mean():5.1f} Tw={tw[m].mean():5.1f} Tc={tc[m].mean():5.1f} |lat|={np.abs(lat[m]).mean():4.1f} "
          f"shade={0.5 * (cj[m] + ca[m]).mean():.2f} PET={pet.mean():5.0f} PAR={par.mean():6.0f} {extra}")


for wid in ("067778", "6909cb", "dba204"):
    w = W.load(S.find_world(wid))
    g, L = w["grid"], w["layers"]
    a = lambda k: np.asarray(L[k], float)  # noqa: E731
    land = is_land(a("elevation"), a("ice")) & (a("ice") <= 0) & ~(np.asarray(L["lake"]) > 0)
    P = 0.5 * (a("precipitation_jul") + a("precipitation_jan"))
    cj, ca = climate.shade_from_hours(g.lat, L["sunshine_jul"], L["sunshine_jan"])
    for p0, p1 in ((550, 700), (700, 900)):
        m = land & (a("temperature") > 18) & (P >= p0) & (P < p1)
        stats(f"{wid} {p0}", g.lat, a("temperature"), a("warm_month"), a("cold_month"), a("precipitation_jul"), a("precipitation_jan"),
              cj, ca, m, f"npp={a('npp')[m].mean():.0f}")

w = W.load(S.find_world("506694"))
g, L = w["grid"], w["layers"]
o = {**earth_on_grid(g), **earth_clouds(g)}
f = lambda k, d: np.where(np.isfinite(np.asarray(o[k], float)), np.asarray(o[k], float), d)  # noqa: E731
a = lambda k: np.asarray(L[k], float)  # noqa: E731
T, tw, tc = f("obs_temp", a("temperature")), f("obs_t_warm", a("warm_month")), f("obs_t_cold", a("cold_month"))
pj, pa = f("obs_p_jul", a("precipitation_jul")), f("obs_p_jan", a("precipitation_jan"))
cj0, ca0 = climate.shade_from_hours(g.lat, L["sunshine_jul"], L["sunshine_jan"])
cj = np.where(np.isfinite(o["obs_sun_jul"]), np.clip((0.95 - o["obs_sun_jul"]) / 0.9, 0, 1), cj0)
ca = np.where(np.isfinite(o["obs_sun_jan"]), np.clip((0.95 - o["obs_sun_jan"]) / 0.9, 0, 1), ca0)
land = is_land(a("elevation"), a("ice")) & (a("ice") <= 0)
P = 0.5 * (pj + pa)
lat, lon = g.lat, g.lon
afr = land & (lon > -20) & (lon < 52) & (lat > -35) & (lat < 20) & (T > 18)
for p0, p1 in ((550, 700), (700, 900)):
    stats(f"EarthAfr {p0}", lat, T, tw, tc, pj, pa, cj, ca, afr & (P >= p0) & (P < p1))
    stats(f"EarthAll {p0}", lat, T, tw, tc, pj, pa, cj, ca, land & (T > 18) & (P >= p0) & (P < p1))
