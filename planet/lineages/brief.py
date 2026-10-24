"""The culinary brief (PW-728): what a region (or a people's range) of a peoples run looks like at an era, as JSON and
Markdown, for the owner's culinary project (docs/proposals/culinary-dnd-intake.md section 7).

    build(run_ref, region=(lat, lon, radius_km) | None, people=id | None, era_kyr=0.0) -> dict   (the contract: BRIEF_VERSION)
    markdown(brief)                                                                         -> str

Built only from what a run and its world hold today: land and biome, climate and seasons, fuels, wild and grown foods,
coast and fish goods, peoples and shares, neighbours, senses and bodies, events and the bad years. What is not modelled
yet (trade reach, reputation, honey, mast, fungi) is present and null, never
invented, so the culinary side can see what is missing. The brief is deterministic: the same run, region and era give
the same text. Everything under `suggested` is rule-based and for the culinary side to overrule.

Which parts depend on the era: the run's frames give the climate class, temperature, rain, tree cover, ice, the peoples,
the crops and animals known and the wild ranges at each era; the world's own layers (soil, biome, rivers, coasts,
growing months, the goods) are those of the world's slice moment, and so are the fuels (the run's present).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from .. import store as S
from .. import timeline as T
from .. import world as W
from ..geo import R_KM
from ..grid import shared_grid
from . import spec as SP

BRIEF_VERSION = 4  # 4: contact history, interfertility tiers and substrate (PW-727); 3: ways of life (PW-723), mineral licks (PW-746)
DEFAULT_RADIUS_KM = 500.0
PRESENCE_MIN = 10  # % of a cell's habitat: a people is present there (presence_present.bin)
RING_KM = 600.0
EVENT_NEAR_KM = 300.0  # events this far past the region's edge count as its own  # how far past the region the neighbours are looked for
KNOWN_SHARE = 0.10  # a crop or animal counts as known in the region when it is known on this share of its land
BAD_YEARS_WINDOW_KYR = 3.0  # droughts and cold spells in this long before the era
EVENT_CAP = 25
MONTHS = 12

NOT_MODELLED = "not modelled yet"
SALT_TRADED_KM = 300.0  # land farther than this from any salt gets its salt by trade, or goes without (a salt-poor interior)


def _popcount(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a).astype(np.int64)
    return sum((a >> b) & 1 for b in range(MONTHS))


def _dist_km(g, lat: float, lon: float) -> np.ndarray:
    la, lo = np.radians(lat), np.radians(lon)
    c = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return np.arccos(np.clip(g.centers @ c, -1, 1)) * R_KM


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
                 "animal_wild", "animal_known", "crop_wild", "crop_known"]
        self.run, self.arr = T.load_frames(self.dir, [n for n in names])
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
    """The cells a people holds at frame i: where it leads or is second (peoples, peoples_whole, mix_*), and at the run's
    present also where its presence is at least PRESENCE_MIN %; a group (no cells of its own in the frames) at an earlier
    era takes its people's range."""
    k = ctx.idx[pid]
    line = ctx.lines[k]
    sel = (ctx.f("mix_lead", i) == k) | (ctx.f("mix_second", i) == k) | (ctx.f("peoples_whole", i) == k) | (ctx.f("peoples", i) == k)
    basis = f"the range of {pid}"
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
    return round(lat, 1), round(lon, 1), round(float(_dist_km(ctx.g, lat, lon)[sel].max()), 0)


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
        d = _dist_km(g, lat, lon)
        sel = d <= rad
        place = {"lat": lat, "lon": lon, "radius_km": rad, "basis": "a circle"}
    elev = ctx.f("elevation", i).astype(float)
    ice = ctx.f("ice", i).astype(float)
    land_all = (elev > 0) | (ice > 0.5)
    land = sel & land_all
    sea = sel & ~land_all
    place["cells"] = int(sel.sum())
    place["land_cells"] = int(land.sum())
    place["area_mkm2"] = round(float(sel.sum()) * 4 * np.pi * R_KM ** 2 / g.n / 1e6, 4)
    place["land_mkm2"] = round(float(land.sum()) * 4 * np.pi * R_KM ** 2 / g.n / 1e6, 4)
    p = m["present"]
    if sel.any():
        dc = _dist_km(g, place["lat"], place["lon"])
        best = min(p.get("landmasses", []), key=lambda lm: float(_dist_km(g, lm["lat"], lm["lon"])[np.argmin(dc)]), default=None)
        place["landmass"] = best["name"] if best else None
    zones = []
    for z in p.get("mixing_zones", []):
        dz = _dist_km(g, z["lat"], z["lon"])
        if sel[int(np.argmin(dz))]:
            zones.append({"lat": z["lat"], "lon": z["lon"], "area_mkm2": z["area_mkm2"], "peoples": z["lines"]})
    brief: dict = {
        "brief_version": BRIEF_VERSION, "run": ctx.dir.name, "world": ctx.world_id,
        "tree": f"{m.get('tree_name')}@{_tree_hash(m)}", "mode": m.get("mode"), "seed": m.get("try_seed"),
        "code": m.get("code"), "era_kyr": era, "era_asked_kyr": era_kyr, "place": place,
    }
    brief["land"] = _land(ctx, i, land, sel)
    brief["bad_years"] = _bad_years(ctx, place, era)
    brief["fuels"] = _fuels(ctx, land, era)
    brief["wild_food"] = _wild_food(ctx, i, land)
    brief["fish"] = _fish(ctx, i, sel, sea, land)
    brief["salt"] = _salt(ctx, land)
    brief["crops"] = _grown(ctx, "crop_known", "crops", i, sel, land)
    brief["animals"] = _grown(ctx, "animal_known", "animals", i, sel, land)
    brief["peoples"] = _peoples(ctx, i, sel)
    brief["animal_foods"] = _animal_foods(brief)
    brief["mixing_zones"] = zones
    brief["substrate"] = _substrate(ctx, brief["peoples"])
    brief["neighbours"] = _neighbours(ctx, i, sel, place)
    brief["trade_reach"] = None
    brief["events"] = _events(ctx, place, era)
    brief["reputation"] = None
    brief["suggested"] = _suggested(brief)
    if people:
        brief["people"] = _people(ctx, people)
    brief["not_modelled"] = {k: NOT_MODELLED for k in ("trade_reach", "reputation", "honey", "mast", "fungi")}
    if brief["substrate"] is None:
        brief["not_modelled"]["substrate"] = "this run has no contact record (made before PW-727)"
    return brief


