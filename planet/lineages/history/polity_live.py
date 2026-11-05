"""Polities in the history, first cut (PW-1434, lane 183; design: docs/review/culture/polities/round7.md). Off by default
(params.POLITIES_LIVE).

In plain words: on each century step of the recent pass, the history now seats chiefdoms, states and dragon realms from its own
numbers, lets them claim land, fall and fight with polities v0's rules (planet/lineages/polities.py: the same reach, claim kernel, fall
hazard and war_v0), and then:
- the brakes read the live polities through the seam (history.rule): a state pacifies the cells it rules (G), hostile peoples count
  as a frontier only across a polity's border or on unruled land (F), and land a foreign state rules bars a faction from splitting off
  (C);
- a conquered people fares by the winner's attitudes (PW-1481, PW-1465; Daniel D54: from Genghis Khan razing cities to Cyrus's
  tolerance, in any era): the history keeps each people's tolerance and aggression (attitudes.Attitudes, stepped here each century
  from the tree's temperament and the live polities' own wars, rule and contacts). A people on the land that changed hands is kept,
  thinned or expelled by the winner's harshness to it: the tree's old enmity (StandIns.hostility) moved by the winner's tolerance,
  + TOL_X x (0.5 - tolerance), and the winner's aggression sets how hard (FATE_AT, FATE_CUT, TOL_X, AGG_MID; judgements). A winner
  of middling tolerance and aggression (0.5) fares exactly as the old placeholder (A);
- invasions you schedule reach as in the read-out (PW-1479, PW-1450): a strong row seats a war band (polities._war_bands) and sends an
  expedition across the gap (polities._expedition, invasions.campaign_budget), the same code as polities.derive.

What the history lacks, and how this cut stands in (round7.md section 2):
- towns: the settlement ledger is made after the run, so a seat is the history's own central place: the sedentary heads of a cell's
  hinterland (farmers: heads x the people's farm share) x the ledger's SHARE, at a cell that is the best of its ring, as
  settlements.py sizes its towns and cities (no site factor);
- the tech calendar: the tech tree runs inside the history (history.tech_live, PW-1466, round8.md): each step it runs down to the
  history's time first, and the gates (chiefdoms, proto-writing or writing, kingship, law, the military edges, boats, a dragon's hoards)
  read what each people knew by then. output.save writes the same calendar out as meta.techtree;
- cultures: a polity is a people's; an empire is a state whose subject peoples hold SUBJECT_SHARE of its sedentary heads.
The after-run read-out (polities.derive) is unchanged and still reads the ledger; this module writes polities_live.json beside it.
"""

from __future__ import annotations

import numpy as np

from .. import attitudes as AT
from .. import invasions as IV
from .. import polities as PO
from ..gridops import nbr_reduce
from ..spread import EST
from . import params as PM
from .rule import StandIns

INVASIONS = None  # (invasions you schedule, as invasions.clean reads them, PW-1433: they now act inside the history)

# ---- pacification by tier (G = 1 / (1 + STATE_Q x tech level x PACIFY[tier]) on the cells a polity rules, 1 on unruled land)
PACIFY = {"chiefdom": 1 / 3, "state": 1.0, "empire": 1.0, "dragon realm": 1 / 3}  # judgement: a chiefdom or a tribute-taking dragon keeps a third of a state's peace
STATE_BAR = 1.0  # judgement (Carneiro 2012's social circumscription made tight): land a foreign state rules bars a faction from splitting off fully
# ---- the loser's peoples (proposal-r2 3.3, "War is mostly a change of owner"; tolerance from the tree's enmities, judgement)
FATE_AT = (0.25, 0.6)  # the winner's harshness to a people on the taken land (_fates: hostility + TOL_X x (0.5 - tolerance)): under 0.25 kept, under 0.6 thinned, else expelled
TOL_X = 2.0  # judgement (PW-1481): tolerance 0..1 spans the whole harshness scale: at 0.5 the old enmity alone, at 0 + 1 (strangers expelled), at 1 - 1 (even old enemies kept)
FATE_CUT = {"kept": 0.0, "thinned": 0.25, "expelled": 0.8}  # the share of its presence on the taken cells it loses (once, at the conquest), for a winner of aggression AGG_MID
AGG_MID = 0.5  # judgement (PW-1481): the cut scales with the winner's aggression / AGG_MID (attitudes: 0.3 a plain people, 0.5 a martial one), never past all of it
FATE_MAX = 0.1  # guard: no people loses more than 10% of its heads to conquests in one step (the rest of the cut is waived)
NEED_X = 4.0  # cost (lane 201b): on an expedition's miss, how far the history looks for the nearest victim polity (the why-not's "lay N km
# away"), in multiples of the largest budget tried; past it the why-not says "more than N km". The read-out (derive) still looks without limit
SUBJECT_SHARE = PO.SUBJECT_SHARE
SEDENTARY_MIN = 1.0  # (heads: a cell with fewer sedentary heads is not settled land a dragon can take tribute from)


