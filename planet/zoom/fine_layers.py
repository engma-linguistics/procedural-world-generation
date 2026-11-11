"""The fine zoom's game and human-use layers (PW-1679): the 25 layers a regional zoom writes besides the terrain ones.

A fine zoom (zoom.fine) is a zoom of a zoom, 25 m to 0.5 km per pixel; its first 48 layers are the terrain, water, climate and
plant ones. This module makes the rest so a rung carries the same layer set as the section it hangs from. Each layer is either
computed (at the pixels, or on a coarser "work grid" of about WORK_KM per pixel where its rule is a property of the
neighbourhood and its distances are in km) or inherited from the parent:

  at the pixels      travel sightline grazing foraging timber fuel building mud_months fire_months green_months hazards
                     (gameattrs.py: per pixel from the plants, soil and slope), fertile fertile_score (humanuse: soil, water,
                     season, slope per pixel), river_nav (humanuse: the channel's own gradient over NAV_RUN_KM of river),
                     coast_type nav_hazard shore_form (zoom.coast: km windows already)
  on the work grid   harbour (fetch and shelter over tens of km, depth within DEPTH_REACH_KM), fresh_water fresh_km spring
                     (reach classes of 3 / 10 / 30 km, springs within 12 km), pass pass_height (basins of 2,000 km2, relief over
                     20 km) — the work grid is the block mean of the pixels, so a rule in km reads km at any pixel size
  inherited          barrier_island, glacial_form (the parent's class, nearest parent pixel: the islands and ice-carved forms
                     are drawn by the section's pass, a fine pass does not redraw them; a barrier class is kept only where the
                     fine water agrees); pass and pass_height for a window under PASS_MIN_WINDOW_KM (no basin that big fits in
                     it): the parent's pass pixel puts one mark on the fine pixel nearest its centre

Nothing here changes a threshold: the rules and numbers are the regional zoom's."""

from __future__ import annotations

import numpy as np

from .. import gameattrs as GA
from .. import humanuse as HU
from . import coast as ZC

WORK_KM = 0.5  # the work grid's pixel: the size the regional zoom's region-scale rules were made at (0.5-4 km)
PASS_MIN_WINDOW_KM = 100.0  # a window narrower than this holds no basin the pass rule asks for (PASS_BASINS_KM2 zoom: 2,000 km2)
D8_NONE = 255


