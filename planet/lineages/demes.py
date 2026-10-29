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
- Travel cost: entering a land cell costs (CORR_EASY / corridor) ** COST_POW, at most COST_MAX (crossing.corridor, the
  history's own contact value from this frame's land, rain, trees, ice and the world's rivers): 1 on a coast, ~1.3 on
  open lowland, ~2-2.3 in desert or mountains. Open sea up to SEA_KM wide is crossed at SEA_COST per cell (canoes over a
  strait, one population either side); a wider gap cuts the people in two. A strip of other peoples' land up to NECK_KM
  wide is bridged the same way (a minority's corridor through a range does not cut it).
- Founder chains: the cells of each deme in the frame before keep its label; newly settled cells take the label of the
  cheapest-to-reach labelled cell (a front carries its parent's name); land reached by no path (a long crossing) starts
  a new deme whose parent is the nearest deme of that people (straight line), if it is at least MIN_CELLS.
- Splits: a deme whose land falls apart (rising sea, a front dying back, a neighbour moving in) and stays apart PERSIST
  frames splits along the gap, dated when it opened: the largest piece keeps its id, each other piece of MIN_CELLS or
  more is a new deme ("split by a gap"). Pieces that rejoin sooner are flicker and leave no trace. A deme whose travel-cost diameter passes
  SPLIT_KM splits in two (isolation by distance): the half holding its oldest cells keeps the id, the other half buds off.
- Fusions: two touching demes of a people fuse when their diameters together are under FUSE_KM (a range that shrank back
  or a land bridge reconnecting two small populations) and have been for PERSIST frames; the older keeps its id.
- Extinction: a deme with no cells left ends at that frame.
- A new people's first demes take as parent the deme of its tree parent on (or nearest) their cells the frame before,
  else the deme that led most of those cells.
Each people is cut on a subgraph of its own cells, the sea within SEA_KM and the necks within NECK_KM of them.
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
from ..kernels import components
from .spread import nearest_label

WINDOW_KYR = 300.0  # frames this recent are cut (the glacial zoom and the recent pass; the deep keyframes are Myr apart)
SECOND_MIN = 10  # % of the cell's heads at which the second people (mix_second) counts as living there
CORR_EASY = 0.8  # the corridor value of a coast: one km of coast costs one "easy km"
COST_MAX = 3.0  # (the dearest land cell: ice, in easy km per km)
COST_POW = 0.5  # travel cost = (CORR_EASY / corridor) ** COST_POW: hard country slows, it does not wall off (the gaps and the distance do)
SEA_KM = 150.0  # open sea a people crosses as one population (a strait); wider gaps cut it
SEA_COST = 2.0  # easy km per km of that sea (a sea people: 1 on its own sea)
SPLIT_KM = 7000.0  # a deme wider than this (travel-cost diameter, easy km) splits in two: ~5,500 km of open lowland, 7,000 of coast
FUSE_KM = 4000.0  # two touching demes of a people whose diameters sum to less fuse
NECK_KM = 120.0  # a strip of other peoples' land this wide does not cut a people (its two sides stay one population), as SEA_KM of sea
PERSIST = 4  # frames a gap split or a fusion must hold before it counts (dated when it began); see docs/review/lineages/demes.md
MIN_CELLS = 40  # a piece cut off becomes its own deme only from this many cells (~125,000 km² at L7); smaller ones stay with theirs
SPLIT_ITER = 8  # (distance splits per deme per frame at most)
SERIES_KEEP = 24  # points of a deme's or a pair's series kept (the rest thinned evenly)
PAIRS_KEEP = 3000  # deme pairs kept in demes.json (the most contact first)
NONE = 65535


# -- numba kernels ------------------------------------------------------------------------------------
@njit(cache=True)
def grow(lab, dist, grp, lab_grp, cost, step_km, nbr_off, nbr_idx):
    """Multi-source Dijkstra with labels: the cells with lab >= 0 are the sources (at dist); a label L may enter cell j only
    if grp[j] == lab_grp[L] (grp -1: no one). Entering j costs cost[j] * step_km. lab and dist are updated in place.
    (A source none of whose neighbours it could improve is not queued: the same result, and an all-but-full labelling
    from the last frame then costs only its edges.)"""
    n = lab.shape[0]
    hq = [(0.0, 0)]
    hq.pop()
    for i in range(n):
        if lab[i] < 0:
            dist[i] = np.inf
    for i in range(n):
        if lab[i] >= 0:
            g = lab_grp[lab[i]]
            for k in range(nbr_off[i], nbr_off[i + 1]):
                j = nbr_idx[k]
                if grp[j] == g and dist[i] + cost[j] * step_km < dist[j]:
                    hq.append((dist[i], i))
                    break
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


@njit(cache=True)
def near_cells(cells, maxd, nbr_off, nbr_idx, d):
    """The cells within maxd graph steps of `cells` (not them) and their steps: a breadth-first walk out from those
    cells only. d: scratch, -1 everywhere on entry and on return."""
    q = np.empty(d.shape[0], np.int64)
    t = 0
    for i in cells:
        d[i] = 0
        q[t] = i
        t += 1
    h = 0
    while h < t:
        i = q[h]
        h += 1
        if d[i] >= maxd:
            continue
        for k in range(nbr_off[i], nbr_off[i + 1]):
            j = nbr_idx[k]
            if d[j] < 0:
                d[j] = d[i] + 1
                q[t] = j
                t += 1
    n0 = cells.shape[0]
    out = q[n0:t].copy()
    dist = np.empty(t - n0, np.int64)
    for a in range(t - n0):
        dist[a] = d[out[a]]
    for a in range(t):
        d[q[a]] = -1
    return out, dist


@njit(cache=True)
def subgraph(idx, gl, nbr_off, nbr_idx):
    """The neighbour lists (CSR) of the cells idx among themselves, in local numbering (gl: global -> local, -1 outside)."""
    m = idx.shape[0]
    off = np.zeros(m + 1, np.int64)
    for a in range(m):
        i = idx[a]
        c = 0
        for k in range(nbr_off[i], nbr_off[i + 1]):
            if gl[nbr_idx[k]] >= 0:
                c += 1
        off[a + 1] = off[a] + c
    out = np.empty(off[m], np.int64)
    for a in range(m):
        i = idx[a]
        p = off[a]
        for k in range(nbr_off[i], nbr_off[i + 1]):
            j = gl[nbr_idx[k]]
            if j >= 0:
                out[p] = j
                p += 1
    return off, out


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


class State:
    """A people's demes at the last frame, on its own cells only: idx (global ids of its cells and the sea and necks it
    crosses), lab (deme per idx cell, -1), O (occupied, per idx cell), since (kyr ago each occupied cell was settled)."""
    __slots__ = ("idx", "lab", "O", "since", "oidx")

    def __init__(self, idx, lab, O, since, oidx):
        self.idx, self.lab, self.O, self.since, self.oidx = idx, lab, O, since, oidx


class Demes:
    def __init__(self, grid, lines: list[dict], cell_km: float, rank: np.ndarray | None = None):
        self.g = grid
        self.ids = [l["id"] for l in lines]
        self.rank = np.full(grid.n, -1, np.int64) if rank is None else rank  # (the present landmass of each cell, by size; for the names)
        self.lines = lines
        self.cell_km = cell_km
        self.hs = max(1, int(round(SEA_KM / cell_km / 2)))  # (sea cells reached from either shore: a gap of 2 hs is crossed)
        self.hl = int(round(NECK_KM / cell_km / 2))  # (land of others reached from either side: a neck of 2 hl is bridged)
        n = grid.n
        self.st: dict[int, State] = {}  # line index -> its demes at the last frame
        self.diam = {}  # deme id -> its diameter at the last frame (easy km)
        self.dcache: dict[int, tuple] = {}  # deme -> ((cells, sum of ids), diameter, (end a, end b) as global ids)
        self.apart: dict[int, list] = {}  # deme -> [kyr ago its land first fell apart, frames it has stayed apart] (PERSIST)
        self.near: dict[tuple, list] = {}  # (deme, deme) -> [kyr ago they first could fuse, frames since]
        self.demes: list[Deme] = []
        self.events: list[dict] = []
        self.pairs: dict[tuple, dict] = {}
        self.prev_map = np.full(n, -1, np.int64)  # the deme of each cell's leading people, the frame before
        la, lo = np.radians(grid.lat), np.radians(grid.lon)
        self.xyz = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1)
        self.gl = np.full(n, -1, np.int64)  # (scratch: global -> local index; kept at -1 between uses)
        self.tmp = np.full(n, -1, np.int64)
        self.tmpf = np.full(n, np.nan)
        self.agos: list[float] = []

    # deme bookkeeping
    def _new(self, line, parent, ago, how, cells=None, when=None):
        d = Deme(len(self.demes), line, parent, ago if when is None else when, how)
        self.demes.append(d)
        if parent is not None and how != "first":
            self._event(d.born, how, d.id, parent, cells, None if when is None else ago)
        return d.id

    def _centre(self, cells):
        c = self.xyz[cells].mean(0)
        nr = float(np.linalg.norm(c))
        if nr < 1e-9:
            return 0.0, 0.0
        c = c / nr
        return round(float(np.degrees(np.arcsin(np.clip(c[2], -1, 1)))), 1), round(float(np.degrees(np.arctan2(c[1], c[0]))), 1)

    def _event(self, ago, kind, deme, other, cells, confirmed=None):
        lat, lon = self._centre(cells) if cells is not None and len(cells) else (None, None)
        e = {"ago_kyr": round(ago, 3), "kind": kind, "deme": deme, "other": other, "lat": lat, "lon": lon,
             "cells": None if cells is None else int(len(cells))}
        if confirmed is not None:
            e["confirmed_kyr"] = round(confirmed, 3)  # (it held PERSIST frames: dated when it began)
        self.events.append(e)

    def _labels_at(self, st: State, cells: np.ndarray, occupied_only: bool = True) -> np.ndarray:
        """A people's deme (last frame) at these global cells, -1 where none."""
        sel = st.O & (st.lab >= 0) if occupied_only else st.lab >= 0
        self.tmp[st.idx[sel]] = st.lab[sel]
        out = self.tmp[cells].copy()
        self.tmp[st.idx[sel]] = -1
        return out

    def update(self, ago: float, occ_by_line: dict, cost: np.ndarray, land: np.ndarray, lead: np.ndarray, second: np.ndarray):
        """occ_by_line: line index -> occupied mask; lead/second: the line index of each cell's leading / second people (-1)."""
        n = self.g.n
        self.agos.append(round(ago, 3))
        cmap = np.full(n, -1, np.int64)  # (lead deme per cell, this frame)
        smap = np.full(n, -1, np.int64)
        self.st0 = dict(self.st)  # (the frame before, for a new people's parent)
        for k in sorted(set(occ_by_line) | set(self.st)):
            O = occ_by_line.get(k)
            old = self.st.get(k)
            oidx = np.flatnonzero(O) if O is not None else np.zeros(0, np.int64)
            if not len(oidx):
                if old is not None:
                    for d in np.unique(old.lab[old.lab >= 0]).tolist():
                        self._end(int(d), ago, "extinct")
                    del self.st[k]
                continue
            pending = old is not None and any(self.demes[d].line == k for d in self.apart) or any(self.demes[a].line == k for a, _ in self.near)
            if old is not None and not pending and np.array_equal(oidx, old.oidx):
                st = old  # (nothing moved: the same demes)
            else:
                st = self._cut(k, O, oidx, old, ago, cost, land)
            self.st[k] = st
            on = st.O & (st.lab >= 0)
            gi, gl_ = st.idx[on], st.lab[on]
            ld = lead[gi] == k
            cmap[gi[ld]] = gl_[ld]
            sd = second[gi] == k
            smap[gi[sd]] = gl_[sd]
            ids, inv, cnt = np.unique(gl_, return_inverse=True, return_counts=True)
            xyz = np.stack([np.bincount(inv, weights=self.xyz[gi, i], minlength=len(ids)) for i in range(3)], 1)
            rk = self.rank[gi]
            rmode = {}
            if len(gi):
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
            self.apart.pop(d, None)
            for key in [key for key in self.near if d in key]:
                del self.near[key]

    def _nearest(self, idx, Lc, lab, cells):
        """The deme of the labelled local cell Lc nearest (straight line) to the centre of these local cells."""
        c = self.xyz[idx[cells]].sum(0)
        return int(lab[Lc[int(np.argmax(self.xyz[idx[Lc]] @ c))]])

    def _cut(self, k, O, oidx, old, ago, cost, land) -> State:
        g = self.g
        step = self.cell_km
        reach, dn = near_cells(oidx, max(self.hs, self.hl), g.nbr_off, g.nbr_idx, self.tmp)
        lr = land[reach]
        extra = reach[np.where(lr, dn <= self.hl, dn <= self.hs)]
        idx = np.sort(np.concatenate([oidx, extra]))  # (its cells, the sea it crosses and the necks of others' land it bridges)
        m = len(idx)
        self.gl[idx] = np.arange(m)
        loff, lidx = subgraph(idx, self.gl, g.nbr_off, g.nbr_idx)
        Ol = self.gl[oidx]
        self.gl[idx] = -1
        Om = np.zeros(m, np.bool_)
        Om[Ol] = True
        costl = np.where(Om & ~land[idx], 1.0, cost[idx])  # (a sea people on its own sea: 1)
        if old is not None:
            self.tmp[old.idx] = old.lab
            oldl = self.tmp[idx].copy()
            self.tmp[old.idx] = -1
            self.tmpf[old.idx] = np.where(old.O, old.since, np.nan)
            sincel = self.tmpf[idx].copy()
            self.tmpf[old.idx] = np.nan
            lab = np.where(Om & (oldl >= 0), oldl, -1).astype(np.int64)
            was = ~np.isnan(sincel)
            for d in set(np.unique(old.lab[old.O & (old.lab >= 0)]).tolist()) - set(np.unique(lab[lab >= 0]).tolist()):
                self._end(int(d), ago, "extinct")
        else:
            lab = np.full(m, -1, np.int64)
            sincel = np.full(m, np.nan)
            was = np.zeros(m, np.bool_)
        since = np.where(Om, np.where(was, sincel, ago), np.nan)  # (when each cell was settled)
        nl = len(self.demes) + 1
        if (lab >= 0).any():
            lab, _ = grow(lab, np.zeros(m), np.zeros(m, np.int64), np.zeros(nl, np.int64), costl, step, loff, lidx)
        comp, nc = components(np.ones(m, np.bool_), loff, lidx)
        srt = np.argsort(comp, kind="stable")
        cuts = np.searchsorted(comp[srt], np.arange(nc + 1))
        members = lambda c: srt[cuts[c]:cuts[c + 1]]  # noqa: E731
        # land reached by no path: new demes (or fragments of the nearest one)
        if (lab < 0).any():
            Lc = np.flatnonzero(lab >= 0)
            had = len(Lc) > 0
            ids, cnt = np.unique(comp[(lab < 0) & Om], return_counts=True)
            small = []
            for r, x in enumerate(np.argsort(-cnt)):
                c, sz = int(ids[x]), int(cnt[x])
                mem = members(c)
                cells = mem[Om[mem]]
                if sz >= MIN_CELLS or (not had and r == 0):
                    if had:
                        d = self._new(k, self._nearest(idx, Lc, lab, cells), ago, "crossing", idx[cells])
                    else:
                        xpar = self._from_people(k, idx[cells])
                        d = self._new(k, xpar, ago, "first" if xpar is None else "from_people", idx[cells])
                    lab[mem] = d
                else:
                    small.append(mem)
            Lc = np.flatnonzero(lab >= 0)
            for mem in small:  # (pieces too small to be a deme: the nearest one's)
                lab[mem] = self._nearest(idx, Lc, lab, mem)
        # splits along a gap: a deme spread over pieces of the people's land that stay apart PERSIST frames
        key = lab[Om] * (nc + 1) + comp[Om]
        u, cnt = np.unique(key, return_counts=True)
        dl, dc = u // (nc + 1), u % (nc + 1)
        big = cnt >= MIN_CELLS
        multi = {int(d) for d, c in zip(*np.unique(dl[big], return_counts=True)) if c >= 2}
        for d in [d for d in self.apart if self.demes[d].line == k and d not in multi]:
            del self.apart[d]  # (joined again before it counted)
        split_now = set()
        for d in multi:
            a = self.apart.setdefault(d, [ago, 0])
            a[1] += 1
            if a[1] >= PERSIST:
                split_now.add(d)
        for d in split_now:
            first = self.apart.pop(d)[0]
            m_ = dl == d
            pcs = sorted(zip(cnt[m_].tolist(), dc[m_].tolist()), reverse=True)
            for sz, c in pcs[1:]:
                if sz < MIN_CELLS:
                    continue
                mem = members(c)
                mem = mem[lab[mem] == d]
                cells = mem[Om[mem]]
                nd = self._new(k, int(d), ago, "split_gap", idx[cells], when=first)
                self.demes[nd].settled = round(float(np.nanmax(since[cells])), 3)  # (the piece was settled then)
                lab[mem] = nd
        # diameters, fusions, then splits by distance (all the wide demes of the people at once, a few rounds)
        D, ends = self._diameters(lab, costl, loff, lidx, idx=idx, cached=True)
        lab, fused = self._fuse(k, lab, D, ago, idx, loff, lidx)
        if fused:
            D, ends = self._diameters(lab, costl, loff, lidx, idx=idx, cached=True)
        for _ in range(SPLIT_ITER):
            wide = [d for d, v in D.items() if v > SPLIT_KM]
            if not wide:
                break
            lab, touched = self._halve(k, wide, ends, lab, Om, costl, since, ago, idx, loff, lidx)
            if not touched:
                break
            D2, e2 = self._diameters(lab, costl, loff, lidx, touched)
            D.update(D2)
            ends.update(e2)
            for d in wide:
                if d not in touched:
                    D[d] = 0.0  # (could not be halved: leave it)
        self.diam.update(D)
        return State(idx, lab, Om, since, oidx)

    def _from_people(self, k, cells):
        """The deme a new people's first deme arose from: of its parent people (the tree's) on these cells or nearest them
        the frame before, else whichever deme led most of these cells then; None if nobody did."""
        pars = [self.ids.index(p) for p in (self.lines[k].get("parents") or []) if p in self.ids]
        for q in pars:
            st = self.st0.get(q)
            if st is None:
                continue
            v = self._labels_at(st, cells)
            v = v[v >= 0]
            if len(v):
                return int(np.bincount(v).argmax())
        for q in pars:  # (the parent's nearest deme: its range need not overlap the child's first cells)
            st = self.st0.get(q)
            if st is not None and (st.O & (st.lab >= 0)).any():
                Lc = np.flatnonzero(st.O & (st.lab >= 0))
                c = self.xyz[cells].sum(0)
                return int(st.lab[Lc[int(np.argmax(self.xyz[st.idx[Lc]] @ c))]])
        pm = self.prev_map[cells]
        pm = pm[pm >= 0]
        return int(np.bincount(pm).argmax()) if len(pm) else None

    def _diameters(self, lab, cost, loff, lidx, only=None, idx=None, cached=False):
        """Per deme in lab (or in `only`): its travel-cost diameter, easy km, and the two ends of it (two sweeps of a Dijkstra
        kept inside each deme's cells): ({deme: km}, {deme: (a, b)}), a and b local cells. cached: a deme whose cells are
        the same as when last measured (count and sum of cell ids) keeps its diameter (the ends are kept as global ids), and
        one whose cells changed but still holds its last far end sweeps once, from that end, instead of twice."""
        m = len(lab)
        nl = len(self.demes)
        mine = lab >= 0
        if only is not None:
            mine &= np.isin(lab, np.fromiter(only, np.int64))
        D, ends = {}, {}
        warm = {}  # deme -> local cell of its last far end, still its own
        if cached:
            ids, inv, cnt = np.unique(lab[mine], return_inverse=True, return_counts=True)
            sm = np.bincount(inv, weights=idx[mine].astype(float), minlength=len(ids))
            sigs = {d: (c, s_) for d, c, s_ in zip(ids.tolist(), cnt.tolist(), sm.tolist())}
            again = []
            for d, key in sigs.items():
                old = self.dcache.get(d)
                if old is not None and old[0] == key:
                    D[d] = old[1]
                    ends[d] = tuple(int(np.searchsorted(idx, x)) for x in old[2])
                    continue
                again.append(d)
                if old is not None:
                    j = int(np.searchsorted(idx, old[2][1]))
                    if j < m and idx[j] == old[2][1] and lab[j] == d:
                        warm[d] = j
            if not again:
                return D, ends
            if len(again) < len(ids):
                mine &= np.isin(lab, np.array(again, np.int64))
        ids = np.unique(lab[mine])
        if not len(ids):
            return D, ends
        grp = np.where(mine, lab, -1).astype(np.int64)
        lg = np.arange(nl, dtype=np.int64)
        first = np.full(nl, -1, np.int64)
        cells = np.flatnonzero(mine)
        first[lab[cells[::-1]]] = cells[::-1]  # (the lowest cell of each deme)
        a = prev = None
        cold = np.array([d for d in ids.tolist() if d not in warm], np.int64)
        for sweep in range(2):
            s = np.full(m, -1, np.int64)
            if sweep == 0:
                if not len(cold):
                    a = np.full(nl, -1, np.int64)
                    continue
                src, on = first[cold], cold
            else:
                for d, j in warm.items():
                    a[d] = j
                src, on = a[ids], ids
            ok = src >= 0
            s[src[ok]] = on[ok]
            g2 = grp if sweep else np.where(np.isin(grp, cold), grp, -1)
            l2, dd = grow(s, np.zeros(m), g2, lg, cost, self.cell_km, loff, lidx)
            prev = a
            a, bv = group_argmax(l2, dd, nl)
        for d in ids.tolist():
            D[int(d)] = float(bv[d]) if np.isfinite(bv[d]) else 0.0
            ends[int(d)] = (int(prev[d]), int(a[d]))
            if cached and prev[d] >= 0 and a[d] >= 0:
                self.dcache[int(d)] = (sigs[int(d)], D[int(d)], (int(idx[prev[d]]), int(idx[a[d]])))
        return D, ends

    def _fuse(self, k, lab, D, ago, idx, loff, lidx):
        """Fuse touching demes of a people whose diameters sum to less than FUSE_KM once they have stayed so PERSIST frames
        (dated when they first could); the older keeps its id."""
        u = np.unique(touching(np.flatnonzero(lab >= 0), lab, loff, lidx))
        cand = {(int(x // NONE), int(x % NONE)) for x in u if D.get(int(x // NONE), 0) + D.get(int(x % NONE), 0) < FUSE_KM}
        for key in [key for key in self.near if self.demes[key[0]].line == k and key not in cand]:
            del self.near[key]
        gone, fused = set(), False
        for key in sorted(cand, key=lambda q: D.get(q[0], 0) + D.get(q[1], 0)):
            r = self.near.setdefault(key, [ago, 0])
            r[1] += 1
            a, b = key
            if r[1] < PERSIST or a in gone or b in gone:
                continue
            keep, lose = (a, b) if self.demes[a].born >= self.demes[b].born else (b, a)
            cells = idx[lab == lose]
            lab = np.where(lab == lose, keep, lab)
            first = r[0]
            self._end(lose, ago, "fused", keep)
            self._event(first, "fusion", keep, lose, cells, ago)
            gone |= {a, b}
            fused = True
        return lab, fused

    def _halve(self, k, big, ends, lab, Om, cost, since, ago, idx, loff, lidx):
        """Split each deme in `big` in two from the two ends of its diameter (one Dijkstra for all); the half with its oldest
        cells keeps the id, the other buds off. Returns (lab, the demes touched: old and new ids)."""
        m = len(lab)
        nl = len(self.demes)
        tmp = {d: nl + i for i, d in enumerate(big)}  # (a temporary label for each b side)
        lg = np.concatenate([np.arange(nl, dtype=np.int64), np.array(big, np.int64)])
        sel = np.isin(lab, np.array(big, np.int64))
        grp = np.where(sel, lab, -1).astype(np.int64)
        s = np.full(m, -1, np.int64)
        for d in big:
            a, b = ends[d]
            if a >= 0 and b >= 0 and a != b:
                s[a], s[b] = d, tmp[d]
        l2, _ = grow(s, np.zeros(m), grp, lg, cost, self.cell_km, loff, lidx)
        touched = set()
        for d in big:
            h0, h1 = sel & (l2 == d), sel & (l2 == tmp[d])
            n0, n1 = int((h0 & Om).sum()), int((h1 & Om).sum())
            if n0 < MIN_CELLS or n1 < MIN_CELLS:
                continue
            age0 = float(np.nanmean(since[h0 & Om]))
            age1 = float(np.nanmean(since[h1 & Om]))
            bud = h1 if age0 >= age1 else h0
            nd = self._new(k, d, ago, "split_distance", idx[bud & Om])
            lab = np.where(bud, nd, lab)
            touched |= {d, nd}
        return lab, touched

    def _contacts(self, ago, cmap, smap, land):
        lm = np.where(land, cmap, -1)
        e = touching(np.flatnonzero(lm >= 0), lm, self.g.nbr_off, self.g.nbr_idx)  # (shared land borders, in cell edges)
        rec = {}
        if len(e):
            u, c = np.unique(e, return_counts=True)
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
            wl = json.loads(S.find_world(m["world"]).read_text())["layers"]  # (only the rivers: world.load would build a grid too)
            flow = np.asarray(wl["flow"], float) if "flow" in wl else None
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
    for st in dm.st.values():
        u, c = np.unique(st.lab[(st.lab >= 0) & st.O], return_counts=True)
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
