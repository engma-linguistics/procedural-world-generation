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
- At sea and on rivers a km also costs a share of the cargo's value (HAND_KM per class, lanes 225 and 226, step4b.md and step4c.md): the
  hands, time and risk of a water haul, which on land are in FALL_KM and the border tolls, while ORBIS's per-km water cost is freight alone.
  RIVER_COURSE (off): a river boat following only its own river's course (the world's downstream links; lane 226).
- Herd animals and horses walk (DROVE_GOODS, lane 226): a drove's cost on land, no river boat.
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

VERSION = 10  # (10: a bulk cargo's season at sea, SEASON, PW-1572; a need for dried fish, trade.py, PW-1573; lane 244; 9: boats follow the river's course, the hands on river hauls, herds and horses walk as droves, lane 226, step4c.md; 8: the hands, time and risk of a sea haul, HAND_KM, lane 225, step4b.md; 7: craft and luxury goods, PW-1522; a handling cost per port call, PW-1529; trading towns need the long-haul network,
# PW-1530; lane 224, step4a.md. 2: routes, trading towns and merchant quarters, PW-1504; herders fetch grain, PW-1511 B; flyers carry wild foods, PW-1510;
# 3: a route is judged per good against its carried volume, and last era's routes hold down to half the bar, PW-1515 and PW-1514;
# 4: grain takers look on until a round finds no more, SEEK_GOODS, lane 216b; 5: market pools and worn ways, lane 218;
# 6: every good looks on until none is left, in one shared walk, and the routes split into long-haul and local, lane 222)
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
RIVER_COURSE = False  # True: a river boat goes only from a cell to the next one down its river's course (the world's `downstream`) or up
# it (lane 226, step4c.md). Off (as main d8152d53): any two neighbouring cells with navigable rivers, so a boat also crosses between
# tributaries and over watersheds (on the judge runs two thirds of those edges are not along a river). On, it cut herders' grain met by a
# tenth to a quarter on all three judge runs (grain went by those crossings), and the river hands bound spices as well without it: an inbox draft
# --- droves (lane 226, step4c.md): herd animals and horses walk to market, driven by their herders over any ground, so on land they cost a
# drove's way, not a pack animal's load; they take no river boat; at sea they ship as middling cargo (freight and the hands)
DROVES = True  # False: carried as any middling cargo, by river boat too (main d8152d53)
DROVE_GOODS = ("livestock", "horses")
DROVE = 0.25  # a drove's cost per km, a pack animal = 1. Texas to Kansas, "as much as a thousand miles" (~1,600 km): "the cost of sending
# cattle over the trail ... was about $1.25 per head; the cost of railway is about $4.00 a head" (Lytle in Freeman 1905, p. 660, quoted in J. Econ. Hist.,
# "End of the Chisholm Trail"); a head was worth $2 in Texas after the war, up to $40 in the north (Wikipedia, Cattle drives in the United
# States). $1.25 against $2-4 at the start is 31-63% of the value over ~1,600 km, an e-fold per ~1,700-4,300 km, which against the middling
# fall-off (433 pack-km) is 0.10-0.25 of a pack animal per km. JUDGEMENT: the dear end (at 0.10 horses' far tenth went 7,400 km overland on
# 3e0eb4, past the sourced ~1,000-3,000 km)
CANOE_COAST = RIVER_UP  # a canoe along the coast, one cell out (`canoes`). JUDGEMENT: paddled, as against a current; no coastal canoe cost
# was found
# --- a port call (PW-1529, step4a.md section 2): loading and unloading, and the harbour's dues, on top of the per-km cost, so a sea haul is
# not almost free over distance. ORBIS prices sea carriage at 0.1 denarii per kg of wheat per day under sail (Scheidel, Meeks & Weiland
# 2012, ORBIS v1 paper) and ~0.001 per km, so a day of a ship's time is ~100 sea-km; and ORBIS has no transshipment cost (Page 2026, J.
# Maritime Archaeology 21: the price edict "does not include transhipment fees"). Page 2026, from P.Lond. 3.948: 9.5 t took 2 days to
# load and 4 to unload. So loading costs 2 ship-days (200 sea-km) where goods go from land onto the sea, unloading 4 (400 sea-km) where
# they come ashore. Page's papyri put harbour operations at 5-10% of a voyage's cost (P.Oxy. 3.522): 600 sea-km is that share of a
# 6,000-12,000 km voyage, more of a short one (as P.Oxy. 14.1650's 51.5%)
DAY_KM = 0.1 / 0.001  # sea-km per ship-day (ORBIS: per day / per km)
LOAD_DAYS, UNLOAD_DAYS = 2.0, 4.0  # Page 2026, P.Lond. 3.948
HARBOUR_DUE = 0.025  # share of the cargo's value paid where it comes ashore: the Roman portorium, the quadragesima of 2.5% (2% earlier;
# De Laet 1949 via ostia-antica.org; the Red Sea's 25% tetarte was a frontier tax, not a harbour's: the toll at a border stands for it)
# --- the hands, time and risk of a sea haul (lane 225, step4b.md): a ship's freight per km is ORBIS's 1/28 of a donkey's, but what a long
# sea haul cost a dear good was not freight. Each stage of it (a season's sail between emporia) passed the cargo to another merchant, who
# was paid for a season of capital, the voyage's risk and his margin. On land these are in the fall-off length (FALL_KM is set from whole
# overland markups, Cato's mill and Kanesh's tin, hands included) and in the toll at every border crossed, rivers included (a river runs
# through the cultures' land). But the per-km cost at sea is ORBIS's freight alone, and a sea haul crosses no border. So a sea km also
# takes a share of the cargo's value (value, not weight, like the toll): the value e-folds every HAND_KM km at sea, on top of the freight.
# Sources (fetched; step4b.md section 1): pepper cost 1-2 g of silver a kilo where it grew, 10-14 at Alexandria, 14-18 at Venice, 20-30
# in Europe's consumer lands (Pearson 1987, The Portuguese in India, p. 41): x8 over Malabar to Alexandria, ~6,000 km mostly by sea
# [est.], one e-fold per ~2,900 km; x1.3 over Alexandria to Venice (~2,400 km, one hand: ~8,300 km); Pliny NH 6.101: India's wares sell
# in Rome "at fully one hundred times their prime cost" (~8,200 km [est.]: ~1,800 km); an Athenian sea loan on a cargo of wine for the
# Pontus round trip, capital and risk alone, 22.5% (30% late in the season; Dem. 35.10: ~3,600 km [est.]: ~17,700 km)
HANDS = True  # False: freight alone at sea (main fe063817)
RIVER_HANDS = True  # the same hands on a river haul (lane 226, step4c.md): both price chains above ran by river as well as by sea (Pliny's
# goods went up the Nile from Juliopolis to Coptos, Pearson's pepper down it to Alexandria), and on a river, as at sea, the per-km cost is
# ORBIS's freight alone. False: freight alone on rivers (main d8152d53)
HAND_KM = {
    # (bulk: none. A bulk cargo went in one hull from port to port, and its sourced sea cost is freight: wheat by sea ~1.3% of its value
    # per 100 Roman miles (Duncan-Jones, review1.md section 6), which ORBIS's freight already gives (~1.8% here). JUDGEMENT: the sea
    # loan's capital and risk (Dem. 35.10, ~17,700 km) left out for bulk; with it, herders' grain met fell by a tenth on 0141d1, step4b.md)
    # JUDGEMENT: Pearson's relayed Indian Ocean haul (~2,900), within the sourced 1,800 (Pliny, polemical) to 8,300 (Alexandria to Venice, one
    # leg); middling goods with the dear ones, as cloth, glass and porcelain crossed the Indian Ocean by the same emporia (Zhao 2015,
    # step4a.md section 1: porcelain reached the Swahili coast "primarily ... indirectly")
    "middling": 3000.0,
    "precious": 3000.0,
}
# --- a bulk cargo's season at sea (PW-1572, lane 244, bought_in_244.md). HAND_KM leaves bulk on freight alone: one hull, port to port. But
# a hull's voyages are counted in seasons, and the cargo's capital and the sea's risk are paid per season. Rome's farthest regular grain
# came from Egypt, "a distance of 1,000 miles", and navigation was "strongly discouraged from mid-November to early March"
# (warhistory.org, "The Roman grain trade"); the Egyptian grain ships "likely only completed one round trip per year", while from Africa
# or Sicily "several round trips per year could be accomplished" (Wikipedia, Cura Annonae). So a laden leg of ~1,000 miles (SEASON_KM)
# used up a ship's whole season, and a shorter one a fraction of it. A season of a sea cargo's capital and risk is priced by the sea
# loan: 22.5% for a season's round trip (Dem. 35.10, HAND_KM's source). Spread over the season's laden leg, a bulk cargo's value e-folds
# every SEASON_KM / ln(1.225) ~ 7,900 km at sea, on top of the freight: ~18% of it gone on Egypt's leg, ~70% on a 10,000 km haul (which
# would also take several seasons). It is a share of value, like the hands; what keeps grain's sea hauls short is that its freight and
# port calls are already a large share of a cheap good's value, and this season's capital adds to them. Dear goods already pay their
# whole relayed price chains (HAND_KM). Sea only: a river haul is short and runs through the cultures' land, where FALL_KM and the tolls
# already carry its hands (lane 226 found river hands cut herders' grain). A further leg's own port call (unloading, wintering, reloading)
# is left out: the walk's cost cannot count legs (it would depend on the path's sea km so far).
SEASON = True  # False: bulk pays freight alone at sea, as before (main dd82c068)
SEASON_CLASSES = ("bulk",)
SEASON_KM = 1000 * 1.609  # one season's laden leg: Egypt to Rome, 1,000 miles (one round trip a year)
SEASON_LOAN = 0.225  # a season's capital and risk on the cargo's value: the sea loan for a season's round trip (Dem. 35.10)
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
HANDLE = True  # PW-1529: a port call costs loading, unloading and the harbour's dues (above); False: the per-km cost only
SEEK_CAP = 400  # every good's takers look on, from source to next best source, until none is left (PW-1519): one shared walk in which an
# emptied source stops spreading and the land it held is walked again from the live sources (_seek, lane 222, step3d.md). This caps the
# sources one taker draws from, a safety cap only. Before: grain ran round after round (lane 216b) and the other goods stopped after 3
# rounds, a compute bound (step3b.md, step3c.md: run to the end with rounds, or with each cell's 8 best sources, they took ~5-30 times as long)
# --- market pools (PW-1514, step3c.md; D64: towns are the hubs). A town's market gathers its hinterland's spare goods and its wants: inside
# the pool the spare goods meet the wants first (a market, no road drawn), and only what is left over travels, from the town, or is
# fetched, to the town. A marginal cell turning from giver to taker then moves a pool's total a little instead of a source in or out
POOL = True
POOL_HOPS = 1.5  # a cell joins its nearest town's pool when the way there is at most this many cell spacings. JUDGEMENT: the town's
# cell and its neighbours (60-80 km at L7), the grid's smallest reach beyond a cell; a market's own reach is smaller (a day's walk,
# ~30 km for Kanesh's cities, review1.md section 4; Skinner's standard areas ~4-5 km), and it is the town spacing that sets the pool
# --- worn ways (PW-1515, step3c.md): a road gets cheaper once traffic uses it, for every good, so goods share trunks
TRUNK = False  # off: on the judge runs worn ways drew as many stretches (531 / 331 / 533 an era against 536 / 327 / 530 without) and
# made them less steady under the land nudge (0.65 / 0.51 / 0.48 against 0.64 / 0.60 / 0.50), at twice the time (step3c.md)
TRAIL = 0.4  # the most a worn way takes off a land edge's cost. Tobler's hiking function (Tobler 1993, from Imhof 1950): off a path one
# walks at 3/5 of the speed on it, so a path costs 0.6 of the open ground. Helbing et al. 1997 (Phys. Rev. E 56: 2527): "frequently
# used trails become more developed, making them more attractive", with a saturating clarity (their eq. 15)
WEAR_HALF = 0.002  # the share of the frame's carried goods over a stretch that wears it halfway. JUDGEMENT (step3c.md): no source gives the
# traffic a track needs; the busiest 1% of carried stretches carry 0.2-0.5% each (3e0eb4), so these are worn most
WEAR_KEEP = 0.5  # the share of last era's wear that is still there (roads persist: Bleakley & Lin 2012, Dalgaard et al. 2022; step3b.md).
# JUDGEMENT: half over an era of 500 years
TRUNK_ITERS = 3  # walks per frame at most: walk, wear the ways the goods took, walk again; it stops sooner once the wear changes by
# less than WEAR_TOL anywhere (a compute bound)
WEAR_TOL = 0.02


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


