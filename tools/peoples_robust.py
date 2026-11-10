"""Peoples robustness suite (lane 77): does the peoples history hold up when the tree changes?

    uv run python tools/peoples_robust.py plan                       # list the variants (no runs)
    uv run python tools/peoples_robust.py run --out DIR [--jobs 4 --threads 4 --max-load 60] [--family base,jitter,...]
    uv run python tools/peoples_robust.py run --out DIR2 --arms now --trees dnd,even_six --seeds 7 --params '{"FIT_CLIP": 2}' --tag clip2
    uv run python tools/peoples_robust.py report --out DIR           # tables from the runs in DIR (report.md, summary.json)
    uv run python tools/peoples_robust.py one SPEC.json OUT.json     # one variant (the runner's worker)

One try (no best-of-N) of each variant tree on each world, nothing saved under runs/ (the worker keeps only the numbers).
Variant families, cut from the stock trees (planet/lineages/samples):
  base    dnd and seven_meals at several seeds
  jitter  every split and arrival date x a seeded factor in 0.5-2 (log-uniform), parents kept older than their children
  subset  a 5-people and a 3-people tree cut from dnd (enabled = false on the rest, stems kept), and dnd plus an authored people
  knob    three peoples (a mainline one, a minor one, a late arrival) at kind factor x0.5 and x2 (PW-1275) against the base at the same seed
  portal  dnd with portal_mode = sites (1 and 3 portals) against off
  authored  the trees under tools/peoples_robust/trees/ (edits of a sample; each says why it exists; all_at_once is information only)
Arms (ARMS): params overrides each variant runs under; now is the model as it stands, nofit the contest without its fit weight (lane 83;
the first arm runs every family, the others base, dnd's jitter, subset and authored). --params adds overrides of your own to every variant.

Per run, per people (a people with its groups rolled up; megafauna and overlays apart): its share of all people, its share of the
peopled cells it leads (the most people there), its range, and whether it lives; a people that dies out is named with why (its
events). The invariants (report): no crash; no authored people silently extinct; no people above MONO_MAX of all people unless the
tree has <= 2; shares move with each people's own kind factor. The spread: each people's share over the base, jitter and portal
runs; a people whose share swings more than SWING x between the seeds, or the jitters, of one world is a brittle point (PW-1207: the
pooled swing, also reported, mixes the two worlds' geography).

How to judge a peoples change: docs/coordination.md ("How to judge a peoples change").
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import planet  # noqa: E402,F401  (thread defaults before numpy)

import argparse
import copy
import json
import math
import os
import subprocess
import sys
import time
import tomllib
import traceback
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "planet" / "lineages" / "samples"
WORLDS = ["4360a3", "af2677"]  # the L6 worlds with their time zooms on disk (2026-10-30)
MONO_MAX = 0.85  # no people above this share of all people (trees of 3+ peoples)
D31_USUAL, D31_NEVER, D31_MANY = 0.5, 0.7, 5  # owner D31 A: the commonest people usually under half, never over 70% with 5+ peoples (reported)
SWING = 10.0  # a people whose share swings more than this x across the seeds, or the jitters, on one world is brittle (PW-1207)
SHARE_FLOOR = 1e-4  # (shares under this count as this in the swing ratio: an extinct people is reported apart)
KNOB_PEOPLES = {"dwarf": "mainline", "bugbear": "minor", "gnome": "late arrival"}
KNOB_X = (0.5, 2.0)
BLOC_MIN_MKM2 = 1.0  # a landmass counts as a bloc's land from this size (the continents and the large islands; at L6 ~80 cells)


# ---------------------------------------------------------------- variants

def _load(name: str) -> dict:
    with open(SAMPLES / f"{name}.toml", "rb") as f:
        return tomllib.load(f)


def _ago(v) -> float:
    from planet.lineages import spec as SP
    return SP.parse_ago(v)


def _when_key(r: dict) -> str | None:
    return next((k for k in ("at", "split", "appears", "arrives", "ago") if k in r), None)


def _kyr(x: float) -> str:
    return f"{x:.6g} kyr"


def jitter(raw: dict, rng: np.random.Generator, lo: float = 0.5, hi: float = 2.0) -> dict:
    """Every split and arrival date x a log-uniform factor in lo..hi; a child is kept younger than its parents (at most 0.9 of the
    youngest parent's date), a stem's sapiens node between its kinds and its own start, an extinction after the line appears."""
    raw = copy.deepcopy(raw)
    rows = {r["id"]: r for r in raw["lineage"]}
    old = {lid: _ago(r[_when_key(r)]) if _when_key(r) else None for lid, r in rows.items()}
    new: dict[str, float] = {}

    def pars(r):
        p = r.get("parents") or ([r["parent"]] if r.get("parent") else [])
        if r.get("group_of") and not p:
            p = [r["group_of"]]
        return list(p)

    def date(lid):
        if lid in new:
            return new[lid]
        r = rows[lid]
        ps = pars(r)
        origin = r.get("origin") or ("split" if ps else "root")
        t = old[lid]
        if t is None:  # (a group without a date: the parser's default)
            new[lid] = None
            return None
        if origin in ("split", "arrival"):
            t = t * math.exp(rng.uniform(math.log(lo), math.log(hi)))
        cap = min([date(q) for q in ps if date(q) is not None], default=None)
        if cap is not None and t >= 0.9 * cap:
            t = 0.9 * cap
        new[lid] = t
        return t

    for lid in rows:
        date(lid)
    for lid, r in rows.items():
        k = _when_key(r)
        if k and new[lid] is not None:
            r[k] = _kyr(new[lid])
    for lid, r in rows.items():
        kids = [c for c, rc in rows.items() if lid in pars(rc) and (rc.get("origin") or "split") == "split"]
        if "sapient" in r:
            s = _ago(r["sapient"]) * (new[lid] / old[lid])
            top = max([new[c] for c in kids], default=0.0)
            r["sapient"] = _kyr(min(max(s, top * 1.0001 + 1e-6), new[lid] * 0.999))
        if "extinct" in r and _ago(r["extinct"]) >= 0.9 * new[lid]:
            r["extinct"] = _kyr(0.5 * new[lid])
    return raw


def subset(raw: dict, keep: list[str]) -> dict:
    """The tree with only the peoples in `keep` (with their ancestors, groups, and the hybrids and templates of kept parents): the
    rest switched off (enabled = false)."""
    raw = copy.deepcopy(raw)
    rows = {r["id"]: r for r in raw["lineage"]}
    on: set[str] = set()
    for lid in keep:
        x = lid
        while x and x not in on:
            on.add(x)
            r = rows[x]
            p = r.get("parents") or []
            x = p[0] if p and (r.get("origin") or "split") == "split" else None
    for lid, r in rows.items():
        o = r.get("origin") or ("split" if r.get("parents") else "root")
        if o == "group" and r.get("group_of") in on:
            on.add(lid)
        if o in ("hybrid", "template") and all(q in on for q in r.get("parents", [])):
            on.add(lid)
    for lid, r in rows.items():
        if lid not in on:
            r["enabled"] = False
    return raw


ADDED_PEOPLE = {  # an author's own people, added to dnd: horned hill folk split from the hominids
    "id": "minotaur", "name": "minotaurs (authored)", "parents": ["hominid"], "at": "600 kyr", "explore": 0.5,
    "temp_c": [6, 24], "rain_mm": [350, 1400], "prefers": ["hills", "open"], "traits": ["hardy"],
}


def knob(raw: dict, lid: str, x: float) -> dict:
    raw = copy.deepcopy(raw)
    from planet.lineages import spec as SP
    for r in raw["lineage"]:
        if r["id"] == lid:
            d = r.get("kind")
            if d is None:  # (left out: inherited or 1; PW-1275: the kind factor on the density ladder)
                d = SP.parse(raw).lines[lid].demo("kind")
            r["kind"] = float(min(max(float(d) * x, SP.KIND_RANGE[0]), SP.KIND_RANGE[1]))
    return raw


def with_seed(raw: dict, seed: int, **meta) -> dict:
    raw = copy.deepcopy(raw)
    raw.setdefault("meta", {})["seed"] = int(seed)
    raw["meta"].update(meta)
    return raw


TREES = Path(__file__).resolve().parent / "peoples_robust" / "trees"  # authored alternative trees (edits of a sample, or whole trees)


def all_at_once(raw: dict, when: str) -> dict:
    """Every living people (and megafauna kind) of the tree as a root of its own at one moment: the stems switched off, the leaves
    re-rooted at `when`, an arrival kept an arrival; groups, hybrids and templates as they were; authored extinctions off."""
    raw = copy.deepcopy(raw)
    from planet.lineages import spec as SP
    t = SP.parse(raw)
    leaves = {l.id for l in t.leaves()}
    for r in raw["lineage"]:
        o = r.get("origin") or ("split" if r.get("parents") else "root")
        if o in ("group", "hybrid", "template"):
            continue
        if r["id"] not in leaves or "extinct" in r:
            r["enabled"] = False
            continue
        for k in ("parents", "parent", "sapient", "split", "appears", "arrives", "ago"):
            r.pop(k, None)
        r["origin"] = "arrival" if o == "arrival" else "root"
        r["at"] = when
    return raw


def authored(path: Path) -> tuple[dict, dict]:
    """(the tree, its info) from a file under TREES: a whole tree, or `base` (a sample's name) with `keep` (a subset), `off` (lines
    switched off), [edit.<id>] (fields set; `unset`: keys removed), [[lineage]] (lines added), [meta] (merged), `all_at_once` (a time)."""
    with open(path, "rb") as f:
        d = tomllib.load(f)
    info = {"rationale": d.get("rationale", ""), "info_only": bool(d.get("info_only"))}
    if "base" not in d:
        return d, info
    raw = _load(d["base"])
    if d.get("keep"):
        raw = subset(raw, list(d["keep"]))
    rows = {r["id"]: r for r in raw["lineage"]}
    for lid in d.get("off", []):
        rows[lid]["enabled"] = False
    for lid, e in d.get("edit", {}).items():
        e = dict(e)
        for k in e.pop("unset", []):
            rows[lid].pop(k, None)
        rows[lid].update(e)
    raw["lineage"].extend(copy.deepcopy(d.get("lineage", [])))
    raw.setdefault("meta", {}).update(d.get("meta", {}))
    raw.setdefault("wish", []).extend(d.get("wish", []))
    if d.get("all_at_once"):
        raw = all_at_once(raw, d["all_at_once"])
    return raw, info


# (lane 83: lane 77's founding arms, range / local / local_vacate, went with the SPLIT_FOUNDING switch; one-spot founding is the model now)
ARMS = {"now": {}, "nofit": {"FIT_Q": 0.0, "BREADTH_Q": 0.0}}  # (nofit: the contest without its fit weight, lane 83, params.FIT_Q)
DEFAULT_ARMS = ("now", "nofit")
LOCAL_FAMILIES = {"base", "jitter-dnd", "subset", "authored"}  # (a second arm's share of the suite; the first runs every family)
ONE_SEED = {"menagerie": 7}  # (the scale test: one seed)


def plan(worlds=WORLDS, families=None, arms=DEFAULT_ARMS, seeds=None, trees=None, params=None, tag=None, meta=None) -> list[dict]:
    """The variants, the range arm first (so a cut-short suite still has the whole of today's model). Filters: families, arms, seeds,
    trees (names as in the report: dnd, seven_meals, dnd5, dnd3, dnd+1, or an authored tree's file name); params: overrides added to
    every variant (its name gets ~<tag>), to judge a change without editing the code."""
    dnd, sm = _load("dnd"), _load("seven_meals")
    out = []

    def add(fam, name, raw, world, arm, **info):
        if families and fam not in families or arm not in arms:
            return
        if arm != DEFAULT_ARMS[0] and fam not in LOCAL_FAMILIES and f"{fam}-{info.get('tree')}" not in LOCAL_FAMILIES:
            return
        if seeds and info.get("seed") not in seeds or trees and info.get("tree") not in trees:
            return
        if info.get("tree") in ONE_SEED and info.get("seed") != ONE_SEED[info["tree"]]:
            return
        if info.get("info_only") and arm != DEFAULT_ARMS[0]:
            return
        prm = {**ARMS[arm], **(params or {})}
        if meta:  # (lane 97: tree meta settings for every variant, e.g. the brakes' dials {"raiders": 2})
            raw = copy.deepcopy(raw)
            raw.setdefault("meta", {}).update(meta)
        suffix = "".join(f"~{x}" for x in ([arm] if arm != DEFAULT_ARMS[0] else []) + ([tag or "p"] if params or meta else []))
        out.append({"family": fam, "name": f"{name}{suffix}@{world}", "world": world, "raw": raw, "arm": arm, "params": prm,
                    "tag": tag if params or meta else None, "meta": meta or None, **info})

    authored_trees = [(p.stem, *authored(p)) for p in sorted(TREES.glob("*.toml"))]
    for arm in arms:
        for w in worlds:
            for s in (7, 10, 13):
                add("base", f"dnd-s{s}", with_seed(dnd, s), w, arm, tree="dnd", seed=s)
                add("base", f"sm-s{s}", with_seed(sm, s), w, arm, tree="seven_meals", seed=s)
            for j in range(1, 5):
                add("jitter", f"dnd-j{j}", with_seed(jitter(dnd, np.random.default_rng(7700 + j)), 7), w, arm, tree="dnd", seed=7, jitter=j)
            for j in range(1, 3):
                add("jitter", f"sm-j{j}", with_seed(jitter(sm, np.random.default_rng(7800 + j)), 7), w, arm, tree="seven_meals", seed=7, jitter=j)
            for s in (7, 10):
                add("subset", f"dnd5-s{s}", with_seed(subset(dnd, ["human", "elf", "dwarf", "halfling", "orc"]), s), w, arm, tree="dnd5", seed=s)
                add("subset", f"dnd3-s{s}", with_seed(subset(dnd, ["human", "goblin", "kobold"]), s), w, arm, tree="dnd3", seed=s)
                plus = copy.deepcopy(dnd)
                plus["lineage"].append(dict(ADDED_PEOPLE))
                add("subset", f"dnd+1-s{s}", with_seed(plus, s), w, arm, tree="dnd+1", seed=s)
                for name, raw, info in authored_trees:
                    add("authored", f"{name}-s{s}", with_seed(raw, s), w, arm, tree=name, seed=s, **info)
                for n in (1, 3):
                    add("portal", f"dnd-sites{n}-s{s}", with_seed(dnd, s, portal_mode="sites", portals=n), w, arm, tree="dnd", seed=s, portals=n)
            for lid in KNOB_PEOPLES:
                for x in KNOB_X:
                    add("knob", f"dnd-{lid}x{x:g}-s7", with_seed(knob(dnd, lid, x), 7), w, arm, tree="dnd", seed=7, knob=lid, x=x)
    if families and "screen" in families:  # (diagnostic screens, only on request: which competition rule makes a small tree a monopoly)
        five = next(raw for name, raw, _ in authored_trees if name == "five_peoples")
        for w in worlds:
            for tname, raw in (("five_peoples", five), ("dnd3", subset(dnd, ["human", "goblin", "kobold"])), ("dnd", dnd)):
                if trees and tname not in trees:
                    continue
                for sname, prm in SCREENS.items():
                    out.append({"family": "screen", "name": f"scr-{tname}-{sname}-s7@{w}", "world": w, "raw": with_seed(raw, 7),
                                "arm": DEFAULT_ARMS[0], "tree": tname, "seed": 7, "screen": sname, "params": {**prm, **(params or {})}})
    return out


SCREENS = {"base": {}, "nofit": {"FIT_Q": 0.0, "BREADTH_Q": 0.0}, "closed1": {"ALPHA_CLOSED": 1.0}, "nohold": {"HOLD_MIN": 0.0},
           "noexpanse": {"EXPANSE_PRESS": 0.0}, "nosurge": {"SURGE_Q": 0.0}}


# ---------------------------------------------------------------- one run

WILD_NEAR = 0.5  # (PW-1385 sizing: a farmed or herded cell where the wild rung gives at least this x the way's own density)


def wild_overlap(h, P) -> dict:
    """PW-1385 sizing (lane 139): per people, its farmed and herded people, and those of them on cells where its wild density (the
    forager or fisher rung, ladder.Ladder.line) is at least WILD_NEAR x the farm (or herd) density it gets there; and per biome class
    (history.habitat.BIOMES) the same summed over all peoples. Rung densities are recovered from Ladder.line with one way known at a
    time (d = s x way + (1 - s) x wild)."""
    from planet.lineages.spread import EST
    from planet.lineages.history.habitat import BIOMES, biome_class
    lad = getattr(h, "ladder", None)
    if lad is None or not lad.ok or h._env_now is None:
        return {}
    bio = biome_class(h._env_now, h._tags_now)
    out, by_b = {}, {}
    for k, l in enumerate(h.lines):
        if l.overlay or l.megafauna or l.marine or not lad.people[k]:
            continue
        pc = h.population(k, P)
        if pc.sum() <= 0:
            continue
        t = lad.tech(k, 0.0)
        if not (t[0] or t[1]):
            continue
        wild = lad.line(k, (False, False, -1.0, -1.0), None)[0]
        d, sf, sh = lad.line(k, t, None)[:3]
        dd = np.maximum(d, 1e-12)
        rows = {}
        if t[0]:
            d1, s1 = lad.line(k, (True, False, t[2], t[3], t[4]), None)[:2]
            farm = np.where(s1 > 0, (d1 - (1 - s1) * wild) / np.maximum(s1, 1e-12), 0.0)
            rows["farm"] = (pc * sf * farm / dd, wild >= WILD_NEAR * farm)
        if t[1]:
            d2, _, s2 = lad.line(k, (False, True, -1.0, -1.0), None)[:3]
            nomad = np.where(s2 > 0, (d2 - (1 - s2) * wild) / np.maximum(s2, 1e-12), 0.0)
            rows["herd"] = (pc * sh * nomad / dd, wild >= WILD_NEAR * nomad)
        who = h.tree.people_of(l.id)
        o = out.setdefault(who, {})
        for way, (ppl, near) in rows.items():
            ppl = np.where(P[k] >= EST, ppl, 0.0)
            v = o.setdefault(way, [0.0, 0.0])
            v[0] += float(ppl.sum())
            v[1] += float(ppl[near].sum())
            for b in np.unique(bio[ppl > 0]):
                if b < 0:
                    continue
                sel = (bio == b) & (ppl > 0)
                w = by_b.setdefault(BIOMES[b], {}).setdefault(way, [0.0, 0.0])
                w[0] += float(ppl[sel].sum())
                w[1] += float(ppl[sel & near].sum())
    rnd = lambda d: {a: {w: [round(x) for x in v] for w, v in b.items()} for a, b in d.items()}  # noqa: E731
    return {"peoples": rnd(out), "biomes": rnd(by_b)}


WILD_RUNGS = (0, 1, 8)  # (ladder.RUNGS forager, fisher, raider: a cell's people living off the wild)


def forage_land(h, P) -> dict:
    """PW-1385 (lane 141): where the wild still feeds people at the end. Per biome class: peopled cells, those whose people are
    mostly on a wild rung (forager, fisher, raider: ladder.Ladder.line's main rung), all people and those on a wild rung. Per people:
    its people, its wild-rung people and wild-led cells (Mkm2), for a forager people (ladder.barters, PW-1386) its people and the part
    its traded farm food feeds (ladder.barter), and for a people knowing cultivation its farmable land (the fertile
    good's share, ladder.farmable, summed over held cells, Mkm2) and the part of it farmed (ladder.sh['farm'])."""
    from planet.lineages.spread import EST
    from planet.lineages.history.habitat import BIOMES, biome_class
    lad = getattr(h, "ladder", None)
    if lad is None or not lad.ok or h._env_now is None:
        return {}
    bio = biome_class(h._env_now, h._tags_now)
    n = h.grid.n
    tot, wild = np.zeros(n), np.zeros(n)
    kinds = {}
    for k, l in enumerate(h.lines):
        if l.overlay or l.megafauna or l.marine or not lad.people[k]:
            continue
        pc = h.population(k, P)
        if pc.sum() <= 0:
            continue
        w = np.isin(lad.rung[k], WILD_RUNGS) & (pc > 0)
        tot += pc
        wild += np.where(w, pc, 0.0)
        o = kinds.setdefault(h.tree.people_of(l.id), {"pop": 0.0, "wild_pop": 0.0, "wild_mkm2": 0.0, "farmable": 0.0, "farmed": 0.0,
                                                      "forager_pop": 0.0, "traded_pop": 0.0})
        o["pop"] += float(pc.sum())
        o["wild_pop"] += float(pc[w].sum())
        if lad.barters(k, lad.tech(k, 0.0)):  # (PW-1386: a forager people, and the people its traded farm food feeds)
            o["forager_pop"] += float(pc.sum())
            o["traded_pop"] += float((pc * lad.barter[k]).sum()) if getattr(lad, "barter", None) is not None else 0.0
            fn = getattr(lad, "_fn", None)
            if fn is not None:  # (its people within reach of 1+ and 5+ farmers per km2: BARTER_HALF)
                o["near1_pop"] = o.get("near1_pop", 0.0) + float(pc[fn >= 1.0].sum())
                o["near5_pop"] = o.get("near5_pop", 0.0) + float(pc[fn >= 5.0].sum())
        o["wild_mkm2"] += float(w.sum() * h.cell_mkm2)
        if lad.tech(k, 0.0)[0] and not lad.den[k]:
            held = P[k] >= EST
            o["farmable"] += float(lad.farmable[held].sum() * h.cell_mkm2)
            o["farmed"] += float(lad.sh["farm"][k][held].sum() * h.cell_mkm2)
    by_b = {}
    peopled = tot > 0
    for b, nm in enumerate(BIOMES):
        sel = peopled & (bio == b)
        if sel.any():
            by_b[nm] = {"cells": int(sel.sum()), "wild_cells": int((sel & (wild > 0.5 * tot)).sum()),
                        "pop": float(tot[sel].sum()), "wild_pop": float(wild[sel].sum())}
    return {"biomes": by_b, "peoples": {a: {x: round(v, 4) for x, v in o.items()} for a, o in kinds.items()},
            "cell_mkm2": float(h.cell_mkm2)}


DEN_HIGH = 0.5  # (PW-1382: den ground at or above this counts as good den ground in den_ground)


def den_ground(h, P) -> dict:
    """PW-1382 (lane 143): how each people sits on the den ground (the `den` good, dens.py) at the end: its range and its people, all
    and on good den ground (>= DEN_HIGH), and on the old proxy, broken country (mountain, hills, breaks: lane 97's den rule); the
    land's own shares of both, for the baseline. Empty without the den good."""
    from planet.lineages.spread import EST
    G = h.goods
    if G is None or "den" not in G or h._tags_now is None:
        return {}
    fit = np.asarray(G["den"], float)
    t = h._tags_now
    land = t["land"]
    hi = fit >= DEN_HIGH
    broken = t["mountain"] | t["hills"] | t["breaks"]
    tree = h.tree
    out = {}
    for k, l in enumerate(h.lines):
        if l.overlay or l.megafauna:
            continue
        who = tree.people_of(l.id)
        pc = h.population(k, P)
        o = out.setdefault(who, {"pop": 0.0, "pop_hi": 0.0, "pop_broken": 0.0, "fit_pop": 0.0})
        o["pop"] += float(pc.sum())
        o["pop_hi"] += float(pc[hi].sum())
        o["pop_broken"] += float(pc[broken].sum())
        o["fit_pop"] += float((pc * fit).sum())
    for who, o in out.items():
        held = h.whole(who, P) >= EST
        o["mkm2"] = float(held.sum() * h.cell_mkm2)
        o["mkm2_hi"] = float((held & hi).sum() * h.cell_mkm2)
        o["mkm2_broken"] = float((held & broken).sum() * h.cell_mkm2)
        o["fit_area"] = float(fit[held].mean()) if held.any() else 0.0
    return {"peoples": out, "land_hi": float(hi[land].mean()), "land_broken": float(broken[land].mean()),
            "land_fit": float(fit[land].mean())}


def measure(h, res, pres) -> dict:
    """The numbers of one try: per people (groups rolled up; megafauna and overlays apart) share of people, of the cells led, range,
    founding; the extinctions and their reasons."""
    from planet.lineages.spread import EST
    from planet.lineages.ladder import RUNGS as LADDER_RUNGS
    tree, P = h.tree, res["present"]
    n = h.grid.n
    peoples = [l for l in tree.leaves() if not l.group_of and not l.megafauna and not l.overlay]
    pid = {l.id: i for i, l in enumerate(peoples)}
    pop = np.zeros((len(peoples), n))
    ways = {l.id: {} for l in peoples}  # (PW-1275: per people, its people and held land per rung of the density ladder)
    for k, l in enumerate(h.lines):
        if l.overlay or l.megafauna or l.marine and False:
            continue
        who = tree.people_of(l.id)
        if who in pid:
            pc = h.population(k, P)
            pop[pid[who]] += pc
            lad = getattr(h, "ladder", None)
            if lad is not None and lad.ok and getattr(h, "_dmap", None) is not None and pc.sum() > 0 and not l.marine:  # (no _dmap: PEOPLE_PROD off)
                for i, nm in enumerate(LADDER_RUNGS):
                    sel = (lad.rung[k] == i) & (pc > 0)
                    if sel.any():
                        w = ways[who].setdefault(nm, [0.0, 0.0, 0.0])  # (people, held km2, people at full presence: the rung's number there)
                        w[0] += float(pc[sel].sum())
                        w[1] += float(sel.sum() * h.cell_mkm2 * 1e6)
                        w[2] += float(h._dmap[k][sel].sum() * h.cell_mkm2 * 1e6)
    tot = pop.sum()
    peopled = pop.sum(0) > 0
    lead = np.argmax(pop, 0)
    out = {}
    ev_by = {}
    for e in h.events:
        ev_by.setdefault(e.get("line"), []).append(e)
    for l in peoples:
        i = pid[l.id]
        held = (h.whole(l.id, P) >= EST)
        alive = bool(pop[i].sum() > 0)
        o = h.origins.get(l.id, {})
        why = None
        m_ext = l.extinct_kyr is not None  # (authored to die out: not a failure)
        if not alive:
            evs = [e for x in [l.id, *tree.groups_of(l.id)] for e in ev_by.get(x, []) if e.get("kind") in ("extinct", "unborn", "refuge")]
            if l.id not in h.started:
                why = "never founded"
            elif evs:
                why = "; ".join(f"{e.get('ago_kyr', e.get('ago'))} kyr: {e.get('text', e.get('kind'))}" for e in evs[-2:])
            else:
                why = f"faded patches {h.faded.get(l.id, 0)}; no event"
        out[l.id] = {"share": float(pop[i].sum() / tot) if tot > 0 else 0.0,
                     "led": float((peopled & (lead == i)).sum() / max(peopled.sum(), 1)),
                     "area_mkm2": round(float(held.sum() * h.cell_mkm2), 3), "pop": float(pop[i].sum()), "alive": alive,
                     "why_gone": why, "origin": {k: o.get(k) for k in ("ago_kyr", "why", "lat", "lon")} if o else None,
                     "found_mkm2": h._found_mkm2.get(l.id), "inherit_mkm2": h._inherit_mkm2.get(l.id, 0.0),
                     "jumps": h.jumps_n.get(l.id, 0), "crossings": h.crossings_n.get(l.id, 0), "faded": h.faded.get(l.id, 0),
                     "refuged": l.id in h._refuged, "kind": l.demo("kind"), "authored_extinct": m_ext,
                     "density": float(pop[i].sum() / max(held.sum() * h.cell_mkm2 * 1e6, 1.0)),
                     "ways": {r: [round(x, 1) for x in v] for r, v in ways[l.id].items()}}
    lost = [x for x in pres.get("lost", [])]
    # continental blocs (lane 83, owner D20: different landmasses led by different sets of peoples): per landmass of the present land
    # of at least BLOC_MIN_MKM2 with people on it, its leading people and that people's share of the landmass's people, and the humans'
    # (and lane 84's measures, PW-1202: the peoples making 90% of its people, n90, and its mix's distance from the world's, half the
    # summed share differences, dist)
    lab, nl = h.grid.components(h.steps[-1].get()["land"])
    world = pop.sum(1) / max(float(pop.sum()), 1e-12)
    blocs = []
    hum = pid.get("human")
    for z in range(nl):
        sel = lab == z
        area = float(sel.sum() * h.cell_mkm2)
        ptot = float(pop[:, sel].sum())
        if area < BLOC_MIN_MKM2 or ptot <= 0:
            continue
        ps = pop[:, sel].sum(1) / ptot
        t = int(np.argmax(ps))
        blocs.append({"mkm2": round(area, 2), "top": peoples[t].id, "top_share": float(ps[t]),
                      "human_share": float(ps[hum]) if hum is not None else 0.0,
                      "n_over_10pct": int((ps >= 0.1).sum()),
                      "n90": int(np.searchsorted(np.cumsum(np.sort(ps)[::-1]), 0.9) + 1), "dist": float(0.5 * np.abs(ps - world).sum()),
                      "pop": ptot})
    kinds = {}
    for e in h.events:
        kinds[e.get("kind")] = kinds.get(e.get("kind"), 0) + 1
    # (lane 97: per line, the share of its K each brake held off at its last step, history.counter)
    brakes = dict(getattr(h, "lost", None) or {})
    origins_all = {lid: o.get("why") for lid, o in h.origins.items()}  # (every line's founding reason, stems included: the fallback counts)
    return {"peoples": out, "n_peoples": len(peoples), "origins_all": origins_all, "refuges": list(getattr(h, "_refuges", [])), "refuge_picks": list(getattr(h, "_refuge_picks", [])), "lost": lost, "brakes": brakes, "event_kinds": kinds, "runtime_s": round(getattr(h, "runtime", 0.0), 1), "blocs": blocs,
            "total_pop": float(tot), "megafauna": {k: v.get("count") if isinstance(v, dict) else None for k, v in (pres.get("megafauna") or {}).items()}}


def run_one(spec: dict) -> dict:
    from planet.lineages.history import model as M

    class Probe(M.History):  # (records each line's founding range and what it inherits from a stem's end; no change to the model)
        def _record_origin(self, line, step, cell, why):
            self.__dict__.setdefault("_found_mkm2", {})[line.id] = round(float((self.p[self.idx[line.id]] >= 0.12).sum() * self.cell_mkm2), 3)
            return super()._record_origin(line, step, cell, why)

        def _hold_out(self, l, k, K, step, held0=None):  # (PW-1558: a refuge of a line that held nothing, and how far from its last land)
            empty = not (self.p[k] > 0).any()
            last = held0 if held0 is not None and held0.any() else self._last_held.get(k)
            super()._hold_out(l, k, K, step, held0)
            if empty and (self.p[k] > 0).any():
                from planet.lineages.gridops import dist_km
                c = int(np.argmax(self.p[k]))
                km = float(dist_km(self.grid, float(self.grid.lat[c]), float(self.grid.lon[c]))[last].min()) if last is not None and last.any() else None
                self.__dict__.setdefault("_refuges", []).append({"line": l.id, "ago_kyr": round(step.ago, 3), "km": None if km is None else round(km)})

        def _refuge_cell(self, l, K, last):  # (PW-1558, lane 269: every nearest-free-country pick, a stem's refuge or a split's founders, and how far from the land it left)
            c = super()._refuge_cell(l, K, last)
            if last is not None and last.any():
                from planet.lineages.gridops import dist_km
                km = float(dist_km(self.grid, float(self.grid.lat[c]), float(self.grid.lon[c]))[last].min())
                self.__dict__.setdefault("_refuge_picks", []).append({"line": l.id, "km": round(km)})
            return c

        def _end_parent(self, line, step, env, tags):
            before = {c: float((self.p[self.idx[c]] >= 0.12).sum()) for c in self._realm_kids(line)}
            super()._end_parent(line, step, env, tags)
            inh = self.__dict__.setdefault("_inherit_mkm2", {})
            for c, b in before.items():
                inh[c] = round(inh.get(c, 0.0) + (float((self.p[self.idx[c]] >= 0.12).sum()) - b) * self.cell_mkm2, 3)

    spec = {**spec, "params": {**ARMS.get(spec.get("arm", "now"), {}), **(spec.get("params") or {})}}
    saved = []
    if spec.get("params"):  # (a diagnostic screen: tuning constants overridden in every module of the history that imported them)
        import importlib, pkgutil
        from planet.lineages import history as HP, spread as SPR
        mods = [importlib.import_module(f"planet.lineages.history.{m.name}") for m in pkgutil.iter_modules(HP.__path__)] + [SPR]
        for k, v in spec["params"].items():
            for mod in mods:
                if hasattr(mod, k):
                    saved.append((mod, k, getattr(mod, k)))
                    setattr(mod, k, type(getattr(mod, k))(v) if not isinstance(getattr(mod, k), tuple) else tuple(v))
    try:
        return _run_spec(spec, Probe)
    finally:  # (put the constants back, so runs in one process don't leak overrides into each other)
        for mod, k, v in reversed(saved):
            setattr(mod, k, v)


def _run_spec(spec: dict, Probe) -> dict:
    from planet.lineages import land as LD
    from planet.lineages import recent as R
    from planet.lineages import spec as SP
    from planet.lineages.history.summary import present_summary
    t0 = time.time()
    tree = SP.parse(spec["raw"])
    tz, now0, world = R.resolve(spec["world"])
    rp = {"kyr": 30.0, "climate_every": 2.0, **spec.get("recent", {})}  # (the CLI defaults; a test passes its own)
    ps = R.Pass(tz, spec.get("now", now0), R.RecentParams(**rp), world_ref=world)
    goods = LD.goods(world) if world and tree.uses else None
    h = Probe(tree, ps, tree.seed * 1000, goods=goods)
    h._found_mkm2, h._inherit_mkm2 = {}, {}
    res = h.run()
    pres = present_summary(h, res["present"])
    m = measure(h, res, pres)
    try:
        m["wild_overlap"] = wild_overlap(h, res["present"])
    except Exception as e:  # (a sizing number: never fail a run on it)
        m["wild_overlap"] = {"error": repr(e)}
    try:
        m["forage_land"] = forage_land(h, res["present"])
    except Exception as e:  # (likewise)
        m["forage_land"] = {"error": repr(e)}
    try:
        m["den_ground"] = den_ground(h, res["present"])
    except Exception as e:  # (likewise)
        m["den_ground"] = {"error": repr(e)}
    m["wall_s"] = round(time.time() - t0, 1)
    import resource
    m["max_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    return m


# ---------------------------------------------------------------- runner

def _slug(name: str) -> str:
    return name.replace("@", "_at_").replace("/", "_")


def run_all(out: Path, jobs: int, threads: int, max_load: float, plan_args: dict | None = None):
    out.mkdir(parents=True, exist_ok=True)
    todo = [v for v in plan(**(plan_args or {})) if not (out / f"{_slug(v['name'])}.json").exists()
            and not (out / f"{_slug(v['name'])}.spec.json").exists()]  # (a spec on disk: in flight, from another runner)
    print(f"{len(todo)} variants to run in {out}", flush=True)
    running: list[tuple[subprocess.Popen, dict, float]] = []
    env = {**os.environ, "NUMBA_NUM_THREADS": str(threads)}
    while todo or running:
        for pr in list(running):
            if pr[0].poll() is not None:
                running.remove(pr)
                print(f"  done {pr[1]['name']} rc={pr[0].returncode} {time.time() - pr[2]:.0f}s", flush=True)
        if todo and max(len(running), len(list(out.glob('*.spec.json')))) < jobs and (os.getloadavg()[0] <= max_load or not running):
            v = todo.pop(0)
            sp = out / f"{_slug(v['name'])}.spec.json"
            sp.write_text(json.dumps(v))
            log = open(out / f"{_slug(v['name'])}.log", "w")
            p = subprocess.Popen([sys.executable, __file__, "one", str(sp), str(out / f"{_slug(v['name'])}.json")],
                                 stdout=log, stderr=subprocess.STDOUT, env=env, cwd=ROOT)
            running.append((p, v, time.time()))
            print(f"start {v['name']} (pid {p.pid}, load {os.getloadavg()[0]:.0f}, {len(todo)} left)", flush=True)
            time.sleep(5)
            continue
        time.sleep(10)


def one(spec_path: str, out_path: str):
    spec = json.loads(Path(spec_path).read_text())
    info = {k: v for k, v in spec.items() if k != "raw"}
    try:
        m = run_one(spec)
        m.update(info, ok=True)
    except Exception:
        m = {**info, "ok": False, "error": traceback.format_exc()}
    Path(out_path).write_text(json.dumps(m, indent=1))
    try:
        Path(spec_path).unlink()
    except OSError:
        pass


# ---------------------------------------------------------------- report

def _fmt(x, pct=True):
    return "-" if x is None else (f"{100 * x:.0f}%" if x >= 0.995 else f"{100 * x:.2g}%") if pct else f"{x:.3g}"


def _d31(ok, lines):
    """Owner D31 A (2026-10-31): the commonest people should usually be under half of all people, and never over D31_NEVER once a tree
    has D31_MANY or more peoples. Reported per tree (families and worlds pooled) and over all tries; a check to read, not an invariant:
    no try fails on it."""
    groups = {}
    for r in ok:
        if r.get("info_only") or not r["peoples"]:
            continue
        groups.setdefault(r.get("tree", "?"), []).append(r)
    groups["all tries"] = [r for v in list(groups.values()) for r in v]
    rows, out = [], {}
    for t, rs in groups.items():
        top = np.array([max(x["share"] for x in r["peoples"].values()) for r in rs])
        many = np.array([max(x["share"] for x in r["peoples"].values()) for r in rs if r["n_peoples"] >= D31_MANY])
        never = float((many <= D31_NEVER).mean()) if len(many) else None
        out[t] = {"runs": len(rs), "median": float(np.median(top)), "under_half": float((top < D31_USUAL).mean()),
                  "many_runs": int(len(many)), "many_never_over": never}
        rows.append(f"| {t} | {len(rs)} | {_fmt(out[t]['median'])} | {100 * out[t]['under_half']:.0f}% | {len(many)} | "
                    f"{'-' if never is None else f'{100 * never:.0f}%'} |")
    lines += ["## The commonest people's share (owner D31 A: reported, not a failure)", "",
              f"Usually under {100 * D31_USUAL:.0f}% of all people; never over {100 * D31_NEVER:.0f}% with {D31_MANY}+ peoples.", "",
              f"| tree | runs | median commonest share | runs under {100 * D31_USUAL:.0f}% | runs with {D31_MANY}+ peoples | "
              f"of those, at or under {100 * D31_NEVER:.0f}% |", "|---|---|---|---|---|---|", *rows, ""]
    return lines, out


def report(out: Path) -> str:
    runs = [json.loads(p.read_text()) for p in sorted(out.glob("*.json")) if not p.name.endswith(".spec.json") and p.name != "summary.json"]
    screens = [r for r in runs if r.get("family") == "screen"]
    runs = [r for r in runs if r.get("family") != "screen"]
    lines = [f"# Peoples robustness suite: {len(runs)} runs ({out})", ""]
    crashed = [r for r in runs if not r.get("ok")]
    ok = [r for r in runs if r.get("ok")]
    # -- invariants per run
    lines += ["## Invariants per run", "", "| run | peoples | crash | lost (why) | top people | top share | mono | most cells led | wall s |", "|---|---|---|---|---|---|---|---|---|"]
    fails = {a: {"runs": 0, "crash": 0, "extinct": 0, "mono": 0, "any": 0} for a in ARMS}
    for r in sorted(runs, key=lambda r: (r["family"], r["name"])):
        fa = fails[r.get("arm", "now")] if not r.get("info_only") else {}
        fa["runs"] = fa.get("runs", 0) + 1
        if not r.get("ok"):
            fa["crash"] = fa.get("crash", 0) + 1
            fa["any"] = fa.get("any", 0) + 1
            lines.append(f"| {r['name']} | - | CRASH: {r['error'].strip().splitlines()[-1][:80]} | | | | | |")
            continue
        P = r["peoples"]
        gone = {k: v["why_gone"] for k, v in P.items() if not v["alive"] and not v.get("authored_extinct")}
        top = max(P, key=lambda k: P[k]["share"]) if P else None
        mono = bool(top and r["n_peoples"] > 2 and P[top]["share"] > MONO_MAX)
        fa["extinct"] = fa.get("extinct", 0) + bool(gone)
        fa["mono"] = fa.get("mono", 0) + mono
        fa["any"] = fa.get("any", 0) + bool(gone or mono)
        g = "; ".join(f"{k} ({(w or '')[:70]})" for k, w in gone.items()) or "-"
        led_top = max(P, key=lambda k: P[k]["led"]) if P else None
        lines.append(f"| {r['name']} | {r['n_peoples']} | - | {g} | {top} | {_fmt(P[top]['share']) if top else '-'} | {'FAIL' if mono else 'ok'} | {led_top} {_fmt(P[led_top]['led']) if led_top else '-'} | {r.get('wall_s')} |")
    lines += ["", "| founding arm | runs counted | any fail | crash | a people extinct | one people over %d%% |" % round(100 * MONO_MAX), "|---|---|---|---|---|---|"]
    for a, f in fails.items():
        if f["runs"]:
            lines.append(f"| {a} | {f['runs']} | {f['any']} | {f['crash']} | {f['extinct']} | {f['mono']} |")
    lines += ["", "(info-only trees, all_at_once, are not counted.)", ""]
    # -- continental blocs (lane 83)
    bl = [r for r in ok if r.get("blocs") is not None]
    if bl:
        lines += [f"## Continental blocs (landmasses of {BLOC_MIN_MKM2:g}+ Mkm² with people)", "",
                  "| run | landmasses | led by a non-human people | non-human majority (>50%) | humans under 50% | distinct leaders | "
                  "median peoples making 90% | mix distance from the world's (people-weighted) | "
                  "leaders (share of the landmass's people, largest landmass first) |", "|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(bl, key=lambda r: (r["family"], r["name"])):
            B = sorted(r["blocs"], key=lambda b: -b["mkm2"])
            nh = sum(b["top"] != "human" for b in B)
            nm = sum(b["top"] != "human" and b["top_share"] > 0.5 for b in B)
            hu = sum(b["human_share"] < 0.5 for b in B)
            lead = ", ".join(f"{b['top']} {_fmt(b['top_share'])}" for b in B[:6])
            n90 = f"{np.median([b['n90'] for b in B]):g}" if B and "n90" in B[0] else "-"
            wt = sum(b.get("pop", 0) for b in B)
            dist = f"{sum(b['dist'] * b['pop'] for b in B) / wt:.2f}" if B and "dist" in B[0] and wt > 0 else "-"
            lines.append(f"| {r['name']} | {len(B)} | {nh} | {nm} | {hu} | {len({b['top'] for b in B})} | {n90} | {dist} | {lead} |")
        lines.append("")
    # -- the commonest people's share (owner D31 A, 2026-10-31): reported, never a failure
    lines, d31 = _d31(ok, lines)
    # -- spread over base + jitter (the same families under each founding arm), per tree
    summ = {"spread": {}, "knob": {}, "fails": fails, "d31": d31}
    stats = {}
    for tree in ("dnd", "seven_meals"):
        for arm in ARMS:
            rs = [r for r in ok if r.get("tree") == tree and r.get("arm", "now") == arm and r["family"] in ("base", "jitter")]
            if not rs:
                continue
            ids = sorted({k for r in rs for k in r["peoples"] if not r["peoples"][k].get("authored_extinct")})
            lines += [f"## Share spread, {tree}, founding {arm} (base + jitter: {len(rs)} runs)", "",
                      "(swing x pooled over both worlds; the worst swing within one world and one family, seeds or jitter, PW-1207, decides"
                      " 'brittle': the pooled one also holds the two worlds' different geography)", "",
                      "| people | share min | median | max | swing x | worst x in one world and family | led min | led median | led max | dead in | brittle |",
                      "|---|---|---|---|---|---|---|---|---|---|---|"]
            rows = []
            for k in ids:
                s = np.array([r["peoples"][k]["share"] for r in rs if k in r["peoples"]])
                ld = np.array([r["peoples"][k]["led"] for r in rs if k in r["peoples"]])
                dead = sum(not r["peoples"][k]["alive"] for r in rs if k in r["peoples"])
                sw = float(max(s.max(), SHARE_FLOOR) / max(s.min(), SHARE_FLOOR))
                grp = {}
                for r in rs:
                    if k in r["peoples"]:
                        grp.setdefault((r["world"], r["family"]), []).append(r["peoples"][k]["share"])
                sw1 = max((max(max(v), SHARE_FLOOR) / max(min(v), SHARE_FLOOR) for v in grp.values() if len(v) > 1), default=1.0)
                rows.append((k, s, ld, dead, sw, float(sw1)))
            for k, s, ld, dead, sw, sw1 in sorted(rows, key=lambda x: -np.median(x[1])):
                br = sw1 > SWING or dead > 0
                st = {"min": float(s.min()), "median": float(np.median(s)), "max": float(s.max()), "swing": sw, "swing_one_world": sw1,
                      "led_median": float(np.median(ld)), "led_max": float(ld.max()), "dead": dead, "n": len(s), "brittle": br}
                summ["spread"].setdefault(f"{tree}/{arm}", {})[k] = stats.setdefault((tree, arm), {})[k] = st
                lines.append(f"| {k} | {_fmt(s.min())} | {_fmt(np.median(s))} | {_fmt(s.max())} | {sw:.3g} | {sw1:.3g} | {_fmt(ld.min())} | {_fmt(np.median(ld))} | {_fmt(ld.max())} | {dead}/{len(s)} | {'BRITTLE' if br else ''} |")
            lines.append("")
    # -- the founding arms side by side
    for tree in ("dnd", "seven_meals"):
        arms = [a for a in ARMS if (tree, a) in stats]
        if len(arms) < 2:
            continue
        lines += [f"## Founding arms compared, {tree}: median share (swing x)", "", "| people | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
        ids = sorted({k for a in arms for k in stats[(tree, a)]}, key=lambda k: -stats[(tree, arms[0])].get(k, {"median": 0})["median"])
        for k in ids:
            cells = []
            for a in arms:
                st = stats[(tree, a)].get(k)
                cells.append("-" if st is None else f"{_fmt(st['median'])} ({st['swing']:.2g}x{', dead ' + str(st['dead']) if st['dead'] else ''})")
            lines.append(f"| {k} | " + " | ".join(cells) + " |")
        nb = {a: sum(v["brittle"] for v in stats[(tree, a)].values()) for a in arms}
        lines += ["", "Brittle peoples (swing over %gx or dead in a run): " % SWING + ", ".join(f"{a} {nb[a]}" for a in arms), ""]
    # -- portals (dnd, founding range): the arrivals' share with portal_mode sites against off
    pr = [r for r in ok if r["family"] == "portal"]
    if pr:
        lines += ["## Portals (dnd): arrivals' share, off vs sites", "", "| world, seed | portals | elf | gnome | triton |", "|---|---|---|---|---|"]
        base = {(r["world"], r["seed"]): r for r in ok if r["family"] == "base" and r.get("tree") == "dnd" and r.get("arm", "now") == DEFAULT_ARMS[0]}
        for (w, s), b in sorted(base.items()):
            for r in [b] + sorted([r for r in pr if r["world"] == w and r["seed"] == s], key=lambda r: r["portals"]):
                lines.append(f"| {w} s{s} | {r.get('portals', 'off')} | " + " | ".join(_fmt(r["peoples"].get(x, {}).get("share")) for x in ("elf", "gnome", "triton")) + " |")
        lines.append("")
    # -- authored trees (and the info-only all-at-once tree beside dnd)
    au = [r for r in ok if r["family"] == "authored"]
    if au:
        lines += ["## Authored trees (median over worlds and seeds; per arm: top people and share, peoples under 0.1%, dead)", "",
                  "| tree | rationale | arm | runs | top | top share | median people >= 1% | under 0.1% | dead |", "|---|---|---|---|---|---|---|---|---|"]
        for tree in sorted({r["tree"] for r in au}):
            for arm in ARMS:
                rs = [r for r in au if r["tree"] == tree and r.get("arm", "now") == arm]
                if not rs:
                    continue
                ids = sorted({k for r in rs for k in r["peoples"] if not r["peoples"][k].get("authored_extinct")})
                med = {k: float(np.median([r["peoples"][k]["share"] for r in rs if k in r["peoples"]])) for k in ids}
                top = max(med, key=med.get)
                big = np.median([sum(r["peoples"][k]["share"] >= 0.01 for k in ids if k in r["peoples"]) for r in rs])
                small = sorted(k for k in ids if med[k] < 0.001)
                dead = sorted({k for r in rs for k in ids if k in r["peoples"] and not r["peoples"][k]["alive"]})
                lines.append(f"| {tree}{' (info only)' if rs[0].get('info_only') else ''} | {rs[0].get('rationale', '')[:90]} | {arm} | {len(rs)} | {top} | "
                             f"{_fmt(med[top])} | {big:g} | {', '.join(small) or '-'} | {', '.join(dead) or '-'} |")
        lines.append("")
        aao = [r for r in au if r.get("info_only")]
        dn = [r for r in ok if r["family"] == "base" and r.get("tree") == "dnd" and r.get("arm", "now") == DEFAULT_ARMS[0]]
        if aao and dn:
            ids = sorted({k for r in aao + dn for k in r["peoples"] if not r["peoples"][k].get("authored_extinct")},
                         key=lambda k: -np.median([r["peoples"].get(k, {"share": 0})["share"] for r in dn]))
            lines += ["### All at once (info only) beside dnd (median share, range arm)", "", "| people | dnd | all at once |", "|---|---|---|"]
            for k in ids:
                a = [r["peoples"][k]["share"] for r in dn if k in r["peoples"]]
                b = [r["peoples"][k]["share"] for r in aao if k in r["peoples"]]
                lines.append(f"| {k} | {_fmt(float(np.median(a))) if a else '-'} | {_fmt(float(np.median(b))) if b else '-'} |")
            lines.append("")
    # -- diagnostic screens: the same tree with one competition rule switched off
    if screens:
        lines += ["## Diagnostic screens (seed 7): one rule off at a time", "",
                  "| tree | world | screen | top | top share | top cells led | others' median share | smallest people |", "|---|---|---|---|---|---|---|---|"]
        for r in sorted(screens, key=lambda r: (r["tree"], r["world"], list(SCREENS).index(r["screen"]) if r["screen"] in SCREENS else 99)):
            if not r.get("ok"):
                lines.append(f"| {r['tree']} | {r['world']} | {r['screen']} | CRASH | | | | |")
                continue
            P = {k: v for k, v in r["peoples"].items() if not v.get("authored_extinct")}
            top = max(P, key=lambda k: P[k]["share"])
            rest = [v["share"] for k, v in P.items() if k != top]
            lo = min(P, key=lambda k: P[k]["share"])
            lines.append(f"| {r['tree']} | {r['world']} | {r['screen']} | {top} | {_fmt(P[top]['share'])} | {_fmt(P[top]['led'])} | "
                         f"{_fmt(float(np.median(rest))) if rest else '-'} | {lo} {_fmt(P[lo]['share'])} |")
        lines.append("")
    # -- knob response
    kn = [r for r in ok if r["family"] == "knob"]
    if kn:
        lines += ["## Knob response (kind factor x0.5 / x1 / x2, same world and seed)", "",
                  "| people | world, seed | share x0.5 | x1 | x2 | led x0.5 | x1 | x2 | area x0.5 | x1 | x2 | monotone |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        base = {(r["world"], r["seed"]): r for r in ok if r["family"] == "base" and r.get("tree") == "dnd" and r.get("arm", "now") == DEFAULT_ARMS[0]}
        for lid in KNOB_PEOPLES:
            for (w, s), b in sorted(base.items()):
                got = {r["x"]: r for r in kn if r["knob"] == lid and r["world"] == w and r["seed"] == s}
                if len(got) < 2:
                    continue
                trio = [got.get(0.5), b, got.get(2.0)]
                if any(t is None for t in trio):
                    continue
                sh = [t["peoples"][lid]["share"] for t in trio]
                le = [t["peoples"][lid]["led"] for t in trio]
                ar = [t["peoples"][lid]["area_mkm2"] for t in trio]
                mono = sh[0] <= sh[1] <= sh[2] and le[0] <= le[1] + 1e-9 and le[1] <= le[2] + 1e-9
                summ["knob"].setdefault(lid, []).append({"world": w, "seed": s, "share": sh, "led": le, "area": ar, "monotone": mono})
                lines.append(f"| {lid} ({KNOB_PEOPLES[lid]}) | {w} s{s} | " + " | ".join(_fmt(x) for x in sh) + " | " +
                             " | ".join(_fmt(x) for x in le) + " | " + " | ".join(f"{x:.3g}" for x in ar) + f" | {'ok' if mono else 'NO'} |")
        lines.append("")
    # -- founding and inheritance (PW-1152): where a people's first range came from
    arms = [a for a in ARMS if any(r.get("arm", "now") == a for r in ok)]
    lines += ["## Founding range and stem inheritance (median over runs, Mkm2: founded / inherited at the stem's end / present)", "",
              "| people | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    ids = sorted({k for r in ok for k in r["peoples"]})
    for k in ids:
        cells = []
        for arm in arms:
            rr = [r for r in ok if r.get("arm", "now") == arm and k in r["peoples"]]
            f = [r["peoples"][k]["found_mkm2"] for r in rr if r["peoples"][k]["found_mkm2"] is not None]
            cells.append(f"{np.median(f):.3g} / {np.median([r['peoples'][k]['inherit_mkm2'] for r in rr]):.3g} / "
                         f"{np.median([r['peoples'][k]['area_mkm2'] for r in rr]):.3g}" if f else "-")
        lines.append(f"| {k} | " + " | ".join(cells) + " |")
    lines.append("")
    text = "\n".join(lines)
    (out / "report.md").write_text(text)
    (out / "summary.json").write_text(json.dumps(summ, indent=1))
    return text


def _filters(a):
    a.add_argument("--family", default=None, help="comma-separated families: base,jitter,subset,authored,knob,portal (screen: on request only)")
    a.add_argument("--arms", default=",".join(DEFAULT_ARMS), help=f"comma-separated arms of {list(ARMS)}")
    a.add_argument("--seeds", default=None, help="comma-separated seeds (default: each family's own)")
    a.add_argument("--trees", default=None, help="comma-separated trees: dnd, seven_meals, dnd5, dnd3, dnd+1, or authored file names")
    a.add_argument("--params", default=None, help='JSON of params overrides for every variant, e.g. \'{"FIT_CLIP": 2}\'')
    a.add_argument("--tag", default=None, help="the overrides' name in the variant names (default p)")
    a.add_argument("--meta", default=None, help='JSON of tree meta settings for every variant, e.g. \'{"raiders": 2, "war": 0}\'')
    a.add_argument("--worlds", default=",".join(WORLDS))


def _plan_args(args) -> dict:
    sp = lambda x: [v for v in x.split(",") if v] if x else None  # noqa: E731
    return {"worlds": sp(args.worlds), "families": set(sp(args.family)) if args.family else None, "arms": tuple(sp(args.arms)),
            "seeds": {int(x) for x in sp(args.seeds)} if args.seeds else None, "trees": set(sp(args.trees)) if args.trees else None,
            "params": json.loads(args.params) if args.params else None, "tag": args.tag,
            "meta": json.loads(args.meta) if args.meta else None}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("plan")
    _filters(a)
    a = sub.add_parser("run")
    a.add_argument("--out", required=True)
    a.add_argument("--jobs", type=int, default=4)
    a.add_argument("--threads", type=int, default=4)
    a.add_argument("--max-load", type=float, default=60.0)
    _filters(a)
    a = sub.add_parser("report")
    a.add_argument("--out", required=True)
    a = sub.add_parser("one")
    a.add_argument("spec")
    a.add_argument("result")
    args = ap.parse_args(argv)
    if args.cmd == "plan":
        for v in plan(**_plan_args(args)):
            print(v["family"], v["name"])
    elif args.cmd == "run":
        run_all(Path(args.out), args.jobs, args.threads, args.max_load, _plan_args(args))
        print(report(Path(args.out)))
    elif args.cmd == "report":
        print(report(Path(args.out)))
    elif args.cmd == "one":
        one(args.spec, args.result)


if __name__ == "__main__":
    main()
