"""The settlement view (PW-1659) and the trade goods map (PW-1508): read-outs for the viewer, from what a peoples run already holds.

In plain words: clicking a town on the globe opens a card with everything the run knows about that place at the slider's moment: its
name, its people (size, the peoples living there and their shares, who founded it, who held it since, wars and walls, the ruins under
it), its goods (what its own cell makes beyond its want and what it lacks, its culture's "has / lacks" line, the brief's "Bought in" line,
and the goods passing through when it is a trading town), who rules it (the polity holding its cell), the faith(s) held there, the
tongues spoken, and a short history. And a trade goods map: pick a good, see per cell where it is spare (surplus) and where it is
lacking, at the land-use frame nearest the slider.

Nothing is recomputed here that is stored or already derived: the place is settlements.json's record; the goods are trade.py's per
(cell, culture) pairs (pairs_at, the numbers its ledger sums to cultures); the rule is the polities doc's century map; the faith is the
gods doc's per-culture faith timeline; the bought-in foods are bought_in.py over the exchange doc; the trading town is trade_routes'
frame view; the tongues are the tongues ledger. Read after the run (D63 A): it changes no run file. Each part is None where the run
lacks its source (a run without a land-use window has no goods), and the viewer hides empty sections.
"""

from __future__ import annotations

import numpy as np

VERSION = 1
TOP_GOODS = 6  # JUDGEMENT (display): goods named per side in the town's own goods
GOOD_MIN = 0.02  # JUDGEMENT (display): a cell's surplus or lack of a good under 2% of its people is not named (trade.SHOW_MIN's cut)
HISTORY_MAX = 40  # JUDGEMENT (display): the history's lines, newest last


# ------------------------------------------------------------------ the place itself (settlements.json; the viewer's settlements.js rules)

def pop_at(s: dict, ago: float) -> float:
    """The site's people at `ago` kyr (its series, newest last); 0 before its founding or after it was left (settlements.js popAt)."""
    if ago > s["founded_kyr"] + 1e-6 or (s.get("abandoned_kyr") is not None and ago <= s["abandoned_kyr"] + 1e-6):
        return 0.0
    sr = s["series"]
    for k in range(1, len(sr)):
        if sr[k][0] <= ago:
            a0, p0 = sr[k - 1]
            a1, p1 = sr[k]
            w = 1.0 if a0 == a1 else (a0 - ago) / (a0 - a1)
            return p0 + (p1 - p0) * w
    return float(sr[-1][1])


def tier_at(s: dict, tiers: dict, ago: float) -> str:
    """village / town / city at `ago` (the holder's techs set the town's size: the site's bands, PW-1114), or the site's own kind
    (mine, pit), or 'ruin' / 'gone' once left."""
    if s.get("abandoned_kyr") is not None and ago <= s["abandoned_kyr"] + 1e-6:
        return "ruin" if s.get("tier_now") == "ruin" else "gone"
    if s["kind"] in ("mine", "pit"):
        return s["kind"]
    tm = tiers["town_min_by_stage"][-1]
    for b in s.get("bands") or []:
        if b[0] >= ago - 1e-6:
            tm = b[1]
    p = pop_at(s, ago)
    return "city" if p >= tiers["city_min"] else "town" if p >= tm else "village"


def holder_at(s: dict, ago: float) -> str:
    h = s["founded_by"]
    for a, p in s.get("holders") or []:
        if a >= ago - 1e-6:
            h = p
    return h


