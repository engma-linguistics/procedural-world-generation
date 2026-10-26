"""Peoples through the three time scales: habitat, origins, spread, competition, late mixing.

Epochs: the source run's keyframes (deep, Myr), the glacial time zoom's frames (kyr),
the recent pass (centuries). Design: docs/proposals/lineages.md.
"""

from __future__ import annotations

import time
import zlib
from dataclasses import dataclass, field

import numpy as np

from .. import store as S
from .. import timeline as T
from ..geo import R_KM, is_land
from . import recent as R
from . import spec as SP
from . import land as LD
from .crossing import Crossings, corridor, short_hop
from . import compose as CP
from . import contacts as CT
from . import landuse as LU
from .animals import Animals
from .crops import Crops
from .spread import EST, graph_dist, nearest_label, rings, rivals_load, spread

HOP_EVERY_KYR = 1.0  # long sea crossings are drawn about this often (with the time since)
PIONEER_P = 1.0  # pressure a people's frontier carries into empty country, at most (its habitat there); 0: only its presence
FOUNDER_KM = 400.0  # a split's founders hold the suitable country within this of the origin
CONVERGE = 400  # passes at a deep (Myr) step: ranges fill what is connected
FARM_KYR = 6.0  # agricultural lines speed up from then
MIX_DROP = 0.6  # competition falls by this share by the present (from mixing_start), in full corridors
ALPHA_CLOSED = 1.4  # competition in closed country (contact 0), whatever the niches: over 1, the larger excludes
TAU_KYR = 1.0  # a people held above its competitive room declines toward it with this e-folding time
REFUGE_MKM2 = 0.5  # ...more slowly as its range shrinks toward this (last refuges hold out: no line is pushed out)
NEAR_KM, NEAR_RANGE = 300.0, 0.5  # a 'near' wish's pull on the habitat: x(1 + 0.5 w) at the other's border, e-folding 300 km
NEAR_TOLERANCE = 0.5  # ...and the two compete this much less with each other
NEAR_ORIGIN_KM, NEAR_ORIGIN = 1000.0, 2.0  # ...and on an origin's placement (up to x3 next to it, e-folding 1000 km)
LOST_PENALTY = 0.05  # best of N: score taken off a try per line lost that the tree says lives at the present
APART_CONTESTED = 0.1  # an 'apart' or 'near' wish counts when the two niches would put at least this share of a's habitat near b's
START_KM = 1500.0  # a start hint's reach (PW-763): 'far_from' ramps from x0.05 at the other's border to x1 over this, 'near' falls off with it
NEAR_SCORE_KM = 330.0  # a 'near' wish is met for the share of a's range within this of b's (3 cells at L6)
LINGER_KYR = 10.0  # a contact hybrid lingers where its parents no longer meet, fading with this e-folding time...
ARRIVAL_ROOM = (0.5, 0.2, 0.0)  # an arrival near its hybrid partner takes the free room (share of its best habitat) of the first tier that has some, PW-861
ARRIVAL_POCKET_RINGS = 3  # ...and the free room around a cell is averaged over this many rings (PW-861)
SPECIES_AREA_Z = 0.3  # PW-888: the share of origins a landmass draws goes as (its habitable area)^z, z ~ 0.25-0.35 (the species-area relationship, Rosenzweig 1995, Species Diversity in Space and Time); islands keep some, as isolation drives speciation
ORIGIN_MVP_MULT = 8.0  # PW-888: a landmass can take an origin only if it can carry a long-term minimum viable population, this many times tree.viable_pop (the founder size, 500 in the presets = Frankham 2014's 500 for lasting evolutionary potential): Traill et al. 2007's median MVP for vertebrates is ~4000 = 8 x 500. Founders still start at the founder size
PIONEER_KYR = 8.0  # a newcomer's founding window (PW-869): the competition it feels is cut by PIONEER_Q at first, ramping back over this, and its founders are not displaced
PIONEER_Q = 0.5  # (its founders take the room as a first settler does in empty country; the incumbents press back as the window closes)
EXPANSE_PRESS = 0.6  # an expansive people (explore from EXPANSE_FROM, in full at +EXPANSE_SPAN) that holds a small share of the country it could hold
EXPANSE_FROM, EXPANSE_SPAN = 0.4, 0.3  # ...presses into country others hold: the competition it feels falls by up to this x its expansiveness x the unfilled
EXPANSE_FILL = 0.5  # share (1 - its range / (this x the country with K >= 0.3)); alone the founding window left the elves at 2 of 8 tries with 500 cells
PARTNER_PULL = 4.0  # a sea landing of a people whose contact hybrid is wanted is this much likelier (x1 + this) on the partner's own coast (PW-861)
MEGAFAUNA_PUSH = 0.1  # the competition a megafauna line (a handful of dragons per country, spec megafauna) puts on others, against its niche overlap (PW-855)
HYBRID_REACH_KM = 600.0  # an arrival whose hybrid is wanted comes down within about this of the other parent's range (PW-852)
LINGER_MIN = 0.3  # ...but where they last met it lives on as a small people of its own (at least this share)
HOLOCENE_KYR = 10.0  # the land's living goods (farmland, pasture, forest, coasts) are today's from then on
INVADE, INVADE_FLOOR = 0.5, 0.3  # frontier invasion (PW-887): on the cells touching its range, a rival thinner than one weighs exp(-INVADE x ln(own density / its))
# (a small demographic edge at the front displaces a thinner people, the modern-human / Neanderthal mechanism: Banks 2008, Kolodny & Feldman 2017), at least INVADE_FLOOR
CROWD_HOP, CROWD_ENTER = 2.0, 0.5  # crowding drives exploration (PW-887): a people that loses share of its held country to rivals crosses water (the crossing rate x 1 + CROWD_HOP x crowd,
# within its craft: crossing.modes) and enters poor country (the entry pressure a0 -> a0 + (1 - a0) x CROWD_ENTER x crowd)
DENSITY_PUSH, DENSITY_CLIP = 0.1, (0.7, 1.4)  # competition felt from a rival x (its density / one's own)^0.1, within
# 0.7..1.4: numbers tell a little where peoples share land (farmers at 10 /km² press on foragers at 2 x1.17; giants
# at 0.005 dent others' room x0.7 and feel theirs x1.4). Mild: at 0.25, 0.5..2, the elves and orcs lost
# most of their land to the humans in single tries on 1df1c3
EXPLORE_MARGIN = (0.25, 0.5)  # into marginal land (K < 0.3) the spread keeps a + (1 - a) K / 0.3, a = [0] + [1] x explore
MVP_TAU_KYR = 2.0  # a separate patch of a people with fewer than meta.viable_pop people fades with this e-folding time
MVP_EVERY_KYR = 1.0  # (looked at about this often; a people's largest patch is never faded: its refuges hold)
GROUP_KIN = 0.5  # a group, its people and its sister groups compete at this share of their niche overlap, with no
# closed-country exclusion (terr 0): one people, mixing freely where their ways of life overlap (PW-665)
GROUP_MARGIN = 0.15  # a group appears where its own habitat beats its people's by this share (its niche exists there)
COMPOSITION_TWO_PCT = 10  # a cell holds 2+ peoples when its second people has at least this share (percent)
PALETTE = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#bcf60c",
           "#fabebe", "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1",
           "#000075", "#a9a9a9", "#ff7f50", "#7fffd4", "#dc143c", "#00bfff", "#adff2f", "#ff69b4", "#cd853f"]


# -- epochs ----------------------------------------------------------------------------------------
@dataclass
class Step:
    ago: float  # kyr before present (of this step's state)
    dt: float  # kyr since the previous step
    epoch: str  # deep | glacial | recent
    store: bool
    get: object  # () -> env dict
    stats: dict = field(default_factory=dict)


def _tags(grid, env: dict, chains: bool = True, volcanic: np.ndarray | None = None) -> dict:
    """Place tags of an epoch (PLACES) and Köppen ids, shared by every line (island_chain only if `chains`:
    the costliest tag, needed only when a wish or a line names it; volcanic from the world's volcanic good,
    land.goods, where given: none in the deep epochs, whose volcanoes were elsewhere)."""
    land = env["land"] & ~(env["ice"] > 0.5)
    sea = ~env["land"]
    ni, src = grid.nbr_idx, grid.nbr_src
    sea_nbr = _nbr(np.logical_or, sea[ni], grid)
    elev = np.maximum(env["elevation"] - env["ice"], 0)
    dh = np.maximum(0.0, _nbr(np.maximum, np.abs(elev[ni] - elev[src]), grid))
    lab, k = grid.components(env["land"])
    sizes = np.bincount(lab[lab >= 0], minlength=k) if k else np.zeros(0)
    island = np.zeros(grid.n, bool)
    if k:
        small = sizes < max(3, 0.004 * env["land"].sum())
        island = env["land"] & (lab >= 0) & small[np.maximum(lab, 0)]
    trees = env.get("tree_cover", np.zeros(grid.n))
    rain = env["precipitation"]
    mountain = land & ((elev > 1500) | (dh > 700))
    cl = env["climate"].astype(int)
    # island chains: islands with another island (or any other landmass) within CHAIN_CELLS cells over the sea
    chain = np.zeros(grid.n, bool)
    if chains and island.any():
        big = np.iinfo(np.int64).max
        lo_ = np.where(env["land"], lab, big)
        hi_ = np.where(env["land"], lab, -1)
        through = ~env["land"] | island
        for _ in range(CHAIN_CELLS):
            l2 = np.minimum(lo_, _nbr(np.minimum, np.where(through[ni], lo_[ni], big), grid))
            h2 = np.maximum(hi_, _nbr(np.maximum, np.where(through[ni], hi_[ni], -1), grid))
            lo_, hi_ = np.where(through, l2, lo_), np.where(through, h2, hi_)
        chain = island & (lo_ != hi_)
    farm = land & _isin(cl, SP.GROUPS["temperate"] + [2, 20, 24]) & (rain > 500) & (elev < 1000)
    hills = land & ~mountain & (LD._window(dh / (grid.spacing * R_KM), LD.HILL_SLOPE) * LD._window(elev, LD.HILL_ELEV) >= 0.5)
    volc = land & (volcanic >= 0.5) if volcanic is not None else np.zeros(grid.n, bool)
    return {"farmland": farm, "jungle": land & _isin(cl, [0, 1]), "steppe": land & _isin(cl, [5, 6]),
            "desert": land & _isin(cl, [3, 4]), "tundra": land & (cl == 28), "island_chain": chain,
            "hills": hills, "volcanic": volc,
            "land": land, "sea": sea, "shore": sea & _nbr(np.logical_or, env["land"][ni], grid), "coast": land & sea_nbr, "island": island, "mountain": mountain,
            "lowland": land & (elev < 500), "inland": land & ~sea_nbr, "forest": land & (trees >= 35),
            "open": land & (trees < 20) & (rain > 200), "wetland": land & (elev < 300) & (rain > 1600),
            "elev": elev, "label": lab, "sizes": sizes}


