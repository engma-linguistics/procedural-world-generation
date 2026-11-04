"""Polities v0 (PW-1431): who rules where at each century step of a peoples run, read after the run from what it stored.

In plain words: at every 100-year step of the settlement ledger, the towns big enough and knowing enough become seats of rule; each
seat holds the peopled land within its reach (travel distance from it); the strongest seats claim first, and a seat already inside
another's claim is one of its towns, not a ruler. A one-cell seat is a chiefdom, a seat with kingship or law and a city is a state, a
state ruling more than one culture of substance is an empire, and a dragon culture that takes tribute rules a dragon realm (dragons
are sapient: one flat absolute ruler, its reach the range a dragon can fly and defend; owner ruling O4, 2026-11-01). Nothing here
re-runs the history: it reads settlements.json, meta.techtree.known, cultures.json and demes.json, and the presence table (which
culture lives where at each stored frame). Source of the design: docs/review/cultures-proposal/proposal-r2.md section 3.3 and round 1
(proposal.md 2.1.1-2.1.2).

The one rule of a step (step()):
  1. Seats. A living town (the ledger's own town size for its time and holder, settlements.json bands) whose people know
     `chiefdoms` and writing (or live beside a people who know writing: the owner's P2 "nearly B", round 2's lenience) is a
     chiefdom seat. It is a state seat when its people also know `kingship` or `law` (round 1 P2 A) and it is a city
     (tiers.city_min), or a smaller town hemmed in (Carneiro 2012: circumscription speeds states): the size it needs falls by
     HEMMED_X x how hemmed in it is. One seat per cell (the biggest town). A seat keeps its tier down to HOLD of the size that
     made it (no flicker at the line).
  2. Dragon seats. Each living dragon culture whose people know `hoards` (hoards and tribute) seats at its core cell.
  3. Claims. Seats claim in order: states with standing armies (technology that outstrips a dragon, O4), dragon realms, other
     states, chiefdoms; within a class, the bigger first (a capital last step counts INCUMBENT times its size). Each claims the
     peopled cells within its reach not yet claimed (travel through unclaimed land only: claimed land is a border). A seat whose
     own cell is already claimed rules nothing: it is a town of that polity.
  0. Falls (PW-1447), before the seats: each state, empire or dragon realm that ruled last step ends with FALL_PER_CENTURY's chance
     per century (Arbesman 2011: lifetimes exponential, ~0.46 per century), a seeded draw per polity and step. Its capital drops one
     tier for COOL_STEPS (a state's to a chiefdom; a dragon realm's dragons hold no realm) and its conquered provinces go free.
  3b. Provinces. A seat that war took (below) claims for its conqueror, right after the conqueror's capital, until the conqueror
     falls (then it rules again, as a successor) or someone else holds its town.
  4. War (PW-1432, war_v0 at the WAR seam): neighbouring town polities that both stood last step (borders() lists who touches whom)
     may fight. Each one's strength is its settled people x MIL_X per military edge its rulers know (MIL_TECHS: bronze, iron,
     riding, standing armies). A state or empire at least WAR_ODDS times stronger than a neighbour takes it with WAR_P's chance per
     century: the loser's army breaks, all its cells change hands, its capital becomes a province (3b), and it falls, "conquered by"
     the winner. Farmers keep farming: nobody dies or moves (deaths and refugees: v4). Each loser faces only its strongest eligible
     neighbour; the strongest attack first. Dragon realms neither attack nor are attacked here (their land is O4's claim order).
     An invasion you schedule (PW-1433: authored.json, invasions.py; derive(invasions=...)) raises the chance between the peoples or
     cultures it names in its window (x2 light; x4 strong, which also needs no edge in strength) and leads the attack on its victims
     over plain war; the doc's "invasions" reads each row out (it happened: what was taken, when, how much land; or why not).

Reach is a budget of foot-km (km on foot over flat ground): a chiefdom CHIEF_KM (its own cell at L7), a state STATE_KM, more with
law and government at a distance; riding and roads make a km cheaper, climbing dearer; the sea needs boats. Every number below is
sourced or labelled a judgement call.
"""

from __future__ import annotations

import heapq
import json
import time
import zlib
from pathlib import Path

import numpy as np
from numba import njit

FORMAT = "procgen-polities/1"
VERSION = 3  # (bump when the rules change: the server's cached docs are remade)

# ---- reach (foot-km)
CHIEF_KM = 27.5  # sourced: a chiefdom reaches ~half a day's travel, "some 25-30 km by foot" (Spencer 2010, via proposal.md 2.1.2)
STATE_KM = 150.0  # sourced range, judged point: Spencer 2010's six primary states reached 50-250 km soon after state institutions (via 2.1.2); the middle
LAW_X = 4 / 3  # judgement: written law (rule delegated by text) extends a state's reach by a third
DISTANCE_X = 2.0  # judgement, checked against Taagepera 1997 (via 2.1.2: the largest polity's jump with "government at a distance"):
DISTANCE_TECHS = ("bureaucracy", "postal_relay", "milestones_waystations")  # (any of these doubles the reach)
RIDE_X, ROAD_X = 1.5, 1.5  # judgement: a ridden km and a km of road each cost two thirds of a walked one
CLIMB_M = 1000.0  # judgement: a km of travel costs (1 + the climb in m / CLIMB_M) more (a 1,000 m climb doubles it)
SAIL_X, BOAT_X = 0.5, 1.0  # judgement: a km by sail costs half a walked one, by small boats (coast-hugging) the same; no boats: no sea
BOATS = ("canoes", "bark_canoes", "reed_boats", "skin_boats", "plank_boats", "rafts")
SAILS = ("sails",)
DRAGON_KM = 250.0  # judgement (O4: the range a dragon can fly and defend against rival dragons): flight ignores sea and slope
# ---- seats
HEMMED_X = 0.5  # judgement (Carneiro 2012, circumscription speeds states up): a fully hemmed-in town is a state seat at half a city's size
HEMMED_RINGS = 2  # judgement: hemmed-in is read over the cells within two rings of the seat (~120 km at L7)
HOLD = 0.8  # judgement: a seat keeps its tier until it shrinks under 0.8 of the size that made it
INCUMBENT = 1.5  # judgement: last step's capital ranks as if 1.5x its size (the ruler in place keeps the advantage)
GAP_STEPS = 2  # judgement: a seat that rules again within 2 steps (200 years) is the same polity, not a new one
STRONG_TECH = "standing_army"  # judgement (O4 "until technology outstrips it"): a state with standing armies claims before dragons
# ---- falls (PW-1447)
FALL_PER_CENTURY = 0.46  # sourced: Arbesman 2011 (41 empires from Taagepera): lifetimes exponential, lambda 0.46 per century, mean ~220 years (via proposal.md 2.1.2)
FALL_TIERS = ("state", "empire")  # judgement: chiefdoms (a town and its cell) come and go with their town's size already
DRAGON_RULER = "ancient"  # judgement: a dragon realm (one absolute ruler, O4) ends when its ruler dies; the ruler is an ancient, dying at the run's dragon mortality schedule (dragon_ages.SCHEDULES, owner 10-28: 0.1% a year, ~0.1 per century)
COOL_STEPS = 1  # judgement (Currie et al. 2010: complexity falls in small steps): a fallen capital rules at most a chiefdom for 1 step (a century)
# ---- war (PW-1432)
WAR_P = 0.25  # judgement: the chance per century that a state at least WAR_ODDS times stronger takes a neighbour (checked against Taagepera 1997's sizes, round2.md)
WAR_ODDS = 1.5  # judgement: the strength an attacker needs, as a multiple of the defender's
MIL_X = 1.5  # judgement: each military edge its rulers know multiplies a polity's strength
MIL_TECHS = ("bronze", "iron", "riding", "standing_army")  # (any of these is one edge)
INVADE_X = {"light": 2.0, "strong": 4.0}  # judgement: an authored invasion row (PW-1433) multiplies WAR_P; a strong one waives WAR_ODDS
# ---- empires
SUBJECT_SHARE = 0.2  # judgement: an empire is a state where another culture (not dragons living over it) holds 20% or more of its settled people
SUBJECT_CELLS = 3  # judgement: the card lists a subject culture with settlements in the polity, or living on 3 or more of its cells
WRITING_TECHS = ("writing",)  # owner P2 "nearly B" (owner-notes-r1.md): a chiefdom needs writing, its own or a neighbour's (round 2's lenience)
TIERS = ("chiefdom", "state", "empire", "dragon realm")
SETTLED_KINDS = ("chief", "minority")  # (seats: a people's own places; mines and pits count for people, never as capitals)
R_EARTH_KM = 6371.0  # (the grid's sphere, as cultures.py and demes.py measure areas)


