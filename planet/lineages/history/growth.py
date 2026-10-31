"""Each people's growth rate in the history (PW-1147, lane 78): which mortality schedule it lives under, and what r does.

The schedule (life_history.SCHEDULES) is a condition of the history, not a date (owner 10-30):
- forager, until the people farms;
- horticulturalist, once it has taken up a staple crop (crops.py's own record: the crop known over animals.TOOK_UP of its land, x
  its propensity);
- agrarian, once farming is its main food (its land-use farm share at least AGRARIAN_FARM) and it has taken up a plough animal (an
  animal whose `plough` is active: the history's marker of intensive field farming, which already adds farm capacity and crop land).
With meta.growth_rates on, x = r / the human forager r scales a people's spread (x sqrt(x): the Fisher-KPP front speed
U = 2 sqrt(nu gamma), Baggaley et al. 2012, arXiv:1203.4471), the displacement of a people by the rivals taking its land (their
load-weighted x), the fade of a small patch (MVP_TAU_KYR / x) and its far jumps (JUMP_RATE x x). A line without canon ages has x = 1.
"""

from __future__ import annotations

import numpy as np

from .. import landuse as LU
from .. import life_history as LH

AGRARIAN_FARM = 0.5  # a design judgement: "mainly farmers", over half its food from fields (landuse.shares farm)
# A farming people's density follows its era (lane 83, PW-1203 A): the tree's number is its density at its own way of life; before it has
# crops it lives as foragers do, at most ERA_DENSITY["forager"]; with a staple crop but no plough, as gardeners, at most ["horticulturalist"].
# forager 0.35 /km2: the upper quartile of Binford 2001 Table 5.01 (D-PLACE B008, 339 forager societies; median 0.11), the dnd foragers' number.
# horticulturalist 5 /km2: the top of the owner's 3-5 for forest gardeners (D20), a judgement for every gardening people.
# (Only for a people that farms, landuse farm share > 0, and only where the history models crops: herders, nomads and foragers keep theirs.)
ERA_DENSITY = {"forager": 0.35, "horticulturalist": 5.0}


class GrowthMixin:
    def _growth_setup(self):
        self._farm_share = np.array([0.0 if l.overlay else LU.shares(self.tree, l)["farm"] for l in self.lines])
        self._era = ["forager"] * len(self.lines)
        self.life_eras: dict[str, dict[str, float]] = {}  # line id -> {schedule: kyr ago it first lived under it}
        self._xs = np.array([LH.x_of(l, "forager") for l in self.lines])
        self._era_dens = self.crops is not None
        for k in range(len(self.lines)):
            self._set_era_density(k)

    def _set_era_density(self, k: int):
        """Line k's density for its era (PW-1203 A): a farming people's at most ERA_DENSITY[era] until it farms as its way of life says."""
        l = self.lines[k]
        if not self._era_dens or l.overlay or l.megafauna or self._farm_share[k] <= 0:
            return
        d = min(self._dens0[k], ERA_DENSITY.get(self._era[k], float("inf")))
        if d != self.dens[k]:
            self.dens[k] = d
            if self._dmap is not None:
                self._dmap[k] = d * self._Fprod[k]

    def _note_eras(self, step):
        """Each active line's schedule this step (after the crops and animals moved)."""
        deep = step.epoch == "deep"
        plough = []
        if self.animals is not None:
            plough = [s for s in self.animals.stocks if s.a.plough and step.ago <= s.a.plough[0]]
        for k, l in enumerate(self.lines):
            if not self.active.get(l.id) or l.overlay:
                continue
            era = "forager"
            if not deep and self.crops is not None and any(k in s.took_up for s in self.crops.stocks):
                era = "agrarian" if self._farm_share[k] >= AGRARIAN_FARM and any(k in s.took_up for s in plough) else "horticulturalist"
            if era != self._era[k]:
                self._era[k] = era
                self._xs[k] = LH.x_of(l, era)
                self._set_era_density(k)
            self.life_eras.setdefault(l.id, {}).setdefault(era, round(float(step.ago), 3))

    def growth_x(self, k: int) -> float:
        """x of line k now (1 with meta.growth_rates off)."""
        return float(self._xs[k]) if self.tree.growth_rates else 1.0
