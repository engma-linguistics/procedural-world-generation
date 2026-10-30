"""A line's habitat: capacity K from its niche, the land's goods and wishes, and how peoples overlap."""

from __future__ import annotations

import numpy as np

from .. import spec as SP
from ..spread import EST, graph_dist
from .params import EDGE_C, EDGE_ELEV_M, EDGE_OCT, HOLOCENE_KYR, MEGAFAUNA_OFF, NEAR_KM, TOLERATE_K, NEAR_ORIGIN, NEAR_ORIGIN_KM, NEAR_RANGE
from .gridops import _isin, _soft
from .tags import _tags
from . import params as PM


def _land_view(env: dict, tags: dict) -> dict:
    """An epoch's inputs on its ice-free land cells only, built once per epoch (the habitat is 0 elsewhere)."""
    v = tags.get("_land_view")
    if v is None:
        li = np.flatnonzero(tags["land"])
        v = tags["_land_view"] = {"li": li, "temp": env["temperature"][li],
                                  "lr": np.log2(np.maximum(env["precipitation"][li], 1.0)),
                                  "elev": tags["elev"][li], "cl": env["climate"][li].astype(int), "has": {}}
    return v


def _fit(line: SP.Lineage, v: dict, edge: bool = False) -> np.ndarray:
    """How well the land cells' climate (and height) fits a line's comfort range, 0..1, soft-edged; edge (PW-1024, megafauna's
    tolerated tier and ecological release): the range widened by EDGE_C, EDGE_OCT and EDGE_ELEV_M on both sides."""
    w = line.trait("widen", 1.0)
    dc, do, de = (EDGE_C, EDGE_OCT, EDGE_ELEV_M) if edge else (0.0, 0.0, 0.0)
    lo, hi = line.temp_c
    mid, half = (lo + hi) / 2, (hi - lo) / 2 * w + dc
    K = _soft(v["temp"], mid - half, mid + half, 4.0 * w)
    rlo, rhi = line.rain_mm
    K = K * _soft(v["lr"], np.log2(max(rlo, 1)) - (w - 1) - do, np.log2(max(rhi, 1)) + (w - 1) + do, 1.0 * w)
    if line.elev_m:
        K = K * _soft(v["elev"], line.elev_m[0] - de, line.elev_m[1] + de, 600.0 * w)
    return K


def edge_fit(line: SP.Lineage, env: dict, tags: dict) -> np.ndarray:
    """_fit(edge=True) on the whole grid (0 off the land): the climate a megafauna kind can live in at the edges (ecological release)."""
    v = _land_view(env, tags)
    out = np.zeros(len(tags["land"]))
    out[v["li"]] = _fit(line, v, edge=True)
    return out


def capacity(line: SP.Lineage, env: dict, tags: dict) -> np.ndarray:
    """Carrying capacity K in [0, 1] of a line's own habitat (worked out on the land cells only; a marine line's, on its
    realm's sea cells, marine_capacity)."""
    if line.marine:
        return marine_capacity(line, env, tags)
    v = _land_view(env, tags)
    li = v["li"]
    K = _fit(line, v)

    def has(tag):
        m = v["has"].get(tag)
        if m is None:
            if tag in SP.PLACES:
                m = tags[tag][li]
            else:
                m = _isin(v["cl"], SP.GROUPS.get(tag) or [SP.KOPPEN_CODES.index(tag)])
            v["has"][tag] = m
        return m

    if line.prefers:
        match = np.zeros(len(K), bool)
        for t in line.prefers:
            match |= has(t)
        K = K * np.where(match, 1.0, MEGAFAUNA_OFF if line.megafauna else 0.4)
        if line.tolerates and line.megafauna:  # (PW-1024: the edge tier, the better of the two: never lowers the own country)
            tol = match.copy()
            for t in line.tolerates:
                tol |= has(t)
            K = np.maximum(K, TOLERATE_K * np.where(tol, _fit(line, v, edge=True), 0.0))
    for t in line.avoids:
        K = K * np.where(has(t), 0.25, 1.0)
    cb = line.trait("coast", 0.0)
    if cb:
        K = K * np.where(has("coast"), 1.0, 1.0 - cb)
    mb = line.trait("mountain", 0.0)
    if mb:
        K = K * np.where(has("mountain"), 1.0, 1.0 - mb)
    ob = line.trait("open", 0.0)
    if ob:
        K = K * np.where(has("open"), 1.0, 1.0 - ob)
    out = np.zeros(len(tags["land"]))
    out[li] = np.clip(K, 0, 1)
    return out


def hold_mask(line: SP.Lineage, tags: dict) -> np.ndarray:
    """The cells a line can hold at all: its realm's (land: the ice-free land; coast: the sea cells next to land, the shelf
    and tidal flats; sea: every sea cell)."""
    return tags["shore"] if line.realm == "coast" else tags["sea"] if line.realm == "sea" else tags["land"]


