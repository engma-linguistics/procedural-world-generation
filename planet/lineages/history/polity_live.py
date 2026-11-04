"""Polities in the history, first cut (PW-1434, lane 183; design: docs/review/culture/polities/round7.md). Off by default
(params.POLITIES_LIVE).

In plain words: on each century step of the recent pass, the history now seats chiefdoms, states and dragon realms from its own
numbers, lets them claim land, fall and fight with polities v0's rules (planet/lineages/polities.py: the same reach, claim kernel, fall
hazard and war_v0), and then:
- the brakes read the live polities through the seam (history.rule): a state pacifies the cells it rules (G), hostile peoples count
  as a frontier only across a polity's border or on unruled land (F), and land a foreign state rules bars a faction from splitting off
  (C);
- a conquered people fares by the winner's tolerance, read from the tree's old enmities (StandIns.hostility): kept, thinned or
  expelled from the land that changed hands (FATE_AT, FATE_CUT; judgements).

What the history lacks, and how this cut stands in (round7.md section 2):
- towns: the settlement ledger is made after the run, so a seat is the history's own central place: the sedentary heads of a cell's
  hinterland (farmers: heads x the people's farm share) x the ledger's SHARE, at a cell that is the best of its ring, as
  settlements.py sizes its towns and cities (no site factor);
- the tech calendar: the tech tree is made after the run, so the gates (chiefdoms, writing, kingship, law, the military edges, boats)
  come from CALENDAR when a harness lends one (another run's meta.techtree.known: a test of the rules, not a product), else from the
  era's tech level (megafauna.tech_level) for a farming people (PROXY_LEV: a plainly labelled judgement);
- cultures: a polity is a people's; an empire is a state whose subject peoples hold SUBJECT_SHARE of its sedentary heads.
The after-run read-out (polities.derive) is unchanged and still reads the ledger; this module writes polities_live.json beside it.
"""

from __future__ import annotations

import numpy as np

from .. import polities as PO
from ..gridops import nbr_reduce
from ..spread import EST
from . import params as PM
from .rule import StandIns

CALENDAR = None  # (a harness's borrowed calendar: {people: {tech: [kyr ago, how, from]}}, another run's meta.techtree.known; None: PROXY_LEV)
INVASIONS = None  # (invasions you schedule, as invasions.clean reads them, PW-1433: they now act inside the history)

# ---- the gates without a tech tree (judgement): the era's tech level (megafauna.tech_level, 0..1) at which a people knows each, for
# the social techs only a farming people (farm share PROXY_FARM or more, past its forager era); a dragon people knows hoards
PROXY_LEV = {"chiefdoms": 0.05, "writing": 0.1, "towns": 0.0, "cities": 0.1, "kingship": 0.15, "law": 0.4, "bronze": 0.1, "iron": 0.4,
             "riding": 0.3, "standing_army": 0.75, "roads": 0.55, "bureaucracy": 0.55, "sails": 0.15, "canoes": 0.0, "hoards": 0.0}
