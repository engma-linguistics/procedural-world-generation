"""How a culture keeps its food and how its kitchen tastes (PW-744, PW-1715; under the culinary ethnography PW-692): read-only, by rule,
from a culture's brief (its land, salt, fish, fuels) and its cuisine profile (cuisine.profile: ways of life, crops, herds, dairy, what it
knows, its body and traits).

    preservation(brief, p)       -> {preserved_share, methods: [{id, label, share, reasons}], absent: [{id, label, why}], text}
    flavour(brief, p, keep)      -> {axes: {axis: {value, level, reasons}}, top, descriptor, text}

Mechanisms, not per-people fixes. Each method's weight is a product of four things, every one a stated reason:
  - the technique: the run's tech tree (meta.techtree.known); a method whose tech the tree has and the people does not know is absent,
    and a tree without that tech at all does not gate it (as cuisine.drink does with fermentation);
  - the environment: lean-season length (frost months, months without growth), aridity, damp, cold, salt reach, the everyday fuel;
  - what there is to keep: grain and pulses farmed, herds and dairy, fish, game, vegetables and fruit;
  - the body (spec.BODY_DEFAULT): no fire (no smoking; ferment and sun instead), raw meat (raw, aged and buried ferments), a low bitter
    sense (sharp, pungent ferments are no hardship), no sweet sense (ferments taken on to sour), a salt craving, a carnivore's diet (no
    grain or vegetable crocks); and the people's traits (a den or underground people keeps a cellar).
Two more inputs (lane 309):
  - bought-in food (PW-1727): the exchange's "Bought in" line (brief.trade_reach, bought_in.py) reaches the profile. Bought salt raises the
    salt reach (so salting, pickling and the salty axis), bought spice, sugar and oil add to the hot, sweet and fatty axes and bought salt
    fish to the savoury one, each at a lower weight than food from its own land, each with a "bought in from ..." reason;
  - a kind's authored leanings (PW-1728): the tree's body key `keeping` (spec.parse_keeping), method -> multiplier and `kept` (how much of
    its food is kept at all), laid over the derived weights with an "authored for this kind" reason. A leaning never opens a method whose
    tech the people does not know.
culinary-dnd's notes are the design intent these follow (docs/review/food/flavour-preservation.md quotes them): goblins' bitter-root
detox and chicha ferments and their "strong stomachs" (the D&D tree's goblinoid body: raw_meat, bitter low), the steppe orcs' "dung fire:
no roasting, no smoking" and dairy ferments "by necessity" (low lactase), the dwarves' cold cellars and salting, the delta lizardfolk's
peat smokehouse and fish ferments, the cat peoples' sour (not sweet) ferments. None of it names a people: a body or a land like theirs
gets the same kitchen on any tree.

Every weight below is JUDGEMENT (invented, not fitted to any real cuisine and not tuned to any run); the shares are "roughly how much",
for the culinary side to overrule. No number here claims to be a measurement.
"""

from __future__ import annotations

WAY_MIN = 0.10  # (as cuisine.WAY_MIN) a way of life counts from this share of the culture's heads
METHODS = (  # id, label, the techs that open it (any one), the plain word for what it is
    ("drying", "drying (sun, wind and frost)", ("smoking_drying", "storage", "raised_granary", "stockfish"), "dried meat, fish, fruit and grain in store"),
    ("smoking", "smoking", ("smoking_drying",), "meat and fish hung in the smoke"),
    ("salting", "salting and brining", ("salting", "solar_salt", "salt_mining"), "salt meat and fish, brined cheese"),
    ("pickling", "pickling (brine and vinegar)", ("pickling", "vinegar"), "vegetables and fruit in brine or vinegar"),
    ("ferment_dairy", "fermenting milk", ("fermented_dairy", "cheese", "fermentation"), "soured milk, curd and cheese"),
    ("ferment_grain", "fermenting grain and fruit (beer, wine, sour dough)", ("fermentation", "beer", "wine", "chicha", "rice_wine", "mead"),
     "beer, wine and soured doughs"),
    ("fish_sauce", "fermenting fish (sauce and paste)", ("fish_sauce",), "fish sauce and paste, buried and aged fish"),
    ("ferment_veg", "fermenting vegetables, roots and meat", ("fermentation", "plant_detox", "acorn_leaching"),
     "crocks of soured roots and greens, leached and fermented starches, buried and aged meat"),
    ("cellaring", "cellaring and freezing", ("cellaring", "ice_house", "storage"), "roots, cheese and meat kept cold"),
    ("rendering", "rendering fat", ("lard_rendering", "ghee_butter"), "lard, tallow, ghee and bone grease"),
)
LABEL = {m[0]: m[1] for m in METHODS}
SMOKY_FUEL = {"peat": 1.0, "wood": 0.8, "dung": 0.35, "charcoal": 0.3, "heath": 0.5, "coal": 0.4, "straw": 0.2, "grass": 0.1, "drift": 0.3,
              "oil": 0.0, "tallow": 0.1, "bone": 0.1}  # JUDGEMENT: how well the everyday fuel smokes food (peat the best; dung's low fire does
