"""The tech tree inside the history (PW-1466, lane 192; design: docs/review/culture/polities/round8.md). Made by the live polities
(history.polity_live), so it runs only when params.POLITIES_LIVE is on; off, the tree is built after the run as before.

In plain words: the tech tree (techtree.Calendar) now runs step by step while the history runs, so a polity seated in a century
reads what its people really knew by then, not an era proxy. Each history step, before the polities' step, the tree runs its own
steps (the same log-spaced steps and the same keyed draws as the tree built after the run) down to the history's time, reading what
the history knows by then:
- the lines' starts and ends so far (a line not yet started is not alive in the tree);
- the populations so far: the tracks of the frames stored so far (the after-run tree also reads the tracks, all of them);
- the contacts so far: each pair's first contact and its border series so far, a pair touching at the last stored frame counting as
  still in touch (the after-run tree reads the whole run's intervals and median borders);
- the tamings so far (crops.py, animals.py record them as they happen);
- the goods each people's country holds now (its range at the last stored frame; the after-run tree reads the present range).
At the end (output.save) the tree is fed the whole run, runs any steps left, and is written out as meta.techtree: one calendar for
the history's polities and the after-run read-out.
D52's town arms (B, E) need the settlement ledger, made after the run, so this tree runs without them (PW-1464 builds them after
the run only).
"""

from __future__ import annotations

import time
import warnings

import numpy as np

from .. import techtree as TT

PRESENT_MIN = 0.05  # (goods_held's share of a cell that makes it a people's country)


