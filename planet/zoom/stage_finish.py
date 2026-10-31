"""The end of the regional zoom build: the halo cropped off, then the climate, vegetation, coastal life, the bed below
grounded ice and the statistics, assembled into the zoom's dict.

Each stage takes the build's context (`ctx`, see regional.ZoomCtx), reads what the stages before it left on it,
and leaves its own results on it. A stage's docstring lists the context names it reads and writes. The helpers and
constants shared with the rest of the zoom are regional's (`RG.`).
"""
from __future__ import annotations

import time

import numpy as np

from .. import gameattrs as GA
from .. import humanuse as HU
from ..climate import LAPSE
from .. import satellite as SAT
from . import coastal as ZCL
from . import kernels as ZK
from . import landforms as ZL
from . import peoples as ZP
from . import vegetation as ZVG
from .. import climate
from .. import coast
from .. import icemass
from ..constants import SEC_PER_YR
from ..geo import latlon
from .. import vegetation
from . import regional as RG


def crop_halo(ctx):
    """Crops the halo off every per-pixel array (the region is all that is kept from here on).
    Reads: P, Pk, all_falls, area, barrier, bi_layer, clim_f, cov_f, deltas, discharge, fjord, form_f, glac_form,
    glac_loess, glacier, h, halo, ice_th, inside, isl, jul_f, kps, lake, lake_depth, lake_in, lake_info, lake_kind,
    lakes, land, lf, lf_lake, lf_sink, n_in, npx, nx, ny, outs, ov_src, own, own_s, pin_src, plunge, precip, px, py,
    rapids_lift, rec, region, res, riv_ids, rock_f, sea, size_in, splits, stages, surf_f, tide_f, top_falls, vf,
    w_cp, wave_f.
    Writes: P, Pk, area, barrier, bi_layer, clim_f, cov_f, discharge, form_f, glac_form, glac_loess, glac_stats,
    glacier, h, ice_th, inside, jul_f, lake, lake_depth, lake_kind, lakes_out, land, lf_lake, n_splits, npx, nx, ny,
    ov_src, own, own_s, pin_src, plunge, precip, px, py, rapids_lift, rec_out, riv_cells, rock_f, sea, size_km,
    stages, surf_f, tide_f, vf, w_cp, wave_f."""
    # --- crop the halo off -------------------------------------------------
    # (what is counted on the drainage network is counted before: the deltas' mouths)
    for d in ctx.deltas:
        d["mouths"] = RG._count_mouths(d, ctx.px, ctx.py, ctx.land, ctx.rec, ctx.discharge, ctx.nx, ctx.ny, ctx.splits)
    ctx.n_splits = int(sum(ctx.region[s_] for s_, _, _ in ctx.splits))
    ctx.riv_cells = set(ctx.riv_ids.tolist())
    keep_px = (np.arange(ctx.halo, ctx.halo + ctx.n_in)[:, None] * ctx.nx + np.arange(ctx.halo, ctx.halo + ctx.n_in)[None, :]).ravel()
    new_px = np.full(ctx.npx, -1, np.int64)
    new_px[keep_px] = np.arange(len(keep_px))

    def crop(a):
        return a[keep_px] if isinstance(a, np.ndarray) and a.shape[:1] == (ctx.npx,) else a

    def crop_idx(a):
        """Pixel indices on the cropped grid (-1: in the halo, or none)."""
        a = np.asarray(a, np.int64)
        return np.where(a >= 0, new_px[np.maximum(a, 0)], -1)

    def shift(rc):
        return [int(rc[0]) - ctx.halo, int(rc[1]) - ctx.halo]

    def inside(rc):
        return 0 <= rc[0] < ctx.n_in and 0 <= rc[1] < ctx.n_in
    ctx.inside = inside

    for f in ctx.all_falls + ctx.top_falls:
        f["px"] = shift(f["px"])
        if "cascades" in f:
            f["cascades"] = [{**c, "px": shift(c["px"])} for c in f["cascades"] if ctx.inside(shift(c["px"]))]
    for kp in ctx.kps:
        if "course_px" in kp:
            ci = crop_idx(kp["course_px"])
            kp["course_px"], kp["course_s"] = ci[ci >= 0], kp["course_s"][ci >= 0]
        for st in kp["steps"]:
            if "lip_px" in st:
                st["lip_px"] = shift(st["lip_px"])
    for d in ctx.lake_info:
        d["outlet"] = shift(d["outlet"]) if d["outlet"] is not None and ctx.inside(shift(d["outlet"])) else None
    ctx.lakes_out = [{"open": lk["exit"] is not None, "outlet": int(crop_idx([ctx.outs[j]])[0]),
                  "n_px": int((new_px[lk["px"]] >= 0).sum()), "level": lk["level"], "grad": lk["grad"],
                  "inflow_m3s": float(ctx.lake_in[j] * RG.KM2_M_PER_YR_TO_M3S)}
                 for j, lk in enumerate(ctx.lakes) if (new_px[lk["px"]] >= 0).any()]
    ctx.rec_out = np.where(ctx.rec[keep_px] >= 0, crop_idx(ctx.rec[keep_px]), -1)
    ctx.pin_src, ctx.ov_src = (a[a >= 0] for a in (crop_idx(ctx.pin_src), crop_idx(ctx.ov_src)))
    ctx.stages = {k: crop(v) for k, v in ctx.stages.items()}
    # each lake's kind (hydrology's lake_kind: 1 open / fresh, 2 closed / salt, 3 a closed basin's dry salt pan):
    # a coarse lake with no exit is closed; a landform basin's closed lake is salt, its playa a pan
    ctx.lake_kind = np.zeros(ctx.npx, np.uint8)
    for lk in ctx.lakes:
        ctx.lake_kind[lk["px"]] = 2 if lk["closed"] else 1  # (a closed lake's fragments too)
    ctx.lake_kind[ctx.lf_lake] = np.where(ctx.lf_sink[ctx.lf_lake], 2, 1)
    ctx.lake_kind[ctx.lf_sink & ~ctx.lf_lake & ~ctx.lake] = 3
    ctx.glac_form, ctx.glac_loess, ctx.glac_stats = ZL.glacial_layers(ctx.lf, ctx.h, ctx.fjord, ctx.lf_lake, ctx.region, ctx.nx, ctx.ny, ctx.res)
    ctx.bi_layer = np.where(ctx.isl["island"], 1, np.where(ctx.isl["lagoon"], 2, np.where(ctx.isl["inlet"], 3, 0))).astype(np.uint8)
    (ctx.h, ctx.lake, ctx.lf_lake, ctx.sea, ctx.land, ctx.plunge, ctx.glacier, ctx.ice_th, ctx.cov_f, ctx.precip, ctx.jul_f, ctx.P, ctx.Pk, ctx.px, ctx.py, ctx.clim_f, ctx.w_cp,
     ctx.lake_depth, ctx.discharge, ctx.area, ctx.rock_f, ctx.surf_f, ctx.form_f, ctx.tide_f, ctx.wave_f, ctx.own, ctx.own_s, ctx.barrier, ctx.rapids_lift,
     ctx.lake_kind, ctx.glac_form, ctx.glac_loess, ctx.bi_layer) = (
        crop(a) for a in (ctx.h, ctx.lake, ctx.lf_lake, ctx.sea, ctx.land, ctx.plunge, ctx.glacier, ctx.ice_th, ctx.cov_f, ctx.precip, ctx.jul_f, ctx.P, ctx.Pk, ctx.px, ctx.py,
                          ctx.clim_f, ctx.w_cp, ctx.lake_depth, ctx.discharge, ctx.area, ctx.rock_f, ctx.surf_f, ctx.form_f, ctx.tide_f, ctx.wave_f, ctx.own,
                          ctx.own_s, ctx.barrier, ctx.rapids_lift, ctx.lake_kind, ctx.glac_form, ctx.glac_loess, ctx.bi_layer))
    if ctx.vf is not None:
        ctx.vf["list"] = [v for v in ctx.vf["list"] if max(abs(v["x_km"]), abs(v["y_km"])) < ctx.size_in / 2]
        ctx.vf = {k: crop(v) for k, v in ctx.vf.items()}
    ctx.nx = ctx.ny = ctx.n_in
    ctx.npx = ctx.nx * ctx.ny
    ctx.size_km = ctx.size_in


