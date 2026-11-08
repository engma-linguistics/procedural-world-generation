# Trade step 3: routes and trading towns (PW-1504, lane 214), with PW-1510 and PW-1511

Design: [design1.md](design1.md) step 3. Sources: [review1.md](review1.md) (R§n). Step 2: [step2.md](step2.md).
Code: `planet/lineages/trade_routes.py` (new), `planet/lineages/trade_flow.py` (doc version 2), `GET /api/trade?run=…&routes=1&ago=…`,
`viewer/globe/trade.js`. Tests: `tests/test_trade_routes.py`. Screenshot: [step3_routes_3e0eb4.png](step3_routes_3e0eb4.png).

## In plain words

- **What's new.** The goods that step 2 moves between cultures now draw roads on the map. Every delivery between two cultures is followed
  back, cell by cell, along the cheapest way it took. A stretch of that way that carries at least 2% of the world's trade in its kind of
  goods (food, salt, metal, fine goods, raw goods) that era is a trade route. Before this lane (main c2792e05) there were no routes and no
  trading towns at all, so every number below is new; the goods' flows themselves are unchanged (see "It changes nothing" below).
- **Trading towns.** A town of the settlement ledger that a route passes through is a trading town. Its kind comes from what passes:
  a **port** where goods come or go by sea, a **caravan town** where a pack-animal route leaves farmland for unfarmed desert or steppe,
  a **river port** where goods come or go by river boat, and a **market town** otherwise (R§4, R§5: ports of trade, caravan cities,
  central places).
