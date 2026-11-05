"""Invasions you schedule (PW-1433), v0 at the polity level: rows Daniel writes in the workbench ("the antelope-kin come down on the
humans around year 1400"), saved in the run's authored.json beside the faiths he wrote, fed to the polities read-out's war step
(polities.derive(invasions=...), lane 175's hook) and read out row by row: "it happened" (who took what from whom, when, how much
land) or "it didn't" and why (no state of the invaders then, no border with the victims, the odds, or the chance).

In plain words: a row never changes the peoples history (polities inside the history are v4). It changes only the polities read
after the run: inside its window, a state of the invaders that borders a polity of the victims fights it with a raised chance (light:
twice the usual, strong: four times, which is certain at war v0's 1 in 4, and a strong row needs no strength edge either).

A row: {"id", "who": {"people": id} | {"culture": uid}, "whom": the same or None (anyone they border), "from_kyr", "to_kyr" (the
window, kyr ago; one year is the century step around it), "year_text" (as typed, NumFmt.parseDate), "place": [lat, lon] or None (the
invaders' land must reach within FROM_KM of it), "strength": "light" | "strong"}. A strong row also reaches (PW-1450, owner D50: REACH_RULE): a war band if the invaders
rule only chiefdoms, an expedition across the gap to the victims if no state of theirs borders them, further for mobile peoples
(mobility()). A people names its groups and daughter lines too
(the antelope-kin row covers the antelope-kin of the steppe); a culture is its cultures.json uid (PW-1283).
"""

from __future__ import annotations

import heapq
import math

import numpy as np

VERSION = 2  # (bump when what a row does changes: the server's cached polities docs with rows are remade; polities.VERSION keys the rest)
MAX_ROWS = 40  # (a sane cap per run)
STRENGTHS = ("light", "strong")
FROM_KM = 1000.0  # judgement: "from where" holds when the invading state has land within 1,000 km of the place picked (a state's reach is
# ~150-300 km from its capital, an empire's a few times that: 1,000 km is "from that part of the continent", not "from that town")


# ---- reach (PW-1450, owner D50: B, C and the mobile peoples). Only a strong row reaches; a light one keeps v0's shared border.
WAR_BAND = True  # (C) a strong row whose invaders rule only chiefdoms seats a state at their largest town that stood last century
EXPEDITION = True  # (B) a strong row whose invaders' states border no victim polity sends the nearest one across the gap
FOREIGN_X = 2.0  # judgement: a km through a third people's polity costs a mobile people twice an open km (riding round its towns);
# a settled people's expedition crosses only unruled land (and sea, with boats), as D50's B reads
CAMPAIGN_KM = None  # OPEN (PW-1478, desk D56): an expedition's budget in foot-km before mobility. None: the state's own reach again
# (option A, now); a number (D56's lean B: 1000.0) is a fixed campaign range. The one place both paths read it (campaign_budget):
# the read-out (polities.derive) and the polities inside the history (history.polity_live)


def campaign_budget(reach: float, mob: float) -> float:
    """An expedition's budget in foot-km: the state's own reach (or CAMPAIGN_KM, PW-1478) x its people's mobility (mobility)."""
    return (reach if CAMPAIGN_KM is None else float(CAMPAIGN_KM)) * mob


def mobility(line: dict | None) -> float:
    """How far a people's expedition reaches, as a multiple of its state's own reach: the model's own mobility numbers, nothing new.
    The best of its traits' speed in the spread (spec.TRAITS: nomadic x2, the history's own pace for them) and 1 + its way's
    mobility (spec.WAY_MOBILE: pastoral nomads 1, transhumants 0.6, agro-pastoralists 0.3, owner on PW-936). A settled people: 1.
    Riding is not here: _reach already makes a ridden km cost two thirds (RIDE_X), so a mounted horde has both."""
    from .spec import TRAITS, WAY_MOBILE
    if not line:
        return 1.0
    sp = [float((TRAITS.get(t) or {}).get("speed", 1.0)) for t in line.get("traits") or []]
    return max([1.0, 1.0 + float(WAY_MOBILE.get(line.get("way") or "", 0.0))] + sp)


