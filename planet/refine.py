"""A finished world refined onto a finer global grid (PW-490 first cut, PW-1198): `planet refine <world> --level 8`.

The tectonic history stays the source world's (L7); only the finished moment is redone on the finer grid. The
icosphere nests (grid._subdivide, nest.step): fine cells 0 .. n7-1 are the coarse cells themselves, the others are
edge midpoints, so every coarse cell keeps its place.

  terrain   the regional zoom's terrain stages on the sphere (zoom/stage_terrain.py: coastline, detail, mean
            correction), with its constants, its ruggedness (stage_terrain.ruggedness), and its noise seeds at the
            same planet-km positions: a coarse cell keeps its land or sea, the new cells between decide by a
            domain-warped land indicator; relief noise by rock ruggedness; each coarse cell keeps its height as the
            mean of its fine cells of its own kind (land of land, sea of sea).
  geology   each fine cell takes one coarse cell's rock column (plate, crust, rock, cover, landform class, strata,
            glacial imprint): the nearest to its warped position among those of its own land or sea.
  finish    world.finish on the fine grid, with the climate run on the coarse grid and brought down to the fine
            cells (nest.climate_coarse: lapse rate on each cell's own height; rain shadows as resolved at the coarse
            grid), then everything per fine cell: erosion, rivers and lakes (sea by connection), waves, tides, the
            sea, coastal life, soils, vegetation and biomes, satellite, human use, game attributes, coast forms,
            resources (the run's history pass on the coarse grid, mapped onto the fine cells).

Not done (lane 104 report): the landform classes' own synthesis (zoom/landforms.py works on the
zoom's pixel raster), sub-cell orographic rain."""
from __future__ import annotations

import time

import numpy as np

from . import kernels
from . import store as S
from . import summit
from . import vegetation as VEG
from . import world as W
from .climate import LAPSE
from .constants import T_REF_C
from .geo import R_KM, is_land, smoothstep
from .grid import Grid, build_grid
from .nest import chain
from .ocean import cell_area_km2
from .tectonics.isostasy import grounded
from .zoom import kernels as ZK
from .zoom import regional as RG
from .zoom.stage_terrain import ruggedness

# the geology a world's finish takes as given (timeline._world's extra), carried from the coarse cells
GEOLOGY = ("plate", "crust", "plate_boundary", "crust_age", "plate_speed", "rock", "surface_rock", "sediment_cover",
           "crust_thickness", "landform", "landform_age", "strata_top", "strata_top_km", "strata_next", "strata_dip",
           "fold_wavelength", "rift_strain", "glaciated_myr", "glacial_erosion", "glacial_till", "glacial_outwash",
           "glacial_loess", "ice_max")
MEAN_PASSES = RG.MEAN_PASSES  # smooth corrections towards each coarse cell's mean (the zoom's count)
# the finish's river-carving pass (world.finish): the source world had its own at 0.3, so a second at that strength
# lowers the land twice (783674 -> L8: mean land 366 -> 310 m at 0.3, 347 m at 0.1; rivers, lakes and islands alike)
EROSION = 0.1
CEIL_M = 300.0  # m a fine land cell may stand above the highest coarse cell round it (soft)
DRAIN_ROUNDS = 3  # fill the noise's hollows, then restore the means, this many times
CORR_SIGMA = 0.3  # the correction's smoothing, in coarse cells (the zoom uses 0.5; with four fine cells a coarse cell that
#   leaves the alternating residuals in place: inland RMS 25 m against 3.5 m at 0.3, L6 -> L7 of world 4360a3)
WARP = 0.35  # the geology's boundary warp, in coarse cells


