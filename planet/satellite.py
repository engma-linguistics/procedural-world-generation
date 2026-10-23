"""True-colour 'satellite view' of worlds and zooms (PW-083; vegetation
proposal section 8.1).

One colour function for the globe and the regional zoom, so the two match.
Each place's colour is mixed in linear light (reflectances add; sRGB doesn't):

1. Bare ground: a soil colour from the climate (dark brown humid soils,
   grey-brown cold ones, red semi-arid soils and yellow sand in hot
   deserts, grey cold deserts), tinted by the exposed rock where it is
   known (basalt dark, limestone and evaporites pale, sandstone red, an
   old shield laterite-red in hot dry country), sand on dune fields, grey
   rock high up. Where the soil is known (worlds and zooms since PW-206),
   its type sets most of the colour (SOIL_SURFACE: red tropical soils,
   near-black earths and peat, pale lime and gypsum, white salt), and thin
   stony soils show their rock.
2. Plants: each plant type's share (the vegetation's per-PFT fractions)
   x its colour, leaf-on or leaf-off in that month (PFT_COLOURS). The leaf
   habit follows vegetation.py's rules: summergreen types need the month
   warmer than their threshold, raingreen ones a moist soil (the rain and
   snowmelt of the month and the two before against the potential
   evaporation),
   grasses both (dormant grass is straw when dry, brown when cold). The
   plants cover `plant_cover` of the ground; the rest shows step 1.
3. Wetlands (the flooded share): darker, olive-brown.
4. Snow: the month's snowpack (climate.months: snow falls below ~0 C and
   melts by degree-days), as a cover 1 - exp(-SWE / SNOW_SWE), partly
   hidden by trees (evergreen crowns hide most of it: the dark boreal
   forest in winter).
5. Land ice (white, greyer and bluer where it melts in summer); lakes by
   depth (shallow ones greenish with sediment), salt lakes turquoise, salt
   pans white; frozen lakes white.
6. The sea by depth, turquoise over warm shallow carbonate shelves, sea
   ice where the month is below freezing (coast.sea_ice_share's rule).

Seasons: 'jul' and 'jan' are those months; 'year' is each hemisphere's
summer (July north of 10 N, January south of 10 S, blended in between),
what a cloud-free mosaic like Blue Marble shows. Hill shading and clouds
are the viewer's (they depend on the light and are drawn on top).

Where the colours are computed (decision, PW-083): here, in Python, baked
into the world (`sat`, `sat_jul`, `sat_jan`: 0xRRGGBB per cell; ~4% of an
L7 world file) and the zoom (`satellite*.png` and the preview). One
implementation serves both, it can use the per-PFT fractions a zoom only
has at build time, and the snowpack needs the month-by-month climate.
`planet satellite <world|zoom>` adds or redoes them on a saved item.
"""

from __future__ import annotations

import numpy as np

from . import climate
from . import soils as SO
from . import vegetation as V
from .geo import world_land
from .surface import ROCKS

SEASONS = ("jul", "jan", "year")
MONTH = {"jul": 6, "jan": 0}
SNOW_SWE = 15.0  # mm of snow water: the cover is 1 - exp(-SWE / this) (~63% at ~5 cm of fresh snow)
MOIST_W = (0.5, 0.3, 0.2)  # the leaf habit's moisture: weights of this month's and the two before's water / PET
YEAR_BLEND = 10.0  # deg of latitude over which 'year' blends the hemispheres' summers


def _hex(c: str) -> np.ndarray:
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], float) / 255.0


def lin(c) -> np.ndarray:
    """sRGB (hex string, or 0..1 array) -> linear light."""
    c = _hex(c) if isinstance(c, str) else np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def srgb8(x: np.ndarray) -> np.ndarray:
    """Linear light (..., 3) -> sRGB uint8."""
    x = np.clip(x, 0, 1)
    s = np.where(x <= 0.0031308, 12.92 * x, 1.055 * x ** (1 / 2.4) - 0.055)
    return np.round(255 * s).astype(np.uint8)


