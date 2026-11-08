"""The technology tree, a first pass (PW-675 prototype): which people knew what, and since when.

The tree is data (samples/techtree.toml): tracks, techs with prerequisites, land the tech needs (land.GOODS), a real-world
earliest date (sources in the file) and a rate. It is read after a peoples history has run, from what the history saved
(the lines with their start and end, the contact record, the first tamings of crops and animals, each people's present
range and the world's goods), so it can be built in output.save and again for a stored run (`planet techtree RUN`). It is a step
function (`Calendar`, PW-1466): with polities in the history switched on, the history runs it century by century from what it knows
by then (history.tech_live) and output.save writes that calendar out; `build` is the same steps fed the whole run at once.
D52's town arms (B, E) read the settlement ledger, which reads the tree: output.save builds the tree without them, then the ledger,
then the tree with them (PW-1464, output._towns_first).

Rules, all seeded and simple. Every draw is keyed on what it is for (PW-1459, `keyed`): a pair's contact front on (seed, giver,
taker), an invention test on (seed, people, tech, step). So a nudge elsewhere in the history meets the same luck here; one shared
stream in loop order reshuffled every later people's dates.
- A people may invent a tech once it knows the tech's needs, its country holds (its present range; a deposit, ore or salt, in a few
  cells) the goods the tech needs, it can hold the tool, and, for a gated tech, the time is past its floor. The invention model
  (PW-675 v1, lane 64; the evidence: docs/references/techtree/README.md) is a hazard per people, per tech, per kyr:
      h = rate x rate_x (kind) x M (culture x domain) x S (pool) x ramp
  - S, the pool's strength (Henrich 2004 eqs. 2-3: skill gains go as ln N, with a threshold N* below which skills are lost):
    ln(pool / N*) / ln(N0 / N*), 0 below N*, at most pool_max. The pool is the tech's `pool`: "all" (the stone-age everyday techs:
    the whole people, N(t)), "specialists" (bronze age on: the non-food-producers, N(t) x s; Childe 1950) or "none" (gesture and
    language, biology gated by the sapiens node). N(t) is the line's population at the time, from its saved track; s is a
    judgement ladder from the people's own techs (forager, villages, farming, towns, cities; [[specialists]]) x a density
    term (Bettencourt et al. 2007: innovation per head rises with settlement size). Every pool is x the kind's learners, its
    generation over a human's 25 yr (capped): skills are lost at each hand-off, so a long-lived kind loses less per kyr.
  - M: the people's culture (its traits and way of life, [culture]) against the tech's `domains`: aggressive peoples war,
    herders and seafarers moving, farmers food, miners craft, and so on; the best match over the tech's domains, capped.
  - ramp = 1 - exp(-h tau), tau the time since the people first met the tech's conditions: the chance rises as the band goes on.
  - The band: a tech whose real-world date is at least gate_kyr (12 kyr: the Pleistocene record and the glacial gate on farming,
    Richerson et al. 2001) keeps it as a hard floor (elder kinds: elder_kyr). Its rate, unless given, is set from Earth's dated
    independent origins (`origins_kyr`, the tech catalogue's): the anchor people's median wait after the floor is the median
    origin's date less the floor (band_wait, PW-1138: pottery, 7 origins from 20 to 5 kyr, waits 9 kyr); with one dated origin
    it is its track's slow rate, and contact carries it (bread, wild cereals: found once on Earth, then spread). A younger tech has no floor: its prerequisites,
    the specialists and the ramp time it, and its date is a soft anchor only. Its rate, unless given, is set so that the first of
    anchor_peers well-placed peoples (anchor_pop, at anchor_dens, knowing what Earth knew then) takes as long after its
    prerequisites as Earth did (Earth's date is its first find, not a typical people's; lane 70, PW-1137).
- A split inherits what its parent knew at the split, a hybrid what both parents knew; a group (a way of life within a
  people) shares its people's knowledge as it goes; an arrival brings its kind's kit (gnomes from the feywild).
- Diffusion: while two peoples are in contact (contacts.Contacts: the first contact, the border length over time), each
  tech one knows and the other could use passes at contact_rate(taker's range) x spread x border/contact_full_km x openness per
  kyr (openness = 1 - 0.7 insularity): fast for traded things, slow for language; x the taker's culture `take` on the tech's
  domains (an aggressive people takes war techs up twice as fast: military tech spread by connectivity, Turchin et al. 2021).
  contact_rate is a front crossing the taker's country at ~1 km/yr (the Neolithic wave of advance, Pinhasi et al. 2005): half
  its people have the tech once the front has gone half its width, so a 1 Mkm2 people takes ~1.4 per kyr, a 9 Mkm2 one ~0.46
  (lane 70, PW-1137; it was a flat 0.15). The front sets out when the giver knows the tech and they are in touch, with a delay
  drawn once, and once it has arrived the taker takes the tech up as soon as it can use it: a package travels together (the
  plough right behind the ox) instead of the taker's clock restarting at each prerequisite. A tech arriving within a step can
  still be invented first over the part of the step before it arrived.
- The crops and herd animals of the history count: a people that first cultivated a crop (crops.py) knows cultivation
  from then, one that tamed or took up an animal (animals.py) knows herding. Each stock is also a tech of its own (stock
  "crops:wheat", PW-1122: crop_wheat, animal_cattle...), known only that way (rate 0, spread 0): wine waits for the vine, the
  ox-drawn plough for cattle. `needs_any` asks for one of a list (riding: a horse, a great elk or a riding lizard).
- The tree holds the tech catalogue (PW-1122, docs/references/tech-catalogue/): ~550 techs; `earth_origins` is how many
  independent origins Earth had, for checking the finds per world.
- Language never passes between stems before their minds (below), but once a people is genetically modern (below a stem with a
  sapiens node) it takes language from any neighbour that has it, at the contact rate (modern_contact, PW-971; owner: almost any
  contact spreads language). The other within-a-people techs (spread = 0) never pass by contact.
- The sapiens node gates (PW-971, PW-978): in a line under a stem with `sapient`, nothing arises or spreads before the node but the
  techs marked `bare = true` (knapping, handaxes: Lomekwi/Oldowan/Acheulean; found and hooked tools). Gesture and call systems, language and everything
  past them wait for the node. A kind's starting kit (the dragons' innate magic, with its gesture roots) is not gated: it is body.
- Each body plan its own bare tools (PW-987): a tech's `grip` says what holds its tool (hands, beak or any); a kind's `hands` is
  true, false (dragons) or "node" (hands only from its stem's sapiens node: cats, birds, saurians) and `beak` lets it hold one in its
  beak. So before their minds the hominids and goblinoids knap, the bird stems use found and hooked tools, the cats and saurians none.
- Nothing goes past the tree's era (meta.era), and the fantasy techs are left out in real mode.
A stem that ends as animals (spec.Lineage.animals_end, PW-965: the dragons' wyverns, drakes and pseudodragons) is untracked past its end, so
no animal line exists here to get language or techs.
Megafauna (dragons, giants) count as peoples here; templates (tieflings) do not: they are their hosts.
"""

from __future__ import annotations

import hashlib
import json
import math
import tomllib
import warnings
from pathlib import Path

import numpy as np

FILE = Path(__file__).parent / "samples" / "techtree.toml"
ERAS = ("stone age", "bronze age", "classical", "medieval", "renaissance", "industrial")
STEPS = 360  # time steps, log-spaced from the oldest line to the present
NEAR_KYR = 0.05  # the last step before the present
DEPOSITS = ("metal", "gold", "iron", "copper", "tin", "gems", "mithril", "coal", "salt", "salt_rock", "stone", "volcanic",
            "vents", "reef", "kelp_beds")  # (the sea's point goods, PW-1491: a vent field, a reef tract, a kelp bed)


def load(path: Path | str | None = None) -> dict:
    return load_raw(tomllib.loads(Path(path or FILE).read_text()))


def load_raw(raw: dict) -> dict:
    """The tree from its parsed TOML: checked, with the techs in prerequisite order."""
    techs = {t["id"]: t for t in raw["tech"]}
    for t in techs.values():
        for n in t.get("needs", []) + t.get("needs_any", []):
            if n not in techs:
                raise ValueError(f"tech {t['id']} needs unknown tech {n}")
        if t["track"] not in {k["id"] for k in raw["track"]}:
            raise ValueError(f"tech {t['id']}: unknown track {t['track']}")
        if t.get("era", "stone age") not in ERAS:
            raise ValueError(f"tech {t['id']}: unknown era {t.get('era')}")
        if t.get("grip", "hands") not in GRIPS:
            raise ValueError(f"tech {t['id']}: unknown grip {t.get('grip')}")
        if not domains_of(t) or any(d not in DOMAINS for d in domains_of(t)):
            raise ValueError(f"tech {t['id']}: domains must be some of {DOMAINS}, got {domains_of(t)}")
        if pool_of(t) not in POOLS:
            raise ValueError(f"tech {t['id']}: unknown pool {t.get('pool')}")
    for key, c in (raw.get("culture") or {}).items():
        if any(d not in DOMAINS + ("take",) for d in c) or any(d not in DOMAINS for d in c.get("take", {})):
            raise ValueError(f"culture {key}: domains must be some of {DOMAINS}")
    for r in raw.get("specialists", []):
        if any(n not in techs for n in r["needs"]):
            raise ValueError(f"specialists rung {r}: unknown tech")
    for k in raw.get("kind", []):
        k["of"] = [k["of"]] if isinstance(k["of"], str) else list(k["of"])  # (one line id or several, PW-1041)
        if k.get("hands", True) not in (True, False, "node"):
            raise ValueError(f"kind {k['of']}: hands must be true, false or \"node\"")
    order, seen = [], set()

    def visit(i, path=()):
        if i in path:
            raise ValueError(f"tech cycle through {i}")
        if i in seen:
            return
        for n in techs[i].get("needs", []) + techs[i].get("needs_any", []):
            visit(n, path + (i,))
        seen.add(i)
        order.append(i)
    for i in techs:
        visit(i)
    raw["order"] = order  # (prerequisites before the techs that need them)
    raw["techs"] = techs
    return raw


