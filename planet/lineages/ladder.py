"""The density ladder (PW-1275, owner rulings PW-1350): a people's density per cell from how it lives there, what it knows and how
rich the land is, times a small kind factor. Nothing here knows a people's name.

    density(cell) = kind x sum over the ways of life of (the share of the people living that way there) x (that way's rung there)

**Published ranges (PW-1383).** Where a rung's number has a published range, ranges.py holds it beside its source (and lists what has none),
and `meta.draw_ranges = true` draws the number from it, seeded by the peoples seed (Ladder.v, Ladder.drawn). Off by default: the constants
below are used as they are.

**The rungs** (docs/review/peoples/density-ladder/ladder.md has every source, read in lane 130 and re-checked). Each rung's number is
the people's *mean* over the land it holds at the reference land quality (Q1 A), so a rung reads a land layer:
(layer / reference) ** power, power 1.3 for foragers (Binford's fit, Q3 C) and 1.0 elsewhere.

| rung | number at the reference | reads | source (ladder.md) |
|---|---|---|---|
| forager | 0.036 /km2 at NPP 330 | total NPP ** 1.3 | Binford 2001 Table 5.01 via D-PLACE, terrestrial fit log10 d = -4.42 + 1.26..1.28 log10 NPP |
| fisher (fishing foragers) | 1.2 x the fish good (0..1) | the fish good | Binford sedentary: median 0.41, top tenth 1.2 |
| garden | 5 at NPP 330 | NPP | Boserup forest/bush fallow 0-4 / 4-64; PNG 5-40 by land quality (all PNG 9-11) |
| plough (rain-fed), by stage | 8 / 14 / 25, at most 35 a cell (Q7 A) | NPP | E. Bronze Age Greece 2.5-14; Roman Rhineland 10.8-17.9; England 13 (1086) to 35 (1315-48) |
| irrigation | 30 -> 240 per watered km2 | water reach | Butzer 1976 Table 4: Nile valley 30 (4000 BC) to 240 (150 BC) |
| pastoral nomad | 0.8 at grazing NPP 263 | grazing NPP | Mongolia 0.35-0.54; Kenya modelled 1-2; Khazanov |
| agro-pastoral | the mix of the two (a cell both farmed and herded) | | Wilson 1986 6-14; Kalff 1-2 to ~200 |
| hold (dwarves) | the valleys' farming rung x trade, + mushrooms | | Q6 A: trade a placeholder until trade exists |

**Who lives which way where (Q2 A): the land decides.** Once a people knows cultivation (it has taken up a staple crop, crops.py),
its farmable cells farm (the share FARM_SHARE of the fertile good); once it knows herding (a herd animal, animals.py), grazing land
outside the fields is herded; the rest stays foraging (or fishing where the waters are rich). So foragers persist on marginal land
and farmers spread with the knowledge. **Rich wild land resists farming (PW-1385 A):** where the wild feeds well above the land's
ordinary foraging (rich waters), a people farms only part of the farmable land, taking up more of it over the millennia it has known
crops (rich_keep); the richest waters stay with foragers and fishers, as on the salmon and estuary coasts of North America. Herding
takes the grazing land where it feeds more people than the wild there (herd_keep). Knowing is slower for kinds little inclined to farm (PW-1373 B): a crop must stand on a fifth of
a people's land for crops.LAG_KYR / its propensity before the people takes it up (hunters ~10x slower than farmers; meat-eaters lean
to herds, animals.DIET_LEAN). Den peoples farm at DEN_FARM_W of that (rare, not forbidden, Q4 A).

**Tech stage, inside the history.** The history does not run the tech tree (techtree.py reads the run afterwards), so the stages are
read from what the history knows: cultivation (a crop taken up), herding (a herd animal), the plough (a plough animal, as
growth.py's agrarian era), and the time since then on the tree's own Earth dates (techtree.toml: plough 6.5 kyr, iron 3.3,
three-field 1.2: the iron rung PLOUGH_STEPS[1] kyr after the plough, the medieval PLOUGH_STEPS[2]; irrigation IRR_LAG after
cultivation, cultivation 11.5 against irrigation 8), capped by the tree's era (meta.era). A proxy until the tech tree runs in step.

**Den peoples (Q4 A).** Goblins, kobolds, troglodytes: the forager rung x kind 1.2, plus a raiding share r of their food that grows
with the farmers' and herders' density within reach, capped (RAID_*): density = forager / (1 - r). Their dens follow the rock
(PW-1382, den_thin): x1 on the best den ground (caves, rock shelters, ground to dig: dens.py), x0.5 where there is none, a preference
and never a range limit (Daniel 11-02).
**Foragers who trade with farmers (PW-1386).** A forager people (it knows no crops; not a den people or a hold) living near farmers
gets up to BARTER_CAP of its foraging food from them, more the denser the farmers within reach (BARTER_*): its foraging rung /
(1 - b), as Congo Basin foragers trade meat, forest goods and labour for farm food (docs/review/peoples/forager-trade/round1.md).
**Dwarven holds (Q6 A).** A people that mines and lives underground (traits `miner` and `subterranean`) farms its valleys at the
farming rung (terraces: the plough rung's stage TERRACE_LAG after it cultivates, without a plough animal), buys food with ore and
craft up to TRADE_CAP of what it eats (a placeholder until trade exists) and adds MUSHROOM_X from its crop waste.
"""

