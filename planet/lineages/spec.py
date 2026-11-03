"""The lineage input: a graph of peoples with origin times, niches, traits, and soft wishes.

TOML (or JSON of the same shape); preset: planet/lineages/samples/dnd.toml. Each
[[lineage]] has an `origin` and a time `at` (years before the present: "8 Myr",
"450 kyr", "12000 yr"; a bare number is kyr):
- root:     arises in the world (no parents)
- split:    branches from `parents = [p]` (the usual tree edge); the parent ends at its last split unless `persists`
- arrival:  comes from outside the world (feywild, the planes) at `place = [lat, lon]` or where its habitat is best
- hybrid:   of two `parents`, where their ranges overlap; `contact = true` (default): it exists only where both
            parents meet (half-elves); false: it founds a people of its own. `linger = false` (contact only): it never
            outlives the meeting (no people of its own where the parents part: the half-elves of the canon). Whether it
            exists at all follows its parents' interfertility stage (STAGES, PW-752: only a viable pair makes a mixed
            people, a sterile one makes sterile young where they meet) unless `exempt = true` (the genre's half-elves
            and half-orcs). [[interfertile]] rows (a, b, tier 0..3 or stage) set a pair's stage by hand.
- template: an overlay on `parents` (hosts) from `at` on (tieflings): a `share` of the hosts' people,
            spreading from a few `sites` through the hosts' range only
- group:    a way of life within a people (`group_of = <people>`, default `at` GROUP_KYR): steppe and forest orcs,
            human seafarers and farmers. Not a split: it appears where its own niche beats its people's, never
            ends its people, mixes freely with it and its sister groups, and rolls up into it in the summaries.
            (The city minorities, `cities = true`, PW-889, were removed by PW-1369: they wait for a towns model.)
A root, arrival or split may say where its origin is placed (PW-763; soft multipliers on the origin's score, never forced):
`near = [ids]` / `far_from = [ids]` (relative to those lines' ranges when it starts; ones not yet alive are ignored),
`lat_band = [south, north]`, `landmass = "largest" | "elsewhere"`.
A line's `realm` (PW-775): "land" (default), "coast" (the sea cells next to land, the shelf and tidal flats: merfolk) or "sea"
(all open water, within its `temp_c` and its `elev_m` as a depth band in negative metres: storm giants). Marine lines (coast, sea)
only take root, arrival or split origins; they compete with each other, not with land peoples, who they meet on the shared coast
(the contact record, the brief); rain, prefers and avoids do not apply to them. The deep folk stay authored (no realm).
Megafauna (PW-855, PW-924: `megafauna = true`, the dragons and the true giants) are counted animals, not peoples: a handful per pocket
of their own country (history.megafauna), exempt from the peoples' range targets; `generation_yr` lowers their viable number,
`group_size = [least, most]` says how many live together and `rivalry` (0..1) weakens the competition they feel and give;
`mass_kg` (a giant kind's ecological mass; dragons' comes from meta.dragon_ages) sets the kind's natural density with
meta.megafauna_natural, which peoples press down to meta.dragon_km2 / meta.giant_km2 (PW-957, PW-963). A megafauna kind's habitat has
tiers (PW-1024, history.habitat): its own country (`prefers`, within `temp_c` and `rain_mm`) in full; `tolerates = [tags]`, places or
climates it accepts at the edges, at reduced suitability and with a margin round its comfort range; elsewhere a tenth; and, by
ecological release (history.megafauna.release), rich neighbouring land that no rival kind holds, at reduced density.
Niche learning (PW-1155, history.params.LEARN): a land people's habitat as given (comfort ranges, prefers, avoids, leanings) is its
cultural preference; its body limits are the same fit over a wider envelope, `limits = { cold_c, heat_c, rain_oct, elev_m, learn }`
(LIMIT_KEYS; defaults history.params BODY_C, BODY_OCT, BODY_ELEV_M; learn x its learning rate, 0 never), and `never = [{ what = tag,
is = "present" | "absent" }]` rules country out for good (sea folk away from the coast, drow in the desert). Living on country its
culture finds marginal, or pressed against it, a people learns it slowly, cell by cell (history.habitat._learn); megafauna, sea
peoples and overlays do not learn. Both tables are the body: inherited down the tree, a child's keys and entries added.
Sapience (PW-965): a stem may say `sapient = "T"`, the one dated "sapiens" node where minds arrive for the whole stem (it must lie
between the stem's start and its first split child: the kinds split after it and inherit it, they do not evolve minds apart).
`animals = true` (a non-persisting stem with split children) gives it a new kind of end, not extinction: at its last split the stem is
assumed to continue only as non-sapient animals (the dragons' wyverns, drakes and pseudodragons), untracked from then on: no people,
no tech, no megafauna count. It is the end a stem already has (history: the stem ends at its last split); the flag only says what
becomes of the rest, and the timeline marks it apart from extinction. Neither field changes the simulation.
So the "tree" is a DAG. Anything a line leaves out it inherits from its first parent.
[[use]] (by = a trait, a place tag or a line's id, good = land.GOODS, weight, optional pull) says what each way
of life looks for in the land (farmland, pasture, ores, harbours, coral coasts, volcanoes...); meta.land_pull how
strongly, or the use's own pull (a line takes the strongest pull of its favoured goods; history._land_mult);
strict = true: off those goods the habitat is cut, not lifted back to a mean of 1 (peoples bound to one country).
meta.mode (PW-695): "fantasy" (default; every line, the fantasy goods) or "real" (only the lines with `real = true`,
the humans, leave the rest out as if disabled; the fantasy goods (FANTASY_GOODS) drop out of [[use]]). Magic is PW-696.
meta.animals / animals_force / animals_at (PW-691, PW-710): the domesticable animals (animal_defs.TABLE; default every
real one), the fantasy ones whose rare taming is forced (tests) and the anchor dates; fantasy animals drop out in real mode.
meta.crops / crops_force / crops_at (PW-721): the same for the staple plants (crop_defs.TABLE).
meta.portal_mode / portals / portal_sites (PW-697): arrivals from outside come "off" (each at its best habitat),
or through N portals placed "random"ly or at interesting "sites" (history.History.portal_cells).
"""

from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass, field, replace
from pathlib import Path

# movement and behaviour (docs/proposals/lineages.md section 2). sea: share of the carried
# pressure kept per sea cell crossed (0: can't cross; establishment needs spread.EST, so 0.55 ~ 3 cells);
# relief: share kept per 1000 m climbed between cells is exp(-relief) (walkers 0.6); speed: x the base
# speed; the rest are habitat knobs. How dense, exploring, seafaring and insular a people is: DEMOGRAPHY.
TRAITS = {
    "flies": {"sea": 0.72, "relief": 0.0},
    "swims": {"sea": 0.55, "coast": 0.15},
    "coastal": {"coast": 0.6},
    "seafaring": {},  # (boats: its sea share, DEMOGRAPHY)
    "agricultural": {"farm": 1.0},
    "nomadic": {"speed": 2.0, "open": 0.3},
    "mountain": {"relief": 0.0, "mountain": 0.5},
    "hardy": {"widen": 1.25},
    "insular": {},  # (insularity and exploration: DEMOGRAPHY)
    "cosmopolitan": {},
    "subterranean": {"relief": 0.15, "widen": 1.15, "mountain": 0.3},
    "aggressive": {"push": 0.7},
    "denning": {"den": 0.5},  # (lane 83, owner D20: a people of dens and warrens in rock, kobolds and goblins. PW-1382 (Daniel 11-02:
    # prefer den ground, never rely on it): its density x(1 - den) where the land has no caves, rock shelters or ground to dig, x1 on the
    # best (the den good, dens.py; history.model.run); its habitat is not cut)
    "martial": {},  # (lane 83: its contest strength, DEMOGRAPHY: a disciplined, warlike people that holds and takes land, dwarves, hobgoblins)  # (PW-756: the load of its rivals is felt at this share, anywhere: a people that takes ground rather than shares it; history.run)
    "hunter": {},  # (no movement knob: hunting and foraging peoples are who tames dogs and first cultivates wild plants, PW-718, PW-721)
    "sea_hunter": {},  # (D28 B, lane 99: a megafauna kind that also lives on the sea's seals and other marine mammals, history.megafauna.sea_food)
    "miner": {},  # (no movement knob: what it looks for in the land is the [[use]] table's)
}
# ways of life (PW-723): how a people gets its living, a cultural trait (a group of a people may differ from it). The goods a
# way reads (weight per good; the same [[use]] rows a trait would give) REPLACE the food rows its traits would give
# (agricultural -> fertile, nomadic -> grazing; place and own-id rows stay), set who tames the herd animals (herd share),
# who first cultivates plants (gather share) and who tames dogs (forage share), and so the fuels and the brief's foods.
# A line with no way keeps its traits' rows. Raiding, tribute and trade belong on top of these (PW-661), not here.
WAYS = {
    "forager": {"foraging": 1.0},  # broad hunting and gathering
    "fisher_forager": {"foraging": 0.6, "fish": 1.0, "shellfish": 0.5},  # specialised, often settled, on rich coasts, rivers and lakes
    "horticulturalist": {"fertile": 0.5, "foraging": 0.5},  # gardens and swidden, still half gathered
    "farmer": {"fertile": 1.0},  # plough and irrigation
    "pastoral_nomad": {"grazing": 1.0},  # herds followed over open country, all year
    "transhumant": {"grazing": 0.7, "fertile": 0.3},  # herds moved between seasonal pastures from a home base with some fields
    "agro_pastoral": {"fertile": 0.5, "grazing": 0.5},  # fields and herds on the same ground
    "sea_nomad": {"fish": 1.0, "harbour": 0.7, "foraging": 0.3},  # boat-dwelling fishers moving along the coasts
}
WAY_FOOD = ("fertile", "grazing", "foraging", "fish", "shellfish")  # (the goods a way's rows replace from the traits; harbours, timber and the rest stay)
# what a way of life presses on others for (PW-756): way -> (good, share of the rivals' load that is felt there at full strength).
# Herders who keep their wealth on the hoof move all of it with them and are not tied to fields, so on good pasture they hold
# their ground against settled neighbours better than those do against them: the load of the rivals on good grazing land is
# felt at this share, in proportion to how far the people keeps herds (animals.herding; HERD_FULL: fully), so nothing before
# the herd animals are known to it (the farmers' analogue is the agricultural trait's push into fertile land, history.run).
WAY_PRESS = {"pastoral_nomad": ("grazing", 0.6)}
# how mobile a way of life is (owner, on PW-936: nomads overlap more). Herders who move with the seasons share a country with settled
# peoples more readily than two settled peoples do: they use the open pasture and the stubble the fields leave, and trade animals,
# hides and dairy for grain and goods, with raids now and then (the nomads' need of the settled world: Khazanov 1984, "Nomads and
# the Outside World"). A settled-mobile pair's competition both ways is x (1 - NOMAD_COEXIST x the more mobile one's WAY_MOBILE);
# what is left is the occasional conflict. Two herding peoples still compete in full for the same pasture.
WAY_MOBILE = {"pastoral_nomad": 1.0, "transhumant": 0.6, "agro_pastoral": 0.3}
NOMAD_COEXIST = 0.5
HERD_FULL = 0.5
LATE_SEA_KYR = 3.0  # short sea hops by boat (the spread's sea factor) from then, for a sea share >= SHORT_HOP_SHARE
SHORT_HOP_SHARE = 0.2
# long sea crossings (crossing.py): way -> (rate per kyr at a zero gap, length scale km, only since kyr ago).
# The chance a line reaches a landmass it doesn't hold in a step of dt kyr is 1 - exp(-dt x sum over its
# ways of rate x exp(-gap / L)) x the landing's habitat. 'raft' is everyone's (drift rafts, storms: monkeys
# across the young Atlantic, lemurs to Madagascar): a few hundred km once in a few Myr. Coastal foragers'
# canoes (Sahul ~60 kyr ago, ~100 km gaps), swimmers and fliers reach further. Every way but the raft is
# x the line's will to explore and leave home (crossing.modes).
HOPS = {
    "raft": (3e-4, 150.0, None),
    "coastal": (0.01, 250.0, None),
    "swims": (0.05, 400.0, None),
    "flies": (0.05, 700.0, None),
}
# boats (the way 'seafaring'): the share of a people's frontier that takes to the sea (sea_share) sets the
# rate, BOATS[0] x share / BOATS_FULL per kyr, and the reach, from BOATS[1] km at share 0 to BOATS[2] km at
# BOATS_FULL, from BOATS[3] kyr ago (the Lapita / Polynesian voyages, 1000s of km). A seafaring people
# (share 0.6) sails as the old 'seafaring' way did (1 /kyr, 1500 km); dwarves (0.05) put to sea ~12x less
# often and less far, but not never.
BOATS = (1.0, 300.0, 1500.0, 6.0)
BOATS_FULL = 0.6
# canoes (PW-677): before the voyaging (BOATS[3]) and since CANOES_KYR ago (Sahul ~60 kyr ago), a people with a
# sea share crosses the way boats do but only over short gaps (reach BOATS[1] km): modern peoples that have been
# around for tens of kyr reach the next landmass over a few hundred km of water, not only after the voyages.
CANOES_KYR = 60.0
# rafts and dugouts (PW-869): coastal and island-hopping peoples (sea share from RAFT_SHARE) cross short gaps (~100 km, rarely more) from RAFT_KYR
# ago: sapiens crossed the Red Sea and the Wallace islands well before Sahul (50-65 kyr ago); they carry no animals.
RAFT_KYR = 100.0

