"""Contact history of the peoples (PW-727): who met whom, when, along what border and in what country; the
interfertility tier of each pair (spec.Tree.tier_of, from split depth); the substrate (who held a cell before its
present people); and the clines that carry a body share across the border of two close (T0/T1) peoples.

Everything here reads the peoples' wholes at the stored epochs and writes output only: the history's wishes, its
empty land and its ranges are not touched. The one exception is `cline`, which smooths the body-share layers
(`body_<trait>`) of the stored frames across T0/T1 borders."""

from __future__ import annotations

import numpy as np

EST = 0.12  # (history.EST: presence below which a people is not there)
PRESENT_OVERLAP = 0.25  # a people holds a cell for the substrate where its presence is at least this
CLINE_KM = 300.0  # how far a body share spreads over a T0/T1 border (in rings of the cell size)
CLINE_RATE = 0.5  # share of the difference to the neighbours taken up per pass
SERIES_KEEP = 14  # points of a pair's border series kept in the run's meta (the rest thinned evenly)


def kind_of(tags: dict, corr: np.ndarray, cells: np.ndarray) -> str:
    """The kind of country along a border (the cells next to it): coast, river, open lowland, closed, or mixed."""
    if not len(cells):
        return "mixed country"
    if float(tags["coast"][cells].mean()) >= 0.4:
        return "coast"
    c = corr[cells]
    if float((c >= 0.85).mean()) >= 0.4:
        return "river"
    if float(tags["open"][cells].mean()) >= 0.5 and float(c.mean()) >= 0.4:
        return "open lowland"
    if float(c.mean()) < 0.4:
        return "closed country"
    return "mixed country"


class Contacts:
    def __init__(self, h):
        self.h = h
        m = h.grid.n
        self.n = len(h.lines)
        self.pairs: dict[tuple, dict] = {}
        self.cur = np.full(m, -1, np.int16)  # the people holding each cell (presence >= PRESENT_OVERLAP), -1: none yet
        self.prev = np.full(m, -1, np.int16)  # ...the last other people that held it
        self.until = np.full(m, np.nan)  # ...and when (kyr ago) it lost the cell
        self.agos: list[float] = []  # (the stored epochs seen, oldest first)

    # -- per stored frame -----------------------------------------------------------------------------
    def update(self, Pw: np.ndarray, step, tags: dict, corr: np.ndarray, land: np.ndarray) -> None:
        h, g = self.h, self.h.grid
        ago = float(step.ago)
        self.agos.append(round(ago, 3))
        pres = (Pw >= EST) & land[None, :]
        held = (Pw >= PRESENT_OVERLAP) & land[None, :]
        rows = [k for k in range(self.n) if pres[k].any()]
        src, dst = g.nbr_src, g.nbr_idx
        for x, a in enumerate(rows):
            ea = np.flatnonzero(pres[a][src])  # (the edges out of a's cells: the edge list holds each neighbour pair both ways)
            sa, da = src[ea], dst[ea]
            for b in rows[x + 1:]:
                edge = pres[b][da]  # (a->b edges are the border)
                if not edge.any():
                    continue
                touch = np.unique(np.concatenate([sa[edge], da[edge]]))
                both = int((held[a] & held[b]).sum())
                small = max(1, min(int(pres[a].sum()), int(pres[b].sum())))
                rec = self.pairs.setdefault((a, b), {"first": ago, "series": [], "kinds": {}})
                # the border: the cells of one people that touch the other's range without being in it (the longer side), one cell long each
                na = np.unique(sa[edge])
                nb = np.unique(da[edge])
                km = max(int((~pres[b][na]).sum()), int((~pres[a][nb]).sum())) * h.cell_km
                rec["series"].append([round(ago, 3), int(round(km)), round(100 * both / small, 1)])
                k = kind_of(tags, corr, touch)
                rec["kinds"][k] = rec["kinds"].get(k, 0) + 1
        # the substrate: a cell changes hands where another people comes to hold it and the old one no longer does
        lead = np.where(held.any(0), np.argmax(np.where(held, Pw, 0), 0), -1).astype(np.int16)
        old = self.cur
        flip = (lead >= 0) & (old >= 0) & (lead != old) & ~held[np.maximum(old, 0), np.arange(g.n)]
        self.prev[flip] = old[flip]
        self.until[flip] = ago
        self.cur = np.where(lead >= 0, lead, old).astype(np.int16)

    def _span(self, ago: float) -> float:
        """The kyr a stored epoch stands for: half the gap to the epoch before and to the one after (the first and the last: half their one gap)."""
        a = self.agos
        j = a.index(ago)
        before = (a[j - 1] - a[j]) / 2 if j > 0 else 0.0
        after = (a[j] - a[j + 1]) / 2 if j + 1 < len(a) else 0.0
        return max(before + after, 0.0)

    # -- results --------------------------------------------------------------------------------------
    def summary(self) -> dict:
        """{pairs, substrate, tier_kyr} for meta.contacts."""
        h = self.h
        T = h.tree
        ids = [l.id for l in h.lines]
        pairs = []
        for (a, b), r in sorted(self.pairs.items(), key=lambda kv: (kv[1]["first"] * -1, kv[0])):
            s = r["series"]
            years = sum(self._span(q[0]) for q in s)
            now = s[-1] if s and s[-1][0] <= 1e-9 else None
            keep = s if len(s) <= SERIES_KEEP else [s[int(round(i))] for i in np.linspace(0, len(s) - 1, SERIES_KEEP)]
            kind = max(r["kinds"], key=lambda q: r["kinds"][q]) if r["kinds"] else None
            sk = T.split_kyr(ids[a], ids[b])
            pairs.append({"a": ids[a], "b": ids[b], "tier": f"T{T.tier_of(ids[a], ids[b])}",
                          "split_kyr": None if sk is None else round(sk, 1),
                          "first_contact_kyr": round(r["first"], 3), "years_in_contact": int(round(years * 1000)),
                          "in_contact_now": now is not None, "border_km_now": now[1] if now else 0,
                          "border_km_peak": max(q[1] for q in s), "mixed_pct_now": now[2] if now else 0.0,
                          "kind": kind, "series": keep})
        sub = {}
        cur, prev, until = self.cur, self.prev, self.until
        for k, l in enumerate(h.lines):
            mine = cur == k
            n = int(mine.sum())
            if not n:
                continue
            rows = []
            for j in np.unique(prev[mine & (prev >= 0) & (prev != k)]):
                sel = mine & (prev == j)
                rows.append({"id": ids[int(j)], "cells": int(sel.sum()), "share": round(float(sel.sum() / n), 3),
                             "held_until_kyr": round(float(np.median(until[sel])), 2)})
            rows.sort(key=lambda q: -q["cells"])
            sub[l.id] = {"cells": n, "first_here_share": round(1 - sum(q["cells"] for q in rows) / n, 3), "held_before": rows[:6]}
        return {"pairs": pairs, "substrate": sub, "tier_kyr": list(T.tier_kyr)}