# -- the parts -----------------------------------------------------------------------------------------
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


def _fuels(ctx: Ctx, land: np.ndarray, era: float) -> dict | None:
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


def _salt(ctx: Ctx, land: np.ndarray) -> dict | None:
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
    out["poor"] = bool(out["km_to_salt"]["mean"] > SALT_TRADED_KM)
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
               "route": None, "origin": None if not first else {"kyr_ago": first["ago_kyr"], "lat": first["lat"], "lon": first["lon"],
                                                              "people": first["line"]}}
        if key == "crops":  # (PW-738: the staples feed the cropland, the cuisine plants flavour and fatten the plate)
            row["kind"] = "staple" if s.get("weight", 0) > 0 else "cuisine"
        out.append(row)
    return sorted(out, key=lambda r: (-(r["since_kyr"] or 0), r["id"]))


LACTASE_FRESH = 0.6  # share of a people who digest fresh milk (body.milk): at or above it milk is drunk fresh, below it soured, curdled and aged
EGG_ANIMALS, NOT_MEAT = ("fowl",), ("dog",)  # (dogs: a pet and a helper before a meal; the canid taboo is not consulted yet, PW-719)


def _animal_foods(brief: dict) -> dict | None:
    """Animals as food goods (PW-719, from the animals known here and the peoples' bodies): meat animals, eggs, dairy animals, and for
    each dairy people whether its milk is drunk fresh or fermented (cheese, yogurt, kefir keep little lactose) by its lactase share."""
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
        out["dairy_peoples"].append({"id": r["id"], "lactase_share": lac, "milk_share": d["milk_share"], "dairy_share": d["dairy_share"],
                                     "animals": d["animals"], "use": "fresh milk, butter and cream" if lac >= LACTASE_FRESH
                                     else "soured and curdled: yogurt, kefir, cheese, butter (the lactose is fermented away)"})
    return out


