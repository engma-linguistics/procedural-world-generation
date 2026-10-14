"""Run the climate model on the real Earth and compare with observations.

    PYTHONPATH=. uv run python tools/earth_check.py [--level 6] [--png out.png] [--json out.json]

Separates *model* error from the generated worlds' odd geography: the model
gets Earth's real elevation and ice (tools/earth_data.py, ETOPO1) at dT=0,
tilt 23.4, and every output is compared with an observed climatology mapped
onto the same cells:

  Koppen   Kottek et al. 2006 (0.5 deg, 1951-2000; same -3 C C/D rule and
           aridity thresholds as the model; As scored as Aw). Peel et al.
           2007 published group shares are printed alongside for reference.
  precip   GPCC v2018 1 deg (land), GPCP v2.3 2.5 deg (land + ocean)
  temp     NCEP/NCAR reanalysis 2 m air temperature 1981-2010 (surface,
           so it already includes the altitude effect, like the model)

All shares/means are area-weighted with the true spherical cell areas.
"Land" for comparisons is the model's land mask (elev > 0); Kottek/GPCC
cells that are missing (sea in their mask) are skipped. "Antarctica" means
lat < -60.

Rivers: the model's runoff (rain minus evaporation) routed over Earth's
elevation on the same grid (hydrology.rivers_and_lakes, with evaporating
lakes), compared at the mouths of big rivers with observed mean discharge
(Dai & Trenberth 2002 / GRDC-style figures; the Nile before its dams).
Inland seas that ETOPO puts below sea level (Caspian, Black Sea) count as
land basins there, so they become lakes. The column "obs P" routes the
runoff the same scheme makes from GPCC's observed rain instead, which
separates evaporation/runoff error from rain error.

Only depends on climate.compute(grid, elev, dT, tilt, ice) and its keys
temp/t_warm/t_cold/precip/p_jul/p_jan/koppen/runoff/aet/lake_evap, plus
KOPPEN/SEA_CLASS, climate.water_balance and hydrology.rivers_and_lakes.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planet import climate, hydrology  # noqa: E402
from planet import images  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools import earth_data  # noqa: E402
from tools.earth_data import cell_areas  # noqa: E402

GROUPS = "ABCDE"
CODES = {i: c for i, c, _, _ in climate.KOPPEN}
COLORS = {i: col for i, _, _, col in climate.KOPPEN}
SEA = climate.SEA_CLASS

# Peel, Finlayson & McMahon (2007), HESS 11:1633, Sect. 4: share of land area
# by main group, *including* Antarctica (all EF). Uses the 0 C C/D boundary,
# so its D share is larger / C smaller than a -3 C classification (the model
# and Kottek use -3 C).
PEEL_2007_INCL_ANT = {"A": 19.0, "B": 30.2, "C": 13.4, "D": 24.6, "E": 12.8}

# ~60 well-known stations. Codes are the commonly cited ones (Wikipedia /
# Peel-style); several are borderline and list all accepted alternatives,
# including the -3 C (Kottek/model) variant where it differs from 0 C.
POINTS = [
    # name, lat, lon, accepted codes
    ("Manaus", -3.1, -60.0, ("Af", "Am")),
    ("Singapore", 1.35, 103.8, ("Af",)),
    ("Kisangani", 0.5, 25.2, ("Af",)),
    ("Jakarta", -6.2, 106.85, ("Am", "Af")),
    ("Miami", 25.8, -80.2, ("Am",)),
    ("Mumbai", 19.1, 72.9, ("Am",)),
    ("Lagos", 6.5, 3.4, ("Aw",)),
    ("Kinshasa", -4.3, 15.3, ("Aw",)),
    ("Darwin", -12.5, 130.8, ("Aw",)),
    ("Bangkok", 13.75, 100.5, ("Aw",)),
    ("Kolkata", 22.6, 88.4, ("Aw",)),
    ("Brasilia", -15.8, -47.9, ("Aw",)),
    ("Riyadh", 24.7, 46.7, ("BWh",)),
    ("Cairo", 30.0, 31.2, ("BWh",)),
    ("Timbuktu", 16.8, -3.0, ("BWh",)),
    ("Karachi", 24.9, 67.0, ("BWh",)),
    ("Lima", -12.0, -77.0, ("BWh",)),
    ("Alice Springs", -23.7, 133.9, ("BWh",)),
    ("Phoenix", 33.4, -112.1, ("BWh",)),
    ("Las Vegas", 36.2, -115.1, ("BWh",)),
    ("Kashgar", 39.5, 76.0, ("BWk",)),
    ("Niamey", 13.5, 2.1, ("BSh",)),
    ("Dakar", 14.7, -17.45, ("BSh",)),
    ("Windhoek", -22.6, 17.1, ("BSh",)),
    ("Ulaanbaatar", 47.9, 106.9, ("BSk", "Dwb", "Dwc")),
    ("Denver", 39.7, -105.0, ("BSk",)),
    ("Madrid", 40.4, -3.7, ("BSk", "Csa")),
    ("Tehran", 35.7, 51.4, ("BSk", "BSh", "Csa")),
    ("Kabul", 34.5, 69.2, ("BSk", "Dsa")),
    ("Los Angeles", 34.05, -118.25, ("Csb", "Csa", "BSh")),
    ("Rome", 41.9, 12.5, ("Csa",)),
    ("Athens", 38.0, 23.7, ("Csa", "BSh")),
    ("Tashkent", 41.3, 69.25, ("Csa", "BSk")),
    ("Cape Town", -33.9, 18.4, ("Csb",)),
    ("Perth", -31.95, 115.9, ("Csa",)),
    ("Santiago", -33.45, -70.7, ("Csb", "BSk")),
    ("Shanghai", 31.2, 121.5, ("Cfa",)),
    ("Tokyo", 35.7, 139.7, ("Cfa",)),
    ("Buenos Aires", -34.6, -58.4, ("Cfa",)),
    ("Atlanta", 33.75, -84.4, ("Cfa",)),
    ("Houston", 29.8, -95.4, ("Cfa",)),
    ("Sydney", -33.9, 151.2, ("Cfa",)),
    ("Sao Paulo", -23.55, -46.6, ("Cfa", "Cwa")),
    ("Istanbul", 41.0, 29.0, ("Csa", "Cfa")),
    ("London", 51.5, -0.13, ("Cfb",)),
    ("Paris", 48.85, 2.35, ("Cfb",)),
    ("Seattle", 47.6, -122.3, ("Csb", "Cfb")),
    ("Vancouver", 49.25, -123.1, ("Cfb", "Csb")),
    ("Auckland", -36.85, 174.8, ("Cfb",)),
    ("Hobart", -42.9, 147.3, ("Cfb",)),
    ("Bogota", 4.7, -74.1, ("Cfb",)),
    ("Hong Kong", 22.3, 114.2, ("Cwa",)),
    ("Delhi", 28.6, 77.2, ("Cwa", "BSh")),
    ("Lusaka", -15.4, 28.3, ("Cwa",)),
    ("Mexico City", 19.4, -99.1, ("Cwb",)),
    ("Nairobi", -1.3, 36.8, ("Cwb",)),
    ("Addis Ababa", 9.0, 38.75, ("Cwb",)),
    ("Johannesburg", -26.2, 28.05, ("Cwb",)),
    ("Kunming", 25.0, 102.7, ("Cwb",)),
    ("Lhasa", 29.65, 91.1, ("Dwb", "Cwb", "BSk")),
    ("Beijing", 39.9, 116.4, ("Dwa", "BSk")),
    ("Seoul", 37.6, 127.0, ("Dwa",)),
    ("Chicago", 41.9, -87.6, ("Dfa",)),
    ("Moscow", 55.75, 37.6, ("Dfb",)),
    ("Montreal", 45.5, -73.6, ("Dfb",)),
    ("Winnipeg", 49.9, -97.1, ("Dfb",)),
    ("Stockholm", 59.3, 18.1, ("Dfb", "Cfb")),
    ("Astana", 51.2, 71.45, ("Dfb", "BSk")),
    ("Novosibirsk", 55.0, 82.9, ("Dfb",)),
    ("Yakutsk", 62.0, 129.7, ("Dfd",)),
    ("Anchorage", 61.2, -149.9, ("Dfc", "Dsc")),
    ("Fairbanks", 64.8, -147.7, ("Dfc", "Dwc", "Dsc")),
    ("Reykjavik", 64.1, -21.9, ("Cfc", "ET")),
    ("Ushuaia", -54.8, -68.3, ("Cfc", "ET")),
    ("Nuuk", 64.2, -51.7, ("ET",)),
    ("Utqiagvik", 71.3, -156.8, ("ET",)),
    ("Summit GL", 72.6, -38.5, ("EF",)),
    ("Vostok", -78.5, 106.8, ("EF",)),
]

# Big rivers: name, observed mean discharge at the mouth (m3/s), and gauges
# on the main stems inside the basin (lat, lon). The routed river through
# each gauge is followed to its end and the flow there summed over distinct
# ends: on 110 km cells of Earth's mean elevation a river can reach the sea
# some way from its real mouth (the Congo through Gabon), but the basin's
# water is still counted. If a river's ends are shared with a bigger river's
# (at 110 km the Orinoco above Caicara drains to the Amazon through the
# Casiquiare gap, and the Ob joins the Yenisei), it is reported as captured
# by that river, with no discharge of its own, rather than double counting.
RIVERS = [
    ("Amazon", 209000, [(-1.95, -55.5)]),  # Obidos
    ("Congo", 41000, [(0.05, 18.3)]),  # Mbandaka
    ("Ganges-Brahmaputra", 38000, [(25.6, 85.1), (26.2, 91.7)]),  # Patna, Guwahati
    ("Orinoco", 37000, [(7.6, -66.2)]),  # Caicara
    ("Yangtze", 30000, [(30.6, 114.3)]),  # Wuhan
    ("Yenisei", 19600, [(61.6, 90.0)]),
    ("Mississippi", 17000, [(32.3, -90.9)]),  # Vicksburg
    ("Lena", 17000, [(66.8, 123.4)]),  # Zhigansk
    ("Mekong", 15000, [(15.1, 105.8)]),  # Pakse
    ("Ob", 12500, [(61.0, 69.0)]),  # Khanty-Mansiysk
    ("Mackenzie", 10000, [(61.9, -121.4)]),  # Fort Simpson
    ("Nile", 2800, [(15.6, 32.5)]),  # Khartoum (natural flow at the sea, before the dams)
    ("Murray", 800, [(-34.2, 142.2)]),  # Mildura
]
# Closed (endorheic) lakes and salt pans: name, lat, lon
CLOSED_LAKES = [
    ("Caspian Sea", 42.0, 50.5),
    ("Aral Sea", 45.0, 60.0),
    ("Great Salt Lake / Great Basin", 40.5, -116.0),
    ("Lake Eyre", -28.5, 137.3),
    ("Lake Chad", 13.0, 14.5),
    ("Lake Balkhash", 46.5, 74.5),
    ("Tarim / Lop Nur", 40.0, 88.0),
    ("Okavango / Makgadikgadi", -20.0, 24.0),
    ("Dead Sea", 31.5, 35.5),
    ("Altiplano (Titicaca, Uyuni)", -18.0, -68.0),
]

# Named regions for the error hunt: (name, lat0, lat1, lon0, lon1)
REGIONS = [
    ("Amazon", -10, 2, -70, -50),
    ("Congo basin", -5, 5, 12, 30),
    ("Borneo/Sumatra", -3, 4, 98, 118),
    ("West Africa coast", 4, 10, -12, 8),
    ("Sahel", 10, 16, -15, 30),
    ("Sahara", 18, 30, -10, 30),
    ("Arabia", 17, 28, 40, 55),
    ("India", 10, 28, 72, 88),
    ("Indochina", 10, 22, 98, 108),
    ("SE China", 22, 32, 105, 122),
    ("NE China/Korea", 36, 46, 115, 130),
    ("Japan", 32, 42, 130, 142),
    ("Tibet", 30, 36, 80, 95),
    ("Central Asia", 38, 48, 55, 75),
    ("Gobi/Mongolia", 40, 48, 95, 115),
    ("W Siberia", 55, 65, 65, 85),
    ("E Siberia", 60, 70, 110, 140),
    ("European Russia", 50, 60, 30, 50),
    ("W Europe", 43, 55, -5, 15),
    ("Mediterranean", 35, 42, -5, 25),
    ("SE USA", 30, 37, -95, -77),
    ("NE USA", 38, 45, -85, -72),
    ("Great Plains", 35, 45, -105, -97),
    ("US Southwest", 31, 37, -116, -108),
    ("Pacific NW", 43, 50, -124, -121),
    ("N Canada", 55, 65, -110, -70),
    ("Alaska", 60, 70, -160, -142),
    ("Mexico N", 25, 31, -110, -100),
    ("Central America", 8, 17, -92, -78),
    ("NE Brazil", -10, -3, -42, -35),
    ("SE Brazil", -25, -18, -50, -40),
    ("Pampas", -38, -30, -65, -58),
    ("Patagonia", -50, -40, -72, -65),
    ("Peru/Atacama coast", -25, -5, -80, -70),
    ("East Africa", -5, 5, 34, 42),
    ("Southern Africa", -30, -20, 18, 30),
    ("Australia interior", -30, -20, 120, 145),
    ("E Australia", -35, -25, 148, 154),
    ("Greenland", 65, 80, -50, -25),
    ("Antarctica", -90, -70, -180, 180),
]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def group_of(ids: np.ndarray) -> np.ndarray:
    """KOPPEN ids -> 0..4 for A..E, -1 for sea/missing."""
    lut = np.array([GROUPS.index(CODES[i][0]) if CODES[i][0] in GROUPS else -1
                    for i in range(len(CODES))])
    return np.where((ids >= 0) & (ids < len(lut)), lut[np.clip(ids, 0, len(lut) - 1)], -1)


def wmean(x, w, m):
    m = m & np.isfinite(x)
    return float(np.sum(x[m] * w[m]) / np.sum(w[m])) if np.sum(w[m]) > 0 else float("nan")


def wquant(x, w, m, qs):
    m = m & np.isfinite(x)
    o = np.argsort(x[m])
    xs, cw = x[m][o], np.cumsum(w[m][o])
    cw /= cw[-1]
    return [float(xs[np.searchsorted(cw, q)]) for q in qs]


def shares(g, w, m):
    tot = np.sum(w[m & (g >= 0)])
    return {G: 100 * float(np.sum(w[m & (g == i)]) / tot) if tot > 0 else float("nan")
            for i, G in enumerate(GROUPS)}


def fmt(x, nd=0):
    return "   -" if x is None or not np.isfinite(x) else f"{x:.{nd}f}"


BANDS = [(lo, lo + 10) for lo in range(-90, 90, 10)]


def band_mask(lat, lo, hi):
    return (lat >= lo) & (lat < hi) if hi < 90 else (lat >= lo)


# --------------------------------------------------------------------------
# the check
# --------------------------------------------------------------------------
def run(level: int):
    t0 = time.time()
    grid = build_grid(level)
    d = earth_data.earth_on_grid(grid)
    t1 = time.time()
    c = climate.compute(grid, d["elev"].astype(np.float64), dT=0.0, tilt=23.4,
                        ice=d["ice"].astype(np.float64))
    t2 = time.time()
    return grid, d, c, (t1 - t0, t2 - t1)


def analyse(grid, d, c) -> dict:
    lat, lon = grid.lat, grid.lon
    w = cell_areas(grid)
    land = d["elev"] > 0
    ant = lat < -60
    k = np.asarray(c["koppen"])
    ok = d["obs_koppen"].astype(int)
    gm, go = group_of(k), group_of(ok)
    both = land & (ok >= 0)
    R = {}

    # ---- Koppen group shares
    R["koppen_shares"] = {
        "model_excl_ant": shares(gm, w, land & ~ant),
        "model_incl_ant": shares(gm, w, land),
        "kottek_excl_ant": shares(go, w, both & ~ant),
        "kottek_incl_ant": shares(go, w, both),
        "peel2007_incl_ant": PEEL_2007_INCL_ANT,
    }
    m = both & ~ant
    R["cell_agreement_excl_ant"] = earth_data.koppen_agreement(grid, k, ok, d["elev"])  # the Earth Koppen score
    conf = np.zeros((5, 5))
    for i in range(5):
        for j in range(5):
            conf[i, j] = np.sum(w[m & (go == i) & (gm == j)])
    R["group_confusion_pct_of_obs_row"] = {
        GROUPS[i]: {GROUPS[j]: 100 * float(conf[i, j] / max(conf[i].sum(), 1e-12)) for j in range(5)}
        for i in range(5)}
    # per-code area share (excl. Antarctica) for the most common codes
    codes = {}
    for cid, code in CODES.items():
        if cid == SEA:
            continue
        codes[code] = {"model": 100 * float(np.sum(w[land & ~ant & (k == cid)]) / np.sum(w[land & ~ant])),
                       "kottek": 100 * float(np.sum(w[m & (ok == cid)]) / np.sum(w[m]))}
    R["code_shares_excl_ant"] = codes

    # ---- by latitude band
    rows = []
    for lo, hi in BANDS:
        b = band_mask(lat, lo, hi)
        rb = {"band": f"{lo}..{hi}", "land_frac": 100 * float(np.sum(w[b & land]) / np.sum(w[b]))}
        if np.sum(w[b & both]) > 0:
            rb["model"] = shares(gm, w, b & both)
            rb["kottek"] = shares(go, w, b & both)
            rb["group_match"] = 100 * float(np.sum(w[b & both & (gm == go)]) / np.sum(w[b & both]))
        P, Pg, T = c["precip"], d["obs_gpcp"], c["temp"]
        rb["P_land_model"] = wmean(P, w, b & land)
        rb["P_land_gpcc"] = wmean(d["obs_precip"], w, b & land)
        rb["P_land_model_on_gpcc"] = wmean(np.where(np.isfinite(d["obs_precip"]), P, np.nan), w, b & land)
        rb["P_ocean_model"] = wmean(P, w, b & ~land)
        rb["P_ocean_gpcp"] = wmean(Pg, w, b & ~land)
        rb["P_land_gpcp"] = wmean(Pg, w, b & land)
        rb["T_land_model"] = wmean(T, w, b & land)
        rb["T_land_obs"] = wmean(d["obs_temp"], w, b & land)
        rb["T_ocean_model"] = wmean(T, w, b & ~land)
        rb["T_ocean_obs"] = wmean(d["obs_temp"], w, b & ~land)
        rb["Trange_land_model"] = wmean(c["t_warm"] - c["t_cold"], w, b & land)
        rb["Trange_land_obs"] = wmean(d["obs_t_warm"] - d["obs_t_cold"], w, b & land)
        rows.append(rb)
    R["bands"] = rows

    # ---- land precipitation distribution (excl. Antarctica, where GPCC exists)
    mp = land & ~ant & np.isfinite(d["obs_precip"])
    qs = [0.1, 0.5, 0.9]
    R["land_precip_excl_ant"] = {
        "model": dict(mean=wmean(c["precip"], w, mp), **dict(zip(["p10", "median", "p90"], wquant(c["precip"], w, mp, qs)))),
        "gpcc": dict(mean=wmean(d["obs_precip"], w, mp), **dict(zip(["p10", "median", "p90"], wquant(d["obs_precip"], w, mp, qs)))),
        "model_all_land_excl_ant_mean": wmean(c["precip"], w, land & ~ant),
    }
    R["global_means"] = {
        "P_model": wmean(c["precip"], w, np.ones_like(land)),
        "P_gpcp": wmean(d["obs_gpcp"], w, np.ones_like(land)),
        "T_model": wmean(c["temp"], w, np.ones_like(land)),
        "T_ncep": wmean(d["obs_temp"], w, np.ones_like(land)),
    }
    # seasonality: share of annual rain in the local summer half-year, land
    north = lat >= 0
    def summer_share(pj, pn):
        return np.where(north, pj, pn) / np.maximum(pj + pn, 1e-9)
    R["summer_rain_share_land"] = {
        "model": wmean(summer_share(c["p_jul"], c["p_jan"]), w, mp),
        "gpcc": wmean(summer_share(d["obs_p_jul"], d["obs_p_jan"]), w, mp),
    }

    # ---- points
    nb_off, nb_idx = grid.nbr_off, grid.nbr_idx
    pts = []
    plat = np.array([p[1] for p in POINTS]); plon = np.array([p[2] for p in POINTS])
    cells = grid.locate(earth_data._unit(plat, plon))
    score = {"exact": 0, "group": 0, "miss": 0}
    for (name, la, lo_, acc), ci in zip(POINTS, cells):
        moved = False
        if not land[ci]:  # coastal city in a sea cell: nearest land cell within 2 rings
            ring = set(nb_idx[nb_off[ci]:nb_off[ci + 1]])
            for j in list(ring):
                ring |= set(nb_idx[nb_off[j]:nb_off[j + 1]])
            cand = [j for j in ring if land[j]]
            if cand:
                q = earth_data._unit(np.array([la]), np.array([lo_]))[0]
                ci = max(cand, key=lambda j: grid.centers[j] @ q)
                moved = True
        mc = CODES[int(k[ci])]
        if mc in acc:
            s = "exact"
        elif mc[0] in {a[0] for a in acc}:
            s = "group"
        else:
            s = "miss"
        score[s] += 1
        pts.append(dict(name=name, lat=la, lon=lo_, true=list(acc), model=mc,
                        kottek=CODES.get(int(ok[ci]), "?") if ok[ci] >= 0 else "?", score=s,
                        moved_to_land=moved, sea_cell=not bool(land[ci]),
                        T=float(c["temp"][ci]), T_obs=float(d["obs_temp"][ci]),
                        Tw=float(c["t_warm"][ci]), Tc=float(c["t_cold"][ci]),
                        Tw_obs=float(d["obs_t_warm"][ci]), Tc_obs=float(d["obs_t_cold"][ci]),
                        P=float(c["precip"][ci]), P_obs=float(d["obs_precip"][ci]),
                        elev=float(d["elev"][ci] + d["ice"][ci])))
    R["points"] = pts
    R["point_score"] = score

    # ---- regions
    regs = []
    for name, a0, a1, o0, o1 in REGIONS:
        rm = land & (lat >= a0) & (lat < a1) & (lon >= o0) & (lon < o1)
        if rm.sum() == 0:
            continue
        rr = dict(name=name, cells=int(rm.sum()),
                  P=wmean(c["precip"], w, rm & np.isfinite(d["obs_precip"])),
                  P_obs=wmean(d["obs_precip"], w, rm),
                  T=wmean(c["temp"], w, rm), T_obs=wmean(d["obs_temp"], w, rm),
                  Tw=wmean(c["t_warm"], w, rm), Tw_obs=wmean(d["obs_t_warm"], w, rm),
                  Tc=wmean(c["t_cold"], w, rm), Tc_obs=wmean(d["obs_t_cold"], w, rm))
        rk = rm & (ok >= 0)
        rr["group_match"] = 100 * float(np.sum(w[rk & (gm == go)]) / max(np.sum(w[rk]), 1e-12))
        # dominant codes
        def top(ids, mm):
            v = np.bincount(ids[mm], w[mm], len(CODES))
            return CODES[int(np.argmax(v))], 100 * float(v.max() / max(v.sum(), 1e-12))
        rr["top_model"] = top(k, rm)
        rr["top_kottek"] = top(np.maximum(ok, 0), rk) if rk.any() else ("?", 0.0)
        regs.append(rr)
    R["regions"] = regs
    R["rivers"] = earth_rivers(grid, d, c, w)
    return R


def earth_rivers(grid, d, c, w) -> dict:
    """Route runoff on Earth and compare discharges at big river mouths."""
    ice = d["ice"].astype(np.float64)
    # Routing ground: the true mean land surface (earth_data clamps land
    # below sea level to 1 m for the climate), and sea cells cut off from
    # the world ocean (Caspian, Black Sea...) are land basins with their
    # real beds; everything raised so that all of it stays above 0.
    sea = d["elev"] <= 0
    lab, k = grid.components(sea)
    big = np.argmax(np.bincount(lab[lab >= 0], minlength=k))
    inland = sea & (lab != big)
    ground = np.where(sea, d["surface"], d["surface"] - ice).astype(np.float64)
    lift = 1.0 - min(ground[~sea | inland].min(), 0.0)
    elev = np.where(sea & ~inland, ground, ground + lift)
    land = elev > 0
    scale = w / w.mean()  # flow in units of mean-cell x m/yr; true areas
    sq = 4 * np.pi * (6371e3) ** 2 / grid.n / 3.156e7  # mean cell x m/yr -> m3/s

    def routed(cc):
        cc = {k2: cc[k2] * scale for k2 in ("runoff", "aet", "lake_evap")}
        return hydrology.rivers_and_lakes(grid, elev, cc, ice)

    flow, down, lk = routed(c)
    # the same evaporation scheme on GPCC's observed rain (model where GPCC has none)
    pj = np.where(np.isfinite(d["obs_p_jul"]), d["obs_p_jul"], c["p_jul"])
    pn = np.where(np.isfinite(d["obs_p_jan"]), d["obs_p_jan"], c["p_jan"])
    wb = climate.water_balance(grid.lat, c["temp"], c["t_warm"], c["t_cold"], pj, pn)
    wb["runoff"] = np.where(land, wb["runoff"], 0.0)
    flow_o, down_o, lk_o = routed(wb)
    def at_mouth(fl, dn, gauges):
        """The biggest river within 150 km of each gauge, followed to its
        end: (m3/s summed over the distinct places they leave the land, km
        from the first gauge to the end, True if one ends in a closed lake)."""
        ends = {}
        for la, lo_ in gauges:
            q = earth_data._unit(np.array([la]), np.array([lo_]))[0]
            near = np.flatnonzero(land & (grid.centers @ q > np.cos(150 / 6371)))
            if not len(near):
                continue
            i = int(near[np.argmax(fl[near])])
            while dn[i] >= 0 and land[dn[i]]:
                i = int(dn[i])
            ends[i] = (float(fl[i] * sq), bool(dn[i] < 0))
        if not ends:
            return float("nan"), float("nan"), False, set()
        q = earth_data._unit(np.array([gauges[0][0]]), np.array([gauges[0][1]]))[0]
        far = max(float(np.arccos(np.clip(grid.centers[i] @ q, -1, 1))) * 6371 for i in ends)
        return sum(v[0] for v in ends.values()), far, any(v[1] for v in ends.values()), set(ends)

    def captor(k, ends):
        """The bigger listed river (by observed discharge) sharing an end with river k."""
        big = [j for j, e in enumerate(ends) if j != k and e & ends[k] and RIVERS[j][1] > RIVERS[k][1]]
        return RIVERS[max(big, key=lambda j: RIVERS[j][1])][0] if big else None

    res = [(at_mouth(flow, down, g), at_mouth(flow_o, down_o, g)) for _, _, g in RIVERS]
    ends_m, ends_o = [r[0][3] for r in res], [r[1][3] for r in res]
    rows = []
    for k, ((name, obs, _), ((m, m_km, m_lake, _), (o, _, o_lake, _))) in enumerate(zip(RIVERS, res)):
        cap, cap_o = captor(k, ends_m), captor(k, ends_o)
        rows.append(dict(name=name, obs=obs, model=float("nan") if cap else m,
                         obs_rain=float("nan") if cap_o else o, model_km=m_km, model_ends_in_lake=m_lake,
                         obs_rain_ends_in_lake=o_lake, model_captured_by=cap, obs_rain_captured_by=cap_o))
    na = land & (grid.lat > -60)
    ratio = float((c["runoff"] * w)[na].sum() / (c["precip"] * w)[na].sum())
    ok = na & np.isfinite(d["obs_precip"])
    ratio_o = float((wb["runoff"] * w)[ok].sum() / (0.5 * (pj + pn) * w)[ok].sum())
    lakes = []
    for name, la, lo_ in CLOSED_LAKES:
        q = earth_data._unit(np.array([la]), np.array([lo_]))[0]
        near = grid.centers @ q > np.cos(350 / 6371)
        kinds = lambda kk: {h: int((kk[near] == v).sum()) for h, v in (("open", hydrology.OPEN_LAKE),
                            ("closed", hydrology.CLOSED_LAKE), ("pan", hydrology.SALT_PAN))}
        lakes.append(dict(name=name, model=kinds(lk["kind"]), obs_rain=kinds(lk_o["kind"])))
    n_closed = grid.components(lk["kind"] == hydrology.CLOSED_LAKE)[1]
    n_open = grid.components(lk["kind"] == hydrology.OPEN_LAKE)[1]
    endo = 100 * float(w[lk["endorheic"] & na].sum() / w[na].sum())
    endo_o = 100 * float(w[lk_o["endorheic"] & na].sum() / w[na].sum())
    return dict(rivers=rows, runoff_ratio=ratio, endorheic_pct=endo, endorheic_pct_obs_rain=endo_o, runoff_ratio_obs_rain=ratio_o, closed_lakes=lakes,
                n_closed=int(n_closed), n_open=int(n_open), n_pans=int((lk["kind"] == hydrology.SALT_PAN).sum()),
                lake_cells=int(lk["wet"].sum()))


def systematic_errors(R) -> list[str]:
    """Plain-language list of the largest errors, ranked."""
    out = []
    for r in R["regions"]:
        if np.isfinite(r["P_obs"]) and r["P_obs"] > 0 and np.isfinite(r["P"]):
            ratio = r["P"] / r["P_obs"]
            if ratio > 1.6 or ratio < 1 / 1.6:
                out.append((abs(np.log2(ratio)), f"{r['name']}: precip {'too wet' if ratio > 1 else 'too dry'} "
                            f"{r['P']:.0f} vs {r['P_obs']:.0f} mm (x{ratio:.2f}); "
                            f"model {r['top_model'][0]} vs obs {r['top_kottek'][0]}"))
        for key, lab in (("T", "annual T"), ("Tc", "coldest month"), ("Tw", "warmest month")):
            dt = r[key] - r[key + "_obs"]
            if np.isfinite(dt) and abs(dt) >= 4:
                out.append((abs(dt) / 4, f"{r['name']}: {lab} {'too warm' if dt > 0 else 'too cold'} "
                            f"{r[key]:.1f} vs {r[key + '_obs']:.1f} C ({dt:+.1f})"))
    for b in R["bands"]:
        if "model" not in b:
            continue
        for G in "AB":
            dm = b["model"][G] - b["kottek"][G]
            if abs(dm) >= 20:
                out.append((abs(dm) / 20, f"band {b['band']}: group {G} share of land "
                            f"{b['model'][G]:.0f}% vs {b['kottek'][G]:.0f}% obs"))
        po, pm = b["P_ocean_gpcp"], b["P_ocean_model"]
        if np.isfinite(po) and po > 0 and np.isfinite(pm) and (pm / po > 1.6 or pm / po < 1 / 1.6):
            out.append((abs(np.log2(pm / po)), f"band {b['band']}: ocean precip {pm:.0f} vs {po:.0f} mm "
                        f"(x{pm / po:.2f})"))
    out.sort(key=lambda t: -t[0])
    return [s for _, s in out]


def report(R, times, level):
    L = []
    p = L.append
    p(f"=== Earth check, level {level} (data {times[0]:.1f}s, climate {times[1]:.1f}s) ===")
    ks = R["koppen_shares"]
    p("\nKoppen main-group shares of land (%), model vs Kottek 2006 (same cells) and Peel 2007")
    p("                       " + "".join(f"{G:>7}" for G in GROUPS))
    for lab, key in (("model   excl. Antarct.", "model_excl_ant"), ("Kottek  excl. Antarct.", "kottek_excl_ant"),
                     ("model   incl. Antarct.", "model_incl_ant"), ("Kottek  incl. Antarct.", "kottek_incl_ant"),
                     ("Peel07  incl. Antarct.", "peel2007_incl_ant")):
        p(f"{lab:23s}" + "".join(f"{ks[key][G]:7.1f}" for G in GROUPS))
    ca = R["cell_agreement_excl_ant"]
    p(f"cell-by-cell agreement with Kottek (land excl. Antarctica, area-weighted): "
      f"exact code {ca['exact']:.0f}%, main group {ca['group']:.0f}%")
    p("group confusion (row = observed, % of row area going to each model group):")
    p("       " + "".join(f"{G:>6}" for G in GROUPS))
    for G, row in R["group_confusion_pct_of_obs_row"].items():
        p(f"  obs {G}" + "".join(f"{row[H]:6.0f}" for H in GROUPS))
    cs = sorted(R["code_shares_excl_ant"].items(), key=lambda kv: -max(kv[1]["model"], kv[1]["kottek"]))
    p("largest codes (% land excl. Ant.), model/obs: " +
      ", ".join(f"{c} {v['model']:.1f}/{v['kottek']:.1f}" for c, v in cs[:14]))

    p("\nBy 10-degree band, land only: group shares model | Kottek (%), group match")
    p(f"{'band':>9} {'land%':>5}  {'A':>3} {'B':>3} {'C':>3} {'D':>3} {'E':>3} | "
      f"{'A':>3} {'B':>3} {'C':>3} {'D':>3} {'E':>3}  match")
    for b in reversed(R["bands"]):
        if "model" not in b:
            continue
        p(f"{b['band']:>9} {b['land_frac']:5.0f}  " + " ".join(f"{b['model'][G]:3.0f}" for G in GROUPS)
          + " | " + " ".join(f"{b['kottek'][G]:3.0f}" for G in GROUPS) + f"  {b['group_match']:4.0f}%")

    lp = R["land_precip_excl_ant"]
    p("\nLand precipitation excl. Antarctica (mm/yr; cells with GPCC data)")
    p(f"{'':8}{'mean':>7}{'p10':>7}{'median':>8}{'p90':>7}")
    for lab in ("model", "gpcc"):
        v = lp[lab]
        p(f"{lab:8}{v['mean']:7.0f}{v['p10']:7.0f}{v['median']:8.0f}{v['p90']:7.0f}")
    g = R["global_means"]
    ss = R["summer_rain_share_land"]
    p(f"global mean P: model {g['P_model']:.0f}, GPCP {g['P_gpcp']:.0f} mm/yr;  "
      f"global mean T: model {g['T_model']:.1f}, NCEP {g['T_ncep']:.1f} C")
    p(f"share of land rain falling in local summer half-year: model {ss['model']:.2f}, GPCC {ss['gpcc']:.2f}")

    p("\nZonal means by band. P mm/yr (land: model vs GPCC; ocean: model vs GPCP); T C vs NCEP 2 m;"
      " Trange = warmest - coldest month, land")
    p(f"{'band':>9} | {'P land':>11} | {'P ocean':>11} | {'T land':>11} | {'T ocean':>11} | {'Trange land':>11}")
    for b in reversed(R["bands"]):
        p(f"{b['band']:>9} | {fmt(b['P_land_model_on_gpcc']):>5} {fmt(b['P_land_gpcc']):>5} | "
          f"{fmt(b['P_ocean_model']):>5} {fmt(b['P_ocean_gpcp']):>5} | "
          f"{fmt(b['T_land_model'], 1):>5} {fmt(b['T_land_obs'], 1):>5} | "
          f"{fmt(b['T_ocean_model'], 1):>5} {fmt(b['T_ocean_obs'], 1):>5} | "
          f"{fmt(b['Trange_land_model'], 0):>5} {fmt(b['Trange_land_obs'], 0):>5}")

    sc = R["point_score"]
    n = sum(sc.values())
    p(f"\nPoint check: {sc['exact']}/{n} exact, {sc['group']}/{n} group only, {sc['miss']}/{n} wrong group "
      f"(* = city in a sea cell, nearest land cell used;"
      f" elev = model cell surface m, often far above a coastal city's)")
    p(f"{'place':14}{'true':>13}{'Kott':>5}{'model':>6} {'elev':>5} {'T':>5}{'Tobs':>6} {'Tc':>5}{'Tcobs':>6} "
      f"{'Tw':>5}{'Twobs':>6} {'P':>6}{'Pobs':>6}  score")
    for q in R["points"]:
        p(f"{q['name'] + ('*' if q['moved_to_land'] else ''):14}{'/'.join(q['true']):>13}{q['kottek']:>5}{q['model']:>6} {q['elev']:5.0f} "
          f"{q['T']:5.1f}{q['T_obs']:6.1f} {q['Tc']:5.1f}{q['Tc_obs']:6.1f} {q['Tw']:5.1f}{q['Tw_obs']:6.1f} "
          f"{q['P']:6.0f}{fmt(q['P_obs']):>6}  {q['score']}")

    p("\nRegions (land; P model vs GPCC mm/yr, T/Tcold/Twarm model vs NCEP, dominant code model vs Kottek)")
    p(f"{'region':20}{'P':>6}{'Pobs':>6} {'T':>6}{'Tobs':>6} {'Tc':>6}{'Tcobs':>6} {'Tw':>5}{'Twobs':>6}  "
      f"{'model':>11} {'Kottek':>11} grp%")
    for r in R["regions"]:
        p(f"{r['name']:20}{fmt(r['P']):>6}{fmt(r['P_obs']):>6} {r['T']:6.1f}{r['T_obs']:6.1f} "
          f"{r['Tc']:6.1f}{r['Tc_obs']:6.1f} {r['Tw']:5.1f}{r['Tw_obs']:6.1f}  "
          f"{r['top_model'][0]:>4} {r['top_model'][1]:3.0f}%   {r['top_kottek'][0]:>4} {r['top_kottek'][1]:3.0f}%  "
          f"{r['group_match']:3.0f}")

    rv = R["rivers"]
    p(f"\nRivers: runoff / rain on land excl. Antarctica {rv['runoff_ratio']:.2f} (Earth ~0.35-0.40; "
      f"{rv['runoff_ratio_obs_rain']:.2f} with GPCC rain). Discharge at the mouth, m3/s:")
    p(f"{'river':20}{'observed':>10}{'model':>10}{'ratio':>7}{'obs P':>10}{'ratio':>7}  gauge->sea km")
    for r in rv["rivers"]:
        p(f"{r['name']:20}{r['obs']:10.0f}{fmt(r['model']):>10}{fmt(r['model'] / r['obs'], 2):>7}"
          f"{fmt(r['obs_rain']):>10}{fmt(r['obs_rain'] / r['obs'], 2):>7}  {fmt(r['model_km']):>6}"
          + ("  (ends in a lake)" if r["model_ends_in_lake"] else "")
          + (f"  (model drains into the {r['model_captured_by']})" if r["model_captured_by"] else "")
          + (f"  (obs P drains into the {r['obs_rain_captured_by']})" if r["obs_rain_captured_by"] else ""))
    p(f"lakes: {rv['n_open']} open, {rv['n_closed']} closed, {rv['n_pans']} salt-pan cells "
      f"({rv['lake_cells']} lake cells); land draining to closed basins {rv['endorheic_pct']:.0f}% "
      f"({rv['endorheic_pct_obs_rain']:.0f}% with GPCC rain; Earth ~18%, excl. Antarctica).")
    p("Known closed basins, cells within 350 km (model | GPCC rain):")
    for q in rv["closed_lakes"]:
        f = lambda k: f"open {k['open']}, closed {k['closed']}, pan {k['pan']}"
        p(f"  {q['name']:30} {f(q['model'])}  |  {f(q['obs_rain'])}")

    p("\nLargest systematic errors (auto-ranked):")
    for s in R["systematic_errors"][:20]:
        p("  - " + s)
    return "\n".join(L)


# --------------------------------------------------------------------------
# PNG
# --------------------------------------------------------------------------
def _hex(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float64)


def _ramp(x, stops):
    xs = np.array([s[0] for s in stops], float)
    cs = np.array([_hex(s[1]) for s in stops])
    x = np.clip(x, xs[0], xs[-1])
    return np.stack([np.interp(x, xs, cs[:, i]) for i in range(3)], -1)


P_STOPS = [(np.log10(30), "#7f3b08"), (np.log10(150), "#d8a05a"), (np.log10(300), "#f3e08f"),
           (np.log10(600), "#a6d96a"), (np.log10(1200), "#1a9850"), (np.log10(2400), "#2c7fb8"),
           (np.log10(5000), "#253494")]
T_STOPS = [(-40, "#2b0057"), (-20, "#3a4cc0"), (0, "#d8e9f5"), (10, "#f7f7b0"), (20, "#f4a442"),
           (30, "#b2182b")]


def render(path, grid, d, c, width=720):
    """2 columns (left model, right observed) x 3 rows (Koppen, log precip,
    annual temperature). Coastlines from the model land mask on P/T panels."""
    h = width // 2
    la = 90 - (np.arange(h) + 0.5) * 180 / h
    lo = -180 + (np.arange(width) + 0.5) * 360 / width
    LA, LO = np.meshgrid(la, lo, indexing="ij")
    cell = grid.locate(earth_data._unit(LA.ravel(), LO.ravel())).reshape(h, width)
    land = (d["elev"] > 0)[cell]
    coast = np.zeros_like(land)
    coast[:, 1:] |= land[:, 1:] != land[:, :-1]
    coast[1:, :] |= land[1:, :] != land[:-1, :]

    kcol = np.array([_hex(COLORS[i]) for i in range(len(COLORS))])

    def kpanel(ids):
        ids = np.where(ids < 0, SEA, ids)
        return kcol[ids]

    def overlay(img):
        img = img.copy()
        img[coast] = 0
        return img

    # observed rasters, sampled per pixel
    kot = earth_data.kottek()
    kmap = earth_data.kottek_to_model_ids()
    kp = kot[np.clip(((90 - LA) / 0.5).astype(int), 0, 359), np.clip(((LO + 180) / 0.5).astype(int), 0, 719)]
    obs_k = np.where(kp >= 0, kmap[np.maximum(kp, 0)], SEA)
    g = earth_data.raster("gpcc")
    gv = np.where(np.abs(g["val"]) > 1e30, np.nan, g["val"]).sum(0)
    pc = earth_data.raster("gpcp")
    days = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])[:, None, None]
    pv = (pc["val"] * days).sum(0)
    obs_p = earth_data._sample(g, LA, LO, gv)
    obs_p = np.where(np.isfinite(obs_p), obs_p, earth_data._sample(pc, LA, LO, pv))
    t = earth_data.raster("ncep_t2m")
    obs_t = earth_data._sample(t, LA, LO, t["val"].mean(0) - 273.15)

    lp = lambda x: np.log10(np.maximum(x, 1.0))
    left = [kpanel(np.asarray(c["koppen"])[cell]),
            overlay(_ramp(lp(np.asarray(c["precip"])[cell]), P_STOPS)),
            overlay(_ramp(np.asarray(c["temp"])[cell], T_STOPS))]
    right = [kpanel(obs_k), overlay(_ramp(lp(obs_p), P_STOPS)), overlay(_ramp(obs_t, T_STOPS))]
    sep_v = np.full((h, 4, 3), 255.0)
    rows = [np.concatenate([a, sep_v, b], 1) for a, b in zip(left, right)]
    sep_h = np.full((4, rows[0].shape[1], 3), 255.0)
    img = np.concatenate([rows[0], sep_h, rows[1], sep_h, rows[2]], 0)
    images.write_png(path, img.astype(np.uint8))


def main():
    ap = argparse.ArgumentParser(description="Compare the climate model on real Earth with observations")
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--png", help="write a model-vs-observed map (rows: Koppen, precip, temp; "
                                  "left model, right observed)")
    ap.add_argument("--json", help="dump the key numbers as JSON")
    ap.add_argument("--width", type=int, default=720, help="PNG panel width in pixels")
    a = ap.parse_args()
    grid, d, c, times = run(a.level)
    R = analyse(grid, d, c)
    R["systematic_errors"] = systematic_errors(R)
    R["level"] = a.level
    print(report(R, times, a.level))
    if a.json:
        Path(a.json).write_text(json.dumps(R, indent=1, default=float))
        print(f"\nwrote {a.json}")
    if a.png:
        render(a.png, grid, d, c, a.width)
        print(f"wrote {a.png}")


if __name__ == "__main__":
    main()
