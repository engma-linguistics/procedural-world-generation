"""Settlements and cities v0, with lifecycles (PW-1011): a ledger of sites that rise and fall over the last ~12 kyr.

Output only, like demes.py: reads a finished peoples run and writes `settlements.json` plus `meta.settlements` into it. Nothing in
the history is read back or changed, so the peoples' outcomes are the same with or without it.

The model (every judgement constant is in the block below; `derive(..., **overrides)` and `planet settlements --set` change them):
- Grain: at most one live site per cell, the cell's chief place (a cell is ~12,500 km^2 at L6, ~3,100 at L7). A seeded spot
  within the cell is its position on the globe.
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
  city's two rings, weighted by heads (towns draw people in: the realistic mixing of PW-910). A city-minority group
  (spec cities = true, PW-889) is a quarter of its spec share in a town or city where it is the cell's overlay in that
  frame or lives there at the present.
- Rivers moving: the history keeps the world's present rivers through time, so there is no drainage per frame to read. A
  stand-in: a site on a navigable river in the lowlands (under RIVER_LOW_M) is left at a seeded chance of RIVER_SHIFT per
  kyr ("the river moved away"), as floodplain rivers shift their beds; the cell may be settled again on the new course.
Not modelled in v0: war and raids (a change of hands is recorded, not a battle), placing sites on a regional zoom's terrain."""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from .. import store as S
from .. import timeline as T
from ..geo import R_KM, is_land
from ..grid import shared_grid
from . import landuse as LU
from . import spec as SP
from .demes import _place, landmass_rank

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
    "TOWN_MIN": 2000,       # people: a town (needs the 'towns' tech)
    "CITY_MIN": 10000,      # people: a city (needs the 'cities' tech)
    "TAU_KYR": 0.3,         # a site's people relax toward the target with this time constant
    "ABANDON": 120,         # people: a site whose target stays under this ...
    "ABANDON_STEPS": 3,     # ... for this many steps is abandoned
    "DROUGHT": 0.25,        # rain this far below the rain at its founding makes an abandonment 'drought'
    "RIVER_SHIFT": 0.03,    # per kyr: chance a lowland river site is left because the river moved (a stand-in, see the docstring)
    "RIVER_LOW_M": 300.0,   # m: river sites below this are on a floodplain that can shift
    "HAND_KYR": 1.0,        # an abandonment within this of a change of hands is 'driven out'
    "JITTER": 0.35,         # a site's spot: up to this x the cell spacing from the cell's centre (seeded)
    "SERIES_KEEP": 40,      # points of a site's population series kept
    "QUARTER_MIN_PCT": 2,   # a people under this % of a place is left out of its 'who lives here'
}
TIERS = ("none", "village", "town", "city")
TECH = ("villages", "towns", "cities")
NONE = 255


