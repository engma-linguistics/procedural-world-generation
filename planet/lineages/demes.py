"""Demes (PW-981): each people's land cut into regional populations, followed through time into a dated tree.

A people's range is one presence field in the history: humans on three continents are one community. This pass reads a
finished peoples run (its stored frames) and, per frame, cuts each people's occupied cells into demes, regional
populations, wherever open sea, hard country (mountains, desert, deep forest, ice) or sheer distance separate them. It then
follows them from frame to frame: when a deme splits off, fuses with another, dies out, and which demes touch.

Output only, like contacts.py: nothing in the history is read back or changed. Written into the run directory:
`demes.json` (the tree, the events, the contact series per deme pair), `layers/demes.bin` (per frame, the deme of each
cell's leading people; 65535 none) and `meta.demes` in run.json (a summary, the file names and the constants).

How a frame is cut (per people):
- Occupied cells: the cell's leading people (peoples_whole), its people with most heads (mix_lead), and its second people
  by heads where at least SECOND_MIN % of the cell (mix_second). Frames store no fuller presence (see the caveat below).
- Travel cost: entering a land cell costs CORR_EASY / corridor (crossing.corridor, the history's own contact value from
  this frame's land, rain, trees, ice and the world's rivers): 1 on a coast, ~1.6 on open lowland, 4-5 in desert or
  mountains, 8 on ice. Open sea up to SEA_KM wide is crossed at SEA_COST per cell (canoes over a strait, one population
  either side); a wider gap cuts the people in two.
- Founder chains: the cells of each deme in the frame before keep its label; newly settled cells take the label of the
  cheapest-to-reach labelled cell (a front carries its parent's name); land reached by no path (a long crossing) starts
  a new deme whose parent is the nearest deme of that people (spread.nearest_label), if it is at least MIN_CELLS.
- Splits: a deme whose land falls apart (rising sea, a front dying back) splits along the gap: the largest piece keeps its
  id, each other piece of MIN_CELLS or more is a new deme ("split by a gap"). A deme whose travel-cost diameter passes
  SPLIT_KM splits in two (isolation by distance): the half holding its oldest cells keeps the id, the other half buds off.
- Fusions: two touching demes of a people fuse when their diameters together are under FUSE_KM (a range that shrank back
  or a land bridge reconnecting two small populations); the older keeps its id.
- Extinction: a deme with no cells left ends at that frame.
- A new people's first demes take as parent the deme (of any people) that held most of their cells the frame before.
Contacts: per frame, per pair of demes (of the same or of different peoples), the land edges where the leading peoples of
two neighbouring cells are those demes, and the cells where one leads and the other is the second people.

Caveats: time resolution is the frame spacing (0.5 kyr in the recent pass, 4 kyr in the glacial zoom); ancestry is
inferred from range change; a people that rarely leads or comes second in a cell is underseen (frames keep only the
leading two peoples per cell); the thresholds are in "easy km" (coast-equivalent travel) and are crude."""

from __future__ import annotations

import heapq
import json
import time
from pathlib import Path

import numpy as np
from numba import njit

from .. import store as S
from .. import timeline as T
from ..geo import is_land
from ..grid import shared_grid
from .crossing import corridor
from .history.tags import _tags
from .spread import graph_dist, nearest_label

WINDOW_KYR = 300.0  # frames this recent are cut (the glacial zoom and the recent pass; the deep keyframes are Myr apart)
SECOND_MIN = 10  # % of the cell's heads at which the second people (mix_second) counts as living there
CORR_EASY = 0.8  # the corridor value of a coast: one km of coast costs one "easy km"
COST_MAX = 3.0  # (the dearest land cell: ice, in easy km per km)
COST_POW = 0.5  # travel cost = (CORR_EASY / corridor) ** COST_POW: hard country slows, it does not wall off (the gaps and the distance do)
SEA_KM = 150.0  # open sea a people crosses as one population (a strait); wider gaps cut it
SEA_COST = 2.0  # easy km per km of that sea (a sea people: 1 on its own sea)
SPLIT_KM = 7000.0  # a deme wider than this (travel-cost diameter, easy km) splits in two: ~5,500 km of open lowland, 7,000 of coast
FUSE_KM = 4000.0  # two touching demes of a people whose diameters sum to less fuse
MIN_CELLS = 40  # a piece cut off becomes its own deme only from this many cells (~125,000 km² at L7); smaller ones stay with theirs
SPLIT_ITER = 8  # (distance splits per deme per frame at most)
SERIES_KEEP = 24  # points of a deme's or a pair's series kept (the rest thinned evenly)
PAIRS_KEEP = 3000  # deme pairs kept in demes.json (the most contact first)
NONE = 65535


