# Coordination notes

Durable how-to for the coordinating session: worktrees, merging, the server, run costs and showcase recipes. Moved here from `docs/plan_next.md` on 2026-10-14. Open work is on the board (`issue-tracking/`).

## Working rules
- Commit locally only, never push.
- Iterate at level 6 (~5 min per run is fine); level 7 is the showcase default.
- Ask about genuine judgement calls (as `needs-decision` tickets); nudge systems rather than force them. Correct the owner's wrong assumptions rather than building on them.
- No backward compatibility: old runs, worlds and zooms can be deleted whenever a change breaks them (`uv run python -m planet delete run:<id>` / `world:` / `zoom:`, or `--orphans`). Don't keep code paths only so old runs replay.
- Lanes run `uv run pytest -m 'not slow'` (plus the tests of the area they touched) before committing under `planet/`. The full suite (13–22 min wall at merges in the week of 2026-10-26, under sim load; `test_timezoom_consistency`'s 51-seed fixture is most of it) runs once, by the coordinator, at merge. Physics lanes that touch the run or time zoom also run the slow tests for their area. Run `uv run python tools/scorecard.py` (~11 min) after model changes, and `tools/earth_check.py` after climate changes.

## Parallel agents and merging
Each agent works in its own worktree, `.claude/worktrees/<branch>`, with `data runs worlds zooms grids` symlinked to the main checkout. **Waiting (owner 2026-10-28): agents never end their turn to wait.** Every time a subagent ends its turn with background work still running, the coordinator is woken and re-sends the whole coordinator conversation. Launch sims detached (`nohup ... &`), then wait for them *in the foreground*, inside your own turn, with blocking calls of up to ~9.5 min each, repeated: `timeout 570 bash -c 'for p in $PIDS; do tail --pid=$p -f /dev/null; done'`. That returns when all are gone (exit 0), or after 570 s (exit 124), in which case you call it again. Don't use `run_in_background` or Monitor for waits, and don't end a turn until the work is done and the final report is ready. Agents stop every background task they started (servers, runs, wait loops) before their final report, or they stay listed as running after they're done. Agents report remaining issues as inbox drafts (`issue-tracking/inbox/draft-*.md`, see `issue-tracking/README.md`), and should merge main before reporting.

When an agent reports:
1. Merge its branch into main; fix conflicts.
2. `uv run pytest`. If outputs legitimately changed, regenerate the goldens: `uv run pytest tests/test_golden.py --update-golden`, and commit `tests/golden/*.json`.
3. Triage its drafts: `board.py intake --list`, then `--reject` / `--merge-into` duplicates, then `board.py intake`. Commit.
4. Restart the server if server code (`planet/server.py`, `planet/api.py`) changed.
5. Clean up outputs (owner rule): `uv run python tools/cleanup_outputs.py` lists, `--yes` deletes, everything not referenced by an open ticket, not younger than 12 h (in-flight work), not the Earth world and not a parent of a kept item. The owner is fine with the coordinator running it.

## docs/review retention
docs/ holds only what agents or the owner read. Lane evidence (reports, tables, images, probe scripts) goes under `docs/review/<topic>/` and is deleted when its tickets close; the history keeps it. A review file stays while an open ticket, a core doc (docs/ outside review/, README.md, CLAUDE.md) or code names it, directly or through a kept review page. `uv run python issue-tracking/board.py review [--orphans]` lists each file with what keeps it; `board.py check` warns about the orphans. When you delete them, note the removal on each closed ticket that cited them: `board.py update PW-n "Removed <path> in cleanup; last present at <sha>."` Large screenshot bundles stay outside git.

Reusable harnesses that live in review: the paired A/B judge, `docs/review/base-climate/v1-finish-16/` (`pjudge.py`, `paired.sh`, README; PW-994).

## Viewer server
`planet serve --no-open` on port 8765 (http://127.0.0.1:8765/viewer/). Restart after server changes:

```sh
pkill -f "planet serve --no-open"; nohup uv run python -m planet serve --no-open > $CLAUDE_JOB_DIR/tmp/serve.log 2>&1 &
```

Favourites: the owner stars runs and worlds in the viewer (gallery, list, peoples workbench); lanes needing a test world for peoples or civilization runs should pick from `uv run python -m planet favourites --ids --kind world` (planet/favourites.py).

Jobs (zooms, time zooms, finished worlds) run `--jobs J` at a time (default 4), each in a worker process (`planet/parallel.py`, `spawn`ed, `--threads T` numba threads each, default the cores shared out, at most 8). Workers exit with the server. Same request, same job; jobs start in submission order; two jobs that need the same slice wait on its file lock (`store.lock`, `runs/.locks/`) and the second reuses it. Highlights that aren't cached are sliced and computed in two worker processes of their own (`server.HIGHLIGHT_WORKERS`, started on the first such request, PW-261), so they wait neither for the jobs nor for each other; cached ones are answered in the server process. Measured 2026-10-15 (Threadripper 9960X, load ~5-15): 4 viewer zooms of one unsliced L6 moment took 22.8 s at `--jobs 1`, and 18.3 s cold / 16.5 s warm at `--jobs 4 --threads 4` (the ~6 s slice comes first; the zooms then run at once).

## Run costs (the table: the Mac laptop, often shared with 2–4 other jobs; the Threadripper numbers are below it)
| Level | Cells | Cell size | `simulate` time | Memory / disk |
|---|---|---|---|---|
| 6 | 41k | ~110 km | ~11–13 min per Gyr (store runs 705–802 s/Gyr; 659 s in the Oct 15 sweep under load; ~260 s/Gyr on the idle Threadripper) | checkpoints ~12 MB each (PW-131, PW-306: seed 1 @ 200 Myr 15.3 -> 11.7 MB); layers ~360–390 MB per Gyr (Oct 15, with vegetation) |
| 7 | 164k | ~55 km | ~50 min per Gyr (Oct 15 sweep: 3 seeds at 2965–3038 s, 11 workers at once; the earlier ~20–40 min was idle) | ~0.9 GB RSS (+~0.45 GB of plate arrays for the geological record since landform); layers ~1.4–1.7 GB per Gyr, checkpoints ~45 MB each (PW-306 estimate from L6's share; ~60 after PW-131, ~140 before) |
| 8 | 655k | ~28 km | ~3–4 h per Gyr (4.1 h for 1.2 Gyr) | ~3.5 GB RAM; ~17 MB per frame, so use `--every 10`; 3.9 GB on disk |

- At level 8, a world plus 5 highlight zooms takes ~8.5 min (Mac, zooms one after the other).
- Mac only (4P+4E cores): `NUMBA_NUM_THREADS=4` is often faster under load; each parallel kernel launch costs ~40–57 µs.
- Concurrency comes from processes, not threads (`planet/parallel.py`). Threadripper 9960X (24C/48T), 2026-10-15: one L6 100 Myr run takes 45.7 s at 4 numba threads and 39–40 s at 16–48 (serial Python/numpy dominates), but 8 at once at 2 threads each take 54 s (`planet simulate --seed 1 2 ... 8 --jobs 8 --threads 2`, load ~5; ~6x the throughput on 16 threads), and the coordinator measured 16 at once in 69 s (~9x). `parallel.simulate_many` is the entry point for multi-seed sweeps (PW-246).
- Speed pass, part 1 (PW-256/257/258 checkpoints; bit-identical): Threadripper, 16 numba threads, one job at a time, seed 3199, wall per CLI process (cold start included), before -> after, mean of 2 interleaved pairs at load 4-9 (4 more pairs at load 9-14 gave the same ratios): L6 zoom 1000 km @ 2 km 7.9 -> 4.85 s (1.6x); L7 zoom 1000 km @ 2 km 9.6 -> 6.9 s (1.4x); L6 time zoom 100 kyr 14.8 -> 10.0 s (1.5x); L7 time zoom 100 kyr 42.7 -> 30.8 s (1.4x); L6 run 100 Myr 34.2 -> 25.9 s (1.3x); L7 run 100 Myr 152.7 -> 122.5 s (1.25x). A checkpoint now costs the run's main thread 0.02 s (L6) / 0.08 s (L7) instead of 0.46 / 1.8 s (written by a background thread). The mantle's spherical harmonics (`mantle.basis`, 0.46 s at L6, 2.2 s at L7 per process) are cached on disk next to numba's cache (`planet/tectonics/__pycache__/mantle_basis_*.npy`, 26 / 105 MB; read back in 3 / 11 ms, same bits; PW-258).
- Thread defaults (`parallel.set_default_threads`, applied when `planet` is imported): numba min(16, cores) unless `NUMBA_NUM_THREADS` is set, and always one BLAS thread. OpenBLAS's thread count changes outputs (matrix sums split by thread: L6 runs at BLAS 1 and 8 differ bit-wise; numba's thread count changes nothing), and at its default of one per core it burns CPU: L6 100 Myr 44 s / 410 s CPU at 48 BLAS threads against 41 s / 115 s at 1. Goldens are made at BLAS 1. Tools import `planet` before numpy for this.
- `highlights --zoom 6 --jobs J`: the world is sliced first, then the zooms run at once. L6, 6 zooms of 500-2000 km: 55.5 s one after the other, 19.4 s at `--jobs 6 --threads 2`, 25.9 s at `--jobs 3 --threads 4`.
- `tools/scorecard.py` runs the Earth climate and each seed at once (`--jobs`, `--threads`): seeds 1 2 at 500 Myr took 369 s one after the other (with the old 48 BLAS threads) and 199 s at `--jobs 3 --threads 8`.
- `tools/health.py` (PW-246; run it after model-changing merge batches): the full sweep (8 L6 + 3 L7 seeds, 1 Gyr, 11 workers x 2 numba threads + a determinism re-run) took 50.7 min wall on 2026-10-15 (L6 runs ~11 min each, L7 ~50 min each, under load 6-63 from other agents); measuring and the report take ~16 s. `--quick` (L6, 500 Myr) ~6 min. First results: `docs/review/health/2026-10-15/report.md`.
- `uv run pytest -m 'not slow'`: ~8 min (730 tests, 2026-10-29, under load); the full `uv run pytest` is 13–22 min under load (see Working rules). `tests/conftest.py` pins 4 numba threads per xdist worker (at 16 threads the old suite burned 1406 s of CPU against 554 s at 4).
- The API's jobs run in worker processes, so each has its own `api.COMPUTE` (one computation at a time per process: needed only under numba's workqueue layer, which aborts on concurrent parallel kernels, PW-084). The threading layer is pinned: `tbb` when libtbb loads (system TBB on the Ubuntu box), else `workqueue` (the Mac). Restarting the server keeps its jobs (`.jobs/<port>.json`; queued and running ones run again).
- Shell gotcha: zsh doesn't split `$x` into words, so `uv run python -m planet simulate $args` passes one argument. Use an array or bash. (A level-7 verification run failed silently this way on 2026-10-14.)

## Showcase recipes
All `--every 4` (L8: `--every 10`), default params except as listed. The same seeds don't give the same geography after physics changes, so pick world times afresh, at a representative moment, not the most dispersed one: `planet slice <run> --at auto` (or `highlights <run> --at auto`) picks the keyframe after 300 Myr whose land %, largest landmass, landmass count and total sea level are jointly nearest the run's own medians, among the frames once the run's last plant group has appeared (`highlights.representative_time`; plant groups arrive late in a run, so an earlier world has no grasses, shrubs or flowering trees, PW-634). When that frame falls in an icehouse era, the pick moves to a warm moment of the same era (the era's least-ice quarter, the most typical among them; PW-700), like Holocene Earth; `planet make`'s time zoom then finishes at its latest interglacial (`--now interglacial`). For a deliberately assembled or dispersed world, give the time.

