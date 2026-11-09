"""Calendars cultures found (PW-1435): a culture that lives through a notable event may start counting the years from it ("year 212
of the Founding of Iligya"); the count spreads with the state or faith that carries it and can fade.

Read-out only, from what a peoples run stores and the read-outs it already has: the faiths (gods doc), the states (polities doc), the
incursions (meta.contacts), the settlement ledger's war events and its towns lost to a shifting river (floods). Nothing is written.
"X years ago" stays the default everywhere; a read-out shows a date in a calendar only when asked (years.in_calendar, the viewer's
"dates in" picker).

**Which events start a count** (each a chance, drawn once per event, deterministic from the run's seed):

- The culture must keep written records when the event happens: its people knows `writing` (meta.techtree.known) by then. Every
  continuous era in the record is from literate societies (the Seleucid era 312 BC, AUC, the Hijri era, the Spanish era; Wikipedia,
  "Calendar era"); before writing, years were named after events ("the Year of the Elephant" in pre-Islamic Arabia; Wikipedia,
  "Islamic calendar"), not counted. Judgement: named years (annals, winter counts) are not modelled.
- A faith founded, or a schism: P_FAITH (P_SCHISM), scaled by how far the faith spread (cultures it ever held / FAITH_FULL). Sourced
  pattern: the religious eras of the record date from a founder's life or a founding moment (Anno Domini, the Hijra, the Buddhist
  era, the Bahá'í era, the Era of the Martyrs); the numbers are judgement.
- A state reaching state or empire rank (its founding, or its rise from a chiefdom): P_STATE by tier, scaled by its life
  (min(1, life / LIFE_FULL_KYR)). Sourced pattern: the founding of a city or state (AUC, Bangkok's founding for the Thai era, the US
  and French republics, the Minguo era), or the start of a reign kept as an era (Diocletian, Yazdegerd III, Lakshmana Sena);
  Chinese dynasties proclaimed a new era name at their founding (Wikipedia, "Chinese era name"). Regnal years that restart every
  reign are not modelled (they are not one count). The numbers are judgement.
- A conquest (a state that conquered another): P_CONQUEST, held by the conqueror. Sourced: the Seleucid era dates from Seleucus I's
  capture of Babylon, the Spanish era and the Pompeian era from Roman conquests, and the conquered regions used them.
- An incursion (meta.contacts: a people that settled among or displaced another), a city or town razed or sacked, a town lost to a
  shifting river: P_INCURSION, P_RAZED, P_SACKED, P_FLOOD, held by the culture that lived through it. No era in Wikipedia's list
  starts from a disaster or a defeat; these odds are small and judgement.

**Spread and fading.** A faith's count is kept by its founding culture and, with P_ADOPT each, by the cultures that held the faith,
for as long as they held it (gods doc `cultures[c].faiths`); it ends with the faith. A state's count is kept by its ruling cultures
and, with P_ADOPT_SUBJECT each, its subject cultures, while the state lives; when the state falls, its rulers keep it on with
P_OUTLIVE for an exponential time of mean OUTLIVE_KYR (the Seleucid era outlived its empire by about a thousand years among the
eastern Christians, the Yazdegerd era outlived the Sasanians; the French Republican and Fascist eras died with their regimes:
Wikipedia, "Calendar era"). A count with neither a state nor a faith behind it fades after an exponential time of mean
LOCAL_KYR. Every holder's use ends when its culture ends. Judgement: the means.

The year of the event is year 1 (AUC 1 is the founding's year, AH 1 the Hijra's; Wikipedia, "Calendar era", "Islamic calendar")."""
from __future__ import annotations

import math
import zlib

import numpy as np

