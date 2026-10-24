"""Horses, the first domesticated animal (PW-688 part 1, the domestication epic PW-691).

No fauna is simulated (PW-184), so the wild horse's range is derived from the land: open temperate grassland
and steppe, as Equus on Earth (cool to mild, semi-arid to moist, little tree cover, not high mountains).
Nothing in it names Earth's continents or a species, so it works on any world and in either the real-world or
the fantasy mode of the planned switch (PW-695): "horses" are the grazing, rideable herd animal of open country.

One taming event picks, per run, a date (an anchor of `meta.horses_at`, 5.5 kyr ago after the Pontic-Caspian
steppe, with a lognormal jitter of ~20%) and a homeland: the first step from then on when a people with a herding
way of life (landuse.shares: the weight of the `grazing` good in its [[use]] rows, so nomads, herders and
steppe orcs) holds ground on the wild range. The landmass is drawn in proportion to herders x wild range there,
the cell likewise. The animal may be tamed again on another landmass later (a small rate per kyr while herders
sit on its wild range there and riding has not arrived); the first pass treats the result as one homogeneous stock.

Riding then spreads as a cultural front over peopled land (RIDE_KMYR km/yr; hops over unpeopled gaps cost
pressure, the sea stops it). A people's adoption is the presence-weighted share of its land where riding is
known, x its propensity (PROP: herders 1, farmers 0.15..0.4, fliers and swimmers and cave-dwellers 0). It:
  - speeds the people's spread over open land (speed x (1 + (HORSE_SPEED - 1) x adoption x open share)),
  - raises the capacity of grazing land for herding peoples (K x (1 + HORSE_GRAZE x adoption x grazing)),
  - and, in the land-use overlay (landuse.py), the land a herding person works (HERD_KM2 x (1 + HORSE_HERD x riding)).
"""

from __future__ import annotations

import numpy as np

from . import landuse as LU
from .spread import EST, rings, spread

ANCHOR_KYR = 5.5  # Pontic-Caspian steppe
JITTER, CLIP = 0.2, (0.7, 1.5)  # date: anchor x lognormal(0, 0.2), within 0.7..1.5
WILD_TEMP = (-4.0, 4.0, 20.0, 27.0)  # mean annual temperature C: rising, full, full, falling
WILD_RAIN = (120.0, 300.0, 1000.0, 1700.0)  # annual rain mm
WILD_TREES = (8.0, 35.0)  # tree cover %: full open below the first, none above the second
WILD_ELEV = (2800.0, 4500.0)  # high ground thins the range, cold plateaus and all (full below the first, none above)
WILD_MIN = 0.35  # a cell is in the wild range from this suitability
WILD_PATCH_MKM2 = 0.25  # a landmass needs this much range to count
HERD_MIN = 0.4  # a people with at least this herding share can tame
OVERLAP_MIN = 3  # cells where herders sit on the wild range
AGAIN_RATE = 0.06  # per kyr, per other landmass with herders on its wild range and no riding yet
RIDE_KMYR = 1.8  # the front of riding over peopled land, km/yr (Pontic steppe to the Altai in ~2 kyr)
RIDE_GAP = 0.8  # pressure kept per unpeopled cell crossed (a gap of ~10 cells still passes)
HORSE_SPEED = 2.5  # x the people's spread over open land at full adoption
HORSE_GRAZE = 0.3  # x(1 + this x adoption x grazing) on a herding people's capacity
CARRY_EVERY_KYR, CARRY_SHARE, CARRY_PROP = 0.5, 0.3, 0.3  # (a people riding over this share of its land, with this propensity, carries it)
TOOK_UP = 0.2  # a people has taken up riding when riding is known over this share of its land
NO_RIDERS = ("flies", "swims", "subterranean")  # (too big, too small or no ground to ride: not a rider's people)


def _win(x, e):
    a, b, c, d = e
    return np.clip(np.minimum((x - a) / (b - a), (d - x) / (d - c)), 0, 1)


def wild_range(env: dict, land: np.ndarray) -> np.ndarray:
    """The wild horse's suitability 0..1 per cell from an epoch's climate and cover (0 off the ice-free land)."""
    t, r = env["temperature"], env["precipitation"]
    tc = env.get("tree_cover", np.zeros(len(t)))
    elev = np.maximum(env["elevation"] - env["ice"], 0)
    open_ = np.clip((WILD_TREES[1] - tc) / (WILD_TREES[1] - WILD_TREES[0]), 0, 1)
    hi = np.clip((WILD_ELEV[1] - elev) / (WILD_ELEV[1] - WILD_ELEV[0]), 0, 1)
    return np.where(land, _win(t, WILD_TEMP) * _win(r, WILD_RAIN) * open_ * hi, 0.0)


