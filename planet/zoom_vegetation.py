"""Vegetation in the regional zoom (PW-214; docs/proposals/vegetation.md
section 3.7): the world's vegetation model (vegetation.py) run per pixel on
the zoom's own terrain, starting from the world's cover fractions.

What the pixel adds to the coarse cell's climate:
1. Temperature from the zoom's lapse-corrected fields (treelines, alpine
   belts, cloud forest on tropical mountains), on the bare ground's climate
   next to coarse ice (PW-160: zoom.ice_ground).
2. Light: the slope's radiation index month by month (zoom_terrain): a
   poleward slope gets less light and less potential evaporation, and is
   cooler (SLOPE_DT C per unit of the index in summer and winter, at most
   SLOPE_DT_MAX), so it stays moister: north-facing forest and
   south-facing grass in semi-arid mountains.
3. Soil water from slope and position: steep slopes hold a thinner soil,
   hollows and valley floors (high topographic wetness index) a deeper one
   plus some groundwater (GW_SHARE of the local runoff in the wettest
   hollows).
4. Rivers: a strip along each river (RIP_W0 + RIP_W1 x log10(Q / 1 m^3/s)
   km wide; its share of the pixel) gets the river's water, up to the
   potential evaporation: gallery forest through savanna and steppe, oasis
   woodland along desert rivers.
5. Wet ground (the flooded habitat of vegetation.flooded, per pixel): big
   rivers' floodplains (low above the river), flat ground with a water
   surplus (mires), flat permafrost, lake shores, a coastal plain's
   marshes (zoom: wetland 1).
6. Competition and fire to equilibrium (vegetation.equilibrium) on the
   pixels, warm-started from the world's fractions (Gaussian-interpolated:
   the cell's history, forest or savanna), with seeds spreading between
   neighbouring pixels.
7. The pixels' mean cover of each type is pulled part of the way (CORR)
   back to the coarse cell's, by a smooth correction field, except where
   the pixel's height differs much from the coarse surface (CORR_DZ: a peak
   the coarse cell couldn't see).
8. Fire mosaic: where fire replaces stands, each pixel's time since the last
   one is drawn from the exponential distribution of stand ages (mean: the
   fire interval), with planet-fixed noise (patches ~FIRE_KM across), so
   overlapping zooms agree; young stands have fewer trees (regrowing at the
   type's own rate), more herbs and pioneers, and a lower canopy, old
   ones more, the mean kept.

The zoom stores the summary layers only (decision 9A); fractions() rebuilds
the per-type fractions of a saved zoom on demand, from the world and the
zoom's stored terrain (same numbers as at build time).
"""

from __future__ import annotations

import time
from types import SimpleNamespace

import numpy as np

from . import climate
from . import vegetation as V
from . import zoom_kernels as ZK
from . import zoom_terrain as ZT
from .climate import LAPSE
from .geo import R_KM, latlon

SLOPE_DT = (4.0, 2.0)  # C per unit of radiation index, summer and winter half-year
SLOPE_DT_MAX = 2.5  # C
GW_SHARE = 0.5  # share of the local runoff the wettest hollows get as groundwater
TWI_REF = 0.05  # tan slope: a pixel draining only itself on this slope is the TWI baseline
TWI_WET = (2.0, 7.0)  # TWI above the baseline: from no groundwater to full (valley floors)
DEEP_SOIL = 0.3  # deeper subsoil in the wettest hollows (x)
STEEP_TAN = (0.2, 0.7)  # tan slope: soil thins from here (~11 deg) to SOIL_THIN at the other (~35 deg)
SOIL_THIN = 0.6
RIP_W0, RIP_W1 = 0.15, 0.4  # km: riparian strip width at 1 m^3/s, and per tenfold more
RIP_SHARE = 0.9  # share of the potential evaporation a river supplies its strip
PLAIN_Q = 100.0  # m^3/s: rivers with floodplains (on a cell: 500)
MIRE_KM = 20.0  # km: the size of the mires' patches (noise on the wetness rank)
FW_MAX = 0.75  # most of a pixel that is flooded (as of a cell: vegetation.flooded)
FLAT_TAN = 0.02  # tan slope under which ground counts as flat for wetlands
CORR, CORR_DZ = 0.6, 800.0  # pull towards the coarse cell's cover, faded out over this much height difference (m)
FIRE_KM = 25.0  # km: the size of the fire mosaic's patches
STEPS = ((10, 2.0), (50, 10.0))  # competition steps (count, years) from the warm start
CHUNK = 40000
SEA_W = 0.02  # weight of the sea cells in the pixels' rain and cloud (the land cells' count)  # pixels per potential-productivity batch (memory)
WETLAND_TYPES = {V.T[k] for k in ("tropical swamp forest", "tropical peat swamp forest", "seasonally flooded grassland",
                                  "freshwater marsh and reedbed", "temperate and boreal swamp forest", "raised bog",
                                  "fen", "permafrost peatland (palsa and polygon mire)")}