# -- numba kernels ------------------------------------------------------------------------------------
@njit(cache=True)
def grow(lab, dist, grp, lab_grp, cost, step_km, nbr_off, nbr_idx):
    """Multi-source Dijkstra with labels: the cells with lab >= 0 are the sources (at dist); a label L may enter cell j only
    if grp[j] == lab_grp[L] (grp -1: no one). Entering j costs cost[j] * step_km. lab and dist are updated in place."""
    n = lab.shape[0]
    hq = [(0.0, 0)]
    hq.pop()
    for i in range(n):
        if lab[i] >= 0:
            hq.append((dist[i], i))
        else:
            dist[i] = np.inf
    heapq.heapify(hq)
    while len(hq):
        di, i = heapq.heappop(hq)
        if di > dist[i]:
            continue
        g = lab_grp[lab[i]]
        for k in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[k]
            if grp[j] != g:
                continue
            v = di + cost[j] * step_km
            if v < dist[j]:
                dist[j] = v
                lab[j] = lab[i]
                heapq.heappush(hq, (v, j))
    return lab, dist


@njit(cache=True)
def group_argmax(lab, val, nl):
    """Per label 0..nl-1: the cell with the largest finite val (-1 none) and that value."""
    best = np.full(nl, -1, np.int64)
    bv = np.full(nl, -np.inf)
    for i in range(lab.shape[0]):
        L = lab[i]
        if L >= 0 and np.isfinite(val[i]) and val[i] > bv[L]:
            bv[L] = val[i]
            best[L] = i
    return best, bv


@njit(cache=True)
def touching(cells, lab, nbr_off, nbr_idx):
    """The pairs of different labels on neighbouring cells among `cells` (lo * 65535 + hi; repeats kept)."""
    out = np.empty(0, np.int64)
    buf = []
    for i in cells:
        a = lab[i]
        for k in range(nbr_off[i], nbr_off[i + 1]):
            b = lab[nbr_idx[k]]
            if b >= 0 and b > a:
                buf.append(a * 65535 + b)
    if len(buf):
        out = np.array(buf, np.int64)
    return out


# -- per frame -------------------------------------------------------------------------------------------
class Deme:
    __slots__ = ("id", "line", "parent", "born", "how", "ended", "end_how", "into", "series", "peak", "peak_at", "first_cells", "settled", "at")

    def __init__(self, id_, line, parent, born, how):
        self.id, self.line, self.parent, self.born, self.how = id_, line, parent, born, how
        self.ended = None
        self.end_how = None
        self.into = None
        self.series: list = []
        self.peak = 0
        self.peak_at = None
        self.first_cells = None
        self.settled = None  # (a piece cut off by a gap: when its land was first settled)
        self.at = None  # (lat, lon, present landmass rank) at its peak, then at its last frame


