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

Jobs (zooms, time zooms, finished worlds) run `--jobs J` at a time (default 4), each in a worker process (`planet/parallel.py`, `spawn`ed, `--threads T` numba threads each, default the cores shared out, at most 8). Workers exit with the server. Same request, same job; jobs start in submission order; two jobs that need the same slice wait on its file lock (`store.lock`, `runs/.locks/`) and the second reuses it. Highlights requests still compute in the server process (under `api.COMPUTE`), no longer behind a running job. Measured 2026-10-15 (Threadripper 9960X, load ~5-15): 4 viewer zooms of one unsliced L6 moment took 22.8 s at `--jobs 1`, and 18.3 s cold / 16.5 s warm at `--jobs 4 --threads 4` (the ~6 s slice comes first; the zooms then run at once).

## Run costs (the table: the Mac laptop, often shared with 2–4 other jobs; the Threadripper numbers are below it)
| Level | Cells | Cell size | `simulate` time | Memory / disk |
|---|---|---|---|---|
| 6 | 41k | ~110 km | ~5–6 min per Gyr | checkpoints ~30–35 MB each; layers ~360–390 MB per Gyr (Oct 15, with vegetation) |
| 7 | 164k | ~55 km | ~20–40 min per Gyr (~1.8 s/Myr under load) | ~0.9 GB RSS (+~0.45 GB of plate arrays for the geological record since landform); layers ~1.4–1.7 GB per Gyr, checkpoints ~130–165 MB each (Oct 15) |
| 8 | 655k | ~28 km | ~3–4 h per Gyr (4.1 h for 1.2 Gyr) | ~3.5 GB RAM; ~17 MB per frame, so use `--every 10`; 3.9 GB on disk |

