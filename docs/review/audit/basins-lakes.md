# Run lane: closed basins and giant lakes (PW-299, PW-300, PW-284; PW-054, PW-243)

Branch `worktree-agent-ab488f391ed3caf1b`, on main b2c7759 (= the night baseline's physics: the branch point's health sweep is bit-identical to `docs/review/night-2026-10-16/health/`). One model change, PW-299. Health sweeps: `docs/review/health-basins-before/` (branch point), `docs/review/health-basins-pw299/` (after), L7: `health-basins-L7-before|after/` (seed 3199), `health-basins-L7b-before|after/` (seeds 21, 11), all 500 Myr, `--no-determinism`. Diagnostic scripts: `basins-lakes/hollow_budget.py`, `basins-lakes/evap_sensitivity.py`.

## Summary
| Step | Result |
|---|---|
| PW-299 | Done. The floodplain share kept on a hollow's slopes is capped at the cell's room below the spill point; deposition above the spill level on hollow cells 2.53% -> 0.00% of all deposition (L5 seed 1, 300 Myr). |
| PW-300 | Diagnosed, stopped: no sound fix in this lane's files. Water balance sound; giant lakes are closed lakes on broad flat continental hollows that sit just short of spilling. Likely causes outside the lane: too-high humid-climate open-water evaporation (climate.py, draft) and hollows made each step by plate resampling (tectonics, draft). |
| PW-284 | Stopped, not landed. The moat makes most L6 closed basins (inland 6.4 -> 3.7% without it) but isn't singled out for giant lakes; sound flexure still needs the load (grid-scale crust spikes) fixed in crust.py first. Write-up on the ticket. |
| PW-054 / PW-243 | Inland drainage fell with PW-299 (L6 4.9 -> 4.2%, L7 8.8 -> 6.0%, 3 seeds): the L7/L6 ratio narrowed 1.8 -> 1.4, by L7 falling. No sound, simple cause found for the shortfall itself. |

