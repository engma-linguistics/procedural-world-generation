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

Discrete volcanoes (PW-001) demo: run 39d004 (seed 13, L7, 500 Myr, `continental_start=0.1 heat_start=2`), world a099c6 (400 Myr), zooms e8fa0e (an island chain, youngest over the plume at -1.9, 35.4), 4e6647 (its atolls, 1 km) and 122cc1 (eroded islands, 1 km); before: world f724bd and its zoom 9834b6 (one big island over a plume).

Other reference outputs: supercontinent-cycle run 6d9dcf (seed 2, 2 Gyr; worlds ffb5bd assembled, 779b14 dispersed); level-7 runs on the final 2026-10-14 code fe7144 (seed 1) and 103c05 (seed 13); (level-8 run 15b1b0 deleted 2026-10-14; next L8 planned after a batch of tickets closes); Earth reference world f8a740 (`tools/earth_world.py`; re-make after climate changes and delete the old one); delta-type demo zooms 00975d / f81832 / ce4b72 on world 0f7abd; lakes demo run 8dc2f2.

After making a showcase: slice its worlds, then `uv run python -m planet highlights <run> --at auto --zoom 6` (or `--at T`) for highlights and pre-made zooms.

## Current state and next steps (2026-10-14 afternoon; for the coordinator after compaction)
**In flight (2026-10-14 evening):** worktrees `.claude/worktrees/<branch>`:
- `landform`: PW-005 data side (PW-006/007/008/009; class layer in runs/worlds/viewer). Zoom batches PW-010–012 come after it merges.
- `zoomsmalls`: PW-062 to PW-070.
- `lakesize`: PW-110 (owner decision A+C: drain threshold scales with basin size) plus the Earth-check Nile drop.
Merged since: hydrofix (PW-058), climfix (PW-102/032/040/034/036), volcanoes (PW-001–004; demo run 39d004, world a099c6, zooms e8fa0e/4e6647/122cc1). Earth world is now f8a740.

**Merged today after the overnight work:** tickets (the board, CLAUDE.md, hook) and quickwins (PW-059/078/081/086/029/045/044/027/105/087 done; PW-106/107 taken in from drafts). `planet slice|highlights <run> --at auto` now picks a representative time; use it for showcase worlds.

**Order of work** (owner-set 2026-10-14: landform classes before the tectonics-quality set; otherwise smallest-easiest first, then biggest impact; avoid files a running agent owns):
1. Now, in parallel with volcanoes (no file overlap):
   - **climate/timezoom batch:** PW-102 (ice persisting after its mountain moves; owner-reported), PW-040, PW-034, PW-036;
   - **hydrology:** PW-058.
2. After volcanoes merges:
   - **PW-005 landform classes**, data side first: PW-006 stratigraphy, PW-007 rocks, PW-008 history, PW-009 classes; then the zoom batches PW-010, PW-011, PW-012;
   - **zoom small batch** PW-062 to PW-070, done before PW-010 starts (both edit `zoom.py`);
   - **tectonics small:** PW-050, PW-048 (keep clear of PW-008's files, or fold them into it).
3. **Tectonics quality:** PW-108 (km-scale cell churn at converging boundaries; may feed PW-053), PW-109 (climate before events, small), PW-053 (sea-level swings), PW-052 (L7 continents ~300 m lower), PW-024 (plate-count nudge), PW-054 (interior basins: the owner-agreed fix for too few closed basins).
4. **Then the L8** (owner approved one, once a big batch of tickets is closed): Earth-like, `--every 10`, ~1.2 Gyr, `--checkpoint-every 300`, plus a matching L7. Use `--at auto` for worlds. It waits for PW-008 (per-cell history is recorded during the run, so an earlier L8 could never get landform classes) and for step 3.
5. **Other big epics:**
   - PW-090 finishing pass (PW-091 first: time zoom from a chosen world → finished world; PW-037 imprint; PW-104 embedded ice ages);
   - PW-013 rain/ocean (PW-014 diagnose first; it can run in parallel with the landform work, since the files differ).
6. **PW-103** (multiscale time) is a vision epic; not scheduled.

**Owner preferences learned today:** L7 is the default; L6 only for quick large-scale tests (weather). The coordinator is the main ticket maker and consumer; the owner looks at specific tickets on request. The owner plans to use worlds for games/TTRPGs with time as a component.
