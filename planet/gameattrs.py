"""Game attributes of the land's plants and soils (PW-206; vegetation proposal
section 8.2, decision 11A; soils proposal section 6).

What a TTRPG or game user wants from a place: how slow it is to walk through,
how far you can see, what it feeds (herds and foragers), what it gives
(timber, fuel), what the ground is like to build on and when it turns to mud,
when it burns, when it is green, and what can hurt you there. Every value is
computed from the place's own layers (the plant types' cover, the canopy,
NPP, biomass, stand age, the flooded share, the soil and the month-by-month
climate), not looked up per named type, so a gallery forest in a savanna or a
burned patch of taiga gets its own values. The rules are crude, written down
next to each attribute, and not fitted to anything: they are game numbers.

  travel        x the time of walking open, level, dry ground (snow-free
                season, off roads): stems and understory, wet ground, peat,
                deadfall in old stands, rough or steep ground; glaciers x4.
  sightline     m you can see at eye level: from the stems and understory
                (a Beer's-law free path), capped at the horizon (5 km).
  grazing       0-5 pasture for herds: the herb layer's NPP plus browse.
  foraging      0-5 wild food for people: mast and fruit trees, game (the
                grazing), wetlands (waterfowl, wild grain, roots), river fish.
  timber        0-5 building timber: woody biomass, height, straight conifers.
  fuel          0-5 firewood and fuel: wood, shrubs, cut peat from bogs, dung on
                pasture.
  building      0-5 building ground: firm rock or gravel good; peat, cracking
                clay, salt, waterlogged ground, permafrost and slopes bad.
  mud_months    months the ground is mud (wet months on clay, silt or poorly
                drained soil; the permafrost's summer thaw).
  fire_months   12-bit mask (bit 0 = January) of the fire-weather months where
                the place burns at all.
  green_months  12-bit mask of the months the plants are in leaf (cover-
                weighted leaf habit, as the satellite view's) and not under snow.
  hazards       bit mask of HAZARDS (deep snow, bogs, biting insects, thorny
                scrub, wildfire, crocodiles, heat, cold, thin air, avalanches).

Farmland (arable class) is humanuse.py's `fertile` (PW-099); the hover card
shows it next to these. One implementation serves worlds (cells) and zooms
(pixels); a zoom has no per-PFT layers stored, so its caller passes the
per-pixel fractions it has at build time (`nu`), or the rules fall back on
tree and plant cover.

    world_layers(grid, layers) -> {name: array} to store with a world
    zoom_layers(layers, res_km, lat, nu) -> the same for a zoom's rasters
"""

from __future__ import annotations

import numpy as np

from . import climate
from . import soils as SO
from . import vegetation as V

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
HAZARDS = [  # (key, name, what triggers it)
    ("snow", "deep snow", "a winter snowpack over ~100 mm of water (~0.4 m of snow)"),
    ("bog", "bogs and mires", "a quarter of the ground flooded part of the year, peat soil, or very poorly drained ground"),
    ("insects", "biting insects", "hot, wet tropics; or wet boreal and tundra summers"),
    ("thorns", "thorny scrub", "desert shrubs, succulents and dry savanna trees cover a third of a dry place"),
    ("fire", "wildfire", "burns every 30 years or more often"),
    ("crocodiles", "crocodiles", "warm all year (coldest month 16 C+), with swamps, mangroves or a big river (1000 m3/s+)"),
    ("heat", "dangerous heat", "warmest month's mean 32 C or more"),
    ("cold", "deadly cold", "coldest month's mean -25 C or less"),
    ("altitude", "thin air", "3500 m or higher"),
    ("avalanche", "avalanches", "steep slopes (28 deg or more) under deep snow"),
]
HAZARD_BIT = {k: 1 << i for i, (k, *_) in enumerate(HAZARDS)}

