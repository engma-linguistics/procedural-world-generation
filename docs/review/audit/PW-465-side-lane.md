# PW-465 side lane: the run's ice pays the time zoom's marine losses (2026-10-21, agent pw465)

Exploratory, not merged. Branch `worktree-agent-af748cc6ffa533997`. Scratch: session scratchpad `pw465/`
(scripts `diag.py`, `flux.py`, `where.py`, `marine.py`, `tz_eval.py`, `score.py`, `runs.sh`, `seeds.sh`,
`moments.sh`; the fresh runs are in `pw465/store_fix`, the PW-460/459 code copy is `pw465/code460`).
Nothing was written to the real store.

**Outcome:** the I = 0 drift on run moments is fixed (9/10 within 25 m, main 4/10). The 10-seed cold-era
check is 7/10 (main 8/10), so it just meets the bar. The run is ~40% slower. The index bar goes from
0/10 to 2/10; the other moments fail on the target, not the drift. PW-460/459 on top still freezes the
cold eras (0/10). Lean: park it under PW-470 (draft-pw465-merge-decision.md).

## 1. Which loss

The zoom from main's run ice at I = 0 (index off, no orbital swing, mean orbit, 50 kyr), with the
zoom's `sea()` step split into its parts (`diag.py`). Sea-level equivalent over 50 kyr, m:

| moment (main's runs) | drift | surface balance | flow into the sea | shelf spreading | breakup (warm air) | shelf melt | front calving |
|---|---|---|---|---|---|---|---|
| s2 @ 500 | +101 | 1492 | 1532 | 1219 | 168 | 119 | 73 |
| s5 @ 520 | +94 | 502 | 523 | 279 | 115 | 95 | 103 |
| s3 @ 200 | +84 | 764 | 698 | 433 | 95 | 137 | 176 |
| s5 @ 260 | -51 | 307 | 244 | 160 | 32 | 43 | 19 |

So it is **neither calving nor mainly shelf melt: it is the flow across the grounding line** (the
shallow-ice flow from the coastal cells into the sea, which then leaves as shelf spreading or breakup).
Shelf melt is 10-20%, front calving of grounded ice 5-25%. Per metre of iced coast (`flux.py`,
`where.py`), the zoom takes 0.9-2.0e5 m2/yr on average; beside water deeper than ~500 m (where the ice
floats) ~1-2e5, beside shallow water ~1e3-5e4 (the ice grounds and the front stands). The run charged a
flat `ICE_CALVE` 5e4 per m of coast, and only to its ablation ring: an accumulation zone touching the sea
paid nothing. The ice lost is mostly interior and marine-bed thinning as the sheets drain to the coast
(e.g. s2 @ 500: -54 m inland, -27 m on beds pressed below the sea, -12 m on the coastal cells).

## 2. The fix (`planet/icemass.py`, `planet/tectonics/earth.py`)

- `icemass.coast_loss`: the zoom's own rules on the run's still geometry, per side of an iced cell facing
  the sea. The shallow-ice flux across the side (D = gamma h^5 |grad s|^2, capped, the sea's D = 0, as
  `sia_flow`'s first step from the coast). Where that ice would float, the flux is lost, less `BUTTRESS` where
  a shelf can stand (`shelf_viable` of the air over the sea, and the sea's sub-shelf melt under one cell of
  shelf doesn't outrun the flux). Where it would ground, `CALVING` x depth x h, at most the flux.
- `earth.coast_cost`: that per land cell, at a margin cell's Nye mean thickness (~740 m at L6), with the
  surface on the true bed (marine beds that `land_view` floors stand `depth` below the sea). Margin cells
  on marine beds whose ice would float, or deeper than `CALVE_DEPTH`, go at once.
- `ablation_zone`: first each sheet's budget is its snow less its coast's loss. A sheet in deficit drops
  its dearest coastal cells (loss less own snow) until the rest pays, up to `ICE_RINGS` rounds. Then the
  ablation ring spreads as before, with `coast_cost` instead of `ICE_CALVE` (removed).
- `earth.marine_view(bed, c)`: the water depth, sea air and sub-shelf melt for it. The callers in
  `update_climate`, `tests/test_invariants.py`, `tests/test_timezoom_consistency.py` and `tools/ice_probe.py`
  pass it.
- Shared rather than duplicated: the zoom's marine constants (`FLOW_A`, `ENHANCEMENT`, `D_CAP`, `CALVING`,
  `CALVE_DEPTH`, `BUTTRESS`, `SHELF_WARM/COLD`, `MELT_K`, `RHO_I/W`) and `shelf_viable` now live in
  `icemass`. `TZParams` takes them as defaults, and `timezoom.ice.shelf_viable` calls `icemass`'s. The zoom's
  output is unchanged (Earth's 600 kyr zoom is identical to main's, below).

## 3. Measures

### 3.1 The 10 PW-471 moments (4 fresh L6 runs of 800 Myr, seeds 5/3/2/11; same times)

The fixed runs give different ice at the same times (the run's trajectory changes), shown as ice % of land.

Drift at I = 0 (index off, mean orbit, no swing), sea level after 50 kyr:

| moment | main ice % land | main @50 kyr | fix ice % land | fix @10 / @20 / @50 kyr |
|---|---|---|---|---|
| s5 @ 260 | 10.4 | -51.1 | 9.1 | -18 / -22 / **-25.9** |
| s5 @ 440 | 28.3 | +26.2 | 8.4 | -10 / -13 / -14.5 |
| s5 @ 520 | 18.0 | +93.5 | 5.8 | -1 / -2 / -0.7 |
| s3 @ 200 | 17.1 | +83.9 | 10.4 | +13 / +17 / +20.4 |
| s3 @ 500 | 10.0 | +21.5 | 20.2 | -18 / -16 / -12.1 |
| s3 @ 620 | 13.4 | +49.2 | 26.8 | -26 / -31 / -22.5 |
| s2 @ 500 | 39.2 | +101.1 | 58.0 | -23 / -6 / +0.5 |
| s2 @ 700 | 13.1 | +17.1 | 29.3 | 0 / +2 / +5.3 |
| s11 @ 200 | 36.4 | +16.0 | 34.9 | -25 / -22 / -17.6 |
| s11 @ 420 | 13.5 | +16.0 | 6.8 | +7 / +17 / +22.3 |
| within 25 m | **4/10** | | | **9/10** (s5 @ 260 misses by 0.9 m) |

The residual drift now runs both ways (the zoom grows a little ice on some moments). The surface balance
and the sea's take match within ~2% on every moment, against 5-15% on main.

The original bar with the glacial index (default, 6.5 C, 400 kyr): cycles (>= 2 endings), every glacial
maximum within 1.5x the target below the start, no interglacial more than 1.5x the target above it:

| moment | cooling C | target m | cycles kyr | maxima m | interglacials m | mean m (main) | pass |
|---|---|---|---|---|---|---|---|
| s5 @ 260 | 5.99 | 85 | 91, 116, 93 | -214..-176 | -144..-108 | -149 (-147) | no: too deep |
| s5 @ 440 | 7.11 | 102 | 96, 94 | -197..-186 | -135..-91 | -138 (+34) | no: too deep |
| s5 @ 520 | 10.29 | 147 | 90, 115, 93 | -238..-156 | -98..-29 | -96 (+154) | no: too deep |
| s3 @ 200 | 2.34 | 34 | 96, 134 | -15 | +37..+54 | +21 (+122) | no: IG +54 > 51 |
| s3 @ 500 | 1.04 | 15 | 115, 94, 94 | -18..-16 | +2..+13 | -7 (+34) | **yes** |
| s3 @ 620 | 3.22 | 47 | 116, 90 | -92..-65 | +3..+65 | -13 (+4) | no: both by a little |
| s2 @ 500 | 0.64 | 9 | 116, 92, 93 | -21..-13 | +23..+38 | +8 (+123) | no: tiny target |
| s2 @ 700 | 0.19 | 2.7 | 92, 115, 94 | 0..+76 | +128..+142 | +86 (+112) | no: loses ice under the orbit |
| s11 @ 200 | 2.05 | 30 | 92, 91, 91 | -36..-21 | -2..+27 | -11 (+70) | **yes** |
| s11 @ 420 | 1.14 | 17 | 91, 93, 114 | 0..+16 | +33..+38 | +24 (-20) | no: IG +38 > 25 |
| pass | | | | | | | **2/10** (main 0/10) |

Every moment cycles at ~90-130 kyr with no runaway. The window means are much closer to the start
(median |mean| 17 m against main's 99 m). The failures are now (a) deep glacials on moments with lots of
free cold land (the s5 moments, 1.5-2.5x the target: PW-492's second finding), (b) tiny targets on moments
with little snowline land, where +20..+40 m interglacials fail a 4-25 m allowance (the target's form,
PW-492), and (c) s2 @ 700, which holds at I = 0 but loses +130 m once the orbit swings (its ice survives
only the mean orbit: PW-464's question).

### 3.2 The run's 10-seed L6 1 Gyr cold-era check (`tools/sealevel.py`; worst era >= -450 m and <= 2% of time below -430 m)

Main was re-run on today's main (2a6f559). It reproduces the pw449 reference exactly.

| seed | main worst / <-430 / <-150 | fix | PW-460/459 on the fix |
|---|---|---|---|
| 3199 | -386 / 0.0% / 31% ok | -210 / 0.0% / 4% ok | -675 / 20% / 42% F |
| 11 | -569 / 5.2% / 37% F | -473 / 5.2% / 14% F | -497 / 12% / 44% F |
| 2 | -404 / 0.0% / 22% ok | -334 / 0.0% / 16% ok | -479 / 3.2% / 56% F |
| 21 | -393 / 0.0% / 11% ok | -220 / 0.0% / 16% ok | -473 / 3.6% / 14% F |
| 1 | -260 / 0.0% / 13% ok | -352 / 0.0% / 15% ok | -529 / 6.8% / 63% F |
| 5 | -215 / 0.0% / 16% ok | -166 / 0.0% / 0.4% ok | -572 / 7.6% / 36% F |
| 7 | -362 / 0.0% / 14% ok | **-745 / 8.0% / 38% F** | -548 / 4.8% / 42% F |
| 13 | -372 / 0.0% / 44% ok | -479 / 5.6% / 38% F | -444 / 3.6% / 57% F |
| 42 | -364 / 0.0% / 27% ok | -304 / 0.0% / 11% ok | -482 / 4.4% / 54% F |
| 99 | -450 / 3.2% / 60% F | -404 / 0.0% / 30% ok | -554 / 14% / 64% F |
| pass | **8/10** | **7/10** | **0/10** |

The fix makes most cold eras milder (time below -150 m falls on 7 of 10 seeds) but deepens three. Seed 7's
icehouse at 240-400 Myr holds -411..-745 m through dT +0.3 C, against main's -263..-94. The cause is
probably that shallow coasts now cost the zoom's flux (~1e3-5e4 m2/yr per m), often less than the old
flat 5e4, so a cold era's coastal sheets spread further along shallow shelves (draft-coast-loss-approximations.md).

**PW-460/459 (246ef40's run side: `icemass` margin ramp and seasonal k, `earth._ice_pass`) on top: 0/10.**
The cold eras still freeze, as on PW-461 (a2: 1/10). The marine budget doesn't stop it: the sheets that
freeze aren't the coastal ones the budget trims. So the run's deglaciation problem with honest margins is
PW-464's (the cycle mean) or B(3), not the marine budget alone.

### 3.3 The Earth time zoom (L6, 600 kyr, default)

Identical to main's PW-471 numbers, as expected, since the zoom's rules didn't change: cycles 108.5, 98.5,
107.5, 99.5, 107 kyr; maxima -86, -87, -94, -97, -99, -104 m; interglacial ice 9.1-12.2% of land; Laurentide
to 42.5 N, 0.7 Mkm2 south of 50 N. Cooling stays 6.5 C: the fix doesn't touch Earth's zoom (it starts from
the real ice).

### 3.4 Run time

Seed 11, L6, 400 Myr, `tools/sealevel.py`, 4 threads each, main and fix side by side: main 257 s wall /
700 s CPU, fix **358 s / 1072 s (+39% wall, +53% CPU)**. The cost is `coast_cost` and the trim loop
(`kernels.components` up to 40 times) in every pass of `ice_sheets` (up to 200 passes per climate update).
It isn't optimised. Computing `coast_cost` once per climate update and trimming only when a sheet is in
deficit should recover most of it. That is a prerequisite for merging.

### 3.5 Tests

`uv run pytest -q`: 512 passed, 1 failed. `test_health.py::test_frame_rivers_end_in_its_own_hollows` fails:
on the changed L4 trajectory a river ends 5 m above a salt pan at 220 Myr. That is hydrology, not ice; it
passes on main, and PW-461's a2 code tripped it too (draft-river-end-beside-salt-pan.md). The goldens
pass, so they weren't updated.

## 4. For a fresh agent

- To merge it: fix the salt-pan test, cut the cost (3.4), and look at seed 7 with the zoom-mean tool
  (PW-467) to see whether its -745 m is the zoom's balance too.
- To go on: PW-464 (the cycle mean) is the next lever. With it, re-apply PW-460/459 and re-run both tables.
- Drafts: draft-pw465-merge-decision.md (needs-decision), draft-coast-loss-approximations.md,
  draft-river-end-beside-salt-pan.md.
