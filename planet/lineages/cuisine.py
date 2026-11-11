"""The cuisine sheet of one culture (PW-1391, with PW-1312's food taboos): culinary-dnd's five questions, answered by rule from a peoples
run at an era, read-only.

    culture_cells(ctx, i, era)          -> (cells, culture) per entry: which culture holds which land cell at frame i (merges followed)
    profile(ctx, i, era, c, mask)       -> what one culture does there: ways of life, crops and herds, dairy, fuel, body, faith, taboos
    sheet(ctx, brief, c, i, era)        -> {fuel, staple, drink, who_eats_together, outsiders_get_wrong, wont_eat, ...}
    suggested(brief)                    -> the region brief's rule-based notes (moved here from brief.py)

culinary-dnd's fact-sheet spine (its docs/00-README-reading-order.md) is Ecology, Fuel, Staples, Techniques, Drink, Who eats together,
Implements, Etiquette, What outsiders get wrong; "every culture is answerable to: what's the fuel, what's the staple, what do they drink,
who eats together". This module answers those four and the outsiders line, and lists what the culture won't eat. Each answer is one
simple rule over what the run already holds (marked JUDGEMENT where it is a reading, not a measurement), so a nudge to the run moves a
line, never the whole sheet; the culinary side overrules any of it. No number here claims to be a real-world measurement.

Where the numbers come from: ways of life are the density ladder's per-cell farm and herd shares of heads (meta.eraq, landuse.frame_inputs:
the last ~12 kyr), weighted by heads over the culture's cells; what a people knows (milking, fermentation, feasting) is meta.techtree.known
with its date; crops and herds are the frame's known layers on the culture's land; taboos and faiths are the Religion tab's taboos and gods docs (server.taboos_doc /
gods_doc: authored faiths and the saved gods mode included, PW-1440; present-day: an earlier era shows the culture's present taboos, or none if it is gone).
"""

from __future__ import annotations

import numpy as np

from .years import years_ago

NONE = 65535
KNOWN_SHARE = 0.10  # (as brief.KNOWN_SHARE) a crop or herd is known on a culture's land from this share of its cells
WAY_MIN = 0.10  # JUDGEMENT: a way of life (farming, herding) counts for the sheet from this share of the culture's heads
WAY_MAIN = 0.5  # JUDGEMENT: ...and is the main one from this share
NEIGH_TOP = 4  # neighbouring cultures compared for "what outsiders get wrong"
OUTSIDER_LINES = 3  # at most this many contrasts
LACTASE_FRESH = 0.6  # (as brief.LACTASE_FRESH) at or above this lactase share milk is drunk fresh, below it soured and aged
LACTASE_KYR = 5.0  # JUDGEMENT (PW-1372): dairying this long brings a herding culture's lactase share up to its herd share; a placeholder
# shape (linear in time, capped), not a fitted selection rate
GRAINS = {"wheat": "barley beer", "rye": "rye and oat beer", "foxtail_millet": "millet beer", "sorghum": "sorghum beer", "rice": "rice wine",
          "maize": "maize beer", "pseudograin": "quinoa beer", "stonegrain": "stonegrain beer"}
FRUIT_DRINKS = {"vine": "wine", "tree_fruit": "cider and fruit wine", "date_palm": "date wine", "coconut": "palm wine (toddy)", "banana": "banana beer",
                "cane": "cane wine", "sap_sugar": "birch and maple sap, fresh in spring"}
INFUSIONS = {"tea": "infusions (tea- and coffee-like)", "cacao": "a frothed cacao drink"}
MEAL_TABOOS = {  # non-food taboos (taboo_defs) that say who eats with whom
    "caste_eat": "the lowest rank may not eat with the others",
    "chief_house": "nobody else eats in the ruler's house",
    "chief_food": "food made for the ruler is not eaten by the lowly",
    "menses_kitchen": "a woman in her courses does not cook or enter the kitchen",
    "motherinlaw": "a man does not share a fire with his mother-in-law",
    "fatherinlaw": "a woman does not share a fire with her father-in-law",
    "clan_exogamy": "marriages are between clans, so the big meals (weddings, funerals) feed two clans at once",
    "rank_endogamy": "seating follows rank",
}
FUEL_COOK = {  # (from the brief's old fuel notes)
    "dung": "low slow fires: boiling, stewing and baking in embers",
    "wood": "open flame: roasting, grilling, smoking",
    "charcoal": "steady clean heat: grilling and long simmering",
    "peat": "smoky steady heat; the smoke flavours what hangs over it",
    "straw": "quick hot flashes, poor for slow cooking",
    "grass": "fuel of last resort: food is boiled briefly or eaten raw before fuel is spent",
    "drift": "scarce fuel: little is cooked long",
    "coal": "long hot fires: kilns, ovens and all-day braises",
    "heath": "brushwood: quick fires, flatbreads and griddles",
    "oil": "sea-mammal oil lamps: slow warming more than cooking",
    "tallow": "rendered fat: lamps and slow pots",
    "bone": "bone and fat fires: little heat, so food is eaten raw, dried or frozen",
}