## Health, L6 (`--quick`: 8 seeds x 500 Myr, frames after 50 Myr; per-seed medians, then the mean)
| metric | before (b2c7759) | after PW-299 |
|---|---|---|
| giant-lake frames (lake > 1 Mkm2), % per run | 8.85 (per seed 6.2 2.7 20.4 9.7 8.8 5.3 14.2 3.5) | 6.19 (0 3.5 15 7.1 3.5 8 8 4.4) |
| largest lake, median of frames, Mkm2 | 0.162 | 0.112 |
| largest lake, any frame, Mkm2 (mean of seeds' maxima) | 4.21 (max 6.84) | 3.47 (max 6.26) |
| inland drainage, % of ice-free land | 4.91 | 4.20 |
| lakes, % of land | 0.595 | 0.431 |
| land, % | 33.5 | 33.5 |
| highest peak, km (mean of seeds' maxima; max) | 8.50 (8.86) | 8.53 (8.73) |
| crust volume end/start | 0.896 (0.878-0.921) | 0.895 (0.867-0.916) |
| sea level, m (mean of seed medians; pooled median) | +9 (+7) | +5 (+11) |
| icehouse spells (ice sea level < -50 m), all seeds | 5 | 6 |
| arid % of land | 29.1 | 29.8 |

The giant-lake share is noisy: the same 8 seeds under variants that shouldn't matter much to it give 6.1-10.8% (table below), so PW-299's 8.85 -> 6.19 is within seed noise. The lake share (0.60 -> 0.43%) and inland drainage (4.9 -> 4.2%) fall at both levels (L7 below): sediment that used to build hollow rims now reaches the floors and fills them.

## PW-299
`surface._route` kept 1 - exp(-d / alluvial) x exp(-slope / 2 m/km) of a river's load on every gentle land cell it passed, inside closed hollows too. Now `erode` computes the terrain's priority-flood once (shared with `_closed_basins`), and inside a hollow (spill > ground) the keep is capped at max(spill - 5 m - ground, 0) / iso_dep less what the cell already got; outside hollows plains aggrade freely, as before. The excess runs on down to the basin floor, where PW-280's room rule fills it.

| L5 seed 1, 300 Myr | before | after |
|---|---|---|
| deposition landing above the spill level on hollow cells (>= 1 m below spill), % of all deposition | 2.53 | 0.00 |
| deposition on hollow cells, % of all | 9.14 | 7.56 |

Test: `test_sediment_budget_closes` now checks every cell inside a hollow, not only river ends (fails on the old code).

## PW-300: where the giant lakes come from
Giant-lake frames of the before sweep, from the stored layers (median over the lake; "hollow" = priority-flood spill - ground; prev = the frame 4 Myr earlier):

| run (seed) @ Myr | Mkm2 | kind | ground m | depth med/max m | rain mm | hollow now/prev m | prev lake overlap |
|---|---|---|---|---|---|---|---|
| s1 @52 | 4.12 | closed | 710 | 24/94 | 32 | 99/60 | 0.00 |
| s1 @288 | 3.31 | closed | 610 | 46/125 | 625 | 47/50 | 0.00 |
| s42 @144 | 6.84 | closed | 608 | 34/160 | 556 | 36/21 | 0.00 |
| s3199 @52 | 5.16 | closed | 758 | 50/141 | 1176 | 52/53 | 0.00 |
| s3199 @272 | 1.54 | closed | 810 | 23/805 | 255 | 146/0 | 0.40 |
| s77 @480 | 4.62 | closed | 150 | 119/228 | 1455 | 151/135 | 0.02 |
| s11 @240 | 3.81 | closed | 830 | 48/199 | 4 | 0/0 (ice-dammed) | 0.47 |
| s505 @424 | 1.64 | closed | 546 | 84/412 | 1302 | 92/0 | 0.00 |

Most are closed, shallow (median 20-120 m) and broad, on plain ~37 km continental crust with no plate boundary nearby, and most appear and vanish within a frame.

**1. The lake water balance is sound.** Replaying 8 giant frames (`timeline.replay`) and recomputing `hydrology.rivers_and_lakes`: for each closed lake, its basin's inflow (runoff over the catchment, incl. rain on the lake) matches the evaporation off the lake (lake_evap - aet over its cells) within ~3% (s42 @144: 1.74 vs 1.76 m x Mkm2/yr; s77 @480: 5.79 vs 5.73; s3199 @52: 6.28 vs 6.24). The one apparent miss (s1 @52, route catchment 2.37 vs 5.37) is rivers ending in dry pits of the same basin, which `kernels.lakes` correctly credits to the basin's lake (steepest-descent catchment 4.47). Open lakes fill their hollows to the spill point (by construction).

**2. The hollows.** Rims of the giant hollows rose 20-190 m relative to their floors within a frame; floors are flat (cover 0.4-1 km, depth max/median 3-8). Budget of closed-hollow volume by substage (`hollow_budget.py`; hollows the lakes keep: `hydrology._bed` with MIN_DEPTH/MIN_SLOPE, then spill - bed; L6, 300 Myr, per 2-Myr step after 50 Myr, km3):

| substage | seed 1: all hollows (gross + / -) | seed 1: in hollows >= 1 Mkm2 | seed 77: all | seed 77: >= 1 Mkm2 |
|---|---|---|---|---|
| resolve (move, resample, collide; dyn recomputed) | +66,317 (+72,958 / -6,641) | +4,580 (+17,654 / -13,075) | +34,214 | -3,350 (+12,352) |
| _age (plume swells decay, new domes) | +9,671 | +11,839 | +803 | +1,662 |
| arcs and plumes | +5,767 | +4,311 | +5,813 | +1,598 |
| stacking, accretion, subduction erosion, stretching | -9,247 | -504 | -10,188 | -780 |
| crust flow and orogeny | -13,231 | -4 | -18,548 | -8 |
| erosion and deposition | -77,588 (+4,541 / -82,128) | -29,983 (+7,216 / -37,198) | -46,683 (+15,929 / -62,612) | -3,374 (+15,063 / -18,437) |
| sediments, burial, reefs, coherence, birth | -3,487 | -71 | -926 | +624 |
| write-back (dyn recomputed) | -9,402 | +5,479 | -10,396 | +1,240 |
| events, world view, the climate's sea shift | +25,071 | -1,583 | +44,309 | -859 |

Plate motion and resampling (`resolve`) makes most of the closed-hollow volume every step, the erosion step removes about as much; for the giant hollows, the swell decay, plumes and the moat's recompute add to it. No single in-lane process stands out. Diagnostic variants (my harness: the same measure as the frames, `output.water_now` every 4 Myr, 8 L6 seeds x 500 Myr; inland = raw ends on land, a little above health's checked measure):

| variant | giant-lake frames % (per seed) | largest lake, median Mkm2 | inland % | lakes % of land |
|---|---|---|---|---|
| branch point | 8.8 (6 3 20 10 9 5 14 4) | 0.171 | 6.41 | 0.60 |
| PW-299 | 6.2 (0 4 15 7 4 8 8 4) | 0.114 | 6.69 | 0.43 |
| PW-299 + no floodplains (`alluvial=1e12`) | 9.8 | 0.101 | 5.99 | 0.35 |
| PW-299 + no hotspots (`hotspots=0`) | 10.3 | 0.111 | 5.72 | 0.43 |
| branch point, no moat (`flexure=0`) | 6.1 | 0.120 | 3.70 | 0.24 |
| PW-299 + MIN_SLOPE tested on the hollow's mean depth (cone-equivalent 3 x mean depth / radius) | 10.8 | 0.136 | 8.20 | 0.43 |

Seed noise in the giant share is about +-2.5 points. The mean-depth rule (tried because a few giants have one 300-800 m pit in a flat floor) made it worse: the giants are flat-floored, not pit-dominated, and flat floors pass a mean-depth test more easily.

**3. Giant closed lakes sit just short of spilling.** On the same replayed frames, the biggest lake with the climate's open-water evaporation scaled (`evap_sensitivity.py`):

| frame | rain mm | x1.0 | x0.85 | x0.7 |
|---|---|---|---|---|
| s42 @144 | 556 | 6.85 closed (all lakes 7.17) | 0.11 open (0.40) | 0.04 open |
| s77 @480 | 1455 | 4.62 closed | 0.05 open | 0.05 |
| s3199 @52 | 1176 | 5.16 closed | 0.87 open | 0.25 |
| s1 @208 | 1273 | 1.20 closed | 0.09 open | 0.07 |
| s1 @288 | 625 | 3.34 closed | 0.14 | 0.21 open |
| s3199 @276 | 285 | 2.47 closed | 3.30 closed | 3.44 open |
| s42 @208 | 1465 | 1.23 closed | 1.51 closed | 1.99 closed |
| s1 @52 (hyperarid) | 32 | 4.15 closed | 5.47 closed | 8.02 closed |

A closed lake spreads over a flat hollow until its evaporation matches its inflow; once it spills, its outlet cuts down (PW-055) and it drains to the valley. So a 15% change in evaporation flips most giant lakes in wet country. The climate gives open water `1.2 x` Oudin PET on top-of-atmosphere radiation, which sees neither clouds nor humidity: 1800-2030 mm/yr at 23-27 C (s3199 @52, s77 @480), against ~1300-1600 mm for humid tropical lakes on Earth, so a lake's extra loss over land evaporation is ~1000-1100 mm instead of a few hundred. That is the likely cause of the ticket's "closed lakes under 1000-1700 mm of rain". It lives in `climate.water_balance`, outside this lane: inbox draft `draft-open-water-evaporation-clouds.md`. Hyperarid giants (s1 @52, 32 mm) grow with less evaporation, as they should; their hollows are the resample/erosion balance above (draft `draft-resolve-makes-hollows.md`).

The L7 case in the ticket (1.4 km deep, 3 Mkm2 in one frame) has an L6 counterpart: the deepest cells of giant lakes are a moat pit beside a single-cell 60 km crust spike (s77 @180, -200 m in a frame), a thinned sediment-filled cell (s3199 @272, 805 m below the lake surface) and plain 36-38 km cells.

## PW-284
Not landed (write-up on the ticket). The moat makes most of L6's closed basins (no moat: inland 6.4 -> 3.7%, lakes 0.60 -> 0.24% of land), but the giant-lake share without it (6.1%) is within seed noise. Sound flexure (share 1, both halves, volume kept, a width from Te) lifts grid-scale crust spikes by nearly their whole root (the 2026-10-15 attempt: 14-40 km peaks), and the only spike-safe forms inside isostasy.py are a yield cap or extra load smoothing, both knobs. What's needed is the ticket's option A in crust.py (stacking and crust flow keep belts smooth at the grid scale) first.

## PW-054 / PW-243 after this lane
| | L6 (8 seeds) | L7 seed 3199 | L7 seeds 21 / 11 | L7, mean of 3 |
|---|---|---|---|---|
| inland drainage, before -> after | 4.91 -> 4.20% | 8.30 -> 5.87% | 8.64 -> 5.69 / 9.56 -> 6.42% | 8.83 -> 5.99% |
| lakes % of land | 0.60 -> 0.43 | 1.03 -> 0.53 | 1.36 -> 0.40 / 1.49 -> 0.63 | 1.29 -> 0.52 |
| giant-lake frames % | 8.85 -> 6.19 | 1.8 -> 10.6 | 13.3 -> 15.0 / 24.8 -> 4.4 | 13.3 -> 10.0 |
| largest lake, median Mkm2 | 0.162 -> 0.112 | 0.24 -> 0.13 | 0.41 -> 0.11 / 0.45 -> 0.19 | 0.37 -> 0.14 |
| highest peak, km | 8.86 -> 8.73 | 8.64 -> 8.85 | 8.56 -> 9.46 / 8.82 -> 8.79 | |
| crust volume end/start | 0.896 -> 0.895 | 0.898 -> 0.900 | 0.921 -> 0.923 / 0.907 -> 0.903 | |

Earth ~18%; the envelope's 8%. L7 drained 1.8x L6's share before and 1.4x after: PW-299 took more off L7 (lakes 1.29 -> 0.52% of land, now close to L6's 0.43%) than off L6, plausibly because a finer grid has more hollow-slope cells for floodplains to build up. So PW-243's gap narrowed, but by L7 falling toward L6, not L6 rising. Seed 21's L7 peak reached 9.46 km after (8.56 before), in one frame, just under the 9.5 km mark (PW-172; chaotic divergence, not a process PW-299 touches). No sound, simple cause showed up beyond what PW-243 and PW-302 already record (cell-mean hollow rules, incision per level). The giant and inland measures move together with the closed lakes (a giant closed lake's catchment is 10-25 Mkm2 of "inland" land), so a fix for the humid evaporation would lower inland drainage further unless basins get deeper; and the resample noise draft suggests part of today's inland share is noise-made hollows.

## Scorecard (L6 seeds 1 / 2, 1 Gyr; `--jobs 3 --threads 2`)
| | before (night baseline, baabbba) | after (this branch) |
|---|---|---|
| Earth climate: Koppen group agreement | 71.0% | 71.0% (no climate change) |
| land at 1 Gyr, seed 1 / 2 | 32.9 / 32.7% | 31.1 / 31.3% |
| crust | 41.8 / 42.7% | 41.2 / 40.9% |
| crust volume end/start | x0.936 / x0.922 | **x0.905 / x0.873** |
| dry (final) | 24.0 / 23.7% | 26.9 / 19.9% |
| ice (final) | 0.9 / 1.2% | 0.3 / 2.5% |
| ocean age | 55.0 / 74.8 Myr | 50.7 / 95.1 Myr |
| land NPP; tree cover | 327 / 338; 29.7 / 28.0% | 415 / 365; 18.7 / 21.7% |

What got worse: continental crust volume on both scorecard seeds (by 3 and 5 points; seed 2 now below the 0.9 envelope). A plausible mechanism: load that used to stay on hollow rims now reaches the floors, fills them, and full basins pass it over the rim toward the sea (PW-280), where some ends on oceanic crust. The 8-seed health sweep shows no change at 500 Myr (0.896 -> 0.895) and L7 none either, so much of it is the two seeds' chaotic divergence; PW-046 owns the slow volume loss. The single-moment values (dry, ice, ocean age, trees) diverge chaotically.

## Goldens
Regenerated: `tests/golden/sim_L4_s1_60myr.json` (the deposition changed).

## Notes
- Replays from a script reproduce the stored run only if `planet` is imported before numpy (its BLAS thread caps): with multi-threaded BLAS the replay diverged by ~24 Myr (5000 cells > 5 m off at 52 Myr).
- Drafts: `draft-open-water-evaporation-clouds.md` (climate), `draft-resolve-makes-hollows.md` (tectonics).
