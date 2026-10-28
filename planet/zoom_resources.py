"""Resources stage 2 (PW-610; design: docs/proposals/resources.md section 6).

Sites concrete deposits in a saved regional zoom from the world's coarse
resource likelihoods (resources.likelihoods, stage 1): points (hard-rock
deposits, laterites, kimberlite fields), seams (coal measures where the
zoom's terrain cuts the buried bed), placers (on the zoom's own rivers,
downstream of the gold and tin it eroded), salt beds and pans, oil and gas
fields. Labels only, after the zoom is built (~1-3 s plus the world's history
pass); the zoom's layers are not touched, its zoom.json gains `resources`.

Consistency with the world map: a world cell's likelihood p is read as "the
chance a notable (medium or larger) deposit of this kind lies in the cell".
Deposits are a Poisson draw whose expected number of notable ones in the cell
is -ln(1 - p) (so P(at least one) = p); small ones come on top
(NOTABLE_SHARE). Inside a cell the draw goes to the pixels whose own ground
fits the model (suitability, normalised over the cell's pixels: it moves
deposits within a cell, never changes a cell's count). So a district on the
world map (cells >= 0.5) shows up as deposits in the zoom. Deterministic per
zoom (its id and seed) and resource.

    site(world, meta, lay, R, hist)   -> {'deposits': [...], 'belts': [...], 'summary': {...}}
    add_to_zoom(ref)                  -> (re)makes a saved zoom's deposits in place (`planet resources zoom:<id>`)
"""

from __future__ import annotations

import json
import time
import zlib
from pathlib import Path

import numpy as np
from numba import njit

from . import resources as RS
from .geo import R_KM, latlon

SIZES = ("small", "medium", "large", "giant")
SIZE_P = np.array([0.70, 0.22, 0.07, 0.01])  # share of deposits by size class
NOTABLE_SHARE = float(SIZE_P[1:].sum())  # medium or larger: what a world likelihood speaks of
P_MAX = 0.98  # likelihoods are capped here before -ln(1 - p)
RIVER_Q = 3.0  # m^3/s: a placer needs a river at least this big
MAX_PER_KEY = 400  # at most this many deposits of one resource per zoom (the biggest kept; counts in the summary)

# per model: (form, grade median, grade log-sigma, grade unit and what, tonnage medians by size class, its unit,
#             depth range m (lo, hi) of the top of the ore where the host is exposed)
MODELS = {
    "porphyry_cu": ("point", 0.45, 0.35, "% Cu", (20, 200, 1000, 5000), "Mt ore", (0, 600)),
    "epithermal_au": ("point", 4.0, 0.8, "g/t Au", (0.3, 3, 15, 60), "Mt ore", (0, 300)),
    "vms": ("point", 6.0, 0.5, "% Cu+Zn", (1, 5, 30, 150), "Mt ore", (0, 800)),
    "orogenic_au": ("point", 5.0, 0.7, "g/t Au", (0.2, 2, 10, 50), "Mt ore", (0, 1200)),
    "sn_w": ("point", 0.6, 0.6, "% Sn+W", (0.5, 5, 30, 150), "Mt ore", (0, 500)),
    "bif_fe": ("point", 55.0, 0.1, "% Fe", (50, 300, 1500, 8000), "Mt ore", (0, 200)),
    "iron_ore": ("point", 45.0, 0.15, "% Fe", (0.01, 0.1, 1, 10), "Mt ore", (0, 10)),
    "magmatic_ni": ("point", 1.2, 0.5, "% Ni", (2, 20, 150, 1000), "Mt ore", (50, 1500)),
    "laterite_ni": ("laterite", 1.3, 0.25, "% Ni", (5, 30, 150, 600), "Mt ore", (0, 30)),
    "bauxite": ("laterite", 45.0, 0.12, "% Al2O3", (5, 50, 300, 1500), "Mt ore", (0, 15)),
    "sed_pbzn": ("point", 7.0, 0.5, "% Pb+Zn", (2, 15, 80, 400), "Mt ore", (50, 1000)),
    "ree": ("point", 2.5, 0.6, "% rare-earth oxides", (1, 10, 80, 800), "Mt ore", (0, 300)),
    "placer_au": ("placer", 0.4, 0.8, "g/m^3 Au", (1, 10, 60, 300), "Mm^3 gravel", (0, 20)),
    "placer_sn": ("placer", 300.0, 0.6, "g/m^3 cassiterite", (1, 10, 60, 300), "Mm^3 sand", (0, 20)),
    "diamond": ("pipes", 0.4, 0.9, "ct/t", (5, 30, 150, 600), "Mt kimberlite", (0, 100)),
    "gem_meta": ("point", 2.0, 1.0, "g/t gem rough", (0.05, 0.5, 3, 20), "Mt host rock", (0, 50)),
    "coal": ("seam", 2.0, 0.5, "m seam", (5, 50, 500, 3000), "Mt coal", (0, 0)),
    "oil": ("field", None, 0, "", (10, 100, 1000, 10000), "million bbl", (0, 0)),
    "gas": ("field", None, 0, "", (0.05, 0.5, 5, 50), "trillion ft^3", (0, 0)),
    "salt": ("bed", 60.0, 0.8, "m bed", (10, 100, 1000, 10000), "Mt salt", (0, 0)),
    "obsidian": ("point", None, 0, "", (0.01, 0.1, 1, 5), "km^2 of glass", (0, 5)),
    "x_mithril": ("point", 30.0, 1.0, "g/t deep-silver", (0.01, 0.1, 0.5, 2), "Mt ore", (1000, 3000)),
    "x_adamant": ("point", 5.0, 1.0, "g/t adamant", (0.01, 0.1, 0.5, 2), "Mt ore", (200, 1500)),
    "x_star_iron": ("point", 80.0, 0.1, "% Fe-Ni", (0.01, 0.1, 1, 5), "Mt meteoric iron", (0, 50)),
}
# (flint and clay are near-ubiquitous: the world's stone map says where; no sites)
KEYS = tuple(k for k in RS.KEYS if k in MODELS)
FORM_NOTE = {
    "point": "a hard-rock deposit", "laterite": "a weathering blanket on flat, well-drained ground",
    "placer": "river or beach gravels where the current slows", "pipes": "a kimberlite field (clustered pipes)",
    "seam": "coal seams in the coal measures", "field": "a field in a trap", "bed": "salt beds or a salt pan",
}


