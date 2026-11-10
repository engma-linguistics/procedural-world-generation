"""The tech tree inside the history (PW-1466, lane 192; design: docs/review/culture/polities/round8.md). Made by the live polities
(history.polity_live), so it runs only when params.POLITIES_LIVE is on; off, the tree is built after the run as before.

In plain words: the tech tree (techtree.Calendar) now runs step by step while the history runs, so a polity seated in a century
reads what its people really knew by then, not an era proxy. Each history step, before the polities' step, the tree runs its own
steps (the same log-spaced steps and the same keyed draws as the tree built after the run) down to the history's time, reading what
the history knows by then:
- the lines' starts and ends so far (a line not yet started is not alive in the tree);
- the populations so far: the tracks of the frames stored so far (the after-run tree also reads the tracks, all of them);
- the contacts so far: each pair's first contact and the border it shares now (at the last stored frame), a pair touching at the
  last stored frame counting as still in touch (the after-run tree reads the whole run's intervals and median borders). A front
  still on its way is re-timed when the border grows (never later): see _retime (PW-1473);
- the tamings so far (crops.py, animals.py record them as they happen);
- the goods each people's country holds now (its range at the last stored frame; the after-run tree reads the present range).
At the end (output.save) the tree is fed the whole run, runs any steps left, and is written out as meta.techtree: one calendar for
the history's polities and the after-run read-out.
D52's town arms (B, E) need a town footprint. The settlement ledger is made after the run, so inside the history the footprint is
the live polities' own central places of town size, counted each recent step (PW-1472, LivePolities.town_cells, note_towns).
"""

from __future__ import annotations

