"""Shore forms in a regional zoom (PW-621; docs/proposals/coast_detail.md stage 2): what the waves and tides
build from the sand and mud the rivers and cliffs give them. Part of `planet coast zoom:<id>` (zoom_coast.py):
a new layer `shore_form` and spit features; the terrain changes only with --terrain (spits raised out of the
sea), like the barrier islands.

Longshore drift (CERC formula; Komar 1998): waves that reach a shore at an angle theta to its normal move sand
along it at a rate ~ H^2.5 sin(2 theta), i.e. ~ P sin(2 theta) for wave power P. The zoom has the waves' power
but not their direction; the dominant waves run with the world's wind (wind_e, wind_n at the pixel's cell),
so the drift per shore pixel is DRIFT = P x 2 cos(theta) sin(theta) along the shore's tangent, signed, with the
shore's normal from the gradient of a smoothed land mask (NORMAL_KM) and theta the angle between the wind
and the landward normal (offshore winds move nothing).

Supply (sand to build with): river mouths (the zoom's discharge where a river meets the sea, ~sqrt(Q)) and
retreating soft cliffs and bluffs (the zoom's shore rise >= SOURCE_RISE m on rock that is not hard, x waves),
summed SUPPLY_KM up the drift. Sand without drift builds out in place (beach ridges); drift without sand
builds nothing.

  1 spit         Where the drifting sand reaches a turn in the coast (a headland's lee, a bay or estuary
                 mouth) it carries on straight into the sea: a spit grows from the shore pixel whose shore
                 falls away ahead (the land LOOK_KM ahead along the drift and half that again landward is
                 sea), over water shallower than SPIT_DEPTH_M, SPIT_KM long x sqrt(supply), its last
                 HOOK_SHARE bent up to HOOK_DEG landward by the waves refracting round its tip (a recurved
                 hook: Spurn Head, Sandy Hook, Farewell Spit). Spits stand >= SPIT_SPACING_KM apart, the
                 best (drift x supply) first.
  2 beach ridges Prograding wave coasts (Tamura 2012): low land (< RIDGE_M) within RIDGE_KM x sqrt(supply)
                 of a wave-built beach near a big sand supply (a delta's flanks, a river mouth) is a
                 strandplain of beach ridges (Nayarit, Coorong, the Rhone and Danube deltas' flanks).
  3 tidal channel  Tidal flats (Allen 2000; Fagherazzi 2008): on tide-dominated shores (tide range >= FLAT_TIDE_M
  4 tidal flat   and >= TIDE_DOMINANT x the waves' Hs: Davis & Hayes 1984) mud and sand fill the shallow
                 floor (< FLAT_DEPTH_M) out to FLAT_KM_PER_M km per m of tide range, with the marsh behind
                 (land below half the range); the ebb drains them through a dendritic channel network, the
                 flats' own D8 drainage toward the deeper sea (planet-fixed noise breaks the flat floor),
                 channels where FLAT_CHANNEL_KM2 or more drains through.
  5 drowned reef Reefs grow at the shore of the sea they live in; at a glacial lowstand that shore lay
                 the time zoom's sea-level drop (meta sea_level_change_m) lower, and as the ice melted the sea
                 rose faster than the reefs could follow (Montaggioni 2005): in reef waters (the coldest month's
                 sea >= REEF_SST C) the sea floor at the lowstand shoreline's depth (-REEF_BAND x the drop) is a
                 drowned reef terrace (now 60-130 m down off an Earth-like ice age; none without ice ages).
"""

from __future__ import annotations

import math

import numpy as np

from ..geo import R_KM, latlon

