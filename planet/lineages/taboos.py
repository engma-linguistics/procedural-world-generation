"""Food taboos per culture, as a readout (PW-1305, religion epic PW-1308). Output only, like cultures.py: reads cultures.json, the run's meta
(animals, crops, reputation, seed), the tech tree's `known` and, for the divine origin, gods.json. Writes `taboos.json`.

A taboo is {target, scope, origin, why}; the explanation, the consequence and the enforcement are the writer's, not computed (the doc, section 6).
- target: a domesticate the culture keeps (animal_defs ids, crop_defs ids) or a wild kind of ITEMS below, whole (parts and seasons are not modelled).
- scope: everyone | priests | a lineage (pregnant women and the like are the writer's to add).
- origin, the five the doc names:
  practical  seasonal poison or parasites: NOT modelled (the sim has neither), so none is emitted;
  symbolic   (the doc's "totem"): a domesticate the culture relies on, held sacred or kin to a lineage (a seeded draw, TOTEM_P per culture);
  identity   the staple of a people this culture fears or despises (meta.present.reputation), refused;
  divine     the domain of one of the culture's gods (gods.json): an herd god's herd animal, a sea god's sea beasts, ...; priests only below
             SPELL_IND individuation, everyone above it;
  purity     Douglas 1966 (Purity and Danger, on Leviticus 11): kinds that straddle the culture's own categories are "unclean". ITEMS carries
             each kind's straddles (JUDGEMENT: my reading of that scheme, not a table out of the book). The number of rules is PURITY_MAX x the
             culture's purity weight. That weight is the moral ledger's (PW-1307), which waits on Daniel; until then it is a seeded placeholder
             in PURITY_RANGE per culture, marked as such in the output.
Seeded per (run seed, culture): the same run gives the same taboos.

Beyond food (PW-1311): every other kind of taboo in taboo_defs.KINDS (totemic, purity and the dead, speech and names, kinship and
marriage, birth, women, sacred places, sacred times, hunting and harvest, chiefly, sumptuary, caste), drawn per culture from its tags
(context(): its way of life, its techs, its gods' domains) by other_taboos(), with their own random stream so the food taboos are as
before. Each taboo has a `kind`; the food ones are kind "food" with their origin as before. Still a readout.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from . import taboo_defs as TD

TOTEM_P = 0.12  # JUDGEMENT: the share of cultures with a sacred domesticate
PURITY_RANGE = (0.1, 0.6)  # JUDGEMENT placeholder for the ledger's purity weight (PW-1307)
PURITY_MAX = 4  # the most purity rules a culture with weight 1 holds
IDENTITY_MAX, DIVINE_MAX = 1, 2
SPELL_IND = 0.5  # as gods.SPELL_IND: a god this individuated makes everyone's rule, a lesser one the priests'
# kinds a culture can meet beyond its domesticates: (label, where it lives, what straddles). JUDGEMENT throughout.
ITEMS = {
    "swine": ("wild swine", "land", ["has a split hoof but does not chew the cud"]),
    "hares": ("hares", "land", ["chews like a cud-eater but has no split hoof"]),
    "eels": ("eels", "water", ["lives in the water but has no fins or scales; moves like a snake"]),
    "shellfish": ("shellfish", "water", ["lives in the water but has no fins or scales"]),
    "sea_beasts": ("whales and seals", "water", ["lives in the water but breathes air and suckles its young"]),
    "waterfowl": ("waterfowl", "water", ["a bird that swims"]),
    "bats": ("bats", "land", ["flies but has fur and no feathers"]),
    "carrion_birds": ("carrion birds", "land", ["flies, but feeds on the dead"]),
    "snakes": ("snakes", "land", ["a land animal with no legs"]),
    "frogs": ("frogs and newts", "wet", ["lives both in the water and on the land"]),
    "insects": ("swarming insects", "land", ["flies but goes on many legs"]),
}
# domesticates that straddle (animal_defs ids)
DOMESTIC_STRADDLE = {"dog": ["a land beast that eats flesh and lives in the house"], "riding_lizard": ["scaled, yet walks and carries like a beast"]}
# a god's domain -> the kinds it can make forbidden: ("herd",) = the culture's top herd animal, ("crop",) = its top crop
DIVINE = {"herd": ("herd",), "harvest": ("crop",), "sea": ("sea_beasts", "shellfish"), "river": ("eels",), "storm": ("waterfowl",), "sky": ("waterfowl",),
          "death": ("carrion_birds",), "hunt": ("swine",)}
HERD = ("cattle", "caprine", "horse", "great_elk", "buffalo", "yak", "camel", "reindeer", "llama", "pig")  # (in order of preference: the first kept is "the herd"; PW-835 rows after the old ones)
BAD = ("feared", "despised", "resented")


def _label(t: str) -> str:
    if t in ITEMS:
        return ITEMS[t][0]
    try:
        from . import animal_defs as AD
        if t in AD.BY_ID:
            return AD.BY_ID[t].label
        from . import crop_defs as CD
        return CD.BY_ID[t].label
    except (ImportError, KeyError, AttributeError):
        return t


def available(people: dict, country: str | None) -> set:
    """The wild kinds a culture meets: sea kinds on a coast (a coastal, swimming or sea-craft people), frogs in wet country, the rest anywhere."""
    tr = set(people.get("traits") or [])
    coastal = bool(tr & {"coastal", "swims", "seafaring"})
    wet = (country or "") in ("tropical wet", "temperate", "continental")
    return {k for k, (_, home, _) in ITEMS.items() if (home != "water" or coastal) and (home != "wet" or wet)}


def culture_taboos(rng: np.random.Generator, *, domestic: list, crops: list, wild: set, enemies: dict, beings: list, purity: float) -> list:
    """The taboos of one culture. domestic/crops: ids it keeps; wild: kinds it meets; enemies: {people: its staple animals/crops}
    of the peoples it fears or despises; beings: [{"domains": [...], "ind": x}] its living gods; purity: its weight 0..1."""
    out: list = []
    taken: set = set()

    def add(target, scope, origin, why, **kw):
        if target in taken:
            return
        taken.add(target)
        out.append({"kind": "food", "target": target, "label": _label(target), "scope": scope, "origin": origin, "why": why, **kw})

    # symbolic: a domesticate held sacred (a lineage's kin)
    keep = [d for d in domestic if d != "dog"]
    if keep and rng.random() < TOTEM_P:
        t = keep[int(rng.integers(len(keep)))]
        add(t, "a lineage", "symbolic", f"the {_label(t)} the culture relies on is kin to one of its lineages")
    # identity: a neighbour's staple, refused
    n = 0
    for people, staples in sorted(enemies.items()):
        for s in staples:
            if s["id"] not in domestic and s["id"] not in crops and n < IDENTITY_MAX:
                add(s["id"], "everyone", "identity", f"the staple of the {people}, whom the culture {s['valence']}", subject=people)
                n += 1
                break
    # divine: the domain of one of its gods
    n = 0
    for b in sorted(beings, key=lambda b: -b["ind"]):
        for d in b["domains"]:
            for kind in DIVINE.get(d, ()):
                t = (next((h for h in HERD if h in domestic), None) if kind == "herd" else crops[0] if kind == "crop" and crops else
                     kind if kind in wild else None)
                if t and t not in taken and n < DIVINE_MAX:
                    add(t, "everyone" if b["ind"] >= SPELL_IND else "priests", "divine",
                        f"it belongs to the {d} domain of {b['label']}", god=b["id"])
                    n += 1
    # purity (Douglas 1966): kinds that straddle its categories; never what it keeps and eats
    cand = {k: ITEMS[k][2] for k in wild} | {k: DOMESTIC_STRADDLE[k] for k in domestic if k in DOMESTIC_STRADDLE and k == "dog"}
    cand = {k: v for k, v in cand.items() if k not in taken}
    n = min(len(cand), int(round(PURITY_MAX * purity)))
    keys = sorted(cand)
    w = np.array([len(cand[k]) for k in keys], float)
    for i in (rng.choice(len(keys), n, replace=False, p=w / w.sum()) if n else []):
        k = keys[int(i)]
        add(k, "everyone", "purity", "unclean: " + cand[k][0], straddles=cand[k])
    return out


METAL = ("copper", "native_copper", "bronze", "iron")


def context(know: set, traits: set, beings: list) -> set:
    """A culture's tags for the catalogue (taboo_defs): ways (farm, herd, forage, hunt, sea), techs, its living gods' leading domains."""
    t = set()
    t |= {"farm"} if "cultivation" in know else set()
    t |= {"herd"} if "herding" in know else set()
    if not t:
        t.add("forage")
    if "farm" not in t:
        t.add("hunt")
    if traits & {"coastal", "swims", "seafaring"}:
        t.add("sea")
    t |= {k for k in ("burial", "temples", "kingship", "writing") if k in know}
    if "moralizing_high_god" in know:
        t.add("high_god")
    if any(m in know for m in METAL):
        t.add("metal")
    for b in beings:
        t |= {"g:" + d for d in b["domains"]}
        if b.get("spells"):
            t.add("spells")
    return t


def _span(rng: np.random.Generator, tags: set) -> str | None:
    """A post-partum taboo length drawn from EA036's counts, the long ones tilted by the way of life (Saucier 1972, summary)."""
    long_x = TD.LONG_FARM if "farm" in tags and "kingship" not in tags else TD.LONG_OTHER
    names = [n for n, _ in TD.POSTPARTUM_EA036]
    w = np.array([c * (long_x if n in ("one to two years", "more than two years") else 1.0) for n, c in TD.POSTPARTUM_EA036], float)
    k = names[int(rng.choice(len(names), p=w / w.sum()))]
    return None if k == "none" else k