from __future__ import annotations

import numpy as np

from . import ranges as RG
from .gridops import nbr_reduce
from .spread import EST

NPP_REF = 330.0  # g C/m2/yr: the land quality at which a rung stands at its number (prey.NPP_REF: the farmers' reference before)
GRAZE_REF = 263.0  # grazing NPP, g C/m2/yr, likewise for herders (prey.GRAZE_REF)
FORAGER = 0.036  # /km2 at NPP_REF: Binford 2001 Table 5.01 (D-PLACE B008) terrestrial foragers' fit (ladder.md, binford_by_npp.py)
FORAGER_POW = 1.3  # Q3 C: the fit's slope, 1.26-1.28
FISH_TOP = 1.2  # /km2 where the fish good is 1: Binford's sedentary foragers' top tenth (median 0.41: a fish good of ~0.47)
FISH_MIN = 0.2  # the fish good under which the waters feed no fishing rung (rich waters only, Kelly p. 46; a judgement: ~a third of land cells pass)
GARDEN = 5.0  # /km2 at NPP_REF: Boserup's forest fallow top / bush fallow low (4), PNG's very-low to low land 5-7 (a judgement inside them)
PLOUGH_STEPS = (0.0, 3.2, 5.3)  # kyr after the plough: bronze, iron (Roman), medieval three-field (techtree.toml: 6.5 / 3.3 / 1.2 kyr ago)
PLOUGH = (8.0, 14.0, 25.0)  # /km2 at NPP_REF: E. Bronze Age Greece 2.5-14 (middle), Roman Rhineland 10.8-17.9, England 13 (1086) to 35 (peak)
PLOUGH_TOP = 35.0  # Q7 A: no cell farms denser than England's medieval peak (35-36 /km2, Broadberry et al. 2011)
NOMAD = 0.8  # /km2 at GRAZE_REF: inside Mongolia 0.35-0.54 and Kenya's modelled 1-2 (the human nomads' number before)
IRR_LAG = 3.5  # kyr from cultivation to irrigation (techtree.toml: cultivation 11.5, irrigation 8)
IRR_STEPS = (0.0, 1.0, 1.5, 2.2, 2.75, 3.85)  # kyr after irrigation, Butzer Table 4's dates (4000, 3000, 2500, 1800, 1250, 150 BC)
IRR = (30.0, 75.0, 130.0, 140.0, 180.0, 240.0)  # people per watered km2 at those dates (Butzer 1976 Table 4, "hypothetical")
WATER_FLOW = (5.0, 200.0)  # river flow (world layer `flow`) from which a cell has a floodplain to water, to the greatest rivers' (a
# judgement: on the L6 worlds ~15% of land cells carry 5 or more, the top 1% ~120)
WATER_MAX = 0.3  # the share of a cell water reaches on the greatest rivers (a judgement: a 10-20 km valley in a ~60 km cell)
FARM_FULL = 0.5  # the fertile good at which all of a cell farms (a judgement: half the world's best farmland class)
DEN_FARM_W = 0.1  # Q4 A: a den people farms at this share of what another people would (rare, not forbidden; a judgement)
TERRACE_LAG = 6.5  # kyr from cultivation to terraces (techtree.toml: cultivation 11.5, terracing 5): a hold's plough-stage valleys
TRADE_CAP = 0.5  # Q6 A: a hold buys at most this share of its food (a placeholder until trade exists)
TRADE_FULL = 0.6  # the ore good (best of the metal goods) at which a hold buys its full TRADE_CAP
MUSHROOM_X = 0.1  # mushrooms on crop waste: ~520 kcal a kg of straw against 1,800-2,600 in a kg of wheat (ladder.md); a small bonus
RAID_CAP = 0.3  # the most of a den people's food raiding gives. No measured share was found; the sources read (ladder.md, "Raiding")
# make raiding a top-up to a foraging or herding base: "For men, raiding approaches hunting in economic significance" (Opler 1941 p. 332,
# Chiricahua); Western Apache meat, raided stock included, ~35% of the diet (Encyclopedia of World Cultures, secondary); "an important
# supplementary means of livelihood", "too unreliable" to live on (Khazanov 1994 pp. 221-222). 0.3: under that meat share (a judgement)
RAID_HALF = 5.0  # farmers' and herders' people/km2 within reach at which raiding gives half its cap (a judgement: a gardening
# village country; raids on herders or foragers like themselves only swap herds back and forth, Khazanov p. 155, so the share follows
# the settled density, near 0 among foragers)
RAID_REACH = 2  # cells (neighbour rings) a den people raids over
# PW-1386: foragers who trade with farmer neighbours (docs/review/peoples/forager-trade/round1.md has the sources and the quotes). A
# forager people (one that knows no crops, not a den people or a hold) gets a share b of its foraging food from farmers within reach,
# for meat, forest goods and labour: its foraging rung / (1 - b), b = BARTER_CAP x farmers near / (farmers near + BARTER_HALF). The
# rich-land and herding choices read the land's own wild, never the bartered top-up.
BARTER_CAP = 0.5  # the most of its foraging food a forager people gets from farmers. Congo Basin foragers living with farmers: "more than
# 60 % of total food weight on farm products" (Mbuti, Ichikawa 1983 p. 55); in the forest camps 11-63% of energy from farm food, "about 50%"
# for most groups (Kitanishi 1995 p. 106 and Table 11, p. 107: Mbuti 11 and 63, Efe 41 and 34, Aka 11, oil palm apart); Aka of Lobaye 55%
# of meal items (Bahuchet 1988, via Kitanishi p. 107). 0.5: the "about 50%", under the Mbuti's 60% by weight
BARTER_HALF = 5.0  # farmers' people/km2 within reach at which the share is half its cap (a judgement, as RAID_HALF: a gardening village
# country; no source relates the share to the farmers' density. The one relation found is distance: Aka camps 3-4 hours' walk from the
# village eat more farm food than camps 5-8 hours away, Bahuchet 1988 via Kitanishi 1995 p. 107; and with no farmers near the share is 0,
# as on the Baka's months-long molongo, "solely on wild food resources", Yasuoka 2004 p. 36)
BARTER_REACH = 1  # cells (neighbour rings) a forager people trades over (those camps are within a day's walk: one ring of ~60 km cells)
REFRESH_KYR = 0.5  # the ladder is redone at least this often in the recent epochs (raids and the plough's stage move with time)
ERA_STAGE = {"stone age": -1, "bronze age": 0, "classical": 1, "medieval": 2, "renaissance": 2, "industrial": 2}  # the plough stage an era allows
RUNGS = ("forager", "fisher", "garden", "plough", "irrigation", "nomad", "agro_pastoral", "hold", "raider")
# PW-1385 A, rich wild land resists farming (docs/review/peoples/density-ladder/rich-foragers.md has the sources). A cell's richness
# = its wild rung over the land's own forager rung, never taken below the usual forager level FORAGER (so poor land's rivers do not read
# as rich; 1 off rich waters). Of its farmable share a people knowing crops farms
# 1 / (1 + x^RICH_POW), x = (richness - 1) / (RICH_HALF x (1 + years it has known crops / RICH_T)).
RICH_HALF = 3.0  # the excess richness half farmed when crops are new (a judgement on the cases: Calusa ~0.8/km2 over a whole domain
# (Worth 2006), ~7x the forager fit there, still unfarmed ~0.55 kyr after maize next door; Ertebolle beside farming ~1 kyr, then farmed)
RICH_T = 1.0  # kyr over which that half point grows by RICH_HALF (Ertebolle ~1 kyr beside farmers, Gron NSF; Yayoi rice reached
# southern Tohoku ~0.6 kyr after Kyushu, Mizoguchi): moderately rich land farms within ~1-1.5 kyr, the richest waters hold for millennia
RICH_POW = 2.0  # the steepness (a judgement: from 90% to 10% farmed across a ninefold richness)
KNOWN_STEP, KNOWN_CAP = 0.5, 15.0  # kyr: the years a people has known crops, in steps (redo a line only when they move) and capped
HERD_POW = 2.0  # PW-1385: herding goes where it feeds more people than the wild, smoothly (a judgement: half where they feed the same)
FREE_RANGING = 0.8  # (the kind factor the dnd preset gives free-ranging kinds, leonin and tabaxi; den peoples 1.2: samples/dnd.toml)