# not smoke, culinary-dnd's steppe orcs: "dung fire, no roasting, no smoking"; an oil lamp gives "no smoke and no flame to speak of")
FAT_CROPS = ("olive", "oil_seeds", "coconut", "avocado", "peanut")
SWEET_CROPS = ("cane", "sap_sugar", "date_palm", "tree_fruit", "vine", "banana", "sweet_potato", "cacao")
HOT_CROPS = ("chili", "spice_tree", "alliums")
VEG_CROPS = ("greens", "alliums", "roots", "squash", "nightshade_fruit", "beans", "pulses", "cowpea", "soybean", "potato", "sweet_potato")
GRAIN_CROPS = ("wheat", "rye", "foxtail_millet", "sorghum", "rice", "maize", "pseudograin", "stonegrain")
BITTER_CROPS = ("tea", "cacao", "greens")
# PW-1727: bought-in food (bought_in.py: per good the share of the culture's people some other culture supplies). JUDGEMENT: a bought share
# counts BOUGHT_GAIN times over (a market's salt reaches more tables than the people counted as supplied), bought salt never makes salt as
# cheap as one's own (BOUGHT_SALT_CAP), and each bought taste adds at most its cap to its axis; nothing below BOUGHT_MIN counts.
BOUGHT_MIN = 0.01  # (bought_in.SHOW_MIN: a giver is named from 1% of the people supplied)
BOUGHT_GAIN = 2.5
BOUGHT_SALT_CAP = 0.8
BOUGHT_TASTE = {"spices": ("hot", 0.15, 0.5), "sugar": ("sweet", 0.1, 0.4), "oil_wine": ("fatty", 0.05, 0.3), "dried_fish": ("umami", 0.05, 0.3)}  # good -> (axis, base, cap)
OIL_GIVER_CROPS = ("olive", "oil_seeds", "coconut")  # (oil_wine is oil where a giver grows these; wine alone adds no fat)
SPICE_AXIS = {"chili": "hot", "spice_tree": "hot", "tea": "bitter", "cacao": "bitter", "vanilla": "sweet"}  # (the "spices" good is what the
# givers' fields grow: pepper and chili are heat, tea and cacao bitterness, vanilla sweetness; givers with no crop named count as heat)
AXES = ("salty", "sour", "umami", "fatty", "hot", "smoky", "sweet", "bitter", "funk", "herbal")
SHORT = {"salty": "salty", "sour": "sour", "umami": "savoury", "fatty": "fatty", "hot": "hot", "smoky": "smoky", "sweet": "sweet",
         "bitter": "bitter", "funk": "funky", "herbal": "herbal"}
AXIS_WORD = {"salty": "salty", "sour": "sour", "umami": "savoury (umami)", "fatty": "fatty", "hot": "hot and pungent", "smoky": "smoky",
             "sweet": "sweet", "bitter": "bitter", "funk": "funky (fermented)", "herbal": "herbal"}


# -- the inputs, read once ------------------------------------------------------------------------------------------------------
def _num(x, d=0.0) -> float:
    return float(x) if isinstance(x, (int, float)) else d