def _sel(g, fr, size_km: float) -> np.ndarray:
    """The coarse cells around the region (as zoom.build)."""
    sp = g.spacing * R_KM
    ang = np.arccos(np.clip(g.centers @ fr.c, -1, 1)) * R_KM
    return np.flatnonzero(ang < size_km * 0.7072 + 4 * sp)


def fine_fields(world: dict, fr, px: np.ndarray, py: np.ndarray, size_km: float) -> dict:
    """The coarse climate the zoom's pixels need, Gaussian-interpolated as
    zoom.build does its fields (sigma half a cell): temperatures reduced to
    sea level (annual, warmest and coldest month; on the bare ground under
    any coarse ice, zoom.ice_ground), the July / January half-years' rain
    (mm/yr), cloud (0..1; None without), runoff (mm/yr, the land's), and
    the world's vegetation fractions (NP, n; land without ice; None without)."""
    from .zoom import ice_ground
    g, L = world["grid"], world["layers"]
    sp = g.spacing * R_KM
    sel = _sel(g, fr, size_km)
    cx, cy = fr.to_plane(g.centers[sel])
    elev = np.asarray(L["elevation"], float)
    e = elev[sel]
    up = LAPSE * np.maximum(e, 0)
    land_c = e > 0
    ice = np.asarray(L.get("ice", np.zeros(g.n)), float)
    tw = np.asarray(L.get("warm_month", L["temperature"]), float)
    tc = np.asarray(L["cold_month"], float) if "cold_month" in L else 2 * np.asarray(L["temperature"], float) - tw
    gw, gc, _ = ice_ground(g, L, ice)
    # (annual: the world's, moved with the months under ice)
    ta = np.asarray(L["temperature"], float) + 0.5 * ((gw - tw) + (gc - tc))
    prc = np.asarray(L["precipitation"], float)
    pj = np.asarray(L.get("precipitation_jul", prc), float)
    pn = np.asarray(L.get("precipitation_jan", prc), float)
    has_cloud = "cloud_jul" in L and "cloud_jan" in L
    cj = np.asarray(L["cloud_jul"], float) / 100 if has_cloud else np.zeros(g.n)
    cn = np.asarray(L["cloud_jan"], float) / 100 if has_cloud else np.zeros(g.n)
    ro = np.asarray(L["runoff"] if "runoff" in L else prc, float)
    cov = climate.ice_cover(g, ice, elev > 0)
    vals = np.column_stack([ta[sel] + up, gw[sel] + up, gc[sel] + up, pj[sel], pn[sel], cj[sel], cn[sel], ro[sel],
                            cov[sel]])
    # (the land's: the sea cells' rain, cloud and runoff count only where no land cell is near, e.g. an island)
    wts = np.where(land_c, 1.0, SEA_W)[:, None] * np.ones_like(vals)
    wts[:, [0, 1, 2, 8]] = 1.0
    wts[:, 7] = land_c
    fine, _ = ZK.gauss_interp(px, py, cx, cy, vals, wts, 0.5 * sp)
    fine = np.nan_to_num(fine, nan=0.0)
    out = dict(t_sl=fine[:, 0], warm_sl=fine[:, 1], cold_sl=fine[:, 2], p_jul=np.maximum(fine[:, 3], 0),
               p_jan=np.maximum(fine[:, 4], 0), cloud_jul=fine[:, 5] if has_cloud else None,
               cloud_jan=fine[:, 6] if has_cloud else None, runoff=np.maximum(fine[:, 7], 0),
               ice_cover=np.clip(fine[:, 8], 0, 1), nu0=None)
    if all(f"veg_{c}" in L for c in V.CODES):
        nu_c = np.stack([np.asarray(L[f"veg_{c}"], float)[sel] / 100 for c in V.CODES], 1)
        w = (land_c & (ice[sel] <= 0)).astype(float)
        f, _ = ZK.gauss_interp(px, py, cx, cy, nu_c, np.repeat(w[:, None], V.NP, 1), 0.5 * sp)
        out["nu0"] = np.nan_to_num(f.T, nan=0.0)
    return out


