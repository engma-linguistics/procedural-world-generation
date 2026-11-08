# Trade step 3c: market pools, worn ways, allocation to the end (PW-1514, PW-1515, PW-1519; lane 218)

Step 3b: [step3b.md](step3b.md). Code: `planet/lineages/trade_flow.py` (`_Frame.pools`, `_exchange`, `_Ledger`, `_Frame.set_wear`,
`POOL`, `TRUNK`; doc version 5), `planet/lineages/trade_routes.py` (`Loads.add` traces each round as it comes, `Loads.traffic`). Tests:
`tests/test_trade_routes.py` (three new). Screenshot: [step3c_routes_3e0eb4.png](step3c_routes_3e0eb4.png) (3e0eb4, the present, the
land-heavy face at 45° N 47° E: 164 stretches, 41 trading towns; port 3, river port 35, market town 3).

Baseline everywhere: **main c2e54f2b** (trade code as lane 216b's merge abb61a0c), judged with the same script on both codes:
[step3b/judge.py](step3b/judge.py) (unchanged but for `TF_<NAME>=value` environment overrides of trade_flow's constants, used to judge the
switches). Runs 0141d1, 3e0eb4 (D&D) and 07c755 (Seven Meals), L7, 26 frames from 12.5 kyr ago; 1 thread per run, 3-6 jobs at once.

## In plain words

- **No ticket's bar is fully met.** One part of one bar is: food routes now appear in most eras that have trading towns, on all three
  runs.
- **Market pools (PW-1514), kept.** Daniel's D64 ruling makes towns the hubs, so each town now runs a market for the land around it.
  - Every cell joins its nearest town if the way there is at most one and a half cell spacings (60-80 km at L7).
  - Inside the pool, spare goods meet the pool's own wants first. That is local market trade, with no road drawn.
  - Only what is left over leaves, from the town, or is fetched, to the town.
  - So a cell on the edge between making a little too much and a little too little now moves its pool's total a little. Before, it
    switched a source on or off.
  - Effects:
    - **Food routes** are now in 12 / 12 / 15 of the 14 / 18 / 18 eras with trading towns (main: 7 / 3 / 12 of 14 / 16 / 18). The food
      bar is met.
    - Grain now reaches towns from the land around them, and more towns trade: 18 eras have trading towns on 3e0eb4 (main 16).
    - **Steadiness bar not met.** Under the land nudge the routes keep 0.64 / 0.60 / 0.50 of themselves against a bar of about 0.7
      (main 0.59 / 0.70 / 0.49). That is better on 0141d1, the same on 07c755, and worse on 3e0eb4.
    - Under the cost nudges they keep 0.82, 0.77 / 0.68, 0.73 / 0.72, 0.65 (main 0.82, 0.74 / 0.81, 0.71 / 0.71, 0.68). They are not
      worse than main on 0141d1. On 3e0eb4 (seed 2, by 0.14) and 07c755 (seed 3, by 0.04) they are worse, so the cost-nudge numbers are
      **not** kept.
    - The routes became a bigger mesh: 536 / 327 / 530 stretches an era (main 410 / 281 / 359).
  - **Why pooling did not reach 0.7.**
    - Towns are sparse in the older eras (1,353 town cells of ~51,000 settled cells on 3e0eb4 6 kyr ago), so most cells there are in no
      pool and still flip as before.
    - A pool's own net (spare goods minus wants) can still cross zero.
    - The route bar is a hard cut at 5% of a good's carried volume, applied to hundreds of stretches. Any change in volume moves the
      stretches near the cut.
- **Worn ways (PW-1515), built and measured, left switched off.** A land stretch that carries traffic gets cheaper for every good, by up
  to 40%: Tobler's hiking function says that off a path one walks at 3/5 of the pace on it. Helbing et al. 1997, "frequently used
  trails become more developed, making them more attractive", gives the mechanism.
  - Each frame walks, wears the ways its goods took, and walks again: at most 3 times, stopping early once the wear changes by under 2%.
    Half of an era's wear carries over to the next era.
  - **It does not make trunks.** Stretches: 531 / 331 / 533 an era (pools alone 536 / 327 / 530). It makes the routes **less** steady:
    land nudge 0.65 / 0.51 / 0.48 (pools alone 0.64 / 0.60 / 0.50). It also doubles the derive time.
  - Why: most route stretches run by river and coast, and those are not worn. Also, the mesh is the union of 20 goods' own top roads, and
    making shared land roads cheaper does not merge goods that come from different sources and go to different takers. The positive
    feedback also amplifies small differences between two nudged worlds.
  - The switch `TRUNK` stays off. **The trunk bar ("a few trunks per landmass") is not met.**
- **Allocation to the end for every good (PW-1519): not met; the allocation is unchanged (grain to the end, the rest 3 rounds).**
  - *Every good run to the end with the existing rounds:* rounds reach the 400 cap for timber, firewood, livestock, spices and gems; the
    mean is 220-240 rounds a good. That is 306 s for 8 frames of 3e0eb4 (pools on) and 213 s for 3 frames (pools off), against a budget
    of ~3 minutes for the whole 26-frame derive.
    - It also floods the routes: 2,400-3,100 stretches an era, 1,300-1,800 of them fine goods. Fine goods fall off over 1,200 km, and run
      to the end they travel far.
  - *216b's suggestion, each cell's 8 best distinct sources from one walk:* built as a single global pass, each taker moving to its next
    live source within the same pass and walked for again only when all 8 are dry.
    - That walk takes 1.6-1.9 s against 0.06 s for the plain walk on 3e0eb4: about 30 times.
    - Goods still need many walks: up to the cap of 50 for timber, firewood, livestock, spices and gems; 13 for grain.
    - Where demand far exceeds supply, whole rings of sources run dry together, and a taker's 8 go in one pass.
    - One frame took 615 s. Not kept.
  - A different allocation (a shared walk in which an emptied source stops spreading), or a decision on how far fine goods should be
    drawn, is needed. See the draft below.
- **Herders' grain met** (mean per snapshot): **3.3% / 12.0% / 12.3%** (main 3.4% / 13.0% / 12.3%). Grain unmet, all eras: 0.53 / 0.48 /
  0.34 (main 0.52 / 0.48 / 0.33). Pooling moves grain between cells inside a pool, so a little of what used to cross from farmers to
  nearby herders is now market trade inside the herders' own pool.

## Judge

Each cell: 0141d1 / 3e0eb4 / 07c755. "Pools" is this lane's final code; "pools + worn ways" is the same with `TF_TRUNK=1`.

| | main c2e54f2b | pools (final) | pools + worn ways |
|---|---|---|---|
| derive, s (1 thread, 3-6 jobs at once) | 40 / 38 / 64 | 42 / 42 / 66 | 94 / 89 / 154 |
| stretches per era (mean) | 410 / 281 / 359 | 536 / 327 / 530 | 531 / 331 / 533 |
| pieces per era (mean, max) | 20.4 (39) / 11.2 (20) / 19.9 (32) | 22.9 (46) / 15.1 (31) / 26.3 (50) | 23.6 (43) / 15.5 (33) / 24.7 (48) |
| eras with trading towns | 14 / 16 / 18 | 14 / 18 / 18 | 14 / 18 / 18 |
| ... with food routes | 7 / 3 / 12 | **12 / 12 / 15** | 12 / 14 / 15 |
| ... with metal / fine goods / raw goods routes | 11, 14, 14 / 9, 14, 16 / 12, 18, 18 | 11, 14, 14 / 9, 16, 18 / 14, 18, 18 | 11, 14, 14 / 10, 16, 18 / 14, 18, 18 |
| ... with two kinds besides salt | 14 / 14 / 18 | 14 / 18 / 18 | 14 / 18 / 18 |
| land nudge, route stretches (mean, min) | 0.59 (0.24) / 0.70 (0.49) / 0.49 (0.15) | 0.64 (0.32) / 0.60 (0.28) / 0.50 (0.15) | 0.65 (0.43) / 0.51 (0.30) / 0.48 (0.10) |
| land nudge, load-weighted | 0.62 / 0.67 / 0.45 | 0.63 / 0.54 / 0.50 | 0.64 / 0.48 / 0.48 |
| land nudge, trading towns | 0.44 / 0.52 / 0.62 | 0.52 / 0.51 / 0.57 | 0.51 / 0.50 / 0.54 |
| cost nudge seed 2 / seed 3 | 0.82, 0.74 / 0.81, 0.71 / 0.71, 0.68 | 0.82, 0.77 / 0.68, 0.73 / 0.72, 0.65 | 0.81, 0.76 / 0.73, 0.69 / 0.71, 0.63 |
| herders' grain met (mean per snapshot) | 3.4% / 13.0% / 12.3% | 3.3% / 12.0% / 12.3% | 3.4% / 12.0% / 12.4% |
| grain unmet, all eras | 0.52 / 0.48 / 0.33 | 0.53 / 0.48 / 0.34 | 0.53 / 0.48 / 0.34 |
| grain allocation rounds (mean, max) | 55, 148 / 59, 139 / 58, 159 | 41, 102 / 41, 86 / 41, 106 | 43, 100 / 43, 89 / 42, 114 |
| trading town-eras: port, caravan, river port, market | 33, 12, 740, 75 / 23, 19, 425, 34 / 65, 23, 825, 102 | 74, 19, 1175, 80 / 66, 29, 618, 79 / 138, 40, 1064, 230 | 76, 19, 1146, 88 / 60, 57, 615, 96 / 138, 39, 1082, 239 |

How the wear's half-point was set (`WEAR_HALF` = 0.2% of the frame's carried goods over one stretch, JUDGEMENT): on 3e0eb4 (frames 134,
140, 146) the busiest 1% of carried stretches carry 0.22-0.46% of the frame's carried goods each, and the busiest one 0.7-1.4%. In
people's worth the traffic grows ~14 times from 6 kyr ago to the present, so wear is measured as a share of the frame's traffic, not as a
fixed amount.