def inputs(brief: dict, p: dict) -> dict:
    """The few numbers both passes read, with the plain fact behind each."""
    land = brief.get("land") or {}
    kop = land.get("koppen") or {}
    arid = sum(v for k, v in kop.items() if str(k)[:2] in ("BW", "BS"))
    tropic = sum(v for k, v in kop.items() if str(k)[:1] == "A")
    cold_c = land.get("coldest_month_c")
    frost = _num(land.get("frost_months_est"))
    grow = land.get("growing_months")
    lean = max(frost, 12.0 - _num(grow, 12.0)) if grow is not None or frost else 0.0
    precip = _num(land.get("precipitation_mm"), 600.0)
    sa = brief.get("salt") or {}
    near = _num(sa.get("within_100km_share"), 0.5 if not sa else 0.0)
    sea_salt = _num((sa.get("source_share_of_land") or {}).get("sea"))
    salt_mine = any("salt" in (m.get("kind") or "") for m in ((brief.get("mining") or {}).get("list") or []))
    salt = min(1.0, near + (0.3 if salt_mine else 0.0)) if sa else 0.5
    if sa.get("poor") or sa.get("poor_on_foot"):
        salt = min(salt, 0.3)
    fi = brief.get("fish") or {}
    fish = max(_num(fi.get("coast_fish")), 0.8 * _num(fi.get("river_runs")) / 0.5 if fi.get("river_runs") else 0.0,
               0.8 * _num(fi.get("lake_fish")) / 0.5 if fi.get("lake_fish") else 0.0)
    fish = min(1.0, fish + (0.3 if p.get("coastal") else 0.0))
    seals = sum(_num(v) for v in ((fi.get("sea_mammals") or {}).values()))
    lead = ((brief.get("fuels") or {}).get("lead")) or {}
    fuel = next(iter(lead), None) or p.get("fuel")
    w = p.get("ways") or {}
    body = p.get("body") or {}
    crops = set(p.get("crops") or {})
    carn = body.get("diet") in ("carnivore", "obligate_carnivore")
    bought = bought_of(brief.get("trade_reach"))
    own_salt = salt
    if "salt" in bought:
        salt = max(salt, min(BOUGHT_SALT_CAP, salt + BOUGHT_GAIN * bought["salt"]["share"]))
    return {"bought": bought, "own_salt": own_salt, "arid": arid, "tropic": tropic, "cold_c": cold_c, "frost": frost, "lean": min(12.0, lean), "precip": precip,
            "temp": land.get("temperature_c"), "elev": _num((land.get("elevation_m") or {}).get("mean")), "tree": _num(land.get("tree_cover_pct")),
            "salt": salt, "salt_km": (sa.get("km_to_salt") or {}).get("mean"), "sea_salt": sea_salt, "salt_mine": salt_mine,
            "fish": fish, "seals": min(1.0, seals), "fuel": fuel, "farm": _num(w.get("farm")), "herd": _num(w.get("herd")),
            "forage": _num(w.get("forage"), 1.0), "crops": crops, "carn": carn, "body": body, "know": set(p.get("know") or ()),
            "dairy": p.get("dairy"), "herds": set(p.get("herds") or {}), "traits": set(_traits(p)), "tree_techs": p.get("tree_techs")}


def bought_of(tr: dict | None) -> dict:
    """{good: {share, from: [giver names], what: [crop goods], crops: set}} of the culture's bought-in foods (its own "Bought in" line,
    bought_in.of_culture; trade only, not tribute), from BOUGHT_MIN of its people supplied. Empty outside the exchange's window."""
    out: dict = {}
    if not tr or "foods" not in tr:
        return out
    for fd in tr["foods"]:
        gv = [g for g in fd.get("givers") or [] if g.get("road") != "tribute"]
        sh = _num(fd.get("share")) - sum(_num(g.get("share")) for g in fd.get("givers") or [] if g.get("road") == "tribute")  # (tribute is not bought)
        if sh < BOUGHT_MIN:
            continue
        crops = {k for g in gv for k in g.get("crops") or ()}
        out[fd["good"]] = {"share": round(sh, 3), "from": [g["name"] for g in gv[:2]], "what": list(dict.fromkeys(w for g in gv for w in g.get("what") or ()))[:3],
                           "crops": crops, "label": fd.get("label") or fd["good"]}
    return out


def bought_why(b: dict, good: str) -> str:
    """'bought in from X and Y (4% of its people supplied)'."""
    r = b[good]
    who = " and ".join(r["from"]) if r["from"] else "other cultures"
    return f"{r['label']} bought in from {who} ({max(1, round(100 * r['share']))}% of its people supplied)"


def _traits(p: dict) -> list:
    t = p.get("line_traits") or []
    return list(t) + (["coastal"] if p.get("coastal") else [])


def _climate_word(x: dict) -> str:
    if x["cold_c"] is not None and (x["cold_c"] <= -8 or x["frost"] >= 5):
        return "cold"
    if x["arid"] >= 0.5:
        return "dry"
    if x["tropic"] >= 0.5:
        return "tropical"
    if x["precip"] >= 1200:
        return "wet"
    return "temperate"


# -- preservation --------------------------------------------------------------------------------------------------------------
def _gate(x: dict, techs: tuple) -> tuple[bool, str | None]:
    """Is the method open to the culture? (True, None) when it knows one of the techs or the run's tree has none of them."""
    tree = x["tree_techs"]
    have = [t for t in techs if t in x["know"]]
    if have:
        return True, None
    if tree is None or not any(t in tree for t in techs):
        return True, None
    return False, f"does not know {techs[0].replace('_', ' ')} yet"


