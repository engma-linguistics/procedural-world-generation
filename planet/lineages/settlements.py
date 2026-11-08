"""Settlements and cities v0, with lifecycles (PW-1011): a ledger of sites that rise and fall over the last ~12 kyr.

Output only, like demes.py: reads a finished peoples run and writes `settlements.json` plus `meta.settlements` into it. Nothing in
the history is read back or changed, so the peoples' outcomes are the same with or without it.

The model (every judgement constant is in the block below; `derive(..., **overrides)` and `planet settlements --set` change them):
- Grain: at most three live sites per cell (a cell is ~12,500 km^2 at L6, ~3,100 at L7), each at a seeded spot within it:
  the cell's chief place (everything below, unless said otherwise); a second people's own place (kind 'minority', PW-1105:
  a dwarf hold or a kobold warren inside the humans' country, friends or foes alike: owner 10-30), founded where the cell's
  second people is SECOND_MIN of the heads or more and big enough, sized as MINORITY_SHARE of its settled heads (a mining
  people: its halls, HOLD_SHARE of its heads) and placed toward the cell's highest neighbour for a mining people; it stays
  its founders' and merges into the chief place (no ruin) once they have led the cell for HAND_KYR; and a mine (kind 'mine',
  owner 10-30) on an ore district or a rock-salt bed (mining.ORE_MIN, SALT_MIN), worked by the lead people (else the second)
  once it knows 'mines' (and 'copper' for ore: mining from the first metalworking), MINE_SHARE of the cell's people.
- When a people may build: its technology (meta.techtree.known) caps the tier. 'villages' allows a village, 'towns' a town
  (TOWN_MIN or more people), 'cities' a city (CITY_MIN or more). The holder is the cell's people with most heads (mix_lead).
- How big, as a hierarchy of central places: a village gathers SHARE[1] of its own cell's sedentary people; a town SHARE[2]
  of its cell and the ring of cells around it (its hinterland), and only where its cell is the best site of that ring; a city
  SHARE[3] of two rings, and only where it is the best of those (so towns stand at least two cells apart and cities three).
  The best site is the sedentary people of the hinterland x the site factor. Each share is x the site factor, and the
  place takes the largest tier its holder may build and its cell may hold. Sedentary people = density (stored per frame: eraq 'dens') x cell area x farmers' share (eraq 'farm'),
  plus FISHER_SHARE of the others on a cell with a harbour or a navigable river (fisher and river villages), plus HOLD_SHARE of
  the holder's people where the holder is a mining people (trait miner or subterranean: dwarves) that knows 'mines' (the land
  use counts miners as neither farmers nor herders, so without this the dwarves' halls would hold no one). The site
  factor (SITE_MIN..SITE_MAX) adds for a harbour on a coast that is still a coast at that time, a navigable river, fresh
  water on site, fertile ground and a pass (the world's human-use layers, humanuse.py), and is capped by the tier allowed.
- Lifecycle, every STEP_KYR from the first frame within the land-use window (landuse.ERA_WINDOW_KYR) to the present, the
  frames' density, farm share and rain interpolated linearly in time, the land, ice and who lives there taken from the nearer
  frame: a site is founded when the target holds FOUND or more for FOUND_STEPS steps; its people relax toward the target
  with TAU_KYR; it is abandoned when the target stays under ABANDON for ABANDON_STEPS steps, or at once when the cell goes
  under the sea or the ice. Why (the first that holds): the sea, the ice, drought (rain DROUGHT or more below the rain at
  its founding), driven out (the holder changed in the last HAND_KYR, or the new holder cannot keep sites), else its people
  left. A ruin stays in the ledger; the cell can be settled again ("on the ruins of" the old site).
- Who lives there: a village's people are its cell's (mostly one people); a town's are its cell and the ring around it, a
  city's two rings, weighted by heads (towns draw people in: the realistic mixing of PW-910). (Minorities' quarters, PW-889, went with
  the city groups, PW-1369: they wait for a towns and minorities model.)
- Rivers moving: the history keeps the world's present rivers through time, so there is no drainage per frame to read. A
  stand-in: a site on a navigable river in the lowlands (under RIVER_LOW_M) is left at a seeded chance of RIVER_SHIFT per
  kyr ("the river moved away"), as floodplain rivers shift their beds; the cell may be settled again on the new course.
Not modelled in v0: war and raids (a change of hands is recorded, not a battle), placing sites on a regional zoom's terrain."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import numpy as np

from .. import store as S
from .. import timeline as T
from ..geo import R_KM, is_land
from ..grid import shared_grid
from . import landuse as LU
from .years import years_ago
from .demes import _place, landmass_rank
from .spread import graph_dist
from .techtree import keyed

# --- judgement constants (PW-1011 v0; see the docstring) -------------------------------------------------------------------
CONST = {
    "STEP_KYR": 0.1,        # the ledger's time step (100 years)
    "SHARE": (0.0, 0.02, 0.008, 0.010),  # share of the sedentary people of its hinterland (own cell; + 1 ring; + 2 rings) a village, town, city gathers
    "FISHER_SHARE": 0.25,   # share of the non-farmers on a harbour or navigable-river cell who live settled (fisher and river villages)
    "HOLD_SHARE": 0.5,      # share of a mining people's heads (the holder, by mix_lead_share) that live settled in its halls and mine towns
    "SITE_MIN": 0.6, "SITE_MAX": 2.0,  # the site factor's range (1 = an ordinary inland cell of middling soil)
    "SITE_HARBOUR": (0.0, 0.15, 0.3, 0.4),  # added for a harbour of class 0..3 (none, anchorage, harbour, fine) on a cell still on the coast
    "SITE_RIVER": (0.0, 0.15, 0.3, 0.4),    # added for a navigable river of class 0..3 (none, small boats, barges, ships)
    "SITE_FRESH": 0.2,      # added for fresh water on site (fresh_water class 3)
    "SITE_FERTILE": 0.4,    # x (fertile_score - 0.5): good soil adds, poor takes away
    "SITE_PASS": 0.1,       # added for a pass
    "FOUND": 300,           # people: a village is founded where the target holds this many ...
    "FOUND_STEPS": 2,       # ... for this many steps running
    # PW-1114: the size classes follow the era, keyed to what the holding people knows, not to the date (Earth dates are only the check).
    # Stage 0..4 = nothing, 'villages', 'towns', 'cities', 'cities' + 'roads' (the classical city: roads carry its food).
    "TOWN_MIN": (1000, 1000, 1000, 1000, 2000),  # people: a town, by stage (needs 'towns'). UNVERIFIED best knowledge (Fletcher 1995 pending): a
                            # Neolithic village is up to ~1,000 and a few thousand is a town; 2,000 once roads and long trade feed larger markets
    "CITY_MIN": 10000,      # people: a city (needs 'cities'). Anchor: the ancient-city cutoff of Reba et al. 2016 (Modelski: 10,000 for 3500-1000 BC)
    "TOWN_CAP": 5000,       # people: the largest a town can be where the people lack 'cities' (UNVERIFIED: the largest Neolithic towns were a few thousand)
    "CITY_CAP": (0, 0, 0, 100000, 1500000),  # people: the largest a city can be, by stage. Anchor (Reba et al. 2016 tables, figshare 2059494/2059497/2059500):
                            # largest listed city 100,000 (3000-2000 BC; 160,000 in 2000-1000 BC, which the roads stage covers); 1.0-1.5 million from 0 to AD 1800
    "TAU_KYR": 0.3,         # a site's people relax toward the target with this time constant
    "ABANDON": 120,         # people: a site whose target stays under this ...
    "ABANDON_STEPS": 3,     # ... for this many steps is abandoned
    "MINORITY_MAX": 2000,   # people: a second people's own (non-hold) place saturates toward this (x*K/(x+K)): the rest of a dense cell's minority lives in hamlets
    "HOLD_MAX": 80000,      # people: a hold's halls level off toward this (about the chief cities' largest in these runs, 70-80k)
    "MINORITY_STEPS": 5,   # PW-1117: a cell's second people must have been the same people for this many steps (0.5 kyr) before it may found a place
    "MINORITY_ABANDON_STEPS": 10,  # ... and its place is abandoned only after its target stays low this long (1 kyr): a second people's share moves often
    "DROUGHT": 0.25,        # rain this far below the rain at its founding makes an abandonment 'drought'
    "RIVER_SHIFT": 0.03,    # per kyr: chance a lowland river site is left because the river moved (a stand-in, see the docstring)
    "RIVER_LOW_M": 300.0,   # m: river sites below this are on a floodplain that can shift
    "HAND_KYR": 1.0,        # an abandonment within this of a change of hands is 'driven out'
    "JITTER": 0.35,         # a site's spot: up to this x the cell spacing from the cell's centre (seeded)
    "SERIES_KEEP": 40,      # points of a site's population series kept
    "QUARTER_MIN_PCT": 2,   # a people under this % of a place is left out of its 'who lives here'
    "SECOND_MIN": 0.05,     # a cell's second people may found a place of its own where it is this share of the heads or more (PW-1105) ...
    "MINORITY_SHARE": 0.1,  # ... gathering this share of its settled heads (a minority clusters in one place, where a cell's chief place
                            # gathers SHARE[1]: the rest live in hamlets), up to a village; a mining people's own place is its halls,
                            # HOLD_SHARE of its heads (+ MINORITY_SHARE of its farmers), up to a town (a hold) if it knows 'towns'
    "MINE_EDGE": 0.2,       # a second people works a cell's deposit instead of the lead when its mining affinity (MINING_TRAIT) is this much higher (PW-1116)
    "MINE_SHARE": 0.004,    # a mine's people: this share of its cell's people. Ore is mined from 'copper' on (the first metalworking,
                            # owner 10-30), rock salt from 'mines'
    # D12 (owner 10-30): mining follows need, not knowledge. A people opens mines where it wants their goods: its own farmers'
    # and herders' metal tools and salt (MINE_NEED), a town's or city's market within two rings (trade), or its own way of life
    # (a mining kind, MINE_KIND). Earth: the Archaic foragers of the Great Lakes hammered native copper from quarries for ~5 kyr
    # and never smelted; the Andes smelted from ~700 BC (ice cores) and Mesoamerica only from AD 800; large copper mines such as
    # the Great Orme open ~4 kyr ago, some three kyr after the first smelting (sources in docs/overview.md 2.25).
    "MINE_NEED": 0.3,       # farmers' + herders' share of a cell's people (eraq farm + herd) from which it wants metal tools and salt (judgement)
    "MINE_LAG_KYR": 1.0,    # median wait, per people (seeded, lognormal), from its copper smelting to its own first ore mines (judgement)
    "MINE_LAG_SIGMA": 0.5,  # ... its spread (ln)
    "MINE_EXPOSE_STEPS": 10,  # a people without the need takes mining up where a mine has stood within two rings this long (1 kyr): slow, by exposure
    "MINE_KIND": 0.8,       # a mining affinity (MINING_TRAIT) from this is a mining kind (miner or subterranean: dwarves, kobolds,
                            # gnomes): it mines for its own sake, at once, and sends colonies
    "COLONY_KM": 300.0,     # a mining kind works the rich districts this far from its own country as a colony of incomers (mining.COLONY_KM, PW-854)
    # PW-1146 (owner D18, option 3): small local pits on ordinary ore. A district is a rich seam (raw ore >= mining.ORE_MIN, one per ring);
    # a pit is a village's own copper or iron pit on ordinary ore (raw >= PIT_ORE, the old 0.5), opened by the lead people where it
    # smelts the metal and has the same need rule as a mine (farmers and herders, a market within two rings, a mining kind, exposure;
    # a mining kind at once, so its pits come first and near home). Denser than districts: the lower ore bar admits ~5x the cells, and
    # one pit per cell stands where the cell feeds it (PIT_SHARE of its people; PIT_FOUND), or one per ring of PIT_RINGS (0: every cell).
    "PIT_SHARE": 0.002,     # a pit's people: this share of its cell's people (a quarter or a half of a mine's) (judgement)
    "PIT_FOUND": 25,        # people: a pit is opened where its target holds this many (a mine: FOUND 300), for FOUND_STEPS running ...
    "PIT_ABANDON": 10,      # ... and is given up under this
    "PIT_RINGS": 1,         # 0: a pit in every eligible cell (2500 a run, ~17x the districts: too many); 1: only the best of a cell and its ring of 1 (~7x the districts)
    "COLONY_ORE": 0.75,     # ... an ore district this rich (the raw best ore good; PW-1146: districts are now >= mining.ORE_MIN = 0.75, so this is no stricter)
}
TIERS = ("none", "village", "town", "city")
STAGES = ("nothing", "villages", "towns", "cities", "cities and roads")  # (PW-1114: what the holding people knows sets the size classes)
PIT_ORE = 0.5  # a raw ore good from this, and under mining.ORE_MIN, is ordinary ore a village can dig (the old 'ore country')
KINDS = ("chief", "minority", "mine", "pit")
MERGED = "merged into the main place"  # (a minority's place whose people came to lead its cell: gone, but not a ruin)  # a cell's chief place, a second people's own place, a mine
TECH = ("villages", "towns", "cities")
LEDGER_TECHS = TECH + ("delving", "fortifications", "mines", "roads", "copper", "iron")  # (every tech the ledger reads: _tech_dates, _known_dates, _mines_dates)


def pop_at(s: dict, ago: float) -> float:
    """A ledger site's people at `ago` kyr (its series, oldest first), 0 before its founding or once it was left."""
    if ago > s["founded_kyr"] + 1e-6 or (s["abandoned_kyr"] is not None and ago <= s["abandoned_kyr"] + 1e-6):
        return 0.0
    sr = s["series"]
    for k in range(1, len(sr)):
        if sr[k][0] <= ago:
            (a0, p0), (a1, p1) = sr[k - 1], sr[k]
            return float(p1 if a0 == a1 else p0 + (p1 - p0) * (a0 - ago) / (a0 - a1))
    return float(sr[-1][1])


