# v1-finish-4: PW-736 (the time zoom's margins in km) and the v1 showcase (PW-202) (2026-10-24)

Branch `worktree-agent-a9ce28d11fbaf1484`, from main 1f0fae4 + v1-finish-3. Scripts here; raw outputs in the session
scratchpad `v1f4/` (`tz/`: tzlevel.py's time zooms; `show/`: the showcase's tracks and remakes). CPU: at most ~12
threads of my own beside the four showcase makes (~20).

## PW-736: the cause

The time zoom's default `margin="edge"` (`timezoom/sim.py` prepare_surface) took a sheet's margin, whose snow and melt
are its edge's (at most edge_h ~400 m thick), as the one ring of iced cells next to bare land: ~120 km at L6, ~60 km
at L7, exactly the run's rule before PW-725. At L7 the ice 60-120 km in from the edge counted at its full thickness,
~1-2 km, so ~4-10 C colder by the lapse rate than as margin: half the ablation zone.

`tzlevel.py` takes one planet moment (an L7 run's keyframe, `source_from_run`) and the same moment averaged onto the
L6 grid (as v1-finish-3's eqcurve.py: L6 cells are L7's first n6 vertices, each the mean of the L7 cells nearest it),
and runs the same 300 kyr time zoom on each (same seed and moment: the same orbits and glacial-index draw; the start's
ice is the same keyframe ice). Nothing is saved to the store. Variants: L6; L7old (the band one ring, the rule before
this fix: MARGIN_KM patched to 1 km); L7 (the fix). Ice volume in million km3 after the first 20 kyr:

| moment | variant | ice start / glacial max / interglacial min / mean | iced cells % max / min / mean | sea level change min / max (m) |
|---|---|---|---|---|
| 89c2ab @ 700 | L6 | 19.4 / 36.9 / 3.8 / 20.5 | 4.85 / 1.00 / 3.08 | -45 / +43 |
| | L7old | 19.4 / **51.9 / 16.0 / 40.4** | 5.43 / 2.24 / 4.48 | -88 / +17 |
| | L7 (fix) | 19.4 / 40.7 / 5.3 / 23.2 | 5.05 / 1.18 / 3.38 | -57 / +40 |
| 6ca373 @ 804 (icy seed) | L6 | 16.5 / 112.3 / 21.2 / 74.3 | 12.00 / 3.53 / 8.71 | -258 / 0 |
| | L7old | 16.5 / **122.3 / 31.8 / 91.9** | 12.87 / 4.69 / 9.84 | -291 / 0 |
| | L7 (fix) | 16.5 / 114.5 / 22.9 / 76.1 | 12.41 / 3.83 / 8.85 | -267 / 0 |

Same forcing (glacial index max 0.89 / 0.87 at both levels; dT_global within 0.4 C, the rest the ice's own feedback).
Before the fix an L7 time zoom held 1.2-2x L6's mean ice and **1.5-4x its interglacial ice**: the finished world's
"now" (the latest interglacial, PW-700) kept 16 Mkm3 of ice where L6 kept 4 on 89c2ab. With the fix L7 is within
3-14% of L6 at every stage (mean 1.13x and 1.02x), the rest the relief's resolution, as PW-725 found for the run.

## PW-736: the fix

`prepare_surface`'s 'edge' margins are now the run's margin band, `earth.margin_band` (the ice within MARGIN_KM =
120 km of bare land, as rings of cells, round(120 / spacing), at least one): one ring at L6 and coarser, two at L7.
The same rule and constant as the run's (PW-725), not a per-level factor. 'ramp' (PW-460) was already in km (the
cell's width) and is unchanged; so is the front (bare land the flow reaches: a new edge, one ring by definition).

- L6 and coarser: bit-identical (one ring; `test_ice_margin_band_level_consistent` asserts the band is one ring at
  L6). Full `uv run pytest -q` green, goldens unchanged (the L4 time zoom goldens included).
- Test: `test_edge_margins_are_the_run_margin_band` (tests/test_timezoom.py): with the band two rings wide the second
  ring's thick ice counts at edge_h, lapse-rate warmer by exactly the ice it doesn't count, and nothing else changes.
- earth_check / scorecard: neither reads the time zoom (Earth's time zoom, tools/tz_earth.py, is L6: unchanged).

**Decision (delegated, evidence clear): fixed.** It materially changes L7 time zooms, so the showcase's time zooms,
worlds and zooms are remade below.

## The v1 showcase (PW-202)

Four `planet make --level 7` runs (random seeds, earthlike, 1 Gyr) made by v1-finish-3 from its worktree (PW-725 in,
PW-736 not). Their runs stand (PW-736 is time zoom only); their time zooms, worlds and zooms were made before the fix
and are deleted (worlds 8d6d85 7243ca 87c1b0 a5d045 with their zooms; time zooms d9c808 ac8532 11cd95 ff1500).
`remake.py` re-ran make's chain after the simulation on this branch (make.make resumed from the run: same
representative moment, 300 kyr time zoom, now = interglacial, highlights, 4 zooms), then `planet resources` and
`planet coast` on the world. (A first try reused the old time zooms: api.timezoom_job finds an existing one with the
same request, so the old outputs had to go first.) c6c24f's four highlight zooms had no islands, so it got a fifth on
its archipelago.

`showcheck.py` (now's glacial index and ice, layers, islands = land masses inside a zoom, deposits) and
`runtrack.py` + v1-finish-3's `passrate.py` (LEVEL=7) on the runs' keyframes (it reproduces the old showcase's
70/79/63/67%):

| seed | run | time zoom | world | zooms | now | icehouse 300-1000 Myr |
|---|---|---|---|---|---|---|
| 957317 | 656f66 @964 | ad26f3 | bacb95 | 5397aa e2c8db 8f040a a7081c | 300 kyr, index 0.00, 7.7 Mkm3 (tz 7.3-18.7), 13.9 C | 64% ICEBOX -> F |
| 619496 | fdb41e @1000 | bd6c87 | c6c24f | baab22 81fd07 4b8885 fd3051 70fe22 | 204 kyr, index 0.00, 38.6 Mkm3 (tz 10.2-123), 16.5 C | 42% -> F (by 2 points) |
| 583167 | 9882e7 @936 | 06667e | f2a9a4 | d0951d 7b8ddc 9e74dd 1b1daa | 298 kyr, index 0.02, 0.4 Mkm3 (tz 0.4-7.6), 19.4 C | 22% ok |
| 639472 | 27929a @944 | 21b68b | 61ac61 | 103ed4 8c58d0 c2c627 2c2557 | 282 kyr, index 0.00, 17.0 Mkm3 (tz 5.0-71.6), 16.8 C | 60% ICEBOX -> F |

Every world's now is an interglacial (glacial index 0.00-0.02, PW-700); each has the 26 resource layers and the coast
layers; every zoom has deposits (93-2907), and each world has zooms with islands (8f040a 2; 7b8ddc 4, 9e74dd 1;
70fe22 73; 2c2557 8, 8c58d0 7). c6c24f's interglacial still holds 39 Mkm3 (an icehouse planet's interglacial, like
Earth's 30): fine as a world.

Against the owner's bar (icehouse <= ~40%, outliers OK, ~70% of seeds passing) the four histories pass **1/4**
(2/4 if 42% counts as ~40%), median 51%; the two ICEBOX flags are deep ice on 30.1% of the updates, at the 30% line.
The same four seeds at L6 (tools/ice_diag.py, same code, scratchpad `v1f4/l6/`): 48, 23, 0, 32% -> **3/4**, median
28%. Every seed is 16-28 points icier at L7. Pooled with v1-finish-3's 8 L7 draws on the same run code: 6/12 pass
(7/12), median ~41%. PW-725 took the level effect from ~+35 points to ~+10-15, not to zero: inbox draft
`draft-l7-runs-still-icier-same-seeds.md` (v1, high).

Superseded (not deleted, for the coordinator): the previous L7 showcase, runs 89c2ab 6ca373 8b1617 7f4f06 (worlds
a95cdc 09262b 730669 d86d34, time zooms 04e831 d07f9f 7ff0cd 0e0301), made with the one-ring rule in both the run
and the time zoom.

## Verdict

PW-736: fixed. The v1 showcase chain works end to end at L7 on the fixed code (runs, carved time zooms, interglacial
worlds with resources and coasts, zooms with islands and deposits). The L7 climate histories are not yet at the
owner's bar (1-2 of 4 here, ~50-58% over 12 draws, vs L6's 3 of 4 on the same seeds): v1 is done for L6 and for the
L7 pipeline; L7's long-run climate needs the remaining level effect fixed (the draft) or the owner's acceptance of
these four as the showcase.