def ref_density(l) -> float:
    """A line's density before the ladder has run (the deep epoch, a run without a world): a forager's, or a fisher's at the median of
    Binford's sedentary foragers (0.41) for the sea peoples and fisher ways, both at the reference land; megafauna: none here."""
    if l.marine or l.way in ("fisher_forager", "sea_nomad"):
        return 0.41
    return FORAGER


def is_den(l) -> bool:
    """A den people (Q4 A: goblins, kobolds, troglodytes): the `denning` trait."""
    return "denning" in l.traits


def den_thin(l, fit: np.ndarray) -> np.ndarray:
    """PW-1382 (Daniel 11-02: den peoples prefer den ground, never rely on it): a line's density factor per cell from the den ground
    `fit` (0..1, the `den` good: caves, rock shelters, ground to dig; dens.py): x1 on the best, x(1 - its `den` trait) where there is
    none (the `denning` trait: 0.5), so a den people keeps half its density on poor ground. 1 for every other line. Its habitat (where it
    can live) never reads this."""
    return 1.0 - l.trait("den", 0.0) * (1.0 - fit)


def is_hold(l) -> bool:
    """A people of holds (Q6 A): miners living underground (dwarves)."""
    return "miner" in l.traits and "subterranean" in l.traits


def rich_keep(rich: np.ndarray, known: float, rich_t: float | None = None) -> np.ndarray:
    """PW-1385 A: the part of a cell's farmable share a people that has known crops for `known` kyr farms, from how rich the wild is
    there over ordinary foraging (rich = the wild rung / the land's own forager rung, at least FORAGER: 1 where nothing is richer than plain
    foraging). 1 on ordinary land; half where the excess richness is RICH_HALF x (1 + known / RICH_T); less beyond, as its RICH_POW
    power. So rich land takes up farming slowly, and the richest waters stay with foragers or fishers for millennia."""
    x = np.maximum(rich - 1.0, 0.0) / (RICH_HALF * (1.0 + max(known, 0.0) / (RICH_T if rich_t is None else rich_t)))
    return 1.0 / (1.0 + x ** RICH_POW)