PROXY_SOCIAL = ("chiefdoms", "writing", "towns", "cities", "kingship", "law", "standing_army", "roads", "bureaucracy")
PROXY_FARM = 0.3
# ---- pacification by tier (G = 1 / (1 + STATE_Q x tech level x PACIFY[tier]) on the cells a polity rules, 1 on unruled land)
PACIFY = {"chiefdom": 1 / 3, "state": 1.0, "empire": 1.0, "dragon realm": 1 / 3}  # judgement: a chiefdom or a tribute-taking dragon keeps a third of a state's peace
STATE_BAR = 1.0  # judgement (Carneiro 2012's social circumscription made tight): land a foreign state rules bars a faction from splitting off fully
# ---- the loser's peoples (proposal-r2 3.3, "War is mostly a change of owner"; tolerance from the tree's enmities, judgement)
FATE_AT = (0.25, 0.6)  # winner's hostility to a people on the taken land: under 0.25 kept, under 0.6 thinned, else expelled
FATE_CUT = {"kept": 0.0, "thinned": 0.25, "expelled": 0.8}  # the share of its presence on the taken cells it loses (once, at the conquest)
FATE_MAX = 0.1  # guard: no people loses more than 10% of its heads to conquests in one step (the rest of the cut is waived)
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
        from .. import invasions as IV
        meta = [{"id": l.id, "group_of": l.group_of, "parents": list(l.parents or [])} for l in L]
        self.anc = IV.ancestors(meta)
        rows, self.inv_notes = IV.clean(INVASIONS, strict=False) if INVASIONS else ([], [])
        self.inv_in = rows
        self.inv_rows = IV.hook_rows(rows, self, 0.1)
        self.inv_log = [IV.new_log() for _ in rows]
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

    # ------------------------------------------------------------ the gates
    def knows(self, people: str, tech: str, ago: float) -> bool:
        if CALENDAR is not None:
            x = (CALENDAR.get(people) or {}).get(tech)
            return bool(x) and float(x[0]) >= ago - 1e-9
        k = self.h.idx.get(people)
        if k is None:
            return False
        if k in self.dragons:
            return tech == "hoards"
        lev = self.MG.tech_level(self.h.tree.era, ago)
        if lev < PROXY_LEV.get(tech, 2.0):
            return False
        if tech in PROXY_SOCIAL:
            return float(self.h._farm_share[k]) >= PROXY_FARM and self.h._era[k] != "forager"
        return True

    # ------------------------------------------------------------ one polity step
    def begin_step(self, step):
        if step.epoch != "recent":
            return
        import time
        t0 = time.time()
        try:
            self._step(step)
        finally:
            self.secs += time.time() - t0

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
        tie = 1.0 + 1e-9 * (g.n - np.arange(g.n)) / g.n  # (equal hinterlands: the lower cell id is the best of its ring)
        H1 = (sed + nbr_reduce(g, np.add, sed[self.idx])) * tie
        H2 = np.bincount(self.r2a, weights=sed[self.r2b], minlength=g.n) * tie
        mx1 = np.maximum(H1, nbr_reduce(g, np.maximum, H1[self.idx]))
        mx2 = np.maximum(H2, nbr_reduce(g, np.maximum, H2[self.idx]))
        mx2 = np.maximum(mx2, nbr_reduce(g, np.maximum, mx2[self.idx]))
        town = np.where(H1 >= mx1, CONST["SHARE"][2] * H1, 0.0)
        city = np.where(H2 >= mx2, CONST["SHARE"][3] * H2, 0.0)
        town_min, city_min = float(CONST["TOWN_MIN"][-1]), float(CONST["CITY_MIN"])
        size = np.maximum(town, city)
        inc_cells = np.array([int(k[1:]) for k in self.prev_cap if k.startswith("c")], np.int64)
        thr = np.full(g.n, town_min)
        thr[inc_cells] *= PO.HOLD
        cand = np.flatnonzero(peopled & land & (size >= thr))
        wcell = np.zeros(g.n, bool)  # (cells where a people that knows writing lives, and their neighbours: the writing gate's lenience)
        for k in heads:
            if self.knows(L[k].id, "writing", ago):
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
            if (self.knows(ppl, "kingship", ago) or self.knows(ppl, "law", ago)) and self.cool.get(key, -1) < k_ and self.knows(ppl, "cities", ago):
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
        before = owner.copy()
        owner = PO.war_v0(owner, ctx)
        taken_log = []
        for w, l_, how in ctx.get("taken", []):
            wk, lk = ruling[w]["key"], ruling[l_]["key"]
            cells = np.flatnonzero(before == l_)
            fates = self._fates(ruling[w], cells, heads)
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
            taken_log.append({"winner": ruling[w]["people"], "loser": ruling[l_]["people"], "cells": int(len(cells)), "how": how, "fates": fates})
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
            if tier == "state":
                anc = self.anc.get(s["people"], {s["people"]})
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
        """The peoples on the land war took fare by the winner's tolerance (its people's hostility to theirs): kept, thinned or expelled.
        Cuts their presence there once (FATE_CUT), never more than FATE_MAX of a people's heads in one step. Returns {people: [fate, heads lost]}."""
        h = self.h
        wk = win["line"]
        if wk is None or not len(cells):
            return {}
        out = {}
        wanc = self.anc.get(win["people"], {win["people"]})
        for k, hk in heads.items():
            on = hk[cells]
            n = float(on.sum())
            if n <= 0:
                continue
            lid = h.lines[k].id
            if lid in wanc or win["people"] in self.anc.get(lid, ()):  # (the winner's own people and kin)
                continue
            z = float(self.hostility[wk, k])
            fate = "kept" if z < FATE_AT[0] else ("thinned" if z < FATE_AT[1] else "expelled")
            cut = FATE_CUT[fate]
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
        return {"format": "procgen-polities-live/1", "first_cut": True, "calendar": "borrowed" if CALENDAR is not None else "era proxy",
                "made_s": round(self.secs, 1), "steps": self.steps, "polities": self.recs, "maps": self.maps,
                "invasions": [{"row": r, "log": {k: v for k, v in lg.items()}} for r, lg in zip(self.inv_in, self.inv_log)],
                "invasion_problems": self.inv_notes,
                "constants": {"FATE_AT": FATE_AT, "FATE_CUT": FATE_CUT, "FATE_MAX": FATE_MAX, "PACIFY": PACIFY, "STATE_BAR": STATE_BAR,
                              "PROXY_LEV": PROXY_LEV, "PROXY_FARM": PROXY_FARM}}