TICKET = 1435
VERSION = 1
P_FAITH, P_SCHISM = 0.5, 0.25  # a founded faith / a schism that reached FAITH_FULL cultures (judgement)
FAITH_FULL = 8  # cultures a faith ever held for the full chance (judgement: a world religion vs a sect)
P_STATE = {"state": 0.02, "empire": 0.1, "dragon realm": 0.05}  # a state reaching this rank and living LIFE_FULL_KYR (judgement: about
# 25 pre-modern eras in Wikipedia's list against the hundreds of literate states and empires the record knows; an era is rare)
LIFE_FULL_KYR = 0.3  # a state this long-lived gets the full chance (judgement: the eras that took hold came from states that lasted)
P_CONQUEST = 0.01  # a conquest by a state or empire (judgement: 3 of those ~25 eras are conquest-dated, against thousands of conquests)
P_INCURSION = 0.03  # an incursion lived through (judgement)
P_RAZED, P_SACKED = 0.03, 0.01  # a town or city razed / sacked (judgement)
P_FLOOD = 0.02  # a town or city lost to a shifting river (judgement)
P_ADOPT = 0.7  # a culture that took up the faith keeps its count too (judgement)
P_ADOPT_SUBJECT = 0.5  # a subject culture of the state keeps its count (judgement; the Pompeian era in the conquered cities)
P_OUTLIVE = 0.5  # the rulers keep the count after the state falls (2 of the 4 fallen-state eras in Wikipedia's list did)
OUTLIVE_KYR = 0.8  # mean years (kyr) it is kept after (judgement; Seleucid ~1 kyr, Yazdegerd ~1.4 kyr and counting)
LOCAL_KYR = 0.3  # mean life (kyr) of a count with no state or faith behind it (judgement)
STATE_TIERS = ("state", "empire", "dragon realm")
SOURCES = ["Wikipedia, 'Calendar era' (list of eras and their epochs): https://en.wikipedia.org/wiki/Calendar_era",
           "Wikipedia, 'Islamic calendar' (the Hijri epoch chosen by Umar about 638, 17 years after; named years before): "
           "https://en.wikipedia.org/wiki/Islamic_calendar",
           "Wikipedia, 'Chinese era name' (a new era at a dynasty's founding, from Emperor Wu of Han, 140 BCE): "
           "https://en.wikipedia.org/wiki/Chinese_era_name"]


def _rng(seed: int, *key) -> np.random.Generator:
    return np.random.default_rng((int(seed) & 0xFFFFFFFF, TICKET, zlib.crc32(repr(key).encode())))


def _short(lines: list, people: str) -> str:
    for l in lines:
        if l["id"] == people:
            return (l.get("name") or people).split(" (")[0]
    return people.replace("_", " ")


def _dist(a_lat, a_lon, b_lat, b_lon) -> float:
    la1, la2 = math.radians(a_lat), math.radians(b_lat)
    d = math.sin(la1) * math.sin(la2) + math.cos(la1) * math.cos(la2) * math.cos(math.radians(a_lon - b_lon))
    return math.acos(max(-1.0, min(1.0, d)))


class _In:
    def __init__(self, cultures, meta, seed):
        self.C = cultures
        self.known = ((meta.get("techtree") or {}).get("known") or {})
        self.seed = seed
        self.by_people: dict = {}
        for c in cultures:
            self.by_people.setdefault(c["people"], []).append(c)

    def literate(self, people: str, ago: float) -> bool:
        w = (self.known.get(people) or {}).get("writing")
        return bool(w) and w[0] >= ago - 1e-9

    def alive(self, c: dict, ago: float) -> bool:
        return c["born_kyr"] >= ago - 1e-9 and (c.get("ended_kyr") is None or c["ended_kyr"] < ago - 1e-9)

    def culture_at(self, people: str, lat, lon, ago: float):
        cs = [c for c in self.by_people.get(people, []) if self.alive(c, ago) and c.get("lat") is not None]
        if not cs or lat is None:
            return None
        return min(cs, key=lambda c: (_dist(lat, lon, c["lat"], c["lon"]), c["id"]))["id"]

    def end_of(self, ci: int) -> float:
        e = self.C[ci].get("ended_kyr")
        return 0.0 if e is None else float(e)


def _hold(holders: list, ci, frm: float, to: float, I: _In) -> None:
    if ci is None:
        return
    to = max(to, I.end_of(ci))
    if frm > to + 1e-9:
        holders.append({"culture": int(ci), "from_kyr": round(frm, 3), "to_kyr": round(to, 3) if to > 1e-9 else None})


