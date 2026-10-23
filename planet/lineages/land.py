"""What the land gives a people: the world's game layers as 0..1 'goods' per cell, and homeland notes.

A finished world carries (or can have added) game attributes (gameattrs.py: grazing, foraging, timber,
fuel, building ground), farmland (humanuse.py's `fertile`), harbours (humanuse.py, at sea), resources
(resources.py: res_* likelihoods, the best building stone) and coast forms (coastform.py: coast type,
seabirds, seals, navigation hazards). The resource and coast layers are add-on commands (`planet resources`,
`planet coast`); a world without them gets them worked out here, in memory (never written to the world).

Each good is scaled to 0..1 against this world's own best (planet-relative: the richest 5% of the land with
any of it count as 1), and the point-like ones (ores, coast forms, harbours) reach one cell ring inland
(at `REACH` of their value), so a people favouring them settles the country around them. The spec's [[use]] table says which
way of life looks for which good (spec.USES); history.History applies it to the habitat.

    goods(world_ref)                 -> {good: 0..1 per cell}, plus the raw layers for the notes ('_raw')
    homeland_notes(h, P, goods, ...) -> {line: [sentence, ...]}
"""

from __future__ import annotations

import time

import numpy as np

from ..geo import R_KM, world_land

REACH = 0.7  # an ore district's or a coast's good reaches one cell ring inland at this share (a people settles around it)
DISTRICT_MIN = 0.5  # cells at or above this make a district (resources.DISTRICT_MIN)
# resources.STONE id -> 0..1: granite and marble best, then quartzite, gneiss, limestone, slate, sandstone, basalt, tuff
GOOD_STONE = {1: 1.0, 2: 1.0, 9: 0.8, 8: 0.6, 3: 0.5, 5: 0.5, 4: 0.4, 6: 0.3, 7: 0.2}

# good -> (what it is, in the notes; geology: valid in glacial epochs too, not only the last HOLOCENE_KYR)
GOODS = {
    "fertile": ("farmland", False),
    "grazing": ("pasture", False),
    "foraging": ("wild food", False),
    "timber": ("timber", False),
    "fuel": ("firewood", False),
    "building": ("firm building ground", True),
    "stone": ("good building stone", True),
    "metal": ("metal ores", True),
    "gold": ("gold", True),
    "iron": ("iron", True),
    "copper": ("copper", True),
    "tin": ("tin", True),
    "gems": ("gems", True),
    "mithril": ("mithril and adamant (fantasy)", True),
    "coal": ("coal", True),
    "harbour": ("natural harbours", False),
    "nav_hazard": ("reefs, shoals and sea ice offshore", False),
    "coral": ("coral coast", False),
    "lagoon": ("lagoons behind barrier islands", False),
    "mangrove": ("mangrove coast", False),
    "cliff": ("sea cliffs", False),
    "seabirds": ("seabird cliffs", False),
    "seals": ("seal haul-outs", False),
}
# ores and the like: counted as districts (connected cells >= DISTRICT_MIN) in the notes; the rest by area
DISTRICTS = {"gold", "iron", "copper", "tin", "gems", "mithril", "coal", "metal", "harbour", "seabirds", "seals", "coral"}
_ORES = {"gold": ("orogenic_au", "epithermal_au", "placer_au"), "iron": ("bif_fe",),
         "copper": ("porphyry_cu", "vms", "sed_pbzn"), "tin": ("sn_w", "placer_sn"), "gems": ("diamond", "gem_meta"),
         "mithril": ("x_mithril", "x_adamant", "x_star_iron"), "coal": ("coal",)}
LIVING = ("fertile", "grazing", "foraging", "timber", "fuel", "building")  # scaled to the world's best
MISSING_SHARE = 0.02  # a living good on less than this share of the land (at 1/10 of its scale) is missing
_CACHE: dict = {}


def _nbr(grid, ufunc, vals):
    return ufunc.reduceat(vals, grid.nbr_off[:-1])


def _reach(grid, v):
    """A district's good reaches the next cell ring at REACH of its value (the country around it)."""
    return np.maximum(v, REACH * _nbr(grid, np.maximum, v[grid.nbr_idx]))


def _rel(v, land):
    """0..1 against this world's own best: the 95th percentile of the land cells that have any."""
    x = v[land & (v > 0)]
    top = float(np.percentile(x, 95)) if len(x) else 1.0
    return np.clip(v / max(top, 1e-9), 0, 1)


