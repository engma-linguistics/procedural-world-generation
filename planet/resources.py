"""Resources layer, stage 1 (PW-155; design: docs/proposals/resources.md).

A coarse per-cell likelihood (0..1) of each resource, derived from what the
run recorded, at world level. No new physics and no run time: a world's own
layers (basement rock, strata, landforms, crust, climate, rivers) plus a
*history* read back from the run's keyframes along the plates' motion (each
cell's ground traced back frame by frame: where it was, what was happening
there). Each resource follows a named deposit model; its rule is written next
to it. A likelihood is "how likely a deposit of this kind lies in this cell
(within prospecting depth)", not a grade: zooms site concrete deposits from it
(stage 2, zoom_resources.py).

    history(run_dir, t_myr, grid)        -> per-cell history arrays (traced keyframes)
    likelihoods(grid, L, meta, hist)     -> {key: 0..1 per cell}
    world_layers(grid, L, meta, hist)    -> the res_* layers to store with a world
    deposits(grid, L)                    -> the summary: top deposit districts per landmass
    add_to_world(ref)                    -> (re)makes a saved world's resource layers in place

The history is optional: without a run (the Earth world, generated worlds)
the rules fall back to the world's layers alone (rock, landforms, ages).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from numba import njit

from .geo import R_KM, world_land

# ---------------------------------------------------------------------------
# The resources: (key, name, group, colour, model). Groups: metal, gem,
# energy, industrial, stone, fantasy. Fantasy ones are marked as such everywhere.
# ---------------------------------------------------------------------------
RESOURCES = [
    ("porphyry_cu", "porphyry copper-molybdenum-gold", "metal", "#d9772b",
     "arc magmatism in the last ~200 Myr, little exhumed (Andes, Rockies)"),
    ("epithermal_au", "epithermal gold-silver", "metal", "#ffd84a",
     "shallow hot springs over young arcs and rifts (< ~60 Myr; Nevada, Japan)"),
    ("vms", "volcanogenic massive sulphide (Cu-Zn-Pb)", "metal", "#3fa7a0",
     "sea-floor vents at spreading ridges and back-arcs, kept where accreted to a continent"),
    ("orogenic_au", "orogenic (lode) gold", "metal", "#f2b705",
     "quartz veins of collision belts and old greenstone belts (Kalgoorlie, Abitibi)"),
    ("sn_w", "tin-tungsten (granite)", "metal", "#9aa3b5",
     "exhumed granites, above all collision granites from thick crust (Cornwall, SE Asia)"),
    ("bif_fe", "banded iron formation", "metal", "#a33b2b",
     "ancient (>= 1.8 Gyr) shield crust, exposed (Pilbara, Labrador)"),
    ("magmatic_ni", "magmatic nickel-copper-PGE", "metal", "#5f7f3a",
     "plume melts and flood basalts on continents (Noril'sk, Bushveld)"),
    ("laterite_ni", "laterite nickel", "metal", "#7cbf4a",
     "long tropical weathering of mafic and ultramafic rock (New Caledonia)"),
    ("bauxite", "bauxite (aluminium)", "metal", "#c45b8f",
     "long tropical weathering of flat, well-drained ground (Guinea, N Australia)"),
    ("sed_pbzn", "sediment-hosted lead-zinc-copper", "metal", "#6b6fd1",
     "carbonates and red beds of rifts and forelands (Mississippi Valley, Kupferschiefer)"),
    ("ree", "rare earths (carbonatite)", "metal", "#d14fd1",
     "alkaline melts where rifts or plumes tap old thick continents (Bayan Obo, Mountain Pass)"),
    ("placer_au", "placer gold", "metal", "#ffe58a",
     "river gravels downstream of eroding gold sources (Klondike, California)"),
    ("placer_sn", "placer tin and heavy minerals", "metal", "#c8cdd8",
     "river and beach sands below tin granites (Malaysia, Indonesia)"),
    ("diamond", "diamonds (kimberlite pipes and their placers)", "gem", "#7fe8ff",
     "plumes and rifts tapping thick, ancient (>= 2.5 Gyr) craton roots"),
    ("gem_meta", "corundum, emerald, garnet (metamorphic gems)", "gem", "#e0245e",
     "high-grade rock of deep collision roots, now exhumed (Myanmar, Colombia)"),
    ("coal", "coal", "energy", "#9d8cf0",
     "buried peat of warm, wet, vegetated lowlands, within ~1.5 km of the surface"),
    ("oil", "oil", "energy", "#2fe08a",
     "organic-rich marine or lake shale cooked in the oil window (~2-5 km) with traps"),
    ("gas", "natural gas", "energy", "#9fc3e6",
     "source rock or coal buried deeper (~4-8 km), with traps"),
    ("salt", "salt and potash (evaporites)", "industrial", "#f1faee",
     "evaporite beds in the strata, and salt pans of closed hot basins"),
    ("obsidian", "obsidian", "stone", "#f5a3c7",
     "young (< ~10 Myr) volcanic glass of arcs, rifts and hotspots"),
    ("flint", "flint and chert", "stone", "#8a8f6a",
     "nodules in exposed limestone and chalk; cherts of old sea floor"),
    ("clay", "clay (brick and kaolin)", "stone", "#b5651d",
     "floodplain mud, exposed shale, and kaolin from weathered granite"),
    ("x_mithril", "deep-silver (mithril-like) [fantasy]", "fantasy", "#b8e0ff",
     "FANTASY: the oldest, deepest craton roots where a plume once rose"),
    ("x_adamant", "adamant [fantasy]", "fantasy", "#a855f7",
     "FANTASY: the deepest collision roots (crust once >= 65 km), now exhumed"),
    ("x_star_iron", "star-iron (meteoric) [fantasy]", "fantasy", "#ff6f3c",
     "FANTASY: seeded impact sites, kept on old surfaces"),
]
KEYS = tuple(r[0] for r in RESOURCES)
REAL = tuple(k for k, _, g, _, _ in RESOURCES if g != "fantasy")
# the dominant-resource map leaves out the near-ubiquitous stone group (its own map is 'stone')
DOMINANT = tuple(k for k, _, g, _, _ in RESOURCES if g in ("metal", "gem", "energy", "industrial"))
DOMINANT_MIN = 0.3  # likelihood under this: 'none' in the dominant map

# building stone: the best stone a cell offers (exposed rock, hardness and look)
STONE = [(0, "none (deep soil or cover)", "#00000000"), (1, "granite", "#e8a0a8"), (2, "marble", "#f4f1ea"),
         (3, "limestone", "#a8dadc"), (4, "sandstone", "#f4a259"), (5, "slate", "#4f5d75"),
         (6, "basalt", "#5a4a5e"), (7, "tuff", "#c98b6b"), (8, "gneiss and schist", "#8e7dbe"),
         (9, "quartzite", "#d8cfc0")]


def legend() -> dict:
    return {"resources": [{"id": i + 1, "key": k, "name": n, "group": g, "color": c, "model": m}
                          for i, (k, n, g, c, m) in enumerate(RESOURCES)],
            "dominant": [{"id": 0, "key": "none", "name": "none likely", "color": "#00000000"}]
                        + [{"id": KEYS.index(k) + 1, "key": k, "name": RESOURCES[KEYS.index(k)][1],
                            "color": RESOURCES[KEYS.index(k)][3]} for k in DOMINANT],
            "stone": [{"id": i, "name": n, "color": c} for i, n, c in STONE]}


LAYER_SPECS = {
    **{f"res_{k}": ("u1", 0.01, "0-1", f"likelihood of {n} ({'FANTASY; ' if g == 'fantasy' else ''}{m})")
       for k, n, g, _, m in RESOURCES},
    "resource": ("u1", 1, "class", "the most likely metal, gem, energy or salt resource (id: legend "
                                   "resources.resources; 0 none above 0.3)"),
    "stone": ("u1", 1, "class", "best building stone exposed (legend resources.stone)"),
    "coal_rank": ("u1", 1, "class", "coal rank where coal is likely: 1 lignite, 2 bituminous, 3 anthracite"),
    "res_depth": ("<u2", 10, "m", "typical depth of the most likely resource's deposit (0 at the surface)"),
}
NAMES = tuple(LAYER_SPECS)

# ---------------------------------------------------------------------------
# History: the run's keyframes read back along the plates' motion
# ---------------------------------------------------------------------------
LOOKBACK_MYR = 600.0  # how far back a cell's ground is traced (errors grow with distance)
PLUME_KM = 450.0  # a plume head's reach under a plate
K_STACK = 10  # strata in the history's column (the run keeps 3)
# lithologies of the history's column
CLASTIC, COALY, SOURCE, EVAP, CARB, VOLC = range(6)
# frame-level rules for what a deposit is (surface.ROCKS ids)
_LIMESTONE, _SANDSTONE, _SHALE, _EVAPORITE, _COAL, _GRANITE, _QUARTZITE, _FLOOD, _DOLOMITE, _TUFF = (
    6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
PEAT_T, PEAT_P, PEAT_ELEV, PEAT_TREE = 5.0, 1000.0, 250.0, 30.0  # warm-enough, wet, low, forested: a coal swamp
SOURCE_DEPTH_M = 1200.0  # shale settling in seas shallower than this (epeiric seas, shelves, rift gulfs)
TROPIC_T, TROPIC_P, TROPIC_ELEV = 20.0, 1200.0, 1500.0  # deep tropical weathering
TROPIC_KEEP_MYR = 60.0  # a laterite profile's survival (erosion, burial): older tropical time counts less


@njit(cache=True)
def _stack_step(typ, km, maxd, ntop, dc, new_t):
    """One keyframe of every cell's column: dc km of cover gained (> 0, of lithology new_t) or lost (< 0, off the
    top). typ/km/maxd (n, K): layers bottom first (ntop of them); maxd: the deepest each has been buried."""
    n, kk = km.shape
    for i in range(n):
        d = dc[i]
        if d > 0:
            j = ntop[i] - 1
            if j >= 0 and typ[i, j] == new_t[i]:
                km[i, j] += d
            else:
                if ntop[i] == kk:  # full: merge the bottom two (the thicker names them)
                    if km[i, 1] > km[i, 0]:
                        typ[i, 0] = typ[i, 1]
                    km[i, 0] += km[i, 1]
                    maxd[i, 0] = max(maxd[i, 0], maxd[i, 1])
                    for q in range(1, kk - 1):
                        typ[i, q], km[i, q], maxd[i, q] = typ[i, q + 1], km[i, q + 1], maxd[i, q + 1]
                    ntop[i] -= 1
                j = ntop[i]
                typ[i, j], km[i, j], maxd[i, j] = new_t[i], d, 0.0
                ntop[i] += 1
        elif d < 0:
            d = -d
            while d > 0 and ntop[i] > 0:
                j = ntop[i] - 1
                if km[i, j] > d:
                    km[i, j] -= d
                    d = 0.0
                else:
                    d -= km[i, j]
                    km[i, j] = 0.0
                    ntop[i] -= 1
        over = 0.0  # burial: overburden from the top down
        for j in range(ntop[i] - 1, -1, -1):
            mid = over + 0.5 * km[i, j]
            if mid > maxd[i, j]:
                maxd[i, j] = mid
            over += km[i, j]


@njit(cache=True)
def _column_summary(typ, km, maxd, ntop, n_t):
    """Per lithology: km left, km-weighted present depth to its middle and deepest burial, and the km of it in the
    oil window (max burial 2-5.5 km), the gas window (4.5-9 km), and within 1.5 km of the surface."""
    n = km.shape[0]
    tot = np.zeros((n, n_t))
    dep = np.zeros((n, n_t))
    mx = np.zeros((n, n_t))
    oil = np.zeros((n, n_t))
    gas = np.zeros((n, n_t))
    shallow = np.zeros((n, n_t))
    for i in range(n):
        over = 0.0
        for j in range(ntop[i] - 1, -1, -1):
            t, h = typ[i, j], km[i, j]
            mid = over + 0.5 * h
            tot[i, t] += h
            dep[i, t] += h * mid
            mx[i, t] += h * maxd[i, j]
            if 2.0 <= maxd[i, j] <= 5.5:
                oil[i, t] += h
            if 4.5 <= maxd[i, j] <= 9.0:
                gas[i, t] += h
            if mid <= 1.5:
                shallow[i, t] += h
            over += h
    for i in range(n):
        for t in range(n_t):
            if tot[i, t] > 0:
                dep[i, t] /= tot[i, t]
                mx[i, t] /= tot[i, t]
    return tot, dep, mx, oil, gas, shallow


def _rotate(p, axis, ang):
    """Rodrigues: each p (n, 3) turned by ang (n,) about axis (n, 3)."""
    c, s = np.cos(ang)[:, None], np.sin(ang)[:, None]
    q = p * c + np.cross(axis, p) * s + axis * (axis * p).sum(1, keepdims=True) * (1 - c)
    return q / np.linalg.norm(q, axis=1, keepdims=True)


def _dilate(grid, mask, hops=1):
    e = np.asarray(grid.edges)
    m = mask.copy()
    for _ in range(hops):
        nm = m.copy()
        nm[e[:, 0]] |= m[e[:, 1]]
        nm[e[:, 1]] |= m[e[:, 0]]
        m = nm
    return m


def history(run_dir: Path, t_myr: float, grid, lookback: float = LOOKBACK_MYR, log=None) -> dict:
    """Each cell's past, read from the run's keyframes where its ground was then: stepped back frame by frame
    with that frame's plate rotations (the plate under the traced point), so it follows plate reorganisations.
    Sea floor is traced only back to its birth (crust_age). Returns per-cell arrays (Myr of each setting, ages
    since it last held, the deepest crust it sat on) and the column summary (column_*: km of coal-bearing,
    source shale, evaporite, carbonate left, and their burial)."""
    from . import store as S
    from .timeline import load_frames
    t0 = time.time()
    run, _ = load_frames(run_dir, ())
    names = ("plate", "crust", "crust_age", "elevation", "landform", "sediment_cover", "strata_top",
             "crust_thickness", "plate_boundary", "temperature", "precipitation", "tree_cover", "lake_kind", "rock")
    names = tuple(k for k in names if k in run["layers"])
    arr = S.read_layers(run_dir, run["layers"], names)
    spec = run["layers"]
    frames = run["frames"]
    times = np.array([f["t"] for f in frames], float)
    k_now = int(np.argmin(np.abs(times - t_myr)))
    t_now = times[k_now]
    ks = [k for k in range(k_now, -1, -1) if t_now - times[k] <= lookback + 1e-9]

    def dec(name, k):
        a = arr[name]
        return S.decode(np.asarray(a[k if a.shape[0] > 1 else 0]), spec[name])

    n = grid.n
    p = grid.centers.copy()
    idx = np.arange(n)
    age_now = dec("crust_age", k_now).astype(float)
    ocean_now = dec("crust", k_now) == 0
    acc = {k: np.zeros(n) for k in ("arc_myr", "fold_myr", "rift_myr", "plume_myr", "tropic_myr", "vent_myr",
                                     "traced_myr")}
    last = {k: np.full(n, 1e4) for k in ("arc", "fold", "rift", "plume", "vent")}
    thick_max = np.zeros(n)
    thick_max_age = np.full(n, 1e4)
    # the column, oldest frame first: walk the traced frames backwards to collect, then replay forwards
    samples = []
    for kk_i, k in enumerate(ks):
        idx = grid.locate(p, idx)
        alive = ~ocean_now | (t_now - times[k] <= age_now + 2.0)
        dt = (times[ks[kk_i - 1]] - times[k]) if kk_i > 0 else (times[k] - times[k - 1] if k > 0 else 0.0)
        age = t_now - times[k]
        lf = dec("landform", k)[idx]
        elev = dec("elevation", k)[idx].astype(float)
        cr = dec("crust", k)[idx] > 0
        bd = dec("plate_boundary", k)
        near_conv = _dilate(grid, bd > 0, 2)[idx]
        near_div = _dilate(grid, bd < 0, 1)[idx]
        th = dec("crust_thickness", k)[idx].astype(float)
        hs = np.asarray(frames[k].get("hotspots") or [], float).reshape(-1, 2)
        if len(hs):
            from .geo import xyz
            hv = xyz(np.radians(hs[:, 0]), np.radians(hs[:, 1]))
            near_pl = (p @ hv.T).max(1) >= np.cos(PLUME_KM / R_KM)
        else:
            near_pl = np.zeros(n, bool)
        land = elev > 0
        tmp = dec("temperature", k)[idx] if "temperature" in arr else np.zeros(n)
        pr = dec("precipitation", k)[idx] if "precipitation" in arr else np.zeros(n)
        sets = {"arc": (lf == 11) | (cr & near_conv & ~land & (lf != 3)),
                "fold": lf == 3, "rift": lf == 4, "plume": near_pl,
                "vent": ~land & (near_div | (near_conv & ~cr))}
        for key, m in sets.items():
            m = m & alive
            acc[key + "_myr"] += np.where(m, dt, 0.0)
            last[key] = np.where(m & (last[key] > age), age, last[key])
        acc["tropic_myr"] += np.exp(-age / TROPIC_KEEP_MYR) * np.where(alive & land & (tmp >= TROPIC_T) & (pr >= TROPIC_P) & (elev < TROPIC_ELEV)
                                      & (lf != 3) & (lf != 11), dt, 0.0)
        acc["traced_myr"] += np.where(alive, dt, 0.0)
        th = np.where(alive, th, 0.0)
        thick_max_age = np.where(th > thick_max, age, thick_max_age)
        thick_max = np.maximum(thick_max, th)
        # what this frame deposits, if it gains cover (strata_top names the rock; the setting adds peat and source shale)
        top = dec("strata_top", k)[idx] if "strata_top" in arr else np.full(n, _SHALE)
        tree = dec("tree_cover", k)[idx] if "tree_cover" in arr else np.zeros(n)
        lake = dec("lake_kind", k)[idx] if "lake_kind" in arr else np.zeros(n)
        lit = np.full(n, CLASTIC, np.int8)
        lit[np.isin(top, (_LIMESTONE, _DOLOMITE))] = CARB
        lit[np.isin(top, (_FLOOD, _TUFF))] = VOLC
        lit[(land & (tmp >= PEAT_T) & (pr >= PEAT_P) & (elev < PEAT_ELEV) & (tree >= PEAT_TREE)) | (top == _COAL)] = COALY
        lit[(~land & (elev > -SOURCE_DEPTH_M) & cr & np.isin(top, (_SHALE, 3))) | (land & (lake == 2))] = SOURCE
        lit[top == _EVAPORITE] = EVAP
        cover = np.where(alive, dec("sediment_cover", k)[idx].astype(float), 0.0)
        samples.append((cover, lit))
        # step back to the previous keyframe along this frame's rotation of the plate under each point
        if kk_i + 1 < len(ks):
            kp = ks[kk_i + 1]
            om = np.zeros((max(int(x) for x in frames[k]["omega"]) + 2, 3))
            for lab, w in frames[k]["omega"].items():
                om[int(lab)] = w
            pl = np.clip(dec("plate", k)[idx].astype(int), 0, len(om) - 1)
            w = om[pl]
            sp = np.linalg.norm(w, axis=1)
            axis = w / np.maximum(sp, 1e-12)[:, None]
            p = _rotate(p, axis, -sp * (times[k] - times[kp]))
    # replay the column forwards
    typ = np.zeros((n, K_STACK), np.int8)
    km = np.zeros((n, K_STACK))
    maxd = np.zeros((n, K_STACK))
    ntop = np.zeros(n, np.int64)
    c0, _ = samples[-1]
    km[:, 0], maxd[:, 0] = c0, c0 / 2  # the cover before the record: one older clastic layer
    ntop[:] = (c0 > 0).astype(np.int64)
    prev = c0
    for cover, lit in reversed(samples[:-1]):
        _stack_step(typ, km, maxd, ntop, cover - prev, lit)
        prev = cover
    tot, dep, mx, oil, gas, shallow = _column_summary(typ, km, maxd, ntop, 6)
    out = {**acc, **{f"last_{k}": v for k, v in last.items()},
           "thick_max": thick_max, "thick_max_age": thick_max_age, "t_now": t_now,
           "column_km": tot, "column_depth": dep, "column_maxburial": mx, "column_oil": oil, "column_gas": gas,
           "column_shallow": shallow, "frames": len(ks), "seconds": round(time.time() - t0, 1)}
    if log:
        log(f"resources: traced {len(ks)} keyframes back to {t_now - times[ks[-1]]:g} Myr in {out['seconds']} s")
    return out


# ---------------------------------------------------------------------------
# Likelihoods
# ---------------------------------------------------------------------------
def sat(x, s):
    """0..1, saturating: 1 - exp(-x/s)."""
    return 1.0 - np.exp(-np.maximum(np.asarray(x, float), 0.0) / s)


def ramp(x, a, b):
    """0 at a, 1 at b (either direction), clipped."""
    return np.clip((np.asarray(x, float) - a) / (b - a), 0.0, 1.0)


def _flow_accumulate(down, flow, src, keep):
    """Carried load: each cell passes keep x (its own source + what reached it) downstream (cells in order of
    rising flow: upstream first)."""
    n = len(src)
    order = np.argsort(flow, kind="stable")
    return _carry(order.astype(np.int64), np.asarray(down, np.int64), np.asarray(src, float), keep)


@njit(cache=True)
def _carry(order, down, src, keep):
    load = src.copy()
    for i in order:
        d = down[i]
        if 0 <= d < len(load) and d != i:
            load[d] += keep * load[i]
    return load


def _impacts(grid, seed: int, surface_age, land):
    """FANTASY star-iron: deterministic impact sites (~1 per 4 Mkm2 per Gyr of kept surface), kept where the
    surface is older than the impact; a crater's ground is ~3 cells."""
    rng = np.random.default_rng(int(seed) ^ 0x5EED_1A)
    n_imp = max(int(grid.n / 400), 4)
    p = rng.normal(size=(n_imp, 3))
    p /= np.linalg.norm(p, axis=1, keepdims=True)
    age = rng.uniform(0, 3000, n_imp)
    cell = grid.locate(p)
    keep = (surface_age[cell] >= age) & land[cell]
    m = np.zeros(grid.n, bool)
    m[cell[keep]] = True
    return np.where(_dilate(grid, m, 1), 1.0, 0.0) * 0.8