@njit(cache=True)
def _grow(a, m):
    """a with room for at least m rows (doubled), the first rows kept."""
    if m <= a.shape[0]:
        return a
    b = np.empty((max(m, 2 * a.shape[0]),) + a.shape[1:], a.dtype)
    b[:a.shape[0]] = a
    return b


@njit(cache=True)
def _seek(src, d0, nbr_off, nbr_idx, ecost, ekm, emode, ebord, esrc, limit, L, tk_off, tk_pair, rem, hc, seeking, cap, avail, avail0, S,
          gT, gC, gF, sc, tcul, inner_km, long_good, long_km, grp, through, tix, tdict, eall, ex, exl):
    """One shared walk in which every taker takes from the best live supply that reaches it, and a source that runs empty stops
    spreading (PW-1519, lane 218's idea). The walk is _walk's (Dijkstra from every source at once, a source starting at d0), and a cell's
    takers (tk_pair[tk_off[c]:tk_off[c+1]], best supplied first as in step 2) are served when the walk settles the cell: each takes
    min(its lack rem x hc, the supply there x hc, what is left at the source). A source emptied this way is dead: the cells it held are
    walked again at once from the live cells bordering them and the live sources among them (as a fresh walk from the live sources would
    reach them: taking a source away lowers no other cost), so a taker it cut short takes from its next best live source. A taker that got
    all it asked (the supply there was its limit) looks no further. It runs until no taker is left seeking; `cap` (sources per taker) is
    only a safety cap.

    Each delivery is traced back to its source along the walk's edges as it happens (the edges change when a source dies): its amount is
    added to every cell passed (through[grp], and at a town (tix >= 0) to tdict per (town, group, giver)), and to every directed edge passed
    (eall; ex for its part between cultures; exl for that part when it is long-haul: long_good, or carried at least long_km). Givers: a
    pooled source (a town in gT) splits among its pool's cultures gC by shares gF, else the source cell's culture sc.

    Returns the deliveries (pair, source cell, amount, km, km per mode, borders, cost-km of carrying, carried?, part between cultures,
    long-haul?),
    the most sources any taker drew from, the number of sources emptied, and the takers the cap stopped while still short."""
    n = nbr_off.shape[0] - 1
    d = np.full(n, np.inf)
    org = np.full(n, -1, np.int64)
    pe = np.full(n, -1, np.int64)
    km = np.zeros(n)
    mkm = np.zeros((n, 4))
    nb = np.zeros(n, np.int32)
    seed = np.full(n, np.inf)
    alive = np.zeros(n, np.bool_)
    head = np.full(n, -1, np.int64)  # (per source: its cells, a linked list, checked against org when read)
    ncell = np.zeros(1024, np.int64)
    nnext = np.zeros(1024, np.int64)
    nn = 0
    stamp = np.zeros(n, np.int64)
    pstamp = np.zeros(n, np.int64)
    serves = np.zeros(tk_pair.shape[0], np.int64)
    m0 = tk_pair.shape[0] + 16
    dp = np.zeros(m0, np.int64)
    do = np.zeros(m0, np.int64)
    dg = np.zeros(m0)
    dkm = np.zeros(m0)
    dmkm = np.zeros((m0, 4))
    dnb = np.zeros(m0)
    dcar = np.zeros(m0)
    dcr = np.zeros(m0, np.bool_)
    dx = np.zeros(m0)
    dl = np.zeros(m0, np.bool_)
    nd = 0
    deaths = 0
    h = [(0.0, np.int64(0))]
    h.pop()
    for k in range(src.shape[0]):
        s = src[k]
        alive[s] = True
        seed[s] = d0[k]
        if d0[k] < d[s]:
            d[s] = d0[k]
            org[s] = s
        heapq.heappush(h, (d0[k], s))
    for s in range(n):
        if org[s] == s:
            ncell = _grow(ncell, nn + 1)
            nnext = _grow(nnext, nn + 1)
            ncell[nn] = s
            nnext[nn] = head[s]
            head[s] = nn
            nn += 1
    while len(h) > 0:
        di, i = heapq.heappop(h)
        if di != d[i]:
            continue
        o = org[i]
        if o < 0 or not alive[o]:
            continue
        # --- serve the takers here
        sup = math.exp(-min(di, 700.0) / L)
        died = False
        for q in range(tk_off[i], tk_off[i + 1]):
            p = tk_pair[q]
            if not seeking[q] or rem[p] <= 0.0:
                continue
            ask = min(rem[p], sup) * hc[q]
            if ask <= 0.0:
                seeking[q] = False
                continue
            got = min(ask, avail[o])
            serves[q] += 1
            seeking[q] = got < ask * (1 - 1e-9) and serves[q] < cap
            if got <= 0.0:
                continue
            avail[o] -= got
            rem[p] -= got / max(hc[q], 1e-12)
            # (the delivery's givers)
            lo = np.searchsorted(gT, o)
            hi = np.searchsorted(gT, o, side="right")
            cross = 0.0
            tc = tcul[p]
            if hi > lo:
                for r in range(lo, hi):
                    if gC[r] >= 0 and gC[r] != tc:
                        cross += got * gF[r]
            elif sc[o] >= 0 and sc[o] != tc:
                cross = got
            m1 = nd + 1
            if m1 > dp.shape[0]:
                dp = _grow(dp, m1)
                do = _grow(do, m1)
                dg = _grow(dg, m1)
                dkm = _grow(dkm, m1)
                dmkm = _grow(dmkm, m1)
                dnb = _grow(dnb, m1)
                dcar = _grow(dcar, m1)
                dcr = _grow(dcr, m1)
                dx = _grow(dx, m1)
                dl = _grow(dl, m1)
            dp[nd] = p
            do[nd] = o
            dg[nd] = got
            dkm[nd] = km[i]
            for m in range(4):
                dmkm[nd, m] = mkm[i, m]
            dnb[nd] = nb[i]
            dcar[nd] = di + L * math.log(max(S[o], 1e-300))
            dcr[nd] = pe[i] >= 0
            dx[nd] = cross
            lng = long_good or km[i] + inner_km[p] >= long_km
            dl[nd] = lng
            nd += 1
            # (trace it back along the walk's edges as they are now)
            j = i
            while True:
                through[grp, j] += got
                t = tix[j]
                if t >= 0:
                    if hi > lo:
                        for r in range(lo, hi):
                            if gC[r] >= 0:
                                key = (t * 8 + grp) * 1_000_003 + gC[r]
                                tdict[key] = tdict.get(key, 0.0) + got * gF[r]
                    elif sc[o] >= 0:
                        key = (t * 8 + grp) * 1_000_003 + sc[o]
                        tdict[key] = tdict.get(key, 0.0) + got
                e = pe[j]
                if e < 0:
                    break
                eall[e] += got
                ex[e] += cross
                if lng:
                    exl[e] += cross
                j = esrc[e]
            if avail[o] <= 1e-9 * max(avail0[o], 1e-12):
                died = True
                break
        if died:  # --- the source is empty: it stops spreading, and the land it held is walked again from the live sources
            alive[o] = False
            deaths += 1
            tag = deaths
            seed[o] = np.inf
            bad = []
            x = head[o]
            while x >= 0:
                j = ncell[x]
                if org[j] == o and stamp[j] != tag:
                    stamp[j] = tag
                    bad.append(j)
                x = nnext[x]
            head[o] = -1
            for j in bad:
                d[j] = np.inf
                org[j] = -1
                pe[j] = -1
                km[j] = 0.0
                for m in range(4):
                    mkm[j, m] = 0.0
                nb[j] = 0
            for j in bad:
                if alive[j] and seed[j] < np.inf:  # (a live source that the dead one had outbid on its own cell)
                    d[j] = seed[j]
                    org[j] = j
                    ncell = _grow(ncell, nn + 1)
                    nnext = _grow(nnext, nn + 1)
                    ncell[nn] = j
                    nnext[nn] = head[j]
                    head[j] = nn
                    nn += 1
                    heapq.heappush(h, (d[j], np.int64(j)))
            for j in bad:
                for e in range(nbr_off[j], nbr_off[j + 1]):
                    b = nbr_idx[e]
                    if stamp[b] != tag and pstamp[b] != tag and d[b] < np.inf:
                        pstamp[b] = tag
                        heapq.heappush(h, (d[b], np.int64(b)))
            continue
        # --- spread
        for e in range(nbr_off[i], nbr_off[i + 1]):
            c = ecost[e]
            if c < 0.0:
                continue
            j = nbr_idx[e]
            nd2 = di + c
            if nd2 < d[j] and nd2 <= limit:
                d[j] = nd2
                org[j] = o
                pe[j] = e
                km[j] = km[i] + ekm[e]
                for m in range(4):
                    mkm[j, m] = mkm[i, m]
                mkm[j, emode[e]] += ekm[e]
                nb[j] = nb[i] + ebord[e]
                ncell = _grow(ncell, nn + 1)
                nnext = _grow(nnext, nn + 1)
                ncell[nn] = j
                nnext[nn] = head[o]
                head[o] = nn
                nn += 1
                heapq.heappush(h, (nd2, j))
    mx = 0
    capped = 0
    for q in range(serves.shape[0]):
        mx = max(mx, serves[q])
        if serves[q] >= cap and not seeking[q] and rem[tk_pair[q]] > 1e-12:
            capped += 1
    return dp[:nd], do[:nd], dg[:nd], dkm[:nd], dmkm[:nd], dnb[:nd], dcar[:nd], dcr[:nd], dx[:nd], dl[:nd], mx, deaths, capped


