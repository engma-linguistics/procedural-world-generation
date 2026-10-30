"""Fuels by region (PW-722): what each cell burns to cook and heat, for a peoples run's present.

Nothing here knows a people's name. Per peopled cell, from the same inputs as the land use (landuse.py: the tree cover
left after clearing and cutting, pasture, cropland, settlement) and from the world and the run:

    wood      standing trees left (the tree cover after clearing and cutting)
    charcoal  burned from wood where settlement is dense (towns and smiths), taken out of the wood share
    dung      dried dung of the herd animals known there (horses, sheep and goats, cattle...), on pasture and fields
    peat      cut peat, from the world's peat_depth
    straw     the stalks and straw of the staple crops known there (crops.py: the grain grasses leave much, the tubers little)
              on the cropland
    grass     dry grass, brush and hay on grazing land, the fuel of last resort
    drift     driftwood and dried seaweed on treeless coasts
    coal      the world's coal outcrops (res_coal), for peoples settled on them who know it (COAL_ERA: the era of the tree
              stands in for a people's tech until the tech tree, PW-675: before the classical era nobody digs it, then more)
    heath     the grass fuel's cold twin: heath, dwarf birch and willow, lichen and moss where the year's mean is below
              HEATH_T (tundra, moors, the subarctic): treeless but not grassland (PW-739)
    oil       sea-mammal oil (seal and whale blubber lamps and stoves) on coasts with seals and whales (the `sea_mammals` good),
              the more where wood is scarce
    tallow    rendered fat of herd animals and game, where herds are known and trees are scarce
    bone      bone burned (with fat) on treeless herd and hunting ground: the poorest fuel (PW-739)

Each fuel's availability (0..1) times how convenient it is to cook with (`PREF`: wood best, grass worst) gives its share,
so a treeless steppe with herds burns dung (low, slow fires), a forest wood, a bog peat, a grain plain straw and
stalks. Crude on purpose: relative yields of a pre-industrial land, an anchor and not a target.

    derive(run_dir)  -> {"layers": per-fuel shares 0..1 per cell, "lead", "summary"}  (reads the run, not written)
    write(run_dir)   -> adds layers/fuel_*.bin, meta.fuels, a line in each people's story and a section of run.txt
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .. import store as S
from ..grid import shared_grid
from . import animal_defs as AD
from .gridops import nbr_reduce
from . import land as LD
from . import landuse as LU
from . import spec as SP

FUELS = ("wood", "charcoal", "dung", "peat", "straw", "grass", "drift", "coal", "heath", "oil", "tallow", "bone")
PHRASE = {"wood": "wood fires", "charcoal": "charcoal fires", "dung": "dung fires", "peat": "peat fires", "straw": "straw-and-stalk fires",
          "grass": "dry-grass-and-brush fires", "drift": "driftwood-and-seaweed fires", "coal": "coal fires", "heath": "heath-and-dwarf-shrub fires",
          "oil": "seal-and-whale-oil lamps and stoves", "tallow": "tallow fires", "bone": "bone-and-fat fires"}
COLORS = {"wood": "#3f7d3a", "charcoal": "#3b3b3b", "dung": "#b07a3a", "peat": "#6b4a2b", "straw": "#e0c04a", "grass": "#a9c25a",
          "drift": "#4a9fb5", "coal": "#8a8a99", "heath": "#8d8f5e", "oil": "#d9b26f", "tallow": "#e8d9b5", "bone": "#c9c2b0"}
PREF = {"wood": 1.0, "peat": 0.7, "dung": 0.55, "straw": 0.5, "coal": 0.9, "drift": 0.6, "grass": 0.3, "heath": 0.4, "oil": 0.8, "tallow": 0.5, "bone": 0.25}  # how good it is to cook over
CHARCOAL = 0.3  # of the wood burned by a dense settlement (10+ people/km2) is made into charcoal
CHAR_DENS = 10.0
PEAT_MIN_M, PEAT_FULL_M = 0.3, 1.5  # peat thinner than the first is not cut; the second is a full supply
WOOD_DEPLETE = 40.0  # settlement (people/km2) at which the wood left is halved by cutting
COAL_FROM, COAL_FULL = 0.3, 0.7  # res_coal likelihood where coal outcrops are worked
# coal needs a people who dig and burn it: the target era stands in for the tech tree (PW-675). Surface "sea coal" is picked up
# from the classical era (Roman Britain, Han China), mines and coal fires are common by the medieval, and by the renaissance
# every outcrop is worked (the preset's era).
COAL_ERA = {"stone age": 0.0, "bronze age": 0.0, "classical": 0.35, "medieval": 0.75, "renaissance": 1.0, "industrial": 1.0}
HEATH_T = (6.0, -2.0)  # mean annual temperature C: the grass fuel is all grass at the first, all heath at the second
FAT_TREELESS = 0.3  # tree cover (0..1) at and above which wood is no scarcer than fat
OIL_SHARE = 0.6  # the sea-mammal oil good counts this much (0..1) in the availability; its lamps burn beside wood too
TALLOW_SHARE, BONE_SHARE = 0.3, 0.2
LEAD_MOSTLY = 0.55  # a people "cooks mostly over X" when X is at least this share of its fuel
LEAD_LISTED = 0.2
BIOMES = (("rainforest", [0, 1]), ("savanna", [2]), ("desert", [3, 4]), ("steppe", [5, 6]), ("mediterranean", [7, 8, 9]),
          ("temperate", list(range(10, 16))), ("subarctic", [18, 19, 22, 23, 26, 27]), ("continental", list(range(16, 28))),
          ("tundra and polar", [28, 29]))
HERD_ANIMALS = tuple(a.id for a in AD.TABLE if "herd" in a.tame)


def mix(tc, pasture, crop, dens, herd_known, peat_m, straw_mix, graze, coast, coal, sea=None, temp=None, coal_known=1.0) -> dict:
    """Fuel shares (0..1, summing to 1 where anyone lives, else 0) per cell from: the tree cover left, the pasture and cropland
    shares of the cell, settlement (people/km2), herd animals known (0/1), peat thickness (m), the staples' straw (0..1), the
    grazing good (0..1), the coast mask and the coal good (0..1); optionally the sea-mammal good (0..1), the mean annual temperature
    (C; None: no heath) and how much of the coal is known to the people (COAL_ERA)."""
    z = np.zeros_like(np.asarray(tc, float))
    sea = z if sea is None else sea
    cold = z if temp is None else np.clip((HEATH_T[0] - temp) / (HEATH_T[0] - HEATH_T[1]), 0, 1)
    open_ground = 1.0 - np.clip(tc / FAT_TREELESS, 0, 1)  # (wood is scarce)
    scrub = np.clip(graze / 0.6, 0, 1) * (1 - np.clip(tc, 0, 1)) * 0.5
    a = {
        "wood": np.clip(tc, 0, 1) / (1.0 + dens / WOOD_DEPLETE),
        "dung": herd_known * np.clip(np.maximum(pasture, 0.25 * crop) / 0.3, 0, 1),
        "peat": np.clip((peat_m - PEAT_MIN_M) / (PEAT_FULL_M - PEAT_MIN_M), 0, 1),
        "straw": np.clip(crop / 0.4, 0, 1) * straw_mix,
        "grass": scrub * (1 - cold),
        "heath": scrub * cold,
        "oil": np.where(coast, np.clip(sea, 0, 1) * OIL_SHARE * (0.4 + 0.6 * open_ground), 0.0),
        "tallow": (0.5 + 0.5 * herd_known) * np.clip(np.maximum(pasture / 0.3, graze / 0.6), 0, 1) * TALLOW_SHARE * open_ground,
        "bone": (0.5 + 0.5 * herd_known) * np.clip(np.maximum(pasture / 0.3, graze / 0.6), 0, 1) * BONE_SHARE * open_ground,
        "drift": np.where(coast, 1.0 - np.clip(tc / 0.3, 0, 1), 0.0) * 0.6,
        "coal": np.clip((coal - COAL_FROM) / (COAL_FULL - COAL_FROM), 0, 1) * coal_known,
    }
    # fat and bone are what is burned when nothing better is to hand: they fill what wood, dung, peat, straw and coal leave
    best = np.maximum.reduce([np.clip(a[k], 0, 1) for k in ("wood", "dung", "peat", "straw", "coal")])
    for k in ("tallow", "bone"):
        a[k] = a[k] * (1.0 - best)
    w = {k: a[k] * PREF[k] for k in a}
    tot = sum(w.values())
    ok = (dens >= 0.05) & (tot > 1e-6)
    sh = {k: np.where(ok, w[k] / np.maximum(tot, 1e-9), 0.0) for k in w}
    sh["charcoal"] = sh["wood"] * CHARCOAL * np.clip(dens / CHAR_DENS, 0, 1)
    sh["wood"] = sh["wood"] - sh["charcoal"]
    return sh


def at_frame(m: dict, goods: dict, q: dict, tc: np.ndarray, animal_bits: np.ndarray | None, crop_bits: np.ndarray | None) -> dict:
    """Fuel shares at a stored frame of the run (PW-742): the frame's land use inputs (landuse.frame_inputs, stored `q`), tree cover
    (0..1), the animals and crops known there; the world's goods are those of its slice moment. Like `derive`, but with the crops'
    `know` and `straw` taken from the stocks known at the frame (every grown stock counts at full growth)."""
    n = m["cells"]
    land = goods["_land"]
    g = shared_grid(m["level"])
    coast = land & nbr_reduce(g, np.logical_or, ~land[g.nbr_idx])
    herd_known = np.zeros(n)
    stocks = (m.get("animals") or {}).get("stocks") or {}
    if animal_bits is not None:
        for aid, st in stocks.items():
            if aid in HERD_ANIMALS:
                herd_known = np.maximum(herd_known, ((animal_bits.astype(np.int64) >> st["bit"]) & 1).astype(float))
    w, sw = np.zeros(n), np.zeros(n)
    if crop_bits is not None:
        for st in ((m.get("crops") or {}).get("stocks") or {}).values():
            x = st.get("weight", 0.0) * ((crop_bits.astype(np.int64) >> st["bit"]) & 1)
            w += x
            sw += x * st.get("straw", 0.0)
    know = np.minimum(w, 1.0)
    straw = np.where(w > 0, sw / np.maximum(w, 1e-9), 0.0)
    fcls = np.clip(np.rint(np.asarray(goods["_raw"]["fertile"]) * 4).astype(int), 0, 4)
    graze = goods["grazing"] if "grazing" in goods else np.zeros(n)
    inp = LU.inputs_from(q)
    cov = LU.cover(inp["dens"], inp["farm"], inp["herd"], inp["wood"], np.clip(tc, 0, 1) * land, fcls, graze, inp["herd_eff"], inp["farm_eff"], know)
    return mix(cov["tree_after"], cov["pasture"], cov["crop"], cov["people"], herd_known, goods.get("_peat", np.zeros(n)), straw, graze, coast,
               goods["coal"] if "coal" in goods else np.zeros(n), sea=goods["sea_mammals"] if "sea_mammals" in goods else None, temp=goods.get("_temp"),
               coal_known=COAL_ERA[m.get("era") or SP.ERA_DEFAULT])


def _last(run_dir: Path, run: dict, key: str):
    spec = run["layers"][key]
    return np.asarray(S.decode(np.asarray(S.read_layer(run_dir, spec)[-1]), spec))


def derive(run_dir: Path) -> dict:
    run_dir = Path(run_dir)
    run, m = LU._load(run_dir)
    d = LU.derive(run_dir)
    lay = d["layers"]
    goods = LD.goods(m["world"])
    n = m["cells"]
    land = goods["_land"]
    g = shared_grid(m["level"])
    coast = land & nbr_reduce(g, np.logical_or, ~land[g.nbr_idx])
    herd = np.zeros(n)
    stocks = (m.get("animals") or {}).get("stocks") or {}
    if "animal_known" in run["layers"] and stocks:
        bits = _last(run_dir, run, "animal_known").astype(np.int64)
        for aid, st in stocks.items():
            if aid in HERD_ANIMALS:
                herd = np.maximum(herd, ((bits >> st["bit"]) & 1).astype(float))
    cl = (m.get("crops") or {}).get("layers") or {}
    straw = np.fromfile(run_dir / cl["straw"]["file"], np.uint8).astype(float) / 100.0 if "straw" in cl else np.full(n, 0.8)
    sh = mix(lay["tree_after"], lay["pasture"], lay["crop"], lay["people"], herd, goods.get("_peat", np.zeros(n)), straw,
             goods["grazing"] if "grazing" in goods else np.zeros(n), coast, goods["coal"] if "coal" in goods else np.zeros(n),
             sea=goods["sea_mammals"] if "sea_mammals" in goods else None, temp=goods.get("_temp"),
             coal_known=COAL_ERA[m.get("era") or SP.ERA_DEFAULT])
    stack = np.stack([sh[k] for k in FUELS])
    lead = np.where(stack.sum(0) > 0, stack.argmax(0), 255).astype(np.uint8)
    area = 4 * np.pi * 6371.0 ** 2 / n  # km2 per cell
    pop = lay["people"] * area * land  # people per cell
    # the mix by people (everyone's fuel weighted by heads) and by biome
    tot_pop = max(float(pop.sum()), 1.0)
    world = {k: round(float((sh[k] * pop).sum() / tot_pop), 3) for k in FUELS}
    cli = _last(run_dir, run, "climate").astype(int)
    by_biome = {}
    for name, ids in BIOMES:
        sel = np.isin(cli, ids) & (pop > 0)
        if sel.any():
            by_biome[name] = {"people": int(pop[sel].sum()), **{k: round(float((sh[k][sel] * pop[sel]).sum() / pop[sel].sum()), 3) for k in FUELS}}
    pres = np.fromfile(run_dir / m["presence_present"]["file"], np.uint8).reshape(m["presence_present"]["shape"]).astype(float) / 100.0
    by_line = {}
    for k, ln in enumerate(m["lineages"]):
        w = pres[k] * pop * (land & (pres[k] >= 0.12))
        if w.sum() <= 0:
            continue
        mixl = {f: float((sh[f] * w).sum() / w.sum()) for f in FUELS}
        top = sorted(mixl.items(), key=lambda x: -x[1])
        by_line[ln["id"]] = {"people": int(w.sum()), **{f: round(v, 3) for f, v in mixl.items()}, "lead": top[0][0], "lead_share": round(top[0][1], 3),
                             "sentence": sentence(top)}
        if (ln.get("body") or {}).get("fire") is False:  # (a people that cooks without fire, body.fire = false, PW-726: the land's fuels are not theirs)
            by_line[ln["id"]].update({"lead": None, "lead_share": 0.0, "fire": False, "sentence": "It cooks without fire."})
    return {"layers": sh, "lead": lead, "summary": {"world": world, "by_biome": by_biome, "by_line": by_line,
                                                   "lead_cells": {FUELS[i]: int((lead == i).sum()) for i in range(len(FUELS))}}}


def sentence(top: list) -> str:
    """'It cooks mostly over dung fires.' / 'It cooks over wood fires and peat fires.' from fuels sorted by share (largest first)."""
    (f0, s0) = top[0]
    if s0 >= LEAD_MOSTLY:
        return f"It cooks mostly over {PHRASE[f0]}."
    some = [PHRASE[f] for f, s in top if s >= LEAD_LISTED][:3]
    if not some:
        some = [PHRASE[f0]]
    return "It cooks over " + (", ".join(some[:-1]) + " and " if len(some) > 1 else "") + some[-1] + "."


def write(run_dir: Path, report: bool = True) -> dict:
    """Adds layers/fuel_*.bin (one frame: the present), meta.fuels, a sentence to each people's story and a run.txt section."""
    run_dir = Path(run_dir)
    d = derive(run_dir)
    n = len(d["lead"])
    (run_dir / "layers").mkdir(exist_ok=True)
    specs = {}
    files = {"lead": d["lead"], **{k: np.clip(np.rint(100 * d["layers"][k]), 0, 100).astype(np.uint8) for k in FUELS}}
    for k, arr in files.items():
        S.write_atomic(run_dir / "layers" / f"fuel_{k}.bin", arr.tobytes())
        specs[k] = {"file": f"layers/fuel_{k}.bin", "dtype": "uint8", "shape": [1, n], "units": "index" if k == "lead" else "% of the cell's fuel",
                    "description": "the leading fuel of the cell (index into meta.fuels.names; 255 none)" if k == "lead" else f"share of the cell's fuel that is {k}"}
    sm = d["summary"]

    def add(run):
        run["meta"]["fuels"] = {"layers": specs, "names": list(FUELS), "colors": COLORS, "phrases": PHRASE, "summary": sm,
                                "constants": {"coal_era": COAL_ERA, "heath_t": HEATH_T, "pref": PREF, "charcoal": CHARCOAL, "char_dens": CHAR_DENS, "peat_full_m": PEAT_FULL_M}}
        for ln in run["meta"]["lineages"]:
            bl = sm["by_line"].get(ln["id"])
            if bl and ln.get("story"):
                ln["story"] = ln["story"].split(" It cooks ")[0] + " " + bl["sentence"]
                run["meta"]["present"].setdefault("stories", {})[ln["id"]] = ln["story"]

    S.update_meta(run_dir, add)
    if report:
        with open(run_dir / "run.txt", "a") as f:
            f.write("\n".join(lines_for_report(sm)) + "\n")
    return sm


def lines_for_report(sm: dict) -> list[str]:
    def row(label, v):
        return f"  {label:<20}" + "".join(f"{round(100 * v[k]):>5}%" for k in FUELS) + (f"  {v['people']:>13,}" if "people" in v else "")
    L = ["", "## Fuels (PW-722): the share of each people's cooking and heating fuel (by heads)",
         f"  {'':<20}" + "".join(f"{k[:6]:>6}" for k in FUELS) + f"  {'people':>13}",
         row("whole world", sm["world"]), "  -- by biome"]
    L += [row(b, v) for b, v in sm["by_biome"].items()]
    L += ["  -- by people"]
    L += [row(lid, v) + f"  {v['sentence']}" for lid, v in sorted(sm["by_line"].items(), key=lambda x: -x[1]["people"])[:24]]
    return L
