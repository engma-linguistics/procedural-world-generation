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
# incursions (PW-756): a people's range jumping into cells another people held, over a short span. Looked at only for the
# last INCURSION_KYR (an older one is out of any memory), as episodes of INCURSION_SPAN kyr; one counts where the taker gains
# at least INCURSION_GAIN of its own range at the start of the episode and at least INCURSION_MIN_MKM2 of ground (the
# ordinary give and take of a frontier, a percent of a big people's range, is not an incursion). The loss is measured
# against what the loser held within LOCAL_KM of the ground (the memory is the frontier people's, not the whole people's),
# and the direction is where the taker's older cells within DIR_KM of the ground taken lie, seen from it.
# The same episode machinery counts a second kind (PW-769): a people living among another (the other still leads those cells)
# whose presence there rises by at least SETTLE_RISE within one stored frame (a ruling minority, a settlement wave), kind
# `settled_among`; the other kind, the old people losing the cells, is `displacement`.
SETTLE_RISE = 0.15
INCURSION_KYR = 100.0
INCURSION_SPAN = 2.0
INCURSION_GAIN = 0.10
INCURSION_MIN_MKM2 = 0.05
LOCAL_KM = 1000.0
DIR_KM = 2000.0
INCURSION_KEEP = 200  # incursions kept in the run's meta (the largest)
R_KM = 6371.0


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
        la, lo = np.radians(h.grid.lat), np.radians(h.grid.lon)
        self.xyz = np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], 1)
        self.takes: dict[tuple, list] = {}  # (taker, loser, kind) -> the takeovers of each stored frame (see _note)
        self._pw: np.ndarray | None = None  # (the last frame's presence)

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
        if flip.any() and ago <= INCURSION_KYR:
            self._note(ago, lead, old, flip)
        if self._pw is not None and ago <= INCURSION_KYR:
            self._note_settled(ago, lead, flip, Pw, pres)
        self._pw = Pw.copy()
        self.prev[flip] = old[flip]
        self.until[flip] = ago
        self.cur = np.where(lead >= 0, lead, old).astype(np.int16)

    def _note_settled(self, ago: float, lead: np.ndarray, flip: np.ndarray, Pw: np.ndarray, pres: np.ndarray) -> None:
        """Record this frame's settling-among per (settler, host): cells the host still leads where the settler's presence rose
        by SETTLE_RISE since the last frame (and is now there). Fed to `_note` as a takeover of kind `settled_among`."""
        rise = (Pw - self._pw >= SETTLE_RISE) & pres & (lead >= 0)[None, :] & ~flip[None, :] & (lead[None, :] != np.arange(self.n)[:, None])
        for a in np.flatnonzero(rise.any(1)):
            self._note(ago, np.full(len(lead), a, np.int16), lead, rise[a], "settled_among", taker_n=int((self._pw[a] >= EST).sum()))

    def _note(self, ago: float, lead: np.ndarray, old: np.ndarray, flip: np.ndarray, kind: str = "displacement", taker_n: int | None = None) -> None:
        """Record this frame's takeovers per (taker, loser): the cells, their centre, the loser's cells near them and the taker's
        own older cells near them (all before this frame's change). For `settled_among` the "loser" is the host that still leads
        the cells and `taker_n` is the settler's range before."""
        key = lead[flip].astype(np.int64) * 1000 + old[flip]
        cos_loc = np.cos(LOCAL_KM / R_KM)
        cells = np.flatnonzero(flip)
        for kk in np.unique(key):
            a, b = int(kk // 1000), int(kk % 1000)
            idx = cells[key == kk]
            c = self.xyz[idx].mean(0)
            norm = float(np.linalg.norm(c))
            if norm < 1e-9:
                continue
            c = c / norm
            dots = self.xyz @ c
            rec = {"ago": ago, "cells": int(len(idx)), "c": c, "loser": int(((old == b) & (dots >= cos_loc)).sum()),
                   "taker": int((old == a).sum()) if taker_n is None else taker_n}
            reach = np.arccos(np.clip(float(dots[idx].min()), -1, 1)) + DIR_KM / R_KM  # (the taken ground's own spread, and DIR_KM beyond it)
            mine = (old == a) & (dots >= np.cos(min(reach, np.pi)))
            if mine.any():
                rec["from"] = self.xyz[mine].mean(0)
                rec["from_n"] = int(mine.sum())
            self.takes.setdefault((a, b, kind), []).append(rec)

    def incursions(self) -> list[dict]:
        """The incursions of the run: episodes (INCURSION_SPAN kyr) in which a people took ground from another by at least
        INCURSION_GAIN of its own range: {by, over, kind, ago_kyr, span_kyr, cells, mkm2, gain, local_share, lat, lon, from_deg}
        (from_deg: the compass bearing, clockwise from north, from the ground taken to the taker's older land near it, or None)."""
        h = self.h
        ids = [l.id for l in h.lines]
        out = []
        for (a, b, kind), recs in self.takes.items():
            recs = sorted(recs, key=lambda r: -r["ago"])
            i = 0
            while i < len(recs):
                first = recs[i]
                grp = [r for r in recs[i:] if first["ago"] - r["ago"] <= INCURSION_SPAN + 1e-9]
                i += len(grp)
                n = sum(r["cells"] for r in grp)
                gain = 1.0 if first["taker"] == 0 else min(1.0, n / first["taker"])
                if n * h.cell_mkm2 < INCURSION_MIN_MKM2 or gain < INCURSION_GAIN:
                    continue
                c = np.sum([r["c"] * r["cells"] for r in grp], 0)
                c = c / np.linalg.norm(c)
                lat, lon = float(np.degrees(np.arcsin(np.clip(c[2], -1, 1)))), float(np.degrees(np.arctan2(c[1], c[0])))
                deg = None
                if first.get("from_n", 0) >= 3:
                    f = first["from"] / max(float(np.linalg.norm(first["from"])), 1e-9)
                    if np.degrees(np.arccos(np.clip(c @ f, -1, 1))) * 111.0 > h.cell_km:  # (the taker's older cells are not the ground taken)
                        la1, la2 = np.radians(lat), np.arcsin(np.clip(f[2], -1, 1))
                        dl = np.arctan2(f[1], f[0]) - np.radians(lon)
                        deg = float(np.degrees(np.arctan2(np.sin(dl) * np.cos(la2), np.cos(la1) * np.sin(la2) - np.sin(la1) * np.cos(la2) * np.cos(dl))) % 360)
                ago = sum(r["ago"] * r["cells"] for r in grp) / n
                out.append({"by": ids[a], "over": ids[b], "kind": kind, "ago_kyr": round(ago, 2), "span_kyr": round(first["ago"] - grp[-1]["ago"], 2),
                            "cells": n, "mkm2": round(n * h.cell_mkm2, 3), "gain": round(gain, 3),
                            "local_share": round(min(1.0, n / max(first["loser"], n)), 3),
                            "lat": round(lat, 2), "lon": round(lon, 2), "from_deg": None if deg is None else round(deg)})
        out.sort(key=lambda r: -r["cells"])
        return sorted(out[:INCURSION_KEEP], key=lambda r: (r["ago_kyr"], r["by"], r["over"]))

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
        return {"pairs": pairs, "substrate": sub, "incursions": self.incursions(), "tier_kyr": list(T.tier_kyr)}


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