def _knows(kn: set, techs) -> bool:
    return any(t in kn for t in techs)


def _tolerance(att: dict | None, c: int, era: float) -> float:
    """A culture's tolerance at the era (attitudes.py read-out: its track, newest sample at or before the era), else the median."""
    r = ((att or {}).get("cultures") or {}).get(str(c))
    if not r:
        return TOL_MID
    best = None
    for kyr, tol, *_ in r.get("track") or []:
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
        if RIVER_COURSE:  # (a boat follows its river: a cell to the next one down its course or up it, lane 226, step4c.md)
            dn = np.asarray(W.get("downstream", np.full(n, -1))).astype(np.int64)
            down = dn[a] == b
            rv &= down | (dn[b] == a)
            rf = np.where(down, M["down"], M["up"])
        else:
            rf = np.where(elev[b] < elev[a], M["down"], M["up"])

        def edges(fc, boats=True):  # (open, factor per km, mode) per edge from the cells' factors
            fa, fb = fc[a], fc[b]
            fac = 0.5 * (fa + fb)
            use = rv & (rf < fac) & boats
            return (fa > 0) & (fb > 0), np.where(use, rf, fac), np.where(use, 1, np.where(sea[a] | sea[b], 2, 0))
        open_, fac, mode = edges(fcell)
        # herds and horses walk (lane 226, step4c.md): on land a drove's cost, over any ground (the herders drive them), never by river
        # boat; at sea as any middling cargo
        drove_e = edges(np.where(land, np.minimum(f_land, DROVE * mx.get("drove", 1.0) * hm), np.where(sea, f_sea, -1.0)), False)
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
            drove_e = (drove_e[0] & ~closed, *drove_e[1:])
            self.war_edges = int(closed.sum())
        else:
            self.war_edges = 0
        fly = np.zeros(n, bool)
        fl = np.array([info[c]["flies"] for c in cu.tolist()], bool) if len(cu) else np.zeros(0, bool)
        fly[cell[fl]] = True
        self.fly = fly
        self.e = {"a": a, "b": b, "hop": hop, "open": open_, "fac": fac, "mode": mode, "bord": bord, "toll": toll,
                  "fly": fly[a] | fly[b], "fetch": fetch_e, "drove": drove_e, "load": land[a] & sea[b], "unload": sea[a] & land[b], "sea_f": M["sea"]}
        self.costs: dict = {}
        self.nbr_off, self.nbr_idx = g.nbr_off.astype(np.int64), g.nbr_idx.astype(np.int64)
        # the stretches (each pair of neighbouring cells, both ways as one): esrc per directed edge, ukey (a * n + b, a < b), uid per edge
        self.esrc = srcs.astype(np.int64)
        lo, hi = np.minimum(self.esrc, self.nbr_idx), np.maximum(self.esrc, self.nbr_idx)
        self.ukey, self.uid = np.unique(lo * n + hi, return_inverse=True)
        self.wear = None  # (per directed edge: the factor a worn way leaves of a land edge's cost, PW-1515; None: no way worn)
        self.nope = np.full(n, -1, np.int64)  # (no edges: deliveries inside a market's pool travel no road of the walk)

    def set_wear(self, traffic: np.ndarray | None):
        """Ways worn by traffic (PW-1515): a land stretch carrying `traffic` people's worth of goods (per stretch, as Loads.traffic) costs
        1 - TRAIL x traffic / (traffic + WEAR_HALF) of its unworn cost, for every good. The cached costs are remade."""
        self.costs = {}
        if traffic is None or not traffic.any():
            self.wear = None
            return
        u = traffic[self.uid]
        self.wear = 1.0 - TRAIL * u / (u + WEAR_HALF)

    def pools(self) -> dict | None:
        """The market pools (PW-1514, D64: towns as hubs): every cell joins the settlement-ledger town nearest it by carrying cost (bulk
        goods' costs, tolls included) if that town lies within POOL_HOPS cell spacings along the way. Christaller and Skinner (review1.md
        section 5): market areas tile the settled land and their size follows settled density, not a fixed walk, so the nearest town
        takes the cell; the cap only keeps a lone town from drawing in empty country. {"org": town cell per cell (-1: none), "km", "mkm",
        "nb": the way to it, "heads": the pool's people per town cell}, or None without towns."""
        from .trade_routes import towns_at
        T = towns_at(self.ctx, self.era)
        tc = np.array(sorted(c for c in T if self.own[c] >= 0), np.int64)
        if not len(tc):
            return None
        c, mode, km = self.cost("bulk")
        d, org, kmv, mkm, nb, pe = _walk(tc, np.zeros(len(tc)), self.nbr_off, self.nbr_idx, c, km, mode, self.e["bord"].astype(np.int32),
                                         np.inf)
        org = np.where((org >= 0) & (kmv <= POOL_HOPS * self.e["hop"] + 1e-6), org, -1)
        heads = TR.cells_at(self.ctx, self.i)["heads"]
        return {"org": org, "km": kmv, "mkm": mkm, "nb": nb,
                "heads": np.bincount(org[org >= 0], weights=heads[org >= 0], minlength=len(org))}

    def cost(self, cl: str, fetch: bool = False, drove: bool = False):
        """(edge cost, edge mode, edge km) for a value class (cached); fetch: with the herders' own animals (PW-1511 B); drove: animals
        that walk (DROVE_GOODS, lane 226)."""
        if (cl, fetch, drove) not in self.costs:
            e, L = self.e, self.L[cl]
            op, fac, mode = (e["drove"] if drove else e["fetch"] if fetch and e["fetch"] is not None else (e["open"], e["fac"], e["mode"]))
            c = np.where(op, e["hop"] * fac, -1.0)
            mode = mode.copy()
            if self.wear is not None:  # (a worn way is cheaper on land, PW-1515; rivers and seas are not worn)
                c = np.where((c > 0) & (mode == 0), c * self.wear, c)
            if cl == "precious":  # (flyers carry light goods over anything)
                air = e["hop"] * AIR
                use = e["fly"] & ((c < 0) | (air < c))
                c = np.where(use, air, c)
                mode = np.where(use, 3, mode)
            if HANDLE:  # (a port call, PW-1529: loading where goods leave the land, unloading and the harbour's dues where they land)
                c = np.where((c >= 0) & e["load"] & (mode == 2), c + LOAD_DAYS * DAY_KM * e["sea_f"], c)
                c = np.where((c >= 0) & e["unload"] & (mode == 2), c + UNLOAD_DAYS * DAY_KM * e["sea_f"] - L * math.log1p(-HARBOUR_DUE), c)
            if HANDS and cl in HAND_KM:  # (the hands, time and risk of a sea haul, per km, as a share of value: lane 225; and of a river
                # haul, lane 226)
                water = (mode == 2) | ((mode == 1) & RIVER_HANDS)
                c = np.where((c >= 0) & water, c + e["hop"] * L / HAND_KM[cl], c)
            if SEASON and cl in SEASON_CLASSES:  # (a bulk cargo's season of capital and risk, spread over a season's laden leg: PW-1572)
                c = np.where((c >= 0) & (mode == 2), c + e["hop"] * L * math.log1p(SEASON_LOAN) / SEASON_KM, c)
            c = np.where((c >= 0) & e["bord"], c - L * np.log1p(-e["toll"]), c)
            self.costs[(cl, fetch, drove)] = (np.ascontiguousarray(c), mode.astype(np.int64), np.full(len(c), e["hop"]))
        return self.costs[(cl, fetch, drove)]

    def cost_of(self, good: str):
        """cost() for a good: its value class, the herders' fetch, a drove."""
        cl = FALL_CLASS.get(good, TR.GOODS[good][1])
        return self.cost(cl, self.fetch and good in FETCH_GOODS, DROVES and good in DROVE_GOODS)

    def sources(self, good: str):
        """(surplus per cell 0..1, the culture whose surplus it is): a cell's biggest surplus of the good among its cultures."""
        P = self.P
        sur = P["surplus"][good]
        cell, cu = P["cell"], P["culture"]
        n = self.ctx.g.n
        S = np.zeros(n)
        sc = np.full(n, -1, np.int64)
        order = np.argsort(sur, kind="stable")
        S[cell[order]] = sur[order]
        sc[cell[order]] = cu[order]
        return S, sc

    def walk(self, good: str, live: np.ndarray | None = None, S: np.ndarray | None = None, sc: np.ndarray | None = None):
        """The supply of a good over the map from its surplus cells (only the `live` ones, if given; S, sc: the surplus per cell and its
        culture, else sources(good)): (supply 0..1 per cell, origin cell, km, km per mode, borders crossed, source culture per cell,
        carrying cost-km, source surplus per cell, the edge each cell was reached by, each edge's mode)."""
        cl = FALL_CLASS.get(good, TR.GOODS[good][1])
        L = self.L[cl]
        n = self.ctx.g.n
        if S is None:
            S, sc = self.sources(good)
        src =np.flatnonzero((S >= TR.SHOW_MIN) & (True if live is None else live))
        c, mode, km = self.cost_of(good)
        g = self.ctx.g
        bord = self.e["bord"].astype(np.int32)
        d0 = -L * np.log(S[src])
        d, org, kmv, mkm, nb, pe = _walk(src.astype(np.int64), d0, self.nbr_off, self.nbr_idx, c, km, mode, bord, L * math.log(1.0 / FLOOR))
        seed = np.full(n, np.inf)
        seed[src] = d0
        self._last = {"good": good, "d": d, "org": org, "km": kmv, "mkm": mkm, "nb": nb, "pe": pe, "S": S, "sc": sc, "L": L,
                      "edges": (c, km, mode, bord), "seed": seed}
        return self._view()

    def _view(self):
        w = self._last
        d, org, S, L = w["d"], w["org"], w["S"], w["L"]
        sup = np.where(np.isfinite(d), np.exp(-np.minimum(d, 700.0) / L), 0.0)
        carry = np.where(org >= 0, d + L * np.log(np.maximum(S[np.maximum(org, 0)], 1e-300)), 0.0)  # (the carrying cost alone, cost-km)
        return sup, org, w["km"], w["mkm"], w["nb"], w["sc"], carry, S, w["pe"], w["edges"][2]


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


