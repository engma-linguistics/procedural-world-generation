# Ice v2 lane: handoff after stage 1b (PW-555)

2026-10-22. Branch `worktree-agent-a059022acff222eac`. It holds the stage-1 lane (`worktree-agent-aa70af297efc2b900`)
with main 1f0fae4 merged. Read first: `stage-1.md`, section "Stage 1b".

## State
- Zoom-only physics; the run is untouched. Defaults: `margin=ramp`, `orbit_resp=seasons`, `sheet_air=cold`,
  `surface_air=fetch` (new: `icemass.surface_share`, `surface_km` 500; `rest` removed). The consistency test still
  runs the run's rules (`RUN_RULE`).
- `uv run pytest -q`: one failure, the L4 endings test (left 62.5 of 60.7 m). New test
  `test_ice_surface_air_grows_with_its_fetch_over_ice`.
- Stage 1 doesn't pass: Earth's interglacial ice is 11.8–15.5% (bar 9–12); the window mean with area is 3/5; the L4
  test and the recovery bar fail.

## What's settled
- The air lever is spent (3 attempts). Attempt 3 is kept because it improves Greenland's and Antarctica's ice-surface climate.
- Base climate: `baseline=obs` (the full bias removal) still fails the interglacial bar, so a partial fix can't pass it.
- The interglacial floor is a dT-0 hysteresis: with the index off, the ice grows in the first weak summer and stays
  (draft-earth-zoom-does-not-hold-todays-ice-at-dt0).
- L4 test: it also fails at L5 and the quadrature is accurate, so this is no resolution limit (draft updated). Keep it as it is.

## Next (needs the owner's call: a new lever under the stop rule)
- The margin balance at today's climate. Greenland's margin cells are at +0.20 m/yr, and the sheet spreads onto its
  coastal strip under an Eemian orbit. Measure it against an observed SMB (RACMO/MAR, not in the repository's data),
  then test the ramp's lower point, the front rule (408 m bright new edge) and the full-cell icing of near-threshold land.
- The judge is the index-off Earth zoom (scratch `icev2s1b/igprobe.py OUT.npz 60 index=off`, then `igfinal.py`).
  Today's ice should come and go with the orbit, within 20% of its area.
- Suite: add two moments (the fixture on the new main, plus one more) to reach the criteria's 7.