# -- which culture is where -----------------------------------------------------------------------------------------------
def _at(C: list, c: int, era: float) -> int:
    """The culture holding culture c's land at the era, after any merges by then."""
    while C[c]["end"] == "merged" and C[c]["into"] is not None and C[c]["ended_kyr"] is not None and C[c]["ended_kyr"] >= era - 1e-9:
        c = C[c]["into"]
    return c


def culture_cells(ctx, i: int, era: float) -> tuple[np.ndarray, np.ndarray]:
    """(cells, culture) at frame i, one entry per people's deme in a land or sea cell: every people's demes on a run with the presence
    table (lane 109), else the leading people's. Cached per frame on the ctx."""
    cache = ctx.__dict__.setdefault("_cult_cells", {})
    if i in cache:
        return cache[i]
    doc = ctx.cultures()
    C, dc = doc["cultures"], np.asarray(doc["deme_culture"], np.int64)
    ov = ctx.overlap()
    if ov is not None:
        pt, allv = ov
        a, b = int(pt["offsets"][i, 0]), int(pt["offsets"][i, -1])
        cell, dem = pt["cells"][a:b].astype(np.int64), allv[a:b].astype(np.int64)
    else:
        dem = np.asarray(ctx.arr["demes"][i]).astype(np.int64)
        cell = np.arange(len(dem))
    ok = (dem < len(dc)) & (dem != NONE)
    cell, cu = cell[ok], dc[dem[ok]]
    ok = cu >= 0
    cell, cu = cell[ok], cu[ok]
    memo: dict = {}
    res = np.array([memo.setdefault(int(x), _at(C, int(x), era)) for x in cu.tolist()], np.int64) if len(cu) else cu
    cache[i] = (cell, res)
    return cache[i]


def mask_of(ctx, i: int, era: float, c: int) -> np.ndarray:
    cell, cu = culture_cells(ctx, i, era)
    m = np.zeros(ctx.g.n, bool)
    m[cell[cu == c]] = True
    return m


def resolve(ctx, c: int, era: float) -> int:
    """The culture standing for c at the era (a merged culture's heir), or SystemExit when c was not yet there."""
    doc = ctx.cultures()
    if doc is None:
        raise SystemExit("this run has no cultures (cultures.json, or demes to work them out from)")
    C = doc["cultures"]
    if not 0 <= c < len(C):
        raise SystemExit(f"no culture {c} in this run (ids 0..{len(C) - 1})")
    if C[c]["born_kyr"] < era - 1e-9:
        raise SystemExit(f"culture {c} ({C[c]['name']}) begins {years_ago(C[c]['born_kyr'])}, after the era asked for")
    return _at(C, c, era)


# -- what one culture does --------------------------------------------------------------------------------------------------
def _known(ctx, pid: str, era: float) -> set:
    """What a people knew at the era (meta.techtree.known: tech -> [kyr ago, how, from])."""
    k = ((ctx.meta.get("techtree") or {}).get("known") or {}).get(pid) or {}
    return {t for t, v in k.items() if v and v[0] is not None and float(v[0]) >= era - 1e-9}


def _in_tree(ctx, tech: str) -> bool:
    return any(t.get("id") == tech for t in (ctx.meta.get("techtree") or {}).get("techs") or [])


def _ways(ctx, i: int, mask: np.ndarray) -> dict | None:
    """Heads-weighted farm and herd shares on the culture's cells at frame i (meta.eraq), None outside its window."""
    eq = ctx.meta.get("eraq")
    if not eq or i not in eq["frames"] or not mask.any():
        return None
    cache = ctx.__dict__.setdefault("_eraq", {})
    j = eq["frames"].index(i)
    if j not in cache:
        cache[j] = {k: np.fromfile(ctx.dir / v["file"], np.uint8).reshape(v["shape"])[j] for k, v in eq["layers"].items() if k in ("dens", "farm", "herd")}
    q = cache[j]
    from .landuse import PEOPLE_SCALE
    heads = np.exp2(q["dens"][mask].astype(float) * PEOPLE_SCALE) - 1.0  # (dens is log2(1 + people per km2) / PEOPLE_SCALE)
    w = heads if heads.sum() > 0 else np.ones(int(mask.sum()))
    farm = float((q["farm"][mask] / 100.0 * w).sum() / w.sum())
    herd = float((q["herd"][mask] / 100.0 * w).sum() / w.sum())
    return {"farm": round(farm, 3), "herd": round(herd, 3), "forage": round(max(0.0, 1.0 - farm - herd), 3),
            "density_km2": round(float(np.median(heads)) if len(heads) else 0.0, 3)}


