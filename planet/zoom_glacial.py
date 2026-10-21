"""Glacial landforms in the regional zoom (PW-092, PW-497): what ice left on a
finished world, drawn from its imprint.

A finished world carries, per coarse cell, the cell-mean bed the ice eroded
(`glacial_erosion`, m), the till it dropped (`glacial_till`, m) and the
thickest ice it ever held (`ice_max`, m) (timeline.world_from_frame; PW-037).
The coarse elevation already holds the carved basins and the till. Here the
zoom redistributes that at its own scale, mean-neutrally (every coarse
cell's mean is restored after the landform pass, as for the other classes):
the cell mean of the erosion is concentrated into a few troughs, the rest of
the ground is left as the coarse cells have it.

Import zoom_landforms, not this module first (it registers Glaciated there).

A Synth (zoom_landforms) that belongs to no coarse landform class: its cells
are the ones the ice reached, plus a ring round them (select()). Its pieces:

  troughs     the ice follows the big valleys (the zoom's drainage, trunks of
              QT m^3/s and more): each trunk's floor is lowered by DELTA_PER_M
              x the cell-mean erosion (the cell's volume gathered into ~1.5
              troughs ~5 km wide: 50 m of cell mean is a 400 m trough), more
              under bigger trunks, modulated along the valley (rock bars and
              overdeepened basins: adverse slopes, so basins stay closed and
              hold lakes), and the walls pulled into a U (a flat floor, a
              power-law wall, P_WALL) of width growing with the trunk. A
              side valley is not lowered with it: it ends hanging above the
              trough (a waterfall in the final drainage). Where a trough
              floor ends below the sea and joins it, it is drowned: a fjord
              (drown()).
  cirques     bowls on the high slopes in the iced country, on a planet-fixed
              lattice (zoom_landforms.blobs); the ridge left between two is
              an arete.
  moraines    ridges along the margin: where the smooth share of iced cells
              passes 0.5 (the terminal belt) and 0.85 (a recessional one),
              lobed, as high as the till says; across a valley they dam a
              lake (basins(), lakes()).
  drumlins    mounds elongated along the ice's flow (the surface slope of the
              bed + ice_max, DERIVED per cell: ice_flow()) on the till plains
              inside the margin (an overlay, after the drainage), plus kettle
              pits on outwash and moraine (ponds where they reach the water
              table).
  outwash     down the proglacial rivers from the margin (the drainage
              traced downstream from it), a gravel plain of up to
              OUTWASH_MAX_M thinning over OUTWASH_KM; the valley floor
              lifted and flattened.
  loess       downwind (the world's wind) of the outwash, a blanket that
              softens the ground (LOESS_PEAK_M at most).
"""

from __future__ import annotations

import numpy as np
from numba import njit

from . import zoom_kernels as ZK
from . import zoom_landforms as ZL
from .zoom_landforms import Synth, smoothstep

ICED_M = 25.0  # a coarse cell the ice reached with at least this much counts as iced
QT = 25.0  # m^3/s: drainage this big is a trunk the ice followed
DELTA_PER_M = 8.0  # trough floor lowering per metre of the cell-mean erosion (see the docstring)
DELTA_MAX = 1300.0  # m
P_WALL = 1.7  # the trough wall's power law (2: a parabola)
WH_KM = 2.2  # half-width (km) of a trough under a trunk of QT; grows as (q / QT)^0.2
WH_MAX_KM = 6.0
E_FULL_M = (6.0, 35.0)  # the cell-mean erosion (m) under which a trunk is hardly lowered, and from which fully
CIRQUE_CELL_KM = 9.0
OUTWASH_MAX_M = 45.0
OUTWASH_KM = 90.0  # e-folding distance of the outwash downstream
LOESS_PEAK_M = 12.0
LOESS_KM = 40.0
FORM = {"trough": 1, "cirque": 2, "moraine": 3, "drumlin": 4, "outwash": 5, "loess": 6, "fjord": 7, "lake": 8}