CHAIN_CELLS = 4
PORTAL_SEP_KM = 1800.0  # portals are at least this far apart
PORTAL_KM = 700.0  # an arriving people founds at a portal if it can live within this of it...
PORTAL_FAR_KM = 2500.0  # ...else within this of it (the portal opens onto bad ground for it); else at its best habitat anywhere


def _depth(grid, mask, cap: int = 80) -> np.ndarray:
    """How deep each cell of `mask` lies in it, in cells from the edge (successive erosions), 0 outside."""
    d = np.zeros(grid.n)
    cur = mask.copy()
    for _ in range(cap):
        if not cur.any():
            break
        d += cur
        cur = cur & _nbr(np.logical_and, cur[grid.nbr_idx], grid)
    return d


def _nbr(ufunc, vals, grid):
    """ufunc over each cell's neighbours (vals: one per CSR edge; every cell has neighbours):
    ufunc.at(out, nbr_src, vals) without the slow unbuffered .at, as nbr_src is sorted."""
    return ufunc.reduceat(vals, grid.nbr_off[:-1])


def _csr_gather(off, rows):
    """The positions in a CSR edge list of the edges of `rows`, row after row, each in its own order."""
    cnt = off[rows + 1] - off[rows]
    start = np.cumsum(cnt) - cnt
    return np.repeat(off[rows] - start, cnt) + np.arange(int(cnt.sum()))


def _isin(cl, ids):
    """np.isin for the small Köppen ids (a lookup table)."""
    lut = np.zeros(max(int(cl.max()), max(ids)) + 1, bool)
    lut[list(ids)] = True
    return lut[cl]


def needs_chains(tree: SP.Tree) -> bool:
    return any(w.want == "island_chain" for w in tree.wishes) or any(
        "island_chain" in (*l.prefers, *l.avoids) for l in tree.lines.values())


def pioneer_factors(age_kyr: float | None, explore: float, held_cells: int, potential_cells: int) -> tuple[float, float]:
    """(the multiplier on the competition a people feels, the share of its founding window left) (PW-869). A newcomer, `age_kyr` since it
    started (None: a deep step, no pioneering), feels PIONEER_Q less competition at first, ramping back over PIONEER_KYR, and its founders are
    not displaced meanwhile (the second number, 1 -> 0). An expansive people (`explore` from EXPANSE_FROM) that holds a small share of the
    country it could hold (K >= 0.3: `potential_cells`; full at EXPANSE_FILL of it) presses into country others hold: that much less."""
    if age_kyr is None:
        return 1.0, 0.0
    pio = max(0.0, 1.0 - age_kyr / PIONEER_KYR)
    m = 1.0 - PIONEER_Q * pio
    expansive = min(1.0, max(0.0, (explore - EXPANSE_FROM) / EXPANSE_SPAN))
    if expansive > 0:
        unfilled = min(1.0, max(0.0, 1.0 - held_cells / (EXPANSE_FILL * max(1, potential_cells))))
        m *= 1.0 - EXPANSE_PRESS * expansive * unfilled
    return m, pio


def invasion_weights(dens: np.ndarray, k: int) -> np.ndarray:
    """What each rival j weighs in line k's competition on the cells next to k's own range: 1 for a rival as dense or denser than k,
    exp(-INVADE x ln(dens_k / dens_j)) (not under INVADE_FLOOR) for a thinner one. Every people by the same rule (PW-887)."""
    adv = np.log(np.maximum(dens[k], 1e-9) / np.maximum(dens, 1e-9))
    return np.clip(np.exp(-INVADE * np.maximum(adv, 0.0)), INVADE_FLOOR, 1.0)


def crowding(K: np.ndarray, room: np.ndarray, held: np.ndarray) -> float:
    """How crowded a people is, 0..1: the mean share of its habitat (K) over its held cells that rivals take (1 - room / K)."""
    if not held.any():
        return 0.0
    return float(np.clip(1.0 - room[held] / np.maximum(K[held], 1e-9), 0.0, 1.0).mean())


def _soft(x, lo, hi, soft):
    return np.clip(np.minimum((x - (lo - soft)) / soft, ((hi + soft) - x) / soft), 0, 1)


def _land_view(env: dict, tags: dict) -> dict:
    """An epoch's inputs on its ice-free land cells only, built once per epoch (the habitat is 0 elsewhere)."""
    v = tags.get("_land_view")
    if v is None:
        li = np.flatnonzero(tags["land"])
        v = tags["_land_view"] = {"li": li, "temp": env["temperature"][li],
                                  "lr": np.log2(np.maximum(env["precipitation"][li], 1.0)),
                                  "elev": tags["elev"][li], "cl": env["climate"][li].astype(int), "has": {}}
    return v


def capacity(line: SP.Lineage, env: dict, tags: dict) -> np.ndarray:
    """Carrying capacity K in [0, 1] of a line's own habitat (worked out on the land cells only; a marine line's, on its
    realm's sea cells, marine_capacity)."""
    if line.marine:
        return marine_capacity(line, env, tags)
    v = _land_view(env, tags)
    li = v["li"]
    w = line.trait("widen", 1.0)
    lo, hi = line.temp_c
    mid, half = (lo + hi) / 2, (hi - lo) / 2 * w
    K = _soft(v["temp"], mid - half, mid + half, 4.0 * w)
    rlo, rhi = line.rain_mm
    K = K * _soft(v["lr"], np.log2(max(rlo, 1)) - (w - 1), np.log2(max(rhi, 1)) + (w - 1), 1.0 * w)
    if line.elev_m:
        K = K * _soft(v["elev"], line.elev_m[0], line.elev_m[1], 600.0 * w)

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
        K = K * np.where(match, 1.0, 0.4)
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