# ---------------------------------------------------------------------------
# Small raster helpers
# ---------------------------------------------------------------------------
def _box(a, r):
    """Box mean of a (ny, nx) over (2r+1)^2, edges clamped (separable cumulative sums)."""
    if r <= 0:
        return a.astype(float)
    out = a.astype(float)
    for ax in (0, 1):
        p = np.pad(out, [(r, r) if k == ax else (0, 0) for k in (0, 1)], mode="edge")
        c = np.cumsum(p, axis=ax)
        c = np.concatenate([np.zeros_like(np.take(c, [0], axis=ax)), c], axis=ax)
        n = out.shape[ax]
        out = (np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=ax) - np.take(c, np.arange(n), axis=ax)) / (2 * r + 1)
    return out


def _receivers(slots, nx, ny):
    """Flat receiver index per pixel from the zoom's D8 slots (-1: none)."""
    s = slots.astype(np.int64).ravel()
    v = np.where(s < 4, s, s + 1)
    dr, dc = v // 3 - 1, v % 3 - 1
    r, c = np.divmod(np.arange(nx * ny), nx)
    rr, cc = r + dr, c + dc
    ok = (s != 255) & (rr >= 0) & (rr < ny) & (cc >= 0) & (cc < nx)
    return np.where(ok, rr * nx + cc, -1)


@njit(cache=True)
def _carry(order, rec, src, keep):
    """Load carried downstream (pixels upstream first): each passes keep x (its own + what reached it) on."""
    load = src.copy()
    for i in order:
        d = rec[i]
        if d >= 0:
            load[d] += keep[i] * load[i]
    return load


def _near(points_rc, nx, ny, radius_px):
    """0..1 per pixel: 1 at each point, falling linearly to 0 at radius_px."""
    out = np.zeros((ny, nx))
    if not len(points_rc):
        return out
    rr, cc = np.mgrid[0:ny, 0:nx]
    for r, c in points_rc:
        r0, r1 = int(max(r - radius_px, 0)), int(min(r + radius_px + 1, ny))
        c0, c1 = int(max(c - radius_px, 0)), int(min(c + radius_px + 1, nx))
        if r0 >= r1 or c0 >= c1:
            continue
        d = np.hypot(rr[r0:r1, c0:c1] - r, cc[r0:r1, c0:c1] - c)
        out[r0:r1, c0:c1] = np.maximum(out[r0:r1, c0:c1], np.clip(1 - d / radius_px, 0, 1))
    return out


# ---------------------------------------------------------------------------
# Siting
# ---------------------------------------------------------------------------
def _seed(meta, key):
    return [int(zlib.crc32(f"{meta['id']}|{meta.get('seed', 1)}|{key}".encode())), 0x5172]


