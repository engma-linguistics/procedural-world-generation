"""Trade step 3 (PW-1504): the big flows become routes on the map, and the towns they pass through become trading towns.

In plain words: step 2 (trade_flow.py) moves each spare good from the land that makes it to the land that lacks it, along the cheapest
way open at the time. Here every delivery is followed back along that way, cell by cell, to where it came from, and its amount is added
to every stretch it crosses. The stretches that carry a large share of the world's trade in some kind of good (food, salt, metal, fine
goods, raw goods) are that era's trade routes. A town of the settlement ledger that such a route passes through is a trading town, and
its kind comes from what passes through it:
- a port: goods come or go by sea there (Polanyi's ports of trade, review1.md section 5; the Hanse kontors, section 4);
- a caravan town: a land route leaves it for desert or steppe, carried by pack animals (the Sahel towns and the
  Silk Road oases, section 4);
- a river port: goods come or go by river boat there;
- a market town otherwise: a central place gathering its country's goods (Christaller, Skinner; section 5).
A trading town where one foreign culture's goods carry a large share of what passes through hosts a merchant quarter of that culture
(Curtin's trade diasporas, section 5: foreign merchant communities living in host towns are the normal institution of trade between
cultures). design1.md step 2: such a quarter removes the toll at that border; step 2's walk reads last era's quarters (trade_flow.derive).

How: the walk keeps, per cell, the edge it was reached by (trade_flow._walk). Each delivery between two cultures (a taker cell's share of
a source's supply, in people's worth) is traced back to its source along those edges (_path_load), per group of goods. A route edge
carries at least ROUTE_SHARE of its group's traded volume between cultures, the world over, that frame. Deliveries inside one culture's
land count towards its towns' throughput (_tally) but draw no route. Read after the run (D63 A): nothing here changes the history.
"""

from __future__ import annotations

import numpy as np
from numba import njit, types
from numba.typed import Dict

# the groups a route is coloured by (design1.md step 3: "coloured by leading good class (food, salt, metal, precious)"), plus raw goods
GROUPS = ("food", "salt", "metal", "precious", "raw")
GROUP_OF = {"grain": 0, "livestock": 0, "dried_fish": 0, "oil_wine": 0, "sugar": 0, "salt": 1, "copper": 2, "tin": 2, "iron": 2, "mithril": 2,
            "spices": 3, "gold": 3, "gems": 3, "ornaments": 3, "timber": 4, "firewood": 4, "stone": 4, "toolstone": 4, "furs": 4, "seal_oil": 4}
ROUTE_SHARE = 0.05  # a stretch is a route when it carries this share of one good's carried volume between cultures in the world that frame
# (carried: the deliveries that cross at least one stretch; goods passed between cultures sharing a cell travel no road: 65-84% of metal).
# Per good, not per group (PW-1515): tin's road is a route though copper's volume dwarfs it (review1.md sections 3-4: Kanesh tin,
# Uluburun). JUDGEMENT: design1.md step 3 "for each flow above a share of the world's total"; no source gives the share. Per good, 2% drew
# a mesh (565-931 stretches in 54-85 pieces an era); 5% draws 267-401 in 11-20 (step3b.md)
ROUTE_HOLD = 0.5  # a stretch over this part of ROUTE_SHARE is a route too when it was one the era before, or when it continues a route
# (SPAN): one road, not broken bits, and roads that persist (path dependence: Bleakley & Lin 2012, Dalgaard et al. 2022; step3b.md).
# JUDGEMENT: the bar's half, as PW-1514 proposed
SPAN = True  # a stretch over the lower bar that joins a route is part of it (a double threshold, as in edge tracing)
QUARTER_SHARE = 0.25  # a trading town hosts a merchant quarter of a foreign culture whose goods are this share of what passes through it.
# JUDGEMENT: Curtin (via Barraclough 1985, review1.md section 5) gives the institution, not a share
KINDS = ("port", "caravan town", "river port", "market town")
ARID = (3, 4, 5, 6)  # Koppen BWh, BWk, BSh, BSk (climate.KOPPEN): hot and cold desert, hot and cold steppe
MODES = ("land", "river", "sea", "air")


@njit(cache=True)
def _tally(cells, amt, giv, grp, pe, esrc, through, tix, tdict):
    """Follows each delivery (taker cell, amount, giver culture) back to its source along the walk's edges (pe: the edge each cell was
    reached by, -1 at a source), adding its amount to every cell passed (through[grp]) and, at a town (tix >= 0), to its tally per
    (town, group, giver) (tdict)."""
    for k in range(cells.shape[0]):
        j = cells[k]
        x = amt[k]
        gv = giv[k]
        while True:
            through[grp, j] += x
            t = tix[j]
            if t >= 0 and gv >= 0:
                key = (t * 8 + grp) * 1_000_003 + gv
                tdict[key] = tdict.get(key, 0.0) + x
            e = pe[j]
            if e < 0:
                break
            j = esrc[e]


