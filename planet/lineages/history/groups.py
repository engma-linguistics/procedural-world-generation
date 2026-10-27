"""Ways of life within a people (PW-665): their origin and divergence in place."""

from __future__ import annotations

import numpy as np

from ..spread import EST
from .params import FOUNDER_KM, GROUP_MARGIN


class GroupsMixin:
    def _group_origin(self, line, step, env, tags, K):
        """A way of life within a people (PW-665): it takes hold where its own habitat beats its people's by
        GROUP_MARGIN (unclipped, so prime land for both still tells them apart): in every such cell of its
        people's range (divergence in place), and as founders (FOUNDER_KM, as a split's) around the cell of the
        largest advantage, its origin. Without such land, at its people's range edge where it does best. Half
        the people's presence there goes over to it (they are of it); the people lives on. None: its people
        isn't there yet (wait)."""
        k = self.idx[line.id]
        pid = line.group_of
        pk = self.idx[pid]
        P = self.p[pk] > EST
        if not P.any():
            if pid not in self.started:
                return None
            cell = int(np.argmax(K * self._noise(line)))
            self._seed_blob(k, cell, K, K > EST, 3)
            return cell, "its people gone: best habitat"
        Kg = self._K(line, env, tags, step, clip=False)
        Kp = self._K(self.tree.lines[pid], env, tags, step, clip=False)
        good = P & (Kg > (1 + GROUP_MARGIN) * Kp) & (K > 2 * EST)
        nudge = self._place_mult(line, tags) * self._wish_near(line, origin=True) * self._noise(line)
        if good.any():
            score = np.where(good, Kg - Kp, 0) * nudge
            why, mask = "where its way of life suits the land better than its people's", good
        else:
            near = self._dilate(P, 2) & tags["land"]
            score = np.where(near, K, 0) * nudge * (K > 2 * EST)
            why, mask = "at its people's range edge (no land suits it better there)", K > EST
            if score.max() <= 0:
                score, why = K * nudge, "best habitat (none near its people)"
        cell = int(np.argmax(score))
        r = max(2, int(round(FOUNDER_KM / self.cell_km)))
        blob = self._seed_blob(k, cell, K, mask, r)
        # a way of life arises in place wherever it suits the land better (divergence, not migration): every such
        # cell of the people's range takes it up, from half the people there
        took = good & ~blob
        self.p[k][took] = np.maximum(self.p[k][took], np.minimum(K[took], np.maximum(0.5 * self.p[pk][took], 2 * EST)))
        self.p[pk][(blob | took) & P] *= 0.5
        self.p[pk][self.p[pk] < EST] = 0
        return cell, why

    def _diverge(self, l, k, env, tags, step):
        """A way of life goes on arising in place after its origin (PW-684): in a cell of its people's range that
        it doesn't hold yet and where its habitat beats its people's by GROUP_MARGIN (as at its origin), half the
        people there go over to it. A people that settles new country later (crossing a sea to a cold coast, or
        to a river plain) lives there as its ways of life suit it, as it would have where it already was."""
        pk = self.idx[l.group_of]
        P = self.p[pk] > EST
        if not P.any():
            return
        Kg = self._K(l, env, tags, step, clip=False)
        Kp = self._K(self.tree.lines[l.group_of], env, tags, step, clip=False)
        new = P & (self.p[k] < EST) & (Kg > (1 + GROUP_MARGIN) * Kp) & (np.minimum(Kg, 1.0) > 2 * EST)
        if new.any():
            self.p[k][new] = np.minimum(np.minimum(Kg[new], 1.0), np.maximum(0.5 * self.p[pk][new], 2 * EST))
            self.p[pk][new] *= 0.5
            self.p[pk][self.p[pk] < EST] = 0
