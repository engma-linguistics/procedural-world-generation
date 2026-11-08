"""Trade step 2 (PW-1503): goods move between neighbours and fade with the cost of carrying them.

In plain words: the goods ledger (trade.py, step 1) says what each culture's land gives beyond its own need and what it lacks. Here the
spare goods travel. From every cell with a surplus, supply spreads over the map and fades with the cost of carrying it there and then:
on foot, by pack animal, by cart or road, by river boat (cheaper downstream), along the coast, over open sea, or (light goods only) on
the wings of a flying people. A cell that lacks a good takes it from the best supply that reaches it, up to its lack; the culture whose
cell that supply came from is the giver. Summed over a culture's cells (D64 B, PW-1500: cells for goods and costs, summed to cultures),
that gives each culture's imports per good: from whom, how far, by what way, and of what kind (gifts between bands, barter, a market,
merchants, tribute).

How (design1.md step 2; numbers and sources in review1.md section 6, cited R§n):
- One cost walk per good per frame (Dijkstra from all of the good's surplus cells at once, as salt_reach._spfa walks from all salt).
  A source cell starts at cost -L ln(surplus), so the supply reaching a cell, exp(-cost / L), is the best of surplus x exp(-carry / L)
  over all sources: Renfrew's exponential fall-off beyond the source (R§1).
- An edge's cost is its km x the cheapest mode open on it at that frame (MODES, per km, a pack animal = 1), plus a toll where it enters
  another culture (TOLL, lowered by that culture's tolerance, attitudes.py; closed by a war between the two sides' polities in that
  century, polities.py). The modes open with techs the tree already has, known by the culture that holds the cell.
- L, the fall-off length, is one per value class (FALL_KM), each from a sourced distance; the class is the ledger's (trade.GOODS), except
  that tin falls off as a precious good (R§6: tin is among the light, valuable goods that go thousands of km; Kanesh, R§3).
- The kind of exchange is a label from the two sides (kind_of); it does not change the physics (R§1: fall-off curves separate valuable
  goods from bulky ones, not reciprocity from markets; review1.md "what the model takes" 4).
- Peoples by body (D65 A + Daniel's additions, PW-1501): flyers carry only light (precious) goods, at a flat cost over any ground or sea
  (AIR); sea peoples move goods over their own water as cheaply as ships (SEA) and meet land peoples at the shore (an ordinary border);
  mining kinds trade from their holds as towns do (trade.py: their people want as a town's; flows to and from them are market trade);
  dragons take tribute from the peoples on their land and their kobolds trade the realm's surplus (via "kobolds"); giants trade or take
  tribute by kind (trade.GIANT_MODE, PW-1507). Flyers also carry foods to regions where they are not grown (flyer_foods: recorded for the
  culinary brief and the crop spread to read later; nothing is spread here).

Read after the run (D63 A, PW-1499): nothing here changes the history or any run file. The doc keeps per frame and culture its imports per
good (food included: grain, herd animals, dried fish), so step 4d can read a culture's bought food in place of ladder.TRADE_CAP and
BARTER_CAP once trade feeds back (food_bought).
"""

from __future__ import annotations

import heapq
import math
import time
from pathlib import Path

import numpy as np
from numba import njit

from ..geo import R_KM
from . import trade as TR

VERSION = 3  # (2: routes, trading towns and merchant quarters, PW-1504; herders fetch grain, PW-1511 B; flyers carry wild foods, PW-1510;
# 3: a route is judged per good against its carried volume, and last era's routes hold down to half the bar, PW-1515 and PW-1514)
FORMAT = "procgen-trade-flows/1"

# --- cost per km of each mode, a pack animal = 1 (R§6). ORBIS (Scheidel, Meeks & Weiland 2012, from Diocletian's Price Edict), denarii per kg
# of wheat per km: donkey or camel 0.028, wagon 0.035, river 0.0034 downstream and 0.0068 upstream, sea ~0.001. Cheng 2024 (China ~1680):
# pack mule on the flat 0.213, in hills 0.452, porter 1.594 taels per 100 kg per 100 km.
PACK = 1.0  # pack animal (`pack_animals`: donkey-, camel- or llama-like; the tech needs herding): ORBIS 0.028
CART = 0.035 / 0.028  # cart on flat open ground (`wheel`), or road on the culture's own land (`roads`, any ground): ORBIS wagon 0.035
PORTER = 3.0  # on foot, always open. JUDGEMENT within Cheng's porter / mule 7.5 (hill roads included; hill-to-flat mule 2.1) and the loads,
# forager women 20-30 kg against a donkey's 65-100 kg (R§2, R§6); ORBIS has no porter cost (design1.md step 2)
HILL = 0.452 / 0.213  # porter and pack animal in hills against the flat (Cheng 2024); blended by the world's hills (and peaks) layer, 0..1
RIVER_DOWN = 0.0034 / 0.028  # river boat downstream (`canoes` on a river navigable by small boats, river_nav >= 1): ORBIS
RIVER_UP = 0.0068 / 0.028  # upstream: ORBIS
SEA = 0.001 / 0.028  # ship along any coast (`sails` or `plank_boats`), over open sea (`navigation`, or ocean ships, animals.ocean_ships): ORBIS
CANOE_COAST = RIVER_UP  # a canoe along the coast, one cell out (`canoes`). JUDGEMENT: paddled, as against a current; no coastal canoe cost
# was found
AIR = PACK  # a flyer's load per km over any ground, mountain or sea. JUDGEMENT (D65 A): a flying people carries a light load as a pack
# animal does; no source
ROUTE = 1.3  # path km per straight km between cell centres (as salt_reach.ROUTE and seafood.ROUTE)
MODES = ("land", "river", "sea", "air")

