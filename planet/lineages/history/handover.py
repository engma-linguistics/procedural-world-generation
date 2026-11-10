"""The split history on a refined world (PW-1265, lane 267; docs/review/refine-l8/split.md): the deep and glacial history runs on
the time zoom's grid (L7) and the settled window on the refined world's grid (L8).

In plain words: the peoples spread, split and learn their country for millions of years on the coarse grid, as on any L7 world. At the
cut, the first moment a crop could be cultivated (the earliest drawn date of the crops this try has: before it nobody farms, so no
town, state, trade or war can exist), the history's state moves onto the fine grid and the rest of the history, the whole settled
window, runs there on the refined world's own layers.

The move (`hand_over`): the grids nest (an L8 grid is the L7 cells plus a cell on each L7 edge's midpoint, nest.step), so
- a cell's category (who holds it, a landmass, a route, a flag) goes to the fine cells from their first parent (the parent itself
  for a kept cell);
- a quantity per area (a habitat share, a density, a learned acceptance, a crop's knowledge) to the mean of the two parents (nest's
  prolongation: a kept cell keeps its own);
- a people's numbers are split by area: each coarse cell's heads go to its own fine cell and the midpoints round it in proportion to
  the area each takes of it (nest's full weighting: the kept cell two halves, each midpoint one half), and each fine cell's presence
  is its heads over its density and area; heads that would land below the presence floor (EST) go to the parent's own fine cell. The
  totals are kept exactly (tests/test_lineages_split.py);
- what comes from the world and the grid (the goods, the ladder's land, the prey field, the landmasses, the neighbour tables) is made
  again from the fine world, not carried; landmass numbers held in the record are renumbered to the fine world's.
At equal levels nothing here runs.
"""

from __future__ import annotations

import numpy as np

from ... import nest as NE
from ...geo import R_KM, cell_area_km2
from ..spread import EST


class Regrid:
    """Coarse -> fine on nested grids (any number of levels apart): keep (first parent), mean (two-parent mean), split (area)."""

    def __init__(self, coarse, fine):
        assert fine.level > coarse.level and np.array_equal(fine.centers[:coarse.n], coarse.centers), "grids don't nest"
        self.coarse, self.fine = coarse, fine
        self.nc, self.nf = coarse.n, fine.n
        self.chain = list(reversed(NE.chain(fine, coarse.level)))  # (coarsest step first)

    def is_cells(self, x) -> bool:
        return isinstance(x, np.ndarray) and x.ndim >= 1 and x.shape[-1] == self.nc

    def keep(self, x: np.ndarray) -> np.ndarray:
        for s in self.chain:
            x = x[..., s["p0"]]
        return x

    def mean(self, x: np.ndarray) -> np.ndarray:
        dt = x.dtype
        for s in self.chain:
            x = 0.5 * (x[..., s["p0"]] + x[..., s["p1"]])
        return x.astype(dt, copy=False)

    def split(self, x: np.ndarray) -> np.ndarray:
        """An amount per cell (last axis) shared out by area: each coarse cell's amount over its own fine cell (two half-slots) and
        the midpoints round it (one half-slot each), in equal-area half-slots (the history counts every cell of a grid alike,
        geo.cell_area_km2). Totals kept exactly."""
        x = np.asarray(x, float)
        for s in self.chain:
            nc = s["nc"]
            slots = np.bincount(s["p0"], minlength=nc) + np.bincount(s["p1"], minlength=nc)
            per = x / slots
            x = per[..., s["p0"]] + per[..., s["p1"]]
        return x

    def auto(self, x):
        """A cell field by its kind: float -> mean, else keep. Containers are walked (dicts and lists changed in place)."""
        if isinstance(x, np.ndarray):
            if not self.is_cells(x):
                return x
            return self.mean(x) if np.issubdtype(x.dtype, np.floating) else self.keep(x)
        if isinstance(x, dict):
            for k in list(x):
                x[k] = self.auto(x[k])
            return x
        if isinstance(x, list):
            for i, v in enumerate(x):
                x[i] = self.auto(v)
            return x
        if isinstance(x, tuple):
            return tuple(self.auto(v) for v in x)
        return x