def herd_keep(nomad: np.ndarray, wild: np.ndarray) -> np.ndarray:
    """PW-1385: the part of a cell's grazable share a people that knows herding herds: whichever of herding and foraging feeds more
    there, smoothly (half where they feed the same; HERD_POW the steepness; rich_foragers.md)."""
    a, b = nomad ** HERD_POW, wild ** HERD_POW
    return a / np.maximum(a + b, 1e-30)


def _interp_stage(t: float, steps, vals) -> float:
    return float(np.interp(t, steps, vals))


class Ladder:
    """Per line, the density per cell and the ways of life, from the world's layers and what each people knows."""

    def __init__(self, h):
        self.h = h
        ps, goods = h.ps, h.goods
        self.ok = goods is not None and getattr(ps, "npp", None) is not None and getattr(ps, "graze_npp", None) is not None
        L = len(h.lines)
        n = h.grid.n
        self.den = np.array([is_den(l) and not l.megafauna for l in h.lines])
        self.hold = np.array([is_hold(l) and not l.megafauna for l in h.lines])
        self.people = np.array([not (l.megafauna or l.overlay) for l in h.lines])
        self.thin = np.ones((L, n)) if self.ok else None  # (PW-1382: a den people's density follows the den ground: den_thin)
        self.state: dict[int, tuple] = {}
        # (PW-1383: the ranged numbers. The module constants are the fixed values; with meta.draw_ranges each is drawn from its published
        # range, seeded by the peoples seed: ranges.py. self.drawn holds the draws ({} when off), recorded in the run's metadata)
        self.v = {"forager_pow": FORAGER_POW, "fish_top": FISH_TOP, "garden": GARDEN, "plough": tuple(PLOUGH), "nomad": NOMAD, "rich_t": RICH_T}
        self.drawn: dict[str, float] = {}
        if getattr(h.tree, "draw_ranges", False):
            d = self.drawn = {k: round(x, 6) for k, x in RG.draw(h.tree.seed).items()}
            self.v.update(forager_pow=d["forager_pow"], fish_top=d["fish_top"], garden=d["garden"], nomad=d["nomad"], rich_t=d["rich_t"],
                          plough=(d["plough_0"], d["plough_1"], d["plough_2"]))
        self.last = None
        self.era_stage = ERA_STAGE.get(h.tree.era, 2)
        self.rung = np.zeros((L, n), np.int8) if self.ok else None  # (each line's main rung per cell, RUNGS index)
        self.sh = {k: np.zeros((L, n)) for k in ("farm", "herd")} if self.ok else None  # (its ways' shares per cell: landuse)
        self.raid = np.zeros((L, n)) if self.ok else None
        self.barter = np.zeros((L, n)) if self.ok else None  # (PW-1386: the part of each cell's food a forager people trades for)
        self._fn = None  # (PW-1386: the farmers near at the last due refresh)
        if not self.ok:
            return
        self.fa = np.maximum(np.asarray(ps.npp, float), 0.0) / NPP_REF
        self.fg = np.maximum(np.asarray(ps.graze_npp, float), 0.0) / GRAZE_REF
        self.ff = np.clip(np.asarray(goods.get("fish", np.zeros(n)), float), 0, 1)
        self.farmable = np.clip(np.asarray(goods["fertile"], float) / FARM_FULL, 0, 1)
        self.grazable = np.clip(np.asarray(goods["grazing"], float) / FARM_FULL, 0, 1)
        ore = np.zeros(n)
        for g in ("metal", "iron", "copper", "gold", "gems", "mithril"):
            if g in goods:
                ore = np.maximum(ore, np.asarray(goods[g], float))
        self.trade = TRADE_CAP * np.clip(ore / TRADE_FULL, 0, 1)
        if "den" in goods:
            fit = np.clip(np.asarray(goods["den"], float), 0.0, 1.0)
            for k, l in enumerate(h.lines):
                if not l.megafauna:
                    self.thin[k] = den_thin(l, fit)
        flow = getattr(ps, "flow", None)
        if flow is None:
            self.water = np.zeros(n)
        else:
            f = np.log10(np.maximum(np.asarray(flow, float), 1e-6) / WATER_FLOW[0]) / np.log10(WATER_FLOW[1] / WATER_FLOW[0])
            self.water = WATER_MAX * np.clip(f, 0, 1)

    # -- what a people knows ----------------------------------------------------------------------
    def tech(self, k: int, ago: float) -> tuple:
        """(knows cultivation, knows herding, plough stage level 0..2 as a float or -1, irrigation kyr since or -1, kyr since it knew
        cultivation in KNOWN_STEP steps up to KNOWN_CAP, 0 if not), from the history's crops and animals."""
        h = self.h
        cult = herd = None
        plough = None
        if h.crops is not None:
            ts = [s.took_up[k] for s in h.crops.stocks if k in s.took_up]
            cult = max(ts) if ts else None
        if h.animals is not None:
            hs = [s.took_up[k] for s in h.animals.stocks if k in s.took_up and s.a.k.get("herd", 0) > 0]
            herd = max(hs) if hs else None
            ps = [min(s.took_up[k], s.a.plough[0]) for s in h.animals.stocks if k in s.took_up and s.a.plough and ago <= s.a.plough[0]]
            plough = max(ps) if ps else None
        if cult is not None and self.hold[k]:  # (a hold's terraces stand for the plough)
            plough = max(plough or -1e9, cult - TERRACE_LAG) if cult - TERRACE_LAG >= ago else plough
        lvl = -1.0
        if plough is not None and cult is not None and self.era_stage >= 0:
            lvl = min(float(np.interp(plough - ago, PLOUGH_STEPS, (0.0, 1.0, 2.0))), float(self.era_stage))
        irr = -1.0
        if cult is not None and self.era_stage >= 0 and cult - IRR_LAG >= ago:
            irr = cult - IRR_LAG - ago
        q = lambda x: round(x * 4) / 4  # noqa: E731  (quarter steps: redo a line only when its tech moves)
        known = round(min(cult - ago, KNOWN_CAP) / KNOWN_STEP) * KNOWN_STEP if cult is not None else 0.0
        return (cult is not None, herd is not None, q(lvl), q(irr) if irr >= 0 else -1.0, known)

    # -- the rungs per cell -----------------------------------------------------------------------
    def line(self, k: int, t: tuple, settled_near: np.ndarray | None, farmers_near: np.ndarray | None = None):
        """(density per cell, farm share, herd share, main rung per cell, raid share or None, barter share or None) of line k with tech
        t; settled_near feeds a den people's raids, farmers_near a forager people's trade (PW-1386)."""
        cult, herd, lvl, irr = t[:4]
        known = t[4] if len(t) > 4 else 0.0  # (kyr it has known crops: PW-1385 A)
        v = self.v
        forage = FORAGER * self.fa ** v["forager_pow"]
        fish = v["fish_top"] * np.clip((self.ff - FISH_MIN) / (1.0 - FISH_MIN), 0, 1)
        wild = np.maximum(forage, fish)
        rung_w = np.where(fish > forage, 1, 0).astype(np.int8)
        raid = None
        if self.den[k] and settled_near is not None:
            raid = RAID_CAP * settled_near / (settled_near + RAID_HALF)
            wild = wild / (1.0 - raid)
            rung_w = np.where(raid > 0.1, 8, rung_w).astype(np.int8)
        nomad = v["nomad"] * self.fg
        wild0 = np.maximum(forage, fish)  # (the wild before any raids or trade: what the land itself feeds)
        barter = None
        if self.barters(k, t) and farmers_near is not None:  # (PW-1386: a forager people trades with farmers near)
            barter = BARTER_CAP * farmers_near / (farmers_near + BARTER_HALF)
            wild = np.maximum(forage / (1.0 - barter), fish)
        sf = self.farmable * (DEN_FARM_W if self.den[k] else 1.0) if cult else np.zeros_like(forage)
        if cult:  # (PW-1385 A: rich wild land resists farming)
            sf = sf * rich_keep(wild0 / np.maximum(forage, FORAGER), known, v["rich_t"])
        sh = (1.0 - sf) * self.grazable * herd_keep(nomad, wild0) if herd else np.zeros_like(forage)
        if cult:
            if lvl >= 0:
                rain = np.minimum(_interp_stage(lvl, (0, 1, 2), v["plough"]) * self.fa, PLOUGH_TOP)
                rr = 3
            else:
                rain = v["garden"] * self.fa
                rr = 2
            farm = rain
            if irr >= 0:
                farm = (1.0 - self.water) * rain + self.water * _interp_stage(irr, IRR_STEPS, IRR)
            if self.hold[k]:
                farm = farm / (1.0 - self.trade) * (1.0 + MUSHROOM_X)
        else:
            farm, rr = np.zeros_like(forage), 2
        sw = 1.0 - sf - sh
        d = sf * farm + sh * nomad + sw * wild
        rung = rung_w.copy()
        rung[(sh > sw) & (sh >= sf)] = 5
        main_farm = (sf >= sh) & (sf >= sw) & (sf > 0)
        rung[main_farm] = 7 if self.hold[k] else rr
        if cult and irr >= 0 and not self.hold[k]:
            rung[main_farm & (self.water * _interp_stage(irr, IRR_STEPS, IRR) > (1.0 - self.water) * rain)] = 4
        rung[(sf >= 0.25) & (sh >= 0.25)] = 6
        if barter is not None:  # (the part of each cell's food that is bartered farm food)
            barter = np.where(d > 0, sw * (wild - wild0) / np.maximum(d, 1e-30), 0.0)
        return d, sf, sh, rung, raid, barter

    def barters(self, k: int, t: tuple) -> bool:
        """PW-1386: line k trades with farmer neighbours: a people that knows no crops (t[0]), not a den people (they raid) or a hold."""
        return bool(self.people[k] and not t[0] and not self.den[k] and not self.hold[k] and not self.h.lines[k].marine)

    def farmers_near(self) -> np.ndarray:
        """Farmers' people/km2 per cell, averaged over BARTER_REACH rings of neighbours (PW-1386: whom a forager people trades with)."""
        return self.settled_near(("farm",), BARTER_REACH)

    def settled_near(self, ways: tuple = ("farm", "herd"), reach: int = RAID_REACH) -> np.ndarray:
        """Farmers' and herders' people/km2 per cell, averaged over RAID_REACH rings of neighbours (what a den people raids); `ways` and
        `reach` pick the ways counted and the rings."""
        h = self.h
        P = np.where(h.p >= EST, h.p, 0.0) if getattr(h, "p", None) is not None else None
        s = np.zeros(h.grid.n)
        if P is None or h._dmap is None:
            return s
        for k in np.flatnonzero(self.people & ~self.den):
            if P[k].any():
                s += P[k] * h._dmap[k] * sum(self.sh[w][k] for w in ways)
        g = h.grid
        deg = np.diff(g.nbr_off).astype(float)
        for _ in range(reach):
            s = 0.5 * s + 0.5 * nbr_reduce(g, np.add, s[g.nbr_idx]) / np.maximum(deg, 1)
        return s

    def refresh(self, ago: float, deep: bool, force: bool = False):
        """Redo the lines whose tech moved (and every line each REFRESH_KYR, for the raids and the stages); writes h._dmap and h.dens."""
        h = self.h
        if not self.ok or h._dmap is None:
            return
        due = force or self.last is None or (not deep and self.last - ago >= REFRESH_KYR)
        sn = self.settled_near() if (due and self.den.any() and not deep) else None
        if due:  # (PW-1386: the farmers near, kept between the due refreshes for lines whose tech moves in between)
            self._fn = None if deep else self.farmers_near()
        fn = self._fn
        for k, l in enumerate(h.lines):
            if not self.people[k] or l.marine:
                continue
            t = (False, False, -1.0, -1.0, 0.0) if deep else self.tech(k, ago)
            if not due and self.state.get(k) == t:
                continue
            self.state[k] = t
            d, sf, shd, rung, raid, barter = self.line(k, t, sn if self.den[k] else None, fn)
            h._dmap[k] = h.kx[k] * d * self.thin[k]
            self.sh["farm"][k], self.sh["herd"][k], self.rung[k] = sf, shd, rung
            P = getattr(h, "p", None)
            x = np.where(P[k] >= EST, P[k], 0.0) if P is not None else np.zeros(1)
            if x.any():  # (its one number: the mean over the land it holds, Q1 A; its farm share, people-weighted: growth's eras, counter)
                w = x * h._dmap[k]
                h.dens[k] = float(w.sum() / (x > 0).sum())
                if hasattr(h, "_farm_share") and w.sum() > 0:
                    h._farm_share[k] = float((w * sf).sum() / w.sum())
            if raid is not None:
                self.raid[k] = raid
            self.barter[k] = 0.0 if barter is None else barter
        if due:
            self.last = ago

    def mean_density(self, k: int, P: np.ndarray) -> float:
        """Line k's people over the area it holds (people/km2), at the presences P (0 where it holds nothing)."""
        h = self.h
        x = np.where(P[k] >= EST, P[k], 0.0)
        a = (x > 0).sum()
        return float((x * h.dens_cells()[k]).sum() / a) if a else 0.0

    def by_rung(self, k: int, P: np.ndarray) -> dict:
        """Line k's people and held area per rung: {rung: (share of its people, held Mkm2, people/km2 there)}."""
        h = self.h
        if not self.ok or h._dmap is None:
            return {}
        x = np.where(P[k] >= EST, P[k], 0.0)
        pop = x * h._dmap[k]
        tot = pop.sum()
        out = {}
        for i, nm in enumerate(RUNGS):
            sel = (self.rung[k] == i) & (x > 0)
            if sel.any():
                out[nm] = (round(float(pop[sel].sum() / tot), 4) if tot > 0 else 0.0, round(float(sel.sum() * h.cell_mkm2), 3),
                           round(float(pop[sel].sum() / sel.sum()), 4))
        return out


