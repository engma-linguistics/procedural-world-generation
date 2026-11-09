"""Tongues (PW-1526): the languages a people speaks besides its own, per culture and era; trade languages and pidgins.

In plain words: at every era of the land-use window (0.5 kyr apart) each culture gets a short list of the other tongues some of its people
speak, with roughly what share of its people speak each and why:
- a neighbour's tongue, spoken by the people living on the border with a bigger neighbour (bilingual borderlands);
- a ruler's tongue, spoken by a subject people's townsfolk at first and by more of its country the longer the rule lasts;
- a host's tongue, spoken by the merchants a trading culture keeps in another culture's town (a merchant quarter);
- a trade language: where trading towns of two or more cultures sit on one long-haul route network, one tongue serves them all. It is
  the ruling state's tongue when one state's peoples hold most of the network's trade, else the busiest trading culture's tongue when
  it holds a clear lead, else a pidgin built mostly on the busiest culture's words. It is spoken in the trading towns on the network and,
  more thinly, along its routes; once established it holds on after the trade or the state that made it has faded, until a much stronger
  tongue takes over (a pidgin gives way to the first real trade language that qualifies);
- a liturgy: the frozen sacred register of a faith whose canon the language pass fixed, spoken by the clergy of every culture that holds
  that faith (only when the run has a languages.json; the language module owns the canon).

The language module (planet/language/) owns the languages themselves. This module owns who speaks which, and names each tongue by the
culture whose tongue it is plus, when the run has languages.json, that culture's living lect id and language id at that era. Nothing
here touches the history or the language pass: read after the run (D63 A), like trade_flow and polities. Sources and design:
docs/review/peoples/trade-languages.md (cited T§n below).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

VERSION = 1
FORMAT = "procgen-tongues/1"
COLUMNS = ["tongue", "kind", "share", "lect", "language", "via"]  # (a ledger row; tongue: the culture whose tongue it is)
KINDS = ("neighbour", "ruler", "host", "lingua franca", "pidgin", "liturgy")

MIN_SHARE = 0.02  # a row is kept when at least this share of the culture's people speak the tongue. JUDGEMENT: a reporting floor
MIN_HEADS = 1000  # ... or, for the tongues of trade (BY_HEADS), when at least this many of its people speak it: a trading town's worth
# (the settlement ledger's smallest town, settlements.json tiers), since only its traders and townsfolk speak it (T§2)
BY_HEADS = ("host", "lingua franca", "pidgin")
TOP_PER_KIND = 4  # a culture lists at most this many tongues of each kind in an era (the most spoken): its biggest borders, its main
# rulers (a big people spread over many polities), its main trade languages. JUDGEMENT: a readable list
NEIGHBOUR_UPTAKE = 0.5  # a culture's speakers of a neighbour's tongue: this x its contact with the neighbour (frame_inputs: per cell of
# the culture, weighted by the cell's heads, the neighbour's part of the culture-cells in the cell and its ring; 1 = every culture met
# there is that neighbour) x 2 x the neighbour's part of the two peoples' heads (the bigger neighbour's tongue is learnt more: higher-status
# tongues spread at the expense of others, T§3; border regions with many cross-border contacts make bilinguals, T§1). JUDGEMENT: no source
# gives the share; a people half-mixed with an even-sized neighbour has a quarter of its people speak it
RULE_SPREAD = 0.25  # each further era of rule adds this share of a subject people's country folk to its speakers of the ruler's tongue
# (shift begins in government and towns, and the ruler's tongue spreads "more and more intensive over time", T§3). JUDGEMENT on the rate:
# an era is 0.5 kyr, ~20 generations, and shift within a community can take 2-3 generations (Breton, T§3), so this is slow on purpose:
# the whole country shifting is the language module's job (its takeover and incursion shifts), not this ledger's
RULE_MAX = 0.9  # a subject people never counts as wholly bilingual here. JUDGEMENT
LF_LEAD = 0.5  # the busiest trading culture's tongue is the trade language when it carries this share of the network's trade. JUDGEMENT:
# a pidgin forms where no one is "clearly dominant" (T§2: the superstrate), so a majority is the line
RULE_TOWNS = 0.5  # a state's tongue is the trade language when its ruling culture and its subjects carry this share of the network's
# trade (Aramaic, Greek koine: imperial tongues as lingua francas, T§2). JUDGEMENT: a majority, as LF_LEAD
HELD = 0.25  # an established trade language counts as carrying this share of the network's trade even when its own people no longer
# trade there (lingua francas outlive the empires that made them: Koine, Latin, T§4). JUDGEMENT
INERTIA = 2.0  # a new tongue replaces an established trade language only when it carries this many times the incumbent's weight. JUDGEMENT
ALONG = 0.25  # the share of the people living on a network's route cells (carriers, innkeepers, porters) who speak its trade language;
# the trading towns' own people all count (it is "used especially by traders", T§2). JUDGEMENT
QUARTER_FOLK = 0.05  # a merchant quarter's people as a share of its host town's people. JUDGEMENT: Curtin's institution, no size
LITURGY_SHARE = 0.01  # the clergy's share of a culture's people (they learn the faith's sacred register, T§5). JUDGEMENT: an order of size
LITURGY_GAP_KYR = 1.0  # the seat culture's own clergy count the canon as a second tongue once it is this old (Latin and Romance). JUDGEMENT


# ------------------------------------------------------------------ the languages, by culture (when the run has languages.json)

class LangIndex:
    """A culture's living lect and language at an era, from languages.json (lects: id, deme, language, born_kyr, died_kyr, minority) and
    cultures.json (each culture's demes). Without languages.json every answer is (None, None): the tongue is named by its culture."""

    def __init__(self, lang: dict | None, C: list):
        self.by_deme: dict = {}
        self.lect_deme: dict = {}
        self.faiths = {}
        if lang:
            for l in lang.get("lects") or []:
                if l.get("deme") is None:
                    continue
                self.lect_deme[l["id"]] = int(l["deme"])
                if l.get("minority"):
                    continue
                self.by_deme.setdefault(int(l["deme"]), []).append(l)
            self.faiths = {int(k): v for k, v in (lang.get("faiths") or {}).items()}
        self.C = C
        self.deme_culture: dict = {}
        for c, x in enumerate(C):
            for d in x.get("demes") or []:
                self.deme_culture.setdefault(int(d), c)

    def at(self, c: int, era: float) -> tuple:
        """(lect id, language id) of culture c at the era: the first of its demes with a lect alive then."""
        if not self.by_deme or not 0 <= c < len(self.C):
            return None, None
        for d in self.C[c].get("demes") or []:
            for l in self.by_deme.get(int(d), ()):
                if l["born_kyr"] >= era - 1e-9 and (l["died_kyr"] is None or l["died_kyr"] <= era + 1e-9):
                    return l["id"], l.get("language")
        return None, None

    def liturgy(self, fid: int) -> tuple | None:
        """(canon lect id, its culture, kyr fixed) of a faith whose liturgy the language pass fixed, else None."""
        L = (self.faiths.get(int(fid)) or {}).get("liturgy")
        if not L or L.get("lect_from") is None:
            return None
        d = L.get("deme", self.lect_deme.get(L["lect_from"]))
        return L["lect_from"], self.deme_culture.get(int(d)) if d is not None else None, float(L.get("kyr") or 0.0)


# ------------------------------------------------------------------ one era

def _components(routes: list) -> dict:
    """cell -> component id over the long-haul route stretches (layers bit 1; trade_routes.Loads.finish)."""
    parent: dict = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in routes:
        a, b = int(r[0]), int(r[1])
        lay = int(r[5]) if len(r) > 5 else 1
        if not lay & 1:
            continue
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    return {x: find(x) for x in parent}


def networks(F: dict) -> list:
    """The era's long-haul networks with trading towns of two or more cultures: [{"cells": set, "towns": [hub], "weight": {culture:
    share of the network's trade}, "cultures": set}]. A town's trade (its hub strength) is its host culture's, less the parts its merchant
    quarters carry, which are the merchants' culture's."""
    comp = _components(F.get("routes") or [])
    by: dict = {}
    for h in F.get("hubs") or []:
        if not h.get("trading", h.get("long")) or h.get("culture") is None or h["culture"] < 0:
            continue
        k = comp.get(int(h["cell"]))
        if k is None:
            continue
        by.setdefault(k, []).append(h)
    cells_of: dict = {}
    for x, k in comp.items():
        cells_of.setdefault(k, set()).add(x)
    out = []
    for k, towns in sorted(by.items()):
        w: dict = {}
        for h in towns:
            s = float(h.get("strength") or 0.0) or 1e-6
            qs = sum(float(q[2]) for q in h.get("quarters") or [])
            w[h["culture"]] = w.get(h["culture"], 0.0) + s * max(0.0, 1.0 - qs)
            for q in h.get("quarters") or []:
                w[int(q[0])] = w.get(int(q[0]), 0.0) + s * float(q[2])
        tot = sum(w.values())
        if len(w) < 2 or tot <= 0:
            continue
        out.append({"cells": cells_of[k], "towns": towns, "weight": {c: v / tot for c, v in w.items()}, "cultures": set(w)})
    return out


def pick(net: dict, rules: dict, last: dict | None, states: set | None = None) -> dict:
    """The network's trade language: {"kind": "lingua franca" | "pidgin", "tongue": culture (the pidgin's: its main word-giver),
    "source": "rule" | "trade" | "held" | "pidgin"}. last: the record this network inherits from the era before (or None)."""
    w = net["weight"]
    top = max(w, key=lambda c: (w[c], -c))
    cand = None
    for r, subj in sorted(rules.items()):  # (a state's ruling culture whose own and subject peoples carry most of the network's trade;
        if states is not None and r not in states:  # a chiefdom imposes no trade language. states None: every ruler counts)
            continue
        foreign = sum(v for c, v in w.items() if c != r and c in subj)
        rw = w.get(r, 0.0) + foreign
        if foreign > 0 and rw >= RULE_TOWNS and (cand is None or rw > cand[1]):  # (a state ruling peoples who trade on the network)
            cand = (r, rw, "rule")
    if cand is None and w[top] >= LF_LEAD:
        cand = (top, w[top], "trade")
    if last is not None and last["kind"] == "lingua franca":
        inc = last["tongue"]
        iw = max(w.get(inc, 0.0), HELD)
        if cand is None or cand[0] == inc or cand[1] < INERTIA * iw:
            return {"kind": "lingua franca", "tongue": inc, "source": "held" if cand is None or cand[0] != inc else cand[2]}
    if cand is not None:
        return {"kind": "lingua franca", "tongue": cand[0], "source": cand[2]}
    if last is not None and last["kind"] == "pidgin":
        return {"kind": "pidgin", "tongue": last["tongue"], "source": "pidgin"}
    return {"kind": "pidgin", "tongue": top, "source": "pidgin"}


def era_rows(inp: dict, last_nets: list, ruled_eras: dict, L: LangIndex) -> tuple[dict, list, list, dict]:
    """One era's ledger. inp: {"ago_kyr", "people": {culture: heads}, "urban": {culture: townsfolk share}, "border": {(a, b): a's contact
    with b, 0..1 (frame_inputs)}, "rules": {ruler: set(subjects)}, "faith": {culture: faith id}, "route_folk": {cell: {culture: share of
    its people}}, "routes", "hubs"} (the last two: trade_routes' frame). last_nets: the era before's trade languages; ruled_eras:
    (ruler, subject) -> eras of rule up to the era before. Returns (rows {culture: [row]}, trade languages, nets for the next era,
    ruled_eras for the next era)."""
    era = float(inp["ago_kyr"])
    people = inp.get("people") or {}
    alive = {c for c, n in people.items() if n > 0}
    rows: dict = {}
    tongue = {c: L.at(c, era) for c in alive}

    def same(a, b):
        la, lb = tongue.get(a, (None, None))[1], tongue.get(b, (None, None))[1]
        return la is not None and la == lb

    def add(c, t, kind, share, via=None, lect=None, language=None):
        if c not in alive or t == c or (kind != "liturgy" and same(c, t)):
            return
        if share < MIN_SHARE and (kind not in BY_HEADS or share * people[c] < MIN_HEADS):
            return
        if lect is None and t in tongue:
            lect, language = tongue[t]
        r = rows.setdefault(c, {})
        k = (t, kind)
        if k not in r or r[k][2] < share:
            r[k] = [t, kind, round(float(min(share, 1.0)), 4), lect, language, via]

    # a neighbour's tongue (border dwellers; the bigger neighbour's more)
    for (a, b), frac in (inp.get("border") or {}).items():
        if a in alive and b in alive:
            add(a, b, "neighbour", min(1.0, NEIGHBOUR_UPTAKE * frac * 2.0 * people[b] / (people[a] + people[b])))
    # a ruler's tongue (townsfolk first, then more of the country each era of rule)
    nxt_ruled: dict = {}
    for r, subj in (inp.get("rules") or {}).items():
        for s in subj:
            if s == r:
                continue
            n = ruled_eras.get((r, s), 0) + 1
            nxt_ruled[(r, s)] = n
            u = float((inp.get("urban") or {}).get(s, 0.0))
            add(s, r, "ruler", min(RULE_MAX, u + (1.0 - u) * min(1.0, RULE_SPREAD * (n - 1))))
    # merchants abroad speak their hosts' tongue
    for h in inp.get("hubs") or []:
        for q in h.get("quarters") or []:
            x = int(q[0])
            if x in alive and h.get("culture") is not None:
                add(x, int(h["culture"]), "host", QUARTER_FOLK * float(h.get("people") or 0) / max(people[x], 1.0), via=h.get("place"))
    # trade languages on the long-haul networks
    langs, nets_out = [], []
    folk = inp.get("route_folk") or {}
    for k, net in enumerate(networks(inp)):
        sites = {h.get("site") for h in net["towns"]}
        prev = max(last_nets, key=lambda p: len(sites & p["sites"]), default=None)
        if prev is not None and not sites & prev["sites"]:
            prev = None
        rec = pick(net, inp.get("rules") or {}, prev["rec"] if prev else None, inp.get("states"))
        lid = prev["id"] if prev is not None and prev["rec"]["kind"] == rec["kind"] and prev["rec"]["tongue"] == rec["tongue"] else f"{rec['kind'].split()[0]}-{era:g}-{k}"
        since = prev["since"] if prev is not None and lid == prev["id"] else era
        t = rec["tongue"]
        tl = tongue.get(t) or L.at(t, era)
        speak: dict = {}
        for h in net["towns"]:
            speak[h["culture"]] = speak.get(h["culture"], 0.0) + float(h.get("people") or 0)
            for q in h.get("quarters") or []:
                speak[int(q[0])] = speak.get(int(q[0]), 0.0) + QUARTER_FOLK * float(h.get("people") or 0)
        for x in net["cells"]:
            for c, s in (folk.get(x) or {}).items():
                speak[c] = speak.get(c, 0.0) + ALONG * s * people.get(c, 0.0)
        heads = 0.0
        for c, v in speak.items():
            if c not in alive:
                continue
            sh = min(1.0, v / max(people[c], 1.0))
            if rec["kind"] == "pidgin" or c != t:
                heads += sh * people[c]
                if rec["kind"] == "pidgin":
                    r = rows.setdefault(c, {})
                    if (sh >= MIN_SHARE or sh * people[c] >= MIN_HEADS) and ((t, "pidgin") not in r or r[(t, "pidgin")][2] < sh):
                        r[(t, "pidgin")] = [t, "pidgin", round(sh, 4), None, None, lid]
                else:
                    add(c, t, "lingua franca", sh, via=lid, lect=tl[0], language=tl[1])
        towns = sorted(net["towns"], key=lambda h: -float(h.get("strength") or 0))
        langs.append({"id": lid, "kind": rec["kind"], "tongue": t, "lect": tl[0], "language": tl[1], "source": rec["source"], "since_kyr": since,
                      "cultures": sorted(net["cultures"]), "weight": {str(c): round(v, 3) for c, v in sorted(net["weight"].items(), key=lambda x: -x[1])},
                      "towns": [h.get("site") for h in towns], "places": [h.get("place") for h in towns[:6]], "speakers": int(round(heads))})
        nets_out.append({"id": lid, "since": since, "sites": sites, "rec": rec})
    # the clergy learn their faith's frozen liturgy
    for c, fid in (inp.get("faith") or {}).items():
        lit = L.liturgy(fid) if fid is not None else None
        if lit is None or lit[1] is None or lit[2] < era - 1e-9:
            continue
        lect, seat, kyr = lit
        if seat == c and kyr - era < LITURGY_GAP_KYR:
            continue
        r = rows.setdefault(c, {}) if c in alive else None
        if r is not None:
            r[(seat, "liturgy")] = [seat, "liturgy", LITURGY_SHARE, lect, None, f"faith {fid}"]
    out = {}
    for c, r in sorted(rows.items()):
        rs = sorted(r.values(), key=lambda x: (-x[2], x[0], x[1]))
        cnt: dict = {}
        nb = []
        for x in rs:
            cnt[x[1]] = cnt.get(x[1], 0) + 1
            if cnt[x[1]] > TOP_PER_KIND:
                nb.append(x)
        rs = [x for x in rs if not any(x is y for y in nb)]
        if rs:
            out[str(c)] = rs
    return out, langs, nets_out, nxt_ruled


def ledger(inps: list, L: LangIndex) -> list:
    """era_rows over the eras in order (oldest first; each carries the era before's trade languages and eras of rule):
    [{"frame", "ago_kyr", "cultures": {culture: [row]}, "trade_languages": [...]}]."""
    eras, last_nets, ruled = [], [], {}
    for inp in inps:
        rows, langs, last_nets, ruled = era_rows(inp, last_nets, ruled, L)
        eras.append({"frame": inp.get("frame"), "ago_kyr": inp["ago_kyr"], "cultures": rows, "trade_languages": langs})
    return eras


# ------------------------------------------------------------------ reading a run

def state_rulers(pol: dict | None, era: float, C: list) -> set:
    """The cultures ruling a state, an empire or a dragon realm (not a chiefdom) at the polities step nearest the era, as
    trade_flow._polity_state reads its rulers."""
    if not pol or not pol.get("steps"):
        return set()
    from . import trade as TR
    st = pol["steps"]
    k = min(range(len(st)), key=lambda q: abs(st[q]["ago"] - era))
    tiers = pol.get("tiers") or []
    cid = {u: v["id"] for u, v in (pol.get("cultures") or {}).items()}
    recs = {r["id"]: r for r in pol["polities"]}
    out = set()
    for e in pol["maps"][k]:
        rec = recs.get(e[0])
        if not rec or not rec.get("rulers") or not 0 <= e[1] < len(tiers) or tiers[e[1]] == "chiefdom":
            continue
        ru = None
        for a, u in rec["rulers"]:
            if a >= era - 1e-9:
                ru = u
        if ru in cid:
            out.add(TR._at(C, cid[ru], era))
    return out


def frame_inputs(ctx, i: int, F: dict, pol: dict | None, gods: dict | None) -> dict | None:
    """era_rows' inputs at frame i from the run (the goods ledger's (cell, culture) pairs for heads, townsfolk, borders and route folk),
    the trade frame F (routes, hubs), the polities doc (who rules whom) and the gods doc (who holds which faith)."""
    from . import trade as TR
    from .trade_flow import _polity_state
    P = TR.pairs_at(ctx, i)
    if P is None:
        return None
    rows = TR.ledger_at(ctx, i) or {}
    era = -float(ctx.ts[i])
    cell, cu, w = np.asarray(P["cell"]), np.asarray(P["culture"]), np.asarray(P["w"], float)
    wsum = P["wsum"]
    people = {int(c): float(r.get("people") or 0) for c, r in rows.items()}
    urb = np.asarray(P.get("urban") if P.get("urban") is not None else np.zeros(len(cell)), float)
    urban: dict = {}
    for c, x in zip(cu.tolist(), (w * urb).tolist()):
        urban[c] = urban.get(c, 0.0) + x
    urban = {c: min(1.0, v / max(wsum.get(c, 0.0), 1e-12)) for c, v in urban.items()}
    at_cell: dict = {}
    for c, x in zip(cell.tolist(), cu.tolist()):
        at_cell.setdefault(c, set()).add(x)
    g = ctx.g
    off, idx = g.nbr_off, g.nbr_idx
    border: dict = {}
    near_of: dict = {}
    for c in at_cell:  # (each culture's part of the culture-cells in the cell and its ring: how often a neighbour is met there)
        cnt: dict = {}
        for j in [c] + idx[off[c]:off[c + 1]].tolist():
            for y in at_cell.get(j, ()):
                cnt[y] = cnt.get(y, 0) + 1
        tot = sum(cnt.values())
        near_of[c] = {y: k / tot for y, k in cnt.items()}
    for c, x, wx in zip(cell.tolist(), cu.tolist(), w.tolist()):
        for y, e in near_of[c].items():
            if y != x:
                border[(x, y)] = border.get((x, y), 0.0) + wx * e
    border = {k: min(1.0, v / max(wsum.get(k[0], 0.0), 1e-12)) for k, v in border.items()}
    rcells = {int(r[0]) for r in F.get("routes") or [] if int(r[5]) & 1} | {int(r[1]) for r in F.get("routes") or [] if int(r[5]) & 1}
    folk: dict = {}
    for c, x, wx in zip(cell.tolist(), cu.tolist(), w.tolist()):
        if c in rcells:
            d = folk.setdefault(c, {})
            d[x] = d.get(x, 0.0) + wx / max(wsum.get(x, 0.0), 1e-12)
    C = ctx.cultures()["cultures"]
    _, _, rules = _polity_state(pol, era, g.n, C)
    states = state_rulers(pol, era, C)
    faith = {}
    if gods:
        from .faithmap import faith_of_culture
        faith = faith_of_culture(gods, era)
    return {"ago_kyr": round(abs(era), 3), "people": people, "urban": urban, "border": border, "rules": rules, "states": states, "faith": faith,
            "route_folk": folk, "routes": F.get("routes") or [], "hubs": F.get("hubs") or []}


def derive(run_dir, tflow: dict, ctx=None, pol: dict | None = None, gods: dict | None = None, lang: dict | None = None) -> dict:
    """The run's tongues ledger over the land-use window, from its exchange doc (trade_flow.derive, with routes), the polities doc, the
    gods doc and languages.json (read from the run when lang is None and the file is there). Read-only."""
    from .brief import Ctx
    t0 = time.time()
    ctx = ctx or Ctx(run_dir)
    C = (ctx.cultures() or {}).get("cultures") or []
    if lang is None:
        f = Path(ctx.dir) / "languages.json"
        if f.exists():
            raw = json.loads(f.read_text())
            lang = {"lects": raw.get("lects") or [], "faiths": raw.get("faiths") or {}}
    L = LangIndex(lang, C)
    inps = []
    for F in tflow.get("frames") or []:  # (oldest first)
        if "routes" not in F:
            continue
        inp = frame_inputs(ctx, int(F["frame"]), F, pol, gods)
        for k in ("trade_cells", "trade_ledger", "trade_pairs"):
            ctx._frame_cache.pop((k, int(F["frame"])), None)
        if inp is not None:
            inps.append({"frame": int(F["frame"]), **inp})
    eras = ledger(inps, L)
    return {"format": FORMAT, "version": VERSION, "run": Path(ctx.dir).name, "columns": COLUMNS, "kinds": list(KINDS),
            "cultures": [{k: x.get(k) for k in ("name", "people")} for x in C], "frames": eras, "had_polities": pol is not None,
            "had_gods": gods is not None, "had_languages": bool(lang), "seconds": round(time.time() - t0, 1),
            "constants": {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float)) and k != "VERSION"},
            "basis": "tongues.py (PW-1526, docs/review/peoples/trade-languages.md): per era, the neighbour's, ruler's, host's, trade and "
                     "liturgical tongues each culture's people speak besides its own. Read-out only."}


