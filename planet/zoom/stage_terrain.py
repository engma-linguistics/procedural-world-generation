"""The first half of the regional zoom build (build()): the pixel grid, the coarse fields on it, the delta plains, the
coastline, the detail noise, the coarse cells' means, the volcanoes, the tides and the landform classes. This is the
target surface the later stages work from.

Each stage takes the build's context (`ctx`, see regional.ZoomCtx), reads what the stages before it left on it,
and leaves its own results on it. A stage's docstring lists the context names it reads and writes. The helpers and
constants shared with the rest of the zoom are regional's (`RG.`).
"""
from __future__ import annotations

import time

import numpy as np

from ..climate import LAPSE
from ..geo import R_KM, arc_km, cell_area_km2
from . import coast as ZC
from . import kernels as ZK
from . import landforms as ZL
from . import volcanoes as ZV
from . import vegetation as ZVG
from .. import coast
from .. import icemass
from . import regional as RG
from ..geo import smoothstep


def frame_and_grid(ctx):
    """The region's pixel grid with its halo (PW-321), the frame on the sphere, the noise seed and the region mask.
    Reads: P, fr, g, halo, lat, lon, n_in, nx, ny, px, py, region, res, res_km, seed, size_km, sp, world, xs, ys.
    Writes: L, P, Pk, S, cell_area, fr, g, halo, n_in, npx, nx, ny, px, py, region, res, size_in, size_km, sp, sunk,
    t0, world, xs, ys."""
    ctx.t0 = time.time()
    ctx.world, ctx.sunk = RG.land_world(ctx.world)
    ctx.g, ctx.L = ctx.world["grid"], ctx.world["layers"]
    ctx.sp = ctx.g.spacing * R_KM  # coarse cell spacing, km
    ctx.cell_area = cell_area_km2(ctx.g.n)
    ctx.n_in = max(16, int(round(ctx.size_km / ctx.res_km)))
    ctx.res = ctx.size_km / ctx.n_in
    # The terrain is built with a halo round the region, cropped off before
    # the climate (PW-321): the landscape goes on past the region's edge, so
    # its drainage isn't cut there. (Without it the edge held at the target
    # surface, streams near it were short, steep catchments that start or end
    # at the edge, and the relief within ~40 km of it was ~2x the inside's.)
    ctx.halo = min(max(RG.WF_EDGE_PX, int(np.ceil(RG.HALO_CELLS * ctx.sp / ctx.res))), ctx.n_in // 4)
    ctx.size_in, ctx.size_km = ctx.size_km, (ctx.n_in + 2 * ctx.halo) * ctx.res
    ctx.nx = ctx.ny = ctx.n_in + 2 * ctx.halo
    ctx.npx = ctx.nx * ctx.ny
    ctx.fr = RG.Frame(ctx.lat, ctx.lon)
    ctx.xs = (np.arange(ctx.nx) + 0.5 - ctx.nx / 2) * ctx.res
    ctx.ys = (ctx.ny / 2 - np.arange(ctx.ny) - 0.5) * ctx.res
    X, Y = np.meshgrid(ctx.xs, ctx.ys)
    ctx.px, ctx.py = X.ravel(), Y.ravel()
    ctx.P = ctx.fr.to_sphere(ctx.px, ctx.py)
    ctx.Pk = np.ascontiguousarray(ctx.P * R_KM)
    ctx.S = int(ctx.seed) * 1_000_003 + 17  # noise seed base
    # the region without its halo: what the stats count (PW-340)
    ctx.region = np.zeros((ctx.ny, ctx.nx), bool)
    ctx.region[ctx.halo:ctx.halo + ctx.n_in, ctx.halo:ctx.halo + ctx.n_in] = True
    ctx.region = ctx.region.ravel()


def coarse_fields(ctx):
    """The coarse cells round the region and their fields (heights, rain, ice, ruggedness, runoff) interpolated onto
    the pixels.
    Reads: L, cx, cy, e_c, elev, fr, g, ind, land_c, log, nx, ny, px, py, r_c, rock, sel, size_km, sp, t0.
    Writes: cov_f, cx, cy, e_c, e_land, e_sea, elev, gc_sl, gw_sl, ice, ind, interior_c, jul_f, land_c, precip, r_c,
    rel, rock, rug, runoff, sel."""
    # --- coarse cells around the region --------------------------------
    ctx.elev = ctx.L["elevation"].astype(float)
    ang = arc_km(ctx.g.centers @ ctx.fr.c)
    ctx.sel = np.flatnonzero(ang < ctx.size_km * 0.7072 + 4 * ctx.sp)
    ctx.cx, ctx.cy = ctx.fr.to_plane(ctx.g.centers[ctx.sel])
    ctx.e_c = ctx.elev[ctx.sel]
    ctx.land_c = ctx.e_c > 0
    # land cells away from the coast (every neighbour land too): their means are kept (stats, PW-268)
    ctx.interior_c = ctx.land_c & (np.bincount(np.repeat(np.arange(ctx.g.n), np.diff(ctx.g.nbr_off)), ctx.elev[ctx.g.nbr_idx] <= 0, ctx.g.n)[ctx.sel] == 0)

    # ruggedness per coarse cell
    nb_e = np.maximum(ctx.elev, 0)
    deg = np.diff(ctx.g.nbr_off)
    src = np.repeat(np.arange(ctx.g.n), deg)
    relief = np.zeros(ctx.g.n)
    np.maximum.at(relief, src, np.abs(nb_e[src] - nb_e[ctx.g.nbr_idx]))
    ctx.rock = ctx.L["rock"].astype(int)
    ctx.r_c = np.array([RG.RUGGED.get(int(k), 0.5) for k in ctx.rock[ctx.sel]])
    cover = ctx.L.get("sediment_cover", np.zeros(ctx.g.n))[ctx.sel]
    ctx.r_c = ctx.r_c * np.where(cover > 0.3, 0.65, 1.0)
    bnd = ctx.L.get("plate_boundary", np.zeros(ctx.g.n))[ctx.sel]
    ctx.r_c = np.where(bnd > 0, np.maximum(ctx.r_c, 0.85), np.where(bnd < 0, np.maximum(ctx.r_c, 0.6), ctx.r_c))
    ctx.r_c = np.maximum(ctx.r_c, np.clip(relief[ctx.sel] / 2500, 0, 1))
    ctx.r_c = np.maximum(ctx.r_c, 0.9 * smoothstep(600, 3500, ctx.e_c))  # high ground is rugged whatever the rock
    ice_c = ctx.L.get("ice", np.zeros(ctx.g.n))[ctx.sel].astype(float)
    ctx.r_c = np.clip(ctx.r_c * np.exp(-ice_c / 500), 0.12, 1.0)

    # (glaciers: the bare ground's summer and winter at sea level, the coarse ice's sheet cover, the rain's
    # share in the July half-year)
    ice_all = ctx.L.get("ice", np.zeros(ctx.g.n)).astype(float)
    gw, gc = (v[ctx.sel] for v in RG.ice_ground(ctx.g, ctx.L, ice_all))
    ice_l = np.where(ctx.elev > 0, ice_all, 0.0)
    cov_c = icemass.sheet_cover(ctx.g, ice_l, air=icemass.sheet_air(ctx.g, ice_l))[ctx.sel]
    if "precipitation_jul" in ctx.L and "precipitation_jan" in ctx.L:
        pj_c, pn_c = (np.asarray(ctx.L[k], float)[ctx.sel] for k in ("precipitation_jul", "precipitation_jan"))
        jul_c = np.where(pj_c + pn_c > 0, pj_c / np.maximum(pj_c + pn_c, 1e-9), 0.5)
    else:
        jul_c = np.full(len(ctx.sel), 0.5)
    vals = np.column_stack([np.maximum(ctx.e_c, 1.0), np.minimum(ctx.e_c, -1.0),
                            ctx.L["precipitation"][ctx.sel].astype(float), ice_c, ctx.r_c, relief[ctx.sel],
                            gw + LAPSE * np.maximum(ctx.e_c, 0), gc + LAPSE * np.maximum(ctx.e_c, 0), cov_c,
                            np.asarray(ctx.L["runoff"] if "runoff" in ctx.L else ctx.L["precipitation"], float)[ctx.sel], jul_c])
    wts = np.ones_like(vals)
    wts[:, 0] = ctx.land_c
    wts[:, 1] = ~ctx.land_c
    wts[:, 2] = np.where(ctx.land_c, 1.0, ZVG.SEA_W)  # (rain: the land's, the sea's only far from any land cell)
    wts[:, 9] = ctx.land_c  # (runoff: the land's; the sea's is 0)
    sig = 0.5 * ctx.sp
    fine, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, vals, wts, sig)
    ctx.e_land = np.nan_to_num(fine[:, 0], nan=1.0)
    ctx.e_sea = np.nan_to_num(fine[:, 1], nan=-50.0)
    ctx.precip, ctx.ice, ctx.rug, ctx.rel = (fine[:, k] for k in range(2, 6))
    ctx.gw_sl, ctx.gc_sl, ctx.cov_f = (np.nan_to_num(fine[:, k], nan=0.0) for k in range(6, 9))
    ctx.jul_f = np.clip(np.nan_to_num(fine[:, 10], nan=0.5), 0, 1)
    # what feeds the streams: the world's runoff (rain minus what the land
    # evaporates, as its own rivers route), not the rain
    ctx.runoff = np.clip(np.nan_to_num(fine[:, 9], nan=0.0), 0, None)
    ctx.ind, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, np.where(ctx.land_c, 1.0, -1.0)[:, None],
                             np.ones((len(ctx.sel), 1)), 0.42 * ctx.sp)
    ctx.ind = ctx.ind[:, 0]
    ctx.log(f"  interpolated {len(ctx.sel)} coarse cells onto {ctx.nx}x{ctx.ny} px [{time.time() - ctx.t0:.1f}s]")