def work_factor(res_km: float, n: int) -> int:
    """Pixels per work-grid pixel: 1 at 0.5 km and coarser."""
    return int(max(1, min(round(WORK_KM / res_km), n // 4)))


def _blocks(a, k, n):
    a = np.asarray(a).reshape(n, n)
    m = n // k
    return a[:m * k, :m * k].reshape(m, k, m, k)


def _mean(a, k, n):
    return _blocks(a, k, n).astype(float).mean((1, 3))


def _max(a, k, n):
    return _blocks(a, k, n).max((1, 3))


def _up(a, k, n, bilinear=False):
    """A work-grid raster back to the pixels (n, n): blocks repeated (or bilinear), the trimmed edge from the last block."""
    a = np.asarray(a)
    if bilinear:
        m = a.shape[0]
        t = (np.arange(n) + 0.5) / k - 0.5
        i0 = np.clip(np.floor(t).astype(int), 0, m - 2) if m > 1 else np.zeros(n, int)
        i1 = np.minimum(i0 + 1, m - 1)
        w = np.clip(t - i0, 0, 1)
        r = a[i0] * (1 - w)[:, None] + a[i1] * w[:, None]
        return r[:, i0] * (1 - w)[None, :] + r[:, i1] * w[None, :]
    big = np.repeat(np.repeat(a, k, 0), k, 1)
    pad = n - big.shape[0]
    return np.pad(big, ((0, pad), (0, pad)), mode="edge") if pad > 0 else big[:n, :n]


def coarse_receiver(rec_slots, area, k, n):
    """D8 slots (uint8, (m, m)) of the work grid from the pixels' receivers: each block's outlet (its pixel of most drainage area)
    is followed down the pixels' own channel until it leaves the block; the block it enters is the receiver."""
    m = n // k
    s = np.asarray(rec_slots).ravel().astype(int)
    kk = s + (s >= 4)
    i = np.arange(n * n)
    r, c = i // n, i % n
    rec = np.where(s == D8_NONE, -1, (r + kk // 3 - 1) * n + (c + kk % 3 - 1))
    rec = np.where((r + kk // 3 - 1 < 0) | (r + kk // 3 - 1 >= n) | (c + kk % 3 - 1 < 0) | (c + kk % 3 - 1 >= n), -1, rec)
    ar = _blocks(area, k, n).transpose(0, 2, 1, 3).reshape(m, m, k * k)
    j = ar.argmax(2)
    br, bc = np.divmod(np.arange(m * m), m)
    cur = ((br * k + j.ravel() // k) * n + (bc * k + j.ravel() % k)).astype(np.int64)
    home = np.arange(m * m)
    out = np.full(m * m, -1, np.int64)
    active = np.ones(m * m, bool)

    def block_of(p):
        pr_, pc_ = p // n, p % n
        ok = (pr_ < m * k) & (pc_ < m * k)
        return np.where(ok, (pr_ // k) * m + pc_ // k, -2)
    for _ in range(8 * k):
        if not active.any():
            break
        nxt = rec[cur]
        gone = active & (nxt < 0)
        active &= ~gone
        b = block_of(np.maximum(nxt, 0))
        left = active & (b != home)
        out[left] = b[left]
        active &= ~left
        cur = np.where(active, nxt, cur)
    out = np.where(out < -1, -1, out)
    dr, dc = out // m - home // m, out % m - home % m
    ok = (out >= 0) & (np.abs(dr) <= 1) & (np.abs(dc) <= 1) & (out != home)
    sl = 3 * (dr + 1) + (dc + 1)
    return np.where(ok, sl - (sl > 4), D8_NONE).astype(np.uint8).reshape(m, m)


def _work_inputs(L, k, n):
    """The layers HU needs for its region-scale parts, on the work grid."""
    m = n // k
    w = np.asarray(L["water"]).reshape(n, n)
    cnt = [(_blocks(w, k, n) == v).sum((1, 3)) for v in (0, 1, 2)]
    water = np.argmax(np.stack(cnt), 0).astype(np.uint8)
    out = {"elevation": _mean(L["elevation"], k, n), "water": water,
           "ice": _mean(L["ice"], k, n), "discharge": _max(L["discharge"], k, n),
           "temperature_jul": _mean(L["temperature_jul"], k, n), "temperature_jan": _mean(L["temperature_jan"], k, n),
           "precipitation": _mean(L["precipitation"], k, n), "lake_depth": _mean(L["lake_depth"], k, n),
           "wetland": np.where(_mean(np.asarray(L["wetland"]) == 2, k, n) >= 0.5, 2, 0),
           "lake_kind": _max(L["lake_kind"], k, n),
           "receiver": coarse_receiver(L["receiver"], L["drainage_area"], k, n)}
    assert out["elevation"].shape == (m, m)
    return out


def _fine_fresh_sources(L, n):
    """The fresh-water sources at the pixels (humanuse's rule): perennial river, fresh lake, wetland."""
    water = np.asarray(L["water"]).ravel()
    q = np.asarray(L["discharge"], float).ravel()
    precip = np.asarray(L["precipitation"], float).ravel()
    lake = (water == 2) & (np.asarray(L["lake_kind"]).ravel() != 2)
    river = (water == 0) & ((q >= HU.RIVER_PERENNIAL_Q["zoom"]) & ((precip >= HU.ARID_MM) | (q >= HU.ARID_Q)))
    return (river | lake | ((water == 0) & (np.asarray(L["wetland"]).ravel() == 2))).reshape(n, n)


def _inherit_pass(pa, pr, pc, n):
    """The parent's pass marks: each parent pass pixel puts its class and height on the fine pixel nearest its centre."""
    cls, hgt = np.zeros(n * n, np.uint8), np.zeros(n * n, int)
    if "pass" not in pa.L:
        return cls.reshape(n, n), hgt.reshape(n, n)
    pidx = pa.index(pr, pc)
    pcls = np.asarray(pa.L["pass"]).ravel()
    sel = np.flatnonzero(pcls[pidx] > 0)
    if sel.size:
        prow, pcol = np.divmod(pidx[sel], pa.nx)
        d = (pr[sel] - prow) ** 2 + (pc[sel] - pcol) ** 2
        o = np.lexsort((d, pidx[sel]))
        sel, pidx_s = sel[o], pidx[sel][o]
        first = np.r_[True, pidx_s[1:] != pidx_s[:-1]]
        pick = sel[first]
        cls[pick] = pcls[pidx[pick]]
        if "pass_height" in pa.L:
            hgt[pick] = np.asarray(pa.L["pass_height"]).ravel()[pidx[pick]]
    return cls.reshape(n, n), hgt.reshape(n, n)


def make(layers: dict, *, n: int, res: float, nu, pix_lat, tilt: float, falls: list, pa, pr, pc, size_km: float,
         world: dict, seed: int, lat: float, lon: float, up, log=print, center: dict | None = None) -> dict:
    """The fine zoom's missing layers ((n, n) arrays) from its finished ones (`layers`: flat or (n, n))."""
    L = {kk: np.asarray(v).reshape(n, n) for kk, v in layers.items()}
    out: dict = {}
    # inherited: the parent's class on the nearest parent pixel
    if "barrier_island" in pa.L:
        bi = pa.nearest("barrier_island", pr, pc).reshape(n, n).astype(np.uint8)
        wat = L["water"]
        out["barrier_island"] = np.where(((bi == 1) & (wat == 0)) | ((bi >= 2) & (wat == 1)), bi, 0).astype(np.uint8)
    else:
        out["barrier_island"] = np.zeros((n, n), np.uint8)
    L["barrier_island"] = out["barrier_island"]
    if "glacial_form" in pa.L:
        out["glacial_form"] = np.where(L["water"] == 0, pa.nearest("glacial_form", pr, pc).reshape(n, n), 0).astype(np.uint8)
    # human use
    falls_px = [(int(f["px"][0]), int(f["px"][1])) for f in falls if "px" in f]
    k = work_factor(res, n)
    px_parts = ("nav", "fertile") if k > 1 else HU.ZOOM_PARTS
    if size_km < PASS_MIN_WINDOW_KM:
        px_parts = tuple(p for p in px_parts if p != "pass")
    out.update(HU.zoom_layers(L, res, falls_px, px_parts))
    if k > 1:
        Lw = _work_inputs(L, k, n)
        wparts = ("harbour", "fresh") + (("pass",) if size_km >= PASS_MIN_WINDOW_KM else ())
        w = HU.zoom_layers(Lw, res * k, (), wparts)
        out["harbour"] = np.where(L["water"] == 1, _up(w["harbour"], k, n), 0).astype(np.uint8)
        fkm = np.where(_fine_fresh_sources(L, n), 0.0, _up(w["fresh_km"], k, n, bilinear=True))
        fr_ = HU.FRESH_REACH["zoom"]
        out["fresh_km"] = (np.round(fkm * 10) / 10).astype(np.float32)
        out["fresh_water"] = np.select([fkm <= fr_[0], fkm <= fr_[1], fkm <= fr_[2]], [3, 2, 1], 0).astype(np.uint8)
        out["spring"] = np.where(L["water"] == 0, _up(w["spring"], k, n), 0).astype(np.uint8)
        if "pass" in w:
            pc_, ph_ = _up(w["pass"], k, n), _up(w["pass_height"], k, n)
            # (a pass is a point: one fine pixel at the work pixel's centre, not a block of them)
            mark = np.zeros((n, n), bool)
            mark[k // 2::k, k // 2::k] = True
            out["pass"], out["pass_height"] = np.where(mark, pc_, 0).astype(np.uint8), np.where(mark, ph_, 0)
    if size_km < PASS_MIN_WINDOW_KM:
        out["pass"], out["pass_height"] = _inherit_pass(pa, pr, pc, n)
    for kk_, v in out.items():
        L[kk_] = v
    # game attributes
    out.update(GA.zoom_layers(L, res, pix_lat, nu, tilt))
    # coast (zoom.coast: km windows; the world's coast classes and the sea state)
    meta = {"res_km": res, "nx": n, "ny": n, "seed": seed,
            "center": center or {"lat": lat, "lon": lon, **({"up": up} if up else {})}}
    cst = ZC.build(world, meta, {**L, **{kk_: v for kk_, v in out.items()}}, seed=seed)
    for kk_ in ("coast_type", "nav_hazard", "shore_form"):
        out[kk_] = cst["layers"][kk_]
    return {"layers": out, "coast": {"features": cst["features"], "stats": cst["stats"]}}
