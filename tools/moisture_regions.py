"""Per-region, per-half-year moisture budget of the model's Earth climate, and
kernel-only sensitivities of the five PW-1093 candidates (lane 58).

    PYTHONPATH=. uv run python tools/moisture_regions.py [--level 6] [--json out.json] [--figs DIR]

Runs the Earth climate as tools/earth_check.py does (moisture_budget.capture),
then re-runs the rain kernel in moisture_budget's instrumented copy (_probe,
bit-for-bit the model's rain) with tracers tagged by box (the regions below,
plus "other land" and "other sea"). For every box and half-year it reports,
in mm/yr over the box (a rate in that half-year):

  E          evaporation in the box (sea uptake + land evaporation)
  conv_wind  net vapour inflow through the box's faces by the mean wind
  conv_drift ... by the storms' poleward drift (face_winds' eddy_drift part;
             the face flux split by its share of the face wind: the upwind
             cell is the same, so the split is exact)
  conv_mix   ... by the eddy mixing (down the vapour's gradient)
  P_kernel   the kernel's rain (E + conv = P_kernel in the steady state)
  spread     what storm_spread moves in or out afterwards (P - P_kernel)
  P, P_obs   the model's final rain and GPCC (land) / GPCP (sea)
  E_obs, conv_obs  NCEP E and P_obs - NCEP E (a reanalysis; E runs ~10% high)
  PW, PW_obs column vapour (moisture_budget's open-sea fit) and NCEP
  origin     the share of the box's rain evaporated in the box itself, on
             other land, in each sea box, and in the other sea
  parts      rain from oversaturation / large-scale / showers (%)

Sensitivities ("cf"): the kernel re-run on the same recorded inputs with one
thing changed, the rain renormalised to the same global mean as compute does
(temperatures, winds, vegetation and the coupled loop held fixed: first-order
answers to "where would the rain go", not a replacement for a solve):

  base       the kernel as is (checks the harness: equals the model's rain)
  c1_sea_ls  candidate 1: large-scale rain rate x1.5 over the sea poleward of 35 deg
  c2_drift8  candidate 2: eddy_drift 1.0 -> 0.8 m/s
  c2_drift0  candidate 2: no drift (before PW-998 round 3)
  c3_recyc   candidate 3: land evaporation down (Fu's w x 0.8 on land poleward of 35 deg)
  c4_cv      candidate 4: shower rate x0.5 over land poleward of 35 deg, local summer half
  c4_aloft   candidate 4, the physical form: the showers' reference air aloft
             (mse_thr) feels jet_anom (0.4) of the land-sea temperature
             contrast, as the jet stream already does, poleward of the
             tropics' even temperature aloft
  c5_reach   candidate 5: the mean wind on land-land faces poleward of 40N x0.7
             in the Oct-Mar half (the westerlies' inland reach)
  c6_summer_wind  the mean wind on land-land faces poleward of 35 deg x0.7 in the local summer half
  c7_land_eff     large-scale and shower rates x0.5 on land poleward of 35 deg
  c1b_sea_ls_20_60, c1c_sea_all  the sea's large-scale rain x1.5 at 20-60 deg; all the sea's rain x1.5
  c8_no_sink_west the subtropics' sinking air taken off SE USA / Gulf / W Atlantic and Pampas /
             S Brazil / SW Atlantic (the western flanks of the Atlantic highs; diagnostic boxes)
  c9_slower_all   every rain rate x0.64 (the kernel's own global rain is ~1.56x the 1000 mm it is scaled to)
  c10_land_slower the land's rain rates x0.65 at all latitudes

--ageo X: a probe, not a kernel re-run: the whole Earth climate solved with
monsoon_wind's cross-isobar share (0.45 x the pressure gradient poleward of
15 deg) set to X (patch_monsoon; 0.45 reproduces the model).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import planet  # noqa: E402,F401  (first: its thread caps must precede numpy)
import numpy as np  # noqa: E402
from planet import climate, images  # noqa: E402
from planet import ocean as ocean_mod  # noqa: E402
from tools import earth_data  # noqa: E402
from tools import moisture_budget as mb  # noqa: E402
from tools.earth_check import REGIONS, group_of  # noqa: E402

HALVES = ("Apr-Sep", "Oct-Mar")  # kernel season 0 = 'jul', 1 = 'jan'
REG = {r[0]: r[1:] for r in REGIONS}
# (name, lat0, lat1, lon0, lon1, surface); lon0 > lon1 wraps the date line
SEA_BOXES = [
    ("N Atlantic storm track", 40, 60, -60, -10, "sea"),
    ("N Pacific storm track", 40, 60, 145, -130, "sea"),
    ("Gulf of Mexico", 18, 30.5, -98, -80, "sea"),
    ("W Atlantic subtropics", 25, 40, -80, -55, "sea"),
    ("E Atlantic subtropics", 20, 40, -55, -10, "sea"),
    ("NW Pacific subtropics", 20, 40, 120, 160, "sea"),
    ("SW Atlantic", -42, -20, -58, -30, "sea"),
    ("Tropical Atlantic", -20, 18, -60, 15, "sea"),
]
LAND_BOXES = [(n, *REG[n], "land") for n in
              ("W Europe", "European Russia", "W Siberia", "E Siberia", "Gobi/Mongolia", "Central Asia",
               "NE USA", "Great Plains", "SE USA", "Pampas", "Patagonia", "Amazon")] + \
             [("S Brazil/Paraguay", -30, -15, -62, -45, "land"), ("Canada 45-60N", 45, 60, -125, -65, "land")]
BOXES = LAND_BOXES + SEA_BOXES
# bands and regions the sensitivities are scored on (annual, mm/yr)
SCORE = ["land 40-50N", "land 50-60N", "land 60-80N", "sea 40-50N", "sea 50-60N", "W Siberia", "E Siberia",
         "Gobi/Mongolia", "NE USA", "W Europe", "European Russia", "Great Plains", "SE USA", "Pampas", "Patagonia"]


def box_mask(grid, sea, lat0, lat1, lon0, lon1, surf):
    lat, lon = grid.lat, grid.lon
    lo = (lon >= lon0) & (lon <= lon1) if lon0 <= lon1 else (lon >= lon0) | (lon <= lon1)
    return (lat >= lat0) & (lat <= lat1) & lo & (sea if surf == "sea" else ~sea)


# --------------------------------------------------------------------------
# kernel inputs with changes (climate._rain_args, with hooks)
# --------------------------------------------------------------------------
def kernel_inputs(rec, tune=None, st_fn=None, wind_fn=None, w_fn=None):
    """climate._rain_args' tuple for the recorded call, with: tune overrides,
    st_fn(st) changing the stacked per-cell inputs (qs, src_q, ls, cv, mse_t,
    mse_thr, rhc), wind_fn(un, kd) the face winds, w_fn(w) Fu's w. Returns
    (args for moisture_budget._probe without its last 8, un, kd)."""
    grid, s_in = rec["grid"], rec["s_in"]
    tune = {**rec["tune"], **(tune or {})}
    n = grid.n
    ocean = rec["elev"] <= 0 if rec["ocean"] is None else rec["ocean"]
    w = np.full(n, tune["budyko_w"]) if rec["w"] is None else \
        np.ascontiguousarray(np.broadcast_to(rec["w"], (n,)), np.float64)
    if w_fn is not None:
        w = np.ascontiguousarray(w_fn(w.copy()), np.float64)
    open_sea = np.ones(n) if rec["open_sea"] is None else np.asarray(rec["open_sea"], np.float64)
    open_sea = np.ascontiguousarray(np.broadcast_to(open_sea, (len(s_in), n)), np.float64)
    st = {k: np.ascontiguousarray(np.stack([d[k] for d in s_in])) for k in
          ("qs", "src_q", "ls", "cv", "mse_t", "mse_thr", "rhc")}
    if st_fn is not None:
        st = {k: np.ascontiguousarray(v, np.float64) for k, v in st_fn(st).items()}
    un, kd = climate.face_winds(grid, s_in, tune)
    if wind_fn is not None:
        un, kd = wind_fn(un.copy(), kd.copy())
    c_self, c_in, nbr, dt = climate._transport(grid, un, kd)
    open_sea = climate.sea_uptake(s_in, open_sea, dt, tune)
    start = rec.get("start")
    warm = start is not None and start["vap"].shape == st["qs"].shape  # (compute's second pass, PW-1364)
    steps = int((climate.RAIN_WARM_DAYS if warm else climate.RAIN_DAYS) * 86400.0 / dt) + 20
    tau_ex = -climate.RATE_S / np.log(1.0 - tune["fex"])
    m0 = start["vap"] if warm else np.where(ocean, st["src_q"], climate.RAIN_INIT * st["qs"])
    ema0 = start["ema"] if warm else np.zeros_like(st["qs"])
    args = (st["qs"], st["src_q"], ocean, st["ls"] / climate.RATE_S, st["cv"] / climate.RATE_S, st["mse_t"],
            st["mse_thr"], np.ascontiguousarray(rec["pet"], np.float64), w, float(tune["soil_mm"]), open_sea,
            c_self, c_in, nbr, climate._faces(grid)["off"], steps, dt, tau_ex, st["rhc"], tune["rh_pow"],
            tune["cv_scale"], tune["evap_cool"], tune["mean_mm"], np.ascontiguousarray(m0, np.float64),
            np.ascontiguousarray(ema0, np.float64), warm)
    return args, un, kd, tune


def run_probe(rec, tag, ntag, **kw):
    args, un, kd, tune = kernel_inputs(rec, **kw)
    F = climate._faces(rec["grid"])
    out = mb._probe(*args, un, kd, F["ea"], F["eb"], F["L"], F["lc"], np.ascontiguousarray(tag, np.int64),
                    int(ntag))
    keys = ("r", "r_ls", "up", "q", "land_e", "r_ex", "r_cv", "dry", "q_before", "r_tag", "f_adv", "f_mix")
    P = dict(zip(keys, out))
    P["dt"], P["un"], P["tune"] = args[16], un, tune
    return P


def final_rain(rec, P, mean_cell):
    """The kernel's rain -> mm/yr as compute makes it: storm_spread, then scaled
    to the same plain cell mean as the model's (mean_cell) and clipped."""
    r = climate.storm_spread(rec["grid"], P["r"], P["r_ls"], rec["s_in"], P["tune"])
    k = mean_cell / max(0.5 * (r[0] + r[1]).mean(), 1e-12)
    return np.clip(r * k, 0, 8000), k