def delta_plains(ctx):
    """Delta plains at the big river mouths: the plain, prodelta and lobe weights and each delta's shape.
    Reads: L, cell_area, cut, deltas, down, e_land, e_sea, elev, flow, fr, g, hf, ind, keep, npx, nx, ny, px, py,
    res, seed, sel, size_km, smooth_c, sp, wC, wD, wR_f, wS, wW_f, zD, zS.
    Writes: cut, deltas, down, flow, hf, keep, lobe, smooth_c, wC, wD, wR_f, wS, wW_f, zD, zS."""
    # --- delta plains at big river mouths --------------------------------
    # Within R of the mouth (R grows with discharge and offshore sediment)
    # the land becomes a flat plain a few metres above the sea (wD, zD), the
    # sea floor shallows (prodelta: wS, zS), and a lobe of new land is pushed
    # out to sea (added to the land/sea indicator). The detail noise and the
    # coarse-mean correction are damped there (wC).
    ctx.flow, ctx.down = ctx.L["flow"].astype(float), ctx.L["downstream"].astype(int)
    ctx.deltas = RG._deltas(ctx.g, ctx.L, ctx.sel, ctx.fr, ctx.sp, ctx.size_km, ctx.elev, ctx.flow, ctx.down, ctx.cell_area)
    ctx.wD, ctx.zD, ctx.wS, ctx.zS, ctx.wC, ctx.lobe, ctx.cut, ctx.smooth_c, ctx.wR_f, ctx.wW_f = (np.zeros(ctx.npx) for _ in range(10))
    ctx.keep = np.full(ctx.npx, -9.0)
    ctx.hf = 1 - smoothstep(*RG.DELTA_PLAIN_GROUND, ctx.e_land)  # a plain only on low coarse ground
    # ... and no prodelta over deep water: a delta builds out over its shelf
    # (a ~300 km plain's prodelta must not fill the trench off it)
    shelf_f = smoothstep(-1000.0, -200.0, ctx.e_sea)
    for j, dl in enumerate(ctx.deltas):
        R = dl["R"]
        r = np.hypot(ctx.px - dl["x"], ctx.py - dl["y"])
        w = smoothstep(R, 0.55 * R, r) * ctx.hf
        ctx.zD = np.where(w > ctx.wD, coast.PLAIN_Z0 + coast.PLAIN_RISE * (r / R) ** 1.5, ctx.zD)
        ctx.wR_f, ctx.wW_f = np.where(w > ctx.wD, dl["wR"], ctx.wR_f), np.where(w > ctx.wD, dl["wW"], ctx.wW_f)
        ctx.wD = np.maximum(ctx.wD, w)
        ctx.zS = np.where(r < 1.2 * R, np.maximum(ctx.zS, -(2.0 + 50.0 * (r / R) ** 2)), ctx.zS)
        ctx.wS = np.maximum(ctx.wS, smoothstep(1.2 * R, 0.5 * R, r) * shelf_f)
        ctx.wC = np.maximum(ctx.wC, smoothstep(1.4 * R, 0.8 * R, r) * np.where(ctx.ind > 0, ctx.hf, shelf_f))
        # its shape from the Galloway weights; the lobe lifts the land/sea
        # indicator at its centre to a little above the coast value
        f = RG._delta_forms(dl, ctx.px, ctx.py, ctx.res, np.random.default_rng(ctx.seed * 7919 + 101 + j), ctx.ind, ctx.nx, ctx.ny)
        lc = np.asarray(dl["lobe_at"])
        k = int(np.argmin((ctx.px - lc[0]) ** 2 + (ctx.py - lc[1]) ** 2))
        amp_l = np.clip(0.35 - ctx.ind[k], 0.0, 2.0) if np.hypot(ctx.px[k] - lc[0], ctx.py[k] - lc[1]) < 2 * ctx.res else 1.0
        ctx.lobe += amp_l * f["lobe"]
        ctx.cut = np.maximum(ctx.cut, f["cut"])
        ctx.smooth_c = np.maximum(ctx.smooth_c, f["smooth"])
        ctx.keep = np.maximum(ctx.keep, f["keep"])
        dl["goals"], dl["form"] = f["goals"], f["kind"]
    ctx.zS = np.where(ctx.wS > 0, ctx.zS, -1e9)