def propensity(tree, l) -> float:
    """How readily a people takes up riding: herders 1, mixed ways between, farmers and others a little, 0 for
    peoples that fly, swim or live underground, and for sparse giants."""
    if l.overlay or any(t in l.traits for t in NO_RIDERS) or l.demo("density") < 0.05:
        return 0.0
    return float(np.clip(0.15 + 0.85 * LU.shares(tree, l)["herd"], 0, 1))


class Horses:
    def __init__(self, h):
        self.h = h
        tree = h.tree
        self.rng = np.random.default_rng((h.seed, 691))  # (its own stream: the peoples' draws are the same with or without)
        self.anchor = tree.horses_at if tree.horses_at is not None else ANCHOR_KYR
        self.d0 = float(np.clip(self.anchor * np.exp(JITTER * self.rng.standard_normal()), CLIP[0] * self.anchor, CLIP[1] * self.anchor))
        n = h.grid.n
        self.rd = np.zeros(n)  # where riding is known, 0..1
        self.wild = np.zeros(n)
        self.herd = np.array([LU.shares(tree, l)["herd"] if not l.overlay else 0.0 for l in h.lines])
        self.prop = np.array([propensity(tree, l) for l in h.lines])
        self.adopt = np.zeros(len(h.lines))
        self.open_share = np.zeros(len(h.lines))
        self.tamed: list[dict] = []
        self.share = np.zeros(len(h.lines))  # of a line's land, the share where riding is known
        self.carry_dt = 0.0
        self.took_up: dict[int, float] = {}  # line index -> when riding reached a fifth of its land
        self.budget = 0.0
        self.why_not = None

    # -- per step -----------------------------------------------------------------------------------
    def step(self, step, env, tags, p, native) -> None:
        """Update the wild range, taming and the riding front for a step (after the epoch's tags, before the peoples move)."""
        if step.epoch == "deep":
            return
        h = self.h
        self.wild = wild_range(env, tags["land"])
        self.climate = env["climate"]
        peopled = (p[native] >= EST).any(0)
        if step.ago <= self.d0 + 1e-9:
            if not self.tamed:
                self._tame(step, p, peopled, first=True)
            else:
                self._tame(step, p, peopled, first=False)
        if self.tamed:
            self._ride(step, env, tags, peopled)
            self.carry_dt += step.dt
            if self.carry_dt >= CARRY_EVERY_KYR:
                self._carry(p)
                self.carry_dt = 0.0
        # adoption by line: the share of its land where riding is known x its propensity
        open_c = tags["open"].astype(float)
        for k in range(len(h.lines)):
            if self.prop[k] <= 0:
                continue
            w = np.where(p[k] >= EST, p[k], 0.0)
            tot = w.sum()
            if tot <= 0 or not self.tamed:
                self.adopt[k] = self.open_share[k] = 0.0
                continue
            self.share[k] = float((w * self.rd).sum() / tot)
            self.adopt[k] = self.share[k] * self.prop[k]
            self.open_share[k] = float((w * open_c).sum() / tot)
            if self.adopt[k] >= TOOK_UP * self.prop[k] and k not in self.took_up:
                self.took_up[k] = round(step.ago, 3)

    def _tame(self, step, p, peopled, first: bool) -> None:
        h = self.h
        herders = [k for k in range(len(h.lines)) if self.herd[k] >= HERD_MIN and self.prop[k] > 0 and h.active[h.lines[k].id]]
        if not herders:
            return
        H = np.max([np.where(p[k] >= 0.25, p[k], 0.0) for k in herders], axis=0)
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
        if first:
            if not ok.any():
                return
            m = int(self.rng.choice(len(by_land), p=np.where(ok, by_land, 0) / np.where(ok, by_land, 0).sum()))
        else:
            seeded = {t["landmass"] for t in self.tamed}
            has_riding = np.bincount(lab[(self.rd >= EST) & (lab >= 0)], minlength=len(by_land)) > 0
            ok &= ~has_riding
            for t in seeded:
                if t < len(ok):
                    ok[t] = False
            if not ok.any():
                return
            if self.rng.random() >= 1 - np.exp(-AGAIN_RATE * step.dt * ok.sum()):
                return
            m = int(self.rng.choice(len(by_land), p=np.where(ok, by_land, 0) / np.where(ok, by_land, 0).sum()))
        pick = np.where(cand & (lab == m), score, 0.0)
        cell = int(self.rng.choice(len(pick), p=pick / pick.sum()))
        blob = rings(cell, (self.wild > 0) | peopled, 2, h.grid.nbr_off, h.grid.nbr_idx) & peopled
        blob[cell] = True
        self.rd[blob] = 1.0
        near = rings(cell, np.ones(len(H), bool), 3, h.grid.nbr_off, h.grid.nbr_idx)
        who = max(herders, key=lambda k: float(p[k][near].sum()))
        cl = h.cross.names[m]["name"] if m < len(h.cross.names) else "?"
        steppe = float(np.isin(self.climate[wild & (lab == m)].astype(int), (5, 6)).mean())
        self.tamed.append({"ago_kyr": round(step.ago, 3), "lat": round(float(h.grid.lat[cell]), 2), "lon": round(float(h.grid.lon[cell]), 2),
                           "landmass": m, "landmass_name": cl, "line": h.lines[who].id, "people": h.lines[who].label(),
                           "country": "steppe" if steppe >= 0.4 else "open grassland", "first": first,
                           "wild_mkm2": round(float(wild_area[m]), 2)})
        h.events.append({"ago_kyr": round(step.ago, 3), "kind": "horses", "line": h.lines[who].id,
                         "text": f"horses are {'tamed' if first else 'tamed again, on their own,'} by the {h.lines[who].label()} on the "
                                 f"{self.tamed[-1]['country']} of {cl}", "lat": self.tamed[-1]["lat"], "lon": self.tamed[-1]["lon"]})

    def _carry(self, p) -> None:
        """A people that rides takes it with it: a patch of its land that riding has not reached (settled over the sea,
        or past a gap the front cannot cross) rides too, as the horses and riders came along."""
        g = self.h.grid
        for k in np.flatnonzero((self.share >= CARRY_SHARE) & (self.prop >= CARRY_PROP)):
            held = p[k] >= EST
            lab, n = g.components(held)
            if n < 2:
                continue
            has = np.zeros(n, bool)
            has[np.unique(lab[held & (self.rd >= EST)])] = True
            new = held & ~has[np.maximum(lab, 0)]
            self.rd[new] = 1.0

    def _ride(self, step, env, tags, peopled) -> None:
        """The front of riding: one ring per pass over peopled land, a gap of unpeopled land costs RIDE_GAP per cell."""
        h = self.h
        self.budget += RIDE_KMYR * step.dt * 1000 / h.cell_km
        passes = int(self.budget)
        self.budget -= passes
        if passes <= 0:
            return
        enter = np.where(peopled, 1.0, RIDE_GAP)
        room = np.where(peopled, 1.0, 0.0)
        spread(self.rd, room, enter, tags["elev"], 0.3, 0.0, env["land"], h.grid.nbr_off, h.grid.nbr_idx, passes)
        self.rd[self.rd >= EST] = 1.0

    # -- what riding does ---------------------------------------------------------------------------
    def speed_mult(self, k: int) -> float:
        return 1.0 + (HORSE_SPEED - 1.0) * self.adopt[k] * self.open_share[k]

    def k_mult(self, k: int) -> np.ndarray | float:
        if self.adopt[k] <= 0 or self.herd[k] <= 0:
            return 1.0
        g = self.h.goods
        graze = g["grazing"] if g is not None and "grazing" in g else np.clip(self.wild * 1.5, 0, 1)
        return 1.0 + HORSE_GRAZE * self.adopt[k] * self.herd[k] * graze * (self.rd >= EST)

    # -- results ------------------------------------------------------------------------------------
    def frame_layers(self) -> dict:
        return {"horse_wild": np.round(self.wild * 100).astype(np.uint8), "horse_riding": np.round(self.rd * 100).astype(np.uint8)}

    def summary(self, P: np.ndarray) -> dict:
        h = self.h
        lab = h.cross.label
        wild = self.wild >= WILD_MIN
        riders = {}
        for k, l in enumerate(h.lines):
            if self.prop[k] > 0 and (P[k] >= EST).any():
                w = np.where(P[k] >= EST, P[k], 0.0)
                riders[l.id] = round(float((w * self.rd).sum() / w.sum()), 3)
        return {"enabled": True, "date_drawn_kyr": round(self.d0, 3), "anchor_kyr": self.anchor, "tamed": self.tamed,
                "wild_mkm2": round(float(wild.sum() * h.cell_mkm2), 2),
                "riding_mkm2": round(float((self.rd >= EST).sum() * h.cell_mkm2), 2),
                "riding_on_wild_mkm2": round(float(((self.rd >= EST) & wild).sum() * h.cell_mkm2), 2),
                "never": None if self.tamed else "no herding people held ground on the wild range after the drawn date",
                "propensity": {l.id: round(float(self.prop[k]), 2) for k, l in enumerate(h.lines) if self.prop[k] > 0},
                "riders_share": riders, "took_up_kyr": {h.lines[k].id: v for k, v in self.took_up.items()},
                "adoption": {l.id: round(float(self.adopt[k]), 3) for k, l in enumerate(h.lines) if self.adopt[k] > 0}}