def climate_on_terrain(ctx):
    """Climate on the fine terrain: lapse-corrected temperature, rain and Koeppen class, the biome.
    Reads: P, biome, clim_f, cov_f, d_sea, fields, fr, glacier, h, ice_th, jul_f, lake, land, lf_lake, nx, ny,
    plunge, precip, px, py, res, sea, size_km, t_cold, t_warm, temp, w_cp, water, world.
    Writes: biome, clim_f, d_sea, fields, marsh, north, pix_lat, t_cold, t_warm, temp, water."""
    # --- climate on the fine terrain -------------------------------------
    # The bare ground's climate (zoom.vegetation.fine_fields: under the
    # coarse ice too), lapse-corrected to the pixel; on the zoom's own
    # glaciers the ice's surface (climate.ice_surface: its thickness and the
    # mass balance's own year, under the coarse ice's sheet cover) (PW-160, PW-277)
    ctx.fields = ZVG.fine_fields(ctx.world, ctx.fr, ctx.px, ctx.py, ctx.size_km)
    hl = np.maximum(ctx.h, 0)
    ctx.temp = ctx.fields["t_sl"] - LAPSE * hl
    ctx.t_warm = ctx.fields["warm_sl"] - LAPSE * hl
    ctx.t_cold = ctx.fields["cold_sl"] - LAPSE * hl
    if ctx.glacier.any():
        ice_px = np.where(ctx.glacier, np.maximum(ctx.ice_th, 1.0), 0.0)
        ctx.t_warm, ctx.t_cold, ctx.temp = climate.ice_surface(ctx.t_warm, ctx.t_cold, ctx.temp, ice_px, np.maximum(ctx.cov_f, icemass.LOCAL),
                                                   latlon(ctx.P)[0], 2 * ctx.precip * ctx.jul_f, 2 * ctx.precip * (1 - ctx.jul_f))
    ctx.pix_lat = latlon(ctx.P)[0]
    ctx.north = ctx.fields["jul_warm"]  # (July is the warmer month: fine_fields, PW-374)
    ctx.clim_f = np.where(ctx.sea, RG.SEA_CLIMATE, ctx.clim_f)
    # land the coarse map has as sea (a volcanic island in a sea cell): a
    # climate from its own temperature and rain
    lone = ctx.land & (ctx.clim_f == RG.SEA_CLIMATE)
    if lone.any():
        k = np.where(ctx.t_cold >= 18, np.where(ctx.precip >= 1800, 0, np.where(ctx.precip >= 1000, 1, 2)),  # Af Am Aw
                     np.where(ctx.t_cold > 0, np.where(ctx.t_warm >= 22, 13, 14), np.where(ctx.t_warm >= 10, 26, 28)))  # Cfa Cfb Dfc ET
        ctx.clim_f = np.where(lone, np.where((ctx.precip < 350) & (ctx.t_cold > 0), 3, k), ctx.clim_f).astype(np.uint8)  # BWh
    alpine = ctx.land & (ctx.clim_f < 28) & (ctx.t_warm < 10)
    ctx.clim_f = np.where(alpine, 28, ctx.clim_f)
    ctx.clim_f = np.where(ctx.land & ((ctx.t_warm < 0) | ctx.glacier), 29, ctx.clim_f).astype(np.uint8)
    ctx.biome = climate.biomes(ctx.h, ctx.temp, ctx.precip, ctx.lake | ctx.lf_lake, land=ctx.h > 0)
    # (the ice sheet biome is the glaciers: cold ground without ice is bare rock up high, else tundra or cold desert)
    bare = (ctx.biome == 4) & ~ctx.glacier
    ctx.biome = np.where(bare, np.where(ctx.h > 1500, 15, np.where(ctx.precip < 250, 7, 5)), ctx.biome)
    ctx.biome = np.where(ctx.glacier, 4, ctx.biome).astype(np.uint8)
    ctx.water = np.where(ctx.sea, 1, np.where(ctx.lake | ctx.plunge | ctx.lf_lake, 2, 0)).astype(np.uint8)
    # marshes: a coastal plain's lowest ground near the sea and its lagoons, where it is wet enough
    ctx.d_sea = ZK.inside_distance(ctx.land, ctx.nx, ctx.ny, False) * ctx.res
    ctx.marsh = (ctx.water == 0) & (ctx.w_cp > 0.5) & (ctx.h < RG.MARSH_M) & (ctx.d_sea <= RG.MARSH_KM) & (ctx.precip > 300.0) & ~ctx.glacier


