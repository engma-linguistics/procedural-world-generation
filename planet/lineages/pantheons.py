"""Regional pantheons v0 (PW-1523, design docs/review/culture/faiths/pantheon1.md section 4, Daniel's rulings D68 of 2026-11-08).

In plain words: in a few regions, the gods of different peoples come to be seen as one another's (the Romans' "Sulis Minerva" at
Bath): the sea god of the leonin and the sea god of the tritons both sit in "the sea seat of the Luki pantheon", each keeping its own
name, people and future. Each people keeps its own god (its patron), which is never matched away. A pantheon gathers around a hub: a
culture that has held towns on a border of several peoples for centuries, or the ruler of a state of several peoples (D68 3A: rare,
about 2-8 per world). Its reach is the open cultures within PANTHEON_KM of the hub (D68 2B); a smaller pantheon whose hub falls inside
a bigger one's reach joins it (Nippur's Enlil under Babylon's Marduk). A culture whose faith refuses other gods (today: a missionary
faith, gods.Faith.missionary; PW-1520 has no separate "exclusive" flag) cannot join, and one that converts to such a faith leaves its
seats (D68 4A). Now and then, under a ruler of several peoples, a brand-new joint god is made for a seat, as Ptolemy's Serapis was for
the Greeks and Egyptians (D68 1C). An open culture with no god of a seat's domain may take the seat's god in (adopted, as Rome took in
Cybele).

A read-out like the minority faiths (PW-1489): it reads the gods (gods.Pantheons) frame by frame and never writes into them, and it draws
on its own random stream, so every being, faith and conversion is the same with it on or off (tests/test_pantheons.py). The adopted and
joint gods live here, not among a culture's own beings: they are worshipped beside its gods and never lead it in v0.

Every number below is a JUDGEMENT unless it names a source; the scales are sourced in pantheon1.md and domains1.md.
"""

from __future__ import annotations

import math

import numpy as np

from . import gods as G

TAU_IDENT = 0.5  # kyr, JUDGEMENT on a sourced scale: two open cultures' alike gods are matched within centuries (Hachiman: a combined kami in the 7th century, a bodhisattva in the 8th: pantheon1.md [SHIN, HONJI])
TAU_ADOPT = 2.0  # kyr, JUDGEMENT: a few times slower, a culture takes in a seat's god it has none of (Cybele came to Rome in 204 BC, Isis's cult spread over centuries: [CYB, ISIS])
RULE_X = 2.0  # JUDGEMENT: matching is this much faster when the culture is ruled by the hub (one state: interpretatio under Rome, the Achaemenids)
HUB_KYR = 0.4  # kyr, JUDGEMENT (design: 0.3-0.5): a hub must hold for this long, so a passing conquest or a brief market seeds nothing (D68 3A)
HUB_MIX = 0.25  # JUDGEMENT: a town hub's border faces other peoples' cultures at least this much (a mixed city's hinterland)
HUB_URBAN = 0.1  # JUDGEMENT: a town hub has at least this share of its people in towns (a trading city, not a market village; PW-1520's urban share)
HUB_SUBJ = 2.0  # JUDGEMENT, set on 0141d1, a24559, a2b637, 3e0eb4 for D68 3A (2-8 per world): an empire hub rules at least twice as much other peoples' land as its own (an empire, not a kingdom with a border march)
HUB_PEOPLES = 2  # an empire hub rules cultures of at least this many peoples, its own included
TAU_HUB_MEM = 0.5  # kyr, JUDGEMENT: a pantheon whose hub stops qualifying lasts this long, then breaks up
PANTHEON_KM = 1200.0  # km, D68 2B: about 800-1,500 km of the hub city, a kingdom's span
TOL_OPEN = 0.5  # JUDGEMENT (design: around the median): a culture this religiously tolerant (attitudes.py, PW-1520) is open to other peoples' gods
IND_GOD = G.CONVERT_MIN  # a being this individuated (temples) is a god that can be matched; spirits stay bound to their land
JOINT_P = 0.1  # JUDGEMENT (D68 1C, "sometimes"): the chance that a seat founded under a ruler of several peoples also gets a brand-new joint god (Serapis: one such god made by royal policy, beside the many plain matchings of interpretatio)
ADOPT_MAX = 3  # JUDGEMENT: a culture takes in at most this many gods from its pantheons
R_KM = G.R_KM

