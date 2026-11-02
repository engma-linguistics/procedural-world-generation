"""The culinary brief (PW-728): what a region (or a people's range) of a peoples run looks like at an era, as JSON and
Markdown, for the owner's culinary project (docs/proposals/culinary-dnd-intake.md section 7).

    build(run_ref, region=(lat, lon, radius_km) | None, people=id | None, era_kyr=0.0) -> dict   (the contract: BRIEF_VERSION)
    markdown(brief)                                                                         -> str

Built only from what a run and its world hold today: land and biome, climate and seasons, fuels, wild and grown foods,
coast and fish goods, peoples and shares, neighbours, senses and bodies, events and the bad years. What is not modelled
yet (trade reach, honey, mast, fungi) is present and null, never
invented, so the culinary side can see what is missing. The brief is deterministic: the same run, region and era give
the same text. Everything under `suggested` is rule-based and for the culinary side to overrule.

Which parts depend on the era: the run's frames give the climate class, temperature, rain, tree cover, ice, the peoples,
the crops and animals known and the wild ranges at each era; the world's own layers (soil, biome, rivers, coasts,
growing months, the goods) are those of the world's slice moment, and so are the fuels (the run's present).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np

from .. import store as S
from .. import timeline as T
from .. import world as W
from ..geo import R_KM
from ..grid import shared_grid
from . import mining as MN
from .history import megafauna as MG
from . import salt_reach as SR
from . import spec as SP
from ..geo import is_land, world_land
from .gridops import dist_km
from .spread import graph_dist

BRIEF_VERSION = 16  # 16: gods and food taboos per culture, where the run has gods.json / taboos.json (PW-1306, PW-1305); 15: the emergent cultures in the region (PW-670, cultures.py); 14: mining districts and the mining colonies of incomers (D12); 13: towns and cities from the settlement ledger (PW-1103); 12: interfertility stages (viable, absorbed, sterile, impossible) and the mixed people per contact pair (PW-752); 11: megafauna density natural where no people presses them, and the age of dragons (PW-957); dragons by stage, their food in cattle and the bounty hook (PW-958, PW-961); 10: counted megafauna per pocket (PW-924); 9: salt works and mining colonies instead of a salt-dwarf group (PW-854), hybrid fertility in the contact pairs (PW-851); 8: salt miners (PW-797); 7: salt reach with trade (PW-745); 6: sea peoples (PW-775); 5: reputation and exonyms (PW-731); 4: contact history, interfertility tiers and substrate (PW-727); 3: ways of life (PW-723), mineral licks (PW-746)
DEFAULT_RADIUS_KM = 500.0
PRESENCE_MIN = 10  # % of a cell's habitat: a people is present there (presence_present.bin)
RING_KM = 600.0
EVENT_NEAR_KM = 300.0  # events this far past the region's edge count as its own  # how far past the region the neighbours are looked for
KNOWN_SHARE = 0.10  # a crop or animal counts as known in the region when it is known on this share of its land
BAD_YEARS_WINDOW_KYR = 3.0  # droughts and cold spells in this long before the era
EVENT_CAP = 25
MONTHS = 12

NOT_MODELLED = "not modelled yet"
SALT_POOR_CUT_OFF = 0.25  # salt-poor: this share of a people's land is out of reach of salt even by trade (PW-745)
SALT_TRADED_KM = 300.0  # land farther than this from any salt gets its salt by trade, or goes without (a salt-poor interior)


def _popcount(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a).astype(np.int64)
    return sum((a >> b) & 1 for b in range(MONTHS))


def _mean(x, sel) -> float | None:
    return round(float(np.mean(np.asarray(x, float)[sel])), 3) if sel.any() else None


def _shares(ids: np.ndarray, names: dict, sel: np.ndarray, top: int = 6) -> dict:
    """{name: share of the selected cells} for an id layer, the commonest few."""
    if not sel.any():
        return {}
    v, c = np.unique(np.asarray(ids)[sel].astype(int), return_counts=True)
    order = np.argsort(-c, kind="stable")[:top]
    return {names.get(int(v[k]), str(int(v[k]))): round(float(c[k] / sel.sum()), 3) for k in order}


def _mode_month(a, sel):
    v = np.asarray(a)[sel].astype(int)
    v = v[v > 0]
    return int(np.bincount(v).argmax()) if len(v) else None


def _frost_months(cold: float, warm: float) -> float:
    """Months below 0 C if the year runs as a cosine between the coldest and warmest months (a rough guide)."""
    if cold >= 0:
        return 0.0
    if warm <= 0:
        return 12.0
    return round(12 * float(np.arccos(np.clip((warm + cold) / (warm - cold), -1, 1))) / np.pi, 1)


def _body(l: dict) -> dict:
    """A line's body with every key (a run made before a key existed lacks it: the baseline fills in)."""
    return {**SP.BODY_DEFAULT, **(l.get("body") or {})}


def _tree_hash(meta: dict) -> str:
    return hashlib.sha256(json.dumps(meta.get("tree"), sort_keys=True, default=str).encode()).hexdigest()[:10]


class Ctx:
    """A run, its frames and (if it has one) its world, opened once for any number of briefs."""

    def __init__(self, run_ref):
        self.dir = S.find_run(run_ref)
        names = ["elevation", "ice", "temperature", "climate", "tree_cover", "precipitation", "peoples", "peoples_whole",
                 "mix_lead", "mix_lead_share", "mix_second", "mix_second_share", "mix_other_share",
                 "animal_wild", "animal_known", "crop_wild", "crop_known", "groups_best", "groups_best_pct", "demes"]
        self.run, _ = T.load_frames(self.dir, ())
        self.arr = S.read_layers(self.dir, self.run["layers"], [n for n in names if n in self.run["layers"]])  # (the group layers: runs since PW-742)
        self.meta = self.run["meta"]
        self.g = shared_grid(self.meta["level"])
        self.ts = np.array([f["t"] for f in self.run["frames"]], float)
        self.lines = self.meta["lineages"]
        self.idx = {l["id"]: l["index"] for l in self.lines}
        self.world_id = self.meta.get("world")
        self.world = W.load(S.find_world(self.world_id))["layers"] if self.world_id else None
        self.legend = S.legends()
        self.goods = None
        if self.world_id:
            from . import land as LD
            self.goods = LD.goods(self.world_id)
        self.fuels = None
        fl = (self.meta.get("fuels") or {}).get("layers")
        if fl:
            self.fuels = {k: _read_single(self.dir, spec) for k, spec in fl.items()}
        self._frame_cache: dict = {}
        self._cultures = False  # (cultures.json, or worked out from the demes on first use: cultures())
        self._religion = False  # (gods.json and taboos.json, if the run has them: religion())
        self._overlap = False  # (the presence table and every people's demes on it, on first use: overlap())
        self._presence = False  # (the presence table alone, on first use: presence_table())

    def presence_table(self) -> dict | None:
        """The run's presence table (output.read_presence: every people's cells per frame, PW-1259), None on a run made before it."""
        if self._presence is False:
            from .output import read_presence
            self._presence = read_presence(self.dir, self.meta)
        return self._presence

    def overlap(self) -> tuple | None:
        """(presence table, demes_all) of a run that has every people's demes (lane 109), else None (the leading people's demes only)."""
        if self._overlap is False:
            self._overlap = None
            fa = ((self.meta.get("demes") or {}).get("all") or {}).get("file")
            if fa and (self.dir / fa).exists():
                from .output import read_presence
                pt = read_presence(self.dir, self.meta)
                allv = np.fromfile(self.dir / fa, dtype="<u2")
                if pt is not None and len(pt["cells"]) == len(allv):
                    self._overlap = (pt, allv)
        return self._overlap

    def religion(self) -> tuple[dict | None, dict | None]:
        """(gods.json, taboos.json) of the run, each None where the run has no such file (never derived here: PW-1306, PW-1305)."""
        if self._religion is False:
            self._religion = tuple(json.loads((self.dir / f).read_text()) if (self.dir / f).exists() else None for f in ("gods.json", "taboos.json"))
        return self._religion

    def cultures(self) -> dict | None:
        """The run's emergent cultures (PW-670): its cultures.json, else derived from its demes (not written), None without demes."""
        if self._cultures is False:
            f = self.dir / "cultures.json"
            if f.exists():
                self._cultures = json.loads(f.read_text())
            elif self.meta.get("demes") and "demes" in self.arr:
                from . import cultures as CU
                self._cultures = CU.derive(self.dir)["doc"]
            else:
                self._cultures = None
        return self._cultures

    def frame_at(self, era_kyr: float) -> int:
        return int(np.argmin(np.abs(self.ts - (-era_kyr))))

    def f(self, name: str, i: int) -> np.ndarray:
        key = (name, i)
        if key not in self._frame_cache:
            self._frame_cache[key] = T.frame(self.run, self.arr, name, i)
        return self._frame_cache[key]


def _read_single(run_dir: Path, spec: dict) -> np.ndarray:
    a = np.fromfile(run_dir / spec["file"], dtype=spec["dtype"]).astype(float)
    return a.reshape(-1)


def _names(legend_list, key="name") -> dict:
    return {int(e["id"]): e[key] for e in legend_list}


def _bits(a: np.ndarray, sel: np.ndarray, stocks: dict, share: float, upto_share_of: np.ndarray) -> dict:
    """{stock id: share of the selected cells that carry its bit} for those at or above `share`."""
    out = {}
    n = max(int(upto_share_of.sum()), 1)
    v = np.asarray(a).astype(np.int64)
    for sid, st in stocks.items():
        if not st.get("enabled", True):
            continue
        s = float((((v >> int(st["bit"])) & 1) > 0)[sel].sum()) / n
        if s >= share:
            out[sid] = round(s, 3)
    return out


def _since(ctx: Ctx, layer: str, stock: dict, sel: np.ndarray, land: np.ndarray, i_era: int) -> float | None:
    """kyr ago when the stock first covered KNOWN_SHARE of the region's land (frames up to the era), None if never."""
    n = max(int(land.sum()), 1)
    for i in range(i_era + 1):
        v = (np.asarray(ctx.f(layer, i)).astype(np.int64) >> int(stock["bit"])) & 1
        if float(v[sel & land].sum()) / n >= KNOWN_SHARE:
            return round(-float(ctx.ts[i]), 2)
    return None


def region_of_people(ctx: Ctx, pid: str, i: int) -> tuple[np.ndarray, tuple | None, str]:
    """The cells a people holds at frame i: every cell where it lives, from the presence table (PW-1269: a dragon or giant
    kind that never leads has a range all the same); on a run without the table, where it leads or is second (peoples,
    peoples_whole, mix_*) and at the run's present also where its presence is at least PRESENCE_MIN %. A group (no cells of its
    own in the frames) at an earlier era takes its people's range."""
    k = ctx.idx[pid]
    line = ctx.lines[k]
    basis = f"the range of {pid}"
    pt = ctx.presence_table()
    if pt is not None and 0 <= i < len(pt["offsets"]):
        a, b = int(pt["offsets"][i, k]), int(pt["offsets"][i, k + 1])
        sel = np.zeros(ctx.g.n, bool)
        sel[pt["cells"][a:b].astype(np.int64)] = True
        basis = f"the range of {pid}, every cell where it lives (presence table)"
        if not sel.any() and line.get("group_of") in ctx.idx:
            return region_of_people(ctx, line["group_of"], i)[0], None, f"the range of {pid}'s people, {line['group_of']}"
        return (sel, _centre(ctx, sel), basis) if sel.any() else (sel, (0.0, 0.0, 0.0), basis)
    sel = (ctx.f("mix_lead", i) == k) | (ctx.f("mix_second", i) == k) | (ctx.f("peoples_whole", i) == k) | (ctx.f("peoples", i) == k)
    basis = f"the range of {pid}, where it leads or is second (a run without the presence table)"
    if i == len(ctx.ts) - 1:
        pp = np.fromfile(ctx.dir / "layers" / "presence_present.bin", dtype=np.uint8).reshape(len(ctx.lines), -1)
        sel = sel | (pp[k] >= PRESENCE_MIN)
    elif not sel.any() and line.get("group_of") in ctx.idx:
        return region_of_people(ctx, line["group_of"], i)[0], None, f"the range of {pid}'s people, {line['group_of']}"
    if not sel.any():
        return sel, (0.0, 0.0, 0.0), basis
    return sel, _centre(ctx, sel), basis