def _layers(world_ref: str):
    from .. import coastform as CF
    from .. import gameattrs as G
    from .. import resources as RS
    from .. import store as S
    from .. import world as W
    w = W.load(S.find_world(world_ref))
    g, L, m = w["grid"], dict(w["layers"]), w["meta"]
    made = []
    if "grazing" not in L:
        orb = m.get("orbit") if isinstance(m.get("orbit"), dict) else {}
        L.update(G.world_layers(g, L, float(orb.get("obliquity", 23.4))))
        made.append("game attributes")
    if "res_orogenic_au" not in L:
        hist = None
        if m.get("source_run") and S.exists("run", m["source_run"]):
            hist = RS.history(S.find_run(m["source_run"]), float(m["t_myr"]), g, log=None)
        L.update(RS.world_layers(g, L, m, hist))
        made.append("resources" + (" (with the run's history)" if hist is not None else ""))
    if "coast_type" not in L:
        L.update(CF.world_layers(g, L, m))
        made.append("coast forms")
    return g, L, made


def goods(world_ref: str | None) -> dict | None:
    """{good: 0..1 per cell} for a world (cached per process), or None without a world."""
    if not world_ref:
        return None
    if world_ref in _CACHE:
        return _CACHE[world_ref]
    from .. import coastform as CF
    t0 = time.time()
    g, L, made = _layers(world_ref)
    f = lambda k: np.asarray(L[k], float) if k in L else np.zeros(g.n)  # noqa: E731
    land = world_land(L)
    sea = ~land
    raw = {}
    raw["fertile"] = f("fertile") / 4.0
    for k in ("grazing", "foraging", "timber", "fuel", "building"):
        raw[k] = f(k) / 5.0
    raw["stone"] = np.vectorize(lambda s: GOOD_STONE.get(int(s), 0.0), otypes=[float])(f("stone"))
    for k, keys in _ORES.items():
        raw[k] = np.max([f(f"res_{x}") for x in keys], axis=0)
    raw["metal"] = np.max([raw[k] for k in ("gold", "iron", "copper", "tin")]
                          + [f(f"res_{x}") for x in ("magmatic_ni", "laterite_ni", "bauxite", "ree")], axis=0)
    # at sea: harbours and hazards, carried to the coast's land cells (the best harbour, the mean hazard offshore)
    coast = land & _nbr(g, np.logical_or, sea[g.nbr_idx])
    hb = np.where(sea, f("harbour") / 3.0, 0.0)
    raw["harbour"] = np.where(coast, _nbr(g, np.maximum, hb[g.nbr_idx]), 0.0)
    nh = np.where(sea, f("nav_hazard"), 0.0)
    cnt = np.maximum(_nbr(g, np.add, sea[g.nbr_idx].astype(float)), 1)
    raw["nav_hazard"] = np.where(coast, _nbr(g, np.add, nh[g.nbr_idx]) / cnt, 0.0)
    ct = f("coast_type").astype(int)
    raw["coral"] = (ct == CF.KEYS["coral"]).astype(float)
    raw["lagoon"] = np.where(ct == CF.KEYS["barrier"], 1.0, 0.5 * f("barrier"))
    raw["mangrove"] = (ct == CF.KEYS["mangrove"]).astype(float)
    raw["cliff"] = np.maximum(np.isin(ct, (CF.KEYS["cliff"], CF.KEYS["fjord"])).astype(float), f("cliff"))
    raw["seabirds"], raw["seals"] = f("seabirds"), f("seals")
    out, missing = {}, []
    for k, v in raw.items():
        v = np.where(land, v, 0.0)
        if k in LIVING and (v[land] >= 0.1).mean() < MISSING_SHARE:
            missing.append(k)  # (a world whose plants lack it, e.g. no grasses: the good is left out, not stretched)
            continue
        if k in LIVING:
            out[k] = _rel(v, land)
        else:  # (likelihoods and classes: already 0..1; point-like, so they reach the country around)
            out[k] = np.where(land, _reach(g, v), 0.0)
    out["_raw"] = {k: np.where(land, v, 0.0) for k, v in raw.items()}
    out["_land"] = land
    out["_made"] = made
    out["_missing"] = missing
    out["_s"] = round(time.time() - t0, 1)
    _CACHE[world_ref] = out
    return out


# -- homeland notes ----------------------------------------------------------------------------------
LANDMARKS = ("mountain_range", "plateau", "great_forest", "savanna", "desert", "rainforest", "wetland", "lake",
             "inland_sea", "largest_river", "inland_basin", "fjords", "hotspot_islands", "atolls", "mediterranean",
             "rift", "ice_sheet")


def landmarks(world_ref: str | None) -> list[dict]:
    """The world's highlight features usable as place names (highlights.find, in memory)."""
    if not world_ref:
        return []
    key = ("_marks", world_ref)
    if key not in _CACHE:
        try:
            from .. import highlights as H
            from .. import store as S
            from .. import world as W
            fs = H.find(W.load(S.find_world(world_ref)))
            _CACHE[key] = [f for f in fs if f.get("kind") in LANDMARKS]
        except Exception:  # (names are a nicety: a world the highlights can't read gets directions)
            _CACHE[key] = []
    return _CACHE[key]


def _dir(lat, lon):
    return f"{abs(lat):.0f}°{'N' if lat >= 0 else 'S'} {abs(lon):.0f}°{'E' if lon >= 0 else 'W'}"


