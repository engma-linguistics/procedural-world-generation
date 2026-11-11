# The glacial time zoom at 2 Myr (PW-1661, lane 280)

Daniel, 2026-11-10: v1.0's time zoom runs 2 Myr instead of 1 Myr. In plain words: every new world gets 2 Myr of ice ages
in 500-year steps instead of 1 Myr (or, from `planet make` and the viewer, instead of 300 kyr), and the peoples' history
gets the time zoom's detailed climate over its last 2 Myr instead of its last 1 Myr (or 300 kyr).

## 1. Inventory: what assumed about 1 Myr (before any change)

Defaults of the span (changed to 2000 kyr):

| where | before | note |
|---|---|---|
| `planet timezoom --kyr` (`planet/__main__.py`) | 1000 | help text "~1 Myr" |
| `timezoom.run.timezoom(kyr=)`, `timezoom.sim.simulate(kyr=)` | 1000 | library defaults |
| `planet make` (`make.DEFAULTS["kyr"]`), so the viewer's start screen and its make dialog | **300** | the make pipeline (and so every showcase, e.g. Earth-like A's fc5311) used 300 kyr, not 1 Myr |
| `POST /api/timezoom` (`api.parse_timezoom_request`) | 300 | the viewer's "time zoom from here" job |
| viewer: start screen (`viewer/start.js` `fKyr`), navigator (`viewer/navigator.js`), run summary box (`viewer/globe/timezoom.js` `TZ_KYR`, `viewer/globe/state.js` `tzKyr`) | choices 100 / 300 / 1000, default 300 | 2000 added as a choice and made the default |
| range checks in `make.parse_make_request` and `api.parse_timezoom_request` | 1..2000 kyr | unchanged: 2000 is inside |

Docs that said 1 Myr: `README.md` (CLI line and the viewer paragraph), `docs/overview.md` (cost table, the pipeline diagram,
"what it does", §2 time-zoom section, the glossary table, the speed list), `docs/wiki/glossary.md`, `CLAUDE.md`,
`planet/timezoom/__init__.py`'s docstring.

The peoples' deep history (`planet/lineages/history/steps.py`): **nothing is tied to 1000 kyr.** The schedule is built from
the time zoom it is given:
- deep steps: the source run's keyframes (every 4 Myr) from the oldest line's date down to the time zoom's start
  (`at_myr`), plus a step at each line's own date in between; so whatever the zoom does not cover, the run's keyframes do.
- glacial steps: every stored frame of the time zoom (2 kyr apart) before the recent window, back to the oldest line.
- recent steps: the recent pass (last 30 kyr at 0.1 kyr).
A longer zoom moves the 1-2 Myr band from deep steps (4 Myr keyframes, `epoch == "deep"`: no goods, no crops, no hunts,
overland-only dispersal, the deep food budget of the megafauna) to glacial steps (the zoom's 2-kyr frames, every mechanic
on). No line appears late: a line's date is a step in either schedule. Spatial "prolongation" (`recent.finer`) is the
L7 -> L8 grid nesting of the split pipeline, independent of the span.

Preset dates (`planet/lineages/samples/*.toml`): every date is years before the present, not tied to the zoom. Between
1 and 2 Myr ago, and so newly inside the zoom:
- dnd: tabaxi 1.2 Myr, giantkin 1.1 Myr, true giants 1 Myr; sapiens nodes of the hominid stem (1.6 Myr), the goblinoids
  (1.2 Myr), the felines and avians (2 Myr).
- seven_meals (frozen: dates untouched): dwarves 1.5 Myr, halflings 1.2 Myr, the human line 1 Myr, dragonborn 1.3 Myr,
  kobolds, bugbears and goblin-kind 2 Myr.
- humans ("real" mode of either tree: only `real = true` lines): archaic humans 400 kyr and humans 200 kyr in dnd, the
  human line 1 Myr in seven_meals; all inside a 1 Myr zoom already.
Nothing older than 2 Myr changes epoch. No preset date needs a change for the span (section 3 checks the runs).

Tests: none asserts the default span (test_make uses explicit `kyr`; the lineages tests build their own fake zooms).
`tests/test_lineages.py`'s preset checks (dragon kinds 500-1000 kyr, giants 1-4 Myr) are about the tree's dates.

## 2. Cost, 1 Myr against 2 Myr on the same code

All on December A (run 0b3439, L7, 163,842 cells, 1000 Myr), main at 9749fb4f plus this branch's default changes (no
change to any model), scratch data root, `NUMBA_NUM_THREADS=4`, the two zooms side by side and the two peoples runs side by
side, machine load 15-50 from other lanes (so "about"). `/usr/bin/time -v` wall and peak RSS.

