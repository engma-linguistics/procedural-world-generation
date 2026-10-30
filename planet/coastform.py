"""Coast form and coast-bound life at the world scale (PW-097, stage 1 of
docs/proposals/coast_detail.md): what kind of shore each coastal land cell
has (ice front, fjord, cliffs, rocky shore, beach, barrier islands and
lagoons, tidal flats and marsh, mangrove coast, delta, coral coast), plus
two scores the zoom draws from (barrier, cliff), seabird and seal colony
likelihoods, and a navigation-hazard score at sea (reefs, shoals, sea ice).

Everything is read from layers a world already stores; nothing upstream
changes (an add-on, `planet coast <world>`, like resources.py). The coastal
land cells' sea-side numbers (wave power, tidal range, sea ice, the water's
mud) are the means over their sea neighbours, as coastal.environment takes
them for mangroves; rocky, the coast's land as coastal.environment rates it
for kelp (high or rugged, hard rock or fresh glacial scour, not a coastal
plain).

Scores (0..1, on coastal land cells):
  barrier  barrier islands and lagoons (Hayes 1979, Davis & Fitzgerald
           2004: wave-dominated, micro- to low mesotidal, low coastal plains
           on a wide gentle shelf with sand to work): low land
           ramp(relief, BAR_RELIEF), a shallow sea in front ramp(depth,
           BAR_DEPTH), waves ramp(wave, BAR_WAVE), small tides ramp(tide,
           BAR_TIDE), sand (soft sediment cover, a coastal plain, a river
           mouth's load nearby), not on fresh glacial scour or under ice.
  cliff    cliffed coast (Sunamura 1992: cliffs where the waves' attack
           beats the rock's strength and the land stands high): rocky x
           ramp(wave, CLIFF_WAVE) x ramp(relief, CLIFF_RELIEF), hard rock
           counting extra.
Classes (CLASSES; first match wins): ice front (grounded ice at the shore),
fjord (fresh glacial scour, high relief, deep water in front), delta (a
river mouth bringing DELTA_KGS kg/s or more of sediment with DELTA_Q m^3/s), mangrove coast
(MANGROVE_PCT % of the cell), tidal flats and salt marsh (macrotidal low
coast, or SALT_MARSH_PCT % marsh), barrier islands (barrier >= BAR_MIN),
coral coast (a sea neighbour with REEF_PCT % reef), cliffs (cliff >=
CLIFF_MIN), rocky shore (rocky >= 0.5), beach (waves >= BEACH_WAVE), else a
sheltered low shore (mud or sand flats, small marshes).

Life on the shore (0..1, coastal land cells):
  seabirds colonies need food (productive water within foraging range:
           upwelling, cold nutrient-rich water, tidal mixing on shelves) and
           a safe place to nest (cliffs, small islands away from land
           predators; Furness & Monaghan 1987).
  seals    pinnipeds: the same food, mostly in cool water (a few warm-water
           species where upwelling keeps the sea cold: Galapagos), hauling
           out on rocky shores, beaches of islands and sea ice.
At sea (0..1, sea cells):
  nav_hazard  reefs, shallow banks away from the coast, sea ice for much of
           the year: where a ship must take care (game-facing).
Simple and literature-based; not tuned to Earth (tools/coast_check.py
checks named places as an anchor).
"""

from __future__ import annotations

import numpy as np

from . import coast
from . import coastal as CL
from .constants import SEC_PER_YR
from .geo import R_KM, cell_area_km2, latlon, ramp, world_land

