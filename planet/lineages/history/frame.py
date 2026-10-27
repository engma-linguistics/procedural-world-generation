"""A stored frame of the history: the layers, the composition, the stats."""

from __future__ import annotations

import numpy as np

from .. import compose as CP, contacts as CT, landuse as LU
from ..spread import EST
from .params import COMPOSITION_TWO_PCT


class FrameMixin:
    def _frame(self, step, env) -> dict:
        natives = np.array([not l.overlay for l in self.lines])
        own = natives[:, None] | self._linger  # (a contact hybrid living on as a people of its own counts there)
        P = np.where(own, self.p, 0)
        dom = np.where(P.max(0) >= EST, P.argmax(0), 255).astype(np.uint8)
        Pw = self.rollup(P)  # (the peoples as wholes: a people and its groups mixing is one people)
        whole = np.where(Pw.max(0) >= EST, Pw.argmax(0), 255).astype(np.uint8)
        mixn = (Pw >= 0.25).sum(0).astype(np.uint8)
        O = np.where(~own, self.p, 0)
        ov = np.where(O.max(0) >= EST, O.argmax(0), 255).astype(np.uint8)
        # the cell's composition (PW-689) and the body flags given as a share of a people (PW-701)
        den = self.fold(P)
        freq = {k: self.fold(P * f[:, None]) / np.maximum(den, 1e-9) for k, f in self.share_traits.items()}
        ramp = self._mix_ramp(step.ago)
        land = env["land"] & ~(env["ice"] > 0.5) if "ice" in env else env["land"]
        Pr = CP.reach(self.grid, Pw, self._suit(), self._corr_now if self._corr_now is not None else np.ones(self.grid.n), land, ramp, EST)
        comp = CP.compose(Pw, Pr, self.cohab, ramp, EST, freq, self.dens)
        CT.cline(self, comp, whole, land)  # (a body share spreads over the border of a close people; output only, PW-727)
        if self.contacts is not None and self._tags_now is not None:
            self.contacts.update(Pw, step, self._tags_now, self._corr_now if self._corr_now is not None else np.ones(self.grid.n), land)
        pop = land & (whole < 255)
        two = pop & (comp["mix_second_share"] >= COMPOSITION_TWO_PCT)
        cstats = {"land_cells": int(land.sum()), "peopled_cells": int(pop.sum()),
                  "empty_land_pct": round(100 * float((land & (whole == 255)).sum() / max(land.sum(), 1)), 2),
                  "two_plus_pct": round(100 * float(two.sum() / max(pop.sum(), 1)), 2),
                  "lead_share_mean_pct": round(float(comp["mix_lead_share"][pop].mean()), 1) if pop.any() else 0.0}
        areas = {l.id: round(float((self.p[k] >= EST).sum() * self.cell_mkm2), 2)
                 for k, l in enumerate(self.lines) if self.active[l.id]}
        pops = {l.id: int(self.population(k).sum()) for k, l in enumerate(self.lines) if self.active[l.id]}
        for l in self.lines:
            k = self.idx[l.id]
            sel = self.p[k] >= EST
            if sel.any():
                v = (self.grid.centers[sel] * self.p[k][sel, None]).sum(0)
                v /= np.linalg.norm(v) or 1
                self.tracks[l.id].append([round(step.ago, 3), round(float(np.degrees(np.arcsin(v[2]))), 2),
                                          round(float(np.degrees(np.arctan2(v[1], v[0]))), 2), areas.get(l.id, 0),
                                          pops.get(l.id, 0)])
        G = np.where(np.array([l.origin == "group" for l in self.lines])[:, None] & own, self.p, 0.0)  # (the groups' own ranges: PW-742)
        gp = G.max(0)
        eraq = LU.frame_inputs(self, P, land) if step.ago <= LU.ERA_WINDOW_KYR and self.goods is not None else None
        return {"ago": step.ago, "epoch": step.epoch, "env": env, "peoples": dom, "eraq": eraq,
                "groups_best": np.where(gp >= EST, G.argmax(0), 255).astype(np.uint8),
                "groups_best_pct": np.where(gp >= EST, np.round(gp * 100), 0).astype(np.uint8), "peoples_mix": mixn,
                "peoples_share": np.round(np.where(dom < 255, P.max(0), 0) * 100).astype(np.uint8),
                "peoples_overlay": ov, "peoples_whole": whole, **comp,
                **(self.animals.frame_layers() if self.animals is not None else {}),
                **(self.crops.frame_layers() if self.crops is not None else {}),
                "stats": {**step.stats, "peoples": areas, "population": pops, **cstats}}