def preservation(brief: dict, p: dict, x: dict | None = None) -> dict:
    """Which ways of keeping food the culture uses, and roughly how much of what it eats each keeps (shares of all its food)."""
    x = x or inputs(brief, p)
    b = x["body"]
    fire = b.get("fire", True)
    raw = bool(b.get("raw_meat"))
    bitter_low = b.get("bitter") == "low"
    sweet_blind = b.get("sweet") is False or (isinstance(b.get("sweet"), float) and b["sweet"] < 0.5)
    den = bool(x["traits"] & {"subterranean", "denning", "delving"})
    grain = x["farm"] >= WAY_MIN and not x["carn"] and bool(x["crops"] & set(GRAIN_CROPS) or x["farm"] >= 0.3)
    veg = x["farm"] >= WAY_MIN and not x["carn"] and bool(x["crops"] & set(VEG_CROPS))
    meat = min(1.0, x["herd"] + 0.6 * x["forage"] + (0.4 if x["carn"] else 0.0))
    fish = x["fish"]
    fruit = bool(x["crops"] & set(SWEET_CROPS))
    cold = x["cold_c"] is not None and x["cold_c"] <= 0
    deep_cold = x["cold_c"] is not None and x["cold_c"] <= -8
    smoky_fuel = SMOKY_FUEL.get(x["fuel"] or "", 0.4)
    damp = min(1.0, max(0.0, (x["precip"] - 500) / 1000))
    R: dict = {m[0]: [] for m in METHODS}
    W: dict = {}
    # drying: sun and wind in a dry land, frost in a cold one; grain in store for farmers
    w = 0.25 + 0.6 * x["arid"] + (0.25 if deep_cold else 0.0) + 0.3 * (1 - damp) * (1 if not cold else 0.5)
    w *= 0.3 + meat + fish + (0.8 if grain else 0.0) + (0.2 if fruit else 0.0)
    if x["arid"] >= 0.3:
        R["drying"].append(f"a dry land ({round(100 * x['arid'])}% steppe and desert): sun and wind dry meat, fruit and curd")
    if deep_cold:
        R["drying"].append(f"hard winters (coldest month {x['cold_c']} C): frost-drying in the wind")
    if grain:
        R["drying"].append("farmed grain and pulses are kept dry in store")
    if damp >= 0.6:
        w *= 0.6
        R["drying"].append(f"a wet land ({round(x['precip'])} mm a year): air-drying spoils, so less of it")
    if not fire:
        w *= 1.3
        R["drying"].append("keeps no fire, so the sun and wind do what smoke would")
    W["drying"] = w
    # smoking: needs fire and a fuel that smokes; damp country, fish and game want it
    w = (0.2 + 0.8 * smoky_fuel) * (0.3 + 0.8 * damp + (0.3 if cold else 0.0)) * (0.2 + meat + 1.2 * fish)
    R["smoking"].append(f"everyday fuel {x['fuel'] or 'unknown'}: " + ("smokes well" if smoky_fuel >= 0.7 else "a middling smoke" if smoky_fuel >= 0.4 else
                                                                         "a poor smoking fire"))
    if damp >= 0.4:
        R["smoking"].append(f"damp air ({round(x['precip'])} mm a year): smoke dries where the sun cannot")
    if fish >= 0.4:
        R["smoking"].append("a fishery: the catch is smoked for the lean months")
    if not fire:
        w = 0.0
        R["smoking"] = ["keeps no fire of its own: nothing is smoked"]
    elif raw:
        w *= 0.8
    W["smoking"] = w
    # salting: salt reach times what there is to salt
    w = (0.05 + 1.1 * x["salt"]) * (0.2 + 0.8 * meat + 1.2 * fish + (0.3 if x["dairy"] else 0.0))
    own = x.get("own_salt", x["salt"])  # (the reason is about its own land; bought salt has its own line below)
    if own >= 0.6:
        R["salting"].append("salt is near: " + ("the sea is the salt" if x["sea_salt"] >= 0.2 else "salt springs or deposits") + (", and its own salt mines" if x["salt_mine"] else ""))
    elif own <= 0.3:
        R["salting"].append(f"salt is far on its own land ({x['salt_km']} km on average)" if "salt" in x.get("bought", {}) else
                            f"salt is far ({x['salt_km']} km on average): traded in and dear, so little is salted")
    else:
        R["salting"].append("salt within reach for part of the land")
    if "salt" in x.get("bought", {}):
        R["salting"].append(bought_why(x["bought"], "salt") + (": salt it has not on its own land" if own <= 0.3 else ""))
    if b.get("salt") == "craving":
        w *= 1.3
        R["salting"].append("its body craves salt")
    if fish >= 0.4:
        R["salting"].append("fish to salt and brine")
    W["salting"] = w
    # pickling: vegetables (or fruit) and salt or vinegar
    w = (0.3 + 0.7 * x["salt"]) * ((0.9 if veg else 0.0) + (0.3 if fruit else 0.0) + (0.2 if x["farm"] >= WAY_MIN and not x["carn"] else 0.0))
    if veg:
        R["pickling"].append("garden vegetables to put up in brine")
    if sweet_blind:
        w *= 1.4
        R["pickling"].append("the people tastes no sweetness: what ferments is taken on to vinegar and sourness")
    if x["carn"]:
        R["pickling"].append("a carnivore's diet: no vegetable crocks")
    W["pickling"] = w
    # dairy
    d = x["dairy"]
    w = 0.0
    if d:
        lac = _num(d.get("lactase_share"))
        w = (0.4 + 1.2 * x["herd"]) * (1.6 - lac)
        R["ferment_dairy"].append(f"milks {', '.join(d.get('animals') or [])}" + (f"; few adults digest fresh milk (lactase {round(100 * lac)}%), so milk is soured and aged"
                                                                                   if lac < 0.6 else "; milk is drunk fresh as well as kept"))
        if d.get("cheese"):
            w *= 1.2
            R["ferment_dairy"].append("knows cheese")
    else:
        R["ferment_dairy"].append("no dairy: it does not herd and milk")
    W["ferment_dairy"] = w
    # grain and fruit ferments
    w = (1.0 if grain else 0.0) * (0.3 + 0.8 * x["farm"]) + (0.4 if fruit else 0.0) + (0.2 if {"honey_hunting", "beekeeping", "mead"} & x["know"] else 0.0)
    if grain:
        R["ferment_grain"].append("farmed grain: beer and soured doughs")
    if fruit:
        R["ferment_grain"].append("fruit and sugar crops: wine and fruit ferments")
    if not grain and not fruit:
        R["ferment_grain"].append("no grain or fruit grown to brew")
        w = min(w, 0.1)
    W["ferment_grain"] = w
    # fish sauce and paste
    w = fish * (0.2 + 0.9 * x["salt"]) * (1.0 + (0.5 if x["tropic"] >= 0.3 or (x["temp"] or 0) >= 18 else 0.0))
    if fish >= 0.3:
        R["fish_sauce"].append("fish to ferment" + (" in a warm climate, where fish turns fast" if (x["temp"] or 0) >= 18 else ""))
    else:
        R["fish_sauce"].append("little fish")
        w *= 0.3
    if raw and bitter_low:
        w *= 1.3
        R["fish_sauce"].append("strong stomachs (raw meat, a low bitter sense): fermented and aged fish are no hardship")
    W["fish_sauce"] = w
    # vegetables, roots, meat: crocks, pits, buried and aged meat
    w = 0.15 + (0.5 if veg else 0.0) + 0.3 * x["forage"] + 0.3 * meat * (1 if (raw or not fire or deep_cold) else 0.3)
    if raw:
        w *= 1.25
        R["ferment_veg"].append("eats meat raw: aged and fermented meat and offal are no hardship")
    if bitter_low:
        w *= 1.4
        R["ferment_veg"].append("a low bitter sense: sharp, pungent ferments and bitter roots made safe by leaching and souring")
    if not fire:
        w *= 1.6
        R["ferment_veg"].append("keeps no fire: fermentation is its cooking")
    if deep_cold:
        R["ferment_veg"].append("cold ground: meat and fish buried to ferment slowly")
    if veg:
        R["ferment_veg"].append("garden vegetables and roots to sour")
    W["ferment_veg"] = w
    # cellaring and freezing
    w = (0.1 + (0.6 if cold else 0.0) + (0.4 if deep_cold else 0.0) + (0.5 if den else 0.0) + 0.0003 * max(0.0, x["elev"] - 1000)) * \
        (0.4 + (0.6 if grain or veg else 0.0) + 0.5 * meat + (0.3 if d else 0.0))
    if cold:
        R["cellaring"].append(f"winters below freezing (coldest month {x['cold_c']} C)" + (": the winter is the freezer" if deep_cold else ""))
    if den:
        R["cellaring"].append("a den and tunnel people: the ground is its cellar")
    if x["elev"] >= 1500:
        R["cellaring"].append(f"high land ({round(x['elev'])} m on average): cool caves and stores")
    W["cellaring"] = w
    # rendering
    fat_animals = x["herd"] + 0.5 * x["forage"] + x["seals"]
    w = (0.1 + fat_animals) * (0.4 + (0.6 if cold else 0.0) + (0.4 if x["fuel"] in ("tallow", "oil", "bone") else 0.0))
    if x["herd"] >= WAY_MIN:
        R["rendering"].append("herd fat to render")
    if x["seals"] >= 0.2:
        R["rendering"].append("sea mammals: oil and blubber")
    if cold:
        R["rendering"].append("cold winters want fat")
    if x["fuel"] in ("tallow", "oil", "bone"):
        R["rendering"].append(f"burns {x['fuel']}: fat is fuel as well as food")
    W["rendering"] = w
    # gates
    absent = []
    for mid, label, techs, _ in METHODS:
        ok, why = _gate(x, techs)
        if not ok:
            absent.append({"id": mid, "label": label, "why": why})
            W[mid] = 0.0
        elif W[mid] < 0.05:
            W[mid] = 0.0
    lean, lean_why = b.get("keeping") or {}, (b.get("keeping") or {}).get("why")
    for mid, label, _, _ in METHODS:  # (PW-1728: the kind's authored leanings, after the gates: a leaning never opens a closed method)
        k = lean.get(mid)
        if k is None or k == 1.0 or any(a["id"] == mid for a in absent):
            continue
        if k == 0.0:
            if W[mid] > 0:
                absent.append({"id": mid, "label": label, "why": "never done by this kind (authored in the tree)" + (f": {lean_why}" if lean_why else "")})
            W[mid] = 0.0
            continue
        W[mid] *= k
        R[mid].append(f"authored for this kind: x{k:g}" + (f" ({lean_why})" if lean_why else ""))
    hunter = not any(W.values())  # (knows none of the keeping techs: a hunter of the moment, as the off-ladder kinds)
    # how much of all food is kept at all: the lean season, with store-keeping farmers and herds (JUDGEMENT)
    pres = 0.08 + 0.045 * x["lean"] + (0.15 if grain else 0.0) + 0.1 * min(1.0, x["herd"]) + (0.05 if x["arid"] >= 0.5 else 0.0)
    if x["forage"] >= 0.6 and not deep_cold:
        pres *= 0.7
    if "kept" in lean and lean["kept"] != 1.0:
        pres *= lean["kept"]
    pres = round(min(0.75, max(0.05 if lean.get("kept", 1.0) > 0 else 0.0, pres)), 2) if not hunter else 0.0
    pres_why = f"lean season about {round(x['lean'])} months" + ("; farmed grain is a stored food" if grain else "") + \
        ("; the herd is a larder on the hoof" if x["herd"] >= 0.3 else "") + ("; foragers store little" if x["forage"] >= 0.6 and not deep_cold else "")
    if "kept" in lean and lean["kept"] != 1.0:
        pres_why += f"; authored for this kind: x{lean['kept']:g} of its food kept" + (f" ({lean_why})" if lean_why else "")
    if hunter:
        pres_why = "it knows none of the ways of keeping food: the kill and the gathered food are eaten fresh"
    tot = sum(W.values()) or 1.0
    meth = sorted(({"id": m[0], "label": m[1], "what": m[3], "share": round(pres * W[m[0]] / tot, 3), "weight": round(W[m[0]], 3), "reasons": R[m[0]]}
                   for m in METHODS if W[m[0]] > 0), key=lambda r: -r["share"])
    meth = [r for r in meth if r["share"] >= 0.005]
    return {"preserved_share": pres, "preserved_why": pres_why, "methods": meth, "absent": absent, "text": text_of(pres, meth),
            "basis": "rule-based (keeping.py): weights are invented judgements over this run's land, fuel, salt, foods, techs and body, not measurements"}