class Demes:
    def __init__(self, grid, lines: list[dict], cell_km: float, rank: np.ndarray | None = None):
        self.g = grid
        self.ids = [l["id"] for l in lines]
        self.rank = np.full(grid.n, -1, np.int64) if rank is None else rank  # (the present landmass of each cell, by size; for the names)
        self.lines = lines
        self.cell_km = cell_km
        self.hs = max(1, int(round(SEA_KM / cell_km / 2)))  # (sea cells reached from either shore: a gap of 2 hs is crossed)
        n = grid.n
        self.lab = {}  # line index -> deme id per cell (-1), the frame before
        self.since = {}  # line index -> kyr ago each cell has been held under its label (nan)
        self.occ_prev = {}
        self.diam = {}  # deme id -> its diameter at the last frame (easy km)
        self.demes: list[Deme] = []
        self.events: list[dict] = []
        self.pairs: dict[tuple, dict] = {}
        self.prev_map = np.full(n, -1, np.int64)  # the deme of each cell's leading people, the frame before
        la, lo = np.radians(grid.lat), np.radians(grid.lon)
        self.xyz = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1)
        self.src, self.dst = grid.nbr_src, grid.nbr_idx
        self.agos: list[float] = []

    # deme bookkeeping
    def _new(self, line, parent, ago, how, cells=None):
        d = Deme(len(self.demes), line, parent, ago, how)
        self.demes.append(d)
        if parent is not None and how != "first":
            self._event(ago, how, d.id, parent, cells)
        return d.id

    def _centre(self, cells):
        c = self.xyz[cells].mean(0)
        nr = float(np.linalg.norm(c))
        if nr < 1e-9:
            return 0.0, 0.0
        c = c / nr
        return round(float(np.degrees(np.arcsin(np.clip(c[2], -1, 1)))), 1), round(float(np.degrees(np.arctan2(c[1], c[0]))), 1)

    def _event(self, ago, kind, deme, other, cells):
        lat, lon = self._centre(cells) if cells is not None and len(cells) else (None, None)
        self.events.append({"ago_kyr": round(ago, 3), "kind": kind, "deme": deme, "other": other, "lat": lat, "lon": lon,
                            "cells": None if cells is None else int(len(cells))})

    def update(self, ago: float, occ_by_line: dict, cost: np.ndarray, land: np.ndarray, lead: np.ndarray, second: np.ndarray):
        """occ_by_line: line index -> occupied mask; lead/second: the line index of each cell's leading / second people (-1)."""
        g, n = self.g, self.g.n
        self.agos.append(round(ago, 3))
        step = self.cell_km
        cmap = np.full(n, -1, np.int64)  # (lead deme per cell, this frame)
        smap = np.full(n, -1, np.int64)
        self.lab0, self.occ0 = dict(self.lab), dict(self.occ_prev)  # (the frame before, for a new people's parent)
        for k in sorted(set(occ_by_line) | set(self.lab)):
            O = occ_by_line.get(k)
            old = self.lab.get(k)
            if O is None or not O.any():
                if old is not None:
                    for d in np.unique(old[old >= 0]):
                        self._end(int(d), ago, "extinct")
                    del self.lab[k], self.since[k]
                    self.occ_prev.pop(k, None)
                continue
            if old is not None and k in self.occ_prev and np.array_equal(O, self.occ_prev[k]):
                lab = old  # (nothing moved: the same demes)
            else:
                lab = self._cut(k, O, old, ago, np.where(O & ~land, 1.0, cost), land, step)
            self.lab[k] = lab
            self.occ_prev[k] = O
            on = O & (lab >= 0)
            cmap = np.where(on & (lead == k), lab, cmap)
            smap = np.where(on & (second == k), lab, smap)
            cells = np.flatnonzero(O & (lab >= 0))
            ids, inv, cnt = np.unique(lab[cells], return_inverse=True, return_counts=True)
            xyz = np.stack([np.bincount(inv, weights=self.xyz[cells, i], minlength=len(ids)) for i in range(3)], 1)
            rk = self.rank[cells]
            rmode = {}
            if len(cells):
                u, c = np.unique(inv * 65536 + rk + 1, return_counts=True)
                for x, y in sorted(zip(u.tolist(), c.tolist()), key=lambda q: q[1]):
                    rmode[x // 65536] = x % 65536 - 1
            for q, (d, c) in enumerate(zip(ids.tolist(), cnt.tolist())):
                dm = self.demes[d]
                dm.series.append((round(ago, 3), int(c)))
                if dm.first_cells is None:
                    dm.first_cells = int(c)
                v = xyz[q] / (np.linalg.norm(xyz[q]) or 1)
                at = (round(float(np.degrees(np.arcsin(np.clip(v[2], -1, 1)))), 1), round(float(np.degrees(np.arctan2(v[1], v[0]))), 1), rmode.get(q, -1))
                if c > dm.peak:
                    dm.peak, dm.peak_at = int(c), round(ago, 3)
                    dm.at = at
                if abs(ago) < 1e-9:
                    dm.at = at  # (alive at the present: where it is now)
        self._contacts(ago, cmap, smap, land)
        self.prev_map = cmap
        return cmap

    def _end(self, d, ago, how, into=None):
        dm = self.demes[d]
        if dm.ended is None:
            dm.ended, dm.end_how, dm.into = round(ago, 3), how, into
            if how == "extinct":
                self._event(ago, "extinct", d, None, None)
            self.diam.pop(d, None)

    def _cut(self, k, O, old, ago, cost, land, step):
        g, n = self.g, self.g.n
        noff, nidx = g.nbr_off, g.nbr_idx
        near = graph_dist(O, self.hs, noff, nidx)
        P = O | (~land & (near >= 0))  # (the people's cells and the sea it crosses as one population)
        grp = np.where(P, 0, -1).astype(np.int64)
        since = self.since.get(k)
        if since is None:
            since = np.full(n, np.nan)
        since = np.where(O, np.where(np.isnan(since) | ~self._was(k, O), ago, since), np.nan)  # (when each cell was settled)
        lab = np.where(O & (old >= 0), old, -1).astype(np.int64) if old is not None else np.full(n, -1, np.int64)
        lost = set(np.unique(old[old >= 0]).tolist()) - set(np.unique(lab[lab >= 0]).tolist()) if old is not None else set()
        for d in lost:
            self._end(int(d), ago, "extinct")
        dist = np.zeros(n)
        nl = len(self.demes) + 1
        if (lab >= 0).any():
            lab, dist = grow(lab, dist, grp, np.zeros(nl + n, np.int64), cost, step, noff, nidx)
        # land reached by no path: new demes (or fragments of the nearest one). (Cells by component, from one sort.)
        comp, nc = g.components(P)
        pc = np.flatnonzero(P)
        srt = pc[np.argsort(comp[pc], kind="stable")]
        cs = comp[srt]
        cuts = np.searchsorted(cs, np.arange(nc + 1))
        members = lambda c: srt[cuts[c]:cuts[c + 1]]  # noqa: E731
        un = P & (lab < 0)
        if un.any():
            had = (lab >= 0).any()
            near_lab = nearest_label(lab, np.ones(n, np.bool_), noff, nidx) if had else lab
            ids, cnt = np.unique(comp[un & O], return_counts=True)
            for r, x in enumerate(np.argsort(-cnt)):
                c, sz = int(ids[x]), int(cnt[x])
                mem = members(c)
                cells = mem[O[mem]]
                par = None
                if had:
                    vals = near_lab[cells]
                    vals = vals[vals >= 0]
                    par = int(np.bincount(vals).argmax()) if len(vals) else None
                if sz >= MIN_CELLS or (not had and r == 0):
                    if par is None:
                        xpar = self._from_people(k, cells)
                        d = self._new(k, xpar, ago, "first" if xpar is None else "from_people", cells)
                    else:
                        d = self._new(k, par, ago, "crossing", cells)
                    lab[mem] = d
                    had = True
                elif par is not None:
                    lab[mem] = par
            if (lab[pc] < 0).any():  # (small pieces of a new people with no deme yet: the nearest one's)
                lab = np.where(P & (lab < 0), nearest_label(lab, np.ones(n, np.bool_), noff, nidx), lab)
        # splits along a gap: a deme spread over several pieces of the people's land
        oc = np.flatnonzero(O)
        key = lab[oc] * (nc + 1) + comp[oc]
        u, cnt = np.unique(key, return_counts=True)
        dl, dc = u // (nc + 1), u % (nc + 1)
        multi = np.flatnonzero(np.r_[dl[1:] == dl[:-1], False] | np.r_[False, dl[1:] == dl[:-1]])
        for d in np.unique(dl[multi]):
            m = dl == d
            pcs = sorted(zip(cnt[m].tolist(), dc[m].tolist()), reverse=True)
            for sz, c in pcs[1:]:
                if sz < MIN_CELLS:
                    continue
                mem = members(c)
                mem = mem[lab[mem] == d]
                cells = mem[O[mem]]
                nd = self._new(k, int(d), ago, "split_gap", cells)
                self.demes[nd].settled = round(float(np.nanmax(since[cells])), 3)  # (the piece was settled then; split off now)
                lab[mem] = nd
        # diameters, fusions, then splits by distance (all the wide demes of the people at once, a few rounds)
        D, ends = self._diameters(lab, P, cost, step)
        lab, fused = self._fuse(k, lab, P, D, ago)
        if fused:
            D, ends = self._diameters(lab, P, cost, step)
        for _ in range(SPLIT_ITER):
            big = [d for d, v in D.items() if v > SPLIT_KM]
            if not big:
                break
            lab, touched = self._halve(k, big, ends, lab, P, O, cost, step, since, ago)
            if not touched:
                break
            D2, e2 = self._diameters(lab, P, cost, step, touched)
            D.update(D2)
            ends.update(e2)
            for d in big:
                if d not in touched:
                    D[d] = 0.0  # (could not be halved: leave it)
        self.diam.update(D)
        self.since[k] = since
        return lab

    def _from_people(self, k, cells):
        """The deme a new people's first deme arose from: of its parent people (the tree's) on these cells or nearest them
        the frame before, else whichever deme led most of these cells then; None if nobody did."""
        pars = {self.ids.index(p) for p in (self.lines[k].get("parents") or []) if p in self.ids}
        if pars:
            for q in pars:
                lq = self.lab0.get(q)
                if lq is None:
                    continue
                v = lq[cells]
                v = v[v >= 0]
                if len(v):
                    return int(np.bincount(v).argmax())
            for q in pars:  # (the parent's nearest deme: its range need not overlap the child's first cells)
                lq = self.lab0.get(q)
                if lq is not None and (lq >= 0).any():
                    near = nearest_label(np.where(self.occ0[q], lq, -1), np.ones(self.g.n, np.bool_), self.g.nbr_off, self.g.nbr_idx)
                    return int(np.bincount(near[cells][near[cells] >= 0]).argmax()) if (near[cells] >= 0).any() else None
        pm = self.prev_map[cells]
        pm = pm[pm >= 0]
        return int(np.bincount(pm).argmax()) if len(pm) else None

    def _was(self, k, O):
        prev = self.occ_prev.get(k)
        return np.zeros_like(O) if prev is None else prev

    def _diameters(self, lab, P, cost, step, only=None):
        """Per deme in lab (or in `only`): its travel-cost diameter, easy km, and the two ends of it (two sweeps of a Dijkstra
        kept inside each deme's cells): ({deme: km}, {deme: (a, b)})."""
        g, n = self.g, self.g.n
        nl = len(self.demes)
        mine = P & (lab >= 0)
        if only is not None:
            mine &= np.isin(lab, np.fromiter(only, np.int64))
        ids = np.unique(lab[mine])
        if not len(ids):
            return {}, {}
        grp = np.where(mine, lab, -1).astype(np.int64)
        lg = np.arange(nl, dtype=np.int64)
        first = np.full(nl, -1, np.int64)
        cells = np.flatnonzero(mine)
        first[lab[cells[::-1]]] = cells[::-1]  # (the lowest cell of each deme)
        a = None
        ends = {}
        for sweep in range(2):
            s = np.full(n, -1, np.int64)
            src = first[ids] if a is None else a[ids]
            ok = src >= 0
            s[src[ok]] = ids[ok]
            l2, dd = grow(s, np.zeros(n), grp, lg, cost, step, g.nbr_off, g.nbr_idx)
            prev = a
            a, bv = group_argmax(l2, dd, nl)
        D = {}
        for d in ids.tolist():
            D[int(d)] = float(bv[d]) if np.isfinite(bv[d]) else 0.0
            ends[int(d)] = (int(prev[d]), int(a[d]))
        return D, ends

    def _fuse(self, k, lab, P, D, ago):
        u = np.unique(touching(np.flatnonzero(P & (lab >= 0)), lab, self.g.nbr_off, self.g.nbr_idx))
        if not len(u):
            return lab, False
        cand = sorted(((D.get(int(x // NONE), 0) + D.get(int(x % NONE), 0), int(x // NONE), int(x % NONE)) for x in u), key=lambda x: x[0])
        gone = set()
        for tot, a, b in cand:
            if tot >= FUSE_KM:
                break
            if a in gone or b in gone:
                continue
            keep, lose = (a, b) if self.demes[a].born >= self.demes[b].born else (b, a)
            cells = np.flatnonzero(lab == lose)
            lab = np.where(lab == lose, keep, lab)
            self._end(lose, ago, "fused", keep)
            self._event(ago, "fusion", keep, lose, cells)
            gone |= {a, b}
        return lab, bool(gone)

    def _halve(self, k, big, ends, lab, P, O, cost, step, since, ago):
        """Split each deme in `big` in two from the two ends of its diameter (one Dijkstra for all); the half with its oldest
        cells keeps the id, the other buds off. Returns (lab, the demes touched: old and new ids)."""
        g, n = self.g, self.g.n
        nl = len(self.demes)
        tmp = {d: nl + i for i, d in enumerate(big)}  # (a temporary label for each b side)
        lg = np.concatenate([np.arange(nl, dtype=np.int64), np.array(big, np.int64)])
        sel = P & np.isin(lab, np.array(big, np.int64))
        grp = np.where(sel, lab, -1).astype(np.int64)
        s = np.full(n, -1, np.int64)
        for d in big:
            a, b = ends[d]
            if a >= 0 and b >= 0 and a != b:
                s[a], s[b] = d, tmp[d]
        l2, _ = grow(s, np.zeros(n), grp, lg, cost, step, g.nbr_off, g.nbr_idx)
        on = sel & O
        touched = set()
        for d in big:
            h0, h1 = sel & (l2 == d), sel & (l2 == tmp[d])
            n0, n1 = int((h0 & O).sum()), int((h1 & O).sum())
            if n0 < MIN_CELLS or n1 < MIN_CELLS:
                continue
            age0 = float(np.nanmean(since[h0 & on])) if n0 else 0.0
            age1 = float(np.nanmean(since[h1 & on])) if n1 else 0.0
            bud = h1 if age0 >= age1 else h0
            nd = self._new(k, d, ago, "split_distance", np.flatnonzero(bud & O))
            lab = np.where(bud, nd, lab)
            touched |= {d, nd}
        return lab, touched

    def _contacts(self, ago, cmap, smap, land):
        s, t = self.src, self.dst
        a, b = cmap[s], cmap[t]
        e = (a >= 0) & (b >= 0) & (a < b) & land[s] & land[t]
        rec = {}
        if e.any():
            u, c = np.unique(a[e] * NONE + b[e], return_counts=True)
            for x, y in zip(u.tolist(), c.tolist()):
                rec[(x // NONE, x % NONE)] = [y, 0]
        m = (cmap >= 0) & (smap >= 0) & (cmap != smap)
        if m.any():
            lo, hi = np.minimum(cmap[m], smap[m]), np.maximum(cmap[m], smap[m])
            u, c = np.unique(lo * NONE + hi, return_counts=True)
            for x, y in zip(u.tolist(), c.tolist()):
                rec.setdefault((x // NONE, x % NONE), [0, 0])[1] = y
        for key, (bd, sh) in rec.items():
            r = self.pairs.setdefault(key, {"first": ago, "series": [], "peak": 0})
            r["series"].append((round(ago, 3), bd, sh))
            r["peak"] = max(r["peak"], bd + sh)
            r["last"] = ago


# -- the run -------------------------------------------------------------------------------------------
def _thin(s: list, k: int) -> list:
    return s if len(s) <= k else [s[int(round(i))] for i in np.linspace(0, len(s) - 1, k)]


def peoples_of(lines: list[dict]) -> list[int]:
    """The lines cut into demes: whole peoples (no groups, templates or overlays)."""
    return [l["index"] for l in lines if not l.get("group_of") and not l.get("overlay") and l.get("origin") != "template"]


def occupied(pw, ml, ms, mss, k) -> np.ndarray:
    return (pw == k) | (ml == k) | ((ms == k) & (mss >= SECOND_MIN))


def derive(run_dir: Path, window_kyr: float = WINDOW_KYR) -> dict:
    """The demes of a stored peoples run: {"layer": (frames, cells) uint16, "doc": demes.json, "summary": meta.demes}."""
    t0 = time.time()
    run_dir = Path(run_dir)
    run, arr = T.load_frames(run_dir, ("elevation", "ice", "precipitation", "climate", "tree_cover", "peoples_whole",
                                        "mix_lead", "mix_second", "mix_second_share"))
    m = run["meta"]
    lines = m["lineages"]
    g = shared_grid(m["level"])
    n = g.n
    cell_km = float(m["cell_size_km"])
    agos = [max(0.0, -f["t"]) for f in run["frames"]]
    use = [j for j, a in enumerate(agos) if a <= window_kyr + 1e-9 and (j + 1 == len(agos) or agos[j + 1] < a)]  # (a frame repeated: the later)
    flow = None
    if m.get("world"):
        try:
            from .. import world as W
            w = W.load(S.find_world(m["world"]))
            flow = w["layers"]["flow"].astype(float) if "flow" in w["layers"] else None
        except SystemExit:
            flow = None
    present_land = is_land(T.frame(run, arr, "elevation", len(agos) - 1), T.frame(run, arr, "ice", len(agos) - 1))
    rank = landmass_rank(g, present_land)
    ks = peoples_of(lines)
    kset = np.zeros(256, bool)
    kset[ks] = True
    dm = Demes(g, lines, cell_km, rank)
    layer = np.full((len(agos), n), NONE, np.uint16)
    for j in use:
        env = {nm: T.frame(run, arr, nm, j).astype(float) for nm in ("elevation", "ice", "precipitation", "climate", "tree_cover")}
        env["land"] = is_land(env["elevation"], env["ice"])
        tags = _tags(g, env, chains=False)
        corr = corridor(tags, env, flow, env["land"] & ~present_land)
        cost = np.where(env["land"], np.minimum((CORR_EASY / np.maximum(corr, 1e-3)) ** COST_POW, COST_MAX), SEA_COST)
        pw, ml, ms, mss = (np.asarray(arr[k][j]).astype(np.int64) for k in ("peoples_whole", "mix_lead", "mix_second", "mix_second_share"))
        lead = np.where((pw < 255) & kset[np.minimum(pw, 255)], pw, -1).astype(np.int64)
        second = np.where((ms < 255) & (mss >= SECOND_MIN), ms, -1).astype(np.int64)
        occ = {}
        for k in set(np.unique(pw).tolist()) | set(np.unique(ml).tolist()) | set(np.unique(ms).tolist()):
            if k < 255 and kset[k]:
                o = occupied(pw, ml, ms, mss, k)
                if o.any():
                    occ[k] = o
        cmap = dm.update(agos[j], occ, cost, env["land"], lead, second)
        layer[j] = np.where(cmap >= 0, cmap, NONE).astype(np.uint16)
    return {"layer": layer, **_document(dm, m, g, agos[use[0]] if use else 0.0, time.time() - t0)}


def landmass_rank(g, present_land: np.ndarray) -> np.ndarray:
    """The present landmass of each cell, ranked by size as crossing.Crossings ranks them (meta.present.landmasses[].rank);
    sea cells (and land of a low stand, now under the sea) take the nearest one's."""
    lab, k = g.components(present_land)
    sizes = np.bincount(lab[lab >= 0], minlength=k)
    rk = np.empty(k, np.int64)
    rk[np.argsort(-sizes)] = np.arange(k)
    rank = np.where(lab >= 0, rk[np.maximum(lab, 0)], -1)
    return nearest_label(rank, np.ones(g.n, np.bool_), g.nbr_off, g.nbr_idx)


def _place(at, lms):
    """'the west of <landmass>' for a deme at (lat, lon, landmass rank): the landmass and where on it."""
    if at is None or not lms:
        return None
    la, lo, lm = at
    nm = next((x for x in lms if x["rank"] == lm), None)
    if nm is None:
        return None
    called = nm.get("called") or nm["name"].split(" (")[0]
    dla, dlo = la - nm["lat"], ((lo - nm["lon"] + 180) % 360) - 180
    span = max(np.sqrt(nm["area_mkm2"] * 1e6) / 111.0 / 4, 3.0)  # (a quarter of the landmass's width, degrees)
    dx = dlo * np.cos(np.radians(la))
    ns = "north" if dla > span else "south" if dla < -span else ""
    ew = "east" if dx > span else "west" if dx < -span else ""
    part = f"{ns}-{ew}" if ns and ew else ns or ew
    return f"the {part} of {called}" if part else called


def _document(dm: Demes, m: dict, g, start, secs) -> dict:
    lines = m["lineages"]
    ids = [l["id"] for l in lines]
    lms = (m.get("present") or {}).get("landmasses") or []
    now: dict[int, int] = {}
    for kk, lab_k in dm.lab.items():
        u, c = np.unique(lab_k[(lab_k >= 0) & dm.occ_prev[kk]], return_counts=True)
        now.update(zip(u.tolist(), c.tolist()))
    per_line: dict[int, int] = {}
    demes = []
    for d in dm.demes:
        per_line[d.line] = per_line.get(d.line, 0) + 1
        place = _place(d.at, lms)
        nm = f"{ids[d.line].replace('_', ' ')} {per_line[d.line]}"
        demes.append({"id": d.id, "people": ids[d.line], "n": per_line[d.line], "name": nm + (f" ({place})" if place else ""), "short": nm,
                      "place": place, "lat": d.at[0] if d.at else None, "lon": d.at[1] if d.at else None,
                      "parent": d.parent, "parent_people": None if d.parent is None else ids[dm.demes[d.parent].line],
                      "born_kyr": d.born, "how": d.how, "settled_kyr": d.settled, "ended_kyr": d.ended, "end": d.end_how, "into": d.into,
                      "peak_cells": d.peak, "peak_kyr": d.peak_at, "cells_now": now.get(d.id, 0) if d.ended is None else 0,
                      "series": [list(x) for x in _thin(d.series, SERIES_KEEP)]})
    cols = _colors(demes, lines)
    for x, c in zip(demes, cols):
        x["color"] = c
    pairs = []
    for (a, b), r in dm.pairs.items():
        s = r["series"]
        now = s[-1] if abs(s[-1][0]) < 1e-9 else None
        years = len(s)
        pairs.append({"a": a, "b": b, "same_people": dm.demes[a].line == dm.demes[b].line, "first_kyr": round(r["first"], 3),
                      "last_kyr": round(r["last"], 3), "frames": years, "peak": r["peak"],
                      "border_now": now[1] if now else 0, "shared_now": now[2] if now else 0,
                      "series": [list(x) for x in _thin(s, SERIES_KEEP)]})
    pairs.sort(key=lambda p: -(p["peak"] * p["frames"]))
    pairs = pairs[:PAIRS_KEEP]
    events = sorted(dm.events, key=lambda e: -e["ago_kyr"])
    for e in events:
        e["text"] = _text(e, demes)
    alive = [x for x in demes if x["ended_kyr"] is None]
    by_people = {}
    for x in demes:
        b = by_people.setdefault(x["people"], {"demes": 0, "alive": 0, "splits": 0, "fusions": 0, "extinct": 0, "first_kyr": x["born_kyr"]})
        b["demes"] += 1
        b["alive"] += x["ended_kyr"] is None
        b["extinct"] += x["end"] == "extinct"
        b["first_kyr"] = max(b["first_kyr"], x["born_kyr"])
    for e in events:
        p = demes[e["deme"]]["people"]
        if e["kind"].startswith("split") or e["kind"] == "crossing":
            by_people[p]["splits"] += 1
        if e["kind"] == "fusion":
            by_people[p]["fusions"] += 1
    doc = {"format": "procgen-demes/1", "from_kyr": round(start, 3), "frames": dm.agos, "demes": demes, "events": events, "pairs": pairs}
    summary = {"file": "demes.json", "layer": "demes", "count": len(demes), "alive": len(alive), "events": len(events), "pairs": len(pairs),
               "by_people": by_people, "from_kyr": round(start, 3), "generated_in_s": round(secs, 1),
               "constants": {"window_kyr": WINDOW_KYR, "second_min_pct": SECOND_MIN, "sea_km": SEA_KM, "sea_cost": SEA_COST,
                             "split_km": SPLIT_KM, "fuse_km": FUSE_KM, "min_cells": MIN_CELLS, "corr_easy": CORR_EASY}}
    return {"doc": doc, "summary": summary}


HOW = {"split_gap": "split off {other} along a gap", "split_distance": "budded off {other} (distance)", "crossing": "was founded over the sea from {other}",
       "from_people": "arose from {other}", "fusion": "took in {other}", "extinct": "died out"}


def _text(e, demes):
    d = demes[e["deme"]]
    o = demes[e["other"]]["name"] if e.get("other") is not None else ""
    return f"{d['name']} " + HOW[e["kind"]].format(other=o)


def _colors(demes: list[dict], lines: list[dict]) -> list[str]:
    """Each deme a shade of its people's colour: hue, lightness and saturation stepped in turn (neighbours differ)."""
    import colorsys
    out = []
    col = {l["id"]: l["color"] for l in lines}
    for x in demes:
        c = col.get(x["people"], "#888888").lstrip("#")
        r, gg, b = (int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
        h, l, s = colorsys.rgb_to_hls(r, gg, b)
        i = x["n"] - 1
        h = (h + ((i * 0.618) % 1 - 0.5) * 0.22) % 1
        l = min(0.82, max(0.22, [0.5, 0.36, 0.66, 0.28, 0.58, 0.44, 0.74][i % 7]))
        s = min(1.0, max(0.35, s * [1, 0.8, 0.9, 1, 0.65, 0.95, 0.75][(i // 7) % 7]))
        rr, g2, bb = colorsys.hls_to_rgb(h, l, s)
        out.append("#" + "".join(f"{round(v * 255):02x}" for v in (rr, g2, bb)))
    return out


def write(run_dir: Path, report: bool = True) -> dict:
    """Adds demes.json, layers/demes.bin and meta.demes (+ run.json "layers".demes) to a peoples run; returns meta.demes."""
    run_dir = Path(run_dir)
    d = derive(run_dir)
    S.write_atomic(run_dir / "layers" / "demes.bin", d["layer"].astype("<u2").tobytes())
    S.write_atomic(run_dir / "demes.json", json.dumps(d["doc"], separators=(",", ":")))
    p = run_dir / "run.json"
    run = json.loads(p.read_text())
    run["layers"]["demes"] = {"file": "layers/demes.bin", "dtype": "uint16", "shape": list(d["layer"].shape), "scale": 1, "offset": 0,
                              "transform": None, "units": "", "description": "the deme (regional population, demes.py, PW-981) of the cell's leading people: index into demes.json demes; 65535 none"}
    run["meta"]["demes"] = d["summary"]
    S.write_json(p, run)
    if report:
        with open(run_dir / "run.txt", "a") as f:
            f.write("\n".join(lines_for_report(d["summary"], d["doc"])) + "\n")
    return d["summary"]


def lines_for_report(sm: dict, doc: dict) -> list[str]:
    L = ["", f"## Demes (PW-981): regional populations since {sm['from_kyr']:g} kyr ago: {sm['count']} in all, {sm['alive']} alive, "
             f"{sm['events']} events ({sm['generated_in_s']} s)"]
    for p, b in sorted(sm["by_people"].items(), key=lambda x: -x[1]["alive"]):
        if b["alive"]:
            L.append(f"  {p:<18} {b['alive']:>3} alive of {b['demes']:>3}; {b['splits']} splits, {b['fusions']} fusions, {b['extinct']} died out")
    alive = sorted((x for x in doc["demes"] if x["ended_kyr"] is None), key=lambda x: -x["cells_now"])
    L.append("  -- the largest now")
    L += [f"  {x['name']:<60} {x['cells_now']:>6} cells, since {x['born_kyr']:g} kyr ({x['how']})" for x in alive[:16]]
    return L