# --------------------------------------------------------------------------
# the budget
# --------------------------------------------------------------------------
def observed(grid, d):
    """Observed P (GPCC on land, GPCP elsewhere), NCEP E and PW, per half [2, n]."""
    obs = mb.observations(grid)
    p = earth_data.raster("gpcp")
    pv = np.where(np.abs(p["val"]) > 1e30, np.nan, p["val"])
    days = np.array([31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])[:, None]
    gm = earth_data._sample(p, grid.lat, grid.lon, pv) * days  # mm per month
    gp = np.stack([gm[3:9].sum(0) * 2, (gm[:3].sum(0) + gm[9:].sum(0)) * 2])
    gc = np.stack([d["obs_p_jul"], d["obs_p_jan"]]).astype(np.float64)
    P = np.where(np.isfinite(gc), gc, gp)
    return dict(P=P, E=np.stack([obs["e_jul"], obs["e_jan"]]), PW=np.stack([obs["pw_jul"], obs["pw_jan"]]),
                P_ann=0.5 * P.sum(0))


def masks(grid, d):
    sea = ~earth_data.land_of(d)
    lat = grid.lat
    M = {name: box_mask(grid, sea, *b) for name, *b in BOXES}
    for lo, hi in ((40, 50), (50, 60), (60, 80)):
        M[f"land {lo}-{hi}N"] = ~sea & (lat >= lo) & (lat < hi)
        M[f"sea {lo}-{hi}N"] = sea & (lat >= lo) & (lat < hi)
    return sea, M