# -- the history -----------------------------------------------------------------------------------
class History:
    def __init__(self, tree: SP.Tree, ps: R.Pass, seed: int, deep_every: int = 1, glacial_every: float = 4.0,
                 goods: dict | None = None):
        self.tree, self.ps, self.grid = tree, ps, ps.grid
        self.goods = goods  # the world's goods (land.goods), or None: the [[use]] table then has no effect
        self._land_m: dict[str, tuple] = {}
        self._pres = None  # (the present epoch's env and tags, for the land-use normaliser)
        self._portals = None  # (the arrivals' portals, portal_cells)
        self._K_now: dict[int, np.ndarray] = {}  # (each line's habitat this step, and the contact value: the composition's reach)
        self._corr_now = None
        self._tags_now = None
        self._deg = np.diff(self.grid.nbr_off)
        self.contacts = None  # (contacts.Contacts, made by run: the contact record, PW-727)
        g = self.grid
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.cell_km = g.spacing * R_KM
        self.cell_mkm2 = 4 * np.pi * R_KM ** 2 / g.n / 1e6
        self.lines = tree.order()
        # (a generator per line, seeded from the run seed and the line's id: no line's draws depend on how many others are alive, so a
        # marine line, or a parent kept alive by one, leaves the land peoples' draws as they were, PW-779)
        self._lrng = {l.id: np.random.default_rng((seed, 779, zlib.crc32(l.id.encode()))) for l in self.lines}
        self.idx = {l.id: k for k, l in enumerate(self.lines)}
        self.alpha = np.zeros((len(self.lines),) * 2)
        for a in self.lines:
            for b in self.lines:
                if a.id != b.id and not a.overlay and not b.overlay:
                    self.alpha[self.idx[a.id], self.idx[b.id]] = niche_overlap(a, b, tree)
        # closed-country extra competition: alpha + (1 - contact) x terr (alpha_eff -> ALPHA_CLOSED for alike ways)
        self.terr = np.zeros_like(self.alpha)
        for a in self.lines:
            for b in self.lines:
                if a.id != b.id and not a.overlay and not b.overlay:
                    i, j = self.idx[a.id], self.idx[b.id]
                    self.terr[i, j] = max(0.0, ALPHA_CLOSED - self.alpha[i, j]) * same_way(a, b)
        # marine lines (coast, sea) compete with each other, not with land peoples: they only share the coast (PW-775)
        mar = np.array([l.marine for l in self.lines])
        if mar.any():
            across = mar[:, None] != mar[None, :]
            self.alpha[across] = 0.0
            self.terr[across] = 0.0
        # a group and its people (and its sister groups) are one people: they mix freely (GROUP_KIN, no exclusion)
        for a in self.lines:
            for b in self.lines:
                if a.id != b.id and not a.overlay and not b.overlay and (a.group_of or b.group_of) \
                        and tree.people_of(a.id) == tree.people_of(b.id):
                    i, j = self.idx[a.id], self.idx[b.id]
                    self.alpha[i, j] *= GROUP_KIN
                    self.terr[i, j] = 0.0
        self._groups = {l.id: [self.idx[x] for x in tree.groups_of(l.id)] for l in self.lines}
        self.cohab = CP.cohabitation(tree, self.lines, self.idx)  # (who lives beside whom: the cells' composition, PW-689)
        self.share_traits = {k: np.array([float(l.body[k]) for l in self.lines]) for k in tree.share_traits()}
        # numbers: a denser rival weighs more (DENSITY_PUSH)
        self.dens = np.array([l.demo("density") for l in self.lines])
        push = np.clip((self.dens[None, :] / self.dens[:, None]) ** DENSITY_PUSH, *DENSITY_CLIP)
        self.alpha *= push
        self.terr *= push
        for b in self.lines:  # megafauna press the peoples hardly at all: a handful of dragons does not hold a country against its farmers (PW-855)
            if b.megafauna:
                self.alpha[:, self.idx[b.id]] *= MEGAFAUNA_PUSH
                self.terr[:, self.idx[b.id]] *= MEGAFAUNA_PUSH
        # each line's rivals: the lines whose presence enters its competition
        for w in tree.wishes:  # peoples wished near each other tolerate each other (they share a border)
            if w.want == "near" and w.a in self.idx and w.b in self.idx:
                f = 1 - NEAR_TOLERANCE * min(w.weight, 1.0)
                # (a people named in a wish counts with its groups, PW-665)
                for i in [self.idx[w.a], *self._groups[w.a]]:
                    for j in [self.idx[w.b], *self._groups[w.b]]:
                        for x, y in ((i, j), (j, i)):
                            self.alpha[x, y] *= f
                            self.terr[x, y] *= f
        self._chains = needs_chains(tree)
        self._rivals = [np.flatnonzero((self.alpha[i] != 0) | (self.terr[i] != 0)) for i in range(len(self.lines))]
        self.steps = self._steps(glacial_every)
        self.events: list[dict] = []
        self.origins: dict[str, dict] = {}
        self.tracks: dict[str, list] = {l.id: [] for l in self.lines}
        self.cross = Crossings(self.grid, self.steps[-1].get(), self.cell_km, self.cell_mkm2, getattr(ps, "world_seed", None),
                            getattr(ps, "world_names", None))
        self.flow = getattr(ps, "flow", None)
        self.animals: Animals | None = None  # (made in run(): the domesticated animals, animals.py)
        self.crops: Crops | None = None  # (made in run(): the cultivated plants, crops.py)

    def _steps(self, glacial_every) -> list[Step]:
        ps, out = self.ps, []
        oldest = max(l.ago_kyr for l in self.lines)
        m = ps.run["meta"]
        now = ps.now
        # deep: the source run's keyframes before the time zoom's start
        if m.get("source_run") and m["source_run"] != "earth" and oldest > now:
            src = S.find_run(m["source_run"])
            run, arr = T.load_frames(src, ("elevation", "ice", "temperature", "precipitation", "climate", "tree_cover"))
            ts = np.array([f["t"] for f in run["frames"]])
            at = m["at_myr"]
            agos = (at - ts) * 1000 + now
            keep = np.flatnonzero((ts < at - 1e-6) & (agos <= oldest + 4000))
            if len(keep) and agos[keep].max() < oldest and keep.min() > 0:
                keep = np.r_[keep.min() - 1, keep]
            prev = None
            # a step at each keyframe, at each line's time between them (on the nearest keyframe's
            # world: 4 Myr keyframes would otherwise lump every split of those 4 Myr into one step)
            # and at the time zoom's start
            evs = sorted({l.ago_kyr for l in self.lines if now < l.ago_kyr <= agos[keep].max()} if len(keep) else set())
            sched = sorted({(float(agos[k]), int(k)) for k in keep} | {(float(a), int(keep[np.argmin(np.abs(agos[keep] - a))]))
                                                                        for a in evs} | {(float(now), int(keep[-1]))},
                           key=lambda x: -x[0]) if len(keep) else []
            for ago_k, k in sched:
                def get(k=k, run=run, arr=arr):
                    f = {n: T.frame(run, arr, n, k).astype(float) for n in ("elevation", "ice", "temperature",
                                                                               "precipitation", "climate")}
                    f["tree_cover"] = T.frame(run, arr, "tree_cover", k).astype(float) if "tree_cover" in arr else np.zeros(len(f["ice"]))
                    f["land"] = is_land(f["elevation"], f["ice"])
                    f["elevation"] = np.where(f["ice"] > 0, np.maximum(f["elevation"], 0) + f["ice"], f["elevation"])
                    return f
                if prev is not None and prev - ago_k < 1e-6:
                    continue
                out.append(Step(ago_k, 4000.0 if prev is None else float(prev - ago_k), "deep", True, get,
                                {**run["frames"][k]["stats"], "epoch": "deep"}))
                prev = ago_k
        # glacial: the time zoom's frames before the recent window
        rstart = now + ps.start
        tz_ts = ps.ts[(ps.ts < rstart - 1e-6) & (now - ps.ts <= oldest + 2)]
        prev = out[-1].ago if out else None
        last_store = None
        for t in tz_ts:
            ago = now - t
            st = last_store is None or (last_store - ago) >= glacial_every - 1e-6
            if st:
                last_store = ago
            k = int(np.argmin(np.abs(ps.ts - t)))
            out.append(Step(float(ago), 2.0 if prev is None else float(prev - ago), "glacial", st,
                            lambda t=t: ps.fields(t - now, variability=False),
                            {**ps.run["frames"][k]["stats"], "epoch": "glacial"}))
            prev = ago
        # recent: century steps with the variability
        e = ps.params.every
        for t in ps.steps:
            ago = -float(t)
            st = abs(round(t / e) * e - t) < 1e-6
            out.append(Step(ago, ps.params.step if prev is not None else ps.params.step, "recent", st,
                            lambda t=float(t): ps.fields(t), {**ps.stats(float(t)), "epoch": "recent"}))
            prev = ago
        return out

    # -- origins ---------------------------------------------------------------------------------
    def _noise(self, line):
        return np.exp(0.5 * self._lrng[line.id].gumbel(size=self.grid.n))

    def _place_mult(self, line, tags):
        m = np.ones(self.grid.n)
        for w in self.tree.wishes:
            if w.a == line.id and w.want in SP.PLACES:
                m = m * np.where(tags[w.want], 1 + 0.5 * w.weight, 1 - 0.25 * min(w.weight, 1))
        return m

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
            q[idx] = rivals_load(self.p, J, self.alpha[k], self.terr[k], idx,
                                  (self._corr_now if self._corr_now is not None else np.full(self.grid.n, 0.5))[idx])
        return q

    def _seed_blob(self, k, cell, K, mask, r):
        g = self.grid
        blob = rings(int(cell), mask | (np.arange(g.n) == cell), r, g.nbr_off, g.nbr_idx) & (K > EST)
        blob[cell] = True
        self.p[k][blob] = np.maximum(self.p[k][blob], np.clip(K[blob], 0.3, 1))
        return blob

    def _by_landmass(self, line, score, K, env):
        """PW-888: the landmass of an origin is drawn before the cell. Each landmass of the step's own land (connected land, so a
        glacial bridge joins two) that the origin's score reaches, and whose habitable country (cells with K > EST) would carry a
        long-term viable population (ORIGIN_MVP_MULT x tree.viable_pop, as _viable counts people), draws with probability (habitable area)^SPECIES_AREA_Z; the
        habitat score then picks the cell within it. Without this the best cell of a heavy-tailed noise field wins wherever it
        falls, and one small continent held 13-15 peoples. The same rule for every people; nothing is drawn when only one
        landmass qualifies."""
        if SPECIES_AREA_Z <= 0:  # (0: off)
            return score
        lab, n = self.grid.components(env["land"])
        suit = (K > EST) & (score > 0) & (lab >= 0)
        if n < 2 or not suit.any():
            return score
        k = self.idx[line.id]
        cells = np.bincount(lab[suit], minlength=n).astype(float)
        founders = np.bincount(lab[suit], weights=K[suit], minlength=n) * self.dens[k] * self.cell_mkm2 * 1e6 * 0.5
        w = np.where(founders >= ORIGIN_MVP_MULT * self.tree.viable_pop, cells, 0.0) ** SPECIES_AREA_Z
        if np.count_nonzero(w) < 2:
            return score
        pick = int(self._lrng[line.id].choice(n, p=w / w.sum()))
        return np.where(lab == pick, score, 0.0)

    def _origin(self, line, step, env, tags, K):
        g, k = self.grid, self.idx[line.id]
        noise = self._noise(line)
        why = "habitat"
        if line.origin in ("root", "arrival"):
            score = K * self._place_mult(line, tags) * self._wish_near(line, origin=True) * self._start_hints(line, env, tags) * noise
            pull = None
            if line.origin == "arrival":  # a newcomer whose hybrids are wanted comes near the other parent
                for h in self.tree.lines.values():
                    if h.origin == "hybrid" and line.id in h.parents:
                        other = [q for q in h.parents if q != line.id][0]
                        if self.active.get(other):  # (PW-852: within HYBRID_REACH_KM of its range, not just three cells: the two should meet soon)
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
                                for _ in range(ARRIVAL_POCKET_RINGS):
                                    pocket = self._smooth(pocket)
                                ok = ok & (pocket >= np.median(pocket[ok]))  # (a restriction, not a weight: the origin's noise is heavy-tailed, a weight of 0.05 is beaten by its luck)
                                m = np.where(ok, m, 0.0)
                                pull = m if pull is None else pull * m
                                score = score * m
            if not line.place:
                score = self._by_landmass(line, score, K, env)
            if line.place:
                la, lo = np.radians(line.place)
                c = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
                d = np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM
                score = score * np.exp(-(d / 600.0) ** 2) + 1e-9 * (d < 300)
                why = "given place"
            cell = int(np.argmax(score))
            if K[cell] <= EST:
                cell = int(np.argmax(np.where(hold_mask(line, tags), K + 1e-6, 0) * noise))
                why += " (poor habitat)"
            if line.origin == "arrival" and not line.place and self.tree.portal_mode != "off" and self.portal_cells():
                # through the portals (PW-697): at each where the people can live within PORTAL_KM (else, within
                # PORTAL_FAR_KM of the nearest that can hold it; else at its best habitat anywhere, as without portals)
                near, far = [], []
                for pt in self.portal_cells():
                    d = np.arccos(np.clip(g.centers @ g.centers[pt["cell"]], -1, 1)) * R_KM
                    ok = (d < PORTAL_KM) & (K > EST)
                    if ok.any():
                        near.append((int(np.argmax(np.where(ok, K * noise, 0))), pt["kind"]))
                        continue
                    ok = (d < PORTAL_FAR_KM) & (K > EST)
                    if ok.any():
                        far.append((float(d[ok].min()), int(np.argmax(np.where(ok, K * noise * np.exp(-d / 1000), 0))), pt["kind"]))
                if not near and far:
                    f = min(far)
                    near = [(f[1], f[2])]
                if near:
                    if pull is not None:  # (the portal nearest the other parent first: PW-852)
                        near.sort(key=lambda x: -pull[x[0]])
                    cell = near[0][0]
                    for c, _ in near[1:]:
                        self._seed_blob(k, c, K, K > EST, 3)
                    why = f"through {'a portal' if len(near) == 1 else str(len(near)) + ' portals'} ({', '.join(sorted({f[1] for f in near}))})"
            self._seed_blob(k, cell, K, K > EST, 3)
        elif line.origin == "split":
            pk = self.idx[line.parents[0]]
            P = self.p[pk] > EST
            if not P.any():
                return self._origin_fallback(line, step, env, tags, K, "parent gone")
            lab, n = g.components(P)
            sizes = np.bincount(lab[P], minlength=n)
            big = int(np.argmax(sizes))
            edge = _nbr(np.logical_or, ~P[g.nbr_idx], g)
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
            score = np.where(P, (K + 0.02) * iso, np.where(near | across, 0.6 * K, 0)) * self._place_mult(line, tags) \
                * self._wish_near(line, origin=True) * self._start_hints(line, env, tags) * noise * (K > 2 * EST)  # (where the founders can live)
            if score.max() <= 0:
                return self._origin_fallback(line, step, env, tags, K, "no room for it by the parent: best habitat")
            score = self._by_landmass(line, score, K, env)
            cell = int(np.argmax(score))
            why = ("isolated part of the parent's range" if lab[cell] != big else
                   "edge of the parent's range" if edge[cell] else "inside the parent's range") if P[cell] \
                else "across the sea from the parent's range (founders carried over)" if across[cell] \
                else "beside the parent's range (new niche)"
            # the founders hold the country around the origin that suits them at least half as well as it
            # suits the parent (FOUNDER_KM), or the whole cut-off part of the parent's range they arose in
            pK = self._K(self.tree.lines[line.parents[0]], env, tags, step)
            r = max(2, int(round(FOUNDER_KM / self.cell_km)))
            blob = self._seed_blob(k, cell, K, (K > EST) & ((K >= 0.5 * pK) | ~P), r)
            if P[cell] and lab[cell] != big:
                part = (lab == lab[cell]) & (K > EST)
                self.p[k][part] = np.maximum(self.p[k][part], np.minimum(K[part], np.maximum(self.p[pk][part], 0.3)))
                blob = blob | part
            self.p[pk][blob & P] = 0.0
        elif line.origin == "hybrid":
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
        elif line.origin == "group":
            res = self._group_origin(line, step, env, tags, K)
            if res is None:
                return False
            cell, why = res
        else:  # template
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
        self._record_origin(line, step, cell, why)
        return True

    def present(self):
        """The present epoch's env and tags (built once)."""
        if self._pres is None:
            env = self.steps[-1].get()
            self._pres = (env, _tags(self.grid, env, self._chains, self._volcanic()))
        return self._pres

    def portal_cells(self) -> list[dict]:
        """The portals the arrivals from outside come through (meta.portal_mode random | sites, meta.portals; PW-697):
        chosen once per try on today's land, at least PORTAL_SEP_KM apart. 'random': any ice-free land. 'sites': the
        tree's portal_sites in turn, shuffled: the deepest part of the largest forest, the middle of the largest desert,
        a coral reef coast, the foot of a volcanic cone (land beside young volcanic ground)."""
        if self._portals is not None:
            return self._portals
        tree, g = self.tree, self.grid
        env, tags = self.present()
        land = tags["land"]
        out: list[dict] = []
        if tree.portal_mode == "off" or not land.any():
            self._portals = out
            return out
        noise = self.rng.random(g.n)
        free = land.copy()

        def pick(score, kind):
            sc = np.where(free, score, 0.0)
            if sc.max() <= 0:
                return False
            c = int(np.argmax(sc + 1e-6 * noise * (sc > 0)))
            out.append({"cell": c, "kind": kind, "lat": round(float(g.lat[c]), 2), "lon": round(float(g.lon[c]), 2)})
            d = np.arccos(np.clip(g.centers @ g.centers[c], -1, 1)) * R_KM
            free[d < PORTAL_SEP_KM] = False
            return True

        if tree.portal_mode == "random":
            for _ in range(tree.portals):
                if not pick(land * 1.0, "random"):
                    break
        else:
            scores = {}
            if "forest" in tree.portal_sites:
                scores["forest"] = _depth(g, tags["forest"])
            if "desert" in tree.portal_sites:
                scores["desert"] = _depth(g, tags["desert"])
            if "reef" in tree.portal_sites and self.goods is not None and "coral" in self.goods:
                scores["reef"] = np.where(land, np.asarray(self.goods["coral"], float), 0.0)
            if "volcano" in tree.portal_sites and tags["volcanic"].any():
                v = tags["volcanic"]
                foot = self._dilate(v, 2) & land & ~v
                scores["volcano"] = foot * (1.0 + self._dilate(v, 1) * 0.5)
            kinds = [k for k in tree.portal_sites if k in scores]
            if not kinds:  # (none of those places on this world: anywhere)
                kinds = ["random"]
                scores["random"] = land * 1.0
            order = [kinds[i] for i in self.rng.permutation(len(kinds))]
            for i in range(tree.portals):
                for k in order[i % len(order):] + order[:i % len(order)]:  # (this kind first, any other if it has no room left)
                    if pick(scores[k], k):
                        break
        self._portals = out
        return out

    def _group_origin(self, line, step, env, tags, K):
        """A way of life within a people (PW-665): it takes hold where its own habitat beats its people's by
        GROUP_MARGIN (unclipped, so prime land for both still tells them apart): in every such cell of its
        people's range (divergence in place), and as founders (FOUNDER_KM, as a split's) around the cell of the
        largest advantage, its origin. Without such land, at its people's range edge where it does best. Half
        the people's presence there goes over to it (they are of it); the people lives on. None: its people
        isn't there yet (wait)."""
        k = self.idx[line.id]
        pid = line.group_of
        pk = self.idx[pid]
        P = self.p[pk] > EST
        if not P.any():
            if pid not in self.started:
                return None
            cell = int(np.argmax(K * self._noise(line)))
            self._seed_blob(k, cell, K, K > EST, 3)
            return cell, "its people gone: best habitat"
        Kg = self._K(line, env, tags, step, clip=False)
        Kp = self._K(self.tree.lines[pid], env, tags, step, clip=False)
        good = P & (Kg > (1 + GROUP_MARGIN) * Kp) & (K > 2 * EST)
        nudge = self._place_mult(line, tags) * self._wish_near(line, origin=True) * self._noise(line)
        if good.any():
            score = np.where(good, Kg - Kp, 0) * nudge
            why, mask = "where its way of life suits the land better than its people's", good
        else:
            near = self._dilate(P, 2) & tags["land"]
            score = np.where(near, K, 0) * nudge * (K > 2 * EST)
            why, mask = "at its people's range edge (no land suits it better there)", K > EST
            if score.max() <= 0:
                score, why = K * nudge, "best habitat (none near its people)"
        cell = int(np.argmax(score))
        r = max(2, int(round(FOUNDER_KM / self.cell_km)))
        blob = self._seed_blob(k, cell, K, mask, r)
        # a way of life arises in place wherever it suits the land better (divergence, not migration): every such
        # cell of the people's range takes it up, from half the people there
        took = good & ~blob
        self.p[k][took] = np.maximum(self.p[k][took], np.minimum(K[took], np.maximum(0.5 * self.p[pk][took], 2 * EST)))
        self.p[pk][(blob | took) & P] *= 0.5
        self.p[pk][self.p[pk] < EST] = 0
        return cell, why

    def _diverge(self, l, k, env, tags, step):
        """A way of life goes on arising in place after its origin (PW-684): in a cell of its people's range that
        it doesn't hold yet and where its habitat beats its people's by GROUP_MARGIN (as at its origin), half the
        people there go over to it. A people that settles new country later (crossing a sea to a cold coast, or
        to a river plain) lives there as its ways of life suit it, as it would have where it already was."""
        pk = self.idx[l.group_of]
        P = self.p[pk] > EST
        if not P.any():
            return
        Kg = self._K(l, env, tags, step, clip=False)
        Kp = self._K(self.tree.lines[l.group_of], env, tags, step, clip=False)
        new = P & (self.p[k] < EST) & (Kg > (1 + GROUP_MARGIN) * Kp) & (np.minimum(Kg, 1.0) > 2 * EST)
        if new.any():
            self.p[k][new] = np.minimum(np.minimum(Kg[new], 1.0), np.maximum(0.5 * self.p[pk][new], 2 * EST))
            self.p[pk][new] *= 0.5
            self.p[pk][self.p[pk] < EST] = 0

    def whole(self, lid: str, P: np.ndarray | None = None) -> np.ndarray:
        """A people's presence with its groups (their sum, at most 1); a line without groups, its own."""
        P = self.p if P is None else P
        k = self.idx[lid]
        gs = self._groups.get(lid)
        if not gs:
            return P[k]
        return np.minimum(1.0, P[k] + P[gs].sum(0))

    def rollup(self, P: np.ndarray) -> np.ndarray:
        """P with each people's row holding its groups too (whole) and the groups' rows zeroed: the peoples as
        wholes, indexed as the lines (the whole-people map layer, the mixing of peoples, the summaries)."""
        if not any(self._groups.values()):
            return P
        out = P.copy()
        for lid, gs in self._groups.items():
            if gs:
                k = self.idx[lid]
                out[k] = np.minimum(1.0, P[k] + P[gs].sum(0))
                out[gs] = 0.0
        return out

    def fold(self, M: np.ndarray) -> np.ndarray:
        """M with each people's row summed with its groups' rows (no cap) and the groups' rows zeroed."""
        out = M.copy()
        for lid, gs in self._groups.items():
            if gs:
                out[self.idx[lid]] = M[self.idx[lid]] + M[gs].sum(0)
                out[gs] = 0.0
        return out

    def _suit(self) -> np.ndarray:
        """How well each people (its groups counted in) could live in each cell this step, 0..1 (from its habitat K)."""
        S = np.zeros_like(self.p)
        for k, K in self._K_now.items():
            if not self.lines[k].overlay and self.active[self.lines[k].id]:
                S[k] = np.where(K >= EST, np.clip(K / CP.SUIT_K, 0.0, 1.0), 0.0)
        for lid, gs in self._groups.items():
            if gs:
                S[self.idx[lid]] = np.maximum(S[self.idx[lid]], S[gs].max(0))
        return S

    def _origin_fallback(self, line, step, env, tags, K, why):
        k = self.idx[line.id]
        cell = int(np.argmax(K * self._noise(line)))
        self._seed_blob(k, cell, K, K > EST, 3)
        self._record_origin(line, step, cell, why)
        return True

    def _record_origin(self, line, step, cell, why):
        g = self.grid
        self.origins[line.id] = {"cell": int(cell), "lat": round(float(g.lat[cell]), 2), "lon": round(float(g.lon[cell]), 2),
                                 "ago_kyr": round(step.ago, 3), "wanted_kyr": line.ago_kyr, "epoch": step.epoch, "why": why}
        verb = {"root": "arises", "split": f"splits from {line.parents[0] if line.parents else '?'}", "arrival": "arrives",
                "hybrid": f"appears where {' and '.join(line.parents)} meet", "template": f"appears among {', '.join(line.parents)}",
                "group": f"becomes a way of life among the {self.tree.lines[line.parents[0]].label() if line.parents else '?'}"}
        self.events.append({"ago_kyr": round(step.ago, 3), "kind": line.origin, "line": line.id,
                            "text": f"{line.label()} {verb[line.origin]} ({why})", "lat": self.origins[line.id]["lat"],
                            "lon": self.origins[line.id]["lon"]})

    def _wish_near(self, line, origin=False):
        """Adjacency wishes as a habitat (or, at an origin, a placement) multiplier.

        near: a pull toward the other people's range that falls off with the distance from it,
        x(1 + NEAR_RANGE w e^(-d / NEAR_KM)) on the habitat outside the other's range (the country
        along its border suits the line better, against third peoples: the ranges close up to a
        shared border instead of one people pushing into or spreading thinly inside the other's;
        the two also compete less, NEAR_TOLERANCE, so neither displaces the other there) and x(1 + NEAR_ORIGIN w e^(-d / NEAR_ORIGIN_KM))
        on an origin's score (a split arises on the side of its parent's range facing the other;
        either people of the wish, whichever comes second). apart: x(1 - 0.6 w p_other), on both peoples."""
        m = np.ones(self.grid.n)
        g = self.grid
        for w in self.tree.wishes:
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

    def _dilate(self, m, r):
        g = self.grid
        m = m.copy()
        for _ in range(r):
            m = m | _nbr(np.logical_or, m[g.nbr_idx], g)
        return m

    def _smooth(self, x):
        """max(x, mean of the neighbours). A presence field is mostly zero: then only the cells next to a held cell are summed
        (each over its own neighbours in the same order as the full sum, so the result is the same to the last bit; PW-743)."""
        g = self.grid
        nz = np.flatnonzero(x)
        if len(nz) * 4 > g.n:
            s = _nbr(np.add, x[g.nbr_idx], g)
        else:
            s = np.zeros(g.n)
            if len(nz):
                rows = np.unique(g.nbr_idx[_csr_gather(g.nbr_off, nz)])
                at = _csr_gather(g.nbr_off, rows)
                cnt = g.nbr_off[rows + 1] - g.nbr_off[rows]
                s[rows] = np.add.reduceat(x[g.nbr_idx[at]], np.cumsum(cnt) - cnt)
        return np.maximum(x, s / self._deg)

    def _realm_kids(self, line) -> list:
        """The living split children in the line's own realm: a land people ends and hands its range over among its land children
        only (a marine child never takes its land, nor holds the parent's end back, PW-779)."""
        return [c for c in self.tree.living_children(line.id) if self.tree.lines[c].marine == line.marine]

    def _end_parent(self, line, step, env, tags):
        """After its last split: the parent's remaining range is shared among its children. Country joined to
        a child's land goes to the nearest child; a part cut off from every child (the stem held other
        landmasses too) carries on as the child whose niche suits it best (mean habitat over the part): the
        stem's isolated stock is that people's own ancestors there, not lost with the stem (PW-677)."""
        g, k = self.grid, self.idx[line.id]
        P = self.p[k] > EST
        lab = np.full(g.n, -1, np.int64)
        kids = [c for c in self._realm_kids(line) if self.active.get(c)]
        for ci, c in enumerate(kids):
            lab[self.p[self.idx[c]] > EST] = ci
        if kids and P.any():
            near = nearest_label(lab, P | (lab >= 0), g.nbr_off, g.nbr_idx)
            orphan = P & (near < 0)
            if orphan.any():
                Kk = [self._K(self.tree.lines[c], env, tags, step) for c in kids]
                comp, nco = g.components(orphan)
                for z in range(nco):
                    part = comp == z
                    best = int(np.argmax([float(K[part].mean()) for K in Kk]))
                    if Kk[best][part].max() > EST:
                        near[part] = best
            for ci, c in enumerate(kids):
                sel = P & (near == ci)
                kc = self.idx[c]
                self.p[kc][sel] = np.maximum(self.p[kc][sel], self.p[k][sel])
        self.p[k][:] = 0
        self.active[line.id] = False
        self.ended[line.id] = step.ago

    # -- the loop --------------------------------------------------------------------------------
    def run(self, progress=lambda f, msg: None) -> dict:
        g, L = self.grid, self.lines
        self.p = np.zeros((len(L), g.n))
        self.active = {l.id: False for l in L}
        self.started, self.ended = {}, {}
        self.crossings_n: dict[str, int] = {}
        self._hop_dt = np.zeros(len(L))
        self._mvp_dt = np.zeros(len(L))
        self._div_dt = np.zeros(len(L))
        self._native = np.array([i for i, x in enumerate(L) if not x.overlay and not x.marine], np.int64)  # (land peoples: the sea ones leave the animals, crops and counts as they were)
        self._nat_set = set(self._native.tolist())
        self.faded: dict[str, int] = {}  # patches faded below the viable population, per line
        self._living = {x.id for x in self.tree.leaves()}
        self._refuged: set[str] = set()
        self._last_meet: dict[str, np.ndarray] = {}  # contact hybrids: where their parents last met
        self._apart: set[str] = set()  # ...and those whose parents no longer meet anywhere
        self._lingered: set[str] = set()
        self._linger = np.zeros((len(L), g.n), bool)  # cells a contact hybrid holds on its own
        budget = np.zeros(len(L))
        self.contacts = CT.Contacts(self)
        self.animals = Animals(self) if (self.tree.animals is None or self.tree.animals or self.tree.animals_force) else None
        self.crops = Crops(self) if (self.tree.crops is None or self.tree.crops or self.tree.crops_force) else None
        frames = []
        nsteps = len(self.steps)
        t0 = time.time()
        for si, step in enumerate(self.steps):
            env = step.get()
            deep = step.epoch == "deep"
            tags = _tags(g, env, self._chains, self._volcanic(deep))  # (the plates have moved since: no present rivers or shelves then)
            tags["corridor"] = corr = corridor(tags, env, None if deep else self.flow,
                                               None if deep else env["land"] & (self.cross.label < 0))
            self._corr_now = corr
            self._tags_now = tags
            Ks = {}
            # events due by this step, oldest first (lines older than the history start at its first step)
            for l in L:
                if l.id in self.started or l.ago_kyr < step.ago - 1e-9:
                    continue
                if l.extinct_kyr is not None and step.ago <= l.extinct_kyr:
                    self.started[l.id] = step.ago
                    continue
                K = Ks[l.id] = self._K(l, env, tags, step)
                if self._origin(l, step, env, tags, K):
                    self.started[l.id] = step.ago
                    self.active[l.id] = True
                    if l.parent:
                        par = self.tree.lines[l.parent]
                        kin = self._realm_kids(par)
                        if not par.persists and kin and all(c in self.started for c in kin) and self.active.get(par.id):
                            self._end_parent(par, step, env, tags)
            if self.animals is not None:
                self.animals.step(step, env, tags, self.p, self._native)
            if self.crops is not None:
                self.crops.step(step, env, tags, self.p, self._native)
            mix = self._mix_ramp(step.ago)
            self._pm = self.p >= EST  # (who holds what at the start of the step, and the count over the natives: kept up to date as each line moves, _sync)
            self._cnt = self._pm[self._native].sum(0, dtype=np.int16)
            order = [l for l in L if self.active[l.id]]
            keys = {l.id: self._lrng[l.id].random() for l in order}  # (the order: a random key per line from its own generator)
            order.sort(key=lambda l: (l.marine, keys[l.id]))
            for l in order:
                k = self.idx[l.id]
                if l.extinct_kyr is not None and step.ago <= l.extinct_kyr + 1e-9:
                    self.p[k][:] = 0
                    self.active[l.id] = False
                    self.ended[l.id] = step.ago
                    self.events.append({"ago_kyr": round(step.ago, 3), "kind": "extinct", "line": l.id,
                                        "text": f"{l.label()} dies out", "lat": None, "lon": None})
                    self._sync(k)
                    continue
                K = Ks.get(l.id)
                if K is None:
                    K = self._K(l, env, tags, step)
                self._K_now[k] = K  # (the composition's reach: where a people could live, CP.reach)
                if l.overlay and l.origin == "hybrid":
                    self._hybrid(l, k, K, step)
                    continue
                self.p[k] = np.minimum(self.p[k], K)
                self.p[k][self.p[k] < EST] = 0
                if l.group_of and not deep:
                    self._div_dt[k] += step.dt
                    if self._div_dt[k] >= HOP_EVERY_KYR:
                        self._diverge(l, k, env, tags, step)
                        self._sync(self.idx[l.group_of])  # (it moved some of its people's range over to the group)
                        self._div_dt[k] = 0.0
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
                    q = rivals_load(self.p, J, self.alpha[k], self.terr[k], idx, c)
                    if INVADE > 0 and not deep and not l.marine and len(J):
                        # frontier invasion: along the contact line a denser people weighs its thinner rivals less (PW-887)
                        front = self._dilate(self.p[k] >= EST, 1)[idx]
                        if front.any():
                            w = invasion_weights(self.dens, k)
                            fi = np.flatnonzero(front)
                            q[fi] = rivals_load(self.p, J, self.alpha[k] * w, self.terr[k] * w, idx[fi], c[fi])
                    if "agricultural" in l.traits and step.ago <= FARM_KYR:
                        q = q * np.where(tags["farmland"][idx], 0.5, 1.0)  # farmers push into others' fertile lowland
                    press = SP.WAY_PRESS.get(l.way) if l.way and self.animals is not None and self.goods is not None else None
                    if press and press[0] in self.goods and step.epoch != "deep":
                        herd = min(1.0, self.animals.herding(k) / SP.HERD_FULL)
                        if herd > 0:  # herders hold good pasture against settled neighbours (spec.WAY_PRESS, PW-756)
                            q = q * (1 - (1 - press[1]) * herd * np.clip(self.goods[press[0]][idx], 0, 1))
                    q = q * l.trait("push", 1.0)
                    qm, pio = pioneer_factors(None if deep else self.started[l.id] - step.ago, l.demo("explore"),
                                              int((self.p[k] >= EST).sum()), int((K >= 0.3).sum()))
                    q = q * qm  # (a newcomer takes room as a first settler does; an expansive people with room to grow presses on, PW-869)
                    f = np.clip(1 - MIX_DROP * mix * self._mixf(l) * c, 0.05, 1)
                    room = np.zeros(g.n)
                    room[idx] = np.clip(K[idx] - f * q, 0, None)
                    over = self.p[k] > room  # displacement: held above its room, a people dwindles there
                    if over.any():
                        held = (self.p[k] >= EST).sum() * self.cell_mkm2
                        r = (1 - np.exp(-step.dt / TAU_KYR)) * np.clip(held / REFUGE_MKM2 - 1, 0, 1) * (1.0 - pio)  # (a newcomer's founders are not displaced, PW-869)
                        self.p[k][over] -= r * (self.p[k][over] - room[over])
                        self.p[k][self.p[k] < EST] = 0
                    if not deep and not l.marine:
                        crowd = crowding(K, room, self.p[k] >= EST)
                speed = l.speed_kmyr * l.trait("speed", 1.0) * (2.0 if "agricultural" in l.traits and step.ago <= FARM_KYR else 1.0)
                if self.animals is not None and not l.marine:  # riders and herders spread faster (animals.py)
                    speed *= self.animals.speed_mult(k)
                if step.epoch == "deep":
                    passes = CONVERGE
                else:
                    budget[k] += speed * step.dt * 1000 / self.cell_km
                    passes = int(budget[k])
                    budget[k] -= passes
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
                if not l.overlay and not l.marine:
                    self._mvp_dt[k] += step.dt
                    if self._mvp_dt[k] >= MVP_EVERY_KYR or deep:
                        self._viable(l, k, self._mvp_dt[k], step)
                        self._mvp_dt[k] = 0.0
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
                        self.events.append({"ago_kyr": round(step.ago, 3), "kind": "refuge", "line": l.id,
                                            "text": f"{l.label()} hold out in a refuge", "lat": round(float(g.lat[cell]), 2),
                                            "lon": round(float(g.lon[cell]), 2)})
                if not (self.p[k] > EST).any() and not l.overlay:
                    self.active[l.id] = False
                    self.ended[l.id] = step.ago
                    self.events.append({"ago_kyr": round(step.ago, 3), "kind": "extinct", "line": l.id,
                                        "text": f"{l.label()} dies out (no habitat left)", "lat": None, "lon": None})
                self._sync(k)
            if step.store or si == nsteps - 1:
                frames.append(self._frame(step, env))
            if si % 25 == 0:
                progress(si / nsteps, f"step {si}/{nsteps} ({step.epoch}, {step.ago:g} kyr ago)")
        self.runtime = time.time() - t0
        return {"frames": frames, "present": self.p.copy()}

    def _sync(self, k):
        """Bring the step's held-mask of line k, and the count of natives holding each cell, up to date after p[k] changed."""
        now = self.p[k] >= EST
        if k in self._nat_set:
            self._cnt += now.astype(np.int16) - self._pm[k]
        self._pm[k] = now

    def _viable(self, l, k, dt, step):
        """A separate patch of the people's land holding fewer than tree.viable_pop people fades (e-folding
        MVP_TAU_KYR): a sparse people (a band roaming thousands of km²) needs a large piece of good country to
        hold a land. Only for lines sparse enough that the viable number needs more than 2 cells; never the
        largest patch (a people's last land is the refuge logic's)."""
        mvp = self.tree.viable_pop
        area = self.cell_mkm2 * 1e6
        if mvp <= 0 or mvp / (self.dens[k] * area * 0.5) <= 2:
            return
        held = self.p[k] >= EST
        if not held.any():
            return
        lab, n = self.grid.components(held)
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

    def population(self, k: int, P: np.ndarray | None = None) -> np.ndarray:
        """People per cell of line k: presence x density x cell area. An overlay (template, contact hybrid) is
        its share of its hosts' people where it is, except where a contact hybrid lives on as a people of its own."""
        P = self.p if P is None else P
        l, area = self.lines[k], self.cell_mkm2 * 1e6
        x = np.where(P[k] >= EST, P[k], 0.0)
        if not l.overlay:
            return x * self.dens[k] * area
        hosts = sum(np.where(P[j] >= EST, P[j], 0.0) * self.dens[j]
                    for q in l.parents for j in [self.idx[q], *self._groups.get(q, [])])
        own = self._linger[k]
        return np.where(own, x * self.dens[k] * area, (x > 0) * l.share * self._fertility(l) * hosts * area)

    def _fertility(self, l) -> float:
        """A contact hybrid's share scales with how fertile its parents' hybrids are by their divergence (PW-851: fertile out to ~1-2 Myr, mostly
        sterile to ~4, none beyond); 1 for a template, and where no divergence date is there to read (half-elves)."""
        if l.origin != "hybrid":
            return 1.0
        f = self.__dict__.setdefault("_fert", {})
        if l.id not in f:
            f[l.id] = self.tree.fertility(*l.parents)
        return f[l.id]

    def _meeting(self, a, b):
        """Where two peoples meet (PW-852): in a cell both hold, or on a frontier: one holds the cell and the other the cell next to it.
        In closed country a rival excludes the other from its cells (history.run, ALPHA_CLOSED), so two ranges on one continent
        usually only touch, and contact is a border, not an overlap. The presence there is the weaker of the two."""
        g = self.grid
        da = np.maximum(a, _nbr(np.maximum, a[g.nbr_idx], g))
        db = np.maximum(b, _nbr(np.maximum, b[g.nbr_idx], g))
        return np.maximum(np.minimum(a, db), np.minimum(da, b))

    def _hybrid(self, l, k, K, step):
        """A contact hybrid: where its parents meet it is a share of their people (and grows with the contact);
        once it has appeared it lingers where they no longer meet, fading (LINGER_KYR) within its own habitat,
        and where they last met it lives on as a small people of its own (PW-613)."""
        g = self.grid
        a, b = (self.whole(q) for q in l.parents)
        O = self._meeting(a, b)
        meet = O >= EST
        old = self.p[k]
        linger = np.minimum(old * np.exp(-step.dt / LINGER_KYR), K) if l.linger else np.zeros(g.n)
        new = np.where(meet, np.maximum(O, linger), linger)
        if meet.any():
            self._last_meet[l.id] = meet & (K > EST)
            self._apart.discard(l.id)
        elif l.linger and l.id in self._last_meet:
            last = self._last_meet[l.id]
            if not last.any():  # (the parents met only where its own habitat is poor: the best of it nearby)
                near = self._dilate(old > 0, 2) if (old > 0).any() else np.ones(g.n, bool)
                last = rings(int(np.argmax(np.where(near, K, 0))), K > EST, 1, g.nbr_off, g.nbr_idx)
                self._last_meet[l.id] = last
            new[last] = np.maximum(new[last], np.clip(K[last] * LINGER_MIN, 2 * EST, None))
            if l.id not in self._apart:
                self._apart.add(l.id)
            if l.id not in self._lingered:  # (the first time only: parents can meet again and part again)
                self._lingered.add(l.id)
                c = int(np.flatnonzero(last)[0]) if last.any() else 0
                self.events.append({"ago_kyr": round(step.ago, 3), "kind": "lingers", "line": l.id,
                                    "text": f"{l.label()} live on as a people of their own where "
                                            f"{' and '.join(self.tree.lines[q].label() for q in l.parents)} last met",
                                    "lat": round(float(g.lat[c]), 2), "lon": round(float(g.lon[c]), 2)})
        new[new < EST] = 0.0
        self.p[k] = new
        self._linger[k] = (new >= EST) & ~meet

    def _K(self, l, env, tags, step, clip=True):
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
        if l.extinct_kyr is not None:  # dwindles toward its end
            span = min(0.3 * (l.ago_kyr - l.extinct_kyr), 20.0)
            if span > 0 and step.ago < l.extinct_kyr + span:
                K = K * max(0.0, (step.ago - l.extinct_kyr) / span)
        return np.clip(K, 0, 1) if clip else np.maximum(K, 0)

    def _volcanic(self, deep: bool = False):
        """The world's volcanic good for the volcanic place tag (None without a world, and in the deep epochs)."""
        return None if deep or self.goods is None else self.goods.get("volcanic")

    def _land_mult(self, l, holocene: bool) -> np.ndarray | float:
        """What the line's way of life looks for in the land (spec [[use]]; land.goods): x(1 - pull + pull G),
        G the best of its favoured goods here (each at its own pull, spec.Tree.pulls_of), normalised to a mean of 1
        over its country unless a use is strict; x(1 - pull |w| g) per
        avoided good. Before HOLOCENE_KYR only the geology (ores, stone) counts: the farmland, pasture,
        forests and coasts are today's. A line with no favoured good of an epoch is left as it is then."""
        from .land import GOODS
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

    def _mix_ramp(self, ago):
        ms = self.tree.mixing_start_kyr
        return 0.0 if ago >= ms or ms <= 0 else 1 - ago / ms

    def _mixf(self, l):
        """How much the late mixing relaxes a line's competition: 2 (1 - insularity) (1 at 0.5; spec.DEMOGRAPHY)."""
        return 2.0 * (1.0 - l.demo("insularity"))

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