def expedition(seeds, budget, land_x, sea_x, mobile, owner, me, targets, off, idx, ekm, edz, sea, blocked, climb_m):
    """The nearest polity in `targets` an expedition reaches from the cells `seeds` (a state's land) within `budget` foot-km: a
    Dijkstra like polities._claim's (land km x land_x x (1 + climb / climb_m), sea km x sea_x, no sea when sea_x < 0, never over
    `blocked` (ice)), over unruled cells, and when `mobile` also through other polities' land at FOREIGN_X. Returns (target polity,
    the corridor's unruled cells, its foot-km, its km) or None."""
    dist: dict = {}
    km: dict = {}
    prev: dict = {}
    h = []
    for c in seeds:
        c = int(c)
        dist[c], km[c] = 0.0, 0.0
        h.append((0.0, c))
    heapq.heapify(h)
    while h:
        d, a = heapq.heappop(h)
        if d > dist.get(a, np.inf):
            continue
        oa = owner[a]
        if oa in targets:
            path = []
            c = a
            while c in prev:
                c = prev[c]
                if owner[c] < 0:
                    path.append(c)
            return int(oa), np.asarray(path[::-1], np.int64), float(d), float(km[a])
        for e in range(off[a], off[a + 1]):
            b = int(idx[e])
            ob = owner[b]
            if blocked[b] or ob == me:
                continue
            if ob >= 0 and ob not in targets and not mobile:
                continue
            if sea[a] or sea[b]:
                if sea_x < 0:
                    continue
                c = ekm[e] * sea_x
            else:
                c = ekm[e] * land_x * (1.0 + edz[e] / climb_m if climb_m > 0 else 1.0)
            if ob >= 0 and ob not in targets:
                c *= FOREIGN_X
            nd = d + c
            if nd <= budget and nd < dist.get(b, np.inf):
                dist[b], km[b], prev[b] = nd, km[a] + ekm[e], a
                heapq.heappush(h, (nd, b))
    return None


def _side(x, what: str, bad) -> dict | None:
    """A row's who or whom in its checked form: {"people": id} or {"culture": uid}; a bare string is a people id (lane 175's hook)."""
    if x is None or x == "" or x == {}:
        return None
    if isinstance(x, str):
        return {"people": x[:80]}
    if isinstance(x, dict):
        if isinstance(x.get("culture"), str) and x["culture"]:
            return {"culture": x["culture"][:160]}
        if isinstance(x.get("people"), str) and x["people"]:
            return {"people": x["people"][:80]}
    bad(f"{what} must be a people or a culture")
    return None


def clean(rows, strict: bool = True) -> tuple[list, list]:
    """Authored invasion rows in their checked form (module docstring). strict (the POST): raise ValueError at the first malformed
    row; else skip it and say so. Only the shape is checked here: a people or culture the run lacks, invaders who are the victims or a
    window after the present are saved as written and explained by the read-out (readout()), never refused or crashed on."""
    out, notes = [], []

    def bad(msg):
        if strict:
            raise ValueError(msg)
        notes.append(msg)
    if rows is None:
        return out, notes
    if not isinstance(rows, list):
        bad("invasions must be a list")
        return out, notes
    if len(rows) > MAX_ROWS:
        bad(f"at most {MAX_ROWS} invasions")
        rows = rows[:MAX_ROWS]
    ids: set = set()
    for i, r in enumerate(rows):
        nm = f"invasion {i + 1}"
        if not isinstance(r, dict):
            bad(f"{nm}: not an object")
            continue
        n0 = len(notes)
        who = _side(r.get("who"), f"{nm}: who", bad)
        whom = _side(r.get("whom"), f"{nm}: whom", bad)
        if len(notes) > n0:
            continue
        if who is None:
            bad(f"{nm}: pick who invades (a people or a culture)")
            continue
        try:
            a = float(r.get("from_kyr"))
            b = float(r.get("to_kyr", a) if r.get("to_kyr") is not None else a)
        except (TypeError, ValueError):
            a = b = float("nan")
        if not (math.isfinite(a) and math.isfinite(b)):
            bad(f"{nm}: its year could not be read")
            continue
        st = r.get("strength") or "light"
        if st not in STRENGTHS:
            bad(f"{nm}: strength must be light or strong")
            continue
        pl = r.get("place")
        if pl is not None:
            try:
                lat, lon = float(pl[0]), float(pl[1])
                if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90):
                    raise ValueError
                pl = [round(lat, 3), round((lon + 180.0) % 360.0 - 180.0, 3)]
            except (TypeError, ValueError, IndexError, KeyError):
                bad(f"{nm}: its place must be [latitude, longitude]")
                continue
        rid = str(r.get("id") or f"i{i + 1}")[:40]
        while rid in ids:
            rid += "x"
        ids.add(rid)
        out.append({"id": rid, "who": who, "whom": whom, "from_kyr": round(max(a, b), 6), "to_kyr": round(min(a, b), 6),
                    "year_text": str(r.get("year_text") or "")[:80], "place": pl, "strength": st})
    return out, notes


# ------------------------------------------------------------------ into the polities' war step