class _Ledger:
    """One walk's bookkeeping: per (giver, taker, good) the flow and its ways, home deliveries, the loads for the routes."""

    def __init__(self, fr: _Frame, loads):
        self.fr, self.loads = fr, loads
        P = fr.P
        self.cell, self.cu, self.w = P["cell"], P["culture"], P["w"]
        nc = len(fr.ctx.cultures()["cultures"])
        self.wsum = np.ones(nc)
        for c, x in P["wsum"].items():
            self.wsum[c] = x
        self.heads = TR.cells_at(fr.ctx, fr.i)["heads"]
        self.agg: dict = {}
        self.home: dict = {}

    def record(self, good, p, at, o, got, km, carry, mkm, nb, pe, emode, split, traced: bool = False):
        """Deliveries to the pairs p (arriving at cells `at`) from source cells o, `got` people's worth each; their ways (km, cost-km,
        km per mode, borders); split: the givers of a pooled source (town cell -> cultures, shares) as (towns, cultures, shares) sorted by
        town, else the source cell's culture (split[3], per cell). traced: the routes have them already (_seek traces as it goes)."""
        T, Cg, F, sc = split
        lo = np.searchsorted(T, o, "left")
        hi = np.searchsorted(T, o, "right")
        k = hi - lo
        cnt = np.maximum(k, 1)
        row = np.repeat(np.arange(len(p)), cnt)
        off = np.arange(len(row)) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        pooled = k[row] > 0
        q = np.where(pooled, lo[row] + off, 0)
        giver = np.where(pooled, Cg[q] if len(Cg) else -1, sc[o[row]])
        amt = got[row] * np.where(pooled, F[q] if len(F) else 1.0, 1.0)
        p, at = p[row], at[row]
        t = self.cu[p]
        if self.loads is not None and not traced:
            self.loads.add(good, at, amt, giver, t, pe, emode)
        cp = self.cell[p]
        v = amt / np.maximum(self.heads[cp], 1e-12) * self.w[p] / self.wsum[t]
        hm = (v > 0) & (giver == t)
        for c, x in _sum_by(t[hm], v[hm]).items():
            self.home.setdefault(c, {})[good] = self.home.get(c, {}).get(good, 0.0) + x
        fl = (v > 0) & (giver >= 0) & (giver != t)
        if fl.any():
            nw = len(self.wsum)
            key = giver[fl] * nw + t[fl]
            u, inv = np.unique(key, return_inverse=True)
            vv = v[fl]
            r = row[fl]
            cols = [vv, vv * km[r], vv * carry[r], *(vv * mkm[r, m] for m in range(4)), vv * nb[r]]
            sums = [np.bincount(inv, weights=x, minlength=len(u)) for x in cols]
            for j, kk in enumerate(u.tolist()):
                a = self.agg.setdefault((kk // nw, kk % nw, good), [0.0, 0.0, 0.0, np.zeros(4), 0.0])
                a[0] += sums[0][j]
                a[1] += sums[1][j]
                a[2] += sums[2][j]
                a[3] = a[3] + np.array([sums[3 + m][j] for m in range(4)])
                a[4] += sums[7][j]


def _exchange(fr: _Frame, pools: dict | None, loads) -> tuple:
    """Every good's allocation over one walk of the frame (with the frame's worn ways): (ledger, unmet, the most sources a taker drew from,
    and the takers SEEK_CAP stopped while still short, per good)."""
    from . import trade_routes as RT
    P = fr.P
    cell, cu, w = P["cell"], P["culture"], P["w"]
    led = _Ledger(fr, loads)
    heads, wsum_arr = led.heads, led.wsum
    n = fr.ctx.g.n
    trading = np.array([fr.info[c]["mode"] == "trade" for c in cu.tolist()], bool) if len(cu) else np.zeros(0, bool)
    unmet: dict = {}
    rounds: dict = {}
    capped: dict = {}
    nw = len(wsum_arr)
    empty = (np.zeros(0, np.int64), np.zeros(0, np.int64), np.zeros(0))
    for good in TR.GOODS:
        lack = P["lack"].get(good)
        if lack is None or not (lack > 0).any():
            continue
        S0, sc0 = fr.sources(good)
        rem = lack.copy()
        want = (lack > 0) & trading
        at = cell.copy()  # (where each pair's goods arrive: its own cell, or its market's town)
        T, Cg, F = empty
        if pools is not None:
            # the market: inside each pool its spare goods meet its wants first, every want met in the same share (a market, no road)
            po = pools["org"]
            amt = S0 * heads
            inp = po >= 0
            supp = np.bincount(po[inp], weights=amt[inp], minlength=n)
            lp = np.flatnonzero(want & (po[cell] >= 0))
            tw = po[cell[lp]]
            ask = rem[lp] * heads[cell[lp]]
            dem = np.bincount(tw, weights=ask, minlength=n)
            f = np.minimum(1.0, np.divide(supp, dem, out=np.zeros(n), where=dem > 0))
            cc = np.flatnonzero(inp & (amt > 0))  # (the givers per town: each culture's share of its pool's spare goods)
            if len(cc):
                key = po[cc] * nw + sc0[cc]
                u, inv = np.unique(key, return_inverse=True)
                s = np.bincount(inv, weights=amt[cc], minlength=len(u))
                T = u // nw
                Cg = u % nw
                F = s / supp[T]
            sc = sc0.copy()
            split = (T, Cg, F, sc)
            got = f[tw] * ask
            g_ok = got > 0
            if g_ok.any():
                lpg = lp[g_ok]
                led.record(good, lpg, tw[g_ok], tw[g_ok], got[g_ok], pools["km"][cell[lpg]], np.zeros(len(lpg)), pools["mkm"][cell[lpg]],
                           pools["nb"][cell[lpg]].astype(float), fr.nope, np.zeros(len(fr.esrc), np.int64), split)
            rem[lp] -= f[tw] * rem[lp]
            # what is left of each pool travels from its town (its spare goods per head of the pool) or is fetched to its town
            net = np.maximum(0.0, supp - dem)
            S = np.where(inp, 0.0, S0)
            tws = np.flatnonzero(net > 0)
            S[tws] = np.minimum(1.0, net[tws] / np.maximum(pools["heads"][tws], 1e-12))
            avail0 = np.where(inp, 0.0, S0 * heads)
            avail0[tws] = net[tws]
            at = np.where(po[cell] >= 0, po[cell], cell)
            # (the walk names one culture per source; the split above names the pool's givers)
        else:
            S, sc = S0, sc0
            split = (T, Cg, F, sc)
            avail0 = S * heads
        want &= rem > 1e-12
        nr = ncap = 0
        p = np.flatnonzero(want)
        if len(p):
            # one shared walk: every taker takes from its best live source, and on to the next when that one runs empty (_seek)
            cl = FALL_CLASS.get(good, TR.GOODS[good][1])
            L = fr.L[cl]
            src = np.flatnonzero(S >= TR.SHOW_MIN)
            c, emode, ekm = fr.cost_of(good)
            ac = at[p]
            o_ = np.argsort(ac, kind="stable")
            p, ac = p[o_], ac[o_]
            tk_off = np.searchsorted(ac, np.arange(n + 1)).astype(np.int64)
            cp = cell[p]
            inner = ac != cp  # (the way on from the town to the pair's own cell)
            ikm = np.zeros(len(cell))
            if pools is not None:
                ikm[p] = np.where(inner, pools["km"][cp], 0.0)
            avail = avail0.copy()
            tr = loads.seek_arrays(good) if loads is not None else RT.seek_dummy(n, len(fr.esrc))
            dp, do, dg, dkm, dmkm, dnb, dcar, dcr, dx, dl, nr, _, ncap = _seek(
                src.astype(np.int64), -L * np.log(S[src]), fr.nbr_off, fr.nbr_idx, c, ekm, emode, fr.e["bord"].astype(np.int32), fr.esrc,
                L * math.log(1.0 / FLOOR), L, tk_off, p.astype(np.int64), rem, heads[cp].astype(float), np.ones(len(p), np.bool_),
                SEEK_CAP, avail, avail0, S, T.astype(np.int64), Cg.astype(np.int64), F.astype(float), split[3].astype(np.int64),
                cu.astype(np.int64), ikm, cl == "precious", RT.LONG_KM, *tr)
            if len(dp):
                ac2, cp2 = at[dp], cell[dp]
                inn = ac2 != cp2
                if pools is not None:
                    dkm = dkm + np.where(inn, pools["km"][cp2], 0.0)
                    dmkm = dmkm + np.where(inn[:, None], pools["mkm"][cp2], 0.0)
                    dnb = dnb + np.where(inn, pools["nb"][cp2], 0)
                led.record(good, dp, ac2, do, dg, dkm, dcar, dmkm, dnb.astype(float), None, None, split, traced=True)
                if loads is not None:
                    loads.seek_done(good, tr, dg, dx, dcr, dl, emode)
        rounds[good] = nr
        if nr and ncap:
            capped[good] = ncap
        q = np.flatnonzero((lack > 0) & trading)
        for c, x in _sum_by(cu[q], rem[q] * w[q] / wsum_arr[cu[q]]).items():
            unmet.setdefault(c, {})[good] = x
    return led, unmet, rounds, capped


def flows_at(ctx, i: int, pol: dict | None = None, att: dict | None = None, scale: dict | None = None, quarters: set | None = None,
             fetch: bool = False, routes: bool = True, last_routes: set | None = None, last_wear: tuple | None = None) -> dict | None:
    """Frame i's exchange: {"flows": [[giver, taker, good, share of the taker's people, people supplied, km, cost-km, mode, kind, via]],
    "home": {culture: {good: share met from its own land elsewhere}}, "unmet": {culture: {good: share}}, "war_edges", "flyer_foods"}; with
    routes (step 3, trade_routes.py) also "routes", "hubs", "quarters" and "volume". quarters: last era's merchant quarters (host, merchant
    culture), whose borders charge no toll; fetch: herders fetch grain with their own animals (PW-1511 B); last_routes: last era's route
    stretches (a * n + b), which stay routes down to trade_routes.ROUTE_HOLD of the bar (PW-1514); last_wear: last era's worn ways (stretch
    keys, traffic), WEAR_KEEP of which is still there (PW-1515). "_wear" (for the next era; derive does not keep it in the doc): this
    frame's worn ways."""
    if TR.pairs_at(ctx, i) is None:
        return None
    fr = _Frame(ctx, i, pol, att, scale, quarters=quarters, fetch=fetch)
    from . import trade_routes as RT
    pools = fr.pools() if POOL else None
    P = fr.P
    cell, cu, w = P["cell"], P["culture"], P["w"]
    wsum = P["wsum"]
    nu = len(fr.ukey)
    worn = np.zeros(nu)
    if TRUNK and last_wear is not None and len(last_wear[0]):
        k = np.searchsorted(fr.ukey, last_wear[0])
        k = np.minimum(k, nu - 1)
        hit = fr.ukey[k] == last_wear[0]
        worn[k[hit]] = WEAR_KEEP * np.asarray(last_wear[1], float)[hit]
    walks = 0
    while True:
        fr.set_wear(worn if TRUNK else None)
        loads = RT.Loads(fr)
        led, unmet, rounds, capped = _exchange(fr, pools, loads)
        walks += 1
        if not TRUNK:
            break
        new = np.maximum(worn, loads.traffic())
        f0 = TRAIL * worn / (worn + WEAR_HALF)
        f1 = TRAIL * new / (new + WEAR_HALF)
        worn = new
        if walks >= TRUNK_ITERS or float(np.max(f1 - f0, initial=0.0)) < WEAR_TOL:
            break
    agg, home = led.agg, led.home
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
    out = {"flows": flows, "home": rnd(home), "unmet": rnd(unmet), "war_edges": fr.war_edges, "flyer_foods": flyer_foods(ctx, fr),
           "rounds": rounds, "capped": capped}
    out["walks"] = walks
    if routes:
        out.update(loads.finish(last_routes))
        out["quarter_edges"] = fr.quarter_edges
    if TRUNK:
        k = np.flatnonzero(worn > 1e-9)
        out["_wear"] = (fr.ukey[k], worn[k])
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
    last_w = None
    if eq and ctx.goods is not None and ctx.cultures() is not None and ctx.world is not None:
        for i, ago in zip(eq["frames"], eq["ago_kyr"]):  # (oldest first: a frame reads the merchant quarters of the one before)
            if frames is not None and i not in frames:
                continue
            f = flows_at(ctx, i, pol, att, scale, quarters=last_q if quarters and routes else None, fetch=fetch, routes=routes,
                         last_routes=last_r, last_wear=last_w)
            if f is not None:
                last_w = f.pop("_wear", None)
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
                          "town_min": TOWN_MIN, "tribute_goods": list(TRIBUTE_GOODS), "quarters": bool(quarters and routes), "fetch": bool(fetch),
                          "pool": POOL, "pool_hops": POOL_HOPS, "trunk": TRUNK, "trail": TRAIL, "wear_half": WEAR_HALF, "wear_keep": WEAR_KEEP,
                          "trunk_iters": TRUNK_ITERS, "seek_cap": SEEK_CAP,
                          "handle": HANDLE, "load_days": LOAD_DAYS, "unload_days": UNLOAD_DAYS, "day_km": DAY_KM, "harbour_due": HARBOUR_DUE,
                          "hands": HANDS, "hand_km": HAND_KM, "river_course": RIVER_COURSE, "river_hands": RIVER_HANDS,
                          "season": SEASON, "season_km": SEASON_KM, "season_loan": SEASON_LOAN,
                          "droves": DROVES, "drove_goods": list(DROVE_GOODS), "drove": DROVE},
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
