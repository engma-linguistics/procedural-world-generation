"""A culture's kitchen through time (PW-1714, under the culinary ethnography PW-692): what entered and left its diet and when, read
after the run from the history's own steps, read-only.

    epochs(ctx, c, era)                -> [{ago_kyr, crops, herds, ways, fuel, dairy, bought, methods, kept, flavour, top, descriptor}]
    events(epochs, known, born, ...)   -> [{ago_kyr, kind, text}] (pure: no run needed)
    timeline(ctx, c, era, now=None)    -> {"epochs", "events", "lines", "flavour_axes", "basis"}

In plain words: the cuisine sheet (cuisine.py, keeping.py) says what a culture eats at one moment. A culinary book is historical: what a
people cooked before the plough, after the goat, once pepper came up the river. This module walks the culture's own life through the
run's stored frames (every frame from its founding to the era asked for; inside the land-use window, the last ~12.5 kyr, a frame each
500 years) and, at each, reads the same things the sheet reads on that frame's land:
  - crops and herds known on the culture's land (the frame's crop_known / animal_known layers, cuisine.profile), with who tamed each or
    whom its people took it from (meta.techtree.known: tech crop_<id> / animal_<id>, its date, how and from whom);
  - its ways of life (farm, herd, wild shares of heads), its lead fuel and its dairy;
  - the ways of keeping food its people knows, dated by the tech that opens each (keeping.METHODS; techtree.known, a people-wide date);
  - what it buys in (the exchange, bought_in.of_culture, inside its window);
  - and its flavour profile (keeping.of on that frame's land, salt, fish, fuels and bought-in food).
Then it lists the changes: an item arrives when it is there on two frames in a row (or on the last), and leaves when it is gone on two in
a row, so a crop flickering at the edge of the 10%-of-cells cut-off is not reported in and out every frame. Every line comes from the
run; nothing is invented. Dates are the frame's (or the tech's own) and read in the culture's calendar where one is chosen (years.py).
"""

from __future__ import annotations

import numpy as np

from .years import years_ago

VERSION = 1
WAY_MIN = 0.10  # (cuisine.WAY_MIN) a way of life counts from this share of the culture's heads
HOLD_SLOW = 3  # JUDGEMENT: the lead fuel and the leading tastes flip at near-ties, so a change there must hold three frames running
MAX_EPOCHS = 60  # JUDGEMENT: at most this many frames are read per culture (evenly thinned, the founding and the era always kept)
FOUNDING_LINE_TOP = 4  # crops, herds and methods named in the founding line


# -- what the culture had at each frame -----------------------------------------------------------------------------------------
def _frames(ctx, c: int, era: float) -> list:
    """(frame, kyr ago) from the culture's founding to the era, oldest first."""
    rec = ctx.cultures()["cultures"][c]
    born = float(rec["born_kyr"])
    out = [(i, round(-float(t), 3) + 0.0) for i, t in enumerate(ctx.ts) if era - 1e-9 <= -float(t) <= born + 1e-9]
    out.sort(key=lambda x: -x[1])
    if len(out) > MAX_EPOCHS:
        keep = sorted(set(np.linspace(0, len(out) - 1, MAX_EPOCHS).round().astype(int).tolist()))
        out = [out[k] for k in keep]
    return out


def _mini_brief(ctx, i: int, era: float, mask: np.ndarray, c: int) -> dict:
    """The parts of a culture's brief keeping.py reads, on frame i's land (brief.build's own readers; no mining or peoples: cheap)."""
    from . import brief as BR
    from ..geo import is_land
    elev = ctx.f("elevation", i).astype(float)
    land_all = is_land(elev, ctx.f("ice", i).astype(float) > 0.5)
    land, sea = mask & land_all, mask & ~land_all
    out = {"land": BR._land(ctx, i, land, mask), "salt": BR._salt(ctx, land, i), "fish": BR._fish(ctx, i, mask, sea, land),
           "fuels": BR._fuels(ctx, land, era, i), "mining": None}
    tf = ctx.trade_flows() if hasattr(ctx, "trade_flows") else None
    if tf is not None:
        from . import bought_in as BI
        out["trade_reach"] = BI.of_culture(ctx, tf, c, era)
    return out