def text_of(pres: float, meth: list) -> str:
    top = [f"{m['label'].split(' (')[0]} ~{max(1, round(100 * m['share']))}%" for m in meth[:5]]
    return f"about {round(100 * pres)}% of what it eats is kept food: " + ", ".join(top) + " (shares of all its food)" if top else "nothing is kept: it eats its food fresh"


# -- flavour -------------------------------------------------------------------------------------------------------------------
def _lvl(v: float) -> str:
    return "high" if v >= 0.6 else "medium" if v >= 0.35 else "low" if v >= 0.12 else "none"


def flavour(brief: dict, p: dict, keep: dict | None = None, x: dict | None = None) -> dict:
    """The kitchen's taste on ten axes, 0..1, each from the culture's ingredients and its ways of keeping food, each with its reasons."""
    x = x or inputs(brief, p)
    keep = keep or preservation(brief, p, x)
    S = {m["id"]: m["share"] / max(0.01, keep["preserved_share"]) for m in keep["methods"]}  # (each method's part of the kept food)
    pres = keep["preserved_share"]
    b, crops = x["body"], x["crops"]
    A = {a: 0.0 for a in AXES}
    R: dict = {a: [] for a in AXES}

    def add(a, v, why):
        if v > 0.01:
            A[a] += v
            R[a].append(why)

    kept = lambda m: pres * S.get(m, 0.0) * 2.5  # noqa: E731  (a method's pull on the plate: its share of all food, scaled)
    bo = x.get("bought") or {}
    own = x.get("own_salt", x["salt"])
    salt_word = "salt near at hand" if own >= 0.6 else "some salt within reach" if own > 0.3 else "salt far and dear"
    if "salt" in bo:
        salt_word = ("salt far on its own land, but " if own <= 0.3 else salt_word + "; and ") + bought_why(bo, "salt")
    add("salty", (0.6 if S.get("salting") or S.get("fish_sauce") else 0.35) * x["salt"], salt_word)
    add("salty", kept("salting") + 0.6 * kept("fish_sauce") + 0.4 * kept("pickling"), "salted, brined and fish-sauced keeping")
    if b.get("salt") == "craving":
        add("salty", 0.2, "a body that craves salt")
    lac = _num((x["dairy"] or {}).get("lactase_share"), 1.0)
    add("sour", kept("pickling") + kept("ferment_dairy") * (1.3 - 0.5 * lac) + 0.6 * kept("ferment_grain") + 0.6 * kept("ferment_veg"),
        "soured keeping: " + ", ".join(LABEL[m].split(" (")[0] for m in ("pickling", "ferment_dairy", "ferment_grain", "ferment_veg") if S.get(m)))
    if b.get("sweet") is False:
        add("sour", 0.2, "tastes no sweetness, so fruit is taken to vinegar and sour")
    um = {"fish sauce and paste": kept("fish_sauce") * 1.5, "aged cheese and curd": 0.5 * kept("ferment_dairy"), "fish": 0.3 * x["fish"],
          "meat and broth": 0.25 * min(1.0, x["herd"] + 0.5 * x["forage"] + (0.5 if x["carn"] else 0.0))}
    add("umami", sum(um.values()), ", ".join(k for k, v in um.items() if v >= 0.03))
    if crops & {"soybean", "beans"} and "soy_ferment" in x["know"]:
        add("umami", 0.3, "fermented beans")
    add("fatty", 0.4 * min(1.0, x["herd"] + 0.4 * x["forage"]) + kept("rendering") * 1.5 + 0.3 * x["seals"], "herd and game fat, rendered fat")
    fc = [c for c in FAT_CROPS if c in crops]
    if fc:
        add("fatty", 0.3, "oil crops: " + ", ".join(c.replace("_", " ") for c in fc))
    if x["cold_c"] is not None and x["cold_c"] <= -8:
        add("fatty", 0.15, "a cold land's diet runs to fat")
    hc = [c for c in HOT_CROPS if c in crops]
    if hc:
        heat = 0.3 * len(hc)
        if "chili" in hc and b.get("capsaicin") is False:
            heat -= 0.3
            add("sweet", 0.2, "chili-like peppers taste only fruity-sweet to this people (it feels no capsaicin burn)")
        add("hot", heat, "pungent crops: " + ", ".join(c.replace("_", " ") for c in hc))
    smoke = SMOKY_FUEL.get(x["fuel"] or "", 0.4)
    add("smoky", kept("smoking") * 1.6, "smoked keeping")
    if b.get("fire", True):
        add("smoky", 0.3 * smoke, f"everyday cooking on {x['fuel'] or 'its fuel'}")
    sc = [c for c in SWEET_CROPS if c in crops]
    add("sweet", min(0.45, 0.12 * len(sc)), "sweet crops: " + ", ".join(c.replace("_", " ") for c in sc))
    if {"honey_hunting", "beekeeping"} & x["know"]:
        add("sweet", 0.2, "honey")
    if x["dairy"] and lac >= 0.6:
        add("sweet", 0.1, "fresh milk")
    if b.get("sweet") is False:
        A["sweet"], R["sweet"] = 0.0, ["the people has no sweet sense: sweetness is not perceived, so not sought"]
    bc = [c for c in BITTER_CROPS if c in crops]
    plants = 0.0 if x["carn"] or p.get("off_ladder") else 1.0  # (a meat-eater, or a kind off the ladder, gathers no greens)
    add("bitter", 0.15 * len(bc) + (0.2 if {"acorn_leaching", "plant_detox"} & x["know"] else 0.0) + 0.15 * x["forage"] * plants,
        "bitter leaves, roots and drinks" + (" (leached and detoxed)" if {"acorn_leaching", "plant_detox"} & x["know"] else ""))
    if b.get("bitter") == "low":
        A["bitter"] *= 1.5
        R["bitter"].append("a low bitter sense: bitter food is eaten without fuss")
    elif b.get("bitter") == "high":
        A["bitter"] *= 0.5
        R["bitter"].append("a keen bitter sense: bitterness is avoided")
    fk = {"fish sauce and aged fish": 1.2 * kept("fish_sauce"), "soured crocks, roots and buried meat": 1.2 * kept("ferment_veg"),
          "soured milk and cheese": 0.6 * kept("ferment_dairy"), "beer and soured dough": 0.2 * kept("ferment_grain")}
    add("funk", sum(fk.values()), "long ferments: " + ", ".join(k for k, v in fk.items() if v >= 0.02))
    if b.get("raw_meat"):
        add("funk", 0.25 if b.get("bitter") == "low" else 0.1, "raw and aged meat" + (", and a strong stomach for it" if b.get("bitter") == "low" else ""))
    add("herbal", (0.3 * x["forage"] + 0.15 * min(1.0, x["tree"] / 60)) * plants + 0.1 * len([c for c in ("greens", "alliums", "tea", "spice_tree") if c in crops]),
        "wild greens and herbs gathered" + (", garden herbs" if crops & {"greens", "alliums"} else ""))
    if b.get("smell") == "keen":
        add("herbal", 0.15, "a keen nose: aroma counts")
    for good, (ax, base, cap) in BOUGHT_TASTE.items():  # (PW-1727: bought-in tastes, below what its own land would give)
        if good not in bo or (good == "oil_wine" and bo[good]["crops"] and not bo[good]["crops"] & set(OIL_GIVER_CROPS)):
            continue
        v = min(cap, base + BOUGHT_GAIN * bo[good]["share"])
        why = bought_why(bo, good) + (f": {', '.join(bo[good]['what'])}" if bo[good]["what"] else "")
        axes = [ax]
        if good == "spices" and bo[good]["crops"] & set(SPICE_AXIS):
            sp = bo[good]["crops"] & set(SPICE_AXIS)
            if b.get("capsaicin") is False and "chili" in sp and "spice_tree" not in sp:
                sp = (sp - {"chili"}) | {"vanilla"}  # (chili that does not burn this people tastes fruity-sweet)
            axes = sorted({SPICE_AXIS[c] for c in sp})
        for a in axes:
            if a == "sweet" and b.get("sweet") is False:
                continue
            add(a, v if a == ax else 0.6 * v, why)
    out = {}
    for a in AXES:
        v = round(min(1.0, A[a]), 2)
        out[a] = {"value": v, "level": _lvl(v), "reasons": R[a]}
    top = sorted((a for a in AXES if out[a]["value"] >= 0.2), key=lambda a: -out[a]["value"])[:3]
    return {"axes": out, "top": top, "descriptor": descriptor(top, keep, x), "text": "; ".join(f"{AXIS_WORD[a]}: {out[a]['level']}" for a in AXES),
            "basis": "rule-based (keeping.py) from the culture's ingredients, its keeping and its senses; invented weights, not tuned to taste"}