| Name | seed | Myr | `--set` |
|---|---|---|---|
| Earth-like A | 11 | 1000 | — |
| Earth-like B | 12 | 1500 | — |
| Water world, land emerges | 13 | 2000 | `continental_start=0.1 heat_start=2` |
| Land-heavy | 14 | 1000 | `continental_fraction=0.6` |
| Cold world | 15 | 1000 | `tilt=15 climate_offset=-6` |
| Hothouse | 16 | 1000 | `tilt=45 climate_offset=3` (5 under the old star that started at the present Sun and brightened, v1-finish-8; the star now ends at the present Sun, so a run adds no late warming from it) |

Current showcase ids: [wiki/state.md](wiki/state.md). After making a showcase: slice its worlds, then `uv run python -m planet highlights <run> --at auto --zoom 6` (or `--at T`) for highlights and pre-made zooms.

## Usage rules (owner, 2026-10-19)
- Models: Haiku for mechanical work (stale refs, docs), Sonnet for moderately thinky work, Opus for the hard ice-age physics (PW-366, PW-030).
- Agents hand off at ~100 tool calls. At most one physics agent plus one cheap job at a time.
- Each agent gets its done-when criteria and a stop rule of ~5 tuning attempts. It starts long simulations in the background and reads only the summary.

## Acceptance rule (owner, 2026-10-20)
Multi-seed criteria pass when ~70% of seeds pass, not all; outlier worlds are allowed. Use 6-10 seeds when 4 is too few to judge. "Not worse" means the share of seeds passing doesn't drop.


