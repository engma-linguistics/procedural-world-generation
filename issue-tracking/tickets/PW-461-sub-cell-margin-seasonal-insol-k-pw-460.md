---
id: PW-461
title: "Sub-cell margin + seasonal insol_k (PW-460/459) deepen the zoom but freeze the run's cold eras (1/10 seeds): the run needs a way to deglaciate"
type: task
status: wontdo
parent: PW-470
milestone: v2
subsystem: tectonics
effort: l
impact: high
found_by: pw460
blocked_by: []
relates: [PW-460, PW-459, PW-033, PW-435, PW-422, PW-115, PW-440]
refs: [planet/icemass.py, planet/tectonics/earth.py, planet/timezoom/sim.py, planet/timezoom/forcing.py, docs/review/audit/PW-033-diagnosis.md]
created: 2026-10-20
updated: 2026-10-26
---

## Description
PW-460 (a margin cell's balance over its sub-cell Nye ramp) and PW-459 (the orbit's effect from each cell's own
seasons) were built in both the run and the time zoom on branch `worktree-agent-a9f64607e1a64d2e8`. Two attempts
were made. In both, the zoom deepens as the diagnosis predicted, but the run's 10-seed cold-era check collapses
(main 8/10, both attempts 1/10). Per the stop rule this was **not merged**.