def _inherit(pmeta: dict, pres: dict, meta: dict, river: np.ndarray) -> list[dict]:
    """A fine zoom's deposits (PW-618): its parent's that lie inside it, the same deposits (name, size, grade) at
    this zoom's pixels. A placer moves to the nearest river pixel within a few parent pixels (the fine zoom's
    river runs a little differently), a kimberlite field's pipes follow."""
    from .geo import xyz
    from .zoom import Frame
    nx, ny, res = int(meta["nx"]), int(meta["ny"]), float(meta["res_km"])
    fr = Frame(meta["center"]["lat"], meta["center"]["lon"])
    pfr = Frame(pmeta["center"]["lat"], pmeta["center"]["lon"])
    pnx, pny, pres_km = int(pmeta["nx"]), int(pmeta["ny"]), float(pmeta["res_km"])

    def to_px(rows_cols):
        rc = np.asarray(rows_cols, float).reshape(-1, 2)
        x, y = (rc[:, 1] - pnx / 2) * pres_km, (pny / 2 - rc[:, 0]) * pres_km
        fx, fy = fr.to_plane(pfr.to_sphere(x, y))
        return ny / 2 - fy / res, fx / res + nx / 2

    rr, cc = np.nonzero(river)
    out = []
    for d in pres.get("deposits", []):
        (r,), (c,) = to_px(d["px"])
        if not (0 <= r < ny and 0 <= c < nx):
            continue
        d = dict(d)
        if d["form"] == "placer" and len(rr) and not river[int(r), int(c)]:
            j = int(np.argmin((rr - r) ** 2 + (cc - c) ** 2))
            if np.hypot(rr[j] - r, cc[j] - c) * res <= 4 * pres_km:
                r, c = rr[j] + 0.5, cc[j] + 0.5
        d["px"] = [round(float(r), 2), round(float(c), 2)]
        if d.get("pipes_px"):
            pr, pc = to_px(d["pipes_px"])
            ok = (pr >= 0) & (pr < ny) & (pc >= 0) & (pc < nx)
            d["pipes_px"] = [[round(float(a), 1), round(float(b), 1)] for a, b in zip(pr[ok], pc[ok])]
        out.append(d)
    return out