def budget(grid, d, c, rec, obs, sea, M):
    area = grid.cell_area_km2
    sc = mb.mm_scale(c, rec)
    tag = np.where(sea, 1, 0)  # 0 other land, 1 other sea, 2.. boxes
    for k, (name, *_b) in enumerate(BOXES):
        tag[M[name] & (tag <= 1)] = 2 + k
    ntag = 2 + len(BOXES)
    P = run_probe(rec, tag, ntag)
    match = bool(np.array_equal(mb.storm_mixed(grid, rec, P["r"], P["r_ls"]), rec["out"][0]))
    un0, _ = climate.face_winds(grid, rec["s_in"], {**rec["tune"], "eddy_drift": 0.0})
    share_drift = np.where(np.abs(P["un"]) > 1e-12, (P["un"] - un0) / np.where(P["un"] == 0, 1, P["un"]), 0.0)
    kf = P["dt"] * sc * 1e-12  # face flux -> km3/yr
    f_adv, f_mix = P["f_adv"] * kf, P["f_mix"] * kf
    f_drift = f_adv * share_drift
    f_wind = f_adv - f_drift
    F = climate._faces(grid)
    ea, eb = F["ea"], F["eb"]
    q_b = P["q_before"]
    qcol = q_b.mean(0)
    pw_obs_ann = np.nan_to_num(obs["PW"].mean(0))
    fit = sea & (np.abs(grid.lat) < 60) & np.isfinite(obs["PW"].mean(0))
    k_pw = float((qcol[fit] * pw_obs_ann[fit] * area[fit]).sum() / (qcol[fit] ** 2 * area[fit]).sum())
    Pm = np.stack([c["p_jul"], c["p_jan"]])
    rows = []
    names = [b[0] for b in BOXES]
    for name in names:
        m = M[name]
        A = area[m].sum()
        if A == 0:
            continue
        inb = m[eb] & ~m[ea]
        outb = m[ea] & ~m[eb]
        mm = lambda km3: float(km3 / A * 1e6)
        wm = lambda x: float(np.nansum((x * area)[m]) / A)
        # inflow side: the outside cell's offset from the inside one
        o_cell = np.where(inb, ea, eb)
        i_cell = np.where(inb, eb, ea)
        dlat = grid.lat[o_cell] - grid.lat[i_cell]
        dlon = (grid.lon[o_cell] - grid.lon[i_cell] + 180) % 360 - 180
        dlon *= np.cos(np.radians(grid.lat[i_cell]))
        side = np.where(np.abs(dlon) > np.abs(dlat), np.where(dlon < 0, 0, 1), np.where(dlat < 0, 2, 3))
        for k, half in enumerate(HALVES):
            def conv(f, sel=None):
                s = (f[k] * inb).sum() - (f[k] * outb).sum() if sel is None else \
                    (f[k] * inb * sel).sum() - (f[k] * outb * sel).sum()
                return mm(s)
            E_sea, E_land = wm(P["up"][k] * sc), wm(P["land_e"][k] * sc)
            Pk = wm(P["r"][k] * sc)
            Pf = wm(Pm[k])
            rt = P["r_tag"][k] * sc  # [ntag, n]
            org = {nm: 100 * wm(rt[2 + j]) / max(Pk, 1e-9) for j, nm in enumerate(names)}
            org_land_other = 100 * wm(rt[0]) / max(Pk, 1e-9)
            org_sea_other = 100 * wm(rt[1]) / max(Pk, 1e-9)
            land_names = [b[0] for b in LAND_BOXES]
            from_land = org_land_other + sum(org[x] for x in land_names)
            ok_p = m & np.isfinite(obs["P"][k])
            ok_e = m & np.isfinite(obs["E"][k])
            Pobs = float((obs["P"][k] * area)[ok_p].sum() / max(area[ok_p].sum(), 1e-9))
            Eobs = float((obs["E"][k] * area)[ok_e].sum() / max(area[ok_e].sum(), 1e-9))
            r_ = max(wm(P["r"][k]), 1e-30)
            row = dict(box=name, half=half, area_mkm2=float(A / 1e6), E=E_sea + E_land, E_sea=E_sea, E_land=E_land,
                       conv_wind=conv(f_wind), conv_drift=conv(f_drift), conv_mix=conv(f_mix),
                       conv_wind_W=conv(f_wind, side == 0), conv_wind_E=conv(f_wind, side == 1),
                       conv_wind_S=conv(f_wind, side == 2), conv_wind_N=conv(f_wind, side == 3),
                       P_kernel=Pk, spread=Pf - Pk,
                       P=Pf, P_obs=Pobs, E_obs=Eobs, conv_obs=Pobs - Eobs,
                       PW=wm(q_b[k] * k_pw), PW_obs=wm(np.nan_to_num(obs["PW"][k])),
                       own_pct=org[name], land_pct=from_land, sea_pct=100 - from_land,
                       origin={**{x: v for x, v in org.items() if v >= 2.0}, "other land": org_land_other,
                               "other sea": org_sea_other},
                       ex_pct=100 * wm(P["r_ex"][k]) / r_, cv_pct=100 * wm(P["r_cv"][k]) / r_,
                       ls_pct=100 * wm(P["r_ls"][k]) / r_, q_qs=wm(q_b[k] / rec["s_in"][k]["qs"]),
                       B=wm(rec["s_in"][k]["B"]), track=wm(rec["s_in"][k]["track"]))
            row["closure"] = row["E"] + row["conv_wind"] + row["conv_drift"] + row["conv_mix"] - Pk
            row["eff"] = Pf / max(row["PW"], 1e-9) / 365.25  # per day
            row["eff_obs"] = Pobs / max(row["PW_obs"], 1e-9) / 365.25
            rows.append(row)
    return dict(match=match, rows=rows, sc=sc, k_pw=k_pw, probe=P, f=dict(wind=f_wind, drift=f_drift, mix=f_mix))