RULE = ("A pantheon gathers around a hub: a culture with towns whose border faces other peoples for HUB_KYR, or the ruler of cultures of "
        "several peoples for HUB_KYR, when the hub is open (religious tolerance at least TOL_OPEN and a faith that does not refuse other gods). "
        "Its reach is the open cultures whose centre lies within PANTHEON_KM of the hub's. Inside it, a culture's god (individuated to temples, "
        "not its people's own patron) and another people's alike god (same leading domain, cosine at least FUSE_COS) are matched as a chance "
        "in time (TAU_IDENT, faster under one ruler): both sit in a shared seat, each keeping its name and people. Under a ruler of several "
        "peoples a new seat sometimes gets a brand-new joint god (JOINT_P). An open culture with no god of a seat's domain may adopt the seat's "
        "head god (TAU_ADOPT). A god leaves its seat when its culture closes, leaves the reach, or drifts off the domain; a seat of one people "
        "breaks up; a pantheon whose hub fails for TAU_HUB_MEM ends, at once if the hub closes; a pantheon whose hub lies in a bigger one's "
        "reach joins it. Read-out only: the gods and faiths are untouched.")


class Extra(G.Being):
    """An adopted or joint god (it lives here, not among a culture's own beings); ind_cap: the individuation it came with."""
    __slots__ = ("ind_cap",)


def _unit(v) -> np.ndarray:
    v = np.asarray(v, float)
    return v / (np.linalg.norm(v) + 1e-12)


def _km(a: np.ndarray, b: np.ndarray) -> float:
    return R_KM * math.acos(max(-1.0, min(1.0, float(a @ b))))


def _latlon(u: np.ndarray) -> list:
    return [round(math.degrees(math.asin(max(-1.0, min(1.0, float(u[2]))))), 2), round(math.degrees(math.atan2(float(u[1]), float(u[0]))), 2)]


def _top(w) -> str:
    return G.DOMAINS[int(np.argmax(w))]


