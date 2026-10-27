"""Movement of a people over the grid: spread and pioneers, long crossings over water, refuges, the viable-population fade."""

from __future__ import annotations

import zlib

import numpy as np

from .. import spec as SP

from ..crossing import modes, short_hop
from ..spread import EST, jump_reach, rings, spread
from ..gridops import nbr_reduce
from .gridops import _csr_gather
from . import megafauna as MG
from .habitat import hold_mask
from .pressure import crowding
from .params import JUMP_HEMMED, JUMP_KM, JUMP_MAX, JUMP_RATE, JUMP_SHAPE, JUMP_SWIM_KM, FOUNDER_KM, CONVERGE, PERSIST_EXP, CROWD_ENTER, CROWD_HOP, EXPLORE_MARGIN, FARM_KYR, HOP_EVERY_KYR, MVP_TAU_KYR, PIONEER_P


class DispersalMixin:
    def _dilate(self, m, r):
        g = self.grid
        m = m.copy()
        for _ in range(r):
            m = m | nbr_reduce(g, np.logical_or, m[g.nbr_idx])
        return m

    def _smooth(self, x):
        """max(x, mean of the neighbours). A presence field is mostly zero: then only the cells next to a held cell are summed
        (each over its own neighbours in the same order as the full sum, so the result is the same to the last bit; PW-743)."""
        g = self.grid
        nz = np.flatnonzero(x)
        if len(nz) * 4 > g.n:
            s = nbr_reduce(g, np.add, x[g.nbr_idx])
        else:
            s = np.zeros(g.n)
            if len(nz):
                rows = np.unique(g.nbr_idx[_csr_gather(g.nbr_off, nz)])
                at = _csr_gather(g.nbr_off, rows)
                cnt = g.nbr_off[rows + 1] - g.nbr_off[rows]
                s[rows] = np.add.reduceat(x[g.nbr_idx[at]], np.cumsum(cnt) - cnt)
        return np.maximum(x, s / self._deg)

    def _sync(self, k):
        """Bring the step's held-mask of line k, and the count of natives holding each cell, up to date after p[k] changed."""
        now = self.p[k] >= EST
        if k in self._nat_set:
            self._cnt += now.astype(np.int16) - self._pm[k]
        self._pm[k] = now

    def line_mvp(self, l) -> float:
        """The viable number of a line's patch: tree.viable_pop for a people of GENERATION_YR, smaller for a longer-lived one. Over the
        same span in years a long-lived line lives fewer generations, and the number it needs goes as the horizon in generations to
        1/PERSIST_EXP (Lande 1993, as origin_mvp): dragons at 200 yr need 1/8 of it, giants at 65 yr ~0.4 (PW-924)."""
        if not l.megafauna:  # (the peoples keep the tree's number; see the inbox draft on a general rule)
            return float(self.tree.viable_pop)
        return self.tree.viable_pop * min(1.0, SP.GENERATION_YR / max(l.generation_yr, 1e-6)) ** (1.0 / PERSIST_EXP)

    def _viable(self, l, k, dt, step):
        """A separate patch of the people's land holding fewer than tree.viable_pop people fades (e-folding
        MVP_TAU_KYR): a sparse people (a band roaming thousands of km²) needs a large piece of good country to
        hold a land. Only for lines sparse enough that the viable number needs more than 2 cells; never the
        largest patch (a people's last land is the refuge logic's)."""
        mvp = self.line_mvp(l)
        area = self.cell_mkm2 * 1e6
        if mvp <= 0 or mvp / (self.dens[k] * area * 0.5) <= 2:
            return
        held = self.p[k] >= EST
        if not held.any():
            return
        lab, n = self.grid.components(held) if not l.megafauna else MG.linked_pockets(self, held, MG.link_km(l))
        if n < 2:
            return
        pop = np.bincount(lab[held], weights=self.p[k][held] * self.dens[k] * area, minlength=n)
        small = pop < mvp
        small[int(np.argmax(pop))] = False
        if not small.any():
            return
        sel = held & small[np.maximum(lab, 0)]
        self.p[k][sel] *= np.exp(-dt / MVP_TAU_KYR)
        self.p[k][self.p[k] < EST] = 0
        self.faded[l.id] = self.faded.get(l.id, 0) + int(small.sum())

    def _disperse(self, l, k, K, room, crowd, step, env, tags):
        """The line's spread over its room this step: the passes its speed buys, then the pioneers into empty country."""
        g = self.grid
        deep = step.epoch == "deep"
        speed =l.speed_kmyr * l.trait("speed", 1.0) * (2.0 if "agricultural" in l.traits and step.ago <= FARM_KYR else 1.0)
        if self.animals is not None and not l.marine:  # riders and herders spread faster (animals.py)
            speed *= self.animals.speed_mult(k)
        if step.epoch == "deep":
            passes = CONVERGE
        else:
            self._budget[k] += speed * step.dt * 1000 / self.cell_km
            passes = int(self._budget[k])
            self._budget[k] -= passes
        if passes > 0:
            sea = l.trait("sea", 0.0)
            if step.ago <= SP.LATE_SEA_KYR:
                sea = max(sea, short_hop(l))
            relief = l.trait("relief", 0.6)
            ice = env["ice"] > 0.5
            # into marginal land (K < 0.3) the pressure keeps a + (1 - a) K / 0.3, a = 0.25 + 0.5 explore:
            # explorers push into poor country, homebodies stay in good
            a0 = EXPLORE_MARGIN[0] + EXPLORE_MARGIN[1] * l.demo("explore")
            a0 += (1 - a0) * CROWD_ENTER * crowd  # (a crowded people is driven into poor country, PW-887)
            enter = np.where(ice, 0.6 if "flies" in l.traits else 0.3, a0 + (1 - a0) * np.minimum(1, K / 0.3))
            land_any = env["land"]
            if l.marine:
                # every cell is 'entered' by its own factor: the realm's cells by their habitat, other sea (a coast
                # line's open water between shores) at the sea share, the land not at all (PW-775)
                enter = np.where(hold_mask(l, tags), enter, np.where(tags["sea"], sea, 0.0))
                spread(self.p[k], room, enter, tags["elev"], 0.0, 0.0, np.ones(g.n, bool), g.nbr_off, g.nbr_idx, min(passes, CONVERGE))
            else:
                spread(self.p[k], room, enter, tags["elev"], relief, sea, land_any, g.nbr_off, g.nbr_idx, min(passes, CONVERGE))
            if not deep and not l.overlay and not l.marine and PIONEER_P > 0:
                # pioneers: a people crowded at home still settles empty country next to its range, at the
                # pressure of the habitat there, not of its own (competition-thinned) presence (PW-683/684)
                src = np.where(self.p[k] >= EST, np.maximum(self.p[k], np.minimum(K, PIONEER_P)), 0.0)
                taken = (self._cnt - self._pm[k] + (self.p[k] >= EST)) > 0  # (== any native line holds it, now)
                new = spread(src, np.where(taken, 0.0, room), enter, tags["elev"], relief, sea, land_any,
                             g.nbr_off, g.nbr_idx, min(passes, CONVERGE))
                fill = (new >= EST) & ~taken & (self.p[k] < EST)
                self.p[k][fill] = new[fill]

    def _sail(self, l, k, K, room, crowd, step, env, tags):
        """Crossings: note where the line got to, and its long crossings over water (landings), about once a kyr."""
        g = self.grid
        if not l.overlay and not l.marine:
            how = "overland" if step.epoch == "deep" else "land bridge" if l.trait("sea", 0.0) == 0 and not (
                step.ago <= SP.LATE_SEA_KYR and short_hop(l)) else "strait"
            self.cross.note(l.id, self.p[k] >= EST, step.ago, how, self.events, l.label())
            # long crossings, looked at about once a kyr (the chance is per kyr; centuries add up)
            self._hop_dt[k] += step.dt * (1.0 + CROWD_HOP * crowd)  # (a crowded people sets out more often, within its craft, PW-887)
            landings = []
            if self._hop_dt[k] >= HOP_EVERY_KYR or step.epoch == "deep":
                landings = self.cross.hop(l, self.p[k], K, room, env, tags, step.ago, self._hop_dt[k], self._lrng[l.id], EST,
                                          self._partner_pull(l))
                self._hop_dt[k] = 0.0
            for cell, way, gap in landings:
                blob = rings(int(cell), K > EST, 1, g.nbr_off, g.nbr_idx) & (room > EST)
                blob[cell] = True
                self.p[k][blob] = np.maximum(self.p[k][blob], np.minimum(np.maximum(room[blob], EST), np.clip(K[blob], 0.3, 1)))
                self.crossings_n[l.id] = self.crossings_n.get(l.id, 0) + 1
                self.cross.note(l.id, blob, step.ago, way, self.events, l.label(), gap)

    def _hold_out(self, l, k, K, step):
        """A line given as living at the present isn't lost: at its lowest it holds out in a refuge."""
        g = self.grid
        if not l.overlay and l.extinct_kyr is None and l.id in self._living and (self.p[k] >= EST).sum() < 3 \
                and K.max() > 2 * EST:
            # a line given as living at the present isn't lost: at its lowest it holds out in a refuge,
            # its best habitat near where it was (as the ice-age refugia did)
            near = self._dilate(self.p[k] > 0, 3) if (self.p[k] > 0).any() else np.ones(g.n, bool)
            cell = int(np.argmax(np.where(near, K, 0) + 1e-3 * K))
            blob = rings(cell, K > EST, 1, g.nbr_off, g.nbr_idx)
            self.p[k][blob] = np.maximum(self.p[k][blob], np.clip(K[blob], 2 * EST, 0.5))
            if l.id not in self._refuged:
                self._refuged.add(l.id)
                self._event_at(step.ago, "refuge", l, f"{l.label()} hold out in a refuge", cell)

    def _jump(self, l, k, K, room, step, env, tags):
        """PW-920: a crowded people hemmed in at home (JUMP_HEMMED) founds on free suitable land farther off now and then: a Poisson
        chance JUMP_RATE x crowding x dt, the place drawn by a fat-tailed kernel exp(-D^JUMP_SHAPE) over D, the distance in the people's
        own jump lengths (land, water: by mobility, params), times the room there. Displaced peoples and those seeking new country."""
        if l.overlay or l.megafauna or JUMP_RATE <= 0:  # (megafauna: counted pockets, PW-924, not grown by jumps)
            return
        g = self.grid
        rng = self.__dict__.setdefault("_jrng", {}).get(l.id)
        if rng is None:  # (a generator of its own: the other draws of the line stay as they were)
            rng = self._jrng[l.id] = np.random.default_rng((self.seed, 920, zlib.crc32(l.id.encode())))
        lam = JUMP_RATE * step.dt
        n_ev = min(int(rng.poisson(lam)), 3)  # (thinned below: crowding, hemmed in, the best place's weight)
        if n_ev == 0:
            return
        held = self.p[k] >= EST
        if not held.any():
            return
        crowd = crowding(K, room, held)
        ring = self._dilate(held, 1) & ~held
        realm = hold_mask(l, tags) if l.marine else env["land"]
        ring &= realm
        good = (K >= 0.3) & (room >= 0.3)
        if ring.any() and (good & ring).sum() >= JUMP_HEMMED * ring.sum():
            return  # (room next door: the spread takes it)
        cell = self.cell_km
        land = env["land"]
        if l.marine:
            cost = np.where(land, np.inf, cell / JUMP_SWIM_KM)
        elif "flies" in l.traits:
            Lf = SP.HOPS["flies"][1]
            cost = np.full(g.n, cell / Lf)
        else:
            Ls = max([m[2] for m in modes(l, step.ago) if m[0] != "raft"], default=0.0)
            cost = np.where(land, cell / JUMP_KM, cell / Ls if Ls > 0 else np.inf)
        for _ in range(n_ev):
            if rng.random() >= crowd:
                continue
            D = jump_reach(held, cost, JUMP_MAX, g.nbr_off, g.nbr_idx)
            # (free land: no other people holds it, as the pioneers settle only empty country; a jump founds new country, not a mixed one)
            taken = (self._cnt - self._pm[k]) > 0 if not l.marine else np.zeros(g.n, bool)
            cand = good & realm & ~taken & ~self._dilate(held, 1) & (D > 0)
            if not cand.any():
                return
            ker = np.where(cand, np.exp(-np.maximum(D, 0) ** JUMP_SHAPE), 0.0)
            if rng.random() >= ker.max():
                continue
            w = ker * np.minimum(K, room)
            c = int(rng.choice(g.n, p=w / w.sum()))
            # the founders hold the free country round the place, ring by ring until it carries a viable population (or FOUNDER_KM)
            free = (room > EST) & (K > EST) & realm & ~taken
            area = self.cell_mkm2 * 1e6
            for r in range(1, max(2, int(round(FOUNDER_KM / cell))) + 1):
                blob = rings(c, free, r, g.nbr_off, g.nbr_idx)
                if (np.minimum(room[blob], np.clip(K[blob], 0.3, 1)) * self.dens[k] * area * 0.5).sum() >= self.tree.viable_pop:
                    break
            self.p[k][blob] = np.maximum(self.p[k][blob], np.minimum(np.maximum(room[blob], EST), np.clip(K[blob], 0.3, 1)))
            self.jumps_n[l.id] = self.jumps_n.get(l.id, 0) + 1
            if not l.marine:
                self.cross.note(l.id, blob, step.ago, "jump", self.events, l.label())
            held = self.p[k] >= EST