def _centre(ctx: Ctx, sel: np.ndarray) -> tuple:
    xyz = ctx.g.centers[sel].mean(axis=0)
    xyz = xyz / max(np.linalg.norm(xyz), 1e-9)
    lat = float(np.degrees(np.arcsin(np.clip(xyz[2], -1, 1))))
    lon = float(np.degrees(np.arctan2(xyz[1], xyz[0])))
    return round(lat, 1), round(lon, 1), round(float(dist_km(ctx.g, lat, lon)[sel].max()), 0)


def build(run_ref, region: tuple | None = None, people: str | None = None, era_kyr: float = 0.0, ctx: Ctx | None = None) -> dict:
    ctx = ctx or Ctx(run_ref)
    g, m = ctx.g, ctx.meta
    i = ctx.frame_at(era_kyr)
    era = round(-float(ctx.ts[i]), 3) + 0.0
    if people:
        if people not in ctx.idx:
            raise SystemExit(f"no people {people!r} in this run (ids: {', '.join(ctx.idx)})")
        sel, cen, basis = region_of_people(ctx, people, i)
        lat, lon, rad = cen or _centre(ctx, sel)
        place = {"lat": lat, "lon": lon, "radius_km": rad,
                 "basis": f"{basis} at {era} kyr ago (its cells; the radius is the farthest one from the centre)"}
    else:
        lat, lon, rad = region if region else (0.0, 0.0, DEFAULT_RADIUS_KM)
        if region is None:
            raise SystemExit("give --region lat,lon[,radius_km] or --people ID")
        d = dist_km(g, lat, lon)
        sel = d <= rad
        place = {"lat": lat, "lon": lon, "radius_km": rad, "basis": "a circle"}
    elev = ctx.f("elevation", i).astype(float)
    ice = ctx.f("ice", i).astype(float)
    land_all = is_land(elev, ice > 0.5)
    land = sel & land_all
    sea = sel & ~land_all
    place["cells"] = int(sel.sum())
    place["land_cells"] = int(land.sum())
    place["area_mkm2"] = round(float(sel.sum()) * 4 * np.pi * R_KM ** 2 / g.n / 1e6, 4)
    place["land_mkm2"] = round(float(land.sum()) * 4 * np.pi * R_KM ** 2 / g.n / 1e6, 4)
    p = m["present"]
    if sel.any():
        dc = dist_km(g, place["lat"], place["lon"])
        best = min(p.get("landmasses", []), key=lambda lm: float(dist_km(g, lm["lat"], lm["lon"])[np.argmin(dc)]), default=None)
        place["landmass"] = best["name"] if best else None
    zones = []
    for z in p.get("mixing_zones", []):
        dz = dist_km(g, z["lat"], z["lon"])
        if sel[int(np.argmin(dz))]:
            zones.append({"lat": z["lat"], "lon": z["lon"], "area_mkm2": z["area_mkm2"], "peoples": z["lines"]})
    brief: dict = {
        "brief_version": BRIEF_VERSION, "run": ctx.dir.name, "world": ctx.world_id,
        "tree": f"{m.get('tree_name')}@{_tree_hash(m)}", "mode": m.get("mode"), "seed": m.get("try_seed"),
        "code": m.get("code"), "era_kyr": era, "era_asked_kyr": era_kyr, "place": place,
    }
    brief["land"] = _land(ctx, i, land, sel)
    brief["bad_years"] = _bad_years(ctx, place, era)
    brief["fuels"] = _fuels(ctx, land, era, i)
    brief["wild_food"] = _wild_food(ctx, i, land)
    brief["fish"] = _fish(ctx, i, sel, sea, land)
    brief["salt"] = _salt(ctx, land, i)
    brief["crops"] = _grown(ctx, "crop_known", "crops", i, sel, land)
    brief["animals"] = _grown(ctx, "animal_known", "animals", i, sel, land)
    brief["peoples"] = _peoples(ctx, i, sel)
    brief["cultures"] = _cultures(ctx, i, land, era)
    brief["sea_peoples"] = _sea_peoples(ctx, i, sel, sea, land_all)
    brief["megafauna"] = _megafauna(ctx, sel, era)
    brief["megafauna_ages"] = (MG.ages_text(ctx.meta["present"].get("megafauna_ages") or {}) or None) if abs(era) <= 1e-6 else None
    brief["animal_foods"] = _animal_foods(brief)
    brief["mixing_zones"] = zones
    brief["substrate"] = _substrate(ctx, brief["peoples"])
    brief["neighbours"] = _neighbours(ctx, i, sel, place)
    brief["mining"] = _mining(ctx, i, sel, land, brief)
    brief["settlements"] = _settlements(ctx, sel, era, people)
    brief["trade_reach"] = None
    brief["events"] = _events(ctx, place, era)
    brief["reputation"] = _reputation(ctx, brief)
    brief["suggested"] = _suggested(brief)
    if people:
        brief["people"] = _people(ctx, people)
    brief["not_modelled"] = {k: NOT_MODELLED for k in ("trade_reach", "honey", "mast", "fungi")}
    if brief["reputation"] is None:
        brief["not_modelled"]["reputation"] = "this run has no reputation table (made before PW-731)"
    if brief["substrate"] is None:
        brief["not_modelled"]["substrate"] = "this run has no contact record (made before PW-727)"
    return brief


# -- the parts -----------------------------------------------------------------------------------------
SETTLE_TOP = 6  # places and ruins listed by name in the brief's towns-and-cities block


def _pop_at(s: dict, ago: float) -> float:
    """A ledger site's people at `ago` kyr (its series, oldest first), 0 before its founding or once it was left."""
    if ago > s["founded_kyr"] + 1e-6 or (s["abandoned_kyr"] is not None and ago <= s["abandoned_kyr"] + 1e-6):
        return 0.0
    sr = s["series"]
    for k in range(1, len(sr)):
        if sr[k][0] <= ago:
            (a0, p0), (a1, p1) = sr[k - 1], sr[k]
            return float(p1 if a0 == a1 else p0 + (p1 - p0) * (a0 - ago) / (a0 - a1))
    return float(sr[-1][1])


def _holder_at(s: dict, ago: float) -> str:
    h = s["founded_by"]
    for a, p in s["holders"]:
        if a >= ago - 1e-6:
            h = p
    return h


def _settlements(ctx: Ctx, sel: np.ndarray, era: float, people: str | None) -> dict | None:
    """The towns and cities of the region at the era, from the settlement ledger (settlements.json, PW-1011): how many of each
    kind, the largest with who lives in them, the towns held by another people than their founders, the
    places of second peoples and the mines, the ruins and what ended them; for a people's brief also its places world-wide."""
    sm = ctx.meta.get("settlements")
    if not sm:
        return None
    if not hasattr(ctx, "_settle"):
        ctx._settle = json.loads((ctx.dir / sm["file"]).read_text())
    doc = ctx._settle
    city = doc["tiers"]["city_min"]
    town = doc["tiers"]["town_min_by_stage"][-1]

    def town_min(s, at):  # the town's size class in force at `at` kyr ago (settlements.py bands, PW-1114: it follows what the holder knows)
        t = town
        for a, tm, _ in s.get("bands") or []:
            if a >= at - 1e-6:
                t = tm
        return t
    name = {l["id"]: re.sub(r" \(.*\)$", "", l["name"]) for l in ctx.lines}

    def tier(s, pop):
        return s["kind"] if s.get("kind") in ("mine", "pit") else "city" if pop >= city else "town" if pop >= town_min(s, era) else "village"

    def row(s, pop):
        h = _holder_at(s, era)
        r = {"id": s["id"], "kind": s.get("kind", "chief"), "tier": tier(s, pop), "people": h, "pop": round(pop), "lat": s["lat"], "lon": s["lon"],
             "place": s.get("place"), "founded_kyr": s["founded_kyr"], "founded_by": s["founded_by"]}
        if abs(era) <= 1e-6:
            r["who"] = s["who"]
        return r

    live, ruins = [], []
    for s in doc["sites"]:
        if not sel[s["cell"]] or era > s["founded_kyr"] + 1e-6:
            continue
        if s["abandoned_kyr"] is not None and era <= s["abandoned_kyr"] + 1e-6:
            if s["tier_now"] == "ruin":
                ruins.append(s)
            continue
        live.append((s, _pop_at(s, era)))
    count: dict = {}
    for s, pop in live:
        count[tier(s, pop)] = count.get(tier(s, pop), 0) + 1
    places = [(s, p) for s, p in live if s.get("kind") not in ("mine", "pit")]
    big = sorted(places, key=lambda sp: -sp[1])[:SETTLE_TOP]
    taken = [(s, p) for s, p in places if _holder_at(s, era) != s["founded_by"] and p >= town_min(s, era)]
    own: dict = {}
    for s, _ in places:
        if s.get("kind") == "minority":
            own[s["founded_by"]] = own.get(s["founded_by"], 0) + 1
    mines: dict = {}
    pits: dict = {}
    colonies: list = []
    for s, p in live:
        if s.get("kind") == "pit":  # (PW-1146: a village's own pit on ordinary ore, counted apart from the districts)
            h = _holder_at(s, era)
            pits[h] = pits.get(h, 0) + 1
        if s.get("kind") == "mine":
            h = _holder_at(s, era)
            mines[h] = mines.get(h, 0) + 1
            if s.get("colony") and h == s["holder"]:  # (D12: a mining town of incomers; the flag is the present's)
                colonies.append({**row(s, p), "district": s.get("district"), "size": "town" if p >= doc["tiers"]["town_min_by_stage"][1] else "village"})
    out = {"basis": f"the settlement ledger (settlements.py, PW-1011) at {era:g} kyr ago: living places in the region's cells; "
                    f"size classes follow what the holding people knows (a town from {min(doc['tiers']['town_min_by_stage'][1:]):,} to {town:,} people, a city from {city:,})",
           "counts": count, "people_in_places": int(sum(p for s, p in places)),
           "largest": [row(s, p) for s, p in big],
           "taken": {"count": len(taken), "list": [{**row(s, p), "held_since_kyr": min(a for a, h in s["holders"] if a >= era - 1e-6)}
                                                 for s, p in sorted(taken, key=lambda sp: -sp[1])[:SETTLE_TOP]]},
           "own_places_of_second_peoples": dict(sorted(own.items(), key=lambda kv: -kv[1])),
           "mines": dict(sorted(mines.items(), key=lambda kv: -kv[1])),
           "pits": dict(sorted(pits.items(), key=lambda kv: -kv[1])),
           "mining_colonies": sorted(colonies, key=lambda r: -r["pop"])[:SETTLE_TOP],
           "ruins": {"count": len(ruins), "why": {}, "largest": [
               {"id": s["id"], "tier": s["tier_peak"], "peak_pop": s["peak_pop"], "people": _holder_at(s, s["abandoned_kyr"]),
                "founded_kyr": s["founded_kyr"], "abandoned_kyr": s["abandoned_kyr"], "why": s["why"], "lat": s["lat"], "lon": s["lon"]}
               for s in sorted(ruins, key=lambda s: -s["peak_pop"])[:SETTLE_TOP]]},
           "names": {}}
    for s in ruins:
        k = "driven out" if (s["why"] or "").startswith("driven out") else s["why"]
        out["ruins"]["why"][k] = out["ruins"]["why"].get(k, 0) + 1
    if people:  # (the people's own places world-wide, at the era; a group's are its people's)
        people = ctx.lines[ctx.idx[people]].get("group_of") or people
        mine_ = [(s, _pop_at(s, era)) for s in doc["sites"] if _holder_at(s, era) == people and _pop_at(s, era) > 0]
        cnt: dict = {}
        for s, p in mine_:
            cnt[tier(s, p)] = cnt.get(tier(s, p), 0) + 1
        top = max((sp for sp in mine_ if sp[0].get("kind") not in ("mine", "pit")), key=lambda sp: sp[1], default=None)
        out["people"] = {"id": people, "counts": cnt, "largest": row(*top) if top else None,
                         "own_places_among_others": sum(s.get("kind") == "minority" for s, _ in mine_),
                         "taken_from_others": sum(s["founded_by"] != people and s.get("kind") not in ("mine", "pit") for s, _ in mine_),
                         "ruins_of_its_founding": sum(1 for s in doc["sites"] if s["founded_by"] == people and s["tier_now"] == "ruin"
                                                      and s["abandoned_kyr"] >= era - 1e-6)}
    used = {r["people"] for r in out["largest"]} | {r["founded_by"] for r in out["largest"]} | set(own) | set(mines) | set(pits) | {r["people"] for r in colonies} | {r["people"] for r in out["ruins"]["largest"]}
    out["names"] = {k: name.get(k, k) for k in sorted(used)}
    return out