# barrier islands (Hayes 1979; Davis & Fitzgerald 2004)
BAR_RELIEF = (150.0, 40.0)  # m: the coast's land this low (mean height or half the rise to the highest neighbour)
BAR_DEPTH = (200.0, 60.0)  # m: mean depth of the sea cells in front (a wide, gentle shelf)
BAR_WAVE = (1.0, 5.0)  # kW/m: waves to build and move the barrier (fair-weather swell ~1 m)
BAR_TIDE = (4.5, 2.0)  # m tidal range: barriers fade into tide-dominated flats above ~4 m (Hayes 1979)
BAR_MIN = 0.35
SAND_COVER = (0.2, 1.0)  # km of sediment cover: a sandy coastal plain to work
# cliffs (Sunamura 1992)
CLIFF_WAVE = (3.0, 15.0)  # kW/m
CLIFF_RELIEF = (30.0, 200.0)  # m
CLIFF_MIN = 0.4
BEACH_WAVE = 2.0  # kW/m: waves enough to sort a beach out of the sand
# fjords
FJORD_RELIEF = (150.0, 500.0)  # m of relief at the coast
FJORD_DEPTH = (60.0, 200.0)  # m: the deepest sea neighbour (a glacial trough's mouth)
GLACIAL_M = 20.0  # m of glacial erosion (time zooms) that counts as fresh scour
GLACIATED_MYR = 2.0  # or under ice this recently (runs' glaciated_myr)
FJORD_TEMP = (12.0, 8.0)  # C annual mean at the coast: glaciers reached the sea in the ice ages (not the
# high Andes over a desert coast; Norway ~7 C, Aysen ~9, British Columbia ~8, Fiordland ~10)
# biogenic and muddy coasts
MANGROVE_PCT = 3.0  # % of the coastal land cell (coastal.py's mangrove layer)
SALT_MARSH_PCT = 3.0
MACROTIDAL_M = 4.0  # m tidal range: tide-dominated coasts (Davies 1964); or on a muddy sea (coastal.MUD) below higher land
FLAT_RELIEF = 100.0  # m: a low coast for tidal flats
REEF_PCT = 0.75  # % reef on a sea neighbour: a coral-fringed coast
DELTA_KGS = 300.0  # kg/s of river sediment (~10 Mt/yr: a large delta's supply)...
DELTA_Q = 1000.0  # ... carried by a big river (m^3/s): a steep torrent's load builds a fan, not a delta plain
# life
PROD_UPWELL = (0.5, 3.0)  # C of upwelling cooling: nutrients (as coastal.KELP_UPWELL)
PROD_COLD = (22.0, 12.0)  # C warmest-month sea surface: cool water is nutrient-rich
PROD_TIDE = (1.0, 4.0)  # m tidal range: tidal mixing fronts on shelves
SEAL_WARM = (25.0, 18.0)  # C warmest-month sea surface: seals are cool-water animals (the few warm-water
# ones, Galapagos and Hawaii, live where the sea stays this cool or at the ramp's edge)
ISLAND_CELLS = 3  # a landmass this small (cells) is an island free of land predators
# hazards at sea
SHOAL_M = (40.0, 10.0)  # m mean depth of an offshore cell: banks and shoals
HAZ_REEF = (0.5, 8.0)  # % reef
HAZ_ICE = (0.3, 0.9)  # share of the year under sea ice

ICE, FJORD, DELTA, MANGROVE, TIDAL, BARRIER, CORAL, CLIFF, ROCKY, BEACH, LOW = range(1, 12)
CLASSES = [  # id, key, name, colour, about
    (0, "none", "not a coast", "#00000000", ""),
    (ICE, "ice", "ice front", "#e4f2ff", "grounded ice meets the sea"),
    (FJORD, "fjord", "fjord coast", "#3b5b8c", "glacial troughs drowned by the sea, steep walls, deep water"),
    (DELTA, "delta", "delta", "#b08a4a", "a big river's mouth building land out of its mud and sand"),
    (MANGROVE, "mangrove", "mangrove coast", "#1f7a3a", "warm, sheltered tidal mud under mangrove forest"),
    (TIDAL, "tidal", "tidal flats and salt marsh", "#8fb87a", "big tides over a low, muddy coast"),
    (BARRIER, "barrier", "barrier islands and lagoons", "#f0a040",
     "long sand islands with inlets, lagoons behind (low coast, waves, small tides)"),
    (CORAL, "coral", "coral coast", "#ff6fa8", "the shore fringed by living coral reef"),
    (CLIFF, "cliff", "cliffs", "#7a4a2a", "high, hard or exposed land cut back by the waves"),
    (ROCKY, "rocky", "rocky shore", "#9a9a9a", "rock at the waterline, low or sheltered (skerries, platforms)"),
    (BEACH, "beach", "beaches", "#f2dc8a", "sand and shingle sorted by the waves"),
    (LOW, "low", "sheltered low shore", "#b9a98a", "calm water on a low coast: sand or mud flats, small marshes"),
]
KEYS = {c[1]: c[0] for c in CLASSES}