def likelihoods(grid, L: dict, meta: dict | None = None, hist: dict | None = None) -> dict:
    """{key: 0..1 per cell} from a world's layers L (and the run's history, if any)."""
    meta = meta or {}
    n = grid.n
    land = world_land(L)
    elev = np.asarray(L["elevation"], float)
    g = lambda k, d=0.0: np.asarray(L[k], float) if k in L else np.full(n, d)  # noqa: E731
    rock = g("rock").astype(int)
    top = g("strata_top", -1).astype(int) if "strata_top" in L else g("surface_rock").astype(int)
    nxt = g("strata_next", -1).astype(int)
    top_km = g("strata_top_km")
    cover = g("sediment_cover")
    age = g("crust_age")
    lf = g("landform").astype(int)
    lfa = g("landform_age")
    thick = g("crust_thickness", 35.0)
    rift = g("rift_strain")
    temp, prec = g("temperature"), g("precipitation")
    cont = g("crust", 1) > 0 if "crust" in L else (rock != 0)
    exposed = cover < 0.3  # basement within reach of a mine
    craton = rock == 5
    arcrock = rock == 2
    granite = (rock == _GRANITE) | (top == _GRANITE)
    orogen = rock == 4
    h = hist
    # proxies when there is no run history: the world's own landforms and rock
    if h is None:
        # (arc basement, or andesite/tuff at the surface: GLiM's intermediate and acid volcanics on Earth)
        arcish = arcrock | np.isin(top, (2, _TUFF))
        arc_myr = np.where(lf == 11, 30.0, np.where(arcish, 30.0, 0.0))
        last_arc = np.where(lf == 11, lfa, np.where(arcish, np.minimum(age, 300), 1e4))
        fold_myr = np.where(lf == 3, 20.0, np.where(orogen, 10.0, 0.0))
        last_fold = np.where(lf == 3, lfa, np.where(orogen, np.minimum(age, 400), 1e4))
        plume_myr = np.where((lf == 7) | (lf == 12), 10.0, 0.0)
        rift_myr = np.where(rift > 0.1, 10.0, 0.0)
        tropic = np.where(land & (temp >= TROPIC_T) & (prec >= TROPIC_P), 80.0, 0.0)
        thick_max = np.maximum(thick, np.where(orogen, 50.0, 0.0))
        vent_myr = np.zeros(n)
        col = None
    else:
        arc_myr, last_arc = h["arc_myr"], h["last_arc"]
        fold_myr, last_fold = h["fold_myr"], h["last_fold"]
        plume_myr, rift_myr, tropic = h["plume_myr"], h["rift_myr"], h["tropic_myr"]
        thick_max, vent_myr = np.maximum(h["thick_max"], thick), h["vent_myr"]
        col = h
    # exhumation proxy: an exhumed granite or a shield shows deep levels; young cover hides them
    deep_level = granite | (lf == 2) | (orogen & exposed)
    R = {}
    # porphyry Cu-Mo-Au (Sillitoe 2010): long-lived arc magmatism, preserved where young and shallow
    R["porphyry_cu"] = 0.7 * (sat(arc_myr, 40) * np.exp(-np.maximum(last_arc, 0) / 100) * np.where(deep_level, 0.35, 1.0)
                        * np.where(land | (elev > -500), 1.0, 0.3) * cont * (cover < 2.5))
    # epithermal Au-Ag: the shallow tops of young arcs and rifts (eroded away within tens of Myr)
    young_rift = (lf == 4) | ((rift > 0.15) & (lfa < 40))
    R["epithermal_au"] = 0.65 * (np.maximum(sat(arc_myr, 20) * np.exp(-np.maximum(last_arc, 0) / 30), 0.6 * young_rift)
                          * np.where(deep_level, 0.15, 1.0) * cont * (cover < 1.5))
    # VMS: sea-floor sulphides at ridges and arcs/back-arcs; on land where that sea floor was accreted (arc and
    # orogen basement that spent time as vent ground), at sea at today's ridges
    ridge_now = (g("plate_boundary") < 0) & ~land
    R["vms"] = np.where(cont, sat(vent_myr, 25) * np.isin(rock, (2, 4)) * (cover < 1.0) * 0.9,
                        np.where(ridge_now, 0.6, 0.0))
    # orogenic gold (Goldfarb & Groves 2015): collision belts that squeezed crust thick, 20-600 Myr ago,
    # moderately exhumed; and greenstone belts in ancient shields
    belt = 0.75 * sat(fold_myr, 30) * ramp(thick_max, 45, 60) * ramp(last_fold, 5, 25) * np.exp(-np.maximum(last_fold - 600, 0) / 300)
    # (greenstone belts and BIF basins lie mostly near craton margins: within ~3 cells of younger crust)
    edge = _dilate(grid, ~craton & cont, 3) & craton
    green = craton * ramp(age, 2400, 2900) * (0.15 + 0.3 * edge)
    R["orogenic_au"] = np.maximum(belt, green) * cont * exposed * np.where(cover < 0.05, 1.0, 0.7)
    # Sn-W: granites, mostly crustal-melt granites of thick collision crust (S-type)
    R["sn_w"] = (np.maximum(granite * 0.55, orogen * exposed * ramp(thick_max, 50, 65) * 0.8)
                 * np.where(granite & (thick_max > 50), 1.4, 1.0)).clip(0, 1) * cont
    # banded iron formations: ancient shield crust (>= ~1.8 Gyr: the age of the iron oceans), exposed
    R["bif_fe"] = craton * ramp(age, 1800, 2700) * exposed * (0.15 + 0.55 * edge)
    # magmatic Ni-Cu-PGE: plume heads and flood basalts on continental crust, best near old cratons
    flood = (lf == 7) | np.isin(top, (_FLOOD,)) | np.isin(nxt, (_FLOOD,))
    R["magmatic_ni"] = (np.maximum(sat(plume_myr, 30) * cont * (cover < 1.0) * np.where(craton, 0.8, 0.45),
                                   flood * 0.6)) * cont
    # laterites: long tropical weathering on flat ground; nickel from mafic/ultramafic parents (basalt, arc and
    # ophiolitic suture rock), bauxite from any aluminous rock that drains well
    flat = ramp(_relief(grid, elev), 600, 150)
    stripped = np.where(g("glaciated_myr", 9999) < 5, 0.2, 1.0)  # recent ice scraped the regolith off
    tro = sat(tropic, 60) * flat * land * (elev > 30) * stripped
    mafic = np.isin(top, (1, _FLOOD)) | (exposed & np.isin(rock, (0, 1))) | (orogen & (lf == 3) & exposed)
    R["laterite_ni"] = tro * mafic * 0.85
    R["bauxite"] = 0.8 * tro * (1.0 - 0.6 * np.isin(top, (_LIMESTONE, _DOLOMITE, _EVAPORITE))) * np.where(elev > 150, 1.0, 0.6)
    # sediment-hosted Pb-Zn-Cu: carbonate or red-bed strata in rifts and orogen forelands
    carb = np.isin(top, (_LIMESTONE, _DOLOMITE)) | np.isin(nxt, (_LIMESTONE, _DOLOMITE))
    foreland = _dilate(grid, (lf == 3) & land, 3) & (lf != 3)
    R["sed_pbzn"] = (carb * np.maximum(foreland * 0.7, (rift > 0.1) * 0.6)
                     + (np.isin(top, (_SANDSTONE,)) & (rift > 0.15) & np.isin(nxt, (_EVAPORITE, _SHALE))) * 0.5).clip(0, 0.9) * cont
    # rare earths: carbonatites where a rift or plume taps an old, thick continent
    R["ree"] = ((craton | (age > 1000)) * np.maximum(sat(plume_myr, 25), sat(rift_myr, 25) * 0.8) * (cover < 1.0) * 0.7) * cont
    # diamonds: kimberlites need a craton root (>= ~2.5 Gyr, thick) tapped by a plume or rift
    root = craton * ramp(age, 2000, 2800) * ramp(thick_max, 34, 42)
    pipes = root * np.maximum(sat(plume_myr, 20), 0.5 * sat(rift_myr, 20)) * (cover < 1.0)
    # metamorphic gems: deep collision roots (>= ~55 km crust) brought up (now thinner, exposed)
    exhumed = ramp(thick_max - thick, 5, 20)
    R["gem_meta"] = orogen * exposed * ramp(thick_max, 50, 62) * np.maximum(exhumed, 0.3) * 0.9
    # energy and salt from the column
    if col is not None:
        ck, cs, oilk, gask, cmax = col["column_km"], col["column_shallow"], col["column_oil"], col["column_gas"], col["column_maxburial"]
        coal_shallow, coal_deep_gas = cs[:, COALY], gask[:, COALY]
        src_oil, src_gas = oilk[:, SOURCE], gask[:, SOURCE]
        evap_km = ck[:, EVAP]
        coal_maxb = cmax[:, COALY]
    else:  # the exposed strata only
        coal_shallow = np.where(top == _COAL, top_km, 0.0) + np.where(nxt == _COAL, 0.2, 0.0)
        coal_deep_gas = np.zeros(n)
        src_oil = np.where((cover > 2) & (cover < 8) & ((top == _SHALE) | (nxt == _SHALE)), 0.5, 0.0)
        src_gas = np.where(cover > 5, 0.4, 0.0)
        evap_km = np.where(top == _EVAPORITE, top_km, 0.0) + np.where(nxt == _EVAPORITE, 0.3, 0.0)
        coal_maxb = np.where(coal_shallow > 0, 1.5, 0.0)
    coal_top = np.where(top == _COAL, np.maximum(top_km, 0.1), 0.0)  # the record's own coal at the surface
    R["coal"] = sat(np.maximum(coal_shallow, coal_top), 0.15) * cont
    # traps: folds (anticlines), rifts (tilted blocks), salt (domes and seals), deltas' growth faults
    trap = np.clip(0.35 + 0.35 * ((lf == 3) | foreland) + 0.3 * (rift > 0.1) + 0.3 * sat(evap_km, 0.3), 0, 1)
    R["oil"] = sat(src_oil, 0.3) * trap * np.where(cover > 1.5, 1.0, 0.3)
    R["gas"] = np.maximum(sat(src_gas, 0.3), sat(coal_deep_gas, 0.3) * 0.8) * trap * np.where(cover > 2.5, 1.0, 0.3)
    salt_pan = (g("lake_kind") == 3) * 0.9 + (g("lake_kind") == 2) * 0.4
    R["salt"] = np.maximum(0.9 * sat(evap_km, 0.5) * (cover < 6.0), salt_pan)
    # placers: what eroding sources shed, carried down rivers, dropped where they slow (low ground)
    down = np.asarray(L.get("downstream", np.full(n, -1)), int)
    flow = g("flow")
    slow = land & (elev < 600)
    au_src = np.maximum.reduce([R["orogenic_au"], R["epithermal_au"], 0.6 * R["porphyry_cu"]]) * land * (elev > 300)
    for key, src, s in (("placer_au", au_src, 0.8), ("placer_sn", R["sn_w"] * land * (elev > 200), 0.8)):
        carried = _flow_accumulate(down, flow, src, 0.7)
        R[key] = sat(carried - src, s) * slow * (flow > np.percentile(flow[land], 60) if land.any() else 0) * 0.85
    diamond_src = pipes * land
    carried_d = _flow_accumulate(down, flow, diamond_src, 0.8) - diamond_src
    R["diamond"] = np.maximum(pipes * 0.85, sat(carried_d, 1.0) * slow * 0.6)
    # stone-group: obsidian (young volcanic glass), flint, clay
    vol = meta.get("volcanoes") or []
    cols = meta.get("volcano_columns") or []
    obs = np.zeros(n)
    if vol and "lat" in cols and "age" in cols:
        v = np.asarray(vol, float)
        ages = v[:, cols.index("age")]
        ok = ages <= 2.0
        if ok.any():
            from .geo import xyz
            cell = grid.locate(xyz(np.radians(v[ok, cols.index("lat")]), np.radians(v[ok, cols.index("lon")])))
            m = np.zeros(n, bool)
            m[cell] = True
            obs = np.where(m, 0.7, 0.0) * land
    R["obsidian"] = np.maximum(obs, ((lf == 11) & (lfa <= 3)) * 0.4 + ((lf == 4) & (lfa <= 10)) * 0.3) * land
    R["flint"] = (np.isin(top, (_LIMESTONE,)) * 0.7 + np.isin(top, (_DOLOMITE,)) * 0.4
                  + (orogen & (lf == 3)) * 0.25) * land
    flood_plain = land & (flow > np.percentile(flow[land], 80) if land.any() else False) & (elev < 300)
    R["clay"] = np.clip(np.isin(top, (_SHALE,)) * 0.5 + flood_plain * 0.5 + granite * sat(tropic, 10) * 0.7
                        + (g("soil_texture") == 4) * 0.4, 0, 1) * land
    # FANTASY exotics: clearly not geology, but tied to plausible settings
    R["x_mithril"] = craton * ramp(age, 3000, 3500) * sat(plume_myr, 40) * ramp(thick_max, 38, 45) * 0.9
    R["x_adamant"] = 0.8 * orogen * ramp(thick_max, 66, 76) * exhumed * exposed
    R["x_star_iron"] = _impacts(grid, int(meta.get("seed", 0)), np.where(cont, age, g("crust_age")), land)
    for k in R:
        R[k] = np.clip(np.nan_to_num(np.asarray(R[k], float)), 0.0, 1.0)
    return R


