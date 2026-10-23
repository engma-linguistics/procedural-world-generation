"""The lineage input: a graph of peoples with origin times, niches, traits, and soft wishes.

TOML (or JSON of the same shape); preset: planet/lineages/samples/dnd.toml. Each
[[lineage]] has an `origin` and a time `at` (years before the present: "8 Myr",
"450 kyr", "12000 yr"; a bare number is kyr):
- root:     arises in the world (no parents)
- split:    branches from `parents = [p]` (the usual tree edge); the parent ends at its last split unless `persists`
- arrival:  comes from outside the world (feywild, the planes) at `place = [lat, lon]` or where its habitat is best
- hybrid:   of two `parents`, where their ranges overlap; `contact = true` (default): it exists only where both
            parents meet (half-elves); false: it founds a people of its own
- template: an overlay on `parents` (hosts) from `at` on (tieflings): a `share` of the hosts' people,
            spreading from a few `sites` through the hosts' range only
So the "tree" is a DAG. Anything a line leaves out it inherits from its first parent.
[[use]] (by = a trait, a place tag or a line's id, good = land.GOODS, weight, optional pull) says what each way
of life looks for in the land (farmland, pasture, ores, harbours, coral coasts, volcanoes...); meta.land_pull how
strongly, or the use's own pull (a line takes the strongest pull of its favoured goods; history._land_mult);
strict = true: off those goods the habitat is cut, not lifted back to a mean of 1 (peoples bound to one country).
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
# speed; late_sea: sea factor from LATE_SEA_KYR ago (boats); the rest are habitat or late-mixing knobs.
TRAITS = {
    "flies": {"sea": 0.72, "relief": 0.0},
    "swims": {"sea": 0.55, "coast": 0.15},
    "coastal": {"coast": 0.6},
    "seafaring": {"late_sea": 0.75},
    "agricultural": {"farm": 1.0},
    "nomadic": {"speed": 2.0, "open": 0.3},
    "mountain": {"relief": 0.0, "mountain": 0.5},
    "hardy": {"widen": 1.25},
    "insular": {"mix": 0.2},
    "cosmopolitan": {"mix": 1.6},
    "subterranean": {"relief": 0.15, "widen": 1.15, "mountain": 0.3},
    "miner": {},  # (no movement knob: what it looks for in the land is the [[use]] table's)
}
LATE_SEA_KYR = 3.0
# long sea crossings (crossing.py): way -> (rate per kyr at a zero gap, length scale km, only since kyr ago).
# The chance a line reaches a landmass it doesn't hold in a step of dt kyr is 1 - exp(-dt x sum over its
# ways of rate x exp(-gap / L)) x the landing's habitat. 'raft' is everyone's (drift rafts, storms: monkeys
# across the young Atlantic, lemurs to Madagascar): a few hundred km once in a few Myr. Coastal foragers'
# canoes (Sahul ~60 kyr ago, ~100 km gaps), swimmers and fliers reach further; seafarers with boats
# (the Lapita / Polynesian voyages, 1000s of km) only late.
HOPS = {
    "raft": (3e-4, 150.0, None),
    "coastal": (0.01, 250.0, None),
    "swims": (0.05, 400.0, None),
    "flies": (0.05, 700.0, None),
    "seafaring": (1.0, 1500.0, 6.0),
}
ORIGINS = ("root", "split", "arrival", "hybrid", "template")

KOPPEN_CODES = ["Af", "Am", "Aw", "BWh", "BWk", "BSh", "BSk", "Csa", "Csb", "Csc", "Cwa", "Cwb", "Cwc", "Cfa", "Cfb",
                "Cfc", "Dsa", "Dsb", "Dsc", "Dsd", "Dwa", "Dwb", "Dwc", "Dwd", "Dfa", "Dfb", "Dfc", "Dfd", "ET", "EF"]
GROUPS = {  # Köppen groups usable in prefers / avoids (climate.KOPPEN ids)
    "tropical": [0, 1, 2], "rainforest": [0, 1], "savanna": [2], "arid": [3, 4, 5, 6], "desert": [3, 4],
    "steppe": [5, 6], "mediterranean": [7, 8, 9], "temperate": list(range(7, 16)), "subtropical": [10, 13],
    "oceanic": [14, 15], "continental": list(range(16, 28)), "subarctic": [18, 19, 22, 23, 26, 27],
    "polar": [28, 29], "tundra": [28],
}
PLACES = ("coast", "island", "mountain", "lowland", "inland", "forest", "open", "wetland",
          "jungle", "steppe", "desert", "tundra", "island_chain", "volcanic", "hills")
# (history._tags; all usable as place wishes. volcanic: the world's volcanoes and young volcanic ground, land.goods,
# glacial and recent epochs only; hills: rolling country, moderate relief under the mountains)


@dataclass
class Lineage:
    id: str
    name: str = ""
    origin: str = "root"  # root | split | arrival | hybrid | template
    parents: list[str] = field(default_factory=list)
    ago_kyr: float = 0.0  # when it appears, splits, arrives, kyr before present
    temp_c: tuple[float, float] = (8.0, 24.0)  # comfort range of the annual mean (soft edges)
    rain_mm: tuple[float, float] = (400.0, 2500.0)  # comfort range of the annual rain (soft edges)
    elev_m: tuple[float, float] | None = None
    prefers: list[str] = field(default_factory=list)
    avoids: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    speed_kmyr: float = 0.5
    persists: bool = False  # keeps living after its last split child
    color: str | None = None
    place: tuple[float, float] | None = None  # arrival: lat, lon
    share: float = 0.1  # template / contact hybrid: share of the hosts' people
    contact: bool = True  # hybrid: exists only where both parents meet
    sites: int = 3  # template: incursion sites
    extinct_kyr: float | None = None  # gone by this long before the present (dwindles over the time before)
    custom: bool = False  # added by the user (the editor marks it), not from a preset
    children: list[str] = field(default_factory=list)  # split children

    @property
    def parent(self) -> str | None:
        return self.parents[0] if self.origin == "split" else None

    @property
    def overlay(self) -> bool:
        """Lives on others' ranges, not a range of its own (templates, contact hybrids)."""
        return self.origin == "template" or (self.origin == "hybrid" and self.contact)

    def trait(self, key: str, default=None):
        """The strongest value of a trait knob over the line's traits."""
        vals = [TRAITS[t][key] for t in self.traits if key in TRAITS.get(t, {})]
        if not vals:
            return default
        return min(vals) if key == "relief" else max(vals)

    def label(self) -> str:
        return self.name or self.id