def _state(p: dict, kp: dict, bought: dict) -> dict:
    """One frame's kitchen, compact."""
    fl, pr = kp["flavour"], kp["preservation"]
    w = p.get("ways") or {}
    return {"crops": sorted(p.get("crops") or {}), "herds": sorted(p.get("herds") or {}),
            "ways": {k: round(float(w.get(k) or 0.0), 2) for k in ("farm", "herd", "forage")}, "fuel": p.get("fuel"),
            "dairy": bool(p.get("dairy")), "cheese": bool((p.get("dairy") or {}).get("cheese")),
            "bought": {g: r["share"] for g, r in bought.items()}, "bought_label": {g: _bought_text(r) for g, r in bought.items()},
            "methods": [m["id"] for m in pr["methods"]], "kept": pr["preserved_share"],
            "flavour": {a: v["value"] for a, v in fl["axes"].items()}, "top": fl["top"], "descriptor": fl["descriptor"]}


def _bought_text(r: dict) -> str:
    what = ", ".join(r.get("what") or []) or r["label"]
    return what + (f" (from {' and '.join(r['from'])})" if r.get("from") else "")


def epochs(ctx, c: int, era: float, now: dict | None = None) -> list:
    """The culture's kitchen at each of its frames, oldest first. `now`: the sheet's own keeping at the era (so the last epoch agrees
    with the sheet above it, which also reads the salt mines)."""
    from . import cuisine as CZ
    from . import keeping as KP
    out = []
    fr = _frames(ctx, c, era)
    for k, (i, e) in enumerate(fr):
        mask = CZ.mask_of(ctx, i, e, c)
        if not mask.any():
            continue
        p = CZ.profile(ctx, i, e, c, mask)
        b = _mini_brief(ctx, i, e, mask, c)
        kp = now if (now is not None and k == len(fr) - 1) else KP.of(b, p)
        st = _state(p, kp, KP.bought_of(b.get("trade_reach")))
        st["ago_kyr"], st["cells"] = e, int(mask.sum())
        out.append(st)
    return out


# -- the changes -----------------------------------------------------------------------------------------------------------------
def _round_kyr(k: float) -> float:
    """A tech's own date, rounded for a readable line: to 100 years inside 10 kyr, to 500 beyond."""
    return round(k * 10) / 10 if k < 10 else round(k * 2) / 2


def _steady(series: list, hold: int = 2) -> list:
    """[(arrived, left)] per step of a series of sets: an item arrives when it is there on this step and the next hold-1 (as many as
    there are), leaves when it is gone on as many. The first step's items are the starting state."""
    out, have = [], set(series[0]) if series else set()
    for t in range(1, len(series)):
        ahead = series[t:t + hold]
        came = {x for x in series[t] if x not in have and all(x in a for a in ahead)}
        went = {x for x in have if all(x not in a for a in ahead)}
        have = (have | came) - went
        out.append((came, went))
    return out


def _how(known: dict, tech: str, names: dict, at: float | None = None) -> str:
    """Who gave the people a tech (people-wide: meta.techtree.known). `at`: when the item reached this culture's land; a crop or herd
    that was there before its people knew it was another people's on the same land."""
    v = known.get(tech)
    if not v or v[0] is None:
        return "another people's, on its land" if at is not None and tech.startswith(("crop_", "animal_")) else ""
    how, frm = v[1], v[2]
    k = float(v[0])
    if at is not None and k < at - 0.25:
        r = _round_kyr(k)
        return "another people's, on its land; its own people took it up " + (f"~{years_ago(r, calendar=False)}" if r > 0 else "only at the present")
    if how == "tamed":
        return f"its people had tamed it ~{years_ago(_round_kyr(k), calendar=False)}"
    if how == "contact" and frm:
        return f"taken up from {names.get(frm, frm)}"
    if how == "invented":
        return "worked out by its own people"
    if how == "inherited" and frm:
        return f"inherited from {names.get(frm, frm)}"
    return ""


def _and(xs: list) -> str:
    xs = [x for x in xs if x]
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1] if xs else ""


