"""Domesticated animals (PW-691): horses, dogs, sheep and goats, cattle, fowl and the rare fantasy mounts, and the
boats that carry them over the sea (PW-688 part 2). The animals' constants are one table, `animal_defs.TABLE`.

No fauna is simulated (PW-184), so each wild range is derived from the land (animal_defs.wild_*), and nothing in it
names Earth or a species: it works on any world and in either the real-world or the fantasy mode (PW-695), where the
fantasy rows (great elk, riding lizards) are rare, off by default and forceable for tests (PW-710).

Per animal, one taming event picks a date per run (the table's anchor with a lognormal jitter of ~20%) and a homeland:
the first step from then on when a people that can tame it (animal.tame: weights on its farm / herd / forage shares)
holds ground on the wild range of a landmass with enough of it. The landmass is drawn in proportion to tamers x wild
range there, the cell likewise. It may be tamed again on another landmass later (a small rate per kyr while tamers sit
on its wild range there and its use has not arrived); the first pass treats each animal as one homogeneous stock.

Its use then spreads as a cultural front over peopled land (the table's km/yr; hops over unpeopled gaps cost pressure,
the sea stops it) and over the sea only in boats able to carry it: `animal_defs.craft_ladder` (canoes, planked boats,
sailing ships, with dates, reaches and the sea share of a people that mans them). Every 0.5 kyr a land that has the animal and a
people with the sea share for a big enough craft may land it, by chance, on a peopled coast of a landmass without it
within the craft's reach (rate falling with the gap); the front then goes on from there. A people's adoption is the
presence-weighted share of its land where the animal is known x its propensity (animal.prop_floor + its shares x
animal.prop; fliers, swimmers, cave-dwellers and sparse giants as the table says). It:
  - speeds the people's spread (speed x (1 + (speed - 1) x adoption [x open share])),
  - raises the capacity of its grazing, foraging or farm land (K x (1 + frac x adoption x share)),
  - and, in the land-use overlay (landuse.py), the land a herder or farmer works.
"""

from __future__ import annotations

import numpy as np

from . import landuse as LU
from .animal_defs import BY_ID, Animal, craft_for, craft_ladder, resolve
from .crossing import sea_gap
from .spread import EST, rings, spread

JITTER, CLIP = 0.2, (0.7, 1.5)  # date: anchor x lognormal(0, 0.2), within 0.7..1.5
CROP_RANGE_KYR = 0.5  # a crop's wild and grown ranges are worked out again after this long (they follow the climate)
GROW_WIDEN = 0.6  # a crop is grown past its wild range: its climate windows widened by this share of their ramps
HOME_PENALTY = 1.0  # x per other first domestication on the landmass (crops: several homelands per world)
WILD_MIN = 0.35  # a cell is in the wild range from this suitability
WILD_PATCH_MKM2 = 0.25  # a landmass needs this much range to count
OVERLAP_MIN = 3  # cells where tamers sit on the wild range
TOOK_UP = 0.2  # a people has taken up an animal when it is known over this share of its land
CONTACT_KMYR = 8.0  # the front of an `uptake = "contact"` animal, km/yr: about ten times the peoples' own expansion (0.5-0.8 km/yr), a mount is adopted on meeting
BARRIER_ENTER = 0.8  # contact animals: pressure kept per peopled cell outside the wild range (a belt of ~3 cells of forest or high ground stops it)
BOAT_EVERY_KYR = 0.5  # how often the crossings are tried
BOAT_RATE = 0.6  # per kyr at no gap, per landmass, for a people with a sea share of 0.6 (scaled by share / 0.6)
BOAT_FULL = 0.6
BOAT_KEEP = 40  # crossings listed per animal in the summary