def coastline(ctx):
    """The coastline: a warped land/sea indicator, wave-dominated delta lagoons, coastal-plain barriers and barrier
    islands.
    Reads: L, P, Pc, Pk, S, barrier, base, bi_island, cut, cx, cy, deltas, e_land, e_sea, hf, ind, ind_n, isl, keep,
    land, land_c, lobe, log, npx, nx, ny, px, py, res, sel, smooth_c, sp, wC, w_cp, world.
    Writes: Pc, barrier, base, bi_island, ind_n, isl, land, w_cp."""
    # --- coastline -------------------------------------------------------
    lam = 0.9 * ctx.sp
    cw = ZK.fbm(ctx.Pk, lam, 4, 0.5, ctx.S + 7) / 0.17 * 0.12 * ctx.sp  # domain warp: bays, headlands
    ctx.Pc = np.ascontiguousarray(ctx.Pk + cw[:, None] * np.array([0.57, -0.41, 0.71]))
    coast_n = ZK.fbm(ctx.Pc, lam, RG._octaves(lam, 2 * ctx.res), 0.62, ctx.S + 1) / 0.15
    ctx.ind_n = np.maximum(ctx.ind + 0.22 * coast_n * (1 - ctx.smooth_c) + ctx.lobe, ctx.keep) - ctx.cut
    # Wave-dominated deltas: a barrier of sand along the flanks, with a
    # lagoon behind it (broken by a few tidal inlets), its width growing
    # with the wave weight above ~0.3.
    lagoon = np.zeros(ctx.npx, bool)
    if any(dl["wW"] > 0.3 for dl in ctx.deltas):
        din = ZK.inside_distance(ctx.ind_n > 0, ctx.nx, ctx.ny) * ctx.res  # km inside the coast
        gate = ZK.fbm(ctx.Pk, 40.0, 2, 0.5, ctx.S + 51) / 0.17
        for dl in ctx.deltas:
            if dl["wW"] <= 0.3:
                continue
            R = dl["R"]
            dx, dy = ctx.px - dl["x"], ctx.py - dl["y"]
            r = np.hypot(dx, dy)
            flank = np.abs(dx * dl["u"][0] + dy * dl["u"][1]) < 0.7 * np.maximum(r, 1e-9)
            bw = max(2.0 * ctx.res, 3.0)  # barrier width, km (at least 2 px)
            lw = max(1.0 * ctx.res, (dl["wW"] - 0.3) / 0.7 * 0.08 * R)  # lagoon width
            band = (din > bw + 0.1 * ctx.res) & (din <= bw + lw) & (r > 0.2 * R) & (r < 1.1 * R) & flank & (ctx.hf > 0.5)
            inlet = (din > 0) & (din <= bw + 0.1 * ctx.res) & (r > 0.2 * R) & (r < 1.1 * R) & flank & (gate < -0.75)
            lagoon |= band | inlet
        ctx.ind_n = np.where(lagoon, np.minimum(ctx.ind_n, -0.05), ctx.ind_n)
        ctx.log(f"  lagoons: {int(lagoon.sum())} px")
    # Coastal plains (zoom.landforms, PW-012) on wave-dominated coasts
    # (strong waves, small tides): a barrier island 2 px wide along the
    # coast, a lagoon behind it, tidal inlets through it here and there;
    # not where a delta shapes the coast (it has its own barriers)
    ctx.barrier = np.zeros(ctx.npx, bool)
    ctx.w_cp = np.zeros(ctx.npx)
    if "landform" in ctx.L and "wave_power" in ctx.L and "tide_range" in ctx.L:
        cp_c = (np.asarray(ctx.L["landform"])[ctx.sel] == ZL.LF.COASTAL_PLAIN) & ctx.land_c
        if cp_c.any():
            # (the share of coastal plain among the land cells around: 1 along its coast)
            f_cp, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, cp_c[:, None].astype(float), ctx.land_c[:, None].astype(float),
                                      0.5 * ctx.sp)
            ctx.w_cp = smoothstep(0.3, 0.6, np.nan_to_num(f_cp[:, 0]))
            mv, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, np.column_stack([np.asarray(ctx.L["tide_range"], float)[ctx.sel],
                                                                     np.asarray(ctx.L["wave_power"], float)[ctx.sel]]),
                                    np.column_stack([~ctx.land_c, ~ctx.land_c]).astype(float), 0.6 * ctx.sp)
            wW_b = (ctx.w_cp * smoothstep(*RG.BARRIER_WAVE, np.nan_to_num(mv[:, 1]))
                    * smoothstep(RG.BARRIER_TIDE[1], RG.BARRIER_TIDE[0], np.nan_to_num(mv[:, 0])) * (1 - ctx.wC))
            if np.any(wW_b > 0.3):
                din = ZK.inside_distance(ctx.ind_n > 0, ctx.nx, ctx.ny, False) * ctx.res  # km inside the coast
                gate = ZK.fbm(ctx.Pk, 30.0, 2, 0.5, ctx.S + 53) / 0.17
                bw = max(2.0 * ctx.res, 1.0)  # barrier width, km (at least 2 px)
                vary = np.clip(0.75 + 0.45 * ZK.fbm(ctx.Pk, 50.0, 2, 0.5, ctx.S + 55) / 0.17, 0.25, 1.3)
                lw = np.maximum(1.5 * ctx.res, RG.BARRIER_LAGOON_KM * wW_b * vary)  # lagoon width
                on = wW_b > 0.3
                band = on & (din > bw + 0.1 * ctx.res) & (din <= bw + lw)
                inlet = on & (din > 0) & (din <= bw + 0.1 * ctx.res) & (gate < -0.85)
                ctx.barrier = on & (din > 0) & (din <= bw + 0.1 * ctx.res) & ~inlet
                ctx.ind_n = np.where(band | inlet, np.minimum(ctx.ind_n, -0.05), ctx.ind_n)
                ctx.log(f"  coastal plain: barrier {int(ctx.barrier.sum())} px, lagoons {int((band | inlet).sum())} px")
    # Barrier islands off the world's barrier coasts (zoom.coast.islands, PW-622), here so the rivers, the satellite
    # view, the coastal life and the harbours all see them: a strip of low sand, the shallow lagoon behind it
    ctx.isl = ZC.islands(ctx.world, ctx.Pk, ctx.P, ctx.ind_n, ctx.e_land, ctx.e_sea, lagoon | ctx.barrier | (ctx.ind_n == -0.05), ctx.sel, ctx.nx, ctx.ny, ctx.res, ctx.S)
    ctx.bi_island = ctx.isl["island"]
    ctx.ind_n = np.where(ctx.bi_island, np.maximum(ctx.ind_n, 0.4), np.where(ctx.isl["lagoon"], np.maximum(ctx.ind_n, -0.12), ctx.ind_n))
    if ctx.bi_island.any():
        ctx.log(f"  barrier islands: {int(ctx.bi_island.sum())} px, lagoons {int(ctx.isl['lagoon'].sum())} px, inlets {int(ctx.isl['inlet'].sum())} px")
    ctx.land = ctx.ind_n > 0
    ramp_l = smoothstep(0.0, 0.55, ctx.ind_n)
    ramp_s = smoothstep(0.0, 0.45, -ctx.ind_n)
    ctx.base = np.where(ctx.land, ctx.e_land * ramp_l, ctx.e_sea * ramp_s)
    if ctx.bi_island.any():
        ctx.base = np.where(ctx.bi_island, ZC.ISLAND_M * (0.5 + 0.5 * ctx.isl["u"]), ctx.base)


