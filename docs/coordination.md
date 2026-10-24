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
- `uv run pytest`: ~4.7 min wall at 16 or 4 numba threads; `tests/conftest.py` uses 4 (554 s of CPU against 1406 s at 16; ~38 min of system CPU at 48).
- The API's jobs run in worker processes, so each has its own `api.COMPUTE` (one computation at a time per process: needed only under numba's workqueue layer, which aborts on concurrent parallel kernels, PW-084). The threading layer is pinned: `tbb` when libtbb loads (system TBB on the Ubuntu box), else `workqueue` (the Mac). Restarting the server keeps its jobs (`.jobs/<port>.json`; queued and running ones run again).
- Shell gotcha: zsh doesn't split `$x` into words, so `uv run python -m planet simulate $args` passes one argument. Use an array or bash. (A level-7 verification run failed silently this way on 2026-10-14.)

## Showcase recipes
All `--every 4` (L8: `--every 10`), default params except as listed. The same seeds don't give the same geography after physics changes, so pick world times afresh, at a representative moment, not the most dispersed one: `planet slice <run> --at auto` (or `highlights <run> --at auto`) picks the keyframe after 300 Myr whose land %, largest landmass, landmass count and total sea level are jointly nearest the run's own medians, among the frames once the run's last plant group has appeared (`highlights.representative_time`; plant groups arrive late in a run, so an earlier world has no grasses, shrubs or flowering trees, PW-634). When that frame falls in an icehouse era, the pick moves to a warm moment of the same era (the era's least-ice quarter, the most typical among them; PW-700), like Holocene Earth; `planet make`'s time zoom then finishes at its latest interglacial (`--now interglacial`). For a deliberately assembled or dispersed world, give the time.

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
**Checks on main after the fixes:** docs/review/after-audit-2026-10-15/ (removed; see git d32f7fa) (1 Gyr health sweep 8 L6 + 3 L7 seeds: 327 outlier spells vs 479 before, determinism bit-identical; scorecard; earth_check Koppen group 71% / exact 33% (was 72 / 39: PW-266's honest water books over-wet dry interiors, owned by PW-013); coast_check waves within 2x 24/33, tides 22/26). Baselines before the fixes: docs/review/baseline-2026-10-15/ (removed; see git d32f7fa).
**Owner decisions to remember:** vegetation decisions in docs/proposals/vegetation.md 9.3 (evolving plant groups; rain recycling; coastal life in PW-188); game attributes (PW-206) parked long-term; satellite view wanted; moons/planet bodies epic PW-216 at the very bottom; foundation round before soils/resources/L8 (owner asked whether base layers are stable). 2026-10-15: GPU path no (PW-253); climate cadence stays 4 Myr (PW-251); approved all audit leans; **audit standard: sound approximations fine, bandaids not** (memory); **no temporary fixes: fold known-wrong items into the ticket that will fix them, reprioritise freely** (PW-305 -> PW-013).
**In flight when this was written:** (1) PW-308 agent: runs barely glaciate after the fixes (deepest ice sea level -9..-48 m on all 11 sweep seeds, was -96..-384; Earth's LGM ~-120 m), bisecting PW-264/265/266/275/276/277/278 on seeds 11/42/2. (2) Zoom-polish agent: PW-118/123/125/168. Both report to the coordinator; merge, `uv run pytest`, intake drafts, update tickets, clean worktrees.
**Next, in order (V1 epic PW-244):** PW-308 (glaciation) -> PW-013 rain/moisture transport (now also owns dry interiors: Sahara 328 mm vs 35, Australia 837 vs 291; with PW-304, PW-228, PW-026, PW-290) -> PW-054 closed basins (L6 3.5-5.2% inland, L7 6-8%, Earth ~18%) and PW-300 giant lakes (top health outliers) -> PW-202 showcase remake on the settled code (6 recipes above + L7 seed 3199 + Earth world via tools/earth_world.py; the current showcase a1d3b9/592f2a/080df3 predates the audit fixes) -> PW-184 life layer -> PW-248 one-command flow -> PW-100 export. Re-run `tools/health.py` (and the scorecard, earth_check) after every model-changing batch.

### Night batch 2026-10-15/16 (owner away ~8 h; coordinator's plan)
Owner: "knock down the backlog; v1-pass what settles easily; deep dives later; slow and steady if too much changes at once to verify." Plan:
- **Run-physics lane, one change at a time**, each measured with `tools/health.py --quick` before/after on its own branch point, so a regression has one suspect: PW-293+309 (sea-level start, in flight) -> PW-313 with PW-112 (Antarctica decays at dT 0; polar bare-ground summers) -> PW-013 (rain transport; owns dry interiors, PW-304/228/026/290/307) -> PW-054/PW-300/PW-284/PW-299 (closed basins, giant lakes, flexure).
- **Parallel lane** (world/zoom/viewer/infra; no run change): PW-125 zoom drops, viewer replay speed + cell pane, soils proposal (owner review), coastal life PW-188/209, infra batch (PW-303 flaky tests, 294, 306, 258, 261, 292). Next when free: coast batch (PW-075, 230, 297) after coastal life; zoom batch (PW-310, 179, 220) after PW-125; vegetation misses (PW-205, 231, 234).
- Owner decisions today: PW-293 A+B; PW-125 sound creep fix checked against tiled finer zooms; PW-302 wontdo (notes on PW-054); PW-307 option a, scheduled by PW-013; soils as a proposal first.

**Night batch progress (2026-10-16 ~03:30).** Merged on main: PW-308 (leads), PW-293+309 (sea level ~+15 m median), PW-125/310/321/179/298(+319)/327/326/339/340 (zoom: undesigned drops 131 -> ~9 on the 8 showcase zooms, shoreface, reef terrain, halo), viewer replay ~5x faster + cell pane + hints + collapsible summary + gzip/memory (PW-317) + climograph (PW-315) + zoom 3D view (PW-072, PW-342), coastal life (PW-188/209), coast batch (PW-297/323/230), world soils (PW-185) + zoom soils (PW-331) + Earth soil data (PW-314/318), Earth gorge lakes and closed basins from HydroSHEDS (PW-236), Earth carbonate shelves (PW-334), polar climate bundle (PW-335/336/337, PW-332 partly), vegetation batch (PW-234/231/205/220), infra (PW-303 flaky tests fixed, 294, 306, 258, 261), lakes/routing speed (PW-255, bit-identical), world land mask (PW-307/197), docs cleanup, rain diagnosis tool (PW-014).
Baseline after the model batches: docs/review/night-2026-10-16/ (removed; see git d32f7fa) (giant-lake frames 2.7-20.4%, inland 3.9-6.2%, Koppen group 71.0% / exact 32.7%).
**Awaiting the owner:** PW-015 moisture-transport proposal (docs/proposals/moisture_transport.md, 6 decisions; coordinator agrees with all leans; prototype on local branch pw015-prototype); PW-320 zoom creep below 2 km (docs/review/zoom-polish/pw320.md; local branch pw320-option-a). New NCEP caches in data/earth (raw_ncep_lhtfl/prate/pwat) not on the earth-data branch.
**Coordinator decisions taken tonight** (on tickets): PW-074 surface wind in the climate (B), PW-336 carried sheet air (A), PW-355 erode over ice surface (A), soils fertility on NPP (C), peat x (1 - alluvial share), sclerophyll summer-drought rule, history-less vegetation start kept, Earth closed basins from HydroSHEDS.
**In flight:** run lane: basins and giant lakes (PW-299, PW-300, PW-284); zoom batch 4 (PW-341, 343, 350, 349, 345); PW-351 earth_check moisture headlines.
**Next:** after the basins lane: PW-355 + PW-354 (world water under ice), PW-344 (route speed, changes down), PW-328, PW-338; then PW-015 once approved; PW-202 showcase remake after PW-015.

## Current state and next steps (2026-10-16 afternoon; supersedes the evening/night notes above where they differ)

**Working model that worked well (keep it):** one *serial run-physics lane* (anything that changes `simulate` outputs: tectonics, climate, ice, surface/hydrology run terms), each change measured with `tools/health.py --quick` before/after on its own branch point so a regression has one suspect; and several *parallel lanes* that don't change run physics (zoom terrain, world-level layers, viewer/3D, highlights, Earth-data tools, infra), each in its own worktree, kept to disjoint files. Merge each lane as it reports: pytest, intake drafts, close tickets, remove worktree, restart the server if server/zoom/world code changed. Commit from `/home/daniel/personal/repos/procedural-world-generation` (the ~/personal path carries the git identity). If the owner needs a quiet machine: SIGSTOP the project's python/pytest processes (not `planet serve`), message each agent PAUSE, re-sweep for new ones; SIGCONT + RESUME afterwards.

**In flight at this point:** PW-015 rain rework (run lane). Stages 1 (physical-time conservative transport: L6/L7 agree, mass residue ~0) and 2 (storm eddies, bulk sea evaporation, Penman lakes = PW-358) built on branch `worktree-agent-adc23e25e68fd8311`; stage 2 dries the humid subtropics (SE USA 277 mm vs 1328, Pampas 217 vs 943; winter east-coast vapour ~20% of NCEP) and makes generated planets drier/icier, so it is NOT merged. The agent is (1) measuring stage 1 alone (merge it alone if it stands), (2) finding the missing east-coast moisture source (+ PW-352 warm summers). Write-up docs/review/audit/pw015-rain.md. Prototype branch `pw015-prototype` kept until PW-015 closes.

**Done since the night notes (all on main):** volcano status (active/dormant/extinct) + highlights (supervolcano, shield, flood basalt, volcanic field, barrier reef, carbonate bank); 3D relief on globe/map (time zooms replay ice in 3D), zoom 3D polish + river fly-through, 3D mesh follows rivers (PW-375), receiver layer (PW-373; all 19 kept zooms rebuilt); time-zoom ice shelves with flotation, buttressing, sub-shelf melt (PW-367); icehouse lag fix (PW-364: deepest -219 m); crust volume (PW-046); faster routing (PW-344); scattered start (PW-328); zoom vegetation straight edges + equator season seam (PW-374); GFED/MOD17/MOD44B Earth vegetation data (PW-204); ice-age showcase (run 2c2810, time zoom 98ee98, see the showcase section).

**Owner decisions (2026-10-16):** PW-015 approved as coordinator sees fit; PW-320 B (keep crisp fine zooms); PW-368 parked (someday); PW-359, PW-366 parked by coordinator; PW-367 A (done). Owner likes the 3D views a lot; prefers features over calibration chasing once close enough; isn't a geophysicist and delegates physics calls (but wants pushback on weak ideas). Four seasons instead of two half-years: revisit only if, after PW-015, the moisture budget shows leftover errors concentrated in bimodal-rain regions.

**Awaiting the owner:** PW-129 nested fine zoom (docs/proposals/nested_fine_zoom.md, three questions; coordinator agrees with the leans: 500 px / 50 km at 100 m, built from a parent zoom only, falls keep the parent's heights).

**Next steps, by lane (parallelisable across lanes; serial within the run lane):**
- *Run lane (serial):* finish PW-015 (stage 1 merge; then stage 2 with the east-coast moisture fix; stage 3 shower trigger with PW-352; PW-016 spin-up rule once Atlantic E-P-R >= +0.25 Sv); then PW-380 equatorial seasonal swing; PW-332/313 Antarctic margin snow (should follow PW-015's storm eddies); PW-300 giant lakes re-check; PW-118 continental volcano height cap (TOP_MAX); PW-212 coal from peat (soils step 7); PW-359 resampling hollows re-measure; PW-284 flexure (needs coarser-than-cell treatment).
- *Zoom lane:* PW-129 fine zoom once the owner answers (high-value for 3D); PW-383 forearc plateaus; PW-370 delta finger; PW-349-style cell-mean checks; glacial landforms in zooms (PW-037 moraines/fjords/drumlins, PW-092) for the ice-age showcase; PW-177 dunes (parked).
- *Viewer/3D lane:* PW-376 done; next: fine-zoom tile (with PW-129), PW-371 globe paint cache locality, PW-316 60 fps replay (only if needed), glacial landforms' look in 3D, a time-zoom ice replay in the zoom 3D view.
- *World layers lane:* PW-377 vegetation fire/NPP geography vs GFED/MOD17; PW-347 boreal fire; PW-330 soils Earth agreement; PW-329 soil climate memory; PW-206 game attributes (owner parked long-term); PW-385 time-zoom warm deep water for shelf melt.
- *Highlights/Earth-data lane:* PW-382 done; more highlight kinds the owner may enjoy (glacial lakes, escarpments, fjords once zooms make them); PW-351 done; PW-354 done.
- *Showcase:* PW-202 remake of the standard showcase runs after PW-015 lands (L7), plus a second ice-age showcase on post-PW-015 code.

## Current state and next steps (2026-10-16 evening; supersedes the sections above where they differ)

**Since the afternoon:**
- PW-015 rain: stage 1 (conservative physical-time transport) merged alone under the owner's relaxed bar. Stage 2 and option A (boundary layer) missed the bar and are parked on branches pw015-prototype, pw015-wip and pw015-optA (handoff docs/review/audit/pw015-handoff.md). PW-015 is blocked on PW-352; rain is now a calibration pass, not a v1 gap.
- PW-387: rain kernel warm start, L7 climate update ~2.3 s.
- PW-380: July/January kept at the equator. The orbital swing size is PW-398, decided: damp it.
- PW-129 nested fine zooms (planet/zoom_fine.py), with the 3D tiles (viewer/zoom3d_place.js), "Fine zoom here", resolution-based exaggeration and canopy displacement.
- PW-390: gorges with no spires.
- Showcases: fall 170672 -> 97b3e7 -> 3e74b0 / b3c260; volcano 193d10 -> 6ea4c1 -> bdff35; lagoon 3ac681 -> a0097b -> 652295.
- Tests run in parallel by default (pytest-xdist, `-n 16 --dist loadscope`): ~2 min instead of 7.5. Use `-n0` for a serial run.
- V1 reassessment: `docs/review/v1-reassessment-2026-10-16.md` (removed 2026-10-23; see git d32f7fa). PW-244 rescoped with the owner (see its updates).
- Stray test fine zoom 543568: an agent's delete was blocked by permissions. The owner decides; don't delete it on an agent's behalf.

**Usage rule:** agents stay narrow and keep context lean; at ~150 tool calls they write a handoff and stop, and a fresh agent continues (memory: agent-context-usage).

**Priority order (owner, 2026-10-16 evening): fixes first.**
1. **Viewer fixes (one agent, owner-reported, high).** These come first.
   - PW-408: rivers flicker on the globe/map, new today, likely relief depth-fighting.
   - PW-409: layout pass. The left panel hides under the legend bar; drop "Why pentagons?"; the zoom 3D right pane overlaps.
   - PW-407: type-to-filter box on the run/world/zoom pickers.
   - PW-406: jet stream as a seasonal core ribbon (small; can ride along).
2. **Fine-zoom quality (zoom lane).** These are in planet/zoom_fine.py, so do them serially, not in parallel.
   - PW-405: river planform; no 90-degree switchbacks; straight bedrock, meandering alluvial.
   - PW-395: volcano form (crater, gullies, no needle cone, no ring).
   - PW-404: sawtooth crests.
   - PW-391: inflow.
   - PW-392: glaciers and overlays not redrawn.
3. **V1 blockers (PW-244), in order:**
   - Run lane: PW-358 (split the Penman lakes out of the stage 2 commit ecffcb9), then the PW-300 re-check, then **freeze run physics**, then PW-202 (remake the L7 showcases = the v1 review).
   - World/timezoom lane: PW-037 glacial carving (great lakes, scoured shields, U-valleys, moraines, escarpments), then PW-092 landforms in zooms; PW-213 vegetation in the time zoom; PW-398 tropical orbit damping.
   - Viewer/infra lane: PW-248 `planet make` + "New planet" button; PW-100 export with PW-099.
4. **Targets agreed for v1:**
   - Speed: ~30-40 min per L7 planet is fine; no optimisation work unless it nears 1 h (talk to the owner first).
   - Reliability: the full health sweep stays inside every envelope with a little wiggle room for known outliers. A deep ice age is fine if the planet recovers.
5. **Calibration later:** rain (PW-015/016/352), giant lakes, Earth scores.

**Worktree base (found 2026-10-16 night):** agent worktrees are created from `origin/main`, which is stale because we never push (1f0fae4). Every agent prompt must start with: "First run `git merge --ff-only main` (local main, from /home/daniel/personal/repos/procedural-world-generation) in your worktree and confirm `git log -1` matches main before doing anything else."

**Zoom lane order update (2026-10-16 night):** after PW-395 (volcano), do PW-412 (floodplains), then PW-416 (river through time, an owner deliverable), before PW-404/391/392.

**Run lane order update (2026-10-16 night):** PW-300 (running), then PW-366 (raised to high: the run's sheets vs the time zoom's ablation/calving, now the main cause of the time zoom's runaway start, PW-418/421), then freeze run physics. Glacial carving (branch pw037-carving) waits for PW-366, then re-fits glacial_k (see PW-418).

**Paused 2026-10-16 late night (owner near weekly limit).** No agents running. Merged tonight: PW-409/407/408(+415 MSAA off)/406 (jet overlay later dropped by owner)/405/395/358/300/412/425/424/426/428, PW-418 diagnosis. Next, in order: run lane PW-366 (high; makes tests/test_timezoom_consistency.py's strict xfail pass), then freeze run physics and PW-202; zoom lane PW-416 (river through time; see docs/review/audit/pw425-handoff.md); glacial carving (branch pw037-carving) after PW-366; owner to answer: PW-030 (real ice-age cycles) in v1? and confirm PW-415 flicker gone in Chrome (then PW-417).

## Current state and next steps (2026-10-16 late night; supersedes earlier sections where they differ)

No agents running; owner near the weekly limit. Owner decisions tonight: PW-030 (real ice-age cycles: slow ~80-90 kyr builds, fast terminations, swing >= 80 m) IS in v1 (high, blocked on PW-366, listed under PW-244); PW-415 Chrome flicker confirmed resolved (done); PW-417 (retire diagnostic URL switches) stays todo/low/small; PW-416 (river through time) is a nice-to-have, not v1 (low).

**Merged today/tonight:**
- PW-409 viewer layout, PW-407 picker filter box, PW-408 + PW-415 river flicker (MSAA off by default).
- PW-406 jet stream overlay, then dropped by the owner (the upper-air sim stays).
- PW-405 river planform, PW-395 volcano form, PW-412 floodplains, PW-425/424 meander trains, PW-426 valley-floor layers in the zoom viewer, PW-428 time zoom sunshine at the cycling ice's latitude.
- PW-358 Penman lakes split out, PW-300 giant lakes re-check.
- PW-418 diagnosis only: the time zoom's runaway start comes from PW-015 stage 1 (snowier sheets) plus the PW-366 run-vs-time-zoom mismatch.
- pytest-xdist: tests run in parallel by default (`-n0` for serial).

**Parked:** glacial carving on branch pw037-carving (re-fit glacial_k after PW-366; see PW-418); PW-015 stage 2 branches (pw015-prototype, pw015-wip, pw015-optA).

**Rules reminders:**
- Agent worktrees start from stale origin/main: every agent first runs `git merge --ff-only main` and confirms `git log -1` matches main.
- Hand off at ~150 tool calls; fresh agent continues. Each agent uses its own scratchpad subdirectory.
- Subagents write inbox drafts, never PW- ids.

**Priority order by lane (v1 first):**
- Run lane (serial): PW-366 (high; makes the strict xfail in tests/test_timezoom_consistency.py pass) -> PW-030 (v1) -> freeze run physics -> PW-202 (remake the L7 showcases = the v1 review).
- Time-zoom lane: PW-037 carving re-fit (after PW-366), PW-213 vegetation in the time zoom, PW-398, PW-427.
- Zoom lane (planet/zoom_fine.py, serial): PW-404, PW-391, PW-392, PW-419, PW-430 (hydrology; run lane if it changes simulate); then nice-to-haves PW-416, PW-433, PW-411, PW-413, PW-420.
- Viewer/infra lane: PW-248 `planet make` + "New planet" button, PW-100 export with PW-099, PW-417, PW-410.
- Calibration later: rain (PW-015/016/352), Earth scores.

**Superseded:** the "Zoom lane order update" (PW-416 before PW-404) and "Run lane order update" lines above; the order here is the one to follow.

**Cleanup item:** `board.py check` warns of 28 refs in open tickets to runs/worlds/zooms that no longer exist (`board.py check --refs` lists them); prune or update them.

## Usage rules (owner, 2026-10-19; supersede the 150-call handoff above)
- Models: Haiku for mechanical work (stale refs, docs), Sonnet for moderately thinky work, Opus for the hard ice-age physics (PW-366, PW-030).
- Agents hand off at ~100 tool calls. At most one physics agent plus one cheap job at a time.
- Each agent gets its done-when criteria and a stop rule of ~5 tuning attempts. It starts long simulations in the background and reads only the summary.
- 2026-10-19: started PW-366 (Opus, option A: 75 kPa, cell-mean rise, reconciled melt and calving) and the stale-ref cleanup (Haiku).

## Morning note (2026-10-20)
No agents running. Server restarted on the latest main.

**Landed overnight:**
- PW-366 done. The run's sheets use 75 kPa with the cell-mean rise, and the time zoom's balance acts within its flow sub-steps. The unforced time-zoom start now holds: L6 drift went from -231 m to +7 m at 20 kyr, and the strict xfail passes.
- PW-030 partial (eed6a3a). The time zoom's ice-albedo feedback now uses the run's rule; Earth's swing went 43 -> 48 m. Real cycles were **not** achieved in 5 attempts. Proglacial lakes and dust were built but had no effect and are not merged; the patch is in docs/review/audit/PW-030/. Full write-up: docs/review/audit/PW-030-handoff.md.
- Stale-ref cleanup (28 refs in 20 open tickets).

**Not merged:** the PW-434 climate-drift sd 3 -> 2. It reshuffled which seed goes deep instead of fixing it.

**Diagnosis:**
- Cold eras run deeper since PW-366 (3 of 4 L6 seeds below -430 m for 5-7% of the time; worst -609 m). That comes from the ice-albedo/CO2 loop, not the drift size: PW-438.
- Time zoom: the CO2 + ice-albedo loop amplifies any drift about 2.5x onto one of two branches. On the cold branch CO2 is clipped and the ice area is saturated, so glacials never end: PW-440, high, needs-decision; agent lean is CO2 that follows the lagged temperature.
- The orbit alone loses ice (fast melt, slow regrowth). A 1.8x stronger orbital response did give 70-100 m cycles, but it melts Earth's interglacial ice away, so the sensitivity must depend on the glacial state.
- PW-439: the sheets' carried air may over-protect big sheets' summer margins.

**Next, waiting for the owner's go:** PW-440 (time zoom, Opus) and PW-438 (run lane, cold-era depth), probably together, since both are the same CO2/ice-albedo loop.

## Acceptance rule (owner, 2026-10-20)
Multi-seed criteria pass when ~70% of seeds pass, not all; outlier worlds are allowed. Use 6-10 seeds when 4 is too few to judge. "Not worse" means the share of seeds passing doesn't drop.

## State before compaction (2026-10-20 evening)
**Running:** one Opus agent on PW-460 + PW-459 together, in the run and the time zoom:
- PW-460: resolution-aware sub-cell margin (each margin cell takes the cell's mean ice surface, not edge_h 408 m).
- PW-459: insol_k derived from each cell's own seasons (measured 0.08-0.09 vs the 0.25 in code).

Worktree branch: worktree-agent-a9f64607e1a64d2e8. Scratchpad: .../scratchpad/pw460/. Handoff, if any: docs/review/audit/PW-460-handoff.md (removed; see git d32f7fa).

**It merges only if:**
- the Earth zoom deepens (~-80 m, multi-Mkm2 Laurentide south of ~50 N);
- the unforced-start consistency test passes;
- at least 7/10 run seeds pass the cold-era check;
- interglacial ice is 9-12% of land (real Earth ~10%; corrected from the old 8-9%).

If the run fails while the zoom succeeds, it writes a needs-decision draft instead.

**On its report:**
1. Merge if it meets the bar (`board.py intake`, pytest, restart the server); otherwise intake its draft.
2. Write up the ice-age state for the owner and update PW-030, PW-033, PW-435, PW-447, PW-459 and PW-460.

**Owner's deadline:** this is the last ice-age implementation batch. Write up and report; chase only an obvious final cleanup, and only until the morning of 2026-10-21. If progress isn't meaningful, propose kludgier approaches (e.g. state-forced cycles) and move to other lanes.

**Today's ice-age record:**
- Merged: PW-366, PW-438 (done), PW-440 (three-mode cycle), PW-442 (timezoom package), PW-450 (time-zoom vegetation).
- Not merged: PW-449 (wontdo; PW-453 keeps main's albedo rule for now). PW-448 and PW-033 are diagnoses (docs/review/audit/PW-448-diagnosis.md, PW-033-diagnosis.md).

**Queued, not v1-blocking:**
- PW-458: missing North Atlantic Drift; Fennoscandia's cold bias comes from it.
- PW-457: eastern Canada's rain seasonality.
- PW-454: glacial tropics green instead of drying.
- PW-445 and PW-444: helper dedupe.
- PW-446: mantle basis cache not reproducible.
- PW-252 and PW-259: speed.

**Showcases:** Earth time zoom 098d5d (with vegetation); the PW-440 cycle zooms 755514, 7d5027 and be3362.

**Owner rules learned today:**
- Haiku for mechanical work, Sonnet for moderate, Opus for ice ages.
- Handoff at 100 calls.
- ~70% of seeds passing is enough.
- No replies to interim "agent waiting" notices.
- Flag refactors, with a Haiku duplicate scan first.
- Thresholds are planet-relative.

## State 2026-10-21 (early morning)
- **Ice ages are parked** under epic PW-470 until after v1. v1 uses the glacial index (PW-471, merged); run moments ship as is (PW-492 option C).
- **Unmerged ice branches kept for later:**
  - `worktree-agent-a9f64607e1a64d2e8`: PW-460/459.
  - `worktree-agent-af748cc6ffa533997`: PW-465 coast_loss. Decision PW-514; write-up docs/review/audit/PW-465-side-lane.md.
- **Merged overnight:**
  - export (PW-100) and projections (PW-477), with the 2D map in the viewer;
  - `planet make`, start screen and navigator, cancel/resume (PW-248/472/473/480/482);
  - fine-zoom redraws (PW-392);
  - glacial carving (PW-037/491/418);
  - the "now" pick (PW-479);
  - glacial landscapes in zooms (PW-092);
  - human-use layers (PW-099);
  - the board's milestone field.
- **Store:** cleaned by the owner. Current showcases: time zoom e9d59c (Earth, carving), finished world 577526 (420 kyr, with rock), zooms 66c45e and 0de6eb (Norway), 21703a (Baltic margin), 4f65aa (Ungava).
- **v2 scope:** the 2026-10-21 v2 proposal (`docs/review/v2-proposal.md`, removed 2026-10-23; see git d32f7fa) has been applied to the board: use `board.py milestones v2` and `board.py tree --open`.
- **Next v1 work:** PW-213 (vegetation in the time zoom), PW-512 (moraine lakes), PW-505 (human-use layers in the viewer), PW-488 (fine-zoom coast staircase), then PW-202 (showcase remake + health sweep) and the final calibration pass.
- `board.py milestones v1` lists what's open.
