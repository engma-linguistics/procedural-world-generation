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
3. Soil (soils.zoom_mineral, PW-331): the soils' mineral pass on the
   pixel's own slope, floodplains and river strips, hollows (colluvium),
   glaciers and rock gives the water the soil holds (thin on steep slopes,
   deep in hollows and on alluvium) and a mild fertility factor on NPP, as
   on the globe; hollows and valley floors (high topographic wetness index)
   also get some groundwater (GW_SHARE of the local runoff in the wettest
   hollows). The organic pass after the vegetation (soil carbon, peat, the
   named types) gives the zoom's soil layers.
4. Rivers: a strip along each river (RIP_W0 + RIP_W1 x log10(Q / 1 m^3/s)
   km wide) gets the river's water, up to the potential evaporation. The
   strip is a habitat of its own inside the pixel (PW-221): where it covers
   some of a pixel (over RIP_MIN), the pixel's plants compete twice, on the
   dry ground and in the strip, and the pixel's cover is the two mixed by
   the strip's share. So a 2-4 km pixel along a desert river is mostly
   desert with a ribbon of woodland, not one mediocre cover; it is named
   oasis / desert riparian woodland where the strip holds a woodland and
   is the pixel's only one (or a fifth of the pixel): gallery forest
   through savanna and steppe, oasis woodland along desert rivers.
5. Wet ground (the flooded habitat of vegetation.flooded, per pixel): big
   rivers' floodplains (low above the river), flat ground with a water
   surplus (mires), flat permafrost, lake shores, a coastal plain's
   marshes (zoom: wetland 1).
6. Competition and fire to equilibrium (vegetation.equilibrium) on the
   pixels, warm-started from the world's fractions (Gaussian-interpolated
   over NU0_SIGMA of a cell at a planet-fixed wandering offset, so the
   cells' forest / open edges don't come out as straight lines along their
   rows: the cell's history, forest or savanna), with seeds spreading
   between neighbouring pixels.
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
from . import soils as SO
from . import store as S
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
RIP_W0, RIP_W1 = 0.15, 0.4  # km: riparian strip width at 1 m^3/s, and per tenfold more
RIP_SHARE = 0.9  # share of the potential evaporation a river supplies its strip
RIP_MIN = 0.02  # share of a pixel the strip must cover to be a habitat of its own there
PLAIN_Q = 100.0  # m^3/s: rivers with floodplains (on a cell: 500)
MIRE_KM = 20.0  # km: the size of the mires' patches (noise on the wetness rank)
FW_MAX = 0.75  # most of a pixel that is flooded (as of a cell: vegetation.flooded)
FLAT_TAN = 0.02  # tan slope under which ground counts as flat for wetlands
CORR, CORR_DZ = 0.6, 800.0  # pull towards the coarse cell's cover, faded out over this much height difference (m)
FIRE_KM = 25.0  # km: the size of the fire mosaic's patches
# The warm start (PW-374): the world's cover is mostly forest or open cell by
# cell (the same bistability), so a half-cell kernel draws its edges along the
# coarse cells' rows, and the pixels' competition, bistable too, keeps them
# as ruler-straight lines and rectangles. History below a cell is unknown:
# read it with a wider kernel, at a planet-fixed wandering offset (rough:
# fbm down to ~8 km), so the pixels' forest / open edges meander
NU0_SIGMA = 0.6  # the warm start's interpolation kernel, x the cell spacing
NU0_WARP, NU0_WARP_L = 0.4, 0.7  # the offset: sd and patch size, x the cell spacing
NU0_WARP_GAIN = 0.75  # its fbm gain (rough, so the edges meander at every scale)
WARP_SEED = 1_000_003 * 7 + 401
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
    sea level (annual, warmest and coldest month: July and January
    interpolated, then the warmer of the two, with jul_warm (bool) where
    that is July; on the bare ground under any coarse ice,
    zoom.ice_ground), the July / January half-years' rain
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
    gw, gc = ice_ground(g, L, ice)
    # (annual: the world's, moved with the months under ice)
    ta = np.asarray(L["temperature"], float) + 0.5 * ((gw - tw) + (gc - tc))
    # July and January, not the warmest and coldest month: those swap at the
    # equator, so interpolating them and swapping back per pixel would put a
    # step of the whole seasonal swing on the pixel row at latitude 0 (PW-374)
    nc = g.lat >= 0
    gw, gc = np.where(nc, gw, gc), np.where(nc, gc, gw)
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
    jul_warm = fine[:, 1] >= fine[:, 2]
    out = dict(t_sl=fine[:, 0], warm_sl=np.maximum(fine[:, 1], fine[:, 2]), cold_sl=np.minimum(fine[:, 1], fine[:, 2]),
               jul_warm=jul_warm, p_jul=np.maximum(fine[:, 3], 0),
               p_jan=np.maximum(fine[:, 4], 0), cloud_jul=fine[:, 5] if has_cloud else None,
               cloud_jan=fine[:, 6] if has_cloud else None, runoff=np.maximum(fine[:, 7], 0),
               ice_cover=np.clip(fine[:, 8], 0, 1), nu0=None)
    if all(f"veg_{c}" in L for c in V.CODES):
        nu_c = np.stack([np.asarray(L[f"veg_{c}"], float)[sel] / 100 for c in V.CODES], 1)
        w = (land_c & (ice[sel] <= 0)).astype(float)
        wx, wy = history_warp(fr, px, py, sp)
        f, _ = ZK.gauss_interp(px + wx, py + wy, cx, cy, nu_c, np.repeat(w[:, None], V.NP, 1), NU0_SIGMA * sp)
        out["nu0"] = np.nan_to_num(f.T, nan=0.0)
    return out