LAYER_SPECS = {  # name: (dtype, scale, units, description), as store.LAYERS takes them
    "coast_type": ("u1", 1, "id", "coast form of coastal land cells (coastform.CLASSES; legend 'coast')"),
    "barrier": ("u1", 0.01, "0-1", "barrier islands and lagoons likelihood (coastal land cells)"),
    "cliff": ("u1", 0.01, "0-1", "cliffed coast likelihood (coastal land cells)"),
    "seabirds": ("u1", 0.01, "0-1", "seabird colony likelihood (coastal land cells)"),
    "seals": ("u1", 0.01, "0-1", "seal and sea lion haul-out likelihood (coastal land cells)"),
    "nav_hazard": ("u1", 0.01, "0-1", "navigation hazard at sea: reefs, shoals, sea ice"),
}
LAYERS = tuple(LAYER_SPECS)


def legend() -> list:
    return [{"id": i, "key": k, "name": nm, "color": col, "about": ab} for i, k, nm, col, ab in CLASSES]


def scores(grid, L: dict, meta: dict | None = None) -> dict:
    """Per cell, 0..1 scores and the fields the classes use (module docstring)."""
    n = grid.n
    elev = np.asarray(L["elevation"], float)
    land = world_land(L)
    sea = ~land
    env = CL.environment(grid, L, meta, ssc=np.asarray(L["turbidity"], float) if "turbidity" in L else None)
    near = env["coastal_land"]
    wave, tide = env["wave_land"], env["tide_land"]
    depth = np.where(sea, -elev, 0.0)
    d_mean = np.where(near, grid.nbr_mean_in(depth, sea)[0], 0.0)
    d_max = np.where(near, grid.nbr_max_in(depth, sea), 0.0)
    rel = grid.nbr_max_in(elev, land)
    relief = np.where(land, np.maximum(elev, 0.5 * np.maximum(rel - elev, 0)), 0.0)
    rocky = env["rocky_land"]
    hard = env["hard"]
    ice = np.asarray(L.get("ice", np.zeros(n)), float)
    scour = np.zeros(n)
    if "glaciated_myr" in L:
        scour = np.maximum(scour, (np.asarray(L["glaciated_myr"], float) < GLACIATED_MYR).astype(float))
    if "glacial_erosion" in L:
        scour = np.maximum(scour, ramp(np.asarray(L["glacial_erosion"], float), 0.5 * GLACIAL_M, GLACIAL_M))
    if "ice_max" in L:
        scour = np.maximum(scour, (np.asarray(L["ice_max"], float) > 100).astype(float))
    scour = np.maximum(scour, (ice > 0).astype(float))
    # sand: soft cover, a coastal plain, or a river mouth's load on this or a neighbouring coast cell
    sand = ramp(np.asarray(L.get("sediment_cover", np.full(n, 0.3)), float), *SAND_COVER)
    if "landform" in L:
        from .landform import COASTAL_PLAIN
        sand = np.maximum(sand, (np.asarray(L["landform"]) == COASTAL_PLAIN).astype(float))
    mouths, kgs = CL.river_loads(grid, L)
    load = np.zeros(n)
    load[mouths] = kgs
    q = np.asarray(L["flow"], float) * (cell_area_km2(n)) * 1e6 / SEC_PER_YR  # m^3/s
    delta = (load >= DELTA_KGS) & (q >= DELTA_Q)
    load_near = np.maximum(load, grid.nbr_max_in(load, land))
    sand = np.maximum(sand, ramp(load_near, 10.0, 100.0))
    barrier = (ramp(relief, *BAR_RELIEF) * ramp(d_mean, *BAR_DEPTH) * ramp(wave, *BAR_WAVE) * ramp(tide, *BAR_TIDE)
               * sand * (1 - 0.8 * scour) * (ice <= 0))
    cliff = np.clip(rocky * (0.7 + 0.3 * hard) * ramp(wave, *CLIFF_WAVE) * ramp(relief, *CLIFF_RELIEF) * 1.3, 0, 1)
    fjord = (scour * ramp(relief, *FJORD_RELIEF) * ramp(d_max, *FJORD_DEPTH)
             * ramp(np.asarray(L["temperature"], float), *FJORD_TEMP))
    mud = np.where(near, grid.nbr_max_in(env["mud"], sea), 0.0)
    # food in the water: upwelling, cool nutrient-rich water, tidal mixing (the sea neighbours' best)
    sj, sn = np.asarray(L["sst_jul"], float), np.asarray(L["sst_jan"], float)
    s_warm = np.maximum(sj, sn)
    up = np.asarray(L.get("upwelling", np.zeros(n)), float)
    tr = np.asarray(L["tide_range"], float)
    ice_y = coast.sea_ice_share(grid, elev, {"t_warm": np.asarray(L["warm_month"], float),
                                             "t_cold": np.asarray(L["cold_month"], float)}, L.get("ice")).mean(0)
    prod_sea = np.where(sea, np.maximum.reduce([ramp(up, *PROD_UPWELL), ramp(s_warm, *PROD_COLD),
                                                0.6 * ramp(tr, *PROD_TIDE)]) * (1 - 0.8 * ramp(ice_y, 0.6, 0.98)), 0)
    cool_sea = np.where(sea, ramp(s_warm, *SEAL_WARM), 0)
    prod = np.where(near, grid.nbr_max_in(prod_sea, sea), 0.0)
    cool = np.where(near, grid.nbr_max_in(cool_sea, sea), 0.0)
    ice_l = np.where(near, grid.nbr_max_in(ice_y, sea), 0.0)
    label, k = grid.components(land)
    size = np.bincount(label[label >= 0], minlength=k)
    island = land & (label >= 0) & (size[np.maximum(label, 0)] <= ISLAND_CELLS)
    nest = np.maximum.reduce([cliff, 0.9 * island, 0.4 * rocky, 0.3 * (ice > 0)])
    beach_ish = ramp(wave, 1.0, 4.0) * (1 - rocky)
    haul = np.maximum.reduce([0.8 * rocky, 0.6 * beach_ish, island.astype(float), ramp(ice_l, 0.2, 0.7)])
    seabirds = np.where(near, prod * nest, 0.0)
    seals = np.where(near, prod * cool * haul, 0.0)
    # hazards at sea
    reef = np.asarray(L.get("reef", np.zeros(n)), float)
    coastal_sea = env["coastal_sea"]
    shoal = np.where(sea & ~coastal_sea, ramp(depth, *SHOAL_M), 0.5 * ramp(depth, 25.0, 5.0))
    hazard = np.where(sea, np.maximum.reduce([ramp(reef, *HAZ_REEF), shoal, 0.7 * ramp(ice_y, *HAZ_ICE)]), 0.0)
    z = np.zeros(n)
    return {"near": near, "barrier": np.where(near, barrier, z), "cliff": np.where(near, cliff, z),
            "fjord": np.where(near, fjord, z), "rocky": rocky, "wave": wave, "tide": tide, "relief": relief,
            "delta": delta, "seabirds": seabirds, "seals": seals, "nav_hazard": hazard,
            "mud": mud, "reef_nbr": np.where(near, grid.nbr_max_in(reef, sea), 0.0), "depth_front": d_mean}


