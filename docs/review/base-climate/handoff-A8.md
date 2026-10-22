# Lane A handoff A8 (2026-10-22)

## State of the branch
- Main and PW-582 attempt 1 (ee0cc87) are merged in. PW-582 attempt 2 is commit fb332ca (stages.md, "PW-582,
  attempt 2"), with the scorecard line after it.
- Ruling 1 is done: `test_run_lakes` searches 60 steps, and its draft is deleted. It passes.
- Attempt 2 is **not merge-ready**. `test_timezoom_consistency::test_ice_at_index_zero_is_the_runs` fails, −26.0 m
  against 25. Its fixture is a full 300 Myr L5 run, so the change gives a different world: 6 plates against 13, and
  sea level −314 m against +5. See `issue-tracking/inbox/draft-timezoom-index-zero-test-chaotic.md`
  (needs-decision). Every ocean change in this lane will keep hitting it, PW-579 included.
- The bar is not met. The Barents doesn't move. Why, and what attempt 3 could be, is in
  `draft-barents-still-frozen-after-pw582.md` (updated): the sill rule treats the Barents shelf as a strait, and a
  branch that only carries what sinks there cools too fast.
- PW-579 and stage 3 are not started. The notes in `handoff-A6.md` still stand.

## Tools (`/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/laneA8/`)
These are A7's tools, pointed at this worktree (`meas.sh`, `pr.sh`, `nr.sh`, `probe.py`, `nordic.py`), plus:
- `nordic.py` now also maps `lid`, `rhoc-1027` (the coarse winter density), `deep-1027`, `t_in` and `s_in-34`.
- `depth.py`: the fine and L5 depths of the Nordic and Barents seas, and of named straits.
- `walin.py`: option B's heat-budget check, per sinking cell.
- `sl.py`: the `cold_moment` time zoom's last-frame stats, outside pytest (~60 s).