class LiveTech:
    """The tech calendar inside the history: `step(step)` at the start of each history step; `known` for the gates."""

    def __init__(self, h):
        self.h = h
        self.secs = 0.0
        self.cal: TT.Calendar | None = None
        self._seen = None  # (the frames stored when the slow inputs were last read)
        self._G = None  # (the goods as cells over threshold: (names, deposit flags, goods x cells float32))
        T = TT.load()
        if TT.town_arms(T):
            warnings.warn(f"tech tree arms {TT.town_arms(T)} need the settlement ledger: the tree inside the history runs without them",
                          stacklevel=2)
        self.T = T
        self.arms = TT.arms_without_towns(T)

    @property
    def known(self) -> dict:
        return self.cal.known if self.cal is not None else {}

    # ------------------------------------------------------------ what the history knows now
    def lines(self) -> list[dict]:
        """meta.lineages' fields the tree reads (output.save's, rounded alike), as known now."""
        h = self.h
        return [{"index": k, "id": l.id, "origin": l.origin, "parents": l.parents, "ago_kyr": l.ago_kyr, "sapient_kyr": l.sapient_kyr,
                 "group_of": l.group_of, "overlay": l.overlay, "traits": l.traits, "way": l.way,
                 "started_kyr": h.started.get(l.id), "ended_kyr": h.ended.get(l.id), "track": h.tracks[l.id],
                 "demography": {kk: round(v, 4) for kk, v in l.demos().items()}, "generation_yr": h.gen_yr(l)}
                for k, l in enumerate(h.lines)]

    def _links(self) -> list[tuple]:
        """The contacts so far as the tree's intervals (techtree.links_of on contacts.summary's pairs, without the summary): a pair
        touching at the last stored frame is still in touch."""
        from ..contacts import SERIES_KEEP
        c = self.h.contacts
        if c is None or not c.agos:
            return []
        ids = [l.id for l in self.h.lines]
        last = c.agos[-1]
        out = []
        for (a, b), r in sorted(c.pairs.items(), key=lambda kv: (kv[1]["first"] * -1, kv[0])):
            if ids[a] not in self.cal.kind or ids[b] not in self.cal.kind:
                continue
            s = r["series"]
            keep = s if len(s) <= SERIES_KEEP else [s[int(round(i))] for i in np.linspace(0, len(s) - 1, SERIES_KEEP)]
            to = 0.0 if s and abs(s[-1][0] - last) < 1e-9 else (min(q[0] for q in keep) if keep else round(r["first"], 3))
            km = float(np.median([q[1] for q in keep])) if keep else 0.0
            out.append((ids[a], ids[b], float(round(r["first"], 3)), to, km))
        return out

    def _stocks(self) -> dict:
        """The tamings so far, as meta.present's crops and animals stocks (`tamed`, `took_up_kyr`): techtree.forced_of reads them."""
        h = self.h
        out = {}
        for key, owner in (("crops", h.crops), ("animals", h.animals)):
            if owner is None:
                continue
            out[key] = {"stocks": {s.a.id: {"tamed": s.tamed, "took_up_kyr": {h.lines[k].id: v for k, v in s.took_up.items()}}
                                   for s in owner.stocks}}
        return out

    def _have(self) -> dict:
        """The goods each people's country holds now (techtree.goods_held on the presence now, all peoples at once)."""
        h, cal = self.h, self.cal
        goods = getattr(h, "goods", None)
        if goods is None:
            return {l["id"]: None for l in cal.people}
        d = self.T["defaults"]
        if self._G is None:
            names, dep, rows = [], [], []
            for g, v in goods.items():
                if g.startswith("_"):
                    continue
                a = np.asarray(v, float)
                if a.shape[0] != h.grid.n:
                    continue
                names.append(g)
                dep.append(g in TT.DEPOSITS)
                rows.append(a >= (d["deposit_min"] if g in TT.DEPOSITS else d["env_min"]))
            self._G = (names, np.array(dep, bool), np.array(rows, np.float32).reshape(len(rows), h.grid.n))
        names, dep, G = self._G
        sel = h.p >= PRESENT_MIN
        n = sel.sum(1)
        cnt = (sel.astype(np.float32) @ G.T).astype(np.int64) if len(names) else np.zeros((len(sel), 0), np.int64)
        out = {}
        for l in cal.people:
            k = cal.idx[l["id"]]
            if n[k] == 0:
                out[l["id"]] = None
                continue
            ok = np.where(dep, cnt[k] >= np.maximum(2, d["deposit_share"] * n[k]), cnt[k] / n[k] >= d["env_share"])
            out[l["id"]] = {g for g, x in zip(names, ok) if x}
        return out

    # ------------------------------------------------------------ the history's step
    def step(self, step):
        """Runs the tree's steps down to this history step's time, from what the history knows at its start."""
        t0 = time.time()
        try:
            h = self.h
            if not h.started:
                return  # (nothing has begun: the tree's steps are fixed from the oldest start, so wait for it)
            lines = None
            if self.cal is None:
                lines = self.lines()
                tr = h.tree
                self.cal = TT.Calendar(lines, tr.mode, tr.era, h.seed, self.T, tr.gods_mode, None, self.arms)
            cal = self.cal
            seen = (len(h.contacts.agos) if h.contacts is not None else 0, sum(len(v) for v in h.tracks.values()))
            if seen != self._seen:  # (a frame was stored: the tracks, contacts and ranges moved)
                self._seen = seen
                cal.feed(lines or self.lines(), links=self._links(), have=self._have())
            for l in cal.people:  # (starts and ends move on any step; a line not yet started waits)
                lid = l["id"]
                s = h.started.get(lid)
                cal.start[lid] = float(s) if s is not None else -1e9
                e = h.ended.get(lid)
                cal.end[lid] = float(e) if e is not None else -1.0
            cal.forced = TT.forced_of(self._stocks(), cal.techs, cal.L)
            cal.advance(step.ago)
        finally:
            self.secs += time.time() - t0

    def result(self, lines: list[dict], contacts: dict | None, pres: dict | None, present: np.ndarray | None, goods: dict | None) -> dict:
        """meta.techtree: fed the whole run (as techtree.build reads it), the steps left run, written out."""
        cal = self.cal
        if cal is None:
            tr = self.h.tree
            return TT.build(lines, contacts, pres, present, goods, tr.mode, tr.era, self.h.seed, T=self.T, gods_mode=tr.gods_mode,
                            arms=self.arms)
        have = {l["id"]: TT.goods_held(cal.T, present, goods, cal.idx[l["id"]]) for l in cal.people}
        cal.feed(lines, TT.links_of(contacts, cal.kind), TT.forced_of(pres, cal.techs, cal.L), have, (pres or {}).get("lines") or {})
        cal.advance()
        out = cal.result()
        out["inside_history"] = {"made_s": round(self.secs, 1), "arms": self.arms}
        return out