def classify(L: dict, s: dict) -> np.ndarray:
    """coast_type ids (CLASSES) from the scores; first match wins."""
    near = s["near"]
    ice = np.asarray(L.get("ice", np.zeros(len(near))), float)
    mang = np.asarray(L.get("mangrove", np.zeros(len(near))), float)
    marsh = np.asarray(L.get("salt_marsh", np.zeros(len(near))), float)
    out = np.zeros(len(near), np.uint8)
    rules = [
        (ICE, ice > 0),
        (FJORD, s["fjord"] >= 0.5),
        (DELTA, s["delta"]),
        (MANGROVE, mang >= MANGROVE_PCT),
        (TIDAL, ((s["tide"] >= MACROTIDAL_M) & ((s["relief"] < FLAT_RELIEF) | (s["mud"] >= 0.5)))
         | (marsh >= SALT_MARSH_PCT)),
        (BARRIER, s["barrier"] >= BAR_MIN),
        (CORAL, s["reef_nbr"] >= REEF_PCT),
        (CLIFF, s["cliff"] >= CLIFF_MIN),
        (ROCKY, s["rocky"] >= 0.5),
        (BEACH, s["wave"] >= BEACH_WAVE),
        (LOW, np.ones(len(near), bool)),
    ]
    free = near.copy()
    for cid, m in rules:
        hit = free & m
        out[hit] = cid
        free &= ~hit
    return out