@dataclass
class Wish:
    a: str
    want: str  # near | apart | one of PLACES
    b: str | None = None
    weight: float = 1.0


@dataclass
class Use:
    """A way of life looking for a good in the land: lines with trait (or preferred place, or the line whose id
    is) `by` favour (weight > 0) or avoid (< 0) the world's `good` (land.GOODS) in their habitat; `pull`
    (0..1, default meta.land_pull) how strongly; `strict`: the habitat off the goods is cut by the pull,
    not renormalised to a mean of 1 over the line's country (history._land_mult)."""
    by: str
    good: str
    weight: float = 1.0
    pull: float | None = None
    strict: bool = False


LAND_PULL = 0.5  # default: habitat x(1 - pull + pull G), G the best of a line's goods (mean 1 over its country)


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

    def uses_of(self, l: Lineage) -> list[tuple[str, float]]:
        """The goods a line looks for (from its traits and preferred places), weights summed per good."""
        out: dict[str, float] = {}
        for u in self._uses_by(l):
            out[u.good] = out.get(u.good, 0.0) + u.weight
        return [(k, v) for k, v in out.items() if v != 0]

    def _uses_by(self, l: Lineage) -> list[Use]:
        return [u for u in self.uses if u.by in l.traits or u.by in l.prefers or u.by == l.id]

    def pull_of(self, l: Lineage) -> float:
        """How strongly a line's land use acts: the strongest pull of its favoured goods (meta.land_pull unless
        a [[use]] gives its own)."""
        ps = [self.land_pull if u.pull is None else u.pull for u in self._uses_by(l) if u.weight > 0]
        return max(ps) if ps else self.land_pull

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


def _check_tag(t, lid):
    if t in GROUPS or t in PLACES or t in KOPPEN_CODES:
        return t
    raise ValueError(f"{lid}: unknown climate or place {t!r} (Köppen codes, {sorted(GROUPS)} or {list(PLACES)})")


def load(path: str | Path) -> Tree:
    p = Path(path)
    raw = json.loads(p.read_text()) if p.suffix == ".json" else tomllib.loads(p.read_text())
    t = parse(raw)
    t.source = str(p)
    return t


def _parents_of(r) -> list[str]:
    ps = r.get("parents")
    if ps is None:
        ps = [r["parent"]] if r.get("parent") else []
    return [str(x) for x in ([ps] if isinstance(ps, str) else ps)]


