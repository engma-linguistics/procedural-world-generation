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
              power-law wall, P_WALL) as wide as 3-5 x its depth (W_D_MID, more under a bigger flux: PW-510). A
              side valley is not lowered with it: it ends hanging above the
              trough (a waterfall in the final drainage). Where a trough
              floor ends below the sea and joins it, it is drowned: a fjord
              (drown()).
  cirques     bowls on the high slopes in the iced country, on a planet-fixed
              lattice (zoom_landforms.blobs); the ridge left between two is
              an arete.
  moraines    ridges along the margin: where the smooth share of iced cells
              passes 0.5 (the terminal belt) and 0.85 (a recessional one),
              lobed, as high as the till says; across a stream one unbroken
              ridge 20-60 m high (a dam: the lake forms behind it, basins(), lakes()).
              Where the ice's margin is out of view, belts at ice-thickness contours.
  drumlins    mounds elongated along the ice's flow (the surface slope of the
              bed + ice_max, DERIVED per cell: ice_flow()) on the till plains
              inside the margin (an overlay, after the drainage), plus kettle
              pits on outwash and moraine (ponds where they reach the water
              table).
  eskers      sinuous ridges from the margin's proglacial streams back up the ice's flow.
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
WH_MAX_KM = 8.0
WMIN_PX = 0.5  # the narrowest trough half-width, in pixels: one pixel across, the least a pixel grid can draw
ICE_FRAC = 0.6  # a trough floor is lowered by at most this share of the thickest ice
W_D_MID = (3.0, 5.0)  # rim-to-rim width over depth of a trough under a small / a big flux
E_FULL_M = (6.0, 35.0)  # the cell-mean erosion (m) under which a trunk is hardly lowered, and from which fully
DEPTH_RANGE_M = (200.0, 1500.0)  # rim-to-floor depth of real fjords and U-valleys (water depth 200-800 m; Sognefjord ~1300 m below sea)
W_D_RANGE = (2.5, 6.0)  # rim-to-rim width over depth of U-valleys: roughly 3-5
TROUGH_MIN_M = 100.0  # the floor lowering from which a trunk counts as a trough in the calibration
Q_DAM = 4.0  # m^3/s: a stream this big that a moraine belt crosses is dammed by it (an unbroken ridge)
DAM_M = (20.0, 60.0)  # a moraine dam's crest above the valley floor
ESKER_KM = (25.0, 90.0)  # length of an esker traced back up the ice's flow from the margin
ESKER_M = (6.0, 18.0)
RECESS_ICE_M = (1100.0, 1900.0)  # thickness contours (m) of the thickest ice where the retreat paused
KETTLE_MAX_M = 40.0
CIRQUE_CELL_KM = 9.0
OUTWASH_MAX_M = 45.0
OUTWASH_KM = 90.0  # e-folding distance of the outwash downstream
LOESS_PEAK_M = 12.0
LOESS_KM = 40.0
FORM = {"trough": 1, "cirque": 2, "moraine": 3, "drumlin": 4, "outwash": 5, "loess": 6, "fjord": 7, "lake": 8, "esker": 9, "kettle": 10}


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