import time

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
        self._stored = None  # (the presence as the last stored frame holds it, at_frame; read once at the next feed)
        self._lm = None  # (the landmass map of the region learners, landmass())
        T = TT.load()
        self.T = T
        self.arms = TT.arms_of(T)
        # (D52's town arms B, E: the ledger is made after the run, so the town footprint is the live seats' own, PW-1472: each recent
        # step LivePolities.town_cells counts each people's town cells and note_towns adds them, as techspread.town_footprint does)
        self.towns = {"_cell_km2": float(h.cell_mkm2 * 1e6)} if TT.town_arms(T) else None

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
                 "demography": {kk: round(v, 4) for kk, v in l.demos().items()}, "generation_yr": h.gen_yr(l),
                 "reached": {str(m): v for m, v in h.cross.reached.get(l.id, {}).items()}}
                for k, l in enumerate(h.lines)]

    def _links(self) -> list[tuple]:
        """The contacts so far as the tree's intervals (techtree.links_of's shape): a pair touching at the last stored frame is still
        in touch, and its border is the one it shares at its last stored touch, not the median so far (PW-1473: a border grows as two
        peoples spread into each other, so the median so far is short of the whole run's median the after-run tree reads, every front
        is slowed, and the delays add up down a chain of takers: writing came 2,000 years late on 899985 seed 7; round9.md)."""
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
            to = 0.0 if s and abs(s[-1][0] - last) < 1e-9 else (float(s[-1][0]) if s else round(r["first"], 3))
            km = float(s[-1][1]) if s else 0.0
            out.append((ids[a], ids[b], float(round(r["first"], 3)), to, km))
        return out

    def _retime(self, ago: float):
        """Re-times the plain fronts still on their way (techtree.Calendar.advance fixes a front's arrival once, from the pair's border
        when it first looks): from the border known now, a front reaches the taker's middle at the giver's date (or the first contact)
        + its keyed delay at today's rate, as advance computes it; kept only if earlier (never later: the front keeps what it has
        crossed), so a front that set out over a short early border speeds up as the border grows. A front with no rate then (a
        border of 0) is timed once the border opens. The arm-touched fronts (D52) are re-timed by advance itself each step; language
        to a people under no sapiens node never arrives. PW-1473, round9.md."""
        cal = self.cal
        D, techs, arms = cal.D, cal.techs, cal.arms
        lk = {}
        for a, b, fr, to, km in cal.links:
            if fr >= ago >= to:
                lk[(a, b)] = lk[(b, a)] = (fr, min(km / D["contact_full_km"], 1.0))
        for k3, at in list(cal.arrive.items()):
            x, y, tid = k3
            if (at is not None and at >= ago) or (x, y) not in lk or tid in cal.known[y] or tid not in cal.known[x]:
                continue
            t = techs[tid]
            if t.get("modern_contact") and cal.node[y] is None:
                continue
            if arms and (tid in cal.touched or (x, y) in cal.kin) and not t.get("modern_contact"):
                continue
            fr, w = lk[(x, y)]
            op = 1 - 0.7 * float((cal.L[y].get("demography") or {}).get("insularity", 0.3))
            # (advance's plain front: contact_rate x border x openness x spread x the taker's culture)
            r = TT.contact_rate(TT._area_at(cal.series[y], ago), D) * w * op * t.get("spread", D["spread"]) * TT.domain_x(cal.culture[y][1], t)
            if r > 0 and (x, y) in cal.unit:
                new = min(cal.known[x][tid][0], fr) - cal.unit[(x, y)] / r
                if at is None or new > at:
                    cal.arrive[k3] = new

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

    def landmass(self) -> np.ndarray:
        """Each cell's present-day landmass for the region learners, as the after-run tree maps it (techtree.landmass_of,
        demes.landmass_rank): Crossings' ranks, today's sea taking the nearest landmass's. PW-1597 (lane 265, round22.md):
        Crossings' own label leaves today's sea out (-1), so a people that once lived on land now drowned or on another coast
        (the tortles at L6 4360a3 seed 7, 3.3 Myr ago: 18% of their range) lost that part of its range from its regions here
        and kept it in the after-run tree: the two trees split its pool differently from the deep past on."""
        if self._lm is None:
            from ..spread import nearest_label
            g = self.h.grid
            self._lm = nearest_label(np.asarray(self.h.cross.label), np.ones(g.n, np.bool_), g.nbr_off, g.nbr_idx)
        return self._lm

    def at_frame(self):
        """At the end of a step that stores a frame (LivePolities.end_step): keeps the presence as that frame stores it, for the
        regions the tree reads from the next step (the peoples may start or arrive before then: the frame is what it reads)."""
        self._stored = self.h.presence_stored()

    def note_towns(self, ago: float, cells: dict):
        """Adds one step of each people's town cells ({people: cells}, LivePolities.town_cells) to the footprint the tree reads
        ({people: (agos oldest first, cells)}, techtree.town_cells_at); a people seen before and not now has none now."""
        tw = self.towns
        for lid in [k for k in tw if k != "_cell_km2"] + [k for k in cells if k not in tw]:
            a, c = tw.setdefault(lid, ([], []))
            a.append(ago)
            c.append(float(cells.get(lid, 0)))

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
                self.cal = TT.Calendar(lines, tr.mode, tr.era, h.seed, self.T, tr.gods_mode, self.towns, self.arms)
            cal = self.cal
            seen = (len(h.contacts.agos) if h.contacts is not None else 0, sum(len(v) for v in h.tracks.values()))
            if seen != self._seen:  # (a frame was stored: the tracks, contacts and ranges moved)
                self._seen = seen
                # (its regions now, PW-1471: the range at the last stored frame, read as the frame stores it and the after-run tree
                # reads it back, regions_through: the peoples as wholes on established cells, on the after-run tree's landmass map,
                # landmass(). PW-1597 (lane 265, round22.md): before, the raw presence of each line down to 0.05, on Crossings' own
                # label, so the two trees split a people's pool differently from the deep past on)
                P = self._stored if self._stored is not None else h.presence_stored()
                self._stored = None
                cal.feed(lines or self.lines(), links=self._links(), have=self._have(), regions=cal.region_shares(P, self.landmass()))
                self._retime(float(step.ago))
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
                            towns=self.towns, arms=self.arms, landmass=self.landmass())
        have = {l["id"]: TT.goods_held(cal.T, present, goods, cal.idx[l["id"]]) for l in cal.people}
        cal.feed(lines, TT.links_of(contacts, cal.kind), TT.forced_of(pres, cal.techs, cal.L), have, (pres or {}).get("lines") or {},
                 cal.region_shares(present, self.landmass()))
        cal.advance()
        out = cal.result()
        out["inside_history"] = {"made_s": round(self.secs, 1), "arms": self.arms}
        return out