# --------------------------------------------------------------------------
# sensitivities
# --------------------------------------------------------------------------
def scenarios(grid, d, rec, sea):
    lat = grid.lat
    land = ~sea
    tune = rec["tune"]
    F = climate._faces(grid)
    ea, eb = F["ea"], F["eb"]
    mid_lat = 0.5 * (lat[ea] + lat[eb])
    summer = np.stack([lat >= 0, lat < 0])  # [season 0 Apr-Sep, 1 Oct-Mar]: the local summer half

    def sea_ls(st):
        st["ls"] = np.where(sea & (np.abs(lat) >= 35), 1.5, 1.0) * st["ls"]
        return st

    def cv_half(st):
        st["cv"] = np.where(land & (np.abs(lat) >= 35) & summer, 0.5, 1.0) * st["cv"]
        return st

    def aloft(st):
        out = []
        for k, s in enumerate(rec["s_in"]):
            S = climate.smooth(grid, s["t_sl"], tune["jet_km"])
            anom = S - climate.zonal_mean(grid, S)
            fade = 1 - np.clip((tune["wtg"] + 15 - np.abs(lat)) / 15, 0, 1)
            t_ref = s["t_ref"] + tune["jet_anom"] * fade * anom
            out.append(t_ref + climate.LQ * tune["rh"] * climate._qsat(t_ref, tune["q_k"]))
        st["mse_thr"] = np.stack(out)
        return st

    def reach(un, kd):
        sel = land[ea] & land[eb] & (mid_lat >= 40)
        un0, _ = climate.face_winds(grid, rec["s_in"], {**tune, "eddy_drift": 0.0})
        drift = un - un0
        un[1] = np.where(sel, 0.7 * un0[1], un0[1]) + drift[1]
        return un, kd

    def reach_summer(un, kd):
        sel = land[ea] & land[eb] & (np.abs(mid_lat) >= 35)
        un0, _ = climate.face_winds(grid, rec["s_in"], {**tune, "eddy_drift": 0.0})
        drift = un - un0
        for k in range(2):
            loc = sel & ((mid_lat >= 0) if k == 0 else (mid_lat < 0))
            un[k] = np.where(loc, 0.7 * un0[k], un0[k]) + drift[k]
        return un, kd

    def land_eff(st):
        f = np.where(land & (np.abs(lat) >= 35), 0.5, 1.0)
        st["cv"] = f * st["cv"]
        st["ls"] = f * st["ls"]
        return st

    def sea_rain_all(st):
        f = np.where(sea, 1.5, 1.0)
        st["ls"] = f * st["ls"]
        st["cv"] = f * st["cv"]
        return st

    def sea_ls_sub(st):
        st["ls"] = np.where(sea & (np.abs(lat) >= 20) & (np.abs(lat) < 60), 1.5, 1.0) * st["ls"]
        return st

    # the subtropics' sinking air taken off the western flanks of the Atlantic's highs (diagnostic boxes)
    west = np.zeros(grid.n, bool)
    for nm in ("SE USA", "Gulf of Mexico", "W Atlantic subtropics", "Pampas", "S Brazil/Paraguay", "SW Atlantic"):
        west |= box_mask(grid, sea, *next(b for b in BOXES if b[0] == nm)[1:5], "sea") | \
            box_mask(grid, sea, *next(b for b in BOXES if b[0] == nm)[1:5], "land")

    def no_sink_west(st):
        ls, cv, rhc = [], [], []
        pole = np.clip((np.abs(lat) - 70) / 15, 0, 1)
        for s in rec["s_in"]:
            sink = np.where(west, 0.0, s["sink"])
            ls.append(tune["base"] * np.clip(tune["bg"] + tune["storm"] * s["B"] + tune["itcz_ls"] * s["itcz"]
                                             - tune["belt_dry"] * sink - 0.3 * pole, 0.05, None))
            cv.append(tune["cv"] * tune["base"] * (1 + tune["itcz_cv"] * s["itcz"])
                      * np.clip(1 - tune["cv_sink"] * sink, 0, 1))
            rhc.append(tune["rh_c"] * np.exp(-tune["q_k"] * climate.LAPSE * tune["lift_m"] * s["B"]
                                             * np.clip(1 - sink, 0, 1)))
        st["ls"], st["cv"], st["rhc"] = np.stack(ls), np.stack(cv), np.stack(rhc)
        return st

    def slower(st, f=0.64):
        st["ls"] = f * st["ls"]
        st["cv"] = f * st["cv"]
        return st

    # the mean wind's convergence per cell (1/s; drift left out: it carries vapour, not air)
    un0, _ = climate.face_winds(grid, rec["s_in"], {**tune, "eddy_drift": 0.0})
    cell = np.repeat(np.arange(grid.n), np.diff(F["off"]))
    conv = np.stack([-np.bincount(cell, F["sg"] * un0[k][F["eid"]] * F["L"][F["eid"]], grid.n) / F["A"]
                     for k in range(2)])
    conv = np.stack([climate.smooth(grid, conv[k], 300.0) for k in range(2)])
    print("  mean-wind convergence (1/s), 5/50/95%: " + " ".join(f"{x:.1e}" for x in np.percentile(conv, [5, 50, 95])),
          file=sys.stderr)

    def conv_lift(c0):
        def f(st):
            st["ls"] = np.clip(1 + conv / c0, 0.3, 4.0) * st["ls"]
            return st
        return f

    w_low = lambda w: np.where(land & (np.abs(lat) >= 35), 0.8 * w, w)
    return {
        "base": {},
        "c1_sea_ls": dict(st_fn=sea_ls),
        "c2_drift8": dict(tune={"eddy_drift": 0.8}),
        "c2_drift0": dict(tune={"eddy_drift": 0.0}),
        "c3_recyc": dict(w_fn=w_low),
        "c4_cv": dict(st_fn=cv_half),
        "c4_aloft": dict(st_fn=aloft),
        "c5_reach": dict(wind_fn=reach),
        "c6_summer_wind": dict(wind_fn=reach_summer),
        "c7_land_eff": dict(st_fn=land_eff),
        "c1b_sea_ls_20_60": dict(st_fn=sea_ls_sub),
        "c1c_sea_all": dict(st_fn=sea_rain_all),
        "c8_no_sink_west": dict(st_fn=no_sink_west),
        "c9_slower_all": dict(st_fn=slower, tune={"fex": 1 - (1 - tune["fex"]) ** 0.64}),
        "c11_conv_lift_2e6": dict(st_fn=conv_lift(2e-6)),
        "c11_conv_lift_5e7": dict(st_fn=conv_lift(5e-7)),
        "c10_land_slower": dict(st_fn=lambda st: {**st, "ls": np.where(land, 0.65, 1.0) * st["ls"],
                                                  "cv": np.where(land, 0.65, 1.0) * st["cv"]}),
    }