def tier_of(pop: float, c: dict) -> int:
    return 3 if pop >= c["CITY_MIN"] else 2 if pop >= c["TOWN_MIN"] else 1 if pop >= c["ABANDON"] else 0


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
        wl = json.loads(S.find_world(world).read_text())["layers"]
    except SystemExit:
        return out
    for k in keys:
        if k in wl:
            out[k] = np.nan_to_num(np.asarray(wl[k], float))
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
    Q = {k: np.fromfile(run_dir / eq["layers"][k]["file"], np.uint8).reshape(eq["layers"][k]["shape"]) for k in ("dens", "farm")}
    dens_f = 2.0 ** (Q["dens"].astype(float) * LU.PEOPLE_SCALE) - 1  # people / km2 per window frame
    farm_f = Q["farm"].astype(float) / 100
    rain_f = np.stack([T.frame(run, arr, "precipitation", j).astype(float) for j in fidx])
    W = _world_layers(m.get("world"), n)
    tech = _tech_dates(m, nl)
    mines = _mines_dates(m, nl)
    tree = SP.parse(m["tree"]) if m.get("tree") else None
    city_groups = {l["index"]: (l["group_of"], float(tree.lines[l["id"]].share) if tree is not None and l["id"] in tree.lines else 0.03)
                   for l in lines if l.get("cities")}
    pp = m.get("presence_present")
    pres_now = np.fromfile(run_dir / pp["file"], np.uint8).reshape(pp["shape"]) if pp else None
    rng = np.random.default_rng((int(m.get("try_seed") or 0), 1011))
    present_land = is_land(T.frame(run, arr, "elevation", len(run["frames"]) - 1), T.frame(run, arr, "ice", len(run["frames"]) - 1))
    rank = landmass_rank(g, present_land)
    lms = (m.get("present") or {}).get("landmasses") or []
    ids = [l["id"] for l in lines]
    people_of = {l["index"]: (l.get("group_of") or l["id"]) for l in lines}

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
    active = np.full(n, -1, np.int64)
    streak = np.zeros(n, np.int64)
    low = np.zeros(n, np.int64)
    last_site = np.full(n, -1, np.int64)
    dt = c["STEP_KYR"]
    relax = 1 - np.exp(-dt / c["TAU_KYR"])
    SHARE = np.asarray(c["SHARE"], float)
    caps = np.array([0.0, c["TOWN_MIN"] - 1, c["CITY_MIN"] - 1, np.inf])
    R1, R2 = _ring_index(g, 1), _ring_index(g, 2)  # (n, k) padded with the cell itself
    tieb = 1 + 1e-6 * np.random.default_rng((int(m.get("try_seed") or 0), 1011, 1)).random(n)

    def who(cell, tier, e, dens, step_ago):
        """{people: % of the place's heads}, and the city-minority quarters, for a place of `tier` in `cell`."""
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
        quarters = []
        if tier >= 2:
            for gi, (gof, share) in city_groups.items():
                here = e["peoples_overlay"][cell] == gi or (step_ago == 0 and pres_now is not None and pres_now[gi, cell] > 0)
                if here:
                    quarters.append({"group": ids[gi], "people": gof, "pct": round(100 * share, 1)})
        return {k: v for k, v in pct.items() if v >= c["QUARTER_MIN_PCT"]}, quarters

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
        has = lead != NONE
        lt = np.where(has[:, None], tech[np.minimum(lead, nl - 1)], -1.0)
        tiers_allowed = np.where(has, (lt >= ago - 1e-9).sum(1) * (lt[:, 0] >= ago - 1e-9), 0)  # (villages first: no towns without them)
        tiers_allowed = np.minimum(tiers_allowed, 3)
        hold = np.where(has, mines[np.minimum(lead, nl - 1)] >= ago - 1e-9, False) * e["mix_lead_share"] / 100  # (a mining holder's halls)
        settled_p = dens * area * (farm + c["FISHER_SHARE"] * (1 - farm) * ((W["harbour"] > 0) & e["coastal"] | (W["river_nav"] > 0))
                                   + c["HOLD_SHARE"] * hold)
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
            target = np.maximum(target, np.minimum(tt, caps[t]))
        target = np.where(e["land"], target, 0.0)
        # founding
        free = active < 0
        streak = np.where(free & (target >= c["FOUND"]), streak + 1, 0)
        for cell in np.flatnonzero(free & (streak >= c["FOUND_STEPS"])).tolist():
            h = people_of[int(lead[cell])]
            ang, r = rng.uniform(0, 2 * np.pi), c["JITTER"] * np.sqrt(rng.uniform())
            la, lo = float(g.lat[cell]), float(g.lon[cell])
            sp = np.degrees(g.spacing)
            la2 = float(np.clip(la + r * sp * np.sin(ang), -89.9, 89.9))
            lo2 = float(((lo + r * sp * np.cos(ang) / max(np.cos(np.radians(la)), 0.2)) + 180) % 360 - 180)
            pop = float(max(c["FOUND"], min(target[cell], c["FOUND"] * 2)))
            s = {"id": len(sites), "cell": cell, "lat": round(la2, 3), "lon": round(lo2, 3), "founded_kyr": float(ago), "founded_by": h,
                 "holder": h, "holders": [[float(ago), h]], "abandoned_kyr": None, "why": None,
                 "ruin_of": int(last_site[cell]) if last_site[cell] >= 0 else None, "resettled_as": None,
                 "pop": pop, "peak_pop": pop, "peak_kyr": float(ago), "series": [[float(ago), round(pop)]],
                 "rain0": float(rain[cell]), "_peak_who": None}
            if s["ruin_of"] is not None:
                sites[s["ruin_of"]]["resettled_as"] = s["id"]
            s["_peak_who"] = who(cell, max(tier_of(pop, c), 1), e, dens, ago)
            sites.append(s)
            active[cell] = s["id"]
            last_site[cell] = s["id"]
            streak[cell] = 0
        # growth, change of hands, decline
        for cell in np.flatnonzero(active >= 0).tolist():
            s = sites[active[cell]]
            if s["founded_kyr"] == ago:
                continue
            s["pop"] += (target[cell] - s["pop"]) * relax
            s["series"].append([float(ago), round(s["pop"])])
            if has[cell]:
                h = people_of[int(lead[cell])]
                if h != s["holder"]:
                    s["holder"] = h
                    s["holders"].append([float(ago), h])
            if s["pop"] > s["peak_pop"]:
                if tier_of(s["pop"], c) > tier_of(s["peak_pop"], c):
                    s["_peak_who"] = who(cell, tier_of(s["pop"], c), e, dens, ago)
                s["peak_pop"], s["peak_kyr"] = s["pop"], float(ago)
            low[cell] = low[cell] + 1 if target[cell] < c["ABANDON"] else 0
            why = None
            if e["sea"][cell]:
                why = "the sea rose over it"
            elif e["ice"][cell]:
                why = "the ice came"
            elif W["river_nav"][cell] > 0 and e["elev"][cell] < c["RIVER_LOW_M"] and rng.random() < c["RIVER_SHIFT"] * dt:
                why = "the river moved away"
            elif low[cell] >= c["ABANDON_STEPS"]:
                if rain[cell] < (1 - c["DROUGHT"]) * s["rain0"]:
                    why = "drought"
                elif len(s["holders"]) > 1 and (s["holders"][-1][0] - ago <= c["HAND_KYR"] or tiers_allowed[cell] == 0):
                    why = f"driven out by the {s['holder'].replace('_', ' ')}" if s["holder"] != s["founded_by"] else "its people left"
                elif tiers_allowed[cell] == 0 and has[cell]:
                    why = f"driven out by the {people_of[int(lead[cell])].replace('_', ' ')}"
                else:
                    why = "its people left"
            if why:
                s["abandoned_kyr"], s["why"] = float(ago), why
                s["_end_who"] = None
                active[cell] = -1
                low[cell] = 0
    # the present's 'who lives here' for the living
    e_now = frame_env(len(fago) - 1)
    for s in sites:
        if s["abandoned_kyr"] is None:
            s["_end_who"] = who(s["cell"], max(tier_of(s["pop"], c), 1), e_now, dens_f[-1], 0.0)
    return _document(sites, c, g, ids, rank, lms, steps, area, time.time() - t0)


