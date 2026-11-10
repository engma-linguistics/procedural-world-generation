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
GROUPS = ("food", "salt", "metal", "precious", "raw", "craft")  # (craft: the middling made goods and horses, PW-1522)
GROUP_OF = {"grain": 0, "livestock": 0, "dried_fish": 0, "oil_wine": 0, "sugar": 0, "salt": 1, "copper": 2, "tin": 2, "iron": 2, "mithril": 2,
            "spices": 3, "gold": 3, "gems": 3, "ornaments": 3, "timber": 4, "firewood": 4, "stone": 4, "toolstone": 4, "furs": 4, "seal_oil": 4,
            "silver": 3, "incense": 3, "silk": 3, "dyes": 3, "arms": 3, "cloth": 5, "glass": 5, "porcelain": 5, "horses": 5}
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
LONG_KM = 500.0  # long-haul (PW-1515, Daniel 11-08: the dense web is real local exchange; long-distance trade was a branching network of
# high-value goods): the precious goods (those that fall off as precious, trade_flow.FALL_CLASS: spices, gold, gems, ornaments, mithril, tin)
# and anything carried at least this far (path km, from its source to its taker). JUDGEMENT within sourced bounds: overland grain went
# 100-200 km at most (review1.md section 6; Cato's mill, Adams 2007), and fine goods and tin 1,000 km and more (Kanesh ~1,200 km); on the
# judge runs 90% of grain's cross-culture deliveries go under 8 stretches, ~480 km at L7 (step3b.md). So 500 km keeps nearly all overland
# grain local and counts grain shipped far by sea or river as long-haul
LOCAL_SHARE = 0.01  # the local layer's bar, as ROUTE_SHARE (of one good's local carried volume, the world over). JUDGEMENT (step3d.md):
# local hauls are short and many, each crossing 1-8 stretches, so no stretch carries much of the world's local volume: at 5% the local
# layer kept 11-92 stretches an era on 3e0eb4 and 0141d1 (6, 3 and 0 kyr ago), at 1% 595-901, about the dense web of lane 218's routes
# (327-536 stretches an era), which Daniel ruled real local exchange (11-08)
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


def long_good(good: str) -> bool:
    """A good that is long-haul wherever it goes: one that falls off as a precious good (trade_flow.FALL_CLASS, trade.GOODS)."""
    from .trade import GOODS
    from .trade_flow import FALL_CLASS
    return FALL_CLASS.get(good, GOODS[good][1]) == "precious"