# demography and movement, per people (PW-650): each can be given in the spec; else it comes from the traits
# (the strongest value among its traits; 'insular' sets exploration and insularity whatever else).
# kind (PW-1275, owner 2026-11-01): a people's density comes from the shared density ladder (lineages.ladder: the way it lives in each
#   cell x what it knows x the land's productivity); `kind` is its own factor on that, 0.5-2 (filled 0.8-1.2 for now: 1 most peoples, 0.8
#   free-ranging kinds, 1.2 den peoples). `density` and `band_km2` are no longer given: a line's density is read off the run.
#   A separate patch with fewer than meta.viable_pop people fades (history.MVP_TAU_KYR), so a sparse people needs a large piece of good
#   country to hold a land at all. Who holds a land is not the density's: the contest goes by fit (history.params.FIT_Q, lane 83).
# explore 0..1: how readily the frontier pushes into marginal land and over the sea (long crossings x 2 explore).
# sea_share 0..1: the share of the frontier that tries water crossings (BOATS; short hops over straits from
#   LATE_SEA_KYR at >= SHORT_HOP_SHARE).
# insularity 0..1: resistance to mixing (the late relaxing of competition x 2 (1 - insularity)) and to leaving
#   home (long crossings x (1.25 - 0.5 insularity)).
# contest > 0 (lane 83, owner D20): martial strength where it contests land with a rival, x on its contest strength (history.params.FIT_Q:
#   x1.5 presses x1.5 harder on its rivals and feels them x1/1.5, within the fit clip). 1 is a people that fights for land as most do; the
#   'martial' trait gives 1.5 (owner: dwarves and hobgoblins, "rather capable and fighty"). A design dial, not a measured number
BAND = 25  # people in a band: band_km2 = BAND / density, the land a band roams
KIND_RANGE = (0.5, 2.0)  # the kind factor's allowed span (owner PW-1275)
DEMO_DEFAULT = {"kind": 1.0, "explore": 0.5, "sea_share": 0.03, "insularity": 0.5, "contest": 1.0}
DEMOGRAPHY = {
    "nomadic": {"explore": 0.7},
    "subterranean": {"explore": 0.35},
    "flies": {"explore": 0.65},
    "seafaring": {"sea_share": 0.6, "explore": 0.7},
    "swims": {"sea_share": 0.4},
    "coastal": {"sea_share": 0.3},
    "cosmopolitan": {"insularity": 0.2, "explore": 0.7},
    "insular": {"insularity": 0.85, "explore": 0.25},
    "martial": {"contest": 1.5},
}
DEMO_KEYS = tuple(DEMO_DEFAULT)
GENERATION_YR = 25.0  # default generation time of a people, years: human foragers 25-30 (Fenner 2005; Langergraber et al. 2012); per line `generation_yr`, inherited by splits and groups
VIABLE_POP = 500.0  # default meta.viable_pop
DRAGON_KM2 = 5000.0  # default meta.dragon_km2 (owner, PW-923, PW-957): one dragon per this many km2 where peoples press them, every kind
GIANT_KM2 = 2000.0  # default meta.giant_km2 (owner, PW-963 option C): one true giant per this many km2 where peoples press them, every
# kind that does not fly. Both are nominal since PW-1068: the competition between lines and the viable-population check take them, but
# no density is set by them (each kind stands at its natural density under the peoples' persecution kill, history.megafauna.kill)
RIVALS_X = (0.0, 0.5, 1.0, 2.0)  # meta.rivals: x the rest of the predator guild's share of the food (history.megafauna.guild_ratio; 0: dragons
# eat alone, no rival predators). Default 1: Carbone, Turvey & Bielby 2011's Cretaceous size classes
GAME_SHARE_X = (0.0, 0.25, 0.5, 1.0)  # meta.game_share: the share of the peoples' wild game that comes out of the dragons' own (cattle-sized)
# prey, the rest being small game a dragon would not live on. Default 1 (all of it; no source either way: inbox draft forager-offtake)
OVERKILL_X = (0.0, 0.1, 0.23, 0.46, 0.6)  # meta.overkill: the share of the wild big herbivores lost where peoples press the land fully
# (prey.field). Default 0.6 (prey.OVERKILL); Sandom et al. 2014 (Fig. 3, p. 5; species lost, not biomass): about 0.46 where modern humans
# arrived first, 0.23 where archaic hominins were there before, near 0 in Africa (at most 13%)
PRESS_X = (0.25, 0.5, 1.0, 2.0, 4.0)  # the choices of meta.press_early / meta.press_late (owner 10-30, D14: the viewer's "how hard peoples
# press dragons and giants", one setting for the early eras and one for the late): multipliers on the peoples' kill (history.megafauna.KILL_Q);
# early holds at the stone age (tech level 0), late at the top (tech level 1), the eras between blend them by their tech level. Default 1, 1
ABUNDANCE_X = (0.25, 0.5, 1.0, 2.0, 4.0)  # the choices of meta.dragon_abundance (lane 103, owner 10-31: "a lever to pull to make 'em more or
# less numerous for a run"): x every dragon kind's density (history.megafauna.abundance), after the food and the persecution. A world-builder's
# choice, not physics. Default 1: the model's ecology
FORAGER_KM2 = 0.1  # default meta.forager_km2: human foragers per km2, the giants' natural-density baseline (scaled by mass^-0.75). No
# located source (PW-976): Hamilton et al. 2007's fit implies 0.03-0.09 for groups of 25-1,000, so 0.1 is the top of that; owner 10-28
# made it a setting (option C) until Binford 2001 can be checked
GIANT_MASS_KG = 2200.0  # a giant kind's ecological mass where the tree gives none: the hill giant's, the proposal's recommended column
MEGAFAUNA_NATURAL = ("food", "prey", "mesotherm", "mammal")  # meta.megafauna_natural (PW-957, PW-966, PW-990): the megafauna's natural density.
# food (owner 10-29, PW-990 option B, the default): a dragon's from its part of the land's surplus after the peoples and the rest of the
# predator guild (history.megafauna.budget), giants as under prey; prey: dragons on the prey field (Carbone & Gittleman 2002, now the
# cross-check); mesotherm / mammal: uniform from mass on Marshall et al. 2021's Damuth lines
MEGAFAUNA_NATURAL_DEFAULT = "food"
MEGAFAUNA_NATURAL_LABELS = {"food": "from the food: their share of the land's surplus", "prey": "from the prey (cross-check)",
                            "mesotherm": "dinosaur line, ~1/65 km²", "mammal": "mammal carnivores, ~1/137 km²"}  # (the peoples editor's menu)
# meta.dragon_ages (PW-958): the dragons' mortality schedule, lineages.dragon_ages.SCHEDULES (base | younger | harsher | gentler);
# meta.dragon_generation (PW-959): schedule | schedule_mass | line. Both candidates until the PW-967 review


def demography(traits) -> dict:
    """The demography knobs a set of traits gives (DEMOGRAPHY: the strongest value; 'insular' overrides)."""
    out = dict(DEMO_DEFAULT)
    for k in DEMO_KEYS:
        vals = [DEMOGRAPHY[t][k] for t in traits if k in DEMOGRAPHY.get(t, {}) and t != "insular"]
        if vals:
            out[k] = max(vals) if k != "insularity" else min(vals)
        if "insular" in traits and k in DEMOGRAPHY["insular"]:
            out[k] = DEMOGRAPHY["insular"][k]
    return out


# senses and bodies (PW-694): what a people tastes, digests and is poisoned by, for the future cuisine pass (PW-692);
# the simulation reads only `diet` (animals.DIET_LEAN: meat-eaters lean to herds over crops, PW-1373) and `fire` (below). Real-world analogues: cats lack the sweet receptor, birds feel no capsaicin,
# lactase persistence in herding humans, onions and garlic poison dogs, cats and birds, chocolate (theobromine) too.
# Inherited from the first parent key by key (a `body` table in the spec gives only what differs).
# The culinary keys (PW-726; intake section 4.3): suction (drinking and slurping), teeth, gut (ruminants are foregut),
# salt (herbivores crave it), display (horns are permanent and ringed, antlers shed yearly) and shed (who sheds: one
# clock or two), display_sex (both | males: which sexes carry horns or antlers, as real species differ: reindeer and oryx both,
# deer, moose and impala males only; PW-730), hours (when it is active), thermo (ectotherms feast and fast) and fire (false: cooks without fire).
# `milk` is the lactase share (fresh milk or fermented only); `milks = false` says a people does not milk its animals at all
# (default: herders milk, PW-784; animals.summary and the brief read it). `grain` (normal | moderate | none, PW-850) is how much grain a
# gut takes: ruminants do eat grain if adapted gradually (acidosis comes from sudden high-grain feeding), so 'moderate'; the brief says so. Only `fire = false` is read by a pass (fuels.py); the rest are for the story and the culinary brief.
BODY_DEFAULT = {"sweet": True, "milk": False, "milks": True, "capsaicin": True, "bitter": "normal", "smell": "normal",
                "diet": "omnivore", "raw_meat": False, "cellulose": False, "toxic": [],
                "suction": "normal", "teeth": "grinding", "gut": "simple", "salt": "normal", "display": "none",
                "shed": "none", "display_sex": "both", "hours": "diurnal", "thermo": "endo", "fire": True, "grain": "normal"}
