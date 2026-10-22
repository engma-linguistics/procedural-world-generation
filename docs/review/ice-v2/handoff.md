# Ice v2 lane: handoff after stage 0 (PW-555)

2026-10-22. Branch `worktree-agent-abf55f5e1e8b62d98`, on main b35de08 plus the stage-0 commit. Read first:
`docs/review/ice-v2-review.md` (the plan), `docs/review/ice-v2-criteria.md` (success criteria, base assumptions,
the recovery lever), `docs/review/ice-v2/checkpoint-0.md` (main measured).

## Done in stage 0
- Criteria doc (owner's questions; Chandler & Sohl folded in; 300 Myr warm-up per the owner).
- Tools (no output change; goldens unchanged; `uv run pytest -q` passes):
  - `planet/tectonics/diag.py` (opt-in Recorder; hooks in `earth.global_temperature` / `update_climate` only when
    `sim.diag` is set) and `tools/ice_diag.py` (runs, `--summary`, `--plot`, `--fields`, `--moments`);
  - `tools/ice_criteria.py` (old and new bars), used by `tools/health.py` (new columns, basin-term envelope,
    `SPINUP` 300) and `tests/test_ice_diag.py`;
  - `tools/tz_mean.py` (PW-467 window mean; suite = fixture, Earth, and pickles in `$ICE_MOMENTS`);
  - `tools/ice_probe.py --stair` (hysteresis staircase, Earth or a pickled moment);
  - run frame stats carry `sea_ice_m` / `sea_tect_m`; `tools/sealevel.py --run` reads them.
- Plots need matplotlib, which isn't a project dependency: `uv run --with matplotlib python tools/ice_diag.py --plot ...`.
- Inbox drafts: recovery lever, CO2 stock (needs-decision), stellar brightening, criteria adoption (needs-decision),
  rain-vs-temperature run/zoom, default climate icier than Earth (needs-decision), onset check height cut.

## Not done / blocked
- **Earth items** (Earth zoom on the suite, Earth hysteresis staircase): `tools/earth_data.py` must download the
  Köppen grid (`koeppen-geiger.vu-wien.ac.at`), which failed with connection resets. This worktree has no cached
  Earth grid. Run them from a checkout with the cache, or once the site answers:
  `uv run python tools/tz_mean.py earth`, `uv run python tools/ice_probe.py --stair 0 -2 ... 6 --iters 3`.
  (Keep PLANET_DATA unset for Earth: the cache sits under the data root.)
- The PW-467 strict-xfail slow test (`tests/test_timezoom_mean.py`) wasn't written; `tz_mean.py fixture` gives the
  number (−116 m vs tol 53 on main).
- The suite moments are main's (s2@500, s1@600, s5@800, s3199@800, s21@700, L6, 1 Gyr runs); a run-physics change
  re-picks them by state (deep, deep, moderate, mild, warm).

## Next: stage 1 (zoom lane, per the review)
Re-apply `margin_ramp` / `seasonal_k` (246ef40) to the zoom only; measure with `tz_mean.py suite` and the Earth zoom.
Checkpoint 0 adds two things for later stages: the thermostat's weak cold-era answer (A3b) and the icy default (A0)
are run-lane questions for the owner (drafts), and the run's sheets sit in a large snow surplus in deep eras, so
option 2 (the run running the zoom's ice core) should remove ~80 m from deep moments by itself.