def closure(T: dict, ids) -> set:
    """The techs and everything they need."""
    out, todo = set(), list(ids)
    while todo:
        i = todo.pop()
        if i not in out:
            out.add(i)
            todo.extend(T["techs"][i].get("needs", []))
    return out


def _kind(T: dict, line: dict, L: dict) -> dict:
    """The [[kind]] rules that hold for a line (its own, else its nearest ancestor's; first parent up the tree)."""
    kinds = {i: k for k in T.get("kind", []) for i in k["of"]}
    seen, cur = set(), line
    while cur is not None and cur["id"] not in seen:
        seen.add(cur["id"])
        if cur["id"] in kinds:
            return kinds[cur["id"]]
        up = cur.get("group_of") or (cur.get("parents") or [None])[0]
        cur = L.get(up)
    return {}


def _node(line: dict, L: dict) -> float | None:
    """The sapiens node (kyr) of the line's own stem or the nearest stem above it (first parent up the tree; PW-971)."""
    seen, cur = set(), line
    while cur is not None and cur["id"] not in seen:
        seen.add(cur["id"])
        if cur.get("sapient_kyr") is not None:
            return float(cur["sapient_kyr"])
        up = cur.get("group_of") or (cur.get("parents") or [None])[0]
        cur = L.get(up)
    return None


def _gen(line: dict, L: dict) -> float | None:
    """The line's generation, yr (meta.lineages generation_yr: history.gen_yr), else its nearest ancestor's; None: not known."""
    seen, cur = set(), line
    while cur is not None and cur["id"] not in seen:
        seen.add(cur["id"])
        if cur.get("generation_yr") is not None:
            return float(cur["generation_yr"])
        up = cur.get("group_of") or (cur.get("parents") or [None])[0]
        cur = L.get(up)
    return None


GRIPS = ("hands", "beak", "any")


def _grips(t: dict, k: dict, node: float | None, ago: float) -> bool:
    """Whether a kind can hold the tool of a tech that needs one (PW-987): its grip ("hands", "beak" or "any") against the
    kind's hands (true; false: dragons; "node": from its stem's sapiens node on, or always without a node) and beak."""
    h = k.get("hands", True)
    hands = h is True or (h == "node" and (node is None or ago <= node))
    beak = bool(k.get("beak"))
    g = t.get("grip", "hands")
    return hands if g == "hands" else beak if g == "beak" else hands or beak


def is_sea(line: dict, L: dict) -> bool:
    """A sea people (PW-1491): its realm is the sea (coast or sea), or it swims and keeps to the coast (the tritons, sea elves, deep
    folk); a group as its people."""
    seen, cur = set(), line
    while cur is not None and cur.get("group_of") and cur["id"] not in seen:
        seen.add(cur["id"])
        cur = L.get(cur["group_of"])
    cur = cur or line
    tr = set(cur.get("traits") or [])
    return cur.get("realm", "land") != "land" or {"swims", "coastal"} <= tr


def sea_ok(t: dict, line: dict, L: dict, inventing: bool = False) -> bool:
    """Whether a people may hold a tech of the sea branch (`sea = true`, PW-1491): a sea people always; a land people only a traded one,
    taken by contact (pearls and nacre)."""
    return not t.get("sea") or is_sea(line, L) or (bool(t.get("traded")) and not inventing)


def _env_ok(t: dict, have: set | None) -> bool:
    if have is None:  # (no range or no goods to read: not checked)
        return True
    if any(g not in have for g in t.get("env", [])):
        return False
    return not t.get("env_any") or any(g in have for g in t["env_any"])


def goods_held(T: dict, present: np.ndarray | None, goods: dict | None, k: int) -> set | None:
    """The goods a line's country holds (its present range): a good at env_min or more on env_share of its cells."""
    if present is None or goods is None:
        return None
    d = T["defaults"]
    sel = present[k] >= 0.05
    if not sel.any():
        return None
    out = set()
    for g, v in goods.items():
        if g.startswith("_"):
            continue
        a = np.asarray(v, float)
        if a.shape[0] != sel.shape[0]:
            continue
        if g in DEPOSITS:  # (a deposit is a point: ore-bearing country, the reach good at deposit_min, in a few of the people's cells will do; PW-1146: not the mines' rich-district test, mining.ORE_MIN 0.75 raw, which would take iron from every people)
            if int((a[sel] >= d["deposit_min"]).sum()) >= max(2, d["deposit_share"] * sel.sum()):
                out.add(g)
        elif float((a[sel] >= d["env_min"]).mean()) >= d["env_share"]:
            out.add(g)
    return out


GODS_MODES = ("faith_made", "belief_only", "absolute")  # (PW-1306)
DOMAINS = ("war", "food", "craft", "build", "move", "know", "ritual", "trade")  # (the same eight as docs/references/tech-catalogue)
POOLS = ("all", "specialists", "none")
GENERATION_REF_YR = 25.0  # (spec.GENERATION_YR: a human generation)
# the median wait of the ramped hazard h (1 - exp(-h tau)) in units of 1 / h: x - 1 + exp(-x) = ln 2
RAMP_MEDIAN = 1.4625


def ramp_first(n: float) -> float:
    """The median wait, in units of 1 / h, of the first of n peoples on the ramped hazard: x - 1 + exp(-x) = ln 2 / n (n = 1:
    RAMP_MEDIAN). Solved by bisection."""
    lo, hi, c = 0.0, 50.0, math.log(2) / max(float(n), 1.0)
    for _ in range(80):
        x = 0.5 * (lo + hi)
        lo, hi = (x, hi) if x - 1 + math.exp(-x) < c else (lo, x)
    return 0.5 * (lo + hi)


def domains_of(t: dict) -> list[str]:
    d = t.get("domains") or []
    return [d] if isinstance(d, str) else list(d)


def pool_of(t: dict) -> str:
    """The pool a tech draws its inventors from: its own `pool`, else the whole people for the stone age and the specialists after."""
    return t.get("pool") or ("all" if t.get("era", "stone age") == "stone age" else "specialists")


def _earth_ready(T: dict, tid: str) -> float | None:
    """When Earth had all of a tech's prerequisites, kyr (the latest of their dates; of a needs_any list, its earliest); None: it
    needs nothing."""
    t = T["techs"][tid]
    e = t.get("earliest_kyr", 0.0)
    ds = [T["techs"][n].get("earliest_kyr", e) for n in t.get("needs", [])]
    real = [n for n in t.get("needs_any", []) if T["techs"][n].get("mode") != "fantasy"] or t.get("needs_any", [])
    if real:  # (Earth's: the fantasy mounts and milk beasts left out)
        ds.append(max(T["techs"][n].get("earliest_kyr", e) for n in real))
    return min(ds, default=None)


def floor_of(T: dict, tid: str, elder: bool = False) -> float | None:
    """A gated tech's hard floor, kyr (its real-world date, or the elder date for an elder kind); None: a soft tech, no floor.
    Gated: dated gate_kyr or older (the Pleistocene and the glacial gate), or came on Earth more than lag_max_kyr after its
    prerequisites (salting, sledges, the calendar: the tree lacks the real precondition, so the date is the only gate it has)."""
    t = T["techs"][tid]
    D = T["defaults"]
    e = t.get("earliest_kyr")
    if e is None:
        return None
    ready = _earth_ready(T, tid)
    if e < D["gate_kyr"] and (ready is None or ready - e <= D["lag_max_kyr"]):
        return None
    return float(t.get("elder_kyr", e)) if elder else float(e)


def strength(pool: float, D: dict) -> float:
    """S: the pool's strength, Henrich's ln N with its threshold: 0 at N* (pool_threshold) or less, 1 at N0 (pool_ref), at most pool_max."""
    n0, n1 = D["pool_threshold"], D["pool_ref"]
    if pool <= n0:
        return 0.0
    return min(math.log(pool / n0) / math.log(n1 / n0), D["pool_max"])


def specialist_share(T: dict, known) -> float:
    """s: the share of a people not getting food, a judgement ladder after Childe 1950: the highest rung whose techs it knows."""
    s = T["defaults"]["specialists_base"]
    for r in T.get("specialists", []):
        if all(n in known for n in r["needs"]):
            s = max(s, float(r["share"]))
    return s


def density_x(dens: float | None, D: dict) -> float:
    """The density term on the specialist pool: (people per km2 / dens_ref) ^ dens_exp, clipped (a judgement after Bettencourt et al.
    2007, Table 1: innovation per head ~ settlement size ^ 0.15-0.3; density stands in for settlement size)."""
    if dens is None or dens <= 0:
        return 1.0
    return float(np.clip((dens / D["dens_ref"]) ** D["dens_exp"], D["dens_x_min"], D["dens_x_max"]))


def learners_x(gen_yr: float | None, D: dict) -> float:
    """The kind's learners: its generation over a human's (Henrich: skill is lost at each hand-off, so a kind that hands on its
    skills a tenth as often loses a tenth as much per kyr; the same as a pool that many times larger), clipped."""
    g = GENERATION_REF_YR if gen_yr is None else float(gen_yr)
    return float(np.clip(g / GENERATION_REF_YR, D["learners_min"], D["learners_max"]))