- **Merchant quarters.** When one foreign culture's goods are a quarter or more of what passes through a trading town, that culture keeps a
  merchant quarter there (Curtin's trade diasporas, R§5). As design1.md says, the quarter removes the toll at that border in the next era
  (500 years later). Tribute-taking kinds (frost and fire giants) send no merchants; a dragon realm's merchants are its kobolds.
- **What the three judge runs show** (0141d1 and 3e0eb4: D&D; 07c755: Seven Meals; all L7, the last 12.5 kyr):
  - A few long routes per era, not a mesh: on average 53-74 stretches (3,000-4,500 km of route) in 5-7 separate pieces over the whole
    world, at most 13-18 pieces in any era.
  - The routes are mostly **salt**, by sea and river. Grain and metal travel between neighbours over short distances (step 2: middling
    goods' median 19-44 km), so their flows rarely share one road long enough to make a route. Fine goods make routes in some eras
    (spices by sea on 07c755 6 kyr ago).
  - Trading towns: 48-159 town-eras over a run; most are **river ports** (66-94%), then market towns. Ports are rare (6 town-eras on 3e0eb4,
    5 of them next to a harbour); **no caravan town appears on any run** (no route leaves farmland for desert or steppe).
  - Steadiness when nudged: the trading towns hold (Jaccard 0.71-0.89 under a ±10% nudge to every land value and cell's people; 0.81-0.99
    under ±10% to the costs). The route stretches hold under the cost nudge (0.78-0.89) but only partly under the land nudge
    (0.68 / 0.73 / 0.57; bar ~0.7). A draft says what to try.
- **Herders' grain (PW-1511).** Option B (herders fetch grain with their own animals) changes almost nothing: herders meet 0.7 / 3.9 / 4.2%
  of their grain need with B against 0.7 / 3.8 / 4.4% today (A). The reason: nearly all herders with a grain lack already know pack
  animals (100% / 86% / 59% of herder snapshots), so B gives them no cheaper way. C (step 3's towns and their merchant quarters) also
  changes almost nothing (0.7 / 3.9 / 4.6%). The shortfall is distance, as step 2 found. **The switch stays off** (`trade_flow.FETCH =
  False`); the measured comparison is in PW-1511 for the coordinator.
- **Flyers' foods (PW-1510).** The record is no longer empty. The aarakocra carry the wild plants of their range (wheat, pulses, alliums,
  oil seeds, beans, squash, tree fruit, vine, ...) to farming neighbours where those plants neither grow wild nor are known, in 21 / 21 / 23
  of the 26 eras. No flying people knows a crop on these runs, so every entry comes from wild plants.
- **Where Daniel sees it.**
  - Globe: Overlays > **Trade routes** (link `?trade=routes`). Lines are coloured by goods (food gold, salt white, metal copper, fine goods
    violet, raw goods green) and wider for a bigger share. Rings mark the trading towns (port blue, caravan town orange, river port cyan,
    market town white). A line under the box counts the era's stretches and towns. Hover a ring: "river port of the X (place, ~N people):
    salt, grain pass through, by river; a merchant quarter of the Y". The overlay follows the time slider in 500-year steps over the last
    ~12,500 years. The first time for a run takes about a minute.
  - Peoples workbench > **Culinary brief** > pick a people and one culture > **Show the brief** > **Trade: goods**: a new **Trading towns**
    table lists the culture's trading towns at the chosen time (kind, people, share, goods passing, merchant quarters).

## What was built

**Predecessors.** `trade_flow._walk` now also returns, per cell, the edge it was reached by. `flows_at` hands every round's deliveries
(taker cell, amount, giver and taker culture) to `trade_routes.Loads`. Nothing in the allocation changed: `flows_at(..., routes=False)`
returns the same flows (test).

**Routes** (`Loads.finish`). Each delivery between two cultures adds its amount to every edge on its way back to its source (`_path_load`,
numba). Per group of goods, an edge's load is divided by the group's traded volume between cultures, the world over, that frame. An edge is
a route when its largest share is `ROUTE_SHARE` = 2% or more (a JUDGEMENT: design1.md's "flows above a share of the world's total" gives
no number). The edge's group is the one with that share, its mode the one carrying most of it. Deliveries inside one culture's land count
for its towns' throughput but draw no route.

Chosen among four rules on 3e0eb4 (every third frame, the same nudges as below):

| Rule | stretches per era | pieces | land nudge J | cost nudge J |
|---|---|---|---|---|
| per-flow trunk: each flow over 1% of its group, the edges carrying half of it | 0-257 | 0-12 | 0.41 | 0.72 |
| all deliveries, 0.5% | 209-1,175 | 14-103 | 0.56 | 0.80 |
| all deliveries, 1% | 20-465 | 2-33 | 0.50 | 0.84 |
| **all deliveries, 2% (kept)** | 0-163 | 0-11 | 0.73 | 0.85 |

**Trading towns** (`Loads._hubs`). The ledger's biggest town or city per cell at the era (`towns_at`, the ledger's own town size) on a route
cell. Kind, first match: port (a sea route touches it), caravan town (a land route from its farmed cell into an unfarmed Koppen B cell, and its
culture knows `pack_animals`), river port (a river route touches it), market town. Each lists its leading goods (share of each good's volume
passing), its modes, and its merchant quarters.

**Merchant quarters.** `QUARTER_SHARE` = 0.25 (a JUDGEMENT; Curtin gives the institution, not a share). `derive` runs the frames oldest
first and passes each frame's quarters to the next; `_Frame` sets the toll to zero on edges entering the host culture's land from the
merchants' land (`QUARTERS = True`).

**PW-1511 B** (`FETCH`, default False). For grain, land cells carried by a herding culture (herding is its biggest way of life) and one
cell beyond them cost a pack animal's rate (with hills), tech or not. Other goods keep their costs (test).

**PW-1510** (`flyer_foods`). A flying trading culture's crops are those it knows plus those growing wild on its own cells (`crop_wild`).
Targets: land in its range and one ring out where a trading, farming, non-flying culture lives and the crop is neither known nor wild.
Each entry says `from`: known or wild.

**Doc.** Per frame `routes` ([cell a, cell b, share, group, mode]), `hubs`, `quarters`, `quarter_edges`, `volume`. The server's cache key
moved with `trade_flow.VERSION` = 2. `culture_view` rows carry `hubs`.

## Judge

Runs: 0141d1 (D&D, world 899985), 3e0eb4 (D&D, world dba204), 07c755 (Seven Meals, world 899985); 26 frames each, 12.5 kyr ago to now.
Baseline: main c2792e05 (step 2), which has no routes or towns. Each cell below gives 0141d1 / 3e0eb4 / 07c755.

**Routes by era** (stretches, route km at ~60 km a stretch, pieces; the leading groups; the modes):

| Era | 0141d1 | 3e0eb4 | 07c755 |
|---|---|---|---|
| 12 kyr | none | none | none |
| 9 kyr | 5 (300 km), 1; fine goods; land | 47 (2,800 km), 4; food 45; sea 44 | none |
| 6 kyr | 121 (7,300 km), 16; salt 115; sea 61, river 33, land 27 | 296 (17,800 km), 12; salt; sea 210, land 75 | 128 (7,700 km), 12; fine goods 67, salt 58; sea 98, river 28 |
| 3 kyr | 81 (4,900 km), 10; salt 73; sea 62, river 17 | 163 (9,800 km), 8; salt; sea 129, river 33 | 52 (3,100 km), 8; salt 42; sea 27, river 20 |
| now | 17 (1,000 km), 2; salt; sea 13, river 4 | 40 (2,400 km), 7; salt; river 34 | 23 (1,400 km), 4; salt; sea 15, river 5 |
| mean over 26 eras | 53, 6.5 pieces (max 18) | 74, 5.1 (max 13) | 58, 7.2 (max 16) |

The design asked for one or a few trunk routes per landmass per era, not a mesh: the model gives 5-7 pieces for the whole world on average.
Routes thin out towards the present, probably because the traded volume spreads over more, shorter flows as towns multiply (the 2% bar is
a share of a growing total); this was not checked further.

**Trading towns** (town-eras over the run): 48 / 148 / 159; river ports 45 / 127 / 108, market towns 3 / 15 / 51, ports 0 / 6 / 0,
caravan towns 0 / 0 / 0. Ports next to a harbour (the cell or a neighbour, harbour ≥ 1): 5 of 6 on 3e0eb4. With a merchant quarter:
19 / 80 / 154 town-eras; toll lifted on 0-1,800 border edges per era.

**Stability** (every third frame; Jaccard against the unnudged run, mean over frames, minimum in brackets):

| Nudge | route stretches | trading towns (cell, kind) | top-5 flows (step 2's metric) |
|---|---|---|---|
| every land value and cell's people × U(0.9, 1.1) | 0.68 (0.21) / 0.73 (0.08) / 0.57 (0.19) | 0.83 / 0.89 / 0.71 | 0.86 / 0.86 / 0.86 |
| each mode factor, L and toll × U(0.9, 1.1), seed 2 | 0.89 / 0.85 / 0.85 | 0.87 / 0.99 / 0.93 | 0.95 / 0.95 / 0.95 |
| the same, seed 3 | 0.89 / 0.89 / 0.78 | 0.96 / 0.99 / 0.81 | 0.94 / 0.93 / 0.94 |

The land nudge moves which culture carries a cell (the biggest trading culture there), so borders, tolls and the ways shift; a hard 2%
cut then drops or adds whole stretches. → draft `draft-trade-routes-land-nudge.md`.

**It changes nothing in step 2's flows when the quarters are off**, and little when on: top-5 (giver, good) per culture against option A
(no quarters, no fetch): quarters on 0.999 / 0.999 / 0.997; fetch on 1.000 on all three.

**Herders' grain** (herder culture-frames with a grain lack ≥ 0.05, herding their biggest way of life; share of the lack met by other
cultures):

| Option | 0141d1 (603 snapshots) | 3e0eb4 (43) | 07c755 (70) |
|---|---|---|---|
| A, today (step 2) | 0.7% | 3.8% | 4.4% |
| B, own animals (`FETCH`) | 0.7% | 3.9% | 4.2% |
| C, step 3's towns and quarters | 0.7% | 3.9% | 4.6% |
| B + C | 0.7% | 4.1% | 4.5% |
| herders getting any grain from others (A) | 10% | 53% | 23% |
| met where some arrives (A) | 7% | 7% | 19% |
| herder snapshots already knowing `pack_animals` | 100% | 86% | 59% |

Step 2 reported 0.5 / 3 / 5% for A with its own herder count; the definitions differ slightly. Khazanov (R§2) says nomads always need farm
grain; no source gives a share, so this is judged as plausible or not, and 1-5% met is not. B would help only herders without pack animals,
and they are few or far from farmland. Neither B nor C closes the gap; what closes it is a decision about the herders' distance to farmland
(where herders live in the history) or about grain's fall-off length for herders driving their own herds, both beyond this lane.

**Flyers' foods** (eras with a record: 21 / 21 / 23 of 26). All entries are the aarakocra's, all from wild plants. Most frequent crops
(culture-eras): 0141d1 beans 136, squash 132, sorghum 127, tree fruit 124, wheat 121; 3e0eb4 alliums 150, wheat 148, pulses 144, oil seeds
139, pseudograin 137; 07c755 oil seeds 133, beans 131, alliums 129, tree fruit 128, vine 123. The takers are the trading, farming,
non-flying cultures in and next to the aarakocra's range. Only the aarakocra carry foods on these runs.

**Runtime.** Derive with routes: 56-60 s (D&D) and 90 s (Seven Meals) per run at L7 with three runs at once, 2 numba threads each; step
2 measured 51-70 s the same way. The server's first call for a run takes about a minute; then each era is a small fetch.

## Not done here

- No per-cell `trade_load` layer: the route stretches and the towns' throughput carry it.
- No caravan towns on these runs; the rule is tested on a hand-made world.
- Polanyi's port of trade (an administered enclave) is not told apart from a port.

## Drafts

- `draft-trade-routes-land-nudge.md`: route stretches hold 0.57-0.73 under the land nudge (bar ~0.7).
- `draft-trade-routes-mostly-salt.md`: the routes are nearly all salt; grain and metal make none, no caravan towns.