def detail(ctx):
    """The base surface from the coast indicator, plus the fractal detail (ruggedness-weighted), and the soft coast
    clamp.
    Reads: P, Pk, S, amp_land, base, bi_island, clamp, detail, elev, g, h, ind_n, isl, land, own, rel, res, rug,
    s_land, s_sea, sea_floor, sp, taper, wD, wS.
    Writes: amp_land, clamp, detail, h, own, s_land, s_sea, sea_floor, taper."""
    # --- detail ----------------------------------------------------------
    lam_f = 0.8 * ctx.sp
    # Noise supplies ranges and massifs down to ~6 px; the valleys inside
    # them are left to the landscape pass (noise can't make drainage).
    fine_l = max(6 * ctx.res, 8.0)
    f1 = ZK.fbm(ctx.Pk, lam_f, RG._octaves(lam_f, fine_l), 0.55, ctx.S + 2) / 0.17
    lam_r = 0.4 * ctx.sp
    rr = ZK.ridged(ctx.Pk, lam_r, RG._octaves(lam_r, fine_l), 0.55, ctx.S + 3)
    rr = (rr - 0.55) / 0.175
    tex = ZK.fbm(ctx.Pk, fine_l, RG._octaves(fine_l, 2 * ctx.res), 0.6, ctx.S + 4) / 0.17
    w_r = np.clip(ctx.rug, 0, 1) ** 2
    ctx.detail = (1 - w_r) * f1 + w_r * (0.4 * f1 + 0.9 * rr)
    ctx.detail = 2.2 * np.tanh(ctx.detail / 2.2) + 0.06 * tex  # no absurd spikes
    ctx.amp_land = (ctx.rug * (0.36 * np.maximum(ctx.base, 0) + 0.3 * np.nan_to_num(ctx.rel) + 25) + 12) * (1 - 0.9 * ctx.wD)
    amp_sea = (5 + 0.08 * np.abs(ctx.base)) * (1 - 0.7 * ctx.wS)
    ctx.taper = np.where(ctx.land, smoothstep(0.0, 0.35, ctx.ind_n), smoothstep(0.0, 0.25, -ctx.ind_n)) * ~ctx.bi_island
    ctx.h = ctx.base + ctx.taper * np.where(ctx.land, ctx.amp_land, amp_sea) * ctx.detail

    # soft floor/ceiling at the coast (the delta plain and prodelta get a much harder one)
    ctx.s_land, ctx.s_sea = 15.0 * (1 - 0.95 * ctx.wD), 15.0 * (1 - 0.9 * ctx.wS)
    ctx.s_land, ctx.s_sea = np.where(ctx.bi_island, 0.4, ctx.s_land), np.where(ctx.isl["lagoon"], 0.5, ctx.s_sea)  # (low sand, shallow lagoon)

    # ... and no sea floor deeper than the deepest coarse cell around it, by more than the sea
    # floor's own detail can reach (PW-844): the mean correction below can't reach a sea cell's
    # mean when the fine coast leaves only a few of its pixels sea (an isolated deep cell among
    # high ground), and drove those few to -23 km (an interpolant has no business leaving the
    # range of its data; the margin is the detail's own reach, amp_sea's at that depth x 2.2)
    ctx.own = ctx.g.locate(ctx.P)
    e_nb = np.minimum(ctx.elev, np.minimum.reduceat(ctx.elev[ctx.g.nbr_idx], ctx.g.nbr_off[:-1]))[ctx.own]
    ctx.sea_floor = np.minimum(e_nb - 2.2 * (5 + 0.08 * np.abs(e_nb)), -0.5)

    def clamp(hh):
        return np.where(ctx.land, 0.5 + RG.softplus(hh - 0.5, ctx.s_land),
                        np.maximum(-0.5 - RG.softplus(-0.5 - hh, ctx.s_sea), ctx.sea_floor))
    ctx.clamp = clamp

    ctx.h = ctx.clamp(ctx.h)


