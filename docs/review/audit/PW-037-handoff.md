# PW-037 handoff: glacial carving on the glacial-index time zoom (2026-10-21, agent pw037-port)

**Outcome: carving is ported by hand onto `planet/timezoom/` (the old branch `pw037-carving` was not
merged). On an Earth L6 zoom it erodes in the observed range, and it stays bounded on drifting run moments
without any gate on the moment. Run time is +4.5%. 512 tests pass, with no golden changes. Mergeable.**

## What was ported (from pw037-carving, 0b2b545 / 3031f22)
- `kernels.py`:
  - `sia_flow` carries debris B with the ice;
  - the in-flow balance (`_balance`, new on main since the branch) drops the melted share of the debris;
  - it adds up the speed U, the yield-limited speed UL and the work W at the bed;
  - `thawed` (Robin's column) and `glacial_erosion` (Hallet's law, the overdeepening limit, nothing
    deeper than calve_depth).
- `sim.py`:
  - `_Sim.carve` (step 2b), the drop of debris in ice the sea takes (in `sea`), `rock_isostasy` at each full
    climate, and the reference bed in `above_flotation`;
  - frames get `glacial_erosion` and `glacial_till`; the state has cut, till, debris, rock_iso, wet_kyr
    and slide_km.
- `sources.py` (`bedrock`: cover and erodibility from the run's rock record), `params.py`, `store.py`
  (layers).
- `finish.py` (minimal: `glacial_imprint`, passed through the state; the Earth world gets the layers),
  `timeline.py` (cover stripped and till added, texture planing, `glaciated_myr` = 0 under the ice).
- `viewer/index.html`: the 'glacial erosion' and 'glacial till' layers.
- Tests: `test_kernel_threads::test_sia_flow` (debris bit-identical across threads and conserved, melt drop,
  UL <= U, W <= tau_y UL), `test_timezoom` (rock conserved, no carving, Robin with the flow's heat, the
  erosion rule), `test_finish` (the world carries the imprint).

## The two physics changes over the branch (PW-418's blocker)
1. **Sliding at most at the bed's yield stress** (`tau_y` = 100 kPa; Nye's plastic bed, ice-sheet basal
   stresses are 50-150 kPa). The shallow-ice speed goes as tau^3 H. Where tau_b = rho g H |grad s| is
   above tau_y (the grid's cliff-like margins, or a sheet far from balance), the speed used for sliding
   is scaled by (tau_y / tau_b)^3, per sub-step. This is the robust estimate PW-418 asked for (its option
   a, made physical), and it is not a gate on the moment. Resolved domes never reach it (test caps
   ~36 kPa).
2. **The flow's own heat thaws the bed.** In Robin's column, G = geothermal + tau_b u (Cuffey & Paterson
   ch. 9: 0.1-1 W/m2 under fast ice). Attempt 1, without it, froze 80-95% of the northern beds: Earth
   eroded 5 m/Myr on average (Laurentide region 5, Norway's coast 3, max 33 outside Antarctica), well below
   the literature. With it, fast outlets are warm-based and slow cold domes stay frozen.
`glacial_k` = 4e-6 and l = 1 are unchanged from the branch: no re-fit was needed.

## Earth (L6, 600 kyr, default; as showcase 6d0ed0)
Per Myr, under cells the ice has covered (4358 cells):

| | mean | median | p90 | p99 | max |
|---|---|---|---|---|---|
| all | 43 | 15 | 128 | 300 | 490 |
| Laurentide region (50-70 N, 105-60 W) | 26 | | 63 | | 250 |
| Fennoscandia | 33 | | 84 | | 142 |
| Norway's coast (fjord cells) | 77 | | 142 | | 219 |
| Greenland | 78 | | 169 | | 390 |
| Antarctica | 72 | | 219 | | 490 |
| Alps, Patagonia | 2-3 | | 3-7 | | 4-8 |

Against the literature:
- Ice sheets erode 0.01-0.1 mm/yr (10-100 m/Myr; Hallet et al. 1996, Koppes et al. 2015). The Laurentide
  is ~40 m/Myr over the Quaternary (Bell & Laine 1985).
- Fjords and outlet troughs reach several hundred m/Myr, and the Great Lakes' overdeepenings are a few
  hundred m. At 110 km cells a fjord is a cell mean (a 2 km by 5 km fjord in a cell is ~100-200 m).
- So the median (15) is "little elsewhere", the p90-p99 (130-300) are the carved valleys and troughs, and
  the max (~500) is the fjords and overdeepenings. That is in range.
- Alps and Patagonia are far too low: their glaciers are only a few cells at L6 (wet share 1-3%).

The erosion builds steadily: the mean under the ice is 0.5 m per 100 kyr in attempt 1 and ~5 m per
100 kyr now.

Till:
- Till is thickest in the outer, briefly iced belt. On North American land it is 25 m where the ice stood
  15-35% of the time and 18 m at 35-60%, against 9 m under the interiors (>60%) and 7 m at the outermost
  reach. Erosion runs the other way: 71 m/Myr under the interiors, 2.5 at the outer edge. So it erodes
  inside and deposits at the margins.
- Off marine fronts the debris piles into one sea cell, 540-640 m at the Ross and Weddell grounding zones
  (draft below).
- Ross grounding-zone cells that flicker between grounded and floating erode ~200 m and get about as much
  till back, so little net change.

Sea level is barely changed by carving: lowest -115 against -111 m. Run time at 300 kyr, 8 threads:
main 35.0 / 35.3 s, carving 36.7 / 36.9 s (+4.5%). `carving=false` is bit-identical to main (same
substeps and sea level).

## Showcase (real store)
- Time zoom **e9d59c**: Earth L6, 600 kyr. Its lowest sea level is -115 m at 594 kyr.
- Finished world **f6e955**, at the 420 kyr interglacial (sea level +1 m):
  - imprint under the cells the ice reached (4177): erosion mean 18.6 m, p90 55 m, max 205 m;
  - till p90 25 m, max 511 m (a marine fan).
- 6d0ed0 and the other 7 old time zooms can no longer be finished (draft).

## Drifting run moments (PW-492; L6, 400 kyr, PW-471's scratch runs)
Per Myr under the ice:

| moment | drift (mean sea level) | mean | p90 | p99 | max | without the yield limit: mean / p99 / max |
|---|---|---|---|---|---|---|
| seed 5 @ 520 (3133f2) | +154 m | 35 | 96 | 381 | 735 | 58 / 784 / 2091 |
| seed 3 @ 200 (575ac0) | +122 m | 45 | 106 | 519 | 733 | |
| seed 5 @ 260 (3133f2) | -148 m | 55 | 149 | 527 | 854 | 92 / 1233 / 3460 |
| seed 11 @ 420 (ea0254) | -19 m | 64 | 151 | 586 | 762 | |

The drifting moments carve 1-1.5x Earth's mean and 1.3-2x its p99. Their first 100 kyr, while the ice
collapses or piles up, carve about twice the later rate (5-6 m against 2.5-3 m per 100 kyr under the ice).
The yield-stress limit halves the mean and cuts the p99 by 2-2.3x and the max by 3-4x. So the drift no
longer digs km-deep basins. What it adds is real carving by ice that is really there, and that is the
run-moment drift's ticket (PW-492), not carving's.

## Not done / drafts filed
- `draft-rerun-time-zooms-for-carving.md`: all 8 time zooms in the real store need re-running to be
  finished (no backward compatibility).
- `draft-glacial-imprint-depth-only-one-myr.md` (needs-decision, from the branch, numbers updated).
- `draft-glacial-outwash-and-loess.md`, `draft-zoom-inputs-from-glacial-imprint.md` (from the branch).
- `draft-glacial-debris-piles-at-marine-fronts.md`: no fan spreading.
- `draft-earth-timezoom-erodibility.md`: Earth has no rock record, so its erodibility is uniform (GLiM is
  cached).
- Seen, not mine: on Earth the glacial-index Laurentide is the Cordilleran and Arctic sheets spreading
  east. Central Canada around Hudson Bay is never iced in 600 kyr (PW-033 / PW-435 territory).

## Scripts (session scratchpad `pw037/`)
- `tz_carve.py`: an in-memory zoom with the erosion and till summary and an npz;
- `maps.py`: erosion, till and ice-share maps, plus the till-by-ice-share table;
- `summ.py`, `timing.py`, `batch1.sh`.
- Outputs are in `pw037/out/`: e600 (attempt 1), e600h (final), m_* (moments), *_nolim.
