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
  meta.war x FEUD_CUT x C x u), u the people's own fill of the land on the cell (_fill) and C its circumscription (history.rule),
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

The seam (PW-1280): the brakes read three stand-ins for states and war through `self.rule` (history.rule.StandIns): a state's
pacification G, the hostile frontier F (and the hostility matrix behind it) and in-fighting's circumscription C. Polities in the
history (v4, PW-1434) swap them by setting `Rule` to a class with the same methods; the formulas here stay.
"""

from __future__ import annotations

import numpy as np

from .. import life_history as LH
from ..gridops import nbr_reduce
from ..spread import EST
from . import params as PM
from .rule import StandIns


class CounterMixin:
    Rule = StandIns  # (the seam polities swap in through, PW-1280: G, F and C come from here; history.rule)

    def _counter_setup(self):
        """At the start of a run: who raids (spec raids), the stand-ins for states and war (history.rule), the fields."""
        L = self.lines
        self._raider = np.array([bool(getattr(l, "raids", False)) and not l.overlay and not l.megafauna and not l.marine for l in L])
        R = self.Rule
        if PM.POLITIES_LIVE and R is StandIns:  # (polities in the history, first cut, PW-1434: off by default; history.polity_live)
            from .polity_live import LivePolities as R
        self.rule = R(self)
        self._cull_d = {}  # (line index -> depletion field of an explicit (slow) cull sawtooth)
        self._cull_log = {}  # (line index -> kyr ago of its last logged cull)
        self.lost = {}  # (line id -> {brake: share of K held off, people-weighted over its land}, at its last step)
        # (each people's own warlikeness A, PW-1172: its war_x, x AGGRESSIVE_X for the `aggressive` trait)
        self._war_a = np.array([float(getattr(l, "war_x", 1.0)) * (PM.AGGRESSIVE_X if "aggressive" in l.traits else 1.0) for l in L])
        self._refugee = np.zeros(len(L))  # (the share of its land war took at its last step: refugees add it to its crowding)
        self.troubles_n = {}  # (line id -> its steps in times of troubles)
        self._trouble_log = {}  # (line index -> kyr ago of its last logged troubles)
        self.refugee_n = {}  # (line id -> its jumps driven mostly by refugees)
        self._kept_note = {}

    def _brakes_on(self, step) -> bool:
        return step.epoch != "deep" and (self.tree.raiders > 0 or self.tree.war > 0)

    def _note_hemmed(self, l, k, K, room, crowd):
        """After the competition: the stand-ins note line k's circumscription for next step's in-fighting (history.rule)."""
        self.rule.after_contest(l, k, K, room, crowd)

    def _brake(self, l, k, K, step, env, tags):
        """Line k's K with the brakes applied (the share kept per cell), and the shares lost noted for the output."""
        if l.overlay or l.megafauna or l.marine or not self._brakes_on(step):
            return K
        held = self.p[k] >= EST
        if not held.any():
            return K
        self.rule.note_habitat(k, K)  # (the unbraked habitat: in-fighting's circumscription reads it)
        kept = np.ones(self.grid.n)
        lost = {}
        F = None
        self._refugee[k] = 0.0
        if self.tree.war > 0:
            wx = self.tree.war * PM.WAR_Q * self._war_era(step) * self._war_a[k]  # (meta.war x the era's dial x the people's own, PW-1172)
            era = self._era[k]  # (a farming or herding way before its people farms fights as foragers do; no way: its era's row)
            hw = PM.H_ERA["forager"] if era == "forager" and l.way not in ("fisher_forager", "sea_nomad") else \
                PM.H_WAY.get(l.way, PM.H_ERA.get(era, 0.0)) if l.way else PM.H_ERA.get(era, 0.0)
            if hw > 0 and wx > 0:
                F = self.rule.frontier(k)
                N = np.asarray(self.dens_at(k), float) * self.p[k]  # (people per km2 on each cell)
                G = self.rule.pacification(k, step)  # (a state's pacification: the stand-in, a farming people with the tech forms states)
                crowd2 = (N / PM.WAR_N0) ** 2
                h = wx * hw * (crowd2 * G + PM.WAR_EXT * F)
                h = h * self._troubles(l, k, wx * hw * (crowd2 + PM.WAR_EXT * F), held, N, step)
                kw = 1.0 - PM.LAND_Q * np.minimum(1.0, h / PM.H_MAX)
                kept *= kw
                lost["war"] = kw
                # (refugees, PW-1172: the share of its people war drives off this step, where its war-torn land now holds fewer than
                # live there, adds to its crowding: a people whose war flares (troubles, or crowding as it grows) sends people out; a
                # standing loss it has already settled under does not)
                pk = self.p[k] * held
                self._refugee[k] = float(np.maximum(0.0, pk - K * kw).sum() / max(float(pk.sum()), 1e-12))
            fx = self.tree.war * PM.FEUD_CUT * self.rule.circumscription(k)
            if fx > 0:  # (in-fighting, every people: lane 101, owner D31 "humans ought also be infighting")
                kf = 1.0 - np.minimum(1.0, fx * self._fill(k, K))
                kept *= kf
                lost["feud"] = kf
        rx = self.tree.raiders
        if rx > 0 and self._raider[k]:
            if F is None:
                F = self.rule.frontier(k)
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
            self.lost.pop(l.id, None)  # (nothing held off this step: no stale shares in the output)
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

    def _war_era(self, step) -> float:
        """E(lev): meta.war_early at tech level 0, meta.war_late at level 1, blended linearly by the era's tech level between (as
        megafauna.press_x blends the dragon-pressure pair; design.md (b))."""
        from . import megafauna as MG
        lev = min(max(MG.tech_level(self.tree.era, step.ago), 0.0), 1.0)
        a, b = self.tree.war_early, self.tree.war_late
        return float(a + (b - a) * lev)

    def _troubles(self, l, k, h_free, held, N, step) -> float:
        """Times of troubles (PW-1172; design.md (b), "Cycles"): Turchin 2009's ~200-300 year secular cycles are at the century step's
        Nyquist limit, so their story is kept as seeded one-step pulses. In the recent epoch a people whose crowded core would fight at
        TROUBLE_H or more were no state to keep the peace (h_free, the hazard with G = 1: Turchin's mechanism is a state too weak to
        hold its people down) falls into troubles with chance TROUBLE_SHARE x dt / TROUBLE_KYR a step (about the share of the time
        Turchin's decline phases take, params); that step its war hazard is
        x TROUBLE_X everywhere it lives. The multiplier on h this step (1 outside troubles)."""
        if step.epoch != "recent" or PM.TROUBLE_SHARE <= 0 or not held.any() or float(h_free[held].max()) < PM.TROUBLE_H:
            return 1.0
        rng = self.__dict__.setdefault("_trng", {}).get(l.id)
        if rng is None:  # (a generator of its own: the other draws of the line stay as they were)
            import zlib
            rng = self._trng[l.id] = np.random.default_rng((self.seed, 1172, zlib.crc32(l.id.encode())))
        if rng.random() >= min(1.0, PM.TROUBLE_SHARE * step.dt / PM.TROUBLE_KYR):
            return 1.0
        self.troubles_n[l.id] = self.troubles_n.get(l.id, 0) + 1
        last = self._trouble_log.get(k)
        if last is None or last - step.ago >= PM.TROUBLE_LOG_KYR:
            c = int(np.argmax(np.where(held, N, -1.0)))
            self._event_at(step.ago, "troubles", l, f"times of troubles among the {l.label()}: feuds, banditry and war in their "
                                                    f"crowded country; fields go unworked and people flee to strongholds", c)
            self._trouble_log[k] = step.ago
        return PM.TROUBLE_X

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
        hk = self.rule.hostility[k]
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
