"""Reputation and exonyms (PW-731): what each people calls each neighbour and why, kept apart from what the neighbour is.

Everything is read from the contact record (`meta.contacts`, contacts.py) and the tree; nothing here touches the simulation.
For an observer O and a subject S that met:
  valence  how O remembers S, from the history of the pair:
             feared    S took O's land (S's substrate holds O's cells; a conquest memory that fades with an e-folding
                       of EFOLD_KYR x the era's scale, or the matching row's own `efold_kyr`, down to MIN_STRENGTH)
             despised  O took S's land (the same, as a held-down people)
             resented  S ruled O (an authored `[[event]] kind = "polity"`: S's state held O's people from `at` until `until`); the
                       memory fades from when the rule ended (or is whole while it stands)
             edge      thin contact (few years, a short border): strangers at the edge of the map
             exotic    some contact, not much (a trade partner, a coast visitor)
             neighbour rich, peaceful contact (years in contact and a mixed zone, or a close tier): O uses S's own name
             A row may carry its own `efold_kyr` (a legend: the invader's name outlasts the event for that many kyr, whatever the
             era); the row then reports `memory_kyr`.
  category the preset's `[[exonym]]` row that best fits S's visible body / ancestry / way / origin (most conditions
           matched; a row may be limited to some valences); the valence's fallback row where none fits
  lumped_with  other subjects in thin contact that O files under the same name
  borrowed  an observer that never met S takes the view of its best-connected neighbour that did (at half strength)
The result is `meta.present.reputation`: {"params", "rows": {observer: {subject: row}}}. The rows are data
(spec.Tree.exonyms): the mechanism holds no story; a preset can give any folk category a body, an ancestry or an arrival
and the valences it applies to. A conquest candidate is one of three (the strongest of S over O stands):
  substrate   cells of S's present range that O held before (memory fades from when they changed hands)
  incursion   derived from the run's own history (contacts.Contacts.incursions, PW-756): S's range jumped into ground O held within a
              short span (a gain of 10% of its own range or more); the loss is the share of O's land within 1000 km of that ground, so a
              big people's frontier memory is not diluted by its far provinces; it carries the compass direction S came from
  authored    `[[event]]` rows (kind conquest: S overran O at a date, PW-730): the fallback, used only where the history found no
              incursion of S over O (an authored anchor is not stacked on a derived one)
Direction (PW-756): a derived incursion carries the bearing S came from; a feared or resented row without one takes the bearing
from O's present range to S's, where both ranges are compact enough to have one (DIR_COMPACT) and lie apart (DIR_MIN_KM).
Not yet read: the run's own polities (PW-661; polities.py runs after this pass), so 'resented' comes only from authored rows."""

from __future__ import annotations

import math

from .years import years_ago

EFOLD_KYR = 1.5  # e-folding time of a conquest's reputation (PW-731)
ERA_FADE = {"stone age": 0.5, "bronze age": 0.7, "classical": 1.0, "medieval": 1.3, "renaissance": 1.6, "industrial": 2.0}  # (memory lasts longer with writing; meta.era is still a placeholder, PW-690)
MIN_STRENGTH = 0.05  # a conquest memory weaker than this is gone: the pair reads by its contact
LOSS_SCALE = 3.0  # strength of a conquest = min(1, LOSS_SCALE x the share of the loser's land taken)
RICH_YEARS = 20000  # years in contact (and a mixed zone) that make contact rich and peaceful
RICH_MIXED_PCT = 2.0
THIN_YEARS = 3000  # under this many years in contact, or a border under THIN_KM at its widest: thin
THIN_KM = 150
BORROW_STRENGTH = 0.5  # share of the view kept when it is borrowed
VALENCES = ("feared", "despised", "resented", "exotic", "edge", "neighbour")
DIR_COMPACT = 0.85  # a range whose cells' mean resultant length is under this (wider than ~30 degrees of arc) has no one direction
DIR_MIN_KM = 300.0  # two ranges' centroids closer than this give no direction
KNOBS = ("efold_kyr", "min_strength", "loss_scale", "rich_years", "thin_years", "thin_km")
ROW_KEYS = ("id", "label", "body", "traits", "ancestor", "origin", "way", "valence", "efold_kyr")


def params(tree) -> dict:
    """The reputation knobs (meta.reputation overrides the defaults)."""
    p = {"efold_kyr": EFOLD_KYR, "min_strength": MIN_STRENGTH, "loss_scale": LOSS_SCALE, "rich_years": RICH_YEARS,
         "thin_years": THIN_YEARS, "thin_km": THIN_KM}
    p.update({k: v for k, v in (getattr(tree, "reputation", None) or {}).items() if k in KNOBS})
    p["era"] = tree.era
    p["era_scale"] = ERA_FADE.get(tree.era, 1.0)
    return p