def marine_capacity(line: SP.Lineage, env: dict, tags: dict) -> np.ndarray:
    """K in [0, 1] of a marine line (PW-775) on its realm's cells: the water temperature (env temperature at sea) within the
    line's comfort range, and, if it gives `elev_m`, the depth band (negative metres: [-200, 0] a shelf people). Rain, prefers and
    avoids do not apply: a coast line holds the shore ring (the habitat is data: its temp_c and elev_m)."""
    li = np.flatnonzero(hold_mask(line, tags))
    w = line.trait("widen", 1.0)
    lo, hi = line.temp_c
    mid, half = (lo + hi) / 2, (hi - lo) / 2 * w
    K = _soft(env["temperature"][li], mid - half, mid + half, 4.0 * w)
    if line.elev_m:
        K = K * _soft(env["elevation"][li], line.elev_m[0], line.elev_m[1], 600.0 * w)
    out = np.zeros(len(tags["land"]))
    out[li] = np.clip(K, 0, 1)
    return out


WAYS = ("flies", "swims", "mountain", "coastal", "subterranean")


def same_way(a: SP.Lineage, b: SP.Lineage) -> float:
    """How alike two lines use the land (1: the same way of life; x0.5 per difference in WAYS): territorial
    exclusion in closed country acts between peoples who would hold the same ground."""
    return float(0.5 ** sum((t in a.traits) != (t in b.traits) for t in WAYS))


def niche_overlap(a: SP.Lineage, b: SP.Lineage, tree: SP.Tree) -> float:
    """Competition between two lines: shared comfort ranges and ways of life, closer kin harder."""
    def ov(x, y, log=False):
        f = np.log2 if log else (lambda v: v)
        x0, x1, y0, y1 = f(max(x[0], 1e-3)), f(x[1]), f(max(y[0], 1e-3)), f(y[1])
        inter = max(0.0, min(x1, y1) - max(x0, y0))
        return inter / max(min(x1 - x0, y1 - y0), 1e-6) if inter > 0 else 0.0
    o = (0.2 + 0.8 * ov(a.temp_c, b.temp_c)) * (0.3 + 0.7 * ov(a.rain_mm, b.rain_mm, True))
    for t in ("flies", "swims", "mountain", "coastal", "subterranean"):
        if (t in a.traits) != (t in b.traits):
            o *= 0.6
    kin_a, kin_b = [a.id] + tree.ancestors(a.id), [b.id] + tree.ancestors(b.id)
    common = next((i for i, x in enumerate(kin_a) if x in kin_b), None)
    kin = 1.0 if common is not None and common <= 1 else 0.85 if common is not None else 0.7
    return float(np.clip(1.15 * o * kin, 0, 0.97))