@njit(cache=True)
def _path_load(cells, amt, pe, esrc, eload, touched):
    """Adds each delivery's amount to every edge on its way back to its source (eload, per directed edge); returns the number of edges
    touched (their ids in touched[:count], each once)."""
    m = 0
    for k in range(cells.shape[0]):
        j = cells[k]
        x = amt[k]
        while pe[j] >= 0:
            e = pe[j]
            if eload[e] == 0.0:
                touched[m] = e
                m += 1
            eload[e] += x
            j = esrc[e]
    return m


def towns_at(ctx, era: float) -> dict:
    """{cell: (site, people)}: the biggest settlement-ledger town or city per cell at the era (the ledger's own town size; trade._urban's
    list of sites that ever reach a town's size)."""
    from .brief import _pop_at
    doc = getattr(ctx, "_settle", None)
    if doc is None or not hasattr(ctx, "_trade_towns"):
        return {}
    town = doc["tiers"]["town_min_by_stage"][-1]
    out: dict = {}
    for s in ctx._trade_towns:
        t = town
        for a, tm, _ in s.get("bands") or []:
            if a >= era - 1e-6:
                t = tm
        p = _pop_at(s, era)
        if p >= t and p > out.get(s["cell"], (None, 0.0))[1]:
            out[s["cell"]] = (s, p)
    return out


