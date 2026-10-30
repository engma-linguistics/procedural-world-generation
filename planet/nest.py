"""A coarser nested grid's view of a fine grid's fields, and back (PW-247).

The grid levels nest (grid._subdivide): cells 0 .. n_k - 1 of a level-(k+1)
grid are the level-k grid's cells, and every other fine cell is the midpoint
of a coarse edge, between two coarse cells. One level down:
  restrict  area-weighted: a coarse cell's Voronoi cell is its own fine cell
            plus half of each midpoint around it (full weighting), each fine
            cell weighted by its area;
  prolong   linear along the coarse edge: a kept cell takes its own coarse
            value, a midpoint the mean of its two parents (the adjoint of
            restrict up to the areas).
Masked variants keep land and sea apart: a land cell restricts from its land
children and prolongs from its land parents (else from both).
Deeper nests repeat one level at a time.

climate_coarse runs climate.compute on the coarser grid for a fine grid's
ground and returns its fields on the fine grid (the run's spin-up climate
at L7 on L6: earth.update_climate, Params.climate_level)."""
from __future__ import annotations

import numpy as np

from . import climate
from .geo import is_land
from .grid import Grid, shared_grid
from .ocean import cell_area_km2

_NEST: dict = {}


def step(fine: Grid) -> dict:
    """One level down from fine (cached): the coarse grid, each fine cell's two parents (p0, p1; a kept cell
    twice itself), and the restriction's weights (half the fine cell's area to each parent)."""
    key = (id(fine), fine.n)
    if key not in _NEST:
        coarse = shared_grid(fine.level - 1)
        nc, n = coarse.n, fine.n
        assert np.array_equal(fine.centers[:nc], coarse.centers), "grids don't nest"
        p0 = np.arange(n)
        p1 = np.arange(n)
        off, idx = fine.nbr_off, fine.nbr_idx
        for i in range(nc, n):
            par = idx[off[i]:off[i + 1]]
            par = par[par < nc]
            assert len(par) == 2, (i, par)
            p0[i], p1[i] = par
        w = 0.5 * cell_area_km2(fine)
        wsum = np.bincount(p0, w, nc) + np.bincount(p1, w, nc)
        _NEST[key] = dict(coarse=coarse, nc=nc, p0=p0, p1=p1, w=w, wsum=wsum)
    return _NEST[key]


def _restrict(s, f, mask=None):
    """f (fine, 1-d) to the coarse grid: area mean over each coarse cell, over mask's cells only (where it has
    none: 0)."""
    w = s["w"] if mask is None else s["w"] * mask
    nc = s["nc"]
    num = np.bincount(s["p0"], w * f, nc) + np.bincount(s["p1"], w * f, nc)
    den = np.bincount(s["p0"], w, nc) + np.bincount(s["p1"], w, nc)
    return num / np.maximum(den, 1e-300)


def _prolong(s, f, cmask=None, fmask=None):
    """Coarse f (1-d, or (nc, k)) to the fine grid; with masks, each fine cell from the parents whose cmask is
    its own fmask (both when neither is)."""
    a, b = f[s["p0"]], f[s["p1"]]
    if cmask is None:
        return 0.5 * (a + b)
    m0 = (cmask[s["p0"]] == fmask).astype(float)
    m1 = (cmask[s["p1"]] == fmask).astype(float)
    none = (m0 + m1) == 0
    m0, m1 = np.where(none, 1.0, m0), np.where(none, 1.0, m1)
    if f.ndim == 2:
        m0, m1 = m0[:, None], m1[:, None]
    return (m0 * a + m1 * b) / (m0 + m1)


def chain(fine: Grid, level: int) -> list[dict]:
    """The steps from fine down to level, finest first."""
    out, g = [], fine
    while g.level > level:
        s = step(g)
        out.append(s)
        g = s["coarse"]
    return out