BODY_CHOICES = {"bitter": ("low", "normal", "high"), "smell": ("low", "normal", "keen"),
                "diet": ("herbivore", "omnivore", "carnivore", "obligate_carnivore"),
                "suction": ("none", "poor", "normal"), "teeth": ("grinding", "conical", "dental_pad", "beak"),
                "gut": ("simple", "hindgut", "foregut"), "salt": ("normal", "craving"), "display": ("none", "horns", "antlers"),
                "shed": ("none", "both", "males"), "display_sex": ("both", "males"), "hours": ("diurnal", "crepuscular", "nocturnal"), "thermo": ("endo", "ecto"),
                "grain": ("normal", "moderate", "none")}
TOXINS = ("alliums", "theobromine")
BODY_BOOLS = ("sweet", "milk", "capsaicin", "raw_meat", "cellulose")


def parse_body(v, lid: str = "") -> dict:
    """Validate a `body` table (only the keys given)."""
    if v in (None, ""):
        return {}
    if not isinstance(v, dict):
        raise ValueError(f"{lid}: body must be a table of {sorted(BODY_DEFAULT)}")
    out = {}
    for k, x in v.items():
        if k not in BODY_DEFAULT:
            raise ValueError(f"{lid}: unknown body key {k!r} (one of {sorted(BODY_DEFAULT)})")
        if k in BODY_BOOLS:
            # true / false, or a share 0..1 of the people (lactase persistence is a population frequency, PW-701)
            if isinstance(x, bool):
                out[k] = x
            elif isinstance(x, (int, float)) and 0 <= x <= 1:
                out[k] = float(x)
            else:
                raise ValueError(f"{lid}: body.{k} must be true, false or a share between 0 and 1")
        elif k in ("fire", "milks"):
            if not isinstance(x, bool):
                raise ValueError(f"{lid}: body.{k} must be true or false")
            out[k] = x
        elif k == "toxic":
            xs = [x] if isinstance(x, str) else list(x)
            bad = [t for t in xs if t not in TOXINS]
            if bad:
                raise ValueError(f"{lid}: unknown toxicity {bad} (one of {list(TOXINS)})")
            out[k] = sorted(set(xs))
        else:
            if x not in BODY_CHOICES[k]:
                raise ValueError(f"{lid}: body.{k} must be one of {list(BODY_CHOICES[k])}")
            out[k] = x
    return out


def body_notes(b: dict) -> list[str]:
    """What is notable about a body (differences from the human-like baseline), as short phrases. A share
    (0 < x < 1) reads as 'x% ...'."""
    out = []
    pct = lambda v: f"{round(100 * v)}% "  # noqa: E731
    if b["sweet"] is not True:
        out.append("cannot taste sweet" if not b["sweet"] else pct(b["sweet"]) + "taste sweet")
    if b["milk"]:
        out.append("digest milk as adults" if b["milk"] is True else pct(b["milk"]) + "digest milk as adults")
    if b.get("milks") is False:
        out.append("do not milk their animals")
    if b["capsaicin"] is not True:
        out.append("feel no capsaicin heat" if not b["capsaicin"] else pct(b["capsaicin"]) + "feel capsaicin heat")
    if b["bitter"] != "normal":
        out.append("taste bitterness faintly" if b["bitter"] == "low" else "are very sensitive to bitter tastes")
    if b["smell"] != "normal":
        out.append("have a poor sense of smell" if b["smell"] == "low" else "have a keen sense of smell")
    if b["diet"] != "omnivore":
        out.append({"herbivore": "are herbivores", "carnivore": "are carnivores",
                    "obligate_carnivore": "are obligate carnivores"}[b["diet"]])
    if b["raw_meat"]:
        out.append("eat raw meat safely" if b["raw_meat"] is True else pct(b["raw_meat"]) + "eat raw meat safely")
    if b["cellulose"]:
        out.append("digest cellulose" if b["cellulose"] is True else pct(b["cellulose"]) + "digest cellulose")
    for k, text in (("suction", {"none": "cannot suck (they lap or tip their drink)", "poor": "suck poorly"}),
                    ("teeth", {"conical": "have conical, tearing teeth", "dental_pad": "have a dental pad and no upper incisors",
                               "beak": "have a beak and no teeth"}),
                    ("gut", {"hindgut": "ferment plant food in a hindgut", "foregut": "ferment plant food in a foregut (they chew the cud)"}),
                    ("salt", {"craving": "crave salt"}),
                    ("display", {"horns": "carry permanent horns (growth rings)", "antlers": "carry antlers, shed yearly"}),
                    ("shed", {"both": "shed antlers in both sexes", "males": "shed antlers in males only"}),
                    ("hours", {"crepuscular": "are active at dawn and dusk", "nocturnal": "are active at night"}),
                    ("thermo", {"ecto": "are ectotherms (their appetite follows the weather)"}),
                    ("grain", {"moderate": "take grain in moderation (a rumen adapted gradually; fields lead with legumes, roots and leafy fodder)",
                               "none": "cannot take grain"})):
        if b.get(k) in text:
            out.append(text[b[k]])
        if k == "display" and b.get("display") in ("horns", "antlers") and b.get("display_sex") == "males":
            out[-1] += ", in males only"  # (which sexes carry the display: real species differ, PW-730)
    if b.get("fire") is False:
        out.append("cook without fire")
    tox = [{"alliums": "alliums (onion, garlic)", "theobromine": "theobromine (chocolate)"}[t] for t in b["toxic"]]
    if tox:
        out.append("are poisoned by " + " and ".join(tox))
    return out


TIER_KYR = (10.0, 1100.0, 4000.0)  # split depths under which peoples are T0, T1, T2 (else T3): interfertility tiers, PW-727. Real hybrids: fertile out to ~1-2 Myr of divergence (horse x donkey is ~4 Myr and mostly sterile; wolf x dog, bison x cattle fertile), mostly sterile to ~4 Myr, none beyond (PW-851)
TIER_FERTILITY = (1.0, 1.0, 0.1, 0.0)  # share of hybrid matings that bear fertile young at each tier (T2: 0.2 at the edge of T1 falling to 0.02 at the edge of T3, see fertility_at)
# PW-752 (owner 10-29): realistic genetics decides who can have children together and for how long after a split. The tiers are four
# stages, in the order a split passes through them: viable (T0: the young are one people with both parents), absorbed (T1: fertile
# young, raised in one parent's people; no mixed people of their own, the genes flow across the border as a cline), sterile (T2: young
# are born where the parents meet, mostly sterile: they never live on as a people) and impossible (T3: no young; also two lines with no
# common ancestor, an arrival from outside and the natives). A hybrid line marked `exempt` (the genre's half-elves and half-orcs) is a
# people of its own whatever its parents' stage; a preset's [[interfertile]] rows set a pair's stage by hand.
STAGES = ("viable", "absorbed", "sterile", "impossible")
STAGE_NOTES = {"viable": "children together, of either people or a mixed people",
               "absorbed": "fertile children, raised in one parent's people (no mixed people of their own)",
               "sterile": "children born, mostly sterile (no lasting mixed people)",
               "impossible": "no children together"}
REALMS = ("land", "coast", "sea")
def fertility_at(d_kyr: float, tier_kyr: tuple = TIER_KYR) -> float:
    """Share of hybrid matings bearing fertile young after d_kyr of divergence: 1 under the T1 limit (fertile, with the
    brake of a cline), then mostly sterile (0.2 falling to 0.02 across T2, log-linear), none beyond the T2 limit (PW-851)."""
    t1, t2 = tier_kyr[1], tier_kyr[2]
    if d_kyr < t1:
        return 1.0
    if d_kyr >= t2:
        return 0.0
    return float(0.2 * (0.02 / 0.2) ** ((d_kyr - t1) / max(t2 - t1, 1e-9)))


ORIGINS = ("root", "split", "arrival", "hybrid", "template", "group")
GROUP_KYR = 6.0  # a group's default time (kyr ago): the Holocene ways of life

# body limits (PW-1155): a line's `limits` table, its body envelope round its comfort range (history.habitat.tolerance; the defaults are
# history.params BODY_C, BODY_OCT, BODY_ELEV_M): cold_c and heat_c, degrees C of the annual mean below and above the comfort range;
# rain_oct, octaves of rain either side; elev_m, metres either side of a height band; learn, x the rate it learns new country (0: never,
# as the megafauna and the sea peoples). Inherited down the tree (the body), each key overridable
LIMIT_KEYS = ("cold_c", "heat_c", "rain_oct", "elev_m", "learn")
# what a kind can never live in, however long it learns (PW-1155, owner 10-30): `never = [{what = "coast", is = "absent"}]`, written like a
# wish: what is a place or climate (PLACES, GROUPS, Köppen codes), is "present" (never where it is: drow in the desert) or "absent" (never
# where it is not: tritons away from the coast). The learned habitat is 0 there (history.habitat._K); inherited, a child adds its own
NEVER_IS = ("present", "absent")

KOPPEN_CODES = ["Af", "Am", "Aw", "BWh", "BWk", "BSh", "BSk", "Csa", "Csb", "Csc", "Cwa", "Cwb", "Cwc", "Cfa", "Cfb",
                "Cfc", "Dsa", "Dsb", "Dsc", "Dsd", "Dwa", "Dwb", "Dwc", "Dwd", "Dfa", "Dfb", "Dfc", "Dfd", "ET", "EF"]
GROUPS = {  # Köppen groups usable in prefers / avoids (climate.KOPPEN ids)
    "tropical": [0, 1, 2], "rainforest": [0, 1], "savanna": [2], "arid": [3, 4, 5, 6], "desert": [3, 4],
    "steppe": [5, 6], "mediterranean": [7, 8, 9], "temperate": list(range(7, 16)), "subtropical": [10, 13],
    "oceanic": [14, 15], "continental": list(range(16, 28)), "subarctic": [18, 19, 22, 23, 26, 27],
    "polar": [28, 29], "tundra": [28],
}
PLACES = ("coast", "island", "mountain", "lowland", "inland", "forest", "open", "wetland",
          "jungle", "steppe", "desert", "tundra", "island_chain", "volcanic", "hills", "breaks")
# (history._tags; all usable as place wishes. volcanic: the world's volcanoes and young volcanic ground, land.goods,
# glacial and recent epochs only; hills: rolling country, moderate relief under the mountains; breaks: rugged open dry grassland, PW-1024)