def place_part(s: dict, sites: list, tiers: dict, ago: float) -> dict:
    """The names and the people of the place: tier, people now, peak, its peoples' shares, founding, holders, wars, walls, ruins under it."""
    by_id = {x["id"]: x for x in sites} if isinstance(sites, list) else sites
    older, k = [], s.get("ruin_of")
    while k is not None and k in by_id and len(older) < 8:  # (the ruins under it, the newest first)
        o = by_id[k]
        older.append({"site": o["id"], "place": o.get("place"), "tier_peak": o.get("tier_peak"), "founded_kyr": o["founded_kyr"],
                      "abandoned_kyr": o.get("abandoned_kyr"), "why": o.get("why"), "by": o["founded_by"]})
        k = o.get("ruin_of")
    nxt = by_id.get(s.get("resettled_as")) if s.get("resettled_as") is not None else None
    hands = [[a, p] for a, p in (s.get("holders") or []) if a >= ago - 1e-6]
    return {"site": s["id"], "kind": s["kind"], "cell": s["cell"], "lat": s["lat"], "lon": s["lon"], "name": s.get("place"),
            "tier": tier_at(s, tiers, ago), "tier_peak": s.get("tier_peak"), "people": round(pop_at(s, ago)),
            "peak_pop": s.get("peak_pop"), "peak_kyr": s.get("peak_kyr"), "series": [x for x in s["series"] if x[0] >= ago - 1e-6],
            "founded_kyr": s["founded_kyr"], "founded_by": s["founded_by"], "holder": holder_at(s, ago), "holders": hands,
            "who": s.get("who") or {}, "who_when": s.get("who_when"), "abandoned_kyr": s.get("abandoned_kyr"), "why": s.get("why"),
            "war": [w for w in (s.get("war") or []) if w[0] >= ago - 1e-6],
            "walled_kyr": s.get("walled_kyr") if s.get("walled_kyr") is not None and s["walled_kyr"] >= ago - 1e-6 else None,
            "district": s.get("district"), "colony": s.get("colony"), "ruins_under": older,
            "resettled_as": None if nxt is None else {"site": nxt["id"], "place": nxt.get("place"), "founded_kyr": nxt["founded_kyr"]}}


# ------------------------------------------------------------------ goods: trade.py's per (cell, culture) pairs

def cell_goods(pairs: dict | None, cell: int, labels: dict) -> dict | None:
    """The cell's own goods at the pairs' frame: per good the mean over its (cell, culture) pairs of the share of the cell's people who
    make it beyond their want (spare) and who want it and lack it at home (lacking). {"spare": [[good, label, 0..1]], "lacking": [...]}"""
    if pairs is None:
        return None
    m = np.asarray(pairs["cell"]) == cell
    if not m.any():
        return {"spare": [], "lacking": []}
    out = {}
    for side, key in (("spare", "surplus"), ("lacking", "lack")):
        v = {g: float(np.asarray(a)[m].mean()) for g, a in pairs[key].items() if len(a)}
        out[side] = [[g, labels.get(g, g), round(x, 3)] for g, x in sorted(v.items(), key=lambda t: -t[1]) if x >= GOOD_MIN][:TOP_GOODS]
    return out


def good_map(pairs: dict | None, good: str, n: int) -> dict | None:
    """One good on every peopled cell at the pairs' frame (PW-1508): {"cells", "spare", "lacking"} with spare and lacking in % of the
    cell's people (the mean over the cell's (cell, culture) pairs, as cell_goods). Cells with no people are left out."""
    if pairs is None:
        return None
    cell = np.asarray(pairs["cell"], np.int64)
    if good not in pairs["surplus"]:
        raise ValueError(f"no good {good!r}")
    cnt = np.bincount(cell, minlength=n)
    sur = np.bincount(cell, weights=np.asarray(pairs["surplus"][good], float), minlength=n)
    lk = np.asarray(pairs["lack"].get(good, np.zeros(len(cell))), float)
    lack = np.bincount(cell, weights=lk if len(lk) == len(cell) else np.zeros(len(cell)), minlength=n)
    keep = np.flatnonzero(cnt > 0)
    c = np.maximum(cnt[keep], 1)
    return {"cells": keep.tolist(), "spare": np.round(100 * sur[keep] / c).astype(int).tolist(),
            "lacking": np.round(100 * lack[keep] / c).astype(int).tolist()}


def eraq_frame(meta: dict, ago: float) -> int | None:
    """The land-use window's frame nearest `ago` kyr (meta.eraq), None without a window."""
    eq = meta.get("eraq")
    if not eq or not eq.get("frames"):
        return None
    k = min(range(len(eq["frames"])), key=lambda j: abs(abs(float(eq["ago_kyr"][j])) - ago))
    return int(eq["frames"][k])


