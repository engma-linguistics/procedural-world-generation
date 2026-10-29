"""Peoples change the land (PW-662): an anthropogenic land-cover overlay for a peoples run's present.

Nothing here knows a people's name. Each line's way of life comes from the tree's [[use]] table (its traits,
preferred places and own id pick the rows, spec.Tree.uses_of): the weights on the goods that feed a people
(`fertile` farming, `grazing` herding, `timber` / `foraging` woodland) give its shares; its numbers come from the
run (presence at the present x the line's density x cell area, as History.population). Overlays (templates and
contact hybrids) are shares of their hosts' people and are not counted twice.

Per cell, from the people there (people/km2 by way of life) and the land's own goods:

    cropland      farming people/km2 x CROP_KM2 (land per person) / yield of the farmland class, up to its cap
    pasture       herding people/km2 x HERD_KM2, and a little hay and fallow meadow around farmers (MEADOW_KM2),
                  on grazing land, outside the cropland
    burned        fire-kept grassland: herders burn woodland margins (BURN_KM2 per herding person) on grazing land
    managed       woodland cut for timber and fuel or coppiced: everyone needs fuel (WOOD_BASE_KM2 per person),
                  timber users a good deal more (WOOD_USE_KM2 x their timber share); of what trees are left
    settlement    all people per km2 (stored log2p1)
    tree_after    tree cover left (cleared for fields and pasture, burned, thinned in managed woods)

A planet-relative "land per person" would be better than the Earth-shaped constants below; the constants are a
modest, pre-industrial first guess (Earth ~1700: ~0.6 ha cropland per person, a few times that in pasture), an
anchor and not a target. History (soil exhaustion, collapse, warfare) is the civilization epic's (PW-661).

    derive(run_dir)  -> dict of the layers and a summary (reads the run, not written)
    write(run_dir)   -> adds layers/anthro_*.bin and meta.anthro to a peoples run (in place; redoes it)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .. import store as S
from ..geo import R_KM
from . import animal_defs as AD
from . import land as LD
from . import spec as SP
from .spread import EST

CROP_KM2 = 0.007  # cropland per farming person (0.7 ha: Earth ~1700 AD)
YIELD = (0.0, 0.55, 0.8, 1.0, 1.15)  # by humanuse farmland class (none, marginal, fair, good, prime): output per area
CROP_CAP = (0.0, 0.35, 0.6, 0.85, 0.95)  # the most of a cell farmed, by class (roads, woods, wet and steep ground stay)
HERD_KM2 = 0.15  # grazing land per herding person (15 ha: extensive pastoralism)
MEADOW_KM2 = 0.01  # hay, fallow and common pasture per farming person
BURN_KM2 = 0.10  # woodland margin burned per herding person
WOOD_BASE_KM2 = 0.003  # woods cut and coppiced for fuel and building, per person of any way of life
WOOD_USE_KM2 = 0.03  # extra, per timber-using person x their timber share
THIN = 0.3  # a managed wood keeps this much less canopy

GRAZE_MIN = 0.1  # grazing good (0..1) under which pasture is not made
FOOD = ("fertile", "grazing", "timber", "foraging")  # the goods that feed a people: the denominator of its shares
LAYERS = ("crop", "pasture", "burned", "managed", "people", "tree_after")
PEOPLE_SCALE = 0.05  # anthro_people stored log2p1: people/km2 = 2^(stored x scale) - 1
UNITS = {"crop": "% of the cell", "pasture": "% of the cell", "burned": "% of the cell", "managed": "% of the cell",
         "people": "people/km2", "tree_after": "% tree cover"}
DOC = {
    "crop": "cleared cropland: share of the cell under fields, from the farming peoples there and the farmland class",
    "pasture": "pasture and meadow: share of the cell grazed by herders (and meadow around farmers)",
    "burned": "fire-kept grassland: share of the cell where herders have burned woodland into grass",
    "managed": "managed or cut woodland: share of the cell cut for timber and fuel or coppiced",
    "people": "settlement density: all peoples, people/km2 (stored log2p1, scale 0.05)",
    "tree_after": "tree cover (%) left after clearing, pasture, burning and cutting",
}


def shares(tree: SP.Tree, l: SP.Lineage) -> dict:
    """A line's way of life from the [[use]] table: {farm, herd, wood, forage} (farm + herd + wood summing to at most 1;
    forage = its share of the wild-food use, `foraging`, or 1 for a hunter; gather = the wild-food use alone (who first cultivates plants); 0 when it uses none of the goods that feed a people: foragers of
    other things, miners, flyers...). The hunter trait counts as a full forage use (PW-718: who tames the dog)."""
    w = {g: max(v, 0.0) for g, v in tree.uses_of(l) if g in FOOD}
    tot = sum(w.values())
    hunt = 1.0 if "hunter" in l.traits and not l.way else 0.0  # (a way of life says it itself: forager, fisher_forager)
    if l.way in ("forager", "fisher_forager", "sea_nomad"):
        hunt = 1.0
    if tot <= 0:
        return {"farm": 0.0, "herd": 0.0, "wood": 0.0, "forage": hunt, "gather": 0.0}
    return {"farm": w.get("fertile", 0.0) / tot, "herd": w.get("grazing", 0.0) / tot,
            "wood": (w.get("timber", 0.0) + 0.3 * w.get("foraging", 0.0)) / tot,
            "forage": min(1.0, hunt + w.get("foraging", 0.0) / tot), "gather": w.get("foraging", 0.0) / tot}


def _load(run_dir: Path):
    run = json.loads((run_dir / "run.json").read_text())
    m = run["meta"]
    if m.get("phase") != "lineages":
        raise ValueError(f"{run_dir.name} is not a peoples run")
    if not m.get("world"):
        raise ValueError(f"{run_dir.name} has no world (no farmland to read)")
    return run, m


CROP_FLOOR = 0.3  # fields without any staple crop known (crops.py) are this share of what they would be with one (PW-721)


def cover(dens, farm, herd, wood, tc, fcls, graze, herd_eff=None, farm_eff=None, know=None) -> dict:
    """Land cover fractions per cell from the people per km2 (all, farming, herding, timber-using), the wild tree
    cover (0..1), the farmland class (0..4) and the grazing good (0..1). herd_eff: the herding people weighted by
    the land a herder works (mounted herders work more: animal_defs herd_land) and farm_eff likewise for farmers (the plough: crop_land); default `herd` and `farm`."""
    herd_eff = herd if herd_eff is None else herd_eff
    farm_eff = farm if farm_eff is None else farm_eff
    grazable = np.clip(graze / 0.6, 0, 1) * (graze >= GRAZE_MIN)
    crop = np.minimum(np.array(CROP_CAP)[fcls], farm_eff * CROP_KM2 / np.maximum(np.array(YIELD)[fcls], 1e-9))
    if know is not None:  # (no staple crop known: little is sown)
        crop = crop * (CROP_FLOOR + (1.0 - CROP_FLOOR) * know)
    room = 1.0 - crop
    pasture = np.minimum(room * 0.9 * grazable, herd_eff * HERD_KM2 + farm * MEADOW_KM2 * (grazable > 0))
    t1 = tc * (1 - crop)
    t2 = t1 * (1 - pasture / np.maximum(room, 1e-9))  # (pasture thins the woods it takes in proportion)
    burned = np.minimum(t2, herd_eff * BURN_KM2 * (grazable > 0))
    t3 = t2 - burned
    managed = np.minimum(1.0, dens * WOOD_BASE_KM2 + wood * WOOD_USE_KM2) * t3  # (managed wood: a share of the trees left)
    return {"crop": crop, "pasture": pasture, "burned": burned, "managed": managed, "people": dens,
            "tree_after": t3 - THIN * managed}


ERA_WINDOW_KYR = 12.5  # frames this recent keep the land-use inputs (frame_inputs) for the brief's fuels per era (PW-742)
ERA_KEYS = ("dens", "farm", "herd", "wood", "herd_mult", "farm_mult")
MULT_SCALE = 20.0  # herd_mult / farm_mult stored x this (1..12.75)


def frame_inputs(h, P: np.ndarray, land: np.ndarray) -> dict:
    """The land use's inputs at a frame of the run (as `derive` reads them for the present), quantised to uint8: `dens` (all
    people/km2, log2p1 / PEOPLE_SCALE), `farm`, `herd`, `wood` (% of the cell's people that farm, herd, use timber), `herd_mult` and
    `farm_mult` (the herders' and farmers' land per person from the animals known, x MULT_SCALE). P: line presence (overlays count
    only where they are a people of their own); h: the History."""
    L, n = P.shape
    sh = getattr(h, "_lu_sh", None)
    if sh is None:
        sh = h._lu_sh = np.array([[0.0, 0.0, 0.0] if l.overlay else [shares(h.tree, l)[k] for k in ("farm", "herd", "wood")] for l in h.lines]).reshape(L, 3)
    d = P * h.dens_cells() * land[None, :]
    d = d * np.array([not l.overlay for l in h.lines])[:, None]
    hl, cl = np.zeros((L, n)), np.zeros((L, n))
    if h.animals is not None:
        for s in h.animals.stocks:
            k = (s.rd >= EST)[None, :] * s.prop[:, None]
            hl += s.a.herd_land * k
            cl += s.a.crop_land * k * (1.0 if s.tamed else 0.0)
    dens = d.sum(0)
    farm, herd, wood = (sh[:, j] @ d for j in range(3))
    herd_eff, farm_eff = (sh[:, 1][:, None] * d * (1 + hl)).sum(0), (sh[:, 0][:, None] * d * (1 + cl)).sum(0)
    q = lambda v: np.clip(np.rint(v), 0, 255).astype(np.uint8)  # noqa: E731
    frac = lambda v: q(100 * v / np.maximum(dens, 1e-9))  # noqa: E731
    return {"dens": q(np.log2(1 + dens) / PEOPLE_SCALE), "farm": frac(farm), "herd": frac(herd), "wood": frac(wood),
            "herd_mult": q(MULT_SCALE * herd_eff / np.maximum(herd, 1e-9)) if herd.any() else q(np.full(n, MULT_SCALE)),
            "farm_mult": q(MULT_SCALE * farm_eff / np.maximum(farm, 1e-9)) if farm.any() else q(np.full(n, MULT_SCALE))}


def inputs_from(q: dict) -> dict:
    """The arrays `cover` takes (people/km2 and the herding, farming and timber-using people/km2, with the herd_eff and farm_eff) from a stored frame_inputs."""
    dens = 2.0 ** (q["dens"].astype(float) * PEOPLE_SCALE) - 1
    farm, herd, wood = (dens * q[k].astype(float) / 100 for k in ("farm", "herd", "wood"))
    return {"dens": dens, "farm": farm, "herd": herd, "wood": wood, "herd_eff": herd * q["herd_mult"] / MULT_SCALE, "farm_eff": farm * q["farm_mult"] / MULT_SCALE}


def derive(run_dir: Path) -> dict:
    run_dir = Path(run_dir)
    run, m = _load(run_dir)
    tree = SP.parse(m["tree"])
    n = m["cells"]
    goods = LD.goods(m["world"])
    land = goods["_land"]
    area_km2 = 4 * np.pi * R_KM ** 2 / n
    pp = m["presence_present"]
    P = np.fromfile(run_dir / pp["file"], np.uint8).reshape(pp["shape"]).astype(float) / 100.0
    # the present's tree cover (last frame)
    tc_spec = run["layers"]["tree_cover"]
    tc = np.asarray(S.decode(np.asarray(S.read_layer(run_dir, tc_spec)[-1]), tc_spec), float) / 100.0
    tc = np.clip(tc, 0, 1) * land

    dens = np.zeros(n)
    farm, herd, wood, herd_eff, farm_eff = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
    # the animals (animals.py): where an animal is known, a herder (herd_land) or a farmer (crop_land, the plough) works more land
    known = {}
    stocks = (m.get("animals") or {}).get("stocks") or {}
    if "animal_known" in run["layers"] and stocks:
        ks = run["layers"]["animal_known"]
        bits = np.asarray(S.decode(np.asarray(S.read_layer(run_dir, ks)[-1]), ks)).astype(np.int64)
        for aid, st in stocks.items():
            known[aid] = ((bits >> st["bit"]) & 1).astype(float)
    by_line = {}
    for k, ln in enumerate(m["lineages"]):
        l = tree.lines.get(ln["id"])
        if l is None or l.overlay:  # (an overlay is a share of its hosts' people: already counted)
            continue
        d = P[k] * float(ln["demography"]["density"]) * land
        if not d.any():
            continue
        s = shares(tree, l)
        dens += d
        farm += s["farm"] * d
        herd += s["herd"] * d
        hl = cl = 0.0
        for aid, kn in known.items():
            a, pr = AD.BY_ID[aid], stocks[aid]["propensity"].get(ln["id"], 0.0)
            hl = hl + a.herd_land * kn * pr
            cl = cl + a.crop_land * kn * pr * (1.0 if stocks[aid]["tamed"] else 0.0)
        herd_eff += s["herd"] * d * (1.0 + hl)
        farm_eff += s["farm"] * d * (1.0 + cl)
        wood += s["wood"] * d
        by_line[ln["id"]] = {**{kk: round(v, 2) for kk, v in s.items()}, "people": float(d.sum() * area_km2)}

    fcls = np.clip(np.rint(np.asarray(goods["_raw"]["fertile"]) * 4).astype(int), 0, 4)
    graze = goods["grazing"] if "grazing" in goods else np.zeros(n)
    cl = (m.get("crops") or {}).get("layers") or {}
    know = np.fromfile(run_dir / cl["know"]["file"], np.uint8).astype(float) / 100.0 if "know" in cl else None
    out = cover(dens, farm, herd, wood, tc, fcls, graze, herd_eff, farm_eff, know)
    crop, pasture, burned, managed, tree_after = (out[k] for k in ("crop", "pasture", "burned", "managed", "tree_after"))

    # summary against the world
    A = area_km2 / 1e6  # Mkm2 per cell
    fert_ok = land & (fcls >= 2)
    fert_any = land & (fcls >= 1)
    sm = {
        "land_mkm2": round(float(land.sum() * A), 2),
        "fertile_mkm2": round(float(fert_ok.sum() * A), 2), "fertile_any_mkm2": round(float(fert_any.sum() * A), 2),
        "cropland_mkm2": round(float((crop).sum() * A), 3), "pasture_mkm2": round(float(pasture.sum() * A), 3),
        "burned_mkm2": round(float(burned.sum() * A), 3), "managed_mkm2": round(float(managed.sum() * A), 3),
        "cropland_on_fertile_mkm2": round(float(crop[fert_ok].sum() * A), 3),
        "tree_before_mkm2": round(float(tc.sum() * A), 2), "tree_after_mkm2": round(float(tree_after.sum() * A), 2),
        "people": int(dens.sum() * area_km2), "farming_people": int(farm.sum() * area_km2),
        "herding_people": int(herd.sum() * area_km2), "wood_people": int(wood.sum() * area_km2),
        "settled_cells_ge1": int((dens >= 1).sum()), "cells_cropland_ge10pct": int((crop >= 0.10).sum()),
    }
    sm["cropland_share_of_fertile"] = round(sm["cropland_on_fertile_mkm2"] / max(sm["fertile_mkm2"], 1e-9), 3)
    sm["cropland_share_of_land"] = round(sm["cropland_mkm2"] / max(sm["land_mkm2"], 1e-9), 3)
    sm["forest_lost_mkm2"] = round(sm["tree_before_mkm2"] - sm["tree_after_mkm2"], 3)
    sm["forest_lost_share"] = round(sm["forest_lost_mkm2"] / max(sm["tree_before_mkm2"], 1e-9), 3)
    sm["by_line"] = {k: v for k, v in sorted(by_line.items(), key=lambda x: -x[1]["people"]) if v["people"] > 0}
    return {"layers": out, "summary": sm}


def encode(layers: dict) -> dict:
    q = {k: np.clip(np.rint(layers[k] * 100), 0, 100).astype(np.uint8) for k in ("crop", "pasture", "burned", "managed", "tree_after")}
    q["people"] = np.clip(np.rint(np.log2(1 + layers["people"]) / PEOPLE_SCALE), 0, 255).astype(np.uint8)
    return q


def write(run_dir: Path) -> dict:
    """Adds layers/anthro_*.bin and meta.anthro to a peoples run (in place; redone if already there)."""
    run_dir = Path(run_dir)
    d = derive(run_dir)
    q = encode(d["layers"])
    n = len(q["crop"])
    specs = {}
    for k in LAYERS:
        (run_dir / "layers").mkdir(exist_ok=True)
        S.write_atomic(run_dir / "layers" / f"anthro_{k}.bin", q[k].tobytes())
        specs[k] = {"file": f"layers/anthro_{k}.bin", "dtype": "uint8", "shape": [1, n], "units": UNITS[k], "description": DOC[k],
                    **({"scale": PEOPLE_SCALE, "transform": "log2p1"} if k == "people" else {"scale": 1, "transform": None})}
    p = run_dir / "run.json"
    run = json.loads(p.read_text())
    run["meta"]["anthro"] = {"layers": specs, "summary": d["summary"],
                             "constants": {"crop_km2": CROP_KM2, "herd_km2": HERD_KM2, "meadow_km2": MEADOW_KM2,
                                           "burn_km2": BURN_KM2, "wood_base_km2": WOOD_BASE_KM2, "wood_use_km2": WOOD_USE_KM2,
                                           "thin": THIN}}
    S.write_json(p, run)
    return d["summary"]


def lines_for_report(sm: dict) -> list[str]:
    return [
        "", "## Peoples change the land (anthropogenic overlay at the present, PW-662)",
        f"  {sm['people']:,} people; farming {sm['farming_people']:,}, herding {sm['herding_people']:,}, timber users {sm['wood_people']:,}",
        f"  cropland {sm['cropland_mkm2']} Mkm² = {100 * sm['cropland_share_of_land']:.1f}% of the land, "
        f"{100 * sm['cropland_share_of_fertile']:.0f}% of the {sm['fertile_mkm2']} Mkm² of fair-to-prime farmland",
        f"  pasture {sm['pasture_mkm2']} Mkm², burned grassland {sm['burned_mkm2']} Mkm², managed woods {sm['managed_mkm2']} Mkm²",
        f"  tree cover {sm['tree_before_mkm2']} -> {sm['tree_after_mkm2']} Mkm² (lost {sm['forest_lost_mkm2']} Mkm², {100 * sm['forest_lost_share']:.1f}%)"]