def parse_rows(rows, body_keys, choices) -> list[dict]:
    """Validate the `[[exonym]]` rows of a spec (id, label and the conditions)."""
    out, seen = [], set()
    for r in rows or []:
        bad = [k for k in r if k not in ROW_KEYS]
        if bad or not r.get("id"):
            raise ValueError(f"exonym {r}: needs an id and only the keys {list(ROW_KEYS)}")
        if r["id"] in seen:
            raise ValueError(f"exonym {r['id']}: duplicate id")
        seen.add(r["id"])
        row = {"id": str(r["id"]), "label": str(r.get("label") or r["id"])}
        b = r.get("body") or {}
        for k, v in b.items():
            if k not in body_keys or (k in choices and v not in choices[k]):
                raise ValueError(f"exonym {r['id']}: body.{k} = {v!r} is not a body key / choice")
        if b:
            row["body"] = dict(b)
        for k in ("traits", "valence"):
            v = r.get(k)
            if v is not None:
                v = [v] if isinstance(v, str) else [str(x) for x in v]
                if k == "valence" and any(x not in VALENCES for x in v):
                    raise ValueError(f"exonym {r['id']}: valence must be some of {list(VALENCES)}")
                row[k] = v
        for k in ("ancestor", "origin", "way"):
            if r.get(k):
                row[k] = str(r[k])
        if r.get("efold_kyr") is not None:
            row["efold_kyr"] = float(r["efold_kyr"])
            if not row["efold_kyr"] > 0:
                raise ValueError(f"exonym {r['id']}: efold_kyr must be > 0 (kyr)")
        out.append(row)
    return out


EVENT_KINDS = ("conquest", "polity")
EVENT_STRENGTH = 0.8  # how deeply an authored conquest is remembered at the moment it happened (0..1)


def parse_events(rows, lines, off=()) -> list[dict]:
    """Validate the `[[event]]` rows of a spec: dated history the owner insists on, kept as an anchor the reputation pass reads
    (PW-730, owner PW-734: a thin slice of history). `kind = "conquest"`, `by` = the people that conquered, `over` = the peoples it
    overran (one id or a list), `at` = when (kyr ago), optional `strength` 0..1. `kind = "polity"` (PW-756): `by` ruled `over` from
    `at` until `until` (kyr ago; left out: the rule stands at the present); it is remembered as 'resented'. No place: where the
    conquerors came from is the world's to say. Events that name a line switched off (real mode, enabled = false) are dropped."""
    from .spec import parse_ago
    out = []
    for r in rows or []:
        kind = str(r.get("kind", "conquest"))
        bad = [k for k in r if k not in ("kind", "by", "over", "at", "strength", "note") + (("until",) if kind == "polity" else ())]
        if bad or kind not in EVENT_KINDS or not r.get("by") or not r.get("over") or r.get("at") in (None, ""):
            raise ValueError(f"event {r}: needs kind {list(EVENT_KINDS)}, by, over, at, and only those keys (and strength, note; until for a polity)")
        over = [str(r["over"])] if isinstance(r["over"], str) else [str(x) for x in r["over"]]
        names = [str(r["by"]), *over]
        if any(x in off for x in names):
            continue
        if any(x not in lines for x in names):
            raise ValueError(f"event {r}: unknown lineage")
        st = float(r.get("strength", EVENT_STRENGTH))
        if not 0 < st <= 1:
            raise ValueError(f"event {r}: strength must be within 0..1")
        ev = {"kind": kind, "by": str(r["by"]), "over": over, "at": parse_ago(r["at"]), "strength": st}
        if kind == "polity":
            ev["until"] = parse_ago(r["until"]) if r.get("until") not in (None, "") else 0.0
            if not 0 <= ev["until"] <= ev["at"]:
                raise ValueError(f"event {r}: a polity's until must be at or after its start (0 <= until <= at, kyr ago)")
        if r.get("note"):
            ev["note"] = str(r["note"])
        out.append(ev)
    return out


def matches(tree, row: dict, s: str) -> int | None:
    """How many of the row's conditions the subject line meets (None: a condition fails)."""
    l = tree.lines[s]
    n = 0
    for k, v in (row.get("body") or {}).items():
        if l.body.get(k) != v:
            return None
        n += 1
    if row.get("traits"):
        if not set(row["traits"]) & set(l.traits):
            return None
        n += 1
    if row.get("ancestor"):
        if row["ancestor"] not in (s, *tree.ancestors(s)):
            return None
        n += 1
    if row.get("origin"):
        if l.origin != row["origin"]:
            return None
        n += 1
    if row.get("way"):
        if l.way != row["way"]:
            return None
        n += 1
    return n