def ledger_dates(known: dict) -> dict:
    """{line: {tech: kyr ago}} of the techs the ledger reads (LEDGER_TECHS), from meta.techtree.known: two trees with the same make the
    same ledger (PW-1464)."""
    return {lid: {t: kn[t][0] for t in LEDGER_TECHS if t in kn} for lid, kn in known.items()}
NONE = 255


def tier_of(pop: float, c: dict, stage: int = 4) -> int:
    """0 none, 1 village, 2 town, 3 city for `pop` people held by a people at `stage` (see CONST TOWN_MIN)."""
    return 3 if pop >= c["CITY_MIN"] else 2 if pop >= c["TOWN_MIN"][stage] else 1 if pop >= c["ABANDON"] else 0


def _tech_dates(m: dict, n_lines: int) -> np.ndarray:
    """(lines, 3): kyr ago each line came to villages, towns, cities (-1: never)."""
    known = (m.get("techtree") or {}).get("known") or {}
    out = np.full((n_lines, 3), -1.0)
    for l in m["lineages"]:
        kn = known.get(l["id"]) or (known.get(l.get("group_of")) if l.get("group_of") else None) or {}
        for j, t in enumerate(TECH):
            if t in kn:
                out[l["index"], j] = float(kn[t][0])
    return out


MINERS = {"miner", "subterranean"}