def _relief(grid, elev):
    """m to the highest neighbour above each cell (vegetation.relief's idea, local)."""
    e = np.asarray(grid.edges)
    d = np.abs(elev[e[:, 0]] - elev[e[:, 1]])
    out = np.zeros(grid.n)
    np.maximum.at(out, e[:, 0], d)
    np.maximum.at(out, e[:, 1], d)
    return out


def stone_class(L: dict) -> np.ndarray:
    """The best building stone exposed (STONE ids)."""
    n = len(L["elevation"])
    land = world_land(L)
    top = np.asarray(L.get("strata_top", L.get("surface_rock", np.zeros(n))), int)
    rock = np.asarray(L.get("rock", np.zeros(n)), int)
    cover = np.asarray(L.get("sediment_cover", np.zeros(n)), float)
    lf = np.asarray(L.get("landform", np.zeros(n)), int)
    dip = np.asarray(L.get("strata_dip", np.zeros(n)), float)
    lut = np.zeros(16, np.int64)
    for r, s in {_GRANITE: 1, _LIMESTONE: 3, _DOLOMITE: 3, _SANDSTONE: 4, _FLOOD: 6, 1: 6, _TUFF: 7, _QUARTZITE: 9,
                 2: 1, 5: 1, 4: 8}.items():
        lut[r] = s
    out = lut[np.clip(top, 0, 15)]
    bare = (cover < 0.05) & np.isin(rock, (2, 5, 4))  # basement at the surface
    out[bare] = lut[rock[bare]]
    # folded limestone in a collision belt is marble; folded shale is slate
    out[(lf == 3) & np.isin(top, (_LIMESTONE, _DOLOMITE)) & (dip > 20)] = 2
    out[(lf == 3) & (top == _SHALE)] = 5
    soil = np.asarray(L.get("soil_depth", np.zeros(n)), float)
    out[(top == _SHALE) & (lf != 3)] = 0
    out[~land | (soil > 3.0)] = 0
    return out


