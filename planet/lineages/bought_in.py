"""Bought-in foods in the culinary brief (trade step 4a for the brief, PW-1505; design1.md step 4a): what a culture buys in to eat and
drink, from whom, how far and by what road, read from the exchange doc (trade_flow.py, server.trade_flow_doc).

    of_culture(ctx, doc, c, era)       -> {"ago_kyr", "foods": [...], "flown_in": [...], "text"} or None outside the land-use window
    staple_note / drink_note / fuel_note(r) -> the cuisine sheet's notes on bought-in grain, fish and meat; wine, tea and cacao; firewood

In plain words: real cuisines are full of food from elsewhere: salt, pepper, wine where no vine grows, salt fish far inland, grain eaten
by herders. The exchange (step 2) already says, per culture and era, which goods reach it from which other culture, how far (km along
the way the goods took, weighted by people supplied), mainly by which way (land, river, sea, a flyer's air) and as what kind of exchange
(gift, barter, market, merchant, tribute). This module picks the foods out of that, names the road the way a cook would (by sea, by river,
by caravan, driven on the hoof, overland from a neighbour's market, flown in, taken as tribute) and, for oil and wine, sugar and spices,
says which crop it is from the giver's own fields (wine where the giver grows the vine, tea where it grows tea).

Read after the run (D63 A, PW-1499): nothing here changes the history or the exchange; the brief only reads it. Shares are of the taker's
people whose want of that good the flow meets (trade_flow.flows_at: "share of the taker's people"), not shares of the diet: the exchange
has no amounts eaten. No number here is a real-world measurement; the cut-offs are display choices, marked JUDGEMENT. Checked on the
stored L7 runs in docs/review/culture/trade/bought_in.md (lane 235).
"""

from __future__ import annotations

from . import trade as TR

VERSION = 1

# the goods that are eaten or drunk, in the order the line lists them when shares tie (trade.GOODS ids)
FOOD_GOODS = ("grain", "dried_fish", "livestock", "salt", "oil_wine", "sugar", "spices", "seal_oil")
FOOD_LABEL = {"grain": "grain", "dried_fish": "dried and salted fish", "livestock": "herd animals", "salt": "salt",
              "oil_wine": "oil and wine", "sugar": "sugar", "spices": "spices", "seal_oil": "seal and whale oil"}
FUEL_GOODS = ("firewood",)  # (the fuel line's bought-in fuel: firewood and charcoal)
# what a crop-made good is, by the crop the giver grows (trade.CROPS); the giver's fields name it
CROP_WHAT = {"olive": "olive oil", "vine": "wine", "oil_seeds": "seed oil", "date_palm": "dates", "coconut": "coconuts",
             "cane": "cane sugar", "sap_sugar": "sap sugar", "spice_tree": "pepper and cinnamon-like spice", "chili": "chilies", "tea": "tea",
             "vanilla": "vanilla", "cacao": "cacao"}
DRINKS = {"vine": "wine", "date_palm": "date wine", "coconut": "palm wine", "tea": "tea", "cacao": "a cacao drink"}  # (cuisine.drink's names)
ROAD = {"sea": "by sea", "river": "by river", "air": "flown in", "caravan": "by caravan", "droves": "driven on the hoof",
        "overland": "overland", "tribute": "as tribute", "local": "on the same land"}
SHOW_MIN = 0.01  # JUDGEMENT (display): a giver is named for a food from 1% of the culture's people supplied (trade_flow.FLOW_MIN is 0.2%)
NOTE_MIN = 0.05  # JUDGEMENT (display): a bought-in food enters the staple, drink or fuel line from 5% of the culture's people supplied
GIVERS_TOP = 3  # givers named per food
WHAT_TOP = 2  # crops named per giver of a crop good (the most widely grown on its land first)
FOODS_TOP = 6  # foods in the one-line text


def frame_of(doc: dict | None, era: float) -> dict | None:
    """The exchange doc's frame nearest the era, None outside the land-use window (more than half a frame step beyond its ends)."""
    fs = (doc or {}).get("frames") or []
    if not fs:
        return None
    f = min(fs, key=lambda f: abs(f["ago_kyr"] - era))
    ags = sorted(x["ago_kyr"] for x in fs)
    step = (ags[-1] - ags[0]) / max(1, len(ags) - 1) if len(ags) > 1 else 0.5
    return f if abs(f["ago_kyr"] - era) <= 0.5 * step + 1e-6 else None


def road(mode: str, good: str, kind: str) -> str:
    """The road a cook would name. JUDGEMENT: land with merchants (a third culture between, and caravans or ships known: trade_flow.kind_of)
    is a caravan; herd animals and horses on land are droves (trade_flow.DROVE_GOODS); other land is overland (a neighbour's market or
    barter, by pack animal, cart or porter)."""
    from .trade_flow import DROVE_GOODS
    if kind == "tribute":
        return "tribute"
    if mode == "land":
        return "droves" if good in DROVE_GOODS else "caravan" if kind == "merchant" else "overland"
    return mode if mode in ROAD else "overland"