# ------------------------------------------------------------------ rule: the polities doc's century maps

def owner_table(doc: dict, n: int) -> np.ndarray:
    """(steps, cells) polity id ruling each cell at each century step, -1 none (int32; built once per doc)."""
    from .polities import _unpack
    T = np.full((len(doc["maps"]), n), -1, np.int32)
    for k, m in enumerate(doc["maps"]):
        for e in m:
            T[k, _unpack(e[2])] = e[0]
    return T


def _span(sp: list, ago: float):
    out = sp[0] if sp else None
    for s in sp or []:
        if s[0] >= ago - 1e-6:
            out = s
    return out


def rule_part(doc: dict | None, names: dict | None, owners: np.ndarray | None, cell: int, ago: float) -> dict | None:
    """Who rules the cell at the century step nearest `ago`, and every polity that held it in the window (oldest first)."""
    if doc is None or owners is None or not doc.get("steps"):
        return None
    st = doc["steps"]
    k = min(range(len(st)), key=lambda i: (abs(st[i]["ago"] - ago), st[i]["ago"]))
    P = (names or doc)["polities"]
    C = (names or doc).get("cultures") or {}

    def card(pid: int, at: float) -> dict:
        r = P[pid]
        ruler = _span(r.get("rulers"), at)
        tier = _span(r.get("tiers"), at)
        return {"id": pid, "name": (_span(r.get("names"), at) or [None, r.get("name")])[1], "tier": tier[1] if tier else r.get("tier_peak"),
                "kind": r.get("kind"), "people": r.get("people_name") or r.get("people"),
                "ruler": (C.get(ruler[1]) or {}).get("name", ruler[1]) if ruler else None, "founded_kyr": r.get("founded_kyr"),
                "fell_kyr": r.get("fell_kyr"), "fell_why": r.get("fell_why"), "capital": (r.get("capital") or {}).get("cell") == cell,
                "capital_place": (r.get("capital") or {}).get("place"), "color": r.get("color")}
    now = int(owners[k, cell])
    spans, last = [], None
    order = sorted(range(len(st)), key=lambda i: -st[i]["ago"])
    for j in order:
        if st[j]["ago"] < ago - 1e-6:
            break
        o = int(owners[j, cell])
        if o != last:
            spans.append([st[j]["ago"], o])
            last = o
    return {"ago": st[k]["ago"], "now": card(now, st[k]["ago"]) if now >= 0 else None,
            "past": [[a, card(o, a) if o >= 0 else None] for a, o in spans]}


# ------------------------------------------------------------------ faith: the gods doc's per-culture faiths

def faith_part(gods: dict | None, cultures: list[int], ago: float, cnames: dict) -> dict | None:
    """The faith of each culture living in the cell at `ago`, and its changes (gods doc: cultures[c].faiths, [[kyr ago, faith]])."""
    if gods is None or not cultures:
        return None
    from .faithmap import faith_of_culture
    fl = {f["id"]: f for f in ((gods.get("faiths") or {}).get("list") or [])}
    fc = faith_of_culture(gods, ago)
    held, changes = {}, []
    for c in cultures:
        f = fc.get(c)
        if f is not None:
            held.setdefault(f, []).append(c)
        for a, fid in (gods.get("cultures") or {}).get(str(c), {}).get("faiths") or []:
            if a >= ago - 1e-6:
                changes.append([a, c, cnames.get(c, str(c)), fid, (fl.get(fid) or {}).get("name", str(fid))])
    rows = [{"faith": f, "name": (fl.get(f) or {}).get("name", str(f)), "core": (fl.get(f) or {}).get("core"),
             "color": (fl.get(f) or {}).get("color"), "missionary": (fl.get(f) or {}).get("missionary"),
             "founded_kyr": (fl.get(f) or {}).get("founded_kyr"), "cultures": [[c, cnames.get(c, str(c))] for c in cs]} for f, cs in held.items()]
    return {"held": rows, "changes": sorted(changes, key=lambda x: -x[0])} if rows or changes else None