def culture_of(T: dict, line: dict) -> tuple[dict, dict]:
    """(invent, take): the people's culture (traits and way, [culture]) as a factor per domain, the best over them, capped."""
    D = T["defaults"]
    inv, take = {}, {}
    for key in list(line.get("traits") or []) + ([line["way"]] if line.get("way") else []):
        c = (T.get("culture") or {}).get(key) or {}
        for d, x in c.items():
            if d == "take":
                for dd, xx in x.items():
                    take[dd] = max(take.get(dd, 1.0), float(xx))
            else:
                inv[d] = max(inv.get(d, 1.0), float(x))
    return ({d: min(x, D["culture_cap"]) for d, x in inv.items()}, take)


def domain_x(c: dict, t: dict) -> float:
    """The best culture factor over a tech's domains (1 without a match)."""
    return max([c.get(d, 1.0) for d in domains_of(t)] + [1.0])


def _anchor_ready(T: dict, tid: str) -> float | None:
    """When Earth's anchor people could start on a Holocene tech, kyr: its prerequisites' date, but no earlier than the glacial gate
    opened (gate_kyr): the whole Holocene package waited on the climate, whatever its old prerequisites."""
    ready = _earth_ready(T, tid)
    e = T["techs"][tid].get("earliest_kyr")
    if ready is None or e is None:
        return ready
    return min(ready, T["defaults"]["gate_kyr"]) if e < T["defaults"]["gate_kyr"] else ready


def anchor_lag(T: dict, tid: str) -> float | None:
    """Earth's lag after the prerequisites, kyr: the tech's date less _anchor_ready, at least lag_min_kyr."""
    e = T["techs"][tid].get("earliest_kyr")
    ready = _anchor_ready(T, tid)
    return None if ready is None or e is None else max(ready - e, T["defaults"]["lag_min_kyr"])


def anchor_strength(T: dict, tid: str) -> float:
    """S of the anchor people (anchor_pop at anchor_dens, a human generation) for a tech, knowing what Earth knew when it could
    start on it (every tech dated then or earlier)."""
    D = T["defaults"]
    t = T["techs"][tid]
    p = pool_of(t)
    if p == "none":
        return 1.0
    n = D["anchor_pop"]
    if p == "specialists":
        ready = _anchor_ready(T, tid)
        ready = t.get("earliest_kyr", 0.0) if ready is None else ready
        earth = {i for i, u in T["techs"].items() if u.get("earliest_kyr") is not None and u["earliest_kyr"] >= ready
                 and u.get("mode") != "fantasy"}
        n *= specialist_share(T, earth) * density_x(D["anchor_dens"], D)
    return strength(n, D)


def band_wait(T: dict, tid: str) -> float | None:
    """A floored tech's band (PW-1138): its date less the median of Earth's dated independent origins (`origins_kyr`, the tech
    catalogue's; one older than the date counts at it), kyr, at least lag_min_kyr: how long a people that could invent it waited
    after the floor, at the median. None: fewer than two dated origins (one find, which then spread: its track's rate), or the
    catalogue's first origin is younger than the tree's date (the two disagree on the find the floor stands for: cordage 500
    kyr in the tree, origins 52 and 40; mines 40, origins 7.5 to 6), so the band does not belong to the floor."""
    t = T["techs"][tid]
    e, ks = t.get("earliest_kyr"), [float(k) for k in t.get("origins_kyr") or []]
    if e is None or len(ks) < 2 or max(ks) < float(e):
        return None
    return max(float(e) - float(np.median([min(k, float(e)) for k in ks])), T["defaults"]["lag_min_kyr"])


def rate_of(T: dict, tid: str) -> float:
    """Per kyr at full strength: the tech's own rate; else, for a Holocene tech (dated after the gate), the anchor rate (the anchor
    people's median wait after the prerequisites is Earth's lag: RAMP_MEDIAN / (lag x S)); for a Pleistocene one with a band
    (band_wait), the same with the band's wait after the floor (PW-1138); else its track's."""
    D = T["defaults"]
    t = T["techs"][tid]
    if "rate" in t:
        return float(t["rate"])
    e = t.get("earliest_kyr")
    soft = e is not None and e < D["gate_kyr"]
    lag = None if e is None else anchor_lag(T, tid) if soft else band_wait(T, tid)
    if lag is not None:
        s = anchor_strength(T, tid)
        if s > 0:  # (a soft tech: Earth's date is the first of anchor_peers peoples' finds; a band: a typical origin's wait)
            return ramp_first(D["anchor_peers"] if soft else 1) / (lag * s)
    return float(D["track_rate"].get(t["track"], D["rate"]))


def own_floor(T: dict, tid: str) -> float | None:
    """D55's floor on a people's (a region's) own inventing, per kyr (PW-1471): a learner (a region, with regions on) that meets a
    soft tech's conditions and has any specialists to spare invents it no slower than the anchor learner does, whatever its size,
    pool or culture. The anchor learner is the one the tech's rate is calibrated on (anchor_pop at anchor_dens, knowing what Earth
    knew; rate_of x anchor_strength): Earth's date is the first find among anchor_peers of them. So the floor lifts only learners
    slower than that and never speeds up the anchor (anchor_check is unchanged by it). Where the tech has dated independent origins
    (`origins_kyr`, at least two), the floor is no faster than Earth's median independent inventor either: RAMP_MEDIAN /
    (_anchor_ready - their median). (Lane 200's first floor was that alone; for writing it was faster than the anchor learner, so it
    sped up every big people.) A hazard, never a date: the tech can still not come, and contact can still bring it first. None: a
    floored (Pleistocene) tech, a tech with its own rate, or the tree's [defaults] own_floor off."""
    t = T["techs"][tid]
    D = T["defaults"]
    if not D.get("own_floor", False) or "rate" in t or floor_of(T, tid) is not None:
        return None
    ready, e = _anchor_ready(T, tid), t.get("earliest_kyr")
    if ready is None or e is None or e >= D["gate_kyr"]:
        return None
    fl = rate_of(T, tid) * anchor_strength(T, tid)
    ks = [float(k) for k in t.get("origins_kyr") or []]
    if len(ks) >= 2:
        wait = max(ready - float(np.median([min(k, float(e)) for k in ks])), D["lag_min_kyr"])
        fl = min(fl, RAMP_MEDIAN / wait)
    return fl if fl > 0 else None


def region_shares(present: np.ndarray | None, landmass: np.ndarray | None, idx: dict, min_share: float,
                  region_mkm2: float = 0.0) -> dict:
    """{people: [(landmass rank, share of its range)]}: each people's regions (PW-1471, D55: a people over several landmasses is
    several learners), the present-day landmasses (crossing.Crossings' ranks) holding at least min_share of its range (presence >=
    0.05, weighted by presence). With region_mkm2 > 0, a people's part of a landmass larger than that many Mkm2 is that many learners
    (ceil(area / region_mkm2), the share split evenly): a region is a stretch of land, not a whole continent. Empty without a range
    or the landmasses."""
    out: dict = {}
    if present is None or landmass is None or present.shape[1] != landmass.shape[0]:
        return out
    lm = np.asarray(landmass)
    ok = lm >= 0
    nl = int(lm.max()) + 1 if ok.any() else 0
    for lid, k in idx.items():
        if k >= present.shape[0]:
            continue
        p = np.where(present[k] >= 0.05, present[k], 0.0)
        tot = float(p[ok].sum())
        if tot <= 0:
            continue
        w = np.bincount(lm[ok], weights=p[ok], minlength=nl) / tot
        rs = [(int(r), float(w[r])) for r in np.flatnonzero(w >= min_share)]
        if region_mkm2 > 0 and rs:
            cell = 4 * math.pi * 6371.0 ** 2 / lm.shape[0] / 1e6
            cells = np.bincount(lm[ok], weights=(p[ok] > 0).astype(float), minlength=nl)
            rs = [(r, x / k) for r, x in rs for k in [max(1, math.ceil(cells[r] * cell / region_mkm2))] for _ in range(k)]
        out[lid] = rs
    return out


def generations(tree_raw: dict | None) -> dict:
    """{line id: generation, yr} from a stored run's meta.tree (a dragon's from its age schedule, as history.gen_yr), for runs
    whose lines don't carry it."""
    if not tree_raw:
        return {}
    from . import dragon_ages as DA
    from . import life_history as LH
    from . import spec as SP
    t = SP.parse(tree_raw)
    return {l.id: (DA.generation_yr(t.dragon_ages, t.dragon_generation, l.generation_yr) if l.megafauna and "flies" in l.traits
                   else LH.generation_yr(l)) for l in t.lines.values()}


def with_generations(lines: list[dict], tree_raw: dict | None) -> list[dict]:
    """meta.lineages with each line's generation_yr, from meta.tree where a stored run's lines don't carry it."""
    if all(l.get("generation_yr") is not None for l in lines):
        return lines
    g = generations(tree_raw)
    return [{**l, "generation_yr": l.get("generation_yr", g.get(l["id"]))} for l in lines]


def _series(line: dict, pops: dict) -> tuple | None:
    """(ago, population, people per km2, area Mkm2) through time from a line's saved track ([ago, lat, lon, area Mkm2,
    population] per frame), oldest first; else its present population alone (area from it and its density); None without either."""
    tr = [r for r in (line.get("track") or []) if len(r) >= 5]
    if tr:
        a = np.array([float(r[0]) for r in tr])
        p = np.array([float(r[4]) for r in tr])
        ar = np.array([float(r[3]) for r in tr])
        o = np.argsort(-a)
        dens = np.where(ar > 0, p / np.maximum(ar, 1e-9) / 1e6, 0.0)
        return a[o], p[o], dens[o], ar[o]
    q = pops.get(line["id"]) or {}
    if q.get("population"):
        n, d = float(q["population"]), float(q.get("density") or 0.0)
        return np.array([0.0]), np.array([n]), np.array([d]), np.array([n / d / 1e6 if d > 0 else 0.0])
    return None