@dataclass
class Lineage:
    id: str
    name: str = ""
    origin: str = "root"  # root | split | arrival | hybrid | template | group
    parents: list[str] = field(default_factory=list)
    ago_kyr: float = 0.0  # when it appears, splits, arrives, kyr before present
    temp_c: tuple[float, float] = (8.0, 24.0)  # comfort range of the annual mean (soft edges)
    rain_mm: tuple[float, float] = (400.0, 2500.0)  # comfort range of the annual rain (soft edges)
    elev_m: tuple[float, float] | None = None
    prefers: list[str] = field(default_factory=list)
    avoids: list[str] = field(default_factory=list)
    limits: dict = field(default_factory=dict)  # body limits (PW-1155, history.habitat.tolerance): margins of the body envelope round the comfort range, LIMIT_KEYS; inherited (it is the body)
    limits_given: dict = field(default_factory=dict)  # of it, what the spec gave on this line itself
    never: list[tuple[str, str]] = field(default_factory=list)  # hard body limits (PW-1155): (what, is) pairs, NEVER_IS; inherited, a child adds its own
    never_given: list[tuple[str, str]] = field(default_factory=list)  # of it, what the spec gave on this line itself
    tolerates: list[str] = field(default_factory=list)  # megafauna (PW-1024): places or climates held at reduced suitability (history.habitat TOLERATE_K), with a margin round the comfort range
    traits: list[str] = field(default_factory=list)
    generation_yr: float = GENERATION_YR  # years per generation (history.origin_mvp scales a daughter's founding floor with the generations it must persist); derived from the canon ages below where given
    adult_yr: float | None = None  # PW-1148 (lane 78): canon age of adulthood, yr; with lifespan_yr the life table (lineages.life_history) gives the generation time and growth rate
    lifespan_yr: float | None = None  # ...canon lifespan, yr
    breeding: str = "mammal"  # ...slow | mammal | brood (Rmax per generation 2 / 3.5 / 7, life_history.BREEDING)
    fertile_yr: tuple[float, float] | None = None  # ...the fertile window, yr (None: from the ages, life_history.FIRST_BIRTH / LAST_BIRTH)
    survival: str = "normal"  # ...normal | harsh (life_history.HARSH: few reach adulthood, more adult deaths)
    mortality: tuple | None = None  # ...annual mortality per stage (infancy, childhood, adulthood, elder), overriding the schedules
    raids: bool = False  # lane 97 (D25): a raider people (default: survival 'harsh'), whose canon losses rise on hostile borders and with in-fighting (history.counter)
    disease_resist: float = 0.0  # lane 97 (D25, PW-1192): 0..1, the share of plague and epidemic losses it shrugs off (dwarves 0.75); it still carries them
    band_pct: tuple[float, float] = (0.0, 100.0)  # lane 78: soft target for its share of the world's people, percent [min, max] (history.bands)
    founders: float | None = None  # arrival (PW-1150): how many people come through, in all its waves (None: today's founding patch)
    waves: int = 1  # arrival: how many waves they come in (history.params.WAVE_KYR apart, or as its plane's thinnings open)
    portal_n: int | None = None  # arrival: how many portals it comes through (None: meta.portals)
    plane: str = "beyond"  # arrival: the realm it comes from (the Feywild...): arrivals of one plane share its portals (wandering mode)
    speed_kmyr: float = 0.5  # expansion: how fast the frontier advances, km/yr (x the traits' speed)
    kind: float | None = None  # the kind factor on the density ladder (PW-1275; None: 1, or the parent's)
    explore: float | None = None  # 0..1, how readily it pushes into new land and over the sea
    sea_share: float | None = None  # 0..1, the share of its frontier that tries water crossings
    insularity: float | None = None  # 0..1, resistance to mixing and to leaving home
    contest: float | None = None  # > 0, its martial strength in a contest for land (lane 83; None: from the traits, DEMOGRAPHY)
    body: dict = field(default_factory=lambda: {**BODY_DEFAULT, "toxic": []})  # senses and body, resolved (BODY_DEFAULT)
    body_given: dict = field(default_factory=dict)  # of it, what the spec gave on this line itself
    way: str | None = None  # way of life (WAYS), inherited from the parent (a group's people) where not given; None: from the traits
    way_given: str | None = None  # of it, what the spec gave on this line itself
    realm: str = "land"  # land | coast (shore ring of sea cells) | sea (all sea cells): PW-775
    persists: bool = False  # keeps living after its last split child
    megafauna: bool = False  # a handful per country (dragons): its range hardly takes room from the peoples that share it (history.MEGAFAUNA_PUSH, PW-855)
    group_size: tuple[float, float] | None = None  # megafauna (PW-924): how many live together, [least, most] (dragons [1, 3]: solitary, a pair with young; giants [5, 20]: a steading); inherited by splits and groups
    rivalry: float = 1.0  # megafauna (PW-924): x the competition the line feels and gives (metallic dragons 0.5: they coexist more readily); inherited by splits and groups
    mass_kg: float | None = None  # megafauna (PW-957, PW-963): the ecological mass, kg, that sets the kind's natural density (history.megafauna); inherited from the first parent
    color: str | None = None
    place: tuple[float, float] | None = None  # arrival: lat, lon
    start_near: list[str] = field(default_factory=list)  # where its origin is placed (PW-763): near these lines' ranges...
    start_far: list[str] = field(default_factory=list)  # ...far from these (only those already alive when it starts)
    start_lat: tuple[float, float] | None = None  # ...within this latitude band (soft edges)
    start_land: str | None = None  # ...on the biggest landmass ('largest') or off it ('elsewhere')
    share: float = 0.1  # template / contact hybrid: share of the hosts' people
    contact: bool = True  # hybrid: exists only where both parents meet
    linger: bool = True  # contact hybrid: lives on as a small people of its own where its parents last met (False: never, PW-758)
    exempt: bool = False  # hybrid (PW-752): the genre exemption, a mixed people whatever its parents' interfertility stage (half-elves, half-orcs)
    sites: int = 3  # template: incursion sites
    extinct_kyr: float | None = None  # gone by this long before the present (dwindles over the time before)
    sapient_kyr: float | None = None  # a stem: the dated "sapiens" node where minds arrive for it (PW-965); not inherited. A marker, not simulated
    animals_end: bool = False  # PW-965: the line's end (its last split) is not extinction: the rest continues as non-sapient animals, untracked. A marker; not inherited
    custom: bool = False  # added by the user (the editor marks it), not from a preset
    real: bool = False  # lives in the real-world mode too (meta.mode = 'real' keeps only these lines, PW-695)
    children: list[str] = field(default_factory=list)  # split children

    @property
    def marine(self) -> bool:
        """Lives on sea cells (realm coast or sea), not on land."""
        return self.realm != "land"

    @property
    def parent(self) -> str | None:
        return self.parents[0] if self.origin == "split" else None

    @property
    def group_of(self) -> str | None:
        """The people a group belongs to (None for any other line)."""
        return self.parents[0] if self.origin == "group" else None

    @property
    def overlay(self) -> bool:
        """Lives on others' ranges, not a range of its own (templates, contact hybrids)."""
        return self.origin == "template" or (self.origin == "hybrid" and self.contact)

    def trait(self, key: str, default=None):
        """The strongest value of a trait knob over the line's traits."""
        vals = [TRAITS[t][key] for t in self.traits if key in TRAITS.get(t, {})]
        if not vals:
            return default
        return min(vals) if key in ("relief", "push") else max(vals)

    def label(self) -> str:
        return self.name or self.id

    def demo(self, key: str) -> float:
        """A demography knob: as given (or inherited), else from the traits (DEMOGRAPHY)."""
        v = getattr(self, key)
        return float(v) if v is not None else demography(self.traits)[key]

    def demos(self) -> dict:
        return {k: self.demo(k) for k in DEMO_KEYS}

    def given_demo(self) -> dict:
        return {k: getattr(self, k) for k in DEMO_KEYS if getattr(self, k) is not None}


PAIR_WANTS = ("near", "apart", "among")  # wishes between two peoples. among (PW-889): a lives readily among b, inside b's country
# (bugbears among goblins and hobgoblins): the pair competes much less (history.params.AMONG_TOLERANCE), b's frontier does not invade a's
# cells, and they live beside each other in a cell's composition as a 'near' pair do; no pull on the habitat


@dataclass
class Wish:
    a: str
    want: str  # near | apart | among | one of PLACES
    b: str | None = None
    weight: float = 1.0


@dataclass
class Use:
    """A way of life looking for a good in the land: lines with trait (or preferred place, or the line whose id
    is) `by` favour (weight > 0) or avoid (< 0) the world's `good` (land.GOODS) in their habitat; `pull`
    (0..1, default meta.land_pull) how strongly; the use's own strength is pull x min(weight, 1) (PW-635: a weight of
    0.5 pulls half as hard as a weight of 1, so mines can bite harder than forests); `strict`: the habitat off the goods is cut by the pull,
    not renormalised to a mean of 1 over the line's country (history._land_mult)."""
    by: str
    good: str
    weight: float = 1.0
    pull: float | None = None
    strict: bool = False


ERAS = ("stone age", "bronze age", "classical", "medieval", "renaissance", "industrial")
ERA_DEFAULT = "renaissance"  # meta.era: the vague D&D-default present (PW-690). The technology tree (techtree.py) caps what
# the peoples know by the present at it; the history is not run forward past the present for it.

FANTASY_GOODS = ("mithril",)  # land.GOODS entries that are not geology (resources group 'fantasy'); real mode ignores them
MODES = ("fantasy", "real")
MODE_DEFAULT = "fantasy"  # meta.mode (PW-695): fantasy = every people and the fantasy goods; real = humans only (lines marked real = true), real goods
PORTAL_MODES = ("off", "random", "sites", "wandering")  # wandering (lane 78): thinnings that drift, open and close (history.portals)
WAVE_KYR = 2.0  # default meta.wave_kyr: an arrival's waves come this far apart (a judgement: a few kyr between the waves of a migration)
PORTAL_OPEN_KYR = 5.0  # default meta.portal_open_kyr: a wandering thinning stays open about this long (x U(0.4, 1.6), as volcanism.hotspots draws a plume's life)
PORTAL_DRIFT_KMKYR = 100.0  # default meta.portal_drift_kmkyr: how fast a plane's frame slides over the world (a judgement: ~500 km over an opening)
BAND_ROUNDS = 3  # default meta.band_rounds: re-runs of the best try that nudge peoples into their share bands (history.bands)
PORTAL_SITES = ("forest", "desert", "reef", "volcano")  # (history.History.portal_sites: deepest forest, middle of a desert, a coral reef, the foot of a volcano)
LAND_PULL = 0.5  # default: habitat x(1 - pull + pull G), G the best of a line's goods (mean 1 over its country)
BRAKE_X = (0.0, 0.5, 1.0, 2.0, 4.0)  # the choices of meta.raiders and meta.war (lane 97, D25; history.counter): how hard the raiders are
# braked (raid losses, culling wars) and how much land war takes: war-torn land from crowded, stateless peoples and every people's
# in-fighting where it has filled its land and has nowhere to split off to (lane 101, D31); default 1, 0 off
SURGE_X = (0.0, 0.5, 1.0, 2.0)  # the choices of meta.surge_early / meta.surge_late (owner 10-30, lane 73): how strongly a people on the upswing
# contests land others hold, x history.params.SURGE_Q (0: no momentum edge); early before the farming onset, late at the present, blended between. Default 1, 1