# ------------------------------------------------------------------ language: the tongues ledger

def tongue_part(tongues: dict | None, cultures: list[int], site: int, ago: float, cnames: dict) -> dict | None:
    """Each culture's own tongue, the other tongues some of its people speak (the tongues ledger's era nearest `ago`), and the trade
    language of the town's network when the town is one of its trading towns."""
    own = [[c, cnames.get(c, str(c))] for c in cultures]
    if tongues is None or not tongues.get("frames"):
        return {"own": own, "others": [], "trade": []} if own else None
    from .tongues import COLUMNS
    f = min(tongues["frames"], key=lambda f: abs(f["ago_kyr"] - ago))
    nm = lambda k: tongues["cultures"][k]["name"] if isinstance(k, int) and 0 <= k < len(tongues["cultures"]) else str(k)  # noqa: E731
    others = []
    for c in cultures:
        for x in f["cultures"].get(str(c)) or []:
            r = dict(zip(COLUMNS, x))
            others.append({"culture": c, "culture_name": cnames.get(c, str(c)), "tongue": r["tongue"], "name": nm(r["tongue"]), "kind": r["kind"],
                           "share": r["share"], "lect": r.get("lect"), "language": r.get("language")})
    trade = [{"kind": t["kind"], "tongue": t["tongue"], "name": nm(t["tongue"]), "source": t.get("source"), "lect": t.get("lect"),
              "language": t.get("language"), "since_kyr": t.get("since_kyr"), "towns": len(t.get("towns") or [])}
             for t in f.get("trade_languages") or [] if site in (t.get("towns") or [])]
    return {"ago_kyr": f["ago_kyr"], "own": own, "others": others, "trade": trade}


# ------------------------------------------------------------------ history: one list, newest last

def history(place: dict, rule: dict | None, faith: dict | None, name) -> list:
    """[[kyr ago, text]] oldest first: founding, ruins under it, changes of hands, wars, walls, rulers, faith changes, abandonment."""
    H = []
    for o in reversed(place["ruins_under"]):
        H.append([o["founded_kyr"], f"an older {o['tier_peak'] or 'place'} of the {name(o['by'])} founded here"])
        if o.get("abandoned_kyr") is not None:
            H.append([o["abandoned_kyr"], f"that older place abandoned: {o.get('why') or 'left'}"])
    H.append([place["founded_kyr"], f"founded by the {name(place['founded_by'])}" + (" on older ruins" if place["ruins_under"] else "")])
    for a, p in place["holders"][1:]:
        H.append([a, f"passed to the {name(p)}"])
    for w in place["war"]:
        H.append([w[0], f"{w[1]} by the {name(w[2])}"])
    if place["walled_kyr"] is not None:
        H.append([place["walled_kyr"], "walled"])
    if place["peak_kyr"] is not None and place["peak_pop"] and place["peak_kyr"] >= (place["series"][-1][0] if place["series"] else 0) - 1e-6:
        H.append([place["peak_kyr"], f"at its largest, ~{place['peak_pop']:,} people"])
    for a, card in (rule or {}).get("past") or []:
        H.append([a, f"ruled by {card['name']} ({card['tier']})" if card else "no state rules it"])
    for a, _c, cn, _f, fn in (faith or {}).get("changes") or []:
        H.append([a, f"{cn} hold {fn}"])
    if place["abandoned_kyr"] is not None and place["tier"] in ("ruin", "gone"):
        H.append([place["abandoned_kyr"], f"abandoned: {place['why'] or 'left'}"])
    start = max([place["founded_kyr"]] + [o["founded_kyr"] for o in place["ruins_under"]])  # (the oldest place on this spot)
    H = [h for h in H if h[0] <= start + 1e-6]  # (the cell's rulers and faiths before anyone lived here are not the town's history)
    H.sort(key=lambda x: -x[0])
    return [[round(a, 2), t] for a, t in H][-HISTORY_MAX:]


