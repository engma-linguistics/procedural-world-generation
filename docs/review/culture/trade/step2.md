# Trade step 2: goods move between neighbours (PW-1503, lane 213)

Design: [design1.md](design1.md) step 2. Sources: [review1.md](review1.md) (R§n below). Step 1: [step1.md](step1.md).
Code: `planet/lineages/trade_flow.py` (new), `planet/lineages/trade.py` (the ledger, now version 2), served by
`GET /api/trade?run=…&culture=…&flows=1` (`planet/server.py::trade_flow_doc`). Tests: `tests/test_trade_flow.py`.

## In plain words

- **What's new.** Goods now travel. Before this lane (current main), the model only said what each culture had spare and what it
  lacked. Now each spare good spreads from the land that makes it to the land that lacks it, and it fades with the cost of carrying
  it there and then. The cheapest way open at that time sets the cost: on foot, by pack animal, by cart or road, by river boat
  (cheaper downstream), along the coast, over open sea, or, for light goods only, on the wings of a flying people.
- **What it's built from.** The cost ratios come from the review: carrying by land costs about 28 times sea and 8 times river
  downstream (ORBIS, R§6). How fast a good fades depends on how much value it packs per kilo. Grain fades within ~100-250 km
  overland, obsidian-like goods within a few hundred km, and tin, spice and gold go thousands of km. Each of these lengths has a
  source.
- **Who trades with whom.**
  - Each culture gets a list of where every good it lacks comes from (which neighbour, how far, by land, river, sea or air), and where its own spare goods go.
  - Each exchange gets a kind: gifts between forager bands, barter, a market, merchants, or tribute.
  - Borders cost a toll of about 10% of the goods' value. A tolerant culture charges less. A war that century closes the border.