def site(world: dict, meta: dict, lay: dict, R: dict, hist: dict | None = None, log=None,
         inherit: tuple[dict, dict] | None = None) -> dict:
    """Deposits for a zoom (meta, decoded layers lay (ny, nx)) from the world's likelihoods R ({key: per cell})
    and the run's history (the coal and salt beds' depth; None: the world's strata only). inherit: (parent zoom's
    meta, its `resources`) for a fine zoom (PW-618): it keeps its parent's deposits that lie inside it (_inherit)
    and re-sites only what depends on its own ground (the coal outcrop belts)."""
    from . import zoom_kernels as ZK
    from .zoom import Frame
    t0 = time.time()
    g, L = world["grid"], world["layers"]
    nx, ny, res = int(meta["nx"]), int(meta["ny"]), float(meta["res_km"])
    fr = Frame(meta["center"]["lat"], meta["center"]["lon"])
    xs = (np.arange(nx) + 0.5 - nx / 2) * res
    ys = (ny / 2 - np.arange(ny) - 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    P = fr.to_sphere(X.ravel(), Y.ravel())
    own = g.locate(P)
    sp = float(meta.get("params", {}).get("coarse_spacing_km") or np.sqrt(4 * np.pi * R_KM ** 2 / g.n))
    size_km = float(meta["size_km"])
    ang = np.arccos(np.clip(g.centers @ fr.c, -1, 1)) * R_KM
    sel = np.flatnonzero(ang < size_km * 0.7072 + 4 * sp)
    cx, cy = fr.to_plane(g.centers[sel])
    cell_area = 4 * np.pi * R_KM ** 2 / g.n
    px_area = res * res

    # the world's fields on the pixels: likelihoods (Gaussian-weighted, as the zoom interpolates its world)
    fields = {k: np.asarray(R[k], float)[sel] for k in KEYS}
    au_src_c = np.maximum.reduce([R["orogenic_au"], R["epithermal_au"], 0.6 * R["porphyry_cu"]])[sel]
    cols = [fields[k] for k in KEYS] + [au_src_c, np.asarray(R["sn_w"], float)[sel]]
    # the coal and salt beds: depth to the top and thickness (km), from the history's column
    if hist is not None:
        th_coal = hist["column_shallow"][:, RS.COALY][sel]
        top_coal = np.maximum(hist["column_depth"][:, RS.COALY][sel] - th_coal / 2, 0.0)
        th_evap = hist["column_km"][:, RS.EVAP][sel]
        top_evap = np.maximum(hist["column_depth"][:, RS.EVAP][sel] - th_evap / 2, 0.0)
        src_dep = hist["column_depth"][:, RS.SOURCE][sel]
        mb = hist["column_maxburial"][:, RS.COALY][sel]
    else:
        top = np.asarray(L.get("strata_top", np.zeros(g.n)), int)[sel]
        tk = np.asarray(L.get("strata_top_km", np.zeros(g.n)), float)[sel]
        cov = np.asarray(L.get("sediment_cover", np.zeros(g.n)), float)[sel]
        th_coal, top_coal = np.where(top == RS._COAL, np.maximum(tk, 0.1), 0.2), np.where(top == RS._COAL, 0.0, 0.3)
        th_evap, top_evap = np.where(top == RS._EVAPORITE, tk, 0.2), np.where(top == RS._EVAPORITE, 0.0, 1.0)
        src_dep, mb = cov * 0.6, np.full(len(sel), 1.0)
    cols += [th_coal, top_coal, th_evap, top_evap, src_dep, mb]
    vals = np.column_stack(cols)
    fine, _ = ZK.gauss_interp(X.ravel(), Y.ravel(), cx, cy, vals, np.ones_like(vals), 0.5 * sp)
    fine = np.nan_to_num(fine)
    lik = {k: fine[:, j].reshape(ny, nx) for j, k in enumerate(KEYS)}
    j0 = len(KEYS)
    au_src, sn_src = fine[:, j0].reshape(ny, nx), fine[:, j0 + 1].reshape(ny, nx)
    th_coal, top_coal, th_evap, top_evap, src_dep, coal_mb = (fine[:, j0 + 2 + q].reshape(ny, nx) for q in range(6))

    # the zoom's own ground
    h = lay["elevation"].astype(float)
    water = lay["water"].astype(int)
    land = water == 0
    sea = water == 1
    rock = lay["rock"].astype(int)
    surf = lay["surface_rock"].astype(int)
    lf = lay.get("landform", np.zeros((ny, nx))).astype(int)
    q = lay["discharge"].astype(float)
    area = lay["drainage_area"].astype(float)
    gy, gx = np.gradient(h, res * 1000.0)
    slope = np.hypot(gx, gy)
    r_cell = max(int(round(0.5 * sp / res)), 1)
    h_s = _box(h, r_cell)  # (~a coarse cell's mean ground)
    hp = h - _box(h, max(int(round(8 / res)), 1))  # ridges (> 0) and valleys (< 0) at ~10-20 km
    sedimentary = np.isin(surf, (3, 6, 7, 8, 9, 10, 14))
    basement = ~sedimentary
    volc = meta.get("stats", {}).get("volcanoes") or []
    v_rc = [(ny / 2 - v["y_km"] / res, v["x_km"] / res + nx / 2) for v in volc]
    v_young = [(ny / 2 - v["y_km"] / res, v["x_km"] / res + nx / 2) for v in volc
               if v.get("status") == "active" or (v.get("age_myr") or 99) <= 2]
    near_v = _near(v_rc, nx, ny, 25 / res)
    near_young = _near(v_young, nx, ny, 10 / res)
    flat = np.clip((0.03 - slope) / 0.025, 0, 1)
    # well drained: the zoom's soils' drainage class (soils.DRAINAGE: 1 excessive, 2 well, ... 5 very poor)
    sd = lay.get("soil_drainage")
    drained = (np.array([0.0, 1.0, 1.0, 0.6, 0.15, 0.05])[np.clip(sd.astype(int), 0, 5)] if sd is not None
               else np.clip(hp / 30 + 0.5, 0, 1))
    soil = lay.get("soil_depth", np.zeros((ny, nx))).astype(float)

    # the coal and salt beds' surfaces: flat-lying at the cell's depth below its mean ground; in fold belts they
    # fold with the ridges the zoom drew (anticlines under its ridges)
    fold = (lf == 3).astype(float)
    fold = _box(fold, 2)
    z_coal_top = h_s - 1000 * top_coal + fold * 1.5 * hp
    z_coal_bot = z_coal_top - 1000 * np.maximum(th_coal, 0.03)
    coal_depth = h - z_coal_top  # m of ground over the bed's top (< 0: the bed rises above the ground: eroded)
    coal_out = land & (h <= z_coal_top) & (h >= z_coal_bot) & (lik["coal"] >= 0.15)
    z_evap_top = h_s - 1000 * top_evap + fold * 1.5 * hp
    evap_depth = h - z_evap_top
    lake_kind = lay.get("lake_kind", np.zeros((ny, nx))).astype(int)
    pan = (lake_kind == 3) | ((lake_kind == 2) & (water == 2))

    # placers: what the zoom's rivers carry from the eroding gold and tin ground upstream, dropped where they slow
    rec = _receivers(lay["receiver"], nx, ny)
    order = np.argsort(area.ravel(), kind="stable").astype(np.int64)
    keep = np.full(nx * ny, 0.985 ** res)  # (~1.5% of the load left behind per km)
    river = land & (q >= RIVER_Q)
    erode = np.clip(slope / 0.05, 0, 1) * land
    vf = lay.get("valley_floor")
    slows = np.clip((0.01 - slope) / 0.008, 0, 1)  # (a gentle reach: < ~0.2-1 %)
    # (the gradient drops: steeper above than here; an alluvial floor where the fine zoom drew one)
    up_steep = np.zeros(nx * ny)
    np.maximum.at(up_steep, np.maximum(rec, 0), np.where(rec >= 0, slope.ravel(), 0.0))
    drop = np.clip(up_steep.reshape(ny, nx) / np.maximum(slope, 1e-4) / 3.0, 0, 1)
    trap = river * np.maximum(slows, drop * 0.7)
    if vf is not None:
        trap = np.maximum(trap, river * (vf > 0) * 0.8)
    coast = land & (_box(sea.astype(float), 1) > 0)
    wave = _box(np.asarray(lay.get("wave_power", np.zeros((ny, nx))), float), 2) * 25 / 9
    beach = coast & (wave > 5.0)
    loads = {}
    for key, src in (("placer_au", au_src), ("placer_sn", sn_src)):
        s = (src * erode).ravel()
        ld = _carry(order, rec, s, keep).reshape(ny, nx) - src * erode
        loads[key] = ld / max(float(np.percentile(ld[river], 95)) if river.any() else 1.0, 1e-9)

    # suitability per model (0..1 with a floor: any ground can host a deposit, the right ground is likelier)
    S = {
        "porphyry_cu": np.where(rock == 2, 1.0, np.where(np.isin(surf, (11, 15, 2)), 0.8, 0.12)) * (1 + 1.5 * near_v)
                       * np.where(sedimentary, 0.4, 1.0),
        "epithermal_au": (np.where(np.isin(surf, (15, 2)), 1.0, np.where(rock == 2, 0.7, np.where(lf == 4, 0.6, 0.1)))
                          * (1 + 2.0 * near_v)),
        "vms": np.where(np.isin(rock, (2, 4)), 1.0, np.where(sea, 0.8, 0.08)) * np.where(sedimentary & land, 0.5, 1.0),
        "orogenic_au": np.where((lf == 3) | (rock == 4) | (rock == 5), 0.6, 0.08) * (1 + (hp > 0)) * basement,
        "sn_w": np.where((surf == 11) | (rock == 11), 1.0, np.where(rock == 4, 0.35, 0.04)),
        "bif_fe": np.where((rock == 5) & basement, 1.0, np.where(rock == 5, 0.2, 0.03)),
        "iron_ore": np.where(sedimentary, 0.8, 0.4) * np.maximum(flat, 0.3),
        "magmatic_ni": np.where(np.isin(surf, (13, 1)), 1.0, np.where(rock == 5, 0.5, 0.15)),
        "laterite_ni": np.where(np.isin(surf, (1, 13, 0)) | np.isin(rock, (0, 1)), 1.0, 0.15) * flat * drained,
        "bauxite": np.where(np.isin(surf, (7, 12, 6, 14, 9)), 0.2, 1.0) * flat * drained * (hp > -20),
        "sed_pbzn": np.where(np.isin(surf, (6, 14)), 1.0, np.where(surf == 7, 0.4, 0.08)),
        "ree": np.where(rock == 5, 0.6, 0.15) * (1 + (lf == 4)),
        "gem_meta": np.where(((rock == 4) | (surf == 12)) & basement, 1.0, 0.08) * (1 + (hp > 0)),
        "obsidian": np.maximum(near_young, np.where(surf == 15, 0.3, 0.02)),
        "diamond": np.where(rock == 5, 1.0, 0.04),
        "x_mithril": np.where(rock == 5, 1.0, 0.02),
        "x_adamant": np.where(rock == 4, 1.0, 0.02) * (1 + (hp > 0)),
        "x_star_iron": np.ones((ny, nx)),
        "placer_au": trap * (0.15 + loads["placer_au"]) + beach * 0.3 * (0.15 + _box(loads["placer_au"], 3)),
        "placer_sn": trap * (0.15 + loads["placer_sn"]) + beach * 0.6 * (0.15 + _box(loads["placer_sn"], 3)),
        "coal": np.where(coal_depth < 0, 0.0, np.clip(1 - coal_depth / 1500, 0, 1)) * (1 + 2 * coal_out),
        "salt": np.maximum(np.where(evap_depth < 0, 0.0, np.clip(1 - evap_depth / 1500, 0, 1)) * (th_evap > 0.02),
                           3.0 * pan),
        # traps: anticline crests in fold belts (under the zoom's ridges), elsewhere any (faults, salt, pinch-outs)
        "oil": np.where(fold > 0.3, np.clip(hp / 60, 0.05, 1), 0.5) * (1 + (th_evap > 0.1)),
        "gas": np.where(fold > 0.3, np.clip(hp / 60, 0.05, 1), 0.5) * (1 + (th_evap > 0.1)),
    }
    onshore = {k for k in KEYS if k not in ("vms", "oil", "gas", "salt", "placer_sn")}
    deposits, counts = [], {}
    inherited = _inherit(inherit[0], inherit[1], meta, river) if inherit else None
    cell_of = np.searchsorted(np.sort(np.unique(own)), own).reshape(ny, nx)
    ncell = int(cell_of.max()) + 1
    for k in KEYS:
        if inherited is not None:
            counts[k] = sum(d["key"] == k for d in inherited)
            continue
        s = np.clip(np.nan_to_num(S[k]), 0, None)
        if MODELS[k][0] not in ("placer", "seam", "bed"):  # (any ground can host one, rarely)
            s = np.maximum(s, 0.01)
        s = s * (land if k in onshore else (land | sea))
        p = np.clip(lik[k], 0, P_MAX)
        lam_cell = -np.log1p(-p) / NOTABLE_SHARE * px_area / cell_area  # per pixel, before the ground moves it
        # the ground's suitability, normalised over each cell's pixels (it moves deposits within a cell)
        m = np.bincount(cell_of.ravel(), s.ravel(), ncell) / np.maximum(np.bincount(cell_of.ravel(), None, ncell), 1)
        lam = lam_cell * np.where(m[cell_of] > 0, s / np.maximum(m[cell_of], 1e-12), 0.0)
        tot = float(lam.sum())
        rng = np.random.default_rng(_seed(meta, k))
        n = int(rng.poisson(tot)) if tot > 0 else 0
        counts[k] = n
        if not n:
            continue
        pick = rng.choice(nx * ny, size=n, p=(lam / tot).ravel())
        sizes = rng.choice(4, size=n, p=SIZE_P)
        for j in np.argsort(-sizes, kind="stable")[:MAX_PER_KEY]:
            i = int(pick[j])
            r, c = divmod(i, nx)
            d = _deposit(k, rng, int(sizes[j]), r + rng.uniform(0.1, 0.9), c + rng.uniform(0.1, 0.9), fr, nx, ny, res,
                         dict(h=h[r, c], surf=surf[r, c], rock=rock[r, c], sedimentary=bool(sedimentary[r, c]),
                              coal_depth=coal_depth[r, c], coal_out=bool(coal_out[r, c]), coal_mb=coal_mb[r, c],
                              lf=lf[r, c], evap_depth=evap_depth[r, c], pan=bool(pan[r, c]), sea=bool(sea[r, c]),
                              src_dep=src_dep[r, c], soil=soil[r, c], river=bool(river[r, c]), q=q[r, c],
                              beach=bool(beach[r, c]), th_evap=th_evap[r, c], p=float(p[r, c])))
            deposits.append(d)
    if inherited is not None:
        deposits = inherited
    # the coal measures at the surface (outcrop belts), as pixels for the map (at most ~6000)
    belts = []
    if coal_out.any():
        idx = np.flatnonzero(coal_out.ravel())
        step = max(1, len(idx) // 6000)
        belts.append({"key": "coal", "what": "coal measures at the surface (outcrop)", "px": idx[::step].tolist(),
                      "step": step, "km2": round(float(coal_out.sum() * px_area))})
    summary = _summary(deposits, counts, lik, own, cell_of, R, sel, g, nx, ny, meta)
    summary["seconds"] = round(time.time() - t0, 1)
    if log:
        log(f"zoom resources: {len(deposits)} deposits sited in {summary['seconds']} s")
    return {"deposits": deposits, "belts": belts, "summary": summary}


def _depth_class(m):
    return "at the surface" if m < 10 else "shallow" if m < 150 else "underground" if m < 1000 else "deep"


def _deposit(k, rng, size, r, c, fr, nx, ny, res, at) -> dict:
    form, g_med, g_sig, g_unit, tons, t_unit, (d_lo, d_hi) = MODELS[k]
    name, grp = next((n, gp) for kk, n, gp, _, _ in RS.RESOURCES if kk == k)
    x, y = (c - nx / 2) * res, (ny / 2 - r) * res
    la, lo = latlon(fr.to_sphere(np.array([x]), np.array([y]))[0])
    tonnage = float(tons[size] * np.exp(rng.normal(0, 0.5)))
    grade = float(g_med * np.exp(rng.normal(0, g_sig))) if g_med is not None else None
    depth = float(np.exp(rng.uniform(np.log(d_lo + 1), np.log(d_hi + 1))) - 1) if d_hi > 0 else 0.0
    host, extra = "", {}
    if form == "point":
        if at["sedimentary"] and k not in ("sed_pbzn", "obsidian", "x_star_iron"):
            depth += float(rng.uniform(100, 600))  # (under the sedimentary cover: found by drilling)
            host = "under sedimentary cover"
        else:
            host = "in exposed basement" if k not in ("sed_pbzn",) else "in carbonate or red-bed strata"
    elif form == "laterite":
        host, extra["blanket_km2"] = "a duricrust blanket on a flat, drained surface", round(tonnage / 15, 1)
    elif form == "placer":
        host = "beach sands" if at["beach"] and not at["river"] else f"river gravels ({at['q']:.0f} m^3/s)"
    elif form == "pipes":
        n = int(rng.integers(5, 31))
        rr = r + rng.normal(0, 5 / res, n)
        cc = c + rng.normal(0, 5 / res, n)
        ok = (rr >= 0) & (rr < ny) & (cc >= 0) & (cc < nx)
        extra["pipes_px"] = [[round(float(a), 1), round(float(b), 1)] for a, b in zip(rr[ok], cc[ok])]
        extra["pipes"] = int(ok.sum())
        extra["diamondiferous"] = max(1, int(round(0.1 * ok.sum())))
        host = f"a field of {int(ok.sum())} kimberlite pipes, {extra['diamondiferous']} rich enough to mine"
    elif form == "seam":
        depth = max(float(at["coal_depth"]), 0.0)
        mb = float(at["coal_mb"])
        rank = "lignite" if mb < 1.5 else "bituminous" if mb < 5.0 else "anthracite"
        if at["lf"] == 3 and rank == "bituminous":
            rank = "anthracite"
        extra["rank"] = rank
        extra["mining"] = "open-cast" if depth < 60 else "drift or shallow shaft" if depth < 300 else "deep shaft"
        extra["seams"] = int(rng.integers(1, 8))
        host = "coal measures at the surface" if at["coal_out"] else f"coal measures {depth:.0f} m down"
    elif form == "bed":
        if at["pan"]:
            depth, host = 0.0, "a salt pan (evaporating closed basin)"
            extra["kind"] = "pan (halite, brines)"
        else:
            depth = max(float(at["evap_depth"]), 0.0)
            dome = at["th_evap"] > 0.5 and rng.random() < 0.4
            host = "a salt dome rising from thick beds" if dome else "evaporite beds"
            extra["kind"] = "dome" if dome else "bedded halite and potash"
            if dome:
                depth *= 0.2
    elif form == "field":
        depth = float(np.clip(1000 * at["src_dep"] * rng.uniform(0.6, 0.95), 500, 6000))
        host = "an anticline crest" if at["lf"] == 3 else "a fault or stratigraphic trap"
        if at["sea"]:
            host += ", offshore"
    d = {"key": k, "name": name, "group": grp, "form": form, "px": [round(r, 2), round(c, 2)],
         "lat": round(float(la), 4), "lon": round(float(lo), 4), "size": SIZES[size],
         "tonnage": round(tonnage, 3 if tonnage < 1 else 1), "tonnage_unit": t_unit,
         "depth_m": round(depth), "depth_class": _depth_class(depth), "host": host,
         "likelihood": round(at["p"], 2)}
    if grade is not None:
        d["grade"] = round(grade, 2 if grade < 10 else 1)
        d["grade_unit"] = g_unit
    d.update(extra)
    return d


def _summary(deposits, counts, lik, own, cell_of, R, sel, g, nx, ny, meta) -> dict:
    """Counts per resource and size, the biggest, and how the world's districts show up (consistency)."""
    by = {}
    for d in deposits:
        e = by.setdefault(d["key"], {"name": d["name"], "group": d["group"], "sited": 0,
                                     **{s: 0 for s in SIZES}})
        e["sited"] += 1
        e[d["size"]] += 1
    for k, e in by.items():
        e["drawn"] = counts.get(k, e["sited"])
    rank = {s: i for i, s in enumerate(SIZES)}
    top = sorted((d for d in deposits if d["group"] != "fantasy"),
                 key=lambda d: (-rank[d["size"]], -RS._VALUE.get(d["key"], 1.0), -d["tonnage"]))[:8]
    # world cells whose pixels make up most of a cell inside the zoom: those at >= 0.5 with a deposit of theirs
    ucells, inv = np.unique(own, return_inverse=True)
    npx = np.bincount(inv)
    full = npx >= 0.5 * np.median(npx)
    cons = {}
    for k in KEYS:
        v = np.asarray(R[k], float)[ucells]
        hi = full & (v >= RS.DISTRICT_MIN)
        if not hi.any():
            continue
        has = np.zeros(len(ucells), bool)
        for d in deposits:
            if d["key"] == k:
                r, c = int(d["px"][0]), int(d["px"][1])
                has[inv[r * nx + c]] = True
        cons[k] = {"district_cells": int(hi.sum()), "with_deposit": int((hi & has).sum())}
    return {"by_resource": by, "biggest": [{k: d[k] for k in ("key", "name", "size", "tonnage", "tonnage_unit",
                                                              "lat", "lon", "depth_m") if k in d} for d in top],
            "districts": cons, "total": len(deposits)}


def text_lines(res: dict) -> list[str]:
    """Plain-text summary lines (the zoom's about panel and the CLI)."""
    s = res["summary"]
    out = [f"{s['total']} deposits sited (resources.py stage 2)"]
    for k, e in sorted(s["by_resource"].items(), key=lambda kv: -kv[1]["sited"]):
        big = ", ".join(f"{e[z]} {z}" for z in SIZES[::-1] if e[z])
        out.append(f"  {e['name']}: {e['sited']} ({big})")
    for d in s["biggest"][:5]:
        out.append(f"  biggest: {d['size']} {d['name']}, {d['tonnage']:g} {d['tonnage_unit']} at {d['lat']}, "
                   f"{d['lon']} ({d['depth_m']} m)")
    for k, c in s["districts"].items():
        out.append(f"  world districts of {k}: {c['with_deposit']} of {c['district_cells']} cells hold a deposit")
    return out


# ---------------------------------------------------------------------------
# A saved zoom, in place
# ---------------------------------------------------------------------------
def add_to_zoom(ref, log=print, world: dict | None = None) -> Path:
    """(Re)makes a saved zoom's deposits in place: zoom.json gets `resources` (deposits, outcrop belts, summary).
    The world's likelihoods are its res_* layers when it has them, else made here (with the run's history when the
    run is stored; the world is not written). world: the loaded world, when the caller has it. Made by every
    zoom build (zoom.zoom, zoom_fine.zoom; PW-618) unless the world has no resource layers."""
    from . import store as S
    from . import world as W
    from . import zoom as Z
    d = S.find_zoom(ref)
    meta, lay = Z.load(d, decode=True)
    sw = meta["source_world"]
    w = world or W.load(S.find_world(sw["id"]))
    m = w["meta"]
    hist = S.read_history(sw["id"])  # (kept beside the world when it was made, PW-609)
    if hist is None and m.get("source_run") and S.exists("run", m["source_run"]):
        hist = RS.history(S.find_run(m["source_run"]), float(m["t_myr"]), w["grid"], log=log)
    real = m.get("mode") == "real"  # (the world's mode, PW-695: no fantasy exotics in the real world)
    keys = [k for k in RS.KEYS if not (real and k in RS.FANTASY)]
    if all(f"res_{k}" in w["layers"] for k in keys):
        R = {k: np.asarray(w["layers"].get(f"res_{k}", 0.0), float) * np.ones(w["grid"].n) for k in RS.KEYS}
    else:
        R = RS.likelihoods(w["grid"], w["layers"], m, hist)
        if real:
            R = {k: (np.zeros(w["grid"].n) if k in RS.FANTASY else v) for k, v in R.items()}
    inherit = None
    if meta.get("parent_zoom"):  # (a fine zoom: its parent's deposits that lie inside, PW-618)
        pmeta = json.loads((S.find_zoom(meta["parent_zoom"]["id"]) / "zoom.json").read_text())
        if pmeta.get("resources"):
            inherit = (pmeta, pmeta["resources"])
    out = site(w, meta, lay, R, hist, log=log, inherit=inherit)
    out["created"] = time.strftime("%Y-%m-%d %H:%M:%S")
    out["history"] = hist is not None
    out["legend"] = [{"key": k, "name": n, "group": gp, "color": c, "model": md, "form": MODELS[k][0]}
                     for k, n, gp, c, md in RS.RESOURCES if k in MODELS and not (real and k in RS.FANTASY)]
    out["mode"] = "real" if real else "fantasy"
    meta["resources"] = out
    S.write_atomic(d / "zoom.json", json.dumps(meta, indent=1))
    return d
