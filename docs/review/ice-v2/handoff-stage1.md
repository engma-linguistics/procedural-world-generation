# Ice v2 lane: handoff during stage 1 (PW-555)

2026-10-22. Branch `worktree-agent-aa70af297efc2b900` (main merged after PW-549). Read first: `stage-1.md`
(what changed, the diagnosis, checkpoint 1), `checkpoint-0.md` (with the Earth addendum), the review's
stage 1.

## State
- Zoom-only physics on the branch (TZParams `margin=ramp`, `orbit_resp=seasons`, `sheet_air=cold`,
  `surface_air=rest`); the run is untouched (`climate.compute`/`air_mass` defaults are bit-identical; the
  consistency test runs the zoom with the run's rules, `RUN_RULE`).
- `uv run pytest -q`: one failure, `test_timezoom_cycle::test_glacials_grow_ice_and_endings_melt_it_fast`
  (L4 ending keeps 25 of 29 m). Goldens: the L4 golden is a run golden, not affected; not regenerated.
- Earth at 5.5 C: cycles, maxima (−108..−138), give-back (0.64–0.91), cooling pass; interglacial ice 12–15%
  of land fails (bar 9–12). Window mean 3/6 on the old moments.
- Suite moments regenerated on the new main (PW-549 changes every trajectory): scratchpad
  `icev2s1/runs/` (seeds 2 1 5 3199 21, moments every 40 Myr from 300). Re-pick deep/deep/moderate/mild/warm
  by `sea_ice_run`: s5@420, s1@780 (deep), s2@660, s3199@900, s21@620. Window mean: main's zoom rules 1/5,
  stage 1 4/5 (stage-1.md). Point `ICE_MOMENTS` at a folder of those five for `tools/tz_mean.py suite`.

## The lever and its stop rule
Lever: the carried sheet air and the ice surface's own air (2 attempts used; one left).
- 1: `sheet_air=cold` (small). 2: `surface_air=rest` (kept: endings work on Earth).
- Remaining evidence: Greenland today is still ~4 C too cold at its margins (−6.1 vs −2.1 observed) and
  ~3 C inland under the zoom's ice rule; the climate's own air there is right (−3.0 vs −4.2). Removing
  `ice_cool` and the local damping altogether matches Greenland, but makes Earth's glacials too shallow
  (−47 m) and Antarctica's interior +6 C too warm (its base bias, PW-039, which `anchor=obs` corrects on
  Earth's start ice only).
- Attempt 3, if taken: the local terms by the cell's own iced surroundings at the scale of the air that
  touches it (a smaller kernel than `SHEET_KM`), checked on Greenland's observed margins and Antarctica.
  If it fails, write it up and move to the base climate (root cause 5), as the review's stop rule says.
- The L4 test: at ~440 km cells the ramp is a dome; the moment deglaciates with no carried air (0.60).
  Moving the test to L5 is a judgement call (needs-decision draft), not done.

## Not done
- Earth interglacial ice share (12–15%) and the L4 test (above).
- The 10-seed check (not needed: the run is unchanged); the fixture on the new main.
- Finished worlds from a stage-1 zoom use the run's ice-surface climate (draft).