def _neighbours(idx: np.ndarray, nx: int, ny: int) -> SimpleNamespace:
    """The 4-neighbours among the pixels idx, as a grid-like CSR (n, nbr_off,
    nbr_idx) for vegetation.equilibrium's seed spread."""
    pos = np.full(nx * ny, -1, np.int64)
    pos[idx] = np.arange(len(idx))
    r, c = idx // nx, idx % nx
    nb = []
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        rr, cc = r + dr, c + dc
        ok = (rr >= 0) & (rr < ny) & (cc >= 0) & (cc < nx)
        j = np.where(ok, pos[np.clip(rr, 0, ny - 1) * nx + np.clip(cc, 0, nx - 1)], -1)
        nb.append(j)
    nb = np.stack(nb, 1)
    cnt = (nb >= 0).sum(1)
    off = np.concatenate([[0], np.cumsum(cnt)]).astype(np.int64)
    flat = nb[nb >= 0].astype(np.int64)  # (row-major: each pixel's neighbours in turn)
    return SimpleNamespace(n=len(idx), nbr_off=off, nbr_idx=flat)


def _uniform(z):
    """Standard normal -> uniform (0, 1)."""
    return np.clip(0.5 * (1 + climate._erf(z / np.sqrt(2))), 1e-4, 1 - 1e-4)


def surface(elevation, lake_depth, water) -> np.ndarray:
    """The surface the terrain indices see: the ground, a lake's water
    surface, 0 at sea (float32 arithmetic, as the stored layers)."""
    e, d = np.asarray(elevation, np.float32), np.asarray(lake_depth, np.float32)
    return np.where(water == 1, np.float32(0), np.where(water == 2, e + d, e)).astype(float)


