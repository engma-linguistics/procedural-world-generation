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
  uniform over the kind's country. The dragons' intake law is the same physiology: Nagy et al. 1999's mammal line over Marshall's 2.1
  (dragon_ages, PW-1066). Farlow 1993 (Am J Sci 293:167, p. 187) fits reptile density = 66.07 M^-1.01
  per km2 (M kg; Damuth 1987's reptile data plus Komodo dragons, from animals two orders of magnitude lighter), ~1 per 50 km2 at
  3.2 t: the same order as this line.
- "mammal": the same on the mammal-carnivore intercept (log10 a = 2.67): ~1 per 137 km2.
The dragons' ecological mass, stage shares and generation time follow meta.dragon_ages (lineages.dragon_ages, PW-958, PW-959).
The food chain after the dragon-density paper's revisions (lane 90, docs/review/dragon-food-chain/report.md): the prey from the above-ground
NPP (prey.above, PW-1073); the yearly offtake from the herds' production (OFFTAKE, PW-1072); a sourced intake law, assimilation and carcass
share (dragon_ages, PW-1066, PW-1067); one metabolic exponent for the guild, the young dragons eating in its smaller classes (dragon_share,
PW-1071); the smaller predators pressed by the peoples too (guild_kept, PW-1070); overkill by how long the fauna knew people (overkill,
PW-1000); a food budget in the deep epoch (deep_budget, PW-1062); a linked population's viable number (linked_mvp, PW-1069); the peoples'
means from the herds and horses the history gives them (means, PW-1177); and the hunting range (HUNT_KM, release, PW-1065).
Giants under "mesotherm" and "mammal" are uniform mass-scaled foragers: human foragers (~0.1 per km2, the proposal's median, whose source is
not yet found: Hamilton et al. 2007 reuses Binford 2001's data but fits area against group size, not density, and its fit implies
0.03-0.09 per km2 for groups of 25-1000, PNAS 104:4765, Table 1, p. 4767; the M^-0.75 body-mass scaling is Damuth/Kleiber, not
from Hamilton) scaled by M^-0.75 from 65 kg: hill giants (2.2 t) ~1 per 140 km2,
storm giants (7.3 t) ~1 per 345.
The older note here ("an apex hunter two to three orders below the herbivore line", after Carbone & Gittleman) was unsupported:
their carnivore line sits ~1.5 orders below the herbivores'.

Peoples press both down by persecution (`kill`, PW-1068): a kill against their slow breeding, rising with the peoples' numbers and
`means` (herds to defend, and weapons and organised hunts by the era's tech level), so they settle at natural x (1 - kill / r) and are
lost from land where the kill outruns their breeding (`local_density`; PW-1246 B, lane 103): near natural beside early foragers, thinned
beside farmers, gone from land as busy as the farmland lions are lost from (25 people per km2, Riggio et al. 2013; constants below). Ripple et al. 2014 (Science 343:1241484, on file) shows the large carnivores pushed back by people (17 of the 31
largest hold on average 47% of their historical range, from <1% to 73%: tiger 18%, lion 17%; p. 1241484-2 and Table 1), gives no
figure for density against potential, and ties their vulnerability to persecution to their slow reproduction (p. 1241484-1).
Cardillo et al. 2004 (PLoS Biol 2:e197, on file) finds carnivore extinction risk tied to slow life history where people are dense
(>= 10 per km2; Tables 2-3, pp. 0911-0912). The peoples also cut the wild herds by overkill (`pressure`, prey.field), a separate
channel. Before the peoples spread the megafauna were many more: the age of dragons (`ages`).
Of these papers Marshall 2021, Carbone & Gittleman 2002, Hamilton et al. 2007, Nagy et al. 1999, Ripple et al. 2014, Cardillo et al. 2004
and Farlow 1993 are on file; Damuth and Binford are cited as the proposal gives them and are not on file (docs/references/megafauna/README.md).

They live long (dragons a few hundred years a generation, giants 50-80 yr), so few of them persist: their patches' viable number
is smaller (History.line_mvp), and pockets within flight or long range of each other are one population (linked_pockets).
They are exempt from the peoples' 300-cell range target and the remnant check: their target is to be present in most of
the world's suitable country for their kind (`suitable_reached`). Breeding is not modelled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from .. import dragon_ages as DA
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
# The yearly offtake follows the herds' production (PW-1072, lane 90): Farlow 1993 (Am J Sci 293:167, eq. 6, p. 172): prey turnover =
# 0.94 M^-0.28 per yr (M kg), at the cattle-sized head the dragons and the peoples take (prey.HEAD_T): 0.165 per yr, against Coe, Cumming
# & Phillipson 1976's 24 African wildlife areas, production / biomass 0.085-0.26, median 0.20 (Table 1, pp. 344-345). Farlow's best case
# lets the predators eat all of it (eq. 3, p. 172); real large-mammal communities run at prey:predator 100:1 to 200:1 against his 50:1
# (p. 176), "the difference between conditions prevailing in real ecological communities and the ideal conditions assumed", and he takes
# that gap to cover the inedible skeleton too. So the predators eat 1/2 to 1/4 of the production's energy (geometric middle 1/2.83); since
# the carcass share is counted on its own (dragon_ages.CARCASS_USE), the share of production killed is that over CARCASS_USE.
TURNOVER = 0.94 * (PR.HEAD_T * 1000.0) ** -0.28  # the herds' production / biomass a year at the head's mass (Farlow eq. 6)
PRODUCTION_KILLED = (1.0 / np.sqrt(8.0)) / DA.CARCASS_USE  # ~0.45: the share of the herds' production all hunters together kill a year
OFFTAKE = PRODUCTION_KILLED * TURNOVER  # ~0.074 of the standing wild biomass a year (was a flat 0.1, unsourced)
STOCK_TOLERABLE = 0.1  # the share of herders' stock the herders tolerate losing a year to dragons before they leave the range (UNVERIFIED; a model
# assumption: herds turn over at ~15-25%/yr (Farlow 1993's eq. 6, p. 172, gives 0.17/yr for 500 kg animals), so a tenth lost is a bad
# year they put up with, PW-977; the herders' tolerance itself is to be sourced)
BUDGET = True  # PW-977 stage 2: the peoples' hunters, the giants and the rest of the predator guild draw on the wild offtake before the dragons do (off only to measure it: the dragons then get all of it, stage 1)
PERSON_KCAL_YR = 2200.0 * 365.0  # a person's food, kcal a year (a working adult's ~2,200 kcal a day; the proposal's Kleiber x 1.7 figure for a 65 kg forager is ~1,900; UNVERIFIED round number)
HEAD_KCAL = DA.edible_kcal()  # edible kcal in a head of cattle-sized prey, ~652,000: one figure for peoples, giants and dragons (PW-1067): Farlow
# 1993's 7 kJ per g live mass (p. 172) x a 0.5 t head x the share of a large carcass eaten (Carbone et al. 2007, p. 367; dragon_ages.CARCASS_USE)
WILD_MEAT = (0.5, 0.05)  # the share of a people's food that is wild game: (a forager's, any other way's). UNVERIFIED round numbers, no source on file: a
# forager eats much of its food as game, herders, farmers and gardeners hunt little (the ethnographic figure is wanted; inbox draft)
# Carbone, Turvey & Bielby 2011, Proc R Soc B 278:2682 (PDF p. 2683-2684, Fig. 1 and Table 1; read 10-29): the carnivorous theropod guild of Late Cretaceous North America by
# size class, as the share of the guild's individuals (their abundances follow the mammalian carnivore line N ~ 1.97 M^-0.88, their Table 3): 20.6 kg 79.9%, 58.3 kg 19.0%, 1,123 kg
# 0.9%, 5,347 kg 0.1%. They give the abundance, not the food; the guild's food by class is that times M^GUILD_EXP: one metabolic exponent for the
# guild and the dragons (PW-1071, lane 90): the dragons' own intake law's (dragon_ages.FMR_B, Nagy et al. 1999's mammal slope 0.734), inside Carbone &
# Gittleman 2002's fitted -0.66 (CI -0.48 to -0.85, p. 2274) and Carbone et al. 2007's 0.6-0.79 (Table 1, p. 364).
# Young dragons eat in the smaller classes (PW-1071): Carbone et al. 2011 built the classes from adult masses but name "juvenile and sub-adult T. rex
# individuals, which may have been relatively abundant compared with adults" among T. rex's competitors (p. 2683). So the apex class's share feeds the
# adults and ancients, and the wyrmlings and young (dragon_ages: ~1/4 of the dragons' food) eat inside the smaller classes' share (`dragon_share`).
GUILD_CLASSES = ((20.6, 79.9), (58.3, 19.0), (1123.0, 0.9), (5347.0, 0.1))  # (mass kg, % of the guild's individuals)
GUILD_APEX_KG = 1000.0  # the classes of this mass and up are the dragons' own size class (a dragon's ecological mass is ~2-3 t)
GUILD_EXP = DA.FMR_B
YOUNG_IN_GUILD = True  # (off only to measure it)
SEA_FOOD = True  # D28 B (owner 10-31, lane 99): kinds with the trait 'sea_hunter' (white, bronze and blue dragons in the dnd tree) also live
# on the sea's marine mammals within their foraging reach (`sea_food`; prey.sea_prey); off only to measure it
FOOD_CAP = True  # PW-977 stage 1: dragons held to the food there (off only to measure what it does, docs/review/megafauna/probe.py)
# Hunting ranges (PW-1065, lane 90; owner 10-31: "dragons have very large hunting ranges"). Jetz et al. 2004 (Science 306:266, Table 1 p. 268)
# fit mammal-carnivore home range H = 52.07 ha x M^1.20 (M kg, n = 70; a far extrapolation past the living carnivores). Over the age schedule's
# stage masses that is a disc of ~2 / 12 / 46 / 173 km radius for wyrmlings / young / adults / ancients.
def _jetz_km(m_kg):
    return float(np.sqrt(52.07 * np.asarray(m_kg, float) ** 1.20 / 100.0 / np.pi))


_DS0 = DA.structure()
FORAGE_KM = float(np.dot(_DS0["food_share"], [_jetz_km(m) for m in _DS0["stage_mass_kg"]]))  # ~77 km: the dragons take their prey from about
# this far round, the food-weighted mean of the stages' ranges (the prey field is averaged over neighbours this far; >= 1 ring)
HUNT_KM = _jetz_km(_DS0["stage_mass_kg"][3])  # ~173 km: the ancients' range; a kind hunts this far out of its own country (`release`)
FORAGER_KG = 65.0  # the giants' baseline (meta.forager_km2 human foragers per km2, PW-976) is for a forager of this mass, scaled by M^-0.75 (proposal, forager-scaled column)
PRESS_N0 = 0.05  # the overkill pressure (`pressure`; prey.field cuts the wild big herbivores where small folk live, after Sandom et al.
# 2014) is 1 - exp(-N / PRESS_N0), N the small folk per km2 in the cell: a thin forager band already cuts the herds most of the way. It no
# longer presses the megafauna themselves; that is the persecution kill below (PW-1068)
# Persecution (PW-1068 option A, owner 10-30): a kill against the megafauna's slow breeding, by age class (owner 10-30: "separate out by age
# class of dragons for mortality"). The peoples' kill effort per cell is KILL_Q x the sum over peoples of (their people per km2 x their
# `means`: how many there are, how organised, how much they have to defend); a stage s of dragons loses effort x VULNERABILITY_s(tech) of
# its number a year. Wyrmlings are reachable with spears, traps and bait; the young less so; adults and ancients hardly at all until the
# tech level is high, so the adults' share of the kill rises with tech. On the dragons' age schedule (dragon_ages: the survival by stage,
# fecundity flat from BREED_FROM) the kill lowers lifetime births R0 by a factor F (R0 / R0 under the kill). Where the dragons are thinned
# their births rise to make up for it, at most BREED_X-fold where they are fewest (density compensation, linear between); they settle where
# the births' rise meets F: natural x (1 - (F - 1) / (BREED_X - 1)) (`dragon_kept`), and where the kill would need more than a BREED_X-fold
# rise they are lost from that land (local extirpation, PW-1246 B, owner 10-31: "inclined towards B"). Giants (no age schedule) take the
# adults' vulnerability in the one-stage form, kept = 1 - kill / r, r = ln(BREED_X) / their generation. A kind is never ended by the kill
# alone: it keeps the land where people are few (the lions' and tigers' pattern below); never above natural.
# Evidence: in long-lived, slow-breeding animals growth is far less sensitive to first-year survival than to the long juvenile and adult
# stages (loggerheads: Crouse, Crowder & Caswell 1987, Ecology 68:1412, p. 1416 and Fig. 1; protecting eggs alone "could not prevent the
# eventual extinction of the model population", p. 1417); the dragons' own schedule agrees (the elasticity of R0 to a stage's survival,
# summed over its years: wyrmlings 6, young 95, adults 242, ancients 92). Large carnivores' slow reproduction leaves them "poorly able to
# respond to persecution" (Ripple et al. 2014, Science 343:1241484, p. 1241484-1), and among carnivores slow life history predicts
# extinction risk where people are dense, >= 10 per km2 (Cardillo et al. 2004, PLoS Biol 2:e197, Tables 2-3, pp. 0911-0912).
# The kill's size (lane 103, replacing lane 63's "dense renaissance farmers at 10 per km2 keep 10% of their dragons", a judgement the owner
# did not want): the lions' range loss. Riggio et al. 2013 (Biodivers Conserv 22:17, CC-BY, on file as
# docs/references/megafauna/riggio2013_savannah_africa_lion_view_biodivconserv.pdf; read 2026-10-31) map Africa's lion areas by excluding
# land above 25 people per km2 (p. 21, rule 3), the density that best matches land converted to crops, overlap peaking "between 10 and 25
# people per km2" in all four focus areas (p. 23); and "Woodroffe (2000) estimated a mean human population density threshold at which lions
# went extinct of 26 people per km2" (p. 30; Woodroffe itself not read). Lions persist, at park-like density, on pastoral land below it
# (Western et al. 2022, lane 99's report). So the apex predator is lost from land of LOSS_KM2 farmers and kept, thinned, below: KILL_Q is
# set so the dragons' own life table (the default schedule, dragon_ages.DEFAULT) reaches F = BREED_X there, at the top tech level (the
# lions' modern Africa) and the means of a farming people with herds and no riding (MEANS_REF). At earlier tech levels the same peoples
# reach far fewer of the adults (VULNERABILITY), so the dragons are lost only from much denser land then. The smaller predators (the guild)
# take the same threshold directly (`guild_kept`). VULNERABILITY and the means stay judgements.
BREED_X = 2.0  # the most the births rise where the megafauna are fewest (a judgement. Crouse 1987 p. 1417: loggerheads could recover by
# fecundity only "if they could more than double egg production, which seems unlikely")
LOSS_KM2 = 25.0  # people per km2 (farmers) at which the apex predator is lost from the land: Riggio et al. 2013 pp. 21, 23 (25; Woodroffe 2000's 26, p. 30)
LOSS_LEV = 1.0  # the tech level of that observation (twentieth-century Africa)
MEANS_REF = None  # (set below: `means` of a farming people that keeps its herds and does not ride, 0.625)
KILL_Q = None  # (set below, `_calibrate`: kill effort a year per head, per person per km2 at full means, ~1.85e-4)
MOTIVE0 = 0.25  # means: a people with no herds still kills what threatens it, at this share of one with herds everywhere (judgement)
FORAGER_ORG = 0.3  # means: a forager band's organised killing against a settled or herding people's (judgement)
VULNERABILITY = {"wyrmling": (1.0, 0.0, 1.0), "young": (0.05, 0.45, 1.0), "adult": (0.01, 0.99, 2.0)}  # (a, b, p): a + b x level^p
ANCIENT_X = 0.5  # ancients are this much less vulnerable than adults (judgement)
# The tech level by era: a calendar proxy for weapons, metal, horses and organised hunts until the peoples' own techs can feed the history
# (the technology tree, techtree.py, is made after it). The present is meta.era; the eras before it are counted back from the present
# on Earth-like spans (kyr each, a judgement); before them, the stone age. Bronze-age peoples are still far from adult dragons (owner 10-30).
ERA_LEVEL = {"stone age": 0.0, "bronze age": 0.15, "classical": 0.55, "medieval": 0.75, "renaissance": 0.9, "industrial": 1.0}
ERA_KYR = {"industrial": 0.25, "renaissance": 0.35, "medieval": 1.0, "classical": 1.3, "bronze age": 2.0}


def guild_ratio(h: History | None = None) -> float:
    """The rest of the predator guild's food over the apex class's, (1 - s) / s: s the share of the guild's food (abundance x M^GUILD_EXP)
    that falls to the classes of GUILD_APEX_KG and up, from Carbone, Turvey & Bielby 2011's size classes (GUILD_CLASSES): ~5.0, so
    wherever dragons take a unit of food, the smaller carnivores take about five (UNVERIFIED as a general rule: one Cretaceous guild
    standing for the dragons' world; PW-977 stage 2). With h, x its tree's meta.rivals (0: no rival predators; default 1)."""
    f = np.array([n * m ** GUILD_EXP for m, n in GUILD_CLASSES])
    top = np.array([m >= GUILD_APEX_KG for m, _ in GUILD_CLASSES])
    return float(f[~top].sum() / f[top].sum()) * (getattr(h.tree, "rivals", 1.0) if h is not None else 1.0)


def young_share(h: History | None = None) -> float:
    """The share of the dragons' food eaten by wyrmlings and the young, who hunt in the smaller classes (YOUNG_IN_GUILD; 0 when off)."""
    if not YOUNG_IN_GUILD:
        return 0.0
    fs = (h.dragon_struct if h is not None and getattr(h, "dragon_struct", None) is not None else DA.structure())["food_share"]
    return float(fs[0] + fs[1])


def dragon_share(h: History | None = None) -> float:
    """The dragons' share of the guild's food (PW-1071): the apex class's 1 / (1 + guild_ratio) feeds the adults and ancients, and the
    young's share of the dragons' food comes out of the smaller classes': D = apex / (1 - young_share), at most 1."""
    return min(1.0, 1.0 / (1.0 + guild_ratio(h)) / (1.0 - young_share(h)))


def guild_kept(h: History, kl, lev: float | None = None):
    """The smaller predators' share of their food-fed number kept under the peoples' kill kl (PW-1070, lane 90): Ripple et al. 2014's 31
    persecuted large carnivores (Science 343:1241484, Table 1) include the wolf- and leopard-sized members of the guild, so the peoples press
    them too, at the wyrmlings' vulnerability (spears, traps and poison reach them at any tech): linearly fewer with the kill, lost from
    land where it is that of LOSS_KM2 farmers of MEANS_REF (lane 103: the lions' threshold itself, Riggio et al. 2013, the lions being
    the guild's largest)."""
    lev = tech_level(h.tree.era, getattr(h, "_ago_now", 0.0)) if lev is None else lev
    v = vulnerability(lev)[0] * press_x(h.tree, lev)
    return np.clip(1.0 - np.asarray(kl, float) * v / (KILL_Q * LOSS_KM2 * MEANS_REF), 0.0, 1.0)


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
    if h.mf_natural == "food" and h.prey_wild is not None:  # (PW-990 B: per t/km2 of prey, the wild offtake's dragons' part / a dragon's food)
        return OFFTAKE * dragon_share(h) / (h.dragon_struct["cattle_yr"] * PR.HEAD_T)
    if h.mf_natural == "prey" and h.prey_wild is not None:
        return CARBONE_A * m ** -CARBONE_B / 10.0
    la = LOG_A["mammal" if h.mf_natural == "mammal" else "mesotherm"]
    return 10 ** la * (1000 * m) ** -DAMUTH_EXP * h.dragon_struct["all_ages"]


def pressed_density(line, tree) -> float:
    """A kind's nominal density, per km2: one per meta.dragon_km2 (dragons) or meta.giant_km2 (giants). Since PW-1068 it no longer sets
    the density anywhere (that is the natural density under the persecution kill, `local_density`); it is the number the competition
    between lines and the viable-population check take."""
    return 1.0 / (tree.dragon_km2 if "flies" in line.traits else tree.giant_km2)


def tech_level(era: str, ago: float) -> float:
    """0..1: the peoples' tech level ago kyr before the present, whose era is `era` (meta.era): ERA_LEVEL at the end of each era, rising
    linearly through it, the eras counted back from the present on ERA_KYR's spans; the stone age (0) before them. A calendar proxy."""
    order = list(ERA_LEVEL)
    i = order.index(era) if era in order else order.index(SP.ERA_DEFAULT)
    xs, ys, t = [0.0], [ERA_LEVEL[order[i]]], 0.0
    for j in range(i, 0, -1):
        t += ERA_KYR[order[j]]
        xs.append(t)
        ys.append(ERA_LEVEL[order[j - 1]])
    return float(np.interp(max(ago, 0.0), xs, ys))


MOUNTED_X = 0.5  # means: a people that rides hunts dragons over open country this much harder (PW-1177; a judgement)


def _known(h: History) -> tuple[np.ndarray, np.ndarray]:
    """Per line, at the step, what the history itself knows a people has (PW-1177, lane 90): herds (animals.herding: the best adoption
    of a herd animal it has tamed or taken up, 0..1) and riding (the best adoption of an animal that speeds it over open country, horses).
    Without the animals pass, herds as its way of life says and no riding."""
    L = len(h.lines)
    A = getattr(h, "animals", None)
    if A is None:
        return np.ones(L), np.zeros(L)
    herds = np.array([A.herding(k) for k in range(L)])
    rides = np.zeros(L)
    for st in A.stocks:
        if st.a.speed > 1.0:
            rides = np.maximum(rides, st.adopt)
    return herds, rides


def means(h: History) -> np.ndarray:
    """Per line, 0..1.5: how hard one person of it presses megafauna, before the tech level (PW-1068): motive x organisation x reach.
    Motive: MOTIVE0 + (1 - MOTIVE0) x the share of its country it stocks (prey.LIVESTOCK) x how far it has the herds yet (`_known`: herds to
    defend only once it keeps them). Organisation: its wild-food share at FORAGER_ORG (bands), the rest (settled and herding) at 1. Reach:
    1 + MOUNTED_X x how far it rides (`_known`). 0 for megafauna and overlays. Read from the history at each step (PW-1177); the weapons
    and metal still come from the era calendar (`tech_level`), as the technology tree is made after the history (PW-946)."""
    m = getattr(h, "_means", None)
    if m is not None and m[0] == getattr(h, "_ago_now", 0.0):
        return m[1]
    from .. import landuse as LU
    herds, rides = _known(h)
    out = np.zeros(len(h.lines))
    for k, l in enumerate(h.lines):
        if l.megafauna or l.overlay:
            continue
        f = min(1.0, LU.shares(h.tree, l)["forage"])
        out[k] = (MOTIVE0 + (1.0 - MOTIVE0) * h._herd[k] * herds[k]) * (f * FORAGER_ORG + (1.0 - f)) * (1.0 + MOUNTED_X * rides[k])
    h._means = (getattr(h, "_ago_now", 0.0), out)
    return out


def vulnerability(lev: float) -> np.ndarray:
    """Per dragon stage (dragon_ages.STAGES), the share of the peoples' kill effort that falls on it at tech level lev (VULNERABILITY)."""
    v = [a + b * lev ** p for a, b, p in (VULNERABILITY[x] for x in ("wyrmling", "young", "adult"))]
    return np.array(v + [ANCIENT_X * v[2]])


def breed_r(h: History, line) -> float:
    """A megafauna kind's most added a year per head where persecution thins it (one-stage form): ln(BREED_X) over its generation."""
    return float(np.log(BREED_X) / max(h.gen_yr(line), 1.0))


_EPS = np.concatenate([[0.0], np.geomspace(1e-7, 1.0, 241)])  # (the kill-effort grid of dragon_kept's table, per head a year)


def births_rise(schedule: str, eps, lev: float) -> np.ndarray:
    """F: the factor lifetime births must rise by to make up for a kill effort eps (per head a year, an array) at tech level lev, on the age
    schedule `schedule` (dragon_ages.SCHEDULES: survival by stage, fecundity flat from BREED_FROM): R0 with no kill over R0 under it."""
    mort = np.asarray(DA.SCHEDULES[schedule], float)[DA.STAGE_OF]
    breed = DA.AGES >= DA.BREED_FROM
    ks = np.atleast_1d(np.asarray(eps, float))[:, None] * vulnerability(lev)[DA.STAGE_OF][None, :]
    l = np.concatenate([np.ones((ks.shape[0], 1)), np.cumprod((1.0 - mort)[None, :] * np.exp(-ks), axis=1)[:, :-1]], axis=1)
    l0 = np.concatenate([[1.0], np.cumprod(1.0 - mort)[:-1]])
    return (l0 * breed).sum() / (l * breed).sum(1)


def _kept_table(h: History, lev: float) -> np.ndarray:
    """dragon_kept over _EPS at tech level lev, on the dragons' age schedule (cached per level)."""
    c = h.__dict__.setdefault("_kept_cache", {})
    key = round(lev, 4)
    if key not in c:
        F = births_rise(h.dragon_struct["name"], _EPS, lev)
        c[key] = np.clip(1.0 - (F - 1.0) / (BREED_X - 1.0), 0.0, 1.0)
    return c[key]


def dragon_kept(h: History, eps, lev: float) -> np.ndarray:
    """The share of their natural density dragons keep under the peoples' kill effort eps (per head a year, `kill`) at tech level lev: each
    stage loses eps x vulnerability(lev) a year; lifetime births R0 fall by a factor F (`births_rise`); the births rise to meet it, at most
    BREED_X-fold where the dragons are fewest (linear compensation): kept = 1 - (F - 1) / (BREED_X - 1), 0 where F >= BREED_X (lost from
    that land, PW-1246 B). Interpolated on a table per level."""
    e = np.clip(np.asarray(eps, float), 0.0, _EPS[-1])
    t = _kept_table(h, lev)
    return np.interp(np.log10(e + 1e-9), np.log10(_EPS + 1e-9), t)


def press_x(tree, lev: float) -> float:
    """The user's multiplier on the peoples' kill at tech level lev (owner 10-30, D14: the viewer's "how hard peoples press dragons and
    giants"): meta.press_early at level 0, meta.press_late at level 1, blended linearly by level between."""
    a, b = getattr(tree, "press_early", 1.0), getattr(tree, "press_late", 1.0)
    return float(a + (b - a) * min(max(lev, 0.0), 1.0))


def kept(h: History, k: int, eps, lev: float | None = None) -> np.ndarray:
    """Line k's share of its natural density kept under the kill effort eps: dragons by age class (`dragon_kept`), giants in the
    one-stage form with the adults' vulnerability, 1 - eps x v_adult / r (0 where the kill outruns their breeding)."""
    lev = tech_level(h.tree.era, getattr(h, "_ago_now", 0.0)) if lev is None else lev
    eps = np.asarray(eps, float) * press_x(h.tree, lev)
    if "flies" in h.lines[k].traits and getattr(h, "dragon_struct", None) is not None:
        return dragon_kept(h, eps, lev)
    return np.clip(1.0 - np.asarray(eps, float) * vulnerability(lev)[2] / breed_r(h, h.lines[k]), 0.0, 1.0)


def kill(h: History, P: np.ndarray, land: np.ndarray | None = None) -> np.ndarray:
    """Per cell, the peoples' kill effort on the megafauna there, per head a year at full vulnerability (PW-1068): KILL_Q x the sum over
    peoples of their people per km2 (presence x density) x their `means`. A sea cell takes the most of the land next to it (storm giants
    on the shore ring). What it costs each kind and age class: `kept`."""
    N = (np.where(P >= EST, P, 0.0) * h.dens_cells() * means(h)[:, None]).sum(0)
    if land is not None:
        g = h.grid
        N = np.where(land, N, np.maximum(N, nbr_reduce(g, np.maximum, np.where(land, N, 0.0)[g.nbr_idx])))
    return KILL_Q * N

def _calibrate() -> tuple[float, float]:
    """(MEANS_REF, KILL_Q): the means of a farming people that keeps its herds (prey.LIVESTOCK's farmer share) and does not ride, and the
    kill effort per head per person per km2 at full means at which LOSS_KM2 such farmers at tech level LOSS_LEV drive the default age
    schedule's births to a BREED_X-fold rise: the dragons lost from that land, as lions are (Riggio et al. 2013; see LOSS_KM2)."""
    m = MOTIVE0 + (1.0 - MOTIVE0) * PR.LIVESTOCK["farmer"]
    lo, hi = 1e-8, 1.0
    for _ in range(100):
        mid = np.sqrt(lo * hi)
        lo, hi = (mid, hi) if births_rise(DA.DEFAULT, mid, LOSS_LEV)[0] < BREED_X else (lo, mid)
    return m, float(np.sqrt(lo * hi) / (LOSS_KM2 * m))


MEANS_REF, KILL_Q = _calibrate()


def setup(h: History) -> None:
    """The natural-density state on a new History: the setting, the dragons' age structure, the static prey and productivity."""
    from .. import dragon_ages as DA
    from .. import prey as PR
    h.mf_natural = h.tree.megafauna_natural
    h.dragon_struct = DA.structure(h.tree.dragon_ages)
    h.prey_wild = PR.wild(getattr(h.ps, "graze_npp", None), getattr(h.ps, "rain0", None))  # (the above-ground part, PW-1073)
    h.prey_prod = None if h.prey_wild is None else _to_shore(h, PR.productivity(h.prey_wild, h.prey_wild > 0))
    h.prey_ref = float(np.median(h.prey_wild[h.prey_wild > 0])) if h.prey_wild is not None and (h.prey_wild > 0).any() else 1.0
    h._herd = PR.herd_share(h.lines)
    h._meat = np.array([meat_need(h, l) for l in h.lines])
    h.dens_nat = np.array([natural_coef(h, l) if l.megafauna else h.dens[k] for k, l in enumerate(h.lines)])
    h._press = h._kill = h._prey = h._food = h._land_now = None
    h._deep_now = False
    h._ago_now = 0.0
    h._first_ago = np.full(h.grid.n, -1.0)  # (per cell, kyr ago small folk first lived there; -1 never: `note_settled`, PW-1000)
    h._overkill = None
    h._deep_food = None  # (the deep epoch's food budget, t/km2/yr for the dragons: `deep_budget`, PW-1062)
    h._wild_mean = None if h.prey_wild is None else float(h.prey_wild[h.prey_wild > 0].mean()) if (h.prey_wild > 0).any() else 0.0
    h.sea_food = sea_food(h)
    h._sea_hunt = np.array([bool(SEA_FOOD and h.sea_food is not None and l.megafauna and "sea_hunter" in l.traits) for l in h.lines])


def sea_food(h: History) -> np.ndarray | None:
    """The sea's food for a sea-hunting dragon per cell, t/km2/yr (D28 B, lane 99): the marine mammals' production (prey.sea_prey, from
    the ocean's NPP, prey.sea_npp) over a dragon's foraging reach (`_reach`, so a coast cell with half its reach at sea gets half), x the
    share of a prey's production all its predators kill (PRODUCTION_KILLED, the land's figure: a judgement for the sea) x the dragons' share
    of the guild (`dragon_share`: the dragons as the apex class among the seal hunters, orcas and sharks in their place; a judgement).
    The peoples' fishing and sealing are not taken out (a simplification). None without an ocean NPP field (or with SEA_FOOD off). The
    deep epoch, whose plates lay elsewhere, has none."""
    npp = getattr(h.ps, "sea_npp", None)
    if not SEA_FOOD or npp is None or h.prey_wild is None:
        return None
    x = PR.sea_prey(npp)
    return _reach(h, x) * PRODUCTION_KILLED * dragon_share(h)


COEVOL_KM = 300.0  # the herds' own range: a land's fauna has known people as long as the longest-peopled land this near (a judgement, = RELEASE_KM)


def note_settled(h: History, P: np.ndarray, ago: float) -> None:
    """Each step (History.run): the cells small folk hold for the first time get `_first_ago` = ago (PW-1000 B, the overkill's clock)."""
    N = (np.where(P >= EST, P, 0.0) * _small_w(h)[:, None]).sum(0)
    new = (N > 0) & (h._first_ago < 0)
    if new.any():
        h._first_ago[new] = ago
        h._overkill = None


def overkill(h: History) -> np.ndarray | float:
    """Per cell, the share of the wild big herbivores lost where small folk press the land fully (prey.field): meta.overkill x
    prey.coevolved_loss of the years the fauna there has lived beside small folk (the longest-peopled land within COEVOL_KM; PW-1000 B).
    A number (meta.overkill) on a History without the clock."""
    base = getattr(h.tree, "overkill", PR.OVERKILL)
    fa = getattr(h, "_first_ago", None)
    if fa is None:
        return base
    c = getattr(h, "_overkill", None)
    if c is not None and c[0] == (h._ago_now, base):
        return c[1]
    g = h.grid
    x = fa.copy()
    for _ in range(max(1, int(round(COEVOL_KM / h.cell_km)))):
        x = np.maximum(x, nbr_reduce(g, np.maximum, x[g.nbr_idx]))
    yrs = np.where(x >= 0, x - h._ago_now, 0.0)
    out = base * PR.coevolved_loss(yrs)
    h._overkill = ((h._ago_now, base), out)
    return out


def deep_budget(h: History, P: np.ndarray, land: np.ndarray) -> None:
    """The deep epoch's food budget (PW-1062 A, lane 90): the plates lay elsewhere, so the present's prey field holds only as a planet
    figure. The dragons' food per km2 = the land's mean wild offtake (OFFTAKE x the present's mean wild prey, after the overkill at the
    step's mean pressure on its land), less the peoples' mean game take there, plus the herders' tolerated stock, x the dragons' share of
    what is left after the pressed guild. Giants are left out (a few per cent of the food). Sets h._deep_food (t/km2/yr)."""
    if h.prey_wild is None or not land.any():
        h._deep_food = None
        return
    press = pressure(h, P, land)[land]
    ok = overkill(h)
    ok = ok[land] if np.ndim(ok) else ok
    W = OFFTAKE * h._wild_mean * float(np.mean(1.0 - ok * press))
    x = np.where(P >= EST, P, 0.0)[:, land]
    hunt = float(((x * h.dens_cells()[:, land] * h._meat[:, None]).sum(0)).mean()) * getattr(h.tree, "game_share", 1.0) if BUDGET else 0.0
    L = STOCK_TOLERABLE * h._wild_mean * PR.LIVESTOCK_X * float(np.clip(x.T @ h._herd, 0, 1).mean())
    pool = W - min(hunt, W) + L
    if BUDGET and h.mf_natural == "food":
        kl = kill(h, P, land)[land]
        pool = pool * (1.0 - (1.0 - dragon_share(h)) * float(np.mean(guild_kept(h, kl))))
    h._deep_food = pool


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


def budget(h: History, P: np.ndarray, press: np.ndarray, tags: dict | None, kl: np.ndarray | None = None) -> dict | None:
    """The food budget per cell, t/km2/yr (PW-977): the prey under the peoples P and their overkill pressure (lineages.prey.field: overkill outside
    refuges, livestock), over a dragon's foraging reach and one ring out to sea, and what the land supplies: the sustainable offtake of
    the wild herds (OFFTAKE) plus the tolerable share of the herders' stock (STOCK_TOLERABLE). Stage 2 (BUDGET): the peoples' hunters
    (density x their game need, `h._meat`) take first from the wild offtake; the giants and the rest of the predator guild (guild_ratio x
    the dragons' own food at the Carbone density of the prey there) take next, from what is left of the wild offtake and the stock;
    the dragons get the rest, `food`. Keys: prey, wild, stock (the supply's two parts), peoples, giants, guild (what each took, at most
    what was there), pool (the supply left after the peoples), food (the dragons'), live (the smoothed livestock, t/km2). None without
    a prey field. kl: the peoples' kill on the giants (`kill`; default from P at the step's time)."""
    if h.prey_wild is None:
        return None
    ref = PR.refuge(tags) if tags is not None else np.zeros(h.grid.n, bool)
    f = PR.field(h.prey_wild, press, ref, PR.stocked(P, h._herd, EST), overkill=overkill(h))
    wild, live = _reach(h, f["wild"]), _reach(h, f["livestock"])
    W, L = OFFTAKE * wild, STOCK_TOLERABLE * live
    z = np.zeros_like(W)
    out = {"prey": wild + live, "wild": W, "stock": L, "peoples": z, "giants": z, "guild": z, "live": live}
    if BUDGET:
        x = np.where(P >= EST, P, 0.0)
        hunt = _reach(h, (x * h.dens_cells() * h._meat[:, None]).sum(0)) * getattr(h.tree, "game_share", 1.0)  # (meta.game_share: the part of
        # the peoples' game that is the dragons' own prey)
        out["peoples"] = take_p = np.minimum(hunt, W)
        pool = W - take_p + L
        gi = np.zeros_like(W)
        if kl is None and any(l.megafauna and "flies" not in l.traits for l in h.lines):
            kl = kill(h, P, h._land_now)
        for k, l in enumerate(h.lines):
            if l.megafauna and "flies" not in l.traits:
                gi += x[k] * local_density(h, k, kl, wild + live) * giant_cattle_yr(eco_mass(h, l)) * PR.HEAD_T
        gi = _reach(h, gi)
        out["giants"] = np.minimum(gi, pool)
        if kl is None:
            kl = kill(h, P, h._land_now)
        # (PW-990 B: the guild's smaller carnivores take their size classes' part of what is left, less what the young dragons eat inside it
        # (dragon_share, PW-1071), and only as many as the peoples' kill leaves them (guild_kept, PW-1070): what a pressed guild leaves, the
        # dragons can take, the release running both ways. Every natural mode alike (lane 90): under "prey" the guild was guild_ratio x the
        # dragons' Carbone food, which at the sourced intake law asks ~1.3x the whole offtake and starved the dragons)
        gd = (1.0 - dragon_share(h)) * (pool - out["giants"]) * guild_kept(h, kl)
        out["guild"] = np.minimum(gd, pool - out["giants"])
        out["pool"] = pool
        out["food"] = pool - out["giants"] - out["guild"]
    else:
        out["pool"] = out["food"] = W + L
    return out


def prey_and_food(h: History, P: np.ndarray, press: np.ndarray, tags: dict | None, kl: np.ndarray | None = None) -> tuple:
    """(prey per cell, t/km2; the food the dragons can live on there, t/km2/yr; the smoothed livestock, t/km2): `budget`'s prey, food and
    live. All None without a prey field."""
    b = budget(h, P, press, tags, kl)
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
        if food is None and prey is None and getattr(h, "_deep_food", None) is not None:  # (the deep epoch's budget, PW-1062)
            return h._deep_food / (h.dragon_struct["cattle_yr"] * PR.HEAD_T)
        if food is not None and getattr(h, "_sea_hunt", None) is not None and h._sea_hunt[k]:
            food = food + h.sea_food  # (D28 B: a sea hunter's food is the land's and the sea's)
        return food / (h.dragon_struct["cattle_yr"] * PR.HEAD_T) if food is not None else c * (prey if prey is not None else h.prey_ref)
    if h.mf_natural not in ("prey", "food") or h.prey_wild is None:
        return c
    if "flies" in l.traits:
        return c * (prey if prey is not None else h.prey_ref)
    return c * h.prey_prod if prey is not None else c


def pressure(h: History, P: np.ndarray, land: np.ndarray | None = None) -> np.ndarray:
    """Per cell, 0..1: the peoples' overkill pressure on the wild herds there (prey.field), 1 - exp(-N / PRESS_N0) with N the small folk
    per km2 (every line that is not megafauna nor an overlay, at its presence x density); also what marks peopled country (summary).
    It does not press the megafauna themselves (`kill`, PW-1068). A sea cell takes the most of the land next to it."""
    N = (np.where(P >= EST, P, 0.0) * h.dens_cells() * _small_w(h)[:, None]).sum(0)
    if land is not None:
        g = h.grid
        N = np.where(land, N, np.maximum(N, nbr_reduce(g, np.maximum, np.where(land, N, 0.0)[g.nbr_idx])))
    return 1.0 - np.exp(-N / PRESS_N0)


def _small_w(h: History) -> np.ndarray:
    """Per line, 1 for the small folk (every line that is not megafauna nor an overlay), else 0."""
    w = getattr(h, "_press_w", None)
    if w is None:
        w = h._press_w = np.array([0.0 if (l.megafauna or l.overlay) else 1.0 for l in h.lines])
    return w


def _pressed(h: History, k: int, kl, prey: np.ndarray | None, food: np.ndarray | None = None) -> np.ndarray:
    """Line k's natural density under the peoples' kill effort kl (per head a year, `kill`): natural x `kept`."""
    nat = np.maximum(natural(h, k, prey, food), 1e-12)
    return nat * kept(h, k, kl)


def food_scale(h: History, P: np.ndarray, kl: np.ndarray, prey: np.ndarray, food: np.ndarray) -> np.ndarray:
    """PW-977 stage 1: per cell, 1 where the dragons there (every kind together, under the peoples' kill kl) need no more than the
    food there (the sustainable offtake of the wild herds plus the herders' tolerable stock share), else food / need: where the land
    cannot feed them, fewer of them are born, survive or stay (starvation and emigration; the dragons' range grows until it holds
    its food). Each dragon needs the age schedule's mean food, cattle a year (dragon_ages.structure)."""
    need = np.zeros(h.grid.n)
    sea_need = np.zeros(h.grid.n)
    sh = getattr(h, "_sea_hunt", None)
    for j, l in enumerate(h.lines):
        if l.megafauna and "flies" in l.traits:
            d = np.where(P[j] >= EST, P[j], 0.0) * _pressed(h, j, kl, prey, food)
            need += d
            if sh is not None and sh[j]:
                sea_need += d
    supply = food
    if sh is not None and sh.any():  # (D28 B: the sea's food feeds only the sea hunters: their share of the need there)
        supply = food + h.sea_food * sea_need / np.maximum(need, 1e-30)
    need = need * h.dragon_struct["cattle_yr"] * PR.HEAD_T
    return np.minimum(1.0, supply / np.maximum(need, 1e-12))


def local_density(h: History, k: int, kl, prey: np.ndarray | None = None, food: np.ndarray | None = None,
                  P: np.ndarray | None = None) -> np.ndarray:
    """Megafauna line k's density per cell, per km2, under the peoples' kill kl (per head a year, `kill`; PW-1068): its natural density
    x `kept` (by age class for dragons): natural where nobody kills them, 0 where the kill outruns their breeding, never above natural. One rule for dragons and giants. Dragons are also held to the food there (food_scale; PW-977 stage 1) where the presences P and
    the food are given (the present's prey; not the deep epoch, whose plates lay elsewhere). Dragons, last, x meta.dragon_abundance (the
    world-builder's dial, not physics: `abundance`)."""
    flies = "flies" in h.lines[k].traits
    d = _pressed(h, k, kl, prey, food if flies else None)
    if FOOD_CAP and food is not None and P is not None and flies:
        d = d * food_scale(h, P, kl, prey, food)
    return d * abundance(h.tree) if flies else d


def abundance(tree) -> float:
    """meta.dragon_abundance (lane 103, owner 10-31: "a lever to pull to make 'em more or less numerous for a run"): a plain multiplier on
    every dragon kind's density everywhere, after the food, the food cap and the persecution, so the dragons' map and their pattern beside
    the peoples keep their shape and only the numbers scale. A world-builder's choice, not physics: at x2 the dragons eat twice the food
    the model's ecology gives them (a richer, more magical world). Default 1 (spec.ABUNDANCE_X)."""
    return float(getattr(tree, "dragon_abundance", 1.0))


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
            out.append(f"The age of {kind}: ~{r['peak']:,} {kind} {SP.years_ago(r['peak_kyr'])}, before the peoples spread; ~{r['present']:,} now.")
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
    hunt = None
    for i in range(max(1, int(round(RELEASE_KM / h.cell_km)), int(round(HUNT_KM / h.cell_km)) if flies else 0)):
        near = near | nbr_reduce(g, np.logical_or, near[g.nbr_idx])
        if flies and i + 1 == max(1, int(round(HUNT_KM / h.cell_km))):
            hunt = near.copy()
    # (PW-1065, lane 90: a dragon hunts its whole range, HUNT_KM out of its own country, rich prey or poor: there at RELEASE_K, the food
    # then setting how many it feeds; farther, to RELEASE_KM, only where the prey is plentiful, as before)
    reach = rich if hunt is None else np.maximum(rich, hunt.astype(float))
    return RELEASE_K * edge_fit(l, env, tags) * reach * (open_ & near)


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


LINKED_MVP = 1000.0  # PW-1069 (lane 90): the fewest a megafauna kind's linked population (its pockets within metapop_km) needs to last: "the
# loose consensus that at least thousands of individuals are needed for long-term persistence" (Marshall et al. 2021, Science 372:284, p. 285);
# "frequent estimates are a few thousand to at least 10,000 individuals" (Burness et al. 2001, PNAS 98:14518, p. 14521). The bottom of that
# range: a regional pocket of tens lasts only as part of a linked population of a thousand or more, never alone


def linked_mvp(h: History, l) -> float:
    """The viable number of a megafauna kind's linked population (History._viable): the long-lived line's own number (line_mvp), at least
    LINKED_MVP. Only the fade reads it; founding and origins keep line_mvp."""
    return max(float(h.line_mvp(l)), LINKED_MVP)


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
    """A giant's food, head of cattle a year: Kleiber BMR x 1.7 (a working human's level) over a head's edible kcal, `HEAD_KCAL`, the one
    figure the peoples and the dragons use (PW-1067; was the proposal's 625 Mcal)."""
    return 70.0 * mass_kg ** 0.75 * 1.7 * 365.0 / HEAD_KCAL


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
    kl = kill(h, P, h._land_now)
    bud = budget(h, P, press, tags, kl)
    prey, food, live, pool = (bud["prey"], bud["food"], bud["live"], bud["pool"]) if bud is not None else (None, None, None, None)
    lvs = None
    if h.prey_wild is not None:
        lvs = PR.field(h.prey_wild, press, PR.refuge(tags), PR.stocked(P, h._herd, EST), overkill=overkill(h))["livestock"]
    ds = h.dragon_struct
    dens = {k: local_density(h, k, kl, prey, food, P) for k, l in enumerate(h.lines) if l.megafauna}
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
        llab, ln_ = linked_pockets(h, held, metapop_km(l))  # (PW-1069: each pocket's linked population against the viable number)
        lpop = np.bincount(llab[held], weights=exp[held], minlength=ln_) if ln_ else np.zeros(0)
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
            lk = int(np.bincount(llab[sel & held]).argmax()) if (sel & held).any() and ln_ else None
            if lk is not None:
                pk["linked_pop"] = int(round(float(lpop[lk])))
                pk["viable"] = bool(lpop[lk] >= linked_mvp(h, l))
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
             "one_per_km2": one_per(held),
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
    peoples live, 1 per 65 where none hunt them): 2 in the swamp at 3.1, 10.2 ...'."""
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
    """'1 per 3,100 km² (1 per 5,000 where peoples live, 1 per 65 where none hunt them)'."""
    s = f"1 per {r['one_per_km2']:,} km²" if r.get("one_per_km2") else "?"
    if r.get("peopled_one_per_km2") and r.get("natural_one_per_km2"):
        s += f" (1 per {r['peopled_one_per_km2']:,} where peoples live, 1 per {r['natural_one_per_km2']:,} where none hunt them)"
    return s
