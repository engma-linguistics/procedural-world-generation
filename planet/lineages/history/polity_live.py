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
- towns: the settlement ledger is made after the run, so the history keeps the ledger's rule on its own inputs (town_cells, PW-1608:
  the chief place and a second people's own place per cell, with the ledger's site factor, settlements._site_factor, PW-1587, its
  halls and fishers); the seats (PW-1596, round24.md) and the confederations (PW-1671, round26.md) read those places as at the end
  of the last step. A seat is a state where its place, of either tier,
  reaches a city's size less HEMMED_X x how hemmed in the seat is over its own two rings (polities._hemmed's reading), as derive tests
  a site's people; the ledger caps a town under a city's size, so a town passes only where it is hemmed in (PW-1594);
- the tech calendar: the tech tree runs inside the history (history.tech_live, PW-1466, round8.md): each step it runs down to the
  history's time first, and the gates (chiefdoms, proto-writing or writing, kingship, law, the military edges, boats, a dragon's hoards)
  read what each people knew by then. output.save writes the same calendar out as meta.techtree;
- cultures: a polity is a people's; an empire is a state whose subject peoples hold SUBJECT_SHARE of its sedentary heads. A dragon
  people seats one realm per culture (the read-out's one per dragon culture; PW-1687, coordinator ruling B; round27.md), its
  cultures cut inside the history by the demes' and the cultures engine's own rules for a dragon kind (DragonCultures: regions
  within a dragon's reach, megafauna.LINK_KM; demes.MIN_KM2, demes.PERSIST, cultures.t_apart, merging side by side);
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


def is_dragon(l) -> bool:
    """A dragon people, as the read-out's _Run.dragons: 'dragon' in its id and the trait 'flies' (lane 281b: was l.trait("flies", 0.0),
    a knob lookup no trait has, so the history seated no dragon realm at all)."""
    return "dragon" in l.id and "flies" in (l.traits or [])


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


def dragon_regions(g, held: np.ndarray, r_link: int, min_cells: int, lab_out: np.ndarray | None = None) -> tuple[np.ndarray, int]:
    """A dragon people's range cut into regions as the demes cut a dragon kind (demes.Demes._cut with mobility's terrain-free reach):
    held cells within 2 x r_link rings of each other (megafauna.LINK_KM: a gap a dragon flies across) are one region; a region of
    fewer than min_cells held cells (demes.MIN_KM2) goes with the nearest bigger one (straight through the grid, as demes' small
    pieces go to the nearest deme); if none is that big, the biggest stands alone. Returns (region per cell, -1 off the range; count),
    regions numbered by size, biggest first (ties: lowest cell)."""
    from ..spread import nearest_label
    n = g.n
    lab = np.full(n, -1, np.int64) if lab_out is None else lab_out
    lab[:] = -1
    if not held.any():
        return lab, 0
    d = held.copy()
    for _ in range(r_link):
        d = d | (nbr_reduce(g, np.maximum, d[np.asarray(g.nbr_idx, np.int64)].astype(np.int8)) > 0)
    comp, _nc = g.components(d)
    hc = comp[held]
    ids, cnt = np.unique(hc, return_counts=True)
    cells = np.flatnonzero(held)
    first = np.full(len(ids), n, np.int64)
    np.minimum.at(first, np.searchsorted(ids, comp[cells]), cells)
    order = np.lexsort((first, -cnt))
    big = [i for i in order if cnt[i] >= min_cells] or [order[0]]
    rank = np.full(int(comp.max()) + 1, -1, np.int64)
    rank[ids[big]] = np.arange(len(big))
    lab[held] = rank[hc]
    if (lab[held] < 0).any():
        seed = np.where(lab >= 0, lab, -1)
        near = nearest_label(seed, np.ones(n, np.bool_), np.asarray(g.nbr_off, np.int64), np.asarray(g.nbr_idx, np.int64))
        lab[held] = near[held]
    return lab, len(big)


class DragonCultures:
    """Each dragon people's cultures followed through the history (PW-1687, coordinator ruling B, round27.md), cut as the demes and
    the cultures engine cut a dragon kind (demes.py, cultures.py), cheaply:
    - regions: dragon_regions each step (pieces within a dragon's reach, megafauna.LINK_KM, are one population; a piece under
      demes.MIN_KM2 goes with the nearest region);
    - each held cell carries a culture label, kept while held; a newly held cell takes the nearest label of its own region (a front
      carries its parent's name). A dragon people's first range is its founding culture, whatever pieces it is in (the cultures
      engine's one founding culture for all the first demes of a people);
    - a region holding none of the people's labels (a crossing), or a part of a label's land in another region of at least MIN_KM2
      (a split by a gap: the label keeps its largest part), is a piece of its parent culture; it is a culture of its own once it has
      stayed apart demes.PERSIST stored frames and cultures.t_apart (its era's time apart), and goes back to its parent if it shares
      a region with the parent's own cells first (flicker leaves no trace);
    - two cultures of a people on neighbouring cells merge, the younger into the older, after cultures.MERGE_CONTACT_KYR x (1 -
      cohesion) side by side (a dragon kind's 0.9: within a century);
    - followed from demes.WINDOW_KYR ago, as the demes are cut (the glacial pass's steps too).
    No new number. Not mirrored: the demes' split by distance (a deme wider than SPLIT_KM x LINK_KM / JUMP_KM halves; the halves
    touch, so the cultures engine merges them back within a century) and niche learning (split_adapted)."""

    def __init__(self, g, coh: dict | None = None):
        from ..seafood import cells_for
        from .. import demes as DE
        from .. import cultures as CU
        from .megafauna import LINK_KM
        self.g, self.DE, self.CU = g, DE, CU
        self.r_link = rings_for(g, LINK_KM / 2)
        self.min_cells = cells_for(g, DE.MIN_KM2)
        self.src, self.dst = np.asarray(g.nbr_src, np.int64), np.asarray(g.nbr_idx, np.int64)
        self.off = np.asarray(g.nbr_off, np.int64)
        self.coh = coh or {}
        self.lab: dict[int, np.ndarray] = {}  # line -> label per cell (-1 off its range)
        self.info: dict[int, list] = {}  # line -> per label: [key (None: a piece not yet apart), born kyr ago, parent, frames, into]
        self.n_cul: dict[int, int] = {}  # line -> cultures made so far (the keys' numbers)
        self.touch: dict[int, dict] = {}  # line -> {(a, b): kyr side by side}

    @staticmethod
    def _into(inf, a: int) -> int:
        while inf[a][4] is not None:
            a = inf[a][4]
        return a

    def _res(self, inf, a: int) -> int:
        """A label's culture: itself if a culture, else its parent's (a piece not yet apart is its parent's), through merges."""
        a = self._into(inf, a)
        while inf[a][0] is None and inf[a][2] is not None:
            a = self._into(inf, inf[a][2])
        return a

    def _new(self, k, people, inf, ago, parent):
        if parent is None:
            inf.append([f"d{people}" if not inf else f"d{people}.{self.n_cul.get(k, 0)}", ago, None, 0, None])
            self.n_cul[k] = self.n_cul.get(k, 0) + 1
        else:
            inf.append([None, ago, parent, 0, None])
        return len(inf) - 1

    def step(self, k: int, people: str, held: np.ndarray, ago: float, dt: float, stored: bool, apart: float) -> list[tuple]:
        """(key, cells) of each culture of people (line k) alive this step, oldest first."""
        from ..spread import nearest_label
        n = self.g.n
        inf = self.info.setdefault(k, [])
        lab = self.lab.get(k)
        lab = np.full(n, -1, np.int64) if lab is None else np.where(held, lab, -1)
        if not held.any():
            self.lab[k], self.touch[k] = lab, {}
            return []
        reg, nr = dragon_regions(self.g, held, self.r_link, self.min_cells)
        if not (lab >= 0).any():  # (the first range, or a kind back from dying out: one culture, whatever its pieces, as the
            f = self._new(k, people, inf, ago, None)  # cultures engine's one founding culture of a people's first demes)
            for r in range(nr):
                lab[reg == r] = f if r == 0 else self._new(k, people, inf, ago, f)
                if r:
                    inf[-1][3] = -1  # (a first deme: its founding culture's for good, unless it falls apart again)
        # newly held cells: the nearest label of their own region; a region with none is a crossing, a piece of the nearest culture
        if (held & (lab < 0)).any():
            for r in range(nr):
                m = reg == r
                if not (lab[m] < 0).any():
                    continue
                if (lab[m] >= 0).any():
                    lab[m] = nearest_label(np.where(m, lab, -1), m | ~held, self.off, self.dst)[m]
                    continue
                anc = nearest_label(np.where(held & ~m, lab, -1), np.ones(n, np.bool_), self.off, self.dst)
                lab[m] = self._new(k, people, inf, ago, self._res(inf, int(anc[np.flatnonzero(m)[0]])))
        # splits by a gap: a label's land in two regions or more keeps its largest part; each other part of MIN_KM2 is a new piece
        cells = np.flatnonzero(held)
        u, c = np.unique(lab[cells] * (nr + 1) + reg[cells], return_counts=True)
        ul, ur = u // (nr + 1), u % (nr + 1)
        lu, lc = np.unique(ul, return_counts=True)
        for a in lu[lc > 1].tolist():
            parts = sorted(zip(c[ul == a].tolist(), ur[ul == a].tolist()), key=lambda t: (-t[0], t[1]))
            for sz, r in parts[1:]:
                if sz >= self.min_cells:
                    lab[(reg == r) & (lab == a)] = self._new(k, people, inf, ago, self._res(inf, a))
        # pieces: back to their culture if they share a region with its own land; a culture of their own once apart long enough. The
        # labels stay on the cells as the demes' ids do (a label falling apart is a split); a culture's own land is its labels', those
        # merged into it and its first demes', not its pieces'
        here = np.unique(lab[held]).tolist()
        own = np.full(len(inf), -1, np.int64)
        for b in here:
            b2 = self._into(inf, b)
            own[b] = self._res(inf, b2) if (inf[b2][0] is not None or inf[b2][3] < 0) else -1
        ol = np.where(lab >= 0, own[np.maximum(lab, 0)], -1)
        for a in here:
            x = inf[a]
            if x[0] is not None or x[4] is not None:
                continue
            p = self._res(inf, a)
            if np.isin(np.unique(reg[lab == a]), np.unique(reg[held & (ol == p) & (lab != a)])).any():
                x[4] = p
                continue
            if x[3] < 0:
                continue
            x[3] += 1 if stored else 0
            if x[3] >= self.DE.PERSIST and x[1] - ago >= apart - 1e-9:
                x[0] = f"d{people}.{self.n_cul[k]}"
                self.n_cul[k] += 1
        # merges: two cultures on neighbouring cells, side by side MERGE_CONTACT_KYR x (1 - cohesion): the younger into the older
        res = np.full(len(inf), -1, np.int64)
        for a in np.unique(lab[held]).tolist():
            res[a] = self._res(inf, a)
        cl = np.where(lab >= 0, res[np.maximum(lab, 0)], -1)
        cs, cd = cl[self.src], cl[self.dst]
        e = (cs >= 0) & (cd >= 0) & (cs < cd)
        old, now, gone = self.touch.get(k, {}), {}, set()
        need = self.CU.MERGE_CONTACT_KYR * (1.0 - self.coh.get(people, 0.0))
        for a, b in sorted(set(zip(cs[e].tolist(), cd[e].tolist()))):
            now[(a, b)] = old[(a, b)] + dt if (a, b) in old else 0.0
            if now[(a, b)] >= need - 1e-9 and a not in gone and b not in gone:
                keep, lose = (a, b) if inf[a][1] >= inf[b][1] else (b, a)
                inf[lose][4] = keep
                cl[cl == lose] = keep
                gone |= {a, b}
                del now[(a, b)]
        self.touch[k], self.lab[k] = now, lab
        alive = np.unique(cl[held]).tolist()
        return [(inf[a][0], np.flatnonzero(cl == a)) for a in sorted(alive, key=lambda a: (-inf[a][1], a))]


class _Rings:
    """Each cell's cells within some rings, from ring_pairs' (cell, other) pairs sorted by cell (the cell itself included): rings[c]."""

    def __init__(self, a, b, off):
        self.b, self.off = b, off

    def __getitem__(self, c):
        return self.b[self.off[c]:self.off[c + 1]]


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
        self._ring_of = _Rings(self.r2a, self.r2b, self.r2off)  # (each cell's cells within HEMMED_KM, as polities._rings: a dragon realm's core)
        L = h.lines
        self.ppl = np.array([i for i, l in enumerate(L) if not (l.overlay or l.megafauna or l.marine)], np.int64)  # (peoples that may hold towns)
        self.dragons = [i for i, l in enumerate(L) if is_dragon(l)]
        try:  # (the kinds' cohesion as the cultures engine reads it from meta.tree, cultures.cohesion)
            from .. import cultures as CU, spec as SP
            coh = CU.cohesion(SP.to_raw(h.tree), getattr(h.tree, "name", None))
        except Exception:
            coh = {}
        self.dcul = DragonCultures(g, coh)  # (PW-1687: each dragon people's cultures, followed from demes.WINDOW_KYR ago)
        self._window = self.dcul.DE.WINDOW_KYR
        self.dregions: dict = {}  # (line -> this step's cultures, DragonCultures.step)
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
        if step.epoch == "recent":  # (the places are also the seats' places from the next step on, PW-1596: kept with or without the arms)
            towns = self.town_cells(float(step.ago), fresh=step.store)
            if getattr(self.tech, "towns", None) is not None:
                self.tech.note_towns(float(step.ago), towns)

    def begin_step(self, step):
        self.tech.step(step)  # (every step: the tree runs down to the history's time before anything reads it)
        if step.epoch != "deep" and float(step.ago) <= self._window + 1e-9:
            self._dragon_cultures(step)
        if step.epoch != "recent":
            return
        import time
        t0 = time.time()
        try:
            self._step(step)
            self._attitudes(step)
        finally:
            self.secs += time.time() - t0

    def _dragon_cultures(self, step):
        """PW-1687: each dragon people's cultures this step (DragonCultures), every glacial and recent step from demes.WINDOW_KYR ago,
        chiefdoms or not, so their time apart is counted as the demes count it."""
        import time
        t0 = time.time()
        h = self.h
        from .. import cultures as CU
        T_ = getattr(self.tech, "T", None)  # (the tree inside the history; a lent calendar has none: the stone age's time apart)
        for k in self.dragons:
            l = h.lines[k]
            held = h.p[k] >= EST if h.active.get(l.id) else np.zeros(self.g.n, bool)
            era = CU.eras({"techs": list(T_["techs"].values()), "known": {l.id: self.tech.known.get(l.id) or {}}}).get(l.id) if T_ else None
            self.dregions[k] = self.dcul.step(k, l.id, held, float(step.ago), float(step.dt), bool(step.store), CU.t_apart(era, float(step.ago)))
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
        hb = self.SE.coast_harbour(g, self.W["harbour"], ~land, coastal)  # (PW-1640: the harbour water beside the coast's land cells)
        q = self.SE._site_factor(self.W, coastal, C, hb)
        water = (hb > 0) | (np.asarray(self.W["river_nav"]) > 0)
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

    def _seat_places(self, ago: float, inc: np.ndarray) -> tuple:
        """(per cell: the biggest of its places in town_cells' ledger state, the chief place or a second people's own, of town size for
        its holder's stage (settlements' TOWN_MIN; x HOLD where last step's seat stood), 0 none; its holder line, -1 none): as
        polities.derive seats a ledger site (_site_tables' town_min by the site's bands)."""
        from ..settlements import CONST as C
        n = self.g.n
        best, who = np.zeros(n), np.full(n, -1, np.int64)
        st = getattr(self, "_towns_st", None)
        if st is None:
            return best, who
        TM = np.asarray(C["TOWN_MIN"], float)
        tm_of = {-1: np.inf}
        for s in (0, 1):
            act, pop, hl = st["act"][s], st["pop"][s], st["holder"][s]
            for k in np.unique(hl[act]).tolist():
                if k not in tm_of:
                    tm_of[k] = float(TM[self._allowed(k, ago)[1]])
            tm = np.array([tm_of.get(k, np.inf) for k in hl.tolist()])
            ok = act & (hl >= 0) & (pop >= tm * np.where(inc, PO.HOLD, 1.0)) & (pop > best)
            best[ok], who[ok] = pop[ok], hl[ok]
        return best, who

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
        city_min = float(CONST["CITY_MIN"])
        inc = np.zeros(g.n, bool)
        inc[np.array([int(k[1:]) for k in self.prev_cap if k.startswith("c")], np.int64)] = True
        # (PW-1596, lane 281, round24.md: a seat is the biggest of the cell's places as the settlement ledger keeps them (town_cells'
        # chief place and second people's own place: the ledger's rule on the history's inputs, as at the end of the last step), of
        # town size for its holder's stage, as derive seats a ledger site; a state tests that place against a city's size (PW-1594:
        # the ledger caps a town under a city, so a town passes only where the seat is hemmed in). Before, the history sized seats on
        # its own central places, without the ledger's mining halls (HOLD_SHARE of a mining people's heads: a hold may grow into a
        # city, PW-1117), and asked for the 'cities' tech by name where the ledger also counts a mining people's delving or
        # fortifications: on L7 899985 seed 7 the read-out on the switch-on history seated gnome holds as states 1,700 years before
        # the live polities did)
        seat_pop, seat_k = self._seat_places(ago, inc)
        cand = np.flatnonzero(peopled & land & (seat_k >= 0))
        wcell = np.zeros(g.n, bool)  # (cells where a people that knows proto-writing or writing lives, and their neighbours: D49's lenience)
        for k in heads:
            if any(self.knows(L[k].id, t, ago) for t in PO.WRITING_TECHS):
                wcell |= h.p[k] >= EST
        wcell = wcell | (nbr_reduce(g, np.maximum, wcell[self.idx].astype(np.int8)) > 0)
        seats = []
        for c in cand.tolist():
            k = int(seat_k[c])
            ppl = L[k].id
            key = f"c{c}"
            if not wcell[c] or not self.knows(ppl, "chiefdoms", ago):
                continue
            tier = "chiefdom"
            if (self.knows(ppl, "kingship", ago) or self.knows(ppl, "law", ago)) and self.knows(ppl, PO.STATE_WRITING, ago) \
                    and self.cool.get(key, -1) < k_:  # (D49: a state needs its own people's writing; the city is the ledger's, capped by stage)
                hem = self._hem_local(c, k, ppl, ago, land, ice, el)  # (PW-1594: the seat's own two rings, as derive)
                need = city_min * (1 - PO.HEMMED_X * hem) * (PO.HOLD if self.prev_cap.get(key) in ("state", "empire") else 1.0)
                if seat_pop[c] >= need:
                    tier = "state"
            strong = tier == "state" and self.knows(ppl, PO.STRONG_TECH, ago)
            self.founded.setdefault(key, ago)
            seats.append({"key": key, "cell": c, "people": ppl, "line": k, "uid": None, "pop": float(seat_pop[c]), "tier": tier,
                          "cls": 0 if strong else (2 if tier == "state" else 3), "rank": float(seat_pop[c]) * (PO.INCUMBENT if key in self.prev_cap else 1.0)})
        # 1b. confederations (polities' step 1b, Turchin 2009's mirror empires, PW-1583): the read-out's rule on the ledger's places
        # (PW-1671: town_cells' sites, as the seats; before, the history's own central places, without the ledger's halls, fishers or
        # a second people's place under the lead's: on L7 899985 seed 7 about half the read-out's confederations, round25.md)
        if PO.CONFED and self.owner is not None:
            seats = self._confederations(seats, *self._ledger_places(), ago, k_, peopled, edz, sea, ice, city_min)
        # 2. dragon realms: one per culture of a dragon people (PW-1687, coordinator ruling B, round27.md), as the read-out's one per
        # dragon culture, with the cultures cut inside the history as the demes and the cultures engine cut a dragon kind
        # (DragonCultures), each at its core by the read-out's rule (polities._core: the most of its cells within two rings), keyed
        # by its culture. Before: one per connected piece (290-310 realms on L6 4360a3 seed 7 against the read-out's 22-25, keys
        # moving every step), then one per people (4-6 against 16-26; round26.md)
        for k in self.dragons:
            l = L[k]
            if not h.active.get(l.id) or not self.knows(l.id, "hoards", ago):
                continue
            for key, cells in self.dregions.get(k) or []:
                if self.cool.get(key, -1) >= k_:
                    continue
                core = PO._core(cells, self._ring_of)
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

    def _ledger_places(self) -> tuple:
        """(per slot and cell, shape (2, n): the people in town_cells' living place there, the chief place (0) and a second people's
        own place (1), any size, 0 none; its holder line, -1 none): the ledger's places as at the end of the last step."""
        n = self.g.n
        st = getattr(self, "_towns_st", None)
        if st is None:
            return np.zeros((2, n)), np.full((2, n), -1, np.int64)
        act = st["act"] & (st["holder"] >= 0)
        return np.where(act, st["pop"], 0.0), np.where(act, st["holder"], -1)

    def _confederations(self, seats, pop, holder, ago, k_, peopled, edz, sea, ice, city_min) -> list:
        """Step 1b (polities._confederations' rule, PW-1583): a people with a state's institutions (chiefdoms, kingship or law, and its
        own real writing, D49) but no city big enough seats a state at one of its places when its own people in its places within a
        state's reach of it number a city's worth (city_min x CONFED_HEADS_X) and a foreign state, empire or dragon realm
        (CONFED_AGAINST) held land within that reach last step; its own city-state within reach rules there instead. The places are
        the ledger's (PW-1671): `pop` and `holder`, shape (2, n), town_cells' chief place and second people's own place per cell, any
        size (_ledger_places), each its holder line's; a line's heads on a cell are its places there summed, as the read-out sums a
        people's sites. Returns the seats with each confederation in place of any seat on its cell."""
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
        has = (holder >= 0) & (pop > 0)
        for k in sorted(set(holder[has].tolist()), key=lambda k: L[k].id):
            ppl = L[k].id
            if not (self.knows(ppl, "chiefdoms", ago) and (self.knows(ppl, "kingship", ago) or self.knows(ppl, "law", ago))
                    and self.knows(ppl, PO.STATE_WRITING, ago)):
                continue
            here = np.where(has & (holder == k), pop, 0.0)
            heads_at = here.sum(axis=0)  # (its places' people per cell, both slots)
            sl, cl = np.nonzero(here)  # (its places, each a candidate seat as the read-out's sites; last step's seats first: no flicker)
            mine = sorted(zip(cl.tolist(), sl.tolist()), key=lambda x: (f"c{x[0]}" not in self.prev_cap, -here[x[1], x[0]], x[0], x[1]))
            covered: set = set()
            tries = 0
            for c, sx_ in mine:
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
                heads = float(heads_at[cells].sum())
                if heads < city_min * PO.CONFED_HEADS_X * (PO.HOLD if self.prev_cap.get(key) in ("state", "empire") else 1.0):
                    continue
                fr = foreign[cells]
                if not np.any((fr >= 0) & (fr != k)):
                    continue
                self.founded.setdefault(key, ago)
                pc = float(here[sx_, c])
                out = [s for s in out if s["cell"] != c]
                out.append({"key": key, "cell": c, "people": ppl, "line": k, "uid": None, "pop": pc, "tier": "state",
                            "cls": 0 if self.knows(ppl, PO.STRONG_TECH, ago) else 2,
                            "rank": pc * (PO.INCUMBENT if key in self.prev_cap else 1.0), "confed": True, "heads": round(heads)})
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