def _mark_name(f: dict) -> str:
    t = f["title"].split(":")
    head = t[0].strip()
    head = head[0].lower() + head[1:]
    rest = t[1].strip() if len(t) > 1 else ""
    if f["kind"] == "mountain_range":
        return f"the {rest} {head.replace('longest ', '')}" if rest else f"the {head}"
    if rest and f["kind"] in ("great_forest", "wetland"):
        return f"the {head} ({rest.split(' of ', 1)[-1]})"
    return f"the {head}"


def place_of(grid, cells: np.ndarray, marks: list[dict], fallback: str | None = None) -> str:
    """A place phrase for a set of cells: the nearest landmark that covers them, else directions."""
    c = grid.centers[cells].mean(0)
    c /= np.linalg.norm(c) or 1
    lat, lon = float(np.degrees(np.arcsin(c[2]))), float(np.degrees(np.arctan2(c[1], c[0])))
    best, bd = None, 1e9
    for f in marks:
        la, lo = np.radians([f["lat"], f["lon"]])
        v = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
        d = float(np.arccos(np.clip(v @ c, -1, 1)) * R_KM)
        if d < 0.6 * f.get("size_km", 1000) and d < bd:
            best, bd = f, d
    if best is not None:
        return f"{_mark_name(best)} at {_dir(best['lat'], best['lon'])}"
    return fallback or f"the country at {_dir(lat, lon)}"


TOP = 5  # 'the world's five richest districts'


def districts(grid, v: np.ndarray) -> list[np.ndarray]:
    """The world's districts of a good (connected cells >= DISTRICT_MIN), richest (summed value) first."""
    hi = v >= DISTRICT_MIN
    if not hi.any():
        return []
    lab, n = grid.components(hi)
    score = np.bincount(lab[lab >= 0], weights=v[lab >= 0], minlength=n)
    return [np.flatnonzero(lab == c) for c in np.argsort(-score) if score[c] > 0]


def homeland_notes(grid, uses: list, held: dict, goods: dict, marks: list[dict], mkm2: float) -> dict:
    """{line: [sentence]}: what each people's land gives it, for the goods its way of life looks for.
    uses: {line: [(good, weight)]} (positive weights only matter); held: {line: bool mask of its land}."""
    raw, land = goods["_raw"], goods["_land"]
    out = {}
    dist_cache = {}
    for lid, U in uses.items():
        H = held.get(lid)
        if H is None or not H.any():
            continue
        notes = []
        for good, w in sorted(U, key=lambda x: -x[1]):
            if w <= 0 or good not in goods:  # (a good missing on this world says nothing)
                continue
            v = raw[good]
            what = GOODS[good][0]
            if good in DISTRICTS:
                if good not in dist_cache:
                    dist_cache[good] = districts(grid, v)
                ds = dist_cache[good]
                ranks = [i + 1 for i, d in enumerate(ds) if H[d].mean() >= 1 / 3]
                mine = [ds[r - 1] for r in ranks]
                n = min(len(ds), TOP)
                top = [r for r in ranks if r <= TOP]
                if top:
                    where = place_of(grid, mine[0], marks)
                    if len(top) == 1:
                        lead = "the world's richest" if top[0] == 1 else f"the world's {_ord(top[0])} richest"
                        notes.append((1.0 / top[0] + 0.5, f"hold {lead} {what} district, in {where}"))
                    else:
                        notes.append((len(top) / n + 0.5, f"hold {_num(len(top))} of the world's {_num(n)} richest "
                                                          f"{what} districts (the best in {where})"))
                elif len(mine) >= 2:
                    notes.append((0.2 * len(mine) / len(ds), f"work {_num(len(mine))} of the world's {len(ds)} {what} "
                                                             f"districts (the best in {place_of(grid, mine[0], marks)})"))
            else:
                good_cells = land & (v >= 0.5)
                tot = v[good_cells].sum()
                if tot <= 0:
                    continue
                share = float(v[good_cells & H].sum() / tot)
                land_share = float(H[land].mean()) if land.any() else 0.0
                if share >= 0.05 and share >= 1.5 * land_share:
                    mask = good_cells & H
                    lab, nc = grid.components(mask)
                    heart = np.flatnonzero(lab == np.argmax(np.bincount(lab[mask], minlength=nc)))
                    notes.append((share, f"hold {round(100 * share)}% of the world's best {what} "
                                         f"({_area(mask.sum() * mkm2)}, the heart of it in {place_of(grid, heart, marks)})"))
        notes.sort(key=lambda x: -x[0])
        if notes:
            out[lid] = [s for _, s in notes[:2]]
    return out


def _ord(n):
    return {2: "second", 3: "third", 4: "fourth", 5: "fifth"}.get(n, f"{n}th")


def _num(n):
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}.get(n, str(n))


def _area(mkm2):
    return f"{mkm2:.2g} Mkm²" if mkm2 >= 0.1 else f"{mkm2 * 1e6:,.0f} km²"