def hook_rows(rows, R, step_kyr: float) -> list[dict]:
    """The rows as polities.war_v0 reads them, one per written row (row["i"] is its place in `rows`): who/whom as written, the window
    widened to the century step around a single year (half a step either side: "around year 1400" is the step nearest it), and the
    place as a mask of the cells within FROM_KM of it. R: polities._Run. A row that can never match (a people the run lacks) is kept:
    it finds no state, and the read-out says why."""
    out = []
    cells = np.asarray(R.g.centers, float)
    for i, r in enumerate(rows or []):
        a, b = float(r["from_kyr"]), float(r.get("to_kyr", r["from_kyr"]))
        if a - b < step_kyr - 1e-9:
            mid, h = (a + b) / 2, step_kyr / 2 - 1e-6
            a, b = max(a, mid + h), min(b, mid - h)
        h = {"i": i, "who": r["who"], "whom": r.get("whom"), "from_kyr": a, "to_kyr": b, "strength": r.get("strength") or "light"}
        if r.get("place"):
            la, lo = np.radians(r["place"][0]), np.radians(r["place"][1])
            p = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
            h["near"] = np.flatnonzero(cells @ p >= np.cos(FROM_KM / 6371.0))
        out.append(h)
    return out


def ancestors(lines: list) -> dict:
    """people id -> the ids a row may name it by: itself, the people it is a group of, and every stem above (a row naming the
    antelope-kin covers the antelope-kin of the steppe; one naming the humans, the human farmers)."""
    by = {l["id"]: l for l in lines}
    memo: dict = {}

    def up(p, seen=()):
        if p in memo:
            return memo[p]
        out = {p}
        l = by.get(p) or {}
        for q in [l.get("group_of")] + list(l.get("parents") or []):
            if q and q not in seen and q != p:
                out |= up(q, seen + (p,))
        memo[p] = out
        return out
    return {p: frozenset(up(p)) for p in by}


def new_log() -> dict:
    """What war_v0 saw of one row, summed over the century steps of its window (polities.war_v0 fills it; readout() reads it)."""
    return {"steps": 0, "state": 0, "state_far": 0, "chief": 0, "state_new": 0, "victim": 0, "victim_dragon": 0, "border": 0, "odds": 0,
            "outranked": 0, "shadowed": 0, "gone": 0, "chance": 0, "p": 0.0, "took": [], "state_kyr": [],
            "exped": [], "exped_fail": 0, "exped_km": 0.0, "exped_mobile": False, "war_band": []}  # (PW-1450: each expedition {ago_kyr, winner_id, loser_id, km,
    # foot_km, corridor_cells, mobility}; tries that reached nothing; the largest budget tried, foot-km; [ago, polity record] per war band)


# ------------------------------------------------------------------ the read-out

def _label(side, R) -> str:
    if side is None:
        return "anyone they border"
    if "culture" in side:
        i = {u: k for k, u in enumerate(R.uids)}.get(side["culture"])
        return R.C["cultures"][i]["name"] if i is not None else f"culture {side['culture']}"
    return R.lname.get(side["people"], side["people"])


