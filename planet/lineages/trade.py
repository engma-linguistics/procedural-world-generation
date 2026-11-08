"""Trade step 1 (PW-1502): the goods ledger. What each culture's own land gives beyond its own need, and what it needs but lacks.

In plain words: for every culture at every frame of the land-use window (the last ~12.5 kyr at 0.5 kyr, meta.eraq), the ledger lists
twenty trade goods in three value classes (bulk, middling, precious; review1.md section 6, value per weight) and says, per good, how
much of the culture's people make it beyond their own need (surplus) and how much of them need it and do not have it at home (lack).
Herders lack grain, farmers lack salt far from salt and tin once they cast bronze, towns lack grain, fuel and fine goods, foragers
beside farmers lack starch and salt, and every good points to the layer it comes from. Nothing is traded yet (that is step 2): this is
what would be traded.

How a number is made (per cell, then summed to the culture with its people as weights; D-T2's lean B, PW-1500):
  output = (the good's land value, 0..1: land.GOODS, crops and herds known on the cell) x (the share of the cell's people who work
           that kind of land, meta.eraq: farm, herd, timber, wild; a deposit (ore, salt, stone, shells) counts in full: whoever lives
           on it digs it, as Provadia's 0.5 ha village boiled salt for the Aegean, review1.md section 3) x (the know gate: the tech that
           unlocks it, see GATE; a tech the tree does not have is no gate, as cuisine's milking rule)
  need   = the share of the cell's people whose way of life wants the good (NEED): review1.md's "what the model takes" list 1
  surplus = max(0, output - need), lack = max(0, need - output); salt's lack is need x (1 - salt on foot), the brief's own reach
           (brief.SALT_TRADED_KM), so it matches the brief's salt-poor interiors.
A culture's surplus and lack of a good are the people-weighted means over its cells (0..1: the share of its people, weighted by
how rich the land is). Like with like: a producing head is set against a needing head. That is the one judgement in the arithmetic
(no yields or rations are sourced for twenty goods); it ranks goods within and between cultures, it is not a tonnage.

Read after the run, like the polities (server.trade_doc, cached under <data root>/.godscache): it never changes the history or any
run file (D63 A, PW-1499: a read-out now, fed back into later runs once it works). Cells summed to cultures (D64 B, PW-1500). Dragons
take tribute and their kobolds trade for the realm; giants take tribute or trade by kind (D65, PW-1501): each row carries its mode
(mode_of), and the tribute-takers' rows are kept for step 2. Sea peoples' sea cells read the sea goods (shelf fish, reef shell).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ..geo import R_KM, is_land

VERSION = 3  # (3: craft and luxury goods made in towns, silver, incense and horses: PW-1522, step4a.md; 2: giants trade or take tribute by kind, GIANT_MODE; a mining kind's hold wants as a town does: PW-1503) (bump when the rules change: the server's cached docs are remade)
CLASSES = ("bulk", "middling", "precious")
# good: (label, value class, where it comes from). Classes per review1.md section 6 ("value per weight is the switch") and design1.md step 1.
GOODS = {
    "grain": ("grain", "bulk", "fertile x a staple crop known on the cell x farm share"),
    "timber": ("timber", "bulk", "timber x timber-using share"),
    "firewood": ("firewood and charcoal", "bulk", "fuel x timber-using share"),
    "stone": ("building stone", "bulk", "stone, once quarrying is known"),
    "dried_fish": ("dried and salted fish", "bulk", "fish (shelf on sea cells), once smoking or salting is known"),
    "salt": ("salt", "middling", "salt (rock, lakes, springs, sea pans), worked for trade once salting, salt mining or solar salt is known"),
    "livestock": ("herd animals, wool, hides and dairy", "middling", "grazing x a herd animal known on the cell x herd share"),
    "oil_wine": ("oil and wine", "middling", "fertile x olive, vine, oil seeds, date palm or coconut known x farm share"),
    "sugar": ("sugar", "middling", "fertile x cane or sap sugar known x farm share"),
    "copper": ("copper", "middling", "copper ore, once native copper or copper is known"),
    "tin": ("tin", "middling", "tin ore, once bronze or the tin trade is known"),
    "iron": ("iron", "middling", "iron ore, once iron or the bloomery is known"),
    "toolstone": ("obsidian", "middling", "volcanic ground (obsidian is volcanic glass); flint is not modelled"),
    "furs": ("furs", "middling", "frozen ground and ice margins, or timber where the year is below freezing, x wild share, once trapping is known"),
    "seal_oil": ("seal and whale oil", "middling", "seal and whale coasts, once the harpoon or whaling is known"),
    "spices": ("spices, tea and cacao", "precious", "fertile x spice tree, chili, tea, vanilla or cacao known x farm share"),
    "gold": ("gold", "precious", "gold ore, once gold and silver working is known"),
    "gems": ("gems", "precious", "gem ground"),
    "ornaments": ("shell and coral ornaments", "precious", "coral and shellfish shores (reef on sea cells), once ornament is known"),
    "mithril": ("mithril and adamant", "precious", "the fantasy metals, once mithril working is known"),
    # PW-1522 (step4a.md): the goods worth carrying far were largely made goods, where only some places had the know-how. Each class is
    # set from the ranges in step4a.md section 1
    "silver": ("silver", "precious", "silver ore (lead-silver, sulphide and epithermal ores), once lead and silver mining is known"),
    "incense": ("frankincense and myrrh", "precious", "hot dry scrub: hot steppe, or hot desert hills, gathered by whoever lives there"),
    "horses": ("horses", "middling", "grazing x horses known on the cell x herd share"),
    "silk": ("silk", "precious", "made in towns: the town share x farmland (mulberry) not frozen, once silk is known"),
    "cloth": ("fine cloth (wool, linen, cotton)", "middling", "made in towns: the town share x farmland or pasture, once wool, linen or cotton is known"),
    "dyes": ("purple and indigo dyes and dyed cloth", "precious", "made in towns: the town share x shellfish shores (purple) or farmland (indigo), once that dye is known"),
    "glass": ("glass", "middling", "made in towns: the town share x fuel, once glass making is known"),
    "porcelain": ("porcelain and stoneware", "middling", "made in towns: the town share x fuel, once porcelain is known"),
    "arms": ("weapons and armour", "precious", "made in towns: the town share x iron or copper ore, once swords or armour are known"),
}
# made goods (PW-1522): made by a town's specialists from inputs on the town's cell or anywhere on its culture's land (the culture brings
# its raw goods to its towns): output = the town share x the input (the cell's, or the culture's mean, the larger) x the know gate. A
# making town meets its own want in proportion to its input, and what its workshops make is for sale (like with like, as above: one
# making head against one wanting head). The input is a proxy, named in GOODS
MADE = ("silk", "cloth", "dyes", "glass", "porcelain", "arms")
SWORDS = ("bronze_sword", "iron_sword", "steel_sword", "scale_armour", "mail", "segmented_plate", "plate_armour")
# the know gate per good: any one of these known opens it (a tech not in the tree is no gate)
GATE = {"stone": ("quarrying", "stone_masonry"), "dried_fish": ("smoking_drying", "salting"), "salt": ("salting", "salt_mining", "solar_salt"),
        "copper": ("native_copper", "copper"), "tin": ("bronze", "tin_trade"), "iron": ("iron", "bloomery"), "toolstone": ("knapping",),
        "furs": ("trapping",), "seal_oil": ("harpoon", "whaling"), "gold": ("gold_silver",), "ornaments": ("ornament",),
        "mithril": ("mithril_work",),
        "silver": ("lead_silver_mining",), "silk": ("silk",), "cloth": ("wool", "flax_linen", "cotton"), "glass": ("glass", "glassblowing"),
        "porcelain": ("porcelain",), "arms": SWORDS}  # (dyes: purple_dye or indigo_dyeing, each with its own input: ledger_at)
# who works the land a good comes from (None: a deposit, everyone on it)
WORK = {"grain": "farm", "timber": "wood", "firewood": "wood", "livestock": "herd", "oil_wine": "farm", "sugar": "farm", "spices": "farm",
        "furs": "forage", "horses": "herd"}
CROPS = {"grain": None, "oil_wine": ("olive", "vine", "oil_seeds", "date_palm", "coconut"), "sugar": ("cane", "sap_sugar"),
         "spices": ("spice_tree", "chili", "tea", "vanilla", "cacao")}  # (grain: any staple crop, crops.stocks weight > 0)
# who needs what (review1.md "what the model takes" 1, design1.md step 1), each a share of a cell's people:
NEED = {
    "grain": "herders (Khazanov 2019: 'non-autarchic'), towns (central places, section 5), foragers beside farmers (Kitanishi 1995: starch)",
    "salt": "farmers and herders (salt is the universal want, section 3; a sheep needs ~9 g a day), foragers beside farmers (Kitanishi 1995)",
    "copper": "farmers and herders who know copper", "tin": "farmers and herders who cast bronze (the tin problem, section 3)",
    "iron": "farmers and herders who know iron",
    "timber": "towns (Uruk's plain lacked hardwood and stone, section 3)", "stone": "towns (Uruk, section 3)",
    "firewood": "towns (central places, section 5)", "livestock": "towns (Nogai horses, tea and horses, section 2)",
    "furs": "towns (Hanse: cloth for furs, section 4)", "gold": "towns (elite demand)", "gems": "towns (elite demand)",
    "spices": "towns that know feasting (elite demand; pepper to Rome, section 4)", "mithril": "towns that know mithril working",
    "ornaments": "foragers who know ornament (hxaro beadwork, section 1)",
    "oil_wine": "farmers who know wine or the oil press (a drink or dish that uses it, design1.md; feasting alone does not need it)",
    "sugar": "farmers who know sugar making",
    "silver": "towns (coin and plate)", "incense": "towns that know incense (temple offerings)",
    "horses": "towns that know riding (cavalry and post)",
    "silk": "towns (elite cloth)", "cloth": "towns", "dyes": "towns (elite cloth)", "glass": "towns", "porcelain": "towns",
    "arms": "towns that know swords or armour",
}  # dried fish, obsidian and sea-mammal oil: no need written yet (flint is not modelled, so want of edge stone would be overstated)
NEED_GATE = {"copper": ("native_copper", "copper"), "tin": ("bronze",), "iron": ("iron", "bloomery"), "spices": ("feasting",),
             "mithril": ("mithril_work",), "ornaments": ("ornament",), "oil_wine": ("wine", "oil_press"), "sugar": ("sugar_making",),
             "incense": ("incense",), "horses": ("riding",), "arms": SWORDS}
TRIBUTE_ROWS = True  # tribute-taking kinds keep a ledger row (marked mode "tribute"): D65 (PW-1501, owner): a dragon realm's needs and surplus
# are traded on its behalf by its kobolds, so step 2 needs them; False leaves them out
# D65 / PW-1507 (coordinator 11-08: the lane's lean B, a mode set by hand per giant kind; the trees' kind ids). A JUDGEMENT per kind, with
# no source: hill giants herd (a way of life of their own) and stone giants keep to their own mountains, so both trade; cloud giants trade
# fine goods and storm giants trade by sea (the ticket's examples); frost and fire giants raid and take tribute (the ticket's example for
# frost; fire giants as smith-lords over the peoples below). A kind not listed falls back to: a way of life of its own trades.
GIANT_MODE = {"hill_giant": "trade", "stone_giant": "trade", "cloud_giant": "trade", "storm_giant": "trade",
              "frost_giant": "tribute", "fire_giant": "tribute"}
OFF_LADDER_HERDS = ("pastoral_nomad", "transhumant", "agro_pastoral")  # an off-ladder kind with one of these ways keeps its own herds (cuisine.profile)


def mode_of(ctx, pid: str) -> dict:
    """How a people's culture takes part in trade (D65, owner 2026-11-07, PW-1501): {"mode": "trade" | "tribute", "via": who carries its
    goods, "off_ladder", "way"}. Dragons (polities' rule: a flying kind named dragon) take tribute and their kobolds trade for the realm
    (via "kobolds"). Giants and other kinds off the density ladder: tribute and/or trade "depending on the kind"; until step 2 sources it,
    a kind with a way of life of its own (hill giants herd) trades and one without takes tribute (a placeholder rule). Everyone else trades."""
    from .cuisine import off_ladder
    line = ctx.lines[ctx.idx[pid]] if pid in ctx.idx else {}
    off = bool(line) and off_ladder(ctx, pid)
    way = line.get("way")
    if "dragon" in pid and "flies" in (line.get("traits") or []):
        return {"mode": "tribute", "via": "kobolds", "off_ladder": off, "way": way}
    if off:
        return {"mode": GIANT_MODE.get(pid) or ("trade" if way else "tribute"), "via": None, "off_ladder": True, "way": way}
    return {"mode": "trade", "via": None, "off_ladder": False, "way": way}
SHOW_MIN = 0.02  # a surplus or lack under this (2% of the culture's people) is left out of the doc (display rounding, not a model number)
LINE_TOP = 3  # goods named per side in the "has / lacks" line
from .ladder import TRADE_CAP as HOLD_TOWN  # noqa: E402 (a hold buys at most this share of its food): the share of a mining kind's people that want as a town's do
NEAR_FARM = 1  # % of a cell's people farming (eraq's resolution) from which foragers there live beside farmers (Kitanishi: within a day's walk; a cell is ~1-2 days across at L7)


def _gate(know: set, techs, tree: set) -> bool:
    return any(t in know for t in techs) or not any(t in tree for t in techs)


def _bits_any(a: np.ndarray, stocks: dict, ids) -> np.ndarray:
    v = np.asarray(a).astype(np.int64)
    out = np.zeros(v.shape, bool)
    for sid, st in stocks.items():
        if st.get("enabled", True) and (ids is None and st.get("weight", 0) > 0 or ids is not None and sid in ids):
            out |= ((v >> int(st["bit"])) & 1) > 0
    return out


def _urban(ctx, era: float, heads: np.ndarray) -> np.ndarray:
    """Share of each cell's people living in a town or city at the era (the settlement ledger's own town size: brief._settlements)."""
    sm = ctx.meta.get("settlements")
    if not sm:
        return np.zeros(ctx.g.n)
    from .brief import _pop_at
    if not hasattr(ctx, "_settle"):
        ctx._settle = json.loads((ctx.dir / sm["file"]).read_text())
    doc = ctx._settle
    town = doc["tiers"]["town_min_by_stage"][-1]
    if not hasattr(ctx, "_trade_towns"):  # (only sites that ever reach a town's size: a small share of the ledger)
        lo = min(doc["tiers"]["town_min_by_stage"])
        ctx._trade_towns = [s for s in doc["sites"] if s.get("kind") not in ("mine", "pit") and s.get("peak_pop", 0) >= lo]
    pop = np.zeros(ctx.g.n)
    for s in ctx._trade_towns:
        t = town
        for a, tm, _ in s.get("bands") or []:
            if a >= era - 1e-6:
                t = tm
        p = _pop_at(s, era)
        if p >= t:
            pop[s["cell"]] += p
    return np.clip(pop / np.maximum(heads, 1e-9), 0.0, 1.0)


def cells_at(ctx, i: int) -> dict | None:
    """The per-cell inputs at frame i (cached on the ctx): people per km2 and people per cell, the farm, herd, timber and wild shares
    (meta.eraq), the town share, salt within walking distance, and each good's land value before the know gates. None outside the
    land-use window or without a world."""
    eq = ctx.meta.get("eraq")
    if not eq or i not in eq["frames"] or ctx.goods is None:
        return None
    key = ("trade_cells", i)
    if key in ctx._frame_cache:
        return ctx._frame_cache[key]
    from .landuse import PEOPLE_SCALE
    from .brief import SALT_TRADED_KM
    j = eq["frames"].index(i)
    q = {k: np.fromfile(ctx.dir / v["file"], np.uint8).reshape(v["shape"])[j] for k, v in eq["layers"].items() if k in ("dens", "farm", "herd", "wood")}
    G, n = ctx.goods, ctx.g.n
    z = lambda k: np.asarray(G[k], float) if k in G else np.zeros(n)  # noqa: E731
    era = -float(ctx.ts[i])
    dens = np.exp2(q["dens"].astype(float) * PEOPLE_SCALE) - 1.0
    heads = dens * 4 * np.pi * R_KM ** 2 / n
    land = is_land(ctx.f("elevation", i).astype(float), ctx.f("ice", i).astype(float) > 0.5)
    farm, herd, wood = (q[k].astype(float) / 100.0 for k in ("farm", "herd", "wood"))
    cst = (ctx.meta.get("crops") or {}).get("stocks") or {}
    ast = {k: v for k, v in ((ctx.meta.get("animals") or {}).get("stocks") or {}).items() if k != "dog"}
    cb = ctx.f("crop_known", i) if "crop_known" in ctx.arr else np.zeros(n, np.int64)
    ab = ctx.f("animal_known", i) if "animal_known" in ctx.arr else np.zeros(n, np.int64)
    fert = z("fertile")
    cold = z("_temp") < 0.0 if "_temp" in G else np.zeros(n, bool)
    sea = ~land
    val = {
        "grain": fert * _bits_any(cb, cst, None), "timber": z("timber"), "firewood": z("fuel"), "stone": z("stone"),
        "dried_fish": np.where(sea, z("shelf"), z("fish")), "salt": z("salt"), "livestock": z("grazing") * _bits_any(ab, ast, tuple(ast)),
        "copper": z("copper"), "tin": z("tin"), "iron": z("iron"), "toolstone": z("volcanic"),
        "furs": np.maximum(z("frost"), z("timber") * cold), "seal_oil": z("sea_mammals"), "gold": z("gold"), "gems": z("gems"),
        "ornaments": np.where(sea, z("reef"), np.maximum(z("coral"), z("shellfish"))), "mithril": z("mithril"),
        "silver": z("silver"), "horses": z("grazing") * _bits_any(ab, ast, ("horse",)),
        # made goods' inputs (MADE): mulberry on unfrozen farmland; flax, cotton or wool; indigo on farmland (purple: _purple); glass and
        # porcelain kilns burn fuel; smiths need ore
        "silk": fert * (z("_temp") > 0.0 if "_temp" in G else 1.0), "cloth": np.maximum(fert, z("grazing") * _bits_any(ab, ast, tuple(ast))),
        "dyes": fert, "_purple": np.maximum(z("shellfish"), z("coral")), "glass": z("fuel"), "porcelain": z("fuel"),
        "arms": np.maximum(z("iron"), z("copper")),
    }
    clim = np.asarray(ctx.f("climate", i)).astype(int) if "climate" in ctx.arr else np.full(n, -1)
    # frankincense and myrrh: trees of hot dry scrub (Koppen BSh, or BWh in hills: the Dhofar and Somali escarpments, step4a.md)
    val["incense"] = np.where(land, ((clim == 5) | ((clim == 3) & (z("hills") >= 0.3))).astype(float), 0.0)
    for g in ("oil_wine", "sugar", "spices"):
        val[g] = fert * _bits_any(cb, cst, CROPS[g])
    salt_own = np.where(sea, 1.0, (np.asarray(G["_salt_km"], float) <= SALT_TRADED_KM).astype(float)) if "_salt_km" in G else np.ones(n)
    out = {"heads": heads, "land": land, "farm": np.where(land, farm, 0.0), "herd": np.where(land, herd, 0.0), "wood": np.where(land, wood, 0.0),
           "urban": _urban(ctx, era, heads), "salt_own": salt_own, "val": {g: np.clip(np.nan_to_num(v), 0.0, 1.0) for g, v in val.items()}}
    ctx._frame_cache[key] = out
    return out


def _known_at(ctx, pid: str, era: float) -> set:
    k = ((ctx.meta.get("techtree") or {}).get("known") or {}).get(pid) or {}
    return {t for t, v in k.items() if v and v[0] is not None and float(v[0]) >= era - 1e-9}


def ledger_at(ctx, i: int) -> dict | None:
    """{culture id: {"surplus": {good: 0..1}, "lack": {good: 0..1}, "ways": {...}, "people": n}} at frame i, every living culture at once
    (vector work over the frame's culture cells, cuisine.culture_cells). None outside the land-use window."""
    key = ("trade_ledger", i)
    if key in ctx._frame_cache:
        return ctx._frame_cache[key]
    X = cells_at(ctx, i)
    if X is None or ctx.cultures() is None:
        return None
    from . import cuisine as CZ
    era = -float(ctx.ts[i])
    cell, cu = CZ.culture_cells(ctx, i, era)
    C = ctx.cultures()["cultures"]
    tree = {t.get("id") for t in (ctx.meta.get("techtree") or {}).get("techs") or []}
    ids = np.unique(cu)
    # per culture: its people's know gates (vectors over the culture ids, then over the entries)
    pos = {int(c): k for k, c in enumerate(ids.tolist())}
    know = {}
    keep = np.ones(len(ids), bool)
    farms, herds = np.ones(len(ids), bool), np.ones(len(ids), bool)
    modes = []
    miner = np.zeros(len(ids), bool)
    for k, c in enumerate(ids.tolist()):
        pid = C[c]["people"]
        miner[k] = "miner" in ((ctx.lines[ctx.idx[pid]].get("traits") or []) if pid in ctx.idx else [])
        kn = know.setdefault(pid, _known_at(ctx, pid, era))
        m = mode_of(ctx, pid)
        modes.append(m)
        keep[k] = m["mode"] == "trade" or TRIBUTE_ROWS
        farms[k] = any(t.startswith("crop_") for t in kn) or "cultivation" in kn  # (as cuisine.profile: a forager culture in a farmed cell does not farm)
        herds[k] = any(t.startswith("animal_") and t != "animal_dog" for t in kn) or "herding" in kn
        if m["off_ladder"]:  # (the farms and herds on its cells are the peoples' below it, not its own: cuisine.profile)
            farms[k] = False
            herds[k] = m["way"] in OFF_LADDER_HERDS
    kc = np.array([pos[int(c)] for c in cu.tolist()], np.int64) if len(cu) else np.zeros(0, np.int64)
    ok = keep[kc]
    cell, kc = cell[ok], kc[ok]
    know_c = [know[C[c]["people"]] for c in ids.tolist()]

    def gate(techs) -> np.ndarray:
        return np.array([_gate(kn, techs, tree) for kn in know_c], bool)[kc] if len(kc) else np.zeros(0, bool)
    raw_farm = X["farm"][cell]
    farm = np.where(farms[kc], raw_farm, 0.0)
    herd = np.where(herds[kc], X["herd"][cell], 0.0)
    wood, urban, land = X["wood"][cell], X["urban"][cell], X["land"][cell]
    forage = np.clip(1.0 - farm - herd, 0.0, 1.0)
    work = {"farm": farm, "herd": herd, "wood": wood, "forage": forage}
    near_farm = (raw_farm >= NEAR_FARM / 100.0) & (forage > 0)
    # an off-ladder kind's "wild" share is hunting and taking, not a forager band's: no starch, salt or bead wants from it (the sources are
    # human foragers); a dragon realm's own wants (its hoard) are step 2's, carried by its kobolds (D65)
    band = forage * ~np.array([m["off_ladder"] for m in modes], bool)[kc] if len(kc) else forage
    settled = np.clip(farm + herd, 0.0, 1.0)
    urban = np.where(np.array([m["off_ladder"] for m in modes], bool)[kc], 0.0, urban) if len(kc) else urban
    # a mining kind's hold trades as a town does (D65, PW-1501): its people want what a town's people want, at the share of their food a hold
    # buys (ladder.TRADE_CAP, the model's own placeholder until step 4d replaces it)
    town = urban  # (the settlement ledger's towns alone: who makes the made goods, MADE; a hold's smiths make arms only)
    urban = np.where(miner[kc], np.maximum(urban, HOLD_TOWN), urban) if len(kc) else urban
    need = {
        "grain": np.clip(herd + urban + band * near_farm, 0.0, 1.0),
        "salt": np.where(land, np.clip(settled + band * near_farm, 0.0, 1.0), 0.0),
        "timber": urban, "stone": urban, "firewood": urban, "livestock": urban, "furs": urban, "gold": urban, "gems": urban,
        "ornaments": band, "silver": urban, "incense": urban, "horses": urban,
    }
    for g in ("copper", "tin", "iron"):
        need[g] = settled
    need["spices"] = urban
    need["mithril"] = urban
    need["oil_wine"] = farm
    need["sugar"] = farm
    for g, techs in ((g, t) for g, t in NEED_GATE.items() if g not in MADE):  # (made goods: gated in the loop below)
        need[g] = need[g] * gate(techs)
    # weights: the cell's people; a culture with no counted people (sea cells, a frame's empty cells) weighs its cells alike
    w = X["heads"][cell]
    wsum = np.bincount(kc, weights=w, minlength=len(ids))
    flat = wsum <= 0
    w = np.where(flat[kc], 1.0, w)
    wsum = np.bincount(kc, weights=w, minlength=len(ids))
    mean = lambda v: np.bincount(kc, weights=w * v, minlength=len(ids)) / np.maximum(wsum, 1e-12)  # noqa: E731
    sur, lack = {}, {}
    pair_sur, pair_lack = {}, {}  # (per (cell, culture) pair, for the exchange: trade_flow.py)
    for g in GOODS:
        v = X["val"][g][cell]
        if g in MADE:  # (PW-1522: the town's specialists, from the cell's or the culture's input; see MADE)
            inp = lambda a: np.maximum(a, mean(a)[kc]) if len(kc) else a  # noqa: E731
            if g == "dyes":
                made = np.maximum(inp(v) * gate(("indigo_dyeing",)), inp(X["val"]["_purple"][cell]) * gate(("purple_dye",)))
            else:
                made = inp(v) * gate(GATE[g])
            made = np.clip(made, 0.0, 1.0)
            nd = urban * gate(NEED_GATE[g]) if g in NEED_GATE else urban
            techs = ("indigo_dyeing", "purple_dye") if g == "dyes" else GATE[g]
            if not any(_gate(kn, techs, tree) for kn in know.values()):  # (nobody alive can make it yet: nobody wants it)
                nd = nd * 0.0
            pair_sur[g] = made * (urban if g == "arms" else town)  # (a mining kind's hold wants as a town does, but makes only arms)
            pair_lack[g] = nd * (1.0 - made)
            sur[g] = mean(pair_sur[g])
            lack[g] = mean(pair_lack[g])
            continue
        out = v * (work[WORK[g]] if g in WORK else 1.0)
        if g in GATE:
            out = out * gate(GATE[g])
        nd = need.get(g)
        if nd is None:
            pair_sur[g] = out
            sur[g] = mean(out)
            continue
        pair_sur[g] = np.maximum(0.0, out - nd)
        pair_lack[g] = nd * (1.0 - X["salt_own"][cell]) if g == "salt" else np.maximum(0.0, nd - out)
        sur[g] = mean(pair_sur[g])
        lack[g] = mean(pair_lack[g])
    ways = {k: mean(v) for k, v in (("farm", farm), ("herd", herd), ("forage", forage), ("urban", urban))}
    people = np.bincount(kc, weights=X["heads"][cell], minlength=len(ids))
    # what a culture is known for: its surplus over the frame's mean surplus of that good (stone and fish lie nearly everywhere, tin does not)
    tk = keep & np.array([m["mode"] == "trade" for m in modes], bool)  # (over the trading cultures)
    fm = {g: float(v[tk].mean()) if tk.any() else 0.0 for g, v in sur.items()}
    res = {}
    for k, c in enumerate(ids.tolist()):
        if not keep[k]:
            continue
        r2 = lambda d: {g: round(float(d[g][k]), 3) for g in sorted(d, key=lambda g: -d[g][k]) if d[g][k] >= SHOW_MIN}  # noqa: E731
        s2, l2 = r2(sur), r2(lack)
        has = sorted((g for g in s2 if s2[g] > fm[g]), key=lambda g: -s2[g] / max(fm[g], 1e-9))[:LINE_TOP]  # (more than the average culture)
        res[int(c)] = {"surplus": s2, "lack": l2, "has": has, "lacks": list(l2)[:LINE_TOP], "mode": modes[k]["mode"], "via": modes[k]["via"],
                       "ways": {a: round(float(b[k]), 3) for a, b in ways.items()}, "people": int(round(float(people[k])))}
    ctx._frame_cache[key] = res
    ctx._frame_cache[("trade_pairs", i)] = {"cell": cell, "culture": ids[kc] if len(kc) else kc, "w": w, "wsum": dict(zip(ids.tolist(), wsum.tolist())),
                                            "surplus": pair_sur, "lack": pair_lack, "urban": urban, "forage": band}
    return res


def pairs_at(ctx, i: int) -> dict | None:
    """The ledger per (cell, culture) pair at frame i (tribute rows included): {"cell", "culture", "w" (the pair's weight in its culture's
    mean), "wsum" (culture -> the sum of its weights), "surplus" and "lack" ({good: per pair, 0..1}), "urban", "forage" (a band's share)}.
    A culture's ledger number is sum(w x pair value) / wsum, so an import per pair summed the same way is a share of its people, like its lack."""
    if ("trade_pairs", i) not in ctx._frame_cache:
        ctx._frame_cache.pop(("trade_ledger", i), None)
        if ledger_at(ctx, i) is None:
            return None
    return ctx._frame_cache[("trade_pairs", i)]


def line(row: dict | None) -> str | None:
    """"has salt, herd animals; lacks grain, tin" from a culture's ledger row: the goods it has most over the average culture of its
    frame, and the goods it lacks most."""
    if not row:
        return None
    has = [GOODS[g][0] for g in row["has"]]
    lacks = [GOODS[g][0] for g in row["lacks"]]
    t = ("has " + (", ".join(has) or "nothing to spare")) + "; " + ("lacks " + ", ".join(lacks) if lacks else "lacks nothing it knows to want")
    if row.get("mode") == "tribute":
        t = "takes tribute" + (f", and its {row['via']} trade for it" if row.get("via") else ", does not trade") + ": " + t
    return t


def derive(run_dir, ctx=None) -> dict:
    """The run's goods ledger: every culture at every frame of the land-use window. Read from the run, never written into it."""
    import time
    from .brief import Ctx
    t0 = time.time()
    ctx = ctx or Ctx(run_dir)
    eq = ctx.meta.get("eraq")
    frames = []
    if eq and ctx.goods is not None and ctx.cultures() is not None:
        for i, ago in zip(eq["frames"], eq["ago_kyr"]):
            led = ledger_at(ctx, i)
            if led is not None:
                frames.append({"frame": i, "ago_kyr": round(abs(float(ago)), 3), "cultures": {str(c): r for c, r in led.items()}})
            ctx._frame_cache.pop(("trade_cells", i), None)
    C = (ctx.cultures() or {}).get("cultures") or []
    return {"format": "procgen-trade-goods/1", "version": VERSION, "run": Path(ctx.dir).name,
            "cultures": [{k: x.get(k) for k in ("name", "people", "born_kyr", "ended_kyr", "end", "into")} for x in C],
            "goods": {g: {"label": a, "class": b, "from": c, "need": NEED.get(g), "gate": list(GATE.get(g, ()))} for g, (a, b, c) in GOODS.items()},
            "classes": list(CLASSES), "frames": frames, "seconds": round(time.time() - t0, 1),
            "constants": {"SHOW_MIN": SHOW_MIN, "NEAR_FARM_PCT": NEAR_FARM, "TRIBUTE_ROWS": TRIBUTE_ROWS},
            "basis": "trade.py (PW-1502, design1.md step 1): per cell output = land value x working share x know gate, need from the way of life; "
                     "surplus = output beyond need, lack = need not met at home; people-weighted over the culture's cells. Nothing is traded yet."}


def _at(C: list, c: int, era: float) -> int:
    from .cuisine import _at as at
    return at(C, c, era)


def culture_view(doc: dict, c: int) -> dict:
    """One culture's ledger through the window: each frame where it (or the culture its land merged into) has a row."""
    C = doc["cultures"]
    if not 0 <= c < len(C):
        raise ValueError(f"no culture {c} in this run (ids 0..{len(C) - 1})")
    rows = []
    for f in doc["frames"]:
        if C[c]["born_kyr"] < f["ago_kyr"] - 1e-9:
            continue
        h = _at(C, c, f["ago_kyr"])
        r = f["cultures"].get(str(h))
        if r is not None:
            rows.append({"ago_kyr": f["ago_kyr"], "as": h, **r, "line": line(r)})
    return {"culture": c, "name": C[c]["name"], "people": C[c]["people"], "goods": doc["goods"], "rows": rows}


def summary(doc: dict) -> dict:
    """Per main way of life of each culture-frame (farm, herd or wild, whichever is the largest share of its people; besides, "towns" for
    the culture-frames with a tenth or more of their people in towns, a judge's cut): per good the mean surplus and lack, and how often
    the good is named in the "has / lacks" line. The judge's table."""
    tally: dict = {}
    for f in doc["frames"]:
        for r in f["cultures"].values():
            w = r["ways"]
            way = max(("farm", "herd", "forage"), key=lambda k: w[k])
            keys = (way,) + (("towns",) if w["urban"] >= 0.1 else ()) if r.get("mode", "trade") == "trade" else ("tribute",)
            for key in keys:
                t = tally.setdefault(key, {"n": 0, "surplus": {}, "lack": {}, "has": {}, "lacks": {}})
                t["n"] += 1
                for side in ("surplus", "lack", "has", "lacks"):
                    for g in r[side]:
                        t[side][g] = t[side].get(g, 0) + (r[side][g] if side in ("surplus", "lack") else 1)
    for t in tally.values():
        for side in ("surplus", "lack", "has", "lacks"):
            t[side] = {g: round(v / t["n"], 3) for g, v in sorted(t[side].items(), key=lambda x: -x[1])}
    return {"version": doc["version"], "goods": doc["goods"], "frames": [{"frame": f["frame"], "ago_kyr": f["ago_kyr"], "cultures": len(f["cultures"])} for f in doc["frames"]],
            "by_way": tally, "seconds": doc.get("seconds")}
