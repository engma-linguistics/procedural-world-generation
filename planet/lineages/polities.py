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
  4. War (PW-1432) plugs in after the claims: WAR(owner, ctx) may move cells between neighbouring polities (borders() lists the
     neighbours); the default changes nothing. A polity whose capital cell is taken falls.

Reach is a budget of foot-km (km on foot over flat ground): a chiefdom CHIEF_KM (its own cell at L7), a state STATE_KM, more with
law and government at a distance; riding and roads make a km cheaper, climbing dearer; the sea needs boats. Every number below is
sourced or labelled a judgement call.
"""

from __future__ import annotations

import heapq
import json
import time
from pathlib import Path

import numpy as np
from numba import njit

FORMAT = "procgen-polities/1"
VERSION = 1  # (bump when the rules change: the server's cached docs are remade)

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
# ---- empires
SUBJECT_SHARE = 0.2  # judgement: an empire is a state where another culture (not dragons living over it) holds 20% or more of its settled people
SUBJECT_CELLS = 3  # judgement: the card lists a subject culture with settlements in the polity, or living on 3 or more of its cells
WRITING_TECHS = ("writing",)  # owner P2 "nearly B" (owner-notes-r1.md): a chiefdom needs writing, its own or a neighbour's (round 2's lenience)
TIERS = ("chiefdom", "state", "empire", "dragon realm")
SETTLED_KINDS = ("chief", "minority")  # (seats: a people's own places; mines and pits count for people, never as capitals)
R_EARTH_KM = 6371.0  # (the grid's sphere, as cultures.py and demes.py measure areas)


def constants() -> dict:
    """The rules' numbers, for the doc (each one's source is beside it above)."""
    return {k: v for k, v in globals().items() if k.isupper() and isinstance(v, (int, float, tuple, str)) and k not in ("FORMAT",)}


# ------------------------------------------------------------------ the claim kernel

@njit(cache=True)
def _claim(seed, budget, land_x, sea_x, climb_m, off, idx, ekm, edz, sea, blocked, may, owner, pid, dist, touched):
    """One seat's claim: a Dijkstra from seed over cells not owned by another polity and not blocked, each step costing its km x
    land_x (x (1 + climb / climb_m) when climb_m > 0), or x sea_x when either end is sea (sea_x < 0: no sea). Claims the cells it
    reaches within budget where may[c] and owner[c] < 0. Returns the number claimed; dist is left all inf."""
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


WAR = no_war


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

def derive(run_dir: Path, war=None) -> dict:
    """The polities doc of a peoples run (FORMAT): the polities (cards) and one map per century step. Read-only."""
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
    for k, ago in enumerate(agos):
        j = R.frame_of(ago)
        F = R.frame(j)
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
            if R.knows(ppl, "kingship", ago) or R.knows(ppl, "law", ago):
                hem = _hemmed(R, F, rings[c], ppl, here_lines, PM.SOCIAL_Q, ago)
                need = city_min * (1 - HEMMED_X * hem) * (HOLD if prev_cap.get(key) in ("state", "empire") else 1.0)
                if p >= need:
                    tier = "state"
            strong = tier == "state" and R.knows(ppl, STRONG_TECH, ago)
            seats.append({"key": key, "site": i, "cell": c, "people": ppl, "pop": p, "tier": tier, "hemmed": round(hem, 2),
                          "cls": 0 if strong else (2 if tier == "state" else 3), "rank": p * (INCUMBENT if key in prev_cap else 1.0)})
        # 2. dragon seats
        for cu, cells in _dragon_cultures(R, F):
            ppl = C[cu]["people"]
            if not R.knows(ppl, "hoards", ago):
                continue
            core = _core(cells, rings)
            key = f"d{R.uids[cu]}"
            seats.append({"key": key, "site": None, "cell": core, "people": ppl, "culture": cu, "pop": 0.0, "tier": "dragon realm",
                          "cls": 1, "rank": len(cells) * (INCUMBENT if key in prev_cap else 1.0), "own": cells})
        seats.sort(key=lambda s: (s["cls"], -s["rank"], s["key"]))
        # 3. claims
        owner = np.full(g.n, -1, np.int64)
        settled = np.zeros(g.n, bool)
        settled[site_cell[live]] = True
        ruling = []
        absorbed = {}
        for s in seats:
            if owner[s["cell"]] >= 0:
                absorbed[s["key"]] = int(owner[s["cell"]])
                continue
            pid = len(ruling)
            if s["tier"] == "dragon realm":
                may = settled.copy()
                may[s["own"]] = True
                got = _claim(s["cell"], DRAGON_KM, 1.0, 1.0, 0.0, off, idx, R.ekm, F["edz"], F["sea"], np.zeros(g.n, bool), may, owner, pid, dist, touched)
                if not np.any((owner == pid) & settled):
                    owner[owner == pid] = -1  # (a dragon realm needs settled subjects to take tribute from: judgement)
                    continue
            else:
                b, lx, sx = _reach(R, s, ago)
                got = _claim(s["cell"], b, lx, sx, CLIMB_M, off, idx, R.ekm, F["edz"], F["sea"], F["ice"], F["peopled"], owner, pid, dist, touched)
            if got:
                ruling.append(s)
        # 4. war (PW-1432 plugs in here)
        owner = war(owner, {"grid": g, "seats": ruling, "ago": ago, "step": k, "prev_owner": prev_owner, "borders": lambda o=owner: borders(o, g)})
        ruling = [s for p, s in enumerate(ruling) if owner[s["cell"]] == p]  # (a capital taken by war: that polity falls)
        # 5. who is ruled, by whom
        step_map = []
        cnt = {t: 0 for t in TIERS}
        ent_owner = owner[F["cells"]]
        cur = {}
        for p, s in enumerate(ruling):
            cells = np.flatnonzero(owner == p)
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
            rec["fell_kyr"], rec["fell_why"] = None, None
            o["last"] = k
            o["absorbed"] = None
            step_map.append([rec["id"], TIERS.index(tier), _pack(cells), subj, int(round(people_n))])
        for key, o in open_.items():  # (the ones that stopped ruling this step: why, kept until they rule again or stay gone)
            if o["last"] == k - 1 and key not in cur:
                rec = polities[o["i"]]
                rec["fell_kyr"] = ago
                rec["fell_why"] = _why_fell(R, rec, key, sites, pop, k, ago, absorbed, cur)
        steps.append({"ago": ago, "frame": j, "counts": cnt, "ruled_cells": int((owner >= 0).sum()),
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
            rec["name"] = "Chiefdom in " + rec["name"][:1].lower() + rec["name"][1:]
        nk = names[rec["name"]] = names.get(rec["name"], 0) + 1  # (numbered in founding order: 'Luki (human) 2' is Luki's second)
        if nk > 1:
            rec["name"] += f" {nk}"
    by_uid = {u: i for i, u in enumerate(R.uids)}
    cult = {u: {"id": by_uid[u], "name": C[by_uid[u]]["name"], "people": C[by_uid[u]]["people"], "color": C[by_uid[u]].get("color")} for u in sorted(used)}
    for rec in polities:
        rec["color"] = _colour(cult.get(rec["rulers"][0][1], {}).get("color") if rec["rulers"] else None, rec["id"])
    return {"format": FORMAT, "version": VERSION, "run": R.dir.name, "step_kyr": step_kyr, "from_kyr": agos[0],
            "cell_km2": round(R.cell_km2, 1), "made_s": round(time.time() - t0, 1), "constants": constants(), "tiers": list(TIERS),
            "steps": steps, "polities": polities, "cultures": cult, "maps": maps}


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
            "founded_kyr": ago, "fell_kyr": None, "fell_why": None, "tiers": [], "rulers": [], "_subjects": set(),
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
    """The step nearest `ago` (kyr): {step, ago, polities: [{id, tier, cells: [...], subjects: {uid: cells}, people}]}."""
    st = doc["steps"]
    if not st:
        return {"step": None, "ago": ago, "polities": []}
    k = min(range(len(st)), key=lambda i: (abs(st[i]["ago"] - ago), st[i]["ago"]))
    return {"step": k, "ago": st[k]["ago"], "polities": [{"id": p, "tier": doc["tiers"][t], "cells": _unpack(runs).tolist(), "subjects": subj, "people": n}
                                                          for p, t, runs, subj, n in doc["maps"][k]]}


def report(doc: dict) -> list[str]:
    """Plain lines for a review: counts, the largest polity and the people per tier at a few moments, and the lifetimes."""
    from .years import years_ago
    out = []
    P = doc["polities"]
    for st, m in zip(doc["steps"], doc["maps"]):
        if round(st["ago"] * 10) % 10 or not m:
            continue
        sizes = sorted(((sum(r[1::2]) * doc["cell_km2"] / 1e6, doc["tiers"][t], n, p) for p, t, r, _, n in m), reverse=True)
        a, t, n, p = sizes[0]
        out.append(f"{years_ago(st['ago'])}: " + ", ".join(f"{v} {k}" + ("s" if v != 1 else "") for k, v in st["counts"].items() if v)
                   + f"; largest {P[p]['name']} ({t}, {a:.3f} Mkm2, ~{n:,} settled people)")
    if doc["maps"] and doc["maps"][-1]:
        last = doc["maps"][-1]
        for t, nm in enumerate(doc["tiers"]):
            ns = sorted(n for _, tt, _, _, n in last if tt == t)
            ar = sorted(sum(r[1::2]) * doc["cell_km2"] for _, tt, r, _, _ in last if tt == t)
            if ns:
                out.append(f"the present, {nm}s: {len(ns)}; settled people median {ns[len(ns) // 2]:,} (range {ns[0]:,}-{ns[-1]:,}); "
                           f"land median {ar[len(ar) // 2]:,.0f} km2 (largest {ar[-1]:,.0f} km2)")
        ruled = sum(sum(r[1::2]) for _, _, r, _, _ in last)
        out.append(f"the present: {ruled * doc['cell_km2'] / 1e6:.2f} Mkm2 ruled ({ruled} cells)")
    lives = [(p["fell_kyr"] if p["fell_kyr"] is not None else 0.0) for p in P]
    dur = sorted(round((p["founded_kyr"] - e) * 1000) for p, e in zip(P, lives) if p["tier_peak"] != "chiefdom")
    if dur:
        out.append(f"states, empires and realms: {len(dur)}; median life {dur[len(dur) // 2]} years; 300+ years: {sum(d >= 300 for d in dur)}")
    return out