# -- the present ------------------------------------------------------------------------------------
def present_summary(h: History, P: np.ndarray) -> dict:
    g, tree = h.grid, h.tree
    out = {"lines": {}, "mixing_zones": [], "wishes": [], "animals": h.animals.summary(P) if h.animals is not None else None,
           "crops": h.crops.summary(P) if h.crops is not None else None}
    pres = P >= EST
    src, dst = g.nbr_src, g.nbr_idx
    for k, l in enumerate(h.lines):
        sel = pres[k]
        if not sel.any():
            continue
        lab, n = g.components(sel)
        sizes = np.sort(np.bincount(lab[sel], minlength=n))[::-1]
        nb = {}
        for j, m in enumerate(h.lines):
            if j != k and pres[j].any():
                touch = int((sel[src] & pres[j][dst]).sum())
                if touch:
                    nb[m.id] = touch
        tr = h.tracks[l.id][-1] if h.tracks[l.id] else None
        out["lines"][l.id] = {"area_mkm2": round(float(sel.sum() * h.cell_mkm2), 2), "patches": int(n),
                              "largest_patch_share": round(float(sizes[0] / sizes.sum()), 2),
                              "centroid": tr[1:3] if tr else None,
                              "neighbours": dict(sorted(nb.items(), key=lambda x: -x[1])[:8]), "overlay": l.overlay}
        if l.group_of:
            out["lines"][l.id]["group_of"] = l.group_of
        if l.overlay and l.origin == "hybrid":  # (the land it holds as a people of its own, its parents apart)
            out["lines"][l.id]["own_mkm2"] = round(float((h._linger[k] & sel).sum() * h.cell_mkm2), 2)
        # numbers: the people (presence x density x area), by present-day landmass
        pc = h.population(k, P)
        lm = h.cross.label
        by = np.bincount(lm[(lm >= 0) & (pc > 0)], weights=pc[(lm >= 0) & (pc > 0)], minlength=len(h.cross.names))
        top = np.argsort(-by)[:6]
        d = l.demos()
        out["lines"][l.id].update(population=int(pc.sum()), density=round(d["density"], 4),
                                  band_km2=round(SP.BAND / d["density"], 1),
                                  by_landmass={str(int(m)): int(by[m]) for m in top if by[m] >= 1},
                                  faded_patches=h.faded.get(l.id, 0))
    natives = np.array([not l.overlay and not l.marine for l in h.lines])  # (the land peoples: the sea ones do not mix or hold land)
    Pw = h.rollup(np.where(natives[:, None], P, 0))  # (peoples as wholes: a people mixing with its own groups is one people)
    mix = (Pw >= 0.25).sum(0) >= 2
    env = h.steps[-1].get()
    tags = _tags(g, env, h._chains, h._volcanic())
    corr = corridor(tags, env, h.flow)
    land = tags["land"]
    out["mixing"] = {"area_mkm2": round(float(mix.sum() * h.cell_mkm2), 2),
                     "land_share": round(float(mix[land].mean()), 3) if land.any() else 0.0,
                     # share of corridor land (contact >= 0.7) and of closed land (< 0.4) that is mixed
                     "in_corridors": round(float(mix[land & (corr >= 0.7)].mean()), 3) if (land & (corr >= 0.7)).any() else None,
                     "corridor_share": round(float((corr[land] >= 0.7).mean()), 3) if land.any() else 0.0,
                     "in_closed": round(float(mix[land & (corr < 0.4)].mean()), 3) if (land & (corr < 0.4)).any() else None}
    held = (np.where(natives[:, None], P, 0) >= EST).any(0)
    lm = h.cross.label
    out["landmasses"] = [{**nm, "held_share": round(float(held[(lm == nm["rank"]) & land].mean()), 2)
                          if ((lm == nm["rank"]) & land).any() else 0.0}
                         for nm in h.cross.names if nm["area_mkm2"] >= 0.05][:30]
    out["empty_continents"] = [nm["name"] for nm in out["landmasses"] if nm["kind"] == "continent" and nm["held_share"] < 0.05]
    # who found each landmass first (any native people, at its origin or on arrival), and who came after
    for nm in out["landmasses"]:
        arr = sorted(((r["ago_kyr"], lid, r) for lid, got in h.cross.reached.items()
                      for m, r in got.items() if m == nm["rank"] and not h.tree.lines[lid].overlay), key=lambda x: -x[0])
        nm["discovered"] = ({"by": arr[0][1], "ago_kyr": arr[0][0], "how": arr[0][2]["how"],
                             **({"gap_km": arr[0][2]["gap_km"]} if "gap_km" in arr[0][2] else {})} if arr else None)
        # (the first of today's peoples to get there: the stems found most land in deep time)
        now = [x for x in arr if x[1] in out["lines"]]
        nm["settled_by"] = ({"by": now[0][1], "ago_kyr": now[0][0], "how": now[0][2]["how"],
                             **({"gap_km": now[0][2]["gap_km"]} if "gap_km" in now[0][2] else {})} if now else None)
        nm["arrivals"] = [{"by": lid, "ago_kyr": a, "how": r["how"]} for a, lid, r in arr[:12]]
        nm["population"] = {lid: v["by_landmass"][str(nm["rank"])] for lid, v in out["lines"].items()
                            if str(nm["rank"]) in v.get("by_landmass", {})}
    lab, n = g.components(mix)
    for z in range(n):
        sel = lab == z
        if sel.sum() < 3:
            continue
        who = [l.id for k, l in enumerate(h.lines) if natives[k] and (Pw[k][sel] >= 0.25).mean() > 0.2]
        c = g.centers[sel].mean(0)
        c /= np.linalg.norm(c)
        out["mixing_zones"].append({"cells": int(sel.sum()), "area_mkm2": round(float(sel.sum() * h.cell_mkm2), 2),
                                    "lat": round(float(np.degrees(np.arcsin(c[2]))), 1),
                                    "lon": round(float(np.degrees(np.arctan2(c[1], c[0]))), 1), "lines": who})
    out["mixing_zones"].sort(key=lambda z: -z["cells"])
    out["mixing_zones"] = out["mixing_zones"][:20]
    out["wishes"] = wish_scores(h, P, tags)
    out["peoples"] = people_rollup(h, P, out["lines"])
    # lines that should be alive at the present (leaves not set to die out) but aren't
    out["lost"] = [l.id for l in tree.leaves() if l.extinct_kyr is None and l.id not in out["lines"]]
    # (an 'apart' wish whose niches rarely meet has nothing to keep apart: left out of the average, PW-682;
    # wish_score_raw: every wish, an 'apart' scored as 1 - closeness, as before)
    cw = [w for w in out["wishes"] if w.get("contested", True)]
    out["wish_score"] = round(sum(w["score"] * w["weight"] for w in cw) / max(sum(w["weight"] for w in cw), 1e-9), 3) if cw else None
    out["wish_score_raw"] = round(sum(w.get("raw", w["score"]) * w["weight"] for w in out["wishes"]) /
                                  max(sum(w["weight"] for w in out["wishes"]), 1e-9), 3) if out["wishes"] else None
    out["wishes_counted"] = len(cw)
    return out