def constants() -> dict:
    """The rules' numbers, for the doc (each one's source is beside it above)."""
    return {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float, tuple, str, dict)) and k not in ("FORMAT",)}


# ------------------------------------------------------------------ the claim kernel

@njit(cache=True)
def _claim(seed, budget, land_x, sea_x, climb_m, off, idx, ekm, edz, sea, blocked, may, owner, pid, dist, touched, claimed):
    """One seat's claim: a Dijkstra from seed over cells not owned by another polity and not blocked, each step costing its km x
    land_x (x (1 + climb / climb_m) when climb_m > 0), or x sea_x when either end is sea (sea_x < 0: no sea). Claims the cells it
    reaches within budget where may[c] and owner[c] < 0. Returns the number claimed (the first that many entries of `claimed` are
    those cells); dist is left all inf."""
    nt = 0
    h = [(0.0, seed)]
    dist[seed] = 0.0
    touched[nt] = seed
    nt += 1
    got = 0
    while len(h) > 0:
        d, a = heapq.heappop(h)
        if d > dist[a]:
            continue
        if owner[a] < 0 and (may[a] or a == seed):
            owner[a] = pid
            claimed[got] = a
            got += 1
        for e in range(off[a], off[a + 1]):
            b = idx[e]
            if blocked[b] or (owner[b] >= 0 and owner[b] != pid):
                continue
            if sea[a] or sea[b]:
                if sea_x < 0:
                    continue
                c = ekm[e] * sea_x
            else:
                c = ekm[e] * land_x
                if climb_m > 0:
                    c *= 1.0 + edz[e] / climb_m
            nd = d + c
            if nd <= budget and nd < dist[b]:
                if dist[b] == np.inf:
                    touched[nt] = b
                    nt += 1
                dist[b] = nd
                heapq.heappush(h, (nd, b))
    for k in range(nt):
        dist[touched[k]] = np.inf
    return got


def borders(owner: np.ndarray, grid) -> dict:
    """{(a, b): shared edges} of the polities that touch (a < b): where war (PW-1432) moves land between neighbours."""
    src, dst = np.asarray(grid.nbr_src), np.asarray(grid.nbr_idx)
    oa, ob = owner[src], owner[dst]
    m = (oa >= 0) & (ob >= 0) & (oa < ob)
    pairs, n = np.unique(np.stack([oa[m], ob[m]], 1), axis=0, return_counts=True) if m.any() else (np.zeros((0, 2), int), [])
    return {(int(a), int(b)): int(k) for (a, b), k in zip(pairs, n)}


def no_war(owner: np.ndarray, ctx: dict) -> np.ndarray:
    """The war seam (PW-1432): given a step's owners (cell -> polity key index, -1 none) and ctx (grid, the step's seats and
    polities, borders(owner, grid), last step's owners), answer the owners after the step's wars. v0: no war."""
    return owner


def draw(run: str, key: str, step: int, what: str) -> float:
    """A seeded uniform draw in [0, 1) per run, polity key, step and purpose: a rebuild gives the same map, and a nudged constant
    meets the same luck (common random numbers, so the +-10% checks compare like with like)."""
    return zlib.crc32(f"{run}|{key}|{step}|{what}".encode()) / 2 ** 32


def strength(people: float, ruler: str, knows, ago: float) -> float:
    """A polity's strength for war v0: its settled people x MIL_X per military edge (MIL_TECHS) its ruling people know."""
    return people * MIL_X ** sum(1 for t in MIL_TECHS if knows(ruler, t, ago))


def _names(spec, seat, anc) -> bool:
    """Does an invasion row's who or whom name this seat's rulers? spec: None (anyone), a people id (lane 175's form), {"people": id}
    (the people, its groups and daughter lines: anc(people) holds the ids it may be named by) or {"culture": uid} (seat["uid"])."""
    if spec is None:
        return True
    if isinstance(spec, str):
        spec = {"people": spec}
    if "culture" in spec:
        return seat.get("uid") is not None and seat.get("uid") == spec["culture"]
    return spec.get("people") in anc(seat["people"])


def _in_window(r: dict, ago: float) -> bool:
    return r["from_kyr"] >= ago - 1e-9 >= r["to_kyr"] - 2e-9


