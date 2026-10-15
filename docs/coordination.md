# Coordination notes

Durable how-to for the coordinating session: worktrees, merging, the server, run costs and showcase recipes. Moved here from `docs/plan_next.md` on 2026-10-14. Open work is on the board (`issue-tracking/`).

## Working rules
- Commit locally only, never push.
- Iterate at level 6 (~5 min per run is fine); level 7 is the showcase default.
- Ask about genuine judgement calls (as `needs-decision` tickets); nudge systems rather than force them. Correct the owner's wrong assumptions rather than building on them.
- No backward compatibility: old runs, worlds and zooms can be deleted whenever a change breaks them (`uv run python -m planet delete run:<id>` / `world:` / `zoom:`, or `--orphans`). Don't keep code paths only so old runs replay.
- Run `uv run pytest` (~5 min; `-m 'not slow'` skips the level-5 envelope worlds) before every commit that touches `planet/`. Run `uv run python tools/scorecard.py` (~11 min) after model changes, and `tools/earth_check.py` after climate changes.

## Parallel agents and merging
Each agent works in its own worktree, `.claude/worktrees/<branch>`, with `data runs worlds zooms grids` symlinked to the main checkout. Agents stop every background task they started (servers, runs, wait loops) before their final report, or they stay listed as running after they're done. Agents report remaining issues as inbox drafts (`issue-tracking/inbox/draft-*.md`, see `issue-tracking/README.md`), and should merge main before reporting.

When an agent reports:
1. Merge its branch into main; fix conflicts.
2. `uv run pytest`. If outputs legitimately changed, regenerate the goldens: `uv run pytest tests/test_golden.py --update-golden`, and commit `tests/golden/*.json`.
3. Triage its drafts: `board.py intake --list`, then `--reject` / `--merge-into` duplicates, then `board.py intake`. Commit.
4. Restart the server if server code (`planet/server.py`, `planet/api.py`) changed.
5. Clean up outputs (owner rule): `uv run python tools/cleanup_outputs.py` lists, `--yes` deletes, everything not referenced by an open ticket, not younger than 12 h (in-flight work), not the Earth world and not a parent of a kept item. The owner is fine with the coordinator running it.

## Viewer server
`planet serve --no-open` on port 8765 (http://127.0.0.1:8765/viewer/). Restart after server changes:

```sh
pkill -f "planet serve --no-open"; nohup uv run python -m planet serve --no-open > $CLAUDE_JOB_DIR/tmp/serve.log 2>&1 &
```

## Run costs (laptop, often shared with 2–4 other jobs)
| Level | Cells | Cell size | `simulate` time | Memory / disk |
|---|---|---|---|---|
| 6 | 41k | ~110 km | ~5–6 min per Gyr | checkpoints ~30–35 MB each; layers ~360–390 MB per Gyr (Oct 15, with vegetation) |
| 7 | 164k | ~55 km | ~20–40 min per Gyr (~1.8 s/Myr under load) | ~0.9 GB RSS (+~0.45 GB of plate arrays for the geological record since landform); layers ~1.4–1.7 GB per Gyr, checkpoints ~130–165 MB each (Oct 15) |
| 8 | 655k | ~28 km | ~3–4 h per Gyr (4.1 h for 1.2 Gyr) | ~3.5 GB RAM; ~17 MB per frame, so use `--every 10`; 3.9 GB on disk |

- At level 8, a world plus 5 highlight zooms takes ~8.5 min.
- `NUMBA_NUM_THREADS=4` is often faster under load on this 4P+4E-core Mac; each parallel kernel launch costs ~40–57 µs.
- The API runs one job at a time and one computation at a time (`api.COMPUTE`: numba's workqueue layer aborts on concurrent parallel kernels; PW-084). Restarting the server keeps its jobs (`.jobs/<port>.json`; queued and running ones run again).
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

Other reference outputs: supercontinent-cycle run 6d9dcf (seed 2, 2 Gyr; worlds ffb5bd assembled, 779b14 dispersed); level-7 runs on the final 2026-10-14 code fe7144 (seed 1) and 103c05 (seed 13); (level-8 run 15b1b0 deleted 2026-10-14; next L8 planned after a batch of tickets closes); Earth reference world dc3732 (`tools/earth_world.py`; re-make after climate changes and delete the old one); ocean and clouds demo world 2085dc (run f59dd6 @ 1000 Myr: salinity, SST, humidity, overturning, cloud cover, sunshine; replaced 9b8200); delta-type demo zooms 00975d / f81832 / ce4b72 on world 0f7abd; lakes demo run 8dc2f2.

After making a showcase: slice its worlds, then `uv run python -m planet highlights <run> --at auto --zoom 6` (or `--at T`) for highlights and pre-made zooms.

## Current state and next steps (2026-10-15; for the coordinator on the new machine)
**State:** everything merged on `main` and pushed to `origin` (GitHub, engma-linguistics/procedural-world-generation); no worktrees, no agents. 215 tests pass. Runs, worlds and zooms are not in git: regenerate them on the new machine (old outputs are out of step with the code anyway; no backward compatibility).
**Done 2026-10-14/15:** finish pipeline (PW-091/193/031), vegetation proposal and model (PW-186/187 steps 1-6: world, run, zoom, climate feedbacks), satellite view (PW-083), glacial isostasy (PW-189), shared ice surface mass balance (PW-190 C, PW-159), weathering thermostat (PW-235), rain-streak and grid-numerics fixes (PW-211/227), foundation round (PW-052/191/046 partly/054 partly/238), hydrology (PW-055/057/201/122/028/237), two small-ticket sweeps.
**Owner decisions to remember:** vegetation decisions in docs/proposals/vegetation.md 9.3 (evolving plant groups; rain recycling; coastal life in PW-188); game attributes (PW-206) parked long-term; satellite view wanted; moons/planet bodies epic PW-216 at the very bottom; foundation round before soils/resources/L8 (owner asked whether base layers are stable).
**Next, in order:**
1. Remake showcase outputs on current code (PW-202): an L7 seed-3199 run, world at `--at auto`, highlights, a few zooms, a time zoom and a finished world. Doubles as the pending L7 checks for PW-172 (peaks below ~9.5 km over 1 Gyr), PW-190 (run ice) and PW-054 (closed basins at L7).
2. Remaining foundation items: PW-240 (run ice in cold eras: narrow climate drift), PW-046 residual thinning, PW-243 (L6/L7 closed-basin gap), PW-242 (back-arc/pull-apart basins), PW-171/170, PW-051 (re-measure, likely resolved), PW-239 (frame lakes on final terrain).
3. Life and land surface: PW-185 soils + PW-212 (vegetation to soils), PW-213 (vegetation in the time zoom), PW-188 coastal life (+PW-209).
4. Then PW-090 finishing pass items and PW-013 rain/ocean (regional rain errors PW-228, clouds PW-232, monsoon PW-233); the L8 run after the foundation and life work.