@dataclass
class Tree:
    name: str
    seed: int
    lines: dict[str, Lineage]
    wishes: list[Wish]
    mixing_start_kyr: float = 3.0
    source: str | None = None
    disabled: list[str] = field(default_factory=list)  # lines switched off (enabled = false) and those that went with them
    uses: list[Use] = field(default_factory=list)  # [[use]]: trait or place -> good, weight
    land_pull: float = LAND_PULL
    surge_early: float = 1.0  # the momentum edge's dial in the early eras (SURGE_X, lane 73)
    surge_late: float = 1.0  # ... and at the present
    raiders: float = 1.0  # meta.raiders (BRAKE_X, lane 97): the raiders' brakes
    war: float = 1.0  # meta.war (BRAKE_X, lane 97): war-torn land and every people's in-fighting (lane 101)
    era: str = ERA_DEFAULT  # meta.era: the target era of the present (placeholder for the technology tree, PW-690)
    animals: list[str] | None = None  # meta.animals: the domesticable animals (animal_defs.IDS) of the world; None: every real one; [] none
    animals_force: list[str] = field(default_factory=list)  # meta.animals_force: fantasy animals whose rare taming is certain (tests)
    animals_at: dict = field(default_factory=dict)  # meta.animals_at: id -> anchor time of the taming, kyr ago (default: the table's)
    crops: list[str] | None = None  # meta.crops: the cultivated plants (crop_defs.IDS) of the world; None: every real one; [] none
    crops_force: list[str] = field(default_factory=list)  # meta.crops_force: fantasy crops whose rare domestication is certain (tests)
    crops_at: dict = field(default_factory=dict)  # meta.crops_at: id -> anchor time of the first cultivation, kyr ago
    mode: str = MODE_DEFAULT  # meta.mode: 'fantasy' (all the peoples, the fantasy goods) or 'real' (only the lines marked real, real goods; PW-695)
    portal_mode: str = "off"  # meta.portal_mode: arrivals from outside: 'off' (each at its best habitat), 'random' or 'sites' (PW-697)
    portals: int = 1  # meta.portals: how many portals the arrivals come through (portal_mode random / sites)
    portal_sites: list[str] = field(default_factory=lambda: list(PORTAL_SITES))  # meta.portal_sites: the kinds of place 'sites' draws from
    viable_pop: float = VIABLE_POP  # a separate patch of a people with fewer people fades (history.MVP_TAU_KYR)
    draw_ranges: bool = False  # meta.draw_ranges (PW-1383): draw the density ladder's sourced numbers from their published ranges (ranges.py), seeded by meta.seed; off: the fixed values
    growth_rates: bool = False  # meta.growth_rates (PW-1147, lane 78): each people's growth rate r (life_history) sets its spread, displacement, fade and jumps
    wave_kyr: float = WAVE_KYR  # meta.wave_kyr: years between an arrival's waves, kyr
    portal_open_kyr: float = PORTAL_OPEN_KYR  # meta.portal_open_kyr: a wandering thinning's mean opening, kyr
    portal_drift_kmkyr: float = PORTAL_DRIFT_KMKYR  # meta.portal_drift_kmkyr: a plane's drift over the world, km per kyr
    band_rounds: int = BAND_ROUNDS  # meta.band_rounds: calibration re-runs for the share bands (history.bands)
    dragon_km2: float = DRAGON_KM2  # dragons (megafauna that fly): one per this many km2, nominal (PW-923, PW-957; PW-1068: competition and viable numbers only)
    forager_km2: float = FORAGER_KM2  # human foragers per km2, the giants' natural-density baseline (PW-976)
    giant_km2: float = GIANT_KM2  # giants (megafauna that do not fly): one per this many km2, nominal (PW-963; PW-1068: competition and viable numbers only)
    press_early: float = 1.0  # how hard peoples press dragons and giants in the early eras: x the kill at tech level 0 (PRESS_X, owner D14)
    press_late: float = 1.0  # ... and in the late eras: x the kill at tech level 1 (blended by tech level between)
    rivals: float = 1.0  # x the rival predator guild's share of the dragons' food (RIVALS_X)
    dragon_abundance: float = 1.0  # x every dragon kind's density, a world-builder's dial, not physics (ABUNDANCE_X; history.megafauna.abundance)
    game_share: float = 1.0  # the share of the peoples' wild game taken from the dragons' prey (GAME_SHARE_X)
    overkill: float = 0.6  # the share of wild big herbivores lost where peoples press the land fully (OVERKILL_X; prey.OVERKILL)
    megafauna_natural: str = MEGAFAUNA_NATURAL_DEFAULT  # the megafauna's natural density: food | prey | mesotherm | mammal (PW-957, PW-966, PW-990)
    dragon_ages: str = "base"  # the dragons' age schedule (PW-958, lineages.dragon_ages)
    dragon_generation: str = "schedule"  # the dragons' generation time: from the schedule, with fecundity ~ mass, or the lines' own (PW-959)
    tier_kyr: tuple = TIER_KYR  # meta.tier_kyr: split depths (kyr) under which two peoples are T0, T1, T2 (else T3; PW-727)
    exonyms: list = field(default_factory=list)  # [[exonym]]: the folk categories a people's neighbours are named by (reputation.py, PW-731)
    events: list = field(default_factory=list)  # [[event]]: dated conquests the reputation pass remembers (reputation.parse_events, PW-730)
    reputation: dict = field(default_factory=dict)  # meta.reputation: knobs of the reputation pass (reputation.params)
    tiers: list = field(default_factory=list)  # [[interfertile]]: per-pair overrides [a, b, tier 0..3] (`tier`, or `stage` by name: STAGES)

    def uses_of(self, l: Lineage) -> list[tuple[str, float]]:
        """The goods a line looks for (from its traits and preferred places), weights summed per good."""
        out: dict[str, float] = {}
        for u in self._uses_by(l):
            out[u.good] = out.get(u.good, 0.0) + u.weight
        return [(k, v) for k, v in out.items() if v != 0]

    def _uses_by(self, l: Lineage) -> list[Use]:
        rows = [u for u in self.uses if u.by in l.traits or u.by in l.prefers or u.by == l.id]
        if l.way:  # (the way's goods replace the food rows its traits give; place and own-id rows stay)
            rows = [u for u in rows if not (u.good in WAY_FOOD and u.by in TRAITS)]
            rows += [Use(l.way, g, w) for g, w in WAYS[l.way].items()]
        return rows

    def pulls_of(self, l: Lineage) -> dict[str, float]:
        """Per favoured good, how strongly it moves a line: the row's pull (meta.land_pull unless given) x
        min(weight, 1), the strongest row where several name the good (PW-635: the weight is the use's own strength)."""
        out: dict[str, float] = {}
        for u in self._uses_by(l):
            if u.weight > 0:
                p = (self.land_pull if u.pull is None else u.pull) * min(u.weight, 1.0)
                out[u.good] = max(out.get(u.good, 0.0), p)
        return out

    def pull_of(self, l: Lineage) -> float:
        """How strongly a line's land use acts at most: the strongest per-good pull (pulls_of); meta.land_pull
        for a line with no favoured good."""
        ps = self.pulls_of(l)
        return max(ps.values()) if ps else self.land_pull

    def strict_of(self, l: Lineage) -> bool:
        """Whether any of a line's favoured goods is a strict use (no renormalising of its land use)."""
        return any(u.strict for u in self._uses_by(l) if u.weight > 0)

    def order(self) -> list[Lineage]:
        """Lines oldest event first (parents before children)."""
        return sorted(self.lines.values(), key=lambda l: (-l.ago_kyr, l.id))

    def leaves(self) -> list[Lineage]:
        """What lives at the present (if the habitat lets it): lines with no split children, or persisting."""
        return [l for l in self.order() if not self.living_children(l.id) or l.persists]

    def living_children(self, lid: str) -> list[str]:
        """Split children that are not set to die out (a side branch that dies leaves its parent going)."""
        return [c for c in self.lines[lid].children if self.lines[c].extinct_kyr is None]

    def share_traits(self) -> list[str]:
        """The body flags some line gives as a share of its people (0..1), not true/false: mapped per cell
        as a population frequency (PW-701)."""
        return [k for k in BODY_BOOLS if any(not isinstance(l.body.get(k), bool) for l in self.lines.values() if not l.overlay)]

    def split_kyr(self, a: str, b: str) -> float | None:
        """Kyr since two lines last shared a population (None: no common ancestor, e.g. an arrival from outside and a native).
        A line splits from its parent when it appears, so the depth is the older of the two branchings below the
        common ancestor (0: the same people or one of its groups; a parent and its child: the child's age).
        An overlay (template, contact hybrid) counts as its closest parent (it is interfertile with its hosts)."""
        la, lb = self.lines[a], self.lines[b]
        if self.people_of(a) == self.people_of(b):
            return 0.0
        if la.overlay or lb.overlay:
            ca = la.parents if la.overlay else [a]
            cb = lb.parents if lb.overlay else [b]
            ds = [self.split_kyr(x, y) for x in ca for y in cb]
            ds = [d for d in ds if d is not None]
            return min(ds) if ds else None
        ca = [a, *self.ancestors(a)]  # (an arrival from outside has no ancestor in the world: none in common with the natives, but its own
        # split children descend from it: elves and drow are kin, PW-752)
        cb = [b, *self.ancestors(b)]
        common = next((x for x in ca if x in cb), None)
        if common is None:
            return None
        ta, tb = ca[:ca.index(common)], cb[:cb.index(common)]
        d = [self.lines[x].ago_kyr for x in (ta[-1:] + tb[-1:])]
        return max(d) if d else 0.0

    def tier_of(self, a: str, b: str) -> int:
        """Interfertility tier of two lines from the depth of their split (meta.tier_kyr: T0 under 10 kyr or the
        same people, T1 under 1.1 Myr, T2 under 4 Myr, else T3), unless a [[interfertile]] row names the pair."""
        for x, y, t in self.tiers:
            if {x, y} == {a, b}:
                return t
        d = self.split_kyr(a, b)
        if d is None:
            return 3
        return next((i for i, lim in enumerate(self.tier_kyr) if d < lim), 3)

    def fertility(self, a: str, b: str) -> float:
        """Share of hybrid matings of two lines that bear fertile young, from their split depth (PW-851). An [[interfertile]]
        row gives its tier's nominal share; no common ancestor (an arrival from outside, another root) gives 0: no young
        (PW-752: realistic genetics; the genre's half-elves are a hybrid line's `exempt`, not a fertility)."""
        for x, y, t in self.tiers:
            if {x, y} == {a, b}:
                return TIER_FERTILITY[t]
        d = self.split_kyr(a, b)
        return 0.0 if d is None else fertility_at(d, self.tier_kyr)

    def stage_of(self, a: str, b: str) -> str:
        """The interfertility stage of two lines (STAGES, from tier_of): viable, absorbed, sterile or impossible (PW-752)."""
        return STAGES[self.tier_of(a, b)]

    def hybrid_factor(self, l: Lineage) -> tuple[float, bool]:
        """(the share of its parents' meeting a hybrid line's people make up, x its `share`; whether it can live on where they part)
        by its parents' stage (PW-752): exempt or viable (1, its own linger); absorbed or impossible (0: no mixed people; absorbed
        young are counted in a parent's people); sterile (the share of matings bearing fertile young, fertility_at; never lingers:
        sterile young leave no people behind). 1 and its linger for any other line."""
        if l.origin != "hybrid" or l.exempt:
            return 1.0, l.linger
        st = self.stage_of(*l.parents)
        if st == "viable":
            return 1.0, l.linger
        if st == "sterile":  # (born where the parents meet; sterile young found no people of their own, contact = false)
            return (self.fertility(*l.parents) if l.contact else 0.0), False
        return 0.0, False

    def groups_of(self, lid: str) -> list[str]:
        """The groups (ways of life) within a people, oldest first."""
        return [l.id for l in self.order() if l.group_of == lid]

    def people_of(self, lid: str) -> str:
        """The people a line belongs to: its people for a group, else itself."""
        return self.lines[lid].group_of or lid

    def ancestors(self, lid: str) -> list[str]:
        out, l = [], self.lines[lid]
        while l.parents:
            out.append(l.parents[0])
            l = self.lines[l.parents[0]]
        return out


_T = re.compile(r"^\s*([0-9.eE+-]+)\s*(myr|ma|mya|kyr|ka|kya|yr|y|years?|bp)?\s*(ago)?\s*$", re.I)