def war_v0(owner: np.ndarray, ctx: dict) -> np.ndarray:
    """War v0 (PW-1432), one plain rule per century step (module docstring, step 4). ctx: "seats" (by polity index; None for one not
    ruling), "strength" (by index), "eligible" (index -> it stood last step and is a town polity), "borders", "run", "step", "ago",
    "invasions" (authored rows, PW-1433: invasions.hook_rows), "inv_log" (one invasions.new_log() per row: what this step saw of it),
    "ancestors" (people -> the ids a row may name it by). Moves every cell of each conquered polity to its conqueror and lists the
    conquests as ctx["taken"] = [(winner index, loser index, how)], how "war" or "invasion"; ctx["taken_row"]: loser -> its row's "i".
    An invasion outranks plain war for the same loser (the row's invaders attack it, not its strongest neighbour)."""
    seats, S, ok = ctx["seats"], ctx["strength"], ctx["eligible"]
    ago = ctx["ago"]
    anc = ctx.get("ancestors") or (lambda p: {p})
    logs = ctx.get("inv_log")
    if logs is not None:  # (every step, in or out of the window: when the invaders had a state at all, the read-out's hint)
        states = [s for s in seats if s is not None and s["tier"] == "state"]
        for r in ctx.get("invasions") or []:
            if r.get("i") is not None and any(_names(r["who"], s, anc) for s in states):
                logs[r["i"]]["state_kyr"].append(ago)
    rows = [r for r in (ctx.get("invasions") or []) if _in_window(r, ago)]
    L = {id(r): (logs[r["i"]] if logs is not None and r.get("i") is not None else None) for r in rows}
    near = {id(r): set(np.unique(owner[r["near"]]).tolist()) for r in rows if r.get("near") is not None}
    for r in rows:  # (what the invaders and victims had this step: the read-out's "why not")
        lg = L[id(r)]
        if lg is None:
            continue
        lg["steps"] += 1
        mine = [p for p, s in enumerate(seats) if s is not None and _names(r["who"], s, anc)]
        st = [p for p in mine if seats[p]["tier"] == "state" and ok(p)]
        lg["state_far"] += bool(st) and id(r) in near and not any(p in near[id(r)] for p in st)
        lg["state"] += any(id(r) not in near or p in near[id(r)] for p in st)
        lg["chief"] += any(seats[p]["tier"] == "chiefdom" for p in mine)
        lg["state_new"] += any(seats[p]["tier"] == "state" and not ok(p) for p in mine)  # (a state fights from its second century)
        vic = [p for p, s in enumerate(seats) if s is not None and p not in mine and _names(r.get("whom"), s, anc)]
        lg["victim"] += any(ok(p) for p in vic)
        lg["victim_dragon"] += any(seats[p]["tier"] == "dragon realm" for p in vic)
    best: dict = {}  # loser -> ((an invasion, winner's strength), winner, chance, how, row)
    tried: list = []  # (winner, loser, row): the pairs an invasion row named
    for (a, b) in ctx["borders"]():
        for w, l in ((a, b), (b, a)):
            if not (ok(w) and ok(l)) or seats[w]["tier"] != "state":
                continue
            p, odds, how, row = WAR_P, WAR_ODDS, "war", None
            hits = [r for r in rows if _names(r["who"], seats[w], anc) and not _names(r["who"], seats[l], anc)
                    and _names(r.get("whom"), seats[l], anc) and (id(r) not in near or w in near[id(r)])]
            for r in hits:  # (several rows on one pair: the strongest leads, the others are shadowed)
                q = min(1.0, WAR_P * INVADE_X[r.get("strength", "light")])
                if row is None or q > p:
                    p, how, row = q, "invasion", r
                    odds = 0.0 if r.get("strength") == "strong" else WAR_ODDS  # (strong: no strength needed at all)
                if L[id(r)] is not None:
                    L[id(r)]["border"] += 1
            for r in hits:
                if r is not row and L[id(r)] is not None:
                    L[id(r)]["shadowed"] += 1
            if row is not None:
                tried.append((w, l, row))
            if S[w] >= odds * S[l] and S[w] > 0:
                rank = (how == "invasion", S[w])
                if l not in best or rank > best[l][0]:
                    best[l] = (rank, w, p, how, row)
            elif row is not None and L[id(row)] is not None:
                L[id(row)]["odds"] += 1
    for w, l, row in tried:
        lg = L[id(row)]
        if lg is not None and l in best and best[l][1] != w and best[l][4] is not row:
            lg["outranked"] += 1
    taken, gone, by_row = [], set(), {}
    for l, (rank, w, p, how, row) in sorted(best.items(), key=lambda kv: (-kv[1][0][1], kv[0])):
        lg = L[id(row)] if row is not None else None
        if w in gone or l in gone:
            if lg is not None:
                lg["gone"] += 1
            continue
        if draw(ctx["run"], seats[l]["key"], ctx["step"], "war") >= p:
            if lg is not None:
                lg["chance"] += 1
                lg["p"] = p
            continue
        owner[owner == l] = w
        gone.add(l)
        taken.append((w, l, how))
        if row is not None:
            by_row[l] = row.get("i")
    ctx["taken"] = taken
    ctx["taken_row"] = by_row
    return owner


WAR = war_v0


# ------------------------------------------------------------------ reading the run

class _Run:
    """What the read-out needs from a peoples run, read once."""

    def __init__(self, run_dir: Path):
        from .. import timeline as T
        from ..grid import shared_grid
        from . import cultures as CU
        from .gods import _resolver
        self.dir = Path(run_dir)
        self.run, self.arr = T.load_frames(self.dir, ("elevation", "ice"))
        m = self.meta = self.run["meta"]
        if not (m.get("settlements") and m.get("cultures") and m.get("demes") and m.get("presence") and (m["demes"].get("all") or {}).get("file")):
            raise SystemExit("this run lacks settlements, cultures or the presence table: run the peoples again")
        self.g = shared_grid(m["level"])
        self.S = json.loads((self.dir / m["settlements"]["file"]).read_text())
        self.C = json.loads((self.dir / m["cultures"]["file"]).read_text())
        self.Dm = json.loads((self.dir / m["demes"]["file"]).read_text())
        self.uids = CU.uids(self.C, self.Dm)
        self.res = _resolver(self.C)
        self.dc = np.asarray(self.C["deme_culture"], np.int64)
        self.lines = m["lineages"]
        self.lname = {l["id"]: l.get("name") or l["id"] for l in self.lines}
        self.lidx = {l["id"]: i for i, l in enumerate(self.lines)}
        self.dragons = {l["id"] for l in self.lines if "dragon" in l["id"] and "flies" in (l.get("traits") or [])}
        self.known = (m.get("techtree") or {}).get("known") or {}
        self.agos = [max(0.0, -f["t"]) for f in self.run["frames"]]
        self.cell_km2 = 4 * np.pi * R_EARTH_KM ** 2 / self.g.n
        c, src, dst = np.asarray(self.g.centers, float), np.asarray(self.g.nbr_src), np.asarray(self.g.nbr_idx)
        self.ekm = np.linalg.norm(c[dst] - c[src], axis=1) * R_EARTH_KM
        self._fr: dict = {}

    def knows(self, people: str, tech: str, ago: float) -> bool:
        k = (self.known.get(people) or {}).get(tech)
        return bool(k) and float(k[0]) >= ago - 1e-9

    def frame_of(self, ago: float) -> int:
        """The stored frame for a step: the latest one at or before it (what had happened by then)."""
        j = 0
        for i, a in enumerate(self.agos):
            if a >= ago - 1e-9:
                j = i
        return j

    def frame(self, j: int) -> dict:
        """Frame j: land, sea, ice, the climb per edge, and who lives where (cells, line index, culture per presence entry)."""
        if j in self._fr:
            return self._fr[j]
        from .. import timeline as T
        from ..geo import is_land
        from .output import read_presence_frame
        g = self.g
        elev = np.asarray(T.frame(self.run, self.arr, "elevation", j), float)
        ice = np.asarray(T.frame(self.run, self.arr, "ice", j), float)
        land = is_land(elev, ice, g)
        cells, dem, off = read_presence_frame(self.dir, self.meta, j)
        line = np.repeat(np.arange(len(off) - 1), np.diff(off))
        ok = dem != 65535
        cells, dem, line = cells[ok].astype(np.int64), dem[ok].astype(np.int64), line[ok]
        ago = self.agos[j]
        C = self.C["cultures"]
        cmap: dict = {}
        cul = np.array([cmap.setdefault(int(self.dc[d]), self.res(int(self.dc[d]), ago)) if self.dc[d] >= 0 else -1 for d in dem], np.int64)
        alive = np.array([c >= 0 and not (C[c]["end"] == "died out" and C[c]["ended_kyr"] is not None and C[c]["ended_kyr"] >= ago - 1e-9)
                          for c in cul], bool) if len(cul) else np.zeros(0, bool)  # (PW-1313: a dead culture keeps no cells)
        cells, line, cul = cells[alive], line[alive], cul[alive]
        peopled = np.zeros(g.n, bool)
        peopled[cells] = True
        src, dst = np.asarray(g.nbr_src), np.asarray(g.nbr_idx)
        f = {"land": land, "sea": ~land, "ice": (ice > 0) & land, "edz": np.abs(np.where(land, elev, 0)[dst] - np.where(land, elev, 0)[src]),
             "cells": cells, "line": line, "cul": cul, "peopled": peopled, "elev": elev}
        self._fr.clear() if len(self._fr) > 3 else None
        self._fr[j] = f
        return f