def descriptor(top: list, keep: dict, x: dict) -> str:
    """One line: the leading tastes and the kind of kitchen ("smoky, sour and fatty: a cold-coast smoking-and-fermenting kitchen")."""
    words = [SHORT[a] for a in top] or ["plain"]
    taste = words[0] if len(words) == 1 else ", ".join(words[:-1]) + " and " + words[-1]
    place = _climate_word(x)
    if x["fish"] >= 0.5:
        place += "-coast" if x["coastal_like"] else " river-and-lake"
    elif x["herd"] >= 0.4:
        place += " herding"
    elif x["farm"] >= 0.5:
        place += " farming"
    else:
        place += " foraging"
    short = {"drying": "drying", "smoking": "smoking", "salting": "salting", "pickling": "pickling", "ferment_dairy": "soured-milk",
             "ferment_grain": "brewing", "fish_sauce": "fish-sauce", "ferment_veg": "fermenting", "cellaring": "cellar", "rendering": "rendering"}
    m = [short[r["id"]] for r in keep["methods"][:2]]
    if x["body"].get("fire") is False or (x["body"].get("raw_meat") and x["body"].get("bitter") == "low"):  # (no fire, or strong stomachs)
        m = m[:1] + ["raw-food"]
    how = "-and-".join(dict.fromkeys(m)) if m else "fresh-food"
    return f"{taste}: a {place} {how} kitchen"


def of(brief: dict, p: dict) -> dict:
    """Both passes for one culture: {"preservation", "flavour"}."""
    x = inputs(brief, p)
    x["coastal_like"] = bool(p.get("coastal")) or _num((brief.get("fish") or {}).get("coast_fish")) >= 0.4
    keep = preservation(brief, p, x)
    return {"preservation": keep, "flavour": flavour(brief, p, keep, x)}