def _land(ctx: Ctx, i: int, land: np.ndarray, sel: np.ndarray) -> dict:
    L, leg = ctx.world, ctx.legend
    out: dict = {}
    kn = {int(e["id"]): f"{e['code']} {e['name']}" for e in leg["koppen"]}
    out["koppen"] = _shares(ctx.f("climate", i), kn, land)  # (this era's frame)
    out["temperature_c"] = _mean(ctx.f("temperature", i), land)
    out["precipitation_mm"] = _mean(ctx.f("precipitation", i), land)
    out["tree_cover_pct"] = _mean(ctx.f("tree_cover", i), land)
    out["elevation_m"] = {"mean": _mean(ctx.f("elevation", i), land), "max": round(float(np.max(ctx.f("elevation", i)[land])), 0) if land.any() else None}
    out["ice_share"] = round(float((ctx.f("ice", i)[sel] > 0.5).mean()), 3) if sel.any() else None
    if L is None:
        out["world"] = None
        return out
    out["world_layers_basis"] = "the world's own moment (not this era)"
    out["biome"] = _shares(L["biome"], _names(leg["biomes"]), land)
    out["soil"] = _shares(L["soil"], {int(e["id"]): e["name"] for e in leg["soils"]["types"]}, land)
    fert = np.asarray(L["fertile"], float)
    out["fertile"] = {"mean_0_4": _mean(fert, land), "share_good": round(float((fert[land] >= 3).mean()), 3) if land.any() else None}
    nav = np.asarray(L["river_nav"]).astype(int)
    out["rivers"] = {"navigable": _shares(nav, _names(leg["human_use"]["river_nav"]), land, 4),
                     "max_flow": round(float(np.asarray(L["flow"], float)[land].max()), 1) if land.any() else None,
                     "fresh_water_km_mean": _mean(L["fresh_km"], land), "lake_share": round(float((np.asarray(L["lake"])[land] > 0).mean()), 3) if land.any() else None}
    ck = {int(e["id"]): e["name"] for e in leg["coast"]}
    out["coast"] = _shares(L["coast_type"], ck, sel & (np.asarray(L["coast_type"]) > 0), 4)
    h = np.asarray(L["harbour"]).astype(int)
    out["harbour_best"] = _names(leg["human_use"]["harbour"]).get(int(h[sel].max()), None) if sel.any() else None
    months = _popcount(L["green_months"])
    out["growing_months"] = _mean(months, land)
    cold, warm = _mean(L["cold_month"], land), _mean(L["warm_month"], land)
    out["coldest_month_c"], out["warmest_month_c"] = cold, warm
    out["frost_months_est"] = _frost_months(cold, warm) if land.any() else None
    out["dry_season"] = None
    out["seasons"] = {"temperature_jan_c": _mean(L["temperature_jan"], land), "temperature_jul_c": _mean(L["temperature_jul"], land),
                      "precipitation_jan_mm": _mean(L["precipitation_jan"], land), "precipitation_jul_mm": _mean(L["precipitation_jul"], land)}
    out["fire_months"] = _mean(_popcount(L["fire_months"]), land)
    out["flood_month"] = _mode_month(L["flood_month"], land)
    out["mud_months"] = _mean(L["mud_months"], land)
    out["resources"] = {"salt_deposit_likelihood": _mean(L["res_salt"], land), "coal": _mean(L["res_coal"], land),
                        "peat_depth_m": _mean(L["peat_depth"], land)}
    return out


def _bad_years(ctx: Ctx, place: dict, era: float) -> list:
    out = []
    for e in ctx.meta.get("episodes") or []:
        ago0, ago1 = -e["t0"], -e["t1"]  # kyr ago, start and end
        if not (era - 1e-6 <= ago1 <= era + BAD_YEARS_WINDOW_KYR):
            continue
        if e["kind"] == "cold reversal":
            if np.sign(place["lat"]) != e.get("hemi", 0) or abs(place["lat"]) < 40:
                continue
        else:
            d = _gc(place["lat"], place["lon"], e["lat"], e["lon"])
            if d > place["radius_km"] + e["radius_km"]:
                continue
        row = {"kind": e["kind"], "kyr_ago": round(ago0, 2), "years": int(round((e["t1"] - e["t0"]) * 1000))}
        if e["kind"] == "drought":
            row["rain_x"] = round(1 + e["amp"], 2)
        else:
            row["temperature_c"] = e["amp"]
        out.append(row)
    return sorted(out, key=lambda r: r["kyr_ago"])