class Nest:
    """A coarse grid g and a finer nested grid G: each fine cell's candidate coarse cells (the one it lies in and
    that cell's neighbours), their squared distances (km^2), and sums over the nest (each coarse cell's
    full-weighting share of the fine cells, nest.step)."""

    def __init__(self, g: Grid, G: Grid):
        assert G.level > g.level and np.array_equal(G.centers[:g.n], g.centers), "grids don't nest"
        self.g, self.G = g, G
        self.own = g.locate(G.centers)
        deg = np.diff(g.nbr_off)
        nb = np.full((g.n, 6), -1, np.int64)
        for k in range(6):
            i = np.flatnonzero(deg > k)
            nb[i, k] = g.nbr_idx[g.nbr_off[i] + k]
        cand = np.concatenate([self.own[:, None], nb[self.own]], 1)
        self.valid = cand >= 0
        self.cand = np.where(self.valid, cand, self.own[:, None])
        self.d2 = (((G.centers[:, None, :] - g.centers[self.cand]) * R_KM) ** 2).sum(-1)
        self.steps = chain(G, g.level)
        self.area = cell_area_km2(G)

    def interp(self, vals, wts=None, sigma_km: float = 1.0):
        """vals (coarse) at each fine cell: a Gaussian-weighted mean of its candidates (sigma km) with per-cell
        weights wts (coarse; where a fine cell has none of weight: nan). The sphere's ZK.gauss_interp."""
        w = np.exp(-0.5 * self.d2 / sigma_km ** 2) * self.valid
        if wts is not None:
            w = w * np.asarray(wts, float)[self.cand]
        den = w.sum(1)
        num = (w * np.asarray(vals, float)[self.cand]).sum(1)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(den > 1e-12, num / np.maximum(den, 1e-300), np.nan)

    def pick(self, pts, same=None, kind=None):
        """Each fine cell's coarse cell for categorical fields: the candidate nearest pts (unit vectors, (nf, 3):
        warped positions), among those whose `kind` (coarse bool) equals `same` (fine bool) where there is one."""
        d = ((pts[:, None, :] - self.g.centers[self.cand]) ** 2).sum(-1) + 9.0 * ~self.valid
        if same is not None:
            d = d + 4.0 * (np.asarray(kind)[self.cand] != np.asarray(same)[:, None])
        return self.cand[np.arange(len(pts)), np.argmin(d, 1)]

    def total(self, x):
        """Each coarse cell's sum of the fine x (its full-weighting share: a midpoint counts half to each parent)."""
        for s in self.steps:
            x = 0.5 * (np.bincount(s["p0"], x, s["nc"]) + np.bincount(s["p1"], x, s["nc"]))
        return x

    def mean(self, f, mask=None):
        """Each coarse cell's area-weighted mean of the fine f over the fine cells of mask, and that share."""
        a = self.area if mask is None else self.area * mask
        num, den = self.total(a * f), self.total(a)
        return num / np.maximum(den, 1e-300), den / np.maximum(self.total(self.area), 1e-300)