def history_warp(fr, px, py, sp: float) -> tuple[np.ndarray, np.ndarray]:
    """Where each pixel reads the world's cover from for the warm start (km,
    added to px, py): a planet-fixed fbm offset (sd NU0_WARP cells, patches
    ~NU0_WARP_L cells across), so overlapping zooms agree and the warm
    start's forest / open edges wander as an unknown history would, rather
    than tracing the coarse cells' rows (PW-374)."""
    P = np.ascontiguousarray(fr.to_sphere(px, py) * R_KM)
    lam = NU0_WARP_L * sp
    octaves = max(1, int(np.ceil(np.log2(lam / 8.0))))
    a = NU0_WARP * sp / 0.17  # (fbm / 0.17: ~unit sd)
    return (a * ZK.fbm(P, lam, octaves, NU0_WARP_GAIN, WARP_SEED),
            a * ZK.fbm(P, lam, octaves, NU0_WARP_GAIN, WARP_SEED + 1))


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


def season_lat(lat, jul_warm) -> np.ndarray:
    """The latitude whose seasons a pixel's climate has, for the month
    models (climate.months: the warmest month is July north of the equator,
    January south of it): the pixel's own, mirrored where its interpolated
    July is the warmer month south of the equator or the colder one north
    of it. That happens only within a coarse cell or so of the equator,
    where July and January cross over smoothly (PW-374), so the months stay
    continuous across it; the mirrored latitude's light differs by a
    fraction of a degree."""
    lat = np.asarray(lat, float)
    return np.where(np.asarray(jul_warm, bool), np.abs(lat), -np.abs(lat))


def _uniform(z):
    """Standard normal -> uniform (0, 1)."""
    return np.clip(0.5 * (1 + climate._erf(z / np.sqrt(2))), 1e-4, 1 - 1e-4)


def surface(elevation, lake_depth, water) -> np.ndarray:
    """The surface the terrain indices see: the ground, a lake's water
    surface, 0 at sea (float32 arithmetic, as the stored layers)."""
    e, d = np.asarray(elevation, np.float32), np.asarray(lake_depth, np.float32)
    return np.where(water == 1, np.float32(0), np.where(water == 2, e + d, e)).astype(float)