## How to judge a peoples change
A change to the peoples history (planet/lineages/history/, the spread, the sample trees) is judged on many trees, not on dnd at one seed (owner 10-30: the preset must survive other dates, other peoples, more or fewer of them). `tools/peoples_robust.py` (lane 77) runs one try of each variant tree at L6 on the L6 worlds with time zooms (4360a3, af2677) and keeps only the numbers (nothing goes under runs/):
- **base**: dnd and seven_meals at seeds 7, 10, 13; **jitter**: every split and arrival date x a seeded 0.5-2; **subset**: a 5-people and a 3-people cut of dnd, and dnd plus an authored people; **knob**: dwarves, bugbears, gnomes at density x0.5 and x2; **portal**: portal_mode sites (1 and 3 portals); **authored**: the trees in `tools/peoples_robust/trees/*.toml` (each with a one-line rationale: native_fey, mountain_stem, goblin_world, five_peoples, late_humans, even_six, menagerie at one seed; all_at_once is information only and never fails the suite).
- **arms** are named params overrides (`ARMS`: range = today, local = `SPLIT_FOUNDING = "local"`, local_vacate); base, the dnd jitters, subset and authored run under each arm in `--arms` (default range,local).
- `uv run python tools/peoples_robust.py run --out <scratch dir> --jobs 4 --threads 4 --max-load 60` (~145 runs, ~3.5 h at load ~40; 2 jobs if the box is busy; it waits for the load; re-running skips the finished ones), then `report --out <dir>` writes report.md and summary.json. `plan` lists the variants without running them.
- Filters for one arm or a quick screen: `--family base,authored --trees dnd,even_six --seeds 7 --worlds 4360a3 --arms range --params '{"INVADE": 0}' --tag noinv` (`--params` overrides any constant in the history modules and spread, for that run only; `--tag` keeps its results apart).
- To test a change, run it on main and on the branch (or add an arm, as SPLIT_FOUNDING does) into two directories and compare the reports.