# the world layers' store specs / the zoom's: (dtype, scale, units, description)
LAYER_SPECS = {
    "travel": ("u1", 0.05, "x", "walking time through the place x open level ground's (snow-free, off roads; 0 at sea)"),
    "sightline": ("<u2", 1, "m", "how far you can see at eye level through the plants (5000: to the horizon)"),
    "grazing": ("u1", 0.1, "0-5", "pasture for herds: herb NPP plus browse"),
    "foraging": ("u1", 0.1, "0-5", "wild food for people: mast and fruit trees, game, wetlands, river fish"),
    "timber": ("u1", 0.1, "0-5", "building timber: woody biomass, height, straight conifers"),
    "fuel": ("u1", 0.1, "0-5", "firewood and fuel: wood, shrubs, peat, dung"),
    "building": ("u1", 0.1, "0-5", "building ground: firm and dry 5 .. peat, cracking clay, thawing permafrost 0-1"),
    "mud_months": ("u1", 1, "months", "months the ground turns to mud"),
    "fire_months": ("<u2", 1, "mask", "fire-weather months, bit 0 = January (0: the place does not burn)"),
    "green_months": ("<u2", 1, "mask", "months the plants are in leaf and free of snow, bit 0 = January"),
    "hazards": ("<u2", 1, "mask", "bit mask of gameattrs.HAZARDS (legend game.hazards)"),
}
NAMES = tuple(LAYER_SPECS)

_HMAX = np.array([p["hmax"] for p in V.PFTS], float)  # m: each plant type's full height
HORIZON_M = 5000.0  # a standing person's horizon on flat ground is ~4.7 km
WOOD_PER_M = 6.0  # t C/ha of wood per m of canopy height at full tree cover (a zoom's biomass, which it doesn't store)


def legend() -> dict:
    """The legend every file stores (store.legends 'game')."""
    return {"hazards": [{"bit": i, "key": k, "name": n, "rule": r} for i, (k, n, r) in enumerate(HAZARDS)],
            "months": list(MONTHS),
            "scales": {k: {"units": u, "description": d} for k, (_, _, u, d) in LAYER_SPECS.items()}}


def _sat(x, k):
    """0..5, saturating: 5 (1 - e^(-x/k))."""
    return 5.0 * (1.0 - np.exp(-np.maximum(x, 0.0) / k))


def _mask(b: np.ndarray) -> np.ndarray:
    """(12, n) bool -> 12-bit masks (bit 0 = January)."""
    return (b.astype(np.int64) << np.arange(12)[:, None]).sum(0).astype(np.uint16)


