"""The technology tree, a first pass (PW-675 prototype): which people knew what, and since when.

The tree is data (samples/techtree.toml): tracks, techs with prerequisites, land the tech needs (land.GOODS), a real-world
earliest date (sources in the file) and a rate. It is read after a peoples history has run, from what the history saved
(the lines with their start and end, the contact record, the first tamings of crops and animals, each people's present
range and the world's goods), so it can be built in output.save and again for a stored run (`planet techtree RUN`).

Rules, all seeded and simple:
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
DEPOSITS = ("metal", "gold", "iron", "copper", "tin", "gems", "mithril", "coal", "salt", "salt_rock", "stone", "volcanic")


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


def build(lines: list[dict], contacts: dict | None, pres: dict | None, present: np.ndarray | None = None,
          goods: dict | None = None, mode: str = "fantasy", era: str | None = "renaissance", seed: int = 0,
          T: dict | None = None, gods_mode: str = "faith_made") -> dict:
    """meta.techtree for a peoples run. gods_mode (PW-1304): "faith_made" (default), "belief_only" or "absolute"; a tech marked
    `gods = true` (divine magic) exists only in faith_made and absolute. `lines` as in meta.lineages (id, origin, parents, group_of, overlay, started_kyr,
    ended_kyr, demography, traits), `contacts` as meta.contacts, `pres` as meta.present (crops and animals: the tamings,
    lines: the populations), `present` the presence per line (lines x cells, 0..1) and `goods` the world's goods."""
    T = T or load()
    D = T["defaults"]
    cap = ERAS.index(era) if era in ERAS else len(ERAS) - 1
    techs = {i: t for i, t in T["techs"].items() if ERAS.index(t.get("era", "stone age")) <= cap
             and (mode != "real" or t.get("mode") != "fantasy") and (gods_mode != "belief_only" or not t.get("gods"))}
    order = [i for i in T["order"] if i in techs]
    rng = np.random.default_rng((seed, 675))
    L = {l["id"]: l for l in lines}
    people = [l for l in lines if not (l.get("overlay") and l.get("origin") == "template")]
    idx = {l["id"]: l.get("index", k) for k, l in enumerate(lines)}
    unmatched = [" | ".join(k["of"]) for k in T.get("kind", []) if not set(k["of"]) & set(L)]
    if unmatched:  # (a rule none of whose ids is a line of this tree applies to nothing, PW-1041)
        warnings.warn(f"tech tree [[kind]] rules name no line of this tree: {', '.join(unmatched)}", stacklevel=2)
    kind = {l["id"]: _kind(T, l, L) for l in people}
    node = {l["id"]: _node(l, L) for l in people}  # (PW-971: the sapiens node, kyr, of the line's stem; None: no stem node above it)
    have = {l["id"]: goods_held(T, present, goods, idx[l["id"]]) for l in people}
    pops = ((pres or {}).get("lines") or {})
    series = {l["id"]: _series(l, pops) for l in people}  # (population and density through time, from the saved tracks)
    gens = {l["id"]: _gen(l, L) for l in people}
    learn = {lid: learners_x(g, D) for lid, g in gens.items()}
    culture = {l["id"]: culture_of(T, l) for l in people}
    rates = {i: rate_of(T, i) for i in techs}
    pool = {i: pool_of(techs[i]) for i in techs}
    ready: dict[str, dict[str, float]] = {l["id"]: {} for l in people}  # (when each people first met a tech's conditions: the ramp)
    start = {l["id"]: float(l.get("started_kyr") if l.get("started_kyr") is not None else l.get("ago_kyr", 0.0)) for l in people}
    end = {l["id"]: float(l["ended_kyr"]) if l.get("ended_kyr") is not None else -1.0 for l in people}
    # forced knowledge: the first tamings of the history (crops.py, animals.py)
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
    # contacts as intervals: (a, b, from kyr, to kyr, border km)
    links = []
    for p in (contacts or {}).get("pairs", []):
        if p["a"] in kind and p["b"] in kind:
            ser = p.get("series") or []
            to = 0.0 if p.get("in_contact_now") else (min(q[0] for q in ser) if ser else p["first_contact_kyr"])
            km = float(np.median([q[1] for q in ser])) if ser else float(p.get("border_km_peak", 0))
            links.append((p["a"], p["b"], float(p["first_contact_kyr"]), to, km))
    t0 = max(start.values(), default=1.0)
    grid = np.concatenate([np.geomspace(max(t0, 1.0), NEAR_KYR, STEPS), [0.0]])
    known: dict[str, dict[str, list]] = {l["id"]: {} for l in people}

    def give(lid, tid, ago, how, frm=None):
        if tid in techs and tid not in known[lid]:
            known[lid][tid] = [round(float(ago), 3), how, frm]

    def held(lid, tid, at):  # (PW-987: a line cannot inherit a tool it cannot hold: the cats take no found tools from the mammal root)
        t = techs[tid]
        return not t.get("hands", True) or _grips(t, kind[lid], node[lid], at)

    def can(lid, tid, ago, inventing, needs=True):
        t = techs[tid]
        k = kind[lid]
        if tid in known[lid] or (needs and any(n not in known[lid] for n in t.get("needs", []))):
            return False
        if needs and t.get("needs_any") and not any(n in known[lid] for n in t["needs_any"]):  # (one of them: a mount, a milk beast)
            return False
        if node[lid] is not None and ago > node[lid] and not t.get("bare"):  # (PW-971: before its stem's minds only bare-bones tools)
            return False
        if t.get("hands", True) and not _grips(t, k, node[lid], ago):
            return False
        if (inventing or not t.get("traded")) and not _env_ok(t, have[lid]):  # (a traded tech, bronze, comes without the ore)
            return False
        if inventing:
            first = floor_of(T, tid, bool(k.get("elder")))  # (a gated tech's floor; a soft tech has none)
            return first is None or ago <= first
        return True

    def strengths(lid, ago):
        """(S of the whole people, S of its specialists, s) now."""
        ser = series[lid]
        n, dens = _at(ser, ago) if ser is not None else (D["pool_default"], None)
        n *= learn[lid]
        s = specialist_share(T, known[lid])
        return strength(n, D), strength(n * s * density_x(dens, D), D), s

    began = set()
    arrive: dict[tuple, float | None] = {}  # ((giver, taker, tech): when its front reaches the taker's middle, kyr; None: never)
    unit: dict[tuple, float] = {}  # ((giver, taker): the pair's front delay, in units of 1 / the contact rate)
    prev = grid[0]
    for ago in grid:
        dt = max(prev - ago, 1e-6) if ago != grid[0] else 0.0
        prev = ago
        alive = [l for l in people if start[l["id"]] >= ago and (end[l["id"]] < 0 or ago > end[l["id"]])]
        for l in alive:  # (inheritance and kits, once, at the line's start)
            lid = l["id"]
            if lid in began:
                continue
            began.add(lid)
            at = min(start[lid], grid[0])
            if l.get("origin") in ("split", "group") or l.get("group_of"):
                src = l.get("group_of") or (l.get("parents") or [None])[0]
                for tid, v in (known.get(src) or {}).items():
                    if v[0] >= at - 1e-9 and not (node[lid] is not None and at > node[lid] and not techs[tid].get("bare")) and held(lid, tid, at):  # (PW-971: a stem under a node inherits only bare tools from before it)
                        give(lid, tid, at, "inherited", src)
            elif l.get("origin") == "hybrid":
                for src in l.get("parents") or []:
                    for tid in list((known.get(src) or {})):
                        if not (node[lid] is not None and at > node[lid] and not techs[tid].get("bare")) and held(lid, tid, at):
                            give(lid, tid, at, "inherited", src)
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
        for a, b, fr, to, km in links:  # (diffusion over borders)
            if not (fr >= ago >= to):
                continue
            w = min(km / D["contact_full_km"], 1.0)
            for x, y in ((a, b), (b, a)):
                if x not in began or y not in began:
                    continue
                cr = None
                for tid in order:
                    if tid not in known[x] or tid in known[y] or known[x][tid][0] < ago:
                        continue
                    k3 = (x, y, tid)
                    if k3 not in arrive:
                        if techs[tid].get("modern_contact") and node[y] is None:  # (language: to any genetically modern people, PW-971)
                            arrive[k3] = None
                            continue
                        if cr is None:
                            op = 1 - 0.7 * float((L[y].get("demography") or {}).get("insularity", 0.3))
                            cr = contact_rate(_area_at(series[y], ago), D) * w * op
                        r = cr * techs[tid].get("spread", D["spread"]) * domain_x(culture[y][1], techs[tid])
                        if (x, y) not in unit:  # (the pair's draw: one front, for all its techs, slower for a slow-spreading one)
                            unit[(x, y)] = float(rng.exponential(1.0))
                        arrive[k3] = min(known[x][tid][0], fr) - unit[(x, y)] / r if r > 0 else None
                    at = arrive[k3]
                    if at is not None and at >= ago and at > cand.get((y, tid), (-1.0,))[0]:
                        cand[(y, tid)] = (at, x)
        # inventing, and the arrivals: a tech that arrives within the step may still be invented first, over the part of the step
        # before it arrived (neither is tried first)
        for l in alive:
            lid = l["id"]
            rx = kind[lid].get("rate_x", 1.0)
            s_all, s_spec, _ = strengths(lid, ago)
            for tid in order:
                arr = cand.get((lid, tid))
                lang = bool(techs[tid].get("modern_contact"))
                took = arr is not None and can(lid, tid, ago, False, needs=not lang)
                h = 0.0
                if can(lid, tid, ago, True):
                    t = techs[tid]
                    sp = 1.0 if pool[tid] == "none" else s_spec if pool[tid] == "specialists" else s_all
                    h = rates[tid] * rx * domain_x(culture[lid][0], t) * sp
                    tau = ready[lid].setdefault(tid, ago) - ago
                    h *= 1 - math.exp(-h * (tau + 0.5 * dt))  # (the ramp, at the middle of the step)
                span = min(max(ago + dt - arr[0], 0.0), dt) if took else dt
                if h > 0 and span > 0 and rng.random() < 1 - math.exp(-h * span):
                    give(lid, tid, ago, "invented", None)
                elif took:
                    if lang:
                        for n in [i for i in order if i in closure(T, [tid]) and i != tid]:
                            give(lid, n, ago, "with " + tid, arr[1])  # (its roots, gesture, come with it)
                    give(lid, tid, ago, "contact", arr[1])
        for l in alive:  # (a group and its people share what they know as they go)
            g = l.get("group_of")
            if g and g in known:
                for x, y in ((g, l["id"]), (l["id"], g)):
                    for tid, v in list(known[x].items()):
                        if v[0] >= ago and tid not in known[y] and can(y, tid, ago, False):
                            give(y, tid, ago, "shared", x)
    firsts = firsts_of(known)
    drivers = {}  # (what drove each living people's inventing at the present: for the report and the viewer)
    for l in people:
        lid = l["id"]
        if end[lid] >= 0:
            continue
        s_all, s_spec, s = strengths(lid, 0.0)
        ser = series[lid]
        drivers[lid] = {"population": int(_at(ser, 0.0)[0]) if ser is not None else None, "specialists": s,
                        "strength_all": round(s_all, 3), "strength_specialists": round(s_spec, 3),
                        "generation_yr": gens[lid], "learners_x": round(learn[lid], 2), "rate_x": kind[lid].get("rate_x", 1.0),
                        "culture": {d: round(x, 2) for d, x in culture[lid][0].items()},
                        "take": {d: round(x, 2) for d, x in culture[lid][1].items()}}
    return {"file": str(T.get("_file", FILE.name)), "era": era, "mode": mode, "gods_mode": gods_mode,
            "tracks": [{"id": k["id"], "name": k["name"]} for k in T["track"]],
            "techs": [{"id": i, "name": techs[i]["name"], "track": techs[i]["track"], "needs": techs[i].get("needs", []),
                       "needs_any": [n for n in techs[i].get("needs_any", []) if n in techs],
                       "env": techs[i].get("env", []), "env_any": techs[i].get("env_any", []),
                       "earliest_kyr": techs[i].get("earliest_kyr"), "elder_kyr": techs[i].get("elder_kyr"),
                       "era": techs[i].get("era", "stone age"), "fantasy": techs[i].get("mode") == "fantasy",
                       "source": techs[i].get("source", ""), "domains": domains_of(techs[i]), "pool": pool[i],
                       "floor_kyr": floor_of(T, i), "rate": round(rates[i], 4),
                       "anchor_lag_kyr": None if floor_of(T, i) is not None else anchor_lag(T, i)} for i in order],
            "known": known, "firsts": firsts, "drivers": drivers,
            "goods_checked": {lid: sorted(v) if v is not None else None for lid, v in have.items()}}


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


def rebuild(run_dir: Path, gods_mode: str | None = None) -> dict:
    """The tech tree of a stored peoples run, built afresh in memory (nothing written): today's tree file, the run's saved lines."""
    from . import land as LD
    run = json.loads((Path(run_dir) / "run.json").read_text())
    m = run["meta"]
    pp = m.get("presence_present")
    present = None
    if pp:
        present = np.frombuffer((Path(run_dir) / pp["file"]).read_bytes(), np.uint8).reshape(pp["shape"]) / 100.0
    goods = LD.goods(m.get("world")) if m.get("world") else None
    lines = with_generations(m["lineages"], m.get("tree"))
    return build(lines, m.get("contacts"), m.get("present"), present, goods, m.get("mode", "fantasy"),
                 m.get("era"), int(m.get("try_seed") or 0), gods_mode=gods_mode or m.get("gods_mode", "faith_made"))


def for_run(run_dir: Path) -> dict:
    """Builds (or rebuilds) meta.techtree of a stored peoples run in place; returns it."""
    from .. import store as S
    tt = rebuild(run_dir)
    S.update_meta(run_dir, lambda r: r["meta"].__setitem__("techtree", tt))  # (re-read under the lock, PW-1040)
    return tt