def _category(tree, s: str, valence: str):
    """The best-fitting row for the subject and valence (most conditions; ties by file order), or None."""
    best, bn = None, -1
    for row in tree.exonyms:
        if row.get("valence") and valence not in row["valence"]:
            continue
        n = matches(tree, row, s)
        if n is not None and n > bn:
            best, bn = row, n
    return best, bn


def _people_pairs(tree, contacts: dict) -> dict:
    """The contact pairs by people (groups folded into their people): {(a, b) with a < b: record}."""
    out: dict = {}
    for r in contacts.get("pairs", []):
        a, b = tree.people_of(r["a"]), tree.people_of(r["b"])
        if a == b or a not in tree.lines or b not in tree.lines:
            continue
        k = (a, b) if a < b else (b, a)
        cur = out.get(k)
        if cur is None:
            out[k] = dict(r, a=k[0], b=k[1])
        else:
            for f in ("years_in_contact", "border_km_peak", "mixed_pct_now"):
                cur[f] = max(cur[f], r[f])
            cur["border_km_now"] += r["border_km_now"]
            cur["first_contact_kyr"] = max(cur["first_contact_kyr"], r["first_contact_kyr"])
            cur["in_contact_now"] = cur["in_contact_now"] or r["in_contact_now"]
    return out


def _takings(tree, sub: dict) -> dict:
    """{(taker, loser): {cells, until_kyr}} from the substrate: the cells of `taker`'s present range that `loser` held before."""
    out: dict = {}
    for taker, v in (sub or {}).items():
        p = tree.people_of(taker)
        for r in v.get("held_before", []):
            q = tree.people_of(r["id"])
            if p == q or p not in tree.lines or q not in tree.lines:
                continue
            e = out.setdefault((p, q), {"cells": 0, "w": 0.0})
            e["cells"] += r["cells"]
            e["w"] += r["cells"] * r["held_until_kyr"]
    for e in out.values():
        e["until_kyr"] = e.pop("w") / max(e["cells"], 1)
    return out


def _incursions(tree, contacts: dict) -> dict:
    """{(taker, loser): [incursion, ...]} by people from the derived incursions (contacts.Contacts.incursions, PW-756)."""
    out: dict = {}
    for r in contacts.get("incursions") or []:
        if r["by"] not in tree.lines or r["over"] not in tree.lines:
            continue
        p, q = tree.people_of(r["by"]), tree.people_of(r["over"])
        if p != q:
            out.setdefault((p, q), []).append(r)
    return out


