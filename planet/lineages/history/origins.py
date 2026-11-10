"""Where and how a line originates: the landmass draw, founders, splits, arrivals, hybrids, templates."""

from __future__ import annotations

import numpy as np

from ...geo import arc_km
from .. import spec as SP
from ..crossing import modes, sea_gap
from ..spread import EST, graph_dist, rings
from . import params as PM
from .params import HYBRID_FROM_KYR, ARRIVAL_POCKET_KM, ARRIVAL_ROOM, FOUNDER_KM, HYBRID_REACH_KM, MVP_REF_GEN, ORIGIN_MVP_MULT, PARTNER_PULL, PERSIST_EXP, SPECIES_AREA_Z, START_KM
from ..gridops import dist_km, nbr_reduce
from ..seafood import rings_for
from .habitat import hold_mask


class OriginsMixin:
    def _noise(self, line):
        return np.exp(0.5 * self._lrng[line.id].gumbel(size=self.grid.n))

    def _start_hints(self, line, env, tags):
        """Origin multiplier from the line's own placement hints (PW-763): near / far from other lines' ranges (those
        alive now), a latitude band, the biggest landmass or off it. Soft: a hint that nothing satisfies changes nothing."""
        g = self.grid
        m = np.ones(g.n)
        for key, far in (("start_near", False), ("start_far", True)):
            for q in getattr(line, key):
                if q not in self.idx or not self.active.get(q):
                    continue
                po = self.whole(q) > EST
                if not po.any():
                    continue
                L = START_KM / self.cell_km
                d = graph_dist(po, int(np.ceil(3 * L)), g.nbr_off, g.nbr_idx)
                d = np.where(d < 0, 3 * L, d)  # (unreached: as far as the search went)
                m = m * (0.05 + 0.95 * (1 - np.exp(-d / L)) if far else 0.2 + 2.0 * np.exp(-d / L))
        if line.start_lat:
            lo, hi = line.start_lat
            out = np.maximum(lo - g.lat, g.lat - hi)  # degrees outside the band (negative inside)
            m = m * np.exp(-(np.maximum(out, 0) / 8.0) ** 2)
        if line.start_land:
            lab, n = g.components(tags["land"])
            if n:
                big = lab == int(np.argmax(np.bincount(lab[lab >= 0], minlength=n)))
                m = m * (np.where(big, 1.0, 0.1) if line.start_land == "largest" else np.where(big, 0.1, 1.0))
        return m

    def _near_range(self, other):
        """Multiplier for an origin by a people's range (PW-852): best at about HYBRID_REACH_KM from it (free land to spread over for
        a few centuries, then the two meet), falling off either side to 0.05 on the range itself (a newcomer among the denser people
        would be squeezed into a refuge: ALPHA_CLOSED) and 0.001 beyond 2.5 reaches. The origin's own luck (the gumbel noise is
        heavy-tailed: over a fine grid its best cell is hundreds of times a typical one) must not carry a newcomer far from the people
        whose hybrid is wanted; where nothing near suits it, it falls back to its habitat."""
        g = self.grid
        po = self.whole(other) > EST
        if not po.any():
            return np.ones(g.n)
        L = max(HYBRID_REACH_KM / self.cell_km, 1.0)  # (a cell at least: coarse test grids)
        d = graph_dist(po, int(np.ceil(2.5 * L)), g.nbr_off, g.nbr_idx)
        m = 0.05 + np.exp(-(((d - L) / (0.8 * L)) ** 2))
        return np.where(d < 0, 0.001, np.where(d == 0, 0.05, m))

    def _partner_pull(self, line):
        """Per cell, how much likelier a sea landing of `line` is there for the sake of its wanted contact hybrids (PW-861): x(1 + PARTNER_PULL)
        right at the range of the other parent of each such hybrid, falling off over HYBRID_REACH_KM; None when no hybrid is wanted or the
        partners hold nothing. Hybrids happen on a frontier, so a people that sails over should come down where its partner already is."""
        partners = [q for h in self.tree.lines.values() if h.origin == "hybrid" and line.id in h.parents and h.contact
                    and self._hybrid_factor(h)[0] > 0
                    for q in h.parents if q != line.id and self.active.get(q)]
        if not partners:
            return None
        g = self.grid
        po = np.zeros(g.n, bool)
        for q in partners:
            po |= self.whole(q) > EST
        if not po.any():
            return None
        L = max(HYBRID_REACH_KM / self.cell_km, 1.0)
        d = graph_dist(po, int(np.ceil(3 * L)), g.nbr_off, g.nbr_idx)
        return 1.0 + PARTNER_PULL * np.where(d < 0, 0.0, np.exp(-np.maximum(d, 0) / L))

    def _rivals_here(self, line, K):
        """The competition `line` would feel at each cell from the peoples alive now (as history.run: niche overlap, closed-country extra)."""
        k = self.idx[line.id]
        idx = np.flatnonzero(K >= EST)
        J = np.array([j for j in self._rivals[k] if self.active[self.lines[j].id]], np.int64)
        q = np.zeros(self.grid.n)
        if len(idx) and len(J):
            q[idx] = self._load(k, K, J, self.alpha[k], self.terr[k], idx,
                                (self._corr_now if self._corr_now is not None else np.full(self.grid.n, 0.5))[idx])
        return q

    def _seed_blob(self, k, cell, K, mask, r):
        g = self.grid
        blob = rings(int(cell), mask | (np.arange(g.n) == cell), r, g.nbr_off, g.nbr_idx) & (K > EST)
        blob[cell] = True
        self.p[k][blob] = np.maximum(self.p[k][blob], np.clip(K[blob], 0.3, 1))
        return blob

    def _found_spread(self, line, k, cell, score, K, mask, r, env):
        """Lane 97 (owner D27): found line k at FOUND_SITES seed sites, the first at `cell`, the others drawn by `score` (in proportion,
        with the line's own generator) on the same landmass within FOUND_SPREAD x JUMP_KM of it and clear of the earlier sites' blobs, each
        site holding the country within r / sqrt(sites) rings of it through `mask` (the founders' area shared among the sites). Returns
        (the union of the blobs, the site cells). With one site, or no room for more, the one blob of radius r, as before."""
        n = max(1, int(PM.FOUND_SITES))
        if n == 1 or PM.FOUND_SPREAD <= 0:
            return self._seed_blob(k, cell, K, mask, r), [cell]
        g = self.grid
        ll, _ = g.components(env["land"])
        ri = max(1, int(round(r / np.sqrt(n))))
        d0 = dist_km(g, float(g.lat[cell]), float(g.lon[cell]))
        cand = (score > 0) & (ll == ll[cell]) & (d0 <= PM.FOUND_SPREAD * PM.JUMP_KM) & (K > 2 * EST)
        sites, blob = [cell], self._seed_blob(k, cell, K, mask, ri)
        clear = 2.0 * (ri + 0.5) * self.cell_km
        cand &= d0 > clear
        rng = self._lrng[line.id]
        for _ in range(n - 1):
            if not cand.any():
                break
            w = np.where(cand, score, 0.0)
            c = int(rng.choice(g.n, p=w / w.sum()))
            sites.append(c)
            blob |= self._seed_blob(k, c, K, mask, ri)
            cand &= dist_km(g, float(g.lat[c]), float(g.lon[c])) > clear
        if len(sites) == 1:  # (no room for a second site: the one founding blob, at its full size)
            blob = self._seed_blob(k, cell, K, mask, r)
        return blob, sites

    def origin_mvp(self, line, ago):
        """PW-888: the people a landmass must carry for the line's origin to persist from `ago` (kyr before the present) to the present:
        ORIGIN_MVP_MULT x viable_pop over MVP_REF_GEN generations, growing as the horizon in generations to 1/PERSIST_EXP (Lande 1993)."""
        gens = max(ago, 0.0) * 1000.0 / max(self.gen_yr(line), 1e-6)
        return ORIGIN_MVP_MULT * self.tree.viable_pop * max(gens / MVP_REF_GEN, 1.0) ** (1.0 / PERSIST_EXP)

    def _root_of(self, lid):
        """The root (or arrival) line a line descends from."""
        l = self.tree.lines[lid]
        while l.parents and l.origin not in ("root", "arrival"):
            l = self.tree.lines[l.parents[0]]
        return l.id

    def _other_roots_land(self, line, lab, n):
        """PW-888 (owner 2026-10-27): per landmass of the step's land, whether peoples of another root line (reptilian,
        mammalian, avian...) hold any of it now: a root starts on a landmass of its own where the world has one."""
        mine = self._root_of(line.id)
        taken = np.zeros(n, bool)
        active = getattr(self, "active", {})
        for j, o in enumerate(self.lines):
            if o.overlay or o.marine or not active.get(o.id) or self._root_of(o.id) == mine \
                    or self.tree.lines[self._root_of(o.id)].origin != "root":
                continue
            at = lab[(self.p[j] >= EST) & (lab >= 0)]
            taken[np.unique(at)] = True
        return taken

    def _by_landmass(self, line, score, K, env, reach=None, ago=0.0, room=False):
        """PW-888: the landmass of an origin is drawn before the cell. Each landmass of the step's own land (connected land, so a
        glacial bridge joins two) that the origin's score reaches, and whose habitable country (cells with K > EST) would carry a
        long-term viable population (ORIGIN_MVP_MULT x tree.viable_pop, as _viable counts people), draws with probability (habitable area)^SPECIES_AREA_Z; the
        habitat score then picks the cell within it. Without this the best cell of a heavy-tailed noise field wins wherever it
        falls, and one small continent held 13-15 peoples. The same rule for every people; nothing is drawn when only one
        landmass qualifies. room (an arrival, lane 73): K is the free room, and a landmass draws in proportion to the founders its free
        room would carry: the species-area rule is of peoples arising in the world, and an arrival from outside inherits no geography
        (by area^z the gnomes landed on a 0.47 Mkm2 islet, or in a continent's leftovers)."""
        if SPECIES_AREA_Z <= 0 and not room:  # (0: off)
            return score
        lab, n = self.grid.components(env["land"])
        suit = (K > EST) & (score > 0) & (lab >= 0)
        if n < 2 or not suit.any():
            return score
        k = self.idx[line.id]
        cells = np.bincount(lab[suit], minlength=n).astype(float)
        d = self.dens_at(k)  # (megafauna: per cell, pressed by the peoples there, PW-957)
        founders = np.bincount(lab[suit], weights=K[suit] * (d[suit] if np.ndim(d) else d), minlength=n) * self.cell_mkm2 * 1e6 * 0.5
        ok = founders >= self.origin_mvp(line, ago)
        if not ok.any():  # (none can carry it for the whole horizon: the one that carries most)
            ok = founders >= founders.max()
        if line.origin == "root" and not line.marine:  # (a root line: off the other root lines' landmasses, where a viable one is left)
            free = ok & ~self._other_roots_land(line, lab, n)
            if free.any():
                ok = free
            elif not ok.any():
                pass
            else:
                cand = (founders > 0) & ~self._other_roots_land(line, lab, n)
                if cand.any():  # (none free can carry the full horizon: the free one that carries most)
                    ok = cand & (founders >= founders[cand].max())
        w = np.where(ok, founders, 0.0) if room else np.where(ok, cells, 0.0) ** SPECIES_AREA_Z
        if reach is not None:  # (founders carried over the sea: a landmass is drawn in proportion to how readily the crossing reaches it)
            top = np.zeros(n)
            np.maximum.at(top, lab[suit], reach[suit])
            w = w * top
        if np.count_nonzero(w) < 1:
            return score
        pick = int(self._lrng[line.id].choice(n, p=w / w.sum()))
        return np.where(lab == pick, score, 0.0)

    def _origin(self, line, step, env, tags, K):
        """Found `line` at this step if its origin is due: True (founded and logged), False (not yet: wait)."""
        noise = self._noise(line)
        if line.origin in ("root", "arrival"):
            res = self._origin_new(line, step, env, tags, K, noise)
        elif line.origin == "split":
            res = self._origin_split(line, step, env, tags, K, noise)
        elif line.origin == "hybrid":
            res = self._origin_hybrid(line, K, noise)
        elif line.origin == "group":
            res = self._group_origin(line, step, env, tags, K)
            if res is None:
                return False
        else:  # template
            res = self._origin_template(line)
        if isinstance(res, bool):  # (a fallback has founded it already, or it must wait)
            return res
        cell, why = res
        self._record_origin(line, step, cell, why)
        return True

    def _origin_new(self, line, step, env, tags, K, noise):
        """A root or an arrival: at its best habitat (through the landmass draw, the wishes and hints), near the other parent of a
        wanted hybrid, at a given place, or through a portal. Returns (cell, why)."""
        g, k = self.grid, self.idx[line.id]
        why = "habitat"
        score = K * self._place_mult(line, tags) * self._wish_near(line, origin=True) * self._start_hints(line, env, tags) * noise
        pull = None
        arrival_room, partnered = None, False
        if line.origin == "arrival" and not line.place:
            # (lane 73) an arrival settles where it can really live, as a split's founders do: its free room (habitat less what the
            # peoples there already take, at their coexistence shares) about the place, not the bare habitat. On the bare habitat the
            # gnomes and elves landed in country others held and were pressed into a pocket of a few cells at once
            free = np.clip(K - self._rivals_here(line, K), 0, None) * (K > EST)
            arrival_room = free if (free >= EST).any() else None
            if arrival_room is not None:
                pocket = free
                for _ in range(rings_for(self.grid, ARRIVAL_POCKET_KM)):
                    pocket = self._smooth(pocket)
                score = score * pocket / np.maximum(K, 1e-9)
        if line.origin == "arrival":  # a newcomer whose hybrids are wanted comes near the other parent
            for h in self.tree.lines.values():
                if h.origin == "hybrid" and line.id in h.parents and self._hybrid_factor(h)[0] > 0:  # (PW-752: a mixed people its stage allows)
                    other = [q for q in h.parents if q != line.id][0]
                    if self.active.get(other):  # (PW-852: within HYBRID_REACH_KM of its range, not just three cells: the two should meet soon)
                        partnered = True
                        m = self._near_range(other)
                        # where the newcomer can really live: free room (habitat less what its rivals already hold there) of at
                        # least half its best; on a crowded continent it would be squeezed into a refuge (ALPHA_CLOSED), so it
                        # then keeps its own best habitat
                        free = K - self._rivals_here(line, K)
                        for share in ARRIVAL_ROOM:  # (PW-861: the freest country near the partner, not only pristine land: on a crowded
                            # continent there is none, and the newcomer fell back to a continent of its own, far from its partner)
                            ok = (m > 0.3) & (K > EST) & (free >= max(share * K.max(), EST))
                            if ok.any():
                                break
                        if ok.any():
                            # ...in the roomier half of those cells: room round about it (the free country within a few rings), so the
                            # newcomer is not squeezed into a pocket of a few cells (it then held 50-100 cells where 1000+ were usual)
                            pocket = np.clip(free, 0, None) * (K > EST)
                            for _ in range(rings_for(self.grid, ARRIVAL_POCKET_KM)):
                                pocket = self._smooth(pocket)
                            ok = ok & (pocket >= np.median(pocket[ok]))  # (a restriction, not a weight: the origin's noise is heavy-tailed, a weight of 0.05 is beaten by its luck)
                            m = np.where(ok, m, 0.0)
                            pull = m if pull is None else pull * m
                            score = score * m
        if not line.place:
            if line.origin == "arrival" and arrival_room is not None and not partnered:  # (a wanted hybrid's partner sites it instead, PW-852, PW-861)
                score = self._by_landmass(line, score, arrival_room, env, ago=step.ago, room=True)
            else:
                score = self._by_landmass(line, score, K, env, ago=step.ago)
        if line.place:
            d = dist_km(g, *line.place)
            score = score * np.exp(-(d / 600.0) ** 2) + 1e-9 * (d < 300)
            why = "given place"
        cell = int(np.argmax(score))
        if K[cell] <= EST:
            cell = int(np.argmax(np.where(hold_mask(line, tags), K + 1e-6, 0) * noise))
            why += " (poor habitat)"
        if line.origin == "arrival" and not line.place:
            # through the portals (PW-697; in force and wandering, PW-1150, lane 78: history.portals): at each where the people can
            # live within PORTAL_KM (else, within PORTAL_FAR_KM of the nearest that can hold it; else at its best habitat anywhere,
            # as without portals); False: wait for a wandering thinning over its land
            got = self._through_portals(line, k, K, noise, pull, step)
            if got is False:
                return False
            if got is not None:
                cell, why, seeded = got
                if seeded:  # (its founders are founded in full at every portal)
                    return cell, why
        r = 3 if line.origin == "root" else max(3, int(round(FOUNDER_KM / self.cell_km)))  # (an arrival's founders: as a split's, lane 73)
        if line.origin == "root" and not line.place and not line.marine:  # (a stem forms over a region: lane 97, D27; an arrival lands where it lands)
            self._found_spread(line, k, cell, score, K, K > EST, r, env)
        else:
            self._seed_blob(k, cell, K, K > EST, r)
        return cell, why

    def _origin_split(self, line, step, env, tags, K, noise):
        """A daughter of a parent's range: inside it, at its edge, beside it or across the sea. Returns (cell, why), or the
        fallback's True."""
        g, k = self.grid, self.idx[line.id]
        pk = self.idx[line.parents[0]]
        P = self.p[pk] > EST
        if not P.any():  # (PW-1184: near the parent's last land, not at the best habitat anywhere)
            last = self._last_held.get(pk)
            par = self.tree.lines[line.parents[0]]
            why = "parent gone: near its last land"
            if line.marine and not par.marine:  # (by design, not a fallback: a sea child never holds a land stem's end back, PW-779)
                why = "by its land stem's last land (a sea people; the stem ended before it)"
            return self._origin_fallback(line, step, env, tags, K, why, last)
        if self.tree.lines[line.parents[0]].megafauna and not line.megafauna:
            return self._origin_off_megafauna(line, step, env, tags, K, noise, P)
        lab, n = g.components(P)
        sizes = np.bincount(lab[P], minlength=n)
        big = int(np.argmax(sizes))
        edge = nbr_reduce(g, np.logical_or, ~P[g.nbr_idx])
        iso = np.where(P & (lab != big), 3.0, np.where(edge & P, 1.5, 1.0))
        # within the parent's range, or a short way beyond it (a daughter taking a new niche next door)
        near = self._dilate(P, 4) & hold_mask(line, tags)
        # ...or, PW-888, founders carried over the sea to a landmass the parent's range does not touch (rafting on drift over
        # Myr, island radiations): its country weighs like the country beside the range; _by_landmass then draws the landmass
        # by habitable area, so a stem on one small continent does not put all its daughters there
        ll, _ = g.components(env["land"])
        touched = np.zeros(ll.max() + 2, bool)
        touched[ll[(P | near) & (ll >= 0)]] = True
        across = hold_mask(line, tags) & (ll >= 0) & ~touched[ll] & (SPECIES_AREA_Z > 0)
        # ...its chance falling with the sea gap from the parent's coast as any crossing does (crossing.hop: the ways open to the
        # parent at that time, rate x exp(-gap / L), relative to a gap of 0), so a far islet is rarely where founders land
        reach = np.ones(g.n)
        src = P & tags["coast"]
        if across.any() and src.any():
            ms = modes(self.tree.lines[line.parents[0]], step.ago)
            if ms:
                d = sea_gap(src, env["land"], g.nbr_off, g.nbr_idx, int(min(6 * max(m[2] for m in ms) / self.cell_km, 200)))
                km = np.maximum(d, 0) * self.cell_km
                f = sum(m[1] * np.exp(-km / m[2]) for m in ms) / sum(m[1] for m in ms)
                reach = np.where(across, np.where(d > 0, f, 0.0), 1.0)
        score = np.where(P, (K + 0.02) * iso, np.where(near, 0.6 * K, np.where(across, 0.6 * K * reach, 0))) * self._place_mult(line, tags) \
            * self._wish_near(line, origin=True) * self._start_hints(line, env, tags) * noise * (K > 2 * EST)  # (where the founders can live)
        if score.max() <= 0:  # (PW-1184: the nearest country it can live in, not the best anywhere)
            return self._origin_fallback(line, step, env, tags, K, "no room for it by the parent: nearest habitat", P)
        score = self._by_landmass(line, score, K, env, reach, step.ago)
        cell = int(np.argmax(score))
        why = ("isolated part of the parent's range" if lab[cell] != big else
               "edge of the parent's range" if edge[cell] else "inside the parent's range") if P[cell] \
            else "across the sea from the parent's range (founders carried over)" if across[cell] \
            else "beside the parent's range (new niche)"
        r = max(2, int(round(FOUNDER_KM / self.cell_km)))
        if not line.megafauna and not line.marine and not self._founders_room(cell, K, env["land"]):
            # (PW-1558, lane 269: the founders stand on an islet too small for a founders' country, beside a stem stranded there: they
            # arise in the nearest free country that can hold one, within reach of the parent's range, as a stem with no land holds out)
            cell = self._refuge_cell(line, K, P)
            why = "no founders' country on the parent's islet: the nearest free country"
            blob, _ = self._found_spread(line, k, cell, np.where(K > 2 * EST, K, 0.0), K, K > EST, r, env)
            self._take(pk, blob, P)
            return cell, why
        # the founders hold the country around the origin that suits them at least half as well as it
        # suits the parent (FOUNDER_KM)
        pK = self._K(self.tree.lines[line.parents[0]], env, tags, step)
        blob, _ = self._found_spread(line, k, cell, score, K, (K > EST) & ((K >= 0.5 * pK) | ~P), r, env)  # (a few sites over one country, D27)
        # (owner 10-30 and D20, PW-1152, PW-1181: a new people emerges at one spot and spreads from there; it takes neither the cut-off
        # part of the parent's range it arises in nor patches across it, so a split of a worldwide stem, the kobolds of the dragons, starts
        # as one people of one country)
        self._take(pk, blob, P)
        return cell, why

    def _founders_room(self, cell, K, land) -> bool:
        """PW-1558 (lane 269): whether a split founded at `cell` stands on land that can hold a founders' country: its landmass (the
        connected land at the step) has at least one founders' country (the cells within FOUNDER_KM, _founders_cells, what a held-out
        stem's refuge needs) of country it can live in (K > 2 EST), anywhere on it. Not so on an islet, or an island with little of its
        habitat: there the daughter is born on a few cells and, before boats, never leaves (dnd jitters on af2677, main 673436c0:
        leonins, halflings, hobgoblins at 0.05-0.14 Mkm2, born beside a stem stranded on a 0.1 Mkm2 islet). Its habitat on the whole
        landmass, not the patch by the cell: a mountain or desert people on a continent has room to come as its neighbours change, and
        is founded by its parent as before."""
        if not land[cell]:
            return True  # (not a land founding this rule speaks to: as before)
        lab, _ = self.grid.components(land)
        return int(((lab == lab[cell]) & (K > 2 * EST)).sum()) >= self._founders_cells(K)

    def _founders_cells(self, K) -> int:
        """A founders' country in cells: the cells within FOUNDER_KM of a cell (a split's founding take, _origin_split), at the best habitat."""
        g = self.grid
        r = max(2, int(round(FOUNDER_KM / self.cell_km)))
        return int(rings(int(np.argmax(K)), np.ones(g.n, bool), r, g.nbr_off, g.nbr_idx).sum())

    def _take(self, pk, blob, P):
        """A daughter takes the stem's land under its founding blob (D20). Where that is the last of it, the stem's land is kept as its
        last land (lane 228, PW-1184): a sibling due at the same step then arises by it, not at the best habitat anywhere, and the stem's
        own refuge (_hold_out, PW-1558) holds out by it, in the nearest country with free room."""
        if not (P & ~blob).any():
            self._last_held[pk] = P.copy()
        self.p[pk][blob & P] = 0.0

    def _origin_off_megafauna(self, line, step, env, tags, K, noise, P):
        """A people split from a megafauna stem (lane 83b: the kobolds and the dragonborn of the dragons). The stem is a handful of
        animals per country over a range that may span the world, so where it lives says nothing about where its people's own country
        lies: drawn by the stem's range (area^z, x3 on a cut-off part of it) the kobolds started on a landmass with a sixth of their
        country, and stayed there. Such a people arises at one spot (D20) as an arrival settles (lane 73): on a landmass within reach of
        the stem's range, drawn in proportion to the founders its free room (habitat less what its rivals take) would carry
        (_by_landmass, room), at its roomiest habitat there. Returns (cell, why)."""
        g, k, pk = self.grid, self.idx[line.id], self.idx[line.parents[0]]
        ll, _ = g.components(env["land"])
        touched = np.zeros(ll.max() + 2, bool)
        touched[ll[self._dilate(P, 4) & (ll >= 0)]] = True
        ok = hold_mask(line, tags) & (ll >= 0) & touched[ll] & (K > 2 * EST)
        free = np.clip(K - self._rivals_here(line, K), 0, None) * (K > EST)
        room = free if (free * ok >= EST).any() else K
        pocket = room
        for _ in range(rings_for(self.grid, ARRIVAL_POCKET_KM)):
            pocket = self._smooth(pocket)
        score = np.where(ok, pocket, 0.0) * self._place_mult(line, tags) * self._wish_near(line, origin=True) \
            * self._start_hints(line, env, tags) * noise
        if score.max() <= 0:
            return self._origin_fallback(line, step, env, tags, K, "no room for it in the stem's country: nearest habitat", P)
        score = self._by_landmass(line, score, room, env, ago=step.ago, room=True)
        cell = int(np.argmax(score))
        r = max(2, int(round(FOUNDER_KM / self.cell_km)))
        blob, _ = self._found_spread(line, k, cell, score, K, K > EST, r, env)  # (a few sites over its own country, D27)
        self._take(pk, blob, P)
        return cell, "where its own country lies, within the stem's range (a people of a megafauna stem)"

    def _origin_hybrid(self, line, K, noise):
        """A hybrid where its parents meet: (cell, why), or False while they have not met."""
        k = self.idx[line.id]
        a, b = (self.whole(q) for q in line.parents)
        O = self._meeting(a, b)
        if O.max() < EST:
            return False  # the parents haven't met yet: wait
        if line.contact:
            self.p[k] = np.where(O >= EST, O, 0.0)
            cell = int(np.argmax(O * noise))
            why = "where the parents meet"
        else:
            cell = int(np.argmax(O * (K + 0.05) * noise))
            self._seed_blob(k, cell, np.maximum(K, O), O > EST, 2)
            why = "where the parents meet (a people of its own)"
        return cell, why

    def _origin_template(self, line):
        """A template (overlay) in its hosts' range, at `sites` incursion sites: (cell, why), or False while no host is there."""
        g, k = self.grid, self.idx[line.id]
        H = np.max([self.whole(q) for q in line.parents], axis=0)
        if H.max() < EST:
            return False
        cells = []
        for _ in range(max(1, line.sites)):
            cell = int(np.argmax(np.where(H > EST, H, 0) * self._noise(line)))
            cells.append(cell)
            self.p[k][rings(cell, H > EST, 1, g.nbr_off, g.nbr_idx)] = 0.5
        cell = cells[0]
        why = f"{len(cells)} incursion sites in the hosts' range"
        return cell, why

    def _origin_fallback(self, line, step, env, tags, K, why, near=None):
        """Found `line` at its best habitat (K x noise); with `near` (a mask: its parent's range, or its last land, PW-1184) at the
        habitat it can found on (K > 2 EST, else K > EST) weighted by exp(-d / FOUNDER_KM), d the distance from `near` over land and sea:
        a split arises by its parent, wherever the parent went."""
        k = self.idx[line.id]
        score = K * self._noise(line)
        if near is not None and near.any():
            g = self.grid
            maxd = int(np.ceil(PM.LAST_LAND_REACH * FOUNDER_KM / self.cell_km))
            d = graph_dist(near, maxd, g.nbr_off, g.nbr_idx)
            d = np.where(d < 0, maxd + 1, d) * self.cell_km
            ok = K > 2 * EST if (K > 2 * EST).any() else K > EST
            score = np.where(ok, score * np.exp(-d / FOUNDER_KM), 0.0)
        cell = int(np.argmax(score))
        self._seed_blob(k, cell, K, K > EST, 3)
        self._record_origin(line, step, cell, why)
        return True

    def _record_origin(self, line, step, cell, why):
        g = self.grid
        self.origins[line.id] = {"cell": int(cell), "lat": round(float(g.lat[cell]), 2), "lon": round(float(g.lon[cell]), 2),
                                 "ago_kyr": round(step.ago, 3), "wanted_kyr": line.ago_kyr, "epoch": step.epoch, "why": why}
        if line.origin == "root" and self._tags_now is not None:  # (PW-888: does it share its landmass with another root line?)
            lab = self._tags_now["label"]
            n = int(lab.max()) + 1
            if lab[cell] >= 0 and n > 0:
                self.origins[line.id]["landmass_cells"] = int((lab == lab[cell]).sum())
                self.origins[line.id]["shares_landmass"] = bool(self._other_roots_land(line, lab, n)[lab[cell]])
        verb = {"root": "arises", "split": f"splits from {line.parents[0] if line.parents else '?'}", "arrival": "arrives",
                "hybrid": f"appears where {' and '.join(line.parents)} meet", "template": f"appears among {', '.join(line.parents)}",
                "group": f"becomes a way of life among the {self.tree.lines[line.parents[0]].label() if line.parents else '?'}"}
        self._event(step.ago, line.origin, line, f"{line.label()} {verb[line.origin]} ({why})",
                    self.origins[line.id]["lat"], self.origins[line.id]["lon"])

    def _realm_kids(self, line, living: bool = True) -> list:
        """The split children in the line's own realm (living: only those not set to die out): a marine child never holds the parent's
        end back (PW-779)."""
        kids = self.tree.living_children(line.id) if living else self.tree.lines[line.id].children
        return [c for c in kids if self.tree.lines[c].marine == line.marine]

    def _unsplit(self, line) -> bool:
        """Whether the line still has split children to come in its realm (PW-1184): it is as much given as living until its last split."""
        return any(c not in self.started for c in self._realm_kids(line, living=False))

    def _end_parent(self, line, step, env, tags):
        """After its last split the stem ends, and its remaining range lies empty for its children to spread into (owner D20, PW-1181:
        it passes to no child, of its own kind or any other; the humans out-spread the other apes into the country that suited them,
        and the jungles still hold the orangutans). Its last land is kept for a split whose parent is gone (PW-1184)."""
        k = self.idx[line.id]
        if (self.p[k] > EST).any():
            self._last_held[k] = self.p[k] > EST
        self.p[k][:] = 0
        self.active[line.id] = False
        self.ended[line.id] = step.ago

    def _start_due(self, step, env, tags, Ks):
        """Start the lines due by this step, oldest first (lines older than the history start at its first step); the habitat
        of each goes in Ks."""
        L = self.lines
        for l in L:
            if l.id in self.started or l.ago_kyr < step.ago - 1e-9:
                continue
            if l.origin == "hybrid" and step.ago > HYBRID_FROM_KYR + 1e-9:  # (no hybrid people before the farming onset, whatever its date)
                continue
            if l.origin == "hybrid" and self._hybrid_factor(l)[0] <= 0:  # (its parents' young are absorbed into a parent people, or none are
                if l.id not in self._unborn:  # born: no mixed people, PW-752; logged once, and listed as lost)
                    self._unborn.add(l.id)
                    st = self.tree.stage_of(*l.parents)
                    self._event(step.ago, "unborn", l, f"no {l.label()}: {' and '.join(self.tree.lines[q].label() for q in l.parents)} are "
                                f"{st} ({SP.STAGE_NOTES[st]})")
                continue
            if l.extinct_kyr is not None and step.ago <= l.extinct_kyr:
                self.started[l.id] = step.ago
                continue
            K = Ks[l.id] = self._K(l, env, tags, step)
            if self._origin(l, step, env, tags, K):
                self.started[l.id] = step.ago
                self.active[l.id] = True
                self._note_K(self.idx[l.id], K)  # (its rivals see its habitat from its first step: the contest's fit, lane 83)
                if l.parent:
                    par = self.tree.lines[l.parent]
                    kin = self._realm_kids(par)  # (PW-1184: the stem ends once every child of its realm has started, the ones set to
                    if not par.persists and kin and not self._unsplit(par) and self.active.get(par.id):  # die out included)
                        self._end_parent(par, step, env, tags)