def _bits_on(ctx, layer: str, key: str, i: int, mask: np.ndarray) -> dict:
    from .brief import _bits
    st = (ctx.meta.get(key) or {}).get("stocks") or {}
    if layer not in ctx.arr or not st or not mask.any():
        return {}
    return _bits(ctx.f(layer, i), mask, st, KNOWN_SHARE, mask)


def _fuel_lead(ctx, i: int, era: float, mask: np.ndarray) -> str | None:
    from .brief import _fuels
    if not mask.any():
        return None
    f = _fuels(ctx, mask, era, i) or {}
    return next(iter(f.get("lead") or {}), None)


def _faith(ctx, c: int, era: float) -> dict | None:
    gd, _ = ctx.religion()
    if not gd or "faiths" not in gd:
        return None
    from .faithmap import faith_of_culture
    f = faith_of_culture(gd, era).get(c)
    if f is None:
        return None
    x = gd["faiths"]["list"][f]
    return {"id": f, "name": x["name"], "core": x.get("core"), "origin_culture": x.get("origin_culture"), "founded_kyr": x.get("founded_kyr")}


def _taboos(ctx, c: int) -> list:
    _, tb = ctx.religion()
    return ((tb or {}).get("cultures") or {}).get(str(c), {}).get("taboos") or []


def off_ladder(ctx, pid: str) -> bool:
    """A kind off the density ladder (dragons and giants: the counted megafauna, or an empty ladder): the farms and herds on its cells
    are the peoples' below it, not its own."""
    pr = ctx.meta.get("present") or {}
    return pid in (pr.get("megafauna") or {}) or ((pr.get("lines") or {}).get(pid) or {}).get("ladder") == {}


def dairy_of(body: dict, herd: float, animals: list, milking_kyr: float | None, era: float, milking: bool, cheese: bool) -> dict | None:
    """A culture's dairy (PW-784, PW-834, PW-1372, PW-793): only where it herds (herd share of heads >= WAY_MIN), knows milking, keeps a
    dairy animal on its land and its body milks (`milks = false`: the antelope- and cervid-kin of Seven Meals). Lactase never makes dairy;
    it only decides fresh or soured milk, and it is the larger of the people's authored body.milk and herd x (years of dairying /
    LACTASE_KYR), capped at the herd share (a placeholder for selection under dairying)."""
    if not body.get("milks", True) or not milking or herd < WAY_MIN or not animals:
        return None
    years = max(0.0, float(milking_kyr) - era) if milking_kyr is not None else 0.0
    f = body.get("milk", False)
    authored = 1.0 if f is True else float(f or 0.0)
    derived = round(herd * min(1.0, years / LACTASE_KYR), 2)
    lac = max(authored, derived)
    return {"animals": list(animals), "lactase_share": round(lac, 2), "fresh": lac >= LACTASE_FRESH, "cheese": cheese,
            "lactase_basis": "the people's body.milk" if authored >= derived else f"herd share {herd:.2f} x {years:.1f} kyr of dairying / {LACTASE_KYR:g} kyr (PW-1372, a placeholder)"}