def _faiths(I: _In, gods: dict, out: list) -> None:
    F = ((gods or {}).get("faiths") or {}).get("list") or []
    G = (gods or {}).get("cultures") or {}
    for f in F:
        oc, t0 = f.get("origin_culture"), float(f["founded_kyr"])
        if oc is None or not I.literate(I.C[oc]["people"], t0):
            continue
        base = P_SCHISM if f.get("how") == "schism" else P_FAITH
        n = len(f.get("cultures_ever") or [])
        p = base * min(1.0, n / FAITH_FULL)
        r = _rng(I.seed, "faith", f["id"])
        if r.random() >= p:
            continue
        end = float(f.get("ended_kyr") or 0.0)
        holders: list = []
        for c in sorted({oc, *(f.get("cultures_ever") or [])}):
            if c != oc and r.random() >= P_ADOPT:
                continue
            hist = (G.get(str(c)) or {}).get("faiths") or []
            spans = []
            for i, (k, fid) in enumerate(hist):  # (oldest first: [kyr ago, faith id]; each lasts to the next)
                if fid == f["id"]:
                    nxt = hist[i + 1][0] if i + 1 < len(hist) else 0.0
                    spans.append((min(float(k), t0), max(float(nxt), end)))
            if not spans and c == oc:
                spans = [(t0, end)]
            for a, b in spans:
                _hold(holders, c, a, b, I)
        word = "Schism" if f.get("how") == "schism" else "Faith"
        out.append({"kind": "schism" if f.get("how") == "schism" else "faith", "epoch_kyr": round(t0, 3), "culture": oc,
                    "label": f"the {str(f['core']).title()} {word}", "faith": f["id"], "p": round(p, 3),
                    "event": f"{f['name']} was {'split off' if f.get('how') == 'schism' else 'founded'}", "holders": holders,
                    "fade": "ends with the faith" + (" (it ended)" if f.get("ended_kyr") is not None else "")})


def _state_holders(I: _In, rec: dict, cul_of, frm: float, r) -> tuple[list, str]:
    fell = rec.get("fell_kyr")
    end = float(fell or 0.0)
    holders: list = []
    rulers = [cul_of(u) for _, u in rec.get("rulers") or []]
    keep = end
    why = "kept while the state lives"
    if fell is not None:
        if r.random() < P_OUTLIVE:
            keep = max(0.0, end - float(r.exponential(OUTLIVE_KYR)))
            why = "kept by its rulers after the state fell" + ("" if keep > 0 else ", to this day")
        else:
            why = "ended when the state fell"
    for ci in dict.fromkeys(c for c in rulers if c is not None):
        _hold(holders, ci, frm, keep, I)
    for u in rec.get("subjects") or []:
        ci = cul_of(u)
        if ci is not None and ci not in rulers and r.random() < P_ADOPT_SUBJECT:
            _hold(holders, ci, min(frm, I.C[ci]["born_kyr"]), end, I)
    return holders, why


def _states(I: _In, pol: dict, out: list) -> None:
    P = (pol or {}).get("polities") or []
    cm = (pol or {}).get("cultures") or {}
    cul_of = lambda u: (cm.get(u) or {}).get("id")  # noqa: E731
    for rec in P:
        rank = next(((a, t) for a, t in rec.get("tiers") or [] if t in STATE_TIERS), None)
        if rank is None and rec.get("tier_peak") in STATE_TIERS:
            rank = (rec["founded_kyr"], rec["tier_peak"])
        if rank is not None:
            t0, tier = float(rank[0]), rec.get("tier_peak") if rec.get("tier_peak") in STATE_TIERS else rank[1]
            ruler = cul_of(_at(rec.get("rulers") or [], t0))
            if ruler is not None and I.literate(I.C[ruler]["people"], t0):
                life = t0 - float(rec.get("fell_kyr") or 0.0)
                p = P_STATE.get(tier, 0.0) * min(1.0, life / LIFE_FULL_KYR)
                r = _rng(I.seed, "state", rec["id"])
                if r.random() < p:
                    holders, why = _state_holders(I, rec, cul_of, t0, r)
                    nm = _place(rec)
                    rise = abs(t0 - float(rec["founded_kyr"])) > 1e-6
                    out.append({"kind": "state", "epoch_kyr": round(t0, 3), "culture": ruler, "state": rec["id"], "p": round(p, 3),
                                "label": f"the {'Rise' if rise else 'Founding'} of {nm}",
                                "event": f"{rec['name']} {'rose to ' + ('an' if tier == 'empire' else 'a') + ' ' + tier if rise else 'was founded'}",
                                "holders": holders, "fade": why})
        if rec.get("fell_how") == "conquered" and rec.get("fell_by") is not None and 0 <= rec["fell_by"] < len(P):
            win = P[rec["fell_by"]]
            t0 = float(rec["fell_kyr"])
            if win.get("tier_peak") not in STATE_TIERS:
                continue
            ruler = cul_of(_at(win.get("rulers") or [], t0))
            if ruler is None or not I.literate(I.C[ruler]["people"], t0):
                continue
            r = _rng(I.seed, "conquest", rec["id"])
            if r.random() >= P_CONQUEST:
                continue
            holders, why = _state_holders(I, win, cul_of, t0, r)
            out.append({"kind": "conquest", "epoch_kyr": round(t0, 3), "culture": ruler, "state": win["id"], "p": P_CONQUEST,
                        "label": f"the Conquest of {_place(rec)}", "event": f"{win['name']} conquered {rec['name']}", "holders": holders,
                        "fade": why})