def b_share(grid, d, c, p):
    """Koppen B share of land outside Antarctica (earth_check's), with rain p [2, n]."""
    w = earth_data.cell_areas(grid)
    land = earth_data.land_of(d)
    k = climate.koppen(d["elev"], c["temp"], c["t_warm"], c["t_cold"], 0.5 * (p[0] + p[1]), p[0], p[1], grid.lat,
                       d["ice"])
    g = group_of(np.asarray(k))
    m = land & (grid.lat >= -60) & (g >= 0)
    return 100 * float(w[m & (g == 1)].sum() / w[m].sum())


def score(grid, d, c, rec, M, p, P, sc_k, obs):
    area = grid.cell_area_km2
    out = {}
    for name in SCORE:
        m = M[name]
        A = area[m].sum()
        out[name] = [float((p[k] * area)[m].sum() / A) for k in range(2)]
    # northward transport at 30N, 50N (Sv), from the face fluxes
    F = climate._faces(grid)
    ea, eb = F["ea"], F["eb"]
    lat = grid.lat
    sc = sc_k
    for phi in (30, 40, 50):
        sgn = np.where((lat[ea] < phi) & (lat[eb] >= phi), 1.0, np.where((lat[eb] < phi) & (lat[ea] >= phi), -1.0, 0))
        f = (P["f_adv"] + P["f_mix"]) * P["dt"] * sc * 1e-12
        out[f"transport {phi}N"] = float(np.mean([(f[k] * sgn).sum() for k in range(2)]) / mb.SV_KM3)
    out["B share"] = b_share(grid, d, c, p)
    land = earth_data.land_of(d)
    nl = land & (lat >= -60)
    e_land = P["land_e"] * sc  # mm/yr, the kernel's land evaporation in this run's scaling
    out["land P"] = float((p.mean(0) * area)[nl].sum() / area[nl].sum())
    out["land E"] = float((e_land.mean(0) * area)[nl].sum() / area[nl].sum())
    out["land P-E (Sv)"] = float(((p.mean(0) - e_land.mean(0)) * area)[land].sum() * 1e-6 / mb.SV_KM3)
    out["scale"] = float(sc)
    out["residence d"] = float((P["q_before"] * area).sum() / (P["r"] * area).sum() * P["dt"] / 86400)
    out["land residence d"] = float((P["q_before"] * area)[:, nl].sum() / (P["r"] * area)[:, nl].sum()
                                    * P["dt"] / 86400)
    out["sea residence d"] = float((P["q_before"] * area)[:, ~land].sum() / (P["r"] * area)[:, ~land].sum()
                                   * P["dt"] / 86400)
    return out


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
DIV = [(-1.0, "#b2182b"), (-0.5, "#e88a7d"), (0.0, "#f0efec"), (0.5, "#7fb0e0"), (1.0, "#2a5fb0")]


