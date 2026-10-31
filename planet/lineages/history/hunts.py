"""Enemies hunting each other where their lands meet (lane 97, owner D26 B, PW-1206): story on the map, not a brake.

The pairs are the ones the tree names as enemies: its 'apart' wishes, the old enmities (dnd: elves and orcs, dwarves and goblins...).
Where two such peoples (with their groups) hold neighbouring cells, the border sees a hunt now and then: an event of kind 'hunt' at a
border cell, which the viewer shows on the map with the other events. Nobody's numbers change: the hunting that thins peoples is the
war ticket's (PW-1172, option A, later). The rate is a judgement for the story's sake (HUNT_PER_KYR x the wish's weight a kyr: a pair at
weight 1 with a shared border logs about one hunt in two kyr), not a measured rate.
"""

from __future__ import annotations

import numpy as np

from ..gridops import nbr_reduce
from . import params as PM


class HuntsMixin:
    def _hunts(self, step):
        """D26 B: the enemies a tree names ('apart' wishes, the old enmities) hunt each other where their lands meet: story on the map
        (events of kind 'hunt'), not a brake. A pair with a shared border logs a hunt with chance HUNT_PER_KYR x dt a step, at a cell of
        the border drawn at random."""
        if step.epoch == "deep" or PM.HUNT_PER_KYR <= 0:
            return
        g = self.grid
        rng = self.__dict__.get("_hrng")
        if rng is None:
            rng = self._hrng = np.random.default_rng((self.seed, 1206))
        for w in self.tree.wishes:
            if w.want != "apart" or w.a not in self.idx or w.b not in self.idx:
                continue
            a, b = self.tree.lines[self.tree.people_of(w.a)], self.tree.lines[self.tree.people_of(w.b)]
            if a.megafauna or b.megafauna or a.marine or b.marine:
                continue
            ia = [self.idx[a.id], *self._groups.get(a.id, [])]
            ib = [self.idx[b.id], *self._groups.get(b.id, [])]
            if not any(self.active.get(self.lines[i].id) for i in ia) or not any(self.active.get(self.lines[i].id) for i in ib):
                continue
            if rng.random() >= min(1.0, PM.HUNT_PER_KYR * min(w.weight, 1.0) * step.dt):
                continue
            A, B = self._pm[ia].any(0), self._pm[ib].any(0)
            border = A & nbr_reduce(g, np.logical_or, B[g.nbr_idx])
            if not border.any():
                continue
            c = int(rng.choice(np.flatnonzero(border)))
            hunter, prey = (a, b) if rng.random() < 0.5 else (b, a)
            self._event_at(step.ago, "hunt", hunter, f"{hunter.label()} and {prey.label()} hunt each other along their border "
                                                     f"(an old enmity); war parties of the {hunter.label()} strike first", c)