class HabitatMixin:
    def _K(self, l, env, tags, step, clip=True):
        if l.cities:  # (a city minority: where it can be, its hosts' cities within reach, PW-889)
            return np.where(self._city_mask(l)[0], 1.0, 0.0)
        if l.overlay and l.origin == "template":
            return np.max([self.whole(q) for q in l.parents], axis=0) * np.where(tags["land"], 1.0, 0)
        K = capacity(l, env, tags)
        if not l.marine:  # (the places, wishes and goods are the land's)
            K = K * self._place_mult(l, tags)
            K = K * self._wish_near(l)
        if self.goods is not None and step.epoch != "deep" and not l.marine:  # (the plates have moved since the deep epochs)
            K = K * self._land_mult(l, step.ago <= HOLOCENE_KYR)
            if self.animals is not None and not l.overlay:  # herds, dogs and ploughs make more of the land
                K = K * self.animals.k_mult(self.idx[l.id])
            if self.crops is not None and not l.overlay and self.goods is not None and step.epoch != "deep":  # crops feed more farmers
                K = K * self.crops.k_mult(self.idx[l.id])
        if PM.ADAPT_KYR > 0 and not l.megafauna and not l.marine and not l.overlay and step.epoch != "deep":
            at = getattr(self, "_adj_t", None)  # (lane 77 arm: preference widening toward tolerance where the people has lived next door)
            if at is not None and at[self.idx[l.id]].any():
                a = PM.ADAPT_MAX * (1.0 - np.exp(-at[self.idx[l.id]] / PM.ADAPT_KYR))
                K = np.maximum(K, a * edge_fit(l, env, tags))
        if l.megafauna and not l.marine:  # (PW-1024 B: ecological release into rich land no rival kind holds; the kind's own habitat kept apart
            from . import megafauna as MG  # for its coverage target, megafauna.summary)
            self._K_own[self.idx[l.id]] = K
            rel = MG.release(self, l, self.idx[l.id], env, tags, step)
            if rel is not None:
                K = np.maximum(K, rel)
        if l.extinct_kyr is not None:  # dwindles toward its end
            span = min(0.3 * (l.ago_kyr - l.extinct_kyr), 20.0)
            if span > 0 and step.ago < l.extinct_kyr + span:
                K = K * max(0.0, (step.ago - l.extinct_kyr) / span)
        return np.clip(K, 0, 1) if clip else np.maximum(K, 0)

    def _land_mult(self, l, holocene: bool) -> np.ndarray | float:
        """What the line's way of life looks for in the land (spec [[use]]; land.goods): x(1 - pull + pull G),
        G the best of its favoured goods here (each at its own pull, spec.Tree.pulls_of), normalised to a mean of 1
        over its country unless a use is strict; x(1 - pull |w| g) per
        avoided good. Before HOLOCENE_KYR only the geology (ores, stone) counts: the farmland, pasture,
        forests and coasts are today's. A line with no favoured good of an epoch is left as it is then."""
        from ..land import GOODS
        key = (l.id, holocene)
        m = self._land_m.get(key)
        if m is None:
            uses = [(g, w) for g, w in self.tree.uses_of(l) if g in self.goods and (holocene or GOODS[g][1])]
            pulls = self.tree.pulls_of(l)  # (per good: pull x min(weight, 1), PW-635)
            pos = [(g, pulls[g]) for g, w in uses if w > 0 and pulls.get(g, 0) > 0]
            pull = max((p for _, p in pos), default=self.tree.land_pull)
            m = 1.0
            if pos:
                G = np.max([p * self.goods[g] for g, p in pos], axis=0)
                m = (1 - pull) + G
                # over the line's own country (today's habitat) the mean is 1: the goods move a people within
                # its niche, toward the farmland or the mines, without making it a weaker people overall
                # (a rare good, a coral coast, lifts its few places rather than cutting everywhere else)
                if self._pres is None:
                    env = self.steps[-1].get()
                    self._pres = (env, _tags(self.grid, env, self._chains, self._volcanic()))
                # (unless strict: a people bound to its country, the giants to their volcanoes and peaks,
                # keeps only 1 - pull of its habitat off it)
                if not self.tree.strict_of(l):
                    hab = capacity(l, *self._pres) > 0.25
                    m = m / max(float(m[hab].mean()) if hab.any() else 1.0, 1 - pull)
            for g, w in uses:
                if w < 0:
                    m = m * (1 - self.tree.pull_of(l) * min(-w, 1.0) * self.goods[g])
            self._land_m[key] = m
        return m

    def _volcanic(self, deep: bool = False):
        """The world's volcanic good for the volcanic place tag (None without a world, and in the deep epochs)."""
        return None if deep or self.goods is None else self.goods.get("volcanic")

    def present(self):
        """The present epoch's env and tags (built once)."""
        if self._pres is None:
            env = self.steps[-1].get()
            self._pres = (env, _tags(self.grid, env, self._chains, self._volcanic()))
        return self._pres

    def _place_mult(self, line, tags):
        m = np.ones(self.grid.n)
        for w in self.tree.wishes:
            if w.a == line.id and w.want in SP.PLACES:
                m = m * np.where(tags[w.want], 1 + 0.5 * w.weight, 1 - 0.25 * min(w.weight, 1))
        return m

    def _wish_near(self, line, origin=False):
        """Adjacency wishes as a habitat (or, at an origin, a placement) multiplier.

        near: a pull toward the other people's range that falls off with the distance from it,
        x(1 + NEAR_RANGE w e^(-d / NEAR_KM)) on the habitat outside the other's range (the country
        along its border suits the line better, against third peoples: the ranges close up to a
        shared border instead of one people pushing into or spreading thinly inside the other's;
        the two also compete less, so neither displaces the other there) and x(1 + NEAR_ORIGIN w e^(-d / NEAR_ORIGIN_KM))
        on an origin's score (a split arises on the side of its parent's range facing the other;
        either people of the wish, whichever comes second). apart: x(1 - 0.6 w p_other), on both peoples."""
        m = np.ones(self.grid.n)
        g = self.grid
        for w in self.tree.wishes:
            if w.want == "among":  # (PW-889: living among a people is a matter of competition and composition, not of the habitat)
                continue
            # (apart acts on both peoples, PW-682: keeping out of each other's country is mutual; near on a, and at an
            # origin on either)
            other = w.b if w.a == line.id else w.a if (w.b == line.id and (w.want == "apart" or (origin and w.want == "near"))) else None
            if not other or not self.active.get(other):
                continue
            po = self.whole(other)
            if w.want == "near":
                L = (NEAR_ORIGIN_KM if origin else NEAR_KM) / self.cell_km
                d = graph_dist(po > EST, int(np.ceil(3 * L)), g.nbr_off, g.nbr_idx)
                pull = np.where(d >= 1, np.exp(-(d - 1) / L), 0.0)  # (outside its range: not into it)
                m = m * (1 + (NEAR_ORIGIN if origin else NEAR_RANGE) * w.weight * pull)
            else:
                m = m * (1 - 0.6 * min(w.weight, 1) * self._smooth(po))
        return m

    def _mix_ramp(self, ago):
        ms = self.tree.mixing_start_kyr
        return 0.0 if ago >= ms or ms <= 0 else 1 - ago / ms

    def _mixf(self, l):
        """How much the late mixing relaxes a line's competition: 2 (1 - insularity) (1 at 0.5; spec.DEMOGRAPHY)."""
        return 2.0 * (1.0 - l.demo("insularity"))