# --- fall-off length per value class, in cost-km (pack-animal km): supply left after carrying = exp(-cost / L)
FALL_KM = {
    # Cato: moving a mill 75 miles cost 39% of its value (Adams 2007, R§6); ~111-121 km by cart: L = 116 km x CART / -ln(0.61) ~ 290
    "bulk": round(116.0 * CART / -math.log(1 - 0.39)),
    # Anatolian obsidian (R§1, the agent-based study): village-to-village relay keeping 50% a hop with villages ~100 km apart fits the
    # 700-800 km tail. On foot: L = 100 km x PORTER / ln 2 ~ 433 (salt's existing trade cap is 450 cost-km)
    "middling": round(100.0 * PORTER / math.log(2)),
    # Kanesh: tin went ~1,200 km by donkey (Dercksen 2022, R§3); Alpine jade >1,000 km. JUDGEMENT: 1,200 pack-km as the e-folding, in
    # design1.md's sourced 1,000-1,500
    "precious": 1200,
}
FALL_CLASS = {"tin": "precious"}  # (R§6: tin, textiles, silver, salt slabs on camels, pepper and beads carry far)
TOLL = 0.10  # share of a good's value lost crossing into another culture at the median tolerance: road tolls ~10% of value (Dercksen 2022, R§3)
TOL_MID = 0.5  # the tolerance at which the toll is TOLL (attitudes.py: the cultures' median is ~0.48-0.5 on the judge runs)
TOLL_MAX = 0.5  # JUDGEMENT: the most an intolerant culture's border takes (a war closes it instead)
FLOOR = 0.01  # supply below 1% of its source's is not followed (a compute cut, not a model number)
FLOW_MIN = 0.002  # a flow under 0.2% of its taker's people is left out of the doc (display rounding)
TOWN_MIN = 0.1  # a culture with this share of its people in towns trades at markets (step 1's judge cut for "towns")
TRIBUTE_GOODS = ("grain", "livestock", "gold", "gems")  # what a tribute-taking kind takes from the peoples on its land: food and the hoard.
# JUDGEMENT (D65: dragons take tribute; R§5: tribute is grain, cloth and luxuries); herds for a dragon's table
CARRIERS = ("pack_saddle", "caravanserais", "sails", "plank_boats", "harbours", "navigation")  # merchants' carriers: caravans and ships (R§4)
FOODS = ("grain", "livestock", "dried_fish")  # the goods that are food (for step 4d: food_bought)
QUARTERS = True  # step 3 (PW-1504): a merchant quarter lifts its border's toll in the next frame (design1.md steps 2-3); False: no carry-over
FETCH = False  # PW-1511 B (needs-decision): True: herders fetch grain with their own animals. Off: it met no more of their need on the judge runs (step3.md)
FETCH_GOODS = ("grain",)  # PW-1511 B: what herders fetch with their own animals (Khazanov 2019: grain from the frontier markets)
ROUNDS = 3  # a taker cut short by an emptied source looks for the next best source up to this many times (a compute bound)


@njit(cache=True)
def _allocate(order, org, ask, avail):
    """Shares out each source's supply (avail, per source cell; reduced in place) to its takers in `order` (best supplied first): each
    gets min(what it asks, what is left)."""
    got = np.zeros(ask.shape[0])
    for k in order:
        o = org[k]
        x = min(ask[k], avail[o])
        if x > 0.0:
            got[k] = x
            avail[o] -= x
    return got


@njit(cache=True)
def _walk(src, d0, nbr_off, nbr_idx, ecost, ekm, emode, ebord, limit):
    """Multi-source least cost (Dijkstra) over the cells: edge e from cell i (nbr_off[i] <= e < nbr_off[i+1]) to nbr_idx[e] costs ecost[e]
    (< 0: closed). Each source s starts at d0. Returns (cost, origin source cell, km along the path, km per mode (n x 4), borders crossed);
    cells beyond `limit` stay at inf with origin -1. Also the edge each cell was reached by (-1 at a source), for the routes (step 3)."""
    n = nbr_off.shape[0] - 1
    d = np.full(n, np.inf)
    org = np.full(n, -1, np.int64)
    pe = np.full(n, -1, np.int64)
    km = np.zeros(n)
    mkm = np.zeros((n, 4))
    nb = np.zeros(n, np.int32)
    h = [(0.0, np.int64(0))]
    h.pop()
    for k in range(src.shape[0]):
        s = src[k]
        if d0[k] < d[s]:
            d[s] = d0[k]
            org[s] = s
            pe[s] = -1
            heapq.heappush(h, (d0[k], s))
    while len(h) > 0:
        di, i = heapq.heappop(h)
        if di > d[i]:
            continue
        for e in range(nbr_off[i], nbr_off[i + 1]):
            c = ecost[e]
            if c < 0.0:
                continue
            j = nbr_idx[e]
            nd = di + c
            if nd < d[j] and nd <= limit:
                d[j] = nd
                org[j] = org[i]
                pe[j] = e
                km[j] = km[i] + ekm[e]
                for m in range(4):
                    mkm[j, m] = mkm[i, m]
                mkm[j, emode[e]] += ekm[e]
                nb[j] = nb[i] + ebord[e]
                heapq.heappush(h, (nd, j))
    return d, org, km, mkm, nb, pe


