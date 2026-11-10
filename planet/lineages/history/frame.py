"""A stored frame of the history: the layers, the composition, the stats."""

from __future__ import annotations

import numpy as np

from .. import compose as CP, contacts as CT, landuse as LU
from ..spread import EST
from .params import COMPOSITION_TWO_PCT, HYBRID_FROM_KYR, LEARNED_MIN


class FrameMixin:
    @staticmethod
    def _presence(Pw) -> tuple:
        """The presence table's rows of a frame (output.write_presence): (line, cell) where the whole people is established (EST),
        sorted by line then cell, and its % of the cell's habitat."""
        pl, pc = np.nonzero(Pw >= EST)
        return pl.astype(np.uint16), pc.astype(np.uint32), np.round(np.clip(Pw[pl, pc], 0, 1) * 100).astype(np.uint8)

    def presence_stored(self) -> np.ndarray:
        """Each people's presence now as a frame stores it and the after-run read-outs read it back (lines x cells, 0..1): the
        peoples as wholes (groups rolled in, overlays out but contact hybrids living on), established cells only, in whole %."""
        natives = np.array([not l.overlay for l in self.lines])
        pl, pc, ps = self._presence(self.rollup(np.where(natives[:, None] | self._linger, self.p, 0)))
        out = np.zeros(self.p.shape, np.float32)
        out[pl.astype(np.int64), pc.astype(np.int64)] = ps / 100.0
        return out

    def _frame(self, step, env) -> dict:
        natives = np.array([not l.overlay for l in self.lines])
        own = natives[:, None] | self._linger  # (a contact hybrid living on as a people of its own counts there)
        P = np.where(own, self.p, 0)
        dom = np.where(P.max(0) >= EST, P.argmax(0), 255).astype(np.uint8)
        Pw = self.rollup(P)  # (the peoples as wholes: a people and its groups mixing is one people)
        whole = np.where(Pw.max(0) >= EST, Pw.argmax(0), 255).astype(np.uint8)
        mixn = (Pw >= 0.25).sum(0).astype(np.uint8)
        # every people's presence (lane 109, PW-670): each whole people, megafauna and contact hybrids living on included, on every cell
        # where it is established (EST): (line, cell) sorted by line then cell, and its % of the cell's habitat (output.py: a sparse table)
        presence = self._presence(Pw)
        O = np.where(~own, self.p, 0)
        ov = np.where(O.max(0) >= EST, O.argmax(0), 255).astype(np.uint8)
        # the cell's composition (PW-689) and the body flags given as a share of a people (PW-701)
        den = self.fold(P)
        freq = {k: self.fold(P * f[:, None]) / np.maximum(den, 1e-9) for k, f in self.share_traits.items()}
        comp, land = self._composition(step.ago, env, Pw, freq)
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
        learned, lstats = self._learned_frame(whole, env)
        G = np.where(np.array([l.origin == "group" for l in self.lines])[:, None] & own, self.p, 0.0)  # (the groups' own ranges: PW-742)
        gp = G.max(0)
        eraq = LU.frame_inputs(self, P, land) if step.ago <= LU.ERA_WINDOW_KYR and self.goods is not None else None
        return {"ago": step.ago, "epoch": step.epoch, "env": env, "peoples": dom, "eraq": eraq,
                "groups_best": np.where(gp >= EST, G.argmax(0), 255).astype(np.uint8),
                "groups_best_pct": np.where(gp >= EST, np.round(gp * 100), 0).astype(np.uint8), "peoples_mix": mixn, "peoples_learned": learned,
                "peoples_share": np.round(np.where(dom < 255, P.max(0), 0) * 100).astype(np.uint8),
                "peoples_overlay": ov, "peoples_whole": whole, "presence": presence, **comp,
                **(self.animals.frame_layers() if self.animals is not None else {}),
                **(self.crops.frame_layers() if self.crops is not None else {}),
                "stats": {**step.stats, "peoples": areas, "population": pops, **cstats, **({"learned": lstats} if lstats else {})}}

    def _composition(self, ago, env, Pw, freq=None):
        """(the cells' composition, PW-689: compose's mix_lead, mix_second and their shares, from the peoples as wholes Pw, their
        reach and the mixing ramp now; the open land it reads). A stored frame's, and the live town count's (PW-1608: the
        settlement ledger reads a frame's)."""
        ramp = self._mix_ramp(ago)
        land = env["land"] & ~(env["ice"] > 0.5) if "ice" in env else env["land"]
        Pr = CP.reach(self.grid, Pw, self._suit(), self._corr_now if self._corr_now is not None else np.ones(self.grid.n), land, ramp, EST)
        # (before the farming onset foragers meet other peoples only at their ranges' edges, PW-927)
        edge = CP.edges(self.grid, Pw, land, EST) if ago > HYBRID_FROM_KYR else None
        return CP.compose(Pw, Pr, self.cohab, ramp, EST, freq, self.dens, edge), land

    def _learned_frame(self, whole, env):
        """Niche learning in a frame (PW-1155): the learned acceptance per cell, % (peoples_learned), of the people leading it as a whole
        (peoples_whole; the most any of its lines, the people or its groups, has learned there), and per line the Mkm² it holds on
        learned country (L >= LEARNED_MIN where its preference alone gives K0 < 0.3) by biome class (habitat.BIOMES)."""
        from .habitat import BIOMES, biome_class
        out = np.zeros(self.grid.n, np.uint8)
        stats = {}
        if not self._L or self._tags_now is None:
            return out, stats
        b = biome_class(env, self._tags_now)
        for k, L in self._L.items():
            sel = whole == self.idx[self.tree.people_of(self.lines[k].id)]
            out[sel] = np.maximum(out[sel], np.round(np.clip(L[sel], 0, 1) * 100).astype(np.uint8))
            got = self._learn_in.get(k)
            if got is None or not self.active.get(self.lines[k].id):
                continue
            m = (self.p[k] >= EST) & (L >= LEARNED_MIN) & (got[0] < 0.3) & (b >= 0)
            if m.any():
                cnt = np.bincount(b[m], minlength=len(BIOMES))
                stats[self.lines[k].id] = {BIOMES[i]: round(float(c * self.cell_mkm2), 3) for i, c in enumerate(cnt) if c}
        return out, stats
