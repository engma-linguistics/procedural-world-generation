# Trade step 3b: routes of every kind, caravan towns, steadier routes (PW-1515, PW-1514; lane 216)

Step 3: [step3.md](step3.md). Code: `planet/lineages/trade_routes.py` (`Loads.finish`, `Loads._hubs`), `planet/lineages/trade_flow.py`
(doc version 3, `last_routes`). Tests: `tests/test_trade_routes.py`. Screenshot: [step3b_routes_3e0eb4.png](step3b_routes_3e0eb4.png)
(3e0eb4, 3,000 years ago: 597 stretches, 37 trading towns; port 2, caravan town 1, river port 27, market town 7).
Baseline everywhere: main cb8374b0 (lane 214's step 3), judged with the same script as the new code.

## In plain words

- **Why the routes were nearly all salt.** A stretch counted as a route when it carried 2% of its *group's* trade (food, salt, metal, fine
  goods, raw goods). Two things made that bar unfair to everything but salt:
  - **Metal mostly never travels.** 65-84% of the metal that changes hands between cultures goes between two cultures living on the same
    cell, so it crosses no road at all, yet it counted in the total each road was measured against.
  - **Rare goods drown in common ones.** Tin is a route good in every source (Kanesh: ~1,200 km by donkey; Uluburun), but it was measured
    against copper's and iron's volume, 20-60 times its own. The same held for spices against ornaments and gold.
  - Salt has few sources and is lacked only far from them, so its deliveries share long roads; it passed the bar and little else did.
- **What changed.** A stretch is now measured against **one good's** volume that actually travels (deliveries that cross at least one
  stretch), and the bar is 5% of that (2% per good drew a mesh of 565-931 stretches an era). A stretch over half the bar is a route too
  when it **was one the era before** (roads and the towns on them persist: Bleakley & Lin 2012 on portage towns; Dalgaard et al. 2022 on
  Roman roads) or when it **continues a route** (one road, not broken bits).
- **Caravan towns now appear** (12 / 19 / 23 town-eras; none before). The old rule wanted a farmed town cell beside an *unfarmed* desert
  or steppe cell; on these worlds almost every dry cell beside a land route has some farming, and no town stood so. Caravan routes ran
  through farmed oases (dates and grain, review1.md section 4), so the rule now asks for a land route from the town into desert or steppe,
  farmed or not, and pack animals.
- **Result against the bars.**
  - Every era with trading towns now shows at least two kinds of goods besides salt (14/14, 14/16, 18/18; before 6/14, 0/14, 13/18).
    Metal routes (mostly tin and iron) appear in 9-12 eras (before 0-1), ports in 23-65 town-eras (before 0-6).
  - **Food: bar not met.** Food routes appear in 5 / 2 / 10 of the eras with towns (before 0 / 0 / 0). Grain moves between neighbours:
    half of it crosses one or two stretches, 90% under 8 (about 60-480 km), which is the review's overland grain distance (100-200 km at
    most, R§6). It goes far only by water, and on these runs towns find enough grain nearby. A second reason, found here: step 2's
    allocation stops after 3 rounds, leaving 62-73% of the world's grain lack unmet (draft below).
  - **Steadiness (PW-1514): bar not met.** Under the land nudge the route stretches keep 0.59 / 0.69 / 0.48 of themselves (baseline 0.45 /
    0.55 / 0.47 with this judge), short of ~0.7; under the cost nudges they keep 0.82, 0.75 / 0.81, 0.73 / 0.73, 0.68 (baseline 0.87,
    0.85 / 0.78, 0.83 / 0.83, 0.73): a little worse on two runs. The cost-nudge numbers are **not** kept.
- **Herders' grain does not move**: 0.73% / 3.81% / 5.13% of the lack met (mean per snapshot), baseline 0.73% / 3.88% / 4.63%. Routes are a
  read-out; only the merchant quarters feed back, and they barely touch grain. Running the allocation for 8 rounds instead of 3 *does*
  move it: 1.5% / 11.3% / 9.6% (draft below).