# ------------------------------------------------------------------ the server's side (the read-out layer: planet.server imported lazily,
# as readout.py does, so nothing the peoples' caches hash imports it)

_cache: dict = {}  # (run id, run.json mtime) -> {"ctx", "sites", "owners"}


def _run_state(d) -> dict:
    import json
    from . import readout as RO
    key = (d.name, (d / "run.json").stat().st_mtime)
    if key not in _cache:
        _cache.clear()
        meta = json.loads((d / "run.json").read_text()).get("meta") or {}
        sd = json.loads((d / meta["settlements"]["file"]).read_text()) if meta.get("settlements") else None
        _cache[key] = {"ctx": RO.Ctx(d.name), "meta": meta, "settle": sd, "by_id": {s["id"]: s for s in sd["sites"]} if sd else {}}
    return _cache[key]


def _try(f):
    try:
        return f()
    except Exception:  # noqa: BLE001  (a part the run cannot give: its section is hidden)
        return None


def build(d, site_id: int, ago: float) -> dict:
    """The settlement view of site `site_id` at `ago` kyr (GET /api/settlement): {"place", "goods", "rule", "faith", "tongues", "history"}."""
    from .. import server
    from . import bought_in as BI, cuisine as CZ, trade as TR, trade_routes as RT, polities as PO, nameslot as NS
    R = _run_state(d)
    if R["settle"] is None:
        raise ValueError("this run has no settlements")
    s = R["by_id"].get(site_id)
    if s is None:
        raise ValueError(f"no site {site_id} in this run")
    ctx, meta = R["ctx"], R["meta"]
    lines = {x["id"]: x for x in meta.get("lineages") or []}
    name = lambda p: (lines.get(p, {}).get("name") or str(p).replace("_", " ")).split(" (")[0]  # noqa: E731
    place = place_part(s, R["by_id"], R["settle"]["tiers"], ago)
    place["peoples"] = {p: name(p) for p in set(place["who"]) | {place["founded_by"], place["holder"]} | {h[1] for h in place["holders"]}
                        | {w[2] for w in place["war"]} | {o["by"] for o in place["ruins_under"]} if p != "others"}
    named = _try(lambda: server.named_cultures(d)["cultures"]) or []
    cnames = {k: c.get("name") for k, c in enumerate(named)}
    # the cultures in the cell at the stored frame nearest ago (one per people's deme there)
    cultures = []
    fi = ctx.frame_at(ago)
    cc = _try(lambda: CZ.culture_cells(ctx, fi, ago))
    if cc is not None:
        cultures = sorted({int(c) for c in np.asarray(cc[1])[np.asarray(cc[0]) == s["cell"]].tolist()})
    # the town's own cultures: those of the peoples living in it (its "who", and its holder); the cell's other cultures live around it
    inside = set(place["who"]) | {place["holder"]}
    town = [c for c in cultures if c < len(named) and named[c]["people"] in inside] or cultures
    cul = [{"culture": c, "in_town": c in town, "name": cnames.get(c, str(c)), "people": named[c]["people"] if c < len(named) else None,
            "people_name": name(named[c]["people"]) if c < len(named) else None} for c in cultures]
    # goods: the cell's own (trade.pairs_at), its cultures' has / lacks lines and bought-in foods, the trading town's goods passing
    goods = None
    ei = eraq_frame(meta, ago)
    if ei is not None and ctx.goods is not None:
        labels = {g: v[0] for g, v in TR.GOODS.items()}
        own = _try(lambda: cell_goods(TR.pairs_at(ctx, ei), s["cell"], labels))
        led = _try(lambda: TR.ledger_at(ctx, ei)) or {}
        eago = abs(float(meta["eraq"]["ago_kyr"][meta["eraq"]["frames"].index(ei)]))
        flow = _try(ctx.trade_flows)
        lines_ = []
        for c in town:
            row = led.get(c)
            bi = _try(lambda: BI.of_culture(ctx, flow, c, eago)) if flow else None
            lines_.append({"culture": c, "name": cnames.get(c, str(c)), "line": TR.line(row) if row else None,
                           "bought_in": _try(lambda: BI.line(ctx, bi)) if bi else None})
        hub = None
        if flow:
            fv = _try(lambda: RT.frame_view(flow, eago)) or {}
            h = next((x for x in fv.get("hubs") or [] if x.get("site") == s["id"] or x.get("cell") == s["cell"]), None)
            if h:
                hub = {"kind": h["kind"], "trading": bool(h.get("trading", h.get("long"))), "goods": [labels.get(g, g) for g in h["goods"]],
                       "modes": h["modes"], "culture_name": h.get("culture_name"), "quarters": [q[1] for q in h.get("quarters") or []],
                       "ago_kyr": fv.get("ago_kyr")}
        goods = {"ago_kyr": eago, "own": own, "cultures": lines_, "hub": hub}
    # rule
    pol = _try(lambda: server.polities_doc(d)) if meta.get("settlements") and meta.get("cultures") else None
    rule = None
    if pol is not None:
        if "owners" not in R:
            R["owners"] = owner_table(pol, ctx.g.n)
        nm = _try(lambda: NS.apply_polities(PO.summary(pol), server.languages_main(d), named))
        rule = _try(lambda: rule_part(pol, nm, R["owners"], s["cell"], ago))
    gods = _try(lambda: server.gods_doc(d))
    if gods is not None and named:
        gods = _try(lambda: NS.apply_faiths(gods, named)) or gods
    faith = _try(lambda: faith_part(gods, town, ago, cnames))
    tdoc = _try(lambda: server.tongues_doc(d)) if meta.get("eraq") and meta.get("world") else None
    tongues = _try(lambda: tongue_part(tdoc, town, s["id"], ago, cnames))
    same = [{"site": x["id"], "kind": x["kind"], "name": x.get("place"), "tier": tier_at(x, R["settle"]["tiers"], ago), "holder": name(holder_at(x, ago))}
            for x in R["by_id"].values() if x["cell"] == s["cell"] and x["id"] != s["id"] and x["founded_kyr"] >= ago - 1e-6]
    return {"version": VERSION, "ago_kyr": ago, "place": place, "cultures": cul, "goods": goods, "rule": rule, "faith": faith,
            "tongues": tongues, "history": history(place, rule, faith, name), "same_cell": same}