def _at(ser, ago: float) -> tuple[float, float]:
    """(population, density) of a series at a time (linear between frames; the nearest end outside them)."""
    a, p, d = ser[:3]
    return float(np.interp(-ago, -a, p)), float(np.interp(-ago, -a, d))


def _area_at(ser, ago: float) -> float | None:
    """The range, Mkm2, of a series at a time; None: not known."""
    if ser is None:
        return None
    v = float(np.interp(-ago, -ser[0], ser[3]))
    return v if v > 0 else None


def contact_rate(area_mkm2: float | None, D: dict) -> float:
    """Per kyr, the rate at which a people takes up a tech its neighbour knows (before spread, border, openness and culture):
    the tech's front crosses the taker's country at contact_speed_km_yr, so half its people have it when the front has gone
    half its width (sqrt of its range); as a hazard with that median, 2 ln 2 v / sqrt(area). The width is at least
    contact_width_min_km. Without a range, the anchor people's (anchor_pop / anchor_dens). Speed: the Neolithic front, 0.6-1.3
    km/yr (Pinhasi, Fort & Ammerman 2005); pottery's among foragers, 0.2-0.5 off and 1.2-3.3 km/yr along favoured corridors
    (Jordan et al. 2016, Table 1)."""
    a = area_mkm2 if area_mkm2 else D["anchor_pop"] / D["anchor_dens"] / 1e6
    width = max(math.sqrt(a * 1e6), D["contact_width_min_km"])
    return 2 * math.log(2) * D["contact_speed_km_yr"] * 1e3 / width


# ---- D52's experiment arms (lane 186, PW-1461; docs/review/culture/writing/round2.md): how urban and administrative know-how
# crosses to a neighbour. One switch, `contact_arms` (the tree's [defaults], or build's `arms`): a string of letters; empty = off =
# the plain front above, bit for bit. Each letter is a mechanism:
#   B  town network: a tech that needs towns or cities crosses the width of the taker's town cells (sqrt of their area), not of
#      its whole range. Needs the town footprint (`towns`, from the settlement ledger: techspread.town_footprint).
#   C  trade contact: when both sides know towns, an urban tech's front runs at arm_trade_km_yr instead of contact_speed_km_yr:
#      pottery's favoured corridors, Jordan et al. 2016: 1.2 (Asian zone) and 3.3 km/yr (African zone) against 0.2 and 0.5 off
#      them (Table 1, read by lane 70); the supplement gives 1.46-5.51 along the Mediterranean corridor (lane 186). 2.2: between.
#   E  elite uptake: a people with chiefdoms, kingship or towns takes an administrative tech (ARM_ADMIN, or `admin = true` in
#      the tree) once the front reaches its nearest town: the width is its town spacing, sqrt(range / town cells). Needs `towns`.
#   T  trade-weighted B (D53, PW-1461; with B): the width is the range's ^ (1 - tau) x the town network's ^ tau, tau the GIVER's
#      trade-mindedness (trade_of): a trading people's writing crosses a taker's towns, an inward one's its whole land.
#   K  kin share: between a people and its parent, its daughter lines or a sibling line, begun within arm_kin_kyr (a language
#      family's depth, a judgement), the taker's insularity does not apply (openness 1): its reserve is against Others.
#   S  settled uptake (D60 B, PW-1490, lane 207): a state tech (`state = true` in the tree: writing, kingship, law, taxation, census,
#      bureaucracy, coinage) is invented, taken up, shared or inherited only by a people with towns of its own then (settled():
#      at least one town cell in the footprint), not from the knowledge alone. Its front still arrives as before, so a people that
#      founds a town takes up a tech already at its border at once. Without a footprint at all, the people's way of life decides
#      (not a mobile one, MOBILE_WAYS). Foragers, herders and sea nomads without towns stay without states and writing, as the
#      Ethnographic Atlas's mobile peoples did (docs/review/culture/techtree/round3.md).
# A front's arrival is recomputed each step for the techs an arm touches and never moves later (a front that gains a road
# speeds up from where it is; the pair's keyed draw is unchanged).
ARM_ADMIN = ("writing", "alphabet", "law")
ARM_URBAN_NEEDS = ("towns", "cities")
ARM_ELITE = ("chiefdoms", "kingship", "towns")
#      Round 3b (lane 207b): (1) settled is read over living memory (MEMORY_GENERATIONS of the people's own generation, at least the
#      footprint's own sampling step), so a town count flickering around one cell, or a town lost a lifetime ago, does not re-close
#      the gate; (2) a people the ledger books no places to (a group: settlements books its places to its people; an overlay hybrid,
#      living among its parents) is settled as its hosts are, unless its own way is a mobile one; (3) a front the gate blocks is
#      carried, not dropped (Calendar.carry): a people without towns that a state tech's front (or that of a tech needing one) has
#      crossed passes it on to its neighbours as a holder would, and takes it up itself at once if it later founds a town, but does
#      not hold it, invent with it or count it. Knowledge already held is never lost (`known` only grows); a split that is not
#      settled at its start carries its parent's state techs instead of holding them.
MOBILE_WAYS = ("forager", "fisher_forager", "hunter", "pastoral_nomad", "nomadic", "sea_nomad", "transhumant")  # (arm S without a footprint)
MEMORY_GENERATIONS = 3  # JUDGEMENT (round 3b): living memory, grandparent to grandchild: a people that held a town within 3 of its
                        # generations still has the people who ran it (25 yr generations: 75 yr; an elf's 145: ~435 yr)
ARM_LETTERS = "BCEKST"
ARM_DEFAULTS = {"contact_arms": "", "arm_trade_km_yr": 2.2, "arm_kin_kyr": 15.0,
                "arm_width_x": 1.0}  # (width_x: a factor on B's and E's width, for the nudge check)


def _arm(D: dict, k: str):
    return D.get(k, ARM_DEFAULTS[k])


TOWN_ARMS = frozenset("BEST")  # (the arms that read the town footprint)


def trade_of(line: dict) -> float:
    """D53's trade-mindedness of a spreading people, 0..1 (PW-1461): its openness, 1 - insularity (the tree's own trade axis,
    attitudes.py: "openness to trade is the insularity the tree already has"), + 0.1 for a cosmopolitan people (attitudes.TOL_COSMO)."""
    tr = line.get("traits") or []
    ins = float((line.get("demography") or {}).get("insularity", 0.85 if "insular" in tr else 0.3 if "cosmopolitan" in tr else 0.5))
    return float(np.clip(1.0 - ins + (0.1 if "cosmopolitan" in tr else 0.0), 0.0, 1.0))


def arms_of(T: dict | None = None) -> str:
    """The tree's D52 arms (its [defaults] contact_arms), as sorted letters."""
    return "".join(sorted(set(str(_arm((T or load())["defaults"], "contact_arms"))) & set(ARM_LETTERS)))


def town_arms(T: dict | None = None) -> str:
    """The tree's arms that need the settlement ledger's town footprint (B, E, S): output.save then builds the tree twice (PW-1464)."""
    return "".join(sorted(set(arms_of(T)) & TOWN_ARMS))


def arms_without_towns(T: dict | None = None) -> str:
    """The tree's arms less B, E and S: the first tree output.save builds, before the ledger exists (PW-1464)."""
    return "".join(sorted(set(arms_of(T)) - TOWN_ARMS))


def kin_pairs(lines: list[dict], kin_kyr: float) -> set:
    """Pairs (both ways) of lines that are kin for arm K: parent and daughter (a split, a hybrid and its parents, a group and its
    people), or two daughters of one parent, where the daughter began within kin_kyr ago."""
    out = set()
    ids = {l["id"] for l in lines}
    kids: dict = {}
    for l in lines:
        began = float(l.get("started_kyr") if l.get("started_kyr") is not None else l.get("ago_kyr", 1e9))
        if began > kin_kyr:
            continue
        for q in ([l["group_of"]] if l.get("group_of") else (l.get("parents") or [])):
            if q in ids:
                out |= {(q, l["id"]), (l["id"], q)}
                kids.setdefault(q, []).append(l["id"])
    for ks in kids.values():
        out |= {(a, b) for a in ks for b in ks if a != b}
    return out


def town_cells_at(tw, ago: float) -> float:
    """A people's town cells at a time, from its footprint (agos oldest first, counts); 0 before it or without one."""
    if tw is None:
        return 0.0
    a, c = tw
    if ago > a[0] + 1e-9:
        return 0.0
    return float(np.interp(-ago, -np.asarray(a), np.asarray(c)))


def town_cells_within(tw, ago: float, w: float) -> float:
    """The most town cells a people held at any time from `w` kyr before `ago` to `ago` (its footprint's samples in that window, and
    the interpolated values at both ends); 0 without a footprint. Arm S reads it over living memory (Calendar.settled)."""
    if tw is None:
        return 0.0
    n = max(town_cells_at(tw, ago), town_cells_at(tw, ago + w))
    a = np.asarray(tw[0], float)
    m = (a >= ago - 1e-9) & (a <= ago + w + 1e-9)
    return max(n, float(np.asarray(tw[1], float)[m].max())) if m.any() else n