NORMAL_KM = 4.0  # smoothing of the land mask for the shore's normal
SOURCE_RISE = 15.0  # m: a bluff or cliff that feeds the beach when it retreats
SUPPLY_KM = 30.0  # km up the drift whose sources feed a spit
RIVER_Q = 5.0  # m3/s: a river mouth that brings sand
LOOK_KM = 3.0  # km ahead along the drift for 'the coast falls away'
SPIT_DEPTH_M = 20.0
SPIT_KM = 6.0  # km of spit per unit sqrt(supply)
SPIT_MAX_KM = 40.0
SPIT_MIN_KM = 2.0
HOOK_SHARE, HOOK_DEG = 0.25, 70.0
SPIT_SPACING_KM = 20.0
MAX_SPITS = 40
MIN_DRIFT = 2.0  # kW/m of along-shore wave power for a spit
RIDGE_M = 8.0
RIDGE_KM = 3.0  # km of strandplain per unit sqrt(supply)
RIDGE_MAX_KM = 20.0
RIDGE_SUPPLY = 1.0  # supply for a strandplain
FLAT_TIDE_M = 2.0
TIDE_DOMINANT = 2.0  # tide range / wave height (Hs) above which tides shape the shore (Davis & Hayes 1984)
FLAT_KM_PER_M = 2.0  # km of flat per m of tide range (Wadden Sea ~2.5 m: 5-10 km; Yellow Sea 4-8 m: 10-20 km)
FLAT_DEPTH_M = 25.0  # m: the inner-shelf floor a flat builds out over (the zoom interpolates its near-shore depths from 60 km world cells, too deep within the first km)
FLAT_CHANNEL_KM2 = 40.0  # km2 drained: the main creeks a 1-4 km pixel can show (small creeks drain ~1-10 km2)
REEF_SST = 18.0
REEF_BAND = (0.9, 1.3)  # x the lowstand drop: the drowned reef rim's depth now (the ground moved a little)
SPIT_M = 2.5  # m: a spit's crest above the sea with --terrain

LEGEND = [{"id": 0, "key": "none", "name": "none", "color": "#00000000"},
          {"id": 1, "key": "spit", "name": "spit (by longshore drift)", "color": "#ffe08a"},
          {"id": 2, "key": "ridges", "name": "beach-ridge plain", "color": "#d9b26f"},
          {"id": 3, "key": "channel", "name": "tidal channel", "color": "#2a6f97"},
          {"id": 4, "key": "flat", "name": "tidal flat", "color": "#a39e8a"},
          {"id": 5, "key": "drowned_reef", "name": "drowned reef (lowstand)", "color": "#c05299"}]
SPIT, RIDGES, CHANNEL, FLAT, DROWNED = 1, 2, 3, 4, 5


def _box(a, r):
    """Mean over a (2r+1)^2 square (edges: zero padded, then normalised by the in-bounds count)."""
    ny, nx = a.shape
    c = np.pad(a, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    r0, r1 = np.clip(np.arange(ny) - r, 0, ny), np.clip(np.arange(ny) + r + 1, 0, ny)
    c0, c1 = np.clip(np.arange(nx) - r, 0, nx), np.clip(np.arange(nx) + r + 1, 0, nx)
    s = c[r1][:, c1] - c[r0][:, c1] - c[r1][:, c0] + c[r0][:, c0]
    return s / ((r1 - r0)[:, None] * (c1 - c0)[None, :])


def _wind_px(world, cells, Pk, ny, nx):
    """The world's annual wind at each pixel as (d_row, d_col) m/s in the zoom's array frame."""
    L = world["layers"]
    if "wind_e" not in L:
        return np.zeros((ny, nx)), np.zeros((ny, nx))
    u = np.asarray(L["wind_e"], float)[cells]
    v = np.asarray(L["wind_n"], float)[cells]
    P = (Pk / R_KM).reshape(ny, nx, 3)
    lat, lon = latlon(Pk / R_KM)
    lat, lon = np.radians(lat), np.radians(lon)
    e = np.stack([-np.sin(lon), np.cos(lon), np.zeros_like(lon)], -1)
    n = np.stack([-np.sin(lat) * np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat)], -1)
    w3 = (u[:, None] * e + v[:, None] * n).reshape(ny, nx, 3)
    ux = np.gradient(P, axis=1)  # +col (east in the frame)
    uy = -np.gradient(P, axis=0)  # -row (north in the frame)
    ux /= np.linalg.norm(ux, axis=-1, keepdims=True)
    uy /= np.linalg.norm(uy, axis=-1, keepdims=True)
    wx, wy = (w3 * ux).sum(-1), (w3 * uy).sum(-1)
    return -wy, wx