def profile(ctx, i: int, era: float, c: int, mask: np.ndarray | None = None) -> dict:
    """One culture at frame i: its people, body, ways of life, what it farms and herds, its dairy and lactase, fuel, faith, taboos."""
    from .brief import _body
    doc = ctx.cultures()
    C = doc["cultures"][c]
    pid = C["people"]
    line = ctx.lines[ctx.idx[pid]]
    mask = mask_of(ctx, i, era, c) if mask is None else mask
    elev = ctx.f("elevation", i).astype(float)
    from ..geo import is_land
    land = mask & is_land(elev, ctx.f("ice", i).astype(float) > 0.5)
    body = _body(line)
    know = _known(ctx, pid, era)
    ways = _ways(ctx, i, land)
    crops_known = _bits_on(ctx, "crop_known", "crops", i, land)
    herds_known = _bits_on(ctx, "animal_known", "animals", i, land)
    cultivates = any(t.startswith("crop_") for t in know) or "cultivation" in know
    herds = any(t.startswith("animal_") and t != "animal_dog" for t in know) or "herding" in know
    off = off_ladder(ctx, pid)
    if off:
        hw = 1.0 if line.get("way") in ("pastoral_nomad", "transhumant", "agro_pastoral") else 0.0
        ways = {"farm": 0.0, "herd": hw, "forage": 1.0 - hw, "density_km2": None, "note": "a kind off the density ladder: it lives by "
                + ("its own herds" if hw else "hunting and taking") + ", not by the farms of the peoples around it"}
        crops_known = {}
        herds_known = herds_known if hw else {}
    elif ways is not None:
        ways = {**ways, "farm": ways["farm"] if cultivates else 0.0, "herd": ways["herd"] if herds else 0.0}
        ways["forage"] = round(max(0.0, 1.0 - ways["farm"] - ways["herd"]), 3)
    if ways is None and (era > 12.5 or not (cultivates or herds)):
        ways = {"farm": 0.0, "herd": 0.0, "forage": 1.0, "density_km2": None, "note": "before the stored ways of life: no crops or herds known yet"}
    cst = (ctx.meta.get("crops") or {}).get("stocks") or {}
    tab = _taboos(ctx, c)
    food_tab = [t for t in tab if t.get("kind", "food") == "food" or t.get("target") in ("totem_kin", "sacred_kind")]
    forbidden = {t["target"] for t in food_tab if t.get("scope") == "everyone"}
    # dairy (PW-784, PW-834, PW-1372): only a culture that herds, knows milking, keeps a dairy animal on its land and whose body milks
    from . import animal_defs as AD
    dairy_an = [a.id for a in AD.TABLE if a.dairy and a.id in herds_known and a.id not in forbidden]
    since = ((ctx.meta.get("techtree") or {}).get("known") or {}).get(pid, {}).get("milking")
    dairy = dairy_of(body, (ways or {}).get("herd") or 0.0, dairy_an, since[0] if since else None, era,
                     "milking" in know or not _in_tree(ctx, "milking"), "cheese" in know)
    return {"id": c, "name": C["name"], "people": pid, "people_name": line["name"], "body": body, "ways": ways, "know": know,
            "crops": {k: v for k, v in crops_known.items() if k not in forbidden}, "staple_crops": [k for k in crops_known if cst.get(k, {}).get("weight", 0) > 0 and k not in forbidden],
            "herds": {k: v for k, v in herds_known.items() if k not in forbidden and k != "dog"}, "dairy": dairy, "fuel": _fuel_lead(ctx, i, era, land),
            "faith": _faith(ctx, c, era), "taboos": tab, "food_taboos": food_tab, "forbidden": sorted(forbidden), "cells": int(land.sum()),
            "traits": C.get("traits") or {}, "off_ladder": off, "coastal": bool(set(line.get("traits") or []) & {"coastal", "swims", "seafaring"}),
            "line_traits": list(line.get("traits") or []), "tree_techs": _tree_techs(ctx)}


def _tree_techs(ctx) -> set | None:
    """The tech ids of the run's tree (None on a run without one: then no keeping method is gated by a tech, keeping.py)."""
    T = (ctx.meta.get("techtree") or {}).get("techs")
    return {t.get("id") for t in T} if T else None


# -- the five answers -------------------------------------------------------------------------------------------------------
def _label(ctx, key: str, sid: str) -> str:
    return ((ctx.meta.get(key) or {}).get("stocks") or {}).get(sid, {}).get("label", sid.replace("_", " "))


def _main_way(p: dict) -> str:
    w = p["ways"] or {}
    best = max(("farm", "herd", "forage"), key=lambda k: (w.get(k) or 0.0))
    return {"farm": "farmers", "herd": "herders", "forage": "foragers"}[best]


def fuel(ctx, brief: dict, p: dict, bi: dict | None = None) -> dict:
    f = brief.get("fuels") or {}
    lead = f.get("lead") or {}
    top = next(iter(lead), None)
    if top is None:
        return {"text": "no fuel layer in this run", "lead": None}
    rest = [k for k in lead if k != top]
    t = f"{top}" + (f" (then {', '.join(rest)})" if rest else "") + f": {FUEL_COOK.get(top, 'the commonest fuel')}"
    if not p["body"].get("fire", True):
        t += "; this people does not keep fire itself, so its cooked food comes from others' hearths or not at all"
    from .bought_in import fuel_note
    nb = fuel_note(bi)
    if nb:
        t += f"; {nb}"
    return {"text": t, "lead": lead, "basis": f.get("basis")}