def _site_tables(R: _Run, agos: list[float]):
    """Per site and step: (people, town threshold), read like the viewer's popAt/holderAt/TIER (viewer/globe/settlements.js)."""
    sites = R.S["sites"]
    tm_default = R.S["tiers"]["town_min_by_stage"][-1]
    A = np.asarray(agos, float)
    pop = np.zeros((len(sites), len(A)), np.float64)
    for i, s in enumerate(sites):
        sr = s.get("series") or []
        if not sr:
            continue
        x = -np.asarray([a for a, _ in sr], float)
        y = np.asarray([p for _, p in sr], float)
        v = np.interp(-A, x, y, left=y[0], right=y[-1])
        v[A > s["founded_kyr"] + 1e-6] = 0
        if s.get("abandoned_kyr") is not None:
            v[A <= s["abandoned_kyr"] + 1e-6] = 0
        pop[i] = v
    def holder(s, ago):
        h = s.get("holder")
        for a, p in s.get("holders") or []:
            if a >= ago - 1e-6:
                h = p
        return h
    def town_min(s, ago):
        t = tm_default
        for b in s.get("bands") or []:
            if b[0] >= ago - 1e-6:
                t = b[1]
        return t
    return pop, holder, town_min


# ------------------------------------------------------------------ the read-out

