"""The seam polities swap in through (PW-1280; polities in the history, v4: PW-1434).

In plain words: the history has no states yet. Three stand-ins answer "who rules here, and who fights whom" for the brakes in
history.counter, and this module holds all three, behind one small object (`History.rule`):

- pacification G (`pacification`): how far a state keeps a people's own violence down. Today a formula of the era's tech level and the
  people's farm share (STATE_Q; Gómez et al. 2016: farming peoples with the tech form states). It feeds war-torn land.
- the hostile frontier F (`frontier`): how much of the country about each cell is held by peoples who hate this one. Today the old
  enmities of the tree (the cohabitation matrix, `hostility`). It feeds war-torn land, raid losses and the culling wars.
- in-fighting's circumscription C (`circumscription`, refreshed after each contest by `after_contest`): how far the land next to a
  people bars a faction from splitting off (Carneiro 2012; FEUD_CUT and SOCIAL_Q). It feeds the in-fighting brake.

The brakes' own formulas (LAND_Q, H_WAY, FEUD_CUT x C x fill, the raid and cull rules) stay in counter: they are what a state or a war
does to a people's numbers, whoever supplies G, F and C. Polities v1 (v4) swaps the stand-ins by setting `History.Rule` to a subclass
that answers the same four questions from real polities (G from the state that rules a cell, F from hostile polities' borders, C
from a polity's own civil wars), without touching counter or the rest of the history. Every method here returns what lane 97 and
lane 101 computed inline in counter.py; the move changed no number (lane 180: runs bit-identical on dnd and seven_meals seed 7).
"""

from __future__ import annotations

import numpy as np

from ..gridops import nbr_reduce
from ..spread import EST
from . import params as PM


class StandIns:
    """Today's stand-ins for states and war (no polities in the history yet). One per History, made at the run's start."""

    def __init__(self, h):
        self.h = h
        L = h.lines
        # hostility 0..1 of i towards j: how far the pair's cohabitation falls under the reference of two open peoples (COHAB_REF, 0.5),
        # in units of an 'apart' wish of weight 1 (compose.APART_FACTOR): an old enmity of weight w reads w, two insular peoples a little
        from ..compose import APART_FACTOR
        H = np.asarray(h.cohab, float)
        self.hostility = np.clip((PM.COHAB_REF - H) / (PM.COHAB_REF * APART_FACTOR), 0.0, 1.0)
        np.fill_diagonal(self.hostility, 0.0)
        for i, l in enumerate(L):  # (kin, megafauna, overlays and the sea peoples are nobody's raiding enemies)
            if l.overlay or l.megafauna or l.marine:
                self.hostility[i, :] = 0.0
                self.hostility[:, i] = 0.0
        self.hostility[h._kin] = 0.0
        self.hem = np.zeros(len(L))  # (each line's circumscription (lane 101) at its last step)
        self.K0 = {}  # (line index -> its unbraked habitat this step)
        self._Fc = None  # (the frontier cache: (presences it was made from, hostile presence lines x cells, {line: F}))

    def pacification(self, k, step) -> float:
        """G, 0..1: the share of line k's own violence a state leaves (1 stateless). Stand-in: 1 / (1 + STATE_Q x tech level x farm
        share), a farming people with the tech forms states (Gómez et al. 2016; Turchin 2009's -alpha S)."""
        from . import megafauna as MG
        lev = MG.tech_level(self.h.tree.era, step.ago)
        return 1.0 / (1.0 + PM.STATE_Q * lev * float(self.h._farm_share[k]))

    def frontier(self, k) -> np.ndarray:
        """F per cell, 0..1: the hostile presence about each cell (the cell and its neighbours), weighted by line k's hostility to each
        people there (the presences at the start of the step)."""
        h = self.h
        g = h.grid
        c = self._Fc
        if c is None or c[0] is not h._pm:  # (once a step, for every line at once: the hostile presence, lines x cells)
            J = np.flatnonzero(self.hostility.any(0))
            HP = np.clip(self.hostility[:, J].astype(np.float32) @ h._pm[J].astype(np.float32), 0.0, 1.0) if len(J) else None
            c = self._Fc = (h._pm, HP, {})
        F = c[2].get(k)
        if F is None:
            x = c[1][k] if c[1] is not None else None
            if x is None or not x.any():
                F = np.zeros(g.n)
            else:
                F = np.clip((x + nbr_reduce(g, np.add, x[g.nbr_idx])) / (1.0 + h._deg), 0.0, 1.0)
            c[2][k] = F
        return F

    def circumscription(self, k) -> float:
        """C, 0..1: line k's circumscription at its last contest (in-fighting's bar on splitting off; 0 before its first)."""
        return self.hem[k]

    def note_habitat(self, k, K):
        """Line k's unbraked habitat this step (circumscription reads it)."""
        self.K0[k] = K

    def after_contest(self, l, k, K, room, crowd):
        """After the competition: line k's circumscription for next step's in-fighting, any people."""
        if l.overlay or l.megafauna or l.marine:
            return
        held = self.h.p[k] >= EST
        self.hem[k] = self.circumscribed(l, k, held, room, crowd) if held.any() else 0.0

    def circumscribed(self, l, k, held, room, crowd) -> float:
        """How circumscribed line k is, 0..1 (lane 101, PW-1240 B; Carneiro 2012): the mean over the cells next to its range of how far
        each bars a faction from splitting off there. Free good country (habitat and room >= 0.3, held by no other people) bars nothing;
        country no one could split off into (habitat under 0.3, or the sea for a people that does not sail) bars fully: environmental
        circumscription; country other peoples hold bars SOCIAL_Q: social circumscription, which Carneiro finds 'generally less tight',
        allowing 'leakage' at the peripheries. Its crowding by rivals on its own land counts as social circumscription where that is
        more. Habitat here is the unbraked one (the brakes' own cut is not a barrier)."""
        h = self.h
        K0 = self.K0.get(k)
        if K0 is None:
            return 0.0
        ring = h._dilate(held, 1) & ~held
        if l.trait("sea", 0.0):  # (a seafaring people can split off over the water: only its land ring bars it)
            ring &= h._land_now
        if not ring.any():
            return 1.0
        land = h._land_now
        taken = (h._cntp - h._pm[k]) > 0
        free = land & (K0 >= 0.3) & (room >= 0.3) & ~taken
        bar = np.where(free, 0.0, np.where(land & taken, PM.SOCIAL_Q, 1.0))
        return float(max(PM.SOCIAL_Q * float(crowd), bar[ring].mean()))