def keyed(seed: int, *key) -> float:
    """A uniform draw in [0, 1) for one purpose (PW-1459): a hash of the seed and the key, so it does not depend on how many
    draws came before it (common random numbers, as polities.draw)."""
    d = hashlib.blake2b("|".join(map(str, (675, seed, *key))).encode(), digest_size=8).digest()
    return (int.from_bytes(d, "little") >> 11) * 2.0 ** -53


def links_of(contacts: dict | None, kind: dict) -> list[tuple]:
    """meta.contacts' pairs as intervals (a, b, from kyr, to kyr, border km) between the tree's peoples."""
    links = []
    for p in (contacts or {}).get("pairs", []):
        if p["a"] in kind and p["b"] in kind:
            ser = p.get("series") or []
            to = 0.0 if p.get("in_contact_now") else (min(q[0] for q in ser) if ser else p["first_contact_kyr"])
            km = float(np.median([q[1] for q in ser])) if ser else float(p.get("border_km_peak", 0))
            links.append((p["a"], p["b"], float(p["first_contact_kyr"]), to, km))
    return links


def forced_of(pres: dict | None, techs: dict, L: dict) -> dict[str, list[tuple[float, str]]]:
    """Forced knowledge: the first tamings of the history (crops.py, animals.py), {line: [(kyr ago, tech)]}. `pres` as meta.present
    (or anything with its "crops" and "animals" stocks' `tamed` and `took_up_kyr`)."""
    forced: dict[str, list[tuple[float, str]]] = {}
    stock_tech = {t.get("stock"): i for i, t in techs.items() if t.get("stock")}
    for key in ("crops", "animals"):  # (stock "crops": any crop; "crops:wheat": that one, PW-1122)
        st = ((pres or {}).get(key) or {}).get("stocks") or {}
        for sid, s in st.items():
            tids = [stock_tech[k] for k in (key, f"{key}:{sid}") if k in stock_tech]
            for tm in s.get("tamed") or []:
                if tm.get("line") in L:
                    forced.setdefault(tm["line"], []).extend((float(tm["ago_kyr"]), tid) for tid in tids)
            for lid, ago in (s.get("took_up_kyr") or {}).items():
                if lid in L and ago is not None:
                    forced.setdefault(lid, []).extend((float(ago), tid) for tid in tids)
    return forced