def compute(world: dict, fr, nx: int, ny: int, res: float, seed: int, size_km: float, h, water, ice, discharge,
            area, marsh, fields: dict | None = None, log=print, want_fractions: bool = False) -> dict:
    """Vegetation of a zoom (see the module doc). h: ground (m, lake beds
    included) and water (0 land, 1 sea, 2 lake), with lake_depth folded in
    by the caller as h_surface; ice (m), discharge (m^3/s), area
    (drainage_area, km^2), marsh (a coastal plain's marsh, bool), all (n,)
    as the zoom stores them. Returns {layers: the zoom layers, terrain:
    zoom_terrain.indices, stats, nu (NP, n_veg) and idx when
    want_fractions}."""
    t0 = time.time()
    n = nx * ny
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    px, py = X.ravel(), Y.ravel()
    P = fr.to_sphere(px, py)
    lat = latlon(P)[0]
    g, L, meta = world["grid"], world["layers"], world.get("meta", {})
    tilt = float(meta.get("params", {}).get("tilt", 23.4))
    vm = meta.get("vegetation", {})
    co2 = float(vm.get("co2", 0.0))
    unlocked = np.array([c in vm["pfts"] for c in V.CODES]) if "pfts" in vm else V.all_unlocked()
    if fields is None:
        fields = fine_fields(world, fr, px, py, size_km)
    sea, lake = water == 1, water == 2
    h = np.where(sea, 0.0, np.asarray(h, float))
    land = water == 0
    glacier = land & (np.asarray(ice) > 0)
    tr = ZT.indices(h, land, sea, np.asarray(discharge, float), np.asarray(area, float), lat, nx, ny, res, tilt)
    veg = land & ~glacier
    idx = np.flatnonzero(veg)
    nv = len(idx)
    hv = np.maximum(h[idx], 0)
    out_type = np.where(sea, 0, np.where(lake, V.T["lake"], np.where(glacier, V.T["ice"], 0))).astype(np.uint8)
    zeros = np.zeros(n)
    res_layers = dict(vegetation=out_type, tree_cover=zeros, plant_cover=zeros, lai=zeros, canopy_height=zeros,
                      npp=zeros, fire_return=zeros)
    if nv == 0:
        return dict(layers=res_layers, terrain=tr, stats={}, idx=idx, nu=np.zeros((V.NP, nv)))

    # --- the pixels' climate --------------------------------------------
    north = lat[idx] >= 0
    temp = fields["t_sl"][idx] - LAPSE * hv
    t_warm = fields["warm_sl"][idx] - LAPSE * hv
    t_cold = fields["cold_sl"][idx] - LAPSE * hv
    ri = tr["ri12"][:, idx]
    summer = np.zeros((12, 1), bool)
    summer[3:9] = True
    summer_half = np.where(north[None, :], summer, ~summer)
    ri_s = np.where(summer_half, ri, 0).sum(0) / 6
    ri_w = np.where(~summer_half, ri, 0).sum(0) / 6
    dtw = np.clip(SLOPE_DT[0] * (ri_s - 1), -SLOPE_DT_MAX, SLOPE_DT_MAX)
    dtc = np.clip(SLOPE_DT[1] * (ri_w - 1), -SLOPE_DT_MAX, SLOPE_DT_MAX)
    t_warm, t_cold, temp = t_warm + dtw, t_cold + dtc, temp + 0.5 * (dtw + dtc)
    # water: groundwater in hollows, a river's water along its banks
    twi_rel = tr["twi"][idx] - np.log(res * 1000.0 / TWI_REF)
    wet = np.clip((twi_rel - TWI_WET[0]) / (TWI_WET[1] - TWI_WET[0]), 0, 1)
    gw = GW_SHARE * fields["runoff"][idx] * wet
    rq = tr["river_q"][idx]
    width = RIP_W0 + RIP_W1 * np.log10(np.maximum(rq, ZT.RIVER_Q) / ZT.RIVER_Q)  # km
    dist = tr["river_dist"][idx] * res  # km from the nearest river pixel's centre
    # (the share of the pixel inside the strip, the river through the nearest river pixel's centre)
    rip = np.clip((np.minimum(dist + 0.5 * res, 0.5 * width) - np.maximum(dist - 0.5 * res, -0.5 * width)) / res, 0, 1)
    rip = np.where(np.isfinite(dist), rip, 0.0)
    slope = tr["slope"][idx]
    cap2 = V.DEEP_MM * (1 - (1 - SOIL_THIN) * np.clip((slope - STEEP_TAN[0]) / (STEEP_TAN[1] - STEEP_TAN[0]), 0, 1)) \
        * (1 + DEEP_SOIL * wet)
    cj = fields["cloud_jul"][idx] if fields["cloud_jul"] is not None else None
    cn = fields["cloud_jan"][idx] if fields["cloud_jan"] is not None else None
    pj, pn = fields["p_jul"][idx], fields["p_jan"][idx]
    latv = lat[idx]
    nu0 = fields["nu0"][:, idx] if fields["nu0"] is not None else None

    # --- productivity, in batches -----------------------------------------
    s1 = {}
    pot = {k: np.zeros((V.NP, nv)) for k in ("npp", "net", "lai", "on_jul", "on_jan")}
    pot["ok"] = np.zeros((V.NP, nv), bool)
    one_d = ("tc", "tw", "tmin", "gdd5", "temp", "precip", "pet_y", "mi", "dry", "lat", "p_summer", "p_winter",
             "fire_season", "dryair", "cap1", "cap2", "cloud")
    for a in range(0, nv, CHUNK):
        b = min(a + CHUNK, nv)
        sl = slice(a, b)
        s = V.site(latv[sl], temp[sl], t_warm[sl], t_cold[sl], pj[sl], pn[sl], tilt,
                   None if cj is None else cj[sl], None if cn is None else cn[sl],
                   light=ri[:, sl], extra_water=gw[sl], extra_pet=RIP_SHARE * rip[sl])
        s["cap2"] = cap2[sl]
        env = V.envelope(s, co2)
        viable = env & unlocked[:, None]
        eff = np.ones((V.NP, b - a))
        for p_, q_ in zip(*np.nonzero(V.standin_map(unlocked))):
            extra = env[q_] & ~env[p_]
            viable[p_] |= extra
            eff[p_] = np.where(extra, V.STANDIN_EFF, eff[p_])
        pt = V.potential(s, viable, eff, co2)
        for k in pot:
            pot[k][:, sl] = pt[k] if k != "ok" else pt["ok"] & viable
        for k in one_d:
            if s.get(k) is not None:
                s1.setdefault(k, []).append(np.asarray(s[k], float))
    s = {k: np.concatenate(v) for k, v in s1.items()}
    s.setdefault("cloud", None)

    # --- wet ground ---------------------------------------------------------
    # the coarse cells (for the flooded share's and the cover's cell means)
    sel = _sel(g, fr, size_km)
    lut = np.full(g.n, -1)
    lut[sel] = np.arange(len(sel))
    own = lut[g.locate(P[idx])]
    cnt = np.bincount(own, minlength=len(sel)).astype(float)
    full_px = 4 * np.pi * R_KM ** 2 / g.n / res ** 2
    cx, cy = fr.to_plane(g.centers[sel])
    sig = 0.5 * g.spacing * R_KM
    ok_c = (cnt > 0.25 * full_px) & (np.asarray(L["elevation"])[sel] > 0)

    flat = np.clip(1 - slope / FLAT_TAN, 0, 1)
    rain_mi = s["precip"] / np.maximum(s["pet_y"], 1.0)
    hand = h[idx] - tr["river_h"][idx]  # height above the nearest river
    big = np.clip(np.log10(np.maximum(rq, 1.0) / PLAIN_Q) / 1.5, 0, 1)
    plain = big * np.clip(1 - hand / (2.0 + 4.0 * big), 0, 1) * np.maximum(flat, 0.3) * (dist < 30.0)
    near_lake = ZT.nearest(lake, nx, ny)[0][idx] <= 1.5
    shore = 0.5 * near_lake * flat
    coast = 0.85 * np.asarray(marsh, bool)[idx]
    if "flooded" in L:
        # The world's flooded share of each cell, as that share of its pixels
        # (a little more, FW_MAX of each, being under water): the wettest
        # ground by rank within the cell, hollows and valley floors (TWI)
        # first, with planet-fixed noise for the mires' patches (MIRE_KM).
        # The cell's floodplain share (vegetation.floodplain) is left out:
        # the pixels' own floodplains, low above their big rivers, take it.
        fl_c = np.asarray(L["flooded"], float)[sel] / 100
        if "flow" in L:
            pl_c = V.floodplain(g, np.asarray(L["elevation"], float), np.asarray(L["flow"], float))[sel]
            fl_c = np.clip(1 - (1 - fl_c) / np.maximum(1 - pl_c, 1e-6), 0, 1)
        f, _ = ZK.gauss_interp(px[idx], py[idx], cx, cy, fl_c[:, None], (np.asarray(L["elevation"])[sel] > 0)[:, None]
                               .astype(float), sig)
        Pk = np.ascontiguousarray(P[idx] * R_KM)
        noise = ZK.fbm(Pk, MIRE_KM, max(1, int(np.ceil(np.log2(MIRE_KM / (3 * res)))) + 1), 0.5,
                       int(seed) * 1_000_003 + 17 + 307) / 0.17
        score = 0.5 * np.clip(twi_rel, -3.0, 8.0) + 2.0 * noise
        order = np.lexsort((score, own))
        first = np.concatenate([[0], np.cumsum(cnt)])[:-1]
        rank = np.empty(nv)
        rank[order] = (np.arange(nv) - first[own[order]] + 0.5) / np.maximum(cnt[own[order]], 1)
        q = np.nan_to_num(f[:, 0]) / FW_MAX
        fw_g = 1 - (1 - FW_MAX * np.clip((rank - (1 - q)) / 0.1 + 0.5, 0, 1)) * (1 - 0.8 * plain)
    else:  # (no flooded layer: the cell formula of vegetation.flooded on the pixel's own ground)
        mire = 0.8 * np.clip((rain_mi - 0.9) / 0.6, 0, 1) * flat ** 2 * np.clip((10.0 - s["temp"]) / 10.0, 0.3, 1.0) \
            * (0.4 + 0.6 * wet)
        perma = 0.45 * (s["temp"] < -2) * np.clip(s["precip"] / 400.0, 0, 1) * flat ** 2 * (0.5 + 0.5 * wet)
        fw_g = 1 - (1 - 0.8 * plain) * (1 - mire) * (1 - perma)
    fw = np.clip(1 - (1 - fw_g) * (1 - shore) * (1 - coast), 0, FW_MAX)

    # --- competition and fire to equilibrium -------------------------------
    grid = _neighbours(idx, nx, ny)
    eq = V.equilibrium(grid, s, pot, fw, np.ones(nv, bool), nu0, STEPS)
    nu = eq["nu"]

    # --- pulled towards the coarse cells' cover ------------------------------
    if fields["nu0"] is not None and CORR > 0:
        world_nu = np.stack([np.asarray(L[f"veg_{c}"], float)[sel] / 100 for c in V.CODES])
        mean = np.stack([np.bincount(own, nu[p], minlength=len(sel)) for p in range(V.NP)]) / np.maximum(cnt, 1)
        lr = np.where(ok_c[None, :], np.log(np.clip((world_nu + 0.02) / (mean + 0.02), 0.5, 2.0)), 0.0)
        fl, _ = ZK.gauss_interp(px[idx], py[idx], cx, cy, lr.T.copy(), np.repeat(ok_c[:, None], V.NP, 1).astype(float),
                                sig)
        # (the smooth coarse surface the cell means were taken on: e_land in zoom.build)
        e_c = np.maximum(np.asarray(L["elevation"], float)[sel], 1.0)
        es, _ = ZK.gauss_interp(px[idx], py[idx], cx, cy, e_c[:, None], (e_c > 1.0)[:, None].astype(float), sig)
        wz = CORR * np.clip(1 - np.abs(hv - np.nan_to_num(es[:, 0], nan=0.0)) / CORR_DZ, 0, 1)
        tot0 = nu.sum(0)
        nu = np.where(pot["ok"], nu * np.exp(wz[None, :] * np.nan_to_num(fl.T)), 0.0)
        tot1 = nu.sum(0)
        nu = nu * np.where(tot1 > 0, np.minimum(tot0, 1.0) / np.maximum(tot1, 1e-9), 0.0)

    # --- fire mosaic ------------------------------------------------------------
    resist, mort = V._col("resist"), V._col("gamma")
    b = eq["burned"]
    trees = V.TREES
    nt = nu[trees].sum(0)
    r_t = (nu[trees] * resist[trees, None]).sum(0) / np.maximum(nt, 1e-9)
    m_fire = 1.0 / np.maximum(b * (1 - r_t), 1e-6)  # years between stand-replacing fires
    burns = (b > 1e-3) & (nt > 0.02) & (m_fire < 2000)
    age = np.full(nv, np.inf)
    if burns.any():
        Pk = np.ascontiguousarray(P[idx] * R_KM)
        S = int(seed) * 1_000_003 + 17
        z = ZK.fbm(Pk, FIRE_KM, max(1, int(np.ceil(np.log2(FIRE_KM / (2 * res)))) + 1), 0.55, S + 301) / 0.17
        u = _uniform(z)
        age = np.where(burns, -m_fire * np.log(1 - u), np.inf)
        T = np.clip(1.0 / np.maximum(eq["g"], 1e-3), 10.0, 150.0)  # years a type takes to regrow
        fac = np.where(burns[None, :] & trees[:, None],
                       (1 - np.exp(-age[None, :] / T)) * (m_fire[None, :] + T) / m_fire[None, :], 1.0)
        new_t = nu * fac
        freed = np.maximum(nu[trees].sum(0) - new_t[trees].sum(0), 0.0)
        nu = np.where(trees[:, None], new_t, nu)
        # the freed ground: in boreal forest half to pioneers (birch, aspen), the rest herbs and shrubs
        pio = np.zeros(V.NP, bool)
        pio[V.IDX["BoBS"]] = True
        boreal = np.zeros(V.NP, bool)
        boreal[[V.IDX[c] for c in ("BoNE", "BoNS", "BoBS")]] = True
        bor = nu[boreal].sum(0) >= 0.5 * np.maximum(nu[trees].sum(0), 1e-9)
        pio_ok = pot["ok"] & pio[:, None] & bor[None, :]
        n_pio = pio_ok.sum(0)
        nu = nu + np.where(pio_ok, 0.5 * freed / np.maximum(n_pio, 1), 0.0)
        rest = freed * np.where(n_pio > 0, 0.5, 1.0)
        low = (V.HERBS | V.SHRUBS)[:, None] & pot["ok"]
        share = np.where(low, np.maximum(nu, 0.01), 0.0)
        nu = nu + share / np.maximum(share.sum(0), 1e-9) * rest
        tot = nu.sum(0)
        nu = np.where(tot > 1, nu / np.maximum(tot, 1e-9), nu)
    eq = dict(eq, nu=nu)

    # --- structure and named types -----------------------------------------
    sm = V.summary(s, pot, eq)
    # canopy height from the pixel's own stand age where fire set it
    hfrac = np.sqrt(np.clip(pot["lai"] / V._col("laimax")[:, None], 0, 1))
    hh = V._col("hmax")[:, None] * hfrac * np.where(trees[:, None], 1 - np.exp(-np.minimum(age, sm["stand_age"]) / 60.0)[None, :], 1.0)
    sm["height"] = np.where(nu > 0.1, hh, 0.0).max(0)
    types = V.classify(s, eq, sm, hv, fw=fw)
    # oasis and desert riparian woodland: trees by a river through dry land
    desert = rain_mi < 0.3
    types = np.where((rip > 0.2) & desert & (sm["tree"] >= 0.1) & ~np.isin(types, list(WETLAND_TYPES)),
                     V.T["oasis / desert riparian woodland"], types)

    def put(v, dtype=float):
        a = np.zeros(n, dtype)
        a[idx] = v
        return a

    layers = dict(
        vegetation=np.where(veg, put(types, np.uint8), out_type).astype(np.uint8),
        tree_cover=put(100 * sm["tree"]), plant_cover=put(100 * sm["cover"]), lai=put(sm["lai"]),
        canopy_height=put(sm["height"]), npp=put(sm["npp"]),
        fire_return=put(np.minimum(np.where(eq["burned"] > 1e-4, 1 / np.maximum(eq["burned"], 1e-9), 0.0), 9999)),
    )
    lt = np.bincount(types, minlength=len(V.TYPES))
    top = np.argsort(-lt)[:10]
    stats = {"vegetation_pct": {V.TYPES[k][1]: round(float(100 * lt[k] / nv), 1) for k in top if lt[k] > 0},
             "tree_cover_mean_pct": round(float(100 * sm["tree"].mean()), 1),
             "npp_mean": round(float(sm["npp"].mean())),
             "wetland_pct": round(100 * float(np.isin(types, list(WETLAND_TYPES)).mean()), 2),
             "riparian_px": int((rip > 0.2).sum()),
             "seconds": round(time.time() - t0, 1)}
    log(f"  vegetation: {nv} px, trees {stats['tree_cover_mean_pct']}% [{time.time() - t0:.1f}s]")
    out = dict(layers=layers, terrain=tr, stats=stats, idx=idx, fw=put(fw))
    if want_fractions:
        out["nu"] = nu
    return out