# ------------------------------------------------------------------ views

def culture_view(doc: dict, c: int) -> list:
    """Per era, culture c's other tongues: [{"ago_kyr", "rows": [{tongue, name, kind, share, lect, language, via}]}]."""
    nm = lambda k: doc["cultures"][k]["name"] if isinstance(k, int) and 0 <= k < len(doc["cultures"]) else str(k)  # noqa: E731
    out = []
    for f in doc["frames"]:
        r = f["cultures"].get(str(c))
        if r:
            out.append({"ago_kyr": f["ago_kyr"], "rows": [dict(zip(COLUMNS, x), name=nm(x[0])) for x in r]})
    return out


def summary(doc: dict) -> dict:
    """Counts per era: cultures with another tongue, rows per kind, trade languages and pidgins, and the share of all heads bilingual."""
    out = []
    for f in doc["frames"]:
        kinds: dict = {}
        for rs in f["cultures"].values():
            for x in rs:
                kinds[x[1]] = kinds.get(x[1], 0) + 1
        tl = f["trade_languages"]
        out.append({"ago_kyr": f["ago_kyr"], "multilingual_cultures": len(f["cultures"]), "rows": kinds,
                    "lingua_francas": sum(1 for x in tl if x["kind"] == "lingua franca"), "pidgins": sum(1 for x in tl if x["kind"] == "pidgin"),
                    "trade_languages": [[x["id"], x["kind"], x["tongue"], x["source"], len(x["cultures"]), x["speakers"]] for x in tl]})
    return {"format": doc["format"], "version": doc["version"], "run": doc["run"], "eras": out, "had_languages": doc["had_languages"]}