def _ramp(x, stops):
    xs = np.array([s[0] for s in stops])
    cs = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for _, h in stops], float)
    x = np.clip(x, xs[0], xs[-1])
    return np.stack([np.interp(x, xs, cs[:, i]) for i in range(3)], -1)


def _pixels(grid, width):
    h = width // 2
    la = 90 - (np.arange(h) + 0.5) * 180 / h
    lo = -180 + (np.arange(width) + 0.5) * 360 / width
    LA, LO = np.meshgrid(la, lo, indexing="ij")
    return grid.locate(earth_data._unit(LA.ravel(), LO.ravel())).reshape(h, width)


def _coast(land_px):
    c = np.zeros_like(land_px)
    c[:, 1:] |= land_px[:, 1:] != land_px[:, :-1]
    c[1:, :] |= land_px[1:, :] != land_px[:-1, :]
    return c


def map_png(path, grid, d, fields, width=720):
    """Panels stacked vertically: each a field on [-1, 1] (diverging ramp, blue +)."""
    cell = _pixels(grid, width)
    coast = _coast(earth_data.land_of(d)[cell])
    rows = []
    for f in fields:
        img = _ramp(np.nan_to_num(f)[cell], DIV)
        img[coast] = 40
        img[~np.isfinite(f[cell])] = 200
        rows.append(img)
        rows.append(np.full((4, width, 3), 255.0))
    images.write_png(path, np.concatenate(rows[:-1], 0).astype(np.uint8))


def bars_svg(path, rows, boxes, title):
    """Grouped horizontal bars per box and half: the budget terms (mm/yr), diverging from 0."""
    terms = [("E", "evaporation in the box", "#1baf7a"), ("conv_wind", "mean-wind inflow", "#2a78d6"),
             ("conv_drift", "storm drift inflow", "#eb6834"), ("conv_mix", "eddy-mixing inflow", "#6250d6")]
    R = {(r["box"], r["half"]): r for r in rows}
    W, lh, x0 = 900, 16, 260
    sel = [(b, h) for b in boxes for h in HALVES if (b, h) in R]
    lo = min(min(R[s][t] for t, *_ in terms) for s in sel)
    hi = max(max(max(R[s][t] for t, *_ in terms), R[s]["P"], R[s]["P_obs"]) for s in sel)
    lo = min(lo, 0)
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (W - x0 - 20)
    H = 76 + len(sel) * (len(terms) * lh + 26)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="11">',
         f'<rect width="{W}" height="{H}" fill="#fcfcfb"/>', f'<text x="10" y="18" font-size="14">{title}</text>']
    for i, (t, lab, col) in enumerate(terms):
        o.append(f'<rect x="{10 + i * 210}" y="28" width="10" height="10" fill="{col}"/>'
                 f'<text x="{24 + i * 210}" y="37" fill="#333">{lab}</text>')
    o.append('<text x="10" y="54" fill="#333">solid black line: model P; dashed: observed P '
             '(GPCC on land, GPCP at sea)</text>')
    y = 72
    o.append(f'<line x1="{sx(0)}" y1="{y - 4}" x2="{sx(0)}" y2="{H - 4}" stroke="#999"/>')
    for s in sel:
        r = R[s]
        o.append(f'<text x="10" y="{y + 2 * lh}" fill="#222">{s[0]}, {s[1]}</text>')
        for j, (t, _l, col) in enumerate(terms):
            v = r[t]
            a, b = sorted((sx(0), sx(v)))
            o.append(f'<rect x="{a:.1f}" y="{y + j * lh + 1}" width="{max(b - a, 0.5):.1f}" height="{lh - 3}" '
                     f'rx="2" fill="{col}"><title>{t}: {v:.0f} mm/yr</title></rect>')
        yb = y + len(terms) * lh
        o.append(f'<line x1="{sx(r["P"]):.1f}" y1="{y}" x2="{sx(r["P"]):.1f}" y2="{yb}" stroke="#111" '
                 f'stroke-width="2"/>')
        o.append(f'<line x1="{sx(r["P_obs"]):.1f}" y1="{y}" x2="{sx(r["P_obs"]):.1f}" y2="{yb}" stroke="#111" '
                 f'stroke-width="2" stroke-dasharray="3,2"/>')
        o.append(f'<text x="{x0 - 8}" y="{y + 3 * lh + 2}" text-anchor="end" fill="#555">P {r["P"]:.0f} / '
                 f'{r["P_obs"]:.0f}</text>')
        y = yb + 26
    for v in np.linspace(0, hi, 5):
        o.append(f'<text x="{sx(v):.0f}" y="{H - 6}" fill="#777" text-anchor="middle">{v:.0f}</text>')
    o.append("</svg>")
    Path(path).write_text("\n".join(o))