def people_rollup(h: History, P: np.ndarray, lines: dict) -> dict:
    """Per people with groups (PW-665): the people as a whole, its own row and its groups' rows together:
    area and patches of their joint range, population and by-landmass numbers summed, each part's share."""
    out = {}
    g = h.grid
    for l in h.lines:
        gs = h.tree.groups_of(l.id)
        if not gs:
            continue
        parts = [x for x in [l.id, *gs] if x in lines]
        if not parts:
            continue
        sel = h.whole(l.id, P) >= EST
        _, n = g.components(sel) if sel.any() else (None, 0)
        pop = sum(lines[x].get("population", 0) for x in parts)
        by: dict[str, int] = {}
        for x in parts:
            for m, v in lines[x].get("by_landmass", {}).items():
                by[m] = by.get(m, 0) + v
        out[l.id] = {"groups": gs, "living": parts, "area_mkm2": round(float(sel.sum() * h.cell_mkm2), 2),
                     "patches": int(n), "population": int(pop),
                     "by_landmass": dict(sorted(by.items(), key=lambda x: -x[1])[:6]),
                     "shares": {x: round(lines[x].get("population", 0) / max(pop, 1), 3) for x in parts}}
    return out


def _within(g, mask: np.ndarray, cell_km: float) -> np.ndarray:
    """Cells within NEAR_SCORE_KM of the mask."""
    near = mask.copy()
    for _ in range(max(1, int(round(NEAR_SCORE_KM / cell_km)))):
        near = near | _nbr(np.logical_or, near[g.nbr_idx], g)
    return near