def world_layers(grid, L: dict, meta: dict | None = None) -> dict:
    """The coast layers (LAYERS) in their stored units: coast_type ids, the rest 0..1."""
    s = scores(grid, L, meta)
    out = {"coast_type": classify(L, s)}
    for k in ("barrier", "cliff", "seabirds", "seals", "nav_hazard"):
        out[k] = np.round(s[k], 2)
    return out


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
def summary(grid, L: dict) -> dict:
    """Shares of the coastline by class (each coastal land cell counted as
    one cell width of coast), each class's longest stretches (connected
    coastal cells) with a centre, and the best seabird and seal coasts."""
    ct = np.asarray(L["coast_type"])
    coast = ct > 0
    if not coast.any():
        return {}
    km = grid.spacing * R_KM
    out = {"coast_km": round(float(coast.sum() * km)), "classes": []}
    for cid, key, name, _, _ in CLASSES[1:]:
        m = ct == cid
        if not m.any():
            continue
        label, k = grid.components(m)
        size = np.bincount(label[label >= 0], minlength=k)
        top = []
        for comp in np.argsort(-size, kind="stable")[:3]:
            cells = np.flatnonzero(label == comp)
            c = grid.centers[cells].mean(0)
            lat, lon = latlon(c / np.linalg.norm(c))
            top.append({"km": round(float(len(cells) * km)), "lat": round(float(lat), 1), "lon": round(float(lon), 1)})
        out["classes"].append({"key": key, "name": name, "km": round(float(m.sum() * km)),
                               "pct": round(100.0 * m.sum() / coast.sum(), 1), "longest": top})
    for k in ("seabirds", "seals"):
        v = np.asarray(L.get(k, np.zeros(grid.n)), float)
        best = np.argsort(-v)[:3]
        out[k] = {"cells_over_half": int((v >= 0.5).sum()),
                  "best": [{"lat": round(float(grid.lat[i]), 1), "lon": round(float(grid.lon[i]), 1),
                            "score": round(float(v[i]), 2)} for i in best if v[i] > 0]}
    hz = np.asarray(L.get("nav_hazard", np.zeros(grid.n)), float)
    out["hazard_km2"] = round(float((hz >= 0.5).sum() * 4 * np.pi * R_KM ** 2 / grid.n))
    return out


def text_section(s: dict) -> str:
    """The world .txt's coast section."""
    lines = [f"## Coasts (coastform.py, PW-097): {s['coast_km']:,} km of coastline"]
    for c in sorted(s["classes"], key=lambda c: -c["km"]):
        lg = "; ".join(f"{t['km']:,} km at {t['lat']:+.0f}, {t['lon']:+.0f}" for t in c["longest"][:2])
        lines.append(f"  {c['name']:<28} {c['pct']:5.1f}%  {c['km']:>8,} km   longest: {lg}")
    for k, nm in (("seabirds", "seabird colonies"), ("seals", "seal haul-outs")):
        b = s.get(k, {})
        if b.get("best"):
            lines.append(f"  {nm}: {b['cells_over_half']} likely coast cells; best at "
                         + ", ".join(f"{t['lat']:+.0f}, {t['lon']:+.0f}" for t in b["best"]))
    lines.append(f"  navigation hazards (reefs, shoals, sea ice): {s.get('hazard_km2', 0):,} km2 of sea")
    return "\n".join(lines)


def add_to_world(ref: str) -> "Path":  # noqa: F821
    """(Re)makes a saved world's coast layers in place (`planet coast <world>`)."""
    import time

    from . import store as S
    from . import world as W
    path = S.find_world(ref)
    w = W.load(path)
    w["layers"].update(world_layers(w["grid"], w["layers"], w["meta"]))
    w["meta"]["coast"] = {"created": time.strftime("%Y-%m-%d %H:%M:%S")}
    return W.save(w, w["name"], path.stem)