# --------------------------------------------------------------------------
def fmt_budget(rows) -> list[str]:
    L = ["| box | half | P / obs | E / obs | wind in (W, E, S, N) | drift in | mix in | spread | conv / obs | "
         "PW / obs | P/PW per day / obs | own % | land % | ex/ls/cv % | q/qs |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['box']} | {r['half']} | {r['P']:.0f} / {r['P_obs']:.0f} | {r['E']:.0f} / {r['E_obs']:.0f} | "
                 f"{r['conv_wind']:+.0f} ({r['conv_wind_W']:+.0f}, {r['conv_wind_E']:+.0f}, {r['conv_wind_S']:+.0f}, "
                 f"{r['conv_wind_N']:+.0f}) | {r['conv_drift']:+.0f} | {r['conv_mix']:+.0f} | {r['spread']:+.0f} | "
                 f"{r['conv_wind'] + r['conv_drift'] + r['conv_mix']:+.0f} / {r['conv_obs']:+.0f} | "
                 f"{r['PW']:.1f} / {r['PW_obs']:.1f} | {r['eff']:.3f} / {r['eff_obs']:.3f} | {r['own_pct']:.0f} | "
                 f"{r['land_pct']:.0f} | {r['ex_pct']:.0f}/{r['ls_pct']:.0f}/{r['cv_pct']:.0f} | {r['q_qs']:.2f} |")
    return L