class Stock:
    """One animal's state: where it is known (`rd`, 0..1), its wild range, the tamings and the crossings."""

    def __init__(self, h, a: Animal, force: bool, anchors: dict | None = None, owner=None):
        self.h, self.a, self.owner = h, a, owner
        tree = h.tree
        self.rng = np.random.default_rng((h.seed, 721, a.bit) if a.plant else (h.seed, 691) if a.bit == 0 else (h.seed, 691, a.bit))  # (own stream: the peoples' draws stay the same)
        self.anchor = (tree.animals_at if anchors is None else anchors).get(a.id, a.anchor_kyr)
        self.d0 = float(np.clip(self.anchor * np.exp(JITTER * self.rng.standard_normal()), CLIP[0] * self.anchor, CLIP[1] * self.anchor))
        self.absent = bool(a.fantasy and not force and self.rng.random() >= a.rare)  # (a rare taming that this world does not have)
        n = h.grid.n
        self.rd = np.zeros(n)
        self.route = np.zeros(n, np.uint8)  # how each cell came to know it (PW-742): 1 first taming (origin), 2 the land front (road), 3 a boat crossing (sea)
        self.wild = np.zeros(n)
        L = len(h.lines)
        sh = np.array([[*[LU.shares(tree, l)[k] for k in ("farm", "herd", "wood", "forage", "gather")]] if not l.overlay else [0.0] * 5 for l in h.lines]).reshape(L, 5)
        self.sh = {"farm": sh[:, 0], "herd": sh[:, 1], "forage": sh[:, 3], "gather": sh[:, 4]}  # (forage: the foraging use or the hunter trait, PW-718)
        self.grow = np.zeros(n)
        self.gk = np.zeros(n)
        self._range_age, self._ranged = 0.0, False
        self.tamer = sum(w * self.sh[k] for k, w in a.tame.items())
        self.prop = np.array([self._propensity(l, i) for i, l in enumerate(h.lines)])
        self.adopt = np.zeros(L)
        self.share = np.zeros(L)
        self.tamed: list[dict] = []
        self.crossings: list[dict] = []
        self.landed: set[int] = set()
        self.took_up: dict[int, float] = {}
        self.budget = 0.0
        self.boat_dt = 0.0
        self.n_crossed = 0
        self.reached: dict[int, float] = {}  # landmass -> when (kyr ago) its use first reached it

    def _propensity(self, l, i) -> float:
        a = self.a
        if l.overlay or any(t in l.traits for t in a.excl) or l.megafauna:
            return 0.0
        return float(np.clip(a.prop_floor + sum(w * self.sh[k][i] for k, w in a.prop.items()), 0, 1))

    # -- per step -----------------------------------------------------------------------------------
    def step(self, step, env, tags, p, native, sea, peopled=None) -> None:
        """Update the wild range, taming, the front and the sea crossings for a step (after the epoch's tags, before the peoples move).
        peopled: the cells any people holds (the same for every stock of a step: Animals.step makes it once)."""
        if not self.a.plant:
            self.wild = self.a.wild(env, tags, tags["land"])
        elif self._range_age + step.dt >= CROP_RANGE_KYR or not self._ranged:  # (a crop's range follows the climate slowly: every 0.5 kyr, not every step)
            self.wild = self.a.wild(env, tags, tags["land"])
            self.grow = self.a.wild(env, tags, tags["land"], widen=GROW_WIDEN)  # (where it can be grown: past its wild range)
            self._range_age, self._ranged = 0.0, True
        else:
            self._range_age += step.dt
        self.climate = env["climate"]
        if self.absent:
            return
        if peopled is None:
            peopled = (p[native] >= EST).any(0)
        if step.ago <= self.d0 + 1e-9:
            self._tame(step, p, peopled, first=not self.tamed)
        if self.tamed:
            self._front(step, env, tags, peopled)
            self.boat_dt += step.dt
            if self.boat_dt >= BOAT_EVERY_KYR:
                self._sail(step, env, tags, p, peopled, sea, self.boat_dt)
                self.boat_dt = 0.0
            lab = self.h.cross.label  # (the present's landmasses, as the summary names them: the step's own land components are numbered
            for c in np.unique(lab[(self.rd >= EST) & (lab >= 0)]):  # otherwise, and a glacial bridge's merged label read as another landmass, lane 73)
                self.reached.setdefault(int(c), round(step.ago, 3))

    def _tame(self, step, p, peopled, first: bool) -> None:
        h, a = self.h, self.a
        tamers = [k for k in range(len(h.lines)) if self.tamer[k] >= a.tame_min and self.prop[k] > 0 and h.active[h.lines[k].id]]
        if not tamers:
            return
        H = np.max([np.where(p[k] >= 0.25, p[k], 0.0) for k in tamers], axis=0)
        wild = self.wild >= WILD_MIN
        lab = h.cross.label
        cand = wild & (H > 0) & (lab >= 0)
        if not cand.any():
            return
        score = np.where(cand, self.wild * H, 0.0)
        by_land = np.bincount(lab[cand], weights=score[cand], minlength=int(lab.max()) + 1)
        n_over = np.bincount(lab[cand], minlength=len(by_land))
        wild_area = np.bincount(lab[wild & (lab >= 0)], minlength=len(by_land)) * h.cell_mkm2
        ok = (n_over >= OVERLAP_MIN) & (wild_area >= WILD_PATCH_MKM2)
        pen = getattr(self.owner, "penalty", HOME_PENALTY)
        if pen != 1.0 and first:  # (several homelands: a landmass that already has a first domestication is less likely again)
            by_land = by_land * pen ** np.array([self.owner.homes.get(i, 0) for i in range(len(by_land))])
        if first:
            if not ok.any():
                return
        else:
            seeded = {t["landmass"] for t in self.tamed}
            has_use = np.bincount(lab[(self.rd >= EST) & (lab >= 0)], minlength=len(by_land)) > 0
            ok &= ~has_use
            for t in seeded:
                if t < len(ok):
                    ok[t] = False
            if not ok.any():
                return
            if self.rng.random() >= 1 - np.exp(-a.again * step.dt * ok.sum()):
                return
        m = int(self.rng.choice(len(by_land), p=np.where(ok, by_land, 0) / np.where(ok, by_land, 0).sum()))
        pick = np.where(cand & (lab == m), score, 0.0)
        cell = int(self.rng.choice(len(pick), p=pick / pick.sum()))
        blob = rings(cell, (self.wild > 0) | peopled, 2, h.grid.nbr_off, h.grid.nbr_idx) & peopled
        blob[cell] = True
        self.route[blob & (self.rd < EST)] = 1
        self.rd[blob] = 1.0
        near = rings(cell, np.ones(len(H), bool), 3, h.grid.nbr_off, h.grid.nbr_idx)
        who = max(tamers, key=lambda k: float(p[k][near].sum()))
        cl = h.cross.names[m]["name"] if m < len(h.cross.names) else "?"
        steppe = float(np.isin(self.climate[wild & (lab == m)].astype(int), (5, 6)).mean())
        self.tamed.append({"ago_kyr": round(step.ago, 3), "lat": round(float(h.grid.lat[cell]), 2), "lon": round(float(h.grid.lon[cell]), 2),
                           "landmass": m, "landmass_name": cl, "line": h.lines[who].id, "people": h.lines[who].label(),
                           "country": "steppe" if steppe >= 0.4 else "open grassland" if a.id == "horse" else "wild country", "first": first,
                           "wild_mkm2": round(float(wild_area[m]), 2)})
        self.landed.add(m)
        if first and self.owner is not None:
            self.owner.homes[m] = self.owner.homes.get(m, 0) + 1
        h.events.append({"ago_kyr": round(step.ago, 3), "kind": "crops" if a.plant else "animals", "line": h.lines[who].id,
                         "text": f"{a.label} are {a.deed if first else a.deed.replace('first ', '') + ' again, on their own,'} by the {h.lines[who].label()} "
                                 f"{'on the ' + self.tamed[-1]['country'] + ' of' if a.id == 'horse' else 'on'} {cl}",
                         "lat": self.tamed[-1]["lat"], "lon": self.tamed[-1]["lon"]})

    def _front(self, step, env, tags, peopled) -> None:
        """The front of use: one ring per pass over peopled land, a gap of unpeopled land costs `gap` per cell."""
        h = self.h
        contact = self.a.uptake == "contact"
        self.budget += (CONTACT_KMYR if contact else self.a.front_kmyr) * step.dt * 1000 / h.cell_km
        passes = int(self.budget)
        self.budget -= passes
        if passes <= 0:
            return
        enter = np.where(peopled, BARRIER_ENTER if contact else 1.0, self.a.gap)
        if contact:
            enter = np.where(peopled & (self.wild >= WILD_MIN), 1.0, enter)
        room = np.where(peopled, 1.0, 0.0)
        before = self.rd >= EST
        spread(self.rd, room, enter, tags["elev"], 0.3, 0.0, env["land"], h.grid.nbr_off, h.grid.nbr_idx, passes)
        self.route[(self.rd >= EST) & ~before] = 2
        self.rd[self.rd >= EST] = 1.0

    def _sail(self, step, env, tags, p, peopled, sea, dt) -> None:
        """Crossings by boat: from a coast where the animal is known and a people with the sea share for a craft that carries
        it holds ground, to a peopled cell of a landmass (of this epoch) without the animal, within the craft's reach."""
        craft = craft_for(self.a.size, step.ago)
        if craft is None:
            return
        name, reach, need = craft
        h = self.h
        crew = [int(k) for k in h._native if sea[k] >= need]
        if not crew:
            return
        known = self.rd >= EST
        manned = (p[crew] >= EST).any(0)
        src = known & tags["coast"] & manned
        if not src.any():
            return
        strength = min(1.0, float(max(sea[k] for k in crew if (p[k][src] >= EST).any())) / BOAT_FULL)
        lab = tags["label"]
        has = np.unique(lab[known & (lab >= 0)])
        land = env["land"]
        d = sea_gap(src, land, h.grid.nbr_off, h.grid.nbr_idx, int(reach / h.cell_km) + 1)
        cand = peopled & ~known & (d > 0) & (lab >= 0) & ~np.isin(lab, has)
        if not cand.any():
            return
        km = d * h.cell_km
        for c in np.unique(lab[cand]):
            sel = cand & (lab == c)
            if km[sel].min() > reach:
                continue
            cell = int(np.flatnonzero(sel)[np.argmin(km[sel])])
            lam = BOAT_RATE * strength * dt * np.exp(-km[cell] / (reach / 2.0))
            if self.rng.random() >= 1 - np.exp(-lam):
                continue
            blob = rings(cell, peopled, 2, h.grid.nbr_off, h.grid.nbr_idx) & peopled
            blob[cell] = True
            self.route[blob & (self.rd < EST)] = 3
            self.rd[blob] = 1.0
            self.n_crossed += 1
            pl = int(h.cross.label[cell])
            rec = {"ago_kyr": round(step.ago, 3), "landmass": pl, "landmass_name": h.cross.names[pl]["name"] if pl >= 0 else "?",
                   "craft": name, "gap_km": round(float(km[cell]))}
            if len(self.crossings) < BOAT_KEEP:
                self.crossings.append(rec)
            if pl >= 0 and pl not in self.landed and h.cross.names[pl]["area_mkm2"] >= 0.05:
                self.landed.add(pl)
                h.events.append({"ago_kyr": rec["ago_kyr"], "kind": "crops" if self.a.plant else "animals", "line": None,
                                 "text": f"{self.a.label} cross the sea to {rec['landmass_name']} in {'an' if name[0] in 'aeiou' else 'a'} {name} "
                                         f"({rec['gap_km']} km of open sea)", "lat": round(float(h.grid.lat[cell]), 2), "lon": round(float(h.grid.lon[cell]), 2)})

    # -- results ------------------------------------------------------------------------------------
    def summary(self, P: np.ndarray, pres_open: float = 0.0) -> dict:
        h, a = self.h, self.a
        wild = self.wild >= WILD_MIN
        riders = {}
        for k, l in enumerate(h.lines):
            if self.prop[k] > 0 and (P[k] >= EST).any():
                w = np.where(P[k] >= EST, P[k], 0.0)
                riders[l.id] = round(float((w * self.rd).sum() / w.sum()), 3)
        never = None
        if self.absent:
            never = "a rare taming this world does not have"
        elif not self.tamed:
            never = "no people that can tame it held ground on its wild range after the drawn date"
        return {"enabled": True, "label": a.label, "noun": a.noun, "bit": a.bit, "fantasy": a.fantasy, "size": a.size, "plant": a.plant, "deed": a.deed,
                "date_drawn_kyr": round(self.d0, 3), "anchor_kyr": self.anchor, "tamed": self.tamed,
                "wild_mkm2": round(float(wild.sum() * h.cell_mkm2), 2),
                "known_mkm2": round(float((self.rd >= EST).sum() * h.cell_mkm2), 2),
                "known_on_wild_mkm2": round(float(((self.rd >= EST) & wild).sum() * h.cell_mkm2), 2),
                "reached_kyr": {h.cross.names[c]["name"]: v for c, v in self.reached.items() if c < len(h.cross.names) and h.cross.names[c]["area_mkm2"] >= 0.05},
                "never": never, "crossed": self.n_crossed, "crossings": self.crossings,
                "propensity": {l.id: round(float(self.prop[k]), 2) for k, l in enumerate(h.lines) if self.prop[k] > 0},
                "users_share": riders, "took_up_kyr": {h.lines[k].id: v for k, v in self.took_up.items()},
                "adoption": {l.id: round(float(self.adopt[k]), 3) for k, l in enumerate(h.lines) if self.adopt[k] > 0}}