def events(ep: list, known: dict, born: float, label=lambda kind, x: x.replace("_", " "), names: dict | None = None,
           method_techs: dict | None = None, tree: set | None = None) -> list:
    """What entered and left the culture's kitchen, oldest first: [{ago_kyr, kind, text}]. `known` is its people's meta.techtree.known
    (tech -> [kyr ago, how, from]); `method_techs` keeping method -> (label, techs); `tree` the run's tech ids (None: no gate)."""
    names = names or {}
    ev: list = []
    if not ep:
        return ev
    for key, kind in (("crops", "crop"), ("herds", "herd"), ("bought", "bought")):
        ser = [set(e[key]) for e in ep]
        for e, (came, went) in zip(ep[1:], _steady(ser)):
            for x in sorted(came):
                if kind == "bought":
                    ev.append({"ago_kyr": e["ago_kyr"], "kind": "bought", "item": x, "text": f"{e['bought_label'].get(x, x)} bought in"})
                    continue
                why = _how(known, ("crop_" if kind == "crop" else "animal_") + x, names, e["ago_kyr"])
                nm = label(kind, x) + (f" ({why})" if why else "")
                ev.append({"ago_kyr": e["ago_kyr"], "kind": kind, "item": x, "name": nm, "text": f"{nm} arrives"})
            for x in sorted(went):
                ev.append({"ago_kyr": e["ago_kyr"], "kind": kind + "_lost", "item": x,
                           "text": (f"{label('bought', x)} no longer bought in" if kind == "bought" else
                                    f"{label(kind, x)} no longer grown" if kind == "crop" else f"{label(kind, x)} no longer kept")})
    for way, word in (("farm", "farming"), ("herd", "herding")):
        ser = [{way} if e["ways"][way] >= WAY_MIN else set() for e in ep]
        for e, (came, went) in zip(ep[1:], _steady(ser)):
            if came:
                ev.append({"ago_kyr": e["ago_kyr"], "kind": "way", "item": way, "text": f"takes up {word} ({round(100 * e['ways'][way])}% of its people)"})
            if went:
                ev.append({"ago_kyr": e["ago_kyr"], "kind": "way_lost", "item": way, "text": f"gives up {word}"})
    ser = [{e["fuel"]} if e["fuel"] else set() for e in ep]
    was = ep[0]["fuel"]
    for e, (came, _) in zip(ep[1:], _steady(ser, HOLD_SLOW)):
        if came:
            ev.append({"ago_kyr": e["ago_kyr"], "kind": "fuel", "item": e["fuel"], "text": f"cooks mostly on {e['fuel']}" + (f" (was {was})" if was else "")})
            was = e["fuel"]
    ser = [({"dairy"} if e["dairy"] else set()) | ({"cheese"} if e["cheese"] else set()) for e in ep]
    for e, (came, _) in zip(ep[1:], _steady(ser)):
        if "dairy" in came:
            ev.append({"ago_kyr": e["ago_kyr"], "kind": "dairy", "item": "dairy", "text": "milks its herds"})
        if "cheese" in came:
            ev.append({"ago_kyr": e["ago_kyr"], "kind": "dairy", "item": "cheese", "text": "makes cheese"})
    # keeping methods: dated by the people's own tech date (people-wide), not by the frame
    end = ep[-1]["ago_kyr"]
    for mid, (lab, techs) in (method_techs or {}).items():
        if tree is not None and not any(t in tree for t in techs):
            continue  # (a tree without the tech does not gate the method: nothing to date)
        have = [(float(known[t][0]), t) for t in techs if known.get(t) and known[t][0] is not None]
        if not have:
            continue
        k, t = max(have)
        if k >= born - 1e-9 or k < end - 1e-9:
            continue  # (known at its founding: the founding line says so; or after the era asked for)
        why = _how(known, t, names)
        ev.append({"ago_kyr": _round_kyr(k), "kind": "keeping", "item": mid, "text": f"{lab.split(' (')[0]} known" + (f" ({why})" if why else "")})
    # flavour: the two leading tastes changing (as a set: a swap of first and second is no change), steadily
    ser = [frozenset(e["top"][:2]) for e in ep]
    last = ep[0]
    for e, (came, _) in zip(ep[1:], _steady([{x} for x in ser], HOLD_SLOW)):
        if came:
            ev.append({"ago_kyr": e["ago_kyr"], "kind": "flavour", "item": "+".join(sorted(next(iter(came)))),
                       "text": f"the kitchen turns {_tastes(e['top'])}" + (f" (was {_tastes(last['top'])})" if last["top"] else "")})
            last = e
    ev.sort(key=lambda r: (-r["ago_kyr"], _ORDER.get(r["kind"], 9)))
    return ev


def _tastes(top: list) -> str:
    from .keeping import SHORT
    return _and([SHORT.get(a, a) for a in top[:2]]) or "plain"