def _knows(kn: set, techs) -> bool:
    return any(t in kn for t in techs)


def _tolerance(att: dict | None, c: int, era: float) -> float:
    """A culture's tolerance at the era (attitudes.py read-out: its track, newest sample at or before the era), else the median."""
    r = ((att or {}).get("cultures") or {}).get(str(c))
    if not r:
        return TOL_MID
    best = None
    for kyr, tol, _ in r.get("track") or []:
        if kyr >= era - 1e-9 and (best is None or kyr < best[0]):
            best = (kyr, tol)
    return float(best[1]) if best else float((r.get("now") or [TOL_MID])[0])


def _herder(row: dict | None) -> bool:
    """A herding culture: herding is the biggest of its ways of life (farm, herd, forage; as kind_of reads a forager band)."""
    w = (row or {}).get("ways") or {}
    return bool(w) and max(("farm", "herd", "forage"), key=lambda k: w.get(k, 0)) == "herd"


def _polity_state(pol: dict | None, era: float, n: int, C: list) -> tuple[np.ndarray, set, dict]:
    """(polity id per cell at the step before the one nearest the era (as its wars began), -1 none; the (winner, loser) pairs at war in that century; ruling culture ->
    the cultures subject to it)."""
    owner = np.full(n, -1, np.int64)
    if not pol or not pol.get("steps"):
        return owner, set(), {}
    from .polities import _unpack
    st = pol["steps"]
    k = min(range(len(st)), key=lambda q: abs(st[q]["ago"] - era))
    half = 0.5 * float(pol.get("step_kyr") or 0.1)
    wars = set()
    for rec in pol["polities"]:
        for t in rec.get("took") or []:
            if abs(float(t[0]) - era) <= half + 1e-9:
                wars.add((rec["id"], int(t[1])))
                wars.add((int(t[1]), rec["id"]))
    cid = {u: v["id"] for u, v in (pol.get("cultures") or {}).items()}
    recs = {r["id"]: r for r in pol["polities"]}
    rules: dict = {}
    for e in pol["maps"][max(k - 1, 0)]:  # (the borders as the century's wars began: a war's step map is drawn after its taking)
        cells = _unpack(e[2])
        owner[cells[cells < n]] = e[0]
    for e in pol["maps"][k]:
        rec = recs.get(e[0])
        if rec and rec.get("rulers"):
            ru = None
            for a, u in rec["rulers"]:
                if a >= era - 1e-9:
                    ru = u
            if ru in cid:
                r = TR._at(C, cid[ru], era)
                rules.setdefault(r, set()).update(TR._at(C, cid[u], era) for u in (e[3] or {}) if u in cid)
    return owner, wars, rules