def staple(ctx, brief: dict, p: dict, bi: dict | None = None) -> dict:
    """The staple: what the culture farms (staple crops known on its land, if it farms), herds (if it herds), fishes or gathers,
    in the order of its ways of life; an obligate carnivore's staple is meat whatever the land grows."""
    w = p["ways"] or {}
    diet = p["body"].get("diet")
    parts = []
    crops = [_label(ctx, "crops", k) for k in sorted(p["staple_crops"], key=lambda k: -p["crops"][k])]
    herds = [_label(ctx, "animals", k) for k in sorted(p["herds"], key=lambda k: -p["herds"][k])]
    fi = brief.get("fish") or {}
    fishery = (fi.get("coast_fish") or 0) >= 0.4 or (fi.get("river_runs") or 0) >= 0.2 or (fi.get("lake_fish") or 0) >= 0.2
    order = sorted(("farm", "herd", "forage"), key=lambda k: -(w.get(k) or 0.0))
    for k in order:
        share = w.get(k) or 0.0
        if k == "farm" and share >= WAY_MIN and diet != "obligate_carnivore":
            parts.append(("grown", f"{', '.join(crops[:3])} ({round(100 * share)}% of the people farm)" if crops else
                          f"farmed food ({round(100 * share)}% of the people farm), but the run's crop layer has no staple growable on its land, so which crop is not known here"))
        elif k == "herd" and share >= WAY_MIN and herds:
            parts.append(("herded", f"the meat{' and milk' if p['dairy'] else ''} of {', '.join(herds[:3])} ({round(100 * share)}% herd)"))
        elif k == "forage" and share >= WAY_MIN and p.get("off_ladder"):
            parts.append(("wild", "meat: game, and herd animals taken from the peoples around it" + (", and fish" if fishery or p["coastal"] else "")))
        elif k == "forage" and share >= WAY_MIN:
            wild = "fish and shore food" if fishery or p["coastal"] else "game"
            parts.append(("wild", f"{wild} and gathered plants ({round(100 * share)}% live by the wild)" if diet != "obligate_carnivore" else
                          f"{wild} ({round(100 * share)}% hunt)"))
    if diet == "obligate_carnivore" and crops:
        parts.append(("note", "they eat no grain or roots themselves (an obligate carnivore's body): crops on their land feed their herds or their trade"))
    if not parts:
        parts.append(("wild", "game and gathered plants"))
    from .bought_in import staple_note
    nb = staple_note(bi)
    if nb:
        parts.append(("bought", nb))
    text = "; ".join(t for _, t in parts)
    never = [t["label"] for t in p["food_taboos"] if t.get("scope") == "everyone" and t.get("kind", "food") == "food"]
    if never:
        text += f" (never {', '.join(never)}: a taboo)"
    return {"text": text, "parts": [{"kind": k, "text": t} for k, t in parts]}


def drink(ctx, brief: dict, p: dict, bi: dict | None = None) -> dict:
    """What the culture drinks, by rule: water; milk (fresh or soured by the lactase share) only where it dairies; beer or wine from the
    grain and fruit it grows, once it knows fermentation (or the run's tree has no such tech); spirits once it distils; infusions."""
    out = ["water"]
    land = brief.get("land") or {}
    k = land.get("koppen") or {}
    if sum(v for kk, v in k.items() if str(kk).startswith("BW")) >= 0.5:
        out[0] = "water, scarce and carried (a desert culture)"
    d = p["dairy"]
    if d:
        out.append(("fresh milk" if d["fresh"] else "soured and fermented milk (yogurt-, kefir-, kumis-like), not fresh") + f" of {', '.join(_label(ctx, 'animals', a) for a in d['animals'])}")
    ferm = "fermentation" in p["know"] or not _in_tree(ctx, "fermentation")
    grown = set(p["crops"])
    farms = ((p["ways"] or {}).get("farm") or 0.0) >= WAY_MIN
    if ferm and farms:
        out += [GRAINS[c] for c in GRAINS if c in grown and c in p["staple_crops"]][:2]
        out += [FRUIT_DRINKS[c] for c in FRUIT_DRINKS if c in grown][:2]
    elif "sap_sugar" in grown:
        out.append(FRUIT_DRINKS["sap_sugar"])
    if ferm and d and not farms:
        out.append("fermented mare's or ewe's milk is the drink of feasts" if "horse" in d["animals"] or "caprine" in d["animals"] else
                   f"fermented {_label(ctx, 'animals', d['animals'][0])} milk at feasts" if d["animals"] else "fermented milk at feasts")
    if "distilling" in p["know"] and ferm:
        out.append("spirits distilled from " + ("the beer and wine" if len(out) > 1 else "what ferments"))
    out += [INFUSIONS[c] for c in INFUSIONS if c in grown]
    from .bought_in import drink_note
    out += drink_note(bi, grown)
    if not ferm:
        out.append("no beer or wine yet (the people does not know fermentation)")
    return {"text": "; ".join(dict.fromkeys(out)), "list": list(dict.fromkeys(out))}


def _own_places(ctx, era: float, pid: str, mask: np.ndarray) -> dict:
    """The culture's people's living places on its cells at the era (the settlement ledger): counts by size and the largest."""
    sm = ctx.meta.get("settlements")
    if not sm:
        return {}
    import json
    from .brief import _holder_at, _pop_at
    if not hasattr(ctx, "_settle"):
        ctx._settle = json.loads((ctx.dir / sm["file"]).read_text())
    doc = ctx._settle
    city, town = doc["tiers"]["city_min"], min(doc["tiers"]["town_min_by_stage"][1:])
    cnt = {"city": 0, "town": 0, "village": 0}
    big = 0.0
    for s in doc["sites"]:
        if s.get("kind") in ("mine", "pit") or not mask[s["cell"]] or era > s["founded_kyr"] + 1e-6:
            continue
        pop = _pop_at(s, era)
        if pop <= 0 or _holder_at(s, era) != pid:
            continue
        cnt["city" if pop >= city else "town" if pop >= town else "village"] += 1
        big = max(big, pop)
    return {"counts": cnt, "largest_pop": round(big)}