What passes: no crash; no authored people dead at the present without a stated reason (authored extinctions excepted); no people over 85% of all people in a tree of 3+; each knob people's share and cells led rising with its own density (x0.5 <= x1 <= x2); and fewer brittle peoples (share swinging over 10x across seeds and jitters, or dead in a run) than before. Shares are of people (presence x density x area, groups rolled up; megafauna and overlays apart), so a sparse people is small by construction: judge it by its swing and its range, not its share. `tests/test_peoples_robust.py` checks the variant builders and one run per arm on the small fake time zoom.

## Current state
See [wiki/state.md](wiki/state.md) (one overwritten page) and [wiki/index.md](wiki/index.md). The dated journals of 2026-10-15 to 2026-10-21 were removed from this file; they are in its git history.

## Earth reference data backup
`data/earth` (git-ignored, ~1.8 GB) holds the downloaded Earth datasets and the caches built from them. On 10-30 a lane's `rm -rf` through a scratch symlink deleted it; it took hours to rebuild, and one source (GPCC v2018) had vanished upstream. Since then:
- a read-only full copy lives off the repo disk at `/home/daniel/backups/procgen-earth/<date>/` (other NVMe), with `SHA256SUMS`;
- `tools/earth_data.SHA256SUMS` (committed) lists the expected checksums.

To restore: `cp -a /home/daniel/backups/procgen-earth/<latest>/* data/earth/ && (cd data/earth && sha256sum -c ../../tools/earth_data.SHA256SUMS)`. Take a fresh dated copy whenever `tools/earth_data.py` changes a source.