class _Frame:
    """One frame's carriers, costs and per-good walks."""

    def __init__(self, ctx, i: int, pol: dict | None, att: dict | None, scale: dict | None = None, quarters: set | None = None,
                 fetch: bool = False):
        self.ctx, self.i = ctx, i
        self.fetch = fetch
        self.era = era = -float(ctx.ts[i])
        sc = scale or {}
        self.L = {k: v * sc.get("L", 1.0) for k, v in FALL_KM.items()}
        self.P = P = TR.pairs_at(ctx, i)
        self.rows = TR.ledger_at(ctx, i) or {}
        g = ctx.g
        n = g.n
        C = ctx.cultures()["cultures"]
        cell, cu = P["cell"], P["culture"]
        tree = {t.get("id") for t in (ctx.meta.get("techtree") or {}).get("techs") or []}
        ids = np.unique(cu)
        self.info = info = {}
        for c in ids.tolist():
            pid = C[c]["people"]
            line = ctx.lines[ctx.idx[pid]] if pid in ctx.idx else {}
            m = TR.mode_of(ctx, pid)
            kn = TR._known_at(ctx, pid, era)
            boat = 3 if "navigation" in kn else 2 if _knows(kn, ("sails", "plank_boats")) else 1 if "canoes" in kn else 0
            info[c] = {"pid": pid, "know": kn, "mode": m["mode"], "via": m["via"], "flies": "flies" in (line.get("traits") or []) and m["mode"] == "trade",
                       "sea": line.get("realm", "land") != "land", "miner": "miner" in (line.get("traits") or []), "boat": boat,
                       "tol": _tolerance(att, c, era), "people": (self.rows.get(c) or {}).get("people", 0), "herder": _herder(self.rows.get(c))}
        from .animals import ocean_ships
        ships = ocean_ships(str(ctx.meta.get("era") or ""), era)
        X = TR.cells_at(ctx, i)
        land = X["land"] & ~(ctx.f("ice", i).astype(float) > 0.5)  # (ground carriers cross no ice sheet)
        ice = ctx.f("ice", i).astype(float) > 0.5
        elev = ctx.f("elevation", i).astype(float)
        sea = ~land & ~ice
        # the carrier of each cell: on land the biggest trading land culture there, at sea a sea people (tribute-takers carry nothing)
        score = np.array([info[c]["people"] + 1.0 if info[c]["mode"] == "trade" else -1.0 for c in cu.tolist()]) if len(cu) else np.zeros(0)
        is_sea_c = np.array([info[c]["sea"] for c in cu.tolist()], bool) if len(cu) else np.zeros(0, bool)
        ok = (score > 0) & np.where(sea[cell], is_sea_c, ~is_sea_c)
        own = np.full(n, -1, np.int64)
        best = np.full(n, -np.inf)
        for p in np.flatnonzero(ok)[np.argsort(score[ok], kind="stable")]:  # (ascending: the biggest written last)
            own[cell[p]] = cu[p]
            best[cell[p]] = score[p]
        self.own = own
        oc = np.maximum(own, 0)
        has = own >= 0
        tab = lambda f, dflt: np.array([f(info[c]) if c in info else dflt for c in range(len(C))])  # noqa: E731 (per culture id)
        attr = lambda f: tab(f, False).astype(bool)[oc] & has  # noqa: E731
        pack = attr(lambda r: "pack_animals" in r["know"])
        wheel = attr(lambda r: "wheel" in r["know"])
        roads = attr(lambda r: "roads" in r["know"])
        canoes = attr(lambda r: "canoes" in r["know"])
        boat = tab(lambda r: r["boat"], 0)[oc] * has
        G = ctx.goods
        hills = np.clip(np.maximum(np.asarray(G.get("hills", np.zeros(n)), float), np.asarray(G.get("peaks", np.zeros(n)), float)), 0, 1)
        hm = 1.0 + (HILL - 1.0) * hills
        mx = sc.get("modes") or {}  # (the judge's nudge: a multiplier per mode factor)
        M = {k: v * mx.get(k, 1.0) for k, v in (("porter", PORTER), ("pack", PACK), ("cart", CART), ("sea", SEA), ("canoe", CANOE_COAST), ("down", RIVER_DOWN), ("up", RIVER_UP))}
        f_land = M["porter"] * hm
        f_land = np.where(pack, np.minimum(f_land, M["pack"] * hm), f_land)
        f_land = np.where(wheel & (hills < 0.5), np.minimum(f_land, M["cart"]), f_land)
        f_land = np.where(roads, np.minimum(f_land, M["cart"]), f_land)
        # sea: a coastal cell (next to land) is open to the best boats of the land cultures beside it (and two cells along the coast);
        # open sea once ocean ships sail or anyone on the map knows navigation; a sea people's own cells always
        nbr_off, nbr_idx = g.nbr_off, g.nbr_idx
        srcs = np.repeat(np.arange(n), np.diff(nbr_off))
        coastal = sea & (np.bincount(srcs, weights=land[nbr_idx].astype(float), minlength=n) > 0)
        tier = np.zeros(n)
        np.maximum.at(tier, srcs, np.where(land[nbr_idx], boat[nbr_idx], 0))
        tier = np.where(coastal, tier, 0)
        for _ in range(2):
            t2 = tier.copy()
            np.maximum.at(t2, srcs, np.where(coastal[nbr_idx], tier[nbr_idx], 0))
            tier = np.where(coastal, t2, 0)
        open_sea = ships or any(r["boat"] >= 3 for r in info.values())
        f_sea = np.where(coastal & (tier >= 2), M["sea"], np.where(coastal & (tier >= 1), M["canoe"], -1.0))
        f_sea = np.where(sea & ~coastal & open_sea, M["sea"], f_sea)
        f_sea = np.where(sea & has, M["sea"], f_sea)  # (a sea people's own water)
        fcell = np.where(land, f_land, np.where(sea, f_sea, -1.0))
        # edges
        a, b = srcs, nbr_idx
        hop = float(g.spacing * R_KM * ROUTE)
        W = ctx.world or {}
        nav = np.asarray(W.get("river_nav", np.zeros(n))).astype(int)
        rv = land[a] & land[b] & (nav[a] >= 1) & (nav[b] >= 1) & canoes[a]
        rf = np.where(elev[b] < elev[a], M["down"], M["up"])

        def edges(fc):  # (open, factor per km, mode) per edge from the cells' factors
            fa, fb = fc[a], fc[b]
            fac = 0.5 * (fa + fb)
            use = rv & (rf < fac)
            return (fa > 0) & (fb > 0), np.where(use, rf, fac), np.where(use, 1, np.where(sea[a] | sea[b], 2, 0))
        open_, fac, mode = edges(fcell)
        fetch_e = None
        if fetch:  # (PW-1511 B: herders fetch grain with their own animals, Khazanov: nomads drove their own herds to frontier markets;
            # pack-animal cost on the land a herding culture carries for, and one cell beyond it, the farmers' edge, tech or not)
            herder = attr(lambda r: r.get("herder", False))
            near = herder.copy()
            near[srcs[herder[nbr_idx]]] = True
            f2 = np.where(near & land, np.minimum(f_land, M["pack"] * hm), f_land)
            fetch_e = edges(np.where(land, f2, np.where(sea, f_sea, -1.0)))
        oa, ob = own[a], own[b]
        bord = (oa >= 0) & (ob >= 0) & (oa != ob)
        tol = tab(lambda r: r["tol"], TOL_MID).astype(float)[np.maximum(ob, 0)]
        toll = np.clip(TOLL * sc.get("toll", 1.0) * (1.0 - tol) / (1.0 - TOL_MID), 0.0, TOLL_MAX)
        self.quarter_edges = 0
        if quarters:  # (step 3, PW-1504: a merchant quarter of the giver's people in the taker's town last era lifts that border's toll,
            # Curtin's trade diaspora; design1.md step 2: "A merchant quarter of the giver's people in the taker's town removes it")
            qk = np.array([h * 1_000_003 + m for h, m in quarters], np.int64)
            lift = bord & np.isin(ob * 1_000_003 + oa, qk)
            toll = np.where(lift, 0.0, toll)
            self.quarter_edges = int(lift.sum())
        self.pol_cell, wars, self.rules = _polity_state(pol, era, n, C)
        if wars:
            pa, pb = self.pol_cell[a], self.pol_cell[b]
            key = pa * 1_000_003 + pb
            wk = np.array([x * 1_000_003 + y for x, y in wars], np.int64)
            closed = bord & (pa >= 0) & (pb >= 0) & np.isin(key, wk)
            open_ &= ~closed
            if fetch_e is not None:
                fetch_e = (fetch_e[0] & ~closed, *fetch_e[1:])
            self.war_edges = int(closed.sum())
        else:
            self.war_edges = 0
        fly = np.zeros(n, bool)
        fl = np.array([info[c]["flies"] for c in cu.tolist()], bool) if len(cu) else np.zeros(0, bool)
        fly[cell[fl]] = True
        self.fly = fly
        self.e = {"a": a, "b": b, "hop": hop, "open": open_, "fac": fac, "mode": mode, "bord": bord, "toll": toll,
                  "fly": fly[a] | fly[b], "fetch": fetch_e}
        self.costs: dict = {}

    def cost(self, cl: str, fetch: bool = False):
        """(edge cost, edge mode, edge km) for a value class (cached); fetch: with the herders' own animals (PW-1511 B)."""
        if (cl, fetch) not in self.costs:
            e, L = self.e, self.L[cl]
            op, fac, mode = e["fetch"] if fetch and e["fetch"] is not None else (e["open"], e["fac"], e["mode"])
            c = np.where(op, e["hop"] * fac, -1.0)
            mode = mode.copy()
            if cl == "precious":  # (flyers carry light goods over anything)
                air = e["hop"] * AIR
                use = e["fly"] & ((c < 0) | (air < c))
                c = np.where(use, air, c)
                mode = np.where(use, 3, mode)
            c = np.where((c >= 0) & e["bord"], c - L * np.log1p(-e["toll"]), c)
            self.costs[(cl, fetch)] = (np.ascontiguousarray(c), mode.astype(np.int64), np.full(len(c), e["hop"]))
        return self.costs[(cl, fetch)]

    def walk(self, good: str, live: np.ndarray | None = None):
        """The supply of a good over the map from its surplus cells (only the `live` ones, if given): (supply 0..1 per cell, origin cell,
        km, km per mode, borders crossed, source culture per cell, carrying cost-km, source surplus per cell, the edge each cell was reached by,
        each edge's mode)."""
        P = self.P
        cl = FALL_CLASS.get(good, TR.GOODS[good][1])
        L = self.L[cl]
        sur = P["surplus"][good]
        cell, cu = P["cell"], P["culture"]
        n = self.ctx.g.n
        S = np.zeros(n)
        sc = np.full(n, -1, np.int64)
        order = np.argsort(sur, kind="stable")
        S[cell[order]] = sur[order]
        sc[cell[order]] = cu[order]
        src = np.flatnonzero((S >= TR.SHOW_MIN) & (True if live is None else live))
        c, mode, km = self.cost(cl, self.fetch and good in FETCH_GOODS)
        g = self.ctx.g
        d, org, kmv, mkm, nb, pe = _walk(src.astype(np.int64), -L * np.log(S[src]), g.nbr_off.astype(np.int64), g.nbr_idx.astype(np.int64), c, km, mode,
                                     self.e["bord"].astype(np.int32), L * math.log(1.0 / FLOOR))
        sup = np.where(np.isfinite(d), np.exp(-np.minimum(d, 700.0) / L), 0.0)
        carry = np.where(org >= 0, d + L * np.log(np.maximum(S[np.maximum(org, 0)], 1e-300)), 0.0)  # (the carrying cost alone, cost-km)
        return sup, org, kmv, mkm, nb, sc, carry, S, pe, mode