def who_eats_together(ctx, brief: dict, p: dict, mask: np.ndarray, era: float) -> dict:
    """JUDGEMENT, a simple rule: the way of life sets the everyday eating group (a forager band shares the kill out; a herding household eats
    from one pot; a farming household at its own hearth), the largest places add the bought meal, feasting adds the big shared meals,
    and the culture's own kinship, rank and purity taboos say who may not eat with whom."""
    lines = []
    w = p["ways"] or {}
    main = _main_way(p)
    places = _own_places(ctx, era, p["people"], mask)
    cnt = places.get("counts") or {}
    dens = w.get("density_km2")
    if main == "foragers":
        if p.get("off_ladder") or ((dens is not None and dens < 0.05) and not any(cnt.values())):
            lines.append("few live together: a household of kin eats alone, and a guest is rare enough to be an event")
        elif any(cnt.values()):
            lines.append("settled foragers: each household eats at its own hearth, and a big catch or kill is shared out across the settlement")
        else:
            lines.append("the camp eats together: whoever brings in game shares it out across every hearth, gathered food stays with the household")
    elif main == "herders":
        lines.append("the herding household eats from one pot in its tent or steading; camps join for a slaughter, which is the feast")
    else:
        lines.append("each household eats at its own hearth; the village eats together at harvest and festivals")
    if cnt.get("city"):
        lines.append(("in their city" if cnt["city"] == 1 else f"in their {cnt['city']} cities") + " many eat bought food: cookshops and stalls feed those without a hearth")
    elif cnt.get("town"):
        lines.append(("market days in their town" if cnt["town"] == 1 else f"market days in their {cnt['town']} towns") + " bring the countryside in to eat")
    if "feasting" in p["know"]:
        lines.append("they hold feasts: food given away in quantity is how standing is made")
    for t in p["taboos"]:
        if t.get("target") in MEAL_TABOOS:
            lines.append(MEAL_TABOOS[t["target"]])
    return {"text": "; ".join(lines), "lines": lines, "places": places,
            "basis": "rule from the main way of life (ladder farm/herd shares), its own places in the settlement ledger, feasting known, and its kinship, rank and purity taboos (JUDGEMENT)"}


def neighbours(ctx, i: int, era: float, c: int, mask: np.ndarray) -> list:
    """The other cultures on or next to the culture's cells at frame i, the most shared or bordering cells first."""
    cell, cu = culture_cells(ctx, i, era)
    g = ctx.g
    ring = mask.copy()
    ring[g.nbr_idx[mask[g.nbr_src]]] = True
    near = ring[cell] & (cu != c)
    if not near.any():
        return []
    u, n = np.unique(cu[near], return_counts=True)
    C = ctx.cultures()["cultures"]
    order = sorted(zip(u.tolist(), n.tolist()), key=lambda x: (off_ladder(ctx, C[x[0]]["people"]), -x[1], x[0]))  # (dragons and giants after the peoples of the land)
    return [k for k, _ in order[:NEIGH_TOP]]


