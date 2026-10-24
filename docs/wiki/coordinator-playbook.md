# Coordinator playbook

How to brief a lane and merge its result. Background: [coordination.md](../coordination.md); board rules: [issue-tracking/README.md](../../issue-tracking/README.md).

## Subagent brief boilerplate (every prompt carries these)
Start with the ticket id, the done-when criteria, and the files worth reading. Then:
- Commit locally only; never push. If git has no identity: `-c user.name="Daniel Bishop" -c user.email=lolologist@gmail.com`.
- Merge or fast-forward local `main` first (`git merge --ff-only main`): agent worktrees start from a stale base.
- Never touch port 8765 or `planet serve`. No `pkill` by pattern, no `pgrep -f` loops. Stop every background task you started before the final report.
- Destructive-DB rule, verbatim: "Destructive DB commands (drop, reset, schema:load, truncate, delete_all, pg_restore --clean) are forbidden against any environment OTHER THAN `test`. `RAILS_ENV=test` operations are permitted as long as `RAILS_ENV=test` is set on the command line itself. If you believe a dev/staging/prod destructive command is required, STOP and report BLOCKED."
- Report every remaining issue, follow-up or judgement call as an inbox draft `issue-tracking/inbox/draft-<slug>.md` (template in the README). Never assign PW- ids. Edit tickets only as the brief says (usually one Updates line).
- No temporary fixes, no loosened assertions. Widening a test's search window with the assertions unchanged is fine; thresholds need the owner.
- Run `uv run pytest -q` (background; 7-15 min) before committing under `planet/`; update goldens only for purposeful output changes.
- Stop rule: ~5 tuning attempts, then report. Start long simulations in the background and read only the summary.
- Final report: what was done, numbers, files, anything unclear. Handoff, not a wall of prose.
- Grid level 7 for showcases, 6 for quick tests. Earth is a test analogue, not a target. Thresholds scale to each planet's own orbit and sunshine.
- The culinary-dnd repo is read-only.

## Model tiers and budget
- Opus: ice-age and hard physics. Sonnet: moderate work. Haiku: mechanical work and docs (stale refs, duplicate-helper hunts).
- Budget ~100 tool calls / ~250k context, then hand off; hard cap 400k. The main thread compacts near 300k.
- One serial run-physics lane at a time (outputs-changing work), plus parallel lanes. Always keep one lane on the v2 fun features.
- Flag refactors to the owner for a yes; a Haiku pre-pass hunts duplicated helpers to share.
- Don't reply to interim "agent waiting" notices; act on final reports.

## Merge procedure (per reported lane)
1. Read the report; `git log main..<branch>` and the diff stat.
2. Merge the branch into local `main` (fast-forward the base first; fix conflicts).
3. Start `uv run pytest -q` in the background; when outputs changed on purpose, `uv run pytest tests/test_golden.py --update-golden` and commit `tests/golden/*.json`. Model changes: `tools/scorecard.py`; climate changes: `tools/earth_check.py`.
4. Intake the drafts: `board.py intake --list`, then `--reject` / `--merge-into` duplicates, then `board.py intake`.
5. Place the new tickets (milestone, parent, relates); the owner delegates placement to the coordinator.
6. Update the lane's ticket (status, `Updates` line). Write rulings as `RULING (owner|coordinator): ...` and add a line to [decisions.md](decisions.md).
7. Commit with trailers (the session's Co-Authored-By and Claude-Session lines). Commit locally only.
8. Clean up the lane's worktree and branch (`git worktree remove`, `git branch -d`), and outputs with `tools/cleanup_outputs.py`.
9. Restart the server if `planet/server.py` or `planet/api.py` changed (recipe in coordination.md, run from the coordinator only).
10. Overwrite [state.md](state.md): lanes, counts, showcase ids, last-updated date.

## Owner interaction
- Ask genuine judgement calls as `needs-decision` tickets (options A, B, C, the lean); push back on weak ideas honestly.
- The owner defers geophysics calls and board placement; features over chasing calibration once close enough. Compare pass rates over several re-rolled draws before calling something signal or chaos.
- To pause compute for the owner, stop the parallel lanes first; the serial lane finishes its run.
