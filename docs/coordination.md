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

Jobs (zooms, time zooms, finished worlds) run `--jobs J` at a time (default 4), each in a worker process (`planet/parallel.py`, `spawn`ed, `--threads T` numba threads each, default the cores shared out, at most 8). Workers exit with the server. Same request, same job; jobs start in submission order; two jobs that need the same slice wait on its file lock (`store.lock`, `runs/.locks/`) and the second reuses it. Highlights that aren't cached are sliced and computed in two worker processes of their own (`server.HIGHLIGHT_WORKERS`, started on the first such request, PW-261), so they wait neither for the jobs nor for each other; cached ones are answered in the server process. Measured 2026-10-15 (Threadripper 9960X, load ~5-15): 4 viewer zooms of one unsliced L6 moment took 22.8 s at `--jobs 1`, and 18.3 s cold / 16.5 s warm at `--jobs 4 --threads 4` (the ~6 s slice comes first; the zooms then run at once).

## Run costs (the table: the Mac laptop, often shared with 2–4 other jobs; the Threadripper numbers are below it)
| Level | Cells | Cell size | `simulate` time | Memory / disk |
|---|---|---|---|---|
| 6 | 41k | ~110 km | ~5–6 min per Gyr | checkpoints ~12 MB each (PW-131, PW-306: seed 1 @ 200 Myr 15.3 -> 11.7 MB); layers ~360–390 MB per Gyr (Oct 15, with vegetation) |
| 7 | 164k | ~55 km | ~20–40 min per Gyr (~1.8 s/Myr under load) | ~0.9 GB RSS (+~0.45 GB of plate arrays for the geological record since landform); layers ~1.4–1.7 GB per Gyr, checkpoints ~45 MB each (PW-306 estimate from L6's share; ~60 after PW-131, ~140 before) |
| 8 | 655k | ~28 km | ~3–4 h per Gyr (4.1 h for 1.2 Gyr) | ~3.5 GB RAM; ~17 MB per frame, so use `--every 10`; 3.9 GB on disk |

- At level 8, a world plus 5 highlight zooms takes ~8.5 min (Mac, zooms one after the other).
- Mac only (4P+4E cores): `NUMBA_NUM_THREADS=4` is often faster under load; each parallel kernel launch costs ~40–57 µs.
- Concurrency comes from processes, not threads (`planet/parallel.py`). Threadripper 9960X (24C/48T), 2026-10-15: one L6 100 Myr run takes 45.7 s at 4 numba threads and 39–40 s at 16–48 (serial Python/numpy dominates), but 8 at once at 2 threads each take 54 s (`planet simulate --seed 1 2 ... 8 --jobs 8 --threads 2`, load ~5; ~6x the throughput on 16 threads), and the coordinator measured 16 at once in 69 s (~9x). `parallel.simulate_many` is the entry point for multi-seed sweeps (PW-246).
- Speed pass, part 1 (PW-256/257/258 checkpoints; bit-identical): Threadripper, 16 numba threads, one job at a time, seed 3199, wall per CLI process (cold start included), before -> after, mean of 2 interleaved pairs at load 4-9 (4 more pairs at load 9-14 gave the same ratios): L6 zoom 1000 km @ 2 km 7.9 -> 4.85 s (1.6x); L7 zoom 1000 km @ 2 km 9.6 -> 6.9 s (1.4x); L6 time zoom 100 kyr 14.8 -> 10.0 s (1.5x); L7 time zoom 100 kyr 42.7 -> 30.8 s (1.4x); L6 run 100 Myr 34.2 -> 25.9 s (1.3x); L7 run 100 Myr 152.7 -> 122.5 s (1.25x). A checkpoint now costs the run's main thread 0.02 s (L6) / 0.08 s (L7) instead of 0.46 / 1.8 s (written by a background thread). The mantle's spherical harmonics (`mantle.basis`, 0.46 s at L6, 2.2 s at L7 per process) are cached on disk next to numba's cache (`planet/tectonics/__pycache__/mantle_basis_*.npy`, 26 / 105 MB; read back in 3 / 11 ms, same bits; PW-258).
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

### Ice-age showcase (2026-10-16)
Made on main at f6dfb0c (zooms on 67875ff's code). Seeds 11, 2, 77, 3199 at L7, 600 Myr, default params, `--every 4` (`simulate --seed 11 2 77 3199 --level 7 --myr 600 --jobs 4 --threads 6`, 34-52 min each, all at once). Deepest ice sea level: seed 2 −153 m, 77 −87, 11 −76, 3199 −37. **Seed 2 (run 2c2810)** has the clearest icehouse that ends: ice sea level −34 m at 440 Myr, −151 m at 496-504 Myr (2.2 °C, ice 10.7% of the surface), then deglaciation to −41 m by 560 Myr (11.9 °C). Ice on a south polar continent with a sheet reaching ~45° S over mid-latitude land, plus northern caps. Seed 77's run 1acec2 is kept as a second icehouse (−87 m at 528 Myr, ending at 600 Myr); seeds 11 and 3199 deleted.
- **Run:** http://localhost:8765/viewer/?run=2c2810&t=536
- **Time zoom 98ee98** (2c2810 @ 536 Myr, during the deglaciation: −78 m of ice, 7.1 °C; 1 Myr, 42 glacial events). It first drifts ~−100 m toward bigger ice (PW-241/295), then swings ±30 m with the orbit; its biggest termination is 606 → 622 kyr (−300 → −241 m, ice 10.9 → 8.5% of the surface). http://localhost:8765/viewer/?run=98ee98&t=606 (a second time zoom from 520 Myr swung less and was deleted.)
- **Finished worlds** (sea level below the time zoom's start / absolute; global temperature):
  - **5cefa3** @ 606 kyr, glacial maximum: −135 / −300 m, 5.2 °C, ice 91 Mkm³. http://localhost:8765/viewer/?world=5cefa3.json
  - **bcd6c8** @ 614 kyr, mid-deglaciation: −104 / −270 m, 5.6 °C, 80 Mkm³; big proglacial lakes along the southern sheet (the largest 490,000 km²). http://localhost:8765/viewer/?world=bcd6c8.json
  - **3f6a76** @ 622 kyr, interglacial: −75 / −241 m, 5.8 °C, 69 Mkm³; the ice-dammed lakes have drained. http://localhost:8765/viewer/?world=3f6a76.json
- **Zooms** (open with http://localhost:8765/viewer/zoom.html?id=ID; add `&view=3d` for the 3D view, `&fall=0` to fly to the highest fall):
  - The proglacial lake through the cycle, 2000 km @ 4 km on the southern sheet's margin (~-46, -43): **5142d1** (glacial max, 670,000 km² of lake dammed against the ice), **0595b3** (deglaciation, 545,000 km²; a Lake Agassiz), **c34822** (interglacial: drained, a few small lakes and new rivers across the freshly bared ground).
  - **1d807b**: the same lake at 1000 km @ 2 km, down to the ice front.
  - **d7444e**: a second ice-dammed lake on bcd6c8, 328,000 km², a long trough between the sheet's margin and the plains (1000 km @ 2 km).
  - **7827c2**: the northern ice margin, a 61,500 km² lake along the ice edge and falls where rivers leave it (1000 km @ 2 km).
  - **225c65**: an ice-capped collision range (peaks to ~8 km under the ice) with outlet glaciers down its valleys and a 303 m fall (500 km @ 1 km). 3D: http://localhost:8765/viewer/zoom.html?id=225c65&view=3d&fall=0
  - **39cf84**: interglacial ice-sheet margin over a steep, cold coast: outlet glacier tongues filling the valleys, extinct volcanoes (500 km @ 1 km, world 3f6a76). 3D: http://localhost:8765/viewer/zoom.html?id=39cf84&view=3d
  - **170672**: a great escarpment (crenulated plateau edge over a shield) with an 822 m scarp fall and a dozen more (500 km @ 1 km). 3D: http://localhost:8765/viewer/zoom.html?id=170672&view=3d&fall=0
  - **226c95**: an escarpment and shield above a coast, 17 falls up to 338 m (500 km @ 1 km).
  - Not for showing: 369394 and 634f6c (rectangular vegetation patches, inbox draft draft-zoom-vegetation-straight-edges). No caprock/cuesta site on these worlds came out legible (two tried, flat at 1000 km), and the zoom doesn't carve fjords, drumlins or moraines yet (PW-037, PW-092).

## Current state and next steps (2026-10-15 evening; for the next coordinator session)
**Machine:** Ubuntu Threadripper 9960X (24C/48T), 183 GB, RTX PRO 6000 (unused: GPU path rejected, PW-253). Python 3.14 (standard build), numpy 2.5.4, numba TBB layer; one BLAS thread always (PW-260). Concurrency comes from processes (`planet/parallel.py`: `simulate --seed A B --jobs`, `highlights --jobs`, `serve --jobs`, `scorecard --jobs`, `tools/health.py`). Goldens are made on this machine. Earth data: `data/earth/` (Koppen map from the owner's `earth-data` branch; the vu-wien server resets connections).
**Done today (2026-10-15):** process concurrency (PW-250), speed wins (PW-256/257, checkpoint writer; L7 run ~20-25 min/Gyr), checkpoint fixes (PW-291 replay at checkpoint times, PW-131 checkpoints 141 -> 63 MB at L7), health sweep tool (PW-246), GPU/CPU profile (PW-249), **physics audit** (PW-245: docs/review/audit/README.md ranks the findings) and **all 25 audit fixes merged** (PW-264..288 except PW-284 full flexure, PW-281 B fallback to A; per-area write-ups docs/review/audit/fixes-*.md). Slab drag slowed the plates (4.5 cm/yr, ocean ~55-65 Myr); sea level uses a fixed reference (sits ~+0..150 m, PW-293); ice sheets build from their margins; overturning heat conserved; fresh-water books closed; hillslope level-consistent; frames' rivers/lakes on final terrain; deltas sized right; mass-neutral zoom carving.
**Checks on main after the fixes:** docs/review/after-audit-2026-10-15/ (1 Gyr health sweep 8 L6 + 3 L7 seeds: 327 outlier spells vs 479 before, determinism bit-identical; scorecard; earth_check Koppen group 71% / exact 33% (was 72 / 39: PW-266's honest water books over-wet dry interiors, owned by PW-013); coast_check waves within 2x 24/33, tides 22/26). Baselines before the fixes: docs/review/baseline-2026-10-15/.
**Owner decisions to remember:** vegetation decisions in docs/proposals/vegetation.md 9.3 (evolving plant groups; rain recycling; coastal life in PW-188); game attributes (PW-206) parked long-term; satellite view wanted; moons/planet bodies epic PW-216 at the very bottom; foundation round before soils/resources/L8 (owner asked whether base layers are stable). 2026-10-15: GPU path no (PW-253); climate cadence stays 4 Myr (PW-251); approved all audit leans; **audit standard: sound approximations fine, bandaids not** (memory); **no temporary fixes: fold known-wrong items into the ticket that will fix them, reprioritise freely** (PW-305 -> PW-013).
**In flight when this was written:** (1) PW-308 agent: runs barely glaciate after the fixes (deepest ice sea level -9..-48 m on all 11 sweep seeds, was -96..-384; Earth's LGM ~-120 m), bisecting PW-264/265/266/275/276/277/278 on seeds 11/42/2. (2) Zoom-polish agent: PW-118/123/125/168. Both report to the coordinator; merge, `uv run pytest`, intake drafts, update tickets, clean worktrees.
**Next, in order (V1 epic PW-244):** PW-308 (glaciation) -> PW-013 rain/moisture transport (now also owns dry interiors: Sahara 328 mm vs 35, Australia 837 vs 291; with PW-304, PW-228, PW-026, PW-290) -> PW-054 closed basins (L6 3.5-5.2% inland, L7 6-8%, Earth ~18%) and PW-300 giant lakes (top health outliers) -> PW-202 showcase remake on the settled code (6 recipes above + L7 seed 3199 + Earth world via tools/earth_world.py; the current showcase a1d3b9/592f2a/080df3 predates the audit fixes) -> PW-184 life layer -> PW-248 one-command flow -> PW-100 export. Re-run `tools/health.py` (and the scorecard, earth_check) after every model-changing batch.

### Night batch 2026-10-15/16 (owner away ~8 h; coordinator's plan)
Owner: "knock down the backlog; v1-pass what settles easily; deep dives later; slow and steady if too much changes at once to verify." Plan:
- **Run-physics lane, one change at a time**, each measured with `tools/health.py --quick` before/after on its own branch point, so a regression has one suspect: PW-293+309 (sea-level start, in flight) -> PW-313 with PW-112 (Antarctica decays at dT 0; polar bare-ground summers) -> PW-013 (rain transport; owns dry interiors, PW-304/228/026/290/307) -> PW-054/PW-300/PW-284/PW-299 (closed basins, giant lakes, flexure).
- **Parallel lane** (world/zoom/viewer/infra; no run change): PW-125 zoom drops, viewer replay speed + cell pane, soils proposal (owner review), coastal life PW-188/209, infra batch (PW-303 flaky tests, 294, 306, 258, 261, 292). Next when free: coast batch (PW-075, 230, 297) after coastal life; zoom batch (PW-310, 179, 220) after PW-125; vegetation misses (PW-205, 231, 234).
- Owner decisions today: PW-293 A+B; PW-125 sound creep fix checked against tiled finer zooms; PW-302 wontdo (notes on PW-054); PW-307 option a, scheduled by PW-013; soils as a proposal first.

**Night batch progress (2026-10-16 ~03:30).** Merged on main: PW-308 (leads), PW-293+309 (sea level ~+15 m median), PW-125/310/321/179/298(+319)/327/326/339/340 (zoom: undesigned drops 131 -> ~9 on the 8 showcase zooms, shoreface, reef terrain, halo), viewer replay ~5x faster + cell pane + hints + collapsible summary + gzip/memory (PW-317) + climograph (PW-315) + zoom 3D view (PW-072, PW-342), coastal life (PW-188/209), coast batch (PW-297/323/230), world soils (PW-185) + zoom soils (PW-331) + Earth soil data (PW-314/318), Earth gorge lakes and closed basins from HydroSHEDS (PW-236), Earth carbonate shelves (PW-334), polar climate bundle (PW-335/336/337, PW-332 partly), vegetation batch (PW-234/231/205/220), infra (PW-303 flaky tests fixed, 294, 306, 258, 261), lakes/routing speed (PW-255, bit-identical), world land mask (PW-307/197), docs cleanup, rain diagnosis tool (PW-014).
Baseline after the model batches: docs/review/night-2026-10-16/ (giant-lake frames 2.7-20.4%, inland 3.9-6.2%, Koppen group 71.0% / exact 32.7%).
**Awaiting the owner:** PW-015 moisture-transport proposal (docs/proposals/moisture_transport.md, 6 decisions; coordinator agrees with all leans; prototype on local branch pw015-prototype); PW-320 zoom creep below 2 km (docs/review/zoom-polish/pw320.md; local branch pw320-option-a). New NCEP caches in data/earth (raw_ncep_lhtfl/prate/pwat) not on the earth-data branch.
**Coordinator decisions taken tonight** (on tickets): PW-074 surface wind in the climate (B), PW-336 carried sheet air (A), PW-355 erode over ice surface (A), soils fertility on NPP (C), peat x (1 - alluvial share), sclerophyll summer-drought rule, history-less vegetation start kept, Earth closed basins from HydroSHEDS.
**In flight:** run lane: basins and giant lakes (PW-299, PW-300, PW-284); zoom batch 4 (PW-341, 343, 350, 349, 345); PW-351 earth_check moisture headlines.
**Next:** after the basins lane: PW-355 + PW-354 (world water under ice), PW-344 (route speed, changes down), PW-328, PW-338; then PW-015 once approved; PW-202 showcase remake after PW-015.