def mean_correction(ctx):
    """Each coarse cell keeps its mean: the sea-share and mean-correction passes, and the delta plains' own heights.
    Reads: amp_land, cell_area, cell_means, clamp, cx, cy, deltas, detail, e_c, full_px, g, h, ind, ind_n,
    interior_c, land, land_c, own, own_s, px, py, res, sel, sp, taper, wC, wD, wS, zD, zS.
    Writes: cell_means, full_px, h, own_s."""
    # --- keep each coarse cell's mean ----------------------------------
    lut = np.full(ctx.g.n, -1)
    lut[ctx.sel] = np.arange(len(ctx.sel))
    ctx.own_s = lut[ctx.own]
    ctx.full_px = ctx.cell_area / ctx.res**2

    def cell_means(hh):
        cnt = np.bincount(ctx.own_s, minlength=len(ctx.sel))
        tot = np.bincount(ctx.own_s, hh, minlength=len(ctx.sel))
        return tot / np.maximum(cnt, 1), cnt
    ctx.cell_means = cell_means

    # A land cell whose fine coast leaves part of it sea keeps first what its mean lacks in that sea
    # (PW-362): the sea floor round its island rises, as a shelf, towards the shore. Its sea pixels
    # had the depth of the sea cells beyond it, a forearc's trench, and the mean correction below
    # lifted its land as much as its sea, a mesa of 1,300-1,600 m on a +194 m cell. (Weighted by how
    # much land the cells round a sea pixel are, ind, so it fades out into the sea cells, which the
    # correction below then sets back to their own means; the sea stays sea: clamp.)
    f_s = np.where(ctx.land, 0.0, np.clip(0.5 * (ctx.ind + 1.0), 0.0, 1.0)) * (1 - ctx.wC)
    fsum = np.bincount(ctx.own_s, f_s, minlength=len(ctx.sel))
    for _ in range(RG.SEA_SHARE_PASSES):
        m, cnt = ctx.cell_means(ctx.h)
        ok_l = ctx.land_c & (cnt > 0.25 * ctx.full_px)
        amp = np.where(ok_l & (fsum > 0.05 * cnt), np.maximum(ctx.e_c - m, 0.0) * cnt / np.maximum(fsum, 1e-9), 0.0)
        corr, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, amp[:, None], ok_l[:, None].astype(float), 0.5 * ctx.sp)
        ctx.h = ctx.clamp(ctx.h + f_s * np.nan_to_num(corr[:, 0]))
    corr_taper = np.where(ctx.land, smoothstep(0.0, 0.3, ctx.ind_n), smoothstep(0.0, 0.3, -ctx.ind_n)) * (1 - ctx.wC)
    # (each pass removes only part of a residual one cell wide, e.g. a trench,
    # because the correction is smooth over half a cell: MEAN_PASSES of them)
    # (a sea cell the fine coast leaves mostly land isn't held to its mean: its few sea pixels
    # would have to carry the whole cell's depth, PW-844; the mirror of PW-362's land cells)
    sea_px = np.bincount(ctx.own_s, ~ctx.land, minlength=len(ctx.sel))
    mostly_land_sea = ~ctx.land_c & (sea_px < 0.5 * np.bincount(ctx.own_s, minlength=len(ctx.sel)))
    for _ in range(RG.MEAN_PASSES):
        m, cnt = ctx.cell_means(ctx.h)
        ok = (cnt > 0.25 * ctx.full_px) & ~mostly_land_sea
        resid = np.where(ok, ctx.e_c - m, 0.0)
        corr, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, resid[:, None], ok[:, None].astype(float), 0.5 * ctx.sp)
        ctx.h = ctx.clamp(ctx.h + corr_taper * np.nan_to_num(corr[:, 0]))
    if ctx.deltas:  # the plain keeps a little of the (damped) detail
        det = ctx.taper * ctx.amp_land * ctx.detail
        ctx.h = np.where(ctx.land, (1 - ctx.wD) * ctx.h + ctx.wD * (ctx.zD + det), (1 - ctx.wS) * ctx.h + ctx.wS * np.maximum(ctx.h, ctx.zS))
        ctx.h = ctx.clamp(ctx.h)
        # what the plain took off an inland cell's mean goes back on its land
        # beyond the plain (PW-349; a coastal cell's mean is left to the
        # delta, whose lobe and channels move its coast; the correction fades
        # out towards the coast, so it needs no clamp: clamp() isn't idempotent)
        f_r = np.where(ctx.land, smoothstep(0.0, 0.3, ctx.ind_n), 0.0) * (1 - ctx.wD)
        for _ in range(RG.MEAN_PASSES):
            m, cnt = ctx.cell_means(ctx.h)
            ok = cnt > 0.25 * ctx.full_px
            resid = np.where(ok & ctx.interior_c, ctx.e_c - m, 0.0)
            if not resid.any():
                break
            corr, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, resid[:, None], ok[:, None].astype(float), 0.5 * ctx.sp)
            ctx.h = ctx.h + f_r * np.nan_to_num(corr[:, 0])
        ctx.h = np.where(ctx.land, np.maximum(ctx.h, 0.5), ctx.h)