def vegetation_layers(ctx):
    """Vegetation and the terrain indices (zoom.vegetation).
    Reads: area, discharge, fields, form_f, fr, glac_loess, glac_stats, glacier, h, ice_th, lake_depth, log, marsh,
    nx, ny, res, seed, size_km, surf_f, vz, water, world.
    Writes: tr, veg_l, vz."""
    # --- vegetation (zoom.vegetation, PW-214) and the terrain indices (PW-196)
    # (on the layers as stored, float32, so zoom.vegetation.fractions can redo it)
    ice_l = np.where(ctx.glacier, np.maximum(ctx.ice_th, 1.0), 0).astype(np.float32)
    ctx.vz = ZVG.compute(ctx.world, ctx.fr, ctx.nx, ctx.ny, ctx.res, ctx.seed, ctx.size_km,
                     ZVG.surface(ctx.h.astype(np.float32), ctx.lake_depth.astype(np.float32), ctx.water), ctx.water, ice_l,
                     ctx.discharge.astype(np.float32), ctx.area.astype(np.float32), ctx.marsh, fields=ctx.fields, log=ctx.log,
                     want_fractions=True, rock=ctx.surf_f, landform=ctx.form_f,  # (and the soils, PW-331)
                     glacial_loess=ctx.glac_loess if ctx.glac_stats else None)
    ctx.veg_l, ctx.tr = ctx.vz["layers"], ctx.vz["terrain"]