def _d8_channels(bed, flat, noise, res, min_km2):
    """Channels of a tidal flat: each flat pixel drains to its lowest 8-neighbour (bed + noise), outlets off
    the flat; the pixels that FLAT_CHANNEL_KM2 or more drain through."""
    ny, nx = bed.shape
    z = bed + noise
    idx = np.flatnonzero(flat.ravel())
    if not len(idx):
        return np.zeros_like(flat)
    zf = z.ravel()
    down = np.full(ny * nx, -1)
    best = np.zeros(len(idx))
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if not (dr or dc):
                continue
            r, c = idx // nx + dr, idx % nx + dc
            ok = (r >= 0) & (r < ny) & (c >= 0) & (c < nx)
            j = np.where(ok, r * nx + c, idx)
            drop = (zf[idx] - zf[j]) / math.hypot(dr, dc)
            better = ok & (drop > best)
            best = np.where(better, drop, best)
            down[idx[better]] = j[better]
    acc = np.zeros(ny * nx)
    acc[idx] = res * res
    for i in idx[np.argsort(-zf[idx])]:
        d = down[i]
        if d >= 0 and flat.ravel()[d]:
            acc[d] += acc[i]
    return (acc >= min_km2).reshape(ny, nx) & flat


def build(world, meta, lay, ctx, terrain=False, seed=1):
    """shore_form (ny, nx) u1, spit features and stats. ctx: zoom_coast.build's shore arrays (land, sea, shore,
    h, wave_sea, tide_sea, rise, hard, ct, cells, Pk, uniform)."""
    land, sea, shore, h = ctx["land"], ctx["sea"], ctx["shore"], ctx["h"]
    res, ct, Pk = ctx["res"], ctx["ct"], ctx["Pk"]
    ny, nx = h.shape
    out = np.zeros((ny, nx), np.uint8)
    # the shore's seaward normal (array frame: d_row, d_col) and tangent
    lm = _box(land.astype(float), max(1, int(round(NORMAL_KM / res))))
    gr, gc = np.gradient(lm)
    norm = np.hypot(gr, gc) + 1e-9
    nr, nc = -gr / norm, -gc / norm  # toward the sea
    tr, tc = -nc, nr
    wr, wc = _wind_px(world, ctx["cells"], Pk, ny, nx)
    ws = np.hypot(wr, wc) + 1e-9
    dr_, dc_ = wr / ws, wc / ws  # where the waves run
    cos_in = -(dr_ * nr + dc_ * nc)  # > 0: waves heading landward
    sin_t = dr_ * tr + dc_ * tc
    drift = np.where(shore & (cos_in > 0), ctx["wave_sea"] * 2 * cos_in * sin_t, 0.0)  # kW/m along +t
    # sand sources: river mouths and retreating soft bluffs
    q = np.asarray(lay.get("discharge", np.zeros_like(h)), float)
    mouth = shore & (q >= RIVER_Q)
    src = np.where(mouth, np.sqrt(q / 100.0), 0.0)
    soft = shore & (ctx["rise"] >= SOURCE_RISE) & ~ctx["hard"]
    src = src + np.where(soft, ctx["wave_sea"] / 20.0 * res, 0.0)
    # spits: roots where the shore falls away ahead along the drift
    look = LOOK_KM / res
    sgn = np.sign(drift)
    ar, ac = tr * sgn, tc * sgn  # the drift's direction
    rr, cc = np.nonzero(shore & (np.abs(drift) >= MIN_DRIFT))
    feats, spit = [], np.zeros((ny, nx), bool)

    def at(m, r, c):
        r, c = np.round(r).astype(int), np.round(c).astype(int)
        ok = (r >= 0) & (r < ny) & (c >= 0) & (c < nx)
        return np.where(ok, m[np.clip(r, 0, ny - 1), np.clip(c, 0, nx - 1)], False)
    a_r, a_c = ar[rr, cc], ac[rr, cc]
    ahead = (~at(land, rr + look * a_r, cc + look * a_c)
             & ~at(land, rr + look * a_r - 0.5 * look * nr[rr, cc], cc + look * a_c - 0.5 * look * nc[rr, cc])
             & at(sea, rr + look * a_r, cc + look * a_c))
    rr, cc = rr[ahead], cc[ahead]
    # supply: the sources within SUPPLY_KM behind each root (up the drift)
    sr, sc = np.nonzero(src > 0)
    sv = src[sr, sc]
    sup = np.zeros(len(rr))
    for k in range(len(rr)):
        dr0, dc0 = sr - rr[k], sc - cc[k]
        d = np.hypot(dr0, dc0) * res
        behind = (dr0 * ar[rr[k], cc[k]] + dc0 * ac[rr[k], cc[k]]) <= 0
        sup[k] = sv[(d <= SUPPLY_KM) & behind].sum()
    score = np.abs(drift[rr, cc]) * np.sqrt(sup)
    depth = np.where(sea, -h, 0.0)
    picked = []
    for k in np.argsort(-score):
        if score[k] <= 0 or len(picked) >= MAX_SPITS:
            break
        r0, c0 = int(rr[k]), int(cc[k])
        if any(math.hypot(r0 - a, c0 - b) * res < SPIT_SPACING_KM for a, b in picked):
            continue
        length = min(SPIT_MAX_KM, SPIT_KM * math.sqrt(sup[k]))
        if length < SPIT_MIN_KM:
            continue
        # march: straight along the drift, the last HOOK_SHARE turning landward
        dr1, dc1 = float(ar[r0, c0]), float(ac[r0, c0])
        lr, lc = -float(nr[r0, c0]), -float(nc[r0, c0])
        side = 1.0 if (dr1 * lc - dc1 * lr) > 0 else -1.0  # which way 'landward' turns the heading
        pr, pc, path, s = float(r0), float(c0), [], 0.0
        step = 0.5
        while s < length:
            f = (s / length - (1 - HOOK_SHARE)) / HOOK_SHARE
            ang = math.radians(HOOK_DEG) * max(f, 0.0) * side
            hr = dr1 * math.cos(ang) - dc1 * math.sin(ang)
            hc = dr1 * math.sin(ang) + dc1 * math.cos(ang)
            pr, pc = pr + step * hr, pc + step * hc
            s += step * res
            ir, ic = int(round(pr)), int(round(pc))
            if not (0 <= ir < ny and 0 <= ic < nx) or depth[ir, ic] > SPIT_DEPTH_M:
                break
            if land[ir, ic]:
                if len(path) > 1:  # (reached land again: a bay-mouth bar)
                    break
                continue
            if not path or path[-1] != (ir, ic):
                path.append((ir, ic))
        if len(path) * res < SPIT_MIN_KM:
            continue
        picked.append((r0, c0))
        for ir, ic in path:
            spit[ir, ic] = True
        lat, lon = latlon(Pk[r0 * nx + c0] / R_KM)
        bearing = (math.degrees(math.atan2(dc1, -dr1)) + 360) % 360
        feats.append({"kind": "spit", "px": [r0, c0], "lat": round(float(lat), 4), "lon": round(float(lon), 4),
                      "length_km": round(len(path) * res, 1), "drift_bearing": round(bearing),
                      "drift_kw_m": round(float(abs(drift[r0, c0])), 1), "supply": round(float(sup[k]), 2),
                      "end_px": list(path[-1])})
    # beach-ridge plains: low land behind beach/low shores with sand to spare
    from ..coastform import BEACH
    beachy = shore & (ct == BEACH)
    sup_r = max(1, int(round(SUPPLY_KM / res)))
    local = _box(src, sup_r) * (2 * sup_r + 1) ** 2
    seed_px = beachy & (local >= RIDGE_SUPPLY)
    ridges = np.zeros((ny, nx), bool)
    if seed_px.any():
        from .coast import _distance
        width = np.clip(RIDGE_KM * np.sqrt(np.where(seed_px, local, 0.0)), 0, RIDGE_MAX_KM)
        wmax = float(width.max())
        low_land = land & (h < RIDGE_M)
        d = _distance(seed_px, low_land, res, wmax)
        # (each plain pixel's width from its nearest seeds: the box max of the seeds' widths)
        from .coastal import window_max
        wnear = window_max(np.where(seed_px, width, -np.inf), max(1, int(math.ceil(wmax / res))))
        ridges = low_land & np.isfinite(d) & (d <= wnear)
    # tidal flats and their channels: tide-dominated shores (the tide range >= TIDE_DOMINANT x the waves'
    # height, and >= FLAT_TIDE_M); the flat runs out over shallow floor as far as the tide range sets
    from ..coast import hs_te
    from .coast import _dilate, _distance
    tide = ctx["tide_sea"]
    hs = np.asarray(hs_te(np.maximum(ctx["wave_sea"], 0.0))[0], float)
    tidal_shore = shore & (tide >= FLAT_TIDE_M) & (tide >= TIDE_DOMINANT * hs)
    flat = np.zeros((ny, nx), bool)
    if tidal_shore.any():
        reach = window_max_safe(np.where(tidal_shore, tide, -np.inf), max(1, int(round(FLAT_KM_PER_M * 12 / res))))
        d = _distance(tidal_shore, sea & (depth < FLAT_DEPTH_M), res, FLAT_KM_PER_M * float(tide[tidal_shore].max()))
        flat = sea & np.isfinite(d) & (d <= FLAT_KM_PER_M * reach)
        flat |= land & _dilate(tidal_shore, 1) & (h < 0.5 * np.maximum(tide, FLAT_TIDE_M))  # (the marsh behind)
    noise = ctx["uniform"](5.0 * res, seed + 91) * 0.5
    chan = _d8_channels(h, flat, noise, res, FLAT_CHANNEL_KM2)
    # drowned reefs at the lowstand shoreline's depth, in reef waters
    drop = abs(float(world["meta"].get("sea_level_change_m") or 0.0))
    reef = np.zeros((ny, nx), bool)
    L = world["layers"]
    if drop >= 20 and ("sst_jan" in L or "sst" in L):
        cold = (np.minimum(np.asarray(L["sst_jan"], float), np.asarray(L["sst_jul"], float)) if "sst_jan" in L
                else np.asarray(L["sst"], float))
        warm = (cold[ctx["cells"]] >= REEF_SST).reshape(ny, nx)
        # (the lowstand's shore: the first pixels deeper than the drop, seaward of floor shallower than it; the
        # reef rim then sank or rose with the ground a little: REEF_BAND)
        lowstand_sea = sea & (depth >= REEF_BAND[0] * drop)
        rim = lowstand_sea & _dilate(sea & (depth < REEF_BAND[0] * drop), 1) & (depth <= REEF_BAND[1] * drop)
        reef = rim & warm
    out[reef] = DROWNED
    out[flat] = FLAT
    out[chan] = CHANNEL
    out[ridges] = RIDGES
    out[spit] = SPIT
    stats = {"spits": len(feats), "spit_km": round(float(spit.sum() * res), 1),
             "beach_ridges_km2": round(float(ridges.sum() * res * res), 1),
             "tidal_flats_km2": round(float((flat & ~chan).sum() * res * res), 1),
             "tidal_channels_km2": round(float(chan.sum() * res * res), 1),
             "drowned_reefs_km2": round(float(reef.sum() * res * res), 1), "lowstand_m": round(drop, 1),
             "drift_kw_m_p90": round(float(np.percentile(np.abs(drift[shore]), 90)), 1) if shore.any() else 0.0}
    terr = None
    if terrain and spit.any():
        u = ctx["uniform"](30.0, seed + 93)
        terr = (spit, SPIT_M * (0.6 + 0.4 * u))
    return {"shore_form": out, "features": feats, "stats": stats, "terrain": terr}


def window_max_safe(a, r):
    from .coastal import window_max
    m = window_max(a, r)
    return np.where(np.isfinite(m), m, 0.0)