def derive(run_dir: Path, war=None, invasions=None, over: dict | None = None) -> dict:
    """The polities doc of a peoples run (FORMAT): the polities (cards) and one map per century step. Read-only.
    invasions: authored rows for war (PW-1433's hook): [{"who": people id, "whom": people id or None, "from_kyr", "to_kyr",
    "strength": "light" | "strong"}]. over: {CONSTANT: value} for this call (the nudge checks), restored after."""
    if over:
        g_ = globals()
        old = {k: g_[k] for k in over}
        g_.update(over)
        try:
            return derive(run_dir, war, invasions)
        finally:
            g_.update(old)
    from .history import params as PM
    t0 = time.time()
    R = _Run(run_dir)
    war = war or WAR
    g = R.g
    step_kyr = float(R.S.get("step_kyr") or 0.1)
    n_steps = int(round(float(R.S["from_kyr"]) / step_kyr)) + 1
    agos = [round(float(R.S["from_kyr"]) - k * step_kyr, 4) for k in range(n_steps)]
    sites = R.S["sites"]
    pop, holder, town_min = _site_tables(R, agos)
    city_min = float(R.S["tiers"]["city_min"])
    seatable = np.array([s["kind"] in SETTLED_KINDS for s in sites], bool)
    site_cell = np.array([s["cell"] for s in sites], np.int64)
    off, idx = np.asarray(g.nbr_off, np.int64), np.asarray(g.nbr_idx, np.int64)
    dist = np.full(g.n, np.inf)
    touched = np.zeros(g.n, np.int64)
    rings = _rings(g, HEMMED_RINGS)
    C = R.C["cultures"]

    polities: list[dict] = []  # (one record per polity; key -> its index in `open_`)
    open_: dict = {}  # polity key ('s<site>' or 'd<uid>') -> {"i": record index, "last": step index, "tier": ...}
    maps = []
    steps = []
    prev_owner = None
    prev_cap: dict = {}  # key -> tier of last step's ruling seats
    claimed = np.zeros(g.n, np.int64)
    lord: dict = {}  # province key -> its conqueror's key (a seat taken by war claims for its conqueror: step 3b)
    prov_rec: dict = {}  # province key -> the record id of the polity it was when taken
    cool: dict = {}  # key -> the last step its seat is held one tier down (after a fall: step 0)
    run_id = R.dir.name
    from . import invasions as IV  # (invasions you schedule, PW-1433: the rows, as war_v0 reads them, and what it saw of each)
    inv_in, inv_notes = IV.clean(invasions, strict=False)
    inv_rows = IV.hook_rows(inv_in, R, step_kyr)
    inv_log = [IV.new_log() for _ in inv_in]
    anc = IV.ancestors(R.lines)
    from . import dragon_ages as DA
    fall_p = 1.0 - float(np.exp(-FALL_PER_CENTURY * step_kyr * 10))  # (the chance per step)
    mort = DA.SCHEDULES[R.meta.get("dragon_ages") or DA.DEFAULT][DA.STAGES.index(DRAGON_RULER)]
    dragon_p = 1.0 - (1.0 - mort) ** (step_kyr * 1000)  # (a dragon realm's: its ruler dies)
    for k, ago in enumerate(agos):
        j = R.frame_of(ago)
        F = R.frame(j)
        # 0. falls (PW-1447): the base hazard, for the polities that ruled last step
        n_fell = 0
        for key, tier in list(prev_cap.items()):
            p = dragon_p if tier == "dragon realm" else (fall_p if tier in FALL_TIERS else 0.0)
            if key in lord or draw(run_id, key, k, "fall") >= p:
                continue
            o = open_.pop(key)
            rec = polities[o["i"]]
            rec["fell_kyr"], rec["fell_how"] = ago, "collapsed"
            rec["fell_why"] = "its ruler died and the realm broke up" if tier == "dragon realm" else "collapsed"
            cool[key] = k + COOL_STEPS - 1
            del prev_cap[key]
            for pk in [pk for pk, r in lord.items() if r == key]:  # (its provinces go free: successors)
                del lord[pk]
                prov_rec.pop(pk, None)
            n_fell += 1
        live = pop[:, k] > 0
        here_lines = _lines_by_cell(F, g.n)
        cl = F.setdefault("cl", {(c, l): u for c, l, u in zip(F["cells"].tolist(), F["line"].tolist(), F["cul"].tolist())})
        live_i = np.flatnonzero(live)
        site_cul = np.array([cl.get((int(site_cell[i]), R.lidx.get(holder(sites[i], ago), -1)), -1) for i in live_i], np.int64)  # (each living
        # site's culture: its holder people's culture on its cell; -1 when the presence table has none there)
        # 1. town seats (the biggest town per cell)
        cand = np.flatnonzero(live & seatable)
        best: dict = {}
        for i in cand:
            s = sites[i]
            key = f"s{s['id']}"
            inc = key in prev_cap
            p = pop[i, k]
            if p < town_min(s, ago) * (HOLD if inc else 1.0):
                continue
            c = int(site_cell[i])
            if c not in best or p > pop[best[c], k]:
                best[c] = i
        seats = []
        for c, i in best.items():
            s = sites[i]
            ppl = holder(s, ago)
            if not ppl or not R.knows(ppl, "chiefdoms", ago):
                continue
            near = here_lines.get(c, set()) | set().union(*(here_lines.get(int(b), set()) for b in idx[off[c]:off[c + 1]]))
            if not any(R.knows(p_, t, ago) for t in WRITING_TECHS for p_ in {ppl} | {R.lines[l]["id"] for l in near}):
                continue
            key = f"s{s['id']}"
            p = float(pop[i, k])
            tier = "chiefdom"
            hem = 0.0
            if (R.knows(ppl, "kingship", ago) or R.knows(ppl, "law", ago)) and cool.get(key, -1) < k:  # (a fallen capital: one tier down)
                hem = _hemmed(R, F, rings[c], ppl, here_lines, PM.SOCIAL_Q, ago)
                need = city_min * (1 - HEMMED_X * hem) * (HOLD if prev_cap.get(key) in ("state", "empire") else 1.0)
                if p >= need:
                    tier = "state"
            strong = tier == "state" and R.knows(ppl, STRONG_TECH, ago)
            cu = cl.get((c, R.lidx.get(ppl, -1)), -1)  # (the seat's culture: what an invasion row naming a culture matches, PW-1433)
            seats.append({"key": key, "site": i, "cell": c, "people": ppl, "uid": R.uids[cu] if cu >= 0 else None, "pop": p, "tier": tier, "hemmed": round(hem, 2),
                          "cls": 0 if strong else (2 if tier == "state" else 3), "rank": p * (INCUMBENT if key in prev_cap else 1.0)})
        # 2. dragon seats
        for cu, cells in _dragon_cultures(R, F):
            ppl = C[cu]["people"]
            if not R.knows(ppl, "hoards", ago):
                continue
            core = _core(cells, rings)
            key = f"d{R.uids[cu]}"
            if cool.get(key, -1) >= k:
                continue  # (a fallen dragon realm: no realm for COOL_STEPS)
            seats.append({"key": key, "site": None, "cell": core, "people": ppl, "culture": cu, "uid": R.uids[cu], "pop": 0.0, "tier": "dragon realm",
                          "cls": 1, "rank": len(cells) * (INCUMBENT if key in prev_cap else 1.0), "own": cells})
        by_key = {s["key"]: s for s in seats}
        for pk in [pk for pk, r in lord.items() if r not in by_key or pk not in by_key]:
            if lord[pk] not in by_key:  # (its conqueror rules no more this step: the province goes free)
                del lord[pk]
                prov_rec.pop(pk, None)

        def order(s):  # (a province claims right after its conqueror's capital: step 3b)
            r = by_key.get(lord.get(s["key"]))
            return (r["cls"], -r["rank"], r["key"], 1, -s["rank"]) if r else (s["cls"], -s["rank"], s["key"], 0, 0.0)
        seats.sort(key=order)
        # 3. claims
        owner = np.full(g.n, -1, np.int64)
        from_rec = np.full(g.n, -1, np.int64)  # (a province's cells: the record id of the polity it was when taken)
        settled = np.zeros(g.n, bool)
        settled[site_cell[live]] = True
        ruling = []
        pid_of: dict = {}
        absorbed = {}
        for s in seats:
            root = lord.get(s["key"])
            if owner[s["cell"]] >= 0:
                absorbed[s["key"]] = int(owner[s["cell"]])
                if root is not None and pid_of.get(root) != owner[s["cell"]]:
                    del lord[s["key"]]  # (someone else holds the province's town: lost)
                    prov_rec.pop(s["key"], None)
                continue
            if root is not None:
                if root not in pid_of:
                    del lord[s["key"]]
                    prov_rec.pop(s["key"], None)
                else:
                    b, lx, sx = _reach(R, s, ago)
                    got = _claim(s["cell"], b, lx, sx, CLIMB_M, off, idx, R.ekm, F["edz"], F["sea"], F["ice"], F["peopled"], owner, pid_of[root], dist, touched, claimed)
                    from_rec[claimed[:got]] = prov_rec[s["key"]]
                    absorbed[s["key"]] = pid_of[root]
                    continue
            pid = len(ruling)
            if s["tier"] == "dragon realm":
                may = settled.copy()
                may[s["own"]] = True
                got = _claim(s["cell"], DRAGON_KM, 1.0, 1.0, 0.0, off, idx, R.ekm, F["edz"], F["sea"], np.zeros(g.n, bool), may, owner, pid, dist, touched, claimed)
                if not np.any(settled[claimed[:got]]):
                    owner[claimed[:got]] = -1  # (a dragon realm needs settled subjects to take tribute from: judgement)
                    continue
            else:
                b, lx, sx = _reach(R, s, ago)
                got = _claim(s["cell"], b, lx, sx, CLIMB_M, off, idx, R.ekm, F["edz"], F["sea"], F["ice"], F["peopled"], owner, pid, dist, touched, claimed)
            if got:
                pid_of[s["key"]] = pid
                ruling.append(s)
        # 4. war (PW-1432): the WAR seam
        so = owner[site_cell[live_i]]
        ppl_pid = np.bincount(so[so >= 0], weights=pop[live_i[so >= 0], k], minlength=len(ruling))
        S_pid = [strength(float(ppl_pid[p]), s["people"], R.knows, ago) for p, s in enumerate(ruling)]
        ctx = {"grid": g, "seats": ruling, "ago": ago, "step": k, "run": run_id, "prev_owner": prev_owner, "strength": S_pid,
               "eligible": lambda p: ruling[p] is not None and ruling[p]["tier"] != "dragon realm" and ruling[p]["key"] in prev_cap and ruling[p]["key"] in open_,
               "invasions": inv_rows, "inv_log": inv_log, "ancestors": lambda p: anc.get(p, (p,)), "borders": lambda o=owner: borders(o, g)}
        before = owner.copy()
        owner = war(owner, ctx)
        n_taken = 0
        for w, l, how in ctx.get("taken", []):
            wk, lk = ruling[w]["key"], ruling[l]["key"]
            lo = open_.pop(lk)
            lrec, wrec = polities[lo["i"]], polities[open_[wk]["i"]]
            lrec["fell_kyr"], lrec["fell_by"], lrec["fell_how"] = ago, wrec["id"], "invaded" if how == "invasion" else "conquered"
            wrec["took"].append([ago, lrec["id"], how])
            ri = ctx.get("taken_row", {}).get(l)
            if ri is not None and 0 <= ri < len(inv_log):  # (the read-out of the row that caused it: what, when, how much land)
                inv_log[ri]["took"].append([ago, lrec["id"], wrec["id"], float((before == l).sum() * R.cell_km2)])
            m = (before == l) & (from_rec < 0)
            from_rec[m] = lrec["id"]
            for pk in [pk for pk, r in lord.items() if r == lk]:
                lord[pk] = wk
            lord[lk], prov_rec[lk] = wk, lrec["id"]
            prev_cap.pop(lk, None)
            n_taken += 1
        ruling = [s if (s is not None and owner[s["cell"]] == p) else None for p, s in enumerate(ruling)]  # (a capital taken: it falls)
        # 5. who is ruled, by whom
        step_map = []
        cnt = {t: 0 for t in TIERS}
        ent_owner = owner[F["cells"]]
        cur = {}
        for p, s in enumerate(ruling):
            cells = np.flatnonzero(owner == p) if s is not None else ()
            if not len(cells):
                continue
            m = ent_owner == p
            cul_here = F["cul"][m]
            lines_here = F["line"][m]
            ruler = s.get("culture")
            if ruler is None:
                ruler = _ruler_culture(R, F, s, cul_here, lines_here)
            mine = owner[site_cell[live_i]] == p
            sp, sc = pop[live_i[mine], k], site_cul[mine]
            people_n = float(sp.sum())
            subj, big = {}, False
            for cu in np.unique(cul_here):
                cu = int(cu)
                if cu == ruler or (s["tier"] != "dragon realm" and C[cu]["people"] in R.dragons):
                    continue  # (dragons living over a state's land are not its subjects: O4)
                n_settled = float(sp[sc == cu].sum())
                ncell = len(np.unique(F["cells"][m][cul_here == cu]))
                if n_settled > 0 or ncell >= SUBJECT_CELLS:
                    subj[R.uids[cu]] = int(round(n_settled))
                    big |= n_settled >= SUBJECT_SHARE * people_n
            tier = s["tier"]
            if tier == "state" and big:
                tier = "empire"
            cnt[tier] += 1
            cur[s["key"]] = (p, s, tier, cells, ruler, subj, people_n)
        # 6. polity records: continue, found, fall
        for key, (p, s, tier, cells, ruler, subj, people_n) in cur.items():
            o = open_.get(key)
            if o is None or k - o["last"] > GAP_STEPS:
                rec = _new_record(R, s, ruler, ago, len(polities))
                polities.append(rec)
                o = open_[key] = {"i": rec["id"], "last": k}
            rec = polities[o["i"]]
            if not rec["tiers"] or rec["tiers"][-1][1] != tier:
                rec["tiers"].append([ago, tier])
            if ruler is not None and (not rec["rulers"] or rec["rulers"][-1][1] != R.uids[ruler]):
                rec["rulers"].append([ago, R.uids[ruler]])
            for u in subj:
                rec["_subjects"].add(u)
            area = len(cells) * R.cell_km2 / 1e6
            if area > rec["peak_mkm2"]:
                rec["peak_mkm2"], rec["peak_kyr"], rec["peak_cells"] = round(area, 4), ago, int(len(cells))
            rec["peak_pop"] = max(rec["peak_pop"], int(round(people_n)))
            rec["fell_kyr"], rec["fell_why"], rec["fell_how"] = None, None, None
            o["last"] = k
            o["absorbed"] = None
            fr = from_rec[cells]  # (its provinces: the land war took, by the polity it was taken from)
            prov = {int(r): _pack(cells[fr == r]) for r in np.unique(fr[fr >= 0])}
            step_map.append([rec["id"], TIERS.index(tier), _pack(cells), subj, int(round(people_n)), prov])
        for key, o in open_.items():  # (the ones that stopped ruling this step: why, kept until they rule again or stay gone)
            if o["last"] == k - 1 and key not in cur:
                rec = polities[o["i"]]
                rec["fell_kyr"] = ago
                rec["fell_why"] = _why_fell(R, rec, key, sites, pop, k, ago, absorbed, cur)
                rec["fell_how"] = "faded"
        steps.append({"ago": ago, "frame": j, "counts": cnt, "ruled_cells": int((owner >= 0).sum()), "taken": n_taken, "collapsed": n_fell,
                      "largest": max(step_map, key=lambda e: len(_unpack(e[2])))[0] if step_map else None})
        maps.append(step_map)
        prev_owner = owner
        prev_cap = {key: v[2] for key, v in cur.items()}
    # the cultures the doc names, keyed by uid (cultures.json's stable uid, PW-1283)
    used, names = set(), {}
    for rec in polities:
        rec["subjects"] = sorted(rec.pop("_subjects"))
        used.update(u for _, u in rec["rulers"])
        used.update(rec["subjects"])
        rec["tier_peak"] = max((t for _, t in rec["tiers"]), key=TIERS.index)
        rec["name"] = _name(R, rec)
        if rec["tier_peak"] == "chiefdom":
            nm = rec["name"]
            rec["name"] = "Chiefdom in " + (nm[:1].lower() + nm[1:] if nm.split(" ")[1:2] == ["of"] else nm)  # ('west of Simath', but 'Ratal')
        nk = names[rec["name"]] = names.get(rec["name"], 0) + 1  # (numbered in founding order: 'Luki (human) 2' is Luki's second)
        if nk > 1:
            rec["name"] += f" {nk}"
    for rec in polities:
        if rec.get("fell_by") is not None:
            rec["fell_why"] = ("invaded and conquered by " if rec["fell_how"] == "invaded" else "conquered by ") + polities[rec["fell_by"]]["name"]
    by_uid = {u: i for i, u in enumerate(R.uids)}
    cult = {u: {"id": by_uid[u], "name": C[by_uid[u]]["name"], "people": C[by_uid[u]]["people"], "color": C[by_uid[u]].get("color")} for u in sorted(used)}
    for rec in polities:
        rec["color"] = _colour(cult.get(rec["rulers"][0][1], {}).get("color") if rec["rulers"] else None, rec["id"])
    return {"format": FORMAT, "version": VERSION, "run": R.dir.name, "step_kyr": step_kyr, "from_kyr": agos[0],
            "cell_km2": round(R.cell_km2, 1), "made_s": round(time.time() - t0, 1), "constants": constants(), "tiers": list(TIERS),
            "steps": steps, "polities": polities, "cultures": cult, "maps": maps,
            "invasions": {"rule": IV.RULE, "rows": IV.readout(inv_in, inv_log, polities, agos, R, anc), "problems": inv_notes}}