def volcanoes(ctx):
    """The volcanoes' cones, their lowered sea floor and the minor cones' volume (zoom volcanoes).
    Reads: L, Pk, base, cell_means, cx, cy, cz, fr, full_px, g, h, land, log, npx, px, py, rel, res, rock, seed,
    sel, size_km, sp, vf, world, wv.
    Writes: cz, h, land, minor_add, rel, vf, vtarget, wv."""
    # --- volcanoes (zoom.volcanoes): each one its own cone -----------------
    ctx.vf = ZV.fields(ctx.world, ctx.fr, ctx.px, ctx.py, ctx.res, ctx.sp, ctx.Pk, ctx.seed, ctx.size_km)
    ctx.vtarget = np.full(ctx.npx, np.nan)  # the volcanoes' surface, for the landscape pass
    ctx.minor_add = np.zeros(ctx.npx)  # what the minor arc cones stand above the ground (m)
    if ctx.vf is not None:
        # (not over a continent; a pile of hotspot lava capped with reef
        # limestone counts as continental crust in the run, so it stays in)
        ok_c = (np.asarray(ctx.L.get("crust", np.zeros(ctx.g.n)))[ctx.sel] == 0) | (ctx.rock[ctx.sel] == 1)
        oceanic, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, ok_c[:, None].astype(float), np.ones((len(ctx.sel), 1)), 0.35 * ctx.sp)
        oceanic = smoothstep(0.3, 0.7, np.nan_to_num(oceanic[:, 0]))
        ctx.wv = ctx.vf["province"] * oceanic * np.isfinite(ctx.vf["floor"])
        # the vents' sea floor: the terrain lowered by the coarse cells'
        # share of the cones themselves (what they stand above the ground
        # under them, averaged over each cell and interpolated as the coarse
        # heights are), at most down to their floor, keeping its texture.
        # Where the coarse ground stands higher than the floor plus that
        # share (a plateau the vents built together, PW-310: an ice-capped
        # hotspot ridge at 2-3 km over vents recorded on a -4 km floor), the
        # rest is ground the cones stand on, not sea between them. (A cone
        # keeps the run's summit height, so on such a plateau it stands less
        # high above the ground, or is buried in it: its share is refitted
        # to what stands above the lowered ground, a few times.)
        above = np.maximum(ctx.base - np.nan_to_num(ctx.vf["floor"], nan=-1e4), 0.0)
        ok_m = None
        lower = np.zeros(ctx.npx)
        for _ in range(4):
            g_s = ctx.base - ctx.wv * lower  # (the ground under the cones, without its texture)
            ctx.rel = ctx.vf["z"] - ctx.vf["z_floor"] - ctx.vf["z_abs"] * np.maximum(g_s - ctx.vf["z_floor"], 0.0)
            m_cone, cnt = ctx.cell_means(np.where(np.isfinite(ctx.vf["z"]), np.maximum(ctx.rel, 0.0), 0.0))
            ok_m = (cnt > 0.25 * ctx.full_px)[:, None].astype(float) if ok_m is None else ok_m
            share, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, m_cone[:, None], ok_m, 0.5 * ctx.sp)
            lower = np.minimum(above, np.nan_to_num(share[:, 0], nan=np.inf))
        ground = np.where(ctx.wv > 0, ctx.h - ctx.wv * lower, ctx.h)
        # the cones on it (absolute near their summits, on the ground at their edges)
        ctx.cz = ctx.vf["z"] + (1 - ctx.vf["z_abs"]) * (ground - ctx.vf["z_floor"])
        # (a continental vent's lava plain lies flat on the smooth coarse
        # ground, filling the hollows; hills stand through it, PW-118)
        cb = ctx.vf["bump"] + (1 - ctx.vf["bump_abs"]) * (np.where(ctx.vf["bump_flat"], ctx.base, ctx.h) - ctx.vf["bump_floor"])
        hv = np.maximum(ground, ctx.cz)
        ctx.h = np.maximum(hv, cb)
        # (a minor arc cone has no volume of its own in the coarse cells: what it
        # stands above the ground comes off its cells' other land, below, PW-116)
        ctx.minor_add = np.where(ctx.vf["bump_minor"] & np.isfinite(ctx.vf["bump"]), np.maximum(cb - hv, 0.0), 0.0)
        ctx.land = np.where(ctx.wv > 0.5, ctx.h > 0, ctx.land | (ctx.h > 0.5))
        ctx.h = np.where(ctx.land, np.maximum(ctx.h, 0.5), np.minimum(ctx.h, -0.5))
        on_v = (ctx.wv > 0.5) & np.isfinite(ctx.vf["z"]) | np.isfinite(ctx.vf["bump"])
        ctx.vtarget = np.where(on_v, ctx.h, np.nan)
        ctx.log(f"  {len(ctx.vf['list'])} volcanoes: " + ", ".join(
            f"{n} {k}" for k, n in sorted(RG._count(v["form"] for v in ctx.vf["list"]).items(), key=lambda kv: -kv[1])))