def parse_ago(v) -> float:
    """'8 Myr' / '450 kyr' / '12000 yr' / a bare number (kyr) -> kyr before present."""
    if isinstance(v, (int, float)):
        return float(v)
    m = _T.match(str(v))
    if not m:
        raise ValueError(f"can't read the time {v!r} (use e.g. '8 Myr', '450 kyr', '12000 yr')")
    x, u = float(m.group(1)), (m.group(2) or "kyr").lower()
    return x * 1000 if u in ("myr", "ma", "mya") else x / 1000 if u in ("yr", "y", "year", "years", "bp") else x


def _pair(v, what):
    if v is None:
        return None
    if not (isinstance(v, (list, tuple)) and len(v) == 2 and float(v[0]) <= float(v[1])):
        raise ValueError(f"{what} must be [low, high], got {v!r}")
    return (float(v[0]), float(v[1]))


def _mass(r: dict, base, lid: str) -> float | None:
    """A megafauna line's `mass_kg` (> 0), else its first parent's."""
    if "mass_kg" not in r:
        return base.mass_kg
    m = float(r["mass_kg"])
    if m <= 0:
        raise ValueError(f"{lid}: mass_kg must be > 0")
    return m


def _check_tag(t, lid):
    if t in GROUPS or t in PLACES or t in KOPPEN_CODES:
        return t
    raise ValueError(f"{lid}: unknown climate or place {t!r} (Köppen codes, {sorted(GROUPS)} or {list(PLACES)})")


LIFE_KEYS = ("adult_yr", "lifespan_yr", "breeding", "fertile_yr", "survival", "mortality")  # inherited by splits and groups
ARRIVAL_KEYS = ("founders", "waves", "portals", "plane")


def _life(r: dict, base, origin: str, lid: str) -> dict:
    """The life-history, share-band and arrival fields of a raw row (lane 78)."""
    from . import life_history as LH
    inh = origin in ("split", "group")
    out = {}
    for k in ("adult_yr", "lifespan_yr"):
        v = r.get(k)
        out[k] = float(v) if v not in (None, "") else (getattr(base, k) if inh else None)
        if out[k] is not None and not out[k] > 0:
            raise ValueError(f"{lid}: {k} must be > 0")
    if (out["adult_yr"] is None) != (out["lifespan_yr"] is None):
        raise ValueError(f"{lid}: give adult_yr and lifespan_yr together")
    if out["adult_yr"] is not None and not out["adult_yr"] < out["lifespan_yr"]:
        raise ValueError(f"{lid}: adult_yr must be under lifespan_yr")
    out["breeding"] = str(r.get("breeding") or (base.breeding if inh else "mammal"))
    if out["breeding"] not in LH.BREEDING:
        raise ValueError(f"{lid}: breeding must be one of {list(LH.BREEDING)}")
    out["survival"] = str(r.get("survival") or (base.survival if inh else "normal"))
    if out["survival"] not in LH.SURVIVAL:
        raise ValueError(f"{lid}: survival must be one of {list(LH.SURVIVAL)}")
    fy = r.get("fertile_yr")
    out["fertile_yr"] = _pair(fy, "fertile_yr") if fy not in (None, "", []) else (base.fertile_yr if inh else None)
    mo = r.get("mortality")
    if mo not in (None, "", []):
        if len(mo) != 4 or any(not 0 <= float(v) < 1 for v in mo):
            raise ValueError(f"{lid}: mortality is four annual rates 0..1 (infancy, childhood, adulthood, elder)")
        out["mortality"] = tuple(float(v) for v in mo)
    else:
        out["mortality"] = base.mortality if inh else None
    rd = r.get("raids")
    out["raids"] = bool(rd) if rd not in (None, "") else out["survival"] == "harsh"  # (a raider is a people living by its losses, whatever its parent)
    dr = r.get("disease_resist")
    out["disease_resist"] = float(dr) if dr not in (None, "") else (base.disease_resist if inh else 0.0)
    if not 0.0 <= out["disease_resist"] <= 1.0:
        raise ValueError(f"{lid}: disease_resist must be within 0..1")
    bp = r.get("band_pct")
    out["band_pct"] = _pair(bp, "band_pct") if bp not in (None, "", []) else (0.0, 100.0)
    if not 0 <= out["band_pct"][0] <= out["band_pct"][1] <= 100:
        raise ValueError(f"{lid}: band_pct must be [min, max] within 0..100")
    if bp not in (None, "", []) and origin in ("group", "template", "hybrid"):
        raise ValueError(f"{lid}: band_pct is for a people (a root, split or arrival; its groups count in its share)")
    fo = r.get("founders")
    out["founders"] = float(fo) if fo not in (None, "") else None
    out["waves"] = int(r.get("waves", 1) or 1)
    pn = r.get("portals")
    out["portal_n"] = int(pn) if pn not in (None, "") else None
    out["plane"] = str(r.get("plane") or "beyond")
    if origin != "arrival":  # (an arrival's own fields mean nothing on a root or split: left in a row whose origin was changed, as
        # the workbench and the peoples suite's edits do, they are ignored rather than refused; lane 78b)
        out.update(founders=None, waves=1, portal_n=None, plane="beyond")
    if out["founders"] is not None and not out["founders"] > 0:
        raise ValueError(f"{lid}: founders must be > 0")
    if not 1 <= out["waves"] <= 20:
        raise ValueError(f"{lid}: waves must be within 1..20")
    if out["portal_n"] is not None and not 1 <= out["portal_n"] <= 12:
        raise ValueError(f"{lid}: portals must be within 1..12")
    return out


def band_warnings(t) -> list[str]:
    """The share bands' sums (lane 78): the minimums past 100% or the maximums under it can't all be met."""
    peoples = [l for l in t.lines.values() if not l.overlay and not l.megafauna and l.origin != "group"]
    lo = sum(l.band_pct[0] for l in peoples)
    hi = sum(l.band_pct[1] for l in peoples)
    out = []
    if lo > 100 + 1e-9:
        out.append(f"the peoples' minimum shares add up to {lo:g}% (over 100%): not all can be met")
    if hi < 100 - 1e-9:
        out.append(f"the peoples' maximum shares add up to {hi:g}% (under 100%): not all can be met")
    return out


def load(path: str | Path, mode: str | None = None) -> Tree:
    p = Path(path)
    raw = json.loads(p.read_text()) if p.suffix == ".json" else tomllib.loads(p.read_text())
    t = parse(raw, mode)
    t.source = str(p)
    return t


def _parents_of(r) -> list[str]:
    ps = r.get("parents")
    if ps is None and r.get("group_of"):
        ps = [r["group_of"]]
    if ps is None:
        ps = [r["parent"]] if r.get("parent") else []
    return [str(x) for x in ([ps] if isinstance(ps, str) else ps)]


