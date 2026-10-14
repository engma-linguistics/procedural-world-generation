# Coordination notes

Durable how-to for the coordinating session: worktrees, merging, the server, run costs and showcase recipes. Moved here from `docs/plan_next.md` on 2026-10-14. Open work is on the board (`issue-tracking/`).

## Working rules
- Commit locally only, never push.
- Iterate at level 6 (~5 min per run is fine); level 7 is the showcase default.
- Ask about genuine judgement calls (as `needs-decision` tickets); nudge systems rather than force them. Correct the owner's wrong assumptions rather than building on them.
- No backward compatibility: old runs, worlds and zooms can be deleted whenever a change breaks them (`uv run python -m planet delete run:<id>` / `world:` / `zoom:`, or `--orphans`). Don't keep code paths only so old runs replay.
- Run `uv run pytest` (~30 s) before every commit that touches `planet/`. Run `uv run python tools/scorecard.py` (~6 min) after model changes, and `tools/earth_check.py` after climate changes.

## Parallel agents and merging
Each agent works in its own worktree, `.claude/worktrees/<branch>`, with `data runs worlds zooms grids` symlinked to the main checkout. Agents report remaining issues as inbox drafts (`issue-tracking/inbox/draft-*.md`, see `issue-tracking/README.md`), and should merge main before reporting.

When an agent reports:
1. Merge its branch into main; fix conflicts.
2. `uv run pytest`. If outputs legitimately changed, regenerate the goldens: `uv run pytest tests/test_golden.py --update-golden`, and commit `tests/golden/*.json`.
3. Triage its drafts: `board.py intake --list`, then `--reject` / `--merge-into` duplicates, then `board.py intake`. Commit.
4. Restart the server if server code (`planet/server.py`, `planet/api.py`) changed.

## Viewer server
`planet serve --no-open` on port 8765 (http://127.0.0.1:8765/viewer/). Restart after server changes:

```sh
pkill -f "planet serve --no-open"; nohup uv run python -m planet serve --no-open > $CLAUDE_JOB_DIR/tmp/serve.log 2>&1 &
```

## Run costs (laptop, often shared with 2–4 other jobs)
| Level | Cells | Cell size | `simulate` time | Memory / disk |
|---|---|---|---|---|
| 6 | 41k | ~110 km | ~6 min per Gyr | checkpoint ~23 MB (≈229 MB per Gyr) |
| 7 | 164k | ~55 km | ~30–40 min per Gyr (~1.8 s/Myr under load) | ~0.9 GB RSS |
| 8 | 655k | ~28 km | ~3–4 h per Gyr (4.1 h for 1.2 Gyr) | ~3.5 GB RAM; ~17 MB per frame, so use `--every 10`; 3.9 GB on disk |

- At level 8, a world plus 5 highlight zooms takes ~8.5 min.
- `NUMBA_NUM_THREADS=4` is often faster under load on this 4P+4E-core Mac; each parallel kernel launch costs ~40–57 µs.
- The API runs one job at a time (numba kernels aren't thread-safe; PW-084).
- Shell gotcha: zsh doesn't split `$x` into words, so `uv run python -m planet simulate $args` passes one argument. Use an array or bash. (A level-7 verification run failed silently this way on 2026-10-14.)

## Showcase recipes
All `--every 4` (L8: `--every 10`), default params except as listed. The same seeds don't give the same geography after physics changes, so pick world times afresh, at a representative moment, not the most dispersed one: `planet slice <run> --at auto` (or `highlights <run> --at auto`) picks the keyframe after 300 Myr whose land %, largest landmass and landmass count are jointly nearest the run's medians (`highlights.representative_time`). For a deliberately assembled or dispersed world, give the time.

| Name | seed | Myr | `--set` | Current L6 run (2026-10-14) | Worlds |
|---|---|---|---|---|---|
| Earth-like A | 11 | 1000 | — | 01b0f7 | 7c5adf, a873d4 |
| Earth-like B | 12 | 1500 | — | 796a25 | 0433b2, dc3565 |
| Water world, land emerges | 13 | 2000 | `continental_start=0.1 heat_start=2` | f0a1b0 | 4adb0e, 717c6b |
| Land-heavy | 14 | 1000 | `continental_fraction=0.6` | 07fb28 | 6b749b, 607924 |
| Cold world | 15 | 1000 | `tilt=15 climate_offset=-6` | 9abc92 | 04e7a7, a9cfd7 |
| Hothouse | 16 | 1000 | `tilt=45 climate_offset=5` | 19385e | 28cfc4, 4d7207 |

Other reference outputs: supercontinent-cycle run 6d9dcf (seed 2, 2 Gyr; worlds ffb5bd assembled, 779b14 dispersed); level-7 runs on the final 2026-10-14 code fe7144 (seed 1) and 103c05 (seed 13); level-8 run 15b1b0 (pre-fix code); Earth reference world 2f38e3 (`tools/earth_world.py`; re-make after climate changes and delete the old one); delta-type demo zooms 00975d / f81832 / ce4b72 on world 0f7abd; lakes demo run 8dc2f2.

After making a showcase: slice its worlds, then `uv run python -m planet highlights <run> --at auto --zoom 6` (or `--at T`) for highlights and pre-made zooms.