def _peoples(ctx: Ctx, i: int, sel: np.ndarray) -> dict:
    lead, ls = ctx.f("mix_lead", i), ctx.f("mix_lead_share", i).astype(float)
    sec, ss = ctx.f("mix_second", i), ctx.f("mix_second_share", i).astype(float)
    oth = ctx.f("mix_other_share", i).astype(float)
    peopled = sel & (lead < 255)
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


GROUP_MIN = 0.05  # a group (a way of life inside a people) counts as present in a region from this mean presence


def _groups_here(ctx: Ctx, i: int, sel: np.ndarray, listed: set) -> list:
    """The groups (human herders, steppe orcs...) the composition layers fold into their people: at the present, from the presence
    layer, those with a mean presence of at least GROUP_MIN over the region's peopled cells. Earlier eras have no per-line frames
    (PW-742): empty. Their ways and dairy are what the brief reads."""
    if i != len(ctx.ts) - 1 or not sel.any():
        return []
    pp = np.fromfile(ctx.dir / "layers" / "presence_present.bin", dtype=np.uint8).reshape(len(ctx.lines), -1)
    rows = []
    for l in ctx.lines:
        if l["overlay"] or not l.get("group_of") or l["id"] in listed:
            continue
        share = float(pp[l["index"]][sel].mean()) / 100.0
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
    d = _dist_km(ctx.g, place["lat"], place["lon"])
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
            "tier_note": "tier from split depth (T0 under 10 kyr or the same people, T1 under 1 Myr, T2 under 40 Myr, else T3); border_km is the border of the two peoples (cells of one that touch the other's range without being in it, x cell size), since_kyr their first contact"
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


def _people_contacts(ctx: Ctx, pid: str) -> dict | None:
    """One people's contact record: the other peoples by tier, who it met and when, who held its land before (PW-727)."""
    c = ctx.meta.get("contacts")
    if c is None:
        return None
    pairs = [r for r in c["pairs"] if pid in (r["a"], r["b"])]
    met = [{"id": r["b"] if r["a"] == pid else r["a"], "tier": r["tier"], "first_contact_kyr": r["first_contact_kyr"],
            "years_in_contact": r["years_in_contact"], "in_contact_now": r["in_contact_now"], "border_km_now": r["border_km_now"],
            "border_km_peak": r["border_km_peak"], "mixed_pct_now": r["mixed_pct_now"], "kind": r["kind"], "series": r["series"]}
           for r in sorted(pairs, key=lambda r: (-r["first_contact_kyr"], r["a"], r["b"]))]
    tree = SP.parse(ctx.meta["tree"], ctx.meta.get("mode"))
    tiers: dict[str, list] = {}
    for l in ctx.lines:
        if l["id"] != pid and not l["group_of"] and l["id"] in tree.lines and pid in tree.lines:
            tiers.setdefault(f"T{tree.tier_of(pid, l['id'])}", []).append(l["id"])
    return {"met": met, "children_with": tiers, "substrate": (c.get("substrate") or {}).get(pid),
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
        notes.append(f"salt is far ({sa['km_to_salt']['mean']} km on average" + ("; only the coast itself makes it" if sa['source_share_of_land'].get('sea', 0) > 0 else "") + "): inland it is traded in, dear and rationed; cure with smoke and sour ferments, and "
                     "season with plant ash before salt")
    elif sa and sa["within_100km_share"] >= 0.5 and sa["source_share_of_land"].get("sea", 0) >= 0.3:
        notes.append("the sea is the salt: cheap, so curing, brining and fish sauce are possible")
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
            "story": l.get("story"), "reputation": None, "contacts": _people_contacts(ctx, pid)}