def compass(deg: float) -> str:
    """The eight-point compass word of a bearing in degrees."""
    return ("north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west")[int(((deg % 360) + 22.5) // 45) % 8]


def _cells_of(tree, sub: dict) -> dict:
    out: dict = {}
    for k, v in (sub or {}).items():
        p = tree.people_of(k)
        out[p] = out.get(p, 0) + v.get("cells", 0)
    return out


def _centroids(tree, sub: dict) -> dict:
    """{people: (unit vector of its present centroid, compactness)}, groups folded into their people (contacts' substrate lat/lon/compact)."""
    acc: dict = {}
    for k, v in (sub or {}).items():
        if v.get("lat") is None or k not in tree.lines:
            continue
        la, lo = math.radians(v["lat"]), math.radians(v["lon"])
        w = v["cells"] * v["compact"]
        e = acc.setdefault(tree.people_of(k), [0.0, 0.0, 0.0, 0])
        e[0] += w * math.cos(la) * math.cos(lo)
        e[1] += w * math.cos(la) * math.sin(lo)
        e[2] += w * math.sin(la)
        e[3] += v["cells"]
    out = {}
    for p, (x, y, z, n) in acc.items():
        r = math.sqrt(x * x + y * y + z * z)
        if r > 0 and n:
            out[p] = ((x / r, y / r, z / r), r / n)
    return out


def bearing_of(cent: dict, o: str, s: str) -> str | None:
    """The compass word of the bearing from O's present range to S's ('from the west': S lies west of O), or None where either
    range is too spread to have one (DIR_COMPACT) or the two lie closer than DIR_MIN_KM."""
    a, b = cent.get(o), cent.get(s)
    if not a or not b or a[1] < DIR_COMPACT or b[1] < DIR_COMPACT:
        return None
    (x1, y1, z1), (x2, y2, z2) = a[0], b[0]
    if math.acos(max(-1.0, min(1.0, x1 * x2 + y1 * y2 + z1 * z2))) * 6371.0 < DIR_MIN_KM:
        return None
    la1, lo1, la2, lo2 = math.asin(z1), math.atan2(y1, x1), math.asin(z2), math.atan2(y2, x2)
    dl = lo2 - lo1
    deg = math.degrees(math.atan2(math.sin(dl) * math.cos(la2), math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dl)))
    return compass(deg)


def build(tree, contacts: dict | None) -> dict | None:
    """The reputation table of a run: {"params", "rows": {observer: {subject: row}}}; None without a contact record."""
    if not contacts:
        return None
    P = params(tree)
    leaves = {l.id for l in tree.leaves()} | {l.id for l in tree.lines.values() if l.origin == "group"}
    alive = {tree.people_of(k) for k in (contacts.get("substrate") or {}) if k in leaves}  # (peoples with land at the present: no stems, no extinct lines)
    pairs = {k: v for k, v in _people_pairs(tree, contacts).items() if k[0] in alive and k[1] in alive}
    take = _takings(tree, contacts.get("substrate"))
    inc = _incursions(tree, contacts)
    held = _cells_of(tree, contacts.get("substrate"))
    cent = _centroids(tree, contacts.get("substrate"))
    rows: dict = {}
    for (a, b), rec in pairs.items():
        for o, s in ((a, b), (b, a)):
            rows.setdefault(o, {})[s] = _view(tree, P, o, s, rec, take, held, inc, cent)
    _lump(rows)
    _borrow(rows, pairs)
    for o in rows:
        for s, r in rows[o].items():
            r["text"] = text(tree, o, s, r)
    return {"params": P, "rows": {o: dict(sorted(v.items())) for o, v in sorted(rows.items())}}


def _view(tree, P: dict, o: str, s: str, rec: dict, take: dict, held: dict, inc: dict | None = None, cent: dict | None = None) -> dict:
    yrs, km = rec["years_in_contact"], rec["border_km_peak"]
    cands = []  # (strength, valence, basis, since, legend memory, direction the taker came from)
    for taker, loser, val in ((s, o, "feared"), (o, s, "despised")):
        t = take.get((taker, loser))
        if not t:
            continue
        lost = t["cells"] / max(held.get(loser, 0) + t["cells"], 1)
        row, _ = _category(tree, s, val)
        own = (row or {}).get("efold_kyr")  # a legend row: its own memory length in kyr (not scaled by the era), PW-754
        efold = own or P["efold_kyr"] * P["era_scale"]
        st = min(1.0, P["loss_scale"] * lost) * math.exp(-t["until_kyr"] / efold)
        if st >= P["min_strength"]:
            cands.append((st, val, f"conquest: {taker} took {t['cells']} cells ({round(100 * lost)}% of {loser}'s land)", t["until_kyr"], own, None))
    derived = False
    for taker, loser, val in ((s, o, "feared"), (o, s, "despised")):  # derived incursions (PW-756): a short, sharp advance into the loser's frontier
        row, _ = _category(tree, s, val)
        own = (row or {}).get("efold_kyr")
        efold = own or P["efold_kyr"] * P["era_scale"]
        for r in (inc or {}).get((taker, loser), []):
            st = min(1.0, P["loss_scale"] * r["local_share"]) * math.exp(-r["ago_kyr"] / efold)
            if st >= P["min_strength"]:
                d = None if r.get("from_deg") is None or val != "feared" else compass(r["from_deg"])
                derived = derived or val == "feared"
                cands.append((st, val, f"incursion (derived): {taker} " + (f"settled among {loser} on {r['cells']} cells" if r.get("kind") == "settled_among" else f"took {r['cells']} cells") + f" in {max(r['span_kyr'], 0.1):g} kyr "
                                       f"({round(100 * r['local_share'])}% of {loser}'s land nearby)" + (f", from the {d}" if d else ""), r["ago_kyr"], own, d))
    for ev in getattr(tree, "events", None) or []:  # authored conquests (PW-730): S's people overran O's, ev["at"] kyr ago (the fallback: where the history found an incursion of S over O, that stands instead)
        if tree.people_of(ev["by"]) != s or o not in {tree.people_of(x) for x in ev["over"]}:
            continue
        if ev["kind"] == "polity":  # authored rule (PW-756): S's state ruled O's people; resented, fading from when the rule ended
            row, _ = _category(tree, s, "resented")
            own = (row or {}).get("efold_kyr")
            end = ev.get("until", 0.0)
            st = ev["strength"] * math.exp(-end / (own or P["efold_kyr"] * P["era_scale"]))
            if st >= P["min_strength"]:
                span = f"from {years_ago(ev['at'])} " + ("to this day" if end <= 0.0005 else f"until {years_ago(end)}")
                cands.append((st, "resented", f"rule (authored): {s} ruled {o} {span}", end, own, None))
            continue
        if derived:
            continue
        row, _ = _category(tree, s, "feared")
        own = (row or {}).get("efold_kyr")
        st = ev["strength"] * math.exp(-ev["at"] / (own or P["efold_kyr"] * P["era_scale"]))
        if st >= P["min_strength"]:
            cands.append((st, "feared", f"conquest (authored): {s} overran {o} {years_ago(ev['at'])}", ev["at"], own, None))
    if cands:
        strength, val, basis, since, legend, came = max(cands, key=lambda c: c[:4])
        if not came and val in ("feared", "resented"):
            came = bearing_of(cent or {}, o, s)
    else:
        rich = (yrs >= P["rich_years"] and rec["mixed_pct_now"] >= RICH_MIXED_PCT) or (rec["tier"] in ("T0", "T1") and yrs >= P["rich_years"] // 2)
        thin = yrs < P["thin_years"] or km < P["thin_km"]
        val = "neighbour" if rich else "edge" if thin else "exotic"
        basis = {"neighbour": f"rich peaceful contact ({yrs} yr, {rec['mixed_pct_now']}% mixed)",
                 "edge": f"thin contact ({yrs} yr, border {km} km)", "exotic": f"some contact ({yrs} yr, along {rec['kind']})"}[val]
        since, legend, came = rec["first_contact_kyr"], None, None
        strength = max(0.0, 1 - yrs / max(P["thin_years"], 1)) if val == "edge" else min(1.0, yrs / max(P["rich_years"], 1))
    if val == "neighbour":
        cat, name = None, tree.lines[s].label()
    else:
        row, _ = _category(tree, s, val)
        cat, name = (row["id"], row["label"]) if row else (val, val)
    out = {"category": cat, "name": name, "valence": val, "basis": basis, "since_kyr": round(since, 2), "strength": round(strength, 3),
           "lumped_with": [], "tier": rec["tier"]}
    if came:
        out["from_dir"] = came
    if legend:  # (only where the row gave its own memory length: every other row is unchanged)
        out["memory_kyr"] = legend
    return out


def _lump(rows: dict) -> None:
    """Thin-contact subjects an observer files under one name are lumped together."""
    for v in rows.values():
        groups: dict = {}
        for s, r in v.items():
            if r["valence"] == "edge":
                groups.setdefault(r["name"], []).append(s)
        for names in groups.values():
            if len(names) > 1:
                for s in names:
                    v[s]["lumped_with"] = sorted(x for x in names if x != s)


def _borrow(rows: dict, pairs: dict) -> None:
    """An observer takes, for a subject it never met, the view of its best-connected neighbour N (the longest contact) if N is
    in contact with that subject now, at half strength; a 'neighbour' valence is not passed on."""
    yrs: dict = {}
    for (a, b), r in pairs.items():
        yrs.setdefault(a, {})[b] = r["years_in_contact"]
        yrs.setdefault(b, {})[a] = r["years_in_contact"]
    now = {(a, b) for (a, b), r in pairs.items() if r["in_contact_now"]}
    add: dict = {}
    for o in sorted(yrs):
        n = min(yrs[o], key=lambda q: (-yrs[o][q], q))
        for s, r in rows.get(n, {}).items():
            if s == o or s in rows.get(o, {}) or r["valence"] == "neighbour" or ((n, s) if n < s else (s, n)) not in now:
                continue
            add[(o, s)] = dict(r, strength=round(r["strength"] * BORROW_STRENGTH, 3), basis=f"borrowed from {n}: " + r["basis"],
                               lumped_with=[], borrowed_from=n)
    for (o, s), r in add.items():
        rows.setdefault(o, {})[s] = r


def text(tree, o: str, s: str, r: dict) -> str:
    on, sn = tree.lines[o].label(), tree.lines[s].label()
    if r["valence"] == "neighbour":
        return f"{on} call {sn} by their own name ({r['basis']})."
    when = f", {years_ago(r['since_kyr'])}" if r["valence"] in ("feared", "despised") else ""
    if r["valence"] == "resented":
        when = ", to this day" if r["since_kyr"] <= 0.0005 else f", until {years_ago(r['since_kyr'])}"
    if r.get("from_dir"):
        when += f", from the {r['from_dir']}"
    lump = f"; one name for {', '.join(r['lumped_with'])} too" if r["lumped_with"] else ""
    return f"{on} call {sn} \"{r['name']}\" ({r['valence']}{when}; {r['basis']}{lump})."