# ------------------------------------------------------------------ helpers

def _rings(g, n: int) -> list:
    """Per cell, the cells within n rings (not itself)."""
    off, idx = np.asarray(g.nbr_off), np.asarray(g.nbr_idx)

    class _Lazy:
        def __getitem__(self, c):
            seen, front = {c}, [c]
            for _ in range(n):
                nxt = []
                for a in front:
                    for b in idx[off[a]:off[a + 1]]:
                        b = int(b)
                        if b not in seen:
                            seen.add(b)
                            nxt.append(b)
                front = nxt
            seen.discard(c)
            return np.fromiter(seen, np.int64)
    return _Lazy()


def _lines_by_cell(F: dict, n: int) -> dict:
    out: dict = {}
    for c, l in zip(F["cells"].tolist(), F["line"].tolist()):
        out.setdefault(c, set()).add(l)
    return out


def _hemmed(R: _Run, F: dict, ring: np.ndarray, people: str, here_lines: dict, social_q: float, ago: float) -> float:
    """How hemmed in a seat is, 0..1 (Carneiro 2012, as counter._circumscribed reads it in the history): over the cells within
    HEMMED_RINGS of it, sea (for a people without boats), ice and peaks of 3,000 m or more bar fully; land other peoples hold and its
    own people do not bars SOCIAL_Q (social circumscription, "less tight"); the rest bars nothing."""
    if not len(ring):
        return 1.0
    me = next((i for i, l in enumerate(R.lines) if l["id"] == people), -1)
    boats = any(R.knows(people, t, ago) for t in BOATS)
    bar = np.zeros(len(ring))
    for i, c in enumerate(ring.tolist()):
        if F["sea"][c]:
            bar[i] = 0.0 if boats else 1.0
        elif F["ice"][c] or F["elev"][c] >= 3000:
            bar[i] = 1.0
        else:
            ls = here_lines.get(c, set())
            bar[i] = social_q if ls and me not in ls else 0.0
    return float(bar.mean())