def world_layers(grid, L: dict, meta: dict | None = None, hist: dict | None = None) -> dict:
    """The resource layers to store with a world: res_<key> (0..1 to 0.01), the dominant class, the best stone,
    coal rank and the dominant resource's typical depth (m)."""
    R = likelihoods(grid, L, meta, hist)
    out = {f"res_{k}": np.round(R[k], 2) for k in KEYS}
    stack = np.stack([R[k] for k in DOMINANT])
    best = stack.argmax(0)
    ids = np.array([KEYS.index(k) + 1 for k in DOMINANT])
    out["resource"] = np.where(stack.max(0) >= DOMINANT_MIN, ids[best], 0)
    out["stone"] = stone_class(L)
    # coal rank from the deepest burial (lignite < ~1.5 km, bituminous to ~5, anthracite beyond or folded)
    if hist is not None:
        mb = hist["column_maxburial"][:, COALY]
    else:
        mb = np.full(grid.n, 1.0)
    lf = np.asarray(L.get("landform", np.zeros(grid.n)), int)
    rank = np.where(mb < 1.5, 1, np.where(mb < 5.0, 2, 3))
    rank = np.where((lf == 3) & (rank == 2), 3, rank)
    out["coal_rank"] = np.where(R["coal"] >= 0.2, rank, 0)
    # typical depth of the dominant resource: placers, laterites, salt pans, obsidian at the surface; the column's
    # depth for coal/oil/gas/salt beds; hard-rock deposits within the first few hundred m
    depth = np.full(grid.n, 200.0)
    key_of = np.array([""] + list(KEYS))[out["resource"]]
    surf = np.isin(key_of, ("placer_au", "placer_sn", "laterite_ni", "bauxite"))
    depth[surf] = 5.0
    if hist is not None:
        dep = hist["column_depth"]
        depth = np.where(key_of == "coal", 1000 * dep[:, COALY], depth)
        depth = np.where(np.isin(key_of, ("oil", "gas")), 1000 * dep[:, SOURCE] * 0.8, depth)
        depth = np.where(key_of == "salt", 1000 * dep[:, EVAP], depth)
    else:
        cover = np.asarray(L.get("sediment_cover", np.zeros(grid.n)), float)
        depth = np.where(np.isin(key_of, ("oil", "gas")), 1000 * cover * 0.6, depth)
    out["res_depth"] = np.round(np.clip(np.where(out["resource"] > 0, depth, 0), 0, 9000) / 10) * 10
    return out