def trough_metrics(cx_cache, h, nx, ny, res, region) -> dict:
    """Depth and width of the troughs measured on the finished ground (PW-510): per trunk pixel in the
    region, the depth is the rim (median height at 0.9-1.3 half-widths from it) above its floor, the
    width is the trough's rim-to-rim width, 2 half-widths. The share (of the trunk length) within the
    literature: rim-to-floor depth DEPTH_RANGE_M and width/depth W_D_RANGE; and the percentiles."""
    tg = cx_cache.get("trough_geom")
    if tg is None:
        return {}
    trunk, t, x, w_t, ok, delta, wh_f, _ = tg
    wr_ = np.maximum(w_t, res)
    ann = ok & (x >= 0.9 * wr_) & (x <= 1.45 * wr_)
    n = nx * ny
    cnt = trunk & region
    ids = np.flatnonzero(cnt)
    if len(ids) < 5:
        return {}
    pix = np.flatnonzero(ann)
    own = t[pix]
    o = np.lexsort((h[pix], own))
    own_s, h_s = own[o], h[pix][o]
    starts = np.r_[0, np.flatnonzero(np.diff(own_s)) + 1]
    ends = np.r_[starts[1:], len(own_s)]
    med = np.full(n, np.nan)
    ok_n = (ends - starts) >= 2
    mid = starts + (ends - starts) // 2
    med[own_s[starts]] = np.where(ok_n, h_s[mid], np.nan)
    rim = med[ids]
    d = rim - h[ids]
    w = 2.0 * w_t[ids]  # km
    good = np.isfinite(d) & (d > 0) & (delta[ids] >= TROUGH_MIN_M)  # (a trough: the ice lowered the floor this much)
    d, w = d[good], w[good]
    if len(d) < 5:
        return {}
    wd = 1000.0 * w / d
    inr = (d >= DEPTH_RANGE_M[0]) & (d <= DEPTH_RANGE_M[1]) & (wd >= W_D_RANGE[0]) & (wd <= W_D_RANGE[1])
    fl = w <= 2.0 * WMIN_PX * res * 1.001  # (at the narrowest a pixel grid draws: its width can't follow its depth)
    pc = lambda a: [round(float(v), 1) for v in np.percentile(a, [10, 50, 90])]  # noqa: E731
    return {"tr_n": int(len(d)), "tr_depth_m_p10_50_90": pc(d), "tr_width_km_p10_50_90": pc(w), "tr_w_over_d_p10_50_90": pc(wd),
            "tr_depth_ok_pct": round(100.0 * float(np.mean((d >= DEPTH_RANGE_M[0]) & (d <= DEPTH_RANGE_M[1]))), 0),
            "tr_wd_ok_pct": round(100.0 * float(np.mean((wd >= W_D_RANGE[0]) & (wd <= W_D_RANGE[1]))), 0),
            "tr_resolved_in_range_pct": (round(100.0 * float(np.mean(inr[~fl])), 0) if (~fl).any() else None),
            "tr_at_pixel_floor_pct": round(100.0 * float(np.mean(fl)), 0),
            "tr_in_range_pct": round(100.0 * float(np.mean(inr)), 0)}


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

    def _margin(self, cx, G, level, gmin=0.004):
        """Signed km from the contour G = level (positive inside the ice; gmin: the smallest slope, per km)."""
        gy, gx = np.gradient(G.reshape(cx.ny, cx.nx), cx.res)
        gm = np.maximum(np.hypot(gx, gy).ravel(), gmin)  # (per km: ~ 1 / a cell's reach)
        return (G - level) / gm

    def _open_width(self, cx, h, trunk, t, x, okl, delta, kwd):
        """Half-width (km) of each trunk pixel's trough and the relief of its rim above the floor (m): the
        trough opens until its rim-to-rim width is kwd x its depth (the floor lowering plus the valley's relief
        up to the rim, read from the ground at the candidate widths): the width follows the depth (PW-510)."""
        res = cx.res
        cands = np.unique(np.maximum(res * np.array([WMIN_PX, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0]), 0.5))
        cands = cands[cands <= WH_MAX_KM + 1e-9]
        n = len(h)
        ids = np.flatnonzero(trunk)
        rel = []
        for w in cands:
            wr_ = max(w, res)  # (the ring can't be nearer than a pixel)
            sel = okl & (x >= 0.9 * wr_) & (x <= 1.45 * wr_)
            cnt = np.bincount(t[sel], minlength=n)[ids]
            sm = np.bincount(t[sel], h[sel], minlength=n)[ids]
            r = np.where(cnt >= 2, sm / np.maximum(cnt, 1) - h[ids], np.nan)
            rel.append(np.maximum(r, 0.0))
        rel = np.array(rel)
        for j in range(1, len(cands)):  # (no ground measured there: the narrower one's)
            rel[j] = np.where(np.isnan(rel[j]), rel[j - 1], rel[j])
        rel = np.where(np.isnan(rel), float(np.clip(cx.zone_relief(h), 150.0, 600.0)), rel)
        rel = np.maximum.accumulate(rel, axis=0)
        D = delta[ids][None, :] + rel
        g = 2000.0 * cands[:, None] - kwd[ids][None, :] * D  # (>= 0: wide enough)
        first = np.argmax(g >= 0, axis=0)
        none = ~(g >= 0).any(axis=0)
        j1 = first
        j0 = np.maximum(first - 1, 0)
        cols = np.arange(len(ids))
        g0, g1 = g[j0, cols], g[j1, cols]
        fr = np.where(j1 > j0, np.clip(-g0 / np.maximum(g1 - g0, 1e-9), 0.0, 1.0), 1.0)
        wsel = cands[j0] + fr * (cands[j1] - cands[j0])
        wsel = np.where(none, cands[-1], wsel)
        rsel = rel[j0, cols] + fr * (rel[j1, cols] - rel[j0, cols])
        rsel = np.where(none, rel[-1], rsel)
        wh = np.zeros(n)
        rl = np.zeros(n)
        wh[ids] = wsel
        rl[ids] = rsel
        return wh, rl

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
            F = f["F"]
            delta = (np.minimum(np.minimum(DELTA_PER_M * E, DELTA_MAX), ICE_FRAC * F) * smoothstep(*E_FULL_M, E)
                     * (0.45 + 0.55 * big) * np.clip(0.8 + 0.55 * nz, 0.15, 1.3))
            kwd = W_D_MID[0] + (W_D_MID[1] - W_D_MID[0]) * big  # (a bigger flux: a wider trough for its depth)
            idx, dpx = nearest_feature(trunk, nx, ny)
            ok = idx >= 0
            t = np.maximum(idx, 0)
            x = dpx * res
            wh_f, rel_f = self._open_width(cx, h, trunk, t, x, ok & land, delta, kwd)
            wh, relief_t = wh_f, rel_f
            d_t, w_t, f_t, r_t = delta[t], wh[t], h[t], relief_t[t]
            xf = 0.35 * w_t
            s_ = (d_t + r_t) / np.maximum(w_t - xf, 1e-6) ** P_WALL
            target = f_t - d_t + s_ * np.maximum(x - xf, 0.0) ** P_WALL
            reach = 1.0 - smoothstep(0.9, 1.15, x / np.maximum(w_t, 1e-6))
            dz_t = np.where(ok & land, (np.minimum(target, h) - h) * reach, 0.0)
            dz += dz_t
            zone = ok & land & (x <= 1.1 * w_t) & (dz_t < -2.0)
            cx.cache["trough_geom"] = (trunk, t, x, w_t, ok, delta, wh_f, None)
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
        strm = (q >= Q_DAM) & land
        damw = 1.0 - smoothstep(wr, 3.0 * wr, ZK.inside_distance(~strm, nx, ny, False) * res) if strm.any() else np.zeros(len(h))
        # the margin (G = 0.5 the terminal belt, 0.85 a recessional one), and where a sheet never ended in view, the
        # retreat's stands at ice-thickness contours (the margin pulls back up the thickness gradient)
        lev = [(G, lvl, k, 0.004, 1.0) for lvl, k in ((0.5, 1.0), (0.85, 0.5))]
        lev += [(f["F"], fl, 0.5, 0.5, 1.0) for fl in RECESS_ICE_M]
        for fld, lvl, k, gmin, _ in lev:
            m = self._margin(cx, fld, lvl, gmin)
            ht = np.clip(6.0 + 2.0 * T, 6.0, 80.0)
            belt = k * np.exp(-0.5 * (m / wr) ** 2)
            mor = np.maximum(mor, belt * ht * lob * hum)
            # across a stream the belt is one unbroken ridge, high enough to hold the water back: a dam
            dam = belt * np.clip(ht, *DAM_M) * (0.85 + 0.15 * hum)
            mor = np.maximum(mor, dam * damw)
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
        cx.cache["src"] = src
        lc = cx.counted(land)
        st["iced_pct"] = round(100.0 * float(np.mean(G[lc] > 0.5)), 0) if lc.any() else 0.0
        st["F_p5_50_95"] = [round(float(v)) for v in np.percentile(f["F"][lc], [5, 50, 95])] if lc.any() else []
        st["margin_pct"] = round(100.0 * float(np.mean((G[lc] > 0.15) & (G[lc] < 0.85))), 0) if lc.any() else 0.0
        st["dam_px"] = int(np.sum(cx.counted(strm & (mor > 15.0))))
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
        """Where closed depressions may hold water: the troughs and moraine zone, and all the country
        inside the margin (a lake behind a moraine dam lies up the valley, beyond the ridge's zone)."""
        z = self.basins(cx)
        if z is None:
            return None
        return np.maximum(z, smoothstep(0.35, 0.5, self._f(cx)["G"]))

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

    def _eskers(self, cx, fin, h):
        """0..1 on the pixels of the eskers: from the proglacial streams at the margin (one per ~25 km of
        it), back up the ice's flow (ux, uy) over ESKER_KM, wandering, fading out up-ice."""
        src = cx.cache.get("src")
        f = self._f(cx)
        if src is None or not src.any() or not (f["dir"] > 0.3).any():
            return None
        nx, ny, res = cx.nx, cx.ny, cx.res
        cand = np.flatnonzero(src & (fin["q"] >= 2.0) & (f["dir"] > 0.3) & (f["G"] > 0.45) & cx.land)
        if not len(cand):
            return None
        B = max(2, int(round(25.0 / res)))
        blk = (cand // nx // B) * 100000 + (cand % nx) // B
        o = np.lexsort((-fin["q"][cand], blk))
        first = np.r_[True, np.diff(blk[o]) != 0]
        seeds = cand[o][first]
        rng = np.random.default_rng(int(cx.seed) + 497)
        ux, uy, G = f["ux"], f["uy"], f["G"]
        out = np.zeros(nx * ny)
        for s0 in seeds:
            L = rng.uniform(*ESKER_KM)
            r, c = float(s0 // nx), float(s0 % nx)
            ang = None
            n = int(L / (0.7 * res))
            for i in range(n):
                ri, ci = int(round(r)), int(round(c))
                if ri < 1 or ci < 1 or ri >= ny - 1 or ci >= nx - 1:
                    break
                j = ri * nx + ci
                if G[j] < 0.5 or not cx.land[j]:
                    break
                a0 = np.arctan2(-uy[j], -ux[j])  # (up-ice; rows run south)
                ang = a0 if ang is None else ang + 0.5 * np.arctan2(np.sin(a0 - ang), np.cos(a0 - ang))
                ang += rng.normal(0.0, 0.35)
                out[j] = max(out[j], 1.0 - float(smoothstep(0.6, 1.0, i / max(n, 1))))
                r -= 0.7 * np.sin(ang)
                c += 0.7 * np.cos(ang)
        return out if out.any() else None

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
        # kettles: pits where buried ice melted out of outwash and moraine, as deep as the deposit stands above the
        # water table (so they hold ponds there), up to KETTLE_MAX_M
        tout = cx.cache.get("tout", 0.0)
        tout = np.zeros(len(h)) if np.isscalar(tout) else tout
        pitz = np.maximum(smoothstep(2.0, 10.0, tout), smoothstep(8.0, 30.0, cx.cache.get("mor", np.zeros(len(h)))))
        if pitz.max() > 0.2:
            qk, _, Rk, _ = ZL.blobs(cx.Pk, 6.0, np.int64(cx.seed + 495), 0.5, np.array([1.0, 3.0]), 1.3, 1.0 * res)
            above = np.maximum(h - fin["base"], 0.0)
            deep = np.clip(above + 5.0 + 4.0 * Rk, 6.0, KETTLE_MAX_M)
            pit = pitz * np.where(qk < 1.0, deep * (1 - np.minimum(qk, 1.0) ** 2), 0.0)
            out -= pit
            cx.cache["kettle"] = pit > 4.0
            st["kettles"] = _components(pit > 4.0, nx, ny, cx.counted(np.ones(len(h), bool)), 1)
        # eskers: sinuous ridges of the subglacial streams, traced back up the ice's flow from the margin's outwash
        esk = self._eskers(cx, fin, h)
        if esk is not None:
            out += esk * np.clip(ESKER_M[0] + 0.25 * T, *ESKER_M)
            cx.cache["esker"] = esk > 0.3
            st["esker_km"] = round(float(np.sum(cx.counted(esk > 0.3))) * res, 0)
        return out