class Calendar:
    """The tech tree as a step function (PW-1466): `advance(ago)` runs its steps down to a time, from what `feed` last gave it, so
    the history can run it century by century (history.tech_live) and the polities in the history read the real calendar.
    `build` is the same object fed once with the whole run and advanced to the present. The steps (log-spaced from the oldest
    line, STEPS) and every draw (`keyed`: (seed, people, tech, step)) are the same either way, so a step run early meets the same
    luck as one run after the history; only what it reads differs (the populations, contacts, tamings and goods known by then)."""

    def __init__(self, lines: list[dict], mode: str = "fantasy", era: str | None = "renaissance", seed: int = 0,
                 T: dict | None = None, gods_mode: str = "faith_made", towns: dict | None = None, arms: str | None = None):
        T = T or load()
        D = T["defaults"]
        self.T, self.D, self.seed, self.mode, self.era, self.gods_mode = T, D, seed, mode, era, gods_mode
        self.arms = arms = set(str(_arm(D, "contact_arms") if arms is None else arms)) & set(ARM_LETTERS)
        cap = ERAS.index(era) if era in ERAS else len(ERAS) - 1
        self.techs = techs = {i: t for i, t in T["techs"].items() if ERAS.index(t.get("era", "stone age")) <= cap
                              and (mode != "real" or t.get("mode") != "fantasy") and (gods_mode != "belief_only" or not t.get("gods"))}
        self.order = [i for i in T["order"] if i in techs]
        self.rank = {i: k for k, i in enumerate(self.order)}
        self.L = L = {l["id"]: l for l in lines}
        self.people = people = [l for l in lines if not (l.get("overlay") and l.get("origin") == "template")]
        self.idx = {l["id"]: l.get("index", k) for k, l in enumerate(lines)}
        unmatched = [" | ".join(k["of"]) for k in T.get("kind", []) if not set(k["of"]) & set(L)]
        if unmatched:  # (a rule none of whose ids is a line of this tree applies to nothing, PW-1041)
            warnings.warn(f"tech tree [[kind]] rules name no line of this tree: {', '.join(unmatched)}", stacklevel=3)
        self.kind = {l["id"]: _kind(T, l, L) for l in people}
        self.sea = {l["id"]: is_sea(l, L) for l in people}  # (PW-1491: who may hold the sea branch)
        self.node = {l["id"]: _node(l, L) for l in people}  # (PW-971: the sapiens node, kyr, of the line's stem; None: no stem node above it)
        self.gens = {l["id"]: _gen(l, L) for l in people}
        self.learn = {lid: learners_x(g, D) for lid, g in self.gens.items()}
        self.culture = {l["id"]: culture_of(T, l) for l in people}
        self.rates = {i: rate_of(T, i) for i in techs}
        self.floors = {i: f for i in techs for f in [own_floor(T, i)] if f is not None}  # (D55's floor on own inventing, PW-1471)
        self.regions: dict = {}  # ({people: [(landmass rank, share)]}: its regions, each a learner; none: the people is one)
        self.reached = {l["id"]: {int(k): float(v["ago_kyr"]) for k, v in (l.get("reached") or {}).items()} for l in people}
        self.pool = {i: pool_of(techs[i]) for i in techs}
        self.ready: dict[str, dict[str, float]] = {l["id"]: {} for l in people}  # (when each people first met a tech's conditions: the ramp)
        self.known: dict[str, dict[str, list]] = {l["id"]: {} for l in people}
        self.hz: dict[str, dict[str, float]] = {l["id"]: {} for l in people}  # (the invention hazard summed so far, per people and tech)
        self.waits: dict[tuple, float] = {}  # ((people, tech): its keyed waiting time, in units of hazard: PW-1483)
        self.state = {i for i, t in techs.items() if t.get("state")} if "S" in arms else set()  # (arm S: D60 B)
        self.towns = towns or {}
        self.carry: dict[str, dict[str, list]] = {l["id"]: {} for l in people}  # (arm S, round 3b: fronts the gate blocked, passed on)
        if arms:
            self.urban = {i for i, t in techs.items() if set(t.get("needs", [])) & set(ARM_URBAN_NEEDS)}
            self.admin = {i for i, t in techs.items() if t.get("admin") or i in ARM_ADMIN}
            self.touched = (self.urban if arms & {"B", "C", "T"} else set()) | (self.admin if "E" in arms else set())
            self.kin = kin_pairs(lines, float(_arm(D, "arm_kin_kyr"))) if "K" in arms else set()
            if arms & {"B", "E"} and not towns:  # (no footprint: a tree built before the settlement ledger, or inside the history)
                warnings.warn(f"tech tree arms {''.join(sorted(arms & {'B', 'E'}))} need a town footprint; without one they do nothing",
                              stacklevel=3)
            self.cell_km2 = float(self.towns.get("_cell_km2") or 0.0)
            self.v_trade = float(_arm(D, "arm_trade_km_yr"))
            self.width_x = float(_arm(D, "arm_width_x"))
        self.began: set = set()
        self.arrive: dict[tuple, float | None] = {}  # ((giver, taker, tech): when its front reaches the taker's middle, kyr; None: never)
        self.unit: dict[tuple, float] = {}  # ((giver, taker): the pair's front delay, in units of 1 / the contact rate)
        self.grid = None
        self.step = 0  # (the next step to run)
        self.prev = None
        self.have: dict = {l["id"]: None for l in people}
        self.series: dict = {l["id"]: None for l in people}
        self.start: dict = {}
        self.end: dict = {}
        self.forced: dict = {}
        self.links: list = []

    # ------------------------------------------------------------ what it reads
    def feed(self, lines: list[dict] | None = None, links: list | None = None, forced: dict | None = None, have: dict | None = None,
             pops: dict | None = None, regions: dict | None = None):
        """What the tree reads, as known now: the lines' starts, ends and tracks (meta.lineages' fields), the contacts as intervals
        (links_of), the tamings (forced_of), the goods each people's country holds (goods_held) and its regions (region_shares).
        None keeps the last."""
        if have is not None:
            self.have = have
        if regions is not None:
            self.regions = regions
        if lines is not None:
            for l in lines:  # (the landmasses each people has reached so far, dated: crossing.Crossings.reached)
                if l["id"] in self.reached and l.get("reached") is not None:
                    self.reached[l["id"]] = {int(k): float(v["ago_kyr"]) for k, v in l["reached"].items()}
            pops = pops or {}
            self.series = {l["id"]: _series(l, pops) for l in lines if l["id"] in self.kind}  # (population and density through time, from the saved tracks)
            self.start = {l["id"]: float(l.get("started_kyr") if l.get("started_kyr") is not None else l.get("ago_kyr", 0.0))
                          for l in lines if l["id"] in self.kind}
            self.end = {l["id"]: float(l["ended_kyr"]) if l.get("ended_kyr") is not None else -1.0 for l in lines if l["id"] in self.kind}
        if forced is not None:
            self.forced = forced
        if links is not None:
            self.links = links

    # ------------------------------------------------------------ the rules
    def give(self, lid, tid, ago, how, frm=None):
        if tid in self.techs and tid not in self.known[lid]:
            self.known[lid][tid] = [round(float(ago), 3), how, frm]

    def held(self, lid, tid, at):  # (PW-987: a line cannot inherit a tool it cannot hold: the cats take no found tools from the mammal root)
        t = self.techs[tid]
        return not t.get("hands", True) or _grips(t, self.kind[lid], self.node[lid], at)

    def can(self, lid, tid, ago, inventing, needs=True, gate=True):
        t = self.techs[tid]
        k = self.kind[lid]
        kn = self.known[lid]
        if tid in kn or (needs and any(n not in kn for n in t.get("needs", []))):
            return False
        if needs and t.get("needs_any") and not any(n in kn for n in t["needs_any"]):  # (one of them: a mount, a milk beast)
            return False
        node = self.node[lid]
        if node is not None and ago > node and not t.get("bare"):  # (PW-971: before its stem's minds only bare-bones tools)
            return False
        if t.get("hands", True) and not _grips(t, k, node, ago):
            return False
        if (inventing or not t.get("traded")) and not _env_ok(t, self.have[lid]):  # (a traded tech, bronze, comes without the ore)
            return False
        if t.get("sea") and not self.sea[lid] and (inventing or not t.get("traded")):  # (the sea branch: sea peoples; pearls by trade)
            return False
        if gate and tid in self.state and not self.settled(lid, ago):  # (arm S, D60 B: a state tech needs towns of the people's own)
            return False
        if inventing:
            first = floor_of(self.T, tid, bool(k.get("elder")))  # (a gated tech's floor; a soft tech has none)
            return first is None or ago <= first
        return True

    def settled(self, lid, ago, depth=0) -> bool:
        """Arm S (D60 B): whether a people is settled enough for a state tech then: a town of its own in the footprint (the
        settlement ledger's, or the live polities' seats inside the history) within living memory (memory()); a people the
        footprint books no places to that is a group or an overlay hybrid: as its hosts (its people, or its parents), unless its
        own way is a mobile one; with no footprint at all, a way of life that is not a mobile one (MOBILE_WAYS)."""
        l = self.L[lid]
        if not self.towns:
            return l.get("way") not in MOBILE_WAYS
        tw = self.towns.get(lid)
        if tw is None:
            hosts = [l["group_of"]] if l.get("group_of") else (l.get("parents") or []) if l.get("overlay") else []
            return l.get("way") not in MOBILE_WAYS and depth < 4 and any(
                h in self.L and h != lid and self.settled(h, ago, depth + 1) for h in hosts)
        return town_cells_within(tw, ago, self.memory(lid, tw)) >= 1

    def memory(self, lid, tw) -> float:
        """Living memory, kyr (round 3b): MEMORY_GENERATIONS of the people's generation, and at least its footprint's sampling step
        (a dip of one sample is below what the footprint resolves)."""
        g = self.gens.get(lid)
        a = tw[0]
        return max(MEMORY_GENERATIONS * (GENERATION_REF_YR if g is None else g) / 1000.0,
                   abs(float(a[0]) - float(a[1])) if len(a) > 1 else 0.0)

    def keeps(self, lid, tid, at) -> bool:
        """Whether a line starting at `at` keeps a tech it inherits: it can hold the tool (PW-987), and a state tech only if settled
        (else it carries it: advance)."""
        t = self.techs[tid]
        return self.held(lid, tid, at) and (tid not in self.state or self.settled(lid, at)) \
            and (not t.get("sea") or self.sea[lid] or bool(t.get("traded")))  # (a land split of a sea people keeps no sea craft)

    def inherit(self, lid, src, tids, at):
        """A line's inheritance at its start `at` from `src` (a split's or group's parent, a hybrid's parents): the techs it keeps
        (keeps(); PW-971: a stem under a node only bare tools from before it). Arm S (round 3b): a state tech it may not hold, and a
        tech needing one it carries, is carried instead (advance), as is what the source carried."""
        techs, node = self.techs, self.node[lid]
        cr = self.carry[lid]
        for tid in sorted(set(tids) | set(self.carry.get(src) or {}), key=self.rank.get) if self.state else tids:
            if tid not in techs or tid in self.known[lid] or tid in cr:
                continue
            if node is not None and at > node and not techs[tid].get("bare"):
                continue
            stuck = tid in (self.carry.get(src) or {}) or any(n in cr for n in techs[tid].get("needs", []))
            if not stuck and self.keeps(lid, tid, at):
                self.give(lid, tid, at, "inherited", src)
            elif self.state and (stuck or tid in self.state) and self.held(lid, tid, at) \
                    and (not techs[tid].get("sea") or self.sea[lid] or bool(techs[tid].get("traded"))):
                cr[tid] = [round(float(at), 3), "carried", src]

    def gated(self, lid, tid, ago) -> bool:
        """Arm S (round 3b): whether only the gate keeps a people from taking a tech up by contact now: it is not settled, and it
        could take it if it were, counting what it carries as known (a tech that needs a state tech it carries)."""
        cr = self.carry[lid]
        t = self.techs[tid]
        if not self.state or tid in self.known[lid] or not (tid in self.state or any(n in cr for n in t.get("needs", []))
                                                             or any(n in cr for n in t.get("needs_any", []))):
            return False  # (no state tech in it: the gate is not what blocks it)
        if self.settled(lid, ago):
            return False
        kn = self.known[lid]
        self.known[lid] = {**kn, **cr}
        try:
            return self.can(lid, tid, ago, False, gate=False)
        finally:
            self.known[lid] = kn

    def wait_of(self, lid, tid) -> float:
        """The people's waiting time for a tech, in units of hazard (PW-1483): one keyed exponential draw (mean 1) per (seed, people,
        tech); the people invents once the hazard summed since it could start reaches it (the inverse method). The chance of inventing
        in a step is 1 - exp(-h dt), as one draw per step gave, but a small change in the hazard now moves the date a little instead
        of re-rolling every later step's luck."""
        k = (lid, tid)
        if k not in self.waits:
            self.waits[k] = -math.log1p(-keyed(self.seed, "wait", lid, tid))
        return self.waits[k]

    def strengths(self, lid, ago):
        """(S of the whole people, S of its specialists, s) now."""
        D = self.D
        ser = self.series[lid]
        n, dens = _at(ser, ago) if ser is not None else (D["pool_default"], None)
        n *= self.learn[lid]
        s = specialist_share(self.T, self.known[lid])
        return strength(n, D), strength(n * s * density_x(dens, D), D), s

    def region_shares(self, present, landmass) -> dict:
        """region_shares for this tree's peoples (its [defaults] region_min_share); {} with [defaults] regions off."""
        if not self.D.get("regions", False):
            return {}
        return region_shares(present, landmass, {l["id"]: self.idx[l["id"]] for l in self.people}, float(self.D.get("region_min_share", 0.1)),
                             float(self.D.get("region_mkm2", 0.0)))

    def learners(self, lid, ago) -> list[tuple[float, float, float]]:
        """[(S of the whole, S of the specialists, share)] per region learner of a people now (PW-1471, D55): its regions reached by
        now (region_shares, Crossings' dated arrivals), each with its share of the people (renormalised); one learner without them."""
        rg = [(r, w) for r, w in self.regions.get(lid) or [] if self.reached[lid].get(r, -1.0) >= ago - 1e-9]
        if len(rg) <= 1:
            s_all, s_spec, _ = self.strengths(lid, ago)
            return [(s_all, s_spec, 1.0)]
        D = self.D
        ser = self.series[lid]
        n, dens = _at(ser, ago) if ser is not None else (D["pool_default"], None)
        n *= self.learn[lid]
        s = specialist_share(self.T, self.known[lid])
        tot = sum(w for _, w in rg)
        return [(strength(n * w / tot, D), strength(n * w / tot * s * density_x(dens, D), D), w / tot) for _, w in rg]

    def knows(self, lid, tid, ago):
        v = self.known[lid].get(tid)
        return v is not None and v[0] >= ago - 1e-9

    def arm_rate(self, x, y, tid, ago, op, w):
        """The contact rate (before spread and culture) of an arm-touched front: width, speed and openness as the arms say."""
        D, arms = self.D, self.arms
        a = _area_at(self.series[y], ago) or D["anchor_pop"] / D["anchor_dens"] / 1e6
        if (x, y) in self.kin:
            op = 1.0
        width = math.sqrt(a * 1e6)
        n = town_cells_at(self.towns.get(y), ago) if tid in self.touched else 0.0
        if "E" in arms and tid in self.admin and n >= 1 and any(self.knows(y, e, ago) for e in ARM_ELITE):
            width = self.width_x * math.sqrt(a * 1e6 / n)  # (the court's reach: the front need only reach its nearest town)
        elif "B" in arms and tid in self.urban and n >= 1 and self.cell_km2 > 0:
            town = min(self.width_x * math.sqrt(n * self.cell_km2), width)  # (the town network's width)
            if "T" in arms:  # (D53: as the giver is minded to trade; tau 0: its whole range, as off; 1: its towns, as B)
                tau = trade_of(self.L[x])
                width = width ** (1 - tau) * town ** tau
            else:
                width = town
        urb = "C" in arms and tid in self.urban and self.knows(x, "towns", ago) and self.knows(y, "towns", ago)
        v = self.v_trade if urb else D["contact_speed_km_yr"]
        return 2 * math.log(2) * v * 1e3 / max(width, D["contact_width_min_km"]) * w * op

    # ------------------------------------------------------------ the steps
    def advance(self, to: float | None = None) -> int:
        """Runs the steps at `to` kyr ago or before it (None: to the present); returns how many it ran. The steps are fixed at the
        first call, from the lines' starts then (the oldest line's start)."""
        T, D, techs, order, L, people, seed = self.T, self.D, self.techs, self.order, self.L, self.people, self.seed
        kind, node, culture, rates, pool, ready, known = self.kind, self.node, self.culture, self.rates, self.pool, self.ready, self.known
        start, end, series, forced, links, arms = self.start, self.end, self.series, self.forced, self.links, self.arms
        began, arrive, unit, hz, carry = self.began, self.arrive, self.unit, self.hz, self.carry
        give, can, held, strengths = self.give, self.can, self.held, self.strengths
        if self.grid is None:
            t0 = max(start.values(), default=1.0)
            self.grid = np.concatenate([np.geomspace(max(t0, 1.0), NEAR_KYR, STEPS), [0.0]])
            self.prev = self.grid[0]
        grid = self.grid
        ran = 0
        while self.step < len(grid):
            step, ago = self.step, grid[self.step]
            if to is not None and ago < to - 1e-9:
                break
            self.step += 1
            ran += 1
            prev = self.prev
            dt = max(prev - ago, 1e-6) if ago != grid[0] else 0.0
            self.prev = ago
            alive = [l for l in people if l["id"] in start and start[l["id"]] >= ago and (end[l["id"]] < 0 or ago > end[l["id"]])]
            for l in alive:  # (inheritance and kits, once, at the line's start)
                lid = l["id"]
                if lid in began:
                    continue
                began.add(lid)
                at = min(start[lid], grid[0])
                if l.get("origin") in ("split", "group") or l.get("group_of"):
                    src = l.get("group_of") or (l.get("parents") or [None])[0]
                    self.inherit(lid, src, [tid for tid, v in (known.get(src) or {}).items() if v[0] >= at - 1e-9], at)
                elif l.get("origin") == "hybrid":
                    for src in l.get("parents") or []:
                        self.inherit(lid, src, list(known.get(src) or {}), at)
                kit = closure(T, [i for i in kind[lid].get("kit", []) if i in T["techs"]])
                for tid in [i for i in order if i in kit]:
                    give(lid, tid, at, "kit" if l.get("origin") == "arrival" else "inherited", None)
            for l in alive:  # (tamings recorded by the history)
                for when, tid in forced.get(l["id"], []):
                    if when >= ago and tid not in known[l["id"]]:
                        for n in [i for i in order if i in closure(T, [tid]) and i != tid]:
                            give(l["id"], n, when, "with " + tid, None)
                        give(l["id"], tid, when, "tamed", None)
            if dt <= 0:
                continue
            # taking up by contact (lane 70, PW-1137): a tech's know-how is a front that sets out into a neighbour's country when the
            # giver knows it and they are in touch, and reaches its middle after a delay (median width / 2v, contact_rate) drawn once
            # per pair, so the techs the giver knew alike arrive together (x 1 / spread: language lags, traded bronze leads);
            # once it has, the neighbour takes it up as soon as it can use it, so a package travels together (the plough behind the
            # ox) instead of the taker's clock restarting at each prerequisite
            cand: dict[tuple, tuple] = {}
            for a, b, fr, to_, km in links:  # (diffusion over borders)
                if not (fr >= ago >= to_):
                    continue
                w = min(km / D["contact_full_km"], 1.0)
                for x, y in ((a, b), (b, a)):
                    if x not in began or y not in began:
                        continue
                    cr = None
                    cx = carry[x]
                    for tid in order:
                        kx = known[x].get(tid) or cx.get(tid)  # (arm S, round 3b: a carried front passes on as a held one)
                        if kx is None or tid in known[y] or kx[0] < ago:
                            continue
                        k3 = (x, y, tid)
                        if arms and (tid in self.touched or (x, y) in self.kin) and not techs[tid].get("modern_contact") \
                                and not (k3 in arrive and arrive[k3] is None):
                            op = 1 - 0.7 * float((L[y].get("demography") or {}).get("insularity", 0.3))
                            r = self.arm_rate(x, y, tid, ago, op, w) * techs[tid].get("spread", D["spread"]) \
                                * domain_x(culture[y][1], techs[tid])
                            if (x, y) not in unit:
                                unit[(x, y)] = -math.log1p(-keyed(seed, "front", x, y))  # (the same keyed draw as the plain front)
                            new = min(kx[0], fr) - unit[(x, y)] / r if r > 0 else None
                            if k3 not in arrive or (new is not None and new > arrive[k3]):
                                arrive[k3] = new  # (never later: the front keeps what it has crossed)
                        if k3 not in arrive:
                            if techs[tid].get("modern_contact") and node[y] is None:  # (language: to any genetically modern people, PW-971)
                                arrive[k3] = None
                                continue
                            if cr is None:
                                op = 1 - 0.7 * float((L[y].get("demography") or {}).get("insularity", 0.3))
                                cr = contact_rate(_area_at(series[y], ago), D) * w * op
                            r = cr * techs[tid].get("spread", D["spread"]) * domain_x(culture[y][1], techs[tid])
                            if (x, y) not in unit:  # (the pair's draw: one front, for all its techs, slower for a slow-spreading one)
                                unit[(x, y)] = -math.log1p(-keyed(seed, "front", x, y))  # (exponential, mean 1)
                            arrive[k3] = min(kx[0], fr) - unit[(x, y)] / r if r > 0 else None
                        at = arrive[k3]
                        if at is not None and at >= ago and at > cand.get((y, tid), (-1.0,))[0]:
                            cand[(y, tid)] = (at, x)
            # inventing, and the arrivals: a tech that arrives within the step may still be invented first, over the part of the step
            # before it arrived (neither is tried first)
            for l in alive:
                lid = l["id"]
                rx = kind[lid].get("rate_x", 1.0)
                lrn = self.learners(lid, ago)  # (its region learners, PW-1471; one for a people on one landmass)
                floors = self.floors
                cr = carry[lid]
                for tid in order:
                    arr = cand.get((lid, tid))
                    if arr is None and tid in cr:  # (arm S, round 3b: a front it carried, taken up once it may)
                        arr = (cr[tid][0], cr[tid][2])
                    lang = bool(techs[tid].get("modern_contact"))
                    took = arr is not None and can(lid, tid, ago, False, needs=not lang)
                    h = 0.0
                    if can(lid, tid, ago, True):
                        t = techs[tid]
                        base = rates[tid] * rx * domain_x(culture[lid][0], t)
                        fl = floors.get(tid, 0.0)
                        for s_all, s_spec, _ in (lrn if pool[tid] != "none" else lrn[:1]):  # (each region learns on its own pool, no
                            sp = 1.0 if pool[tid] == "none" else s_spec if pool[tid] == "specialists" else s_all  # slower than D55's floor)
                            h += max(base * sp, fl if sp > 0 else 0.0)
                        tau = ready[lid].setdefault(tid, ago) - ago
                        h *= 1 - math.exp(-h * (tau + 0.5 * dt))  # (the ramp, at the middle of the step)
                    span = min(max(ago + dt - arr[0], 0.0), dt) if took else dt
                    got = False
                    if h > 0 and span > 0:  # (PW-1483: one keyed waiting time per (people, tech), met by the hazard summed so far)
                        acc = hz[lid].get(tid, 0.0)
                        got = acc + h * span >= self.wait_of(lid, tid)
                        if not got:
                            hz[lid][tid] = acc + h * span
                    if got:
                        give(lid, tid, ago, "invented", None)
                    elif took:
                        if lang:
                            for n in [i for i in order if i in closure(T, [tid]) and i != tid]:
                                give(lid, n, ago, "with " + tid, arr[1])  # (its roots, gesture, come with it)
                        give(lid, tid, ago, "contact", arr[1])
                    elif arr is not None and tid not in cr and self.gated(lid, tid, ago):
                        cr[tid] = [round(float(ago), 3), "carried", arr[1]]  # (arm S, round 3b: blocked by the gate alone: carried on)
            for l in alive:  # (a group and its people share what they know as they go)
                g = l.get("group_of")
                if g and g in known:
                    for x, y in ((g, l["id"]), (l["id"], g)):
                        for tid, v in list(known[x].items()):
                            if v[0] >= ago and tid not in known[y] and can(y, tid, ago, False):
                                give(y, tid, ago, "shared", x)
                            elif v[0] >= ago and tid not in known[y] and tid not in carry[y] and self.gated(y, tid, ago):
                                carry[y][tid] = [round(float(ago), 3), "carried", x]
        return ran

    # ------------------------------------------------------------ meta.techtree
    def result(self) -> dict:
        """meta.techtree from the steps run so far (all of them, after advance())."""
        T, techs, order, known, people, end = self.T, self.techs, self.order, self.known, self.people, self.end
        firsts = firsts_of(known)
        drivers = {}  # (what drove each living people's inventing at the present: for the report and the viewer)
        for l in people:
            lid = l["id"]
            if self.end.get(lid, -1.0) >= 0:
                continue
            s_all, s_spec, s = self.strengths(lid, 0.0)
            ser = self.series[lid]
            drivers[lid] = {"population": int(_at(ser, 0.0)[0]) if ser is not None else None, "specialists": s,
                            "strength_all": round(s_all, 3), "strength_specialists": round(s_spec, 3),
                            "generation_yr": self.gens[lid], "learners_x": round(self.learn[lid], 2), "rate_x": self.kind[lid].get("rate_x", 1.0),
                            "culture": {d: round(x, 2) for d, x in self.culture[lid][0].items()},
                            "take": {d: round(x, 2) for d, x in self.culture[lid][1].items()}}
        pool, rates = self.pool, self.rates
        return {"file": str(T.get("_file", FILE.name)), "era": self.era, "mode": self.mode, "gods_mode": self.gods_mode,
                "tracks": [{"id": k["id"], "name": k["name"]} for k in T["track"]],
                "techs": [{"id": i, "name": techs[i]["name"], "track": techs[i]["track"], "needs": techs[i].get("needs", []),
                           "needs_any": [n for n in techs[i].get("needs_any", []) if n in techs],
                           "env": techs[i].get("env", []), "env_any": techs[i].get("env_any", []),
                           "earliest_kyr": techs[i].get("earliest_kyr"), "elder_kyr": techs[i].get("elder_kyr"),
                           "era": techs[i].get("era", "stone age"), "fantasy": techs[i].get("mode") == "fantasy",
                           **({"sea": True} if techs[i].get("sea") else {}), **({"state": True} if techs[i].get("state") else {}),
                           "source": techs[i].get("source", ""), "domains": domains_of(techs[i]), "pool": pool[i],
                           "floor_kyr": floor_of(T, i), "rate": round(rates[i], 4),
                           "anchor_lag_kyr": None if floor_of(T, i) is not None else anchor_lag(T, i)} for i in order],
                "known": known, "firsts": firsts, "drivers": drivers,
                "goods_checked": {lid: sorted(v) if v is not None else None for lid, v in self.have.items()}}