def _gc(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance, km."""
    a, b, c, d = map(np.radians, (lat1, lon1, lat2, lon2))
    h = np.sin((c - a) / 2) ** 2 + np.cos(a) * np.cos(c) * np.sin((d - b) / 2) ** 2
    return float(2 * R_KM * np.arcsin(np.sqrt(np.clip(h, 0, 1))))


def _fuels_at(ctx: Ctx, i: int, land: np.ndarray) -> dict | None:
    """The fuels at a stored frame within the run's window of land-use inputs (landuse.frame_inputs; PW-742): the region's mean shares and
    leads, from the frame's settlement, ways, tree cover, animals and crops known and the world's goods; None outside the window."""
    eq = ctx.meta.get("eraq")
    if not eq or i not in eq["frames"] or ctx.goods is None:
        return None
    from . import fuels as FU
    j = eq["frames"].index(i)
    q = {k: np.fromfile(ctx.dir / v["file"], np.uint8).reshape(v["shape"])[j] for k, v in eq["layers"].items()}
    tc = np.asarray(T.frame(ctx.run, ctx.arr, "tree_cover", i), float) / 100.0
    ab = ctx.f("animal_known", i) if "animal_known" in ctx.arr else None
    cb = ctx.f("crop_known", i) if "crop_known" in ctx.arr else None
    sh = FU.at_frame(ctx.meta, ctx.goods, q, tc, ab, cb)
    out = {k: _mean(v, land) for k, v in sh.items()}
    stack = np.stack([sh[k] for k in FU.FUELS])
    lead = np.where(stack.sum(0) > 0, stack.argmax(0), 255).astype(int)
    out["lead"] = _shares(lead, {k: n for k, n in enumerate(FU.FUELS)}, land, 3)
    out["basis"] = (f"this era (the frame {eq['ago_kyr'][j]} kyr ago): its settlement, ways of life, tree cover, herds and crops known; "
                    "the world's own goods (peat, coal, grazing, sea mammals) are those of its slice moment")
    return out


def _fuels(ctx: Ctx, land: np.ndarray, era: float, i: int | None = None) -> dict | None:
    if era > 0 and i is not None:
        at = _fuels_at(ctx, i, land)
        if at is not None:
            return at
    if ctx.fuels is None:
        return None
    out = {k: _mean(v / 100.0, land) for k, v in ctx.fuels.items() if k != "lead"}
    names = (ctx.meta.get("fuels") or {}).get("names") or []
    if "lead" in ctx.fuels and names and land.any():
        lead = ctx.fuels["lead"].astype(int)
        out["lead"] = _shares(lead, {k: n for k, n in enumerate(names)}, land, 3)
    out["basis"] = "the run's present (fuels.py), not this era" if era > 0 else "the run's present (fuels.py)"
    return out


def _wild_food(ctx: Ctx, i: int, land: np.ndarray) -> dict:
    out: dict = {"mast": None, "honey": None, "fungi": None}
    if ctx.goods is not None:
        for k in ("foraging", "grazing", "timber"):
            if k in ctx.goods:
                out[k] = _mean(ctx.goods[k], land)
    st = (ctx.meta.get("animals") or {}).get("stocks") or {}
    wild = _bits(ctx.f("animal_wild", i), land, st, KNOWN_SHARE, land)
    out["game"] = [{"id": k, "label": st[k]["label"], "range_share": v} for k, v in wild.items()]
    sc = (ctx.meta.get("crops") or {}).get("stocks") or {}
    cw = _bits(ctx.f("crop_wild", i), land, sc, KNOWN_SHARE, land)
    out["wild_crops"] = [{"id": k, "label": sc[k]["label"], "range_share": v} for k, v in cw.items()]
    return out


def _fish(ctx: Ctx, i: int, sel: np.ndarray, sea: np.ndarray, land: np.ndarray) -> dict | None:
    L = ctx.world
    if L is None:
        return None
    coastal = sel & (np.asarray(L["coast_type"]) > 0)
    near_sea = sea | coastal
    out = {"basis": "the world's own moment; sea cells inside the region and its coast",
           "sea_cells": int(sea.sum()), "coast_cells": int(coastal.sum()),
           "river_runs": None}
    for k in ("kelp", "reef", "seagrass", "salt_marsh", "mangrove", "upwelling", "seals", "seabirds"):
        if k in L:
            out[k] = _mean(L[k], near_sea)
    out["sst_c"] = _mean(L["sst"], sea)
    out["tide_range_m"] = _mean(L["tide_range"], near_sea)
    if ctx.goods is not None:
        for k in ("coral", "lagoon", "mangrove", "harbour", "storm_coast"):
            if k in ctx.goods:
                out[f"good_{k}"] = _mean(ctx.goods[k], land | coastal)
    if ctx.goods is not None and "_raw" in ctx.goods and "fish" in ctx.goods:
        out.update(_seafood(ctx, land, coastal))
    return out


def _seafood(ctx: Ctx, land: np.ndarray, coastal: np.ndarray) -> dict:
    """The sea's and the rivers' food (PW-732, seafood.py): the goods over the region's coast, the mix of where the fish
    comes from, river runs and big lakes, shellfish and sea mammals."""
    R, G = ctx.goods["_raw"], ctx.goods
    runs, lakes = land & (R["fish_run"] > 0.05), land & (R["fish_lake"] > 0.05)
    out: dict = {}
    for k in ("fish", "shellfish", "sea_mammals"):
        if k in G:
            out[f"coast_{k}"] = _mean(G[k], coastal)
    wet = coastal | runs | lakes  # (cells that fish at all)
    if wet.any():
        w = np.array([R["fish_sea"][wet].sum(), R["fish_run"][wet].sum(), R["fish_lake"][wet].sum()])
        tot = max(float(w.sum()), 1e-9)
        out["fish_mix"] = {"sea": round(float(w[0]) / tot, 3), "river runs": round(float(w[1]) / tot, 3), "lakes": round(float(w[2]) / tot, 3)}
    else:
        out["fish_mix"] = None
    out["river_runs"] = _mean(R["fish_run"], runs) if runs.any() else None
    out["lake_fish"] = _mean(R["fish_lake"], lakes) if lakes.any() else None
    out["sea_mammals"] = {k: _mean(R[k], coastal) for k in ("seals", "whales") if coastal.any()}
    out["shelf"] = None
    return out


def _salt(ctx: Ctx, land: np.ndarray, i: int) -> dict | None:
    """Salt (PW-732, seafood.py): which sources the region has, how far the land is from salt and what the nearest source
    is, plant ash as the fallback. The world's own moment."""
    G = ctx.goods
    if G is None or "_salt_km" not in G or not land.any():
        return None
    R = G["_raw"]
    km, kind = G["_salt_km"][land], G["_salt_kind"][land].astype(int)
    from .seafood import SALT_KINDS, SALT_PARTS, SALT_UNREACHED
    src = {k.replace("salt_", ""): round(float((R[k][land] >= 0.25).mean()), 3) for k in SALT_PARTS}
    out: dict = {"basis": "the world's own moment (seafood.py): land distance to the nearest salt, bent by routes",
                 "source_share_of_land": src,
                 "km_to_salt": {"mean": round(float(km.mean())), "p90": round(float(np.percentile(km, 90))), "max": round(float(km.max()))},
                 "nearest_source": {SALT_KINDS[k]: round(float((kind == k).mean()), 3) for k in range(1, len(SALT_KINDS)) if (kind == k).any()},
                 "unreached_share": round(float((km >= SALT_UNREACHED).mean()), 3),
                 "within_100km_share": round(float((km <= 100).mean()), 3),
                 "beyond_trade_km_share": round(float((km > SALT_TRADED_KM).mean()), 3),
                 "plant_ash": _mean(G["fuel"], land) if "fuel" in G else None}
    out["poor_on_foot"] = bool(out["km_to_salt"]["mean"] > SALT_TRADED_KM)
    rc = _salt_reach(ctx, i)
    if rc is not None:  # PW-745: trade along rivers and contact zones, to a cap
        how, tkm = rc["how"][land], rc["km"][land]
        out["reach"] = {"basis": f"cost-distance to salt: rivers x{SR.RIVER_COST}, contact zones x{SR.TRADE_COST}, capped at {SR.TRADE_CAP_KM:g} km; own = within {SALT_TRADED_KM:g} km on foot, "
                                 "traded = beyond that but inside the cap, cut off = beyond the cap (no salt works or goods yet)",
                        "own_share": round(float((how == 1).mean()), 3), "traded_share": round(float((how == 2).mean()), 3),
                        "cut_off_share": round(float((how == 3).mean()), 3),
                        "traded_km": {"mean": round(float(tkm[how <= 2].mean())) if (how <= 2).any() else None}}
        gain = rc["gain"][land]
        if rc["gain"].any():  # PW-797: land that gets salt only because a mining people works the beds
            out["reach"]["from_mines_share"] = round(float(gain.mean()), 3)
            out["reach"]["basis"] += f"; salt a mining people works is traded {SR.MINED_CAP:g}x further"
        out["poor"] = bool(out["reach"]["cut_off_share"] >= SALT_POOR_CUT_OFF)
    else:
        out["poor"] = out["poor_on_foot"]
    return out


def _salt_reach(ctx: Ctx, i: int) -> dict | None:
    """Whole-grid salt reach at frame i (cached per brief context): salt_reach.reach over the world's land, with the frame's contact zones."""
    key = ("salt_reach", i)
    if key in ctx._frame_cache:
        return ctx._frame_cache[key]
    G, W = ctx.goods, ctx.world
    out = None
    if G is not None and "_salt_km" in G and W is not None and "flow" in W:
        wl = world_land(W)
        zone = SR.contact_zone(ctx.g, wl, ctx.f("peoples", i), _marine_mask(ctx))
        mined, works = _salt_works(ctx, i)
        out = SR.reach(ctx.g, wl, np.asarray(G["_salt_km"], float), np.asarray(W["flow"], float), zone, SALT_TRADED_KM,
                       mined=mined, works=works)
    ctx._frame_cache[key] = out
    return out


def _salt_works(ctx: Ctx, i: int) -> tuple[np.ndarray, np.ndarray]:
    """(mines, works) at frame i (PW-854): the mines are rock-salt beds in the miners' own country plus their colonies (beds held by
    other peoples within MN.COLONY_KM of it); the works are the beds in the country of any other settled people. Whole grid."""
    key = ("salt_works", i)
    if key not in ctx._frame_cache:
        G = ctx.goods
        lead = ctx.f("mix_lead", i).astype(int)
        mar = _marine_mask(ctx)
        settled = (lead != 255) & ~mar[np.minimum(lead, len(mar) - 1)]
        mine = _miner_cells(ctx, i)
        hops = int(np.ceil(MN.COLONY_KM / (ctx.g.spacing * R_KM)))
        d = graph_dist(mine, hops, ctx.g.nbr_off, ctx.g.nbr_idx) if mine.any() else np.full(ctx.g.n, -1)
        mined = MN.worked_salt(G, mine) | MN.colony_cells(G, mine, settled, d >= 0)
        ctx._frame_cache[key] = (mined, MN.settled_works(G, settled, mined))
    return ctx._frame_cache[key]


def _miner_cells(ctx: Ctx, i: int, k: int | None = None) -> np.ndarray:
    """Cells (whole grid, frame i) where a line with the miner trait (or line k) leads, is second or is the strongest group (PW-797)."""
    key = ("miner_cells", i, k)
    if key not in ctx._frame_cache:
        ks = [k] if k is not None else [l["index"] for l in ctx.lines if MN.is_miner(l.get("traits")) and not l["overlay"]]
        out = np.zeros(ctx.g.n, bool)
        layers = [ctx.f("mix_lead", i), ctx.f("mix_second", i)] + ([ctx.f("groups_best", i)] if "groups_best" in ctx.arr else [])
        for a in layers:
            out |= np.isin(a, ks)
        ctx._frame_cache[key] = out
    return ctx._frame_cache[key]


def _mining(ctx: Ctx, i: int, sel: np.ndarray, land: np.ndarray, brief: dict) -> dict | None:
    """Mining peoples of the region (PW-797, mining.py): per line with the miner trait (people or group) the work its country gives it
    (salt, ore, or both), the salt it can sell, what its country lacks (so what it buys back) and the peoples it trades with. The
    world's own moment (the goods are geology)."""
    G = ctx.goods
    if G is None or "salt_rock" not in G or not land.any():
        return None
    mined, works = _salt_works(ctx, i)
    p = brief["peoples"]
    partners = [r["id"] for r in p["list"] if not MN.is_miner(ctx.lines[ctx.idx[r["id"]]].get("traits"))]
    partners += [n["id"] for n in brief["neighbours"]["list"] if n["id"] not in partners and not MN.is_miner(ctx.lines[ctx.idx[n["id"]]].get("traits"))]
    rows = []
    for r in p["list"] + p.get("groups", []):
        l = ctx.lines[ctx.idx[r["id"]]]
        if l["overlay"] or not MN.is_miner(l.get("traits")):
            continue
        w = MN.people_kind(G, land & _miner_cells(ctx, i, l["index"]))
        if w is None or w["kind"] is None:
            continue
        row = {"id": r["id"], "name": r["name"], "kind": w["kind"], "salt_share": w["salt_share"], "ore_share": w["ore_share"]}
        if "salt" in w["kind"]:
            row["sells"] = "rock salt (and the cured foods it makes cheap)"
            row["gets_back"] = w["lacks"] or ["grain, meat, hides and timber from the neighbours' farms and herds (a mining people farms little): the salt pays for it"]
            row["trades_with"] = partners[:4]
        rows.append(row)
    return {"basis": f"lines with the miner trait over the cells where they lead or are second here; a bed is rock salt (good salt_rock) >= {MN.SALT_MIN}, ore a "
                     f"district (>= {MN.ORE_MIN}) of {', '.join(MN.ORE_GOODS)}; a kind needs {MN.HELD_MIN:.0%} of their cells; the mined salt is traded {SR.MINED_CAP:g}x further than unworked salt",
            "list": rows,
            "worked_salt_share_of_land": round(float(MN.worked_salt(G, _miner_cells(ctx, i))[land].mean()), 3),
            # PW-854: salt is something peoples seek, not a subgroup: any settled people works the beds in its country (salt works),
            # and a miner people (dwarves) sends colonies to beds in reach of its own country
            "salt_works": {"basis": f"rock-salt beds (>= {MN.SALT_MIN}) in the country of a settled people: works; of a miner people, or within {MN.COLONY_KM:g} km of it: mines and colonies "
                                    f"(salt traded {SR.MINED_CAP:g}x further than unworked beds, works {SR.WORKS_CAP:g}x)",
                           "mines_and_colonies_share_of_land": round(float(mined[land].mean()), 3),
                           "colony_share_of_land": round(float((mined & ~MN.worked_salt(G, _miner_cells(ctx, i)))[land].mean()), 3),
                           "works_share_of_land": round(float(works[land].mean()), 3)}}


def _route(ctx: Ctx, s: dict, arr: np.ndarray, sel: np.ndarray, land: np.ndarray) -> dict | None:
    """How the region's cells that know a stock at this era came to know it (PW-742): shares by `origin` (the first taming's own ground),
    `road` (the front of use over peopled land) and `sea` (a boat crossing), and the `dominant` one; null for a run made before the route was kept.
    `wing` (carried by birds) is not modelled: nothing in the spread does it."""
    f = s.get("route_file")
    if not f or not (ctx.dir / f).exists():
        return None
    cache = ctx.__dict__.setdefault("_routes", {})
    if f not in cache:
        cache[f] = np.fromfile(ctx.dir / f, np.uint8)
    cells = sel & land & (((arr.astype(np.int64) >> int(s["bit"])) & 1) == 1)
    n = int(cells.sum())
    if not n:
        return None
    out = {name: round(float((cache[f][cells] == v).sum() / n), 3) for v, name in ((1, "origin"), (2, "road"), (3, "sea"))}
    out["dominant"] = max(("origin", "road", "sea"), key=lambda k: out[k])
    return out


def _grown(ctx: Ctx, layer: str, key: str, i: int, sel: np.ndarray, land: np.ndarray) -> list | None:
    st = (ctx.meta.get(key) or {}).get("stocks")
    if not st:
        return None
    known = _bits(ctx.f(layer, i), land, st, KNOWN_SHARE, land)
    out = []
    for sid, share in known.items():
        s = st[sid]
        first = (s.get("tamed") or [None])[0]
        row = {"id": sid, "label": s["label"], "known_share": share, "since_kyr": _since(ctx, layer, s, sel, land, i),
               "route": _route(ctx, s, ctx.f(layer, i), sel, land), "origin": None if not first else {"kyr_ago": first["ago_kyr"], "lat": first["lat"], "lon": first["lon"],
                                                              "people": first["line"]}}
        if key == "crops":  # (PW-738: the staples feed the cropland, the cuisine plants flavour and fatten the plate)
            row["kind"] = "staple" if s.get("weight", 0) > 0 else "cuisine"
        out.append(row)
    return sorted(out, key=lambda r: (-(r["since_kyr"] or 0), r["id"]))


LACTASE_FRESH = 0.6  # share of a people who digest fresh milk (body.milk): at or above it milk is drunk fresh, below it soured, curdled and aged
EGG_ANIMALS, NOT_MEAT = ("fowl",), ("dog",)  # (dogs: a pet and a helper before a meal; the canid taboo is not consulted yet, PW-719)


def _animal_foods(brief: dict) -> dict | None:
    """Animals as food goods (PW-719, from the animals known here and the peoples' bodies): meat animals, eggs, dairy animals, and for
    each dairy people (the dairy animals of its herd x its way of life, PW-784: herders milk, unless body.milks is false) whether its milk
    is drunk fresh or fermented (cheese, yogurt, kefir keep little lactose): the lactase share decides only that, never whether it has dairy."""
    from . import animal_defs as AD
    an = brief.get("animals")
    if an is None:
        return None
    known = {a["id"]: a for a in an}
    dairy_ids = [a.id for a in AD.TABLE if a.dairy and a.id in known]
    out: dict = {"meat": [{"id": k, "known_share": a["known_share"]} for k, a in known.items() if k not in NOT_MEAT],
                 "eggs": [{"id": k, "known_share": known[k]["known_share"]} for k in EGG_ANIMALS if k in known],
                 "dairy_animals": [{"id": k, "known_share": known[k]["known_share"]} for k in dairy_ids], "dairy_peoples": []}
    for r in brief["peoples"]["list"] + brief["peoples"].get("groups", []):
        d = r.get("dairy")
        if not d:
            continue
        milk = r["body"].get("milk", False)
        lac = 1.0 if milk is True else 0.0 if milk is False else float(milk)
        out["dairy_peoples"].append({"id": r["id"], "lactase_share": lac, "milks_share": d["milks_share"], "dairy_share": d["dairy_share"],
                                     "animals": d["animals"], "use": "fresh milk, butter and cream (and cheese)" if lac >= LACTASE_FRESH
                                     else "fermented, not fresh: yogurt, kefir, kumis, cheese, butter (the lactose is fermented away)"})
    return out


def _dairy_line(af: dict) -> str:
    """The brief's dairy-animals line. Animals known on the land are not milk on the plate (PW-850/PW-800): where no people here milks
    (the ruminant peoples' body.milks = false, or no herders), the animals are named as known only and the line says nobody milks them."""
    names = ", ".join(f"{a['id']} ({_pc(a['known_share'])})" for a in af["dairy_animals"])
    if not names:
        return "- Dairy animals: none"
    if not af["dairy_peoples"]:
        return f"- Dairy animals: none milked here (known on the land, but no people of this region milks: {names})"
    return f"- Dairy animals: {names}"


def _peoples(ctx: Ctx, i: int, sel: np.ndarray) -> dict:
    lead, ls = ctx.f("mix_lead", i), ctx.f("mix_lead_share", i).astype(float)
    sec, ss = ctx.f("mix_second", i), ctx.f("mix_second_share", i).astype(float)
    oth = ctx.f("mix_other_share", i).astype(float)
    mar = _marine_mask(ctx)
    peopled = sel & (lead < 255) & ~mar[np.minimum(lead, len(mar) - 1)]  # (the land's peoples: the sea peoples are _sea_peoples')
    n = int(peopled.sum())
    share: dict[int, float] = {}
    for k in np.unique(lead[peopled]).tolist():
        share[k] = share.get(k, 0.0) + float(ls[peopled & (lead == k)].sum())
    m2 = peopled & (sec < 255)
    for k in np.unique(sec[m2]).tolist():
        share[k] = share.get(k, 0.0) + float(ss[m2 & (sec == k)].sum())
    rows = []
    for k, v in sorted(share.items(), key=lambda kv: (-kv[1], kv[0])):
        if n and v / n / 100 >= 0.005:
            l = ctx.lines[k]
            row = {"id": l["id"], "name": l["name"], "share": round(v / n / 100, 3), "groups_of": l["group_of"], "overlay": l["overlay"],
                   "way": l.get("way"), "body": _body(l)}
            dairy = ((ctx.meta.get("animals") or {}).get("dairy") or {}).get(l["id"])
            if dairy:
                row["dairy"] = dairy
            rows.append(row)
    other = float(oth[peopled].sum()) / n / 100 if n else 0.0
    ways: dict[str, float] = {}
    for r in rows:
        if r.get("way") and not r["overlay"]:
            ways[r["way"]] = round(ways.get(r["way"], 0.0) + r["share"], 3)
    groups = _groups_here(ctx, i, sel & (lead < 255), {r["id"] for r in rows})
    return {"ways_of_life": dict(sorted(ways.items(), key=lambda kv: -kv[1])), "groups": groups, "peopled_cells": n, "empty_share": round(1 - n / max(int(sel.sum()), 1), 3), "others_together": round(other, 3), "list": rows,
            "share_basis": "mean over the region's peopled cells of each people's share of the cell's heads (composition, PW-689)"}


def _megafauna(ctx: Ctx, sel: np.ndarray, era: float) -> list | None:
    """PW-924: the counted megafauna (dragons, giants) with a pocket in the region, at the present: '~2 black dragons in this swamp'."""
    mf = ctx.meta["present"].get("megafauna")
    if mf is None or abs(era) > 1e-6:
        return None
    names = {l["id"]: l["name"] for l in ctx.lines}
    out = []
    for lid, r in mf.items():
        here = [p for p in r["pocket_list"] if sel[int(np.argmin(dist_km(ctx.g, p["lat"], p["lon"])))]]
        if here:
            st = [sum(p["stages"][i] for p in here) for i in range(4)] if all("stages" in p for p in here) else None
            out.append({"id": lid, "name": names.get(lid, lid).split(" (")[0], "count": sum(p["count"] for p in here),
                        "pockets": here[:8], "one_per_km2": r["one_per_km2"], "density": MG.density_text(r), "world_count": r["count"],
                        "stages": st, "cattle_yr": sum(p.get("cattle_yr", 0) for p in here) if st else None,
                        "bounty": _bounty(here)})
    return sorted(out, key=lambda x: -x["count"])


def _bounty(pockets: list) -> str | None:
    """PW-961: the adventurer hook. An ancient dragon's yearly kill against the herders' stock inside its own range (its food over
    the prey's sustainable offtake, history.megafauna): where that takes a large share of the herd, the families are ruined and the
    lord posts a bounty. The pocket where an ancient takes the largest share of a herd of at least 20, said so; else None."""
    def herd(p):
        return p["livestock_head"] / max(p["km2"], 1) * p.get("ancient_range_km2", 0)
    ok = [p for p in pockets if p.get("stages") and p["stages"][3] and p.get("livestock_head") and herd(p) >= 20]
    if not ok:
        return None
    best = min(ok, key=herd)
    n, eat = best["stages"][3], best.get("ancient_cattle_yr", 0)
    eat_txt = f"~{eat:.0f} head a year from" if eat else "its kills from"
    return (f"{n} ancient{'s' if n > 1 else ''} in the {best['country']} at {best['lat']:g}, {best['lon']:g}: each takes {eat_txt} the"
            f" ~{herd(best):,.0f} head the herders keep in its ~{best.get('ancient_range_km2', 0):,} km² range; where bounties are posted")


def _marine_mask(ctx: Ctx) -> np.ndarray:
    """Per line index: lives at sea (realm coast or sea, PW-775; a run made before it has none). One extra False at the end."""
    return np.array([l.get("realm", "land") != "land" for l in ctx.lines] + [False], bool)


SEA_FOOD_MIN = 0.2  # a sea good (0..1) from this is a food the people has; the kelp, seal and reef layers (a share of the cell) from SEA_LAYER_MIN
SEA_LAYER_MIN = 0.05
_SEA_BASIS = ("peoples whose realm is the sea: coast (the shore ring of sea cells next to land) or sea (open water); share_of_sea is their share of the "
              "region's sea cells; goods are the world's coastal-life layers over their cells and the land coast they touch (the moment of the world's slice); "
              "foods are the goods at or above a fixed floor; land_contacts is the contact record with the land peoples whose cells it touches now (up to 6, longest border first)")


def _sea_peoples(ctx: Ctx, i: int, sel: np.ndarray, sea: np.ndarray, land_all: np.ndarray) -> dict | None:
    """The peoples of the sea (PW-775; realm coast: the shore ring, realm sea: open water) in the region: the cells of the region
    where each leads or is second (as region_of_people), its share of the region's sea cells, the sea goods over those cells (the
    world's coastal-life layers) and over the land coast they touch (seafood.py: fish, shellfish, sea mammals), the foods that
    makes, and its contact record with the land peoples of that coast. None for a run with no marine line."""
    mar = _marine_mask(ctx)
    ks = [k for k in range(len(ctx.lines)) if mar[k]]
    if not ks:
        return None
    g, L = ctx.g, ctx.world
    pp = None
    if i == len(ctx.ts) - 1:
        pp = np.fromfile(ctx.dir / "layers" / "presence_present.bin", dtype=np.uint8).reshape(len(ctx.lines), -1)
    lead, sec = ctx.f("mix_lead", i), ctx.f("mix_second", i)
    whole, dom = ctx.f("peoples_whole", i), ctx.f("peoples", i)
    elev = ctx.f("elevation", i).astype(float)
    rows = []
    for k in ks:
        mine = (lead == k) | (sec == k) | (whole == k) | (dom == k)
        if pp is not None:
            mine = mine | (pp[k] >= PRESENCE_MIN)
        mc = sel & sea & mine
        if not mc.any():
            continue
        l = ctx.lines[k]
        near = np.logical_or.reduceat(mc[g.nbr_idx], g.nbr_off[:-1])
        coast = land_all & near  # (the land coast it touches, in the region or just past its edge)
        goods: dict = {"sea_cells": int(mc.sum()), "coast_cells": int(coast.sum()), "depth_m": _mean(-elev, mc)}
        if L is not None:
            for key in ("kelp", "reef", "seagrass", "upwelling", "seals", "seabirds"):
                if key in L:
                    goods[key] = _mean(L[key], mc)
            goods["sst_c"] = _mean(L["sst"], mc)
            goods["tide_range_m"] = _mean(L["tide_range"], mc | coast)
        if ctx.goods is not None:
            for key in ("fish", "shellfish", "sea_mammals"):
                if key in ctx.goods and coast.any():
                    goods[f"coast_{key}"] = _mean(ctx.goods[key], coast)
        v = lambda key: goods.get(key) or 0.0  # noqa: E731
        foods = [f for f, on in (("fish", v("coast_fish") >= SEA_FOOD_MIN), ("shellfish", v("coast_shellfish") >= SEA_FOOD_MIN),
                                 ("kelp", v("kelp") >= SEA_LAYER_MIN),
                                 ("seals", v("seals") >= SEA_LAYER_MIN or v("coast_sea_mammals") >= SEA_FOOD_MIN)) if on]
        met = (_people_contacts(ctx, l["id"]) or {}).get("met") or []
        rows.append({"id": l["id"], "name": l["name"], "realm": l["realm"], "way": l.get("way"), "body": _body(l),
                     "share_of_sea": round(float(mc.sum() / max(int(sea.sum()), 1)), 3), "goods": goods, "foods": foods,
                     "land_contacts": sorted((m for m in met if m["in_contact_now"] and not mar[ctx.idx[m["id"]]]),
                                             key=lambda m: (-m["border_km_now"], m["id"]))[:6]})
    rows.sort(key=lambda r: (-r["share_of_sea"], r["id"]))
    return {"list": rows, "basis": _SEA_BASIS}


GROUP_MIN = 0.05  # a group (a way of life inside a people) counts as present in a region from this mean presence


def _groups_here(ctx: Ctx, i: int, sel: np.ndarray, listed: set) -> list:
    """The groups (human herders, steppe orcs...) the composition layers fold into their people: at the present, from the presence
    layer, those with a mean presence of at least GROUP_MIN over the region's peopled cells. At any era in a run with the `groups_best`
    layers (PW-742) the group with most presence in each cell counts there (a group beside a stronger one is not seen); an older run reads
    the present's presence layer and has nothing at earlier eras. Their ways and dairy are what the brief reads."""
    if not sel.any():
        return []
    gb = ctx.f("groups_best", i) if "groups_best" in ctx.arr else None
    gp = ctx.f("groups_best_pct", i).astype(float) if gb is not None else None
    if gb is None and i != len(ctx.ts) - 1:
        return []
    pp = None if gb is not None else np.fromfile(ctx.dir / "layers" / "presence_present.bin", dtype=np.uint8).reshape(len(ctx.lines), -1)
    rows = []
    for l in ctx.lines:
        if l["overlay"] or not l.get("group_of") or l["id"] in listed:
            continue
        share = float(np.where(gb == l["index"], gp, 0.0)[sel].mean()) / 100.0 if gb is not None else float(pp[l["index"]][sel].mean()) / 100.0
        if share < GROUP_MIN:
            continue
        row = {"id": l["id"], "name": l["name"], "share": round(share, 3), "groups_of": l["group_of"], "overlay": False,
               "way": l.get("way"), "body": _body(l)}
        dairy = ((ctx.meta.get("animals") or {}).get("dairy") or {}).get(l["id"])
        if dairy:
            row["dairy"] = dairy
        rows.append(row)
    return sorted(rows, key=lambda r: (-r["share"], r["id"]))


def _neighbours(ctx: Ctx, i: int, sel: np.ndarray, place: dict) -> dict:
    if not sel.any():
        return {"list": []}
    d = dist_km(ctx.g, place["lat"], place["lon"])
    ring = (d > place["radius_km"]) & (d <= place["radius_km"] + RING_KM) & ~sel
    own = set(np.unique(ctx.f("peoples_whole", i)[sel & (ctx.f("peoples_whole", i) < 255)]).tolist())
    whole = ctx.f("peoples_whole", i)
    rows = []
    for k in np.unique(whole[ring & (whole < 255)]).tolist():
        c = int((ring & (whole == k)).sum())
        row = {"id": ctx.lines[k]["id"], "ring_cells": c, "also_in_region": k in own, "border_km": None, "since_kyr": None, "tier": None}
        best = None  # (the longest contact with a people of the region)
        for o in own:
            r = _pair(ctx, ctx.lines[o]["id"], row["id"])
            if r and (best is None or r["border_km_peak"] > best[1]["border_km_peak"]):
                best = (ctx.lines[o]["id"], r)
        if best:
            o, r = best
            row.update(with_people=o, border_km=r["border_km_now"], since_kyr=r["first_contact_kyr"], tier=r["tier"],
                       years_in_contact=r["years_in_contact"], kind=r["kind"])
        rows.append(row)
    rows.sort(key=lambda r: (-r["ring_cells"], r["id"]))
    return {"ring_km": RING_KM, "list": rows[:12],
            "tier_note": "tier from split depth (T0 under 10 kyr or the same people: viable, T1 under 1.1 Myr: fertile young absorbed into a parent people, T2 under 4 Myr: mostly sterile, else T3: no young; PW-752); border_km is the border of the two peoples (cells of one that touch the other's range without being in it, x cell size), since_kyr their first contact"
            if ctx.meta.get("contacts") else "interfertility tiers: " + NOT_MODELLED}


def _pair(ctx: Ctx, a: str, b: str) -> dict | None:
    """The contact record of two peoples (meta.contacts, PW-727), in either order; None without one."""
    for r in (ctx.meta.get("contacts") or {}).get("pairs", []):
        if {r["a"], r["b"]} == {a, b}:
            return r
    return None


def _substrate(ctx: Ctx, peoples: dict) -> dict | None:
    """Who held the region's ground before its present peoples (meta.contacts.substrate): per people here, the peoples
    that held its cells before, with the share of its cells and the median time they lost them (kyr ago)."""
    sub = (ctx.meta.get("contacts") or {}).get("substrate")
    if sub is None:
        return None
    out = {r["id"]: sub[r["id"]] for r in peoples["list"] if r["id"] in sub and not r["overlay"]}
    return {"by_people": out, "basis": "the people holding most of a cell (presence at least 25%) before its present one, at the stored epochs; "
                                         "counts are of the people's whole present range in the run, not only the region"}


def _rep_table(ctx: Ctx) -> dict | None:
    r = (ctx.meta.get("present") or {}).get("reputation")
    return r.get("rows") if r else None


def _rep_row(ctx: Ctx, subject: str, r: dict) -> dict:
    """One reputation row beside what the subject is: the name it is called, why, and its own way and display (PW-731)."""
    l = ctx.lines[ctx.idx[subject]]
    b = l.get("body") or {}
    return {"id": subject, "called": r["name"], "category": r["category"], "valence": r["valence"], "basis": r["basis"],
            "since_kyr": r["since_kyr"], "strength": r["strength"], "lumped_with": r["lumped_with"], "borrowed_from": r.get("borrowed_from"),
            "from_dir": r.get("from_dir"), "actually": {"name": l["name"], "way": l.get("way"), "display": b.get("display"), "tier": r.get("tier")}, "text": r["text"]}


def _reputation(ctx: Ctx, brief: dict) -> dict | None:
    """What the region's peoples call the peoples of the region and its ring of neighbours, kept beside what those are."""
    rows = _rep_table(ctx)
    if rows is None:
        return None
    here = [r["id"] for r in brief["peoples"]["list"]]
    subj = set(here) | {n["id"] for n in brief["neighbours"]["list"]}
    out = {}
    for o in here:
        rs = [_rep_row(ctx, s, r) for s, r in (rows.get(o) or {}).items() if s in subj and s in ctx.idx]
        if rs:
            out[o] = sorted(rs, key=lambda r: (-r["strength"], r["id"]))[:8]
    return {"by_people": out, "basis": "from the contact record: valence from who took whose land (a conquest fades with an e-folding of about 1.5 kyr x the era's scale) or how thin / rich the contact is; the name from the folk category (preset [[exonym]] rows) that best fits the neighbour's body, ancestry, way or arrival. `actually` is what the neighbour is, kept apart from the name"}


def _people_reputation(ctx: Ctx, pid: str) -> dict | None:
    rows = _rep_table(ctx)
    if rows is None:
        return None
    calls = [_rep_row(ctx, s, r) for s, r in (rows.get(pid) or {}).items() if s in ctx.idx]
    by = [_rep_row(ctx, o, v[pid]) for o, v in rows.items() if pid in v and o in ctx.idx]

    def key(r):
        return (-r["strength"], r["id"])
    return {"calls": sorted(calls, key=key), "called_by": sorted(by, key=key)}


def _people_contacts(ctx: Ctx, pid: str) -> dict | None:
    """One people's contact record: the other peoples by tier, who it met and when, who held its land before (PW-727)."""
    c = ctx.meta.get("contacts")
    if c is None:
        return None
    pairs = [r for r in c["pairs"] if pid in (r["a"], r["b"])]
    met = [{"id": r["b"] if r["a"] == pid else r["a"], "tier": r["tier"], "first_contact_kyr": r["first_contact_kyr"],
            "years_in_contact": r["years_in_contact"], "in_contact_now": r["in_contact_now"], "border_km_now": r["border_km_now"],
            "border_km_peak": r["border_km_peak"], "mixed_pct_now": r["mixed_pct_now"], "kind": r["kind"], "series": r["series"],
            **({"stage": r["stage"]} if "stage" in r else {}), **({"mixed_people": r["mixed_people"]} if r.get("mixed_people") else {})}
           for r in sorted(pairs, key=lambda r: (-r["first_contact_kyr"], r["a"], r["b"]))]
    tree = SP.parse(ctx.meta["tree"], ctx.meta.get("mode"))
    tiers: dict[str, list] = {}
    stages: dict[str, list] = {}
    for l in ctx.lines:
        if l["id"] != pid and not l["group_of"] and l["id"] in tree.lines and pid in tree.lines:
            tiers.setdefault(f"T{tree.tier_of(pid, l['id'])}", []).append(l["id"])
            stages.setdefault(tree.stage_of(pid, l["id"]), []).append(l["id"])
    return {"met": met, "children_with": tiers, "children_by_stage": {s: stages[s] for s in SP.STAGES if s in stages},
            "stage_notes": SP.STAGE_NOTES, "substrate": (c.get("substrate") or {}).get(pid),
            "tier_kyr": c["tier_kyr"], "basis": "stored epochs; years_in_contact sums the span each stored epoch stands for (half the gap to its neighbours) in which the two ranges touch"}


def _events(ctx: Ctx, place: dict, era: float) -> list:
    out = []
    for e in ctx.run.get("events") or []:
        ago = -e["t"]
        if ago + 1e-9 < era:
            continue
        d = _gc(place["lat"], place["lon"], e["lat"], e["lon"])
        if d <= place["radius_km"] + EVENT_NEAR_KM:
            out.append({"kyr_ago": round(ago, 2), "kind": e["kind"], "text": e["text"], "km": round(d)})
    out.sort(key=lambda r: (r["kyr_ago"], r["text"]))
    return out[:EVENT_CAP]


def _suggested(brief: dict) -> dict:
    notes = []
    f = brief.get("fuels") or {}
    lead = f.get("lead") or {}
    top = next(iter(lead), None)
    if top == "dung":
        notes.append("dung is the commonest cooking fuel: low slow fires, so boiling, stewing and baking in embers before searing")
    elif top == "wood":
        notes.append("wood is the commonest cooking fuel: open flame is available (roasting, grilling, smoking)")
    elif top == "peat":
        notes.append("peat is the commonest cooking fuel: smoky, steady heat; peat smoke flavours what hangs over it")
    elif top == "straw":
        notes.append("straw and stalks are the commonest cooking fuel: quick hot flashes, poor for slow cooking")
    elif top == "grass":
        notes.append("dry grass and brush are the fuel of last resort here: food is boiled or eaten raw before fuel is spent")
    elif top == "drift":
        notes.append("driftwood and dried seaweed are the commonest fuel: fuel is scarce, so little is cooked long")
    elif top:
        notes.append(f"the commonest cooking fuel is {top}")
    sa, fi = brief.get("salt") or {}, brief.get("fish") or {}
    if sa.get("poor"):
        notes.append(f"salt is far ({sa['km_to_salt']['mean']} km on average" + (f"; {round(100 * sa['reach']['cut_off_share'])}% of the land is out of trade's reach" if sa.get("reach") else "") + ("; only the coast itself makes it" if sa['source_share_of_land'].get('sea', 0) > 0 else "") + "): inland it is traded in, dear and rationed; cure with smoke and sour ferments, and "
                     "season with plant ash before salt")
    elif sa and sa["within_100km_share"] >= 0.5 and sa["source_share_of_land"].get("sea", 0) >= 0.3:
        notes.append("the sea is the salt: cheap, so curing, brining and fish sauce are possible")
    for m in (brief.get("mining") or {}).get("list", []):
        if "salt" not in m["kind"]:
            continue
        also = " and ore" if m["kind"] == "salt and ore" else ""
        notes.append(f"{m['name']} ({m['id']}) mine rock salt{also}: salt is their trade good, so their halls cure and brine freely (salt pork, brined cheese, "
                     f"pickles) and the neighbours ({', '.join(m['trades_with']) or 'whoever comes to trade'}) buy it; they buy back {', '.join(m['gets_back'])}")
    if fi.get("fish_mix") and fi.get("coast_fish") is not None and fi["coast_fish"] >= 0.6:
        notes.append("a rich fishery on this coast: fish is a staple, salted or dried for the lean months")
    grown = [c["id"] for c in brief.get("crops") or []]
    for cid, text in (("olive", "olives are grown here: olive oil is the cooking fat, and the fruit is cured"),
                      ("vine", "vines are grown here: wine and vinegar are within reach"),
                      ("chili", "chili-like peppers are grown here: heat is a local seasoning"),
                      ("spice_tree", "tropical spice trees grow here: pepper-like and cinnamon-like spices are local, and trade goods elsewhere"),
                      ("cane", "sugar cane is grown here: sugar and cane syrup sweeten, and ferment"),
                      ("tea", "tea- and coffee-like plants are grown here: infusions are the everyday drink")):
        if cid in grown:
            notes.append(text)
    if "sap_sugar" in grown and "cane" not in grown:
        notes.append("sap sugar (maple and birch) is the local sweetener: spring boiling, syrups")
    ways = brief["peoples"].get("ways_of_life") or {}
    herd = sum(ways.get(w, 0.0) for w in ("pastoral_nomad", "transhumant", "agro_pastoral"))
    if herd >= 0.25:
        notes.append("herding is a main way of life here (" + ", ".join(w.replace("_", " ") for w in ways if w in ("pastoral_nomad", "transhumant", "agro_pastoral"))
                     + "): the herd is the larder (meat, milk, blood, fat), grain and salt come by trade or the season's move; a feast is a slaughter")
    if ways.get("fisher_forager", 0.0) + ways.get("sea_nomad", 0.0) >= 0.25:
        notes.append("fisher-foragers live here: the catch and the shore are the staples, often settled where the water is rich")
    if ways.get("forager", 0.0) >= 0.5:
        notes.append("foraging is the main way of life here: a broad wild menu by season, little stored")
    dairy = [p["id"] for p in brief["peoples"]["list"] if p.get("dairy")]
    if dairy:
        notes.append(f"dairy herders here ({', '.join(dairy)}): what ferments follows what is stored, so soured milk and cheese before beer")
    elif grown and any(c in grown for c in ("wheat", "foxtail_millet")):
        notes.append("grain is grown here: what ferments follows what is stored, so beer or bread before wine")
    return {"basis": "rule-based from this brief only; the culinary side overrules", "notes": notes, "drink": None}


CULTURES_TOP = 6  # cultures listed in the brief (the most land in the region first)


def _cultures(ctx: Ctx, i: int, land: np.ndarray, era: float) -> list | None:
    """The emergent cultures (PW-670) living on the region's land at the era: name, people, share of the land, what changed. On a run
    with every people's demes (lane 109) a culture counts wherever its people lives, so the shares overlap (a dragon kind's culture
    over the peoples below it); on an older run only where its people leads."""
    doc = ctx.cultures()
    if doc is None or "demes" not in ctx.arr:
        return None
    C, dc = doc["cultures"], np.asarray(doc["deme_culture"], np.int64)
    ov = ctx.overlap()
    if ov is not None:
        pt, allv = ov
        a, b = int(pt["offsets"][i, 0]), int(pt["offsets"][i, -1])
        cell, dem = pt["cells"][a:b].astype(np.int64), allv[a:b].astype(np.int64)
        keep = (dem < len(dc)) & land[cell]
        dem = dem[keep]
    else:
        dem = np.asarray(ctx.arr["demes"][i]).astype(np.int64)
        dem = dem[land & (dem < len(dc))]
    if not len(dem):
        return []

    def at(c):  # (the culture holding it at the era, after any merges by then)
        while C[c]["end"] == "merged" and C[c]["into"] is not None and C[c]["ended_kyr"] is not None and C[c]["ended_kyr"] >= era - 1e-9:
            c = C[c]["into"]
        return c

    u, n = np.unique(dc[dem], return_counts=True)
    tot = {}
    for c, k in zip(u.tolist(), n.tolist()):
        if c >= 0:
            tot[at(c)] = tot.get(at(c), 0) + k
    out = []
    for c, k in sorted(tot.items(), key=lambda x: -x[1])[:CULTURES_TOP]:
        x = C[c]
        out.append({"id": c, "name": x["name"], "people": x["people"], "how": x["how"], "since_kyr": x["born_kyr"], "land_share": round(k / int(land.sum()), 3),
                    "sea_craft": (x["traits"].get("sea_craft") or {}).get("verdict"), "changes": x["changes"]})
        gd, tb = ctx.religion()
        if gd and str(c) in gd["cultures"]:  # (PW-1306: its living gods, the most individuated first)
            bs = sorted((gd["beings"][j] for j in gd["cultures"][str(c)]["living"]), key=lambda b: -b["individuation"])
            out[-1]["gods"] = {"mode": gd["gods_mode"], "beings": [{"label": b["label"], "individuation": b["individuation"], "domains": [t[0] for t in b["top"]],
                                                                    "grants_spells": b["grants_spells"], "bound_to": b["bound_to"]} for b in bs]}
        if tb and str(c) in tb["cultures"]:  # (PW-1305)
            out[-1]["taboos"] = [{k: t[k] for k in ("label", "scope", "origin", "why")} for t in tb["cultures"][str(c)]["taboos"]]
    return out


def _people(ctx: Ctx, pid: str) -> dict:
    l = ctx.lines[ctx.idx[pid]]
    p = ctx.meta["present"]
    chain, cur, seen = [], l, set()
    while cur and cur["id"] not in seen:
        seen.add(cur["id"])
        chain.append({"id": cur["id"], "name": cur["name"], "origin": cur["origin"], "ago_kyr": cur["ago_kyr"]})
        par = cur["parents"][0] if cur["parents"] else None
        cur = ctx.lines[ctx.idx[par]] if par in ctx.idx else None
    st = p["lines"].get(pid) or {}
    return {"id": pid, "name": l["name"], "origin": l["origin"], "parents": l["parents"], "lineage_chain": chain, "groups": l["groups"],
            "group_of": l["group_of"], "overlay": l["overlay"], "way": l.get("way"), "body": _body(l), "started_kyr": l["started_kyr"],
            "ended_kyr": l["ended_kyr"], "extinct_kyr": l["extinct_kyr"], "origin_place": l["origin_place"],
            "demography": l["demography"], "present": {k: st.get(k) for k in ("area_mkm2", "patches", "population", "centroid", "by_landmass")},
            "homeland": (p.get("homeland") or {}).get(pid), "neighbours_present": st.get("neighbours"),
            "story": l.get("story"), "reputation": _people_reputation(ctx, pid), "contacts": _people_contacts(ctx, pid)}


# -- Markdown --------------------------------------------------------------------------------------------
def _kv(d: dict | None, fmt=lambda v: str(v)) -> str:
    return ", ".join(f"{k} {fmt(v)}" for k, v in (d or {}).items()) or "none"


def _pc(v) -> str:
    return f"{100 * v:.0f}%"


def _settlements_md(st: dict | None) -> list[str]:
    if not st:
        return []
    nm = lambda k: st["names"].get(k, k)  # noqa: E731
    c = st["counts"]
    t = ["", "## Towns and cities", "",
         f"- {c.get('city', 0)} cities, {c.get('town', 0)} towns, {c.get('village', 0)} villages, {c.get('mine', 0)} mining districts (one per ring of cells: the pits of one seam) and {c.get('pit', 0)} local pits (a village's own copper or iron pit on ordinary ore); "
         f"{st['people_in_places']:,} people in them; {st['ruins']['count']} ruins"]
    for r in st["largest"]:
        t += [f"- {r['tier']} of the {nm(r['people'])}" + (" (their own place among another people)" if r["kind"] == "minority" else "")
              + f", {r['place'] or f'{r['lat']}, {r['lon']}'}: ~{r['pop']:,} people, founded ~{r['founded_kyr']:g} kyr ago by the {nm(r['founded_by'])}"
              + ("; " + ", ".join(f"{nm(k)} {v}%" for k, v in r["who"].items()) if r.get("who") else "")]
    if st["taken"]["count"]:
        t += [f"- {st['taken']['count']} towns and cities held by another people than their founders: " + "; ".join(
              f"a {r['tier']} of the {nm(r['founded_by'])} held by the {nm(r['people'])} since ~{r['held_since_kyr']:g} kyr ago" for r in st["taken"]["list"])]
    if st["own_places_of_second_peoples"]:
        t += ["- Places of their own among another people: " + ", ".join(f"{nm(k)} {v}" for k, v in st["own_places_of_second_peoples"].items())]
    if st["mines"]:
        t += ["- Mining districts worked by: " + ", ".join(f"{nm(k)} {v}" for k, v in st["mines"].items())]
    for r in st.get("mining_colonies") or []:
        t += [f"  - a mining {r.get('size', 'town')} of {nm(r['people'])}, {r['pop']:,} incomers working the {r.get('district') or 'ore'} district"
              + (f" ({r['place']})" if r.get("place") else "") + f", since {r['founded_kyr']:g} kyr ago"]
    if st["ruins"]["count"]:
        t += ["- Ruins, why abandoned: " + ", ".join(f"{k} {v}" for k, v in sorted(st["ruins"]["why"].items(), key=lambda kv: -kv[1]))]
        t += [f"  - the ruin of a {r['tier']} of the {nm(r['people'])} (at most ~{r['peak_pop']:,} people), {r['lat']}, {r['lon']}: "
              f"founded ~{r['founded_kyr']:g} kyr ago, abandoned ~{r['abandoned_kyr']:g} kyr ago ({r['why']})" for r in st["ruins"]["largest"]]
    pp = st.get("people")
    if pp:
        pc = pp["counts"]
        lg = pp["largest"]
        t += [f"- The {nm(pp['id'])} world-wide: {pc.get('city', 0)} cities, {pc.get('town', 0)} towns, {pc.get('village', 0)} villages, {pc.get('mine', 0)} mines, {pc.get('pit', 0)} local pits"
              f" ({pp['own_places_among_others']} of their own among another people, {pp['taken_from_others']} taken from others); "
              f"{pp['ruins_of_its_founding']} ruins of places they founded"
              + (f"; the largest a {lg['tier']} of ~{lg['pop']:,} at {lg['place'] or f'{lg['lat']}, {lg['lon']}'}" if lg else "")]
    t += [f"- ({st['basis']})"]
    return t


def markdown(b: dict) -> str:
    pl, land = b["place"], b["land"]
    t = [f"# Culinary brief: {pl['lat']}, {pl['lon']} (r {pl['radius_km']:g} km), {b['era_kyr']:g} kyr ago", "",
         f"Run {b['run']} on world {b['world']}, tree {b['tree']} ({b['mode']}), seed {b['seed']}, brief_version {b['brief_version']}. "
         f"Region: {pl['basis']}; {pl['land_cells']} land cells, {pl['land_mkm2']} Mkm2 of land" + (f", on {pl['landmass']}" if pl.get("landmass") else "") + ".", ""]
    t += ["## Land", "",
          f"- Climate: {_kv(land['koppen'], _pc)}; {land['temperature_c']} C mean, {land['precipitation_mm']} mm rain, tree cover {land["tree_cover_pct"]}%, "
          f"elevation {land['elevation_m']['mean']} m (max {land['elevation_m']['max']}), ice {land['ice_share']}"]
    if "biome" in land:
        t += [f"- Biome: {_kv(land['biome'], _pc)}", f"- Soil: {_kv(land['soil'], _pc)}",
              f"- Fertile ground: mean {land['fertile']['mean_0_4']} of 4, {land['fertile']['share_good']} good",
              f"- Rivers: {_kv(land['rivers']['navigable'], _pc)}; fresh water {land['rivers']['fresh_water_km_mean']} km away on average; lakes {land['rivers']['lake_share']}",
              f"- Coast: {_kv(land['coast'], _pc)}; best harbour: {land['harbour_best']}",
              f"- Seasons: {land['growing_months']} growing months, about {land['frost_months_est']} frost months (estimate); "
              f"coldest month {land['coldest_month_c']} C, warmest {land['warmest_month_c']} C; January {land['seasons']['temperature_jan_c']} C and "
              f"{land['seasons']['precipitation_jan_mm']} mm, July {land['seasons']['temperature_jul_c']} C and {land['seasons']['precipitation_jul_mm']} mm; "
              f"fire months {land['fire_months']}, flood month {land['flood_month']}, mud months {land['mud_months']}",
              f"- Resources: {_kv(land['resources'])} (the world's own moment, not this era)"]
    t += ["", "## Bad years", ""]
    t += [f"- {r['kind']} {r['kyr_ago']} kyr ago for {r['years']} years" + (f", rain x{r['rain_x']}" if "rain_x" in r else f", {r['temperature_c']} C") for r in b["bad_years"]] or ["- none in the window"]
    t += ["", "## Fuels", ""]
    f = b["fuels"]
    t += [f"- {_kv({k: v for k, v in f.items() if k not in ('lead', 'basis')})}", f"- Commonest: {_kv(f.get('lead'), _pc)}", f"- ({f['basis']})"] if f else ["- not in this run"]
    w = b["wild_food"]
    t += ["", "## Wild food", "", f"- Goods: foraging {w.get('foraging')}, grazing {w.get('grazing')}, timber {w.get('timber')} (0 to 1 against this world's best)",
          "- Game ranges: " + (", ".join(f"{g['label']} ({_pc(g['range_share'])})" for g in w["game"]) or "none"),
          "- Wild crop ranges: " + (", ".join(f"{g['label']} ({_pc(g['range_share'])})" for g in w["wild_crops"]) or "none"),
          "- Mast, honey, fungi: " + NOT_MODELLED]
    fi = b["fish"]
    t += ["", "## Coast and fish", ""]
    t += [f"- {_kv({k: v for k, v in fi.items() if v is not None and k not in ('basis',)})}"] if fi else ["- no world"]
    sa = b["salt"]
    t += ["", "## Salt", ""]
    if sa:
        t += [f"- Sources over the region's land (share of cells): {_kv(sa['source_share_of_land'], _pc)}",
              f"- Distance to salt: mean {sa['km_to_salt']['mean']} km, p90 {sa['km_to_salt']['p90']} km, max {sa['km_to_salt']['max']} km; "
              f"within 100 km {_pc(sa['within_100km_share'])}; beyond {SALT_TRADED_KM:g} km {_pc(sa['beyond_trade_km_share'])}"
              + (f"; no salt anywhere on the landmass {_pc(sa['unreached_share'])}" if sa["unreached_share"] else ""),
              f"- Nearest source: {_kv(sa['nearest_source'], _pc)}",
              *([f"- Salt reach with trade: own {_pc(sa['reach']['own_share'])}, traded {_pc(sa['reach']['traded_share'])}, cut off {_pc(sa['reach']['cut_off_share'])} of the land"
                 f" (mean {sa['reach']['traded_km']['mean']} km of cost where reached)"
                 + (f", {_pc(sa['reach']['from_mines_share'])} of it only because miners work the beds" if sa["reach"].get("from_mines_share") else "")
                 + f"; salt-poor: {'yes' if sa['poor'] else 'no'}"] if sa.get("reach") else []), f"- Plant ash (fuel good, 0 to 1): {sa['plant_ash']}"]
    else:
        t += ["- no world"]
    mi = b.get("mining")
    if mi and mi["list"]:
        t += ["", "## Mining peoples", ""]
        for m in mi["list"]:
            t += [f"- {m['name']} ({m['id']}): {m['kind']} miners (rock salt on {_pc(m['salt_share'])} of their cells, ore on {_pc(m['ore_share'])})"
                  + (f"; sells {m['sells']}; buys back {', '.join(m['gets_back'])}; trades with {', '.join(m['trades_with']) or 'no one named here'}" if m.get("sells") else "")]
        t += [f"- ({mi['basis']})"]
    t += _settlements_md(b.get("settlements"))
    for key, title, kind in (("crops", "Crops known (staples)", "staple"), ("crops", "Cuisine plants known (fruit, oil, spice, sugar, infusions, greens)", "cuisine"),
                             ("animals", "Animals known", None)):
        t += ["", f"## {title}", ""]
        t += [f"- {c['label']}: {_pc(c['known_share'])} of the land, here since {c['since_kyr']} kyr ago" + (
              f" (first tamed {c['origin']['kyr_ago']} kyr ago by {c['origin']['people']} at {c['origin']['lat']}, {c['origin']['lon']})" if c["origin"] else "")
              for c in b[key] or [] if kind is None or c.get("kind") == kind] or ["- none"]
    p = b["peoples"]
    t += ["", "## Peoples", "", f"- {p['peopled_cells']} peopled cells, {_pc(p['empty_share'])} empty",
          "- Ways of life (share of heads): " + (_kv(p["ways_of_life"], _pc) if p.get("ways_of_life") else "not in this run").replace("_", " ")]
    for r in p["list"] + p.get("groups", []):
        body = r["body"]
        t += [f"- {r['name']} ({r['id']}): {_pc(r['share'])}" + (f", {r['way'].replace('_', ' ')}" if r.get("way") else "") + (f" (culture of {r['groups_of']}, mean presence)" if r.get("groups_of") and r.get("share") is not None and r in p.get("groups", []) else "") + (", dairy " + json.dumps(r["dairy"]) if r.get("dairy") else ""),
              f"  - body: {'; '.join(SP.body_notes(body)) or 'the human-like baseline'}"]
    cu = b.get("cultures")
    if cu:
        t += ["", "## Cultures here (emergent, PW-670; placeholder names)", ""]
        t += [f"- {c['name']} ({c['people']}, {c['how']}, since {c['since_kyr']:g} kyr): lives on {_pc(c['land_share'])} of the land"
              + (f"; {'; '.join(c['changes'])}" if c["changes"] else "") for c in cu]
        for c in cu:
            if c.get("gods") and c["gods"]["beings"]:
                t += [f"  - gods of the {c['name']} ({c['gods']['mode']}): " + "; ".join(
                    f"{g['label']} ({g['individuation']:.2f}{', grants spells' if g['grants_spells'] else ''})" for g in c["gods"]["beings"][:5])]
            if c.get("taboos"):
                t += [f"  - food taboos of the {c['name']}: " + "; ".join(f"{x['label']} ({x['origin']}, {x['scope']})" for x in c["taboos"])]
    mf = b.get("megafauna")
    if mf:
        t += ["", "## Megafauna (counted)", ""]
        for r in mf:
            st = f" ({MG.stages_of(r)}; ~{r['cattle_yr']:,} head of cattle a year)" if r.get("stages") and r["count"] else ""
            t += [f"- ~{r['count']} {r['name']} here{st} ({r['world_count']} in the world, {r['density']}): " + "; ".join(
                  f"{p['count']} in the {p['country']} at {p['lat']:g}, {p['lon']:g} ({p['groups']})" for p in r["pockets"])]
            if r.get("bounty"):
                t += [f"  - {r['bounty']}"]
    if b.get("megafauna_ages"):
        t += [""] + [f"- {x}" for x in b["megafauna_ages"]]
    sp = b.get("sea_peoples")
    if sp and sp["list"]:
        t += ["", "## Sea peoples", ""]
        for r in sp["list"]:
            gd = r["goods"]
            t += [f"- {r['name']} ({r['id']}, {r['realm']} realm): {_pc(r['share_of_sea'])} of the region's sea, {r['way'].replace('_', ' ') if r.get('way') else 'no set way'}"
                  + (f"; sea foods: {', '.join(r['foods'])}" if r["foods"] else "; no sea food above the floor"),
                  f"  - body: {'; '.join(SP.body_notes(r['body'])) or 'the human-like baseline'}",
                  "  - sea goods: " + _kv({k: v for k, v in gd.items() if k not in ("sea_cells", "coast_cells")})]
            t += [f"  - meets {c['id']}: {c['tier']}, since {c['first_contact_kyr']} kyr ago ({c['years_in_contact']} yr), border {c['border_km_now']} km now"
                  + (f", along {c['kind']}" if c.get("kind") else "") for c in r["land_contacts"]]
    if b["mixing_zones"]:
        t += ["", "Mixing zones (where peoples meet): " + "; ".join(f"{z['lat']}, {z['lon']} ({', '.join(map(str, z['peoples']))})" for z in b["mixing_zones"])]
    af = b.get("animal_foods")
    t += ["", "## Animal foods (from the animals known and the peoples' bodies)", ""]
    if af:
        t += ["- Meat animals: " + (", ".join(f"{a['id']} ({_pc(a['known_share'])})" for a in af["meat"]) or "none"),
              "- Eggs: " + (", ".join(f"{a['id']} ({_pc(a['known_share'])})" for a in af["eggs"]) or "none"),
              _dairy_line(af)]
        t += [f"- Dairy people {d['id']} (lactase {_pc(d['lactase_share'])}): {d['use']}" for d in af["dairy_peoples"]]
    else:
        t += ["- not in this run"]
    t += ["", "## Neighbours", ""]
    t += [f"- {n['id']}: {n['ring_cells']} ring cells" + (", also inside" if n["also_in_region"] else "")
          + (f"; with {n['with_people']}: {n['tier']}, in contact since {n['since_kyr']} kyr ago ({n['years_in_contact']} yr), "
             f"border {n['border_km']} km now" + (f", along {n['kind']}" if n.get("kind") else "") if n.get("with_people") else "")
          for n in b["neighbours"]["list"]] or ["- none"]
    if b.get("substrate"):
        t += ["", "## Substrate (who held the land before)", ""]
        t += [f"- {pid}: " + ("; ".join(f"{r['id']} until {r['held_until_kyr']} kyr ago ({_pc(r['share'])} of its cells)" for r in v["held_before"])
                             or "no other people held its cells") + f" ({_pc(v['first_here_share'])} first held by itself)"
              for pid, v in b["substrate"]["by_people"].items()] or ["- none"]
    if b.get("reputation"):
        t += ["", "## What the peoples call their neighbours (and what those are)", ""]
        for o, rs in b["reputation"]["by_people"].items():
            t += [f"- {o}:"] + [f"  - {r['id']} ({r['actually']['name']}, {r['actually']['way'] or 'no set way'}"
                                + (f", {r['actually']['display']}" if r['actually']['display'] not in (None, 'none') else "")
                                + f") is called \"{r['called']}\": {r['valence']}, {r['basis']}"
                                + (f", {r['since_kyr']:g} kyr ago" if r["valence"] in ("feared", "despised") else "") + f", strength {r['strength']}"
                                + (f"; lumped with {', '.join(r['lumped_with'])}" if r["lumped_with"] else "") for r in rs]
    t += ["", "## Events", ""]
    t += [f"- {e['kyr_ago']} kyr ago ({e['kind']}, {e['km']} km): {e['text']}" for e in b["events"]] or ["- none"]
    if "people" in b:
        q = b["people"]
        t += ["", f"## The people: {q['name']}", "", "- Lineage: " + " <- ".join(f"{c['id']} ({c['origin']}, {c['ago_kyr']} kyr)" for c in q["lineage_chain"]),
              f"- Body: {'; '.join(SP.body_notes(q['body'])) or 'the human-like baseline'}", f"- Present: {_kv(q['present'])}", f"- Homeland: {q['homeland']}", f"- Story: {q['story']}"]
        c = q.get("contacts")
        if c:
            bs = c.get("children_by_stage") or {}
            t += ["- Children with other peoples (by how long ago they split, PW-752): "
                  + ("; ".join(f"{k} ({c['stage_notes'][k]}): {', '.join(v)}" for k, v in bs.items() if k != "impossible") or "none")
                  + ("; impossible with the rest" if "impossible" in bs else "")]
            t += [f"- Met {m['id']} ({m['tier']}) {m['first_contact_kyr']} kyr ago, {m['years_in_contact']} yr in contact, border {m['border_km_now']} km now "
                  f"(peak {m['border_km_peak']}), mixed {m['mixed_pct_now']}%, along {m['kind']}" for m in c["met"]]
            sb = c.get("substrate")
            if sb:
                t += ["- Held land before it: " + ("; ".join(f"{r['id']} until {r['held_until_kyr']} kyr ago ({_pc(r['share'])})" for r in sb["held_before"])
                                                   or "nobody (first on its ground)")]
    if "people" in b and (b["people"].get("reputation") or {}).get("calls") is not None:
        rp = b["people"]["reputation"]
        t += ["", "### Names (PW-731)", ""]
        t += [f"- calls {r['id']} \"{r['called']}\" ({r['valence']}, {r['basis']})" for r in rp["calls"]] or ["- calls nobody anything special"]
        t += [f"- is called \"{r['called']}\" by {r['id']} ({r['valence']}, {r['basis']})" for r in rp["called_by"]]
    t += ["", "## Suggested (rule-based, overrule freely)", ""] + [f"- {n}" for n in b["suggested"]["notes"]]
    t += ["", "## Not modelled yet (null in the JSON)", "", "- " + ", ".join(b["not_modelled"]), ""]
    return "\n".join(t)


DEFAULT_ERAS = (0.0, 0.5, 1.0, 2.0, 3.0, 6.0, 9.0, 12.0)  # kyr ago: the era slices of --all (the nearest stored frame each; repeats are dropped)


def all_briefs(run_ref, out_dir, eras=DEFAULT_ERAS, log=print) -> list[Path]:
    """PW-742 --all: one brief per people (peoples and groups, not overlays) at each era slice, and per mixing zone at the present,
    into out_dir/<run>/ as people_<id>_<era>kyr and zone_<lat>_<lon>_present (.json and .md). A Ctx opens the run once.
    A people with no cells at an era is skipped (a group falls back to its people's range; place.basis says so)."""
    ctx = Ctx(run_ref)
    out = Path(out_dir) / ctx.dir.name
    out.mkdir(parents=True, exist_ok=True)
    frames, written = [], []
    for e in eras:
        i = ctx.frame_at(e)
        if i not in frames:
            frames.append(i)
    for i in frames:
        era = round(-float(ctx.ts[i]), 3) + 0.0
        for l in ctx.lines:
            if l["overlay"]:
                continue
            if not region_of_people(ctx, l["id"], i)[0].any():
                continue
            b = build(ctx.dir.name, people=l["id"], era_kyr=era, ctx=ctx)
            stem = f"people_{l['id']}_{era:g}kyr"
            (out / f"{stem}.json").write_text(dumps(b))
            (out / f"{stem}.md").write_text(markdown(b))
            written.append(out / f"{stem}.json")
    for z in ctx.meta["present"].get("mixing_zones", []):
        rad = max(150.0, round(float(np.sqrt(z["area_mkm2"] * 1e6 / np.pi)), -1))
        b = build(ctx.dir.name, region=(z["lat"], z["lon"], rad), era_kyr=0.0, ctx=ctx)
        stem = f"zone_{z['lat']:g}_{z['lon']:g}_present"
        (out / f"{stem}.json").write_text(dumps(b))
        (out / f"{stem}.md").write_text(markdown(b))
        written.append(out / f"{stem}.json")
    log(f"{len(written)} briefs in {out}")
    return written


def dumps(b: dict) -> str:
    return json.dumps(b, indent=1, sort_keys=False, default=lambda o: o.item() if hasattr(o, "item") else str(o))