def _reach(R: _Run, s: dict, ago: float) -> tuple[float, float, float]:
    """(budget in foot-km, cost per land km, cost per sea km or -1) of a town seat."""
    ppl = s["people"]
    if s["tier"] == "chiefdom":
        b = CHIEF_KM
    else:
        b = STATE_KM * (LAW_X if R.knows(ppl, "law", ago) else 1.0) * (DISTANCE_X if any(R.knows(ppl, t, ago) for t in DISTANCE_TECHS) else 1.0)
    lx = (1 / RIDE_X if R.knows(ppl, "riding", ago) else 1.0) * (1 / ROAD_X if R.knows(ppl, "roads", ago) else 1.0)
    sx = SAIL_X if any(R.knows(ppl, t, ago) for t in SAILS) else (BOAT_X if any(R.knows(ppl, t, ago) for t in BOATS) else -1.0)
    return b, lx, sx


def _dragon_cultures(R: _Run, F: dict):
    """(culture, its cells) of each dragon culture on the map at this frame."""
    dl = np.array([R.lines[l]["id"] in R.dragons for l in range(len(R.lines))], bool)
    m = dl[F["line"]]
    out = []
    for cu in np.unique(F["cul"][m]):
        cells = np.unique(F["cells"][m & (F["cul"] == cu)])
        out.append((int(cu), cells))
    return out


def _core(cells: np.ndarray, rings) -> int:
    """A dragon culture's seat: of its cells (a sample of at most 400), the one with the most of its cells within two rings."""
    S = set(cells.tolist())
    pick = cells if len(cells) <= 400 else cells[np.linspace(0, len(cells) - 1, 400).astype(int)]
    return int(max(pick.tolist(), key=lambda c: (sum(1 for b in rings[c].tolist() if b in S), -c)))


def _ruler_culture(R: _Run, F: dict, s: dict, cul_here: np.ndarray, lines_here: np.ndarray):
    """The ruling culture of a town seat: its holder people's culture on the capital's cell, else that people's culture on most of
    the polity's cells, else None."""
    li = next((i for i, l in enumerate(R.lines) if l["id"] == s["people"]), -1)
    at = (F["cells"] == s["cell"]) & (F["line"] == li)
    if at.any():
        return int(F["cul"][at][0])
    mine = cul_here[lines_here == li]
    if len(mine):
        v, n = np.unique(mine, return_counts=True)
        return int(v[np.argmax(n)])
    return None


def _new_record(R: _Run, s: dict, ruler, ago: float, pid: int) -> dict:
    site = R.S["sites"][s["site"]] if s.get("site") is not None else None
    lat, lon = (site["lat"], site["lon"]) if site else (float(np.degrees(np.arcsin(R.g.centers[s["cell"]][2]))), float(np.degrees(np.arctan2(R.g.centers[s["cell"]][1], R.g.centers[s["cell"]][0]))))
    return {"id": pid, "key": s["key"], "kind": "dragon" if s["tier"] == "dragon realm" else "town", "people": s["people"],
            "people_name": R.lname.get(s["people"], s["people"]).split(" (")[0],
            "capital": {"site": site["id"] if site else None, "cell": int(s["cell"]), "lat": round(lat, 2), "lon": round(lon, 2),
                        "place": site.get("place") if site else None},
            "founded_kyr": ago, "fell_kyr": None, "fell_why": None, "fell_how": None, "fell_by": None, "took": [], "tiers": [], "rulers": [], "_subjects": set(),
            "peak_mkm2": 0.0, "peak_kyr": ago, "peak_cells": 0, "peak_pop": 0}


def _why_fell(R: _Run, rec: dict, key: str, sites, pop, k: int, ago: float, absorbed: dict, cur: dict) -> str:
    if key in absorbed:
        return "its capital came under a stronger neighbour"
    if rec["kind"] == "dragon":
        return "the dragons lost their hold (no settled people within reach, or the culture ended)"
    i = rec["capital"]["site"]
    s = sites[i] if i is not None else None
    if s is not None and pop[i, k] <= 0:
        return f"its capital was abandoned ({s.get('why') or 'left'})" if s.get("abandoned_kyr") is not None else "its capital emptied"
    return "its capital shrank below a seat of rule"


def _name(R: _Run, rec: dict) -> str:
    """A name for the card: its capital's region and ruling people, 'West of Simath (human)', numbered when repeated (real names: PW-856's names slot, later)."""
    if rec["kind"] == "dragon":
        return f"Realm of the {R.lname.get(rec['people'], rec['people']).split(' (')[0]}"
    place = rec["capital"]["place"] or f"cell {rec['capital']['cell']}"
    place = place.removeprefix("the ")
    return f"{place[:1].upper()}{place[1:]} ({rec['people'].replace('_', '-')})"


