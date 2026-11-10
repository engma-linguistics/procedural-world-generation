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
  + TOL_X x (0.5 - tolerance), raised by its aggression in proportion to its intolerance (PW-1487, Daniel D59 C: a martial, intolerant
  winner expels or razes in any era; a tolerant conqueror, Cyrus, still keeps), and the winner's aggression also sets how hard
  (FATE_AT, FATE_CUT, TOL_X, AGG_HARSH, AGG_MID; judgements). A plain winner (aggression AGG_HARSH) of middling tolerance (0.5) fares
  exactly as the old placeholder (A);
- invasions you schedule reach as in the read-out (PW-1479, PW-1450): a strong row seats a war band (polities._war_bands) and sends an
  expedition across the gap (polities._expedition, invasions.campaign_budget), the same code as polities.derive.

What the history lacks, and how this cut stands in (round7.md section 2):
- towns: the settlement ledger is made after the run, so a seat is the history's own central place: the sedentary heads of a cell's
  hinterland (farmers: heads x the people's farm share) x the ledger's SHARE x the ledger's site factor (a harbour on a coast that is
  still a coast, a navigable river, fresh water, fertile ground, a pass: settlements._site_factor, PW-1587), at a cell that is the
  best of its ring by the same score, as settlements.py sizes its towns and cities. A seat is a state where its place, of either tier,
  reaches a city's size less HEMMED_X x how hemmed in the seat is over its own two rings (polities._hemmed's reading), as derive tests
  a site's people; the ledger caps a town under a city's size, so a town passes only where it is hemmed in (PW-1594);
- the tech calendar: the tech tree runs inside the history (history.tech_live, PW-1466, round8.md): each step it runs down to the
  history's time first, and the gates (chiefdoms, proto-writing or writing, kingship, law, the military edges, boats, a dragon's hoards)
  read what each people knew by then. output.save writes the same calendar out as meta.techtree;