def parse(raw: dict, mode: str | None = None) -> Tree:
    """mode: overrides meta.mode ('fantasy' | 'real'); in real mode only the lines marked `real = true` live."""
    meta = raw.get("meta", {})
    mode = str(mode or meta.get("mode") or MODE_DEFAULT).strip().lower()
    if mode not in MODES:
        raise ValueError(f"meta.mode must be one of {list(MODES)}")
    given = raw.get("lineage") or raw.get("lineages") or []
    if not given:
        raise ValueError("no [[lineage]] entries")
    rows = {}
    for r in given:
        lid = str(r["id"])
        if lid in rows:
            raise ValueError(f"lineage {lid!r} given twice")
        rows[lid] = r
    lines: dict[str, Lineage] = {}

    def build(lid: str, seen=()) -> Lineage:
        if lid in lines:
            return lines[lid]
        if lid in seen:
            raise ValueError(f"lineage {lid!r} is its own ancestor")
        r = rows[lid]
        pars = _parents_of(r)
        origin = str(r.get("origin") or ("split" if pars else "root"))
        if origin not in ORIGINS:
            raise ValueError(f"{lid}: origin must be one of {ORIGINS}")
        lo, hi = {"root": (0, 0), "arrival": (0, 0), "split": (1, 1), "hybrid": (2, 2), "template": (1, 9), "group": (1, 1)}[origin]
        if not lo <= len(pars) <= hi:
            raise ValueError(f"{lid}: a {origin} line takes {lo}{'' if lo == hi else '+'} parent(s), got {pars}")
        for q in pars:
            if q not in rows:
                raise ValueError(f"{lid}: unknown parent {q!r}")
        bases = [build(q, seen + (lid,)) for q in pars]
        base = bases[0] if bases else Lineage(id="")
        when = next((r[k] for k in ("at", "split", "appears", "arrives", "ago") if k in r), None)
        if when is None and origin == "group":
            when = min(GROUP_KYR, 0.5 * bases[0].ago_kyr)
        if origin == "group" and bases[0].origin in ("group", "template") or origin == "group" and bases[0].overlay:
            raise ValueError(f"{lid}: a group belongs to a people of its own (not a group, template or contact hybrid)")
        if when is None:
            raise ValueError(f"{lid}: give at (e.g. at = '2 Myr')")
        ago = parse_ago(when)
        for b in bases:
            if ago >= b.ago_kyr:
                raise ValueError(f"{lid} at {ago:g} kyr must come after its parent {b.id} ({b.ago_kyr:g} kyr)")
        temp, rain, traits = base.temp_c, base.rain_mm, list(base.traits)
        if origin == "hybrid":  # between its parents
            a, b = bases
            temp = ((a.temp_c[0] + b.temp_c[0]) / 2, (a.temp_c[1] + b.temp_c[1]) / 2)
            rain = ((a.rain_mm[0] * b.rain_mm[0]) ** 0.5, (a.rain_mm[1] * b.rain_mm[1]) ** 0.5)
            traits = sorted(set(a.traits) | set(b.traits))
        traits = [str(x) for x in r.get("traits", traits)]
        for x in traits:
            if x not in TRAITS:
                raise ValueError(f"{lid}: unknown trait {x!r} (one of {sorted(TRAITS)})")
        if r.get("density") not in (None, "") or r.get("band_km2") not in (None, ""):
            raise ValueError(f"{lid}: density and band_km2 are no longer given: density comes from the density ladder (PW-1275); "
                             f"set `kind` (a factor {KIND_RANGE[0]}-{KIND_RANGE[1]}) instead")
        if r.get("cities") or r.get("hosts"):
            raise ValueError(f"{lid}: cities / hosts are no longer given: minorities in other peoples' towns were removed (PW-1369) "
                             "until a towns and minorities model")
        demo = {}
        # (lane 83b: a people split from a megafauna stem, the kobolds and dragonborn of the dragons, takes no demography from it: the stem's
        # numbers are a handful of solitary flying animals' (the dragons' explore 0.3, insularity 0.85), not a people's)
        off_mega = origin == "split" and bases and base.megafauna and not r.get("megafauna", False)
        for k in DEMO_KEYS:
            v = r.get(k)
            if v in (None, ""):
                # inherited from a split's parent where given there (else from its own traits); a hybrid's,
                # an arrival's or a template's from its own (merged) traits unless given
                demo[k] = getattr(base, k) if origin in ("split", "group") and not off_mega else None
                continue
            v = float(v)
            if k == "contest" and not v > 0:
                raise ValueError(f"{lid}: {k} must be > 0")
            if k == "kind" and not KIND_RANGE[0] <= v <= KIND_RANGE[1]:
                raise ValueError(f"{lid}: kind must be within {KIND_RANGE[0]}..{KIND_RANGE[1]}")
            if k not in ("kind", "contest") and not 0 <= v <= 1:
                raise ValueError(f"{lid}: {k} must be within 0..1")
            demo[k] = v
        lgiven = dict(r.get("limits") or {})
        for key, v in lgiven.items():
            if key not in LIMIT_KEYS:
                raise ValueError(f"{lid}: unknown limits key {key!r} (one of {LIMIT_KEYS})")
            if not isinstance(v, (int, float)) or v < 0:
                raise ValueError(f"{lid}: limits.{key} must be a number >= 0")
            lgiven[key] = float(v)
        ngiven = []
        for e in r.get("never", []):
            if not isinstance(e, dict) or set(e) - {"what", "is"} or "what" not in e:
                raise ValueError(f"{lid}: never takes tables {{what = <place or climate>, is = 'present' | 'absent'}}")
            how = str(e.get("is", "present"))
            if how not in NEVER_IS:
                raise ValueError(f"{lid}: never.is must be one of {NEVER_IS}")
            ngiven.append((_check_tag(str(e["what"]), lid), how))
        bgiven = parse_body(r.get("body"), lid)
        body = {**base.body, **bgiven} if bases else {**BODY_DEFAULT, **bgiven}
        body["toxic"] = list(body["toxic"])
        wgiven = r.get("way")
        if wgiven in ("",):
            wgiven = None
        if wgiven is not None and wgiven not in WAYS:
            raise ValueError(f"{lid}: unknown way of life {wgiven!r} (one of {sorted(WAYS)})")
        realm = str(r.get("realm") or (base.realm if origin == "split" else "land"))
        if realm not in REALMS:
            raise ValueError(f"{lid}: realm must be one of {REALMS}")
        if realm != "land" and origin not in ("root", "arrival", "split"):
            raise ValueError(f"{lid}: a marine line (realm {realm}) takes a root, arrival or split origin")
        place = r.get("place")
        if place is not None:
            place = (float(place["lat"]), float(place["lon"])) if isinstance(place, dict) else (float(place[0]), float(place[1]))
        sl = r.get("lat_band")
        if sl is not None:
            sl = _pair(sl, "lat_band")
            if not -90 <= sl[0] <= sl[1] <= 90:
                raise ValueError(f"{lid}: lat_band must be [south, north] within -90..90")
        sland = r.get("landmass")
        if sland not in (None, "", "largest", "elsewhere"):
            raise ValueError(f"{lid}: landmass must be 'largest' or 'elsewhere'")
        hints = {}
        for key in ("near", "far_from"):
            ids = [str(x) for x in r.get(key, [])]
            for q in ids:
                if q not in rows or q == lid:
                    raise ValueError(f"{lid}: {key} names an unknown line {q!r}")
            hints[key] = ids
        life = _life(r, base, origin, lid)
        if origin == "hybrid" and r.get("disease_resist") in (None, "") and bases:  # (a mixed people: its parents' mean, PW-1192)
            life["disease_resist"] = sum(b.disease_resist for b in bases) / len(bases)
        l = replace(base, id=lid, name=str(r.get("name", lid)), origin=origin, parents=pars, ago_kyr=ago,
                    temp_c=_pair(r.get("temp_c"), "temp_c") or temp,
                    rain_mm=_pair(r.get("rain_mm"), "rain_mm") or rain,
                    elev_m=_pair(r.get("elev_m"), "elev_m") if "elev_m" in r else base.elev_m,
                    prefers=[_check_tag(x, lid) for x in r.get("prefers", base.prefers)],
                    avoids=[_check_tag(x, lid) for x in r.get("avoids", base.avoids)],
                    tolerates=[_check_tag(x, lid) for x in r.get("tolerates", base.tolerates)],
                    limits={**(base.limits if bases else {}), **lgiven}, limits_given=lgiven,
                    never=list(dict.fromkeys((base.never if bases else []) + ngiven)), never_given=ngiven,
                    traits=traits, speed_kmyr=float(r.get("speed_kmyr", r.get("expansion_kmyr", base.speed_kmyr))), **demo,
                    generation_yr=float(r.get("generation_yr", base.generation_yr if origin in ("split", "group") else GENERATION_YR)),
                    body=body, body_given=bgiven, way=wgiven or (base.way if bases else None), way_given=wgiven, realm=realm, persists=bool(r.get("persists", False)), megafauna=bool(r.get("megafauna", base.megafauna if (bases and origin == "group") else False)), group_size=_pair(r.get("group_size"), "group_size") or (base.group_size if origin in ("split", "group") else None), rivalry=float(r.get("rivalry", base.rivalry if origin in ("split", "group") else 1.0)), mass_kg=_mass(r, base, lid), color=r.get("color"), place=place,
                    start_near=hints["near"], start_far=hints["far_from"], start_lat=sl, start_land=sland or None,
                    share=float(r.get("share", 0.1)), contact=bool(r.get("contact", True)),
                    linger=bool(r.get("linger", True)), exempt=bool(r.get("exempt", False)),
                    sites=int(r.get("sites", 3)), custom=bool(r.get("custom", False)), real=bool(r.get("real", False)), children=[],
                    extinct_kyr=parse_ago(r["extinct"]) if r.get("extinct") not in (None, "") else None,
                    sapient_kyr=parse_ago(r["sapient"]) if r.get("sapient") not in (None, "") else None,
                    animals_end=bool(r.get("animals", False)), **life)
        if l.sapient_kyr is not None and (origin == "group" or not 0 < l.sapient_kyr < ago):
            raise ValueError(f"{lid}: sapient ({l.sapient_kyr:g} kyr) must come after the stem appears ({ago:g} kyr) and before the present")
        if l.extinct_kyr is not None and not 0 <= l.extinct_kyr < ago:
            raise ValueError(f"{lid}: extinct ({l.extinct_kyr:g} kyr) must come after it appears ({ago:g} kyr)")
        lines[lid] = l
        return l

    for lid in rows:
        build(lid)
    # disabled lines (enabled = false) leave cleanly: a split child re-parents to the disabled line's parent
    # (or, under a disabled root or arrival, becomes a root or arrival itself, keeping the niche it inherited);
    # hybrids and templates of a disabled line go too (no half-elves without elves)
    off = {lid for lid, r in rows.items() if r.get("enabled", True) is False}
    if mode == "real":  # humans only: the lines marked real stay, the rest leave like a disabled line
        if not any(r.get("real") for r in rows.values()):
            raise ValueError("real mode needs lines marked `real = true` (the humans)")
        off |= {lid for lid, r in rows.items() if not r.get("real")}
    changed = True
    while changed:
        changed = False
        for l in lines.values():
            if l.id not in off and l.origin in ("hybrid", "template", "group") and any(q in off for q in l.parents):
                off.add(l.id)
                changed = True
    for l in sorted(lines.values(), key=lambda l: -l.ago_kyr):
        if l.id in off or l.origin != "split" or l.parents[0] not in off:
            continue
        p = lines[l.parents[0]]
        while p.id in off and p.origin == "split":
            p = lines[p.parents[0]]
        if p.id in off:
            l.origin, l.parents = ("arrival" if p.origin == "arrival" else "root"), []
        else:
            l.parents = [p.id]
    disabled = sorted(off)
    lines = {k: v for k, v in lines.items() if k not in off}
    for l in lines.values():
        if l.origin == "split":
            lines[l.parents[0]].children.append(l.id)
    for l in lines.values():  # the kinds split after the sapiens node and inherit it (PW-965)
        if l.sapient_kyr is not None:
            late = [c for c in l.children if lines[c].ago_kyr > l.sapient_kyr]
            if late:
                raise ValueError(f"{l.id}: sapient ({l.sapient_kyr:g} kyr) must come before its kinds split ({', '.join(late)} split earlier)")
        if l.animals_end and (l.persists or l.extinct_kyr is not None or not any(lines[c].extinct_kyr is None for c in l.children)):
            raise ValueError(f"{l.id}: animals = true needs a stem that ends at its last split (living split children; not persists, not extinct)")
    wishes = []
    for w in raw.get("wish", raw.get("wishes", [])):
        want = str(w["want"])
        if w["a"] in off or w.get("b") in off:
            continue
        if w["a"] not in lines or (w.get("b") and w["b"] not in lines):
            raise ValueError(f"wish {w}: unknown lineage")
        if want in PAIR_WANTS and not w.get("b"):
            raise ValueError(f"wish {w}: '{want}' needs b")
        if want not in PAIR_WANTS and want not in PLACES:
            raise ValueError(f"wish {w}: want must be near, apart, among or one of {PLACES}")
        wishes.append(Wish(str(w["a"]), want, w.get("b") or None, float(w.get("weight", 1.0))))
    from .land import GOODS
    uses = []
    for u in raw.get("use", raw.get("uses", [])):
        by, good = str(u.get("by", "")), str(u.get("good", u.get("layer", "")))
        if by in off or (mode == "real" and good in FANTASY_GOODS):
            continue
        if by not in TRAITS and by not in PLACES and by not in GROUPS and by not in KOPPEN_CODES and by not in lines:
            raise ValueError(f"use {u}: by must be a trait ({sorted(TRAITS)}), a place or climate tag or a line's id")
        if good not in GOODS:
            raise ValueError(f"use {u}: good must be one of {list(GOODS)}")
        pull = None if u.get("pull") in (None, "") else float(u["pull"])
        if pull is not None and not 0 <= pull <= 1:
            raise ValueError(f"use {u}: pull must be within 0..1")
        uses.append(Use(by, good, float(u.get("weight", 1.0)), pull, bool(u.get("strict", False))))
    t = Tree(str(meta.get("name", "peoples")), int(meta.get("seed", 1)), lines, wishes,
             float(parse_ago(meta.get("mixing_start", 3.0))))
    t.disabled = disabled
    t.mode = mode
    t.portal_mode = str(meta.get("portal_mode") or "off").strip().lower()
    if t.portal_mode not in PORTAL_MODES:
        raise ValueError(f"meta.portal_mode must be one of {list(PORTAL_MODES)}")
    t.portals = int(meta.get("portals", 1))
    if not 1 <= t.portals <= 12:
        raise ValueError("meta.portals must be within 1..12")
    t.portal_sites = [str(x) for x in meta.get("portal_sites", PORTAL_SITES)]
    if not t.portal_sites or any(x not in PORTAL_SITES for x in t.portal_sites):
        raise ValueError(f"meta.portal_sites must be some of {list(PORTAL_SITES)}")
    t.uses = uses
    t.growth_rates = bool(meta.get("growth_rates", False))
    t.draw_ranges = bool(meta.get("draw_ranges", False))
    for key, dflt in (("wave_kyr", WAVE_KYR), ("portal_open_kyr", PORTAL_OPEN_KYR), ("portal_drift_kmkyr", PORTAL_DRIFT_KMKYR)):
        setattr(t, key, float(meta.get(key, dflt)))
        if getattr(t, key) < 0 or (key != "portal_drift_kmkyr" and getattr(t, key) <= 0):
            raise ValueError(f"meta.{key} must be > 0")
    t.band_rounds = int(meta.get("band_rounds", BAND_ROUNDS))
    if not 0 <= t.band_rounds <= 8:
        raise ValueError("meta.band_rounds must be within 0..8")
    tk = tuple(float(parse_ago(x)) for x in meta.get("tier_kyr", TIER_KYR))
    if len(tk) != 3 or list(tk) != sorted(tk) or tk[0] <= 0:
        raise ValueError("meta.tier_kyr must be three rising split depths (T0, T1, T2 limits)")
    t.tier_kyr = tk
    for r in raw.get("interfertile", []):
        a, b, tr = str(r.get("a", "")), str(r.get("b", "")), r.get("tier")
        if r.get("stage") not in (None, ""):  # (the stage by name: viable, absorbed, sterile or impossible, PW-752)
            if r["stage"] not in STAGES or (tr is not None and tr != STAGES.index(r["stage"])):
                raise ValueError(f"interfertile {r}: stage must be one of {list(STAGES)} (and agree with tier if both are given)")
            tr = STAGES.index(r["stage"])
        if a in off or b in off:
            continue
        if a not in lines or b not in lines or a == b or tr not in (0, 1, 2, 3):
            raise ValueError(f"interfertile {r}: a and b must be two lines of the tree and a tier 0..3 or a stage {list(STAGES)}")
        t.tiers.append((a, b, int(tr)))
    from . import reputation as RP
    t.exonyms = RP.parse_rows(raw.get("exonym"), BODY_DEFAULT, BODY_CHOICES)
    t.events = RP.parse_events(raw.get("event"), lines, off)
    t.reputation = dict(meta.get("reputation") or {})
    bad = [k for k in t.reputation if k not in RP.KNOBS]
    if bad:
        raise ValueError(f"meta.reputation: unknown keys {bad}")
    from . import animal_defs as AD
    am = meta.get("animals")
    t.animals = None if am is None else [str(x) for x in am]
    t.animals_force = [str(x) for x in meta.get("animals_force", [])]
    for x in [*(t.animals or []), *t.animals_force, *(meta.get("animals_at") or {})]:
        if x not in AD.BY_ID:
            raise ValueError(f"meta.animals: unknown animal '{x}' (known: {', '.join(AD.IDS)})")
    t.animals_at = {str(k): parse_ago(v) for k, v in (meta.get("animals_at") or {}).items() if v not in (None, "")}
    if mode == "real":  # the fantasy domestications are left out in the real-world mode (PW-710)
        t.animals = [x for x in (AD.REAL_IDS if t.animals is None else t.animals) if not AD.BY_ID[x].fantasy]
        t.animals_force = [x for x in t.animals_force if not AD.BY_ID[x].fantasy]
    from . import crop_defs as CD
    cm = meta.get("crops")
    t.crops = None if cm is None else [str(x) for x in cm]
    t.crops_force = [str(x) for x in meta.get("crops_force", [])]
    for x in [*(t.crops or []), *t.crops_force, *(meta.get("crops_at") or {})]:
        if x not in CD.BY_ID:
            raise ValueError(f"meta.crops: unknown crop '{x}' (known: {', '.join(CD.IDS)})")
    t.crops_at = {str(k): parse_ago(v) for k, v in (meta.get("crops_at") or {}).items() if v not in (None, "")}
    if mode == "real":  # the fantasy plants are left out in the real-world mode
        t.crops = [x for x in (CD.REAL_IDS if t.crops is None else t.crops) if not CD.BY_ID[x].fantasy]
        t.crops_force = [x for x in t.crops_force if not CD.BY_ID[x].fantasy]
    t.land_pull = float(meta.get("land_pull", LAND_PULL))
    for k in ("surge_early", "surge_late", "raiders", "war"):
        setattr(t, k, float(meta.get(k, 1.0)))
        if getattr(t, k) < 0:
            raise ValueError(f"meta.{k} must be >= 0")
    t.era = str(meta.get("era") or ERA_DEFAULT).strip().lower()
    if t.era not in ERAS:
        raise ValueError(f"meta.era must be one of {list(ERAS)}")
    t.viable_pop = float(meta.get("viable_pop", VIABLE_POP))
    if t.viable_pop < 0:
        raise ValueError("meta.viable_pop must be >= 0")
    t.dragon_km2 = float(meta.get("dragon_km2", DRAGON_KM2))
    if t.dragon_km2 <= 0:
        raise ValueError("meta.dragon_km2 must be > 0")
    t.giant_km2 = float(meta.get("giant_km2", GIANT_KM2))
    if t.giant_km2 <= 0:
        raise ValueError("meta.giant_km2 must be > 0")
    for k, d in (("press_early", 1.0), ("press_late", 1.0), ("rivals", 1.0), ("game_share", 1.0), ("overkill", 0.6), ("dragon_abundance", 1.0)):
        setattr(t, k, float(meta.get(k, d)))
        if getattr(t, k) < 0:
            raise ValueError(f"meta.{k} must be >= 0")
    if t.game_share > 1 or t.overkill > 1:
        raise ValueError("meta.game_share and meta.overkill must be <= 1")
    t.forager_km2 = float(meta.get("forager_km2", FORAGER_KM2))
    if t.forager_km2 <= 0:
        raise ValueError("meta.forager_km2 must be > 0")
    from . import dragon_ages as DA
    for key, opts, dflt in (("megafauna_natural", MEGAFAUNA_NATURAL, MEGAFAUNA_NATURAL_DEFAULT), ("dragon_ages", tuple(DA.SCHEDULES), DA.DEFAULT),
                            ("dragon_generation", DA.GENERATION, DA.GENERATION_DEFAULT)):
        v = str(meta.get(key) or dflt).strip().lower()
        if v not in opts:
            raise ValueError(f"meta.{key} must be one of {list(opts)}")
        setattr(t, key, v)
    if not 0 <= t.land_pull <= 1:
        raise ValueError("meta.land_pull must be within 0..1")
    return t