def _giver_crops(ctx, frame: int, era: float, giver: int, cache: dict) -> dict:
    """The crops the giver grows on its own land at the frame, {crop: share of its land} (cuisine's crop_known reading), cached per giver."""
    if giver not in cache:
        from ..geo import is_land
        from . import cuisine as CZ
        try:
            m = CZ.mask_of(ctx, frame, era, giver)
            m &= is_land(ctx.f("elevation", frame).astype(float), ctx.f("ice", frame).astype(float) > 0.5)
            cache[giver] = dict(CZ._bits_on(ctx, "crop_known", "crops", frame, m))
        except (KeyError, IndexError, ValueError):
            cache[giver] = {}
    return cache[giver]


def _ranked(grown: dict, need) -> list:
    """The crops of `need` the giver grows, the most widely grown first."""
    return sorted((k for k in need if k in grown), key=lambda k: -grown[k])


def _name(doc: dict, ctx, k: int) -> tuple[str, str | None]:
    C = doc.get("cultures") or []
    x = C[k] if 0 <= k < len(C) else {}
    pid = x.get("people")
    pn = ctx.lines[ctx.idx[pid]]["name"] if ctx is not None and pid in getattr(ctx, "idx", {}) else pid
    return x.get("name") or f"culture {k}", pn


def of_culture(ctx, doc: dict | None, c: int, era: float) -> dict | None:
    """Culture c's bought-in foods at the era (the exchange doc's nearest frame; c already resolved to the culture holding its land then).
    {"ago_kyr", "frame", "as", "foods": [{"good", "label", "share", "unmet", "home", "givers": [{"culture", "name", "people", "share", "km",
    "road", "mode", "kind", "via", "what"}]}], "fuel": [same, firewood], "flown_in": [{"crop", "by", "by_name", "cells"}], "carries": [...],
    "text", "basis"}, or None without a doc or outside its window."""
    f = frame_of(doc, era)
    if f is None:
        return None
    C = (ctx.cultures() or {}).get("cultures") or []
    h = TR._at(C, c, f["ago_kyr"]) if C else c
    fera = float(f["ago_kyr"])
    crops_of: dict = {}
    by_good: dict = {}
    for x in f["flows"]:
        if x[1] != h or (x[2] not in FOOD_GOODS and x[2] not in FUEL_GOODS):
            continue
        by_good.setdefault(x[2], []).append(x)
    home = f.get("home", {}).get(str(h), {})
    unmet = f.get("unmet", {}).get(str(h), {})

    def rows(goods):
        out = []
        for g in goods:
            xs = sorted(by_good.get(g, []), key=lambda x: -x[3])
            tot = float(sum(x[3] for x in xs))
            if tot < SHOW_MIN:
                continue
            givers = []
            for x in xs:
                if x[3] < SHOW_MIN or len(givers) >= GIVERS_TOP:
                    break
                nm, pn = _name(doc, ctx, int(x[0]))
                what = None
                need = TR.CROPS.get(g)
                if need:
                    gc = _giver_crops(ctx, int(f["frame"]), fera, int(x[0]), crops_of)
                    what = [CROP_WHAT[k] for k in _ranked(gc, need)[:WHAT_TOP]] or None
                givers.append({"culture": int(x[0]), "name": nm, "people": pn, "share": round(float(x[3]), 3), "km": int(x[5]),
                               "road": road(x[7], g, x[8]), "mode": x[7], "kind": x[8], "via": x[9], "what": what,
                               "crops": _ranked(_giver_crops(ctx, int(f["frame"]), fera, int(x[0]), crops_of), TR.CROPS.get(g) or ())})
            out.append({"good": g, "label": FOOD_LABEL.get(g, TR.GOODS[g][0]), "share": round(min(1.0, tot), 3),
                        "unmet": round(float(unmet.get(g, 0.0)), 3), "home": round(float(home.get(g, 0.0)), 3), "givers": givers})
        out.sort(key=lambda r: -r["share"])
        return out

    foods, fuel = rows(FOOD_GOODS), rows(FUEL_GOODS)
    flown, carries = [], []
    for r in f.get("flyer_foods") or []:
        for t, cells in r.get("to") or []:
            if int(t) == h:
                nm, pn = _name(doc, ctx, int(r["culture"]))
                flown.append({"crop": r["crop"], "from": r.get("from"), "by": int(r["culture"]), "by_name": nm, "by_people": pn, "cells": int(cells)})
        if int(r["culture"]) == h:
            carries.append({"crop": r["crop"], "from": r.get("from"), "to": [_name(doc, ctx, int(t))[0] for t, _ in (r.get("to") or [])][:3]})
    out = {"ago_kyr": f["ago_kyr"], "frame": int(f["frame"]), "as": int(h), "foods": foods, "fuel": fuel, "flown_in": flown, "carries": carries}
    out["text"] = line(ctx, out)
    out["basis"] = ("the exchange (trade_flow.py, read after the run): each food reaching this culture from another, the share of its people "
                    "whose want of it that giver meets (not a share of the diet), km along the way the goods took, the way that carried most "
                    "of those km, and the kind of exchange; the giver's own fields name a crop good")
    return out