def soil_mineral(world: dict, fr, pxv, pyv, sel, cell, lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul,
                 cloud_jan, slope, res, rock, landform, plain, strip, hollow, glacier, nx, ny, idx) -> dict:
    """soils.zoom_mineral on the bare land pixels idx (their climate,
    slope (tan), floodplain and river-strip shares, hollows, all (nv,)):
    the exposed rock and landform as the zoom stores them (n,; else the
    pixel's cell's), the cell's landform age, last glaciation and salt
    lakes nearby, its loess interpolated (land cells), and the zoom's
    glaciers' forefields."""
    g, L = world["grid"], world["layers"]
    rock = np.asarray(rock)[idx] if rock is not None else np.asarray(L.get("surface_rock", L["rock"]))[cell]
    if landform is not None:
        landform = np.asarray(landform)[idx]
    elif "landform" in L:
        landform = np.asarray(L["landform"])[cell]
    lfa = np.asarray(L["landform_age"], float)[cell] if "landform_age" in L else None
    glac = np.asarray(L["glaciated_myr"], float)[cell] if "glaciated_myr" in L else None
    salt = SO.salt_near(g, L["lake_kind"])[cell] if "lake_kind" in L else np.zeros(len(idx), bool)
    loess = np.zeros(len(idx))
    if "loess" in L:
        cx, cy = fr.to_plane(g.centers[sel])
        f, _ = ZK.gauss_interp(pxv, pyv, cx, cy, np.asarray(L["loess"], float)[sel][:, None],
                               (np.asarray(L["elevation"])[sel] > 0)[:, None].astype(float), 0.5 * g.spacing * R_KM)
        loess = np.nan_to_num(f[:, 0])
    ice_km = ZT.nearest(np.asarray(glacier, bool), nx, ny)[0][idx] * res
    return SO.zoom_mineral(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt, cloud_jul, cloud_jan, slope, res, rock,
                           landform, lfa, glac, plain, strip, hollow, loess, salt, ice_km)


# the zoom's soil layers (soils.world_layers' names, stored as on the globe: store.LAYERS)
SOIL_LAYER_DOC = {k: (S.LAYERS[k]["units"], S.LAYERS[k]["description"] + " (per pixel: soils.zoom_mineral)",
                      {f: S.LAYERS[k][f] for f in ("dtype", "scale", "offset")})
                  for k in ("soil", "soil_depth", "soil_texture", "soil_water", "soil_fertility", "soil_drainage",
                            "soil_carbon", "peat_depth", "permafrost", "loess")}