def heads_split(R: Regrid, P: np.ndarray, D: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Presences P (lines x coarse cells) at densities D (people/km2, lines x coarse cells) -> (fine presences, fine densities) with
    the same people (presence >= EST x density x the grid's cell area) on every line: heads split by area (Regrid.split) over the
    two-parent mean density; heads that would sit under EST go back to the parent's own fine cell."""
    a_c, a_f = cell_area_km2(R.nc), cell_area_km2(R.nf)
    H = np.where(P >= EST, P, 0.0) * D * a_c
    Df = R.mean(np.asarray(D, float))
    with np.errstate(invalid="ignore", divide="ignore"):
        Hf = R.split(H)
        Pf = np.where(Df > 0, Hf / np.maximum(Df * a_f, 1e-300), 0.0)
    thin = (Pf > 0) & (Pf < EST)
    if thin.any():
        # (one level at a time would be exact for any chain; L7 -> L8 is one: the fine cells 0..nc-1 are the coarse cells themselves)
        s = R.chain[-1] if len(R.chain) == 1 else None
        assert s is not None, "heads_split: one level at a time"
        nc = s["nc"]
        slots = np.bincount(s["p0"], minlength=nc) + np.bincount(s["p1"], minlength=nc)
        per = H / slots
        back = np.zeros_like(H)
        for p in (s["p0"], s["p1"]):
            back += np.stack([np.bincount(p[thin[k]], per[k, p[thin[k]]], nc) for k in range(len(H))]) if H.ndim == 2 else \
                np.bincount(p[thin], per[p[thin]], nc)
        Hf = np.where(thin, 0.0, Hf)
        Hf[..., :nc] += back
        with np.errstate(invalid="ignore", divide="ignore"):
            Pf = np.where(Df > 0, Hf / np.maximum(Df * a_f, 1e-300), 0.0)
    return Pf, Df


def cut_kyr(h) -> float | None:
    """The cut (kyr ago): the earliest drawn date of a first cultivation among this try's crops (animals.Stock.d0; the first step at
    or after it may tame one, so no farming, and no town, state, trade or war, comes before). None without crops: the hand-over is
    then at the last step (the present), the history on the coarse grid to the end."""
    if h.crops is None:
        return None
    d = [s.d0 for s in h.crops.stocks if not s.absent]
    return max(d) if d else None


def _relabel(old: np.ndarray, new: np.ndarray, R: Regrid) -> dict:
    """Coarse landmass number -> fine landmass number: the fine label most of its cells carry on their own fine cells."""
    out = {}
    kept = new[:R.nc]
    for c in np.unique(old[old >= 0]):
        f = kept[(old == c) & (kept >= 0)]
        if len(f):
            out[int(c)] = int(np.bincount(f).argmax())
    return out


def hand_over(h, ps, goods, si: int) -> None:
    """Moves History h onto ps's grid (finer than h's) before its step si: see the module notes. ps: the refined world's Pass;
    goods: its goods (land.goods), or None. h.steps from si on are the fine world's."""
    from .. import crossing as CR
    from .. import ladder as LD
    from . import megafauna as MG

    R = Regrid(h.grid, ps.grid)
    L = h.lines
    # -- the people: heads split by area (megafauna and peoples alike; overlays are a share of their hosts: mean)
    D = np.stack([np.broadcast_to(np.asarray(h.dens_at(k), float), (R.nc,)) if not l.overlay else np.zeros(R.nc)
                  for k, l in enumerate(L)])
    Pf, Df = heads_split(R, h.p, D)
    ov = np.array([l.overlay for l in L])
    Pf[ov] = R.mean(h.p[ov])
    h.handover = {"coarse": h.grid.level, "fine": ps.grid.level,
                  "people_before": float((np.where(h.p >= EST, h.p, 0) * D)[~ov].sum() * cell_area_km2(R.nc))}
    old_label, old_reached = h.cross.label, h.cross.reached
    # -- the dynamic state: by kind (h.p, and what is made again from the fine world, are left out here)
    made_again = {"grid", "ps", "goods", "steps", "cross", "flow", "ladder", "rule", "contacts", "animals", "crops", "p", "tree", "lines",
                  "_deg", "prey_wild", "prey_prod", "sea_food", "_pres", "_overkill", "_dens_memo", "_dAT", "_L", "_Fc"}
    for k, v in list(vars(h).items()):
        if k not in made_again:
            setattr(h, k, R.auto(v))
    h.p = Pf
    if h._Lm is not None:  # (the learned acceptance: one matrix, its rows the lines' views)
        h._L = {k: h._Lm[k] for k in h._L}
    if h._dmap is not None:
        h._dmap = np.ascontiguousarray(R.mean(h._dmap))
    # -- the world and the grid, from the fine world
    h.ps, h.grid, h.goods = ps, ps.grid, goods
    g = h.grid
    h._deg = np.diff(g.nbr_off)
    h.cell_km = g.spacing * R_KM
    h.cell_mkm2 = cell_area_km2(g.n) / 1e6
    h.flow = getattr(ps, "flow", None)
    fine = h._steps(h._glacial_every)  # (the same schedule on the fine world)
    assert len(fine) == len(h.steps) and all(abs(a.ago - b.ago) < 1e-9 for a, b in zip(fine, h.steps)), "the fine world's steps differ"
    h.steps[si:] = fine[si:]
    h._pres = h._overkill = h._dens_memo = None
    h.__dict__.pop("_dens_memo", None)
    h.prey_wild = None
    MG_keep = {k: getattr(h, k) for k in ("_press", "_kill", "_prey", "_food", "_land_now", "_deep_now", "_ago_now", "_first_ago",
                                          "_deep_food")}
    MG.setup(h)  # (the static prey and productivity of the fine world; its per-step state is carried)
    for k, v in MG_keep.items():
        setattr(h, k, v)
    old_ladder = h.ladder
    h.ladder = LD.Ladder(h)  # (the fine world's land; refreshed in full at the next step)
    if old_ladder.ok and h.ladder.ok:
        for k in ("rung", "raid", "barter"):
            setattr(h.ladder, k, R.auto(getattr(old_ladder, k)))
        h.ladder.sh = R.auto(old_ladder.sh)
        h.ladder.drawn, h.ladder.v = old_ladder.drawn, old_ladder.v
    # -- the landmasses: the fine world's present, renumbered in the record
    h.cross = CR.Crossings(g, h.steps[-1].get(), h.cell_km, h.cell_mkm2, getattr(ps, "world_seed", None),
                           getattr(ps, "world_names", None))
    lab = _relabel(old_label, h.cross.label, R)
    h.cross.reached = {lid: {lab.get(m, m): v for m, v in got.items()} for lid, got in old_reached.items()}
    # -- contacts
    c = h.contacts
    if c is not None:
        c.cur, c.prev, c.until = R.keep(c.cur), R.keep(c.prev), R.keep(c.until)
        c._pw = None if c._pw is None else R.mean(c._pw)
        la, lo = np.radians(g.lat), np.radians(g.lon)
        c.xyz = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1)
    # -- domesticated animals and crops: their knowledge and routes carried, their ranges made again on the fine land
    for own in (h.animals, h.crops):
        if own is None:
            continue
        own.homes = {lab.get(m, m): v for m, v in own.homes.items()}
        for s in own.stocks:
            for k, v in list(vars(s).items()):
                if k not in ("h", "a", "owner", "rng"):
                    setattr(s, k, R.auto(v))  # (rd, the knowledge: mean; route: first parent; wild, grow, gk: made again below)
            s._ranged = False  # (a crop's range made again on the fine land at the next step)
            s.landed = {lab.get(m, m) for m in s.landed}
            s.reached = {lab.get(m, m): v for m, v in s.reached.items()}
            for t in s.tamed:
                t["landmass"] = lab.get(t["landmass"], t["landmass"])
    # -- the brakes' seam (and polities in the history, PW-1434): made again on the fine grid; what is not per cell carried
    old = h.rule
    grid_made = {"h", "g", "off", "idx", "src", "ekm", "cell_km2", "dist", "touched", "claimed", "r2a", "r2b", "r2off", "W", "_Fc"}
    h.rule = type(old)(h)
    for k, v in vars(old).items():
        if k not in grid_made:
            setattr(h.rule, k, R.auto(v))
    tech = getattr(h.rule, "tech", None)
    if tech is not None:
        tech.h = h
        if tech.towns is not None:
            tech.towns["_cell_km2"] = float(h.cell_mkm2 * 1e6)
    h.handover["people_after"] = float((np.where(h.p >= EST, h.p, 0) * Df)[~ov].sum() * cell_area_km2(R.nf))


def regrid_frames(frames: list, coarse, fine) -> list:
    """The stored frames before the cut, on the fine grid: every cell layer from the fine cell's first parent (the coarse history's
    picture, cell for cell); the sparse presence likewise."""
    R = Regrid(coarse, fine)
    p0 = R.keep(np.arange(R.nc))
    order = np.argsort(p0, kind="stable")
    starts = np.searchsorted(p0[order], np.arange(R.nc + 1))
    out = []
    def keep(x):
        if R.is_cells(x):
            return R.keep(x)
        if isinstance(x, dict):
            return {k: keep(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return type(x)(keep(v) for v in x)
        return x

    for f in frames:
        pres = f.get("presence")
        f = {k: (v if k == "presence" else keep(v)) for k, v in f.items()}
        if pres is not None:
            pl, pc, pv = pres
            cnt = starts[pc + 1] - starts[pc]
            rep = np.repeat(np.arange(len(pc)), cnt)
            first = np.repeat(np.cumsum(cnt) - cnt, cnt)
            kids = order[starts[pc][rep] + np.arange(len(rep)) - first].astype(pc.dtype)
            o = np.lexsort((kids, pl[rep]))
            f["presence"] = (pl[rep][o], kids[o], pv[rep][o])
        out.append(f)
    return out