def tides_and_flats(ctx):
    """Waves and tides on the fine grid, barrier dune ridges, the deltas' tidal flats, channels and beach ridges.
    Reads: L, Pk, S, barrier, cut, cx, cy, delta_floor, deltas, h, land, land_c, log, npx, nx, ny, px, py, res,
    s_sea, sel, sp, t0, wD, wW_f, zD.
    Writes: delta_floor, h, s_sea, tide_f, wave_f."""
    # waves and tides on the fine grid (from the sea cells): the deltas' tidal
    # flats, and layers of the zoom
    ctx.tide_f, ctx.wave_f = np.zeros(ctx.npx), np.zeros(ctx.npx)
    if "tide_range" in ctx.L and "wave_power" in ctx.L:
        mv, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, np.column_stack([np.asarray(ctx.L["tide_range"], float)[ctx.sel],
                                                                 np.asarray(ctx.L["wave_power"], float)[ctx.sel]]),
                                np.column_stack([~ctx.land_c, ~ctx.land_c]).astype(float), 0.6 * ctx.sp)
        ctx.tide_f, ctx.wave_f = np.nan_to_num(mv[:, 0]), np.nan_to_num(mv[:, 1])
    ctx.delta_floor = np.full(ctx.npx, -np.inf)  # beach ridges and levees, held as floors in the landscape pass
    if ctx.barrier.any():  # (a coastal plain's barrier islands: a dune ridge a few metres high)
        ctx.delta_floor = np.where(ctx.barrier & ctx.land, 2.0 + 2.5 * smoothstep(-1.0, 1.0, ZK.fbm(ctx.Pk, 6.0, 2, 0.5, ctx.S + 54) / 0.17),
                               ctx.delta_floor)
    if ctx.deltas:
        # Tidal flats: offshore of a tide-influenced delta, a band of sea floor
        # between low and mean tide (exposed at low water), wider with the
        # tide weight. Beach ridges: on a wave-influenced delta plain, old
        # shorelines a few metres high parallel to the coast (spacing
        # exaggerated to a few pixels), broken here and there.
        dsea = ZK.inside_distance(~ctx.land, ctx.nx, ctx.ny, False) * ctx.res
        din = ZK.inside_distance(ctx.land, ctx.nx, ctx.ny, False) * ctx.res
        gate = ZK.fbm(ctx.Pk, 30.0, 2, 0.5, ctx.S + 52) / 0.17
        lam_r = max(3.0 * ctx.res, 3.0)
        for dl in ctx.deltas:
            r = np.hypot(ctx.px - dl["x"], ctx.py - dl["y"])
            Wf = 0.15 * dl["wT"] * dl["R"]
            if Wf > ctx.res:
                flat = ~ctx.land & (dsea < Wf) & (r < 1.2 * dl["R"])
                ctx.h = np.where(flat, np.maximum(ctx.h, -0.5 * max(dl["tide"], 0.5) * dsea / Wf - 0.05), ctx.h)
                # (held by the hard floor of a prodelta, also where the delta faces deep water)
                ctx.s_sea = np.where(flat, 1.5, ctx.s_sea)
                # the funnels and creeks themselves are scoured deep by the tidal
                # currents (flats only along their banks)
                chan = ~ctx.land & (ctx.cut > 0.4) & (r < 1.1 * dl["R"])
                ctx.h = np.where(chan, np.minimum(ctx.h, -(1.5 + 0.8 * dl["tide"]) * np.minimum(ctx.cut, 1.3)), ctx.h)
        ridge = 2.5 * ctx.wW_f * np.cos(np.pi * din / lam_r) ** 2 * (gate > -0.3)
        on = ctx.land & (ctx.wD > 0.5) & (ctx.wW_f > 0.25) & (din > 0.5 * ctx.res) & (ridge > 0.3)
        ctx.delta_floor = np.where(on, ctx.zD + ridge, ctx.delta_floor)
    ctx.log(f"  coast + detail + mean correction [{time.time() - ctx.t0:.1f}s]")