# ---------------------------------------------------------------------------
# Summary: deposit districts per landmass
# ---------------------------------------------------------------------------
DISTRICT_MIN = 0.5  # cells at or above this likelihood make a district


def deposits(grid, L: dict, per_landmass: int = 6, landmasses: int = 6) -> dict:
    """{'districts': [...], 'by_landmass': {name: [top districts]}, 'land_pct': {key: % of land >= 0.5}}.
    A district is a connected patch of cells at >= DISTRICT_MIN; its score is the sum of likelihoods (cells)."""
    from .geo import latlon
    from .world import landmasses as lms
    land = world_land(L)
    masses = lms(grid, land)[:landmasses]
    owner = np.full(grid.n, "", dtype=object)
    for m in masses:
        owner[m["_members"]] = m["name"]
    out = {"land_pct": {}, "by_landmass": {m["name"]: [] for m in masses}, "sea": []}
    nl = max(int(land.sum()), 1)
    for k, name, grp, _, _ in RESOURCES:
        if f"res_{k}" not in L:
            continue
        v = np.asarray(L[f"res_{k}"], float)
        hi = v >= DISTRICT_MIN
        out["land_pct"][k] = round(100 * float((hi & land).sum()) / nl, 2)
        if not hi.any():
            continue
        lab, nc = grid.components(hi)
        score = np.bincount(lab[lab >= 0], weights=v[lab >= 0], minlength=nc)
        for c in np.argsort(-score)[:12]:
            cells = np.flatnonzero(lab == c)
            peak = cells[np.argmax(v[cells])]
            lat, lon = latlon(grid.centers[cells].mean(0) / np.linalg.norm(grid.centers[cells].mean(0)))
            d = {"resource": k, "name": name, "fantasy": grp == "fantasy", "cells": len(cells),
                 "score": round(float(score[c]), 1), "peak": round(float(v[peak]), 2),
                 "lat": round(float(lat), 1), "lon": round(float(lon), 1)}
            where = owner[cells[land[cells]]] if land[cells].any() else []
            if len(where):
                u, cnt = np.unique(where, return_counts=True)
                lm = u[np.argmax(cnt)]
                if lm in out["by_landmass"]:
                    out["by_landmass"][lm].append(d)
            elif grp != "fantasy":
                out["sea"].append(d)
    for lm in out["by_landmass"]:
        ds = sorted(out["by_landmass"][lm], key=lambda d: -d["score"] * _VALUE.get(d["resource"], 1.0))
        real, seen = [], {}
        for d in ds:  # (at most two districts of one resource per landmass)
            if not d["fantasy"] and seen.get(d["resource"], 0) < 2 and len(real) < per_landmass:
                real.append(d)
                seen[d["resource"]] = seen.get(d["resource"], 0) + 1
        fan = [d for d in ds if d["fantasy"]][:2]
        out["by_landmass"][lm] = real + fan
    out["sea"] = sorted(out["sea"], key=lambda d: -d["score"])[:5]
    return out