def outsiders(ctx, i: int, era: float, p: dict, others: list) -> dict:
    """What outsiders get wrong, from contrasts with the neighbouring cultures (each a rule; JUDGEMENT): a taboo against something they
    eat, milk drunk or refused, a body that tastes differently, a way of life read as poverty, a different fire. The strongest
    OUTSIDER_LINES, one per kind."""
    from . import animal_defs as AD, crop_defs as CD
    cand = []

    def nm(q):
        return q["name"]
    # 1. a taboo against what a neighbour eats
    for t in p["food_taboos"]:
        if t.get("scope") != "everyone":
            continue
        kept = t["target"] in AD.BY_ID or t["target"] in CD.BY_ID  # (a domesticate: only a neighbour that keeps it eats it; a wild kind, any)
        eaters = [q for q in others if t["target"] not in q["forbidden"] and (not kept or t["target"] in q["herds"] or t["target"] in q["crops"])]
        if eaters:
            cand.append((0, "taboo", f"a guest from {nm(eaters[0])} who brings {t['label']} gives offence: the {p['name']} do not eat it ({t['why']})"))
            break
    # 2. milk
    milkers = [q for q in others if q["dairy"]]
    dry = [q for q in others if not q["dairy"] and (q["herds"] or q["ways"] and (q["ways"].get("herd") or 0) > 0)]
    if p["dairy"] and dry:
        what = "milk-drinking for a habit of children" if p["dairy"]["fresh"] else "soured milk for spoiled food"
        cand.append((1, "milk", f"{nm(dry[0])}, who do not milk, take the {p['name']}'s {what}; to them it is the everyday food"))
    elif not p["dairy"] and p["herds"] and milkers:
        cand.append((1, "milk", f"{nm(milkers[0])}, who milk, expect the {p['name']}'s herds to give milk and cheese; they keep them for meat, hides and work"
                     + (", and their body does not milk its animals" if not p["body"].get("milks", True) else "")))
    # 3. body: a sense or diet the neighbours lack
    b = p["body"]
    for q in others:
        qb = q["body"]
        if b.get("diet") == "obligate_carnivore" and qb.get("diet") != "obligate_carnivore":
            cand.append((2, "body", f"{nm(q)} lay out bread and fruit for them; the {p['name']} live on meat and leave the rest"))
        elif not b.get("sweet", True) and qb.get("sweet", True):
            cand.append((2, "body", f"{nm(q)} honour a guest with sweets; the {p['name']} cannot taste sweet, so the gift falls flat"))
        elif b.get("capsaicin", True) is False and qb.get("capsaicin", True):
            cand.append((2, "body", f"{nm(q)} expect them to wince at chili; the {p['name']} do not feel its heat"))
        else:
            continue
        break
    # 4. a way of life read as poverty
    me = _main_way(p)
    for q in others:
        them = _main_way(q)
        if me == them:
            continue
        if me in ("herders", "foragers") and them == "farmers":
            cand.append((3, "way", f"{nm(q)}, who farm, take the {p['name']} for poor because they grow little grain; "
                         + ("their wealth walks: the herd is the granary" if me == "herders" else "they eat a broad wild menu by season and store little")))
        elif me == "farmers" and them in ("herders", "foragers"):
            cand.append((3, "way", f"{nm(q)} think the {p['name']} eat a dull round of the same staple; to them the stored harvest is the safety and the feast"))
        else:
            continue
        break
    # 5. a different fire
    for q in others:
        if p["fuel"] and q["fuel"] and q["fuel"] != p["fuel"] and not p["off_ladder"] and not q["off_ladder"]:
            cand.append((4, "fire", f"{nm(q)}, who cook over {q['fuel']}, expect {FUEL_COOK.get(q['fuel'], q['fuel']).split(':')[0]}; "
                         f"the {p['name']} cook over {p['fuel']} ({FUEL_COOK.get(p['fuel'], p['fuel']).split(':')[0]})"))
            break
    cand.sort(key=lambda x: x[0])
    lines = [t for _, _, t in cand[:OUTSIDER_LINES]]
    return {"text": "; ".join(lines) if lines else "no neighbouring culture differs enough here to misread them",
            "lines": lines, "neighbours": [{"id": q["id"], "name": q["name"], "people": q["people"]} for q in others]}


def wont_eat(p: dict) -> dict:
    """The culture's food taboos (taboos.json, PW-1305/PW-1312), split into its faith's (a god's domain) and its own."""
    rows = [{k: t.get(k) for k in ("label", "scope", "origin", "why")} for t in p["food_taboos"]]
    faith = [r for r in rows if r["origin"] == "divine"]
    own = [r for r in rows if r["origin"] != "divine"]
    return {"faith": faith, "own": own, "faith_name": (p["faith"] or {}).get("name"),
            "basis": "the taboos doc (present-day: the culture's taboos now)" if rows else "no food taboos (or no cultures in this run)"}


def food_fit(p: dict) -> dict:
    """The culture's people's body against food (PW-905, food_fit.py): what it thrives on, is poorly suited to or harmed by, with the
    foods its own fields grow that do not suit it."""
    from . import food_fit as FF
    out = FF.summary(p["body"], p["crops"])
    return {**out, "text": FF.line(p["body"], p["crops"])}


def sheet(ctx, brief: dict, c: int, i: int, era: float) -> dict:
    mask = mask_of(ctx, i, era, c)
    p = profile(ctx, i, era, c, mask)
    others = [profile(ctx, i, era, k) for k in neighbours(ctx, i, era, c, mask)]
    tr = brief.get("trade_reach")
    bi = tr if tr and "foods" in tr else None
    return {"culture": {k: p[k] for k in ("id", "name", "people", "people_name", "ways", "dairy", "faith", "cells")},
            "fuel": fuel(ctx, brief, p, bi), "staple": staple(ctx, brief, p, bi), "drink": drink(ctx, brief, p, bi),
            "who_eats_together": who_eats_together(ctx, brief, p, mask, era), "outsiders_get_wrong": outsiders(ctx, i, era, p, others),
            "wont_eat": wont_eat(p), "food_fit": food_fit(p), "goods": goods(ctx, c, i), "bought_in": bought_in(bi),
            **keeping(brief, p),
            "basis": "rule-based from this run at this era (cuisine.py); every line is for the culinary side to overrule"}


