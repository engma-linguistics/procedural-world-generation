"""Lane 125: cloud, shade, sunshine and coldest-month temperature of warm land by rain band and region:
the Earth model-climate run vs observed (CRU sunshine, NCEP temperature, GPCC rain), then finished worlds.

    PYTHONPATH=. uv run python docs/review/base-climate/tropical-cloud/bands.py earth OUT.npz
    PYTHONPATH=. PLANET_DATA=<root> uv run python docs/review/base-climate/tropical-cloud/bands.py tables OUT.npz WORLD...

'earth' runs vegetation.coupled_climate on Earth at L7 (reads the worktree's private data/earth copy, as
docs/review/base-climate/summer-heat/diag.py base) and saves the fields. 'tables' prints the tables.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate  # noqa: E402

REG = [("Sahel", 10, 16, -15, 30), ("E Africa", -5, 5, 34, 42), ("S Africa savanna", -25, -10, 15, 35),
       ("India", 10, 28, 72, 88), ("N Australia", -20, -11, 125, 145), ("Brazil cerrado", -20, -8, -55, -42)]
BANDS = [(400, 900), (900, 1500), (1500, 6000)]
mode = sys.argv[1]


def wm(x, m, w):
    m = m & np.isfinite(x)
    return float((x * w)[m].sum() / w[m].sum()) if m.sum() else float("nan")


def earth():
    from planet import vegetation
    from planet.grid import build_grid
    from tools import earth_data
    g = build_grid(7)
    d = earth_data.earth_on_grid(g)
    cl = earth_data.earth_clouds(g)
    elev, ice = d["elev"].astype(float), d["ice"].astype(float)
    c, _ = vegetation.coupled_climate(g, elev, 0.0, 23.4, ice)
    dh = climate.day_hours(g.lat, 23.4)
    np.savez_compressed(sys.argv[2], lat=g.lat, lon=g.lon, land=earth_data.land_of(d), ice=ice,
                        w=earth_data.cell_areas(g),
                        m_T=c["temp"], m_tw=c["t_warm"], m_tc=c["t_cold"], m_P=c["precip"],
                        m_pj=c["p_jul"], m_pn=c["p_jan"],
                        m_cj=c["cloud_jul"], m_cn=c["cloud_jan"], m_shj=c["shade_jul"], m_shn=c["shade_jan"],
                        m_sunj=c["sun_jul"] / np.maximum(dh[0], 1e-6), m_sunn=c["sun_jan"] / np.maximum(dh[1], 1e-6),
                        o_T=d["obs_temp"], o_tw=d["obs_t_warm"], o_tc=d["obs_t_cold"], o_P=d["obs_precip"],
                        o_pj=d["obs_p_jul"], o_pn=d["obs_p_jan"], o_sunj=cl["obs_sun_jul"], o_sunn=cl["obs_sun_jan"],
                        o_ncepj=cl["obs_cloud_ncep_jul"], o_ncepn=cl["obs_cloud_ncep_jan"])
    print("saved")


def row(tag, m, w, F):
    print(f"{tag:26} n={int(m.sum()):5d} P={wm(F['P'], m, w):5.0f} MAT={wm(F['T'], m, w):5.1f} "
          f"Tcold={wm(F['tc'], m, w):5.1f} Twarm={wm(F['tw'], m, w):5.1f} sky={wm(F['sky'], m, w):.2f} "
          f"sun={wm(F['sun'], m, w):.2f} shade={wm(F['shade'], m, w):.2f}")


def tables():
    z = np.load(sys.argv[2])
    lat, lon, w = z["lat"], z["lon"], z["w"]
    land = z["land"] & (z["ice"] <= 0)
    avg = lambda a, b: 0.5 * (z[a] + z[b])  # noqa: E731
    shade_o = lambda s: climate.shade(s)  # noqa: E731
    M = dict(P=z["m_P"], T=z["m_T"], tc=z["m_tc"], tw=z["m_tw"], sky=avg("m_cj", "m_cn"),
             sun=avg("m_sunj", "m_sunn"), shade=avg("m_shj", "m_shn"))
    O = dict(P=z["o_P"], T=z["o_T"], tc=z["o_tc"], tw=z["o_tw"], sky=avg("o_ncepj", "o_ncepn"),
             sun=avg("o_sunj", "o_sunn"), shade=0.5 * (shade_o(z["o_sunj"]) + shade_o(z["o_sunn"])))
    for name, F, Pm, Tm in (("EARTH MODEL (mask: model rain, model T)", M, M["P"], M["T"]),
                            ("EARTH MODEL (mask: observed rain and T)", M, O["P"], O["T"]),
                            ("EARTH OBSERVED (CRU sun, NCEP cloud/T, GPCC rain; mask observed)", O, O["P"], O["T"]),
                            ("EARTH MODEL, same cells (rain in band in model AND observed)", M, None, O["T"]),
                            ("EARTH OBSERVED, same cells (rain in band in model AND observed)", O, None, O["T"])):
        warm = land & (Tm > 18) & (np.abs(lat) < 35)
        print("\n" + name)

        def inband(p0, p1):
            if Pm is not None:
                return (Pm >= p0) & (Pm < p1)
            return (M["P"] >= p0) & (M["P"] < p1) & (O["P"] >= p0) & (O["P"] < p1)

        for p0, p1 in BANDS:
            row(f"all {p0}-{p1}", warm & inband(p0, p1), w, F)
        for rn, a, b, lo, hi in REG:
            rm = warm & (lat >= a) & (lat <= b) & (lon >= lo) & (lon <= hi)
            for p0, p1 in BANDS:
                if (rm & inband(p0, p1)).sum() >= 5:
                    row(f"{rn} {p0}-{p1}", rm & inband(p0, p1), w, F)


def worlds():
    from planet import store as S, world as W
    from planet.geo import is_land
    for wid in sys.argv[3:]:
        wd = W.load(S.find_world(wid))
        g, L = wd["grid"], wd["layers"]
        a = lambda k: np.asarray(L[k], float)  # noqa: E731
        land = is_land(a("elevation"), a("ice")) & (a("ice") <= 0) & ~(np.asarray(L["lake"]) > 0)
        dh = climate.day_hours(g.lat, 23.4)
        sj, sn = a("sunshine_jul") / np.maximum(dh[0], 1e-6), a("sunshine_jan") / np.maximum(dh[1], 1e-6)
        F = dict(P=0.5 * (a("precipitation_jul") + a("precipitation_jan")), T=a("temperature"), tc=a("cold_month"),
                 tw=a("warm_month"), sky=0.01 * 0.5 * (a("cloud_jul") + a("cloud_jan")), sun=0.5 * (sj + sn),
                 shade=0.5 * (climate.shade(sj) + climate.shade(sn)))
        w = np.ones(g.n)  # (area weights: the cells are near equal-area)
        warm = land & (F["T"] > 18) & (np.abs(g.lat) < 35)
        print(f"\nWORLD {wid} L{g.level}")
        for p0, p1 in BANDS:
            row(f"all {p0}-{p1}", warm & (F["P"] >= p0) & (F["P"] < p1), w, F)


{"earth": earth, "tables": tables, "worlds": worlds}[mode]()