TABLE = [  # (rung, its number at the reference land, what it reads, the sourced range) for the workbench (viewer/lineages.html)
    ("forager", f"{FORAGER} /km2 at NPP {NPP_REF:g}", f"total NPP ^{FORAGER_POW}", "0.01-0.4 (Binford 2001)"),
    ("fisher", f"{FISH_TOP} x the fish good", "rich waters", "0.1-2, rich coasts to ~9 (Binford; Kelly 2013)"),
    ("garden", f"{GARDEN:g} /km2 at NPP {NPP_REF:g}", "total NPP", "2-20 (Boserup; PNG)"),
    ("plough", " / ".join(f"{v:g}" for v in PLOUGH) + f" /km2 (bronze / iron / medieval), at most {PLOUGH_TOP:g}", "total NPP",
     "2.5-14 bronze age, 11-18 Roman, 13-35 medieval (Butzer; Zimmermann; Broadberry)"),
    ("irrigation", f"{IRR[0]:g}-{IRR[-1]:g} per watered km2", "river reach", "30-240 per watered km2 (Butzer 1976)"),
    ("nomad", f"{NOMAD} /km2 at grazing NPP {GRAZE_REF:g}", "grazing NPP", "0.3-2 (Mongolia; Kenya; Khazanov)"),
    ("agro_pastoral", "fields and herds in one cell", "both", "1-15 (Wilson 1986)"),
    ("hold", f"its valleys' farming x trade (to {TRADE_CAP:g} of its food, placeholder) + {MUSHROOM_X:g} mushrooms", "the valleys", "its valleys' rung"),
    ("raider", f"forager / (1 - raid share), raids to {RAID_CAP:g} of food", "farmers near", "a top-up (Opler 1941; Khazanov 1994)"),
    ("forager, trading", f"forager / (1 - trade share), farm food to {BARTER_CAP:g} of its foraging food", "farmers near",
     "farm food 11-63% of energy, ~50% typical (Ichikawa 1983; Kitanishi 1995)"),
]