def compute(lat, F: dict, nu: np.ndarray | None = None, rough=None, q=None, tilt: float = 23.4) -> dict:
    """Game attributes of n places. F: 1-D arrays (n,) in real units:
    land (bool), ice (m), elevation (m), temp, t_warm, t_cold (C), p_jul,
    p_jan (mm/yr), tree, cover (0..1: tree and plant cover), lai, height (m),
    npp (g C/m2/yr), fire_return (yr, 0 none); optional: biomass (t C/ha),
    stand_age (yr), flooded (0..1), mangrove (0..1), slope (deg), soil,
    soil_texture, soil_drainage, soil_depth, peat_depth, permafrost, loess.
    nu (NP, n): the plant types' shares of the ground, or None (rules fall
    back on tree and plant cover). rough: x walking time for the ground's
    roughness (the caller's: a world cell's relief, a zoom pixel's slope).
    q: m^3/s of river through the place. Returns {LAYER_SPECS name: array}."""
    lat = np.asarray(lat, float)
    n = len(lat)
    g = lambda k, d=0.0: np.asarray(F[k], float) if k in F and F[k] is not None else np.full(n, d)
    land = np.asarray(F["land"], bool) & (g("ice") <= 0)
    glacier = np.asarray(F["land"], bool) & (g("ice") > 0)
    tree, cover = np.clip(g("tree"), 0, 1), np.clip(g("cover"), 0, 1)
    lai, hgt, npp = g("lai"), g("height"), np.maximum(g("npp"), 0)
    flooded, peat = np.clip(g("flooded"), 0, 1), g("peat_depth")
    fire = g("fire_return")
    tex, drain = g("soil_texture").astype(int), g("soil_drainage").astype(int)
    soil, perma = g("soil").astype(int), g("permafrost").astype(int)
    biomass = g("biomass") if "biomass" in F else WOOD_PER_M * tree * hgt
    age = g("stand_age", 100.0)
    tw, tc = np.maximum(g("t_warm"), g("t_cold")), np.minimum(g("t_warm"), g("t_cold"))
    mo = climate.months(lat, g("temp"), tw, tc, g("p_jul"), g("p_jan"), tilt)
    mi = mo["p"].sum(0) / np.maximum(mo["pet"].sum(0), 1.0)
    snow_max = mo["snow"].max(0)
    # the plant types' shares of the cover
    if nu is not None:
        tot = np.maximum(nu.sum(0), 1e-9)
        sh = lambda mask: nu[mask].sum(0) / tot
        herb_s, shrub_s = sh(V.HERBS), sh(V.SHRUBS)
        pick = lambda *codes: sum(nu[V.IDX[c]] for c in codes)
        shrub = (nu * np.clip(_HMAX / 3.0, 0, 1)[:, None])[V.SHRUBS].sum(0)  # (of the ground; dwarf heath hardly hinders)
        needle = pick("TeNE", "BoNE", "BoNS") / np.maximum(nu[V.TREES].sum(0), 1e-9)
        mast = (pick("TeBS") + 0.6 * pick("TeBE") + 0.7 * pick("TrBR") + 0.4 * pick("TrBE") + 0.3 * pick("BoBS")) / tot
        thorny = (pick("XerS", "Succ") + np.where(mi < 0.7, pick("TrBR", "SclS"), 0)) / tot
    else:  # (the rest of the cover under no trees is herbs, a little of it shrubs)
        rest = np.clip(cover - tree, 0, 1)
        herb_s = 0.8 * rest / np.maximum(cover, 1e-9)
        shrub_s = 0.2 * rest / np.maximum(cover, 1e-9)
        shrub = 0.2 * rest
        needle = np.where(tc < -5, 0.8, 0.3)
        mast = 0.4 * tree * (tc > -10)
        thorny = np.where(mi < 0.4, shrub_s, 0.0)
    herb_npp = npp * herb_s
    out = {}

    # travel: stems (cover x height class), understory (shrubs, and the dense lower layers of a
    # high-LAI forest), wet ground, peat, deadfall in old stands, rough ground
    veg = 1.0 + tree * np.sqrt(np.clip(hgt / 20.0, 0, 1.3)) + 1.2 * shrub + 0.15 * tree * np.clip(lai - 3.0, 0, 4)
    veg += 0.2 * tree * np.clip((age - 300.0) / 300.0, 0, 1)  # deadfall in old growth
    wet = 1.0 + 3.0 * flooded + 0.5 * (soil == SO.PEAT) + 0.3 * (drain >= 5)
    tr = veg * wet * (1.0 if rough is None else np.asarray(rough, float))
    out["travel"] = np.where(land, np.clip(tr, 1.0, 12.5), np.where(glacier, 4.0, 0.0))

    # sightline: eye-level obstruction per metre (trunks, shrubs, the understory of tall leafy forest)
    k = 0.02 * tree + 0.04 * shrub + 0.004 * tree * np.clip(lai - 3.0, 0, 4)
    out["sightline"] = np.where(land | glacier, np.minimum(HORIZON_M, 1.0 / np.maximum(k, 1.0 / HORIZON_M)), 0)

    # grazing: the herb layer's NPP, plus 30% of the shrubs' as browse; frozen or snowed-in months graze less
    open_months = ((mo["t"] > 0) & (mo["snow"] < 30)).sum(0)
    graze = (herb_npp + 0.3 * npp * shrub_s) * (0.4 + 0.6 * open_months / 12.0)
    out["grazing"] = np.where(land, _sat(graze, 250.0), 0)

    # foraging: mast and fruit trees, game (the grazing), wetlands (waterfowl, wild grain, roots), river fish
    x = 1.2 * mast * np.clip(npp / 600.0, 0, 1.5) + 0.16 * out["grazing"] + 2.0 * flooded
    if q is not None:
        x = x + 0.5 * np.clip(np.log10(1.0 + np.asarray(q, float) / 50.0) / 2.0, 0, 1)
    out["foraging"] = np.where(land, 5.0 * (1.0 - np.exp(-x)), 0)

    # timber: woody biomass, height, straight-grown conifers
    out["timber"] = np.where(land, _sat(biomass, 40.0) * (0.7 + 0.3 * np.clip(needle, 0, 1))
                             * np.sqrt(np.clip(hgt / 25.0, 0, 1)), 0)

    # fuel: wood, shrubs (twigs and dead stems), peat, dung on pasture
    xf = biomass / 30.0 + 1.0 * shrub + 1.5 * np.clip(4.0 * flooded, 0, 1) * (peat >= 0.5) + 0.04 * out["grazing"]
    out["fuel"] = np.where(land, 5.0 * (1.0 - np.exp(-xf)), 0)

    # building ground: by the soil, then permafrost, slope and flooding
    b = np.full(n, 4.0)
    b = np.where((tex == 1) | (soil == SO.SAND), 3.5, b)  # loose sand
    b = np.where(tex == 4, 3.0, b)  # soft clay
    b = np.where(np.isin(soil, (SO.THIN, SO.RENDZINA, SO.GYPSIC, SO.CALCIC)), 5.0, b)  # firm: rock, gravel, hardpan
    b = np.where(g("loess") >= 5, np.minimum(b, 3.5), b)  # thick loess slumps when wet
    b = np.where(np.isin(soil, (SO.GLEY, SO.SALT)) | (drain >= 5), 2.0, b)
    b = np.where(soil == SO.VERTISOL, 1.5, b)  # swelling and cracking
    b = np.where(soil == SO.PEAT, 0.5, b)
    b = b * np.array([1.0, 0.8, 0.5, 0.4])[np.clip(perma, 0, 3)]
    st = np.clip((g("slope") - 12.0) / (35.0 - 12.0), 0, 1)
    b = b * (1 - 0.8 * st) * (1 - 0.7 * flooded)
    out["building"] = np.where(land, b, 0)

    # mud: wet, thawed months (rain and snowmelt beyond the evaporation) on clay, silt or poorly drained
    # ground; the summer thaw over permafrost
    tex_w = np.array([0, 0, 0.6, 1.0, 1.0, 1.0])[np.clip(tex, 0, 5)]
    drain_w = np.array([0, 0, 0.5, 1.0, 1.0, 1.0])[np.clip(drain, 0, 5)]
    wetm = (mo["water"] > mo["pet"]) & (mo["t"] > 0)
    thaw = (perma >= 2)[None, :] & (mo["t"] > 0)
    mud = np.maximum(np.round(wetm.sum(0) * tex_w * drain_w), np.round(0.7 * thaw.sum(0)))
    out["mud_months"] = np.where(land, mud, 0)

    # fire weather (vegetation.site's rule, month by month) where the place burns at all
    ratio = mo["water"] / np.maximum(mo["pet"], 1e-6)
    dry = np.clip((1.0 - ratio) / 0.8, 0, 1) * (mo["t"] > 5) * (mo["snow"] <= 1)
    burns = land & (fire > 0) & (fire < 5000)
    fm = (dry >= 0.5) & burns[None, :]
    none = burns & ~fm.any(0)  # (burns, but in short dry spells: its driest warm month)
    if none.any():
        fm[np.argmax(dry, 0)[none], np.flatnonzero(none)] = True
    out["fire_months"] = np.where(burns, _mask(fm), 0)

    # green months: the cover-weighted leaf habit (satellite.leaf_on), or the warm, moist months
    if nu is not None:
        from .satellite import leaf_on
        tot = np.maximum(nu.sum(0), 1e-9)
        gm = np.stack([(nu * leaf_on(mo, m)).sum(0) / tot >= 0.5 for m in range(12)])
    else:
        gm = (mo["t"] > 5) & (ratio > 0.3)
    gm &= mo["snow"] < 30  # (in leaf and not under snow)
    out["green_months"] = np.where(land & (cover > 0.05), _mask(gm), 0)

    # hazards
    hz = np.zeros(n, np.int64)
    put = lambda key, cond: np.where(cond, HAZARD_BIT[key], 0)
    hz |= put("snow", snow_max >= 100.0)
    hz |= put("bog", (flooded >= 0.25) | (soil == SO.PEAT) | (drain >= 5))
    hz |= put("insects", ((tc >= 15) & (tw >= 22) & (mi >= 0.8)) | ((tc <= -10) & (tw >= 10) & ((flooded >= 0.1) | (perma >= 2))))
    hz |= put("thorns", (thorny >= 0.33) & (mi < 0.7) & (cover >= 0.1))
    hz |= put("fire", burns & (fire <= 30))
    hz |= put("crocodiles", (tc >= 16) & ((flooded >= 0.25) | (g("mangrove") >= 0.1)
                                          | (np.asarray(q, float) >= 1000 if q is not None else False)))
    hz |= put("heat", tw >= 32)
    hz |= put("cold", tc <= -25)
    hz |= put("altitude", g("elevation") >= 3500)
    hz |= put("avalanche", (g("slope") >= 28) & (snow_max >= 100.0))
    out["hazards"] = np.where(land | glacier, hz, 0).astype(np.uint16)

    return {k: np.round(v / LAYER_SPECS[k][1]) * LAYER_SPECS[k][1] if LAYER_SPECS[k][1] != 1 else
            np.asarray(v).astype(int) for k, v in out.items()}