## What changed in the code

- `Loads.finish(last)`: per good, the carried volume between cultures (`den`, deliveries whose taker cell is not the source cell) is the
  denominator; each good's load is summed over both directions of a stretch; the stretch keeps its strongest good (its group colours it);
  its mode is the one carrying the biggest share. Routes: strength ≥ `ROUTE_SHARE` (0.05); also strength ≥ `ROUTE_HOLD` × `ROUTE_SHARE`
  (0.5) if the stretch was a route the era before (`last`, from `derive`) or joins a route (`SPAN`, grown until nothing joins).
- `Loads._hubs`: caravan town = a land route stretch from the town's cell into a Koppen B cell (BWh, BWk, BSh, BSk), farmed or not, and the
  host culture knows `pack_animals`.
- `trade_flow.VERSION` = 3 (the server's cached docs are remade); `flows_at(..., last_routes=)`; `derive` passes each frame's route set on.

## Judge

Runs 0141d1, 3e0eb4 (D&D) and 07c755 (Seven Meals), L7, 26 frames from 12.5 kyr ago. Script: lane 214's judge was not committed, so it
was rebuilt from lane 213's (`judge2.py`: the land nudge multiplies every land value and every cell's people by U(0.9, 1.1), seed 1; the
cost nudges every mode factor, L and the toll by U(0.9, 1.1), seeds 2 and 3), with the nudged run derived on every frame (the hold reads
the era before) and Jaccard taken on every third frame. Run on main cb8374b0 it gives 0.45 / 0.61 / 0.46 for the land nudge where step3.md
reported 0.68 / 0.73 / 0.57; the nudge draws differ, so all comparisons below are this judge on both codes. Each cell: 0141d1 / 3e0eb4 /
07c755.

| | main cb8374b0 | this lane |
|---|---|---|
| stretches per era (mean) | 53 / 74 / 58 | 401 / 267 / 341 |
| pieces per era (mean, max) | 6.5 (18) / 5.1 (13) / 7.2 (16) | 19.9 (37) / 11.0 (20) / 19.8 (32) |
| eras with trading towns | 14 / 14 / 18 | 14 / 16 / 18 |
| ... with food routes | 0 / 0 / 0 | 5 / 2 / 10 |
| ... with metal routes | 0 / 1 / 0 | 11 / 9 / 12 |
| ... with two kinds besides salt | 6 / 0 / 13 | 14 / 14 / 18 |
| trading town-eras: port, caravan, river port, market | 0, 0, 45, 3 / 6, 0, 127, 15 / 0, 0, 108, 51 | 34, 12, 715, 61 / 23, 19, 433, 35 / 65, 23, 838, 102 |
| land nudge, route stretches (mean, min) | 0.45 (0.28) / 0.55 (0.20) / 0.47 (0.00) | 0.59 (0.21) / 0.69 (0.49) / 0.48 (0.15) |
| land nudge, load-weighted | 0.45 / 0.50 / 0.47 | 0.62 / 0.65 / 0.44 |
| cost nudge seed 2 / seed 3 | 0.87, 0.85 / 0.78, 0.83 / 0.83, 0.73 | 0.82, 0.75 / 0.81, 0.73 / 0.73, 0.68 |
| herders' grain met (mean per snapshot) | 0.73% / 3.88% / 4.63% | 0.73% / 3.81% / 5.13% |
| derive, seconds (1 thread, 6 jobs at once) | 63 / 62 / 88 | 76 / 73 / 107 |

Other rules tried (every frame, no nudge): per group with the carried denominator at 2%: food in 0 / 1 / 1 eras, metal in 0 / 7 / 2;
per good at 2%: food in 11 / 18 / 19 eras but 931 / 565 / 865 stretches an era in 54-85 pieces (a mesh). Per group at 2% with the hold
and the span: land nudge 0.62 / 0.56 / 0.62, still short. No rule tried reached ~0.7 on all three runs.