def _known_dates(m: dict, n_lines: int, tech: str) -> np.ndarray:
    """(lines,): kyr ago each line (or its people, for a group) came to `tech` (-1: never)."""
    known = (m.get("techtree") or {}).get("known") or {}
    out = np.full(n_lines, -1.0)
    for l in m["lineages"]:
        kn = known.get(l["id"]) or (known.get(l.get("group_of")) if l.get("group_of") else None) or {}
        if tech in kn:
            out[l["index"]] = float(kn[tech][0])
    return out


def _miner_lines(m: dict, n_lines: int) -> np.ndarray:
    """(lines,): a mining people (trait miner or subterranean, its own or its people's)."""
    by_id = {l["id"]: l for l in m["lineages"]}
    out = np.zeros(n_lines, bool)
    for l in m["lineages"]:
        up = by_id.get(l.get("group_of") or "", {})
        out[l["index"]] = bool(MINERS & (set(l.get("traits") or []) | set(up.get("traits") or [])))
    return out


# How readily a people works a deposit (PW-1116), 0..1, from what its kind carries: the strongest of its traits' weights,
# or its kin's (lore: orcs and goblinoids dig and delve in the D&D settings), less for light-boned flyers and sea folk.
# A kind with no hands never knows 'mines' (the techtree's grip), so hands need no weight here.
MINING_TRAIT = {"miner": 1.0, "subterranean": 0.8, "mountain": 0.25, "hardy": 0.1}
MINING_KIN = {"orc": 0.4, "goblinoid": 0.4}  # (ancestor line -> weight)
MINING_BASE = 0.05
MINING_DAMP = {"flies": 0.3, "swims": 0.2}  # (brittle hollow bones; living in the water)


def _mining_affinity(m: dict, n_lines: int) -> np.ndarray:
    """(lines,): how readily each line works a deposit (see MINING_TRAIT); a group takes its people's traits too."""
    by_id = {l["id"]: l for l in m["lineages"]}
    out = np.full(n_lines, MINING_BASE)
    for l in m["lineages"]:
        up = by_id.get(l.get("group_of") or "", {})
        tr = set(l.get("traits") or []) | set(up.get("traits") or [])
        a = max([MINING_BASE] + [MINING_TRAIT[t] for t in tr if t in MINING_TRAIT])
        seen, stack = set(), [l["id"], up.get("id", "")]
        while stack:  # (ancestry: the kin table)
            x = stack.pop()
            if x in seen or x not in by_id:
                continue
            seen.add(x)
            a = max(a, MINING_KIN.get(x, 0.0))
            stack += list(by_id[x].get("parents") or [])
        for t, f in MINING_DAMP.items():
            if t in tr:
                a *= f
        out[l["index"]] = a
    return out


ORE_NAMES = {"gold": "gold", "iron": "iron", "copper": "copper", "tin": "tin", "gems": "gem", "mithril": "mithril", "metal": "metal ore"}


def _deposits(world: str | None, n: int) -> dict:
    """{"dep": (2, cells) an ore district, a rock-salt bed worth working (mining.ORE_MIN, SALT_MIN); "ore": (cells,) the best ore
    good (0..1); "name": cell -> what the district is worked for ('copper and gold', 'rock salt')}, from the world's goods."""
    out = {"dep": np.zeros((2, n), bool), "ore": np.zeros(n), "G": None, "pit": np.zeros(n, bool), "pit_iron": np.zeros(n, bool),
           "pit_name": np.full(n, "ore")}
    if not world:
        return out
    from . import land as LD
    from . import mining as MN
    try:
        G = LD.goods(world)
    except SystemExit:
        return out
    if not G:
        return out
    ore = MN.ore_cells(G)
    out.update(dep=np.stack([ore >= MN.ORE_MIN, MN.salt_cells(G) >= MN.SALT_MIN]), ore=ore, G=G)
    # ordinary ore (PW-1146): raw best ore from PIT_ORE up to the districts' bar; named for its best named ore good ('metal ore': none)
    named = [k for k in MN.ORE_GOODS if k in G and k != "metal"]
    if named:
        vals = np.stack([MN.ore_good(G, k) for k in named])
        best = vals.argmax(0)
        out["pit"] = (ore >= PIT_ORE) & (ore < MN.ORE_MIN)
        out["pit_name"] = np.where(vals.max(0) >= PIT_ORE, np.array([ORE_NAMES[k] for k in named])[best], "metal ore")
        out["pit_iron"] = np.array(named)[best] == "iron"
        out["pit_iron"] &= vals.max(0) >= PIT_ORE
    return out


def district_name(D: dict, cell: int) -> str:
    """What a mining district is worked for: its ore goods at mining.ORE_MIN or more, richest first (the broad 'metal ore'
    only when no named ore is), else rock salt."""
    from . import mining as MN
    G = D["G"]
    if G is None:
        return "ore"
    got = sorted(((float(MN.ore_good(G, k)[cell]), ORE_NAMES[k]) for k in MN.ORE_GOODS if k in G and k != "metal"
                  and float(MN.ore_good(G, k)[cell]) >= MN.ORE_MIN), reverse=True)[:2]
    if got:
        return " and ".join(n for _, n in got)
    if D["dep"][0, cell]:
        return "metal ore"
    return "rock salt"


def _mines_dates(m: dict, n_lines: int) -> np.ndarray:
    """(lines,): kyr ago a mining people (trait miner or subterranean, its own or its people's) came to 'mines' (-1: never, or not miners)."""
    known = (m.get("techtree") or {}).get("known") or {}
    by_id = {l["id"]: l for l in m["lineages"]}
    out = np.full(n_lines, -1.0)
    for l in m["lineages"]:
        up = by_id.get(l.get("group_of") or "", {})
        if MINERS & (set(l.get("traits") or []) | set(up.get("traits") or [])):
            kn = known.get(l["id"]) or known.get(up.get("id", "")) or {}
            if "mines" in kn:
                out[l["index"]] = float(kn["mines"][0])
    return out


def _world_layers(world: str | None, n: int) -> dict:
    keys = ("harbour", "river_nav", "fresh_water", "fertile_score", "pass")
    out = {k: np.zeros(n) for k in keys}
    out["fertile_score"] += 0.5
    if not world:
        return out
    try:
        wl = S.world_layers(world, keys)
    except SystemExit:
        return out
    for k, v in wl.items():
        out[k] = np.nan_to_num(np.asarray(v, float))
    return out


def _site_factor(W: dict, coastal: np.ndarray, c: dict) -> np.ndarray:
    hb = np.clip(np.rint(W["harbour"]), 0, 3).astype(int)
    rv = np.clip(np.rint(W["river_nav"]), 0, 3).astype(int)
    q = (1.0 + np.where(coastal, np.asarray(c["SITE_HARBOUR"])[hb], 0.0) + np.asarray(c["SITE_RIVER"])[rv]
         + c["SITE_FRESH"] * (np.rint(W["fresh_water"]) >= 3) + c["SITE_FERTILE"] * (W["fertile_score"] - 0.5) + c["SITE_PASS"] * (W["pass"] > 0))
    return np.clip(q, c["SITE_MIN"], c["SITE_MAX"])