def _mix(a, b, t):
    t = np.asarray(t, float)
    return a + (b - a) * (t[..., None] if t.ndim else t)


def _smooth(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def _ramp(v, stops) -> np.ndarray:
    """Linear-light colours (n, 3) along value stops [(v, hex)]."""
    xs = np.array([s[0] for s in stops], float)
    cs = np.array([lin(s[1]) for s in stops])
    v = np.asarray(v, float)
    return np.stack([np.interp(v, xs, cs[:, k]) for k in range(3)], -1)


# ---------------------------------------------------------------------------
# Palette (sRGB; tuned by eye against Blue Marble-style imagery)
# ---------------------------------------------------------------------------
# each plant type at full cover: (leaf-on, leaf-off). Evergreens: one colour.
# Grasses: leaf-off is dry straw; COLD_DORMANT is their cold-season brown.
PFT_COLOURS = {
    "TrBE": ("#24461f", None), "TrBR": ("#3c5c26", "#8a7752"), "TeBE": ("#2e5228", None),
    "TeBS": ("#3f6530", "#776a58"), "TeNE": ("#243f28", None), "BoNE": ("#1d3423", None),
    "BoNS": ("#4b6334", "#6c6255"), "BoBS": ("#4f6e36", "#81776a"), "SclS": ("#5c6340", None),
    "XerS": ("#878256", "#a19274"), "DecS": ("#5c6a3d", "#796e5e"), "HthS": ("#5d563e", None),
    "C4G": ("#7d8a44", "#c4aa76"), "C3G": ("#6c8945", "#b9a77d"), "TunH": ("#6c7450", "#877d66"),
    "Succ": ("#7c7a5a", None), "Moss": ("#8a8870", None), "WetH": ("#4a6638", "#867859"),
    "Sph": ("#6b583d", None),
}
COLD_DORMANT = "#8c8068"  # grass and herbs dormant in the cold
assert list(PFT_COLOURS) == V.CODES

# bare ground
SOIL_HUMID_WARM, SOIL_HUMID_COLD = "#5e4b38", "#6b665b"
DESERT_RED, DESERT_SAND, DESERT_COLD = "#b77a4b", "#d8b681", "#a39a87"
LATERITE = "#a8653d"  # an old shield's iron crust in hot, dry country (Australia)
DUNE_SAND = "#ddbb86"
# each soil type's bare, dry surface (soils.TYPES keys; None: keep the climate's colour). Muted, as seen from orbit:
# red Ferralsols, near-black earths and peat, pale lime and gypsum crusts, white salt (PW-206; soils proposal 6)
SOIL_SURFACE = {
    "none": None, "peat": "#3d3127", "frozen": "#6f675b", "thin": None, "salt": "#e2ddd0", "alluvium": "#6e6352",
    "gley": "#5f5d55", "andosol": "#3e3631", "sand": "#d3b88a", "gypsic": "#d8c49c", "calcic": "#c7ab84",
    "vertisol": "#4a4440", "chestnut": "#7d6449", "chernozem": "#3a322b", "podzol": "#8f877a", "rendzina": "#6b675c",
    "ferralsol": "#8f4a2c", "acrisol": "#a0643f", "luvisol": "#7c6046", "cambisol": "#8a7457",
}
SOIL_WEIGHT = 0.7  # how much of the bare colour the soil sets (the rest: the climate's guess, then the rock)
HIGH_ROCK = "#8a857e"
ROCK_COLOURS = {  # exposed rock (surface_rock), by key
    "ocean": "#4d4842", "hotspot": "#3f3a36", "arc": "#6a6159", "sediment": "#b09a78", "orogen": "#858079",
    "craton": "#9a8676", "limestone": "#cdc4ad", "sandstone": "#c08350", "shale": "#857a69",
    "evaporite": "#e4dfd2", "coal": "#4f4943", "granite": "#b3a191", "quartzite": "#cbc3b2",
    "flood_basalt": "#3f3a36", "dolomite": "#bbb6a8", "tuff": "#a49580",
}
CRATON = [r[1] for r in ROCKS].index("craton")
CARBONATE = [i for i, r in enumerate(ROCKS) if r[1] in ("limestone", "dolomite")]
DUNES = 9  # landform.CLASSES: dune field (erg)
WETLAND = "#3b4a33"
SNOW, LAND_ICE, MELTING_ICE = "#f1f4f7", "#e8eef4", "#c6d4df"
# water
SEA = [(0, "#2b6a80"), (20, "#1f5070"), (60, "#173d63"), (200, "#122f55"), (1000, "#0d2147"), (3000, "#0a193b"),
       (6000, "#08132f")]
SHELF_TURQUOISE = "#3aa5b0"
SEA_ICE = "#dbe3ea"
# coastal life (coastal.py, PW-188): reefs' pale turquoise flats, dark seagrass beds, the brown-olive kelp
# canopy at the surface, dark mangrove forest, salt marsh (growing season, winter)
REEF, SEAGRASS, KELP = "#7fd6cf", "#1f3a33", "#3a3a22"
MANGROVE, SALT_MARSH = "#1e3a22", ("#6f8048", "#8f8360")
FRESH_LAKE = [(0, "#4b6a5c"), (10, "#30566a"), (50, "#1f4062"), (300, "#142e52")]
SALT_LAKE = [(0, "#5aa49a"), (20, "#3f8a90"), (100, "#2c6a80")]
SALT_PAN = "#e6e0d3"


def _rock_table() -> np.ndarray:
    return np.array([lin(ROCK_COLOURS[r[1]]) for r in ROCKS])


# ---------------------------------------------------------------------------
# The colour function
# ---------------------------------------------------------------------------
def leaf_on(mo: dict, m: int) -> np.ndarray:
    """(NP, n) 0..1: how far each plant type is in leaf in month m, by
    vegetation.py's leaf habits (smoothed): evergreen always; summergreen
    above its temperature threshold; raingreen on a moist soil; grasses
    warm and moist enough. Moisture: the month's water (rain and
    snowmelt) against its potential evaporation, weighted with the two
    months before (MOIST_W: the soil remembers), capped at 1."""
    t = mo["t"][m]
    r = sum(w * mo["water"][m - k] / np.maximum(mo["pet"][m - k], 1.0) for k, w in enumerate(MOIST_W))
    r = np.clip(r, 0, 1)
    out = np.ones((V.NP, len(t)))
    for i, p in enumerate(V.PFTS):
        on = p["on"]
        if p["phen"] == V.SUMMERGREEN:
            out[i] = _smooth(on - 2.0, on + 2.0, t)
        elif p["phen"] == V.RAINGREEN:
            out[i] = _smooth(0.5 * on, 1.5 * on + 0.05, r) * _smooth(-2.0, 2.0, t)
        elif p["phen"] == V.HERBAL:
            out[i] = _smooth(on - 2.0, on + 3.0, t) * _smooth(0.08, 0.3, r)
    return out


def _soil_table() -> np.ndarray:
    return np.array([lin(SOIL_SURFACE[t[1]]) if SOIL_SURFACE[t[1]] else np.full(3, np.nan) for t in SO.TYPES])


def _bare(mo, temp, elev, rock, landform, soil=None) -> np.ndarray:
    pet = np.maximum(mo["pet"].sum(0), 1.0)
    mi = mo["p"].sum(0) / pet
    arid = _smooth(0.5, 0.08, mi)
    hot = _smooth(2.0, 20.0, temp)
    humid = _mix(lin(SOIL_HUMID_COLD), lin(SOIL_HUMID_WARM), hot)
    desert = _mix(lin(DESERT_COLD), _mix(lin(DESERT_RED), lin(DESERT_SAND), _smooth(0.15, 0.03, mi)), hot)
    c = _mix(humid, desert, arid)
    rock_w = 0.2 + 0.35 * arid
    if soil is not None:  # the soil's own surface colour where it is known (PW-206); thin soils show their rock
        st = _soil_table()[np.clip(np.asarray(soil, int), 0, len(SO.TYPES) - 1)]
        known = np.isfinite(st[:, 0])
        c = np.where(known[:, None], _mix(c, np.nan_to_num(st), SOIL_WEIGHT), c)
        rock_w = np.where(np.asarray(soil) == SO.THIN, 0.7, np.where(known, 0.6 * rock_w, rock_w))
    if rock is not None:
        rock = np.clip(np.asarray(rock, int), 0, len(ROCKS) - 1)
        rc = _rock_table()[rock]
        rc = np.where((rock == CRATON)[:, None], _mix(rc, lin(LATERITE), arid * hot), rc)
        c = _mix(c, rc, rock_w)
    if landform is not None:
        c = _mix(c, lin(DUNE_SAND), 0.75 * (np.asarray(landform) == DUNES))
    return _mix(c, lin(HIGH_ROCK), 0.6 * _smooth(2500.0, 4500.0, elev))


def colours(month: int, lat, elev, water, lake_depth, temp, t_warm, t_cold, p_jul, p_jan, nu, cover, tree,
            ice=None, lake_kind=None, rock=None, landform=None, wet=None, soil=None, tilt: float = 23.4,
            mo: dict | None = None, coastal: dict | None = None, landuse: dict | None = None) -> np.ndarray:
    """Linear-light colours (n, 3) of month (0 = January ... 11) for n places.
    water: 0 land, 1 sea, 2 lake; elev: ground (sea and lake floors
    included), m; lake_depth: m; temp, t_warm, t_cold: annual, warmest and
    coldest month, C; p_jul, p_jan: the half-years' rain, mm/yr; nu (NP, n):
    each plant type's share; cover, tree: plant and tree cover (0..1); ice:
    m of land ice; lake_kind: 1 fresh, 2 salt, 3 salt pan (None: by the
    climate, salt where dry); rock: exposed rock ids (surface.ROCKS);
    landform: class ids; soil: soils.TYPES ids (bare ground takes their colour); wet: flooded share (0..1). mo: climate.months of
    these places, when the caller has it. coastal: coastal life's shares
    (0..1; coastal.py) "reef", "kelp", "seagrass" (sea), "mangrove",
    "salt_marsh" (land). landuse: the peoples' land use of a zoom (zoom_peoples.py, PW-667): "use" (ids 0 wild, 1
    cropland, 2 pasture, 3 burned grass, 4 managed woods, 5 settlement) and "tone" (0..1 per field parcel)."""
    n = len(lat)
    if mo is None:
        mo = climate.months(lat, temp, t_warm, t_cold, p_jul, p_jan, tilt)
    water = np.asarray(water)
    elev = np.asarray(elev, float)
    m = month
    t_m = mo["t"][m]
    # --- land: ground, plants, wetlands
    c = _bare(mo, temp, elev, rock, landform, soil)
    g = leaf_on(mo, m)
    cold = 1 - _smooth(-1.0, 4.0, t_m)
    tot = np.maximum(nu.sum(0), 1e-9)
    veg = np.zeros((n, 3))
    for i, code in enumerate(V.CODES):
        on, off = PFT_COLOURS[code]
        green = lin(on)
        if off is None:
            col = np.broadcast_to(green, (n, 3))
        else:
            dormant = lin(off)
            if V.PFTS[i]["phen"] == V.HERBAL:
                dormant = _mix(np.broadcast_to(dormant, (n, 3)), lin(COLD_DORMANT), cold)
            col = _mix(dormant, green, g[i])
        veg += (nu[i] / tot)[:, None] * col
    c = _mix(c, veg, np.clip(cover, 0, 1) * (nu.sum(0) > 0.01))
    if landuse is not None:
        c = _landuse(c, landuse, g, cold, t_m, water)
    if wet is not None:
        c = _mix(c, lin(WETLAND), 0.35 * np.clip(wet, 0, 1))
    cz = {k: np.clip(np.asarray(v, float), 0, 1) for k, v in (coastal or {}).items()}
    if "salt_marsh" in cz:  # green in the growing season, straw-brown in winter
        sm = _mix(lin(SALT_MARSH[1]), lin(SALT_MARSH[0]), _smooth(2.0, 10.0, t_m))
        c = _mix(c, sm, cz["salt_marsh"] * (water == 0))
    if "mangrove" in cz:
        c = _mix(c, lin(MANGROVE), cz["mangrove"] * (water == 0))
    # --- snow, partly hidden by trees (evergreen crowns most)
    swe = 0.5 * (mo["snow"][m - 1] + mo["snow"][m])
    evg = sum(nu[i] for i, p in enumerate(V.PFTS) if p["cls"] == V.TREE and p["phen"] == V.EVERGREEN)
    trees = np.maximum(sum(nu[i] for i, p in enumerate(V.PFTS) if p["cls"] == V.TREE), 1e-9)
    mask = np.clip(tree, 0, 1) * (0.5 + 0.4 * np.clip(evg / trees, 0, 1))
    snow = (1 - np.exp(-swe / SNOW_SWE)) * (1 - mask)
    c = _mix(c, lin(SNOW), snow)
    # --- land ice: white, greyer-blue where it melts this month
    if ice is not None:
        ic = _mix(lin(LAND_ICE), lin(MELTING_ICE), _smooth(-2.0, 3.0, t_m) * (1 - snow))
        c = _mix(c, ic, _smooth(0.0, 30.0, np.asarray(ice, float)) * (water == 0))
    # --- lakes
    lake = water == 2
    if lake.any():
        d = np.maximum(np.asarray(lake_depth, float), 0)
        if lake_kind is None:  # (zooms) closed basins in dry country: salty
            mi = mo["p"].sum(0) / np.maximum(mo["pet"].sum(0), 1.0)
            kind = np.where(mi < 0.3, 2, 1)
        else:
            kind = np.asarray(lake_kind)
        lc = np.where((kind == 2)[:, None], _ramp(d, SALT_LAKE), _ramp(d, FRESH_LAKE))
        lc = np.where((kind == 3)[:, None], lin(SALT_PAN), lc)
        frozen = _smooth(-1.0, -6.0, t_m) * (kind != 3)
        lc = _mix(lc, _mix(lin(SEA_ICE), lin(SNOW), 1 - np.exp(-swe / SNOW_SWE)), frozen)
        c = np.where(lake[:, None], lc, c)
    # --- the sea: depth, warm carbonate shelves, sea ice
    sea = water == 1
    if sea.any():
        d = np.maximum(-elev, 0)
        sc = _ramp(d, SEA)
        carb = np.isin(np.asarray(rock), CARBONATE) if rock is not None else np.zeros(n, bool)
        shelf = (1 - _smooth(0.0, 60.0, d)) * _smooth(18.0, 25.0, temp) * np.where(carb, 0.85, 0.45)
        sc = _mix(sc, lin(SHELF_TURQUOISE), shelf)
        # coastal life on the sea floor (seen through the water: fainter deeper down; the kelp's
        # canopy floats at the surface)
        vis = 1 - 0.6 * _smooth(5.0, 40.0, d)
        for k, col, a in (("seagrass", SEAGRASS, 0.55 * vis), ("kelp", KELP, 0.6), ("reef", REEF, 0.75 * vis)):
            if k in cz:
                sc = _mix(sc, lin(col), a * cz[k])
        frozen = _smooth(climate.FREEZE + 1.0, climate.FREEZE - 3.0, t_m)
        sc = _mix(sc, _mix(lin(SEA_ICE), lin(SNOW), 1 - np.exp(-swe / SNOW_SWE)), frozen)
        c = np.where(sea[:, None], sc, c)
    return c


# the peoples' land use on a zoom (zoom_peoples.py, PW-667): fields (plough, crop, stubble), pasture, burned ground, villages
FIELD = {"plough": "#8c6d4b", "crop": "#a3b24a", "ripe": "#d3b45c"}
PASTURE_COL = ("#8f9a5a", "#a9bf62")  # (dormant, growing)
BURNED_COL = "#a98a52"
TOWN_COL = "#8d7b6a"


def _landuse(c, lu, g, cold, t_m, water):
    """Linear-light colours c with the cleared land painted over the plants: fields in patches (a parcel's tone: the
    crop's stage, ploughed earth to green to ripe, winter-bare in the cold), pasture, burned grass and village ground."""
    use, tone = np.asarray(lu["use"]), np.asarray(lu["tone"], float)
    gc = g[V.IDX["C3G"]]  # (the growing season of grass)
    plough = np.broadcast_to(lin(FIELD["plough"]), c.shape)
    crop = _mix(plough, np.broadcast_to(lin(FIELD["crop"]), c.shape), _smooth(0.2, 0.55, tone))  # (each parcel's own stage)
    crop = _mix(crop, np.broadcast_to(lin(FIELD["ripe"]), c.shape), _smooth(0.7, 0.85, tone))
    field = _mix(_mix(plough, lin(COLD_DORMANT), 0.4), crop, _smooth(0.1, 0.6, gc))  # (the season: bare earth and stubble in the off season)
    field = _mix(field, lin(COLD_DORMANT), 0.5 * cold)
    past = _mix(np.broadcast_to(lin(PASTURE_COL[0]), c.shape), np.broadcast_to(lin(PASTURE_COL[1]), c.shape), gc)
    past = _mix(past, lin(COLD_DORMANT), 0.5 * cold)
    land = water == 0
    for k, col, a in ((1, field, 0.85), (2, past, 0.40), (3, np.broadcast_to(lin(BURNED_COL), c.shape), 0.65),
                      (5, np.broadcast_to(lin(TOWN_COL), c.shape), 0.7)):
        c = _mix(c, col, a * ((use == k) & land))
    return c


def seasons(lat, **kw) -> dict:
    """{'jul', 'jan', 'year'}: sRGB uint8 (n, 3) colours (colours()'s
    arguments as keywords; the months are computed once)."""
    lat = np.asarray(lat, float)
    if kw.get("mo") is None:
        kw["mo"] = climate.months(lat, kw["temp"], kw["t_warm"], kw["t_cold"], kw["p_jul"], kw["p_jan"],
                                  kw.get("tilt", 23.4))
    out = {s: colours(MONTH[s], lat, **kw) for s in ("jul", "jan")}
    w = _smooth(-YEAR_BLEND, YEAR_BLEND, lat)  # 1 north (July), 0 south (January)
    out["year"] = _mix(out["jan"], out["jul"], w)
    return {k: srgb8(v) for k, v in out.items()}


def pack(rgb: np.ndarray) -> np.ndarray:
    """uint8 (n, 3) -> int 0xRRGGBB (the world's sat layers)."""
    rgb = np.asarray(rgb, np.int64)
    return (rgb[:, 0] << 16) | (rgb[:, 1] << 8) | rgb[:, 2]


def unpack(v) -> np.ndarray:
    v = np.asarray(v, np.int64)
    return np.stack([(v >> 16) & 255, (v >> 8) & 255, v & 255], -1).astype(np.uint8)


# ---------------------------------------------------------------------------
# Worlds and zooms
# ---------------------------------------------------------------------------
WORLD_LAYERS = {"year": "sat", "jul": "sat_jul", "jan": "sat_jan"}


def world_layers(grid, L: dict, tilt: float = 23.4) -> dict:
    """The world's satellite layers (sat, sat_jul, sat_jan: 0xRRGGBB) from
    its other layers (needs the vegetation's veg_<PFT>)."""
    elev = np.asarray(L["elevation"], float)
    temp = np.asarray(L["temperature"], float)
    tw = np.asarray(L.get("warm_month", L["temperature"]), float)
    tc = np.asarray(L.get("cold_month", 2 * temp - tw), float)
    kind = np.asarray(L.get("lake_kind", np.zeros(grid.n)), int)
    land = world_land(L)  # (a bed below the sea under grounded ice is land: its ice is drawn)
    lake = land & (kind > 0)
    water = np.where(~land, 1, np.where(lake, 2, 0))
    depth = np.asarray(L.get("lake_level", elev), float) - elev
    nu = np.stack([np.asarray(L[f"veg_{c}"], float) / 100 for c in V.CODES])
    col = seasons(grid.lat, elev=elev, water=water, lake_depth=depth, temp=temp, t_warm=tw, t_cold=tc,
                  p_jul=np.asarray(L["precipitation_jul"], float), p_jan=np.asarray(L["precipitation_jan"], float),
                  nu=nu, cover=np.asarray(L["plant_cover"], float) / 100, tree=np.asarray(L["tree_cover"], float) / 100,
                  ice=L.get("ice"), lake_kind=kind, rock=L.get("surface_rock"), landform=L.get("landform"), soil=L.get("soil"),
                  wet=np.asarray(L["flooded"], float) / 100 if "flooded" in L else None, tilt=tilt,
                  coastal={k: np.asarray(L[k], float) / 100 for k in COASTAL if k in L})
    return {WORLD_LAYERS[s]: pack(v) for s, v in col.items()}


COASTAL = ("reef", "kelp", "seagrass", "mangrove", "salt_marsh")  # coastal.LAYERS
ZOOM_COASTAL = {"reef": 1, "kelp": 2, "seagrass": 3, "mangrove": 4, "salt_marsh": 5}  # zoom_coastal.LIFE ids


def parcel_tone(ny: int, nx: int, res_km: float, parcel_km: float = 3.0) -> np.ndarray:
    """0..1 per pixel, a fixed pseudo-random value for each parcel (square block of ~parcel_km): the patchwork of fields."""
    k = max(1, int(round(parcel_km / res_km)))
    r, q = np.meshgrid(np.arange(ny) // k, np.arange(nx) // k, indexing="ij")
    h = (r * 73856093 ^ q * 19349663 ^ 0x5bd1e995) & 0xFFFFFFFF
    h = ((h ^ (h >> 15)) * 2246822519) & 0xFFFFFFFF
    return ((h ^ (h >> 13)) & 0xFFFF).astype(float).ravel() / 65535.0


def zoom_images(Lz: dict, nu: np.ndarray, lat: np.ndarray, tilt: float = 23.4, res_km: float = 1.0) -> dict:
    """{'jul', 'jan', 'year'}: (ny, nx, 3) uint8 unshaded colours of a zoom.
    Lz: its layers (real units; (ny, nx)); nu (NP, ny*nx): the per-pixel
    plant fractions (zoom_vegetation); lat (ny*nx,)."""
    ny, nx = Lz["elevation"].shape
    f = {k: np.asarray(v).ravel() for k, v in Lz.items()}
    tj, tn = f["temperature_jul"].astype(float), f["temperature_jan"].astype(float)
    tw, tc, temp = np.maximum(tj, tn), np.minimum(tj, tn), f["temperature"].astype(float)
    pj, pn = f["precipitation_jul"].astype(float), f["precipitation_jan"].astype(float)
    # (the months on the seasons the pixel has: July summer where it is the
    # warmer month, which near the equator need not follow the latitude's sign, PW-374)
    lat = np.asarray(lat, float)
    mo = climate.months(np.where(tj >= tn, np.abs(lat), -np.abs(lat)), temp, tw, tc, pj, pn, tilt)
    col = seasons(lat, elev=f["elevation"].astype(float), water=f["water"], lake_depth=f["lake_depth"],
                  temp=temp, t_warm=tw, t_cold=tc, p_jul=pj, p_jan=pn, mo=mo,
                  nu=nu, cover=f["plant_cover"].astype(float) / 100, tree=f["tree_cover"].astype(float) / 100,
                  ice=f["ice"], rock=f.get("surface_rock"), landform=f.get("landform"), soil=f.get("soil"), lake_kind=f.get("lake_kind"),
                  wet=(f["wetland"] > 0) * 0.6 if "wetland" in f else None, tilt=tilt,
                  coastal={k: f["coastal_life"] == i for k, i in ZOOM_COASTAL.items()} if "coastal_life" in f else None,
                  landuse={"use": f["land_use"], "tone": parcel_tone(ny, nx, res_km)} if "land_use" in f else None)
    return {k: v.reshape(ny, nx, 3) for k, v in col.items()}