def terrain(nest: Nest, L: dict, seed: int = 1, log=print) -> dict:
    """The fine bed (m) and land, from the coarse world's layers L: the zoom's coastline, detail and mean
    correction (stage_terrain), on the sphere. Returns elevation, land, the warped positions (for the geology)
    and the mean-keeping stats."""
    g, G = nest.g, nest.G
    sp, res = g.spacing * R_KM, G.spacing * R_KM
    e7 = np.asarray(L["elevation"], float)
    ice7 = np.asarray(L.get("ice", np.zeros(g.n)), float)
    land7 = is_land(e7, ice7, g)
    S_ = int(seed) * 1_000_003 + 17  # (the zoom's noise seed base: same noise at the same planet points)
    Pk = np.ascontiguousarray(G.centers * R_KM)

    # coastline (stage_terrain.coastline): the land indicator, warped noise; a coarse cell keeps its land or sea
    ind = nest.interp(np.where(land7, 1.0, -1.0), None, 0.42 * sp)
    lam = 0.9 * sp
    cw = ZK.fbm(Pk, lam, 4, 0.5, S_ + 7) / 0.17 * 0.12 * sp
    Pc = np.ascontiguousarray(Pk + cw[:, None] * np.array([0.57, -0.41, 0.71]))
    coast_n = ZK.fbm(Pc, lam, RG._octaves(lam, 2 * res), 0.62, S_ + 1) / 0.15
    ind_n = ind + 0.22 * coast_n
    ind_n[:g.n] = np.where(land7, np.maximum(ind_n[:g.n], 0.05), np.minimum(ind_n[:g.n], -0.05))
    land = ind_n > 0
    # (no specks: a lone new cell of land in the sea, or of sea in the land, that the noise's finest octave flipped,
    # takes its neighbours' side: L8 had 1,554 one-cell islets of new cells against 165 in a native L8 world)
    for side in (land, ~land):
        lab, k = G.components(side)
        size = np.bincount(lab[side], minlength=k)
        lone = side & (size[np.maximum(lab, 0)] == 1)
        lone[:g.n] = False
        ind_n = np.where(lone, -0.05 if side is land else 0.05, ind_n)
    land = ind_n > 0
    # (land's true heights: a closed hollow below sea level is land, geo.is_land, and its fine cells may stay below)
    e_land = np.nan_to_num(nest.interp(np.where(e7 > 0, e7, np.minimum(e7, -1.0)), land7, 0.5 * sp), nan=1.0)
    sunk = land & ((e_land <= 0) | (land7 & (e7 <= 0))[nest.own])
    e_sea = np.nan_to_num(nest.interp(np.minimum(e7, -1.0), ~land7, 0.5 * sp), nan=-50.0)
    base = np.where(land, e_land * smoothstep(0.0, 0.55, ind_n), e_sea * smoothstep(0.0, 0.45, -ind_n))

    # detail (stage_terrain.detail): relief noise by ruggedness; the finest octave two fine cells (the zoom stops at
    # 6 px, leaving the valleys to its landscape pass; here the finish's erosion cuts them)
    r7, _ = ruggedness(g, L)
    rug = np.nan_to_num(nest.interp(r7, None, 0.5 * sp), nan=0.5)
    lrel = np.nan_to_num(nest.interp(summit.local_relief(g, e7), None, 0.5 * sp), nan=0.0)
    fine_l = 2 * res
    lam_f, lam_r = 0.8 * sp, 0.4 * sp
    f1 = ZK.fbm(Pk, lam_f, RG._octaves(lam_f, fine_l), 0.55, S_ + 2) / 0.17
    rr = (ZK.ridged(Pk, lam_r, RG._octaves(lam_r, fine_l), 0.55, S_ + 3) - 0.55) / 0.175
    w_r = np.clip(rug, 0, 1) ** 2
    detail = (1 - w_r) * f1 + w_r * (0.4 * f1 + 0.9 * rr)
    detail = 2.2 * np.tanh(detail / 2.2)
    amp_land = RG.land_amp(rug, lrel)
    amp_sea = 5 + 0.08 * np.abs(base)
    taper = np.where(land, smoothstep(0.0, 0.35, ind_n), smoothstep(0.0, 0.25, -ind_n))
    h = base + taper * np.where(land, amp_land, amp_sea) * detail
    s_land = s_sea = 15.0
    # (no sea floor deeper than the deepest coarse cell round it, by more than the detail's reach: PW-844)
    e_nb = np.minimum(e7, np.minimum.reduceat(e7[g.nbr_idx], g.nbr_off[:-1]))[nest.own]
    sea_floor = np.minimum(e_nb - 2.2 * (5 + 0.08 * np.abs(e_nb)), -0.5)
    # ... and no land higher than the highest coarse cell round it by more than CEIL_M (a soft cap): at 28 km the
    # zoom's 2 km amplitude put cell means 3 km above the coarse peaks
    top = np.maximum(e7, np.maximum.reduceat(e7[g.nbr_idx], g.nbr_off[:-1]))[nest.own] + CEIL_M

    def clamp(hh):
        hl = top - RG.softplus(top - hh, 0.25 * CEIL_M)
        return np.where(land, np.where(sunk, hh, 0.5 + RG.softplus(hl - 0.5, s_land)),
                        np.maximum(-0.5 - RG.softplus(-0.5 - hh, s_sea), sea_floor))
    h = clamp(h)

    # mean correction (stage_terrain.mean_correction): each coarse cell's height is the mean of its fine cells of
    # its own kind (land of land, sea of sea: as nest.climate_coarse restricts the ground)
    corr_taper = np.where(land, smoothstep(0.0, 0.3, ind_n), smoothstep(0.0, 0.3, -ind_n))

    def means(hh):
        ml, sl = nest.mean(hh, land)
        ms, ss = nest.mean(hh, ~land)
        return np.where(land7, ml, ms), np.where(land7, sl, ss)

    def correct(hh, passes):
        for _ in range(passes):
            m, share = means(hh)
            ok = share > 0.25  # (a coarse cell the fine coast leaves mostly the other kind isn't held: PW-844)
            resid = np.where(ok, e7 - m, 0.0)
            # (a fine cell takes the correction of the coarse cells of its own kind round it)
            corr = np.where(land, nest.interp(resid, ok & land7, CORR_SIGMA * sp),
                            nest.interp(resid, ok & ~land7, CORR_SIGMA * sp))
            hh = clamp(hh + corr_taper * np.nan_to_num(corr))
        return hh
    h = correct(h, MEAN_PASSES)

    # drainage: the noise's closed hollows drain (filled to their spill, priority_flood), but where the coarse world
    # holds water or drains inland (its lakes, closed basins, hollows below sea level): a pit the coarse terrain
    # doesn't have is crossed by channels the noise doesn't draw (as hydrology.fill_shallow's shallow hollows); then
    # the means again (the zoom's landscape pass grades its rivers instead)
    lk7 = np.asarray(L.get("lake_kind", np.zeros(g.n))) > 0
    keep = (lk7 | _inland(g, L, land7) | (land7 & (e7 <= 0)))[nest.own] & land
    filled = 0
    for r in range(DRAIN_ROUNDS):
        # (the sea by connection: a fine bit of sea the new coast cut off from the ocean is a hollow and drains too)
        outlet = ~is_land(h, None, G) | keep
        hf = kernels.priority_flood_to(h.astype(float), outlet, G.nbr_off, G.nbr_idx, 0.01)[0]
        filled = max(filled, int((hf > h + 0.5).sum()))
        h = np.where(outlet, h, np.maximum(h, hf))
        if r < DRAIN_ROUNDS - 1:  # (the last fill stays: the means move by what it raises)
            h = correct(h, MEAN_PASSES // 2)
    m, share = means(h)
    interior = land7 & (np.bincount(np.repeat(np.arange(g.n), np.diff(g.nbr_off)), ~land7[g.nbr_idx], g.n) == 0)
    bias = (m - e7)[interior]
    stats = {"interior_cells": int(interior.sum()), "inland_cell_mean_bias_m": round(float(bias.mean()), 2),
             "inland_cell_mean_rms_error_m": round(float(np.sqrt((bias ** 2).mean())), 2),
             "land_cells": int(land.sum()), "filled_cells": filled, "land_share": round(float((nest.area * land).sum() / nest.area.sum()), 4),
             "coarse_land_share": round(float((cell_area_km2(g) * land7).sum() / cell_area_km2(g).sum()), 4)}
    log(f"  terrain: land {stats['land_share']:.1%} (coarse {stats['coarse_land_share']:.1%}); inland cell means "
        f"bias {stats['inland_cell_mean_bias_m']:+.1f} m, RMS {stats['inland_cell_mean_rms_error_m']:.1f} m")
    # the geology's warped positions: ragged boundaries between coarse cells' rock columns, not hexagons
    a = WARP * sp
    wv = np.column_stack([ZK.fbm(Pk, sp, 3, 0.5, S_ + 201 + k) / 0.17 for k in range(3)])
    Pw = G.centers + a / R_KM * wv
    Pw /= np.linalg.norm(Pw, axis=1, keepdims=True)
    return {"elevation": h, "land": land, "land7": land7, "warped": Pw, "stats": stats}


def _inland(g: Grid, L: dict, land: np.ndarray) -> np.ndarray:
    """The coarse land whose water ends on land (a closed basin's), by its stored receivers."""
    if "downstream" not in L:
        return np.zeros(g.n, bool)
    down = np.asarray(L["downstream"], np.int64)
    end = np.where(down >= 0, down, np.arange(g.n))
    for _ in range(64):  # (pointer doubling: 2^64 steps)
        nxt = end[end]
        if np.array_equal(nxt, end):
            break
        end = nxt
    return land & land[end]


def _held_orbit(meta: dict, log=print):
    """A finished time-zoom world's orbit anomaly on its own grid (finish.orbit_dt), or None."""
    if not meta.get("timezoom") or meta.get("timezoom_kyr") is None:
        return None
    from . import finish as F
    from .timeline import load_frames
    try:
        tz_dir = S.find_run(meta["timezoom"])
    except SystemExit:
        log(f"  (time zoom {meta['timezoom']} is gone: no orbit anomaly)")
        return None
    run, _ = load_frames(tz_dir, ())
    st = F.frame_state(tz_dir, F.frame_index(run, float(meta["timezoom_kyr"])))
    return F.orbit_dt(run, st)


def refine(world: dict, level: int, erosion: float = EROSION, seed: int = 1, log=print) -> dict:
    """The world (world.load's shape: a tectonic world on its grid) refined onto the level-`level` grid: a new
    world dict for world.save."""
    t0 = time.time()
    g: Grid = world["grid"]
    L, m0 = world["layers"], world["meta"]
    if m0.get("method") != "tectonics":
        raise SystemExit("refine needs a world from a run (method tectonics)")
    if level <= g.level:
        raise SystemExit(f"--level must be finer than the world's ({g.level})")
    G = build_grid(level)
    nest = Nest(g, G)
    sp = g.spacing * R_KM
    log(f"  grids L{g.level} -> L{level}: {g.n} -> {G.n} cells [{time.time() - t0:.1f}s]")
    tr = terrain(nest, L, seed, log)
    elev, land, land7 = tr["elevation"], tr["land"], tr["land7"]
    pick = nest.pick(tr["warped"], land, land7)
    log(f"  terrain [{time.time() - t0:.1f}s]")

    # the ice: the coarse land's, smoothed, on the fine land; grounded on the fine bed
    ice7 = np.asarray(L.get("ice", np.zeros(g.n)), float)
    ice = np.where(land, np.nan_to_num(nest.interp(np.where(land7, ice7, 0.0), land7, 0.5 * sp), nan=0.0), 0.0)
    ice = grounded(elev, np.round(ice, 1))
    # the geology: one coarse cell's column per fine cell
    extra = {k: np.asarray(L[k])[pick] for k in GEOLOGY if k in L}
    if "_plate_velocity" in L:  # (on the fine cell's tangent plane)
        v = np.asarray(L["_plate_velocity"], float)[pick]
        p = G.centers
        extra["_plate_velocity"] = v - (v * p).sum(1, keepdims=True) * p
    extra["ice"] = ice

    # the plants' history: the coarse world's cover, CO2, unlocked groups (a time zoom's trees held)
    mv = m0.get("vegetation", {})
    nu0 = np.stack([np.clip(np.nan_to_num(nest.interp(np.asarray(L[f"veg_{c}"], float) / 100.0, land7, 0.5 * sp),
                                          nan=0.0), 0, 1) if f"veg_{c}" in L else np.zeros(G.n) for c in VEG.CODES])
    pfts = set(mv.get("pfts", VEG.CODES))
    veg = {"nu0": nu0, "pco2": float(mv.get("pco2", VEG.CA_REF)), "unlocked": np.array([c in pfts for c in VEG.CODES]),
           "groups": mv.get("groups"), "reef_builders": bool(mv.get("reef_builders", True)),
           **({"held": True} if m0.get("timezoom") else {})}

    # the run's records, on the coarse grid, mapped onto the fine cells: the soils' climate memory and the
    # resources' history
    memory = hist = None
    sr = m0.get("source_run")
    run_dir = S.find_run(sr) if sr and S.exists("run", sr) else None
    if run_dir is not None:
        from .timeline import soil_memory
        v7 = np.asarray(L["_plate_velocity"], float) if "_plate_velocity" in L else np.zeros((g.n, 3))
        mem = soil_memory(run_dir, float(m0["t_myr"]), g, v7)
        if mem is not None:
            z7, z = np.maximum(np.asarray(L["elevation"], float), 0.0), np.maximum(elev, 0.0)

            def down(a, temp):
                a = np.asarray(a, float)
                if a.ndim == 2:
                    return np.stack([down(r, temp) for r in a])
                if temp:  # (through the lapse rate, as the climate)
                    return np.nan_to_num(nest.interp(a + LAPSE * z7, None, 0.5 * sp)) - LAPSE * z
                return np.nan_to_num(nest.interp(a, None, 0.5 * sp))
            memory = {k: (down(v, "temp" in k) if isinstance(v, np.ndarray) and v.shape[-1] == g.n and k != "ages"
                          else v) for k, v in mem.items()}
        if W.resources_on() and "landform" in L:
            from . import resources
            h7 = resources.history(run_dir, float(m0["t_myr"]), g)
            hist = {k: (v[pick] if isinstance(v, np.ndarray) and v.ndim and v.shape[0] == g.n else v)
                    for k, v in h7.items()}
    else:
        log(f"  (source run {sr} is gone: no soil memory, no resources)")
    od = _held_orbit(m0, log)
    log(f"  records [{time.time() - t0:.1f}s]")

    keep = ("seed", "source_run", "source_run_name", "t_myr", "hotspots", "volcanoes", "volcano_columns",
            "global_temp_c", "sea_level_m", "from_keyframe", "finished", "timezoom", "timezoom_name", "timezoom_kyr",
            "sea_level_change_m", "ice_volume_mkm3", "orbit", "mode", "replay_matches_keyframe", "code")
    meta = {"method": "tectonics", **{k: m0[k] for k in keep if k in m0}, "level": level,
            "ice_bed_below_sea_cells": int(((ice > 0) & (elev <= 0)).sum()),
            "refined_from": {"world": world.get("id") or m0.get("id"), "name": world.get("name"), "level": g.level,
                             "terrain": tr["stats"], "climate_level": g.level, "seed": seed}}
    pm = m0.get("params", {})
    dT = float(m0["global_temp_c"]) - T_REF_C
    tilt = float(pm.get("tilt", 23.4))
    out = W.finish(G, elev, extra, meta, erosion=erosion, params={"tectonics": pm.get("tectonics", {})}, dT=dT,
                   tilt=tilt, ice=ice, veg=veg, orbit_dt=od, soil_memory=memory, climate_level=g.level,
                   history=hist, t0=t0)
    out["meta"]["refined_from"]["seconds"] = round(time.time() - t0, 1)
    log(f"  finished [{time.time() - t0:.1f}s]")
    return out


def _log(*a):
    print(*a, flush=True)


def refine_world(ref: str, level: int, erosion: float = EROSION, seed: int = 1, log=_log):
    """`planet refine`: load the world ref (id or path), refine it, save the new world; returns its path."""
    path = S.find_world(ref)
    t = time.time()
    world = W.load(path)
    world["id"] = path.stem
    log(f"  loaded {path.name} (L{world['meta']['level']}) [{time.time() - t:.1f}s]")
    out = refine(world, level, erosion, seed, log)
    name = f"{world.get('name') or path.stem} refined to L{level}"
    t = time.time()
    p = W.save(out, name)
    log(f"  saved {p.name} [{time.time() - t:.1f}s]")
    return p