# ---------------------------------------------------------------------------
# Worlds and zooms
# ---------------------------------------------------------------------------
def _soil_fields(L, get):
    return {k: get(k) for k in ("soil", "soil_texture", "soil_drainage", "soil_depth", "peat_depth", "permafrost", "loess")
            if k in L}


def world_layers(grid, L: dict, tilt: float = 23.4) -> dict:
    """The layers to store with a world (world.finish), from its stored layers (needs the vegetation)."""
    if "vegetation" not in L or "veg_Moss" not in L:
        return {}
    from . import hydrology
    from .geo import is_land
    a = lambda k, d=0.0: np.asarray(L[k], float) if k in L else np.full(grid.n, d)
    el, ice = a("elevation"), a("ice")
    land = is_land(el, ice) & ~((np.asarray(L["lake"]) > 0) if "lake" in L else np.zeros(grid.n, bool))
    nu = np.stack([a(f"veg_{c}") / 100 for c in V.CODES])
    # a cell's roughness: its relief (m to the steepest neighbour) as hill country is to walk across
    rough = 1.0 + np.clip(V.relief(grid, el) / 1500.0, 0, 3)
    q = hydrology.discharge(grid, a("flow")) if "flow" in L else None
    F = {"land": land, "ice": ice, "elevation": el, "temp": a("temperature"), "t_warm": a("warm_month"),
         "t_cold": a("cold_month"), "p_jul": a("precipitation_jul"), "p_jan": a("precipitation_jan"),
         "tree": a("tree_cover") / 100, "cover": a("plant_cover") / 100, "lai": a("lai"), "height": a("canopy_height"),
         "npp": a("npp"), "fire_return": a("fire_return"), "biomass": a("biomass"), "stand_age": a("stand_age"),
         "flooded": a("flooded") / 100, "mangrove": a("mangrove") / 100, **_soil_fields(L, a)}
    return compute(grid.lat, F, nu, rough, q, tilt)