What the code does (the branch's last commit; attempt 2):
- `icemass.margin_ramp(H, width)`: a margin cell's ice H is a Nye ramp sqrt(2 tau/(rho g) x) across an iced share
  f = (H / (2/3 x top))^(2/3) of the cell, top = the ramp at the cell's width (1354 m at L6). Its balance is
  f x the mean of the balance at the 2-point Gauss heights (0.46 and 0.89 x top sqrt(f), ~620 / ~1200 m when
  iced across). Used for old ice next to bare land in the run (`earth._ice_pass`) and for margins in the zoom
  (`prepare_surface` / `year`). New margins (run: bare land) and fronts (zoom) stay at the edge's `EDGE_H` in
  attempt 2; attempt 1 used the full-cell ramp for them too.
- `icemass.seasonal_k`: C per W/m2 = (t_warm - t_cold) / the lagged sun's seasonal range at the cell's latitude,
  the range floored at 0.25 x the planet's largest. On Earth L6 that is 0.08-0.09 on land at 20-70 N, about
  0.023 at sea (0.27 x land, so `insol_sea` comes out by itself), and 0.08-0.09 on the ice sheets.
  `icemass.orbit_k` is now shared by the run and the zoom. `INSOL_K`, `INSOL_SEA`, `insol_k`, `insol_sea` and
  `edge_h` are gone, and `TZParams.insol_gain` (default 1) is a multiplier for experiments. The zoom takes k
  from each full climate's ground temperatures, plus the obs bias. `finish.orbit_dt` takes it from the frame's
  climate.

Earth time zoom, L6, 600 kyr. The interglacial-ice bar is 9-12% of land. "Margin only" / "k only" keep the
other rule at its old value (old k approximated as 3x the seasonal k: 0.25 on land, 0.07 at sea).

| variant | min sea level (m) | IG ice % land | Laurentide at min, Mkm2 / south | Laur. southmost | time Laur. > 2 Mkm2 | Fenno at min (Mkm2) | endings / backstops | mean sea level |
|---|---|---|---|---|---|---|---|---|
| main | -45.1 | 8.7-9.8 | 1.63 / 54.9 | 53.9 | 0% | 1.53 | 2 / 0 | -13.9 |
| main obs | -31.0 | 8.8-10.3 | 2.48 / 53.9 | 49.5 | 9% | 0 | 2 / 2 | -12.2 |
| a1 both (fronts at the ramp too) | -155.9 | 14.7-17.5 | 2.43 / 56.7 | 50.6 | 17% | 3.63 | 5 / 0 | -84.4 |
| a1 both, obs | -92.5 | 12.8-14.4 | **5.66 / 46.4** | 46.4 | 94% | 0.91 | 7 / 0 | -52.8 |
| a1 margin only | -146.3 | 10.3-14.2 | 2.75 / 51.6 | 50.5 | 5% | 3.55 | 6 / 0 | -46.7 |
| a1 margin only, obs | **-82.2** | **9.5-12.3** | **5.65 / 45.6** | 44.9 | 65% | 0.77 | 5 / 0 | -29.6 |
| k only | -60.1 | 12.0-12.8 | 1.52 / 56.7 | 55.7 | 0% | 1.28 | 6 / 0 | -31.6 |
| k only, obs | -37.4 | 10.8-11.5 | 2.28 / 53.9 | 52.9 | 10% | 0 | 4 / 0 | -24.4 |
| a2 both (fronts at the edge) | -90.0 | 14.2-15.4 | 1.71 / 55.9 | 54.9 | 0% | 2.23 | 6 / 0 | -52.0 |
| a2 both, obs | -63.3 | 11.4-12.1 | 4.33 / 49.6 | 49.5 | 63% | 0 | 7 / 0 | -35.3 |

The extra interglacial ice is North American and Arctic-island ice (a1 obs: 3.4 Mkm2 in North America and
2.7 in the Greenland box at the interglacials, against 0.35 / 0.76 on main). The warm precession phases are
weaker now, so they no longer clear it.

The unforced-start consistency test (`tests/test_timezoom_consistency.py`, bar 25 m, 20 kyr) gives sea-level
change, and in brackets the cold moment's iced share of the planet at the start:
main -17.3 (1.1%), k only +14.7 (5.5%), margin only +17.9 (6.5%), a1 both **+76.2** (12.2%), a2 both **+64.5**
(10.4%). Each lever alone passes. Together the run's cold moment ices 10-12% of the planet, mostly coastal.
The zoom then loses it to calving (12,400 km3/yr against +11,100 of surface balance) and to shelf melt
(72 M km3 over 20 kyr, against 1.7 M with k only). The run's calving charge doesn't remove an accumulation
zone that touches the sea.

The run's 10-seed L6 1 Gyr cold-era check. The bar is worst era >= -450 m and at most 2% of time below -430 m.

| seed | main (pw449 ref) | a1 both | a1 margin only | k only | a2 both | a2 margin only |
|---|---|---|---|---|---|---|
| 3199 | -386 ok | -614 | -659 | -471 | -521 | -514 |
| 11 | -569 F | -584 | -615 | -575 | -601 | -675 |
| 2 | -404 ok | -510 | -789 | -752 | -614 | -622 |
| 21 | -393 ok | -529 | -492 | -295 ok | -330 ok | -580 |
| 1 | -260 ok | -534 | -454 | -393 ok | -648 | -434 ok |
| 5 | -215 ok | -540 | -472 | -228 ok | -730 | -330 ok |
| 7 | -362 ok | -419 ok | -483 | -326 ok | -580 | -575 |
| 13 | -372 ok | -476 | -694 | -309 ok | -526 | -666 |
| 42 | -364 ok | -662 | -530 | -382 ok | -556 | -407 ok |
| 99 | -450 F | -667 | -506 | -450 F | -529 | -483 |
| pass | **8/10** | 1/10 | 0/10 | 6/10 | 1/10 | 3/10 |

With the margin lever the time below -150 m goes from 10-60% to 45-87%. The run's sheets hardly ever retreat
from a cold era.

**Why the run can't take an honest margin.** The run's ice is a flux-free equilibrium extent under the
cycle-averaged balance (`earth.ice_sheets`), with the old ice's height counted, so the rule has hysteresis. The
time zoom deglaciates through its endings (the cycle's melt and calving boosts, the CO2 release) and its
calving and shelves. The run has none of these, and its only brake on a sheet was the margin melting as its
outermost 10 km (408 m). That brake is the error PW-460 removes. Once the margin is honest (~900 m mean at L6),
a cold era's sheets hold on through the warming that follows. PW-422's "a ring a pass" creep is the same
effect.

The cold moment (seed 11 @ 400 Myr, a2 code, 600 kyr zoom): see the Updates line on PW-460.

Two fast tests also change outcome with a2 (not investigated, since the change isn't merged):
`test_timezoom.py::test_glacial_cooling_turns_forest_to_tundra_and_cools_further` (the plants' forcing goes
+0.08 W/m2 instead of negative) and `test_health.py::test_frame_rivers_end_in_its_own_hollows`.

Options:
- (A) **Merge PW-459 alone** (seasonal k in the run and the zoom). The run gets 6/10 (bar ~7, main 8). The
  interglacials keep 12.0-12.8% of land (bar 9-12). The Laurentide's geography doesn't change, and Earth gets
  -60 m (obs -37). It's sound physics on its own, but it gives no LGM geography and it makes the interglacials
  icier.
- (B) **Both levers, plus a way for the run's ice to deglaciate**, so that the run's mean ice is the cycle's
  time-mean extent rather than the extent under the cycle-averaged balance. For example: (1) the run's sheet is
  the mean over the cycle's orbital states of each state's own extent (no hysteresis carried between states),
  or (2) a calving and marine-margin charge that removes coastal accumulation zones whose snow can't pay for
  their calving (the zoom's budget), or (3) the run's cold eras drawn from a short time-zoom-like integration.
  Then re-run the 10 seeds and the consistency test. The Earth zoom side is ready: margin only + obs already
  meets every Earth target. Lean, but it's a run-physics project (l-xl) in the serial run lane.
- (C) Keep both at main's values and accept pulse-like Earth glacials (-45 m, Laurentide <= 1.7 Mkm2).
- [ ] decide

## Updates
- 2026-10-26: Status todo -> wontdo. Wontdo: merged into PW-465. (PW-900 backlog reorg).
- 2026-10-23: Status needs-decision -> todo. Coordinator (2026-10-24): owner defers geophysics; not an owner question. The physics lane decides it against the v1/v2 north star (seed robustness first) when it reaches it.
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: Created from inbox draft draft-subcell-margin-needs-run-deglaciation.md (found by pw460).