def build(lines: list[dict], contacts: dict | None, pres: dict | None, present: np.ndarray | None = None,
          goods: dict | None = None, mode: str = "fantasy", era: str | None = "renaissance", seed: int = 0,
          T: dict | None = None, gods_mode: str = "faith_made", towns: dict | None = None, arms: str | None = None,
          landmass: np.ndarray | None = None) -> dict:
    """meta.techtree for a peoples run, after its history (a Calendar fed the whole run and run to the present). gods_mode (PW-1304):
    "faith_made" (default), "belief_only" or "absolute"; a tech marked `gods = true` (divine magic) exists only in faith_made and
    absolute. `lines` as in meta.lineages (id, origin, parents, group_of, overlay, started_kyr,
    ended_kyr, demography, traits), `contacts` as meta.contacts, `pres` as meta.present (crops and animals: the tamings,
    lines: the populations), `present` the presence per line (lines x cells, 0..1), `goods` the world's goods and `landmass` each
    cell's present-day landmass (crossing.Crossings.label: the region learners, PW-1471; None: each people one learner). towns, arms:
    D52's experiment arms (ARM_DEFAULTS above; towns = {people: (agos oldest first, town cells), "_cell_km2": km2})."""
    c = Calendar(lines, mode, era, seed, T, gods_mode, towns, arms)
    have = {l["id"]: goods_held(c.T, present, goods, c.idx[l["id"]]) for l in c.people}
    c.feed(lines, links_of(contacts, c.kind), forced_of(pres, c.techs, c.L), have, (pres or {}).get("lines") or {},
           c.region_shares(present, landmass))
    c.advance()
    return c.result()


