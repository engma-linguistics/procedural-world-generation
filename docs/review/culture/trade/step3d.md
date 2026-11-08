# Trade step 3d: every good seeks to the end; long-haul and local layers (PW-1519, PW-1515; lane 222)

Step 3c: [step3c.md](step3c.md). Code: `planet/lineages/trade_flow.py` (`_seek`, `_exchange`, `SEEK_CAP`; doc version 6),
`planet/lineages/trade_routes.py` (`LONG_KM`, `LOCAL_SHARE`, `Loads.finish`, `Loads._layer`, `Loads.seek_arrays` / `seek_done`), viewer
`viewer/globe/trade.js` and the "Local exchange" box under Trade routes, the Culinary brief's trading-towns table (`viewer/lineages.html`).
Tests: `tests/test_trade_routes.py` (three new, two replaced). Judge: [step3d/judge.py](step3d/judge.py) (step 3b's, plus unmet per good and
the layers). Screenshots, 3e0eb4 at the present, the land-heavy face at 45° N 47° E:
[long-haul only](step3d_longhaul_3e0eb4.png), [with local exchange](step3d_local_3e0eb4.png).

**Baseline everywhere: main b16e65ac** (lane 218's trade code), judged with the same script: its two trade files with `--base`. Runs 0141d1,
3e0eb4 (D&D) and 07c755 (Seven Meals), L7, 26 frames from 12.5 kyr ago, 1 thread per run. Main's steadiness numbers are step3c.md's for the
same trade code ("pools (final)"); main was not re-judged under the nudges here (the machine was paused for heat mid-lane).

## In plain words

- **Every good now keeps looking until nothing is left (PW-1519: bar met).** A place short of a good takes from the best source it can
  reach; when that source runs dry, it takes from the next best, and so on, until its need is met or no source can reach it. Before, only
  grain did this; the other 19 goods gave up after 3 tries.
  - How: one shared walk for each good. Supply spreads out from every source at once (as before), and places are served in order, best
    supplied first. When a source runs dry it stops spreading, and the land it held is walked again at once from the live sources around
    it. This was lane 218's idea; it replaces the round-by-round re-walks and the "8 best sources" walk, both too slow (step3c.md).
  - A safety cap of 400 sources per taker remains. It bit twice in 26 frames x 3 runs (two timber takers on 3e0eb4); it never bit
    otherwise. The most sources one taker used: 6-10 for grain, up to 160-380 for timber, firewood, salt, copper and livestock.
  - **Time: within the budget.** The whole derive takes 82 s / 89 s / 153 s (3 runs at once on a lightly loaded machine). On the same
    heavily loaded machine at the same moment, main took 53 / 49 / 79 s and this code 109 / 117 / 183 s: about 2.2 times main. The two D&D
    runs stay under 3 minutes either way; the Seven Meals run is at about 3 minutes under heavy load.
  - **What it changes** (unmet share of each good's world-wide lack, all 26 eras; main → now; 0141d1 / 3e0eb4 / 07c755):

    | good | main b16e65ac | this lane |
    |---|---|---|
    | grain | 0.53 / 0.48 / 0.34 | 0.53 / 0.48 / 0.34 (it already sought to the end) |
    | livestock | 0.91 / 0.97 / 0.89 | **0.54 / 0.83 / 0.21** |
    | spices | 0.96 / 0.98 / 0.85 | **0.60 / 0.69 / 0.13** |
    | gold | 0.75 / 0.70 / 0.44 | **0.56 / 0.44 / 0.18** |
    | gems | 0.83 / 0.86 / 0.81 | **0.44 / 0.78 / 0.33** |
    | ornaments | 0.91 / 0.93 / 0.91 | 0.58 / 0.73 / 0.61 |
    | timber | 0.88 / 0.91 / 0.89 | 0.74 / 0.86 / 0.61 |
    | firewood | 0.86 / 0.90 / 0.83 | 0.74 / 0.85 / 0.56 |
    | mithril | 0.92 / 0.94 / 0.90 | 0.83 / 0.85 / 0.76 |
    | stone | 0.07 / 0.26 / 0.14 | 0.03 / 0.14 / 0.06 |
    | oil and wine | 0.93 / 0.96 / 0.86 | 0.87 / 0.94 / 0.80 |
    | salt, copper, iron, tin, furs, sugar | 0.96-1.00 | 0.96-1.00 (unchanged: see below) |

  - Salt, copper, iron, tin and furs stay ~97-100% unmet: their sources are few and small against the want, and what exists is shared out
    either way. That is the ledger's supply, not the allocation (no change here; worth a look in the craft-goods ticket).
  - Herders' grain met: 3.1% / 12.6% / 12.1% (main 3.3% / 12.0% / 12.3%): unchanged, as grain already sought.
- **The overlay now splits long-haul from local (PW-1515, Daniel's 11-08 ruling).**
  - **Long-haul** is the precious goods (spices, gold, gems, ornaments, mithril, and tin, which falls off as a precious good) plus anything
    carried **500 km or more** from its source. Why 500 km: overland grain went 100-200 km at most (review1.md section 6), fine goods and
    tin 1,000 km and more (Kanesh ~1,200 km), and 216b measured 90% of grain's deliveries under ~480 km at L7. So 500 km keeps nearly all
    overland grain local, and counts grain shipped far by sea or river as long-haul.
  - **Each layer is measured against its own volume.** Measured against all of a good's volume, the long hauls drowned the short ones: at
    the present on 3e0eb4, 2,044 of 2,060 route stretches were long-haul and the local web had all but vanished. So a stretch is a
    long-haul route if it carries 5% of one good's long-haul volume, and a local route if it carries 1% of one good's local volume
    (`LOCAL_SHARE`, a judgement: local hauls are short and many, so no stretch carries much of the world's local trade; at 5% the local
    layer kept only 11-92 stretches an era, at 1% 595-901, about the density of main's web). A stretch can be in both layers.
  - **Viewer:** "Trade routes" draws the long-haul network, wider for a bigger share. A new box under it, "Local exchange" (off by default,
    `?tradeLocal=1`), adds the local web as thin lines that fade the less they carry. A trading town's hover card says "on the long-haul
    network" where it is; the Culinary brief's trading-towns table marks those towns "long-haul".
  - **How it reads.** The long-haul network is large: on average 1,520 / 1,520 / 1,800 stretches an era (2,800-3,200 at the present),
    mostly sea lanes (60-75%) and rivers, carrying fine goods. It is **tree-shaped**: 27-34 pieces an era, with ~90-130 junctions and
    ~150-240 loose ends in the later eras, and only 7-15 loops on average (out of thousands of stretches). So it is a branching network, as
    the Silk Road picture asks, but far from "a few trunks": precious goods fall off over 1,200 pack-km, which by sea is many thousands of
    km, and now that they seek to the end they reach almost everywhere by water. The local layer averages ~620 stretches an era, in many
    small pieces (a stretch or two each, around towns and along rivers).
  - **Steadiness (measured, not chased; PW-1525 waits on Daniel).** Jaccard of route stretches, mean over every third frame (min):

    | | main (step3c.md) | all routes, now | long-haul layer | local layer |
    |---|---|---|---|---|
    | land nudge | 0.64 / 0.60 / 0.50 | 0.80 (0.68) / 0.79 (0.69) / 0.75 (0.54) | **0.83 (0.69) / 0.84 (0.71) / 0.75 (0.42)** | 0.68 / 0.66 / 0.71 |
    | cost nudge, seed 2 | 0.82 / 0.68 / 0.72 | 0.87 / 0.83 / 0.81 | 0.87 / 0.85 / 0.86 | 0.84 / 0.80 / 0.75 |
    | cost nudge, seed 3 | 0.77 / 0.73 / 0.65 | 0.81 / 0.80 / 0.75 | 0.81 / 0.83 / 0.81 | 0.76 / 0.74 / 0.68 |

    The long-haul layer clears the old ~0.7 land-nudge bar on all three runs (mean), and every cost-nudge number is above main's. The
    routes got steadier mostly because goods now settle to the end instead of stopping after 3 tries at whatever source happened to be
    first: the cut-off made small nudges flip which source a taker reached.
- **Other effects to know about.**
  - Food routes now appear in every era with trading towns (14/14, 18/18, 18/18; main 12/14, 12/18, 15/18).
  - **Many more trading towns:** a route of either layer through a ledger town makes it a trading town, so there are ~800 at the present
    on 3e0eb4 (main step3c.md: 41), most of them river ports. Draft below.

## What changed in the code

- `trade_flow._seek` (numba): the shared walk, serving, source death and re-walk, and the tracing of each delivery along the walk's edges
  as it is made (to the stretch loads, the town tallies and the long-haul loads). `_allocate`, `_rewalk`, `_Frame.rewalk`, `ROUNDS` and
  `SEEK_GOODS` are gone. `flows_at` reports per good the most sources a taker drew from (`"rounds"`) and the takers the cap stopped
  (`"capped"`).
- `trade_routes`: `LONG_KM` (500), `LOCAL_SHARE` (0.01), `long_good`; `Loads.finish` judges each layer against its own volume (`_layer`:
  bar, last era's hold, span). Route records are now `[a, b, strength, group, mode, layers (1 long-haul, 2 local, 3 both), long-haul
  strength, long-haul group, local strength, local group]`; a hub has `"long"`; `culture_hubs` rows a seventh field.
- `trade_flow.VERSION` = 6: the server's cached trade docs are remade.

## Status

- PW-1519: **met.** Every good's allocation runs until a round finds no more; only the safety cap (2 takers in 78 frame-runs). The derive
  stays within ~3 minutes for the D&D runs (82-117 s), at ~2.2 times main's time.
- PW-1515: the long-haul / local split is built, drawn and exposed (`/api/trade?routes=1`, the hover card, the Culinary brief). The
  long-haul network reads as a branching tree but is big (1,500-1,800 stretches an era). Whether to thin it, and how steadiness is
  judged (PW-1525), is for Daniel.
