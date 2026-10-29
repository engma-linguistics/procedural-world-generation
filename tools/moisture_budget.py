"""Moisture budget of the climate model on the real Earth (PW-014).

    PYTHONPATH=. uv run python tools/moisture_budget.py [--level 6] [--json out.json]

Runs the model's climate on Earth's terrain (as tools/earth_check.py does:
dT 0, tilt 23.4, the vegetation's feedbacks) with the rain kernel's inputs
recorded, then re-runs the kernel in an instrumented copy (_probe: the
same arithmetic as climate._rain, plus tagged water tracers and a split of
every term; tests/test_moisture_budget.py checks the copy reproduces the
model's rain bit for bit). Reports:

  basins     E, P, river runoff and E-P-R per ocean basin (Atlantic,
             Pacific, Indian, Arctic, Southern = south of 35S, Mediterranean
             and the seas cut off from the world ocean), model vs NCEP E -
             GPCP P, and published fresh-water budgets
  exchange   where each drainage basin's evaporation rains out (tracers),
             and the net vapour flux across the drainage divides: Central
             America, the Andes, the Rockies, Africa, Eurasia
  zonal      zonal-mean E-P (sea and all), model vs NCEP/GPCP
  inland     precipitation and column vapour along westerly and monsoon
             paths, model vs GPCC / NCEP precipitable water, by distance
             from the coast; and land rain by distance from the sea
  residence  the vapour's rain-out time and length (days, km)
             and the recycling of land evaporation (tracers; van der Ent
             et al. 2010: 40% of land rain is land-evaporated)
  regions    the kernel's terms per region and half-year (rain parts:
             oversaturation / large-scale / showers; the shower trigger's
             parts; local evaporation; own-region recycling)
  books      the transport's mass residue, split into its causes (PW-304)

Observations (tools/earth_data.py, cached in data/earth): GPCP v2.3 (sea
and land), GPCC (land), NCEP/NCAR reanalysis 1991-2020 latent heat flux
(evaporation), precipitation and precipitable water (a reanalysis, not an
observation: its E is ~10% high and its E-P doesn't close; used for
patterns and the zonal/basin shape, with published numbers alongside).

Units: model rain is scaled as climate.compute scales it (global mean
1000 mm/yr). The kernel's vapour is in _qsat units (1 = saturated surface
air at 0 C); it is turned into a column (mm) by one factor fitted over the
open sea against NCEP precipitable water. The kernel runs in physical
time (PW-015: wind 1 is climate.U_REF m/s); its rain is per time step
(climate._rain_args' dt), the faces' fluxes in model units x m2/s.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import planet  # noqa: E402,F401  (first: its thread caps must precede numpy, planet/parallel.py)
import numpy as np  # noqa: E402
from numba import njit, prange  # noqa: E402
from planet import climate, kernels, vegetation  # noqa: E402
from planet import ocean as ocean_mod  # noqa: E402
from planet.climate import LQ, _budyko1  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools import earth_data  # noqa: E402
from tools.earth_check import REGIONS  # noqa: E402

R_KM = 6371.0
SV_KM3 = 1e6 * 3.15576e7 / 1e9  # km3/yr in one Sverdrup (31,558)
LV = 2.5e6  # J/kg: latent heat of vaporisation (NCEP's E = lhtfl / LV)
YEAR_S = 3.15576e7

BASINS = ["Atlantic", "Pacific", "Indian", "Arctic", "Southern", "Med+inland"]

# Published fresh-water budgets (Sv; + = the ocean loses water to the air, E - P - R), rounded
# ranges from several studies, for scale only. Atlantic north of ~30S, Arctic included unless noted.
PUBLISHED = {
    "Atlantic+Arctic E-P-R": "+0.3..+0.6 Sv (Baumgartner & Reichel 1975; Zaucker & Broecker 1992; "
                             "Talley 2008)",
    "Pacific E-P-R": "about 0 to -0.3 Sv (net gain; same sources)",
    "Indian E-P-R": "about +0.3..+0.6 Sv (net loss; same sources)",
    "Atlantic -> Pacific across Central America": "~0.2-0.3 Sv westward (Zaucker & Broecker 1992; "
                                                 "PW-014's 0.25 Sv)",
    "river runoff": "Atlantic ~0.6 Sv (incl. Mediterranean), Pacific ~0.3, Indian ~0.15, Arctic ~0.1 "
                    "(Dai & Trenberth 2002, approx.)",
    "land recycling": "40% of land precipitation evaporated from land; 57% of land evaporation rains "
                      "on land (van der Ent et al. 2010)",
    "residence time": "~8-10 days for the global atmosphere's water (Trenberth 1998; van der Ent & "
                      "Tuinenburg 2017)",
}

# Paths along which the air carries moisture inland: (name, season, axis, start, end, band lo,
# band hi). axis 'lon': distance along the latitude band from lon start toward end; 'lat': along
# the meridian band. Season: 'jan' (Oct-Mar), 'jul' (Apr-Sep) or 'ann'.
PATHS = [
    ("Eurasia 50-60N, winter westerlies", "jan", "lon", -10, 120, 50, 60),
    ("Europe 43-50N, winter westerlies", "jan", "lon", -5, 60, 43, 50),
    ("N America 40-50N, winter westerlies", "jan", "lon", -124, -65, 40, 50),
    ("N America 30-50N, summer Gulf inflow (S->N)", "jul", "lat", 29, 50, -100, -90),
    ("West Africa monsoon (S->N)", "jul", "lat", 5, 25, -10, 10),
    ("Ganges plain monsoon (E->W)", "jul", "lon", 90, 70, 22, 30),
    ("East Asia monsoon (S->N)", "jul", "lat", 22, 45, 110, 122),
    ("Amazon trades (E->W)", "ann", "lon", -35, -75, -10, 0),
    ("N Australia monsoon (N->S)", "jan", "lat", -12, -32, 125, 145),
]
PATH_BIN_KM = 500.0

# Drainage-divide sections for the vapour flux between drainage basins (basin a -> basin b,
# lat/lon window)
SECTIONS = [
    ("Central America (Atlantic -> Pacific)", "Atlantic", "Pacific", 5, 20, -105, -75),
    ("Andes (Atlantic -> Pacific)", "Atlantic", "Pacific", -35, 5, -85, -60),
    ("N America west (Atlantic -> Pacific)", "Atlantic", "Pacific", 20, 66, -170, -95),
    ("Africa (Atlantic -> Indian)", "Atlantic", "Indian", -35, 35, -20, 60),
    ("Eurasia (Atlantic -> Indian)", "Atlantic", "Indian", 25, 66, -20, 180),
    ("Eurasia (Atlantic -> Pacific)", "Atlantic", "Pacific", 0, 66, 60, 180),
    ("Eurasia (Arctic -> Pacific)", "Arctic", "Pacific", 40, 90, 60, 180),
    ("Eurasia (Arctic -> Atlantic)", "Arctic", "Atlantic", 40, 90, -20, 180),
    ("Eurasia (Arctic -> Indian)", "Arctic", "Indian", 25, 90, 40, 120),
    ("N America (Arctic -> Atlantic)", "Arctic", "Atlantic", 40, 90, -170, -50),
    ("Southern edge (Atlantic -> Southern)", "Atlantic", "Southern", -60, -20, -80, 30),
]

PROBE_REGIONS = ["Sahara", "Sahel", "Arabia", "Australia interior", "Gobi/Mongolia", "Tibet", "Central Asia",
                 "Great Plains", "W Siberia", "European Russia", "W Europe", "India", "SE China", "Amazon",
                 "Congo basin", "SE USA", "Pampas", "Japan", "E Australia", "Mediterranean", "SE Brazil",
                 "Mexico N"]


# --------------------------------------------------------------------------
# the instrumented kernel
# --------------------------------------------------------------------------
@njit(cache=True, parallel=True)
def _probe(qs, src_q, ocean, ls_rate, cv_rate, mse_t, mse_thr, pet, budyko_w, soil_mm, open_sea, c_self, c_in,
           nbr, off, steps, dt, tau_ex, rh_c, rh_pow, cv_scale, evap, mean_mm, m0, un, kd, ea, eb, L, lc,
           tag, ntag):
    """climate._rain, line for line, plus: tracers of the vapour by where it
    evaporated (tag: per cell, 0..ntag-1; a well-mixed column, so each tracer
    is carried as the vapour is and rains its share r/q of the cell's rain),
    and tail means of the land's evaporation, the rain's parts
    (oversaturation, large-scale, showers), the shower trigger's dry part
    (mse_t + tcor - mse_thr, C), the vapour before the rain and the faces'
    fluxes (un, kd: climate.face_winds; the wind's and the eddy mixing's,
    ea -> eb, model units x m2/s). Returns (rain, rain_ls, sea uptake,
    vapour after rain, land evaporation, rain from oversaturation, shower
    rain, trigger's dry part, vapour before rain, rain by tracer
    [S, ntag, n], face flux by the wind [S, ne], by mixing [S, ne])."""
    S, n = qs.shape
    ne = ea.shape[0]
    m = np.ascontiguousarray(m0.T)
    m1 = np.empty((n, S))
    acc = np.zeros((S, n))
    acc_ls = np.zeros((S, n))
    ema = np.zeros((S, n))
    tcor = np.zeros((S, n))
    acc_up = np.zeros((S, n))
    acc_q = np.zeros((S, n))
    land_e = np.zeros((S, n))
    acc_le = np.zeros((S, n))
    acc_ex = np.zeros((S, n))
    acc_cv = np.zeros((S, n))
    acc_dry = np.zeros((S, n))
    acc_qb = np.zeros((S, n))
    acc_fa = np.zeros((S, ne))
    acc_fm = np.zeros((S, ne))
    T = np.zeros((S, ntag, n))
    T1 = np.zeros((S, ntag, n))
    acc_t = np.zeros((S, ntag, n))
    for k in range(S):
        for i in range(n):
            T[k, tag[i], i] = m[i, k]
    tail = max(steps // 4, 1)
    fex = 1.0 - np.exp(-dt / tau_ex)
    scale = 1.0
    for it in range(steps):
        tcor_due = evap != 0 and it >= 20 and it % 10 == 0
        if (it >= 5 and it % 5 == 0) or tcor_due:
            tot = 0.0
            for k in range(S):
                for i in range(n):
                    tot += ema[k, i]
            scale = mean_mm * S * n / max(tot, 1e-12)
        if it >= 5 and it % 5 == 0:
            for i in prange(n):
                if not ocean[i]:
                    aet = np.empty(S)
                    tot_p = 0.0
                    tot_e = 0.0
                    for k in range(S):
                        o = (k - 1) % S
                        p_o = ema[o, i] * scale / S
                        kept = min(p_o - _budyko1(p_o, pet[o, i] / S, budyko_w[i]), soil_mm)
                        p_k = ema[k, i] * scale / S
                        aet[k] = _budyko1(p_k + kept, pet[k, i] / S, budyko_w[i])
                        tot_p += p_k
                        tot_e += aet[k]
                    f = tot_p / tot_e if tot_e > tot_p else 1.0
                    for k in range(S):
                        land_e[k, i] = f * aet[k] * S / scale
        if tcor_due:
            for i in prange(n):
                if not ocean[i]:
                    for k in range(S):
                        lp = np.log10(max(ema[k, i] * scale, 1.0) / 100.0) / 1.2
                        tcor[k, i] = evap * (1.0 - 2.0 * min(max(lp, 0.0), 1.0))
        last = it >= steps - tail
        if last:
            for e in prange(ne):
                a, b = ea[e], eb[e]
                for k in range(S):
                    u = un[k, e]
                    fa = (u * m[a, k] if u > 0 else u * m[b, k]) * L[e]
                    acc_fa[k, e] += fa
                    acc_fm[k, e] += kd[k, e] / lc[e] * (m[a, k] - m[b, k]) * L[e]
        for i in prange(n):
            for k in range(S):
                q = c_self[k, i] * m[i, k]
                for j in range(off[i], off[i + 1]):
                    q += c_in[j, k] * m[nbr[j], k]
                for g in range(ntag):
                    tg = c_self[k, i] * T[k, g, i]
                    for j in range(off[i], off[i + 1]):
                        tg += c_in[j, k] * T[k, g, nbr[j]]
                    T1[k, g, i] = tg
                if ocean[i]:
                    if src_q[k, i] > q:
                        up = open_sea[k, i] * (src_q[k, i] - q)
                        if last:
                            acc_up[k, i] += up
                        q += up
                        T1[k, tag[i], i] += up
                else:
                    q += land_e[k, i]
                    T1[k, tag[i], i] += land_e[k, i]
                    if last:
                        acc_le[k, i] += land_e[k, i]
                excess = max(q - qs[k, i], 0.0)
                rh = min(q / max(qs[k, i], 1e-12) / rh_c, 1.0)
                rate = ls_rate[k, i] * rh**rh_pow
                r_ls = min(rate * dt, 1.0) * (q - excess)
                dry = mse_t[k, i] + tcor[k, i] - mse_thr[k, i]
                inst = (mse_t[k, i] + tcor[k, i] + LQ * q - mse_thr[k, i]) / cv_scale  # (as _rain adds it up)
                if inst > 0:
                    rate += cv_rate[k, i] * min(inst, 2.0)
                r = fex * excess + min(rate * dt, 1.0) * (q - excess)
                m1[i, k] = q - r
                ema[k, i] += 0.05 * (r - ema[k, i])
                share = r / q if q > 0 else 0.0
                for g in range(ntag):
                    rg = T1[k, g, i] * share
                    T1[k, g, i] -= rg
                    if last:
                        acc_t[k, g, i] += rg
                if last:
                    acc[k, i] += r
                    acc_ls[k, i] += r_ls
                    acc_q[k, i] += q - r
                    acc_ex[k, i] += fex * excess
                    acc_cv[k, i] += r - fex * excess - r_ls
                    acc_dry[k, i] += dry
                    acc_qb[k, i] += q
        m, m1 = m1, m
        T, T1 = T1, T
    return (acc / tail, acc_ls / tail, acc_up / tail, acc_q / tail, acc_le / tail, acc_ex / tail, acc_cv / tail,
            acc_dry / tail, acc_qb / tail, acc_t / tail, acc_fa / tail, acc_fm / tail)


def kernel_args(rec: dict) -> tuple:
    """climate.rain's arguments to climate._rain, from a recorded call."""
    return climate._rain_args(*(rec[k] for k in ("grid", "elev", "s_in", "tune", "pet", "w", "open_sea", "ocean")))


def probe(rec: dict, tag: np.ndarray, ntag: int) -> dict:
    """Run the instrumented kernel on a recorded climate.rain call."""
    a = kernel_args(rec)
    F = climate._faces(rec["grid"])
    un, kd = climate.face_winds(rec["grid"], rec["s_in"], rec["tune"])
    out = _probe(*a[:-2], un, kd, F["ea"], F["eb"], F["L"], F["lc"], np.ascontiguousarray(tag, np.int64), int(ntag))
    keys = ("r", "r_ls", "up", "q", "land_e", "r_ex", "r_cv", "dry", "q_before", "r_tag", "f_adv", "f_mix")
    P = dict(zip(keys, out))
    P["dt"] = a[16]
    return P


def capture(grid, elev, ice, compute=None):
    """The Earth climate as earth_check makes it, with the last climate.rain
    call's inputs and outputs recorded (rec). Returns (climate, rec)."""
    rec = {}
    orig = climate.rain

    def recording(grid_, elev_, seasons_in, tune, pet, w=None, open_sea=None, ocean=None, start=None):
        out = orig(grid_, elev_, seasons_in, tune, pet, w, open_sea, ocean, start)
        rec.clear()
        rec.update(grid=grid_, elev=elev_, s_in=seasons_in, tune=tune, pet=pet, w=w, open_sea=open_sea,
                   ocean=ocean, out=out)
        return out

    climate.rain = recording
    try:
        c = (compute or (lambda: vegetation.coupled_climate(grid, elev, 0.0, 23.4, ice)[0]))()
    finally:
        climate.rain = orig
    return c, rec


# --------------------------------------------------------------------------
# masks
# --------------------------------------------------------------------------
def basins(grid, elev) -> np.ndarray:
    """Ocean basin of each sea cell (index into BASINS; -1 on land).
    Southern: south of 35S. Arctic: north of 66N, but the Nordic seas (45W-20E,
    south of 80N) are the Atlantic's. Mediterranean (with the Black Sea) and
    seas cut off from the world ocean (Caspian): 'Med+inland'. Indian: 20-100E
    north of 35S, and the seas off NW Australia (100-130E south of 8S); the
    Indonesian seas are the Pacific's. Atlantic vs Pacific: the two sides of
    the Americas (connected sea, with Panama walled off)."""
    lat, lon = grid.lat, grid.lon
    sea = elev <= 0
    lab = np.full(grid.n, -1)
    comp, k = grid.components(sea)
    world = np.argmax(np.bincount(comp[comp >= 0], minlength=k))
    inland = sea & (comp != world)
    med = sea & (((lat > 30) & (lat < 46) & (lon > -5.6) & (lon < 37) & ~((lat > 42.5) & (lon < 3)))
                 | ((lat > 40) & (lat < 47.5) & (lon > 27) & (lon < 42)))
    south = sea & (lat <= -35)
    arctic = sea & (lat >= 66) & ~((lon > -45) & (lon < 20) & (lat < 80))
    indian = sea & (lat > -35) & (lat < 31) & (((lon >= 20) & (lon < 100))
                                               | ((lon >= 100) & (lon < 130) & (lat < -8))
                                               | ((lon >= 100) & (lon < 105) & (lat < 6)))
    for b, msk in ((5, inland | med), (4, south), (3, arctic), (2, indian)):
        lab[msk & (lab < 0)] = b
    rest = sea & (lab < 0)
    wall = (lon > -84) & (lon < -77) & (lat > 6.5) & (lat < 10.5)
    comp2, k2 = grid.components(rest & ~wall)
    seed = {0: (30.0, -40.0), 1: (0.0, -160.0)}
    for b, (la, lo) in seed.items():
        q = earth_data._unit(np.array([la]), np.array([lo]))[0]
        i = int(np.argmax(np.where(rest & ~wall, grid.centers @ q, -2)))
        lab[(comp2 == comp2[i]) & rest & ~wall] = b
    # leftovers (the Panama wall, small bays cut off at this level): the nearest labelled sea
    left = np.flatnonzero(sea & (lab < 0))
    while len(left):
        for i in left:
            nb = grid.nbr_idx[grid.nbr_off[i]:grid.nbr_off[i + 1]]
            nb = nb[lab[nb] >= 0]
            if len(nb):
                lab[i] = np.bincount(lab[nb]).argmax()
        new = np.flatnonzero(sea & (lab < 0))
        if len(new) == len(left):
            lab[new] = 1
            break
        left = new
    return lab


def drainage(grid, elev, surf, basin) -> np.ndarray:
    """Basin of every cell: the sea's own, and for land the basin its rivers
    reach (routed downhill as ocean.river_input routes the runoff)."""
    sea = elev <= 0
    _, down, order = kernels.priority_flood(np.where(sea, np.minimum(surf, 0.0), np.maximum(surf, 1e-3)),
                                            grid.nbr_off, grid.nbr_idx, 0.01)
    lab = np.where(sea, basin, -1)
    for i in order:
        if not sea[i] and down[i] >= 0:
            lab[i] = lab[down[i]]
    return lab


def coast_distance(grid, sea) -> np.ndarray:
    """km from each cell to the nearest sea cell (graph hops x spacing)."""
    h = grid.spacing * R_KM
    d = np.where(sea, 0, -1)
    front = np.flatnonzero(sea)
    k = 0
    while len(front):
        k += 1
        nb = np.concatenate([grid.nbr_idx[grid.nbr_off[i]:grid.nbr_off[i + 1]] for i in front]) \
            if len(front) < 2000 else _nbrs_of(grid, front)
        nb = np.unique(nb[d[nb] < 0])
        d[nb] = k
        front = nb
    return np.where(d < 0, 0, d) * h


def _nbrs_of(grid, cells):
    off, idx = grid.nbr_off, grid.nbr_idx
    cnt = off[cells + 1] - off[cells]
    start = np.repeat(off[cells], cnt)
    step = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
    return idx[start + step]


def region_mask(grid, a0, a1, o0, o1):
    lat, lon = grid.lat, grid.lon
    return (lat >= a0) & (lat <= a1) & (lon >= o0) & (lon <= o1)


# --------------------------------------------------------------------------
# observations
# --------------------------------------------------------------------------
def observations(grid) -> dict:
    """NCEP E, P, precipitable water on the grid (annual and half-years)."""
    out = {}

    def halves(m):  # monthly (12, n) means -> (annual, Apr-Sep, Oct-Mar) means
        return m.mean(0), m[3:9].mean(0), np.concatenate([m[:3], m[9:]]).mean(0)

    for key, name, f in (("ncep_lhtfl", "e", YEAR_S / LV), ("ncep_prate", "p", YEAR_S), ("ncep_pwat", "pw", 1.0)):
        try:
            r = earth_data.raster(key)
        except RuntimeError as e:  # (PSL's servers rate-limit; the rest of the budget still runs)
            print(f"  no {key}: {e}")
            out[name] = out[name + "_jul"] = out[name + "_jan"] = np.full(grid.n, np.nan)
            continue
        v = np.where(np.abs(r["val"]) > 1e20, np.nan, r["val"]).astype(np.float64) * f
        m = earth_data._bilinear(r, v, grid.lat, grid.lon)
        if name == "pw":
            m = np.maximum(m, 0.0)  # (a few slightly negative values over the poles)
        out[name], out[name + "_jul"], out[name + "_jan"] = halves(m)

    return out


# --------------------------------------------------------------------------
# the budget
# --------------------------------------------------------------------------
def mm_scale(c, rec) -> float:
    """Model rain units -> mm/yr, as compute scales them."""
    r_jul, r_jan = rec["out"][0]
    p = c["precip"]
    return float(p.mean() / max((0.5 * (r_jul + r_jan)).mean(), 1e-12))


def edge_fluxes(grid, P, sc) -> dict:
    """Tail-mean vapour flux through each face (climate._faces: from ea to
    eb), per season, in km3/yr of water: the wind's (adv) and the eddy
    mixing's (mix). sc: model rain units per step -> mm/yr (mm_scale)."""
    F = climate._faces(grid)
    k = P["dt"] * sc * 1e-12  # (model units x m2/s) -> km3/yr
    return dict(adv=P["f_adv"] * k, mix=P["f_mix"] * k, a=F["ea"], b=F["eb"])


def analyse(grid, d, c, rec) -> dict:
    lat, lon = grid.lat, grid.lon
    area = ocean_mod.cell_area_km2(grid)
    # (the land by its ice surface: the bed under the ice is the true one,
    # below the sea in West Antarctica and central Greenland, PW-354)
    surf = d["elev"].astype(np.float64) + d["ice"].astype(np.float64)
    sea = ~earth_data.land_of(d)
    land = ~sea
    basin = basins(grid, surf)
    drain = drainage(grid, surf, surf, basin)
    NB = len(BASINS)
    sc = mm_scale(c, rec)
    obs = observations(grid)
    R = dict(level=grid.level, cell_km=float(grid.spacing * R_KM))

    # ---- the probe: tracers by drainage basin and sea/land
    tag = np.where(sea, basin, NB + np.maximum(drain, 0))
    t0 = time.time()
    P1 = probe(rec, tag, 2 * NB)
    print(f"  probe 1: {time.time() - t0:.0f} s", file=sys.stderr)
    R["probe_matches_model"] = bool(np.array_equal(storm_mixed(grid, rec, P1["r"], P1["r_ls"]), rec["out"][0]))
    # ---- the probe: tracers by region (land), other land, sea
    regs = [r for r in REGIONS if r[0] in PROBE_REGIONS]
    rtag = np.where(sea, 0, 1)
    for k, (name, a0, a1, o0, o1) in enumerate(regs):
        rtag[land & region_mask(grid, a0, a1, o0, o1) & (rtag == 1)] = 2 + k
    t0 = time.time()
    P2 = probe(rec, rtag, 2 + len(regs))
    print(f"  probe 2: {time.time() - t0:.0f} s", file=sys.stderr)

    S = 2
    P_mm = np.stack([c["p_jul"], c["p_jan"]])  # mm/yr rate per half-year (the model's, storms' spread included)
    E_sea = P1["up"] * sc
    E_land = P1["land_e"] * sc
    E_all = E_sea + E_land
    Pann, Eann = P_mm.mean(0), E_all.mean(0)

    # ---- river runoff into each basin: the model's water balance runoff, routed
    # (Earth's closed basins, HydroSHEDS: their runoff evaporates inland and reaches no sea)
    closed = earth_data.earth_closed(grid) >= 0 if grid.level >= 5 else np.zeros(grid.n, bool)
    runoff = np.where(land & ~closed, c["runoff"], 0.0)
    R["closed_runoff_sv"] = km3_(np.where(land & closed, c["runoff"], 0.0), area) / SV_KM3
    km3 = lambda x_mm, m: float((x_mm * area)[m].sum() * 1e-6)  # mm/yr over km2 -> km3/yr
    rows = []
    gp = np.nan_to_num(d["obs_gpcp"].astype(np.float64))
    for b, name in enumerate(BASINS):
        m = sea & (basin == b)
        cm = land & (drain == b)
        e, p = km3(Eann, m), km3(Pann, m)
        rr = km3(runoff, cm)
        oe, op = km3(np.nan_to_num(obs["e"]), m), km3(gp, m)
        onp = km3(np.nan_to_num(obs["p"]), m)
        rows.append(dict(basin=name, area_mkm2=float(area[m].sum() / 1e6), E_sv=e / SV_KM3, P_sv=p / SV_KM3,
                         R_sv=rr / SV_KM3, EPR_sv=(e - p - rr) / SV_KM3, EP_mm=(e - p) / max(area[m].sum(), 1) * 1e6,
                         obs_E_sv=oe / SV_KM3, obs_P_gpcp_sv=op / SV_KM3, obs_EP_sv=(oe - op) / SV_KM3,
                         obs_EP_ncep_sv=(oe - onp) / SV_KM3,
                         obs_EP_mm=(oe - op) / max(area[m].sum(), 1) * 1e6))
    R["basins"] = rows
    # Atlantic + Arctic
    aa = [r for r in rows if r["basin"] in ("Atlantic", "Arctic")]
    R["atlantic_arctic_EPR_sv"] = sum(r["EPR_sv"] for r in aa)
    R["atlantic_arctic_obs_EP_sv"] = sum(r["obs_EP_sv"] for r in aa)

    # ---- where each drainage basin's evaporation rains (tracers), km3/yr -> Sv
    rt = P1["r_tag"] * sc  # (S, 2NB, n) mm/yr
    rain_from = rt.mean(0)  # annual
    dest = np.where(sea, basin, drain)
    mat = np.zeros((NB, NB))
    for s in range(NB):  # source drainage basin = its sea + its land
        src = rain_from[s] + rain_from[NB + s]
        for t in range(NB):
            mat[s, t] = km3(src, dest == t) / SV_KM3
    evap_by = np.array([km3(Eann, dest == s) / SV_KM3 for s in range(NB)])
    R["exchange"] = dict(basins=BASINS, rain_sv=mat.tolist(), evap_sv=evap_by.tolist(),
                         net_export_sv=[float(mat[s].sum() - mat[s, s] - (mat[:, s].sum() - mat[s, s]))
                                        for s in range(NB)])

    # ---- vapour flux across drainage divides (each face once, + from its a to its b)
    F = edge_fluxes(grid, P1, sc)
    fa, fb = F["a"], F["b"]
    sec_rows = []
    for name, a, b, a0, a1, o0, o1 in SECTIONS:
        ia, ib = BASINS.index(a), BASINS.index(b)
        win = region_mask(grid, a0, a1, o0, o1)
        inw = win[fa] & win[fb]
        sgn = np.where((dest[fa] == ia) & (dest[fb] == ib) & inw, 1.0,
                       np.where((dest[fa] == ib) & (dest[fb] == ia) & inw, -1.0, 0.0))
        tot = [float(((F["adv"][k] + F["mix"][k]) * sgn).sum() / SV_KM3) for k in range(S)]
        sec_rows.append(dict(section=name, jul_sv=tot[0], jan_sv=tot[1], ann_sv=float(np.mean(tot)),
                             edges=int((sgn != 0).sum())))
    R["sections"] = sec_rows

    # ---- northward vapour transport across latitude circles (Sv): the kernel's face fluxes (the wind's
    # and the eddy mixing's), and what the E - P south of each circle implies, model and NCEP E - GPCP P
    # (the observed global mean E - P taken off: NCEP's E runs high)
    ep_o = np.where(np.isfinite(obs["e"]), obs["e"], Eann) - np.where(np.isfinite(gp), gp, Pann)
    ep_o = ep_o - (ep_o * area).sum() / area.sum()
    ep_m = Eann - Pann
    mer = []
    for phi in range(-70, 80, 10):
        sgn = np.where((lat[fa] < phi) & (lat[fb] >= phi), 1.0, np.where((lat[fb] < phi) & (lat[fa] >= phi), -1.0, 0.0))
        adv = np.mean([(F["adv"][k] * sgn).sum() for k in range(S)]) / SV_KM3
        mix = np.mean([(F["mix"][k] * sgn).sum() for k in range(S)]) / SV_KM3
        south = lat < phi
        mer.append(dict(lat=phi, adv_sv=float(adv), eddy_sv=float(mix),
                        implied_sv=km3(ep_m, south) / SV_KM3, obs_implied_sv=km3(ep_o, south) / SV_KM3))
    R["meridional"] = mer

    # ---- zonal-mean E - P (10 deg bands), sea and all
    zon = []
    for lo in range(-80, 90, 10):
        bm = (lat >= lo) & (lat < lo + 10)
        row = dict(band=f"{lo}..{lo + 10}")
        for nm, msk in (("sea", bm & sea), ("all", bm)):
            if area[msk].sum() == 0:
                continue
            wm = lambda x: float((x * area)[msk].sum() / area[msk].sum())
            row[f"{nm}_E"], row[f"{nm}_P"] = wm(Eann), wm(Pann)
            ok = msk & np.isfinite(obs["e"]) & np.isfinite(gp)
            row[f"{nm}_obs_E"] = float((obs["e"] * area)[ok].sum() / area[ok].sum())
            row[f"{nm}_obs_P"] = float((gp * area)[ok].sum() / area[ok].sum())
        zon.append(row)
    R["zonal"] = zon

    # ---- column vapour: model q -> mm via one factor fitted over the open sea
    q_b = P1["q_before"]
    qcol = q_b.mean(0)
    fit = sea & (np.abs(lat) < 60) & np.isfinite(obs["pw"])
    k_pw = float((qcol[fit] * obs["pw"][fit] * area[fit]).sum() / (qcol[fit] ** 2 * area[fit]).sum())
    R["pw_mm_per_unit"] = k_pw
    pw_m = [q_b[0] * k_pw, q_b[1] * k_pw]

    # ---- inland paths
    obs_pj, obs_pn = d["obs_p_jul"].astype(np.float64), d["obs_p_jan"].astype(np.float64)
    seas = dict(jul=(P_mm[0], obs_pj, pw_m[0], obs["pw_jul"]), jan=(P_mm[1], obs_pn, pw_m[1], obs["pw_jan"]),
                ann=(Pann, d["obs_precip"].astype(np.float64), 0.5 * (pw_m[0] + pw_m[1]), obs["pw"]))
    paths = []
    for name, season, axis, start, end, b0, b1 in PATHS:
        pm, po, wm_, wo = seas[season]
        if axis == "lon":
            band = land & (lat >= b0) & (lat < b1)
            x = (lon - start) * np.sign(end - start) * 111.2 * np.cos(np.radians(lat))
            xmax = abs(end - start) * 111.2 * np.cos(np.radians(0.5 * (b0 + b1)))
        else:
            band = land & (lon >= b0) & (lon < b1)
            x = (lat - start) * np.sign(end - start) * 111.2
            xmax = abs(end - start) * 111.2
        bins = []
        for j in range(int(np.ceil(xmax / PATH_BIN_KM))):
            m = band & (x >= j * PATH_BIN_KM) & (x < (j + 1) * PATH_BIN_KM) & np.isfinite(po)
            if area[m].sum() == 0:
                continue
            wmean = lambda f: float((f * area)[m].sum() / area[m].sum())
            bins.append(dict(km=(j + 0.5) * PATH_BIN_KM, P=wmean(pm), P_obs=wmean(po), PW=wmean(wm_),
                             PW_obs=wmean(np.nan_to_num(wo)), cells=int(m.sum())))
        paths.append(dict(path=name, season=season, bins=bins, decay=_decay(bins)))
    R["paths"] = paths

    # land rain by distance from the sea (all land outside Antarctica / Greenland's ice)
    dist = coast_distance(grid, sea)
    dd = []
    nl = land & (lat > -60) & (d["ice"] <= 0) & np.isfinite(d["obs_precip"])
    for lo_, hi_ in ((0, 1), (1, 300), (300, 600), (600, 1000), (1000, 1500), (1500, 2500), (2500, 9e9)):
        m = nl & (dist >= lo_) & (dist < hi_)
        if area[m].sum() == 0:
            continue
        wmean = lambda f: float((f * area)[m].sum() / area[m].sum())
        dd.append(dict(km=f"{lo_:.0f}-{hi_:.0f}" if hi_ < 1e9 else f">{lo_:.0f}", P=wmean(Pann),
                       P_obs=wmean(d["obs_precip"].astype(np.float64)), PW=wmean(0.5 * (pw_m[0] + pw_m[1])),
                       PW_obs=wmean(np.nan_to_num(obs["pw"])), area_mkm2=float(area[m].sum() / 1e6)))
    R["coast_distance"] = dd

    # ---- residence time and rain-out length, recycling
    dt = P1["dt"]
    wind = [np.linalg.norm(s["v"], axis=1) * climate.U_REF for s in rec["s_in"]]  # m/s
    res = []
    for k, nm in enumerate(("jul", "jan")):
        qm = (q_b[k] * area).sum() / area.sum()
        rm = (P1["r"][k] * area).sum() / area.sum()
        tau_s = qm / rm * dt
        mv = float((wind[k] * area).sum() / area.sum())
        res.append(dict(season=nm, tau_hours=float(tau_s / 3600), length_km=float(tau_s * mv / 1000),
                        wind_mean=mv))
    pw_o = np.nan_to_num(obs["pw"])
    ok = np.isfinite(obs["pw"]) & np.isfinite(gp)
    res_obs_days = float((pw_o * area)[ok].sum() / (gp * area)[ok].sum() * 365.25)
    R["residence"] = dict(model=res, obs_days_pw_over_gpcp=res_obs_days)
    land_rain = (Pann * area)[land].sum()
    from_land = (rain_from[NB:].sum(0) * area)[land].sum()
    land_evap = (Eann * area)[land].sum()
    land_evap_on_land = (rain_from[NB:].sum(0) * area)[land].sum()
    R["recycling"] = dict(land_rain_from_land_pct=100 * float(from_land / land_rain),
                          land_evap_rains_on_land_pct=100 * float(land_evap_on_land / land_evap))

    # ---- the kernel's terms per region and half-year
    rr = []
    tags_rain = P2["r_tag"]
    for k_r, (name, a0, a1, o0, o1) in enumerate(regs):
        m = land & region_mask(grid, a0, a1, o0, o1)
        if not m.any():
            continue
        for k, nm in enumerate(("jul", "jan")):
            wmean = lambda f: float((f * area)[m].sum() / area[m].sum())
            r_ = wmean(P1["r"][k])
            q_ = wmean(q_b[k])
            obs_p = (obs_pj, obs_pn)[k]
            row = dict(region=name, season=nm, P=wmean(P_mm[k]),
                       P_obs=float((np.nan_to_num(obs_p) * area)[m & np.isfinite(obs_p)].sum()
                                   / max(area[m & np.isfinite(obs_p)].sum(), 1e-9)),
                       PW=wmean(pw_m[k]), PW_obs=wmean(np.nan_to_num((obs["pw_jul"], obs["pw_jan"])[k])),
                       rh=wmean(q_b[k] / rec["s_in"][k]["qs"]), rainout_per_day=r_ / max(q_, 1e-12) * 86400 / dt,
                       ex_pct=100 * wmean(P1["r_ex"][k]) / max(r_, 1e-12),
                       ls_pct=100 * wmean(P1["r_ls"][k]) / max(r_, 1e-12),
                       cv_pct=100 * wmean(P1["r_cv"][k]) / max(r_, 1e-12),
                       dry_C=wmean(P1["dry"][k]), lq_C=wmean(LQ * q_b[k]),
                       evap_over_P=wmean(P1["land_e"][k]) / max(r_, 1e-12),
                       land_origin_pct=100 * wmean(rain_from_season(P1, k, NB, land_tags=True)) / max(r_, 1e-12),
                       own_region_pct=100 * wmean(tags_rain[k, 2 + k_r]) / max(r_, 1e-12),
                       wind=wmean(wind[k]))
            # rain efficiency (rain per unit of column vapour) relative to the observed one
            row["eff_ratio"] = (row["P"] / max(row["PW"], 1e-9)) / max(row["P_obs"] / max(row["PW_obs"], 1e-9), 1e-9)
            rr.append(row)
    R["regions"] = rr

    # ---- the books: global steady-state residue (area-weighted). The transport keeps the vapour's
    # mass exactly, so what is left is the steady state's drift over the tail
    books = []
    A = area / area.mean()
    for k, nm in enumerate(("jul", "jan")):
        src = P1["up"][k] + P1["land_e"][k]
        tot = (A * (src - P1["r"][k])).sum() / (A * P1["r"][k]).sum()
        books.append(dict(season=nm, net_src_minus_rain_pct=100 * float(tot)))
    R["books"] = books
    R["books_note"] = ("net = (E - P)/P over the globe in the kernel's steady state: the transport is "
                       "conservative, so this is the vapour's drift over the averaging tail.")
    R["freshwater_mean_m_yr"] = float(np.mean(c.get("freshwater", np.zeros(1))))
    return R


def headlines(R) -> dict:
    """The few numbers PW-015's steps are judged by, out of analyse()'s result (earth_check and the
    scorecard store them): basin E-P-R (Sv, with NCEP E - GPCP P before runoff beside it), the
    Atlantic-minus-Pacific E-P-R per area (mm/yr), northward vapour transport at 40S and 50N (Sv, with what
    the E - P south of the circle implies), sea P at 50-60S (mm/yr), the rain efficiency (P/PW over the
    observed P/PW) over the probe regions' half-years, and the kernel's mass residue (% of rain)."""
    b = {r["basin"]: r for r in R["basins"]}
    H = {}
    for n in ("Atlantic", "Pacific", "Indian"):
        H[f"{n.lower()}_epr_sv"] = round(b[n]["EPR_sv"], 3)
        H[f"{n.lower()}_obs_ep_sv"] = round(b[n]["obs_EP_sv"], 3)
    per_area = {n: (b[n]["EPR_sv"] * SV_KM3 / b[n]["area_mkm2"]) for n in ("Atlantic", "Pacific")}  # km3/Mkm2 = mm
    H["atl_minus_pac_epr_mm"] = round(per_area["Atlantic"] - per_area["Pacific"])
    mer = {r["lat"]: r for r in R["meridional"]}
    for tag, phi in (("s40", -40), ("n50", 50)):
        H[f"transport_{tag}_sv"] = round(mer[phi]["adv_sv"] + mer[phi]["eddy_sv"], 3)
        H[f"transport_{tag}_implied_sv"] = round(mer[phi]["obs_implied_sv"], 3)
    z = next(r for r in R["zonal"] if r["band"] == "-60..-50")
    H["sea_p_50_60s_mm"], H["sea_p_50_60s_obs_mm"] = round(z["sea_P"]), round(z["sea_obs_P"])
    eff = [(r["eff_ratio"], f"{r['region']} {r['season']}") for r in R["regions"]]
    H["rain_eff_median"] = round(float(np.median([e for e, _ in eff])), 2)
    w = max(eff, key=lambda e: abs(np.log(max(e[0], 1e-6))))
    H["rain_eff_worst"], H["rain_eff_worst_where"] = round(float(w[0]), 2), w[1]
    H["mass_residue_pct"] = [round(r["net_src_minus_rain_pct"], 2) for r in R["books"]]  # Apr-Sep, Oct-Mar
    return H


def headline_lines(H) -> list[str]:
    """headlines() as report lines (targets from docs/proposals/moisture_transport.md section 8)."""
    return [
        f"E-P-R (Sv; + loses water; obs = NCEP E - GPCP P before runoff, an upper bound; literature E-P-R "
        f"Atlantic+Arctic +0.3..+0.6): Atlantic {H['atlantic_epr_sv']:+.2f} "
        f"(obs {H['atlantic_obs_ep_sv']:+.2f}), Pacific {H['pacific_epr_sv']:+.2f} (obs {H['pacific_obs_ep_sv']:+.2f}), "
        f"Indian {H['indian_epr_sv']:+.2f} (obs {H['indian_obs_ep_sv']:+.2f}); Atlantic minus Pacific "
        f"{H['atl_minus_pac_epr_mm']:+d} mm/yr per area (PW-016 needs >= +100, Atlantic >= +0.25)",
        f"northward vapour transport (Sv): 40S {H['transport_s40_sv']:+.2f} (implied {H['transport_s40_implied_sv']:+.2f}), "
        f"50N {H['transport_n50_sv']:+.2f} (implied {H['transport_n50_implied_sv']:+.2f}); "
        f"sea P at 50-60S {H['sea_p_50_60s_mm']} mm/yr (GPCP {H['sea_p_50_60s_obs_mm']})",
        f"rain efficiency (P/PW over observed) in the probe regions: median {H['rain_eff_median']:.2f}, worst "
        f"{H['rain_eff_worst']:.2f} ({H['rain_eff_worst_where']}); kernel mass residue "
        f"{H['mass_residue_pct'][0]:+.2f} / {H['mass_residue_pct'][1]:+.2f}% of rain (Apr-Sep / Oct-Mar)"]


def storm_mixed(grid, rec, r, r_ls):
    """The kernel's rain with the storms' frontal rain spread over a storm's
    size, as climate.rain does after the kernel."""
    return climate.storm_spread(grid, r, r_ls, rec["s_in"], rec["tune"])


def km3_(x_mm, area_km2, mask=None) -> float:
    """mm/yr over cells (km2) -> km3/yr."""
    v = x_mm * area_km2
    return float((v if mask is None else v[mask]).sum() * 1e-6)


def rain_from_season(P, k, NB, land_tags=True):
    """Rain in season k that evaporated from land (tracers NB..2NB-1)."""
    return P["r_tag"][k, NB:].sum(0) if land_tags else P["r_tag"][k, :NB].sum(0)


def _decay(bins) -> dict:
    """e-folding length (km) of P and PW from the first bin to the last, model and obs."""
    if len(bins) < 2:
        return {}
    a, b = bins[0], bins[-1]
    dx = b["km"] - a["km"]
    f = lambda x0, x1: float(dx / np.log(x0 / x1)) if x0 > 0 and x1 > 0 and x0 != x1 else float("nan")
    return dict(P_km=f(a["P"], b["P"]), P_obs_km=f(a["P_obs"], b["P_obs"]), PW_km=f(a["PW"], b["PW"]),
                PW_obs_km=f(a["PW_obs"], b["PW_obs"]), far_over_near=b["P"] / max(a["P"], 1e-9),
                far_over_near_obs=b["P_obs"] / max(a["P_obs"], 1e-9))


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------
def _f(x, nd=0):
    return "   -" if x is None or not np.isfinite(x) else f"{x:.{nd}f}"


def report(R) -> str:
    L = [f"# Moisture budget, Earth L{R['level']} (cell {R['cell_km']:.0f} km)", ""]
    L.append(f"probe reproduces the model's rain: {R['probe_matches_model']}")
    L += ["", "## Ocean basins (Sv; E - P - R > 0: the basin loses water to the air)",
          "| basin | area Mkm2 | E | P | R | E-P-R | E-P mm/yr | obs E (NCEP) | obs P (GPCP) | obs E-P | obs E-P mm/yr |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in R["basins"]:
        L.append(f"| {r['basin']} | {r['area_mkm2']:.0f} | {r['E_sv']:.2f} | {r['P_sv']:.2f} | {r['R_sv']:.2f} | "
                 f"{r['EPR_sv']:+.2f} | {r['EP_mm']:+.0f} | {r['obs_E_sv']:.2f} | {r['obs_P_gpcp_sv']:.2f} | "
                 f"{r['obs_EP_sv']:+.2f} | {r['obs_EP_mm']:+.0f} |")
    L.append(f"\nAtlantic + Arctic E-P-R: model {R['atlantic_arctic_EPR_sv']:+.2f} Sv; "
             f"obs E-P (NCEP E - GPCP P) {R['atlantic_arctic_obs_EP_sv']:+.2f} Sv before runoff")
    L += ["", "Published:"] + [f"- {k}: {v}" for k, v in PUBLISHED.items()]
    X = R["exchange"]
    L += ["", "## Where each drainage basin's evaporation rains (Sv; rows: source, columns: destination)",
          "| from \\ to | " + " | ".join(X["basins"]) + " | evap | net export |",
          "|---" * (len(X["basins"]) + 3) + "|"]
    for s, b in enumerate(X["basins"]):
        L.append(f"| {b} | " + " | ".join(f"{v:.2f}" for v in X["rain_sv"][s])
                 + f" | {X['evap_sv'][s]:.2f} | {X['net_export_sv'][s]:+.2f} |")
    L += ["", "## Vapour flux across drainage divides (Sv, + from the first basin to the second)",
          "| section | Apr-Sep | Oct-Mar | year | edges |", "|---|---|---|---|---|"]
    for r in R["sections"]:
        L.append(f"| {r['section']} | {r['jul_sv']:+.3f} | {r['jan_sv']:+.3f} | {r['ann_sv']:+.3f} | {r['edges']} |")
    L += ["", "## Northward vapour transport (Sv): kernel edge fluxes, and implied by E - P south of the circle",
          "| lat | advection | eddy mixing | total | implied (model E-P) | implied (NCEP E - GPCP P) |",
          "|---|---|---|---|---|---|"]
    for r in R["meridional"]:
        L.append(f"| {r['lat']} | {r['adv_sv']:+.2f} | {r['eddy_sv']:+.2f} | {r['adv_sv'] + r['eddy_sv']:+.2f} | "
                 f"{r['implied_sv']:+.2f} | {r['obs_implied_sv']:+.2f} |")
    L += ["", "## Zonal-mean E - P (mm/yr), model vs NCEP E - GPCP P",
          "| band | sea E | sea P | sea E-P | obs sea E | obs sea P | obs sea E-P | all E-P | obs all E-P |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in R["zonal"]:
        g = lambda k: r.get(k, float("nan"))
        L.append(f"| {r['band']} | {_f(g('sea_E'))} | {_f(g('sea_P'))} | {_f(g('sea_E') - g('sea_P'))} | "
                 f"{_f(g('sea_obs_E'))} | {_f(g('sea_obs_P'))} | {_f(g('sea_obs_E') - g('sea_obs_P'))} | "
                 f"{_f(g('all_E') - g('all_P'))} | {_f(g('all_obs_E') - g('all_obs_P'))} |")
    L += ["", (f"## Inland paths (P mm/yr in the season; PW mm, model vapour x {R['pw_mm_per_unit']:.1f} mm "
               "per unit, fitted over the open sea)")]
    for p in R["paths"]:
        dcy = p["decay"]
        L.append(f"\n**{p['path']}** ({p['season']}): far/near P model {_f(dcy.get('far_over_near'), 2)} "
                 f"obs {_f(dcy.get('far_over_near_obs'), 2)}; e-fold P {_f(dcy.get('P_km'))} km "
                 f"(obs {_f(dcy.get('P_obs_km'))}), PW {_f(dcy.get('PW_km'))} km (obs {_f(dcy.get('PW_obs_km'))})")
        L.append("| km | P | P obs | ratio | PW | PW obs |")
        L.append("|---|---|---|---|---|---|")
        for b in p["bins"]:
            L.append(f"| {b['km']:.0f} | {b['P']:.0f} | {b['P_obs']:.0f} | {b['P'] / max(b['P_obs'], 1):.2f} | "
                     f"{b['PW']:.1f} | {b['PW_obs']:.1f} |")
    L += ["", "## Land rain by distance from the sea (annual; outside Antarctica and ice)",
          "| km | area Mkm2 | P | P obs (GPCC) | ratio | PW | PW obs |", "|---|---|---|---|---|---|---|"]
    for r in R["coast_distance"]:
        L.append(f"| {r['km']} | {r['area_mkm2']:.1f} | {r['P']:.0f} | {r['P_obs']:.0f} | "
                 f"{r['P'] / max(r['P_obs'], 1):.2f} | {r['PW']:.1f} | {r['PW_obs']:.1f} |")
    L += ["", "## Residence and recycling"]
    for r in R["residence"]["model"]:
        L.append(f"- {r['season']}: vapour/rain {r['tau_hours'] / 24:.1f} days; rain-out length "
                 f"{r['length_km']:.0f} km (mean wind {r['wind_mean']:.1f} m/s)")
    L.append(f"- observed PW / GPCP P: {R['residence']['obs_days_pw_over_gpcp']:.1f} days")
    rc = R["recycling"]
    L.append(f"- land rain that evaporated from land: {rc['land_rain_from_land_pct']:.0f}% (obs ~40%); "
             f"land evaporation that rains on land: {rc['land_evap_rains_on_land_pct']:.0f}% (obs ~57%)")
    L += ["", "## The kernel's terms by region (rates in the half-year; trigger: showers fire when dry + LQ q > 0)",
          ("| region | half | P | P obs | PW | PW obs | q/qs | rain/day | ex% | ls% | cv% | dry C | LQ q C | "
           "E/P | land-origin % | own-region % | wind m/s | (P/PW) / obs |"),
          "|---" * 18 + "|"]
    for r in R["regions"]:
        L.append(f"| {r['region']} | {r['season']} | {r['P']:.0f} | {r['P_obs']:.0f} | {r['PW']:.1f} | "
                 f"{r['PW_obs']:.1f} | {r['rh']:.2f} | {r['rainout_per_day']:.3f} | {r['ex_pct']:.0f} | "
                 f"{r['ls_pct']:.0f} | {r['cv_pct']:.0f} | {r['dry_C']:+.1f} | {r['lq_C']:.1f} | "
                 f"{r['evap_over_P']:.2f} | {r['land_origin_pct']:.0f} | {r['own_region_pct']:.0f} | "
                 f"{r['wind']:.1f} | {r['eff_ratio']:.2f} |")
    L += ["", "## Books (the kernel's steady state, % of global rain)",
          "| half | (E - P)/P |", "|---|---|"]
    for r in R["books"]:
        L.append(f"| {r['season']} | {r['net_src_minus_rain_pct']:+.3f} |")
    L.append(R["books_note"])
    return "\n".join(L)


def run(level: int):
    grid = build_grid(level)
    d = earth_data.earth_on_grid(grid)
    t0 = time.time()
    c, rec = capture(grid, d["elev"].astype(np.float64), d["ice"].astype(np.float64))
    print(f"  climate: {time.time() - t0:.0f} s", file=sys.stderr)
    return grid, d, c, rec


def main():
    ap = argparse.ArgumentParser(description="Moisture budget of the climate model on Earth (PW-014)")
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--json", help="dump the numbers as JSON")
    a = ap.parse_args()
    t0 = time.time()
    grid, d, c, rec = run(a.level)
    R = analyse(grid, d, c, rec)
    print(report(R))
    print(f"\n({time.time() - t0:.0f} s)")
    if a.json:
        Path(a.json).write_text(json.dumps(R, indent=1, default=float))


if __name__ == "__main__":
    main()