class Animals:
    def __init__(self, h):
        self.h = h
        tree = h.tree
        self.homes: dict[int, int] = {}  # landmass -> first domestications on it (crops.py spreads the homelands)
        self.stocks = self._make(tree)
        self.ago = 0.0
        L = len(h.lines)
        self.open_share = np.zeros(L)
        self.speed = np.ones(L)
        self.sea = np.array([l.demo("sea_share") for l in h.lines])

    def _make(self, tree) -> list:
        return [Stock(self.h, a, a.id in tree.animals_force, None, self) for a in resolve(tree.animals, tree.animals_force, tree.mode)]

    def step(self, step, env, tags, p, native) -> None:
        if step.epoch == "deep":
            return
        self.ago = step.ago
        pn = p[native]
        held = pn >= EST
        peopled = held.any(0)
        for s in self.stocks:
            s.step(step, env, tags, p, native, self.sea, peopled)
        # adoption by line: the share of its land where the animal is known x its propensity (one matrix product)
        W = np.where(held, pn, 0.0)
        tot = W.sum(1)
        ok = tot > 0
        den = np.where(ok, tot, 1.0)
        self.open_share[:] = 0.0
        self.open_share[native] = np.where(ok, W @ tags["open"].astype(float) / den, 0.0)
        RD = np.stack([s.rd for s in self.stocks]) if self.stocks else np.zeros((0, W.shape[1]))
        sh = (W @ RD.T) / den[:, None] if len(RD) else np.zeros((len(native), 0))
        self.speed[:] = 1.0
        for j, s in enumerate(self.stocks):
            s.share[:] = 0.0
            s.share[native] = np.where(ok, sh[:, j], 0.0)
            s.adopt[:] = s.share * s.prop
            a = s.a
            if a.speed != 1.0:
                self.speed *= 1.0 + (a.speed - 1.0) * s.adopt * (self.open_share if a.speed_open else 1.0)
            for k in np.flatnonzero(s.adopt >= TOOK_UP * s.prop) if s.tamed else []:
                if s.prop[k] > 0 and int(k) not in s.took_up:
                    s.took_up[int(k)] = round(step.ago, 3)

    # -- what the animals do ------------------------------------------------------------------------
    def speed_mult(self, k: int) -> float:
        return float(self.speed[k])

    def herding(self, k: int) -> float:
        """How far the line keeps herds (0..1): the best adoption among the animals that carry a herd (a.k 'herd': sheep, goats,
        cattle, horses...), so a people with no domestic herd known has none to press with (PW-756)."""
        return float(max([s.adopt[k] for s in self.stocks if "herd" in s.a.k] or [0.0]))

    def k_mult(self, k: int):
        out = None
        graze = None
        for s in self.stocks:
            if s.adopt[k] <= 0:
                continue
            a = s.a
            fr = dict(a.k)
            if a.plough and self.ago <= a.plough[0]:
                fr["farm"] = fr.get("farm", 0.0) + a.plough[1]
            if not fr:
                continue
            terms = 0.0
            for key, f in fr.items():
                share = s.sh[key][k]
                if share <= 0:
                    continue
                if key == "herd":
                    if graze is None:
                        g = self.h.goods
                        graze = g["grazing"] if g is not None and "grazing" in g else np.clip(s.wild * 1.5, 0, 1)
                    terms = terms + f * share * graze
                else:
                    terms = terms + f * share
            if np.any(terms):
                add = s.adopt[k] * terms * (s.rd >= EST)
                out = 1.0 + add if out is None else out + add
        return 1.0 if out is None else out

    # -- results ------------------------------------------------------------------------------------
    def frame_layers(self) -> dict:
        n = self.h.grid.n
        known, wild = np.zeros(n, np.uint8), np.zeros(n, np.uint8)
        for s in self.stocks:
            known |= ((s.rd >= EST) * (1 << s.a.bit)).astype(np.uint8)
            wild |= ((s.wild >= WILD_MIN) * (1 << s.a.bit)).astype(np.uint8)
        return {"animal_known": known, "animal_wild": wild}

    def summary(self, P: np.ndarray) -> dict:
        h = self.h
        stocks = {s.a.id: s.summary(P) for s in self.stocks}
        # dairy (PW-784): which dairy animals a people keeps (known on its land) x its way of life (herders milk, by their herd share; so do peoples with lactase)
        # unless its body says `milks = false`; the lactase share (body.milk) only decides fresh milk or fermented (brief.py)
        dairy = {}
        for k, l in enumerate(h.lines):
            f = l.body.get("milk")
            lac = 1.0 if f is True else float(f or 0.0)
            herd = float(self.stocks[0].sh["herd"][k]) if self.stocks else 0.0
            milks = max(herd, lac)  # (herders milk by their herd share; a people with lactase milks, that is how it came to have it)
            if l.overlay or not l.body.get("milks", True) or milks <= 0:
                continue
            best = [(s.share[k], s.a.id) for s in self.stocks if s.a.dairy and s.share[k] > 0.05]
            if best:
                dairy[l.id] = {"lactase_share": round(lac, 2), "milks_share": round(milks, 2), "animals": [i for _, i in sorted(best, reverse=True)],
                               "dairy_share": round(milks * max(b for b, _ in best), 3)}
        return {"mode": h.tree.mode, "stocks": stocks, "dairy": dairy,
                "craft": [{"name": n, "since_kyr": s, "reach_km": r, "carries_up_to": ["people only", "dogs and fowl", "sheep, goats", "horses and cattle"][b + 1], "sea_share_needed": need}
                          for n, s, r, b, need in craft_ladder()]}
