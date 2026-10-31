"""Competition between peoples at a step: the room a line has left in its habitat, and how crowded that leaves it."""

from __future__ import annotations

import numpy as np

from .. import spec as SP
from ..spread import EST, coexist_cap, load_rows
from . import params as PM
from .params import HOLD_MIN, INTEGRATE, INVADE, FARM_KYR, MIX_DROP, REFUGE_MKM2, TAU_KYR
from .pressure import crowding, expanse_factor, integration_weights, invasion_weights, squeeze, surge, surge_q


class CompetitionMixin:
    def _strength(self, k) -> float:
        """Line k's contest strength apart from the cell (lane 83, params.FIT_Q): (1 / its breadth)^BREADTH_Q x its martial strength."""
        return float(self._martial[k]) * float(max(self._breadth[k], 1.0)) ** -PM.BREADTH_Q

    def _note_K(self, k, K):
        """Keep line k's habitat this step for its rivals (their coexistence shares, params.COEXIST), and its fit: how well the land
        suits its body and ways (habitat._K before the places, wishes, goods, herds and crops), with its breadth, the sum of the fit over
        the cells (the contest, FIT_Q)."""
        self._Kmat[k] = K
        F = self._fit_now.pop(k, None)
        self._Fmat[k] = K if F is None else F
        self._breadth[k] = float(self._Fmat[k].sum())

    def _fit_w(self, k, K, J, idx) -> np.ndarray:
        """The contest's fit weight (lane 83, owner D20, params.FIT_Q) of each rival j in J on line k at the cells idx, (len(J), len(idx)):
        clip(S_j / S_k, 1 / FIT_CLIP, FIT_CLIP), S = fit^FIT_Q x strength (_strength), the fit at the line's last step (_note_K; the
        habitat K for a line with none kept yet). Where both suit a cell alike, and are alike broad and strong, 1: the pair's own competition."""
        if not len(J) or not len(idx):
            return np.ones((len(J), len(idx)))
        s = np.array([self._strength(j) for j in J]) / self._strength(k)
        if PM.FIT_Q:
            Fk = self._Fmat[k][idx] if self._Fmat[k].any() else K[idx]
            Fj = np.maximum(self._Fmat[np.ix_(J, idx)], self.p[np.ix_(J, idx)])  # (a row not kept yet reads as the presence)
            w = (np.maximum(Fj, 1e-3) / np.maximum(Fk, 1e-3)[None, :]) ** PM.FIT_Q * s[:, None]
        else:
            w = np.repeat(s[:, None], len(idx), axis=1)
        return np.clip(w, 1.0 / PM.FIT_CLIP, PM.FIT_CLIP)

    def _load(self, k, K, J, a, t, idx, c, W=None):
        """The competition line k (habitat K) feels on the cells idx from its rivals J (coefficients a, t: the pair's own, or as
        weighted this step): sum_j (a_j + (1 - contact) t_j) W_j p_j, W the contest's fit weight (_fit_w), each rival's presence capped
        at its coexistence share with k where the pair's own coefficients (x W) are both under 1 (params.COEXIST, spread.coexist_cap)."""
        if not len(J) or not len(idx):
            return np.zeros(len(idx))
        if W is None:
            W = self._fit_w(k, K, J, idx)
        if not PM.COEXIST:
            P = self.p[np.ix_(J, idx)]
        else:
            P = coexist_cap(self.p, J, self.alpha[k], self.terr[k], self._aT[k], self._tT[k], self._Kmat, K, idx, c, W)
        return load_rows(P * W, a, t, J, c)

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
            W = self._fit_w(k, K, J, idx)  # (lane 83: the one that suits a cell better presses harder there)
            q = self._load(k, K, J, ak, tk, idx, c, W)
            if INVADE > 0 and not deep and not l.marine and len(J):
                # frontier invasion: along the contact line a denser people weighs its thinner rivals less (PW-887); not a people
                # its rival lives among by a wish (PW-889)
                front = self._dilate(self.p[k] >= EST, 1)[idx]
                if front.any():
                    w = np.where(self._among[k], 1.0, invasion_weights(self.dens, k))
                    fi = np.flatnonzero(front)
                    q[fi] = self._load(k, K, J, ak * w, tk * w, idx[fi], c[fi], W[:, fi])
            if PM.LEARN and len(J):  # (on its learned country a people lives as the locals do: no way-of-life discount there, PW-1155)
                q = q + self._learned_load(k, J, idx, c)
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
            f = np.clip(1 - MIX_DROP * mix * self._mixf(l) * c, 0.05, 1)
            room = np.zeros(g.n)
            room[idx] = np.clip(K[idx] - f * q, 0, None)
            over = self.p[k] > room  # displacement: held above its room, a people dwindles there
            if over.any():
                held = (self.p[k] >= EST).sum() * self.cell_mkm2
                tau = TAU_KYR
                if self.tree.growth_rates and len(J):  # (PW-1147: the rivals grow into the room at their own rate: their load-weighted x)
                    oi = np.flatnonzero(over[idx])
                    if len(oi):
                        qx = self._load(k, K, J, ak * self._xs, tk * self._xs, idx[oi], c[oi], W[:, oi])
                        q0 = self._load(k, K, J, ak, tk, idx[oi], c[oi], W[:, oi])
                        xt = np.ones(g.n)
                        xt[idx[oi]] = np.where(q0 > 1e-12, qx / np.maximum(q0, 1e-12), 1.0)
                        tau = TAU_KYR / np.clip(xt[over], 1e-3, None)
                r = (1 - np.exp(-step.dt / tau)) * np.clip(held / REFUGE_MKM2 - 1, 0, 1)
                self.p[k][over] -= r * (self.p[k][over] - room[over])
                if np.any(r > 0) and HOLD_MIN > 0:  # (the hold lapses where it is thinned under HOLD_MIN x K, the range kept above the refuge floor)
                    lapse = np.flatnonzero(over & (self.p[k] >= EST) & (self.p[k] < HOLD_MIN * K))
                    spare = int((self.p[k] >= EST).sum() - np.ceil(REFUGE_MKM2 / self.cell_mkm2))
                    if len(lapse) and spare > 0:
                        lapse = lapse[np.argsort(self.p[k][lapse] / np.maximum(K[lapse], 1e-9), kind="stable")[:spare]]
                        self.p[k][lapse] = 0.0
                self.p[k][self.p[k] < EST] = 0
            if not deep and not l.marine:
                crowd = crowding(K, room, self.p[k] >= EST)
        return room, crowd