**The caravan rule's inputs** (route-stretch ends over all eras, main's routes): land stretches into a Koppen B cell 136 / 204 / 271; of
those into an unfarmed one 8 / 45 / 146; from a farmed cell 0 / 5 / 6; with a town there 0 / 0 / 0. The unfarmed condition and the town
condition were what removed them.

**Grain's distance** (cross-culture food deliveries, amount-weighted, eras 6, 3 and 0 kyr ago on main): median 1-2 stretches, 90th
percentile 4-8, 99th 13-33; 0-36% passes between cultures on one cell. The busiest food stretch carries 0.3-0.75% of the world's food
trade (metal: 0.1-0.55%). This is local exchange, as the review expects for grain overland (R§6: "cheaper to ship grain from one end of
the Mediterranean to the other than to cart it 75 miles"); long grain hauls need a city that has emptied its hinterland, and the 3-round
allocation stops before many such takers reach a far source.

**Allocation rounds.** With `trade_flow.ROUNDS` = 8 (not merged), the unmet share of the world's grain lack in the last six eras falls from
0.66-0.73 / 0.66-0.70 / 0.62-0.65 to 0.52-0.62 / 0.49-0.59 / 0.44-0.49, herders' grain met rises to 1.5% / 11.3% / 9.6% (any grain: 15% /
54% / 44%), food routes appear in 5 / 6 / 10 eras (5 / 2 / 10 with 3 rounds), and the derive takes 1.7-2.0 times as long. → draft
`draft-trade-allocation-rounds-cut-grain.md`.

## Sources fetched this lane