- cultures: a polity is a people's; an empire is a state whose subject peoples hold SUBJECT_SHARE of its sedentary heads.
This module writes polities_live.json; when a run has it, the after-run read-out (polities.derive, PW-1575) draws these polities, not
its own: the viewer's Polities layer, the state cards and the religion read-out's rulers are this map, named and coloured by derive.
"""

from __future__ import annotations

import numpy as np

from .. import attitudes as AT
from .. import invasions as IV
from .. import polities as PO
from ..gridops import nbr_reduce
from ..spread import EST
from .gridops import _csr_gather
from . import params as PM
from ..seafood import rings_for
from .rule import StandIns

FORMAT = "procgen-polities-live/2"  # (/2, PW-1575: map entries carry the seat's people and the provinces; took and the row logs carry record ids)
INVASIONS = None  # (invasions you schedule, as invasions.clean reads them, PW-1433: they now act inside the history)

# ---- pacification by tier (G = 1 / (1 + STATE_Q x tech level x PACIFY[tier]) on the cells a polity rules, 1 on unruled land)
PACIFY = {"chiefdom": 1 / 3, "state": 1.0, "empire": 1.0, "dragon realm": 1 / 3}  # judgement: a chiefdom or a tribute-taking dragon keeps a third of a state's peace
STATE_BAR = 1.0  # judgement (Carneiro 2012's social circumscription made tight): land a foreign state rules bars a faction from splitting off fully
# ---- the loser's peoples (proposal-r2 3.3, "War is mostly a change of owner"; tolerance from the tree's enmities, judgement)
FATE_AT = (0.25, 0.6)  # the winner's harshness to a people on the taken land (_fates: harshness()): under 0.25 kept, under 0.6 thinned, else expelled
TOL_X = 2.0  # judgement (PW-1481): tolerance 0..1 spans the whole harshness scale: at 0.5 the old enmity alone, at 0 + 1 (strangers expelled), at 1 - 1 (even old enemies kept)
FATE_CUT = {"kept": 0.0, "thinned": 0.25, "expelled": 0.8}  # the share of its presence on the taken cells it loses (once, at the conquest), for a winner of aggression AGG_MID
AGG_HARSH = AT.AGG_BASE  # reasoned (PW-1487, D59 C): the aggression at which a winner is as harsh as its tolerance alone says (a plain
# people's, attitudes.AGG_BASE 0.3). Each 0.1 of aggression above it adds TOL_X x 0.1 x (1 - tolerance): a fully intolerant winner's
# aggression weighs exactly as its tolerance does (TOL_X), a fully tolerant one's not at all. The gate is Daniel's own two poles (D54):
# Genghis Khan and Cyrus were both great conquerors, so aggression cannot make every conqueror harsh; it makes an intolerant one harsher
AGG_MID = 0.5  # judgement (PW-1481): the cut scales with the winner's aggression / AGG_MID (attitudes: 0.3 a plain people, 0.5 a martial one), never past all of it
FATE_MAX = 0.1  # guard: no people loses more than 10% of its heads to conquests in one step (the rest of the cut is waived)
NEED_X = 4.0  # cost (lane 201b): on an expedition's miss, how far the history looks for the nearest victim polity (the why-not's "lay N km
# away"), in multiples of the largest budget tried; past it the why-not says "more than N km". The read-out (derive) still looks without limit
SUBJECT_SHARE = PO.SUBJECT_SHARE
SEDENTARY_MIN = 1.0  # (heads: a cell with fewer sedentary heads is not settled land a dragon can take tribute from)
REVOLT = True  # switch (PW-1513, desk D67 B, Daniel 11-08: on, 'as long as the rulers haven't softened': the fate is read from the winner's attitudes at the retaking, so a ruler grown tolerant keeps them): a people that submitted to a ruler and later rises against
# it (seats a polity of its own on land that ruler held last step, while that ruler still stands) has broken its terms: when the same
# ruler next takes land it lives on, it may not submit again and meets the fate the winner's attitudes then give it (Herat, 1222).
# No new number: the trigger is the polities' own seats and claims, the fate is _fates' own. Off: output byte-identical to before


def harshness(hostility: float, tol: float, agg: float) -> float:
    """A winner's harshness to a people on the land it took (PW-1481, PW-1487): its people's old enmity to theirs, + TOL_X x (0.5 -
    tolerance), + TOL_X x (aggression - AGG_HARSH) x (1 - tolerance). Read against FATE_AT: kept, thinned, expelled."""
    return hostility + TOL_X * (0.5 - tol) + TOL_X * (agg - AGG_HARSH) * (1.0 - tol)


def ring_pairs(off, idx, r: int):
    """(a, b): every (cell, other) pair with `other` within r neighbour rings of `cell`, the cell itself included, once each, sorted
    by cell then other (PW-1627: any number of rings; the frontier alone is expanded, so an L8 refine's four rings stay cheap)."""
    off, idx = np.asarray(off, np.int64), np.asarray(idx, np.int64)
    n = len(off) - 1
    deg = np.diff(off)
    seen = np.arange(n, dtype=np.int64) * (n + 1)  # (codes a * n + b: each cell itself)
    fa, fb = np.arange(n, dtype=np.int64), np.arange(n, dtype=np.int64)
    for _ in range(r):
        d = deg[fb]
        na = np.repeat(fa, d)
        nb = idx[np.repeat(off[fb], d) + np.arange(int(d.sum())) - np.repeat(np.cumsum(d) - d, d)]
        cand = np.unique(na * n + nb)
        new = cand[~np.isin(cand, seen, assume_unique=True)]
        seen = np.union1d(seen, new)
        fa, fb = new // n, new % n
    return seen // n, seen % n


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
        # (the cells within HEMMED_KM of each cell, once: (cell, other) pairs, the cell itself included; PW-1627: two rings at L7,
        # four on an L8 refine, the seat's hemmed-in reading and the city's hinterland in km together)
        from ..settlements import CONST as SE_CONST
        self.r_town, self.r_city = rings_for(g, SE_CONST["TOWN_KM"]), rings_for(g, SE_CONST["CITY_KM"])
        self.r2a, self.r2b = ring_pairs(self.off, self.idx, rings_for(g, PO.HEMMED_KM))
        self.r2off = np.searchsorted(self.r2a, np.arange(g.n + 1))  # (pairs are sorted by cell: each cell's ring, r2b[r2off[c]:r2off[c+1]])
        self._pairs: dict[int, tuple] = {}
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
        from .. import settlements as SE  # (PW-1587: the ledger's site factor, on the world's own site layers)
        self.SE = SE
        self.W = SE._world_layers(getattr(getattr(h, "ps", None), "world_ref", None), g.n)
        # the polity state between steps (as polities.derive keeps it)
        self.owner = None  # (cell -> index into self.ruling this step, -1 none; None before the first polity)
        self.ruling: list = []
        self.tier_of: list = []
        self.prev_cap: dict = {}  # key -> tier last step
        self.open_: dict = {}  # key -> record index
        self.lord: dict = {}
        self.prov_state: set = set()
        self.prov_rec: dict = {}  # (province key -> the record id of the polity it was when taken: the read-out's provinces, PW-1575)
        self.cool: dict = {}
        self.founded: dict = {}  # key -> kyr ago of its founding (its luck)
        self.recs: list = []
        self.steps: list = []
        self.maps: list = []
        self.k = 0
        self.secs = 0.0
        self._ago = 0.0
        self.run_key = f"try{h.seed}"
        self.submitted: dict = {}  # (REVOLT: people -> the ruling peoples it submitted to)
        self.revolted: dict = {}  # (REVOLT: (people, ruler) -> kyr ago of its rising, until the ruler next takes land it lives on)
        self.submissions: list = []  # (REVOLT: [ago, people, ruler] per submission)
        self.revolts: list = []  # (REVOLT: [ago, people, ruler, seat cell] per rising)
        self.punished: list = []  # (REVOLT: [ago, people, ruler, fate, heads lost, heads moved] per retaking that found a revolt)
        from .tech_live import LiveTech
        self.tech = LiveTech(h)  # (the tech tree inside the history, PW-1466: output.save writes it out)

    # ------------------------------------------------------------ the gates
    def knows(self, people: str, tech: str, ago: float) -> bool:
        """Whether a people knew a tech by then: the tech tree inside the history (history.tech_live), as polities.Readout.knows."""
        x = (self.tech.known.get(people) or {}).get(tech)
        return bool(x) and float(x[0]) >= ago - 1e-9

    # ------------------------------------------------------------ one polity step
    def end_step(self, step):
        """D52's town arms B, E (PW-1472): each people's town cells, counted at the end of the step on the state it ends with (the
        state a frame stored at this step holds, as the ledger reads it); the tree reads them from the next step on (PW-1612 B).
        On a step that stores a frame the tree also keeps the presence as stored, for its regions (LiveTech.at_frame, PW-1597)."""
        if step.store and hasattr(self.tech, "at_frame"):
            self.tech.at_frame()
        if step.epoch == "recent" and getattr(self.tech, "towns", None) is not None:
            self.tech.note_towns(float(step.ago), self.town_cells(float(step.ago), fresh=step.store))

    def begin_step(self, step):
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

    def _site(self):
        """Each cell's site factor now (settlements._site_factor, the ledger's own: 1 an ordinary inland cell; a harbour counts only
        on a cell that is a coast at this time)."""
        land = np.asarray(self.h._env_now["land"], bool)
        coastal = land & (nbr_reduce(self.g, np.maximum, (~land)[self.idx].astype(np.int8)) > 0)
        return self.SE._site_factor(self.W, coastal, self.SE.CONST)

    def _hin(self, v, r):
        """The sum of v over each cell's cells within r rings (the cell itself included): a town's or a city's hinterland."""
        if r == 1:  # (the one-ring sum as it always was, so L7 is unchanged to the bit)
            return v + nbr_reduce(self.g, np.add, v[self.idx])
        if r not in self._pairs:
            self._pairs[r] = (self.r2a, self.r2b) if r == rings_for(self.g, PO.HEMMED_KM) else ring_pairs(self.off, self.idx, r)
        a, b = self._pairs[r]
        return np.bincount(a, weights=v[b], minlength=self.g.n)

    def _ringmax(self, v, r):
        """The max of v over each cell's cells within r rings (itself included)."""
        for _ in range(r):
            v = np.maximum(v, nbr_reduce(self.g, np.maximum, v[self.idx]))
        return v

    def _places(self, sed, q):
        """(the size of each cell's central place, town or city; the city size alone): settlements' SHARE on the hinterland's sedentary
        heads (TOWN_KM for a town, CITY_KM for a city) x the cell's site factor q, at a cell that is the best of its ring by that score
        (as the ledger), else 0."""
        from ..settlements import CONST
        g = self.g
        tie = 1.0 + 1e-9 * (g.n - np.arange(g.n)) / g.n  # (equal hinterlands: the lower cell id is the best of its ring)
        H1, H2 = self._hin(sed, self.r_town) * q * tie, self._hin(sed, self.r_city) * q * tie
        mx1, mx2 = self._ringmax(H1, self.r_town), self._ringmax(H2, self.r_city)
        town = np.where(H1 >= mx1, CONST["SHARE"][2] * H1, 0.0)
        city = np.where(H2 >= mx2, CONST["SHARE"][3] * H2, 0.0)
        return np.maximum(town, city), city

    def _second_places(self, heads, lead, q):
        """(each cell's second people's own place, as the settlement ledger sizes it: MINORITY_SHARE of its settled heads, saturating
        toward MINORITY_MAX, x the cell's site factor q, where it is SECOND_MIN of the cell's heads or more and not the lead people's
        own kin; that people, -1 none). No fishers or holds."""
        from ..settlements import CONST
        n = self.g.n
        L = self.h.lines
        tot = np.zeros(n)
        for hk in heads.values():
            tot += hk
        best, second = np.zeros(n), np.full(n, -1, np.int64)
        for k, hk in heads.items():
            kin = np.array([j >= 0 and (L[j].id in self.anc.get(L[k].id, {L[k].id}) or L[k].id in self.anc.get(L[j].id, ())) for j in range(-1, len(L))])
            m = (hk > best) & ~kin[lead + 1]
            best[m], second[m] = hk[m], k
        ok = (second >= 0) & (best >= CONST["SECOND_MIN"] * np.maximum(tot, 1e-12))
        farm = np.array([0.0 if self.h._era[k] == "forager" else float(self.h._farm_share[k]) for k in range(len(L))] + [0.0])
        own = np.where(ok, CONST["MINORITY_SHARE"] * best * farm[second], 0.0)
        own = own * CONST["MINORITY_MAX"] / (own + CONST["MINORITY_MAX"]) * q
        return own, np.where(ok, second, -1)

    def _hem_local(self, c, k, people, ago, land, ice, el) -> float:
        """How hemmed in the seat at cell c is, 0..1, as the read-out reads it (polities._hemmed): over the cells within HEMMED_KM of it,
        sea (for a people without boats), ice and peaks of 3,000 m or more bar fully; land other peoples hold and its own does not bars
        SOCIAL_Q; the rest bars nothing."""
        ring = self.r2b[self.r2off[c]:self.r2off[c + 1]]
        ring = ring[ring != c]
        if not len(ring):
            return 1.0
        boats = any(self.knows(people, t, ago) for t in PO.BOATS)
        h = self.h
        others = np.zeros(len(ring), bool)
        for j in self.ppl:
            if j != k and h.active.get(h.lines[j].id):
                others |= h.p[j][ring] >= EST
        own = h.p[k][ring] >= EST
        bar = np.where(~land[ring], 0.0 if boats else 1.0,
                       np.where(ice[ring] | (el[ring] >= 3000), 1.0, np.where(others & ~own, PM.SOCIAL_Q, 0.0)))
        return float(bar.mean())

    def _stage(self, people: str, ago: float) -> int:
        """A town-knowing people's settlement stage (settlements' TOWN_MIN index): 4 with cities and roads, 3 with cities, else 2."""
        return 4 if self.knows(people, "roads", ago) and self.knows(people, "cities", ago) else 3 if self.knows(people, "cities", ago) else 2

    def _allowed(self, k: int, ago: float) -> tuple:
        """(the largest place tier a line's techs allow, its settlement stage), as the ledger's allowed and stage_of: villages
        first (no towns without them), then one tier for each of villages, towns and cities known (a mining people's 'delving' or
        'fortifications' counting as cities); stage 4 with cities and roads."""
        from ..settlements import TECH
        lid = self.h.lines[k].id
        if not self.knows(lid, TECH[0], ago):
            return 0, 0
        cities = self.knows(lid, TECH[2], ago) or (self._miner(k) and any(self.knows(lid, t, ago) for t in ("delving", "fortifications")))
        al = min(int(self.knows(lid, TECH[1], ago)) + int(cities) + 1, 3)
        return al, al + int(al >= 3 and self.knows(lid, "roads", ago))

    def town_cells(self, ago: float, fresh: bool = True) -> dict:
        """Each people's town cells now (PW-1472: the town footprint D52's arms B, E and S read, techtree.Calendar.towns), counted
        as the settlement ledger counts them (techspread.town_footprint): a cell counts for a people where it holds a *site* of town
        size for its stage (settlements' TOWN_MIN). Call once per century step (end_step does): the sites carry over.

        PW-1608: the ledger's own rule (settlements.derive) on the ledger's own inputs, taken from the history now as a stored frame
        takes them: the land use's people and farmers per cell (landuse.frame_inputs, quantised as stored) and the cells'
        composition (who leads a cell and who is second, by compose's heads: frame._composition). Each cell has a chief place (its
        lead people's) and a second people's own place. The target is the ledger's: the largest of a village on the cell's own
        settled, a town on its ring where the cell is the best of it and a city on two rings where it is the best of those, each
        capped by the holder's stage; a second people's place, MINORITY_SHARE of its settled heads saturating toward MINORITY_MAX,
        + its halls toward HOLD_MAX. The settled are the farmers, FISHER_SHARE of the others on a harbour or navigable river, and
        a mining people's halls (HOLD_SHARE of its heads, once it knows 'mines'). A site is founded where the target holds FOUND
        for FOUND_STEPS (a second people's place only once that people has been the cell's second for MINORITY_STEPS), grows toward
        its target with TAU_KYR, changes hands with the cell's lead (a chief place), and is left when its target stays under
        ABANDON for ABANDON_STEPS (MINORITY_ABANDON_STEPS), under the sea or ice, or (a second people's place) merged once its own
        people has led the cell for HAND_KYR. Before, the history sized places on its own densities and lead peoples and counted
        every cell whose place was of town size that step: mid-history a third more town cells than the ledger at L7 and other
        peoples' towns (lane 254b, round19.md). Not kept: war's sacks and razings, the ledger's seeded river shifts, and its
        blending of the frames on either side of a step.

        PW-1612: the ledger reads each step from the stored frame at or before it, held until the next (frames every 0.5 kyr); so
        do these: `fresh` (end_step: a step that stores a frame) takes the inputs from the history now, any other step keeps the
        last ones taken. PW-1612 B: end_step counts after the peoples move, so a frame's step takes the state that frame stores
        (before, the start of its step: the state one century older).
        {people: cells}."""
        from ..settlements import CONST as C
        from .. import landuse as LU
        L, h, g = self.h.lines, self.h, self.g
        n, nl = g.n, len(self.h.lines)
        st = getattr(self, "_towns_st", None)
        if st is not None and st["ago"] == ago:
            return st["out"]
        if st is None:
            st = self._towns_st = {"ago": None, "out": {}, "act": np.zeros((2, n), bool), "pop": np.zeros((2, n)),
                                   "streak": np.zeros((2, n), np.int64), "low": np.zeros((2, n), np.int64),
                                   "holder": np.full((2, n), -1, np.int64), "cand": np.full(n, -1, np.int64),
                                   "cand_run": np.zeros(n, np.int64), "lead": None, "lead_since": np.full(n, np.inf)}
        dt = C["STEP_KYR"] if st["ago"] is None else max(st["ago"] - ago, 0.0)
        relax = 1 - np.exp(-dt / C["TAU_KYR"])
        if fresh or "inp" not in st:
            env = h._env_now
            # the ledger's inputs now, as a frame stores them (history.frame._frame)
            own = np.array([not l.overlay for l in L])[:, None] | h._linger
            P = np.where(own, h.p, 0)
            comp, land = h._composition(ago, env, h.rollup(P))
            land = np.asarray(land, bool)
            fi = LU.frame_inputs(h, P, land)
            coastal = land & (nbr_reduce(g, np.maximum, (~land)[self.idx].astype(np.int8)) > 0)
            st["inp"] = {"land": land, "comp": comp, "coastal": coastal,
                         "dens": (2.0 ** (fi["dens"].astype(float) * LU.PEOPLE_SCALE) - 1) * self.cell_km2,  # (people per cell)
                         "farm": fi["farm"].astype(float) / 100,
                         "ice": (np.asarray(env["ice"], float) > 0.5) if "ice" in env else np.zeros(n, bool)}
        inp = st["inp"]
        land, comp, coastal, dens, farm, ice = (inp[k] for k in ("land", "comp", "coastal", "dens", "farm", "ice"))
        lead, second = (np.where(comp[x] < 255, comp[x].astype(np.int64), -1) for x in ("mix_lead", "mix_second"))
        lead_sh, second_sh = comp["mix_lead_share"].astype(float), comp["mix_second_share"].astype(float)
        q = self.SE._site_factor(self.W, coastal, C)
        water = ((np.asarray(self.W["harbour"]) > 0) & coastal) | (np.asarray(self.W["river_nav"]) > 0)
        al_x, stage_x = np.zeros(nl + 1, np.int64), np.zeros(nl + 1, np.int64)  # (by line; the last row, index -1, is none)
        hold_x = np.zeros(nl + 1, bool)  # (a mining people that knows 'mines': its halls)
        for k in np.unique(np.concatenate([lead, second, st["holder"].ravel()])).tolist():
            if k >= 0:
                al_x[k], stage_x[k] = self._allowed(k, ago)
                hold_x[k] = self._miner(k) and self.knows(L[k].id, "mines", ago)
        people = [l.group_of or l.id for l in L]
        same = np.zeros((nl + 1, nl + 1), bool)
        for a in range(nl):
            same[a, :nl] = [people[a] == p for p in people]
        TM, SH, CITY_CAP = np.asarray(C["TOWN_MIN"], float), C["SHARE"], np.asarray(C["CITY_CAP"], float)

        def caps(stage):  # (settlements' caps_of: the largest a village, town, city can be, by stage)
            return (TM[stage] - 1, np.where(stage >= 3, C["CITY_MIN"] - 1, C["TOWN_CAP"]), CITY_CAP[stage])
        # the chief place's target: the largest tier the lead may build and the cell may hold
        fish = farm + C["FISHER_SHARE"] * (1 - farm) * water
        sed = np.where(land, dens * (fish + C["HOLD_SHARE"] * hold_x[lead] * lead_sh / 100), 0.0)
        al0, stage0 = al_x[lead], stage_x[lead]
        cap0 = caps(stage0)
        tie = 1.0 + 1e-9 * (n - np.arange(n)) / n  # (equal hinterlands: the lower cell id is the best of its ring)
        H1, H2 = self._hin(sed, self.r_town), self._hin(sed, self.r_city)
        s1, s2 = H1 * q * tie, H2 * q * tie
        best1, best2 = s1 >= self._ringmax(s1, self.r_town), s2 >= self._ringmax(s2, self.r_city)
        tgt0 = np.zeros(n)
        for t, hin, best in ((1, sed, True), (2, H1, best1), (3, H2, best2)):
            tgt0 = np.maximum(tgt0, np.minimum(np.where(best & (al0 >= t), SH[t] * hin * q, 0.0), cap0[t - 1]))
        tgt0 = np.where(land & (lead >= 0), tgt0, 0.0)
        # the second people's own place: the cell's second people (SECOND_MIN of its people or more, not the lead's own people);
        # once founded, the line that founded it
        cand = np.where((second >= 0) & (second_sh >= 100 * C["SECOND_MIN"]) & ~same[lead, second], second, -1)
        line1 = np.where(st["act"][1], st["holder"][1], cand)
        sh1 = np.where(line1 < 0, 0.0, np.where(lead == line1, lead_sh, np.where(second == line1, second_sh, 0.0))) / 100
        heads1 = dens * sh1
        own1 = C["MINORITY_SHARE"] * heads1 * fish
        own1 = own1 * C["MINORITY_MAX"] / (own1 + C["MINORITY_MAX"])
        hold1 = hold_x[line1] & (line1 >= 0)
        hall1 = C["HOLD_SHARE"] * heads1 * hold1 * q
        hall1 = hall1 / np.sqrt(1 + (hall1 / C["HOLD_MAX"]) ** 2)
        al1, stage1 = al_x[line1], stage_x[line1]
        cap1 = caps(stage1)
        ti1 = np.where(hold1, al1, np.minimum(al1, 2))  # (a hold may grow into a city of its own)
        tgt1 = np.where(land & (al1 >= 1), np.minimum(own1 * q + hall1, np.select([ti1 == 1, ti1 == 2, ti1 >= 3], list(cap1), 0.0)), 0.0)
        st["cand_run"] = np.where(cand >= 0, np.where(cand == st["cand"], st["cand_run"] + 1, 1), 0)
        st["cand"] = cand
        if st["lead"] is not None:
            st["lead_since"] = np.where(lead != st["lead"], ago, st["lead_since"])
        st["lead"] = lead
        # the sites: founded, grown, handed on and left as the ledger's
        act, pop, streak, low, holder = st["act"], st["pop"], st["streak"], st["low"], st["holder"]
        for s, tgt, hl, ready, quit_ in ((0, tgt0, lead, True, C["ABANDON_STEPS"]),
                                          (1, tgt1, line1, st["cand_run"] >= C["MINORITY_STEPS"], C["MINORITY_ABANDON_STEPS"])):
            grow = act[s].copy()
            streak[s] = np.where(~act[s] & (tgt >= C["FOUND"]) & ready, streak[s] + 1, 0)
            new = ~act[s] & (streak[s] >= C["FOUND_STEPS"]) & (hl >= 0)
            act[s] |= new
            pop[s] = np.where(new, np.maximum(C["FOUND"], np.minimum(tgt, 2 * C["FOUND"])), pop[s])
            holder[s] = np.where(new, hl, holder[s])
            streak[s][new] = 0
            pop[s] = np.where(grow, pop[s] + (tgt - pop[s]) * relax, pop[s])
            if s == 0:
                holder[s] = np.where(grow & (hl >= 0), hl, holder[s])
            low[s] = np.where(grow, np.where(tgt < C["ABANDON"], low[s] + 1, 0), low[s])
            gone = grow & (~land | ice | (low[s] >= quit_))
            if s == 1:  # (merged into the chief place once its own people has led the cell for HAND_KYR)
                gone |= grow & (holder[s] >= 0) & same[lead, holder[s]] & (st["lead_since"] - ago >= C["HAND_KYR"] - 1e-9)
            act[s] &= ~gone
            low[s][gone] = 0
            if s == 1:
                holder[s][gone] = -1
        town = act & (pop >= TM[np.stack([stage0, stage1])])  # (the size class in force: each slot's people's stage now, PW-1114)
        names = sorted(set(people))
        pid = np.array([names.index(p) for p in people] + [-1])  # (by line -> its people; a group's places are its people's)
        hp = pid[holder]
        out: dict = {}
        for i in np.unique(hp[town]).tolist():
            if i >= 0:
                out[names[i]] = int((((hp[0] == i) & town[0]) | ((hp[1] == i) & town[1])).sum())
        st["ago"], st["out"] = ago, out
        return out

    def _miner(self, k: int) -> bool:
        """A mining people (settlements.MINERS: trait miner or subterranean, its own or its people's)."""
        l = self.h.lines[k]
        up = self.lines[self.lidx[l.group_of]]["traits"] if l.group_of in self.lidx else []
        return bool(self.SE.MINERS & (set(l.traits or []) | set(up)))

    def _step(self, step):
        h, g = self.h, self.g
        ago = self._ago = float(step.ago)
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
        q = self._site()  # (PW-1587: the ledger's site factor; without it the history had about as many cities as a ledger without it)
        size, city = self._places(sed, q)
        own, second = self._second_places(heads, lead, q)  # (PW-1583: a second people's own place, as the ledger's minority places)
        m = own > size  # (one seat per cell, as derive: the bigger place; its people holds the seat, and a second people's is a town at most)
        size, hold, city = np.where(m, own, size), np.where(m, second, lead), np.where(m, 0.0, city)
        city_min = float(CONST["CITY_MIN"])
        inc_cells = np.array([int(k[1:]) for k in self.prev_cap if k.startswith("c")], np.int64)
        thr = np.full(g.n, float(min(CONST["TOWN_MIN"])))
        thr[inc_cells] *= PO.HOLD
        cand = np.flatnonzero(peopled & land & (size >= thr))
        # (PW-1594: a state seat is tested on its place whichever its tier, as derive tests a site's people; the ledger caps a town
        # under a city's size, so a town (the best of its ring) passes only where the seat is hemmed in, a city (the best of two) anywhere)
        place_st = np.maximum(np.minimum(size, city_min - 1e-6), city)
        wcell = np.zeros(g.n, bool)  # (cells where a people that knows proto-writing or writing lives, and their neighbours: D49's lenience)
        for k in heads:
            if any(self.knows(L[k].id, t, ago) for t in PO.WRITING_TECHS):
                wcell |= h.p[k] >= EST
        wcell = wcell | (nbr_reduce(g, np.maximum, wcell[self.idx].astype(np.int8)) > 0)
        seats = []
        for c in cand.tolist():
            k = int(hold[c])
            ppl = L[k].id
            key = f"c{c}"
            if not wcell[c] or not self.knows(ppl, "chiefdoms", ago):
                continue
            tmin = float(CONST["TOWN_MIN"][self._stage(ppl, ago)])  # (PW-1583: a town by its people's stage, as the ledger and town_cells)
            if size[c] < tmin * (PO.HOLD if key in self.prev_cap else 1.0) or not self.knows(ppl, "towns", ago):
                continue
            tier = "chiefdom"
            if (self.knows(ppl, "kingship", ago) or self.knows(ppl, "law", ago)) and self.knows(ppl, PO.STATE_WRITING, ago) \
                    and self.cool.get(key, -1) < k_ and self.knows(ppl, "cities", ago):  # (D49: a state needs its own people's writing)
                hem = self._hem_local(c, k, ppl, ago, land, ice, el)  # (PW-1594: the seat's own two rings, as derive)
                need = city_min * (1 - PO.HEMMED_X * hem) * (PO.HOLD if self.prev_cap.get(key) in ("state", "empire") else 1.0)
                if place_st[c] >= need:
                    tier = "state"
            strong = tier == "state" and self.knows(ppl, PO.STRONG_TECH, ago)
            self.founded.setdefault(key, ago)
            seats.append({"key": key, "cell": c, "people": ppl, "line": k, "uid": None, "pop": float(size[c]), "tier": tier,
                          "cls": 0 if strong else (2 if tier == "state" else 3), "rank": float(size[c]) * (PO.INCUMBENT if key in self.prev_cap else 1.0)})
        # 1b. confederations (polities' step 1b, Turchin 2009's mirror empires, PW-1583): the read-out's rule on the history's own places
        if PO.CONFED and self.owner is not None:
            place = np.where(peopled & land, np.maximum(CONST["SHARE"][1] * sed * q, size), 0.0)
            seats = self._confederations(seats, place, hold, ago, k_, peopled, edz, sea, ice, city_min)
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
        wide = ({r for pk, r in self.lord.items() if pk in self.prov_state} if "conquest" in PO.WIDE_BY else set()) | \
            ({s["key"] for s in seats if s.get("confed")} if "confederation" in PO.WIDE_BY else set())  # (who rules past STATE_MAX_KM, PW-1449)
        # 3. claims (polities' kernel)
        owner = np.full(g.n, -1, np.int64)
        from_rec = np.full(g.n, -1, np.int64)  # (a province's cells: the record id of the polity it was when taken; record only, PW-1575)
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
                    got = PO._claim(s["cell"], b, lx, sx, PO.CLIMB_M, self.off, self.idx, self.ekm, edz, sea, ice, peopled, owner, pid_of[root],
                                    self.dist, self.touched, self.claimed)
                    from_rec[self.claimed[:got]] = self.prov_rec.get(s["key"], -1)
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
        if REVOLT and self.owner is not None:
            self._risings(ruling, pid_of, ago)
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
            fates = self._fates(ruling[w], cells, heads, owner == w)
            if ruling[w]["line"] is not None:
                self.att.won(int(ruling[w]["line"]))
            ri = ctx.get("taken_row", {}).get(l_)
            km2 = float(len(cells) * self.cell_km2)
            lrec = self.recs[self.open_.pop(lk)] if lk in self.open_ else None
            wrec = self.recs[self.open_[wk]] if wk in self.open_ else None
            lid, wid = (lrec["id"] if lrec is not None else -1), (wrec["id"] if wrec is not None else -1)
            if ri is not None:  # (the two sides by people, then by record id: the read-out's row log, PW-1575)
                self.inv_log[ri]["took"].append([ago, ruling[l_]["people"], ruling[w]["people"], km2, lid, wid])
            if lrec is not None:
                lrec["fell_kyr"], lrec["fell_how"] = ago, ("invaded by " if how == "invasion" else "conquered by ") + ruling[w]["people"]
                lrec["fell_by"] = wid
            if wrec is not None:  # ([kyr ago, loser people, cells, how, the fates of the peoples there, loser record id, the cells
                # taken: the settlement ledger's war reads each place's fate from them, PW-1599])
                wrec["took"].append([round(ago, 3), ruling[l_]["people"], int(len(cells)), how, fates, lid, cells.tolist()])
            from_rec[(before == l_) & (from_rec < 0)] = lid
            self.prov_rec[lk] = lid
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
            if s.get("confed") and tier in ("state", "empire"):  # (1b, as derive: [kyr ago, its people's heads in its places within reach])
                rec.setdefault("confed", []).append([round(ago, 3), s["heads"]])
            a = len(cells) * self.cell_km2 / 1e6
            if a > rec["peak_mkm2"]:
                rec["peak_mkm2"], rec["peak_kyr"] = round(a, 4), round(ago, 3)
            fr = from_rec[cells]  # (as derive's maps: [record, tier, cells, the people holding its seat, its provinces by the record taken from])
            step_map.append([o, PO.TIERS.index(tier), PO._pack(cells), s["people"], {int(r): PO._pack(cells[fr == r]) for r in np.unique(fr[fr >= 0])}])
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

    def _confederations(self, seats, place, lead, ago, k_, peopled, edz, sea, ice, city_min) -> list:
        """Step 1b (polities._confederations' rule, PW-1583): a people with a state's institutions (chiefdoms, kingship or law, and its
        own real writing, D49) but no city big enough seats a state at one of its places when its own people in its places within a
        state's reach of it number a city's worth (city_min x CONFED_HEADS_X) and a foreign state, empire or dragon realm
        (CONFED_AGAINST) held land within that reach last step; its own city-state within reach rules there instead. The places are
        the history's: each cell's central place (a village: SHARE[1] of its own sedentary heads; a town or city where _places
        seats one), held by the cell's lead people. Returns the seats with each confederation in place of any seat on its cell."""
        g, L = self.g, self.h.lines
        by_pid = np.full(len(self.ruling) + 1, -1, np.int64)  # (cells a state, empire or dragon realm held last step: its seat's people, as a line index)
        for p, s in enumerate(self.ruling):
            if s is not None and p < len(self.tier_of) and self.tier_of[p] in PO.CONFED_AGAINST:
                by_pid[p] = self.lidx.get(s["people"], -2)
        foreign = by_pid[self.owner]  # (owner -1: the last entry, -1)
        if not (foreign >= 0).any():
            return seats
        state_at = {s["cell"]: s for s in seats if s["tier"] == "state"}
        scratch = np.full(g.n, -1, np.int64)
        out = list(seats)
        has = (lead >= 0) & (place > 0)
        for k in sorted(set(lead[has].tolist()), key=lambda k: L[k].id):
            ppl = L[k].id
            if not (self.knows(ppl, "chiefdoms", ago) and (self.knows(ppl, "kingship", ago) or self.knows(ppl, "law", ago))
                    and self.knows(ppl, PO.STATE_WRITING, ago)):
                continue
            mine = sorted(np.flatnonzero(has & (lead == k)).tolist(), key=lambda c: (f"c{c}" not in self.prev_cap, -place[c], c))
            covered: set = set()
            tries = 0
            for c in mine:
                key = f"c{c}"
                if tries >= PO.CONFED_TRY:
                    break
                if c in covered or c in state_at or self.cool.get(key, -1) >= k_:
                    continue
                tries += 1
                b, lx, sx = PO._reach(self, {"people": ppl, "tier": "state"}, ago, "confederation" in PO.WIDE_BY)
                got = PO._claim(c, b, lx, sx, PO.CLIMB_M, self.off, self.idx, self.ekm, edz, sea, ice, peopled, scratch, 0, self.dist,
                                self.touched, self.claimed)
                cells = self.claimed[:got].copy()
                scratch[cells] = -1
                covered.update(cells.tolist())
                if any(int(x) in state_at and state_at[int(x)]["people"] == ppl for x in cells):
                    continue
                heads = float(place[cells][lead[cells] == k].sum())
                if heads < city_min * PO.CONFED_HEADS_X * (PO.HOLD if self.prev_cap.get(key) in ("state", "empire") else 1.0):
                    continue
                fr = foreign[cells]
                if not np.any((fr >= 0) & (fr != k)):
                    continue
                self.founded.setdefault(key, ago)
                out = [s for s in out if s["cell"] != c]
                out.append({"key": key, "cell": c, "people": ppl, "line": k, "uid": None, "pop": float(place[c]), "tier": "state",
                            "cls": 0 if self.knows(ppl, PO.STRONG_TECH, ago) else 2,
                            "rank": float(place[c]) * (PO.INCUMBENT if key in self.prev_cap else 1.0), "confed": True, "heads": round(heads)})
        return out

    def _close(self, key, ago, how):
        o = self.open_.pop(key, None)
        if o is not None:
            self.recs[o]["fell_kyr"], self.recs[o]["fell_how"] = round(ago, 3), how

    def _fates(self, win, cells, heads, ruled=None) -> dict:
        """The peoples on the land war took fare by the winner's attitudes (PW-1481, PW-1487): its harshness to each (harshness: its
        people's old enmity to theirs, moved by its tolerance and by its aggression gated by its intolerance) reads kept, thinned or
        expelled (FATE_AT); the cut (FATE_CUT) scales with its aggression / AGG_MID. A tolerant winner keeps even an old enemy's people more often; an intolerant one thins or expels even a
        people it had no quarrel with; an aggressive one cuts harder. Cuts their presence there once, never more than FATE_MAX of a
        people's heads lost in one step. Where the cut goes (PW-1496, Daniel D61 C): a thinning is lost (war deaths); an expulsion by
        a winner at or above the martial mark (aggression AGG_MID, a martial people's own: attitudes AGG_BASE + AGG_CONTEST x 0.5) is
        lost too ("razed": Genghis Khan's sacks); below it the expelled share moves to the same people's nearest land the winner does
        not rule (ruled: the winner's cells after the step's wars, else the taken cells alone; _refuge), spread over its cells there
        by its existing density (the Assyrian deportations' refugees), and is lost only if it has none ("expelled", heads lost).
        Submit or resist (D61, Daniel 11-07: Genghis Khan's "submit and you are spared, resist and you are destroyed"): a people the
        winner would thin, expel or raze submits, and is kept ("submitted"), if its own aggression is below the winner's (the less
        warlike yields to the more); one at least as warlike resists and meets that fate. No new number: the two peoples' own
        attitudes (attitudes.Attitudes) decide (round12.md).
        Returns {people: [fate, heads lost, heads moved]}, fate kept, submitted, thinned, expelled or razed."""
        h = self.h
        wk = win["line"]
        if wk is None or not len(cells):
            return {}
        out = {}
        wanc = self.anc.get(win["people"], {win["people"]})
        tol, agg = self.att.get(int(wk))
        if ruled is None:
            ruled = np.zeros(self.g.n, bool)
            ruled[cells] = True
        for k, hk in heads.items():
            on = hk[cells]
            n = float(on.sum())
            if n <= 0:
                continue
            lid = h.lines[k].id
            if lid in wanc or win["people"] in self.anc.get(lid, ()):  # (the winner's own people and kin)
                continue
            z = harshness(float(self.hostility[wk, k]), tol, agg)
            fate = "kept" if z < FATE_AT[0] else ("thinned" if z < FATE_AT[1] else "expelled")
            rose = self.revolted.pop((lid, win["people"]), None) if REVOLT else None  # (REVOLT: it broke its terms to this ruler)
            if fate != "kept" and rose is None and self.att.get(int(k))[1] < agg:  # (submits: less warlike than the winner, it yields and is kept)
                out[lid] = ["submitted", 0, 0]
                if REVOLT:
                    self.submitted.setdefault(lid, set()).add(win["people"])
                    self.submissions.append([round(self._ago, 3), lid, win["people"]])
                continue
            if fate == "expelled" and agg >= AGG_MID:
                fate = "razed"
            cut = min(1.0, FATE_CUT["expelled" if fate == "razed" else fate] * agg / AGG_MID)
            gone = moved = 0.0
            if cut > 0:
                tot = float(hk.sum())
                done = self.__dict__.setdefault("_cut_now", {})
                spent = done.get((k, self.k), 0.0)
                cut = min(cut, max(0.0, (FATE_MAX * tot - spent) / n))
                if cut > 0:
                    gone = cut * n
                    pb = h.p[k][cells].copy()
                    h.p[k][cells] *= (1.0 - cut)
                    h.p[k][cells[h.p[k][cells] < EST]] = 0.0
                    hk = heads[k] = hk.copy()
                    hk[cells] = np.where(h.p[k][cells] > 0, hk[cells] * (1.0 - cut), 0.0)  # (no heads left where its presence fell under EST: a later fate this step must not move refugees onto a cell it has left, PW-1583)
                    if fate == "expelled":  # (the heads that left the taken cells, those whose presence fell under EST too)
                        gone = float((on * (1.0 - np.divide(h.p[k][cells], pb, out=np.ones_like(pb), where=pb > 0))).sum())
                        moved = self._refuge(k, hk, cells, ruled, gone)
                    done[(k, self.k)] = spent + (cut * n if fate != "expelled" else gone - moved)
            out[lid] = [fate, int(round(gone - moved)), int(round(moved))]
            if rose is not None:
                self.punished.append([round(self._ago, 3), lid, win["people"], *out[lid]])
        return out

    def _risings(self, ruling, pid_of, ago):
        """REVOLT (PW-1513, D67 B): a people that submitted to a ruling people and now seats a polity of its own on a cell that ruler's
        polity held last step, while that polity still stands this step, has risen against it: (people, ruler) is marked until the
        ruler next takes land the people lives on (_fates: no second submission)."""
        for s in ruling:
            rulers = self.submitted.get(s["people"])
            if not rulers or s["tier"] == "dragon realm":
                continue
            o = int(self.owner[s["cell"]])
            prev = self.ruling[o] if 0 <= o < len(self.ruling) else None
            if prev is None or prev["people"] not in rulers or prev["people"] == s["people"] or prev["key"] not in pid_of:
                continue
            if (s["people"], prev["people"]) not in self.revolted:
                self.revolted[(s["people"], prev["people"])] = round(ago, 3)
                self.revolts.append([round(ago, 3), s["people"], prev["people"], int(s["cell"])])
            rulers.discard(prev["people"])

    def _refuge(self, k, hk, cells, ruled, n) -> float:
        """PW-1496 (D61 C): n expelled heads of people k go to its nearest land the winner does not rule: the cells it holds off the
        taken land and off the winner's (hk > 0), the connected patch (or patches, at the same distance) first reached ring by ring
        from the taken cells, spread there by its existing density (its presence there scaled up alike, never past full presence, 1).
        Updates h.p[k] and hk in place; returns the heads moved (0 if it has no such land: they are lost)."""
        h = self.h
        cand = (hk > 0) & (h.p[k] > 0) & ~ruled
        cand[cells] = False
        if not cand.any():
            return 0.0
        seen = np.zeros(self.g.n, bool)
        seen[cells] = True
        front = np.asarray(cells, np.int64)
        hit = front[:0]
        while len(front):
            nb = np.unique(self.idx[_csr_gather(self.off, front)])
            nb = nb[~seen[nb]]
            seen[nb] = True
            hit = nb[cand[nb]]
            if len(hit):
                break
            front = nb
        if not len(hit):
            return 0.0
        patch = np.zeros(self.g.n, bool)
        patch[hit] = True
        front = hit
        while len(front):  # (the connected patch of its land the first ring reached)
            nb = np.unique(self.idx[_csr_gather(self.off, front)])
            nb = nb[cand[nb] & ~patch[nb]]
            patch[nb] = True
            front = nb
        at = np.flatnonzero(patch)
        have = float(hk[at].sum())
        p0 = h.p[k][at].copy()
        h.p[k][at] = np.minimum(1.0, p0 * (1.0 + n / have))
        add = hk[at] * (h.p[k][at] / p0 - 1.0)
        hk[at] += add
        return float(add.sum())

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
        return {"format": FORMAT, "first_cut": True, "calendar": "the tech tree inside the history (PW-1466)",
                "made_s": round(self.secs, 1), "tech_s": round(self.tech.secs, 1), "steps": self.steps, "polities": self.recs, "maps": self.maps,
                "attitudes": self.att.doc() | {"keyed_by": "people (line index; the history has no cultures)"},
                "invasions": [{"row": r, "log": {k: v for k, v in lg.items()}} for r, lg in zip(self.inv_in, self.inv_log)],
                "invasion_problems": self.inv_notes,
                **({"revolt": {"rule": "PW-1513 D67 B", "revolts": self.revolts, "punished": self.punished,
                               "submissions": self.submissions}} if REVOLT else {}),
                "constants": {"FATE_AT": FATE_AT, "FATE_CUT": FATE_CUT, "FATE_MAX": FATE_MAX, "PACIFY": PACIFY, "STATE_BAR": STATE_BAR, "AGG_MID": AGG_MID, "TOL_X": TOL_X, "AGG_HARSH": AGG_HARSH,
                              "CAMPAIGN_KM": IV.CAMPAIGN_KM, "NEED_X": NEED_X,
}}