def other_taboos(rng: np.random.Generator, tags: set) -> list:
    """The taboos of one culture beyond food, from its tags: each kind is held with its chance (taboo_defs.KINDS, x KIND_BOOST per tag),
    then 1..max of its rules whose needs the culture meets, weighted by their boosts."""
    out = []
    for kind, (name, _, _, base, most) in TD.KINDS.items():
        if kind == "food":
            continue
        need = TD.KIND_NEEDS.get(kind)
        if need and need not in tags:
            continue
        p = base
        for tg, x in TD.KIND_BOOST.get(kind, {}).items():
            if tg in tags:
                p *= x
        if rng.random() >= min(p, 0.97 if kind not in ("kinship", "postpartum") else 1.0):
            continue
        rules = [r for r in TD.RULES if r[1] == kind and all(n in tags for n in r[4])]
        if kind == "kinship":  # (the nuclear-family rule everywhere; clan exogamy at EA015's share; the rest drawn)
            pick = [TD.RULE["incest_core"]] + ([TD.RULE["clan_exogamy"]] if rng.random() < TD.EXOGAMY_P and "kingship" not in tags else [])
            rules = [r for r in rules if r[0] not in ("incest_core", "clan_exogamy")]
            n = int(rng.integers(0, most - len(pick) + 1)) if most > len(pick) else 0
        else:
            pick, n = [], 1 + int(rng.binomial(most - 1, 0.4)) if most > 1 else 1
        if rules and n:
            w = np.array([np.prod([x for tg, x in r[5].items() if tg in tags] or [1.0]) for r in rules], float)
            pick += [rules[int(i)] for i in rng.choice(len(rules), min(n, len(rules)), replace=False, p=w / w.sum())]
        for rid, _, text, who, needs, boost, src in pick:
            if rid == "postpartum":
                span = _span(rng, tags)
                if span is None:
                    continue
                text = text.format(span=span)
            why = [t for t in (*needs, *boost) if t in tags]
            out.append({"kind": kind, "target": rid, "label": text, "scope": who, "origin": kind,
                        "why": f"{name}; drawn from: {', '.join(why) if why else 'any culture'}", "source": src})
    return out