def cline(h, comp: dict, lead: np.ndarray, land: np.ndarray) -> int:
    """Carry each body share (`comp['body_<trait>']`, % of the cell) across the borders of close peoples: between
    two peoples of tier T0/T1 the share diffuses over about CLINE_KM into the neighbour's side, so a trait one people
    has (milk) reaches into the next one's country by a gradient rather than stopping at the line. `lead`: the whole
    people of each cell (255 none). Returns the border edges used."""
    traits = [k for k in comp if k.startswith("body_")]
    if not traits:
        return 0
    g = h.grid
    ids = [l.id for l in h.lines]
    nl = len(ids)
    T = getattr(h, "_tier_matrix", None)
    if T is None:
        T = np.full((nl, nl), 3, np.int8)
        for i in range(nl):
            for j in range(nl):
                T[i, j] = 0 if i == j else h.tree.tier_of(ids[i], ids[j])
        h._tier_matrix = T
    src, dst = g.nbr_src, g.nbr_idx
    ls, ld = lead[src].astype(np.int64), lead[dst].astype(np.int64)
    ok = (ls < nl) & (ld < nl) & land[src] & land[dst]
    tier = np.where(ok, T[np.minimum(ls, nl - 1), np.minimum(ld, nl - 1)], 3)
    close = tier <= 1
    border = close & (ls != ld)
    if not border.any():
        return 0
    passes = int(np.clip(round(CLINE_KM / h.cell_km), 1, 8))
    m = np.zeros(g.n, bool)
    m[src[border]] = True
    for _ in range(passes - 1):
        m[dst[close & m[src]]] = True
    use = close & m[src] & m[dst]
    deg = np.maximum(np.bincount(src[use], minlength=g.n), 1)
    for k in traits:
        v = comp[k].astype(float)
        for _ in range(passes):
            d = np.bincount(src[use], weights=(v[dst] - v[src])[use], minlength=g.n) / deg
            v = v + CLINE_RATE * d
        comp[k] = np.where(m & ok_cells(lead, nl, land), np.round(np.clip(v, 0, 100)), comp[k]).astype(np.uint8)
    return int(border.sum() // 2)


def ok_cells(lead: np.ndarray, nl: int, land: np.ndarray) -> np.ndarray:
    return (lead < nl) & land