class Regional:
    """The regional pantheons of one replay, fed after each gods frame (step()). No I/O."""

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng((int(seed), 1523))  # (its own stream: gods.Pantheons.rng is never drawn from)
        self.pans: list[dict] = []
        self.seats: list[dict] = []
        self.seat_of: dict[int, int] = {}  # id(being object) -> seat id
        self.extra: list = []  # the adopted and joint gods (gods.Being objects, id assigned at output)
        self.adopted_n: dict[int, int] = {}
        self.hub_t: dict[int, list] = {}  # culture -> [kyr it has qualified, kind]
        self.people: dict[int, str] = {}
        self.centre: dict[int, np.ndarray] = {}
        self.events: list[dict] = []
        self.counts = {"pantheons": 0, "joined": 0, "identified": 0, "seats": 0, "joint": 0, "adopted": 0, "left": 0, "seats_dissolved": 0, "ended": 0}

    # ---- the accessor lane 219 (PW-1520) may override: how open a culture is to other peoples' gods, 0..1
    def openness(self, P, c: int) -> float:
        f = P.faith_of.get(c)
        if f is None or P.faiths[f].missionary:  # (D68 4A: a faith that refuses other gods; today the missionary ones)
            return 0.0
        return P.att.religious(c)

    def _ev(self, ago, kind, text, **kw):
        self.events.append({"kyr": round(float(ago), 3), "kind": kind, "text": text, **kw})
        self.counts[kind] = self.counts.get(kind, 0) + 1

    # ---- one frame
    def step(self, P, ago: float, dt: float, cultures: dict, contacts=None, where=None, rule_steps=(), urban=None):
        for c, u in cultures.items():
            self.people[c] = u.get("people", "?")
        for c, (n, v) in (where or {}).items():
            if n:
                self.centre[c] = _unit(v)
        live = {c for c in cultures if any(b.status == "living" for b in P.by.get(c, ()))}
        opn = {c: self.openness(P, c) for c in live}
        is_open = {c for c, o in opn.items() if o >= TOL_OPEN}
        self._tend_extra(P, ago, dt, cultures, live)
        if dt <= 0:
            return
        # hubs
        mix: dict[int, float] = {}
        for (a, b), (wa, wb) in (contacts or {}).items():
            if a in live and b in live and self.people.get(a) != self.people.get(b):
                mix[a] = mix.get(a, 0.0) + wa
                mix[b] = mix.get(b, 0.0) + wb
        ruled_by: dict[int, int] = {}
        empire = set()
        for _, rule in rule_steps or ():
            for r, subs, *_ in rule:
                ps = {self.people.get(r)} | {self.people.get(x) for x, sh in subs if sh > 0}
                foreign = sum(sh * P.cells.get(x, 0) for x, sh in subs if self.people.get(x) != self.people.get(r))
                if len(ps - {None}) >= HUB_PEOPLES and foreign >= HUB_SUBJ * max(P.cells.get(r, 0), 1):
                    empire.add(r)  # (an empire of several peoples, not a kingdom with a border march: D68 3A)
                for x, sh in subs:
                    if sh >= 0.5:
                        ruled_by[x] = r
        for c in live:
            kind = "empire" if c in empire else "city" if (urban or {}).get(c, 0.0) >= HUB_URBAN and mix.get(c, 0.0) >= HUB_MIX else None
            if kind is None:
                self.hub_t.pop(c, None)
            else:
                t = self.hub_t.setdefault(c, [0.0, kind])
                t[0] += dt
                t[1] = "empire" if "empire" in (t[1], kind) else kind
        for c in list(self.hub_t):
            if c not in live:
                self.hub_t.pop(c)
        alive = [p for p in self.pans if p["ended"] is None]
        for p in alive:
            self._tend_pantheon(P, p, ago, dt, live, is_open)
        alive = [p for p in self.pans if p["ended"] is None]
        hubs_now = {p["hub"] for p in alive}
        for c in sorted(self.hub_t):
            t, kind = self.hub_t[c]
            if t < HUB_KYR or c in hubs_now or c not in is_open or c not in self.centre:
                continue
            c0 = self.centre[c]
            if len({self.people.get(x) for x in is_open if x in self.centre and _km(self.centre[x], c0) <= PANTHEON_KM}) < HUB_PEOPLES:
                continue  # (no other people's open cultures within reach: nobody to share gods with)
            host = next((p for p in alive if c in p["reach"] or (p["hub"] in self.centre and _km(self.centre[c], self.centre[p["hub"]]) <= PANTHEON_KM)), None)
            if host is not None:  # (a hub inside a bigger pantheon's reach sits under it: the city god under the capital's)
                if c not in host["under"]:
                    host["under"].append(c)
                    self._ev(ago, "joined", f"{P_name(c)}'s shrine joins the {host['name']}", pantheon=host["id"], culture=c)
                continue
            p = {"id": len(self.pans), "hub": c, "kind": kind, "name": f"pantheon of culture {c}", "founded": round(float(ago), 3), "ended": None,
                 "end": None, "into": None, "reach": set(), "under": [], "seats": [], "bad": 0.0, "track": [], "patrons": {}}
            self.pans.append(p)
            alive.append(p)
            hubs_now.add(c)
            self._ev(ago, "pantheons", f"a pantheon gathers about culture {c} ({kind})", pantheon=p["id"], culture=c)
            self._tend_pantheon(P, p, ago, 0.0, live, is_open)
        self._merge_nested(ago, alive)
        for p in self.pans:
            if p["ended"] is None:
                self._identify(P, p, ago, dt, opn, ruled_by, cultures)
                self._adopt(P, p, ago, dt, opn, cultures)
                c0 = self.centre.get(p["hub"])
                p["track"].append([round(float(ago), 3), *(_latlon(c0) if c0 is not None else [None, None]), len(p["reach"])])

    def _tend_extra(self, P, ago, dt, cultures, live):
        for b in self.extra:
            if b.status != "living":
                continue
            if b.culture not in live:
                b.status, b.ended, b.end = "ended", round(float(ago), 3), "its culture ended"
                self._leave_seat(b, ago, "its culture ended")
                continue
            u = cultures.get(b.culture)
            if dt > 0 and u is not None:
                b.w = G._drift(b.w, P.sal.get(b.culture, u["sal"]), dt)  # (it drifts with its new land: a sea god taken inland becomes a river god)
                b.ind += (min(b.ind_cap, G.tier(u["know"], False)) - b.ind) * (1.0 - math.exp(-dt / G.TAU_IND))
            if not b.hist or abs(b.hist[-1][0] - ago) >= 0.5:
                b.hist.append([round(float(ago), 3), round(float(b.ind), 3), _top(b.w)])

    def _tend_pantheon(self, P, p, ago, dt, live, is_open):
        h = p["hub"]
        hub_ok = h in self.hub_t and self.hub_t[h][0] >= HUB_KYR and h in is_open
        if h not in live or h not in is_open:  # (the hub gone, or closed: the fast path, Akhenaten's decree)
            self._end_pantheon(p, ago, "its hub culture ended" if h not in live else "its hub turned to a faith that refuses other gods, or grew intolerant")
            return
        p["bad"] = 0.0 if hub_ok else p["bad"] + dt
        if p["bad"] >= TAU_HUB_MEM:
            self._end_pantheon(p, ago, "its hub stopped being a meeting place")
            return
        c0 = self.centre.get(h)
        p["reach"] = {c for c in is_open if c in self.centre and c0 is not None and _km(self.centre[c], c0) <= PANTHEON_KM} | {h}
        if len({self.people.get(c) for c in p["reach"]}) < HUB_PEOPLES:  # (open cultures of one people only: no pantheon to gather)
            if hub_ok:  # (else already counted)
                p["bad"] += dt
            if p["bad"] >= TAU_HUB_MEM:
                self._end_pantheon(p, ago, "no other people's open cultures are left in its reach")
                return
        p["under"] = [c for c in p["under"] if c in p["reach"]]
        p["patrons"] = self._patrons(P, p["reach"])
        pat = set(p["patrons"].values())
        for s in [self.seats[i] for i in p["seats"]]:
            if s["ended"] is not None:
                continue
            for c, b in list(s["members"].items()):
                why = ("its culture left the pantheon's reach or closed to other gods" if c not in p["reach"] else
                       "it is no longer worshipped" if b.status != "living" else
                       f"it drifted off {s['domain']}" if _top(b.w) != s["domain"] else
                       "it became its people's own god" if b.how not in ("adopted", "joint") and _root(P, b) in pat else None)
                if why:
                    s["members"].pop(c)
                    self.seat_of.pop(id(b), None)
                    s["events"].append([round(float(ago), 3), "left", c, why])
                    self._ev(ago, "left", f"{G.label(b.w, b.ind)} of culture {c} leaves the {s['domain']} seat: {why}", pantheon=p["id"], seat=s["id"], culture=c)
            if len({self.people.get(c) for c in s["members"]}) < 2:
                self._end_seat(s, ago, "only one people's gods are left in it")

    def _end_seat(self, s, ago, why):
        for c, b in s["members"].items():
            self.seat_of.pop(id(b), None)
        s["last"] = [(c, b) for c, b in s["members"].items()]
        s["members"] = {}
        s["ended"], s["end"] = round(float(ago), 3), why
        self._ev(ago, "seats_dissolved", f"the {s['domain']} seat breaks up: {why}", pantheon=s["pantheon"], seat=s["id"])

    def _end_pantheon(self, p, ago, why, into=None):
        for i in p["seats"]:
            if self.seats[i]["ended"] is None:
                self._end_seat(self.seats[i], ago, "its pantheon ended" if into is None else "its pantheon joined a bigger one")
        p["ended"], p["end"], p["into"] = round(float(ago), 3), why, into
        p["last_reach"] = sorted(p["reach"])
        self._ev(ago, "ended", f"the {p['name']} ends: {why}", pantheon=p["id"])

    def _leave_seat(self, b, ago, why):
        si = self.seat_of.pop(id(b), None)
        if si is not None:
            s = self.seats[si]
            for c, x in list(s["members"].items()):
                if x is b:
                    s["members"].pop(c)
                    s["events"].append([round(float(ago), 3), "left", c, why])

    def _merge_nested(self, ago, alive):
        """A pantheon whose hub lies in a bigger one's reach joins it (its seats' members move to the bigger one's seats of their domain)."""
        for p in sorted(alive, key=lambda p: (len(p["reach"]), -p["id"])):
            if p["ended"] is not None:
                continue
            host = max((q for q in alive if q is not p and q["ended"] is None and p["hub"] in q["reach"] and len(q["reach"]) >= len(p["reach"])),
                       key=lambda q: (len(q["reach"]), -q["id"]), default=None)
            if host is None:
                continue
            moved = []
            for i in p["seats"]:
                s = self.seats[i]
                if s["ended"] is None:
                    moved.append((s["domain"], dict(s["members"]), s.get("joint")))
            self._end_pantheon(p, ago, "its hub came into a bigger pantheon's reach", into=host["id"])
            host["under"].append(p["hub"])
            for dom, mem, joint in moved:
                t = self._seat_on(host, dom)
                if t is None:
                    t = self._new_seat(host, dom, ago)
                    t["joint"] = joint
                for c, b in mem.items():
                    if c not in t["members"] and id(b) not in self.seat_of:
                        t["members"][c] = b
                        self.seat_of[id(b)] = t["id"]
                        t["events"].append([round(float(ago), 3), "joined", c, "its pantheon joined this one"])

    def _patrons(self, P, reach) -> dict:
        """Per people in the reach, its own god: the lineage that leads (high) the most of its land there."""
        tally: dict = {}
        for c in reach:
            lead = P.lead(c)
            if lead is not None:
                k = (self.people.get(c), _root(P, lead))
                tally[k] = tally.get(k, 0) + P.cells.get(c, 1)
        out: dict = {}
        for (pp, r), n in sorted(tally.items(), key=lambda kv: (-kv[1], kv[0][1])):
            out.setdefault(pp, r)
        return out

    def _seat_on(self, p, dom):
        return next((self.seats[i] for i in p["seats"] if self.seats[i]["ended"] is None and self.seats[i]["domain"] == dom), None)

    def _new_seat(self, p, dom, ago):
        s = {"id": len(self.seats), "pantheon": p["id"], "domain": dom, "members": {}, "founded": round(float(ago), 3), "ended": None, "end": None,
             "events": [], "joint": None}
        self.seats.append(s)
        p["seats"].append(s["id"])
        self.counts["seats"] += 1
        return s

    def _identify(self, P, p, ago, dt, opn, ruled_by, cultures):
        pat = set(p["patrons"].values())
        cand: dict = {}  # (culture, domain) -> its best free god there
        for c in sorted(p["reach"]):
            for b in P.by.get(c, ()):
                if b.status != "living" or b.ind < IND_GOD or id(b) in self.seat_of or _root(P, b) in pat:
                    continue
                k = (c, _top(b.w))
                if k not in cand or b.ind > cand[k].ind:
                    cand[k] = b
        placed = set()
        for (x, dom), b in sorted(cand.items(), key=lambda kv: (kv[0][0], G.DOMAINS.index(kv[0][1]))):
            if (x, dom) in placed:
                continue
            s = self._seat_on(p, dom)
            fast = RULE_X if ruled_by.get(x) == p["hub"] or x == p["hub"] else 1.0
            if s is not None:
                if x in s["members"]:
                    continue
                cen = np.mean([m.w for m in s["members"].values()], 0)
                if G._cos(b.w, cen) < G.FUSE_COS:
                    continue
                head_c = p["hub"] if p["hub"] in s["members"] else min(s["members"])
                rate = opn.get(x, 0.0) * opn.get(head_c, 0.0) * fast / TAU_IDENT
                if self.rng.random() < 1.0 - math.exp(-rate * dt):
                    s["members"][x] = b
                    self.seat_of[id(b)] = s["id"]
                    placed.add((x, dom))
                    s["events"].append([round(float(ago), 3), "identified", x, ""])
                    self._ev(ago, "identified", f"{G.label(b.w, b.ind)} of culture {x} is matched with the {dom} seat", pantheon=p["id"], seat=s["id"], culture=x)
                continue
            mates = [(G._cos(b.w, y.w), yc) for (yc, d2), y in cand.items() if d2 == dom and (yc, d2) not in placed and self.people.get(yc) != self.people.get(x)]
            mates = [m for m in mates if m[0] >= G.FUSE_COS]
            if not mates:
                continue
            _, y = max(mates, key=lambda m: (m[0], -m[1]))
            rate = opn.get(x, 0.0) * opn.get(y, 0.0) * fast / TAU_IDENT
            if self.rng.random() < 1.0 - math.exp(-rate * dt):
                s = self._new_seat(p, dom, ago)
                for c, bb in ((x, b), (y, cand[(y, dom)])):
                    s["members"][c] = bb
                    self.seat_of[id(bb)] = s["id"]
                    placed.add((c, dom))
                    s["events"].append([round(float(ago), 3), "identified", c, "founded the seat"])
                self._ev(ago, "identified", f"the gods of {dom} of cultures {x} and {y} are matched: a new seat", pantheon=p["id"], seat=s["id"], culture=x)
                if p["kind"] == "empire" and self.rng.random() < JOINT_P:  # (D68 1C: sometimes a brand-new joint god, as Serapis was)
                    self._joint(p, s, ago, cultures)

    def _joint(self, p, s, ago, cultures):
        mem = list(s["members"].values())
        w = np.mean([m.w for m in mem], 0)
        b = Extra(-1, w / w.sum(), round(float(ago), 3), p["hub"], "joint", None)
        b.ind = b.ind_cap = max(m.ind for m in mem)
        b.dev = max(m.dev for m in mem)
        b.fused = [m.id for m in mem]  # (the gods it was made from)
        self.extra.append(b)
        s["joint"] = b
        self._ev(ago, "joint", f"a new joint god of {s['domain']} is made at culture {p['hub']} for the seat's peoples", pantheon=p["id"], seat=s["id"], culture=p["hub"])

    def _adopt(self, P, p, ago, dt, opn, cultures):
        for i in p["seats"]:
            s = self.seats[i]
            if s["ended"] is not None or len({self.people.get(c) for c in s["members"]}) < 2:
                continue
            d = G.DOMAINS.index(s["domain"])
            head_c = p["hub"] if p["hub"] in s["members"] else min(s["members"])
            head = s["joint"] if s.get("joint") is not None and s["joint"].status == "living" else s["members"][head_c]
            for x in sorted(p["reach"]):
                if x in s["members"] or x not in cultures or self.adopted_n.get(x, 0) >= ADOPT_MAX:
                    continue
                if any(b.status == "living" and b.w[d] >= G.COVER_W for b in P.by.get(x, ())):
                    continue  # (it has a god of this domain already: matching, not adoption)
                if self.rng.random() < 1.0 - math.exp(-opn.get(x, 0.0) / TAU_ADOPT * dt):
                    b = Extra(-1, head.w.copy(), round(float(ago), 3), x, "adopted", head)
                    b.ind_cap = head.ind
                    b.ind = min(head.ind, G.tier(cultures[x]["know"], False))
                    b.dev = 0.5
                    self.extra.append(b)
                    self.adopted_n[x] = self.adopted_n.get(x, 0) + 1
                    s["members"][x] = b
                    self.seat_of[id(b)] = s["id"]
                    s["events"].append([round(float(ago), 3), "adopted", x, ""])
                    self._ev(ago, "adopted", f"culture {x} takes in the {s['domain']} god of the {p['name']}", pantheon=p["id"], seat=s["id"], culture=x)

    # ---- the read-out
    def finish(self, P, C: list, docs: list) -> dict:
        """Give the adopted and joint gods their ids (after the gods' own), name the pantheons, and return the doc. docs: the being docs
        (gods.being_doc), extended in place with the extra gods and each being's `seat`."""
        n0 = len(docs)
        for k, b in enumerate(self.extra):
            b.id = n0 + k
        for b in self.extra:
            if isinstance(b.parent, G.Being):
                b.parent = b.parent.id
            d = G.being_doc(P, b)
            docs.append(d)
        for d in docs:
            d["seat"] = None
        def bid(b):  # noqa: E306
            return b.id
        for s in self.seats:
            mem = s["members"] if s["ended"] is None else dict(s.get("last") or [])
            if s["ended"] is None:
                for b in mem.values():
                    docs[bid(b)]["seat"] = s["id"]
            s["_mem"] = mem
        hubname = lambda c: C[c]["name"] if 0 <= c < len(C) else f"culture {c}"  # noqa: E731
        out = []
        for p in self.pans:
            p["name"] = f"the {hubname(p['hub'])} pantheon"
        for p in self.pans:
            reach = sorted(p["reach"]) if p["ended"] is None else p.get("last_reach", [])
            seats = []
            for i in p["seats"]:
                s = self.seats[i]
                mem = s["_mem"]
                seats.append({"id": s["id"], "domain": s["domain"], "founded_kyr": s["founded"], "ended_kyr": s["ended"], "end": s["end"],
                              "members": [{"being": bid(b), "culture": c, "people": self.people.get(c), "label": docs[bid(b)]["label"], "how": b.how}
                                          for c, b in sorted(mem.items())],
                              "joint": bid(s["joint"]) if s.get("joint") is not None else None, "events": s["events"]})
            live_seats = [s for s in seats if s["ended_kyr"] is None]
            head = None
            if live_seats:
                own = [s for s in live_seats if any(m["culture"] == p["hub"] for m in s["members"])]
                pool = own or live_seats
                head = max(pool, key=lambda s: (max((docs[m["being"]]["individuation"] for m in s["members"] if m["culture"] == p["hub"]), default=0.0),
                                                len(s["members"]), -s["id"]))["id"]
            peoples = sorted({self.people.get(c) for c in reach} - {None})
            out.append({"id": p["id"], "name": p["name"], "hub": p["hub"], "hub_name": hubname(p["hub"]), "kind": p["kind"], "founded_kyr": p["founded"],
                        "ended_kyr": p["ended"], "end": p["end"], "into": p["into"], "reach": reach, "under": p["under"], "peoples": peoples,
                        "cells": int(sum(P.cells.get(c, 0) for c in reach)), "head": head, "seats": seats,
                        "patrons": {pp: r for pp, r in sorted(p["patrons"].items()) if pp in peoples}, "track": p["track"][:: max(1, len(p["track"]) // 60)]})
        land = sum(n for c, n in P.cells.items() if any(b.status == "living" for b in P.by.get(c, ())))
        living = [q for q in out if q["ended_kyr"] is None]
        covered = {c for q in living for c in q["reach"]}
        summary = {"living": len(living), "ever": len(out), "land_share": round(sum(P.cells.get(c, 0) for c in covered) / max(land, 1), 3),
                   "seats_living": sum(1 for q in living for s in q["seats"] if s["ended_kyr"] is None),
                   "adopted_gods": sum(1 for b in self.extra if b.how == "adopted"), "joint_gods": sum(1 for b in self.extra if b.how == "joint"),
                   "counts": dict(self.counts)}
        return {"rule": RULE, "constants": {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float))},
                "list": out, "events": self.events, "summary": summary}


def P_name(c: int) -> str:
    return f"culture {c}"


def _root(P, b) -> int:
    """A being's lineage: up through `parent` over its founded, born, split and converted copies (a converted culture's new leading
    god belongs to its converter's lineage)."""
    i = b.id
    seen = 0
    while seen < 10000:
        x = P.beings[i]
        if x.parent is None or x.how not in ("founded", "born", "split", "converted"):
            return i
        i, seen = x.parent, seen + 1
    return i


def patrons(P, people_of: dict) -> dict:
    """Per people, the whole world over: its own god, the lineage leading (high) the most of its land, with the share of its land it leads."""
    tally: dict = {}
    tot: dict = {}
    for c, bs in P.by.items():
        if not any(b.status == "living" for b in bs):
            continue
        lead = P.lead(c)
        pp = people_of.get(c)
        if lead is None or pp is None:
            continue
        n = P.cells.get(c, 1)
        k = (pp, _root(P, lead))
        tally[k] = tally.get(k, 0) + n
        tot[pp] = tot.get(pp, 0) + n
    out: dict = {}
    for (pp, r), n in sorted(tally.items(), key=lambda kv: (-kv[1], kv[0][1])):
        if pp not in out:
            out[pp] = {"lineage": r, "share": round(n / max(tot[pp], 1), 3)}
    return out