def _document(sites, c, g, ids, rank, lms, steps, area, secs) -> dict:
    out = []
    by_people: dict[str, dict] = {}
    for s in sites:
        alive = s["abandoned_kyr"] is None
        tier_peak, tier_now = tier_of(s["peak_pop"], c), (tier_of(s["pop"], c) if alive else 0)
        place = _place((s["lat"], s["lon"], int(rank[s["cell"]])), lms)
        who, quarters = (s["_end_who"] if alive else s["_peak_who"]) or ({}, [])
        ser = s["series"]
        if len(ser) > c["SERIES_KEEP"]:
            keep = np.unique(np.r_[np.linspace(0, len(ser) - 1, c["SERIES_KEEP"]).round().astype(int), int(np.argmax([p for _, p in ser]))])
            ser = [ser[i] for i in keep]
        rec = {"id": s["id"], "cell": s["cell"], "lat": s["lat"], "lon": s["lon"], "place": place,
               "tier_peak": TIERS[max(tier_peak, 1)], "tier_now": TIERS[tier_now] if alive else "ruin",
               "founded_kyr": round(s["founded_kyr"], 3), "founded_by": s["founded_by"], "holder": s["holder"],
               "holders": [[round(a, 3), h] for a, h in s["holders"]], "abandoned_kyr": None if alive else round(s["abandoned_kyr"], 3),
               "why": s["why"], "ruin_of": s["ruin_of"], "resettled_as": s["resettled_as"],
               "pop_now": round(s["pop"]) if alive else 0, "peak_pop": round(s["peak_pop"]), "peak_kyr": round(s["peak_kyr"], 3),
               "who": who, "who_when": "now" if alive else "at its height", "quarters": quarters, "series": ser}
        out.append(rec)
        for p, key in ((s["founded_by"], "founded"), (s["holder"] if alive else None, "alive")):
            if p is None:
                continue
            b = by_people.setdefault(p, {"founded": 0, "alive": 0, "ruins": 0, "towns_now": 0, "cities_now": 0, "cities_ever": 0, "largest_now": 0})
            b[key] += 1
        b = by_people[s["founded_by"]]
        if not alive:
            b["ruins"] += 1
        b["cities_ever"] += tier_peak == 3
        if alive:
            bh = by_people[s["holder"]]
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
           "tiers": {"village": [c["ABANDON"], c["TOWN_MIN"]], "town": [c["TOWN_MIN"], c["CITY_MIN"]], "city": [c["CITY_MIN"], None]},
           "sites": out}
    summary = {"file": "settlements.json", "founded": len(out), "alive": len(alive), "ruins": len(out) - len(alive),
               "resettled": sum(r["ruin_of"] is not None for r in out),
               "now": {t: sum(r["tier_now"] == t for r in alive) for t in TIERS[1:]},
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
    if report:  # (a redo replaces the section of run.txt it wrote before)
        p = run_dir / "run.txt"
        old = p.read_text() if p.exists() else ""
        a = old.find("\n## Settlements (PW-1011")
        if a >= 0:
            b = old.find("\n## ", a + 1)
            old = old[:a] + (old[b:] if b >= 0 else "\n")
        S.write_atomic(p, old.rstrip("\n") + "\n" + "\n".join(lines_for_report(d["summary"], d["doc"])) + "\n")
    return d["summary"]


def lines_for_report(sm: dict, doc: dict) -> list[str]:
    L = ["", f"## Settlements (PW-1011 v0): since {sm['from_kyr']:g} kyr ago, {sm['founded']} founded, {sm['alive']} alive now "
             f"({sm['now']['village']} villages, {sm['now']['town']} towns, {sm['now']['city']} cities), {sm['ruins']} ruins, "
             f"{sm['resettled']} on older ruins; {sm['people_in_places_now']:,} people in them now ({sm['generated_in_s']} s)",
         "  why abandoned: " + (", ".join(f"{k} {v}" for k, v in sorted(sm["why"].items(), key=lambda kv: -kv[1])) or "none")]
    for p, b in sm["by_people"].items():
        L.append(f"  {p:<16} founded {b['founded']:>4}, alive {b['alive']:>4} ({b['towns_now']} towns, {b['cities_now']} cities; "
                 f"largest {b['largest_now']:,}), ruins {b['ruins']:>4}, cities ever {b['cities_ever']}")
    big = sorted((r for r in doc["sites"] if r["abandoned_kyr"] is None), key=lambda r: -r["pop_now"])[:8]
    L.append("  -- the largest now")
    L += [f"  {r['tier_now']} of the {r['holder']}, {r['place'] or '?'}: {r['pop_now']:,}, since {r['founded_kyr']:g} kyr; "
          + ", ".join(f"{k} {v}%" for k, v in r["who"].items()) + ("; quarters " + ", ".join(f"{q['group']} {q['pct']}%" for q in r["quarters"]) if r["quarters"] else "")
          for r in big]
    return L