def _crop_label(ctx, sid: str) -> str:
    return ((ctx.meta.get("crops") or {}).get("stocks") or {}).get(sid, {}).get("label", sid.replace("_", " ")) if ctx is not None else sid


def _and(xs) -> str:
    xs = list(dict.fromkeys(xs))
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1] if xs else ""


def giver_text(g: dict) -> str:
    """'the dwarves of X (600 km by river, 35%)' for one giver of one food: how far, by what road, through whom, and the share of the
    taker's people it supplies."""
    rd = g["road"]
    far = "on the same land" if rd == "local" or g["km"] <= 0 else f"{g['km']:,} km" + ("" if rd == "tribute" else f" {ROAD[rd]}")
    via = f", through its {g['via']}" if g.get("via") else ""
    return f"{g['name']} ({far}{via}, {round(100 * g['share'])}%)"


def _what(fd: dict, givers: list) -> str:
    return _and(w for g in givers for w in (g.get("what") or [])) or fd["label"]


def _split(fd: dict) -> tuple[list, list]:
    """(bought, taken): a food's givers split into trade and tribute."""
    return [g for g in fd["givers"] if g["road"] != "tribute"], [g for g in fd["givers"] if g["road"] == "tribute"]


def line(ctx, r: dict) -> str:
    """The cuisine sheet's "Bought in" line: per food (most people supplied first) its main givers, how far and by what road; then what
    it takes as tribute, and the crops flyers bring. Percentages: of the culture's people that giver supplies."""
    bought, taken = [], []
    for fd in r["foods"][:FOODS_TOP]:
        b, t = _split(fd)
        if b:
            x = f"{_what(fd, b)} from {_and(giver_text(g) for g in b[:2])}"
            if fd["unmet"] >= NOTE_MIN:
                x += f", {round(100 * fd['unmet'])}% go without"
            bought.append(x)
        if t:
            taken.append(f"{_what(fd, t)} from {_and(giver_text(g) for g in t[:2])}")
    parts = bought + (["takes as tribute " + "; ".join(taken)] if taken else [])
    for fl in r["flown_in"][:2]:
        parts.append(f"{_crop_label(ctx, fl['crop'])} (not grown here), flown in by {fl['by_name']}")
    if not parts:
        return "nothing: it eats what its own land gives" + (" (its flyers carry " + _and(_crop_label(ctx, x["crop"]) for x in r["carries"][:3]) + " to others)" if r["carries"] else "")
    return "; ".join(parts) + " (%: of its people supplied)"


def _big(r: dict | None, goods, key: str = "foods") -> list:
    return [fd for fd in (r or {}).get(key, []) if fd["good"] in goods and fd["share"] >= NOTE_MIN and fd["givers"]]


def staple_note(r: dict | None) -> str | None:
    """Grain, salt fish and herd animals bought in or taken (herders' grain, inland salt fish): a note for the staple line."""
    out = []
    for fd in _big(r, ("grain", "dried_fish", "livestock")):
        b, t = _split(fd)
        if b:
            out.append(f"{fd['label']} bought in from {giver_text(b[0])}")
        if t:
            out.append(f"{fd['label']} taken as tribute from {giver_text(t[0])}")
    return "; ".join(out) or None


def drink_note(r: dict | None, grown: set) -> list:
    """Wine, date and palm wine, tea and cacao bought in where the culture does not grow that crop itself: the giver's fields name it."""
    out = []
    for fd in _big(r, ("oil_wine", "spices")):
        for g in fd["givers"]:
            for k in g.get("crops") or ():
                if k in DRINKS and k not in grown and g["share"] >= SHOW_MIN:
                    out.append(f"{DRINKS[k]} bought in from {giver_text(g)}")
    return list(dict.fromkeys(out))[:2]


def fuel_note(r: dict | None) -> str | None:
    xs = _big(r, FUEL_GOODS, "fuel")
    if not xs:
        return None
    return "firewood and charcoal bought in from " + giver_text(xs[0]["givers"][0])


def region(ctx, doc: dict | None, cultures: list | None, era: float, top: int = 3) -> dict | None:
    """A region's or a people's brief: the bought-in foods of its largest cultures (brief["cultures"], most land first)."""
    if doc is None or not cultures:
        return None
    rows = []
    for x in cultures[:top]:
        r = of_culture(ctx, doc, int(x["id"]), era)
        if r is not None:
            rows.append({"culture": int(x["id"]), "name": x["name"], "text": r["text"], "foods": r["foods"]})
    return {"cultures": rows, "basis": "per culture, its cuisine sheet's Bought in line (bought_in.py)"} if rows else None