class Loads:
    """One frame's deliveries, filled by trade_flow.flows_at after each round of each good's allocation; finish() makes the routes."""

    def __init__(self, fr):
        self.fr = fr
        g = fr.ctx.g
        self.n = n = g.n
        self.esrc = np.repeat(np.arange(n), np.diff(g.nbr_off)).astype(np.int64)
        lo, hi = np.minimum(self.esrc, g.nbr_idx), np.maximum(self.esrc, g.nbr_idx)
        self.ukey, self.uid = np.unique(lo.astype(np.int64) * n + hi, return_inverse=True)  # (each directed edge's stretch: both ways as one)
        self.through = np.zeros((len(GROUPS), n))
        self.towns = towns_at(fr.ctx, fr.era)
        self.tcells = np.array(sorted(self.towns), np.int64)
        self.tix = np.full(n, -1, np.int64)
        self.tix[self.tcells] = np.arange(len(self.tcells))
        self.tdict = Dict.empty(key_type=types.int64, value_type=types.float64)
        self.tgood = np.zeros((len(self.tcells), len(GROUP_OF)))  # (per town and good: the volume passing)
        self.tot = np.zeros(len(GROUPS))
        self.tot_good: dict = {}
        self.batches: list = []

    def add(self, good: str, cells: np.ndarray, amt: np.ndarray, giv: np.ndarray, taker: np.ndarray, pe: np.ndarray, emode: np.ndarray):
        """Deliveries of a good this round: taker cells, amounts (people's worth), giver and taker cultures; the walk's edges and modes."""
        ok = amt > 0
        if not ok.any():
            return
        cells, amt, giv, taker = cells[ok].astype(np.int64), amt[ok].astype(float), giv[ok].astype(np.int64), taker[ok].astype(np.int64)
        gi = GROUP_OF[good]
        before = self.through[gi, self.tcells].copy() if len(self.tcells) else None
        _tally(cells, amt, giv, gi, pe, self.esrc, self.through, self.tix, self.tdict)
        if before is not None:
            self.tgood[:, list(GROUP_OF).index(good)] += self.through[gi, self.tcells] - before
        self.tot[gi] += float(amt.sum())
        self.tot_good[good] = self.tot_good.get(good, 0.0) + float(amt.sum())
        self.batches.append((good, cells, amt, giv, taker, pe, emode))

    def finish(self, last: set | None = None) -> dict:
        """{"routes": [[cell a, cell b, strength, group, mode]], "hubs": [...], "quarters": [[host culture, merchant culture]], "volume"}:
        every carried delivery between two cultures adds its amount to each stretch on its way. A stretch's strength is the largest share
        of one good's carried volume between cultures (that frame, the world over) it carries; a stretch of strength ROUTE_SHARE or more
        is a route, and so is one of ROUTE_HOLD x ROUTE_SHARE or more that was a route the era before (last: the stretches as a * n + b).
        Its group is that good's; its mode the one carrying the biggest share of goods over it."""
        n = self.n
        ne, nu = len(self.esrc), len(self.ukey)
        xtot = np.zeros(len(GROUPS))
        den: dict = {}
        for (good, cells, amt, giv, taker, pe, emode) in self.batches:
            fx = (giv >= 0) & (giv != taker)
            xtot[GROUP_OF[good]] += float(amt[fx].sum())
            den[good] = den.get(good, 0.0) + float(amt[fx & (pe[cells] >= 0)].sum())  # (carried: the taker is not the source cell itself)
        eload = np.zeros(ne)
        touched = np.zeros(ne, np.int64)
        st = np.zeros(nu)
        sg = np.zeros(nu, np.int64)
        emu = np.zeros((len(MODES), nu))
        per: dict = {}
        for (good, cells, amt, giv, taker, pe, emode) in self.batches:
            fx = (giv >= 0) & (giv != taker)
            if not fx.any() or den.get(good, 0.0) <= 0:
                continue
            m = _path_load(cells[fx], amt[fx], pe, self.esrc, eload, touched)
            es = touched[:m]
            x = eload[es] / den[good]
            per.setdefault(good, []).append((self.uid[es], x))
            np.add.at(emu, (emode[es], self.uid[es]), x)
            eload[es] = 0.0
        for good, parts in per.items():  # (per good, both ways of a stretch summed; the stretch keeps its strongest good)
            u = np.concatenate([p[0] for p in parts])
            x = np.concatenate([p[1] for p in parts])
            uu, inv = np.unique(u, return_inverse=True)
            sx = np.bincount(inv, weights=x, minlength=len(uu))
            up = sx > st[uu]
            st[uu[up]] = sx[up]
            sg[uu[up]] = GROUP_OF[good]
        ok = st >= ROUTE_SHARE
        weak = np.flatnonzero((st >= ROUTE_HOLD * ROUTE_SHARE) & ~ok)
        if last and len(weak):  # (last era's routes hold down to the lower bar)
            held = np.isin(self.ukey[weak], np.fromiter(last, np.int64, len(last)))
            ok[weak[held]] = True
            weak = weak[~held]
        if SPAN and len(weak):  # (a route runs on through stretches over the lower bar that continue it: one road, not broken bits)
            on = np.zeros(n, bool)
            ks = self.ukey[ok]
            on[ks // n] = True
            on[ks % n] = True
            wa, wb = self.ukey[weak] // n, self.ukey[weak] % n
            while len(weak):
                j = on[wa] | on[wb]
                if not j.any():
                    break
                ok[weak[j]] = True
                on[wa[j]] = True
                on[wb[j]] = True
                weak, wa, wb = weak[~j], wa[~j], wb[~j]
        keep = np.flatnonzero(ok)
        keep = keep[np.argsort(-st[keep], kind="stable")]
        ua, ub = self.ukey[keep] // n, self.ukey[keep] % n
        md = emu[:, keep].argmax(0) if len(keep) else np.zeros(0, np.int64)
        routes = [[int(a), int(b), round(float(s), 4), int(g), int(m)] for a, b, s, g, m in
                  zip(ua.tolist(), ub.tolist(), st[keep].tolist(), sg[keep].tolist(), md.tolist())]
        touch = np.zeros((len(MODES), n), bool)
        for m in range(len(MODES)):
            sel = md == m
            touch[m, ua[sel]] = True
            touch[m, ub[sel]] = True
        hubs, quarters = self._hubs(np.maximum(self.tot, 1e-12), touch.any(0), touch, ua, ub, md)
        self.batches = []
        return {"routes": routes, "hubs": hubs, "quarters": quarters, "volume": {GROUPS[k]: int(round(float(xtot[k]))) for k in range(len(GROUPS))}}

    def _hubs(self, tot, on_route, touch, ua, ub, md):
        fr = self.fr
        ctx, i = fr.ctx, fr.i
        if not len(self.tcells):
            return [], []
        from . import trade as TR
        X = TR.cells_at(ctx, i)
        clim = np.asarray(ctx.f("climate", i)).astype(int) if "climate" in ctx.arr else np.full(self.n, -1)
        arid = np.isin(clim, ARID) & X["land"]
        # a land route stretch from the town's cell into desert or steppe: the caravan's way. Farmed or not: the oases that fed the Saharan
        # and Silk Road caravans grew dates and grain (review1.md section 4), and the Sahel towns farmed (PW-1515: the old rule asked for a
        # farmed town cell beside an unfarmed dry one, and no town on the judge runs stood so)
        land_e = md == 0
        caravan_edge = np.zeros(self.n, bool)
        for x, y in ((ua, ub), (ub, ua)):
            caravan_edge[x[land_e & arid[y]]] = True
        norm = self.through / tot[:, None]
        hub_cells = [c for c in self.tcells.tolist() if on_route[c]]
        goods = list(GROUP_OF)
        # tallies per (town, giver): normalised over groups
        keys = np.array(list(self.tdict.keys()), np.int64) if len(self.tdict) else np.zeros(0, np.int64)
        vals = np.array(list(self.tdict.values()), float) if len(self.tdict) else np.zeros(0)
        gv = keys % 1_000_003
        tg = keys // 1_000_003
        t_ix, g_ix = tg // 8, tg % 8
        nv = vals / tot[g_ix] if len(vals) else vals
        hubs, quarters = [], []
        names = ctx.cultures()["cultures"]
        for c in hub_cells:
            t = int(self.tix[c])
            s, pop = self.towns[c]
            host = int(fr.own[c])
            pack = host >= 0 and "pack_animals" in fr.info.get(host, {}).get("know", ())
            kind = ("port" if touch[2, c] else "caravan town" if caravan_edge[c] and pack else "river port" if touch[1, c] else "market town")
            whole = float(norm[:, c].sum())
            sel = t_ix == t
            by: dict = {}
            for x, v in zip(gv[sel].tolist(), nv[sel].tolist()):
                by[x] = by.get(x, 0.0) + v
            # (merchants are a trading culture's, or a dragon realm's kobolds (D65); a kind that takes tribute sends no merchants)
            trader = lambda x: fr.info.get(x, {}).get("mode") == "trade" or bool(fr.info.get(x, {}).get("via"))  # noqa: E731
            q = sorted(((x, v / whole) for x, v in by.items() if x != host and x >= 0 and whole > 0 and trader(x)), key=lambda r: -r[1])
            qs = [[int(x), round(float(v), 3)] for x, v in q if v >= QUARTER_SHARE]
            for x, _ in qs:
                if host >= 0:
                    quarters.append([host, x])
            tgn = {goods[k]: self.tgood[t, k] / max(self.tot_good.get(goods[k], 0.0), 1e-12) for k in range(len(goods)) if self.tgood[t, k] > 0}
            top = sorted(tgn, key=lambda k: -tgn[k])[:4]
            hubs.append({"site": s["id"], "cell": int(c), "place": s.get("place"), "people": int(round(pop)), "culture": host,
                         "culture_name": names[host]["name"] if 0 <= host < len(names) else None, "kind": kind,
                         "strength": round(float(norm[:, c].max()), 4), "goods": top,
                         "modes": [MODES[m] for m in range(len(MODES)) if touch[m, c]],
                         "quarters": [[x, (names[x]["name"] if 0 <= x < len(names) else str(x)) + (f" ({fr.info[x]['via']})" if fr.info.get(x, {}).get("via") else ""), v]
                                      for x, v in qs]})
        hubs.sort(key=lambda h: -h["strength"])
        return hubs, quarters


def frame_view(doc: dict, ago_kyr: float) -> dict:
    """The routes and trading towns of the frame nearest ago_kyr (GET /api/trade?routes=1&ago=), or an empty view outside the window."""
    fs = [f for f in doc.get("frames") or [] if "routes" in f]
    if not fs:
        return {"ago_kyr": None, "routes": [], "hubs": [], "groups": list(GROUPS), "modes": list(MODES)}
    f = min(fs, key=lambda f: abs(f["ago_kyr"] - ago_kyr))
    if abs(f["ago_kyr"] - ago_kyr) > 0.25 + 1e-6:
        return {"ago_kyr": None, "routes": [], "hubs": [], "groups": list(GROUPS), "modes": list(MODES), "window": [fs[0]["ago_kyr"], fs[-1]["ago_kyr"]]}
    return {"ago_kyr": f["ago_kyr"], "routes": f["routes"], "hubs": f["hubs"], "groups": list(GROUPS), "modes": list(MODES),
            "volume": f.get("volume"), "route_share": ROUTE_SHARE, "quarter_share": QUARTER_SHARE}


def culture_hubs(f: dict, c: int) -> list:
    """The trading towns on culture c's land in a frame: [[place, kind, people, strength, goods, quarters]]."""
    return [[h["place"], h["kind"], h["people"], h["strength"], h["goods"], [q[1] for q in h["quarters"]]] for h in f.get("hubs") or []
            if h["culture"] == c]
