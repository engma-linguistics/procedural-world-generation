"""Contact hybrids (PW-613, PW-852): where their parents meet, lingering and fertility."""

from __future__ import annotations

import numpy as np

from ..spread import EST, rings
from .params import LINGER_KYR, LINGER_MIN
from ..gridops import nbr_reduce


class ContactMixin:
    def _meeting(self, a, b):
        """Where two peoples meet (PW-852): in a cell both hold, or on a frontier: one holds the cell and the other the cell next to it.
        In closed country a rival excludes the other from its cells (history.run), so two ranges on one continent
        usually only touch, and contact is a border, not an overlap. The presence there is the weaker of the two."""
        g = self.grid
        da = np.maximum(a, nbr_reduce(g, np.maximum, a[g.nbr_idx]))
        db = np.maximum(b, nbr_reduce(g, np.maximum, b[g.nbr_idx]))
        return np.maximum(np.minimum(a, db), np.minimum(da, b))

    def _hybrid(self, l, k, K, step):
        """A contact hybrid: where its parents meet it is a share of their people (and grows with the contact);
        once it has appeared it lingers where they no longer meet, fading (LINGER_KYR) within its own habitat,
        and where they last met it lives on as a small people of its own (PW-613)."""
        g = self.grid
        a, b = (self.whole(q) for q in l.parents)
        O = self._meeting(a, b)
        meet = O >= EST
        old = self.p[k]
        linger = np.minimum(old * np.exp(-step.dt / LINGER_KYR), K) if l.linger else np.zeros(g.n)
        new = np.where(meet, np.maximum(O, linger), linger)
        if meet.any():
            self._last_meet[l.id] = meet & (K > EST)
            self._apart.discard(l.id)
        elif l.linger and l.id in self._last_meet:
            last = self._last_meet[l.id]
            if not last.any():  # (the parents met only where its own habitat is poor: the best of it nearby)
                near = self._dilate(old > 0, 2) if (old > 0).any() else np.ones(g.n, bool)
                last = rings(int(np.argmax(np.where(near, K, 0))), K > EST, 1, g.nbr_off, g.nbr_idx)
                self._last_meet[l.id] = last
            new[last] = np.maximum(new[last], np.clip(K[last] * LINGER_MIN, 2 * EST, None))
            if l.id not in self._apart:
                self._apart.add(l.id)
            if l.id not in self._lingered:  # (the first time only: parents can meet again and part again)
                self._lingered.add(l.id)
                c = int(np.flatnonzero(last)[0]) if last.any() else 0
                self._event_at(step.ago, "lingers", l,
                               f"{l.label()} live on as a people of their own where "
                               f"{' and '.join(self.tree.lines[q].label() for q in l.parents)} last met", c)
        new[new < EST] = 0.0
        self.p[k] = new
        self._linger[k] = (new >= EST) & ~meet

    def _fertility(self, l) -> float:
        """A contact hybrid's share scales with how fertile its parents' hybrids are by their divergence (PW-851: fertile out to ~1-2 Myr, mostly
        sterile to ~4, none beyond); 1 for a template, and where no divergence date is there to read (half-elves)."""
        if l.origin != "hybrid":
            return 1.0
        f = self.__dict__.setdefault("_fert", {})
        if l.id not in f:
            f[l.id] = self.tree.fertility(*l.parents)
        return f[l.id]