def kind_of(fr: _Frame, giver: int, taker: int, borders: float) -> str:
    """The kind of exchange from the two sides (R§1-R§5; a label, it does not change the physics): tribute where the taker takes tribute
    (dragons, tribute giants) or rules the giver's polity; gifts between forager bands (hxaro, R§1); merchants where a third culture lies
    between and either side knows trade and a carrier (caravans or ships, R§4-5: merchant diasporas); a market where either side has towns
    and knows markets, or is a mining kind's hold (R§5); else barter, the default down-the-line exchange."""
    I, R = fr.info, fr.rows
    ti, gi = I.get(taker, {}), I.get(giver, {})
    if ti.get("mode") == "tribute" or giver in fr.rules.get(taker, ()):
        return "tribute"
    wt, wg = (R.get(taker) or {}).get("ways") or {}, (R.get(giver) or {}).get("ways") or {}
    band = lambda w: bool(w) and max(("farm", "herd", "forage"), key=lambda k: w.get(k, 0)) == "forage"  # noqa: E731
    if band(wt) and band(wg):
        return "gift"
    if borders >= 1.5 and any("trade" in r.get("know", ()) and _knows(r.get("know", ()), CARRIERS) for r in (ti, gi)):
        return "merchant"
    if ti.get("miner") or gi.get("miner") or any(w.get("urban", 0) >= TOWN_MIN and "markets" in r.get("know", ()) for w, r in ((wt, ti), (wg, gi))):
        return "market"
    return "barter"


def _sum_by(keys: np.ndarray, vals: np.ndarray) -> dict:
    """{key: sum of vals} over the positive sums."""
    if not len(keys):
        return {}
    u, inv = np.unique(keys, return_inverse=True)
    s = np.bincount(inv, weights=vals, minlength=len(u))
    return {int(a): float(b) for a, b in zip(u.tolist(), s.tolist()) if b > 0}