def _at(spans: list, ago: float):
    out = spans[0][1] if spans else None
    for a, v in spans:
        if a >= ago - 1e-9:
            out = v
    return out


def _place(rec: dict) -> str:
    nm = str(rec.get("name") or "").removeprefix("Chiefdom in ")
    nm = nm.split(" (")[0]
    if not nm:
        return f"state {rec.get('id')}"
    if nm.split(" ")[1:2] == ["of"] and nm.split(" ")[0].lower().replace("-", " ").split(" ")[0] in ("north", "south", "east", "west"):
        return "the " + nm[:1].lower() + nm[1:]  # ('the west of Simath', as the place reads in a sentence)
    return nm[:1].upper() + nm[1:]


def _local(I: _In, out: list, kind: str, key, people: str, lat, lon, t0: float, p: float, label: str, event: str) -> None:
    if not I.literate(people, t0):
        return
    r = _rng(I.seed, kind, key)
    if r.random() >= p:
        return
    ci = I.culture_at(people, lat, lon, t0)
    if ci is None:
        return
    holders: list = []
    _hold(holders, ci, t0, max(0.0, t0 - float(r.exponential(LOCAL_KYR))), I)
    out.append({"kind": kind, "epoch_kyr": round(t0, 3), "culture": ci, "p": p, "label": label, "event": event, "holders": holders,
                "fade": "kept by the culture that lived through it, with no state or faith behind it"})


def _incursions(I: _In, meta: dict, lines: list, out: list) -> None:
    for k, x in enumerate(((meta.get("contacts") or {}).get("incursions") or [])):
        by = _short(lines, x["by"])
        verb = "settled among" if x.get("kind") == "settled_among" else "drove out"
        _local(I, out, "incursion", k, x["over"], x.get("lat"), x.get("lon"), float(x["ago_kyr"]), P_INCURSION,
               f"the Coming of the {by}", f"the {by} came and {verb} the {_short(lines, x['over'])}")


def _sites(I: _In, sites: list, names: dict, out: list) -> None:
    for s in sites or []:
        if s.get("tier_peak") not in ("town", "city"):
            continue
        nm = names.get(s["id"]) or s.get("place") or f"site {s['id']}"
        for ev in s.get("war") or []:
            ago, what, by = float(ev[0]), ev[1], ev[2] if len(ev) > 2 else None
            if what not in ("razed", "sacked"):
                continue
            holder = _at(s.get("holders") or [], ago + 1e-6) or s.get("holder")
            if holder is None:
                continue
            _local(I, out, what, s["id"], holder, s.get("lat"), s.get("lon"), ago, P_RAZED if what == "razed" else P_SACKED,
                   f"the {'Burning' if what == 'razed' else 'Sack'} of {nm}", f"the {s['tier_peak']} {nm} was {what}" + (f" by the {by}" if by else ""))
        if s.get("why") == "the river moved away" and s.get("abandoned_kyr") is not None:
            ago = float(s["abandoned_kyr"])
            holder = _at(s.get("holders") or [], ago + 1e-6) or s.get("holder")
            if holder:
                _local(I, out, "flood", s["id"], holder, s.get("lat"), s.get("lon"), ago, P_FLOOD, f"the Flood of {nm}",
                       f"the river left the {s['tier_peak']} {nm} and it was abandoned")