def _colour(base: str | None, pid: int) -> str:
    """A polity's colour: its ruling culture's, shifted in lightness by its id so neighbouring polities of one culture differ."""
    import colorsys
    h = (base or "#888888").lstrip("#")
    r, gg, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, ll, ss = colorsys.rgb_to_hls(r, gg, b)
    ll = min(0.8, max(0.25, ll + ((pid * 37) % 7 - 3) * 0.06))
    hh = (hh + ((pid * 13) % 5 - 2) * 0.015) % 1
    r, gg, b = colorsys.hls_to_rgb(hh, ll, max(0.35, ss))
    return "#%02x%02x%02x" % (round(r * 255), round(gg * 255), round(b * 255))


def _pack(cells: np.ndarray) -> list:
    """Sorted cells as runs [start, length, start, length, ...] (a polity's land is mostly contiguous cell ids? no: but it compresses
    chiefdoms and keeps the doc small)."""
    c = np.sort(np.asarray(cells, np.int64))
    if not len(c):
        return []
    br = np.flatnonzero(np.diff(c) != 1) + 1
    starts = np.concatenate([[0], br])
    ends = np.concatenate([br, [len(c)]])
    return np.stack([c[starts], ends - starts], 1).ravel().tolist()


def _unpack(runs: list) -> np.ndarray:
    a = np.asarray(runs, np.int64).reshape(-1, 2)
    return np.concatenate([np.arange(s, s + n) for s, n in a]) if len(a) else np.zeros(0, np.int64)


# ------------------------------------------------------------------ the doc's views

def summary(doc: dict) -> dict:
    """The doc without its maps: the polities (cards), the cultures they name and the per-step counts (the viewer's first fetch)."""
    return {k: v for k, v in doc.items() if k != "maps"}


def step_view(doc: dict, ago: float) -> dict:
    """The step nearest `ago` (kyr): {step, ago, polities: [{id, tier, cells: [...], subjects: {uid: people}, people,
    provinces: {record id: [cells]}}]} (provinces: the land war took, by the polity it was taken from; see the record's "took")."""
    st = doc["steps"]
    if not st:
        return {"step": None, "ago": ago, "polities": []}
    k = min(range(len(st)), key=lambda i: (abs(st[i]["ago"] - ago), st[i]["ago"]))
    return {"step": k, "ago": st[k]["ago"], "polities": [{"id": e[0], "tier": doc["tiers"][e[1]], "cells": _unpack(e[2]).tolist(), "subjects": e[3], "people": e[4],
                                                          "provinces": {str(r): _unpack(v).tolist() for r, v in (e[5] if len(e) > 5 else {}).items()}}
                                                         for e in doc["maps"][k]]}


def lifetimes(doc: dict) -> dict:
    """Per kind ('states and empires', 'dragon realms'): the years from founding to fall of those that fell, and Taagepera 1997's
    measure, the years at half or more of the polity's peak area (whole steps), for all of them."""
    step_y = round(doc["step_kyr"] * 1000)
    area: dict = {}
    for m in doc["maps"]:
        for e in m:
            area.setdefault(e[0], []).append(sum(e[2][1::2]))
    out = {}
    for kind, tiers in (("states and empires", ("state", "empire")), ("dragon realms", ("dragon realm",))):
        P = [p for p in doc["polities"] if p["tier_peak"] in tiers]
        fell = sorted(round((p["founded_kyr"] - p["fell_kyr"]) * 1000) for p in P if p["fell_kyr"] is not None)
        half = sorted(sum(a >= 0.5 * max(area[p["id"]]) for a in area[p["id"]]) * step_y for p in P if p["id"] in area)
        out[kind] = {"n": len(P), "fell": fell, "half": half, "standing": sum(p["fell_kyr"] is None for p in P),
                     "how": {h: sum(p.get("fell_how") == h for p in P) for h in ("conquered", "invaded", "collapsed", "faded")}}
    return out


def report(doc: dict) -> list[str]:
    """Plain lines for a review: counts, the largest polity and the people per tier at a few moments, the conquests and the lifetimes."""
    from .years import years_ago
    out = []
    P = doc["polities"]
    for st, m in zip(doc["steps"], doc["maps"]):
        if round(st["ago"] * 10) % 10 or not m:
            continue
        sizes = sorted(((sum(e[2][1::2]) * doc["cell_km2"] / 1e6, doc["tiers"][e[1]], e[4], e[0]) for e in m), reverse=True)
        a, t, n, p = sizes[0]
        out.append(f"{years_ago(st['ago'])}: " + ", ".join(f"{v} {k}" + ("s" if v != 1 else "") for k, v in st["counts"].items() if v)
                   + f"; largest {P[p]['name']} ({t}, {a:.3f} Mkm2, ~{n:,} settled people); over 1 Mkm2: {sum(x[0] >= 1 for x in sizes)}")
    if doc["maps"] and doc["maps"][-1]:
        last = doc["maps"][-1]
        for t, nm in enumerate(doc["tiers"]):
            ns = sorted(e[4] for e in last if e[1] == t)
            ar = sorted(sum(e[2][1::2]) * doc["cell_km2"] for e in last if e[1] == t)
            if ns:
                out.append(f"the present, {nm}s: {len(ns)}; settled people median {ns[len(ns) // 2]:,} (range {ns[0]:,}-{ns[-1]:,}); "
                           f"land median {ar[len(ar) // 2]:,.0f} km2 (largest {ar[-1]:,.0f} km2)")
        ruled = sum(sum(e[2][1::2]) for e in last)
        out.append(f"the present: {ruled * doc['cell_km2'] / 1e6:.2f} Mkm2 ruled ({ruled} cells)")
    peak = max(P, key=lambda p: p["peak_mkm2"], default=None)
    if peak:
        out.append(f"largest ever: {peak['name']} ({peak['tier_peak']}), {peak['peak_mkm2']:.2f} Mkm2 {years_ago(peak['peak_kyr'])}")
    out.append(f"conquests: {sum(s.get('taken', 0) for s in doc['steps'])}; collapses: {sum(s.get('collapsed', 0) for s in doc['steps'])}")
    for kind, L in lifetimes(doc).items():
        if L["n"]:
            f, h = L["fell"], L["half"]
            out.append(f"{kind}: {L['n']} ({L['standing']} still stand); founding to fall, median {f[len(f) // 2] if f else '-'} years"
                       f" (300+ years: {sum(d >= 300 for d in f)} of {len(f)}); at half peak area or more, median {h[len(h) // 2] if h else '-'} years"
                       f" (300+: {sum(d >= 300 for d in h)}); fell by " + ", ".join(f"{k} {v}" for k, v in L["how"].items() if v))
    return out