def coastal_life(ctx):
    """Coastal and shallow-sea life (zoom.coastal); mangrove and salt-marsh pixels.
    Reads: Pk, biome, cz, d_sea, fr, glacier, h, keep_means, marsh, nx, ny, px, py, res, sea, seed, size_km, surf_f,
    veg_l, vf, water, world.
    Writes: biome, cz, h, wetland."""
    # --- coastal and shallow-sea life (zoom.coastal, PW-188); names mangrove and salt-marsh pixels
    ctx.cz = ZCL.place(ctx.world, ctx.fr, ctx.Pk, ctx.px, ctx.py, ctx.nx, ctx.ny, ctx.res, ctx.size_km, ctx.seed, ctx.h, ctx.water, ctx.glacier, ctx.d_sea, ctx.surf_f,
                   ctx.vf["reef"] if ctx.vf is not None else None)
    if np.isfinite(ctx.cz["reef_top"]).any():  # reefs as terrain (PW-326): each cell's mean kept on the shelf around (lagoons)
        on_r = np.isfinite(ctx.cz["reef_top"])
        h_r = np.where(on_r, np.maximum(ctx.h, np.nan_to_num(ctx.cz["reef_top"], nan=-1e9)), ctx.h)
        ctx.h = ctx.keep_means(h_r, ctx.h, ctx.sea, np.where(ctx.cz["shelf"], 1.0, 0.1) * (ctx.sea & ~on_r))
        ctx.h = np.where(ctx.sea, np.minimum(ctx.h, -0.5), ctx.h)
    ctx.veg_l["vegetation"] = ZCL.name_vegetation(ctx.cz["layer"], ctx.veg_l["vegetation"])
    ctx.biome = vegetation.biome_of(ctx.veg_l["vegetation"], ctx.biome).astype(np.uint8)
    # wetlands: 1 a coastal plain's marsh, 2 the vegetation's (floodplains, mires, lake shores: PW-178)
    ctx.wetland = np.where(ctx.marsh, 1, np.where((ctx.water == 0) & np.isin(ctx.veg_l["vegetation"], list(ZVG.WETLAND_TYPES)), 2, 0)
                       ).astype(np.uint8)