def zoom_layers(L: dict, res_km: float, lat, nu: np.ndarray | None = None, tilt: float = 23.4) -> dict:
    """A zoom's layers (ny, nx) from its decoded rasters L (2-D, real units); lat (ny*nx,) of the pixels;
    nu (NP, ny*nx): the per-pixel plant fractions (zoom_vegetation, at build time), or None."""
    el = np.asarray(L["elevation"], float)
    ny, nx = el.shape
    a = lambda k, d=0.0: np.asarray(L[k], float).ravel() if k in L else np.full(ny * nx, d)
    water = a("water")
    tj, tn = a("temperature_jul"), a("temperature_jan")
    lat = np.asarray(lat, float)
    lat_s = np.where(tj >= tn, np.abs(lat), -np.abs(lat))  # (the seasons the pixel has, PW-374)
    slope = np.degrees(np.arctan(np.hypot(*np.gradient(el, res_km * 1000.0)))).ravel()
    rough = np.exp(3.5 * np.tan(np.radians(np.minimum(slope, 60.0))))  # Tobler's hiking function, either way
    wl = a("wetland")
    F = {"land": water == 0, "ice": a("ice"), "elevation": el.ravel(), "temp": a("temperature"),
         "t_warm": np.maximum(tj, tn), "t_cold": np.minimum(tj, tn), "p_jul": a("precipitation_jul"),
         "p_jan": a("precipitation_jan"), "tree": a("tree_cover") / 100, "cover": a("plant_cover") / 100,
         "lai": a("lai"), "height": a("canopy_height"), "npp": a("npp"), "fire_return": a("fire_return"),
         "flooded": np.where(wl == 2, 0.6, np.where(wl == 1, 0.4, 0.0)), "slope": slope,
         "mangrove": (a("coastal_life") == 4).astype(float), **_soil_fields(L, a)}
    out = compute(lat_s, F, nu, rough, a("discharge") if "discharge" in L else None, tilt)
    return {k: v.reshape(ny, nx) for k, v in out.items()}


def zoom_layer_doc() -> dict:
    """zoom.LAYER_DOC entries: name -> (units, description, encoding or none)."""
    doc = {}
    for k, (dt, sc, units, desc) in LAYER_SPECS.items():
        enc = {"dtype": dt, "scale": sc} if sc != 1 else ({"dtype": dt} if dt != "u1" else None)
        doc[k] = (units, desc + " (gameattrs.py)", *([enc] if enc else []))
    return doc