def _rings(g, cell: int, r: int) -> np.ndarray:
    cur, seen = {cell}, {cell}
    for _ in range(r):
        nxt = set()
        for x in cur:
            for y in g.nbr_idx[g.nbr_off[x]:g.nbr_off[x + 1]].tolist():
                if y not in seen:
                    seen.add(y)
                    nxt.add(y)
        cur = nxt
    return np.fromiter(seen, np.int64)


def _ring_index(g, r: int) -> np.ndarray:
    """(cells, k): each cell's cells within r rings, padded with the cell itself."""
    rows = [_rings(g, i, r) for i in range(g.n)]
    k = max(len(x) for x in rows)
    out = np.empty((g.n, k), np.int64)
    for i, x in enumerate(rows):
        out[i, :len(x)] = x
        out[i, len(x):] = i
    return out


def derive(run_dir: Path, **over) -> dict:
    """{"doc": settlements.json, "summary": meta.settlements} of a stored peoples run. `over`: CONST overrides for this call."""
    t0 = time.time()
    c = {**CONST, **{k: v for k, v in over.items() if v is not None}}
    unknown = set(over) - set(CONST)
    if unknown:
        raise ValueError(f"unknown settlement constants: {', '.join(sorted(unknown))}")
    run_dir = Path(run_dir)
    run, arr = T.load_frames(run_dir, ("elevation", "ice", "precipitation", "mix_lead", "mix_lead_share", "mix_second",
                                        "mix_second_share", "mix_other_share", "peoples_overlay"))
    m = run["meta"]
    eq = m.get("eraq")
    if not eq:
        raise SystemExit(f"run {run_dir.name}: no land-use inputs per frame (meta.eraq): not a peoples run on a world")
    lines = m["lineages"]
    nl = len(lines)
    g = shared_grid(m["level"])
    n = g.n
    area = 4 * np.pi * R_KM ** 2 / n
    fidx, fago = list(eq["frames"]), [float(a) for a in eq["ago_kyr"]]
    Q = {k: np.fromfile(run_dir / eq["layers"][k]["file"], np.uint8).reshape(eq["layers"][k]["shape"]) for k in ("dens", "farm", "herd")
         if k in eq["layers"]}
    dens_f = 2.0 ** (Q["dens"].astype(float) * LU.PEOPLE_SCALE) - 1  # people / km2 per window frame
    farm_f = Q["farm"].astype(float) / 100
    herd_f = Q["herd"].astype(float) / 100 if "herd" in Q else np.zeros_like(farm_f)
    rain_f = np.stack([T.frame(run, arr, "precipitation", j).astype(float) for j in fidx])
    W = _world_layers(m.get("world"), n)
    tech = _tech_dates(m, nl)
    # a mining people's fortified halls count as its city tech (fortifications, or the fantasy delving): its holds may grow past a town (PW-1117)
    dlv, mnr = np.maximum(_known_dates(m, nl, "delving"), _known_dates(m, nl, "fortifications")), _miner_lines(m, nl)
    tech[:, 2] = np.where(mnr & (dlv >= 0), np.maximum(tech[:, 2], dlv), tech[:, 2])
    mines = _mines_dates(m, nl)
    present_land = is_land(T.frame(run, arr, "elevation", len(run["frames"]) - 1), T.frame(run, arr, "ice", len(run["frames"]) - 1))
    rank = landmass_rank(g, present_land)
    lms = (m.get("present") or {}).get("landmasses") or []
    ids = [l["id"] for l in lines]
    people_of = {l["index"]: (l.get("group_of") or l["id"]) for l in lines}
    plural = {l["id"]: re.sub(r" \(.*\)$", "", l.get("name") or l["id"].replace("_", " ")) for l in lines}  # ('the humans', 'the elves')

    steps = np.round(np.arange(fago[0], -1e-9, -c["STEP_KYR"]), 3)
    if steps[-1] != 0:
        steps = np.append(steps, 0.0)
    cache: dict[int, dict] = {}

    def frame_env(j):  # land, ice and who lives there at window frame j (cached: the steps between two frames share them)
        if j not in cache:
            fj = fidx[j]
            elev, ice = T.frame(run, arr, "elevation", fj), T.frame(run, arr, "ice", fj)
            land = is_land(elev, ice) & ~(np.asarray(ice) > 0.5)
            sea = ~is_land(elev, ice)
            coastal = land & (np.add.reduceat(sea[g.nbr_idx].astype(np.int64), g.nbr_off[:-1]) > 0)
            e = {"land": land, "sea": sea, "elev": np.asarray(elev), "ice": np.asarray(ice) > 0.5, "coastal": coastal,
                 **{k: np.asarray(arr[k][fj]) for k in ("mix_lead", "mix_lead_share", "mix_second", "mix_second_share", "mix_other_share", "peoples_overlay")}}
            e["q"] = _site_factor(W, coastal, c)
            cache.clear()
            cache[j] = e
        return cache[j]

    tiers_allowed = None
    sites: list[dict] = []
    # three slots per cell (KINDS): the chief place, a second people's own place, a mine; each with its live site, its
    # founding streak, its low streak and its last site (the ruin a new one is founded on)
    active = np.full((4, n), -1, np.int64)
    streak = np.zeros((4, n), np.int64)
    low = np.zeros((4, n), np.int64)
    last_site = np.full((4, n), -1, np.int64)
    line_of = np.full((4, n), NONE, np.int64)  # (the line a minority's place belongs to)
    seed = int(m.get("try_seed") or 0)
    def u(*key):  # (a draw keyed on its purpose, slot, cell and year, PW-1459: a nudge elsewhere leaves it alone)
        return keyed(seed, "settle", *key)
    lead_since = np.full(n, np.inf)  # kyr ago the cell's lead line last changed
    cand_run = np.zeros(n, np.int64)  # steps the cell's second people has been the same one (PW-1117)
    prev_cand = np.full(n, NONE, np.int64)
    prev_lead = None
    dt = c["STEP_KYR"]
    relax = 1 - np.exp(-dt / c["TAU_KYR"])
    SHARE = np.asarray(c["SHARE"], float)
    TOWN_MIN = np.asarray(c["TOWN_MIN"], float)
    CITY_CAP = np.asarray(c["CITY_CAP"], float)
    R1, R2 = _ring_index(g, 1), _ring_index(g, 2)  # (n, k) padded with the cell itself
    tieb = 1 + 1e-6 * np.random.default_rng((seed, 1011, 1)).random(n)
    # indexed by line, with one more row for NONE (np.minimum(line, nl)): never
    tech_x = np.r_[tech, np.full((1, 3), -1.0)]
    mines_x = np.r_[mines, -1.0]  # (a mining people's 'mines')
    mines_any = np.r_[_known_dates(m, nl, "mines"), -1.0]  # (anyone's 'mines')
    roads_x = np.r_[_known_dates(m, nl, "roads"), -1.0]
    copper_any = np.r_[_known_dates(m, nl, "copper"), -1.0]
    iron_any = np.r_[_known_dates(m, nl, "iron"), -1.0]
    miner_line = np.r_[_miner_lines(m, nl), False]
    affinity = np.r_[_mining_affinity(m, nl), 0.0]
    D = _deposits(m.get("world"), n)
    deposit = D["dep"]
    for k_, v_ in (("pit", np.zeros(n, bool)), ("pit_iron", np.zeros(n, bool)), ("pit_name", np.full(n, "ore"))):
        D.setdefault(k_, v_)
    # D12: mining follows need. A mining kind (MINE_KIND) mines for its own sake; any other people waits a seeded lag after its
    # copper smelting before it opens ore mines on its own initiative (MINE_LAG_KYR), and needs farmers and herders, a market or
    # a neighbouring mine (exposure)
    kind_x = affinity >= c["MINE_KIND"]
    lag = np.exp(np.log(c["MINE_LAG_KYR"]) + c["MINE_LAG_SIGMA"] * np.random.default_rng((seed, 1131)).standard_normal(nl + 1)) if c["MINE_LAG_KYR"] > 0 else np.zeros(nl + 1)
    ore_from = np.where(copper_any >= 0, copper_any - np.where(kind_x, 0.0, lag), -1.0)  # (kyr ago a people opens ore mines of its own will)
    exp_run = np.zeros(n, np.int64)  # (steps a mine has stood within two rings of the cell)
    # mining colonies (D12, the PW-854 rule for ore): a mining kind works the rich districts within COLONY_KM of its country
    col_lines = [i for i in range(nl) if kind_x[i]]
    col_rings = max(1, int(round(c["COLONY_KM"] / (g.spacing * R_KM))))
    col_cache: dict[int, np.ndarray] = {}
    rich = deposit[0] & (D["ore"] >= c["COLONY_ORE"])
    same_people = np.zeros((nl + 1, nl + 1), bool)
    for a in range(nl):
        for b in range(nl):
            same_people[a, b] = people_of[a] == people_of[b]

    def who(cell, tier, e, dens, step_ago):
        """{people: % of the place's heads} for a place of `tier` in `cell`."""
        cells = _rings(g, cell, {1: 0, 2: 1, 3: 2}.get(tier, 0))
        heads: dict[str, float] = {}
        for x in cells.tolist():
            w = dens[x] * area
            if w <= 0:
                continue
            for k, s in ((e["mix_lead"][x], e["mix_lead_share"][x]), (e["mix_second"][x], e["mix_second_share"][x])):
                if k != NONE and s:
                    p = people_of[int(k)]
                    heads[p] = heads.get(p, 0.0) + w * float(s)
            if e["mix_other_share"][x]:
                heads["others"] = heads.get("others", 0.0) + w * float(e["mix_other_share"][x])
        tot = sum(heads.values()) or 1.0
        pct = {k: round(100 * v / tot) for k, v in sorted(heads.items(), key=lambda kv: -kv[1])}
        return {k: v for k, v in pct.items() if v >= c["QUARTER_MIN_PCT"]}

    def allowed(li, ago):  # (n,) line index -> the largest tier its techs allow (villages first: no towns without them)
        lt = tech_x[np.minimum(li, nl)]
        return np.minimum((lt >= ago - 1e-9).sum(1) * (lt[:, 0] >= ago - 1e-9), 3)

    def stage_of(li, ago):  # (n,) line index -> 0 nothing, 1 villages, 2 towns, 3 cities, 4 cities + roads (PW-1114)
        al = allowed(li, ago)
        return al + ((al >= 3) & (roads_x[np.minimum(li, nl)] >= ago - 1e-9))

    def caps_of(stage):  # (n,) stage -> the largest a village, town, city can be there (0 where the people can't build one)
        vc = TOWN_MIN[stage] - 1
        tc = np.where(stage >= 3, c["CITY_MIN"] - 1, c["TOWN_CAP"])
        return (np.zeros(len(stage)), vc, tc, CITY_CAP[stage])

    def spot(k, cell, e, ago):
        """A seeded spot in the cell: anywhere for a chief place or a mine; a mining people's own place leans to the
        cell's highest neighbour (the holds in the hills)."""
        yr = int(round(ago * 1000))
        ang, r = 2 * np.pi * u("spot", k, cell, yr, 0), c["JITTER"] * np.sqrt(u("spot", k, cell, yr, 1))
        la, lo = float(g.lat[cell]), float(g.lon[cell])
        cl = max(np.cos(np.radians(la)), 0.2)
        sp_ = np.degrees(g.spacing)
        if k == 1 and miner_line[min(int(line_of[1, cell]), nl)]:
            nb = g.nbr_idx[g.nbr_off[cell]:g.nbr_off[cell + 1]]
            top = int(nb[np.argmax(e["elev"][nb])])
            ang = float(np.arctan2(float(g.lat[top]) - la, ((float(g.lon[top]) - lo + 180) % 360 - 180) * cl))
            r = c["JITTER"] * (0.6 + 0.4 * u("spot", k, cell, yr, 2))
        la2 = float(np.clip(la + r * sp_ * np.sin(ang), -89.9, 89.9))
        lo2 = float(((lo + r * sp_ * np.cos(ang) / cl) + 180) % 360 - 180)
        return round(la2, 3), round(lo2, 3)

    def colony_line(jf, ago):
        """(cells,): the mining kind whose colony would work a cell (NONE: none within COLONY_KM): of those that know 'mines'
        and 'copper' now, the most inclined, then the nearest."""
        if jf not in col_cache:  # (graph steps from each mining kind's country at frame jf: where it leads or is a second people of SECOND_MIN)
            e_ = frame_env(jf)
            Dl = np.full((len(col_lines), n), -1, np.int64)
            for r, li in enumerate(col_lines):
                own = (e_["mix_lead"] == li) | ((e_["mix_second"] == li) & (e_["mix_second_share"] >= 100 * c["SECOND_MIN"]))
                if own.any():
                    Dl[r] = graph_dist(own, col_rings, g.nbr_off, g.nbr_idx)
            col_cache.clear()
            col_cache[jf] = Dl
        Dl = col_cache[jf]
        out = np.full(n, NONE, np.int64)
        if not col_lines:
            return out
        li = np.asarray(col_lines)
        ok = (Dl >= 0) & ((mines_any[li] >= ago - 1e-9) & (copper_any[li] >= ago - 1e-9))[:, None]
        score = np.where(ok, affinity[li][:, None] * 100 - Dl, -np.inf)
        best = np.argmax(score, 0)
        return np.where(np.isfinite(score.max(0)), li[best], NONE)

    for ago in steps:
        j = int(np.searchsorted(-np.asarray(fago), -ago, side="right") - 1)  # (the frame at or before this step)
        j = min(max(j, 0), len(fago) - 1)
        k2 = min(j + 1, len(fago) - 1)
        span = fago[j] - fago[k2]
        w = 0.0 if span <= 0 else (fago[j] - ago) / span
        dens = (1 - w) * dens_f[j] + w * dens_f[k2]
        farm = (1 - w) * farm_f[j] + w * farm_f[k2]
        rain = (1 - w) * rain_f[j] + w * rain_f[k2]
        e = frame_env(j if w < 0.5 else k2)
        lead = e["mix_lead"].astype(np.int64)
        second = e["mix_second"].astype(np.int64)
        has = lead != NONE
        if prev_lead is not None:
            lead_since = np.where(lead != prev_lead, ago, lead_since)
        prev_lead = lead
        tiers_allowed = np.where(has, allowed(lead, ago), 0)
        stage0 = np.where(has, stage_of(lead, ago), 0)
        capc = caps_of(stage0)
        hold = np.where(has, mines_x[np.minimum(lead, nl)] >= ago - 1e-9, False) * e["mix_lead_share"] / 100  # (a mining holder's halls)
        waterside = ((W["harbour"] > 0) & e["coastal"] | (W["river_nav"] > 0))
        settled_p = dens * area * (farm + c["FISHER_SHARE"] * (1 - farm) * waterside + c["HOLD_SHARE"] * hold)
        sp = np.where(e["land"], settled_p, 0.0)
        target = np.zeros(n)
        for t, R in ((1, None), (2, R1), (3, R2)):  # (the largest tier the holder may build and the cell may hold)
            hin = sp if R is None else sp[R].sum(1)
            if R is not None:
                score = hin * e["q"] * tieb  # (a seeded tie-break: on even ground one cell of a ring is still the best)
                best = score >= score[R].max(1) - 1e-9
            else:
                best = np.ones(n, bool)
            tt = np.where(best & (tiers_allowed >= t), SHARE[t] * hin * e["q"], 0.0)
            target = np.maximum(target, np.minimum(tt, capc[t]))
        target = np.where(e["land"], target, 0.0)

        # a second people's own place (PW-1105): while the slot is free its line is the cell's second people (SECOND_MIN
        # of the heads or more, and a people of its own, not a group of the lead's people); once founded, the line that
        # founded it, wherever it stands in the cell; once its people have led the cell for HAND_KYR it merges into the
        # chief place (no ruin: MERGED). Sized as a village of its own heads (+ HOLD_SHARE of them in a mining
        # people's halls) x the site factor, up to a town; whether the lead is friend or foe does not matter (owner 10-30).
        cand = np.where((second != NONE) & (e["mix_second_share"] >= 100 * c["SECOND_MIN"])
                        & ~same_people[np.minimum(lead, nl), np.minimum(second, nl)], second, NONE)
        line_of[1] = np.where(active[1] >= 0, line_of[1], cand)
        l1 = line_of[1]
        sh1 = np.where(l1 == NONE, 0.0, np.where(lead == l1, e["mix_lead_share"], np.where(second == l1, e["mix_second_share"], 0.0))) / 100
        al1 = np.where(l1 != NONE, allowed(l1, ago), 0)  # (a hold may grow into a city of its own: PW-1117)
        stage1 = np.where(l1 != NONE, stage_of(l1, ago), 0)
        cap1 = caps_of(stage1)
        hold1 = mines_x[np.minimum(l1, nl)] >= ago - 1e-9
        heads1 = dens * area * sh1
        own1 = c["MINORITY_SHARE"] * heads1 * (farm + c["FISHER_SHARE"] * (1 - farm) * waterside)
        own1 = own1 * c["MINORITY_MAX"] / (own1 + c["MINORITY_MAX"])  # (a minority gathers in one place only so far, the rest live in hamlets: it saturates smoothly, so no pile at a cap)
        hall1 = c["HOLD_SHARE"] * heads1 * hold1 * e["q"]
        hall1 = hall1 / np.sqrt(1 + (hall1 / c["HOLD_MAX"]) ** 2)  # (a hold feeds from its mountain like a city from its hinterland: it levels off smoothly, no pile at a cap)
        set1 = own1 * e["q"] + hall1
        ti1 = np.where(hold1, al1, np.minimum(al1, 2))
        target1 = np.where(e["land"] & (al1 >= 1), np.minimum(set1, np.select([ti1 == 1, ti1 == 2, ti1 >= 3], [cap1[1], cap1[2], cap1[3]], 0.0)), 0.0)
        # (PW-1117) a second people must have been the cell's second people for MINORITY_STEPS before it founds a place
        cand_run = np.where(cand != NONE, np.where(cand == prev_cand, cand_run + 1, 1), 0)
        prev_cand = cand.copy()
        ready = (np.ones(n, bool), cand_run >= c["MINORITY_STEPS"], np.ones(n, bool), np.ones(n, bool))
        stages = (stage0, stage1, None, None)

        # a mine (owner 10-30): a cell with an ore or rock-salt deposit, worked by its lead people if it knows 'mines', else
        # by its second people; MINE_SHARE of the cell's people (the miners and those who feed them). D12: only where it is
        # wanted: a mining kind; farmers and herders (MINE_NEED) or a town's market within two rings, for ore only once the
        # people's own lag after its smelting is over; or a mine has stood within two rings for MINE_EXPOSE_STEPS (exposure)
        mine_now = active[2] >= 0
        exp_run = np.where(mine_now[R2].any(1), exp_run + 1, 0)
        exposed = exp_run >= c["MINE_EXPOSE_STEPS"]
        town_now = np.zeros(n, bool)
        ac = np.flatnonzero(active[0] >= 0)
        town_now[ac] = [sites[i]["tier"] >= 2 for i in active[0][ac].tolist()]
        need = (farm + (1 - w) * herd_f[j] + w * herd_f[k2]) >= c["MINE_NEED"]
        want_ = need | town_now[R2].any(1)

        def ore_ok(li):
            lx = np.minimum(li, nl)
            return deposit[0] & (copper_any[lx] >= ago - 1e-9) & (kind_x[lx] | (want_ & (ore_from[lx] >= ago - 1e-9)) | exposed)

        def can_mine(li):
            lx = np.minimum(li, nl)
            ok = (li != NONE) & (mines_any[lx] >= ago - 1e-9)
            return ok & ((deposit[1] & (kind_x[lx] | want_ | exposed)) | ore_ok(li))
        # PW-1116: the cell's mining-inclined people works the deposit even as a second people (SECOND_MIN of the heads, a
        # people of its own) when it is clearly more inclined than the lead (MINE_EDGE); else the lead, else the second
        sec_ok = (second != NONE) & (e["mix_second_share"] >= 100 * c["SECOND_MIN"]) & ~same_people[np.minimum(lead, nl), np.minimum(second, nl)]
        a_l, a_s = affinity[np.minimum(lead, nl)], affinity[np.minimum(second, nl)]
        lead_ok, sec_can = has & can_mine(lead), sec_ok & can_mine(second)
        take_sec = sec_can & (~lead_ok | (a_s >= a_l + c["MINE_EDGE"]))
        lm = np.where(take_sec, second, np.where(lead_ok, lead, NONE))
        # a colony: the nearest of the most inclined mining kinds within COLONY_KM works a rich ore district held by others
        # (settled ground, the cell's people feed it) when it is clearly more inclined than whoever would work it here
        col = colony_line(j if w < 0.5 else k2, ago)
        a_c, a_cur = affinity[np.minimum(col, nl)], np.where(lm != NONE, affinity[np.minimum(lm, nl)], 0.0)
        take_col = rich & has & e["land"] & (col != NONE) & (a_c >= a_cur + c["MINE_EDGE"]) & (col != lead) & (col != second)
        lm = np.where(take_col, col, lm)
        a_m = affinity[np.minimum(lm, nl)]
        ore_m = (lm != NONE) & (take_col | ore_ok(lm))  # (worked for its ore, else for its rock salt)
        want = np.where(e["land"] & (lm != NONE), c["MINE_SHARE"] * (0.5 + a_m) * dens * area, 0.0)
        # one mining district per ring of cells (the best of it, as a town is): a seam is worked at a few pits, not in every cell
        mscore = want * tieb
        target2 = np.where(mscore >= mscore[R1].max(1) - 1e-9, want, 0.0)

        # a pit (PW-1146): ordinary ore, dug by the lead people where it smelts that metal (iron: iron) and wants it, as a mine
        pit_ok = (D["pit"] & has & (lead != NONE) & e["land"]
                  & (np.where(D["pit_iron"], iron_any[np.minimum(lead, nl)], copper_any[np.minimum(lead, nl)]) >= ago - 1e-9)
                  & (kind_x[np.minimum(lead, nl)] | (want_ & (ore_from[np.minimum(lead, nl)] >= ago - 1e-9)) | exposed))
        pwant = np.where(pit_ok, c["PIT_SHARE"] * (0.5 + affinity[np.minimum(lead, nl)]) * dens * area, 0.0)
        pscore = pwant * tieb
        target3 = pwant if c["PIT_RINGS"] <= 0 else np.where(pscore >= pscore[R1].max(1) - 1e-9, pwant, 0.0)
        pl = np.where(pit_ok, lead, NONE)

        for k, tgt, hl in ((0, target, lead), (1, target1, l1), (2, target2, lm), (3, target3, pl)):
            free = active[k] < 0
            fnd, aban = (c["PIT_FOUND"], c["PIT_ABANDON"]) if k == 3 else (c["FOUND"], c["ABANDON"])
            streak[k] = np.where(free & (tgt >= fnd) & ready[k], streak[k] + 1, 0)
            for cell in np.flatnonzero(free & (streak[k] >= c["FOUND_STEPS"]) & (hl != NONE)).tolist():
                h = people_of[int(hl[cell])]
                la2, lo2 = spot(k, cell, e, ago)
                pop = float(max(fnd, min(tgt[cell], fnd * 2)))
                s = {"id": len(sites), "kind": KINDS[k], "cell": cell, "lat": la2, "lon": lo2, "founded_kyr": float(ago), "founded_by": h,
                     "holder": h, "holders": [[float(ago), h]], "abandoned_kyr": None, "why": None,
                     "ruin_of": int(last_site[k, cell]) if last_site[k, cell] >= 0 else None, "resettled_as": None,
                     "pop": pop, "peak_pop": pop, "peak_kyr": float(ago), "series": [[float(ago), round(pop)]],
                     "rain0": float(rain[cell]), "_peak_who": None}
                tm = float(TOWN_MIN[int(stages[k][cell])]) if k < 2 else 0.0
                s["bands"] = [[float(ago), tm, float(c["CITY_MIN"])]]  # (the size classes in force, PW-1114: [kyr ago, town min, city min])
                s["tier"] = s["tier_pk"] = max(tier_of(pop, c, int(stages[k][cell])), 1) if k < 2 else 1
                if s["ruin_of"] is not None:
                    sites[s["ruin_of"]]["resettled_as"] = s["id"]
                s["_peak_who"] = who(cell, s["tier"], e, dens, ago) if k == 0 else {h: 100}
                if k == 3:  # (a pit: what it digs)
                    s["district"], s["colony"] = D["pit_name"][cell], False
                if k == 2:  # (the district it works; a colony: worked by incomers, its people neither leads nor is second here)
                    s["district"] = district_name(D, cell) if ore_m[cell] else "rock salt"
                    s["colony"] = bool(take_col[cell])
                sites.append(s)
                active[k, cell] = s["id"]
                last_site[k, cell] = s["id"]
                streak[k, cell] = 0
            # growth, change of hands, decline
            for cell in np.flatnonzero(active[k] >= 0).tolist():
                s = sites[active[k, cell]]
                if s["founded_kyr"] == ago:
                    continue
                s["pop"] += (tgt[cell] - s["pop"]) * relax
                s["series"].append([float(ago), round(s["pop"])])
                if k == 2:
                    s["colony"] = bool(take_col[cell])
                    if ore_m[cell] and s["district"] == "rock salt":  # (a salt mine whose people came to smelt: now worked for its ore too)
                        s["district"] = district_name(D, cell) + " and rock salt"
                if hl[cell] != NONE and k != 1:  # (a minority's place stays its own people's)
                    h = people_of[int(hl[cell])]
                    if h != s["holder"]:
                        s["holder"] = h
                        s["holders"].append([float(ago), h])
                if k < 2:  # (the size class at this date: the holder's stage sets the town's size, PW-1114)
                    tm = float(TOWN_MIN[int(stages[k][cell])])
                    if tm != s["bands"][-1][1]:
                        s["bands"].append([float(ago), tm, float(c["CITY_MIN"])])
                    s["tier"] = tier_of(s["pop"], c, int(stages[k][cell]))
                    if s["tier"] > s["tier_pk"]:
                        if k == 0:
                            s["_peak_who"] = who(cell, s["tier"], e, dens, ago)
                        s["tier_pk"] = s["tier"]
                if s["pop"] > s["peak_pop"]:
                    s["peak_pop"], s["peak_kyr"] = s["pop"], float(ago)
                low[k, cell] = low[k, cell] + 1 if tgt[cell] < aban else 0
                why = None
                if e["sea"][cell]:
                    why = "the sea rose over it"
                elif e["ice"][cell]:
                    why = "the ice came"
                elif k == 1 and same_people[min(int(lead[cell]), nl), min(int(line_of[1, cell]), nl)] and lead_since[cell] - ago >= c["HAND_KYR"] - 1e-9:
                    why = MERGED
                elif k < 2 and W["river_nav"][cell] > 0 and e["elev"][cell] < c["RIVER_LOW_M"] and u("river", k, cell, int(round(ago * 1000))) < c["RIVER_SHIFT"] * dt:
                    why = "the river moved away"
                elif low[k, cell] >= (c["MINORITY_ABANDON_STEPS"] if k == 1 else c["ABANDON_STEPS"]):
                    lp = plural.get(people_of[int(lead[cell])], "?") if has[cell] else "?"
                    if rain[cell] < (1 - c["DROUGHT"]) * s["rain0"]:
                        why = "drought"
                    elif k == 0 and len(s["holders"]) > 1 and (s["holders"][-1][0] - ago <= c["HAND_KYR"] or tiers_allowed[cell] == 0):
                        why = f"driven out by the {plural.get(s['holder'], s['holder'])}" if s["holder"] != s["founded_by"] else "its people left"
                    elif k == 0 and tiers_allowed[cell] == 0 and has[cell]:
                        why = f"driven out by the {lp}"
                    elif k > 0 and has[cell] and people_of[int(lead[cell])] != s["holder"] and lead_since[cell] - ago <= c["HAND_KYR"]:
                        why = f"driven out by the {lp}"  # (the cell changed hands lately and its own people dwindled)
                    else:
                        why = "its people left"
                if why:
                    s["abandoned_kyr"], s["why"] = float(ago), why
                    s["_end_who"] = None
                    active[k, cell] = -1
                    low[k, cell] = 0
                    if k == 1:
                        line_of[1, cell] = NONE
    # the present's 'who lives here' for the living
    e_now = frame_env(len(fago) - 1)
    for s in sites:
        if s["abandoned_kyr"] is None:
            s["_end_who"] = (who(s["cell"], max(s["tier"], 1), e_now, dens_f[-1], 0.0) if s["kind"] == "chief"
                             else {s["holder"]: 100})
    return _document(sites, c, g, ids, rank, lms, steps, area, time.time() - t0)


