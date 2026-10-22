# Ice v2 lane: handoff after stage 1c (PW-555)

2026-10-22. Branch `worktree-agent-a339320374f6026c2`: stage 1b's lane (`worktree-agent-a059022acff222eac`) and
main merged. Read first: `stage-1.md`, section "Stage 1c".

## State
- Zoom-only physics; the run is untouched. Defaults: `margin=ramp`, `orbit_resp=seasons`, `sheet_air=cold`,
  `surface_air=fetch`, and new `front=ramp` (bare land the flow reaches is the sheet's outermost `edge_km` 10 km of
  ramp, sampled like a margin's, with the fetch share). `ramp_n` (the ramp's quadrature) stays 0. `RUN_RULE` in the
  consistency test gets `front=edge`.
- New tools: `tools/tz_earth.py --dt0` (the yardstick), `tools/tz_earth.py --greenland` (the margin balance against
  RACMO2.3p3), `tools/earth_data.py` `racmo_greenland_raw` / `earth_greenland_smb` (cached in `data/earth`),
  `tools/h5_reader.py` reads dense netCDF-4 groups.
- `uv run pytest -q`: one failure, the L4 endings test (83.4 of 78.2 m left), unchanged.

## What's settled
- The margin lever is spent (3 attempts): (a) the ramp's quadrature, no effect; (b) `front=ramp`, kept (dT-0 ice
  1.30 → 1.17 of today's: the recovery bar passes); (c) caps in place come from the base climate's cold mountains.
- RACMO: a margin cell's balance near nil is right (outer 110 km +0.15, outer 55 km +0.01). The zoom's margin
  geometry matches; its margin summers are 2-5 C too cold on Greenland's north and east margins.

## Not passing
Maxima −49..−93 m at 5.5–6 C (the honest front makes glacials shallower), give-back 0.51–0.55 on the first glacial,
interglacials 11.4–13.1%, the suite 4/7 with area (bar 5), the L4 test, and the dT-0 ice doesn't follow the orbit.

## Next (the owner's call)
1. The ice-surface air on margins (draft-zoom-ice-surface-too-cold-on-greenland): the remaining surplus is there, but
   the air lever already hit its stop rule. A new attempt needs the owner's yes.
2. Or accept the zoom bars as they stand and move to stage 3 (the run takes the zoom's rules). The deep moments and
   the fixture show the run's ice doesn't match honest margins in either direction; that is run-side.
3. The depth bar: with an honest front Earth needs > 6 C for −80 m. Decide whether ≤ 6 C stays (LGM 4.5–6 C) or the
   index's cooling share (PW-538) is the place to look.