def parse(raw: dict) -> Tree:
    meta = raw.get("meta", {})
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
        lo, hi = {"root": (0, 0), "arrival": (0, 0), "split": (1, 1), "hybrid": (2, 2), "template": (1, 9)}[origin]
        if not lo <= len(pars) <= hi:
            raise ValueError(f"{lid}: a {origin} line takes {lo}{'' if lo == hi else '+'} parent(s), got {pars}")
        for q in pars:
            if q not in rows:
                raise ValueError(f"{lid}: unknown parent {q!r}")
        bases = [build(q, seen + (lid,)) for q in pars]
        base = bases[0] if bases else Lineage(id="")
        when = next((r[k] for k in ("at", "split", "appears", "arrives", "ago") if k in r), None)
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
        place = r.get("place")
        if place is not None:
            place = (float(place["lat"]), float(place["lon"])) if isinstance(place, dict) else (float(place[0]), float(place[1]))
        l = replace(base, id=lid, name=str(r.get("name", lid)), origin=origin, parents=pars, ago_kyr=ago,
                    temp_c=_pair(r.get("temp_c"), "temp_c") or temp,
                    rain_mm=_pair(r.get("rain_mm"), "rain_mm") or rain,
                    elev_m=_pair(r.get("elev_m"), "elev_m") if "elev_m" in r else base.elev_m,
                    prefers=[_check_tag(x, lid) for x in r.get("prefers", base.prefers)],
                    avoids=[_check_tag(x, lid) for x in r.get("avoids", base.avoids)],
                    traits=traits, speed_kmyr=float(r.get("speed_kmyr", base.speed_kmyr)),
                    persists=bool(r.get("persists", False)), color=r.get("color"), place=place,
                    share=float(r.get("share", 0.1)), contact=bool(r.get("contact", True)),
                    sites=int(r.get("sites", 3)), custom=bool(r.get("custom", False)), children=[],
                    extinct_kyr=parse_ago(r["extinct"]) if r.get("extinct") not in (None, "") else None)
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
    changed = True
    while changed:
        changed = False
        for l in lines.values():
            if l.id not in off and l.origin in ("hybrid", "template") and any(q in off for q in l.parents):
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
    wishes = []
    for w in raw.get("wish", raw.get("wishes", [])):
        want = str(w["want"])
        if w["a"] in off or w.get("b") in off:
            continue
        if w["a"] not in lines or (w.get("b") and w["b"] not in lines):
            raise ValueError(f"wish {w}: unknown lineage")
        if want in ("near", "apart") and not w.get("b"):
            raise ValueError(f"wish {w}: '{want}' needs b")
        if want not in ("near", "apart") and want not in PLACES:
            raise ValueError(f"wish {w}: want must be near, apart or one of {PLACES}")
        wishes.append(Wish(str(w["a"]), want, w.get("b") or None, float(w.get("weight", 1.0))))
    from .land import GOODS
    uses = []
    for u in raw.get("use", raw.get("uses", [])):
        by, good = str(u.get("by", "")), str(u.get("good", u.get("layer", "")))
        if by in off:
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
    t.uses = uses
    t.land_pull = float(meta.get("land_pull", LAND_PULL))
    if not 0 <= t.land_pull <= 1:
        raise ValueError("meta.land_pull must be within 0..1")
    return t


def to_raw(t: Tree) -> dict:
    """The tree back in the input's shape (JSON-able)."""
    out = []
    for l in t.order():
        r = {"id": l.id, "name": l.name, "origin": l.origin, "at": f"{l.ago_kyr:g} kyr"}
        if l.parents:
            r["parents"] = l.parents
        r.update(temp_c=list(l.temp_c), rain_mm=list(l.rain_mm), prefers=l.prefers, avoids=l.avoids,
                 traits=l.traits, speed_kmyr=l.speed_kmyr)
        if l.elev_m is not None:
            r["elev_m"] = list(l.elev_m)
        if l.place is not None:
            r["place"] = list(l.place)
        if l.color:
            r["color"] = l.color
        if l.persists:
            r["persists"] = True
        if l.extinct_kyr is not None:
            r["extinct"] = f"{l.extinct_kyr:g} kyr"
        if l.custom:
            r["custom"] = True
        if l.origin in ("template", "hybrid"):
            r["share"] = l.share
        if l.origin == "hybrid":
            r["contact"] = l.contact
        if l.origin == "template":
            r["sites"] = l.sites
        out.append(r)
    return {"meta": {"name": t.name, "seed": t.seed, "mixing_start": f"{t.mixing_start_kyr:g} kyr", "land_pull": t.land_pull},
            "lineage": out, "wish": [{k: v for k, v in vars(w).items() if v is not None} for w in t.wishes],
            "use": [{k: v for k, v in vars(u).items() if v is not None and v is not False} for u in t.uses]}