def _document(sites, c, g, ids, rank, lms, steps, area, secs) -> dict:
    out = []
    by_people: dict[str, dict] = {}
    for s in sites:
        alive = s["abandoned_kyr"] is None
        tier_peak, tier_now = s["tier_pk"], (max(s["tier"], 1) if alive else 0)
        place = _place((s["lat"], s["lon"], int(rank[s["cell"]])), lms)
        who = (s["_end_who"] if alive else s["_peak_who"]) or {}
        ser = s["series"]
        if len(ser) > c["SERIES_KEEP"]:
            keep = np.unique(np.r_[np.linspace(0, len(ser) - 1, c["SERIES_KEEP"]).round().astype(int), int(np.argmax([p for _, p in ser]))])
            ser = [ser[i] for i in keep]
        mine = s["kind"] in ("mine", "pit")  # (the two small-works kinds: no town sizes)
        rec = {"id": s["id"], "kind": s["kind"], "cell": s["cell"], "lat": s["lat"], "lon": s["lon"], "place": place,
               "tier_peak": s["kind"] if mine else TIERS[max(tier_peak, 1)], "tier_now": (s["kind"] if mine else TIERS[tier_now]) if alive else "merged" if s["why"] == MERGED else "ruin",
               "founded_kyr": round(s["founded_kyr"], 3), "founded_by": s["founded_by"], "holder": s["holder"],
               "holders": [[round(a, 3), h] for a, h in s["holders"]], "abandoned_kyr": None if alive else round(s["abandoned_kyr"], 3),
               "why": s["why"], "ruin_of": s["ruin_of"], "resettled_as": s["resettled_as"],
               "pop_now": round(s["pop"]) if alive else 0, "peak_pop": round(s["peak_pop"]), "peak_kyr": round(s["peak_kyr"], 3),
               "who": who, "who_when": "now" if alive else "at its height", "series": ser,
               "bands": [[round(a, 3), t, cm] for a, t, cm in s["bands"]] if not mine else []}
        if mine:  # (D12: what the district is worked for, and whether by a colony of incomers)
            rec["district"], rec["colony"] = s.get("district"), bool(s.get("colony"))
        out.append(rec)
        for p, key in ((s["founded_by"], "founded"), (s["holder"] if alive else None, "alive")):
            if p is None:
                continue
            b = by_people.setdefault(p, {"founded": 0, "alive": 0, "ruins": 0, "towns_now": 0, "cities_now": 0, "cities_ever": 0, "largest_now": 0,
                                         "villages_now": 0, "own_places_now": 0, "mines_now": 0, "pits_now": 0, "colonies_now": 0, "taken_now": 0})
            b[key] += 1
        b = by_people[s["founded_by"]]
        if not alive and s["why"] != MERGED:
            b["ruins"] += 1
        b["cities_ever"] += tier_peak == 3 and not mine
        if alive:
            bh = by_people[s["holder"]]
            bh["own_places_now"] += s["kind"] == "minority"
            bh["mines_now"] += s["kind"] == "mine"
            bh["pits_now"] += s["kind"] == "pit"
            bh["colonies_now"] += mine and bool(s.get("colony"))
            if mine:
                continue
            bh["taken_now"] += s["holder"] != s["founded_by"]  # (held now by another people than its founders)
            bh["villages_now"] += tier_now <= 1
            bh["towns_now"] += tier_now == 2
            bh["cities_now"] += tier_now == 3
            bh["largest_now"] = max(bh["largest_now"], round(s["pop"]))
    whys: dict[str, int] = {}
    for r in out:
        if r["why"]:
            k = "driven out" if r["why"].startswith("driven out") else r["why"]
            whys[k] = whys.get(k, 0) + 1
    alive = [r for r in out if r["abandoned_kyr"] is None]
    doc = {"format": "procgen-settlements/1", "from_kyr": float(steps[0]), "step_kyr": c["STEP_KYR"], "constants": c,
           "tiers": {"village_min": c["ABANDON"], "town_min_by_stage": list(c["TOWN_MIN"]), "city_min": c["CITY_MIN"],
                     "city_cap_by_stage": list(c["CITY_CAP"]), "stages": STAGES},
           "sites": out}
    summary = {"file": "settlements.json", "founded": len(out), "alive": len(alive), "ruins": sum(r["tier_now"] == "ruin" for r in out), "merged": sum(r["tier_now"] == "merged" for r in out),
               "resettled": sum(r["ruin_of"] is not None for r in out),
               "now": {t: sum(r["tier_now"] == t for r in alive) for t in (*TIERS[1:], "mine", "pit")},
               "minority_now": sum(r["kind"] == "minority" for r in alive),
               "colonies_now": sum(bool(r.get("colony")) for r in alive),
               "why": whys, "people_in_places_now": int(sum(r["pop_now"] for r in alive)),
               "by_people": dict(sorted(by_people.items(), key=lambda kv: -kv[1]["founded"])),
               "from_kyr": float(steps[0]), "cell_km2": round(area), "generated_in_s": round(secs, 1)}
    return {"doc": doc, "summary": summary}