_ORDER = {"way": 0, "crop": 1, "herd": 2, "dairy": 3, "keeping": 4, "bought": 5, "fuel": 6, "crop_lost": 7, "herd_lost": 7, "bought_lost": 7,
          "way_lost": 7, "flavour": 8}


def founding(ep: list, born: float, known: dict, method_techs: dict, label) -> str:
    """The first line: what the culture ate and how it kept food when it began (or at the first frame it held land)."""
    e = ep[0]
    w = e["ways"]
    way = max(("farm", "herd", "forage"), key=lambda k: w[k])
    s = {"farm": "farmers", "herd": "herders", "forage": "foragers"}[way]
    bits = [s]
    if e["crops"]:
        bits.append("growing " + _and([label("crop", x) for x in e["crops"][:FOUNDING_LINE_TOP]]))
    if e["herds"]:
        bits.append("keeping " + _and([label("herd", x) for x in e["herds"][:FOUNDING_LINE_TOP]]))
    kn = [method_techs[m][0].split(" (")[0] for m in e["methods"][:FOUNDING_LINE_TOP] if m in method_techs]
    bits.append("keeping food by " + _and(kn) if kn else "eating its food fresh")
    return f"{s.capitalize()}" + ("; " + "; ".join(bits[1:]) if len(bits) > 1 else "") + f"; the kitchen {e['descriptor'].split(':')[0]}"


def lines(ep: list, ev: list, born: float, known: dict, method_techs: dict, label) -> list:
    """[{ago_kyr, when, text}]: the founding line, then the events grouped by date ("~4,000 years ago: wheat arrive; salting known")."""
    if not ep:
        return []
    out = [{"ago_kyr": ep[0]["ago_kyr"], "when": years_ago(ep[0]["ago_kyr"]), "text": "founded: " + founding(ep, born, known, method_techs, label)
            if abs(ep[0]["ago_kyr"] - born) < 1.0 else "first seen: " + founding(ep, born, known, method_techs, label)}]
    by: dict = {}
    for r in ev:
        by.setdefault(r["ago_kyr"], []).append(r)
    for k in sorted(by, reverse=True):
        rs = by[k]
        new = [r["name"] for r in rs if r["kind"] in ("crop", "herd")]
        txt = ([_and(new) + (" arrive" if len(new) > 1 else " arrives")] if new else []) + [r["text"] for r in rs if r["kind"] not in ("crop", "herd")]
        out.append({"ago_kyr": k, "when": years_ago(k), "text": "; ".join(txt)})
    return out


def timeline(ctx, c: int, era: float, now: dict | None = None) -> dict:
    """The culture's kitchen through time, from its founding to the era: {epochs, events, lines, flavour_axes, basis}."""
    from . import cuisine as CZ
    from . import keeping as KP
    rec = ctx.cultures()["cultures"][c]
    pid = rec["people"]
    known = ((ctx.meta.get("techtree") or {}).get("known") or {}).get(pid) or {}
    names = {l["id"]: (l.get("name") or l["id"]).split(" (")[0] for l in ctx.lines}
    tree = CZ._tree_techs(ctx)
    mt = {m[0]: (m[1], m[2]) for m in KP.METHODS}

    def label(kind, x):
        if kind == "crop":
            return CZ._label(ctx, "crops", x)
        if kind == "herd":
            return CZ._label(ctx, "animals", x)
        if kind == "bought":
            from .bought_in import FOOD_LABEL
            return FOOD_LABEL.get(x, x.replace("_", " "))
        return x.replace("_", " ")

    ep = epochs(ctx, c, era, now)
    ev = events(ep, known, float(rec["born_kyr"]), label, names, mt, tree)
    return {"version": VERSION, "culture": c, "born_kyr": rec["born_kyr"], "epochs": ep, "events": ev,
            "lines": lines(ep, ev, float(rec["born_kyr"]), known, mt, label), "flavour_axes": list(KP.AXES),
            "basis": "read from this run's stored frames from the culture's founding to this era (crops and herds known on its land, its ways of "
                     "life, fuel, dairy and bought-in food at each frame; keeping methods dated by its people's tech dates, meta.techtree.known; the "
                     "flavour by keeping.py on each frame's land). An item arrives when there on two frames running, leaves when gone on two."}


def markdown(t: dict | None) -> list:
    if not t or not t.get("lines"):
        return []
    out = ["- Kitchen through time:"]
    out += [f"  - {r['when']}: {r['text']}" for r in t["lines"]]
    return out
