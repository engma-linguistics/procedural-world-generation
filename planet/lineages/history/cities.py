"""A people's minority in other peoples' cities (PW-889, owner 10-29: "stuff can be two things"): goblins and kobolds living as an
untrusted minority in the towns of humans and dwarves, as in the Forgotten Realms, beside their own wild country.

A group of its people with `cities = true` (spec): an overlay (no range of its own, no competition), present in its hosts' city cells
(the densest CITY_TOP of the peopled land by the host peoples' settlement, presence x density, and at least CITY_MIN_KM2) within
CITY_REACH_KM over land of its own people's range (it comes in from its people's country), from its own date on. Its people there are a `share` of the hosts' people (peoples.population). It rolls
up into its people's numbers (summary.people_rollup), not its range: the people's cells, its pass count and the map's peoples are its own
country's."""

from __future__ import annotations

import numpy as np

from ..spread import EST
from .params import CITY_MIN_KM2, CITY_REACH_KM, CITY_TOP


class CitiesMixin:
    def _city_hosts(self, l) -> list[int]:
        """The rows of a city group's hosts: its `hosts` (with their groups) or every land people that is not its own, nor an overlay,
        megafauna or a sea people."""
        own = self.tree.people_of(l.id)
        if l.hosts:
            ids = [q for h in l.hosts for q in (h, *self.tree.groups_of(h))]
        else:
            ids = [x.id for x in self.lines if not x.overlay and not x.megafauna and not x.marine and self.tree.people_of(x.id) != own]
        return [self.idx[q] for q in ids if q in self.idx]

    def _city_mask(self, l) -> tuple[np.ndarray, np.ndarray]:
        """(the city cells a city group lives in now, the hosts' presence there): the hosts' settlement (people per km2: presence x density,
        summed) among the densest CITY_TOP of the peopled land and at least CITY_MIN_KM2, on land within CITY_REACH_KM of its people's range."""
        g = self.grid
        rows = self._city_hosts(l)
        if not rows:
            return np.zeros(g.n, bool), np.zeros(g.n)
        dc = self.dens_cells()
        Ph = np.where(self.p[rows] >= EST, self.p[rows], 0.0)
        settle = (Ph * np.asarray(dc[rows])).sum(0)
        land = getattr(self, "_land_now", None)
        land = np.ones(g.n, bool) if land is None else land
        mine = (self.whole(self.tree.people_of(l.id)) >= EST) & land
        if not mine.any():
            return np.zeros(g.n, bool), np.zeros(g.n)
        r = max(1, int(round(CITY_REACH_KM / self.cell_km)))
        near = mine.copy()
        for _ in range(r):  # (over land only: the minority walks in from its people's country)
            near = near | (self._dilate(near, 1) & land)
        peopled = land & (settle > 0)
        if not peopled.any():
            return np.zeros(g.n, bool), np.zeros(g.n)
        top = max(CITY_MIN_KM2, float(np.quantile(settle[peopled], 1.0 - CITY_TOP)))
        city = near & land & (settle >= top)
        return city, Ph.max(0)

    def _city(self, l, k, step) -> None:
        """A city group this step: present (at its hosts' presence) in the city cells it can reach, nowhere else."""
        city, hp = self._city_mask(l)
        self.p[k] = np.where(city, np.maximum(hp, EST), 0.0)

    def _origin_city(self, line):
        """A city group appears in the first city cells within reach of its people: (cell, why), or False while there are none (no
        towns yet, or its people is not near any)."""
        k = self.idx[line.id]
        city, hp = self._city_mask(line)
        if not city.any():
            return False
        self.p[k] = np.where(city, np.maximum(hp, EST), 0.0)
        cell = int(np.argmax(np.where(city, hp, 0) * self._noise(line)))
        return cell, f"in the cities of its neighbours ({int(city.sum())} city cells within reach)"
