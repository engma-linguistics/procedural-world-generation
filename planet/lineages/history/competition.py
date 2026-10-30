"""Competition between peoples at a step: the room a line has left in its habitat, and how crowded that leaves it."""

from __future__ import annotations

import numpy as np

from .. import spec as SP
from ..spread import EST, rivals_load
from .params import HOLD_MIN, INTEGRATE, INVADE, FARM_KYR, MIX_DROP, REFUGE_MKM2, TAU_KYR
from .pressure import crowding, integration_weights, invasion_weights, pioneer_factors, squeeze


class CompetitionMixin:
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
            q = rivals_load(self.p, J, ak, tk, idx, c)
            if INVADE > 0 and not deep and not l.marine and len(J):
                # frontier invasion: along the contact line a denser people weighs its thinner rivals less (PW-887); not a people
                # its rival lives among by a wish (PW-889)
                front = self._dilate(self.p[k] >= EST, 1)[idx]
                if front.any():
                    w = np.where(self._among[k], 1.0, invasion_weights(self.dens, k))
                    fi = np.flatnonzero(front)
                    q[fi] = rivals_load(self.p, J, ak * w, tk * w, idx[fi], c[fi])
            if "agricultural" in l.traits and step.ago <= FARM_KYR:
                q = q * np.where(tags["farmland"][idx], 0.5, 1.0)  # farmers push into others' fertile lowland
            press = SP.WAY_PRESS.get(l.way) if l.way and self.animals is not None and self.goods is not None else None
            if press and press[0] in self.goods and step.epoch != "deep":
                herd = min(1.0, self.animals.herding(k) / SP.HERD_FULL)
                if herd > 0:  # herders hold good pasture against settled neighbours (spec.WAY_PRESS, PW-756)
                    q = q * (1 - (1 - press[1]) * herd * np.clip(self.goods[press[0]][idx], 0, 1))
            q = q * l.trait("push", 1.0)
            qm, pio = pioneer_factors(None if deep else self.started[l.id] - step.ago, l.demo("explore"),
                                      int((self.p[k] >= EST).sum()), int((K >= 0.3).sum()))
            q = q * qm  # (a newcomer takes room as a first settler does; an expansive people with room to grow presses on, PW-869)
            f = np.clip(1 - MIX_DROP * mix * self._mixf(l) * c, 0.05, 1)
            room = np.zeros(g.n)
            room[idx] = np.clip(K[idx] - f * q, 0, None)
            over = self.p[k] > room  # displacement: held above its room, a people dwindles there
            if over.any():
                held = (self.p[k] >= EST).sum() * self.cell_mkm2
                r = (1 - np.exp(-step.dt / TAU_KYR)) * np.clip(held / REFUGE_MKM2 - 1, 0, 1) * (1.0 - pio)  # (a newcomer's founders are not displaced, PW-869)
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