- **Peoples by body** (Daniel's ruling D65):
  - Flyers carry light goods over anything.
  - Sea peoples carry goods over their own water as cheaply as ships, and trade with land peoples at the shore.
  - Mining kinds trade from their holds as towns do.
  - Dragons take food and treasure as tribute from the peoples on their land, and their kobolds trade the realm's spare goods.
  - Giants trade or take tribute by kind: hill, stone, cloud and storm giants trade; frost and fire giants take tribute.
- **It matches the review where it should.** On the three judge runs (two D&D, one Seven Meals):
  - **Grain overland:** half of it goes under ~100-115 km and 90% under ~185-240 km (review: ~100-200 km overland). Grain goes far only by water. By sea the median is 350-410 km and the longest 10% go over 900-1,400 km. 65-84% of bulk goods move by river or sea.
  - **Middling goods** (salt, metals, obsidian-like): 89-96% of the volume stays within 300 km (review: obsidian's ~300 km supply zone).
  - **Spices** cross continents, 92-99% of them by ship, with a median of 1,500-3,000 km. **Gold** travels a median of 500-1,200 km.
  - Foragers buy at most half their grain need (review: ~50%, Kitanishi). In two of the three runs, the share they buy falls with distance.
- **Where it falls short.**
  - **Herders:** on average only 0.5-5% of their grain need is met (6-19% where any grain reaches them). The herders in these worlds live hundreds of km from farmland, and grain fades fast overland. This is a draft for Daniel.
  - **Tin:** it travels 1,000+ km in 25% and 35% of its volume on the two D&D runs, but only 2% on Seven Meals. In these worlds the few tin deposits sit mostly under dragon realms, or next to the bronze users who take it first.
  - **Flyers' foods:** no flying trading people knows a crop in these runs, so the record of foods flyers carry to new regions is empty (a draft).
- **It is stable.** A random ±10% nudge to every land value and every cell's people keeps 84-85% of each culture's top-5 (giver, good) pairs. A ±10% nudge to every cost factor, fall-off length and toll keeps 92-95%. The design's bar was ~0.7.
- **It is fast:** 50-70 s for a whole L7 run (26 frames) while three judges ran at once (40-55 s alone), plus the polities and gods docs it reads (cached). The doc is ~2.4 MB.
- **It changes nothing in the history** (D63 A). The goldens do not move. A culture's bought food (`trade_flow.food_bought`) is kept in a form step 4d can read in place of `ladder.TRADE_CAP` and `BARTER_CAP`, once trade feeds back.
- **Where Daniel sees it:** Peoples workbench > **Culinary brief** > pick a people and **one culture** > **Show the brief**. In the **Trade: goods** panel:
  - the Surplus table has a **goes to** column;
  - the Lacks table has a **comes from** column, with the two biggest partners per good: name, km, by land, river, sea or air, and the kind (hover for the share);
  - below them, a **Trading partners** table: people supplied each way, and the main kind.
  The first time for a run takes about a minute.

## What was built

**The walk** (`trade_flow._walk`, numba Dijkstra). There is one walk per good per frame, from all of the good's surplus cells at once,
as `salt_reach._spfa` walks from all salt. A source starts at cost −L·ln(surplus), so the supply reaching a cell, exp(−cost/L), is the
best of surplus × exp(−carry/L) over all sources. That is Renfrew's exponential fall-off (R§1). The walk keeps the origin, the km, the km
per mode and the borders crossed.

**Shared supply.** A source gives at most its surplus, in people's worth, like for like as in the ledger. Its best-supplied takers are
served first (`_allocate`). A taker cut short because its source ran out looks for the next-best source, at most 3 rounds (`ROUNDS`, a
compute bound). Without this sharing, every far taker got a copy of the same surplus. Ornaments then went a median 1,500 km at 12.5 kyr
ago; with it, they go 216 km.

**Costs per km, pack animal = 1** (`trade_flow.py`, each with its source):

| Mode | Factor | Opens with | Source |
|---|---|---|---|
| on foot (porter) | 3 | always | JUDGEMENT in Cheng 2024's porter/mule 7.5 (design1.md) |
| pack animal | 1 | `pack_animals` | ORBIS donkey/camel 0.028 |
| cart (flat), road (own land) | 1.25 | `wheel` where hills < 0.5; `roads` | ORBIS wagon 0.035 |
| hills (porter, pack) | ×2.12 at full hills/peaks, linear | | Cheng 2024: mule hills 0.452 / flat 0.213 |
| river down / up | 0.121 / 0.243 | `canoes`, river_nav ≥ 1 on both cells | ORBIS 0.0034 / 0.0068 |
| coast by canoe | 0.243 | `canoes` on the land beside it (and 2 cells along) | JUDGEMENT: paddled, as upstream |
| coast by ship, open sea | 0.036 | `sails`/`plank_boats` (coast); `navigation` anywhere or ocean ships (open sea) | ORBIS 0.001 |
| a sea people's own water | 0.036 | always | D65 A |
| flyers (precious goods only) | 1 | a flying trading people on either cell, over anything | JUDGEMENT (D65 A: no source) |

A cell's carrier is the biggest trading culture living on it; on sea cells it is a sea people. Ice sheets are closed to ground carriers.
The land-to-sea step costs the mean of the two cells' factors (no harbour gate; step 3 is where ports appear).

**Fall-off length L per value class** (cost-km, supply left after carrying = exp(−cost/L)):
- **bulk 290.** Cato: moving a mill 75 miles cost 39% of its value (Adams 2007, R§6), ~116 km by cart: L = 116 × 1.25 / −ln 0.61.
- **middling 433.** Anatolian obsidian (R§1): relay keeping 50% per hop with villages ~100 km apart fits the 700-800 km tail. On foot:
  L = 100 × 3 / ln 2. Salt's old cap was 450 cost-km.
- **precious 1,200.** Kanesh tin went ~1,200 km by donkey (Dercksen, R§3). This is a JUDGEMENT within design1.md's 1,000-1,500.
- Tin falls off as a precious good (`FALL_CLASS`; R§6 lists tin among the light goods that go thousands of km), though the ledger keeps
  it middling.

**Borders.**
- **Toll.** Entering another culture's cell costs −L·ln(1 − toll). The toll is 10% of value (Kanesh road tolls, Dercksen, R§3) at
  tolerance 0.5 (`TOL_MID`, the median on these runs). It scales by (1 − tolerance)/0.5, capped at 50% (JUDGEMENT). Tolerance comes from
  the gods doc's attitudes read-out.
- **War.** A war between the two cells' polities closes the edge in the century step nearest the frame (`polities.py` "took" records).
  It uses the borders as they stood when the war began (the step before), because the step's own map is drawn after the taking. This
  closes 2-200 border edges per frame on the judge runs. Nothing in `polities.py`, `invasions.py` or `polity_live.py` was edited.

**Kinds** (`kind_of`; a label only, it does not change the physics: R§1, review1.md "what the model takes" 4):
- **tribute:** the taker takes tribute (dragons, frost and fire giants) or rules the giver's polity;
- **gift:** both are mostly foragers (hxaro, R§1);
- **merchant:** a third culture lies between them (mean borders crossed ≥ 1.5), and either knows `trade` and a carrier (caravans or
  ships, R§4-5);
- **market:** either has ≥10% of its people in towns and knows `markets`, or is a mining kind;
- **barter:** everything else.

**Tribute-takers.** A dragon realm, or a frost or fire giant kind, takes grain, herd animals, gold and gems (`TRIBUTE_GOODS`, a JUDGEMENT:
R§5's tribute is grain, cloth and luxuries) from the trading peoples on its own cells, up to its people's worth. Its own surplus goes out
through the walk, labelled `via: kobolds` for dragons.

**Ledger changes (trade.py v2).**
- `GIANT_MODE`: a mode set by hand per giant kind (PW-1507, the lane's lean B). Hill, stone, cloud and storm giants trade; frost and
  fire giants take tribute. This is a JUDGEMENT per kind; kinds not listed keep step 1's rule.
- A mining kind's people want as a town's do, at `ladder.TRADE_CAP` of them (the share of its food a hold buys, the model's own
  placeholder).
- `pairs_at` exposes the per-(cell, culture) surplus and lack.
- No other ledger number moved.

**Flyers' foods** (`flyer_foods`). For each flying trading culture and each crop it knows: the farmed land cells in its range, and one
ring beyond it, where the crop is not known, and the cultures there. Nothing is spread. It is a record for step 4a and the crop spread.

**Outputs** (`derive`, cached under `.godscache/tradeflow-<run>.json`). Per frame:
- flows `[giver, taker, good, share of the taker's people, people supplied, km, carry cost-km, mode, kind, via]`;
- per culture, the share of each good met from its own land elsewhere (`home`), and the share unmet (`unmet`);
- `war_edges` and `flyer_foods`.

`food_bought(doc, culture, ago)` is the step 4d hook.

## Judge (measure only)

Runs:
- 0141d1: D&D, world 899985;
- 3e0eb4: D&D, world dba204;
- 07c755: Seven Meals, world 899985.

All three are L7 with 26 frames (12.5 kyr ago to now). How to read the tables:
- **Volume** is people supplied (share × the taker's people).
- **Distances** are path km, volume-weighted.
- **Tribute is left out of the distance tables**: it is local by construction.
- **Baseline:** current main has no exchange at all, so every number below is new. The comparisons are against the review's sourced
  ranges.

**Distance by value class** (median / 90th percentile km; share of volume within 300 km; share going ≥1,000 km; share by river or sea).
Each cell gives 0141d1 / 3e0eb4 / 07c755.

| Class | median km | 90th pct km | ≤300 km | ≥1,000 km | by water | Review |
|---|---|---|---|---|---|---|
| bulk | 181 / 211 / 235 | 517 / 448 / 556 | 74 / 71 / 65% | 3 / 2 / 3% | 67 / 80 / 80% | grain ~100-200 km overland, far only by water (R§6) |
| middling | 35 / 44 / 19 | 222 / 328 / 147 | 94 / 89 / 96% | 1.5 / 2 / 0.7% | 36 / 46 / 40% | obsidian supply zone ~300 km, axes mostly <200 km (R§1, R§3) |
| precious | 522 / 384 / 613 | 3,462 / 2,142 / 3,261 | 31 / 36 / 26% | 33 / 24 / 35% | 70 / 59 / 69% | tin, jade, beads: 1,000+ km (R§3, R§4) |

**Bulk overland against by water** (median / 90th pct km):

| Mode | 0141d1 | 3e0eb4 | 07c755 |
|---|---|---|---|
| land | 96 / 240 | 113 / 214 | 105 / 184 |
| river | 222 / 431 | 220 / 362 | 245 / 424 |
| sea | 391 / 1,398 | 413 / 1,315 | 347 / 913 |

Grain overland stays in the review's 100-200 km. Every bulk flow of 1,000 km or more goes by water.

**Goods of note:**
- **Spices:** median 1,671 / 2,972 / 1,486 km; 81 / 82 / 59% go ≥1,000 km; 99 / 99 / 92% by sea or river (R§4: pepper by ship).
- **Gold:** median 497 / 1,227 / 824 km.
- **Ornaments (shell beads):** median 606 / 554 / 601 km. At 12.5 kyr ago, when only foragers trade them as gifts: 216 km median, 548 km
  at the 90th percentile (3e0eb4). The review has hxaro partners at 2-200 km and beads from >300 km (R§1).
- **Salt:** median 489 / 540 / 604 km. Salt's lack is written only for land more than 300 km from salt (the brief's walk, step 1), so
  traded salt goes far by construction.
- **Tin:** 25 / 35 / 2% of its volume goes ≥1,000 km; median 89 / 485 / 96 km. This is short of the review's 1,000-4,000 km. Tin is
  held by almost no trading culture (step 1: 0-7 snapshots per run), so it comes from tribute land and the nearest bronze users take
  it first. Seven Meals' tin lies near its users.

**Obsidian-like fall-off** (toolstone supply relative to its source, against path km; no want of edge stone is written, PW-1506):

| km | 0-150 | 150-300 | 300-500 | 500-800 | 800-1,200 | >1,200 |
|---|---|---|---|---|---|---|
| 6 kyr ago (0141d1 / 3e0eb4 / 07c755) | 0.84 / 0.88 / 0.81 | 0.72 / 0.76 / 0.73 | 0.61 / 0.61 / 0.65 | 0.52 / 0.45 / 0.59 | 0.46 / 0.38 / 0.52 | 0.27 / 0.30 / 0.30 |

The fall-off is steady, with no step: Renfrew's shape, exponential in cost. In km it is slower than the Anatolian relay on foot, which
keeps 0.4% at 700-800 km. By 6 kyr ago most carriers have pack animals and river boats, and the curve is in cost, not km.

**Herders' grain** (herder snapshots with a grain lack ≥ 0.05; R§2, Khazanov: herders need farm grain):

| | 0141d1 | 3e0eb4 | 07c755 |
|---|---|---|---|
| snapshots | 603 | 43 | 70 |
| get some grain from another culture | 10% | 54% | 23% |
| all of it from farming cultures | yes | yes | 21 of 23 |
| mean share of their lack met | 0.5% | 3% | 5% |
| met where some arrives, by its mean km: 60-150 / 150-300 / >300 km | 1 / 9 / 6% | 6 / 8 / 6% | — / 15 / 19% |

This is the weak point. 0141d1's herders are mostly goliaths, and its present frame shows why:
- 4 of the 6 biggest goliath herder cultures have no grain within reach at all;
- the biggest one's grain comes from a median 4,000 km.

The world's grain surplus, 424 M people's worth, is twice the world's lack. So the grain exists; it is too far from the herders.
→ draft `draft-trade-herders-grain-far.md`.

**Foragers' farm food** (R§2, Kitanishi: at most about half, falling with distance):
- The most any forager culture buys is 0.50 / 0.46 / 0.29 of its people, and none buys more than half.
- The share of the lack met falls with the mean km of the grain:

  | Mean km of the grain | 0141d1 | 3e0eb4 | 07c755 |
  |---|---|---|---|
  | 60-150 km | 0.48 | 0.48 | 0.43 |
  | 150-300 km | 0.43 | 0.40 | 0.39 |
  | >300 km | 0.50 | 0.26 | 0.26 |

  It falls in two runs. 0141d1 is the exception: its far flows are coastal foragers fed by sea.
- Kitanishi's 1.5 h against 4-5 h walks are inside one ~55 km cell, so the model cannot resolve them.

**Sea against land.** Sea carries bulk 3-4 times further than land, and middling goods ~2-9 times further at the median (tables above).
Flyers' air mode carries 211 / 328 / 490 precious flows over the run.

**Kinds** (flows over the run): tribute 19.4k / 17.2k / 19.7k, barter 7.6k / 6.0k / 7.3k, gift 1.9k / 3.9k / 2.0k,
market 1.3k / 3.9k / 0.8k, merchant 0.9k / 0.7k / 0.6k.

**Stability** (top-5 (giver, good) per culture-frame, Jaccard against the unnudged run; every third frame, ~1,500-1,700
culture-frames):

| Nudge | 0141d1 | 3e0eb4 | 07c755 |
|---|---|---|---|
| every land value and cell's people × U(0.9, 1.1) (step 1's nudge) | 0.849 | 0.846 | 0.843 |
| each mode factor, L and the toll × U(0.9, 1.1), seed 2 | 0.942 | 0.939 | 0.947 |
| the same, seed 3 | 0.928 | 0.923 | 0.935 |

design1.md's bar was ~0.7 (a judgement). The design also asked for a reseeded run; that needs a new history run, which was not made here.

**Runtime:**
- derive 51.6 / 50.7 / 69.6 s per run at L7, while three judges ran at once at 2 numba threads each (40-55 s run alone);
- plus the polities doc (30-65 s if it isn't cached) and the gods doc (~20 s), both disk-cached by the server;
- the doc is 2.4 MB.

## Not done here

- The workbench **Trade tab** of the ticket: the culture panel in the brief tab carries the same content (comes from / goes to, partners,
  kinds) for one culture. A whole-run tab is left to step 3, where the routes give it a map.
- The brief's salt reach still uses `salt_reach.py`. Moving the brief onto this pass's salt is step 4a's job (PW-1505).
- Money (`commodity_money`, `coinage`) does not lower the border toll: no source gives an amount.
- Step 3 (routes) needs the walk's predecessors. The walk can return them cheaply; they are not kept in the doc.

## Drafts

- `draft-trade-herders-grain-far.md`: herders meet 0.5-5% of their grain need (needs-decision).
- `draft-trade-flyer-foods-empty.md`: no flying trading people knows a crop on the judge trees, so the flyer food record is empty.
