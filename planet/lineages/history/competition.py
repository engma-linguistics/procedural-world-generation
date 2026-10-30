"""Competition between peoples at a step: the room a line has left in its habitat, and how crowded that leaves it."""

from __future__ import annotations

import numpy as np

from .. import spec as SP
from ..spread import EST, coexist_cap, load_rows, rivals_load
from . import params as PM
from .params import HOLD_MIN, INTEGRATE, INVADE, FARM_KYR, MIX_DROP, REFUGE_MKM2, TAU_KYR
from .pressure import crowding, expanse_factor, integration_weights, invasion_weights, squeeze, surge, surge_q


class CompetitionMixin:
    def _load(self, k, K, J, a, t, idx, c):
        """The competition line k (habitat K) feels on the cells idx from its rivals J (coefficients a, t: the pair's own, or as
        weighted this step): sum_j (a_j + (1 - contact) t_j) p_j, each rival's presence capped at its coexistence share with k where
        the pair's own coefficients are both under 1 (params.COEXIST, spread.coexist_cap)."""
        if not PM.COEXIST or not len(J) or not len(idx):
            return rivals_load(self.p, J, a, t, idx, c)
        P = coexist_cap(self.p, J, self.alpha[k], self.terr[k], self._aT[k], self._tT[k], self._Kmat, K, idx, c)
        return load_rows(P, a, t, J, c)

    def _compete(self, l, k, K, step, tags, corr, mix, deep):
        """The room line `l` (index k, habitat K) has at this step after its rivals, and its crowding (0..1). A people held above
        its room dwindles toward it, so this changes self.p[k]."""
        g, L = self.grid, self.lines
        crowd = 0.0
        if l.overlay:  # template: within its hosts, no competition
            room = K
        else:
            # competition, scaled by the cell's contact value: exclusion in closed country,
            # relaxed in corridors, most during the late mixing
            # (alpha_eff = alpha + (1 - c)(ALPHA_CLOSED - alpha) x same_way, Lotka-Volterra-like: under 1
            # the peoples settle side by side, over 1 the larger one excludes; contact c: crossing.corridor)
            # (only where the line can hold ground, K >= EST, and only over its rivals: the room
            # elsewhere is never used, so this is exact and ~5x cheaper than over every cell and line)
            idx = np.flatnonzero(K >= EST)
            J = np.array([j for j in self._rivals[k] if self.active[L[j].id]], np.int64)
            c = corr[idx]
            ak, tk = self.alpha[k], self.terr[k]
            if INTEGRATE > 0 and not deep and not l.marine and len(J):
                # integration under pressure (PW-889): a squeezed people feels its friendlier neighbours less, so it shares their land
                sq = squeeze(self._crowd[k], int((self.p[k] >= EST).sum()), int((K >= 0.3).sum()))
                if sq > 0:
                    iw = integration_weights(self.cohab[k], sq)
                    ak, tk = ak * iw, tk * iw
            q = self._load(k, K, J, ak, tk, idx, c)
            if INVADE > 0 and not deep and not l.marine and len(J):
                # frontier invasion: along the contact line a denser people weighs its thinner rivals less (PW-887); not a people
                # its rival lives among by a wish (PW-889)
                front = self._dilate(self.p[k] >= EST, 1)[idx]
                if front.any():
                    w = np.where(self._among[k], 1.0, invasion_weights(self.dens, k))
                    fi = np.flatnonzero(front)
                    q[fi] = self._load(k, K, J, ak * w, tk * w, idx[fi], c[fi])
            if "agricultural" in l.traits and step.ago <= FARM_KYR:
                q = q * np.where(tags["farmland"][idx], 0.5, 1.0)  # farmers push into others' fertile lowland
            press = SP.WAY_PRESS.get(l.way) if l.way and self.animals is not None and self.goods is not None else None
            if press and press[0] in self.goods and step.epoch != "deep":
                herd = min(1.0, self.animals.herding(k) / SP.HERD_FULL)
                if herd > 0:  # herders hold good pasture against settled neighbours (spec.WAY_PRESS, PW-756)
                    q = q * (1 - (1 - press[1]) * herd * np.clip(self.goods[press[0]][idx], 0, 1))
            q = q * l.trait("push", 1.0)
            if not deep:  # (an expansive people with room to grow presses on, PW-869)
                q = q * expanse_factor(l.demo("explore"), int((self.p[k] >= EST).sum()), int((K >= 0.3).sum()))
            # momentum (owner 10-30, lane 73): a people on the upswing, a newcomer among them, contests held land with an edge that
            # fades when its growth stalls (pressure.surge), at the era's dial (meta.surge_early / surge_late)
            mo, self._mref[k] = surge(float(self.p[k].sum()), self._mref[k], step.dt)
            if mo > 0:
                q = q * (1.0 - surge_q(self.tree.surge_early, self.tree.surge_late, step.ago) * mo)
            if l.mainline and PM.MAINLINE_Q > 0:  # (option C: the genre's core peoples, authored)
                q = q * (1.0 - PM.MAINLINE_Q)
            f = np.clip(1 - MIX_DROP * mix * self._mixf(l) * c, 0.05, 1)
            room = np.zeros(g.n)
            room[idx] = np.clip(K[idx] - f * q, 0, None)
            over = self.p[k] > room  # displacement: held above its room, a people dwindles there
            if over.any():
                held = (self.p[k] >= EST).sum() * self.cell_mkm2
                r = (1 - np.exp(-step.dt / TAU_KYR)) * np.clip(held / REFUGE_MKM2 - 1, 0, 1)
                self.p[k][over] -= r * (self.p[k][over] - room[over])
                if r > 0 and HOLD_MIN > 0:  # (the hold lapses where it is thinned under HOLD_MIN x K, the range kept above the refuge floor)
                    lapse = np.flatnonzero(over & (self.p[k] >= EST) & (self.p[k] < HOLD_MIN * K))
                    spare = int((self.p[k] >= EST).sum() - np.ceil(REFUGE_MKM2 / self.cell_mkm2))
                    if len(lapse) and spare > 0:
                        lapse = lapse[np.argsort(self.p[k][lapse] / np.maximum(K[lapse], 1e-9), kind="stable")[:spare]]
                        self.p[k][lapse] = 0.0
                self.p[k][self.p[k] < EST] = 0
            if not deep and not l.marine:
                crowd = crowding(K, room, self.p[k] >= EST)
        return room, crowd