def _niche_closeness(h: History, w, tags: dict) -> float:
    """Share of a's habitat (own niche at the present, K >= 0.25, its groups' too) within NEAR_SCORE_KM of b's
    habitat: how close the two would sit with no wish and no competition."""
    env = h.steps[-1].get()

    def hab(lid):
        ids = [lid, *h.tree.groups_of(lid)]
        return np.any([capacity(h.tree.lines[x], env, tags) >= 0.25 for x in ids], axis=0) & (tags["land"] | tags["sea"])
    ha, hb = hab(w.a), hab(w.b)
    if not ha.any() or not hb.any():
        return 0.0
    return float(_within(h.grid, hb, h.cell_km)[ha].mean())


def wish_scores(h: History, P: np.ndarray, tags: dict | None = None) -> list[dict]:
    g = h.grid
    if tags is None:
        tags = _tags(g, h.steps[-1].get(), h._chains, h._volcanic())
    out = []
    for w in h.tree.wishes:
        a = h.whole(w.a, P) >= EST  # (a people with groups: as a whole)
        if not a.any():
            out.append({**vars(w), "score": 0.0, "note": "a is gone"})
            continue
        if w.want in SP.PLACES:
            # half: how much of that kind of place the line holds (half of it is full marks); half: how much
            # of its range is there, against how common the place is (8x its share of the land, at most 1/2)
            t = tags[w.want] & tags["land"]
            if not t.any():
                out.append({**vars(w), "score": 0.0, "note": f"no {w.want} on this world"})
                continue
            base = t.sum() / max(tags["land"].sum(), 1)
            cover, share = float(a[t].mean()), float(t[a].mean())
            s = 0.5 * min(1.0, cover / 0.5) + 0.5 * min(1.0, share / min(0.5, 8 * base))
        else:
            b = h.whole(w.b, P) >= EST
            near = _within(g, b, h.cell_km)
            close = float(near[a].mean()) if b.any() else 0.0
            if w.want == "near":
                s = min(1.0, 2.5 * close)
                # (PW-699: as 'apart', a 'near' wish counts only where the two niches can reach each other)
                base = _niche_closeness(h, w, tags)
                if base < APART_CONTESTED:
                    out.append({**vars(w), "score": round(s, 3), "baseline": round(base, 3), "contested": False, "raw": round(s, 3),
                                "note": "niches rarely meet: not counted"})
                    continue
                out.append({**vars(w), "score": round(s, 3), "baseline": round(base, 3), "contested": True, "raw": round(s, 3)})
                continue
            else:
                # apart: against what the niches alone would give (the share of a's habitat within reach of b's
                # habitat, both before competition); a pair whose niches hardly meet has nothing to keep apart
                base = _niche_closeness(h, w, tags)
                if base < APART_CONTESTED:
                    out.append({**vars(w), "score": round(1.0 - close, 3), "baseline": round(base, 3), "contested": False, "raw": round(1.0 - close, 3),
                                "note": "niches rarely meet: not counted"})
                    continue
                s = float(np.clip(1.0 - close / base, 0.0, 1.0))
                out.append({**vars(w), "score": round(s, 3), "baseline": round(base, 3), "contested": True, "raw": round(1.0 - close, 3),
                            "closeness": round(close, 3)})
                continue
        out.append({**vars(w), "score": round(s, 3)})
    return out