def ice_flow(grid, L) -> dict:
    """Per coarse cell the unit direction the ice flowed (east, north): down
    the slope of the bed plus the thickest ice, (elevation + ice_max); zero
    where the ice was thinner than ICED_M. The world doesn't store the flow
    (PW-499); the surface of the thickest ice is where it came from."""
    from .soils import _edges  # (the cells' edges: neighbour, east/north direction, km)
    s = np.asarray(L["elevation"], float) + np.asarray(L["ice_max"], float)
    own, nb, de, dn, km = _edges(grid)
    deg = np.diff(grid.nbr_off).astype(float)
    ge = 2 * np.bincount(own, (s[nb] - s[own]) / km * de, minlength=grid.n) / deg
    gn = 2 * np.bincount(own, (s[nb] - s[own]) / km * dn, minlength=grid.n) / deg
    mag = np.hypot(ge, gn)
    ok = (np.asarray(L["ice_max"], float) >= ICED_M) & (mag > 1e-6)
    return {"ice_fe": np.where(ok, -ge / np.maximum(mag, 1e-12), 0.0),
            "ice_fn": np.where(ok, -gn / np.maximum(mag, 1e-12), 0.0)}


def nearest_feature(mask, nx, ny):
    """(flat index of the nearest True pixel (-1: none), its distance in
    pixels), by jump flooding."""
    n = nx * ny
    ii = np.arange(n)
    r, c = ii // nx, ii % nx
    idx = np.where(mask, ii, -1)
    best = np.where(mask, 0.0, np.inf)
    step = 1 << int(np.ceil(np.log2(max(nx, ny, 2))))
    while step >= 1:
        for dr in (-step, 0, step):
            for dc in (-step, 0, step):
                if dr == 0 and dc == 0:
                    continue
                r2, c2 = r + dr, c + dc
                ok = (r2 >= 0) & (r2 < ny) & (c2 >= 0) & (c2 < nx)
                cand = idx[np.where(ok, r2 * nx + c2, 0)]
                has = ok & (cand >= 0)
                cs = np.maximum(cand, 0)
                d = np.where(has, np.hypot(r - cs // nx, c - cs % nx), np.inf)
                better = d < best
                idx, best = np.where(better, cand, idx), np.where(better, d, best)
        step //= 2
    return idx, best


@njit(cache=True)
def downstream_dist(rec, order, src, nx, res):
    """km along the flow paths from the nearest source upstream (inf: none
    upstream). order: outlets first."""
    n = rec.shape[0]
    dd = np.full(n, np.inf)
    for i in range(n):
        if src[i]:
            dd[i] = 0.0
    for t in range(order.shape[0] - 1, -1, -1):
        i = order[t]
        r = rec[i]
        if r >= 0 and dd[i] < np.inf:
            diag = (r % nx != i % nx) and (r // nx != i // nx)
            v = dd[i] + res * (1.4142135623730951 if diag else 1.0)
            if v < dd[r]:
                dd[r] = v
    return dd


def _land_blur(a, land, nx, ny, r):
    wl = land.reshape(ny, nx).astype(float)
    return ZL._box_mean(a.reshape(ny, nx) * wl, wl, r).ravel()


def _components(mask, nx, ny, count_in, min_px=1):
    """Number of 8-connected components of mask with at least min_px pixels in count_in."""
    if not mask.any():
        return 0
    lab, sizes = ZK.label_components(mask, nx, ny)
    inside = np.bincount(lab[mask & count_in], minlength=len(sizes)) if (mask & count_in).any() else np.zeros(len(sizes))
    return int(np.sum(inside >= min_px))


class Glaciated(Synth):
    """The ice's landforms (module docstring)."""
    layers = ("glacial_erosion", "glacial_till", "ice_max", "iced", "ice_fe", "ice_fn", "wind_e", "wind_n")
    ponds = True  # kettle pits that reach the water table hold ponds
    overlay_q = 3.0

    def select(self, L, sel, form, land_c, grid):
        if "ice_max" not in L or "glacial_erosion" not in L:
            return None
        iced = np.asarray(L["ice_max"], float) >= ICED_M
        ring = np.add.reduceat(iced[grid.nbr_idx].astype(float), grid.nbr_off[:-1]) > 0
        return (iced | ring)[sel] & land_c

    # -- smooth fields ------------------------------------------------------
    def _f(self, cx):
        """The imprint's smooth fields on the pixels (cached)."""
        c = cx.cache
        if "f" not in c:
            p = cx.prm
            fe, fn = p["ice_fe"], p["ice_fn"]
            nrm = np.hypot(fe, fn)
            c["f"] = {"E": np.maximum(p["glacial_erosion"], 0.0), "T": np.maximum(p["glacial_till"], 0.0),
                      "F": np.maximum(p["ice_max"], 0.0), "G": np.clip(p["iced"], 0.0, 1.0),
                      "ux": np.where(nrm > 0.05, fe / np.maximum(nrm, 1e-9), 0.0),
                      "uy": np.where(nrm > 0.05, fn / np.maximum(nrm, 1e-9), 0.0), "dir": np.clip(nrm, 0, 1),
                      "wx": p["wind_e"], "wy": p["wind_n"]}
        return c["f"]

    def _margin(self, cx, G, level):
        """Signed km from the margin contour G = level (positive inside the ice)."""
        gy, gx = np.gradient(G.reshape(cx.ny, cx.nx), cx.res)
        gm = np.maximum(np.hypot(gx, gy).ravel(), 0.004)  # (per km: ~ 1 / a cell's reach)
        return (G - level) / gm

    # -- the shape hook: troughs, cirques, moraines, outwash, loess ------------
    def shape(self, cx, h):
        if cx.rec is None or cx.q is None:
            return None
        f = self._f(cx)
        nx, ny, res = cx.nx, cx.ny, cx.res
        land = cx.land
        st = cx.cache.setdefault("stats", {})
        dz = np.zeros(len(h))
        # troughs --------------------------------------------------------------
        E, q = f["E"], cx.q
        trunk = (q >= QT) & land & (cx.w > 0.3) & (E > 3.0)
        zone = np.zeros(len(h), bool)
        if trunk.any():
            nz = cx.noise(14.0, 2, 461)  # along the valley: bars and overdeepened basins
            big = np.clip(np.log(np.maximum(q, QT) / QT) / np.log(8.0), 0.0, 1.0)
            delta = (np.minimum(DELTA_PER_M * E, DELTA_MAX) * smoothstep(*E_FULL_M, E) * (0.45 + 0.55 * big)
                     * np.clip(0.8 + 0.55 * nz, 0.15, 1.3))
            wh = np.clip(WH_KM * (np.maximum(q, QT) / QT) ** 0.2, 1.6 * res, WH_MAX_KM)
            idx, dpx = nearest_feature(trunk, nx, ny)
            ok = idx >= 0
            t = np.maximum(idx, 0)
            x = dpx * res
            relief = float(np.clip(cx.zone_relief(h), 150.0, 1200.0))
            d_t, w_t, f_t = delta[t], wh[t], h[t]
            xf = 0.35 * w_t
            s_ = (d_t + relief) / np.maximum(w_t - xf, 1e-6) ** P_WALL
            target = f_t - d_t + s_ * np.maximum(x - xf, 0.0) ** P_WALL
            reach = 1.0 - smoothstep(0.9, 1.15, x / np.maximum(w_t, 1e-6))
            dz_t = np.where(ok & land, (np.minimum(target, h) - h) * reach, 0.0)
            dz += dz_t
            zone = ok & land & (x <= 1.1 * w_t) & (dz_t < -2.0)
            cx.cache["floor"] = ok & (x <= 0.8 * w_t)  # (what the sea may flood: the trough's floor and lower walls)
            st["trough_km"] = round(float(np.sum(cx.counted(trunk))) * res, 0)
            st["trough_floor_lowering_m"] = round(float(np.percentile(d_t[trunk], 90)), 0)
        cx.cache["zone_trough"] = zone
        # cirques ---------------------------------------------------------------
        hc = ZL.drain_level(h, cx.rec, cx.order, cx.chan) if cx.chan is not None else np.minimum(h, np.percentile(h, 5))
        d = np.maximum(h - hc, 0.0)
        qb, idb, Rb, _ = ZL.blobs(cx.Pk, CIRQUE_CELL_KM, np.int64(cx.seed + 471), 0.55, np.array([2.5, 6.0]), 1.5,
                                  1.5 * res)
        erel = d / max(cx.zone_relief(h), 30.0)
        rb_ = max(2, int(round(40.0 / res)))
        high = smoothstep(0.0, 0.5, (h - _land_blur(h, land, nx, ny, rb_)) / max(cx.zone_relief(h), 30.0))  # (the high ground)
        elig = smoothstep(0.8, 1.6, erel) * high * smoothstep(3.0, 15.0, E) * smoothstep(0.55, 0.8, f["G"]) * land
        bowl = np.where(qb < 1.0, 70.0 * Rb * (1 - np.minimum(qb, 1.0) ** 2) ** 1.3, 0.0)
        dz_c = -np.minimum(bowl * elig, 0.6 * d)
        dz += dz_c
        cirq = (dz_c < -30.0)
        cx.cache["zone_cirque"] = cirq
        st["cirques"] = _components(cirq, nx, ny, cx.counted(np.ones(len(h), bool)), 1)
        # moraines ---------------------------------------------------------------
        G, T = f["G"], f["T"]
        lob = 0.25 + 0.75 * smoothstep(-1.0, 0.2, cx.noise(25.0, 2, 481))  # (lobed, rarely broken)
        hum = 0.75 + 0.25 * cx.noise(4.0, 2, 482)
        wr = max(3.5, 1.5 * res)
        mor = np.zeros(len(h))
        for lvl, k in ((0.5, 1.0), (0.85, 0.5)):
            m = self._margin(cx, G, lvl)
            ht = np.clip(6.0 + 2.0 * T, 6.0, 80.0)
            mor = np.maximum(mor, k * ht * np.exp(-0.5 * (m / wr) ** 2) * lob * hum)
        mor = mor * land * smoothstep(0.1, 0.4, G)
        dz += mor
        cx.cache["mor"] = mor
        cx.cache["zone_moraine"] = mor > 0.35 * np.maximum(mor.max(), 1e-6) if mor.max() > 5 else np.zeros(len(h), bool)
        # outwash ------------------------------------------------------------------
        m50 = self._margin(cx, G, 0.5)
        src = land & (np.abs(m50) <= max(2.0 * wr, 1.5 * res)) & (T + E > 1.0)
        tout = np.zeros(len(h))
        if src.any() and cx.chan is not None:
            dd = downstream_dist(cx.rec, cx.order, src, nx, res)
            t0 = np.clip(8.0 + 1.2 * T, 8.0, OUTWASH_MAX_M)
            tch = np.where(cx.chan & np.isfinite(dd) & (dd > 0.0), t0 * np.exp(-dd / OUTWASH_KM), 0.0)
            tl = ZL.drain_level(tch, cx.rec, cx.order, cx.chan)  # (each hillslope pixel: its channel's)
            idx2, dpx2 = nearest_feature(cx.chan & (tch > 0.5), nx, ny)
            wp = np.clip(3.0 + 2.0 * np.sqrt(np.maximum(q[np.maximum(idx2, 0)], 1.0) / 10.0), 1.5 * res, 22.0)
            lat = 1.0 - smoothstep(0.5, 1.0, dpx2 * res / wp)
            want = hc + tl * lat
            tout = np.where(land & (tl > 1.0) & (idx2 >= 0), np.maximum(want - h, 0.0), 0.0)
            tout = np.where(d < tl, tout, 0.0)
            dz += tout
        cx.cache["tout"] = tout
        plain = tout > 2.0
        # loess ----------------------------------------------------------------------
        lo = np.zeros(len(h))
        if plain.any():
            wx, wy = f["wx"], f["wy"]
            sp_ = np.hypot(wx, wy)
            ux, uy = np.where(sp_ > 0.05, wx / np.maximum(sp_, 1e-9), 1.0), np.where(sp_ > 0.05, wy / np.maximum(sp_, 1e-9), 0.0)
            a0 = plain.astype(float).reshape(ny, nx)
            r, c = (np.arange(len(h)) // nx), (np.arange(len(h)) % nx)
            K = int(min(80, np.ceil(3 * LOESS_KM / res)))
            acc, nrm = np.zeros(len(h)), 0.0
            for k in range(K + 1):
                wgt = np.exp(-k * res / LOESS_KM)
                r2 = np.clip(np.rint(r + k * uy).astype(int), 0, ny - 1)  # (rows run south: north = -row)
                c2 = np.clip(np.rint(c - k * ux).astype(int), 0, nx - 1)
                acc += wgt * a0[r2, c2]
                nrm += wgt
            lo = LOESS_PEAK_M * acc / nrm * 2.2
            lo = np.minimum(lo, LOESS_PEAK_M) * land
            soft = smoothstep(1.0, 6.0, lo)
            rb = max(1, int(round(3.0 / res)))
            dz += soft * (_land_blur(h + dz, land, nx, ny, rb) - (h + dz)) * land
        cx.cache["loess"] = lo
        # forms for the layer and stats ------------------------------------------------
        form = np.zeros(len(h), np.uint8)
        form[lo >= 2.0] = FORM["loess"]
        form[plain] = FORM["outwash"]
        form[cx.cache["zone_moraine"]] = FORM["moraine"]
        form[zone] = FORM["trough"]
        form[cirq] = FORM["cirque"]
        cx.cache["form"] = form
        st["moraine_belts"] = _components(cx.cache["zone_moraine"] & (mor > 8.0), nx, ny, cx.counted(np.ones(len(h), bool)), max(3, int(10.0 / res)))
        st["outwash_km2"] = round(float(np.sum(cx.counted(plain))) * res * res, 0)
        st["loess_km2"] = round(float(np.sum(cx.counted(lo >= 2.0))) * res * res, 0)
        st["loess_max_m"] = round(float(lo.max()), 1)
        return dz

    # -- closed depressions that hold water ----------------------------------------
    def basins(self, cx):
        z = np.maximum(cx.cache.get("zone_trough", 0), cx.cache.get("zone_moraine", 0))
        return None if np.isscalar(z) else z.astype(float)

    def lakes(self, cx):
        return self.basins(cx)

    # -- the sea floods a trough that joins it: a fjord --------------------------------
    def drown(self, cx, h, sea):
        zone = cx.cache.get("zone_trough")
        if zone is None or not zone.any():
            return None
        cand = zone & cx.land & (h < -2.0) & (cx.cache.get("floor", zone))
        if not cand.any():
            return None
        lab, _ = ZK.label_components(cand | sea, cx.nx, cx.ny)
        wet = np.unique(lab[sea & (lab >= 0)])
        return cand & np.isin(lab, wet)

    # -- the overlay after the final drainage: drumlins and kettles -----------------------
    def overlay(self, cx, h, fin):
        f = self._f(cx)
        nx, ny, res = cx.nx, cx.ny, cx.res
        st = cx.cache.setdefault("overlay_stats", {})
        G, T = f["G"], f["T"]
        # drumlin country: inside the margin, on the till plains, where the ground is gentle and the ice flowed
        gy, gx = np.gradient(h.reshape(ny, nx), res * 1000.0)
        slope = np.hypot(gx, gy).ravel()
        zone = cx.land * smoothstep(0.6, 0.9, G) * (1 - smoothstep(0.03, 0.12, slope)) * smoothstep(4.0, 14.0, T) * f["dir"]
        out = np.zeros(len(h))
        if zone.max() > 0.2:
            n0 = cx.noise(1.2 * res + 1.0, 2, 491)
            r, c = (np.arange(len(h)) // nx), (np.arange(len(h)) % nx)
            ux, uy = f["ux"], f["uy"]
            K = max(2, int(round(8.0 / res)))
            a0 = n0.reshape(ny, nx)
            acc = np.zeros(len(h))
            for k in range(-K, K + 1):
                r2 = np.clip(np.rint(r - k * uy).astype(int), 0, ny - 1)
                c2 = np.clip(np.rint(c + k * ux).astype(int), 0, nx - 1)
                acc += a0[r2, c2]
            streak = acc / np.sqrt(2 * K + 1)
            amp = np.clip(1.5 + 0.7 * T, 4.0, 30.0)
            out += zone * amp * np.maximum(streak - 0.3, 0.0)
            cx.cache["drum"] = zone > 0.5
            st["drumlin_km2"] = round(float(np.sum(cx.counted(zone > 0.5))) * res * res, 0)
        # kettles: pits on outwash and moraine
        pitz = np.maximum(smoothstep(2.0, 10.0, cx.cache.get("tout", 0.0) if not np.isscalar(cx.cache.get("tout", 0.0)) else np.zeros(len(h))),
                          smoothstep(8.0, 30.0, cx.cache.get("mor", np.zeros(len(h)))))
        if pitz.max() > 0.2:
            qk, _, Rk, _ = ZL.blobs(cx.Pk, 7.0, np.int64(cx.seed + 495), 0.35, np.array([0.8, 2.5]), 1.3, 1.0 * res)
            out -= pitz * np.where(qk < 1.0, np.clip(9.0 * Rk, 6.0, 25.0) * (1 - np.minimum(qk, 1.0) ** 2), 0.0)
        return out