| stage | 1 Myr (`--kyr 1000`) | 2 Myr (`--kyr 2000`) |
|---|---|---|
| time zoom | 82048d: 1:01:51 wall (3,709 s own), 4.5 GB peak, 501 frames, 886 MB on disk | 040d59: 1:54:05 wall (6,843 s own), 6.6 GB peak, 1,001 frames, 1.7 GB on disk |
| finish at `--now interglacial` | d17df8 at 992 kyr, ~2.5 min | 6e2f17 at 1,988 kyr, ~1.5 min |
| dnd peoples, 1 try (`planet lineages <world> --tree dnd --tries 1`) | b74691: 1:15:30 wall, history 2,231 s, 815 steps, 14.5 GB peak, 2.7 GB on disk | 580f8c: 1:26:57 wall, history 2,966 s, 1,310 steps, 20.3 GB peak, 4.5 GB on disk |
| split (refine to L8, then the history L7 to the first farming, L8 after) | 025b98 on 5d09cc (docs/review/refine-l8/split.md): history 55 min, 1:56:41 wall, 35.5 GB peak | refine of 6e2f17 to L8 (bcf4ba): 4:22 wall, 11.7 GB peak; split run 1f49d0 (`planet lineages bcf4ba --tree dnd --tries 1`): 2:09:40 wall, **69.3 GB peak** (`/usr/bin/time -v`), exit 0. Peak almost doubles against the 1 Myr split (different world; same tree) — ticketed (coordinator, 11-10). |

So at L7 the time zoom costs ~1 h per 1000 kyr, linear in the span (3.7 and 3.4 s per kyr), and its memory grows by 2.1 GB
per extra Myr (the frames are held in memory until written). The peoples history adds ~500 glacial steps (one per stored
2-kyr frame of the extra Myr) for +33% history time, +15% wall and +40% peak memory (the stored frames). An earlier pair on
Earth-like A (a19366) was dropped after its 1 Myr zoom (0629ca: 54:57 wall, 4.8 GB peak): that run is older than the
current tectonics parameters, so `finish` refuses it.

`make.TZ_S_PER_KYR[7]` was 0.65 s/kyr (5x too low against these runs); it is now 3.5, and L8 15 (docs/coordination.md's 10-20 s
per kyr). The viewer's estimate in the run summary box scaled linearly with cells (32 min for 2 Myr at L7); it now scales
as cells^1.9 (~4 min per 1000 kyr at L6, ~56 min at L7).

The 2 Myr zoom is not the 1 Myr zoom continued: their sea levels part from the first frames (82048d vs 040d59 at 100 kyr:
-59 vs -33 m). The glacial index's sunshine thresholds are percentiles of the summer sun over the whole span
(`timezoom.cycle.Index`, at least 800 kyr): 422.1 / 433.2 / 461.8 W/m2 for 1 Myr, 422.8 / 433.4 / 461.7 for 2 Myr, and that
small shift moves the first build's timing. Both are sound (the 2 Myr span samples the 405-kyr eccentricity cycle more
fully): 10 cycles of 99 kyr mean in 1 Myr, 20 of 100 kyr in 2 Myr, mean glacial index 0.50 and 0.53.

## 3. The peoples on the 2 Myr zoom against the 1 Myr zoom

Same code, same world, same tree (dnd), one try each (seed 7000); `/data/personal/scratch/lane280/cmp_pp.py`.
Baseline: b74691 on the 1 Myr zoom (present 992 kyr) against 580f8c on the 2 Myr zoom (present 1,988 kyr).

- **No line appears late.** Every line starts at its drawn date in both runs (start = date for all 59 lines; the only
  difference is half-orcs, a hybrid placed when its parents first meet: 4.2 against 5.6 kyr ago). The lines dated
  1.0-1.2 Myr (tabaxi, giantkin, true giants) are placed in the glacial epoch on the 2 Myr zoom instead of the deep one;
  the stems (20, 19.5, 10, 6, 4 Myr) are on the run's keyframes in both, as before.
- **The same 42 lines live at the present**; same farming dates (first cultivation 12.0 kyr ago, then 10.7, 10.6, 10.2,
  10.0; 34 crops taken up in both). Cultures 573 / 579 (alive 212 / 189), demes 687 / 704, settlements alive 24,328 / 27,433
  (cities 283 / 270, towns 5,387 / 6,545).
- **Numbers per people move a lot**: total people at the present 571 M against 908 M (+59%); humans 103 M -> 53 M, dwarves
  80 M -> 5 M, kobolds 5.4 M -> 0.6 M, halflings 15 M -> 117 M, orcs 17 M -> 107 M, tabaxi 14 M -> 60 M, hobgoblins 49 M -> 127 M.
  The land is the same (35.0% and 34.9%). With one try each, on two presents of different climate (the zooms part early,
  section 2), this cannot be laid on the span: the dnd peoples swing this much between tries (the try scores are
  0.771 and 0.684). An inbox draft asks for the re-rolled comparison before v1.0's numbers are trusted.

Nothing here called for a change to the history or the presets: the schedule already follows the zoom it is given, and no
date sits in a gap the longer zoom opens.

## 4. Why the 2 Myr split peaks at 69 GB (PW-1691, lane 305)