def readout(rows: list, logs: list, polities: list, agos: list, R, anc: dict | None = None) -> list[dict]:
    """One read-out per written row: {id, ...the row, happened, text, why, took: [{ago_kyr, winner, loser, km2}], km2}. Odd rows (a
    people or culture the run lacks, invaders who are the victims, a window after the present or before the first century the
    polities are read from) say so; nothing here raises on a row."""
    uids = set(R.uids)
    first, last = (max(agos), min(agos)) if agos else (0.0, 0.0)
    out = []
    for r, L in zip(rows, logs):
        who, whom = _label(r["who"], R), _label(r.get("whom"), R)
        o = {k: r.get(k) for k in ("id", "who", "whom", "from_kyr", "to_kyr", "year_text", "place", "strength")}
        o |= {"who_name": who, "whom_name": whom, "happened": False, "took": [], "km2": 0, "why": None}
        why = None
        for side, nm in ((r["who"], "invaders"), (r.get("whom"), "victims")):
            if side is None:
                continue
            if "culture" in side and side["culture"] not in uids:
                why = why or f"the {nm} are no culture of this run ({side['culture']})"
            if "people" in side and side["people"] not in R.lidx:
                why = why or f"the {nm} are no people of this run ({side['people']})"
        if why is None and r.get("whom") is not None and r["who"] == r["whom"]:
            why = "the invaders are the victims: a people (or culture) never invades itself"
        if why is None and r["from_kyr"] < -1e-9:
            why = "its window is after the present"
        if why is None and agos and r["to_kyr"] > first + step_of(agos) / 2:
            why = f"its window ends before the first century the polities are read from ({first:g} kyr ago: before that no people has both chiefdoms and writing)"
        if why is None and L["steps"] == 0:
            why = "no century step of the polities falls in its window"
        from .polities import name_at  # (each side as it was called then: the people holding its capital, PW-1451)
        if why is None and L["took"]:
            o["happened"] = True
            for ago, li, wi, km2 in L["took"]:
                o["took"].append({"ago_kyr": ago, "winner": name_at(polities[wi], ago), "winner_id": wi, "loser": name_at(polities[li], ago), "loser_id": li, "km2": int(round(km2))})
            o["km2"] = int(round(sum(t["km2"] for t in o["took"])))
            ex = [e for e in L.get("exped") or [] if any(t["ago_kyr"] == e["ago_kyr"] and t["loser_id"] == e["loser_id"] for t in o["took"])]
            if ex:  # (PW-1450: how far it reached: the expeditions that led to a conquest)
                o["reach"] = [{**e, "winner": name_at(polities[e["winner_id"]], e["ago_kyr"]), "loser": name_at(polities[e["loser_id"]], e["ago_kyr"])} for e in ex]
        elif why is None:
            them = f"the {who}" if "people" in r["who"] else who
            vic = "any polity" if r.get("whom") is None else (f"the {whom}" if "people" in r["whom"] else whom)
            if not L["state"]:
                if L["state_far"]:
                    why = f"{them} had a state then, but none with land within {FROM_KM:,.0f} km of the place you picked"
                elif L["state_new"]:
                    why = f"{them} had a state then only in the century it was founded (a polity fights from its second century on)"
                elif L["chief"]:
                    why = f"{them} had only chiefdoms then (war v0: only a state attacks)"
                else:
                    why = f"no state of {them} existed then"
            elif not L["victim"]:
                why = (f"{vic} ruled only dragon realms then, and war v0 neither attacks a dragon realm nor lets one attack" if L["victim_dragon"]
                       else f"{vic} ruled no polity then (a people with no chiefdom or state cannot be conquered)")
            elif not L["border"]:
                why = f"no state of {them} bordered a polity of {vic} then"
                if L.get("exped_fail"):
                    why += (f", and none reached one on an expedition (the furthest went {L['exped_km']:,.0f} km on foot over flat "
                            "ground, more with riding and roads, across unruled land" + (" or through others' land" if L.get("exped_mobile") else "") + "; "
                            + (f"the nearest polity of theirs lay {L['exped_need']:,.0f} km away on the same terms)" if math.isfinite(L.get("exped_need", math.inf))
                               else f"none lay within {L['exped_need_gt']:,.0f} km on the same terms)" if L.get("exped_need_gt")
                               else "none could be reached at all that way)"))
            elif L["shadowed"] and not (L["outranked"] or L["gone"] or L["chance"]):
                why = "another invasion you wrote, of the same invaders on the same victims in the same years, led every attack"
            elif L["odds"] and not (L["outranked"] or L["gone"] or L["chance"]):
                why = f"{them} were never half again as strong as the {('neighbours' if r.get('whom') is None else 'victims')} they bordered (a light invasion keeps war's odds; a strong one waives them)"
            elif L["outranked"] and not L["chance"]:
                why = f"a stronger neighbour attacked {vic} first each time"
            elif L["gone"] and not L["chance"]:
                why = f"the invading state was itself conquered that century"
            else:
                why = f"the chance failed: {L['chance']} tr{'y' if L['chance'] == 1 else 'ies'} at {L['p']:.0%} per century"
        o["why"] = why
        if L.get("war_band"):  # (PW-1450: the centuries a war band ruled for the row)
            o["war_band"] = [{"ago_kyr": a, "polity": name_at(polities[i], a), "polity_id": i} for a, i in L["war_band"]]
        sk = L["state_kyr"]  # (the hint for a better window: the centuries in which the invaders ruled a state at all)
        o["states"] = {"centuries": len(sk), "from_kyr": max(sk) if sk else None, "to_kyr": min(sk) if sk else None}
        out.append(o)
    return out


REACH_RULE = ("A strong invasion also reaches (owner D50). If the invaders rule only chiefdoms, their largest town rules as a state for "
              "the window (a war band). If none of their states borders the victims, the one nearest sends an expedition: it "
              "crosses unruled land (and sea, with boats) within its own reach again, claims that corridor for the century and "
              "attacks the first polity of the victims it meets. Mobile peoples reach further: nomads and pastoral nomads twice as "
              "far (transhumant herders 1.6 times), and they may ride through other peoples' states at half pace; riding and roads "
              "make every km cheaper on top. A light invasion still needs a shared border.")


def step_of(agos: list) -> float:
    return abs(agos[0] - agos[1]) if len(agos) > 1 else 0.1


RULE = ("An invasion you write changes only the states and wars read after the run, never the peoples history. In its window "
        "(one year: the century around it), a state of the invaders that borders a polity of the victims attacks it with twice war's "
        "usual chance per century (light) or four times, which is certain (strong). A strong invasion also needs no edge in strength; "
        "a light one still needs the invaders half again as strong. Invaders are a people (with its groups and daughter lines) or one "
        f"culture; a place means the invading state must hold land within {FROM_KM:,.0f} km of it. Dragon realms neither attack nor are "
        "attacked in war v0.")
