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

(in progress: see the state section at the end)