def patch_monsoon(ageo: float):
    """A probe (whole Earth solve, not a kernel re-run): monsoon_wind with its cross-isobar share
    (the -0.45 x pressure gradient poleward of 15 deg) set to ageo; everything else as climate's."""
    orig = climate.monsoon_wind

    def mw(grid, t_sl, shift, strength=1.0, big=0.0, big_km=2000.0, front=None, belt=1.0, column=None):
        anom = t_sl - climate.zonal_mean(grid, t_sl)
        if column is not None:
            anom = anom * np.where(anom >= 0, column[0], column[1])
        warmth = climate.smooth(grid, anom, 900.0)
        if big > 0:
            warmth = warmth + big * climate.smooth_big(grid, anom, big_km)
        g = climate.gradient(grid, -warmth) * 1000.0
        geo = np.cross(grid.centers, g) * np.sign(grid.lat)[:, None]
        w = np.clip(np.abs(grid.lat) / 15.0, 0, 1)[:, None]
        v = strength * 0.3 * (w * (0.9 * geo - ageo * g) - (1 - w) * g)
        m = np.linalg.norm(v, axis=1, keepdims=True)
        cap = 0.7 * strength * np.clip((65 - np.abs(grid.lat)) / 25, 0.3, 1)[:, None]
        v = v * np.minimum(1, cap / np.maximum(m, 1e-9))
        return climate.wind(grid, shift, front, belt) + v, warmth

    climate.monsoon_wind = mw
    return orig


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--ageo", type=float, help="probe: monsoon_wind's cross-isobar share (climate's 0.45)")
    ap.add_argument("--json")
    ap.add_argument("--figs")
    ap.add_argument("--no-cf", action="store_true", help="skip the sensitivities")
    a = ap.parse_args()
    t0 = time.time()
    if a.ageo is not None:
        patch_monsoon(a.ageo)
    grid, d, c, rec = mb.run(a.level)
    obs = observed(grid, d)
    sea, M = masks(grid, d)
    B = budget(grid, d, c, rec, obs, sea, M)
    print(f"# Regional moisture budget, Earth L{a.level}\n\nprobe reproduces the model's rain: {B['match']}; "
          f"worst box closure (E + inflow - P_kernel): "
          f"{max(abs(r['closure']) for r in B['rows']):.1f} mm/yr\n")
    print("\n".join(fmt_budget(B["rows"])))
    print("\nOrigin of each box's rain (% of its kernel rain, sources >= 2%):")
    for r in B["rows"]:
        org = ", ".join(f"{k} {v:.0f}" for k, v in sorted(r["origin"].items(), key=lambda kv: -kv[1]) if v >= 2)
        print(f"- {r['box']}, {r['half']}: {org}")
    area = grid.cell_area_km2
    Pp = B["probe"]
    phys = float((Pp["r"].mean(0) * area).sum() / area.sum() / Pp["dt"] * mb.YEAR_S * B["k_pw"])
    print(f"\nThe kernel's own global rain (vapour units x {B['k_pw']:.1f} mm, the open-sea PW fit): {phys:.0f} "
          f"mm/yr; compute rescales it to {np.mean(c['precip']):.0f} (x{np.mean(c['precip']) / phys:.2f})")
    land_ = earth_data.land_of(d)
    for nm, msk in (("land (to 60S)", land_ & (grid.lat >= -60)), ("sea", ~land_)):
        for k, h in enumerate(HALVES):
            ok = msk & np.isfinite(obs["PW"][k]) & np.isfinite(obs["P"][k])
            mod = (Pp["q_before"][k] * area)[ok].sum() / (Pp["r"][k] * area)[ok].sum() * Pp["dt"] / 86400
            ob = (obs["PW"][k] * area)[ok].sum() / (obs["P"][k] * area)[ok].sum() * 365.25
            pm = (np.stack([c["p_jul"], c["p_jan"]])[k] * area)[ok].sum() / area[ok].sum()
            po = (obs["P"][k] * area)[ok].sum() / area[ok].sum()
            print(f"- {nm}, {h}: vapour residence (PW / P) model {mod:.1f} d (kernel's own rate), observed "
                  f"{ob:.1f} d; P {pm:.0f} vs {po:.0f} mm/yr")
    out = dict(level=a.level, budget=B["rows"], match=B["match"], kernel_phys_mm=phys)
    if not a.no_cf:
        mean_cell = float(np.mean(c["precip"]))
        tag = np.where(sea, 1, 0)
        res = {}
        for name, kw in scenarios(grid, d, rec, sea).items():
            P = run_probe(rec, tag, 2, **kw)
            p, k = final_rain(rec, P, mean_cell)
            sc_k = k  # model units per step -> mm/yr for this run (before storm_spread's redistribution)
            res[name] = score(grid, d, c, rec, M, p, P, sc_k, obs)
            print(f"  cf {name}: {time.time() - t0:.0f} s", file=sys.stderr)
        base = res["base"]
        obs_s = {nm: [float((obs["P"][k] * grid.cell_area_km2)[M[nm] & np.isfinite(obs["P"][k])].sum()
                            / grid.cell_area_km2[M[nm] & np.isfinite(obs["P"][k])].sum())
                      for k in range(2)] for nm in SCORE}
        print("\n## Sensitivities (annual mm/yr; kernel only, global mean held)")
        print("| | obs | " + " | ".join(res) + " |")
        print("|---|---|" + "---|" * len(res))
        for nm in SCORE:
            print(f"| {nm} | {np.mean(obs_s[nm]):.0f} | " + " | ".join(f"{np.mean(v[nm]):.0f}" for v in res.values())
                  + " |")
        for nm in SCORE[:3] + ["W Siberia", "Gobi/Mongolia", "SE USA", "Pampas"]:
            for k, h in enumerate(HALVES):
                print(f"| {nm} {h} | {obs_s[nm][k]:.0f} | " + " | ".join(f"{v[nm][k]:.0f}" for v in res.values())
                      + " |")
        for key in ("transport 30N", "transport 40N", "transport 50N", "B share", "land P", "land E", "residence d",
                    "land residence d", "sea residence d",
                    "land P-E (Sv)"):
            print(f"| {key} | | " + " | ".join(f"{v[key]:.2f}" for v in res.values()) + " |")
        print("| scale vs base | | " + " | ".join(f"{v['scale'] / base['scale']:.3f}" for v in res.values()) + " |")
        out["cf"], out["cf_obs"] = res, obs_s
    if a.figs:
        fd = Path(a.figs)
        fd.mkdir(parents=True, exist_ok=True)
        Pm = np.stack([c["p_jul"], c["p_jan"]])
        lr = [np.log2(np.maximum(Pm[k], 10) / np.maximum(obs["P"][k], 10)) / 2 for k in range(2)]
        map_png(fd / f"rain_ratio_L{a.level}.png", grid, d, lr)
        Pp = B["probe"]
        land_share = [np.where(sea, np.nan, Pp["r_tag"][k][0] / np.maximum(Pp["r"][k], 1e-30)) for k in range(2)]
        # land-origin share of rain: own box + other land tracers
        nb = len(LAND_BOXES)
        lo = [np.where(sea, np.nan, (Pp["r_tag"][k][0] + Pp["r_tag"][k][2:2 + nb].sum(0))
                       / np.maximum(Pp["r"][k], 1e-30)) for k in range(2)]
        map_png(fd / f"land_origin_L{a.level}.png", grid, d, [2 * x - 1 for x in lo])
        del land_share
        cvs = [np.where(sea, np.nan, Pp["r_cv"][k] / np.maximum(Pp["r"][k], 1e-30)) * 2 - 1 for k in range(2)]
        map_png(fd / f"shower_share_L{a.level}.png", grid, d, cvs)
        bars_svg(fd / f"budget_north_L{a.level}.svg", B["rows"],
                 ["W Europe", "European Russia", "W Siberia", "Gobi/Mongolia", "NE USA", "Great Plains",
                  "N Atlantic storm track", "N Pacific storm track"],
                 f"Vapour budget by box and half-year, Earth L{a.level} (mm/yr over the box)")
        bars_svg(fd / f"budget_subtropics_L{a.level}.svg", B["rows"],
                 ["SE USA", "Gulf of Mexico", "W Atlantic subtropics", "Pampas", "S Brazil/Paraguay", "SW Atlantic"],
                 f"Vapour budget by box and half-year, Earth L{a.level} (mm/yr over the box)")
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1, default=float))
    print(f"\n({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