def compute(world: dict, fr, nx: int, ny: int, res: float, seed: int, size_km: float, h, water, ice, discharge,
            area, marsh, fields: dict | None = None, log=print, want_fractions: bool = False, rock=None,
            landform=None) -> dict:
    """Vegetation of a zoom (see the module doc). h: ground (m, lake beds
    included) and water (0 land, 1 sea, 2 lake), with lake_depth folded in
    by the caller as h_surface; ice (m), discharge (m^3/s), area
    (drainage_area, km^2), marsh (a coastal plain's marsh, bool), all (n,)
    as the zoom stores them; rock: the exposed rock (surface_rock) and
    landform (the coarse cells' class), for the soils. Returns {layers: the
    zoom layers (vegetation and soils), terrain:
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
                      npp=zeros, fire_return=zeros, **{k: zeros for k in SOIL_LAYER_DOC})
    if nv == 0:
        return dict(layers=res_layers, terrain=tr, stats={}, idx=idx, nu=np.zeros((V.NP, nv)))

    # --- the pixels' climate --------------------------------------------
    # (the seasons: July is summer where it is the warmer month, PW-374)
    north = np.asarray(fields["jul_warm"], bool)[idx]
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
    cj = fields["cloud_jul"][idx] if fields["cloud_jul"] is not None else None
    cn = fields["cloud_jan"][idx] if fields["cloud_jan"] is not None else None
    pj, pn = fields["p_jul"][idx], fields["p_jan"][idx]
    latv = season_lat(lat[idx], north)
    nu0 = fields["nu0"][:, idx] if fields["nu0"] is not None else None

    # the coarse cells (for the flooded share's and the cover's cell means)
    sel = _sel(g, fr, size_km)
    lut = np.full(g.n, -1)
    lut[sel] = np.arange(len(sel))
    cell = g.locate(P[idx])
    own = lut[cell]
    cnt = np.bincount(own, minlength=len(sel)).astype(float)
    full_px = 4 * np.pi * R_KM ** 2 / g.n / res ** 2
    cx, cy = fr.to_plane(g.centers[sel])
    sig = 0.5 * g.spacing * R_KM
    ok_c = (cnt > 0.25 * full_px) & (np.asarray(L["elevation"])[sel] > 0)
    # the big rivers' floodplains: low above the river
    flat = np.clip(1 - slope / FLAT_TAN, 0, 1)
    hand = h[idx] - tr["river_h"][idx]  # height above the nearest river
    # the rivers' floods (PW-028): a spring-flood or monsoon river floods
    # more of its plain, and higher (stage ~ discharge^0.4), than a steady one
    fs = V.flood_scale(np.asarray(L["flood_ratio"], float)[sel][np.maximum(own, 0)]) if "flood_ratio" in L else 1.0
    big = np.clip(np.log10(np.maximum(rq * fs, 1.0) / PLAIN_Q) / 1.5, 0, 1)
    plain = big * np.clip(1 - hand / ((2.0 + 4.0 * big) * fs ** 0.4), 0, 1) * np.maximum(flat, 0.3) * (dist < 30.0)

    # --- soils, mineral pass (soils.zoom_mineral): the water the soil holds,
    # its fertility and permafrost, for the vegetation
    t_s = time.time()
    sp_m = soil_mineral(world, fr, px[idx], py[idx], sel, cell, latv, temp, t_warm, t_cold, pj, pn, tilt,
                        cj, cn, slope, res, rock, landform, plain, rip, wet, glacier, nx, ny, idx)
    t_soil = time.time() - t_s

    # --- productivity, in batches -----------------------------------------
    s1 = {}
    one_d = ("tc", "tw", "tmin", "gdd5", "temp", "precip", "pet_y", "mi", "dry", "lat", "p_summer", "p_winter",
             "fire_season", "summer_drought", "dryair", "cap1", "cap2", "cloud")
    # (the pixels' dry ground, then the river strips of those that have one:
    # base maps each of these habitats to its pixel)
    rsel = np.flatnonzero(rip > RIP_MIN)
    nr = len(rsel)
    base = np.concatenate([np.arange(nv), rsel])
    ep = np.concatenate([np.zeros(nv), np.full(nr, RIP_SHARE)])
    nh = nv + nr
    pot = {k: np.zeros((V.NP, nh)) for k in ("npp", "net", "lai", "on_jul", "on_jan")}
    pot["ok"] = np.zeros((V.NP, nh), bool)
    pot["c4_share"] = np.full(nh, 0.5)  # (the grasses' C4 share, vegetation.potential)
    for a in range(0, nh, CHUNK):
        b = min(a + CHUNK, nh)
        sl = base[a:b]
        s = V.site(latv[sl], temp[sl], t_warm[sl], t_cold[sl], pj[sl], pn[sl], tilt,
                   None if cj is None else cj[sl], None if cn is None else cn[sl],
                   light=ri[:, sl], extra_water=gw[sl], extra_pet=ep[a:b])
        s["cap1"], s["cap2"] = sp_m["cap1"][sl], sp_m["cap2"][sl]
        f_soil = sp_m["f_soil"][sl][None, :]
        sl = slice(a, b)
        env = V.envelope(s, co2)
        viable = env & unlocked[:, None]
        eff = np.ones((V.NP, b - a))
        for p_, q_ in zip(*np.nonzero(V.standin_map(unlocked))):
            extra = env[q_] & ~env[p_]
            viable[p_] |= extra
            eff[p_] = np.where(extra, V.STANDIN_EFF, eff[p_])
        pt = V.potential(s, viable, eff, co2)
        pt = dict(pt, npp=pt["npp"] * f_soil, net=pt["net"] * f_soil)  # (the soil's fertility, as on the globe)
        for k in pot:
            if k == "c4_share":
                pot[k][sl] = pt[k]
            else:
                pot[k][:, sl] = pt[k] if k != "ok" else pt["ok"] & viable
        for k in one_d:
            if s.get(k) is not None:
                s1.setdefault(k, []).append(np.asarray(s[k], float))
    s_h = {k: np.concatenate(v) for k, v in s1.items()}
    s_h.setdefault("cloud", None)
    s = {k: (None if v is None else v[:nv]) for k, v in s_h.items()}  # the pixels' own (dry ground) site

    # --- wet ground ---------------------------------------------------------
    rain_mi = s["precip"] / np.maximum(s["pet_y"], 1.0)
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
            pl_c = V.floodplain(g, np.asarray(L["elevation"], float), np.asarray(L["flow"], float),
                                flood_ratio=L.get("flood_ratio"))[sel]
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
        perma = 0.45 * V.PERMA_WET[sp_m["permafrost"]] * np.clip(s["precip"] / 400.0, 0, 1) * flat ** 2 \
            * (0.5 + 0.5 * wet)
        fw_g = 1 - (1 - 0.8 * plain) * (1 - mire) * (1 - perma)
    fw = np.clip(1 - (1 - fw_g) * (1 - shore) * (1 - coast), 0, FW_MAX)

    # --- competition and fire to equilibrium -------------------------------
    # (the strips seed each other along the river, the dry ground each other)
    g_d, g_r = _neighbours(idx, nx, ny), _neighbours(idx[rsel], nx, ny)
    grid = SimpleNamespace(n=nh, nbr_off=np.concatenate([g_d.nbr_off, g_r.nbr_off[1:] + g_d.nbr_off[-1]]),
                           nbr_idx=np.concatenate([g_d.nbr_idx, g_r.nbr_idx + nv]))
    eq = V.equilibrium(grid, s_h, pot, fw[base], np.ones(nh, bool), None if nu0 is None else nu0[:, base], STEPS)
    nu = eq["nu"]
    # each habitat's weight in its pixel: the strip's share, the dry ground the rest
    wgt = np.ones(nh)
    wgt[rsel] = 1 - rip[rsel]
    wgt[nv:] = rip[rsel]

    def mix(a):
        """Per pixel, the habitats' values weighted by their share ((..., nh) -> (..., nv))."""
        a = np.asarray(a, float) * wgt
        out = a[..., :nv].copy()
        np.add.at(out.T, rsel, a[..., nv:].T) if a.ndim > 1 else np.add.at(out, rsel, a[nv:])
        return out

    # --- pulled towards the coarse cells' cover ------------------------------
    if fields["nu0"] is not None and CORR > 0:
        world_nu = np.stack([np.asarray(L[f"veg_{c}"], float)[sel] / 100 for c in V.CODES])
        nu_px = mix(nu)
        mean = np.stack([np.bincount(own, nu_px[p], minlength=len(sel)) for p in range(V.NP)]) / np.maximum(cnt, 1)
        lr = np.where(ok_c[None, :], np.log(np.clip((world_nu + 0.02) / (mean + 0.02), 0.5, 2.0)), 0.0)
        fl, _ = ZK.gauss_interp(px[idx], py[idx], cx, cy, lr.T.copy(), np.repeat(ok_c[:, None], V.NP, 1).astype(float),
                                sig)
        # (the smooth coarse surface the cell means were taken on: e_land in zoom.build)
        e_c = np.maximum(np.asarray(L["elevation"], float)[sel], 1.0)
        es, _ = ZK.gauss_interp(px[idx], py[idx], cx, cy, e_c[:, None], (e_c > 1.0)[:, None].astype(float), sig)
        wz = CORR * np.clip(1 - np.abs(hv - np.nan_to_num(es[:, 0], nan=0.0)) / CORR_DZ, 0, 1)
        tot0 = nu.sum(0)
        nu = np.where(pot["ok"], nu * np.exp(wz[base][None, :] * np.nan_to_num(fl.T)[:, base]), 0.0)
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
    age = np.full(nh, np.inf)
    if burns.any():
        Pk = np.ascontiguousarray(P[idx] * R_KM)
        S = int(seed) * 1_000_003 + 17
        z = ZK.fbm(Pk, FIRE_KM, max(1, int(np.ceil(np.log2(FIRE_KM / (2 * res)))) + 1), 0.55, S + 301) / 0.17
        u = _uniform(z)[base]
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
    sm_h = V.summary(s_h, pot, eq)
    # canopy height from the pixel's own stand age where fire set it
    hfrac = np.sqrt(np.clip(pot["lai"] / V._col("laimax")[:, None], 0, 1))
    hh = V._col("hmax")[:, None] * hfrac * np.where(trees[:, None], 1 - np.exp(-np.minimum(age, sm_h["stand_age"]) / 60.0)[None, :], 1.0)
    sm_h["height"] = np.where(nu > 0.1, hh, 0.0).max(0)
    # the pixel: its habitats mixed by their shares (the canopy: the taller
    # habitat's where it has the most trees in the pixel)
    sm = {k: mix(v) for k, v in sm_h.items() if k not in ("height", "fire_return")}
    burned = mix(eq["burned"])
    sm["fire_return"] = np.where(burned > 1e-4, 1.0 / np.maximum(burned, 1e-9), 0.0)
    t_w = sm_h["tree"] * wgt
    strip_h = np.zeros(nv, bool)
    strip_h[rsel] = t_w[nv:] > t_w[rsel]
    sm["height"] = sm_h["height"][:nv].copy()
    sm["height"][rsel] = np.where(strip_h[rsel], sm_h["height"][nv:], sm_h["height"][rsel])
    nu = mix(nu)
    eq = dict(eq, nu=nu, burned=burned)
    types = V.classify(s, eq, sm, hv, fw=fw)
    # oasis and desert riparian woodland: trees by a river through dry land,
    # where the strip holds a woodland and is a fifth of the pixel or its only trees
    desert = rain_mi < 0.3
    strip_wood = np.zeros(nv, bool)
    strip_wood[rsel] = (sm_h["tree"][nv:] >= 0.1) & ((rip[rsel] > 0.2) | (sm_h["tree"][rsel] < 0.05))
    types = np.where(strip_wood & desert & (sm["tree"] >= 0.1 * np.minimum(rip / 0.2, 1)) & ~np.isin(types, list(WETLAND_TYPES)),
                     V.T["oasis / desert riparian woodland"], types)

    def put(v, dtype=float):
        a = np.zeros(n, dtype)
        a[idx] = v
        return a

    layers = dict(
        vegetation=np.where(veg, put(types, np.uint8), out_type).astype(np.uint8),
        tree_cover=put(100 * sm["tree"]), plant_cover=put(100 * sm["cover"]), lai=put(sm["lai"]),
        canopy_height=put(sm["height"]), npp=put(sm["npp"]),
        fire_return=put(np.minimum(sm["fire_return"], 9999)),
    )
    # --- soils, organic pass (soils.organic): soil carbon, peat and the named types, from the vegetation
    t_s = time.time()
    so = SO.organic(sp_m, dict(eq=dict(nu=nu, burned=burned), sm=dict(npp=sm["npp"]), fw=fw))
    layers.update({k: put(v, np.asarray(v).dtype) for k, v in SO.world_layers(sp_m, so).items()})
    t_soil += time.time() - t_s
    st_ = np.bincount(so["types"], minlength=len(SO.TYPES))
    lt = np.bincount(types, minlength=len(V.TYPES))
    top = np.argsort(-lt)[:10]
    stats = {"vegetation_pct": {V.TYPES[k][1]: round(float(100 * lt[k] / nv), 1) for k in top if lt[k] > 0},
             "tree_cover_mean_pct": round(float(100 * sm["tree"].mean()), 1),
             "npp_mean": round(float(sm["npp"].mean())),
             "wetland_pct": round(100 * float(np.isin(types, list(WETLAND_TYPES)).mean()), 2),
             "riparian_px": int((rip > 0.2).sum()),
             "seconds": round(time.time() - t0, 1),
             # the soils (soils.zoom_mineral, organic): % of the bare land by type, mean depth and carbon
             "soils": {"soil_pct": {SO.TYPES[k][2]: round(float(100 * st_[k] / nv), 1)
                                    for k in np.argsort(-st_)[:10] if st_[k] > 0},
                       "depth_mean_m": round(float(sp_m["depth"].mean()), 2),
                       "carbon_mean_kg_m2": round(float(so["carbon"].mean()), 1),
                       "seconds": round(t_soil, 2)}}
    log(f"  vegetation: {nv} px, trees {stats['tree_cover_mean_pct']}%, soils {t_soil:.2f}s "
        f"[{time.time() - t0:.1f}s]")
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
                (lay.get("wetland", np.zeros((ny, nx))) == 1).ravel(), log=lambda *a: None, want_fractions=True,
                rock=lay["surface_rock"].ravel(), landform=lay["landform"].ravel() if "landform" in lay else None)
    out = {}
    for p, c in enumerate(V.CODES):
        a = np.zeros(nx * ny)
        a[r["idx"]] = r["nu"][p]
        out[c] = a.reshape(ny, nx)
    out["vegetation"] = r["layers"]["vegetation"].reshape(ny, nx)
    return out