def to_raw(t: Tree) -> dict:
    """The tree back in the input's shape (JSON-able)."""
    out = []
    for l in t.order():
        r = {"id": l.id, "name": l.name, "origin": l.origin, "at": f"{l.ago_kyr:g} kyr"}
        if l.origin == "group":
            r["group_of"] = l.group_of
        elif l.parents:
            r["parents"] = l.parents
        r.update(temp_c=list(l.temp_c), rain_mm=list(l.rain_mm), prefers=l.prefers, avoids=l.avoids,
                 **({"tolerates": l.tolerates} if l.tolerates else {}), traits=l.traits, speed_kmyr=l.speed_kmyr, generation_yr=l.generation_yr, **l.given_demo())
        if l.elev_m is not None:
            r["elev_m"] = list(l.elev_m)
        if l.marine or (l.origin == "split" and t.lines[l.parents[0]].marine):  # (a land tree's raw stays as it was)
            r["realm"] = l.realm
        if l.place is not None:
            r["place"] = list(l.place)
        if l.start_near:
            r["near"] = l.start_near
        if l.start_far:
            r["far_from"] = l.start_far
        if l.start_lat:
            r["lat_band"] = list(l.start_lat)
        if l.start_land:
            r["landmass"] = l.start_land
        if l.body_given:
            r["body"] = l.body_given
        if l.limits_given:
            r["limits"] = l.limits_given
        if l.never_given:
            r["never"] = [{"what": w, "is": i} for w, i in l.never_given]
        if l.way_given:
            r["way"] = l.way_given
        if l.color:
            r["color"] = l.color
        if l.persists:
            r["persists"] = True
        if l.megafauna:
            r["megafauna"] = True
        if l.group_size is not None:
            r["group_size"] = list(l.group_size)
        if l.rivalry != 1.0:
            r["rivalry"] = l.rivalry
        if l.mass_kg is not None:
            r["mass_kg"] = l.mass_kg
        if l.extinct_kyr is not None:
            r["extinct"] = f"{l.extinct_kyr:g} kyr"
        if l.sapient_kyr is not None:
            r["sapient"] = f"{l.sapient_kyr:g} kyr"
        if l.animals_end:
            r["animals"] = True
        if l.custom:
            r["custom"] = True
        if l.real:
            r["real"] = True
        if l.origin in ("template", "hybrid"):
            r["share"] = l.share
        if l.origin == "hybrid":
            r["contact"] = l.contact
            if not l.linger:
                r["linger"] = False
            if l.exempt:
                r["exempt"] = True
        if l.origin == "template":
            r["sites"] = l.sites
        if l.adult_yr is not None:
            r.update(adult_yr=l.adult_yr, lifespan_yr=l.lifespan_yr)
        if l.breeding != "mammal":
            r["breeding"] = l.breeding
        if l.survival != "normal":
            r["survival"] = l.survival
        if l.fertile_yr is not None:
            r["fertile_yr"] = list(l.fertile_yr)
        if l.mortality is not None:
            r["mortality"] = list(l.mortality)
        if l.raids != (l.survival == "harsh"):
            r["raids"] = l.raids
        if l.disease_resist:
            r["disease_resist"] = l.disease_resist
        if tuple(l.band_pct) != (0.0, 100.0):
            r["band_pct"] = list(l.band_pct)
        if l.origin == "arrival":
            if l.founders is not None:
                r["founders"] = l.founders
            if l.waves != 1:
                r["waves"] = l.waves
            if l.portal_n is not None:
                r["portals"] = l.portal_n
            if l.plane != "beyond":
                r["plane"] = l.plane
        out.append(r)
    return {"meta": {"name": t.name, "seed": t.seed, "mixing_start": f"{t.mixing_start_kyr:g} kyr", "land_pull": t.land_pull,
                     "surge_early": t.surge_early, "surge_late": t.surge_late, "raiders": t.raiders, "war": t.war,
                     "era": t.era, "viable_pop": t.viable_pop, "dragon_km2": t.dragon_km2, "giant_km2": t.giant_km2, "forager_km2": t.forager_km2,
                     "press_early": t.press_early, "press_late": t.press_late, "rivals": t.rivals, "dragon_abundance": t.dragon_abundance, "game_share": t.game_share, "overkill": t.overkill, "megafauna_natural": t.megafauna_natural, "dragon_ages": t.dragon_ages, "dragon_generation": t.dragon_generation,
                     **({"tier_kyr": [f"{x:g} kyr" for x in t.tier_kyr]} if t.tier_kyr != TIER_KYR else {}), "mode": t.mode, "portal_mode": t.portal_mode,
                     "portals": t.portals, "portal_sites": t.portal_sites, "growth_rates": t.growth_rates, "draw_ranges": t.draw_ranges, "wave_kyr": t.wave_kyr,
                     "portal_open_kyr": t.portal_open_kyr, "portal_drift_kmkyr": t.portal_drift_kmkyr, "band_rounds": t.band_rounds,
                     **({"reputation": t.reputation} if t.reputation else {}),
                     **({"animals": t.animals} if t.animals is not None else {}),
                     **({"animals_force": t.animals_force} if t.animals_force else {}),
                     **({"animals_at": {k: f"{v:g} kyr" for k, v in t.animals_at.items()}} if t.animals_at else {}),
                     **({"crops": t.crops} if t.crops is not None else {}),
                     **({"crops_force": t.crops_force} if t.crops_force else {}),
                     **({"crops_at": {k: f"{v:g} kyr" for k, v in t.crops_at.items()}} if t.crops_at else {})},
            "lineage": out, "exonym": t.exonyms,
            "event": [{**e, "at": f"{e['at']:g} kyr"} for e in t.events], "interfertile": [{"a": a, "b": b, "tier": x, "stage": STAGES[x]} for a, b, x in t.tiers],
            "wish": [{k: v for k, v in vars(w).items() if v is not None} for w in t.wishes],
            "use": [{k: v for k, v in vars(u).items() if v is not None and v is not False} for u in t.uses]}