def derive(run_dir: Path, gods: dict | None = None, techtree: dict | None = None) -> dict:
    """taboos.json of a stored peoples run that has cultures (read-only). gods: its gods.json document (the divine origin), if any."""
    t0 = time.time()
    run_dir = Path(run_dir)
    run = json.loads((run_dir / "run.json").read_text())
    m = run["meta"]
    doc = json.loads((run_dir / m["cultures"]["file"]).read_text())
    known = (techtree or m.get("techtree") or {}).get("known") or {}
    pres = m.get("present") or {}
    stocks = {"animals": ((pres.get("animals") or {}).get("stocks") or {}), "crops": ((pres.get("crops") or {}).get("stocks") or {})}
    lines = {l["id"]: l for l in m["lineages"]}
    rep = ((pres.get("reputation") or {}).get("rows")) or {}
    seed = int(m.get("seed") or 0)

    def kept(people, key, prefix):
        k = known.get(people) or {}
        return [sid for sid, s in stocks[key].items() if s.get("enabled", True) and f"{prefix}_{sid}" in k]

    def staples(subject):  # (the animals and crops a people tamed or took up, earliest first)
        out = []
        for key in ("animals", "crops"):
            for sid, s in stocks[key].items():
                ago = [t["ago_kyr"] for t in s.get("tamed") or [] if t["line"] == subject] + [a for l, a in (s.get("took_up_kyr") or {}).items() if l == subject and a is not None]
                if ago and not (key == "animals" and sid == "dog"):
                    out.append((max(ago), sid))
        return [{"id": sid} for _, sid in sorted(out, reverse=True)[:2]]

    by_god: dict = {}
    for b in (gods or {}).get("beings", []):
        if b["status"] == "living":
            by_god.setdefault(b["culture"], []).append({"id": b["id"], "label": b["label"], "ind": b["individuation"],
                                                        "domains": [t[0] for t in b["top"][:2]], "spells": b.get("grants_spells")})
    out = {}
    for c in doc["cultures"]:
        if c["end"] is not None:
            continue
        rng = np.random.default_rng((seed, c["id"], 1305))
        pur = float(rng.uniform(*PURITY_RANGE))
        en = {}
        for subj, r in (rep.get(c["people"]) or {}).items():
            if r.get("valence") in BAD and subj in lines:
                st = staples(subj)
                if st:
                    en[lines[subj].get("name", subj)] = [{**s, "valence": r["valence"]} for s in st]
        tb = culture_taboos(rng, domestic=kept(c["people"], "animals", "animal"), crops=kept(c["people"], "crops", "crop"),
                            wild=available(lines.get(c["people"]) or {}, c.get("country_now")), enemies=en,
                            beings=by_god.get(c["id"], []), purity=pur)
        kn = set(known.get(c["people"]) or {})
        tags = context(kn, set((lines.get(c["people"]) or {}).get("traits") or []), by_god.get(c["id"], []))
        tb += other_taboos(np.random.default_rng((seed, c["id"], 1311)), tags)
        out[str(c["id"])] = {"name": c["name"], "people": c["people"], "purity_weight": round(pur, 3), "purity_weight_is": "placeholder (PW-1307)",
                             "tags": sorted(tags), "taboos": tb}
    return {"format": "procgen-taboos/2", "cultures": out,
            "kinds": {k: {"name": v[0], "what": v[1], "sources": list(v[2])} for k, v in TD.KINDS.items()},
            "sources": {k: {"title": v[0], "url": v[1], "level": v[2]} for k, v in TD.SOURCES.items()},
            "summary": {"cultures": len(out), "with_taboos": sum(bool(v["taboos"]) for v in out.values()),
                        "by_origin": {o: sum(t["kind"] == "food" and t["origin"] == o for v in out.values() for t in v["taboos"])
                                      for o in ("symbolic", "identity", "divine", "purity", "practical")},
                        "by_kind": {k: sum(t["kind"] == k for v in out.values() for t in v["taboos"]) for k in TD.KINDS},
                        "generated_in_s": round(time.time() - t0, 1)}}