def fractions(zoom_ref) -> dict:
    """Per-type cover fractions of a saved zoom, recomputed (decision 9A:
    zooms store the summary layers only): {code: (ny, nx) fractions}, plus
    'vegetation' (the named types, as stored)."""
    from . import world as W
    from .zoom import Frame, find_world, load
    meta, lay = load(zoom_ref, decode=True)
    world = W.load(find_world(meta["source_world"]["id"]))
    nx, ny, res = meta["nx"], meta["ny"], meta["res_km"]
    fr = Frame(meta["center"]["lat"], meta["center"]["lon"])
    surf = surface(lay["elevation"].ravel(), lay["lake_depth"].ravel(), lay["water"].ravel())
    r = compute(world, fr, nx, ny, res, meta["seed"], meta["size_km"], surf, lay["water"].ravel(),
                lay["ice"].ravel(), lay["discharge"].ravel(), lay["drainage_area"].ravel(),
                (lay.get("wetland", np.zeros((ny, nx))) == 1).ravel(), log=lambda *a: None, want_fractions=True)
    out = {}
    for p, c in enumerate(V.CODES):
        a = np.zeros(nx * ny)
        a[r["idx"]] = r["nu"][p]
        out[c] = a.reshape(ny, nx)
    out["vegetation"] = r["layers"]["vegetation"].reshape(ny, nx)
    return out