# how much a district counts in the per-landmass ranking (games care about gold more than clay)
_VALUE = {"porphyry_cu": 1.5, "epithermal_au": 1.6, "orogenic_au": 1.6, "placer_au": 1.4, "diamond": 2.0,
          "gem_meta": 1.6, "oil": 1.5, "gas": 1.0, "coal": 1.2, "bif_fe": 1.3, "vms": 1.3, "magmatic_ni": 1.3,
          "sn_w": 1.1, "bauxite": 1.0, "laterite_ni": 1.0, "sed_pbzn": 1.1, "ree": 1.2, "salt": 0.8,
          "placer_sn": 0.9, "obsidian": 0.5, "flint": 0.4, "clay": 0.3}


def text_section(summary: dict) -> str:
    """The world .txt's '## Resources' section from deposits()."""
    out = ["## Resources (resources.py, PW-155: coarse likelihoods; districts = connected cells >= 0.5)"]
    for lm, ds in summary["by_landmass"].items():
        if not ds:
            out.append(f"- landmass {lm}: nothing above 0.5")
            continue
        out.append(f"- landmass {lm}: " + "; ".join(
            f"{d['name']} ({d['cells']} cells, peak {d['peak']:.2f}, at {d['lat']:g}, {d['lon']:g})" for d in ds))
    if summary.get("sea"):
        out.append("- at sea: " + "; ".join(f"{d['name']} ({d['cells']} cells at {d['lat']:g}, {d['lon']:g})"
                                           for d in summary["sea"]))
    lp = summary["land_pct"]
    out.append("- % of land >= 0.5: " + ", ".join(f"{k} {v:g}" for k, v in lp.items() if v > 0))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# A saved world, in place
# ---------------------------------------------------------------------------
def add_to_world(ref: str, use_history: bool = True, log=print) -> Path:
    """(Re)makes a saved world's resource layers in place (`planet resources <world>`), with the run's history
    when the world came from a run that is still stored."""
    from . import store as S
    from . import world as W
    path = S.find_world(ref)
    w = W.load(path)
    m = w["meta"]
    hist = None
    if use_history and m.get("source_run") and S.exists("run", m["source_run"]):
        hist = history(S.find_run(m["source_run"]), float(m["t_myr"]), w["grid"], log=log)
    w["layers"].update(world_layers(w["grid"], w["layers"], m, hist))
    m["resources"] = {"history": hist is not None, "keyframes": hist["frames"] if hist else 0,
                      "created": time.strftime("%Y-%m-%d %H:%M:%S")}
    return W.save(w, w["name"], path.stem)