def landform_classes(ctx):
    """The landform classes' weights and hooks (plateaus, scarps), applied to the surface with each cell's mean kept.
    Reads: L, Pk, S, base, clamp, cx, cy, fr, full_px, g, h, keep_means, land, land_c, lf, log, minor_add, nx, ny,
    own_s, px, py, region, res, sel, sp, vtarget.
    Writes: ground_up, h, keep_means, lf, lf_gorges, scarp."""
    # --- landform classes (zoom.landforms): weights, parameters, hooks ----
    ctx.lf = ZL.Landforms.build(ctx.L, ctx.sel, ctx.cx, ctx.cy, ctx.land_c, ctx.px, ctx.py, ctx.Pk, ctx.sp, ctx.res, ctx.nx, ctx.ny, ctx.S, ctx.land, ctx.base,
                            lambda v, w, s: ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, v, w, s), ctx.g, ctx.fr.to_plane)
    if ctx.lf is not None:
        ctx.lf.set_region(ctx.region)

    def keep_means(z, hh, where, f=None):
        """z with each coarse cell's mean change from hh undone (a smooth
        correction, like the detail's), on `where`, in proportion to f (0..1:
        the land the change came from; the rest keeps its height)."""
        f = np.where(where, 1.0 if f is None else f, 0.0)
        for _ in range(2):
            dsum = np.bincount(ctx.own_s, np.where(where, z - hh, 0.0), minlength=len(ctx.sel))
            fsum = np.bincount(ctx.own_s, f, minlength=len(ctx.sel))
            cnt = np.bincount(ctx.own_s, minlength=len(ctx.sel))
            ok = (cnt > 0.25 * ctx.full_px) & (fsum > 0.05 * cnt)
            amp = np.where(ok, -dsum / np.maximum(fsum, np.maximum(0.3 * cnt, 1e-9)), 0.0)  # (a cell barely touched: bounded)
            corr, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, amp[:, None], ok[:, None].astype(float), 0.5 * ctx.sp)
            z = z + f * np.nan_to_num(corr[:, 0])
        return z
    ctx.keep_means = keep_means

    if ctx.minor_add.any():  # (the minor arc cones' volume off their cells' other land: see the volcanoes above)
        ctx.h = ctx.clamp(ctx.keep_means(ctx.h, ctx.h - ctx.minor_add, ctx.land, (~np.isfinite(ctx.vtarget)).astype(float)))
    ctx.lf_gorges = []  # falls over the landform classes' cliffs retreated into gorges: (head pixel, km)
    ctx.ground_up = None  # where the classes' top beds hold the ground: (weight, level) per pixel (designed falls' fit)
    ctx.scarp = None  # single scarps (escarpments): weight, level, height per pixel
    if ctx.lf is not None:
        dz = ctx.lf.target(ctx.h)
        if dz is not None:
            ctx.h = ctx.clamp(ctx.keep_means(ctx.h + dz, ctx.h, ctx.land))
        ctx.ground_up = ctx.lf.plateau(ctx.h)
        ctx.scarp = ctx.lf.scarps(ctx.h)
        ctx.log("  landforms: " + ", ".join(f"{k} {v}%" for k, v in ctx.lf.stats().items()))