def write(run_dir: Path, report: bool = True, **over) -> dict:
    """Adds settlements.json and meta.settlements to a peoples run; returns meta.settlements."""
    run_dir = Path(run_dir)
    d = derive(run_dir, **over)
    S.write_atomic(run_dir / "settlements.json", json.dumps(d["doc"], separators=(",", ":")))
    S.update_meta(run_dir, lambda r: r["meta"].__setitem__("settlements", d["summary"]))
    if report:
        report_section(run_dir, d["summary"], d["doc"])
    return d["summary"]


def report_section(run_dir: Path, summary: dict | None = None, doc: dict | None = None) -> None:
    """Writes the ledger's section of run.txt (a redo replaces the section it wrote before); summary and doc default to the run's own
    meta.settlements and settlements.json."""
    run_dir = Path(run_dir)
    if summary is None:
        summary = json.loads((run_dir / "run.json").read_text())["meta"]["settlements"]
    if doc is None:
        doc = json.loads((run_dir / "settlements.json").read_text())
    p = run_dir / "run.txt"
    old = p.read_text() if p.exists() else ""
    a = old.find("\n## Settlements (PW-1011")
    if a >= 0:
        b = old.find("\n## ", a + 1)
        old = old[:a] + (old[b:] if b >= 0 else "\n")
    S.write_atomic(p, old.rstrip("\n") + "\n" + "\n".join(lines_for_report(summary, doc)) + "\n")