def api(query: str) -> tuple[dict, int]:
    """GET /api/settlement?run=<id>&site=<site id>&ago=<kyr ago>: the settlement view (PW-1659)."""
    from urllib.parse import parse_qsl
    from .. import store as S
    q = dict(parse_qsl(query))
    try:
        if not q.get("run") or q.get("site") in (None, ""):
            raise ValueError("run= and site= are required")
        return build(S.find_run(q["run"]), int(q["site"]), max(0.0, float(q.get("ago") or 0.0))), 200
    except ValueError as e:
        return {"error": str(e)}, 400
    except SystemExit as e:
        return {"error": str(e)}, 404
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}"}, 500


def good_view(d, good: str, ago: float) -> dict:
    """GET /api/trade?run=&good=&ago= (PW-1508): one good's spare and lacking per peopled cell at the land-use frame nearest ago."""
    from . import trade as TR
    R = _run_state(d)
    ctx, meta = R["ctx"], R["meta"]
    goods = {g: {"label": v[0], "class": v[1]} for g, v in TR.GOODS.items()}
    if good not in TR.GOODS:
        raise ValueError(f"good must be one of {', '.join(TR.GOODS)}")
    ei = eraq_frame(meta, ago)
    if ei is None or ctx.goods is None:
        raise ValueError("this run has no land-use window or no world: no goods")
    eago = abs(float(meta["eraq"]["ago_kyr"][meta["eraq"]["frames"].index(ei)]))
    return {"good": good, "label": goods[good]["label"], "frame": ei, "ago_kyr": eago, "goods": goods, **good_map(TR.pairs_at(ctx, ei), good, ctx.g.n)}