class LivePolities(StandIns):
    """StandIns with live polities: begin_step runs one polity step; pacification, frontier and circumscribed read its owners."""

    def __init__(self, h):
        super().__init__(h)
        g = h.grid
        self.g = g
        self.off, self.idx = np.asarray(g.nbr_off, np.int64), np.asarray(g.nbr_idx, np.int64)
        self.src = np.asarray(g.nbr_src, np.int64)
        c = np.asarray(g.centers, float)
        self.ekm = np.linalg.norm(c[self.idx] - c[self.src], axis=1) * PO.R_EARTH_KM
        self.cell_km2 = h.cell_mkm2 * 1e6
        self.dist = np.full(g.n, np.inf)
        self.touched = np.zeros(g.n, np.int64)
        self.claimed = np.zeros(g.n, np.int64)
        deg = np.diff(self.off)  # (the cells within two rings of each cell, once: (cell, other) pairs, the cell itself included)
        e = np.repeat(np.arange(len(self.idx)), deg[self.idx])
        dn = deg[self.idx]
        far = self.idx[self.off[self.idx[e]] + np.arange(len(e)) - np.repeat(np.cumsum(dn) - dn, dn)]  # (each neighbour's neighbours)
        pairs = np.unique(np.concatenate([np.stack([np.arange(g.n), np.arange(g.n)], 1), np.stack([self.src, self.idx], 1),
                                          np.stack([self.src[e], far], 1)]), axis=0)
        self.r2a, self.r2b = pairs[:, 0], pairs[:, 1]
        L = h.lines
        self.ppl = np.array([i for i, l in enumerate(L) if not (l.overlay or l.megafauna or l.marine)], np.int64)  # (peoples that may hold towns)
        self.dragons = [i for i, l in enumerate(L) if l.megafauna and "dragon" in l.id and l.trait("flies", 0.0)]
        meta = [{"id": l.id, "group_of": l.group_of, "parents": list(l.parents or [])} for l in L]
        self.anc = IV.ancestors(meta)
        rows, self.inv_notes = IV.clean(INVASIONS, strict=False) if INVASIONS else ([], [])
        self.inv_in = rows
        self.inv_rows = IV.hook_rows(rows, self, 0.1)
        self.inv_log = [IV.new_log() for _ in rows]
        # (what polities._expedition and attitudes.temperament read of each line, as the run's meta lineages hold it)
        self.lines = [{"id": l.id, "traits": list(l.traits or []), "way": l.way, "demography": l.demos()} for l in L]
        self.lidx = {l.id: i for i, l in enumerate(L)}
        self.att = AT.Attitudes({m["id"]: m for m in self.lines}, h.seed)  # (PW-1481: each people's tolerance and aggression, keyed by line)
        self.att_ago = None
        from . import megafauna as MG
        self.MG = MG
        # the polity state between steps (as polities.derive keeps it)
        self.owner = None  # (cell -> index into self.ruling this step, -1 none; None before the first polity)
        self.ruling: list = []
        self.tier_of: list = []
        self.prev_cap: dict = {}  # key -> tier last step
        self.open_: dict = {}  # key -> record index
        self.lord: dict = {}
        self.prov_state: set = set()
        self.cool: dict = {}
        self.founded: dict = {}  # key -> kyr ago of its founding (its luck)
        self.recs: list = []
        self.steps: list = []
        self.maps: list = []
        self.k = 0
        self.secs = 0.0
        self.run_key = f"try{h.seed}"
        from .tech_live import LiveTech
        self.tech = LiveTech(h)  # (the tech tree inside the history, PW-1466: output.save writes it out)

    # ------------------------------------------------------------ the gates
    def knows(self, people: str, tech: str, ago: float) -> bool:
        """Whether a people knew a tech by then: the tech tree inside the history (history.tech_live), as polities.Readout.knows."""
        x = (self.tech.known.get(people) or {}).get(tech)
        return bool(x) and float(x[0]) >= ago - 1e-9

    # ------------------------------------------------------------ one polity step
    def begin_step(self, step):
        if step.epoch == "recent" and getattr(self.tech, "towns", None) is not None:  # (D52's town arms B, E: the live seats' towns, PW-1472)
            self.tech.note_towns(float(step.ago), self.town_cells(float(step.ago)))
        self.tech.step(step)  # (every step: the tree runs down to the history's time before anything reads it)
        if step.epoch != "recent":
            return
        import time
        t0 = time.time()
        try:
            self._step(step)
            self._attitudes(step)
        finally:
            self.secs += time.time() - t0

    def _attitudes(self, step):
        """Steps each people's attitudes one century (attitudes.Attitudes.step): the memories _step set (conquest, rule, subjection),
        and its contacts now (the other peoples on or beside its land). No faiths in the history: no missionary term."""
        h = self.h
        ago = float(step.ago)
        dt = 0.0 if self.att_ago is None else max(self.att_ago - ago, 0.0)
        self.att_ago = ago
        ks = [int(k) for k in self.ppl if h.active.get(h.lines[k].id) and (h.p[k] >= EST).any()]
        if not ks:
            return
        M = np.stack([h.p[k] >= EST for k in ks]).astype(np.float32)
        D = np.stack([h._dilate(m > 0, 1) for m in M]).astype(np.float32)
        n = ((D @ M.T) > 0).sum(1) - 1  # (the other peoples on or beside its land)
        self.att.step(ago, dt, {k: h.lines[k].id for k in ks}, {k: int(n[i]) for i, k in enumerate(ks)}, set())

    def _heads(self):
        """(sedentary heads per cell, all peoples; lead people per cell, -1 none; peopled cells)."""
        h = self.h
        area = self.cell_km2
        sed = np.zeros(self.g.n)
        best = np.zeros(self.g.n)
        lead = np.full(self.g.n, -1, np.int64)
        heads = {}
        for k in self.ppl:
            if not h.active.get(h.lines[k].id):
                continue
            x = np.where(h.p[k] >= EST, h.p[k], 0.0)
            if not x.any():
                continue
            hk = x * np.asarray(h.dens_at(int(k)), float) * area
            heads[int(k)] = hk
            f = 0.0 if h._era[k] == "forager" else float(h._farm_share[k])
            sed += hk * f
            m = hk > best
            best[m] = hk[m]
            lead[m] = k
        return sed, lead, heads

    def _places(self, sed):
        """(the size of each cell's central place, town or city; the city size alone): settlements' SHARE on the hinterland's sedentary
        heads (one ring for a town, two for a city) at a cell that is the best of its ring, else 0."""
        from ..settlements import CONST
        g = self.g
        tie = 1.0 + 1e-9 * (g.n - np.arange(g.n)) / g.n  # (equal hinterlands: the lower cell id is the best of its ring)
        H1 = (sed + nbr_reduce(g, np.add, sed[self.idx])) * tie
        H2 = np.bincount(self.r2a, weights=sed[self.r2b], minlength=g.n) * tie
        mx1 = np.maximum(H1, nbr_reduce(g, np.maximum, H1[self.idx]))
        mx2 = np.maximum(H2, nbr_reduce(g, np.maximum, H2[self.idx]))
        mx2 = np.maximum(mx2, nbr_reduce(g, np.maximum, mx2[self.idx]))
        town = np.where(H1 >= mx1, CONST["SHARE"][2] * H1, 0.0)
        city = np.where(H2 >= mx2, CONST["SHARE"][3] * H2, 0.0)
        return np.maximum(town, city), city

    def town_cells(self, ago: float) -> dict:
        """Each people's town cells now (PW-1472: the town footprint D52's arms B and E read, techtree.Calendar.towns): the cells whose
        central place (_places) is of town size for the stage its lead people knows (settlements' TOWN_MIN by stage, as the ledger
        sizes a town), where that people knows towns. {people: cells}."""
        from ..settlements import CONST
        L, h = self.h.lines, self.h
        sed, lead, _ = self._heads()
        size = self._places(sed)[0]
        land = np.asarray(h._env_now["land"], bool)
        tm = CONST["TOWN_MIN"]
        out: dict = {}
        for k in np.unique(lead[(lead >= 0) & land & (size >= min(tm))]).tolist():
            lid = L[k].id
            if not self.knows(lid, "towns", ago):
                continue
            stage = 4 if self.knows(lid, "roads", ago) and self.knows(lid, "cities", ago) else 3 if self.knows(lid, "cities", ago) else 2
            out[lid] = int(((lead == k) & land & (size >= tm[stage])).sum())
        return out

    def _step(self, step):
        h, g = self.h, self.g
        ago = float(step.ago)
        L = h.lines
        any_gate = any(self.knows(L[k].id, "chiefdoms", ago) for k in self.ppl if h.active.get(L[k].id)) or bool(self.prev_cap)
        if not any_gate:
            return
        k_ = self.k
        self.k += 1
        env = h._env_now
        land = np.asarray(env["land"], bool)
        ice = (np.asarray(env["ice"], float) > 0) & land
        el = np.where(land, np.asarray(env["elevation"], float), 0.0)
        edz = np.abs(el[self.idx] - el[self.src])
        sea = ~land
        sed, lead, heads = self._heads()
        peopled = lead >= 0
        fall_p = 1.0 - float(np.exp(-PO.FALL_PER_CENTURY * step.dt * 10))
        from .. import dragon_ages as DA
        mort = DA.SCHEDULES[getattr(h.tree, "dragon_ages", None) or DA.DEFAULT][DA.STAGES.index(PO.DRAGON_RULER)]
        dragon_p = 1.0 - (1.0 - mort) ** (step.dt * 1000)
        luck = lambda key: f"{key}@{self.founded.get(key, ago)}"
        # 0. falls
        n_fell = 0
        for key, tier in list(self.prev_cap.items()):
            p = dragon_p if tier == "dragon realm" else (fall_p if tier in PO.FALL_TIERS else 0.0)
            if key in self.lord or PO.draw(self.run_key, luck(key), k_, "fall") >= p:
                continue
            self._close(key, ago, "collapsed")
            self.cool[key] = k_ + PO.COOL_STEPS - 1
            del self.prev_cap[key]
            for pk in [pk for pk, r in self.lord.items() if r == key]:
                del self.lord[pk]
            n_fell += 1
        # 1. town seats: the history's central places (settlements' SHARE on the hinterland's sedentary heads, the best of its ring)
        from ..settlements import CONST
        size, city = self._places(sed)
        town_min, city_min = float(CONST["TOWN_MIN"][-1]), float(CONST["CITY_MIN"])
        inc_cells = np.array([int(k[1:]) for k in self.prev_cap if k.startswith("c")], np.int64)
        thr = np.full(g.n, town_min)
        thr[inc_cells] *= PO.HOLD
        cand = np.flatnonzero(peopled & land & (size >= thr))
        wcell = np.zeros(g.n, bool)  # (cells where a people that knows proto-writing or writing lives, and their neighbours: D49's lenience)
        for k in heads:
            if any(self.knows(L[k].id, t, ago) for t in PO.WRITING_TECHS):
                wcell |= h.p[k] >= EST
        wcell = wcell | (nbr_reduce(g, np.maximum, wcell[self.idx].astype(np.int8)) > 0)
        seats = []
        for c in cand.tolist():
            k = int(lead[c])
            ppl = L[k].id
            key = f"c{c}"
            if not wcell[c] or not self.knows(ppl, "chiefdoms", ago):
                continue
            if size[c] < town_min * (PO.HOLD if key in self.prev_cap else 1.0) or not self.knows(ppl, "towns", ago):
                continue
            tier = "chiefdom"
            if (self.knows(ppl, "kingship", ago) or self.knows(ppl, "law", ago)) and self.knows(ppl, PO.STATE_WRITING, ago) \
                    and self.cool.get(key, -1) < k_ and self.knows(ppl, "cities", ago):  # (D49: a state needs its own people's writing)
                need = city_min * (1 - PO.HEMMED_X * float(self.hem[k])) * (PO.HOLD if self.prev_cap.get(key) in ("state", "empire") else 1.0)
                if city[c] >= need:
                    tier = "state"
            strong = tier == "state" and self.knows(ppl, PO.STRONG_TECH, ago)
            self.founded.setdefault(key, ago)
            seats.append({"key": key, "cell": c, "people": ppl, "line": k, "uid": None, "pop": float(size[c]), "tier": tier,
                          "cls": 0 if strong else (2 if tier == "state" else 3), "rank": float(size[c]) * (PO.INCUMBENT if key in self.prev_cap else 1.0)})
        # 2. dragon realms: one per dragon people's range (each connected piece), at its core
        for k in self.dragons:
            l = L[k]
            if not h.active.get(l.id) or not self.knows(l.id, "hoards", ago):
                continue
            held = h.p[k] >= EST
            if not held.any():
                continue
            lab, n = g.components(held)
            for j in range(n):
                cells = np.flatnonzero(held & (lab == j))
                core = int(cells[np.argmax(h.p[k][cells])])
                key = f"d{l.id}:{core}"
                if self.cool.get(key, -1) >= k_:
                    continue
                self.founded.setdefault(key, ago)
                seats.append({"key": key, "cell": core, "people": l.id, "line": k, "uid": None, "pop": 0.0, "tier": "dragon realm", "cls": 1,
                              "rank": len(cells) * (PO.INCUMBENT if key in self.prev_cap else 1.0), "own": cells})
        if IV.WAR_BAND and self.inv_rows:  # (PW-1479, D50 C: a strong row whose invaders rule only chiefdoms seats a war band, as derive)
            PO._war_bands(self, seats, self.inv_rows, ago, self.prev_cap, self.open_, self.anc)
        by_key = {s["key"]: s for s in seats}
        for pk in [pk for pk, r in self.lord.items() if r not in by_key or pk not in by_key]:
            self.lord.pop(pk, None)

        def order(s):
            r = by_key.get(self.lord.get(s["key"]))
            return (r["cls"], -r["rank"], r["key"], 1, -s["rank"]) if r else (s["cls"], -s["rank"], s["key"], 0, 0.0)
        seats.sort(key=order)
        wide = ({r for pk, r in self.lord.items() if pk in self.prov_state} if "conquest" in PO.WIDE_BY else set())
        # 3. claims (polities' kernel)
        owner = np.full(g.n, -1, np.int64)
        settled = sed >= SEDENTARY_MIN
        ruling, pid_of = [], {}
        for s in seats:
            root = self.lord.get(s["key"])
            if owner[s["cell"]] >= 0:
                if root is not None and pid_of.get(root) != owner[s["cell"]]:
                    del self.lord[s["key"]]
                continue
            if root is not None:
                if root not in pid_of:
                    del self.lord[s["key"]]
                else:
                    b, lx, sx = PO._reach(self, s, ago, root in wide)
                    PO._claim(s["cell"], b, lx, sx, PO.CLIMB_M, self.off, self.idx, self.ekm, edz, sea, ice, peopled, owner, pid_of[root],
                              self.dist, self.touched, self.claimed)
                    continue
            pid = len(ruling)
            if s["tier"] == "dragon realm":
                may = settled.copy()
                may[s["own"]] = True
                got = PO._claim(s["cell"], PO.DRAGON_KM, 1.0, 1.0, 0.0, self.off, self.idx, self.ekm, edz, sea, np.zeros(g.n, bool), may, owner, pid,
                                self.dist, self.touched, self.claimed)
                if not np.any(settled[self.claimed[:got]]):
                    owner[self.claimed[:got]] = -1
                    continue
            else:
                b, lx, sx = PO._reach(self, s, ago, s["key"] in wide)
                got = PO._claim(s["cell"], b, lx, sx, PO.CLIMB_M, self.off, self.idx, self.ekm, edz, sea, ice, peopled, owner, pid,
                                self.dist, self.touched, self.claimed)
            if got:
                pid_of[s["key"]] = pid
                ruling.append(s)
        # 4. war (polities.war_v0, unchanged)
        ppl_pid = np.bincount(owner[owner >= 0], weights=sed[owner >= 0], minlength=len(ruling))
        S_pid = [PO.strength(float(ppl_pid[p]), s["people"], self.knows, ago) for p, s in enumerate(ruling)]
        ctx = {"grid": g, "seats": ruling, "ago": ago, "step": k_, "run": self.run_key, "luck": luck, "prev_owner": self.owner, "strength": S_pid,
               "eligible": lambda p: ruling[p] is not None and ruling[p]["tier"] != "dragon realm" and ruling[p]["key"] in self.prev_cap and ruling[p]["key"] in self.open_,
               "invasions": self.inv_rows, "inv_log": self.inv_log, "ancestors": lambda p: self.anc.get(p, (p,)),
               "borders": lambda o=owner: PO.borders(o, g)}
        if IV.EXPEDITION and self.inv_rows:  # (PW-1479, D50 B: the expedition across the gap, the read-out's own hook)
            F = {"edz": edz, "sea": sea, "ice": ice}
            ctx["expedition"] = lambda o, st, vic, ruling=ruling, F=F: PO._expedition(self, F, ruling, o, st, vic, ago, wide, self.off, self.idx,
                                                                                             need_x=NEED_X)
        before = owner.copy()
        owner = PO.war_v0(owner, ctx)
        for lg in self.inv_log:  # (an expedition's two sides as record ids, as derive)
            for e in lg["exped"]:
                if "w" in e:
                    e["winner_id"], e["loser_id"] = self.open_[ruling[e.pop("w")]["key"]], self.open_[ruling[e.pop("l")]["key"]]
        for k in heads:  # (PW-1481: every people on the map has attitudes before a fate reads them)
            self.att.ensure(k, L[k].id)
        taken_log = []
        for w, l_, how in ctx.get("taken", []):
            wk, lk = ruling[w]["key"], ruling[l_]["key"]
            cells = np.flatnonzero(before == l_)
            fates = self._fates(ruling[w], cells, heads)
            if ruling[w]["line"] is not None:
                self.att.won(int(ruling[w]["line"]))
            ri = ctx.get("taken_row", {}).get(l_)
            km2 = float(len(cells) * self.cell_km2)
            if ri is not None:
                self.inv_log[ri]["took"].append([ago, ruling[l_]["people"], ruling[w]["people"], km2])
            lrec = self.recs[self.open_.pop(lk)] if lk in self.open_ else None
            wrec = self.recs[self.open_[wk]] if wk in self.open_ else None
            if lrec is not None:
                lrec["fell_kyr"], lrec["fell_how"] = ago, ("invaded by " if how == "invasion" else "conquered by ") + ruling[w]["people"]
            if wrec is not None:
                wrec["took"].append([round(ago, 3), ruling[l_]["people"], int(len(cells)), how, fates])
            taken_log.append({"winner": ruling[w]["people"], "loser": ruling[l_]["people"], "cells": int(len(cells)), "how": how, "fates": fates,
                              "winner_att": [round(v, 3) for v in self.att.get(int(ruling[w]["line"]))] if ruling[w]["line"] is not None else None})
            for pk in [pk for pk, r in self.lord.items() if r == lk]:
                self.lord[pk] = wk
            self.lord[lk] = wk
            (self.prov_state.add if ruling[l_]["tier"] == "state" else self.prov_state.discard)(lk)
            self.prev_cap.pop(lk, None)
        ruling = [s if (s is not None and owner[s["cell"]] == p) else None for p, s in enumerate(ruling)]
        # 5. tiers (an empire: a state whose subject peoples hold SUBJECT_SHARE of its sedentary heads), records
        tiers = [None] * len(ruling)
        cur = {}
        cnt = {t: 0 for t in PO.TIERS}
        step_map = []
        for p, s in enumerate(ruling):
            if s is None:
                continue
            cells = np.flatnonzero(owner == p)
            if not len(cells):
                continue
            tier = s["tier"]
            anc = self.anc.get(s["people"], {s["people"]})
            if s["line"] is not None and tier != "dragon realm":  # (PW-1481: rule over many, and subjection, for the attitudes)
                subj = [k for k in heads if not (L[k].id in anc or s["people"] in self.anc.get(L[k].id, ())) and heads[k][cells].any()]
                self.att.ruled(int(s["line"]), len(subj))
                for k in subj:
                    self.att.subject(k)
            if tier == "state":
                own = sum(float(heads[k][cells].sum()) for k in heads if L[k].id in anc or s["people"] in self.anc.get(L[k].id, ()))
                tot = sum(float(heads[k][cells].sum()) for k in heads)
                if tot > 0 and (tot - own) >= SUBJECT_SHARE * tot:
                    tier = "empire"
            tiers[p] = tier
            cnt[tier] += 1
            cur[s["key"]] = tier
            o = self.open_.get(s["key"])
            if o is None:
                self.open_[s["key"]] = o = len(self.recs)
                self.recs.append({"id": o, "key": s["key"], "people": s["people"], "cell": s["cell"], "founded_kyr": round(ago, 3), "tiers": [],
                                  "fell_kyr": None, "fell_how": None, "peak_mkm2": 0.0, "peak_kyr": None, "took": []})
            rec = self.recs[o]
            if s.get("war_band") is not None:  # (PW-1479: the war band a row seated, on the record and in the row's log, as derive)
                rec.setdefault("war_band", []).append(ago)
                self.inv_log[s["war_band"]]["war_band"].append([ago, o])
            if not rec["tiers"] or rec["tiers"][-1][1] != tier:
                rec["tiers"].append([round(ago, 3), tier])
            a = len(cells) * self.cell_km2 / 1e6
            if a > rec["peak_mkm2"]:
                rec["peak_mkm2"], rec["peak_kyr"] = round(a, 4), round(ago, 3)
            step_map.append([o, PO.TIERS.index(tier), PO._pack(cells)])
        for key in [k for k in self.open_ if k not in cur]:
            rec = self.recs[self.open_.pop(key)]
            if rec["fell_kyr"] is None:
                rec["fell_kyr"], rec["fell_how"] = round(ago, 3), "faded"
        sizes = [len(PO._unpack(e[2])) for e in step_map if e[1] in (1, 2)]
        big = max(((len(PO._unpack(e[2])), self.recs[e[0]]["people"]) for e in step_map if e[1] in (1, 2)), default=(0, None))
        self.steps.append({"ago": round(ago, 3), "counts": cnt, "states": cnt["state"] + cnt["empire"],
                           "ruled_mkm2": round(float((owner >= 0).sum()) * self.cell_km2 / 1e6, 2),
                           "largest_mkm2": round(big[0] * self.cell_km2 / 1e6, 3), "largest_people": big[1],
                           "over1": int(sum(s * self.cell_km2 / 1e6 > 1 for s in sizes)), "taken": taken_log, "collapsed": n_fell})
        self.maps.append(step_map)
        self.owner = owner
        self.ruling = ruling
        self.tier_of = tiers
        self.prev_cap = cur
        self._Fc = None  # (the frontier reads the new owners)

    def _close(self, key, ago, how):
        o = self.open_.pop(key, None)
        if o is not None:
            self.recs[o]["fell_kyr"], self.recs[o]["fell_how"] = round(ago, 3), how

    def _fates(self, win, cells, heads) -> dict:
        """The peoples on the land war took fare by the winner's attitudes (PW-1481): its harshness to each, its people's old enmity to
        theirs (hostility) + TOL_X x (0.5 - its tolerance), reads kept, thinned or expelled (FATE_AT); the cut (FATE_CUT) scales with its
        aggression / AGG_MID. A tolerant winner keeps even an old enemy's people more often; an intolerant one thins or expels even a
        people it had no quarrel with; an aggressive one cuts harder. Cuts their presence there once, never more than FATE_MAX of a
        people's heads in one step. Returns {people: [fate, heads lost]}."""
        h = self.h
        wk = win["line"]
        if wk is None or not len(cells):
            return {}
        out = {}
        wanc = self.anc.get(win["people"], {win["people"]})
        tol, agg = self.att.get(int(wk))
        for k, hk in heads.items():
            on = hk[cells]
            n = float(on.sum())
            if n <= 0:
                continue
            lid = h.lines[k].id
            if lid in wanc or win["people"] in self.anc.get(lid, ()):  # (the winner's own people and kin)
                continue
            z = float(self.hostility[wk, k]) + TOL_X * (0.5 - tol)
            fate = "kept" if z < FATE_AT[0] else ("thinned" if z < FATE_AT[1] else "expelled")
            cut = min(1.0, FATE_CUT[fate] * agg / AGG_MID)
            if cut > 0:
                tot = float(hk.sum())
                done = self.__dict__.setdefault("_cut_now", {})
                spent = done.get((k, self.k), 0.0)
                cut = min(cut, max(0.0, (FATE_MAX * tot - spent) / n))
                if cut > 0:
                    h.p[k][cells] *= (1.0 - cut)
                    h.p[k][cells[h.p[k][cells] < EST]] = 0.0
                    hk = heads[k] = hk.copy()
                    hk[cells] *= 1.0 - cut
                    done[(k, self.k)] = spent + cut * n
            out[lid] = [fate, int(round(cut * n))]
        return out

    # ------------------------------------------------------------ the seam's answers, from the live polities
    def pacification(self, k, step):
        if self.owner is None:
            return 1.0
        lev = self.MG.tech_level(self.h.tree.era, step.ago)
        w = np.array([PACIFY.get(t, 0.0) if t else 0.0 for t in self.tier_of] + [0.0])
        return 1.0 / (1.0 + PM.STATE_Q * lev * w[self.owner])  # (owner -1 reads the last entry: unruled, 1)

    def frontier(self, k):
        if self.owner is None:
            return super().frontier(k)
        h, g = self.h, self.g
        c = self._Fc
        if c is None or c[0] is not h._pm:
            J = np.flatnonzero(self.hostility.any(0))
            HP = np.clip(self.hostility[:, J].astype(np.float32) @ h._pm[J].astype(np.float32), 0.0, 1.0) if len(J) else None
            o = self.owner
            across = (o[self.idx] < 0) | (o[self.idx] != o[self.src])  # (an edge into unruled land or another polity's)
            c = self._Fc = (h._pm, HP, {}, across, o < 0)
        F = c[2].get(k)
        if F is None:
            x = c[1][k] if c[1] is not None else None
            if x is None or not x.any():
                F = np.zeros(g.n)
            else:  # (hostile peoples under the same ruler are co-subjects: they count only on unruled land or across a border)
                F = np.clip((x * c[4] + nbr_reduce(g, np.add, x[self.idx] * c[3])) / (1.0 + h._deg), 0.0, 1.0)
            c[2][k] = F
        return F

    def circumscribed(self, l, k, held, room, crowd) -> float:
        base = super().circumscribed(l, k, held, room, crowd)
        if self.owner is None or not any(t in ("state", "empire") for t in self.tier_of if t):
            return base
        h = self.h
        K0 = self.K0.get(k)
        if K0 is None:
            return base
        ring = h._dilate(held, 1) & ~held
        if l.trait("sea", 0.0):
            ring &= h._land_now
        if not ring.any():
            return base
        anc = self.anc.get(l.id, {l.id})
        foreign = np.array([bool(s) and t in ("state", "empire") and s["people"] not in anc and l.id not in self.anc.get(s["people"], ())
                            for s, t in zip(self.ruling, self.tier_of)] + [False])
        fr = foreign[self.owner] & ring
        if not fr.any():
            return base
        land = h._land_now
        taken = (h._cntp - h._pm[k]) > 0
        free = land & (K0 >= 0.3) & (room >= 0.3) & ~taken & ~fr
        bar = np.where(free, 0.0, np.where(fr, STATE_BAR, np.where(land & taken, PM.SOCIAL_Q, 1.0)))
        return float(max(PM.SOCIAL_Q * float(crowd), bar[ring].mean()))

    # ------------------------------------------------------------ the record
    def doc(self) -> dict:
        from .. import invasions as IV
        return {"format": "procgen-polities-live/1", "first_cut": True, "calendar": "the tech tree inside the history (PW-1466)",
                "made_s": round(self.secs, 1), "tech_s": round(self.tech.secs, 1), "steps": self.steps, "polities": self.recs, "maps": self.maps,
                "attitudes": self.att.doc() | {"keyed_by": "people (line index; the history has no cultures)"},
                "invasions": [{"row": r, "log": {k: v for k, v in lg.items()}} for r, lg in zip(self.inv_in, self.inv_log)],
                "invasion_problems": self.inv_notes,
                "constants": {"FATE_AT": FATE_AT, "FATE_CUT": FATE_CUT, "FATE_MAX": FATE_MAX, "PACIFY": PACIFY, "STATE_BAR": STATE_BAR, "AGG_MID": AGG_MID, "TOL_X": TOL_X,
                              "CAMPAIGN_KM": IV.CAMPAIGN_KM, "NEED_X": NEED_X,
}}