def flows_at(ctx, i: int, pol: dict | None = None, att: dict | None = None, scale: dict | None = None, quarters: set | None = None,
             fetch: bool = False, routes: bool = True, last_routes: set | None = None) -> dict | None:
    """Frame i's exchange: {"flows": [[giver, taker, good, share of the taker's people, people supplied, km, cost-km, mode, kind, via]],
    "home": {culture: {good: share met from its own land elsewhere}}, "unmet": {culture: {good: share}}, "war_edges", "flyer_foods"}; with
    routes (step 3, trade_routes.py) also "routes", "hubs", "quarters" and "volume". quarters: last era's merchant quarters (host, merchant
    culture), whose borders charge no toll; fetch: herders fetch grain with their own animals (PW-1511 B); last_routes: last era's route
    stretches (a * n + b), which stay routes down to trade_routes.ROUTE_HOLD of the bar (PW-1514)."""
    if TR.pairs_at(ctx, i) is None:
        return None
    fr = _Frame(ctx, i, pol, att, scale, quarters=quarters, fetch=fetch)
    from . import trade_routes as RT
    loads = RT.Loads(fr) if routes else None
    P = fr.P
    cell, cu, w = P["cell"], P["culture"], P["w"]
    wsum = P["wsum"]
    nc = len(ctx.cultures()["cultures"])
    wsum_arr = np.ones(nc)
    for c, x in wsum.items():
        wsum_arr[c] = x
    heads = TR.cells_at(ctx, i)["heads"]
    trading = np.array([fr.info[c]["mode"] == "trade" for c in cu.tolist()], bool) if len(cu) else np.zeros(0, bool)
    agg: dict = {}
    home: dict = {}
    unmet: dict = {}
    for good in TR.GOODS:
        lack = P["lack"].get(good)
        if lack is None or not (lack > 0).any():
            continue
        # the supply is shared: a source gives at most its surplus (in people's worth, like for like, as the ledger), the nearest takers
        # first (best supply first); a taker cut short by an emptied source tries the next best source in the next round
        rem = lack.copy()
        avail = None
        want = (lack > 0) & trading
        for _ in range(ROUNDS):
            p = np.flatnonzero(want & (rem > 0))
            if not len(p):
                break
            sup, org, km, mkm, nb, sc, carry, S, pe, emode = fr.walk(good, None if avail is None else avail > 1e-9 * np.maximum(avail0, 1e-12))
            if avail is None:
                avail0 = S * heads
                avail = avail0.copy()
            cp, t = cell[p], cu[p]
            o = org[cp]
            ask = np.minimum(rem[p], sup[cp]) * heads[cp]
            ok = (o >= 0) & (ask > 0)
            p, cp, t, o, ask = p[ok], cp[ok], t[ok], o[ok], ask[ok]
            if not len(p):
                break
            order = np.argsort(sup[cp] * -1.0, kind="stable")
            got = _allocate(order, o, ask, avail)
            cut = got < ask * (1 - 1e-9)
            rem[p] -= got / np.maximum(heads[cp], 1e-12)
            giver = sc[o]
            if loads is not None:
                loads.add(good, cp, got, giver, t, pe, emode)
            v = got / np.maximum(heads[cp], 1e-12) * w[p] / wsum_arr[t]
            hm = (v > 0) & (giver == t)
            for c, x in _sum_by(t[hm], v[hm]).items():
                home.setdefault(c, {})[good] = home.get(c, {}).get(good, 0.0) + x
            fl = (v > 0) & (giver >= 0) & (giver != t)
            if fl.any():
                key = giver[fl] * len(wsum_arr) + t[fl]
                u, inv = np.unique(key, return_inverse=True)
                vv = v[fl]
                cols = [vv, vv * km[cp[fl]], vv * carry[cp[fl]], *(vv * mkm[cp[fl], m] for m in range(4)), vv * nb[cp[fl]]]
                sums = [np.bincount(inv, weights=x, minlength=len(u)) for x in cols]
                for k, kk in enumerate(u.tolist()):
                    a = agg.setdefault((kk // len(wsum_arr), kk % len(wsum_arr), good), [0.0, 0.0, 0.0, np.zeros(4), 0.0])
                    a[0] += sums[0][k]
                    a[1] += sums[1][k]
                    a[2] += sums[2][k]
                    a[3] = a[3] + np.array([sums[3 + m][k] for m in range(4)])
                    a[4] += sums[7][k]
            want = np.zeros(len(rem), bool)
            want[p[cut]] = True  # (only those cut short by an emptied source look further)
        q = np.flatnonzero((lack > 0) & trading)
        for c, x in _sum_by(cu[q], rem[q] * w[q] / wsum_arr[cu[q]]).items():
            unmet.setdefault(c, {})[good] = x
    # tribute-takers: the realm takes food and its hoard from the peoples on its land (no walk: they live there)
    tcul = {c for c, r in fr.info.items() if r["mode"] == "tribute"}
    if tcul:
        by_cell: dict = {}
        for k in range(len(cell)):
            by_cell.setdefault(int(cell[k]), []).append(k)
        for k in range(len(cell)):
            t = int(cu[k])
            if t not in tcul:
                continue
            for good in TRIBUTE_GOODS:
                givers = [(int(cu[q]), float(P["surplus"][good][q])) for q in by_cell[int(cell[k])] if int(cu[q]) not in tcul and P["surplus"][good][q] > 0]
                tot = sum(v for _, v in givers)
                if tot <= 0:
                    continue
                share = min(1.0, tot) * w[k] / wsum[t]
                for gv, v in givers:
                    a = agg.setdefault((gv, t, good), [0.0, 0.0, 0.0, np.zeros(4), 0.0])
                    a[0] += share * v / tot
    flows = []
    for (gv, t, good), (v, kmw, cw, mk, nbw) in agg.items():
        if v < FLOW_MIN:
            continue
        mode = MODES[int(np.argmax(mk))] if mk.sum() > 0 else "local"
        kind = kind_of(fr, gv, t, nbw / v)
        via = fr.info.get(gv, {}).get("via")
        flows.append([gv, t, good, round(float(v), 4), int(round(v * fr.info.get(t, {}).get("people", 0))), int(round(kmw / v)), int(round(cw / v)),
                      mode, kind, via])
    flows.sort(key=lambda f: -f[3])
    rnd = lambda d: {str(c): {g: round(x, 4) for g, x in v.items() if x >= FLOW_MIN} for c, v in d.items()}  # noqa: E731
    out = {"flows": flows, "home": rnd(home), "unmet": rnd(unmet), "war_edges": fr.war_edges, "flyer_foods": flyer_foods(ctx, fr)}
    if loads is not None:
        out.update(loads.finish(last_routes))
        out["quarter_edges"] = fr.quarter_edges
    return out


def flyer_foods(ctx, fr: _Frame) -> list:
    """Foods a flying people carries into land where they are not grown (Daniel, D65: as birds have carried seeds). Per flying trading
    culture: the crops it knows, and the crops growing wild on its own cells (PW-1510: a flyer that forages carries the wild plants of its
    range; crops.py's crop_wild layer); for each, the land in its range and one ring beyond where another culture farms and the crop is
    neither known nor wild, and who farms there. [{"culture", "crop", "from": "known" | "wild", "cells", "to": [[culture, cells]]}]: a
    record for the culinary brief (step 4a) and the crop spread to read later (a flow of seed and food); nothing is spread here."""
    stocks = (ctx.meta.get("crops") or {}).get("stocks") or {}
    if not stocks or "crop_known" not in ctx.arr:
        return []
    P, i = fr.P, fr.i
    cell, cu = P["cell"], P["culture"]
    flyers = [c for c, r in fr.info.items() if r["flies"]]
    if not flyers:
        return []
    X = TR.cells_at(ctx, i)
    bits = np.asarray(ctx.f("crop_known", i)).astype(np.int64)
    wild = np.asarray(ctx.f("crop_wild", i)).astype(np.int64) if "crop_wild" in ctx.arr else np.zeros(ctx.g.n, np.int64)
    g = ctx.g
    srcs = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
    farmed = np.zeros(g.n)
    np.maximum.at(farmed, cell, np.where(np.array([fr.info[c]["flies"] for c in cu.tolist()], bool), 0.0, X["farm"][cell]))
    farmer_c = np.array([not r["flies"] and r["mode"] == "trade" and ((fr.rows.get(int(k)) or {}).get("ways") or {}).get("farm", 0) > 0
                         for k, r in ((k, fr.info[k]) for k in cu.tolist())], bool) if len(cu) else np.zeros(0, bool)
    out = []
    for c in flyers:
        mine = np.zeros(g.n, bool)
        mine[cell[cu == c]] = True
        wild_here = int(np.bitwise_or.reduce(wild[mine])) if mine.any() else 0
        crops = []
        for s, st in stocks.items():
            if not st.get("enabled", True):
                continue
            if f"crop_{s}" in fr.info[c]["know"]:
                crops.append((s, "known"))
            elif (wild_here >> int(st["bit"])) & 1:
                crops.append((s, "wild"))
        if not crops:
            continue
        reach = mine.copy()
        reach[srcs[mine[g.nbr_idx]]] = True
        for s, how in crops:
            b = int(stocks[s]["bit"])
            tgt = np.flatnonzero(reach & X["land"] & (((bits >> b) & 1) == 0) & (((wild >> b) & 1) == 0) & (farmed > 0))
            if not len(tgt):
                continue
            hit = np.isin(cell, tgt) & farmer_c  # (the farming trading cultures there: who could take the crop up)
            who, cnt = np.unique(cu[hit], return_counts=True)
            top = sorted(zip(who.tolist(), cnt.tolist()), key=lambda x: -x[1])[:5]
            out.append({"culture": int(c), "crop": s, "from": how, "cells": tgt.tolist(), "to": [[int(a), int(b)] for a, b in top]})
    return out


def derive(run_dir, ctx=None, pol: dict | None = None, att: dict | None = None, scale: dict | None = None, frames=None,
           quarters: bool | None = None, fetch: bool | None = None, routes: bool = True) -> dict:
    """The run's exchange over the land-use window. pol: the polities doc (server.polities_doc), att: the attitudes read-out (gods doc
    "attitudes"); without them no border is closed by war and every culture has the median tolerance. scale: a nudge for the judge
    ({"L", "modes", "toll"} multipliers). routes: trace the routes and trading towns (step 3); quarters (default QUARTERS): last frame's
    merchant quarters lift their border's toll; fetch (default FETCH): herders fetch grain with their own animals (PW-1511 B)."""
    from .brief import Ctx
    t0 = time.time()
    ctx = ctx or Ctx(run_dir)
    eq = ctx.meta.get("eraq")
    out = []
    quarters = QUARTERS if quarters is None else quarters
    fetch = FETCH if fetch is None else fetch
    last_q: set = set()
    last_r: set = set()
    if eq and ctx.goods is not None and ctx.cultures() is not None and ctx.world is not None:
        for i, ago in zip(eq["frames"], eq["ago_kyr"]):  # (oldest first: a frame reads the merchant quarters of the one before)
            if frames is not None and i not in frames:
                continue
            f = flows_at(ctx, i, pol, att, scale, quarters=last_q if quarters and routes else None, fetch=fetch, routes=routes,
                         last_routes=last_r)
            if f is not None:
                out.append({"frame": i, "ago_kyr": round(abs(float(ago)), 3), **f})
                last_q = {(int(h), int(m)) for h, m in f.get("quarters") or []}
                last_r = {int(a) * ctx.g.n + int(b) for a, b, *_ in f.get("routes") or []}
            for k in ("trade_cells", "trade_ledger", "trade_pairs"):
                ctx._frame_cache.pop((k, i), None)
    C = (ctx.cultures() or {}).get("cultures") or []
    return {"format": FORMAT, "version": VERSION, "ledger_version": TR.VERSION, "run": Path(ctx.dir).name,
            "cultures": [{k: x.get(k) for k in ("name", "people")} for x in C],
            "goods": {g: {"label": a, "class": b, "falls_as": FALL_CLASS.get(g, b)} for g, (a, b, _) in TR.GOODS.items()},
            "frames": out, "seconds": round(time.time() - t0, 1), "had_polities": pol is not None, "had_attitudes": att is not None,
            "constants": {"modes_per_km": {"porter": PORTER, "pack": PACK, "cart_road": round(CART, 3), "hill_x": round(HILL, 2),
                                           "river_down": round(RIVER_DOWN, 3), "river_up": round(RIVER_UP, 3), "sea": round(SEA, 3),
                                           "canoe_coast": round(CANOE_COAST, 3), "air": AIR},
                          "fall_km": FALL_KM, "toll": TOLL, "tol_mid": TOL_MID, "toll_max": TOLL_MAX, "floor": FLOOR, "flow_min": FLOW_MIN,
                          "town_min": TOWN_MIN, "tribute_goods": list(TRIBUTE_GOODS), "quarters": bool(quarters and routes), "fetch": bool(fetch)},
            "basis": "trade_flow.py (PW-1503, design1.md step 2): per good one least-cost walk from its surplus cells; supply = surplus x "
                     "exp(-cost / L) by value class; a cell takes min(its lack, the best supply reaching it); summed to cultures. Read-out only."}


# ------------------------------------------------------------------ views

def food_bought(doc: dict, c: int, ago_kyr: float) -> float:
    """The share of a culture's people fed by bought food at the frame nearest ago_kyr (grain, herd animals and dried fish from other
    cultures), for step 4d (PW-1499: the hold and forager placeholders, ladder.TRADE_CAP and BARTER_CAP, read this once trade feeds back)."""
    if not doc["frames"]:
        return 0.0
    f = min(doc["frames"], key=lambda f: abs(f["ago_kyr"] - ago_kyr))
    return float(min(1.0, sum(x[3] for x in f["flows"] if x[1] == c and x[2] in FOODS)))


def culture_view(doc: dict, c: int, C: list) -> list:
    """Per frame for culture c (or whoever held its land then): per good where it comes from and where it goes, and its partners.
    [{"ago_kyr", "as", "from": {good: [[giver, name, share, km, mode, kind, via]]}, "to": {good: [[taker, name, people, km, mode, kind]]},
    "home": {good: share}, "partners": [[culture, name, people in, people out, main kind]], "hubs": its trading towns (step 3,
    trade_routes.culture_hubs)}]"""
    nm = lambda k: doc["cultures"][k]["name"] if 0 <= k < len(doc["cultures"]) else str(k)  # noqa: E731
    rows = []
    for f in doc["frames"]:
        h = TR._at(C, c, f["ago_kyr"])
        fin = [x for x in f["flows"] if x[1] == h]
        fout = [x for x in f["flows"] if x[0] == h]
        if not fin and not fout and str(h) not in f["home"]:
            continue
        frm: dict = {}
        for x in fin:
            frm.setdefault(x[2], []).append([x[0], nm(x[0]), x[3], x[5], x[7], x[8], x[9]])
        to: dict = {}
        for x in sorted(fout, key=lambda x: -x[4]):
            to.setdefault(x[2], []).append([x[1], nm(x[1]), x[4], x[5], x[7], x[8]])
        part: dict = {}
        for x in fin:
            p = part.setdefault(x[0], [0, 0, {}])
            p[0] += x[4]
            p[2][x[8]] = p[2].get(x[8], 0) + x[4]
        for x in fout:
            p = part.setdefault(x[1], [0, 0, {}])
            p[1] += x[4]
            p[2][x[8]] = p[2].get(x[8], 0) + x[4]
        partners = sorted(([k, nm(k), a, b, max(kd, key=kd.get) if kd else None] for k, (a, b, kd) in part.items()), key=lambda r: -(r[2] + r[3]))
        from .trade_routes import culture_hubs
        rows.append({"ago_kyr": f["ago_kyr"], "as": h, "from": {g: v[:4] for g, v in frm.items()}, "to": {g: v[:4] for g, v in to.items()},
                     "home": f["home"].get(str(h), {}), "unmet": f["unmet"].get(str(h), {}), "partners": partners[:8], "hubs": culture_hubs(f, h)[:8]})
    return rows