# -- Markdown --------------------------------------------------------------------------------------------
def _kv(d: dict | None, fmt=lambda v: str(v)) -> str:
    return ", ".join(f"{k} {fmt(v)}" for k, v in (d or {}).items()) or "none"


def _pc(v) -> str:
    return f"{100 * v:.0f}%"


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
              f"- Nearest source: {_kv(sa['nearest_source'], _pc)}", f"- Plant ash (fuel good, 0 to 1): {sa['plant_ash']}"]
    else:
        t += ["- no world"]
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
        t += [f"- {r['name']} ({r['id']}): {_pc(r['share'])}" + (f", {r['way'].replace('_', ' ')}" if r.get("way") else "") + (" (group, mean presence)" if r.get("groups_of") and r.get("share") is not None and r in p.get("groups", []) else "") + (", dairy " + json.dumps(r["dairy"]) if r.get("dairy") else ""),
              f"  - body: {'; '.join(SP.body_notes(body)) or 'the human-like baseline'}"]
    if b["mixing_zones"]:
        t += ["", "Mixing zones (where peoples meet): " + "; ".join(f"{z['lat']}, {z['lon']} ({', '.join(map(str, z['peoples']))})" for z in b["mixing_zones"])]
    af = b.get("animal_foods")
    t += ["", "## Animal foods (from the animals known and the peoples' bodies)", ""]
    if af:
        t += ["- Meat animals: " + (", ".join(f"{a['id']} ({_pc(a['known_share'])})" for a in af["meat"]) or "none"),
              "- Eggs: " + (", ".join(f"{a['id']} ({_pc(a['known_share'])})" for a in af["eggs"]) or "none"),
              "- Dairy animals: " + (", ".join(f"{a['id']} ({_pc(a['known_share'])})" for a in af["dairy_animals"]) or "none")]
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
    t += ["", "## Events", ""]
    t += [f"- {e['kyr_ago']} kyr ago ({e['kind']}, {e['km']} km): {e['text']}" for e in b["events"]] or ["- none"]
    if "people" in b:
        q = b["people"]
        t += ["", f"## The people: {q['name']}", "", "- Lineage: " + " <- ".join(f"{c['id']} ({c['origin']}, {c['ago_kyr']} kyr)" for c in q["lineage_chain"]),
              f"- Body: {'; '.join(SP.body_notes(q['body'])) or 'the human-like baseline'}", f"- Present: {_kv(q['present'])}", f"- Homeland: {q['homeland']}", f"- Story: {q['story']}"]
        c = q.get("contacts")
        if c:
            t += ["- Can have children with: " + (", ".join(f"{k} {'/'.join(v)}" for k, v in sorted(c["children_with"].items())) or "none")
                  + " (T0 the same people or under 10 kyr apart; T1 sister peoples; T2 distant; T3 not)"]
            t += [f"- Met {m['id']} ({m['tier']}) {m['first_contact_kyr']} kyr ago, {m['years_in_contact']} yr in contact, border {m['border_km_now']} km now "
                  f"(peak {m['border_km_peak']}), mixed {m['mixed_pct_now']}%, along {m['kind']}" for m in c["met"]]
            sb = c.get("substrate")
            if sb:
                t += ["- Held land before it: " + ("; ".join(f"{r['id']} until {r['held_until_kyr']} kyr ago ({_pc(r['share'])})" for r in sb["held_before"])
                                                   or "nobody (first on its ground)")]
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