**Diagnosis.** The extra memory is the history's own stored frames from before the cut, held in memory at the fine grid's size.
Not the recent pass (`recent.Pass` memory-maps the time zoom's frames, `timeline.load_frames`, and `recent_rain.npz` holds only
the 30-kyr window's ~16 full climates), not the ice history. Line numbers are main at 3085f020.

- The history keeps every stored frame in a list until the run is written (`history/model.py:267`). A frame
  (`history/frame.py:71`) holds the step's whole climate (`env`: elevation, ice, temperature, rain, tree cover as float64, the
  climate class and a land mask, from `recent.Pass.fields`, `recent.py:353-366`) and ~20 cell layers (peoples, composition,
  crop and animal bit flags as uint64 / uint16, body shares), about 80-90 bytes a cell.
- A glacial frame is stored every 4 kyr of the time zoom (`steps.py:66`, `History(glacial_every=4.0)`, `model.py:44`): the
  2 Myr zoom stores ~250 more glacial frames than the 1 Myr one, all before the cut (12 kyr ago on Earth-like A).
- At the cut, `regrid_frames` (`history/handover.py:231-259`, called at `model.py:223`) copies every frame stored so far onto
  the fine grid at once (`R.keep`, the fine cell's first parent): each one becomes 4x its L7 size, and they all stay to the
  end. At L8 a frame is ~55 MB, so ~250 more frames is ~14 GB more.
- `output.save` then holds the frames, the encoded layers as per-frame lists (`output.py:93-101`) and the same layers
  stacked (`output.py:105`, `np.stack`) before `write_layers` (`output.py:114`): the frames' encoded layers twice more, ~45
  bytes a cell each time, again scaling with the frame count. This is where lane 267 saw the 1 Myr split peak (after the
  history; section 1 of docs/review/refine-l8/split.md).

Measured on a small analogue (an L6 run, 0760b3, seed 250979, 1000 Myr; zooms of 1 and 2 Myr from 1000 Myr; finished at
the interglacial and refined to L7: worlds 56ff8d and 2cf3b0; dnd tree, one try; RSS sampled every 0.5 s, by stage):
`regrid_frames` alone added 3.8 GB on the 1 Myr zoom (4.25 -> 8.04 GB) and 6.7 GB on the 2 Myr zoom (5.5 -> 12.2 GB),
against a history that had peaked at 4.5 and 5.5 GB before it; `np.stack` then added 2.3 GB (1 Myr) and 4.7 GB (2 Myr), and
the stacked layers stayed alive through every after-run stage, since `save` holds them to its end. Each run's peak came
during the languages pass, the last stage, on top of all of it. Both zooms store 1 frame per 4 kyr, and the 2 Myr run kept
580 frames (cut at step 1191 of 1312, 12.0 kyr ago) against the 1 Myr run's 333 (cut at step 691 of 812).

**The fix** (lane 305):
- `handover.FineFrames` (`history/handover.py`, used at `model.py:223`): the frames stored before the cut stay on the coarse
  grid and are read on the fine grid one field at a time, when asked (the same `R.keep` and sparse-presence rule as
  `regrid_frames`, which is kept and tested against it); nothing regridded is kept.
- `output.save` writes the frames' layers with `store.LayerStream` as it reads them (the same files, bytes and metadata as
  `write_layers` of the stacked arrays) instead of holding per-frame lists and their stack.
- On the way, the split run on main crashed after the hand-over (three times, each a coarse-grid object carried onto the
  fine grid since PW-1687 and the live tech tree): the dragon cultures (`dcul`, `dregions`), the live tech tree's goods,
  landmass and stored-presence caches, and the live polities' ring counts and ring table (`r_town`, `r_city`, `_ring_of`,
  `inv_rows`) are now made on the fine grid or carried by first parent. `r_town`/`r_city` had been carried silently at their
  coarse ring counts (fewer rings than the km asks on L8). Every split run on main stops at the first stored frame after the cut
  without this, so the baseline below is main plus these hand-over fixes only.

**Measured** on the same L6 -> L7 analogue, `/usr/bin/time -v` peak RSS and wall, two threads each, four runs side by side.
Baseline: main 3085f020 plus the hand-over fixes ("before"), against this branch ("after"); same worlds, same tree and seed.

| | 1 Myr zoom (56ff8d) | 2 Myr zoom (2cf3b0) |
|---|---|---|
| peak before | 14.1 GB | 20.4 GB |
| peak after | 8.7 GB | 10.3 GB |
| 2 Myr peak over the 1 Myr peak | before 1.45x | after 1.19x |
| history (`generated_in_s`) before / after | | 1,505 / 1,357 s |
| wall before / after | 54:04 / 55:03 | 1:01:08 / 58:12 |

**Outputs**: every file of the before and after runs is byte-identical (101 layer files, the presence tables, demes,
cultures, settlements...), except timing fields, the run id inside `languages.json` and the tree file's path (the two
checkouts); `same.py` in the lane's scratch.

*Estimate* for L8 (not measured here: lane 280's December A worlds are gone and rebuilding the 2 Myr zoom is ~2 h): the
analogue's 2 Myr run fell to 0.50x of its before peak; on lane 280's 69.3 GB that is ~35 GB, near the 1 Myr split's 35.5 GB
(itself before the fix: it should fall too). `tools/split_peak_l8.sh <scratch root>` rebuilds the chain from December A and
measures it, for an overnight run.
