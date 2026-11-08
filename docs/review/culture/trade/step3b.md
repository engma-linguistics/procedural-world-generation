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
