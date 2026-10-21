# PW-514 handoff (2026-10-21, agent pw514; stopped at ~100 tool calls)

**State:** branch `worktree-agent-ae1d70b30254180ac`. It holds both ice merges, PW-464 (`earth.cycle_ice`)
and the cost cut. Results and diagnosis are in `docs/review/audit/PW-514-batch.md`. The decision draft is
`issue-tracking/inbox/draft-honest-margins-need-sheet-deglaciation.md`.

**Numbers:**
- cold eras 1/10 (main 8/10);
- wall +4% (the bar is +15%);
- Earth zoom maxima -141..-182 m and interglacial ice 16-20%; at 4.5 C cooling, -90..-124 m and 15-18%;
- consistency test +40.7 m.

**Not done:**
- the PW-471 run-moment table;
- scorecard and earth_check;
- the golden update;
- the PW-515 root cause. Its failure depends on the trajectory: it fails only in the full suite on the
  merge state and passes on HEAD. Use `pw514/pan_diag.py`, and `pw514/merge_code/tests/test_health.py`,
  which pickles the sim on failure. Run the suite in order without `-x`, or with the goldens excluded.

**Next step:** an owner decision on the draft. If the choice is to cherry-pick only the cost cut onto
coast_loss (PW-514 A), take the `coast_cost`/`start`-once and `PASS_TOL` hunks from commit b74f2c0 in
`planet/tectonics/earth.py`, without `cycle_ice`. Then re-run `pw514/seeds.sh` (with TIMING=1).