## What changed in the code

- `_Frame.pools()`: a walk from every settlement-ledger town cell held by a trading carrier, with bulk goods' costs and tolls. A cell
  joins the town that reaches it at least cost, when the way is at most `POOL_HOPS` (1.5) spacings. Christaller and Skinner
  (review1.md section 5): market areas tile the land and their size follows settled density, so the nearest town takes the cell.
- `_exchange` (per good, the old body of `flows_at`):
  - the pool's spare goods (each cell's biggest surplus x its people) meet the pool's wants first, every want in the same share; these
    deliveries are recorded at the town with no road (`Loads.add` with no edges), and counted as market trade between cultures;
  - what is left of a pool becomes one source at the town, its surplus per head of the pool as the walk's starting supply;
  - a pooled want asks at its town; the way on from the town to the cell adds its km, mode and borders to the flow;
  - the givers of a pooled source are split by each culture's share of the pool's spare goods (`_Ledger.record`).
- `Loads.add` traces each round's deliveries along the walk's edges as they come (the routes no longer keep a copy of the walk's edges per
  round), and `_Frame.rewalk` no longer copies them.
- `_Frame.set_wear`, `Loads.traffic`, the loop in `flows_at` and `derive`'s `last_wear`: the worn ways, behind `TRUNK` (off).
- `trade_flow.VERSION` = 5 (the server's cached trade docs are remade); the doc's constants list the new switches.

## Sources fetched this lane

- Helbing, D., Schweitzer, F., Keltsch, J. & Molnár, P. 1997, "Active Walker Model for the Formation of Human and Animal Trail Systems",
  Phys. Rev. E 56: 2527-2539 (https://arxiv.org/abs/cond-mat/9806097, PDF read). "frequently used trails become more developed, making
  them more attractive, whereas rarely used trails vanish again"; pedestrians "prefer to use existing trails, but they build a new
  shortcut, if the relative detour would be too large"; a trail's clarity saturates at a maximum (their eq. 15); the result is a
  "minimal detour system".
- Tobler's hiking function (Wikipedia, https://en.wikipedia.org/wiki/Tobler%27s_hiking_function, citing Tobler 1993, NCGIA Technical
  Report 93-1, from Imhof 1950): "For off-path travel, this value should be multiplied by 3/5".

## Bars changed mid-lane (Daniel's feedback, relayed by the coordinator on 2026-11-08)

- **The dense web is not a fault.** Local exchange really was a dense web. Long-distance trade was a branching network that carried
  high-value goods (the Silk Road as a river with its tributaries). "Thin the mesh toward a few trunks" is **dropped** as a bar, and no
  stretches are to be cut to hit a count.
- **Shared roads stay only if they help** steadiness, or make the long-haul network read as a network, with a source. Measured here,
  worn ways did neither (table above), so `TRUNK` stays off.
- **New overlay task (not started in this lane, which reached its hand-off budget):** draw two layers without hiding the local web.
  - The **long-haul network**, drawn by default: precious goods and anything carried more than about 500 km.
  - **Local exchange**, a toggle: bulk and middling goods over short distances.
  - A suggested cut, from this repo's own measurements: step3b.md found grain's cross-culture deliveries at a median of 1-2 stretches,
    with 90% under 8 stretches. Eight stretches is about 480 km at L7 (60 km cells, 1.3 path factor). So ~500 km leaves nearly all
    overland grain local. review1.md R§6 gives overland grain 100-200 km at most, and tin and fine goods 1,000 km and more.
- **The bars that remain:**
  - PW-1514: land-nudge Jaccard ~0.7 or more, with the cost nudge no worse than main;
  - PW-1515: food routes in most eras with towns;
  - PW-1519: every good seeks until none is left, within ~3 minutes per run.
- **No new goods.** The coming craft-goods ticket (silk, cloth, dyes, incense, glass, silver, weapons) runs after this merge.

## Status

- PW-1514: not done. Land nudge 0.64 / 0.60 / 0.50 against ~0.7; cost nudges lower than main on 3e0eb4 and 07c755. Pools are kept for
  the food result (PW-1515) and as the hub rule D64 asks for.
- PW-1515: food routes in most eras with towns: **met** (12/14, 12/18, 15/18). Kinds besides salt: kept (14/14, 18/18, 18/18). The
  trunk-count bar is dropped (above). The new long-haul / local overlay split is not built, so the ticket stays open for it.
- PW-1519: not done. Every good run to the end needs hundreds of rounds or dozens of 8-best walks; neither fits ~3 minutes. Draft below.
