"""Brakes on a people's numbers (lane 97, owner D25, 2026-10-31): cuts to a people's carrying capacity K on each cell, the one channel
lane 82 designed for every counter-pressure (docs/review/peoples-counterpressures/design.md, "The shared plug"; PW-1165).

Four brakes, each a share `kept` of K (multiplied together, never below COUNTER_FLOOR, and on the cells a people holds never under
BRAKE_HOLD of presence: lane 101, a brake thins a people where it lives but never takes the land outright, so no brake ends a people):
- war-torn land (D25 A; lane 82's K(W), PW-1172's land term): K x (1 - LAND_Q min(1, h_war / H_MAX)), h_war the way of life's
  violent-death rate (H_WAY, the medians lane 82 read from Our World in Data's compilation of Keeley, Gat, Bowles et al.) x [(N / N0)^2 G
  + WAR_EXT F], N the people's density there, G the state's pacification, F the hostile frontier. Dense, stateless, hemmed-in peoples
  lose land; sparse ones hardly any.
- raid losses (D25 B, lane 85): a raider people's (survival 'harsh': kobolds, goblins) extra losses, the deaths its fast breeding already
  pays for, scaled by R on each cell. On a border with peoples who hate it R rises (1 + RAID_Q F). kept = r(R) / r(1) on its life
  table (life_history.harsh_kept), so a people of normal survival has nothing to scale and is untouched.
- in-fighting (D25 for the raiders, the owner's addition: "assume in-fighting to keep them down"; D31 for every people: "HUMANS
  ought also be infighting"): feuds and succession fights rise when a people has nowhere to split off to. A village grows "to a
  certain size" and can no longer be held together, so it fissions (Chagnon, PNAS profile 2014); internal political conflict is the
  main cause of group fission (Walker and Hill 2014, Human Nature 25:465); where the land is circumscribed and filled, the quarrels
  turn to war (Carneiro 2012's restatement of his 1970 theory, Social Evolution & History 11(2):5). Lane 101 (PW-1240 B): K x (1 -
  meta.war x FEUD_CUT x C x u), u the people's own fill of the land on the cell (_fill) and C its circumscription (_circumscribed),
  graded as Carneiro grades it: free good country next door bars nothing, others' land bars SOCIAL_Q (social circumscription leaks),
  unlivable country fully. A thinned people fights less, so the cut settles instead of sitting at lane 97's flat ~35% for raiders only.
- culling wars (D25 C, lane 85): a raider people's crowded frontier, outnumbered there by peoples who hate it, is hunted down to 40%
  (CULL_D 0.6) with chance CULL_P a step, and bounces back with the e-folding RECOVER_YR / x (x its growth multiple). Faster than the
  step, as for every raider, the step takes the sawtooth's mean (0.28 for any x) and logs one 'cull' event.

The sizes. R's range: violent and accidental deaths are 4-69% of all deaths in small-scale societies, average 19% (Gurven & Kaplan
2007, PDR 33:321, p. 341-343, read by lane 85): from about 0.2x to 3.6x the average. R is held within that (R_MAX 3.6); RAID_Q
is a judgement within it. The rates are absolute violent-death rates (lane 82's table, per 100,000 a year); applied as deaths to the
life tables they would barely dent a fast breeder (+0.5%/yr of adult deaths keeps kobolds 98%), which is why the raiders' brake scales
their own canon losses rather than adding the human rates.

The dials: meta.raiders (raid losses and culls) and meta.war (war-torn land and every people's in-fighting), both 1 by default;
0 switches a brake off. Off in the deep epoch (no densities then), as lane 82 designed.
"""

from __future__ import annotations

import numpy as np

from .. import life_history as LH
from ..gridops import nbr_reduce
from ..spread import EST
from . import params as PM