def climate_coarse(fine: Grid, level: int, elev, dT, tilt, ice, veg=None, rain_start=None) -> dict:
    """climate.compute(fine, elev, dT, tilt, ice, veg=veg, rain_start=rain_start), run on the nested
    level-`level` grid: the ground is restricted to it (a coarse cell is land where at least half its area is,
    at the mean height of its land or of its sea floor, with its land's mean ice; the vegetation's feedbacks are
    its land's means), and the climate prolonged back (masked by land and sea; temperatures through sea level
    by the lapse rate, so a fine cell's height still sets its air; vectors back onto the fine tangent planes; the
    water balance, the lakes' evaporation and the Koppen class again on the fine cells' own climate).
    rain_start: the coarse grid's rain state (the result's "rain_state" is the coarse kernel's)."""
    steps = chain(fine, level)
    e, ice = np.asarray(elev, float), np.asarray(ice, float)
    land = is_land(e, ice)
    masks, e_c, ice_c, veg_c, share = [land], e, np.where(land, ice, 0.0), veg, land.astype(float)
    for s in steps:
        lf = masks[-1]
        share = _restrict(s, share)
        lc = share >= 0.5
        e_c = np.where(lc, np.maximum(_restrict(s, e_c, lf), 1.0), np.minimum(_restrict(s, e_c, ~lf), -1.0))
        ice_c = np.where(lc, _restrict(s, ice_c, lf), 0.0)
        if veg_c is not None:
            veg_c = {k: _restrict(s, np.asarray(v, float), lf) for k, v in veg_c.items()}
        masks.append(lc)
    coarse = steps[-1]["coarse"] if steps else fine
    c = climate.compute(coarse, e_c, dT, tilt, ice_c, veg=veg_c, rain_start=rain_start)
    if not steps:
        return c
    surf_c, bed_c = np.maximum(e_c + ice_c, 0.0), np.maximum(e_c, 0.0)
    air = ("temp", "t_warm", "t_cold", "t_jul", "t_jan")
    out = dict(c)  # (temperatures to sea level for the way up; lists, the coarse rain state, ints: kept or redone)
    out["ground"] = tuple(climate.LAPSE * bed_c + t for t in c["ground"])
    for k in air:
        out[k] = climate.LAPSE * surf_c + c[k]
    for i in range(len(steps) - 1, -1, -1):  # up one level at a time
        s, cm, fm = steps[i], masks[i + 1], masks[i]
        for k, v in list(out.items()):
            if k == "ground":
                out[k] = tuple(_prolong(s, t, cm, fm) for t in v)
            elif k in ("rain_state", "moc_state", "moc_sites") or not isinstance(v, np.ndarray):
                continue
            elif v.dtype.kind != "f":
                continue
            elif v.ndim == 1 and len(v) == s["nc"]:
                out[k] = _prolong(s, v, cm, fm)
            elif v.ndim == 2 and v.shape[0] == s["nc"]:  # (n, 3) vectors
                out[k] = _prolong(s, v, cm, fm)
            elif v.ndim == 2 and v.shape[1] == s["nc"]:  # (k, n) stacks
                out[k] = np.stack([_prolong(s, r, cm, fm) for r in v])
    surf, bed = np.maximum(e + np.where(land, ice, 0.0), 0.0), np.maximum(e, 0.0)
    for k in air:
        out[k] = out[k] - climate.LAPSE * surf
    out["ground"] = tuple(t - climate.LAPSE * bed for t in out["ground"])
    p = fine.centers
    for k, v in out.items():  # vectors back onto the fine cells' tangent planes
        if isinstance(v, np.ndarray) and v.ndim == 2 and v.shape == (fine.n, 3):
            out[k] = v - (v * p).sum(1, keepdims=True) * p
    # the water's books on the fine cells' own temperatures and rain (as compute's last water_balance)
    tune = climate.TUNE
    fb = climate.vegetation_feedbacks(land & (ice <= 0), veg, tune)
    wb = climate.water_balance(fine.lat, out["temp"], out["t_warm"], out["t_cold"], out["p_jul"], out["p_jan"],
                               tilt, tune, fb["w"])
    wb["runoff"] = np.where(land, wb["runoff"], 0.0)
    wb["lake_evap"] = np.where(land, climate.open_water_evap(fine.lat, out["temp"], out["t_warm"], out["t_cold"],
                                                             out["rh_jul"], out["rh_jan"], out["cloud_jul"],
                                                             out["cloud_jan"], tilt, tune), 0.0)
    out.update(wb)
    out["precip"] = 0.5 * (out["p_jul"] + out["p_jan"])
    out["koppen"] = climate.koppen(e, out["temp"], out["t_warm"], out["t_cold"], out["precip"], out["p_jul"],
                                   out["p_jan"], fine.lat, ice)
    return out


def prolong_rain_state(fine: Grid, state: dict | None) -> dict | None:
    """A coarse rain state (climate.compute's rain_state) on the fine grid: the warm start for the first fine
    update after coarse ones (the run's finish window)."""
    if state is None:
        return None
    steps = chain(fine, int(np.log2((state["vap"].shape[-1] - 2) / 10) / 2 + 0.5))
    out = {k: np.asarray(v, float) for k, v in state.items()}
    for s in reversed(steps):
        out = {k: np.stack([_prolong(s, r) for r in v]) for k, v in out.items()}
    return out