- At level 8, a world plus 5 highlight zooms takes ~8.5 min (Mac, zooms one after the other).
- Mac only (4P+4E cores): `NUMBA_NUM_THREADS=4` is often faster under load; each parallel kernel launch costs ~40–57 µs.
- Concurrency comes from processes, not threads (`planet/parallel.py`). Threadripper 9960X (24C/48T), 2026-10-15: one L6 100 Myr run takes 45.7 s at 4 numba threads and 39–40 s at 16–48 (serial Python/numpy dominates), but 8 at once at 2 threads each take 54 s (`planet simulate --seed 1 2 ... 8 --jobs 8 --threads 2`, load ~5; ~6x the throughput on 16 threads), and the coordinator measured 16 at once in 69 s (~9x). `parallel.simulate_many` is the entry point for multi-seed sweeps (PW-246).
- Speed pass, part 1 (PW-256/257/258 checkpoints; bit-identical): Threadripper, 16 numba threads, one job at a time, seed 3199, wall per CLI process (cold start included), before -> after, mean of 2 interleaved pairs at load 4-9 (4 more pairs at load 9-14 gave the same ratios): L6 zoom 1000 km @ 2 km 7.9 -> 4.85 s (1.6x); L7 zoom 1000 km @ 2 km 9.6 -> 6.9 s (1.4x); L6 time zoom 100 kyr 14.8 -> 10.0 s (1.5x); L7 time zoom 100 kyr 42.7 -> 30.8 s (1.4x); L6 run 100 Myr 34.2 -> 25.9 s (1.3x); L7 run 100 Myr 152.7 -> 122.5 s (1.25x). A checkpoint now costs the run's main thread 0.02 s (L6) / 0.08 s (L7) instead of 0.46 / 1.8 s (written by a background thread).
- Thread defaults (`parallel.set_default_threads`, applied when `planet` is imported): numba min(16, cores) unless `NUMBA_NUM_THREADS` is set, and always one BLAS thread. OpenBLAS's thread count changes outputs (matrix sums split by thread: L6 runs at BLAS 1 and 8 differ bit-wise; numba's thread count changes nothing), and at its default of one per core it burns CPU: L6 100 Myr 44 s / 410 s CPU at 48 BLAS threads against 41 s / 115 s at 1. Goldens are made at BLAS 1. Tools import `planet` before numpy for this.
- `highlights --zoom 6 --jobs J`: the world is sliced first, then the zooms run at once. L6, 6 zooms of 500-2000 km: 55.5 s one after the other, 19.4 s at `--jobs 6 --threads 2`, 25.9 s at `--jobs 3 --threads 4`.
- `tools/scorecard.py` runs the Earth climate and each seed at once (`--jobs`, `--threads`): seeds 1 2 at 500 Myr took 369 s one after the other (with the old 48 BLAS threads) and 199 s at `--jobs 3 --threads 8`.
- `tools/health.py` (PW-246; run it after model-changing merge batches): the full sweep (8 L6 + 3 L7 seeds, 1 Gyr, 11 workers x 2 numba threads + a determinism re-run) took 50.7 min wall on 2026-10-15 (L6 runs ~11 min each, L7 ~50 min each, under load 6-63 from other agents); measuring and the report take ~16 s. `--quick` (L6, 500 Myr) ~6 min. First results: `docs/review/health/2026-10-15/report.md`.
- `uv run pytest`: ~4.7 min wall at 16 or 4 numba threads; `tests/conftest.py` uses 4 (554 s of CPU against 1406 s at 16; ~38 min of system CPU at 48).
- The API's jobs run in worker processes, so each has its own `api.COMPUTE` (one computation at a time per process: needed only under numba's workqueue layer, which aborts on concurrent parallel kernels, PW-084). The threading layer is pinned: `tbb` when libtbb loads (system TBB on the Ubuntu box), else `workqueue` (the Mac). Restarting the server keeps its jobs (`.jobs/<port>.json`; queued and running ones run again).
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
**State (2026-10-15, evening):** on the Ubuntu Threadripper (24C/48T, 183 GB, RTX PRO 6000 96 GB). Python 3.14 (standard build; ~11% faster than 3.11, bit-identical) and numpy 2.5.4; goldens regenerated on this machine (Linux x86 floats differ from the Mac's, and OpenBLAS's thread count changed outputs until PW-260 pinned it to 1). Process-level concurrency merged (PW-250: `planet/parallel.py`, `serve --jobs`, `highlights --jobs`, `simulate --seed A B ... --jobs`, `scorecard --jobs`). 220 tests pass (4.6 min wall, ~9 min CPU). Old Mac outputs are gone; the first showcase on this machine:
- **L7 seed 3199, 1 Gyr: run a1d3b9** (29.7 min, shared with two agents; only ~2.8 cores busy on average). World **592f2a** at `--at auto` = 380 Myr, 64 highlights, zooms dff894 3ac681 e33c3d 01686d b16fb7 02734d (world + highlights + 6 zooms 1 min 38 s, before parallel zooms). Time zoom **86c513** at 380 Myr (a warm era: +-7 m, 0 glacial events; 8.3 min) and finished world **bd9a7a** from it; time zoom **080df3** at 480 Myr (the run's coldest era: lowest sea level -128 m at 126 kyr, 44 glacial events; 19 min) and finished world **fac2af** at its glacial maximum (126 kyr, global 8.0 C).
- L7 checks from a1d3b9: PW-172 3 of 251 keyframes above 9.5 km (944/964/968 Myr, max 10.6 km); PW-240 run sea level down to -288 m at 480 Myr (44 keyframes below -150 m); PW-054 world 592f2a drains 11.2% of land inland (quick measure: following `downstream` to its end; Earth ~18%).
- Speed: PW-249's profile (docs/review/gpu/profile.md): climate ~55% of a run, serial/numpy glue dominates, CPU headroom ~2x (not 5-10x), GPU not worth a second code path yet (PW-253). Speed tickets PW-251..259 under PW-247/249.
**Done 2026-10-14/15:** finish pipeline (PW-091/193/031), vegetation proposal and model (PW-186/187 steps 1-6: world, run, zoom, climate feedbacks), satellite view (PW-083), glacial isostasy (PW-189), shared ice surface mass balance (PW-190 C, PW-159), weathering thermostat (PW-235), rain-streak and grid-numerics fixes (PW-211/227), foundation round (PW-052/191/046 partly/054 partly/238), hydrology (PW-055/057/201/122/028/237), two small-ticket sweeps.
**Owner decisions to remember:** vegetation decisions in docs/proposals/vegetation.md 9.3 (evolving plant groups; rain recycling; coastal life in PW-188); game attributes (PW-206) parked long-term; satellite view wanted; moons/planet bodies epic PW-216 at the very bottom; foundation round before soils/resources/L8 (owner asked whether base layers are stable).
**V1 epic (PW-244, owner-agreed 2026-10-15)** organises what follows: `board.py tree --open` under PW-244. Order: PW-202 showcase remake and review → PW-245 physics audit (high; agents that didn't write the code, one per subsystem) and PW-246 multi-seed health sweep → PW-013 rain → PW-240 run ice → PW-184 life layer → PW-247 speed pass (on the new machine) → PW-248 one-command flow → PW-100 export.
**Next, in order:**
1. Remake showcase outputs on current code (PW-202): an L7 seed-3199 run, world at `--at auto`, highlights, a few zooms, a time zoom and a finished world. Doubles as the pending L7 checks for PW-172 (peaks below ~9.5 km over 1 Gyr), PW-190 (run ice) and PW-054 (closed basins at L7).
2. Remaining foundation items: PW-240 (run ice in cold eras: narrow climate drift), PW-046 residual thinning, PW-243 (L6/L7 closed-basin gap), PW-242 (back-arc/pull-apart basins), PW-171/170, PW-051 (re-measure, likely resolved), PW-239 (frame lakes on final terrain).
3. Life and land surface: PW-185 soils + PW-212 (vegetation to soils), PW-213 (vegetation in the time zoom), PW-188 coastal life (+PW-209).
4. Then PW-090 finishing pass items and PW-013 rain/ocean (regional rain errors PW-228, clouds PW-232, monsoon PW-233); the L8 run after the foundation and life work.