def derive(cultures: list[dict], meta: dict, lines: list[dict] | None = None, gods: dict | None = None, polities: dict | None = None,
           sites: list | None = None, place_names: dict | None = None, seed: int | None = None) -> dict:
    """The calendars of a run: {"format", "calendars": [{id, name, epoch_kyr, kind, event, culture, holders: [{culture, from_kyr,
    to_kyr (None: in use now)}], ended_kyr, alive, p, fade}], "by_culture": {culture id: [calendar ids]}, "constants", "sources"}.
    cultures: cultures.json records (names from the slot); the rest as the read-outs give them (any may be None)."""
    lines = lines or meta.get("lineages") or []
    seed = int(meta.get("seed") or 0) if seed is None else seed
    I = _In(cultures, meta, seed)
    out: list = []
    _faiths(I, gods, out)
    _states(I, polities, out)
    _incursions(I, meta, lines, out)
    _sites(I, sites, place_names or {}, out)
    out = [x for x in out if x["holders"]]
    out.sort(key=lambda x: (-x["epoch_kyr"], x["kind"], x["label"]))
    for i, x in enumerate(out):
        x["id"] = i
        x["culture_name"] = cultures[x["culture"]]["name"]
        x["name"] = x["label"]
        ends = [h["to_kyr"] for h in x["holders"]]
        x["alive"] = any(e is None for e in ends)
        x["ended_kyr"] = None if x["alive"] else max(ends)
    seen = {}
    for x in out:
        seen[x["name"]] = seen.get(x["name"], 0) + 1
    k: dict = {}
    for x in out:  # (still shared, oldest first: 'the Founding of Iligya II' is the second)
        nm = x["name"]
        if seen[nm] > 1:
            k[nm] = k.get(nm, 0) + 1
            x["name"] = f"{nm} {_ROMAN[k[nm] - 1]}" if k[nm] <= len(_ROMAN) else f"{nm} {k[nm]}"
    by: dict = {}
    for x in out:
        for h in x["holders"]:
            by.setdefault(str(h["culture"]), [])
            if x["id"] not in by[str(h["culture"])]:
                by[str(h["culture"])].append(x["id"])
    return {"format": "procgen-calendars/1", "version": VERSION, "calendars": out, "by_culture": by,
            "counts": {"all": len(out), "alive": sum(x["alive"] for x in out),
                       "by_kind": {kd: sum(x["kind"] == kd for x in out) for kd in sorted({x["kind"] for x in out})}},
            "constants": {"p_faith": P_FAITH, "p_schism": P_SCHISM, "faith_full": FAITH_FULL, "p_state": P_STATE,
                          "life_full_kyr": LIFE_FULL_KYR, "p_conquest": P_CONQUEST, "p_incursion": P_INCURSION, "p_razed": P_RAZED,
                          "p_sacked": P_SACKED, "p_flood": P_FLOOD, "p_adopt": P_ADOPT, "p_adopt_subject": P_ADOPT_SUBJECT,
                          "p_outlive": P_OUTLIVE, "outlive_kyr": OUTLIVE_KYR, "local_kyr": LOCAL_KYR},
            "rule": "A culture that keeps written records may start counting the years from a notable event it lives through: a faith "
                    "founded or split, a state founded or risen to a state or empire, a conquest, an incursion, a town razed or sacked, "
                    "a town lost to the river. The count spreads with the state or faith and fades without one. Year 1 is the event's "
                    "year.", "sources": SOURCES}


_ROMAN = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")


def calendar_of(doc: dict | None, cid) -> dict | None:
    """The calendar {name, epoch_kyr, ...} with id `cid` (int or str) in a calendars doc, None if there is none."""
    if doc is None or cid in (None, ""):
        return None
    try:
        i = int(cid)
    except (TypeError, ValueError):
        return None
    cs = doc.get("calendars") or []
    return cs[i] if 0 <= i < len(cs) and cs[i]["id"] == i else None