def write(run_dir: Path, out_dir: Path | None = None, gods: dict | None = None, techtree: dict | None = None) -> dict:
    from .. import store as S
    d = derive(Path(run_dir), gods, techtree)
    dest = Path(out_dir) if out_dir else Path(run_dir)
    dest.mkdir(parents=True, exist_ok=True)
    S.write_atomic(dest / "taboos.json", json.dumps(d, separators=(",", ":")))
    return d["summary"]


def write_religion(run_dir: Path, out_dir: Path | None = None, mode: str = "faith_made", techtree: dict | None = None, rebuild: bool = False) -> dict:
    """The religion readouts of a run, gods.json then taboos.json (which reads the gods), into the run or out_dir; returns both summaries."""
    from . import gods as GD
    if rebuild and techtree is None:
        from . import techtree as TT
        techtree = TT.rebuild(Path(run_dir))
    gd = GD.derive(Path(run_dir), mode, techtree)
    dest = Path(out_dir) if out_dir else Path(run_dir)
    dest.mkdir(parents=True, exist_ok=True)
    from .. import store as S
    S.write_atomic(dest / "gods.json", json.dumps(gd, separators=(",", ":")))
    return {"gods": gd["summary"], "faiths": gd["summary"].get("faiths"), "taboos": write(run_dir, out_dir, gd, techtree)}