def simulate(tree: SP.Tree, ps: R.Pass, tries: int = 4, progress=lambda f, msg: None,
             goods: dict | None = None) -> tuple[History, dict, dict]:
    """Best of `tries` seeds by the wishes' score, less LOST_PENALTY per living line lost (e.g. a contact
    hybrid whose parents no longer meet); one try without wishes."""
    best = None
    n = tries if tree.wishes else 1
    scores, tstats = [], []
    for k in range(n):
        progress(k / n, f"try {k + 1}/{n}: recent pass: full climates (kept on disk after the first run)")  # (History.__init__ makes them; PW-743)
        h = History(tree, ps, tree.seed * 1000 + k, goods=goods)
        res = h.run(lambda f, msg, k=k: progress((k + f) / n, f"try {k + 1}/{n}: {msg}"))
        pres = present_summary(h, res["present"])
        sc = pres["wish_score"] if pres["wish_score"] is not None else 0.0
        scores.append(round(float(sc), 3))
        fs = res["frames"][-1]["stats"] if res.get("frames") else {}  # (the present frame; PW-707)
        tstats.append({"wish_score": round(float(sc), 3), "lost": len(pres["lost"]),
                       **{q: fs.get(q) for q in ("empty_land_pct", "two_plus_pct", "lead_share_mean_pct")}})
        key = sc - LOST_PENALTY * len(pres["lost"])  # (a try that keeps every living line is preferred)
        if best is None or key > best[3] + 1e-9:
            best = (h, res, pres, key)
    best[2]["tries"] = scores
    best[2]["try_stats"] = tstats
    best[2]["tries_mean"] = {q: round(float(np.mean([t[q] for t in tstats if t[q] is not None])), 3)
                             for q in ("wish_score", "empty_land_pct", "two_plus_pct", "lead_share_mean_pct")
                             if any(t[q] is not None for t in tstats)}
    return best[:3]