def ice_bed(ctx):
    """The bed below the sea under grounded ice.
    Reads: cx, cy, e_bed, e_c, glacier, h, ice_th, keep_means, land_c, own_s, px, py, sel, sp, sunk.
    Writes: e_bed, h, ice_th."""
    # --- the bed below the sea under grounded ice (PW-356) ------------------
    # The terrain was built on the land view (land_world: a sub-sea bed under
    # grounded ice at 1 m, its ice thinned to keep the surface). Under the
    # zoom's glaciers the bed now sinks to the world's, its relief kept: by
    # each coarse cell's depth below the view (interpolated as the coarse
    # heights are), then each such cell's iced pixels corrected to the true
    # bed's mean (the view's 1 m floor had let its relief only rise above
    # it); a load's dip or a marine basin is hundreds of km wide, smooth at
    # the zoom's scale. The ice thickens by as much, so its surface and the
    # coastline stay. (Bare land in such a cell, rare, keeps the view's
    # ground above the sea.)
    sunk_c = ctx.sunk[ctx.sel]
    ctx.e_bed = ctx.e_c - sunk_c  # the true coarse bed
    if np.any(sunk_c > 0) and ctx.glacier.any():
        dz, _ = ZK.gauss_interp(ctx.px, ctx.py, ctx.cx, ctx.cy, sunk_c[:, None], ctx.land_c[:, None].astype(float), 0.5 * ctx.sp)
        hb = np.where(ctx.glacier, ctx.h - np.maximum(np.nan_to_num(dz[:, 0]), 0.0), ctx.h)
        n_g = np.bincount(ctx.own_s, ctx.glacier, minlength=len(ctx.sel))
        m_g = np.bincount(ctx.own_s, np.where(ctx.glacier, ctx.h, 0.0), minlength=len(ctx.sel)) / np.maximum(n_g, 1)
        drop = np.where((sunk_c > 0) & (n_g > 0), m_g - ctx.e_bed, 0.0)  # (how far each cell's ice pixels go down)
        for _ in range(RG.MEAN_PASSES // 2):  # (a one-cell basin keeps its depth, as in the detail's correction)
            hb = np.minimum(ctx.keep_means(hb, ctx.h - drop[ctx.own_s], ctx.glacier), ctx.h)
        ctx.ice_th = np.where(ctx.glacier, ctx.ice_th + (ctx.h - hb), ctx.ice_th)
        ctx.h = hb


def stats(ctx):
    """The statistics the zoom reports.
    Reads: L, all_falls, area, barrier, bi_layer, biome, cell_means, clim_f, cz, deltas, discharge, e_bed, e_c,
    elev, fields, form_f, fr, full_px, glac_form, glac_stats, glacier, h, ice_th, interior_c, kps, lake, lake_depth,
    lake_info, lake_kind, land, land_all, layers, lf, lf_counts, lf_gorges, lf_lake, lf_overlay, marsh, n_rivers_in,
    n_splits, north, nx, ny, own, peoples, pix_lat, precip, rec_out, res, riv_cells, river_segs, rock_f, sea, seed,
    size_km, stats, sunk, surf_f, t_cold, t_warm, temp, tide_f, top_falls, tr, veg_l, vf, vz, water, wave_f,
    wetland, world.
    Writes: coarse, e_c, layers, sat, stats."""
    # --- stats -----------------------------------------------------------
    ctx.e_c = ctx.e_bed  # (the cells' true bed)
    m_fine, cnt = ctx.cell_means(ctx.h)
    full = cnt > 0.6 * ctx.full_px
    inland_c = ctx.interior_c & full
    coarse_land_px = ctx.land_all[ctx.own]
    ctx.stats = {
        "land_pct": round(100 * ctx.land.mean(), 1),
        "coarse_land_pct": round(100 * coarse_land_px.mean(), 1),
        "land_sea_agreement_pct": round(100 * (ctx.land == coarse_land_px).mean(), 1),
        "mean_elev_m": round(float(ctx.h.mean()), 1),
        "coarse_mean_elev_m": round(float((ctx.elev - ctx.sunk)[ctx.own].mean()), 1),
        "mean_land_elev_m": round(float(ctx.h[ctx.land].mean()), 1) if ctx.land.any() else None,
        "cell_mean_rms_error_m": round(float(np.sqrt(np.mean((m_fine - ctx.e_c)[full] ** 2))), 1) if full.any() else None,
        "cell_mean_bias_m": round(float(np.mean((m_fine - ctx.e_c)[full])), 1) if full.any() else None,
        "inland_cell_mean_bias_m": round(float(np.mean((m_fine - ctx.e_c)[inland_c])), 1) if inland_c.any() else None,
        "inland_cell_mean_rms_error_m": (round(float(np.sqrt(np.mean((m_fine - ctx.e_c)[inland_c] ** 2))), 1)
                                         if inland_c.any() else None),
        "min_m": round(float(ctx.h.min()), 1),
        "max_m": round(float(ctx.h.max()), 1),
        "max_discharge_m3s": round(float(ctx.discharge.max()), 1),
        "lakes": int(len(np.unique(ZK.label_components(ctx.lake | ctx.lf_lake, ctx.nx, ctx.ny)[0][ctx.lake | ctx.lf_lake]))),
        # (of which in a landform class's closed basins: a rift's half-grabens, a scoured shield)
        "landform_lakes": int(len(np.unique(ZK.label_components(ctx.lf_lake, ctx.nx, ctx.ny)[0][ctx.lf_lake]))),
        # (their closed basins by water balance: full lakes, closed lakes below the spill, dry flats, silted up)
        "landform_basins": ctx.lf_counts,
        # (the overlays: dunes' types, karst's dolines, poljes, towers, ponds, sinking streams and springs)
        "landform_overlay": ctx.lf_overlay,
        # (the glacial landforms, zoom.glacial: troughs, fjords, cirques, moraine belts, outwash, loess, lakes)
        "glacial": ctx.glac_stats,
        "barrier_px": int(ctx.barrier.sum()), "wetland_pct": round(100 * float((ctx.wetland > 0).mean()), 2),
        "marsh_pct": round(100 * float(ctx.marsh.mean()), 2),
        # the vegetation (zoom.vegetation): % of the vegetated land by named type, mean tree cover and NPP
        "vegetation": ctx.vz["stats"],
        # coastal and shallow-sea life (zoom.coastal): km^2 of each habitat
        "coastal_life": ctx.cz["stats"],
        # reefs as terrain (zoom.coastal, PW-326): km^2 of fringing, barrier and patch reef flats
        "reef_forms": ctx.cz.get("reef_forms", {}),
        "lake_pct": round(100 * ctx.lake.mean(), 2),
        # (the cells with pixels in the region; of them, coarse river cells)
        "coarse_cells": int(len(np.unique(ctx.own))),
        "coarse_river_cells": int(sum(int(c) in ctx.riv_cells for c in np.unique(ctx.own))),
        "rivers_entering": ctx.n_rivers_in,
        "largest_lakes": ctx.lake_info[:5],
        # Galloway weights (coast.galloway) and the shape they gave each delta
        "deltas": [{"mouth_km": [round(d["x"], 1), round(d["y"], 1)], "discharge_m3s": round(d["q"]),
                    "plain_radius_km": round(d["R"]), "type": d["gw"]["type"], "weights": d["gw"]["weights"],
                    "wave_power_kw_m": round(d["wave"], 1), "tide_range_m": round(d["tide"], 2),
                    "sediment_mt_yr": {k: round(d["gw"][f"sediment_{k}_kgs"] * SEC_PER_YR / 1e9, 1)
                                       for k in ("river", "wave", "tide")},
                    "mouths": d["mouths"], "fingers": d.get("fingers", [0, 0]),
                    "depth_front_m": round(d["depth_front_m"]), "buoyant": round(d["buoy"], 2),
                    "form": d["form"], "marine_layers": d["marine"],
                    "seaward": [round(float(v), 3) for v in d["u"]],
                    "lat_lon": [round(v, 3) for v in RG._latlon(ctx.fr.to_sphere(np.array([d["x"]]), np.array([d["y"]]))[0])]}
                   for d in ctx.deltas],
        "distributary_splits": ctx.n_splits,
        # the biggest pixel-scale falls (see waterfalls()), ~15 km apart; kind "lip": a knickpoint kept
        # from a steep coarse reach (see knickpoints()), with its gorge and plunge pool; "scarp" / "bench":
        # over a landform's cliff (zoom.landforms), with a plunge pool; "lake outlet"; "drop": any other
        "waterfalls": ctx.top_falls,
        # every fall >= WF_MIN_DROP m (px, lat, lon, height_m, discharge_m3s, kind), highest first
        "falls": ctx.all_falls,
        "falls_count": {"30m": sum(f["height_m"] >= 30 for f in ctx.all_falls),
                        "100m": sum(f["height_m"] >= 100 for f in ctx.all_falls)},
        "knickpoints": sum(len(kp.get("course_px", ())) > 0 for kp in ctx.kps),  # (reaches with falls in the region)
        # the volcanoes drawn (zoom.volcanoes), with what they look like now
        "volcanoes": ctx.vf["list"] if ctx.vf is not None else [],
        # % of the land each synthesised landform class shapes (zoom.landforms)
        "landforms": ctx.lf.stats() if ctx.lf is not None else {},
        "landform_gorges": len(ctx.lf_gorges),
    }
    ctx.layers = {
        "elevation": ctx.h.astype(np.float32),
        "water": ctx.water,
        "lake_depth": ctx.lake_depth.astype(np.float32),
        # (lake pixels: fresh unless closed; ponds and plunge pools are fresh; pans are dry land)
        "lake_kind": np.where(ctx.water == 2, np.where(ctx.lake_kind == 2, 2, 1), np.where(ctx.lake_kind == 3, 3, 0)).astype(np.uint8),
        "discharge": ctx.discharge.astype(np.float32),
        "drainage_area": ctx.area.astype(np.float32),
        # each pixel's D8 receiver, as the landscape pass routed the water (PW-373: the 3D view's rivers)
        "receiver": RG.d8_slots(ctx.rec_out, ctx.nx),
        "precipitation": ctx.precip.astype(np.float32),
        "temperature": ctx.temp.astype(np.float32),
        # July and January (the interpolated cells' own, PW-374) and the half-years' rain (PW-139)
        "temperature_jul": np.where(ctx.north, ctx.t_warm, ctx.t_cold), "temperature_jan": np.where(ctx.north, ctx.t_cold, ctx.t_warm),
        "precipitation_jul": ctx.fields["p_jul"], "precipitation_jan": ctx.fields["p_jan"],
        "ice": np.where(ctx.glacier, np.maximum(ctx.ice_th, 1.0), 0).astype(np.float32),
        "tide_range": np.where(ctx.sea, ctx.tide_f, 0).astype(np.float32),
        "wave_power": np.where(ctx.sea, ctx.wave_f, 0).astype(np.float32),
        "rock": ctx.rock_f,
        "surface_rock": ctx.surf_f,
        "climate": ctx.clim_f,
        "biome": ctx.biome,
        **({"landform": ctx.form_f} if ctx.form_f is not None else {}),
        **({"glacial_form": ctx.glac_form} if ctx.glac_stats else {}),  # (its loess goes to the soils' "loess", PW-884)
        "wetland": ctx.wetland,
        "barrier_island": ctx.bi_layer,
        "coastal_life": ctx.cz["layer"],
        # vegetation (decision 9A: the summary layers; zoom.vegetation.fractions recomputes each type's cover)
        **ctx.veg_l,
        # terrain indices (zoom.terrain, PW-196)
        "radiation_index": ctx.tr["radiation_index"], "twi": ctx.tr["twi"],
        "river_dist": np.where(ctx.land, np.minimum(ctx.tr["river_dist"], 255), 0),
        "coast_dist": np.where(ctx.land, np.minimum(ctx.tr["coast_dist"], 255), 0),
        # cloud cover (%) of the half-years, the world's interpolated (the satellite view's clouds)
        **({f"cloud_{s}": np.round(100 * ctx.fields[f"cloud_{s}"]) for s in ("jul", "jan")}
           if ctx.fields.get("cloud_jul") is not None else {}),
    }
    # human-use layers (humanuse.py, PW-099): navigable rivers, harbours, passes, farmland, fresh water
    ctx.layers.update({k: v.ravel() for k, v in HU.zoom_layers(
        {k: np.asarray(v).reshape(ctx.ny, ctx.nx) for k, v in ctx.layers.items()}, ctx.res,
        HU.falls_pixels(ctx.stats.get("falls", []), ctx.fr, ctx.nx, ctx.ny, ctx.res)).items()})
    # the peoples' land use (zoom.peoples, PW-667), an optional overlay: only with a peoples run (zoom(peoples=RUN))
    peo = None
    if ctx.peoples is not None:
        nu_w = np.zeros((vegetation.NP, ctx.nx * ctx.ny))
        nu_w[:, ctx.vz["idx"]] = ctx.vz["nu"]
        peo = ZP.apply(ctx.world, ctx.fr, ctx.nx, ctx.ny, ctx.res, ctx.size_km, ctx.peoples, {k: np.asarray(v).ravel() for k, v in ctx.layers.items()}, nu_w, ctx.seed)
        ctx.layers.update(peo["layers"])
        ctx.layers["biome"] = vegetation.biome_of(ctx.layers["vegetation"], ctx.layers["biome"]).astype(np.uint8)
        ctx.layers["land_use"] = peo["land_use"]
        ctx.stats["peoples"] = peo["stats"]
        ctx.vz["nu"] = peo["nu"][:, ctx.vz["idx"]]
    # the satellite view (satellite.py, PW-083), from each pixel's plant fractions
    nu = np.zeros((vegetation.NP, ctx.nx * ctx.ny))
    nu[:, ctx.vz["idx"]] = ctx.vz["nu"]
    tilt = float(ctx.world["meta"].get("params", {}).get("tilt", 23.4))
    # game attributes of the plants and soils (gameattrs.py, PW-206), from the same per-pixel fractions
    ctx.layers.update({k: v.ravel() for k, v in GA.zoom_layers(
        {k: np.asarray(v).reshape(ctx.ny, ctx.nx) for k, v in ctx.layers.items()}, ctx.res, ctx.pix_lat, nu, tilt).items()})
    ctx.sat = SAT.zoom_images({k: np.asarray(v).reshape(ctx.ny, ctx.nx) for k, v in ctx.layers.items()}, nu, ctx.pix_lat, tilt, ctx.res)
    ctx.coarse = {"elevation": ctx.elev[ctx.own], "precipitation": ctx.L["precipitation"][ctx.own].astype(float),
              "river_segs": ctx.river_segs}


def assemble(ctx):
    """The zoom's dict: layers, stats, the debug stages and the satellite view.
    Reads: coarse, fit_log, fr, iterations, kps, lakes_out, layers, nx, ny, ov_src, pin_src, rapids_lift, rec_out,
    res, river_min_flow, sat, sp, stages, stats, t0.
    Writes: ."""
    return {"nx": ctx.nx, "ny": ctx.ny, "res": ctx.res, "frame": ctx.fr, "layers": {k: v.reshape(ctx.ny, ctx.nx) for k, v in ctx.layers.items()},
            "stats": ctx.stats, "coarse": ctx.coarse, "rec": ctx.rec_out, "kps": ctx.kps, "satellite": ctx.sat,
            "lakes": ctx.lakes_out,
            "debug": {"pinned": ctx.pin_src, "overrides": ctx.ov_src, "rapids_lift": ctx.rapids_lift, "stages": ctx.stages, "fit": ctx.fit_log},
            "seconds": round(time.time() - ctx.t0, 1),
            "params": {"iterations": ctx.iterations, "river_min_flow": ctx.river_min_flow, "coarse_spacing_km": round(ctx.sp, 1)}}
