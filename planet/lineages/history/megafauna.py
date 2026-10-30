"""Megafauna as counted animals (PW-924): dragons and the true giants, a handful per pocket of their own country.

Densities (PW-957, PW-963, PW-966; docs/proposals/megafauna-scaling.md, papers in docs/references/megafauna/). Each kind has a
natural density, approached where no people presses it, and a present-day density where peoples do (meta.dragon_km2,
meta.giant_km2). The natural density is a setting, meta.megafauna_natural, with the literature's candidates (owner, 10-28: shown on
the PW-967 review before any is fixed):
- "prey" (default): from the static prey field (lineages.prey: wild herbivores from grazing NPP after overkill, plus livestock),
  taken over a dragon's foraging reach (FORAGE_KM). Dragons on Carbone & Gittleman (2002, Science 295:2273): carnivores per 10 t of
  prey = 89.1 M^-1.05 (M kg; checked against the paper, PDF p. 2, N = 25) at the ecological mass, ~1 per 530 km2 at 1 t/km2 of prey for the base schedule's 3.2 t. Giants as
  mass-scaled foragers (below) x the land's productivity over its median (lineages.prey.productivity, the PW-833 rule).
- "mesotherm": Damuth's law, density = a M^-0.75, on the intercept Marshall et al. (2021, Science 372:284) fit to dinosaurs,
  log10 a = 2.99 (M in g, per km2; checked: Marshall Table 1, p. 284), at the ecological mass, its food spread over every age: ~1 per 65 km2 for the base schedule,
  uniform over the kind's country. Reptile field metabolic rate (Nagy, Girard & Brown 1999, Annu Rev Nutr 19:247, Table 2 p. 260:
  reptiles 0.196 M^0.889, mammals 4.82 M^0.734 kJ/day, M in g; checked) at dragon size is ~0.55 of a mammal's, about the factor
  between this and the mammal-carnivore intercept. Farlow 1993 (Am J Sci 293:167, p. 187) fits reptile density = 66.07 M^-1.01
  per km2 (M kg; Damuth 1987's reptile data plus Komodo dragons, from animals two orders of magnitude lighter), ~1 per 50 km2 at
  3.2 t: the same order as this line.
- "mammal": the same on the mammal-carnivore intercept (log10 a = 2.67): ~1 per 137 km2.
The dragons' ecological mass, stage shares and generation time follow meta.dragon_ages (lineages.dragon_ages, PW-958, PW-959).
Giants under "mesotherm" and "mammal" are uniform mass-scaled foragers: human foragers (~0.1 per km2, the proposal's median, whose source is
not yet found: Hamilton et al. 2007 reuses Binford 2001's data but fits area against group size, not density, and its fit implies
0.03-0.09 per km2 for groups of 25-1000, PNAS 104:4765, Table 1, p. 4767; the M^-0.75 body-mass scaling is Damuth/Kleiber, not
from Hamilton) scaled by M^-0.75 from 65 kg: hill giants (2.2 t) ~1 per 140 km2,
storm giants (7.3 t) ~1 per 345.
The older note here ("an apex hunter two to three orders below the herbivore line", after Carbone & Gittleman) was unsupported:
their carnivore line sits ~1.5 orders below the herbivores'.

Peoples press both down easily (`pressure`, one suppression number: persecution, not hunting). Ripple et al. 2014 (Science
343:1241484, on file) shows the large carnivores pushed back by people (17 of the 31 largest hold on average 47% of their historical
range, from <1% to 73%: tiger 18%, lion 17%; p. 1241484-2 and Table 1); it gives no figure for density against potential, so the
"few percent of their potential" behind the present-day value has no source on file. Where small folk hold the land a kind sits
at the present-day value (`local_density`); where no people holds it, at its natural density. Before the peoples spread they were
many more: the age of dragons (`ages`).
Of these papers Marshall 2021, Carbone & Gittleman 2002, Hamilton et al. 2007, Nagy et al. 1999, Ripple et al. 2014 and Farlow 1993
are on file; Damuth and Binford are cited as the proposal gives them and are not on file (docs/references/megafauna/README.md).

They live long (dragons a few hundred years a generation, giants 50-80 yr), so few of them persist: their patches' viable number
is smaller (History.line_mvp), and pockets within flight or long range of each other are one population (linked_pockets).
They are exempt from the peoples' 300-cell range target and the remnant check: their target is to be present in most of
the world's suitable country for their kind (`suitable_reached`). Breeding is not modelled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .. import prey as PR
from .. import spec as SP
from ..gridops import nbr_reduce
from ..spread import EST, jump_reach, rings
from .habitat import hold_mask

if TYPE_CHECKING:
    from .model import History

LINK_KM = 1500.0  # pockets this close are one population: a dragon's flight, and a giant's roaming too (PW-936: owner ruling that
# giants "just need to be where they need to be", hand-waved placement being fine for megafauna; so the walking giants, hill, cloud
# and frost, roam as far as dragons fly and wade straits, rather than a walker's 800 km JUMP_KM that left their country out of reach)
SUITABLE = 0.5  # a cell is suitable country for a kind where its habitat suitability (History._suit) is at least this
TARGET_SHARE = 0.5  # the target: at least this share of the suitable country lies in patches the kind reaches
COUNTRY = {"wetland": "swamp", "forest": "forest", "jungle": "jungle", "volcanic": "volcano country", "mountain": "mountains",
           "tundra": "tundra", "desert": "desert", "hills": "hills", "coast": "coast", "steppe": "steppe", "island": "island",
           "open": "open country", "shore": "coast", "sea": "sea"}


DAMUTH_EXP = 0.75  # density ~ M^-0.75 (Damuth 1981)
LOG_A = {"mesotherm": 2.99, "mammal": 2.99 - np.log10(2.1)}  # Marshall et al. 2021: log10 of Damuth's intercept (M in g, per km2); checked: Table 1 p. 284, mammal = 2.99 - log10(2.1) from the text
# for dinosaur-like mesotherms, and for mammal carnivores (2.1x lower, the proposal's table)
NATURAL = SP.MEGAFAUNA_NATURAL  # meta.megafauna_natural: food (the default, PW-990 B) | prey | mesotherm | mammal
NATURAL_DEFAULT = SP.MEGAFAUNA_NATURAL_DEFAULT
CARBONE_A, CARBONE_B = 89.1, 1.05  # Carbone & Gittleman 2002: carnivores per 10,000 kg of prey = 89.1 M^-1.05, M in kg (checked: PDF p. 2)
OFFTAKE = 0.1  # the share of the wild herds' standing biomass a predator can take a year and keep them (PW-967's rough figure, ~10%/yr). Bounded
# by Farlow 1993 (Am J Sci 293:167): prey biomass turnover = 0.94 M^-0.28 per yr (M kg; eq. 6, p. 172, from Farlow 1990), 0.26 / 0.17 /
# 0.14 per yr for 100 / 500 / 1000 kg prey, is what every predator together could take; real big predators get less (prey:predator
# 100:1-200:1 in modern large-mammal faunas against his 50:1 best case, p. 176). 0.1 sits inside that; the value itself is a judgement
STOCK_TOLERABLE = 0.1  # the share of herders' stock the herders tolerate losing a year to dragons before they leave the range (UNVERIFIED; a model
# assumption: herds turn over at ~15-25%/yr (Farlow 1993's eq. 6, p. 172, gives 0.17/yr for 500 kg animals), so a tenth lost is a bad
# year they put up with, PW-977; the herders' tolerance itself is to be sourced)
BUDGET = True  # PW-977 stage 2: the peoples' hunters, the giants and the rest of the predator guild draw on the wild offtake before the dragons do (off only to measure it: the dragons then get all of it, stage 1)
PERSON_KCAL_YR = 2200.0 * 365.0  # a person's food, kcal a year (a working adult's ~2,200 kcal a day; the proposal's Kleiber x 1.7 figure for a 65 kg forager is ~1,900; UNVERIFIED round number)
HEAD_KCAL = 625e3  # edible kcal in a head of cattle-sized prey (the proposal's figure, as giant_cattle_yr; it also serves wild game of that size). Cross-check: at
# Farlow 1993's 7 kJ per g live mass (p. 172) a 0.5 t head (prey.HEAD_T) holds ~840,000 kcal, so 625,000 is ~3/4 of it eaten
WILD_MEAT = (0.5, 0.05)  # the share of a people's food that is wild game: (a forager's, any other way's). UNVERIFIED round numbers, no source on file: a
# forager eats much of its food as game, herders, farmers and gardeners hunt little (the ethnographic figure is wanted; inbox draft)
# Carbone, Turvey & Bielby 2011, Proc R Soc B 278:2682 (PDF p. 2683-2684, Fig. 1 and Table 1; read 10-29): the carnivorous theropod guild of Late Cretaceous North America by
# size class, as the share of the guild's individuals (their abundances follow the mammalian carnivore line N ~ 1.97 M^-0.88, their Table 3): 20.6 kg 79.9%, 58.3 kg 19.0%, 1,123 kg
# 0.9%, 5,347 kg 0.1%. They give the abundance, not the food; the guild's food by class is that times a metabolic M^0.75 (Kleiber; the exponent is not from the paper).
GUILD_CLASSES = ((20.6, 79.9), (58.3, 19.0), (1123.0, 0.9), (5347.0, 0.1))  # (mass kg, % of the guild's individuals)
GUILD_APEX_KG = 1000.0  # the classes of this mass and up are the dragons' own size class (a dragon's ecological mass is ~2-3 t)
GUILD_KLEIBER = 0.75
FOOD_CAP = True  # PW-977 stage 1: dragons held to the food there (off only to measure what it does, docs/review/megafauna/probe.py)
FORAGE_KM = 60.0  # a dragon takes its prey from about this far round (the prey field is averaged over neighbours this far; >= 1 ring).
# Cross-check: Jetz et al. 2004 (Science 306:266, Table 1 p. 268) fit mammal-carnivore home range H = 52.07 ha x M^1.20 (M kg, n = 70);
# at 3.2 t that is ~8,400 km2, a disc ~52 km in radius (a far extrapolation beyond the living carnivores)
FORAGER_KG = 65.0  # the giants' baseline (meta.forager_km2 human foragers per km2, PW-976) is for a forager of this mass, scaled by M^-0.75 (proposal, forager-scaled column)
PRESS_N0 = 0.05  # peoples press megafauna easily: the pressure is 1 - exp(-N / PRESS_N0), N the small folk per km2 in the cell, so a
# thin forager band (0.1 per km2, held at half its habitat) presses ~2/3 of the way and any settled people all the way (owner, PW-963:
# "pushed down easily by peoples"; Ripple et al. 2014 shows large carnivores' ranges cut to ~half by people, not their density)


def guild_ratio() -> float:
    """The rest of the predator guild's food over the apex class's, (1 - s) / s: s the share of the guild's food (abundance x M^0.75)
    that falls to the classes of GUILD_APEX_KG and up, from Carbone, Turvey & Bielby 2011's size classes (GUILD_CLASSES): ~5.0, so
    wherever dragons take a unit of food, the smaller carnivores take about five (UNVERIFIED as a general rule: one Cretaceous guild
    standing for the dragons' world; PW-977 stage 2)."""
    f = np.array([n * m ** GUILD_KLEIBER for m, n in GUILD_CLASSES])
    top = np.array([m >= GUILD_APEX_KG for m, _ in GUILD_CLASSES])
    return float(f[~top].sum() / f[top].sum())


def meat_need(h: History, line) -> float:
    """A person's wild-game need, t of live prey a year: the person's food (PERSON_KCAL_YR) x the share that is wild game (WILD_MEAT: a
    forager's, else the other ways') over a head's edible kcal x HEAD_T. 0 for megafauna, overlays and the sea peoples (fish)."""
    if line.megafauna or line.overlay or line.marine or line.way in ("fisher_forager", "sea_nomad"):
        return 0.0
    from .. import landuse as LU
    fr = min(1.0, LU.shares(h.tree, line)["forage"])
    return (WILD_MEAT[0] * fr + WILD_MEAT[1] * (1.0 - fr)) * PERSON_KCAL_YR / HEAD_KCAL * PR.HEAD_T


def eco_mass(h: History, line) -> float:
    """A kind's ecological mass, kg: a dragon's from the age schedule (meta.dragon_ages), a giant's `mass_kg` (else the hill giant's)."""
    if "flies" in line.traits:
        return h.dragon_struct["eco_mass_kg"]
    return line.mass_kg or SP.GIANT_MASS_KG


def natural_coef(h: History, line) -> float:
    """The number behind a kind's natural density: per km2 (uniform modes, and giants: x the productivity under "prey"), or for a
    dragon under "prey", per km2 per t/km2 of prey (Carbone & Gittleman)."""
    m = eco_mass(h, line)
    if "flies" not in line.traits:
        return h.tree.forager_km2 * (m / FORAGER_KG) ** -DAMUTH_EXP
    if h.mf_natural == "food" and h.prey_wild is not None:  # (PW-990 B: per t/km2 of prey, the wild offtake's apex part / a dragon's food; the deep epoch's)
        return OFFTAKE / (1.0 + guild_ratio()) / (h.dragon_struct["cattle_yr"] * PR.HEAD_T)
    if h.mf_natural == "prey" and h.prey_wild is not None:
        return CARBONE_A * m ** -CARBONE_B / 10.0
    la = LOG_A["mammal" if h.mf_natural == "mammal" else "mesotherm"]
    return 10 ** la * (1000 * m) ** -DAMUTH_EXP * h.dragon_struct["all_ages"]


def pressed_density(line, tree) -> float:
    """The present-day density in peopled country, per km2: one per meta.dragon_km2 (dragons) or meta.giant_km2 (giants)."""
    return 1.0 / (tree.dragon_km2 if "flies" in line.traits else tree.giant_km2)


def setup(h: History) -> None:
    """The natural-density state on a new History: the setting, the dragons' age structure, the static prey and productivity."""
    from .. import dragon_ages as DA
    from .. import prey as PR
    h.mf_natural = h.tree.megafauna_natural
    h.dragon_struct = DA.structure(h.tree.dragon_ages)
    h.prey_wild = PR.wild(getattr(h.ps, "graze_npp", None))  # (made for any tree: the people density reads it too, PW-974)
    h.prey_prod = None if h.prey_wild is None else _to_shore(h, PR.productivity(h.prey_wild, h.prey_wild > 0))
    h.prey_ref = float(np.median(h.prey_wild[h.prey_wild > 0])) if h.prey_wild is not None and (h.prey_wild > 0).any() else 1.0
    h._herd = PR.herd_share(h.lines)
    h._meat = np.array([meat_need(h, l) for l in h.lines])
    h.dens_nat = np.array([natural_coef(h, l) if l.megafauna else h.dens[k] for k, l in enumerate(h.lines)])
    h._press = h._prey = h._food = h._land_now = None
    h._deep_now = False


def _to_shore(h: History, x: np.ndarray) -> np.ndarray:
    """A land field carried one ring out to sea (the most of the land next to each sea cell): the shore's storm giants and the
    dragons hunting a coast."""
    g = h.grid
    land = x > 0
    return np.where(land, x, nbr_reduce(g, np.maximum, np.where(land, x, 0.0)[g.nbr_idx]))


def _reach(h: History, x: np.ndarray) -> np.ndarray:
    """A field averaged over a dragon's foraging reach (FORAGE_KM) and carried one ring out to sea."""
    g = h.grid
    deg = np.diff(g.nbr_off).astype(float)
    for _ in range(max(1, int(round(FORAGE_KM / h.cell_km)))):
        x = (x + nbr_reduce(g, np.add, x[g.nbr_idx])) / (1.0 + deg)
    return _to_shore(h, x)


def budget(h: History, P: np.ndarray, press: np.ndarray, tags: dict | None) -> dict | None:
    """The food budget per cell, t/km2/yr (PW-977): the prey under the peoples P and their pressure (lineages.prey.field: overkill outside
    refuges, livestock), over a dragon's foraging reach and one ring out to sea, and what the land supplies: the sustainable offtake of
    the wild herds (OFFTAKE) plus the tolerable share of the herders' stock (STOCK_TOLERABLE). Stage 2 (BUDGET): the peoples' hunters
    (density x their game need, `h._meat`) take first from the wild offtake; the giants and the rest of the predator guild (guild_ratio x
    the dragons' own food at the Carbone density of the prey there) take next, from what is left of the wild offtake and the stock;
    the dragons get the rest, `food`. Keys: prey, wild, stock (the supply's two parts), peoples, giants, guild (what each took, at most
    what was there), pool (the supply left after the peoples), food (the dragons'), live (the smoothed livestock, t/km2). None without
    a prey field."""
    if h.prey_wild is None:
        return None
    ref = PR.refuge(tags) if tags is not None else np.zeros(h.grid.n, bool)
    f = PR.field(h.prey_wild, press, ref, PR.stocked(P, h._herd, EST))
    wild, live = _reach(h, f["wild"]), _reach(h, f["livestock"])
    W, L = OFFTAKE * wild, STOCK_TOLERABLE * live
    z = np.zeros_like(W)
    out = {"prey": wild + live, "wild": W, "stock": L, "peoples": z, "giants": z, "guild": z, "live": live}
    if BUDGET:
        x = np.where(P >= EST, P, 0.0)
        hunt = _reach(h, (x * h.dens_cells() * h._meat[:, None]).sum(0))
        out["peoples"] = take_p = np.minimum(hunt, W)
        pool = W - take_p + L
        gi = np.zeros_like(W)
        for k, l in enumerate(h.lines):
            if l.megafauna and "flies" not in l.traits:
                gi += x[k] * local_density(h, k, press, wild + live) * giant_cattle_yr(eco_mass(h, l)) * PR.HEAD_T
        gi = _reach(h, gi)
        out["giants"] = np.minimum(gi, pool)
        if h.mf_natural == "food":  # (PW-990 B: the guild's smaller carnivores take their size classes' part of what is left)
            gd = guild_ratio() / (1.0 + guild_ratio()) * (pool - out["giants"])
        else:
            gd = guild_ratio() * CARBONE_A * h.dragon_struct["eco_mass_kg"] ** -CARBONE_B / 10.0 * h.dragon_struct["cattle_yr"] * PR.HEAD_T * (wild + live)
        out["guild"] = np.minimum(gd, pool - out["giants"])
        out["pool"] = pool
        out["food"] = pool - out["giants"] - out["guild"]
    else:
        out["pool"] = out["food"] = W + L
    return out


def prey_and_food(h: History, P: np.ndarray, press: np.ndarray, tags: dict | None) -> tuple:
    """(prey per cell, t/km2; the food the dragons can live on there, t/km2/yr; the smoothed livestock, t/km2): `budget`'s prey, food and
    live. All None without a prey field."""
    b = budget(h, P, press, tags)
    return (None, None, None) if b is None else (b["prey"], b["food"], b["live"])


def prey_now(h: History, P: np.ndarray, press: np.ndarray, tags: dict | None) -> np.ndarray | None:
    """The prey per cell, t/km2 (prey_and_food's first); None without a prey field."""
    return prey_and_food(h, P, press, tags)[0]


def natural(h: History, k: int, prey: np.ndarray | None, food: np.ndarray | None = None):
    """Line k's natural density, per km2: per cell under "prey" (dragons from the prey, giants from the productivity), else a number.
    prey None (the deep epoch, when the plates lay elsewhere and the present's prey field does not apply): uniform, a dragon at the
    land's median prey, a giant at its forager-scaled density."""
    l, c = h.lines[k], h.dens_nat[k]
    if h.mf_natural == "food" and "flies" in l.traits and h.prey_wild is not None:  # (PW-990 B: the dragons' part of the food / a dragon's food)
        return food / (h.dragon_struct["cattle_yr"] * PR.HEAD_T) if food is not None else c * (prey if prey is not None else h.prey_ref)
    if h.mf_natural not in ("prey", "food") or h.prey_wild is None:
        return c
    if "flies" in l.traits:
        return c * (prey if prey is not None else h.prey_ref)
    return c * h.prey_prod if prey is not None else c


def pressure(h: History, P: np.ndarray, land: np.ndarray | None = None) -> np.ndarray:
    """Per cell, 0..1: how hard the peoples press the megafauna there, 1 - exp(-N / PRESS_N0) with N the small folk per km2 (every
    line that is not megafauna nor an overlay, at its presence x density). A sea cell takes the most of the land next to it (storm
    giants on the shore ring are pressed by the coast's peoples)."""
    w = getattr(h, "_press_w", None)
    if w is None:
        w = h._press_w = np.array([0.0 if (l.megafauna or l.overlay) else 1.0 for k, l in enumerate(h.lines)])
    N = (np.where(P >= EST, P, 0.0) * h.dens_cells() * w[:, None]).sum(0)
    if land is not None:
        g = h.grid
        N = np.where(land, N, np.maximum(N, nbr_reduce(g, np.maximum, np.where(land, N, 0.0)[g.nbr_idx])))
    return 1.0 - np.exp(-N / PRESS_N0)


def _pressed(h: History, k: int, s: np.ndarray, prey: np.ndarray | None, food: np.ndarray | None = None) -> np.ndarray:
    nat = np.maximum(natural(h, k, prey, food), 1e-12)
    return nat * np.minimum(1.0, h.dens[k] / nat) ** s


def food_scale(h: History, P: np.ndarray, s: np.ndarray, prey: np.ndarray, food: np.ndarray) -> np.ndarray:
    """PW-977 stage 1: per cell, 1 where the dragons there (every kind together, at their pressed densities) need no more than the
    food there (the sustainable offtake of the wild herds plus the herders' tolerable stock share), else food / need: where the land
    cannot feed them, fewer of them are born, survive or stay (starvation and emigration; the dragons' range grows until it holds
    its food). Each dragon needs the age schedule's mean food, cattle a year (dragon_ages.structure)."""
    need = np.zeros(h.grid.n)
    for j, l in enumerate(h.lines):
        if l.megafauna and "flies" in l.traits:
            need += np.where(P[j] >= EST, P[j], 0.0) * _pressed(h, j, s, prey, food)
    need = need * h.dragon_struct["cattle_yr"] * PR.HEAD_T
    return np.minimum(1.0, food / np.maximum(need, 1e-12))


def local_density(h: History, k: int, s: np.ndarray, prey: np.ndarray | None = None, food: np.ndarray | None = None,
                  P: np.ndarray | None = None) -> np.ndarray:
    """Megafauna line k's density per cell, per km2, under pressure s (0..1): its natural density where s = 0, falling geometrically
    to the pressed present-day value at s = 1. Where the natural density is already sparser (poor country), peoples do not raise it.
    One rule for dragons and giants. Dragons are also held to the food there (food_scale; PW-977 stage 1) where the presences P and
    the food are given (the present's prey; not the deep epoch, whose plates lay elsewhere)."""
    d = _pressed(h, k, s, prey, food if "flies" in h.lines[k].traits else None)
    if FOOD_CAP and food is not None and P is not None and "flies" in h.lines[k].traits:
        d = d * food_scale(h, P, s, prey, food)
    return d


def ages(h: History) -> dict:
    """The counts over time (the frames' populations): per kind (dragons, giants), the count at the present and at its peak, and when.
    The peak is the age of dragons (and of giants): the deep past before the peoples spread."""
    by: dict[float, dict] = {}
    for l in h.lines:
        if l.megafauna:
            kind = "dragons" if "flies" in l.traits else "giants"
            for row in h.tracks.get(l.id, []):
                d = by.setdefault(row[0], {"dragons": 0, "giants": 0})
                d[kind] += row[4]
    if not by:
        return {}
    now = min(by)
    out = {}
    for kind in ("dragons", "giants"):
        a = max(by, key=lambda t: (by[t][kind], t))
        if by[a][kind] > 0:
            out[kind] = {"peak": int(by[a][kind]), "peak_kyr": round(float(a), 1), "present": int(by[now][kind])}
    return out


def ages_text(a: dict) -> list[str]:
    """'The age of dragons: ~3,400 dragons 410 kyr ago, before the peoples spread; ~350 now.'"""
    out = []
    for kind, r in a.items():
        if r["peak"] > r["present"] and r["peak_kyr"] > 0:
            out.append(f"The age of {kind}: ~{r['peak']:,} {kind} {r['peak_kyr']:g} kyr ago, before the peoples spread; ~{r['present']:,} now.")
    return out


RELEASE = True  # PW-1024 B (owner 10-29): ecological release. A kind spreads, at reduced density, into land outside its own country where the
# prey is plentiful and no rival kind holds it, so open niches fill on any world and preset (off only to measure it). The idea is competitive release, a species
# freed of its competitors widening its niche; the form and numbers here are a design judgement, not fitted to any data
RELEASE_K = 0.3  # the habitat such land offers at most: under scatter's SUITABLE (no new pockets are founded there, the kind walks or flies
# in from land it holds next door) and under TOLERATE_K (the edge it accepts): a design judgement, "reduced density" as about a third
RELEASE_PREY = 2.0  # the prey (the step's prey field over a forager's reach, wild herds and stock) over the land's median wild prey at which the
# release is full; none at or below the median ("plentiful": better than the usual land), in proportion between. A design judgement
RELEASE_KM = 300.0  # "neighbouring land": only within this distance of the kind's own country (its habitat without release suits it at least
# half, as for the coverage target: K >= SUITABLE x compose.SUIT_K), so a kind widens round its country rather than creeping across a continent.
# About five of a dragon's foraging reaches (FORAGE_KM) or five L7 cells. A design judgement
# (whose presence closes the land: another kind of the same sort, dragons for a dragon and giants for a giant, holding the cell)


def release(h: History, l, k: int, env: dict, tags: dict, step) -> np.ndarray | None:
    """PW-1024 B: the habitat ecological release offers megafauna kind k this step, per cell: RELEASE_K x its climate at the edges
    (habitat.edge_fit: the comfort range widened as for its tolerated country) x how plentiful the prey is (RELEASE_PREY) x open (no
    other kind of its sort holds the cell) x near (within RELEASE_KM of its own country, h._K_own). None in the deep epoch (no prey field
    for the plates then) or with RELEASE off."""
    if not RELEASE or l.marine or step.epoch == "deep" or getattr(h, "_prey", None) is None:
        return None
    from .habitat import edge_fit
    rich = np.clip((h._prey / max(h.prey_ref, 1e-9) - 1.0) / (RELEASE_PREY - 1.0), 0.0, 1.0)
    flies = "flies" in l.traits
    riv = [j for j, x in enumerate(h.lines) if j != k and x.megafauna and not x.marine and ("flies" in x.traits) == flies
           and h.active.get(x.id)]
    open_ = ~(h.p[riv] >= EST).any(0) if riv else np.ones(h.grid.n, bool)
    from .. import compose as CP
    own = getattr(h, "_K_own", {}).get(k)
    if own is None:
        return None
    g = h.grid
    near = own >= SUITABLE * CP.SUIT_K
    for _ in range(max(1, int(round(RELEASE_KM / h.cell_km)))):
        near = near | nbr_reduce(g, np.logical_or, near[g.nbr_idx])
    return RELEASE_K * edge_fit(l, env, tags) * rich * (open_ & near)


SCATTER_RATE = 1.0  # (PW-924 coverage: was 0.2) new pockets a megafauna line founds per kyr, at most SCATTER_MAX a step: "new dragons just turn up now and then" (owner: breeding
SCATTER_MAX = 3  # stays a mystery), in free suitable country within SCATTER_LINKS of its reach (link_km) of a pocket it holds; they do not
SCATTER_LINKS = 5.0  # wait for crowding as a people's jump does (History._jump), and they settle beside peoples, whom they hardly press


def scatter(h: History, l, k: int, K: np.ndarray, step, env: dict) -> None:
    """PW-924: a megafauna line reaches many separate pockets of its country by flight or long range, not one big range: a Poisson
    number of new pockets (SCATTER_RATE x dt) in cells of suitable habitat (K >= SUITABLE, its realm) not yet held, within SCATTER_LINKS
    reaches of the pockets it holds (over land and sea, LINK_KM), drawn by K."""
    g = h.grid
    rng = h.__dict__.setdefault("_mrng", {}).get(l.id)
    if rng is None:
        rng = h._mrng[l.id] = np.random.default_rng((h.seed, 924, k))
    n_ev = min(int(rng.poisson(SCATTER_RATE * step.dt)), SCATTER_MAX)
    held = h.p[k] >= EST
    if n_ev == 0 or not held.any():
        return
    reach = link_km(l)
    land = env["land"]
    realm = hold_mask(l, h._tags_now) if l.marine else land
    cost = np.full(g.n, h.cell_km / reach)  # (over land and sea alike: dragons fly, giants wade straits; LINK_KM)
    D = jump_reach(held, cost, SCATTER_LINKS, g.nbr_off, g.nbr_idx)
    cand = (K >= SUITABLE) & realm & ~held & (D > 0)
    if not cand.any():
        return
    w = np.where(cand, K, 0.0)
    for c in rng.choice(g.n, size=n_ev, replace=False if cand.sum() >= n_ev else True, p=w / w.sum()):
        blob = rings(int(c), cand, 1, g.nbr_off, g.nbr_idx)
        blob[c] = True
        h.p[k][blob] = np.maximum(h.p[k][blob], np.clip(K[blob], 0.3, 1))
        if not l.marine:
            h.cross.note(l.id, blob, step.ago, "jump", h.events, l.label())


def link_km(line) -> float:
    return LINK_KM


def metapop_km(line) -> float:
    """PW-936: pockets within the reach of scatter (SCATTER_LINKS x link_km) are one metapopulation for the viable-number fade
    (History._viable): the same dispersal that founds a pocket from its neighbours keeps it in touch with them, as patches linked by
    colonisation persist together though each alone would wink out (Levins 1969; Hanski 1998, "Metapopulation dynamics", Nature 396).
    Linked only within one reach, a pocket scatter founded farther off was faded as an isolate (most of the red and black dragons' losses)."""
    return SCATTER_LINKS * link_km(line)


def linked_pockets(h: History, held: np.ndarray, km: float) -> tuple[np.ndarray, int]:
    """Components of `held`, joining pockets within `km` of each other (over land and sea): the held cells are grown by half
    the reach, the grown mask labelled, and the labels read back on the held cells (as grid.components: -1 outside, count)."""
    g = h.grid
    grown = held.copy()
    for _ in range(max(1, int(round(0.5 * km / h.cell_km)))):
        grown |= nbr_reduce(g, np.logical_or, grown[g.nbr_idx])
    lab, _ = g.components(grown)
    lab = np.where(held, lab, -1)
    used = np.unique(lab[held])
    remap = np.full(int(lab.max()) + 2 if held.any() else 1, -1)
    remap[used] = np.arange(len(used))
    return np.where(held, remap[np.maximum(lab, 0)], -1), len(used)


def _country(line, tags: dict, sel: np.ndarray) -> str:
    best, word = 0.0, None
    for t in [*line.prefers, "wetland", "forest", "jungle", "desert", "tundra", "volcanic", "mountain", "hills", "coast", "steppe"]:
        if t in tags and isinstance(tags[t], np.ndarray) and tags[t].dtype == bool:
            s = float(tags[t][sel].mean())
            if s > best + 0.05 or (word is None and s > 0):
                best, word = s, COUNTRY.get(t, t)
    if line.marine:
        return "coastal sea"
    return word if best >= 0.25 else "country"


def groups_note(line, n: int) -> str:
    lo, hi = line.group_size or (1.0, 1.0)
    if hi <= 3:
        return "solitary" if n <= 1 else ("a mated pair" if n == 2 else "mostly solitary, now and then a pair with young")
    mean = 0.5 * (lo + hi)
    st = max(1, int(round(n / mean)))
    return f"{st} steading{'s' if st > 1 else ''} of ~{max(int(lo), int(round(n / st)))}"




def giant_cattle_yr(mass_kg: float) -> float:
    """A giant's food, head of cattle a year: Kleiber BMR x 1.7 (a working human's level), 625 Mcal edible a head (the proposal)."""
    return 70.0 * mass_kg ** 0.75 * 1.7 * 365.0 / 625e3


def food_state(h: History, P: np.ndarray, dens: dict, food, live, pool=None) -> dict | None:
    """PW-977 stage 1: per cell, in cattle a year, the dragons' expected food need (all kinds, at their densities `dens`), what the
    land supplies them (the sustainable offtake of the wild herds plus the tolerable stock share `food`), the herders' stock there
    (`live`, t/km2) and the part of the need that falls on it (the dragons take wild prey and stock in proportion to what each
    supplies; `pool`, the supply before the guild's share, is what they split: default `food`). None without a prey field."""
    if food is None:
        return None
    pool = food if pool is None else pool
    area = h.cell_mkm2 * 1e6
    dem = np.zeros(h.grid.n)
    for k, d in dens.items():
        if "flies" in h.lines[k].traits:
            dem += np.where(P[k] >= EST, P[k], 0.0) * d * area
    dem = dem * h.dragon_struct["cattle_yr"]
    return {"demand": dem, "supply": food * area / PR.HEAD_T, "stock": live * area / PR.HEAD_T,
            "stock_take": dem * STOCK_TOLERABLE * live / np.maximum(pool, 1e-12)}


def summary(h: History, P: np.ndarray, tags: dict) -> dict:
    """Per megafauna line alive at the present: the count, its pockets (each with a count, place, country and groups; dragons by
    stage, with the prey, livestock and food there), counts by landmass, the densities (realised, natural, pressed) and the target
    (share of its suitable country reached)."""
    from .. import dragon_ages as DA
    g, out = h.grid, {}
    area = h.cell_mkm2 * 1e6
    S = h._suit() if getattr(h, "_K_now", None) else None
    if S is not None:  # (PW-1024: the target is over the kind's own country and what it tolerates, not the land open to it by ecological release)
        from .. import compose as CP
        for k, K in getattr(h, "_K_own", {}).items():
            if h.active[h.lines[k].id]:
                S[k] = np.where(K >= EST, np.clip(K / CP.SUIT_K, 0.0, 1.0), 0.0)
    lm, names = h.cross.label, {nm["rank"]: nm["name"] for nm in h.cross.names}
    if not any(l.megafauna for l in h.lines):
        return out
    press = pressure(h, P, h._land_now)
    bud = budget(h, P, press, tags)
    prey, food, live, pool = (bud["prey"], bud["food"], bud["live"], bud["pool"]) if bud is not None else (None, None, None, None)
    lvs = None
    if h.prey_wild is not None:
        lvs = PR.field(h.prey_wild, press, PR.refuge(tags), PR.stocked(P, h._herd, EST))["livestock"]
    ds = h.dragon_struct
    dens = {k: local_density(h, k, press, prey, food, P) for k, l in enumerate(h.lines) if l.megafauna}
    fs = food_state(h, P, dens, food, live, pool)
    for k, l in enumerate(h.lines):
        if not l.megafauna:
            continue
        held = P[k] >= EST
        if not held.any():
            continue
        rng = np.random.default_rng((h.seed, 924, k))
        flies = "flies" in l.traits
        dk = dens[k]  # (per cell: natural where no people presses them, PW-957; dragons held to their food, PW-977)
        nat = np.broadcast_to(np.asarray(natural(h, k, prey, food if flies else None), float), dk.shape)
        exp = np.where(held, P[k], 0.0) * dk * area
        lab, n = g.components(held)
        pockets = []
        for z in range(n):
            sel = lab == z
            e = float(exp[sel].sum())
            c = int(np.floor(e) + (rng.random() < e - np.floor(e)))  # (counts, not means: unbiased rounding of the expected number)
            if c <= 0:
                continue
            v = g.centers[sel].mean(0)
            v /= np.linalg.norm(v)
            m = lm[sel]
            m = m[m >= 0]
            land = int(np.bincount(m).argmax()) if m.size else None
            pk = {"count": c, "expected": round(e, 2), "cells": int(sel.sum()), "km2": int(round(sel.sum() * area)),
                  "lat": round(float(np.degrees(np.arcsin(v[2]))), 1), "lon": round(float(np.degrees(np.arctan2(v[1], v[0]))), 1),
                  "country": _country(l, tags, sel), "landmass": land, "landmass_name": names.get(land),
                  "groups": groups_note(l, c)}
            if flies:  # (PW-958 stages; PW-967 food in cattle against the livestock there, an ancient's range from its food)
                pk["stages"] = DA.split(c, ds["name"], rng)
                if prey is not None:
                    pt = float(prey[sel].mean())
                    pk["prey_t_km2"] = round(pt, 2)
                    pk["livestock_head"] = int(round(float(lvs[sel].sum()) * area / PR.HEAD_T))
                    pk["ancient_range_km2"] = int(round(ds["stage_cattle_yr"][3] * PR.HEAD_T / max(float(food[sel].mean()), 1e-6)))
                    pk["ancient_cattle_yr"] = round(ds["stage_cattle_yr"][3], 1)
                pk["cattle_yr"] = int(round(sum(n_ * f for n_, f in zip(pk["stages"], ds["stage_cattle_yr"]))))
                if fs is not None:  # (all dragon kinds there together, expected numbers: the share of the food and of the stock they take)
                    sup = float(fs["supply"][sel].sum())
                    pk["food_use"] = round(float(fs["demand"][sel].sum()) / sup, 3) if sup > 0 else None
                    stock = float(fs["stock"][sel].sum())
                    pk["stock_take"] = round(float(fs["stock_take"][sel].sum()) / stock, 4) if stock > 0 else None
            pockets.append(pk)
        pockets.sort(key=lambda p: -p["count"])
        by: dict[str, int] = {}
        for p in pockets:
            if p["landmass"] is not None:
                by[str(p["landmass"])] = by.get(str(p["landmass"]), 0) + p["count"]
        x = np.where(held, P[k], 0.0)
        ppl = held & (press >= 0.5)  # (peopled country: the peoples press them at least half way)

        def one_per(sel, d=dk):
            return int(round(float(x[sel].sum()) / max(float((x * d)[sel].sum()), 1e-12))) if sel.any() else None
        count = int(sum(p["count"] for p in pockets))
        r = {"count": count, "pockets": len(pockets), "per_km2": round(float(h.dens[k]), 6),
             "one_per_km2": one_per(held), "pressed_one_per_km2": int(round(1.0 / h.dens[k])),
             "natural_one_per_km2": one_per(held, nat), "natural_count": int(round(float((x * nat).sum()) * area)),
             "natural_mode": h.mf_natural if (h.prey_wild is not None or h.mf_natural != "prey") else "prey (no prey field: uniform)",
             "peopled_one_per_km2": one_per(ppl),
             "wild_one_per_km2": one_per(held & ~ppl), "peopled_share": round(float(x[ppl].sum() / max(x.sum(), 1e-12)), 2),
             "mass_kg": round(eco_mass(h, l)), "generation_yr": round(h.gen_yr(l)),
             "cattle_yr_each": round(ds["cattle_yr"] if flies else giant_cattle_yr(eco_mass(h, l)), 1),
             "group_size": list(l.group_size) if l.group_size else None,
             "by_landmass": dict(sorted(by.items(), key=lambda x: -x[1])), "pocket_list": pockets}
        if flies:
            r["ages"] = ds["name"]
            r["stages"] = [int(sum(p["stages"][i] for p in pockets)) for i in range(4)]
        if S is not None:  # (suitable: the kind's own country, its prefers, as its habitat sits at MEGAFAUNA_OFF elsewhere)
            suit = S[k] >= SUITABLE
            if suit.any():
                sl, sn = g.components(suit)
                hit = np.zeros(sn, bool)
                hit[np.unique(sl[suit & held])] = True
                r["suitable_km2"] = int(round(suit.sum() * area))
                r["suitable_reached"] = round(float(hit[sl[suit]].mean()), 2)
                r["target_met"] = bool(r["suitable_reached"] >= TARGET_SHARE)
        out[l.id] = r
    return out


def line_text(lid: str, name: str, r: dict, n: int = 3) -> str:
    """One line for the report and the brief: '~12 black dragons in 9 pockets (1 per 3,100 km2 over their country: 1 per 5,000 where
    peoples press them, 1 per 65 where none do): 2 in the swamp at 3.1, 10.2 ...'."""
    tops = "; ".join(f"{p['count']} in the {p['country']} at {p['lat']:g}, {p['lon']:g}"
                     + (f" ({p['landmass_name']})" if p.get("landmass_name") else "") for p in r["pocket_list"][:n])
    tgt = f", in {round(100 * r['suitable_reached'])}% of their country" if "suitable_reached" in r else ""
    st = f" ({stages_of(r)})" if r.get("stages") and r["count"] else ""
    return f"~{r['count']} {name}{st} in {r['pockets']} pockets ({density_text(r)}{tgt}): {tops}"


def stages_of(r: dict) -> str:
    """'1 ancient, 6 adults, 4 young, 1 wyrmling' (PW-958)."""
    from .. import dragon_ages as DA
    return DA.stages_text(r["stages"])


def density_text(r: dict) -> str:
    """'1 per 3,100 km² (1 per 5,000 where peoples press them, 1 per 65 where none do)'."""
    s = f"1 per {r['one_per_km2']:,} km²" if r.get("one_per_km2") else "?"
    if "pressed_one_per_km2" in r:
        s += f" (1 per {r['pressed_one_per_km2']:,} where peoples press them, 1 per {r['natural_one_per_km2'] or 0:,} where none do)"
    return s