- Bleakley, H. & Lin, J. 2012, "Portage and Path Dependence", QJE 127(2): 587-644
  (https://econpapers.repec.org/RePEc:oup:qjecon:v:127:y:2012:i:2:p:587-644): towns formed where goods were hauled around falls stay
  important after the reason is gone ("we document the continuing importance of historical portage sites").
- Dalgaard, C.-J., Kaarsen, N., Olsson, O. & Selaya, P. 2022, "Roman roads to prosperity: Persistence and non-persistence of public
  infrastructure", J. Comparative Economics 50(4): 896-916 (https://econpapers.repec.org/RePEc:eee:jcecon:v:50:y:2022:i:4:p:896-916):
  denser Roman roads go with denser roads and settlement later, through market towns; the persistence fades where caravans replaced
  wheeled transport.

## Status

- PW-1515: not done. Other kinds besides salt and caravan towns: met. Food in most eras with towns: not met; the doc explains the
  overland part with sources, and the allocation cut is a defect left in a draft.
- PW-1514: not done. Land nudge 0.48-0.69 against ~0.7; the cost-nudge numbers fell by up to 0.1. Next to try: the carrier smoothed by the
  people's share (the land nudge flips the biggest culture on a cell, `_Frame.own`), which neither the hold nor the span touches.

## Pass 2 (lane 216b): grain looks on until it finds no more; why the routes still move; trunks tried

Baseline everywhere: **main ca03c9e6** (its trade code is cb8374b0's, so pass 1's baseline), judged with the same script as this pass:
[step3b/judge.py](step3b/judge.py), now committed (lane 214's never was). Each cell: 0141d1 / 3e0eb4 / 07c755.

### In plain words

- **Grain now keeps looking.** A place short of grain takes from the best supply it can reach; when that source runs dry, it looks for
  the next one. Until now it gave up after 3 tries, a limit set to save time, not a model number. Now it keeps trying until a round
  finds no more grain (40-160 rounds; a cap of 400 is only a safety net). Each try re-walks only the land the dry sources had been
  supplying, so the whole derive takes about as long as on main (45-67 s, against 48-64 s for main on the same machine load).
  - Grain still unmet, all eras: **0.52 / 0.48 / 0.33** of the world's grain lack (main 0.76 / 0.73 / 0.68). Last six eras: 0.27-0.48 /
    0.28-0.47 / 0.18-0.23 (main 0.66-0.73 / 0.66-0.70 / 0.62-0.64).
  - Herders' grain met (mean per snapshot): **3.4% / 13.0% / 12.3%** (main 0.73% / 3.9% / 4.6%; pass 1 0.73% / 3.8% / 5.1%).
  - Food routes: in **7 / 3 / 12** of the 14 / 16 / 18 eras with trading towns (main 0 / 0 / 0; pass 1 5 / 2 / 10). The food bar
    ("most eras with towns") is met on 07c755 only.
  - The other goods still stop after 3 tries. Run to the end, they need up to 200 rounds each and the derive takes about 6 times as
    long (305 s for 8 frames of 3e0eb4), far over the 3-minute budget (draft below).
- **Why the routes move under the land nudge (PW-1514).** The suspected cause, a cell's carrier culture flipping, is not it: in 18
  sampled frames (6 per run) the nudge flipped the carrier on no cell in 13, and on 1-699 cells (at most 1.5% of carrier cells) in 5. Splitting the nudge on
  07c755: nudging only the people per cell leaves the routes **0.93** of themselves; nudging only each good's land value leaves **0.50**.
  The routes move because a cell's spare goods are what it makes minus what it needs: where the two are close, a 10% nudge turns a cell
  from a source into a taker or back, the best source for its neighbours changes, and the deliveries take other roads. So smoothing the
  carrier (the brief's fix) cannot reach the bar, and it was not built. A fix has to work on the source side (for example, a market
  pooling its hinterland's spare goods before they travel), which is a model change for a later pass.
- **Thinning the mesh: two mechanisms tried, neither kept.**
  - *Cut back to towns and sources* (a route's loose ends must be towns or sources; a piece reaching no town goes): 149 / 105 / 207
    stretches an era in 7 / 4 / 10 pieces (main 53 / 74 / 58 in 6.5 / 5.1 / 7.2), but the routes became much less steady (land nudge
    0.43 / 0.41 / 0.44; cost nudges 0.57-0.72 against main's 0.73-0.87) and food routes fell to 3 / 3 / 9 eras. The cut is all or
    nothing: one town dropping off a piece's end removes the whole piece.
  - *Count a delivery only from its source to the town nearest its taker* (past that town goods are spread to the countryside in small
    lots; a delivery meeting no town draws no route): 250 / 129 / 281 stretches, land nudge 0.56 / 0.48 / 0.56, food in 0 / 2 / 8 eras.
    Measured against only the volume that reaches towns instead: 337 / 260 / 377 stretches, land nudge 0.51 / 0.60 / 0.57, food in
    10 / 9 / 14 eras of 14 / 18 / 19 (the best food result, still short on 3e0eb4), cost nudges 0.61-0.78.
  - **Why the mesh stays far over "a few trunks per landmass":** each of 20 goods draws its own roads, and a stretch is a route if it
    carries 5% of *one* good's travelling volume; the union of 20 goods' top stretches, each good with its own sources and takers, is
    hundreds of stretches whatever is done at the ends. A few trunks would need goods to share roads (a road once used getting cheaper
    for every good), which is also a model change.

### Judge, pass 2

| | main ca03c9e6 | pass 1 (a7c01778) | pass 2 (this) |
|---|---|---|---|
| derive, s (1 thread, 3-6 jobs at once) | 48 / 48 / 64 | 76 / 73 / 107 (6 jobs) | 48 / 45 / 67 |
| grain allocation rounds (mean, max) | 3 | 3 | 55, 148 / 59, 139 / 58, 159 |
| grain unmet, all eras | 0.76 / 0.73 / 0.68 | (last six eras 0.62-0.73) | 0.52 / 0.48 / 0.33 |
| herders' grain met | 0.73% / 3.9% / 4.6% | 0.73% / 3.8% / 5.1% | 3.4% / 13.0% / 12.3% |
| stretches per era (mean) | 53 / 74 / 58 | 401 / 267 / 341 | 410 / 281 / 359 |
| pieces per era (mean, max) | 6.5 (18) / 5.1 (13) / 7.2 (16) | 19.9 (37) / 11.0 (20) / 19.8 (32) | 20.4 (39) / 11.2 (20) / 19.9 (32) |
| eras with trading towns | 14 / 14 / 18 | 14 / 16 / 18 | 14 / 16 / 18 |
| ... with food routes | 0 / 0 / 0 | 5 / 2 / 10 | 7 / 3 / 12 |
| ... with two kinds besides salt | 6 / 0 / 13 | 14 / 14 / 18 | 14 / 14 / 18 |
| land nudge, route stretches (mean, min) | 0.45 (0.28) / 0.55 (0.20) / 0.47 (0.00) | 0.59 (0.21) / 0.69 (0.49) / 0.48 (0.15) | 0.59 (0.24) / 0.70 (0.49) / 0.49 (0.15) |
| cost nudge seed 2 / seed 3 | 0.87, 0.85 / 0.78, 0.83 / 0.83, 0.73 | 0.82, 0.75 / 0.81, 0.73 / 0.73, 0.68 | 0.82, 0.74 / 0.81, 0.71 / 0.71, 0.68 |
| trading town-eras: port, caravan, river port, market | 0, 0, 45, 3 / 6, 0, 127, 15 / 0, 0, 108, 51 | 34, 12, 715, 61 / 23, 19, 433, 35 / 65, 23, 838, 102 | 33, 12, 740, 75 / 23, 19, 425, 34 / 65, 23, 825, 102 |

Land-nudge parts (07c755, pass-2 code, nudged run derived on every frame): people only 0.93 (min 0.84), land values only 0.50 (min
0.14), judge with `RNUDGE=heads` / `RNUDGE=val`. Carrier flips: `_Frame.own` with and without the land nudge, every fifth frame of the window.

Screenshot: [step3b_routes_3e0eb4.png](step3b_routes_3e0eb4.png) (3e0eb4, 3,000 years ago, centred on 45° N 47° E, the land-heavy face).

### Code, pass 2

- `trade_flow.SEEK_GOODS` = ("grain",): its allocation runs until a round finds no more (no taker cut short by an emptied source reaches
  a live one), `SEEK_CAP` = 400 a safety cap; other goods keep `ROUNDS` = 3. `flows_at` records the rounds per good (`"rounds"`).
- `trade_flow._rewalk` and `_Frame.rewalk`: after a round, only the cells the emptied sources had supplied are walked again, from the
  live cells bordering them and any live source among them; the rest keep their cost and path (tested against a fresh walk).
  `_Frame.walk` keeps the walk's state (`_last`); later rounds read the supply and carrying cost at the asking cells only.
- `trade_flow.VERSION` = 4 (the server's cached trade docs are remade).
- Not kept: the cut-back rule and the market-anchored loads (above); the code is not on the branch.

### Status after pass 2

- PW-1515: not done. Kinds besides salt and caravan towns: met (pass 1). Food routes in most eras with towns: met on 07c755 (12/18),
  not on 0141d1 (7/14) or 3e0eb4 (3/16).
- PW-1514: not done. Land nudge 0.59 / 0.70 / 0.49 against ~0.7 (met on 3e0eb4 only); cost nudges 0.68-0.82 against main's 0.73-0.87,
  lower than main's in 5 of 6 by up to 0.12. The cause is the source side (land values), not the carrier.
- Lane 216's draft on the 3-round cut is folded in and deleted; the other goods' cut is a new draft.