class CounterMixin:
    def _counter_setup(self):
        """At the start of a run: who raids (spec raids), the hostility between each pair (from the cohabitation matrix), the fields."""
        L, n = self.lines, self.grid.n
        self._raider = np.array([bool(getattr(l, "raids", False)) and not l.overlay and not l.megafauna and not l.marine for l in L])
        # hostility 0..1 of i towards j: how far the pair's cohabitation falls under the reference of two open peoples (COHAB_REF, 0.5),
        # in units of an 'apart' wish of weight 1 (compose.APART_FACTOR): an old enmity of weight w reads w, two insular peoples a little
        from ..compose import APART_FACTOR
        H = np.asarray(self.cohab, float)
        self._hos = np.clip((PM.COHAB_REF - H) / (PM.COHAB_REF * APART_FACTOR), 0.0, 1.0)
        np.fill_diagonal(self._hos, 0.0)
        for i, l in enumerate(L):  # (kin, megafauna, overlays and the sea peoples are nobody's raiding enemies)
            if l.overlay or l.megafauna or l.marine:
                self._hos[i, :] = 0.0
                self._hos[:, i] = 0.0
        self._hos[self._kin] = 0.0
        self._hem = np.zeros(len(L))  # (each line's hemmed-in share (lane 97) or circumscription (lane 101) at its last step)
        self._K0 = {}  # (line index -> its unbraked habitat this step)
        self._cull_d = {}  # (line index -> depletion field of an explicit (slow) cull sawtooth)
        self._cull_log = {}  # (line index -> kyr ago of its last logged cull)
        self.lost = {}  # (line id -> {brake: share of K held off, people-weighted over its land}, at its last step)
        self._kept_note = {}

    def _brakes_on(self, step) -> bool:
        return step.epoch != "deep" and (self.tree.raiders > 0 or self.tree.war > 0)

    def _frontier(self, k) -> np.ndarray:
        """F per cell, 0..1: the hostile presence about each cell (the cell and its neighbours), weighted by line k's hostility to each
        people there (the presences at the start of the step)."""
        g = self.grid
        c = self.__dict__.get("_Fc")
        if c is None or c[0] is not self._pm:  # (once a step, for every line at once: the hostile presence, lines x cells)
            J = np.flatnonzero(self._hos.any(0))
            HP = np.clip(self._hos[:, J].astype(np.float32) @ self._pm[J].astype(np.float32), 0.0, 1.0) if len(J) else None
            c = self._Fc = (self._pm, HP, {})
        F = c[2].get(k)
        if F is None:
            h = c[1][k] if c[1] is not None else None
            if h is None or not h.any():
                F = np.zeros(g.n)
            else:
                F = np.clip((h + nbr_reduce(g, np.add, h[g.nbr_idx])) / (1.0 + self._deg), 0.0, 1.0)
            c[2][k] = F
        return F

    def _note_hemmed(self, l, k, K, room, crowd):
        """After the competition: line k's circumscription for next step's in-fighting (_circumscribed), any people."""
        if l.overlay or l.megafauna or l.marine:
            return
        held = self.p[k] >= EST
        self._hem[k] = self._circumscribed(l, k, held, room, crowd) if held.any() else 0.0

    def _circumscribed(self, l, k, held, room, crowd) -> float:
        """How circumscribed line k is, 0..1 (lane 101, PW-1240 B; Carneiro 2012): the mean over the cells next to its range of how far
        each bars a faction from splitting off there. Free good country (habitat and room >= 0.3, held by no other people) bars nothing;
        country no one could split off into (habitat under 0.3, or the sea for a people that does not sail) bars fully: environmental
        circumscription; country other peoples hold bars SOCIAL_Q: social circumscription, which Carneiro finds 'generally less tight',
        allowing 'leakage' at the peripheries. Its crowding by rivals on its own land counts as social circumscription where that is
        more. Habitat here is the unbraked one (the brakes' own cut is not a barrier)."""
        K0 = self._K0.get(k)
        if K0 is None:
            return 0.0
        ring = self._dilate(held, 1) & ~held
        if l.trait("sea", 0.0):  # (a seafaring people can split off over the water: only its land ring bars it)
            ring &= self._land_now
        if not ring.any():
            return 1.0
        land = self._land_now
        taken = (self._cntp - self._pm[k]) > 0
        free = land & (K0 >= 0.3) & (room >= 0.3) & ~taken
        bar = np.where(free, 0.0, np.where(land & taken, PM.SOCIAL_Q, 1.0))
        return float(max(PM.SOCIAL_Q * float(crowd), bar[ring].mean()))

    def _brake(self, l, k, K, step, env, tags):
        """Line k's K with the brakes applied (the share kept per cell), and the shares lost noted for the output."""
        if l.overlay or l.megafauna or l.marine or not self._brakes_on(step):
            return K
        held = self.p[k] >= EST
        if not held.any():
            return K
        self._K0[k] = K  # (the unbraked habitat: in-fighting's fill and circumscription read it)
        kept = np.ones(self.grid.n)
        lost = {}
        F = None
        wx = self.tree.war * PM.WAR_Q
        if wx > 0:
            era = self._era[k]  # (a farming or herding way before its people farms fights as foragers do; no way: its era's row)
            hw = PM.H_ERA["forager"] if era == "forager" and l.way not in ("fisher_forager", "sea_nomad") else \
                PM.H_WAY.get(l.way, PM.H_ERA.get(era, 0.0)) if l.way else PM.H_ERA.get(era, 0.0)
            if hw > 0:
                F = self._frontier(k)
                N = np.asarray(self.dens_at(k), float) * self.p[k]  # (people per km2 on each cell)
                from . import megafauna as MG
                lev = MG.tech_level(self.tree.era, step.ago)
                G = 1.0 / (1.0 + PM.STATE_Q * lev * float(self._farm_share[k]))  # (a farming people with the tech forms states, Gómez et al. 2016)
                h = wx * hw * ((N / PM.WAR_N0) ** 2 * G + PM.WAR_EXT * F)
                kw = 1.0 - PM.LAND_Q * np.minimum(1.0, h / PM.H_MAX)
                kept *= kw
                lost["war"] = kw
            fx = self.tree.war * PM.FEUD_CUT * self._hem[k]
            if fx > 0:  # (in-fighting, every people: lane 101, owner D31 "humans ought also be infighting")
                kf = 1.0 - np.minimum(1.0, fx * self._fill(k, K))
                kept *= kf
                lost["feud"] = kf
        rx = self.tree.raiders
        if rx > 0 and self._raider[k]:
            if F is None:
                F = self._frontier(k)
            R = np.clip(np.round((1.0 + rx * PM.RAID_Q * F) / 0.05) * 0.05, 1.0, PM.R_MAX)
            era = self._era[k]
            kr = np.ones(self.grid.n)
            for v in np.unique(R[held]):
                kr[R == v] = LH.harsh_kept(l, era, float(v))
            kept *= kr
            lost["raid"] = kr
            kc = self._cull(l, k, K * kept, F, step, rx)
            if kc is not None:
                kept *= kc
                lost["cull"] = kc
        if not lost:
            return K
        kept = np.maximum(kept, PM.COUNTER_FLOOR)
        Kb = K * kept
        if PM.BRAKE_HOLD > 0:  # (lane 101: a brake thins a people where it lives, it never takes the land outright)
            Kb = np.where(held, np.maximum(Kb, np.minimum(K, PM.BRAKE_HOLD)), Kb)
        w = (K * held)
        ws = float(w.sum())
        if ws > 0:
            self.lost[l.id] = {b: round(float(((1.0 - np.maximum(v, PM.COUNTER_FLOOR)) * w).sum() / ws), 4) for b, v in lost.items()}
            self.lost[l.id]["all"] = round(float(((K - Kb) * held).sum() / ws), 4)
        return Kb

    def _fill(self, k, K) -> np.ndarray:
        """Line k's own fill of the land on each cell, 0..1: its presence at the step's start over its unbraked habitat (lane 101,
        PW-1240 B). Chagnon's villages 'grow to a certain size and could not be held together' (PNAS profile 2014); Walker and Hill
        2014 find internal political conflict the main cause of a group's fission, resource scarcity the second; Carneiro 2012:
        circumscribed crowding brings war once the population 'reaches this point' of filling its land. So in-fighting rises with the
        people's own numbers on the land, and a people thinned by its brakes, or spreading into new country, fights less."""
        return np.clip(self.p[k] / np.maximum(K, 1e-9), 0.0, 1.0)

    def _cull(self, l, k, K, F, step, rx):
        """Culling wars on line k's crowded hostile frontier (D25 C): the share kept per cell this step, or None."""
        g = self.grid
        x = max(self.growth_x(k), 1e-3)
        tau = PM.RECOVER_YR / x  # (yr)
        dt = step.dt * 1000.0
        d = self._cull_d.get(k)
        if d is not None:
            d *= np.exp(-dt / tau)
        site = (self.p[k] >= PM.CULL_FULL * K) & (self.p[k] >= EST) & (F >= PM.CULL_F)
        if not site.any():
            return None if d is None or d.max() < 1e-3 else 1.0 - d
        lab, n = g.components(site)
        area = self.cell_mkm2 * 1e6
        dk = np.asarray(self.dens_at(k), float)
        mine = np.bincount(lab[site], weights=(self.p[k] * (dk if dk.ndim else dk) * area)[site], minlength=n)
        ring = self._dilate(site, 1)
        hk = self._hos[k]
        foe = np.zeros(g.n)
        for j in np.flatnonzero(hk >= 0.5 * PM.CULL_F):
            if self.active.get(self.lines[j].id):
                dj = np.asarray(self.dens_at(j), float)
                foe += self.p[j] * (dj if dj.ndim else dj) * area
        # (the foes about each site component: their people on the component and the cells next to it, counted to the nearest site cell)
        lab_r = np.where(site, lab, nbr_reduce(g, np.maximum, np.where(site, lab, -1)[g.nbr_idx]))
        theirs = np.bincount(lab_r[ring & (lab_r >= 0)], weights=foe[ring & (lab_r >= 0)], minlength=n)
        rng = self.__dict__.setdefault("_crng", {}).get(l.id)
        if rng is None:
            import zlib
            rng = self._crng[l.id] = np.random.default_rng((self.seed, 1196, zlib.crc32(l.id.encode())))
        hit = (theirs > mine) & (rng.random(n) < min(1.0, PM.CULL_P * rx))
        if not hit.any():
            return None if d is None or d.max() < 1e-3 else 1.0 - d
        struck = hit[lab] & site
        depth = min(0.95, PM.CULL_D * rx)
        if tau * np.log(depth / PM.CULL_AGAIN) <= dt:  # (a sawtooth faster than the step: its mean, r-neutral)
            dm = depth * (1.0 - PM.CULL_AGAIN / depth) / np.log(depth / PM.CULL_AGAIN)
            out = np.where(struck, 1.0 - dm, 1.0 if d is None else 1.0 - d)
        else:  # (a slow breeder: the explicit sawtooth)
            if d is None:
                d = self._cull_d[k] = np.zeros(g.n)
            d[struck] = np.maximum(d[struck], depth)
            out = 1.0 - d
        last = self._cull_log.get(k)
        if last is None or last - step.ago >= PM.CULL_LOG_KYR:
            c = int(np.argmax(np.where(struck, self.p[k] * (dk if dk.ndim else dk), -1.0)))
            foes = [self.lines[j] for j in np.flatnonzero(hk > 0) if self.active.get(self.lines[j].id) and self._pm[j][self._dilate(struck, 1)].any()]
            names = ", ".join(sorted({f.label() for f in foes})[:3]) or "their neighbours"
            self._event_at(step.ago, "cull", l, f"{names} hunt the {l.label()} of a crowded border back to their warrens "
                                                 f"({int(struck.sum())} cells cut to {100 * (1 - depth):.0f}%; they breed back)", c)
            self._cull_log[k] = step.ago
        return out