def seek_dummy(n: int, ne: int) -> tuple:
    """trade_flow._seek's tracing arrays when no routes are traced."""
    tdict = Dict.empty(key_type=types.int64, value_type=types.float64)
    return 0, np.zeros((len(GROUPS), n)), np.full(n, -1, np.int64), tdict, np.zeros(ne), np.zeros(ne), np.zeros(ne)


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
        self.esrc, self.ukey, self.uid = fr.esrc, fr.ukey, fr.uid  # (each directed edge's stretch: both ways as one; _Frame.stretches)
        self.through = np.zeros((len(GROUPS), n))
        self.towns = towns_at(fr.ctx, fr.era)
        self.tcells = np.array(sorted(self.towns), np.int64)
        self.tix = np.full(n, -1, np.int64)
        self.tix[self.tcells] = np.arange(len(self.tcells))
        self.tdict = Dict.empty(key_type=types.int64, value_type=types.float64)
        self.tgood = np.zeros((len(self.tcells), len(GROUP_OF)))  # (per town and good: the volume passing)
        self.tot = np.zeros(len(GROUPS))
        self.tot_good: dict = {}
        self.den: dict = {}  # (per good: the volume carried between cultures, deliveries that cross at least one stretch)
        self.den_long: dict = {}  # (... of it long-haul: a precious good, or carried LONG_KM or more)
        self.xtot = np.zeros(len(GROUPS))
        self.parts: dict = {}  # (per good: [(stretch ids, edge modes, load)] between cultures, traced as they come)
        self.all_load = np.zeros(len(self.ukey))  # (every carried delivery's load per stretch, inside a culture too: the traffic, PW-1515)
        self.carried = 0.0  # (the frame's carried volume, all goods: deliveries that cross at least one stretch)
        ne = len(self.esrc)
        self._eload = np.zeros(ne)
        self._touched = np.zeros(ne, np.int64)

    def add(self, good: str, cells: np.ndarray, amt: np.ndarray, giv: np.ndarray, taker: np.ndarray, pe: np.ndarray, emode: np.ndarray,
            tally: bool = True):
        """Deliveries of a good this round: taker cells (where the goods arrive), amounts (people's worth), giver and taker cultures; the
        walk's edges (pe: the edge each cell was reached by, -1 at a source) and their modes. Each is traced back along its way now (the
        walk's edges change from round to round). tally: count it towards the towns it passes (False: traffic only)."""
        ok = amt > 0
        if not ok.any():
            return
        cells, amt, giv, taker = cells[ok].astype(np.int64), amt[ok].astype(float), giv[ok].astype(np.int64), taker[ok].astype(np.int64)
        gi = GROUP_OF[good]
        if tally:
            before = self.through[gi, self.tcells].copy() if len(self.tcells) else None
            _tally(cells, amt, giv, gi, pe, self.esrc, self.through, self.tix, self.tdict)
            if before is not None:
                self.tgood[:, list(GROUP_OF).index(good)] += self.through[gi, self.tcells] - before
            self.tot[gi] += float(amt.sum())
            self.tot_good[good] = self.tot_good.get(good, 0.0) + float(amt.sum())
        carried = pe[cells] >= 0
        if not carried.any():
            if tally:
                fx = (giv >= 0) & (giv != taker)
                self.xtot[gi] += float(amt[fx].sum())
            return
        self.carried += float(amt[carried].sum())
        m = _path_load(cells[carried], amt[carried], pe, self.esrc, self._eload, self._touched)
        es = self._touched[:m].copy()
        np.add.at(self.all_load, self.uid[es], self._eload[es])
        self._eload[es] = 0.0
        if not tally:
            return
        fx = (giv >= 0) & (giv != taker)
        self.xtot[gi] += float(amt[fx].sum())
        sel = fx & carried
        if sel.any():
            self.den[good] = self.den.get(good, 0.0) + float(amt[sel].sum())
            if long_good(good):
                self.den_long[good] = self.den_long.get(good, 0.0) + float(amt[sel].sum())
            m = _path_load(cells[sel], amt[sel], pe, self.esrc, self._eload, self._touched)
            es = self._touched[:m].copy()
            x = self._eload[es].copy()
            self.parts.setdefault(good, []).append((self.uid[es], emode[es].astype(np.int64), x, x if long_good(good) else np.zeros(len(x))))
            self._eload[es] = 0.0

    def seek_arrays(self, good: str) -> tuple:
        """The arrays trade_flow._seek traces a good's deliveries into as they happen: (group, through, town index per cell, town tallies,
        and per directed edge the load, the load between cultures, its long-haul part); seek_done() books them."""
        gi = GROUP_OF[good]
        self._before = self.through[gi, self.tcells].copy() if len(self.tcells) else None
        ne = len(self.esrc)
        return gi, self.through, self.tix, self.tdict, np.zeros(ne), np.zeros(ne), np.zeros(ne)

    def seek_done(self, good: str, tr: tuple, got: np.ndarray, cross: np.ndarray, carried: np.ndarray, lng: np.ndarray, emode: np.ndarray):
        """Books a good's deliveries traced by _seek (got: amounts, cross: their part between cultures, carried: crossed a stretch, lng:
        long-haul)."""
        gi, eall, ex, exl = tr[0], tr[4], tr[5], tr[6]
        if self._before is not None:
            self.tgood[:, list(GROUP_OF).index(good)] += self.through[gi, self.tcells] - self._before
        self.tot[gi] += float(got.sum())
        self.tot_good[good] = self.tot_good.get(good, 0.0) + float(got.sum())
        self.xtot[gi] += float(cross.sum())
        self.carried += float(got[carried].sum())
        es = np.flatnonzero(eall > 0)
        np.add.at(self.all_load, self.uid[es], eall[es])
        es = np.flatnonzero(ex > 0)
        if len(es):
            self.den[good] = self.den.get(good, 0.0) + float(cross[carried].sum())
            self.den_long[good] = self.den_long.get(good, 0.0) + float(cross[carried & lng].sum())
            self.parts.setdefault(good, []).append((self.uid[es], emode[es].astype(np.int64), ex[es], exl[es]))

    def traffic(self) -> np.ndarray:
        """Per stretch: the share of the frame's carried goods (all goods, people's worth, inside cultures too) that crosses it, both ways
        summed (PW-1515). A share, so a road's wear does not grow with the world's people from era to era."""
        return self.all_load / max(self.carried, 1e-12)

    def _layer(self, st: np.ndarray, last: set | None, share: float = ROUTE_SHARE) -> np.ndarray:
        """The route stretches of one layer from their strengths: ROUTE_SHARE or more; or ROUTE_HOLD x ROUTE_SHARE or more and a route
        (of either layer) the era before (last: the stretches as a * n + b), or continuing a route of this layer (SPAN)."""
        n = self.n
        ok = st >= share
        weak = np.flatnonzero((st >= ROUTE_HOLD * share) & ~ok)
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
        return ok

    def finish(self, last: set | None = None) -> dict:
        """{"routes": [[cell a, cell b, strength, group, mode, layers, long-haul strength, long-haul group, local strength, local group]],
        "hubs": [...], "quarters": [[host culture, merchant culture]], "volume"}: every carried delivery between two cultures adds its
        amount to each stretch on its way. Two layers (PW-1515, Daniel 11-08: the dense web is real local exchange; long-distance trade was
        a branching network of high-value goods): long-haul deliveries (precious goods, or carried LONG_KM or more) and local ones (the
        rest). In each layer a stretch's strength is the largest share of one good's carried volume between cultures in that layer (that
        frame, the world over) it carries, and its group is that good's; a stretch of strength ROUTE_SHARE or more is a route of the layer,
        and so is one of ROUTE_HOLD x ROUTE_SHARE or more that was a route the era before or continues a route of the layer (_layer). Each
        layer is measured against its own volume, so short hauls are not drowned by the long ones and the other way round. layers: 1
        long-haul, 2 local, 3 both; strength and group are the stronger layer's (0 for a layer it is not a route of); its mode the one
        carrying the biggest share of goods over it."""
        n = self.n
        nu = len(self.ukey)
        xtot = self.xtot
        S = np.zeros((2, nu))  # (strength per layer: 0 long-haul, 1 local)
        SG = np.zeros((2, nu), np.int64)
        emu = np.zeros((len(MODES), nu))
        for good, parts in self.parts.items():  # (per good, both ways of a stretch summed; the stretch keeps its strongest good per layer)
            den = self.den.get(good, 0.0)
            if den <= 0:
                continue
            dl = self.den_long.get(good, 0.0)
            u = np.concatenate([p[0] for p in parts])
            md = np.concatenate([p[1] for p in parts])
            x = np.concatenate([p[2] for p in parts])
            xl = np.minimum(np.concatenate([p[3] for p in parts]), x)
            np.add.at(emu, (md, u), x / den)
            uu, inv = np.unique(u, return_inverse=True)
            for k, (v, dd) in enumerate(((xl, dl), (x - xl, den - dl))):
                if dd <= 1e-12 * den:
                    continue
                sx = np.bincount(inv, weights=v / dd, minlength=len(uu))
                up = sx > S[k, uu]
                S[k, uu[up]] = sx[up]
                SG[k, uu[up]] = GROUP_OF[good]
        lo, lc = self._layer(S[0], last), self._layer(S[1], last, LOCAL_SHARE)
        S[0] = np.where(lo, S[0], 0.0)
        S[1] = np.where(lc, S[1], 0.0)
        ok = lo | lc
        st = S.max(0)
        sg = np.where(S[0] >= S[1], SG[0], SG[1])
        keep = np.flatnonzero(ok)
        keep = keep[np.argsort(-st[keep], kind="stable")]
        ua, ub = self.ukey[keep] // n, self.ukey[keep] % n
        md = emu[:, keep].argmax(0) if len(keep) else np.zeros(0, np.int64)
        lay = lo[keep].astype(np.int64) + 2 * lc[keep].astype(np.int64)
        r4 = lambda v: round(float(v), 4)  # noqa: E731
        routes = [[int(a), int(b), r4(s), int(g), int(m), int(y), r4(xl), int(gl), r4(xc), int(gc)] for a, b, s, g, m, y, xl, gl, xc, gc in
                  zip(ua.tolist(), ub.tolist(), st[keep].tolist(), sg[keep].tolist(), md.tolist(), lay.tolist(), S[0, keep].tolist(),
                      SG[0, keep].tolist(), S[1, keep].tolist(), SG[1, keep].tolist())]
        touch = np.zeros((len(MODES), n), bool)
        for m in range(len(MODES)):
            sel = md == m
            touch[m, ua[sel]] = True
            touch[m, ub[sel]] = True
        lh = (lay & 1) > 0
        on_long = np.zeros(n, bool)  # (a town on the long-haul network)
        on_long[ua[lh]] = True
        on_long[ub[lh]] = True
        hubs, quarters = self._hubs(np.maximum(self.tot, 1e-12), touch.any(0), touch, ua, ub, md, on_long)
        self.parts = {}
        return {"routes": routes, "hubs": hubs, "quarters": quarters, "volume": {GROUPS[k]: int(round(float(xtot[k]))) for k in range(len(GROUPS))}}

    def _hubs(self, tot, on_route, touch, ua, ub, md, on_long):
        fr = self.fr
        ctx, i = fr.ctx, fr.i
        if not len(self.tcells):
            return [], []
        from . import trade as TR
        from .trade_flow import has_pack
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
            pack = host >= 0 and has_pack(fr.info.get(host, {}).get("know", ()))
            # PW-1530 (coordinator's ruling A): a trading town needs a long-haul route through it, and merchant quarters follow it; a
            # town only the local web passes stays a market town (drawn smaller)
            trading = bool(on_long[c])
            kind = ("port" if touch[2, c] else "caravan town" if caravan_edge[c] and pack else "river port" if touch[1, c] else "market town")
            if not trading:
                kind = "market town"
            whole = float(norm[:, c].sum())
            sel = t_ix == t
            by: dict = {}
            for x, v in zip(gv[sel].tolist(), nv[sel].tolist()):
                by[x] = by.get(x, 0.0) + v
            # (merchants are a trading culture's, or a dragon realm's kobolds (D65); a kind that takes tribute sends no merchants)
            trader = lambda x: fr.info.get(x, {}).get("mode") == "trade" or bool(fr.info.get(x, {}).get("via"))  # noqa: E731
            q = sorted(((x, v / whole) for x, v in by.items() if x != host and x >= 0 and whole > 0 and trader(x)), key=lambda r: -r[1])
            qs = [[int(x), round(float(v), 3)] for x, v in q if v >= QUARTER_SHARE] if trading else []
            for x, _ in qs:
                if host >= 0:
                    quarters.append([host, x])
            tgn = {goods[k]: self.tgood[t, k] / max(self.tot_good.get(goods[k], 0.0), 1e-12) for k in range(len(goods)) if self.tgood[t, k] > 0}
            top = sorted(tgn, key=lambda k: -tgn[k])[:4]
            hubs.append({"site": s["id"], "cell": int(c), "place": s.get("place"), "people": int(round(pop)), "culture": host,
                         "culture_name": names[host]["name"] if 0 <= host < len(names) else None, "kind": kind,
                         "strength": round(float(norm[:, c].max()), 4), "goods": top,
                         "modes": [MODES[m] for m in range(len(MODES)) if touch[m, c]], "long": trading, "trading": trading,
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
    """The trading towns on culture c's land in a frame: [[place, kind, people, strength, goods, quarters, on the long-haul network]]."""
    return [[h["place"], h["kind"], h["people"], h["strength"], h["goods"], [q[1] for q in h["quarters"]], bool(h.get("long"))]
            for h in f.get("hubs") or [] if h["culture"] == c]