def lines_for_report(sm: dict, doc: dict) -> list[str]:
    L = ["", f"## Settlements (PW-1011 v0): since {years_ago(sm['from_kyr'])}, {sm['founded']} founded, {sm['alive']} alive now "
             f"({sm['now']['village']} villages, {sm['now']['town']} towns, {sm['now']['city']} cities, {sm['now']['mine']} mining districts, {sm['now']['pit']} local pits, {sm.get('colonies_now', 0)} of them colonies; {sm['minority_now']} of the places a second people's own), {sm['ruins']} ruins, "
             f"{sm['resettled']} on older ruins; {sm['people_in_places_now']:,} people in them now ({sm['generated_in_s']} s)",
         "  why abandoned: " + (", ".join(f"{k} {v}" for k, v in sorted(sm["why"].items(), key=lambda kv: -kv[1])) or "none")]
    for p, b in sm["by_people"].items():
        L.append(f"  {p:<16} founded {b['founded']:>4}, alive {b['alive']:>4} ({b['towns_now']} towns, {b['cities_now']} cities; "
                 f"largest {b['largest_now']:,}; {b['own_places_now']} own places among others, {b['mines_now']} mining districts, {b.get('pits_now', 0)} pits, {b.get('colonies_now', 0)} colonies), ruins {b['ruins']:>4}, cities ever {b['cities_ever']}")
    big = sorted((r for r in doc["sites"] if r["abandoned_kyr"] is None and r["kind"] not in ("mine", "pit")), key=lambda r: -r["pop_now"])[:8]
    L.append("  -- the largest now")
    L += [f"  {r['tier_now']} of the {r['holder']}, {r['place'] or '?'}: {r['pop_now']:,}, since {r['founded_kyr']:g} kyr; "
          + ", ".join(f"{k} {v}%" for k, v in r["who"].items())
          for r in big]
    return L