def _source_rank(how: str) -> int:
    """How much a record says the people found the tech itself: invented, then tamed or brought (a kit, or the roots
    that come with a taming), then got from someone else (contact, shared, inherited)."""
    if how == "invented":
        return 0
    if how in ("tamed", "kit") or how.startswith("with "):
        return 1
    return 2


def firsts_of(known: dict) -> dict:
    """Each tech's first people: the oldest date; on a tie (two records on the same grid step) the one that found it
    itself, so a same-step contact taker is never credited over its giver (PW-1012)."""
    firsts = {}
    for lid, kn in known.items():
        for tid, v in kn.items():
            f = firsts.get(tid)
            if f is None or v[0] > f["ago_kyr"] or (v[0] == f["ago_kyr"] and _source_rank(v[1]) < _source_rank(f["how"])):
                firsts[tid] = {"line": lid, "ago_kyr": v[0], "how": v[1]}
    return firsts


def lines_for_report(tt: dict, lines: list[dict]) -> list[str]:
    """A few lines for run.txt: when each people came to language and how many techs each knows now."""
    alive = [l for l in lines if l.get("leaf") and l["id"] in tt["known"]]
    out = [f"technology (techtree.py, PW-675 v1): {len(tt['techs'])} techs in {len(tt['tracks'])} tracks"]
    lang = sorted(((tt["known"][l["id"]].get("language") or [None])[0] or -1, l["id"]) for l in alive)
    out.append("  language: " + "; ".join(f"{lid} {'none' if a < 0 else f'{a:g} kyr ({tt['known'][lid]['language'][1]})'}"
                                         for a, lid in sorted(lang, key=lambda x: -x[0])))
    out.append("  techs known now: " + ", ".join(f"{l['id']} {len(tt['known'][l['id']])}" for l in
                                                 sorted(alive, key=lambda l: -len(tt["known"][l["id"]]))))
    for k, ids in (("farming", ("cultivation", "herding")), ("metal", ("copper",)), ("writing", ("writing",)),
                   ("cities", ("cities",))):
        got = [(max(tt["known"][l["id"]][i][0] for i in ids if i in tt["known"][l["id"]]), l["id"]) for l in alive
               if any(i in tt["known"][l["id"]] for i in ids)]
        own = sum(1 for l in alive for i in ids[:1] if (tt["known"][l["id"]].get(i) or [0, ""])[1] in ("invented", "tamed"))
        out.append(f"  {k}: {len(got)} of {len(alive)} peoples, {own} found it themselves; first "
                   + (", ".join(f"{lid} {a:g} kyr" for a, lid in sorted(got, reverse=True)[:4]) if got else "none"))
    return out


def anchor_check(tids, seeds: int = 41, T: dict | None = None, peers: int | None = None) -> dict:
    """The soft anchor's check: for each tech, a world of `peers` (anchor_peers) isolated anchor peoples (anchor_pop at
    anchor_dens, a human generation, no culture) that know what Earth knew when the tech's prerequisites came; the median wait
    (kyr) of the FIRST of them to find the tech over `seeds` builds, against Earth's lag (anchor_lag). {tech: (median lag,
    Earth lag, share of draws in which one got it)}."""
    T = T or load()
    D = T["defaults"]
    n = int(peers or D["anchor_peers"])
    out = {}
    for tid in tids:
        ready = _anchor_ready(T, tid)
        after = {i for i in T["techs"] if tid in closure(T, [i])}  # (the tech and everything that needs it)
        kit = [i for i, u in T["techs"].items() if u.get("earliest_kyr") is not None and u["earliest_kyr"] >= ready
               and i not in after and u.get("mode") != "fantasy"]
        ids = [f"anchor{k}" for k in range(n)]
        T2 = {**T, "kind": [{"of": ids, "kit": kit}]}
        area = D["anchor_pop"] / D["anchor_dens"] / 1e6
        lines = [{"id": i, "origin": "root", "ago_kyr": ready, "started_kyr": ready, "ended_kyr": None, "parents": [],
                  "group_of": None, "overlay": False, "demography": {"insularity": 0.5}, "generation_yr": GENERATION_REF_YR,
                  "track": [[ready, 0, 0, area, D["anchor_pop"]], [0.0, 0, 0, area, D["anchor_pop"]]]} for i in ids]
        waits = []
        for s in range(seeds):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tt = build(lines, None, None, seed=s, T=T2, era=None)
            got = [ready - v[0] for i in ids for v in [tt["known"][i].get(tid)] if v and v[1] == "invented"]
            waits.append(min(got) if got else math.inf)
        got = [w for w in waits if math.isfinite(w)]
        out[tid] = (float(np.median(waits)), anchor_lag(T, tid), len(got) / seeds)
    return out


def rebuild(run_dir: Path, gods_mode: str | None = None, T: dict | None = None, arms: str | None = None,
            seed: int | None = None) -> dict:
    """The tech tree of a stored peoples run, built afresh in memory (nothing written): today's tree file, the run's saved lines.
    T, arms: a tree and D52's arms to try; the town footprint is read from the run's settlement ledger when an arm needs it.
    seed: another draw of the tree's luck over the same history (default: the run's own)."""
    from . import land as LD
    run = json.loads((Path(run_dir) / "run.json").read_text())
    m = run["meta"]
    pp = m.get("presence_present")
    present = None
    if pp:
        present = np.frombuffer((Path(run_dir) / pp["file"]).read_bytes(), np.uint8).reshape(pp["shape"]) / 100.0
    goods = LD.goods(m.get("world")) if m.get("world") else None
    lines = with_generations(m["lineages"], m.get("tree"))
    D = (T or load())["defaults"]
    towns = None
    if set(str(_arm(D, "contact_arms") if arms is None else arms)) & TOWN_ARMS and m.get("settlements"):
        from .techspread import town_footprint
        towns = town_footprint(run_dir)
    return build(lines, m.get("contacts"), m.get("present"), present, goods, m.get("mode", "fantasy"),
                 m.get("era"), int(m.get("try_seed") or 0) if seed is None else seed, T=T, gods_mode=gods_mode or m.get("gods_mode", "faith_made"),
                 towns=towns, arms=arms, landmass=landmass_of(run_dir, m))


def landmass_of(run_dir: Path, m: dict) -> np.ndarray | None:
    """Each cell's present-day landmass of a stored run (demes.landmass_rank on its last frame: Crossings' ranks), for rebuild."""
    from .. import timeline as TL
    from ..geo import is_land
    from ..grid import shared_grid
    from .demes import landmass_rank
    try:
        run, arr = TL.load_frames(Path(run_dir), ("elevation", "ice"))
    except (KeyError, FileNotFoundError):
        return None
    j = len(run["frames"]) - 1
    return landmass_rank(shared_grid(m["level"]), is_land(TL.frame(run, arr, "elevation", j), TL.frame(run, arr, "ice", j)))


def for_run(run_dir: Path) -> dict:
    """Builds (or rebuilds) meta.techtree of a stored peoples run in place; returns it."""
    from .. import store as S
    tt = rebuild(run_dir)
    S.update_meta(run_dir, lambda r: r["meta"].__setitem__("techtree", tt))  # (re-read under the lock, PW-1040)
    return tt