def keeping(brief: dict, p: dict) -> dict:
    """How the culture keeps its food and how its kitchen tastes (keeping.py, PW-744, PW-1715): {"preservation", "flavour"}."""
    from . import keeping as KP
    return KP.of(brief, p)


def bought_in(bi: dict | None) -> dict | None:
    """The "Bought in" line (PW-1505, bought_in.py): the foods the culture buys in, from whom, how far, by what road; None outside the
    exchange's window (the last ~12.5 kyr) or on a run without one."""
    if bi is None:
        return None
    return {"text": bi["text"], "foods": bi["foods"], "flown_in": bi["flown_in"], "ago_kyr": bi["ago_kyr"], "basis": bi["basis"]}


def goods(ctx, c: int, i: int) -> dict | None:
    """The culture's "has / lacks" line from the goods ledger (trade.py, PW-1502); None outside the land-use window (the last ~12.5 kyr)
    or for a kind that takes tribute rather than trading."""
    from . import trade as TR
    r = (TR.ledger_at(ctx, i) or {}).get(c)
    if r is None:
        return None
    return {"text": TR.line(r), "has": r["has"], "lacks": r["lacks"], "surplus": r["surplus"], "lack": r["lack"],
            "basis": "the goods ledger (trade.py): what its own land gives beyond its own need, and what its ways of life want but do not have at home"}


def markdown(s: dict, era: float) -> list[str]:
    cu = s["culture"]
    w = cu["ways"] or {}
    t = [f"## Cuisine sheet: {cu['name']} ({cu['people_name']}), {years_ago(era)}", "",
         f"- Fuel: {s['fuel']['text']}", f"- Staple: {s['staple']['text']}", f"- Drink: {s['drink']['text']}",
         f"- Who eats together: {s['who_eats_together']['text']}",
         f"- What outsiders get wrong: {s['outsiders_get_wrong']['text']}"]
    if s.get("goods"):
        t.append(f"- Has / lacks: {s['goods']['text']}")
    if s.get("bought_in"):
        t.append(f"- Bought in: {s['bought_in']['text']}")
    we = s["wont_eat"]
    if we["faith"] or we["own"]:
        t.append("- Won't eat:")
        for r in we["faith"]:
            t.append(f"  - {r['label']} ({r['scope']}; " + (f"of the faith, {we['faith_name']}" if we["faith_name"] else "of its gods") + f": {r['why']})")
        for r in we["own"]:
            t.append(f"  - {r['label']} ({r['scope']}; {r['origin']}: {r['why']})")
    else:
        t.append("- Won't eat: nothing forbidden")
    if s.get("preservation"):
        k = s["preservation"]
        t.append(f"- Keeping food: {k['text']}")
        for m in k["methods"][:6]:
            t.append(f"  - {m['label']} ~{max(1, round(100 * m['share']))}% ({m['what']}): because " + "; ".join(m["reasons"]))
        if k["absent"]:
            t.append("  - not yet: " + "; ".join(f"{a['label']} ({a['why']})" for a in k["absent"]))
    if s.get("flavour"):
        fl = s["flavour"]
        t.append(f"- Flavour: {fl['descriptor']}")
        for a, v in fl["axes"].items():
            if v["level"] != "none":
                t.append(f"  - {a}: {v['level']} ({v['value']}): because " + "; ".join(v["reasons"]))
    if s.get("through_time"):
        from .kitchen_time import markdown as kt_md
        t += kt_md(s["through_time"])
    if s.get("food_fit"):
        t.append(f"- Body and food ({cu['people_name']}): {s['food_fit']['text']}")
    t.append(f"- Ways of life: farm {w.get('farm')}, herd {w.get('herd')}, wild {w.get('forage')}" + (f" ({w['note']})" if w.get("note") else "")
             + (f"; faith: {cu['faith']['name']}" if cu.get("faith") else ""))
    if s["outsiders_get_wrong"]["neighbours"]:
        t.append("- Neighbours compared: " + ", ".join(f"{q['name']} ({q['people']}, culture {q['id']})" for q in s["outsiders_get_wrong"]["neighbours"]))
    t += [f"- ({s['basis']})", ""]
    return t


# -- the region brief's notes (was brief._suggested) ---------------------------------------------------------------------
def suggested(brief: dict) -> dict:
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
    pigs = any(a.get("id") == "pig" for a in brief.get("animals") or [])
    for m in (brief.get("mining") or {}).get("list", []):
        if "salt" not in m["kind"]:
            continue
        also = " and ore" if m["kind"] == "salt and ore" else ""
        cured = "salt pork" if pigs else "salt meat"  # (PW-835: pork only where pigs are kept on the region's land)
        notes.append(f"{m['name']} ({m['id']}) mine rock salt{also}: salt is their trade good, so their halls cure and brine freely ({cured}, brined cheese, "
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
