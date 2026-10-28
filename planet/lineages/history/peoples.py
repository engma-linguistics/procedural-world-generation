"""A people as a whole with its groups: presence, rollup and fold, suitability, population."""

from __future__ import annotations

import numpy as np

from .. import compose as CP
from ..spread import EST
from . import megafauna as MG


class PeoplesMixin:
    def dens_at(self, k: int, P: np.ndarray | None = None):
        """Line k's density, per km2: a people's own (a number); a megafauna line's per cell, natural where no people presses it and
        pressed where peoples do (an array, MG.local_density; P: the presences to take the pressure and prey from, else those at the
        start of the step)."""
        if not self.lines[k].megafauna:
            return self.dens[k]
        if (P is None or P is self.p) and self._press is not None:
            return MG.local_density(self, k, self._press, self._prey)
        P = self.p if P is None else P
        c = self.__dict__.get("_dens_memo")
        if c is None or c[0] is not P:  # (one pressure and prey per presence array: the summary asks for every line)
            s = MG.pressure(self, P, self._land_now)
            prey = MG.prey_now(self, P, s, self._tags_now) if self._tags_now is not None and not self._deep_now else None
            c = self._dens_memo = (P, s, prey)
        return MG.local_density(self, k, c[1], c[2])

    def gen_yr(self, l) -> float:
        """A line's generation time, years: its own, or a dragon's from its age schedule (meta.dragon_generation, PW-959)."""
        if l.megafauna and "flies" in l.traits:
            from .. import dragon_ages as DA
            return DA.generation_yr(self.tree.dragon_ages, self.tree.dragon_generation, l.generation_yr)
        return l.generation_yr

    def whole(self, lid: str, P: np.ndarray | None = None) -> np.ndarray:
        """A people's presence with its groups (their sum, at most 1); a line without groups, its own."""
        P = self.p if P is None else P
        k = self.idx[lid]
        gs = self._groups.get(lid)
        if not gs:
            return P[k]
        return np.minimum(1.0, P[k] + P[gs].sum(0))

    def rollup(self, P: np.ndarray) -> np.ndarray:
        """P with each people's row holding its groups too (whole) and the groups' rows zeroed: the peoples as
        wholes, indexed as the lines (the whole-people map layer, the mixing of peoples, the summaries)."""
        if not any(self._groups.values()):
            return P
        out = P.copy()
        for lid, gs in self._groups.items():
            if gs:
                k = self.idx[lid]
                out[k] = np.minimum(1.0, P[k] + P[gs].sum(0))
                out[gs] = 0.0
        return out

    def fold(self, M: np.ndarray) -> np.ndarray:
        """M with each people's row summed with its groups' rows (no cap) and the groups' rows zeroed."""
        out = M.copy()
        for lid, gs in self._groups.items():
            if gs:
                out[self.idx[lid]] = M[self.idx[lid]] + M[gs].sum(0)
                out[gs] = 0.0
        return out

    def _suit(self) -> np.ndarray:
        """How well each people (its groups counted in) could live in each cell this step, 0..1 (from its habitat K)."""
        S = np.zeros_like(self.p)
        for k, K in self._K_now.items():
            if not self.lines[k].overlay and self.active[self.lines[k].id]:
                S[k] = np.where(K >= EST, np.clip(K / CP.SUIT_K, 0.0, 1.0), 0.0)
        for lid, gs in self._groups.items():
            if gs:
                S[self.idx[lid]] = np.maximum(S[self.idx[lid]], S[gs].max(0))
        return S

    def population(self, k: int, P: np.ndarray | None = None) -> np.ndarray:
        """People per cell of line k: presence x density x cell area. An overlay (template, contact hybrid) is
        its share of its hosts' people where it is, except where a contact hybrid lives on as a people of its own."""
        P = self.p if P is None else P
        l, area = self.lines[k], self.cell_mkm2 * 1e6
        x = np.where(P[k] >= EST, P[k], 0.0)
        if not l.overlay:
            return x * self.dens_at(k, P) * area
        hosts = sum(np.where(P[j] >= EST, P[j], 0.0) * self.dens[j]
                    for q in l.parents for j in [self.idx[q], *self._groups.get(q, [])])
        own = self._linger[k]
        return np.where(own, x * self.dens[k] * area, (x > 0) * l.share * self._fertility(l) * hosts * area)
