# 1 Gyr level-8 world (lane 105)

## In plain words
Daniel asked for a 1 Gyr level-8 world "without eating all the cores". It is made, ran on 8 of the 48 cores the whole time,
and is in the store now. It took about **7.5 hours** end to end: the 1 Gyr tectonics and climate run 5 h 26 min, a 9 min slice,
a 300 kyr ice-age time zoom 1 h 48 min, and a 9 min finish at the latest interglacial. Nothing crashed, nothing was retried.

Open in the viewer (port 8765):
- **Showcase world (finished at an interglacial, the recommended one):** http://localhost:8765/viewer/?world=0af5ae.json
- Plain slice of the run's last frame, no ice-age finish: http://localhost:8765/viewer/?world=928016.json
- Run: http://localhost:8765/viewer/?run=6a6fd6  Time zoom: http://localhost:8765/viewer/?run=7d803e
- For comparison: the 100 Myr L8 world http://localhost:8765/viewer/?world=a16f5a.json and the L7 seed-11 world http://localhost:8765/viewer/?world=2a7385.json

What the world is like, in words: one huge continent (Hizam, 30% of the planet's surface and 87% of all land) plus three
smaller landmasses over 1 million km2 and a scatter of islands. 35% land, 15.4 C mean, peak 6,000 m, 3,200 river cells of
real size, and a biggest river that runs 239 cells (about 7,000 km) and reaches the main ocean. Much more mountainous than the
100 Myr world, and far less of it drains into closed basins. The "it is one supercontinent" shape is the same family as 100 Myr's Hizam; seed 11 at L8 seems to like it.

What is not good (carried over from the L8 notes, not new): the continental margin is a cliff, and the shelf is almost
absent (0.6% of the ocean, Earth 7%; see the table). Measured, not fixed here: no code changed.

## What it cost (8 cores, pinned with `taskset -c 0-7`, `--threads 8`, other lanes running alongside)
| Stage | Wall | Peak RAM | Size |
|---|---|---|---|
| `simulate` 1000 Myr, `--every 10 --checkpoint-every 100` (run 6a6fd6) | 5 h 25 min 42 s (19,533 s) | 30.2 GB at the very end (final write); 10-16 GB through the run, 18.6 GB spike at the 500 Myr keyframe | run dir 5.9 GB, 120 keyframes, 10 checkpoints of ~200 MB |
| `slice 6a6fd6 --at auto` (world 928016, = the run's end) | 9 min 52 s | 19.7 GB | 422 MB |
| `timezoom 6a6fd6 --at 1000 --kyr 300` (run 7d803e) | 1 h 47 min 39 s (about 21 s per kyr) | 12.0 GB | 1.1 GB, 151 frames |
| `finish 7d803e --now interglacial` (world 0af5ae, picked 292 kyr) | 9 min 8 s | 15.2 GB | 432 MB |
| Total | about 7 h 32 min | 30.2 GB max | about 7.8 GB added to the store |

Pace of the run (from checkpoint times): the first 100 Myr took 52 min (about 31 s/Myr, a slow start), then 100 Myr every 18-40 min
(about 11-20 s/Myr), and the last 100 Myr took about 65 min, because the final 10 Myr run a 0.5 Myr climate step. Averaged: 19.5 s/Myr,
5.7 h per Gyr at 8 cores. The `docs/coordination.md` table says "~3-4 h per Gyr" at L8; with 8 cores and today's model plan on about 5.5 h.
The run prints nothing until it ends (output is buffered through `uv`); the checkpoints in `runs/<id>/state/` are the only progress marker (one per 100 Myr).
/tmp stayed at 85-87 GB free the whole time (the output goes to the store on disk; the frozen worktree's venv is 262 MB).

Time zoom: the L8 pace is about 21 s/kyr here (the `make` estimate assumes 2.6 s). The 300 kyr zoom had its lowest sea level at -153 m (90 kyr), ice up to 8.9%
of the surface, 9 glacial events. The finish picked the latest interglacial at 292 kyr (sea level -79 m). I did the time zoom the showcase way (what `planet make` does: simulate, time zoom 300 kyr, finish
`--now interglacial`) by hand, because `make` could not be pinned to cores per stage; highlights and regional zooms were **not** made (not asked, and a16f5a's 86 s + 4 x 110 s).

## Counts: the 1 Gyr world against the 100 Myr one and the L7 one
My own script (scratch, deleted), on the stored worlds. Land = elevation above 0 (plus ground under ice). Islands = connected land groups by area. The
inland-drainage share follows each land cell's `downstream` chain to its end: "ends on land or a lake" (first number), and "ends anywhere but the main ocean" (second, adds sea-level pockets).
Lane 96's 9.5% figure used another definition, so compare only within the rows here.

| | **0af5ae** L8 1 Gyr (finished) | 928016 L8 1 Gyr (plain slice) | a16f5a L8 100 Myr | 2a7385 L7 792 Myr + 300 kyr |
|---|---|---|---|---|
| cells / km2 per cell | 655,362 / 778 | same | same | 163,842 / 3,113 |
| land share | 35.2% | 34.7% | 34.1% | 36.2% |
| sea level (total) | +65.9 m | +144.5 m | +311.6 m | -7.7 m |
| shelf (0 to -200 m) share of ocean | **0.64%** | 1.17% | 4.18% | 0.61% |
| landmasses over 1 Mkm2 | 4 | 4 | 7 | 4 |
| largest landmass, share of all land | 86.6% | 86.9% | 46.8% | 70.4% |
| islands 10k-100k km2 (mid-sized) | 14 | 13 | 10 | 4 |
| islands 100k-1M km2 | 5 | 3 | 6 | 4 |
| islands under 10k km2 | 308 | 293 | 247 | 53 |
| land cells touching ocean (coast) | 12,231 | 12,347 | 11,734 | 4,658 |
| inland drainage, share of land (ends on land / not main ocean) | 5.5% / 14.5% | 5.0% / 9.9% | 28.1% / 31.4% | 10.8% / 11.3% |
| river cells with flow >= 300 | 3,215 | 3,310 | 3,580 | 585 |
| largest river (flow, length) | 18,333, 239 cells, into the main ocean | 19,067, 248 cells, into the main ocean | 6,332, 132 cells, ends in an inland sea pocket | 3,239, 63 cells, main ocean |
| lake cells (open / closed / salt pan) | 2,162 (80 / 57 / 34) | 943 (75 / 44 / 29) | 1,913 (49 / 44 / 31) | 44 (14 / 4 / 7) |
| mean temp / highest peak / mean land elevation | 15.4 C / 5,998 m / 894 m | 15.6 C / 5,921 m / 870 m | 12.8 C / 3,248 m / 362 m | 21.0 C / 5,730 m / 676 m |
| tree cover mean | 25.1% | 30.3% | 24.1% | 15.8% |

Reading it:
- A 1 Gyr run fixes the 100 Myr world's age problems: peaks are 6,000 m (not 3,248), mean land 890 m, the biggest river is 3x the flow and reaches the real ocean, inland drainage falls from 28% to 5.5% (L7 10.8%).
  The 100 Myr world's "largest river ends inland" problem (explore.md #5) is gone here, at least for the top river.
- Mid-sized islands (10k-100k km2): 14 against 10 (100 Myr) and 4 (L7). lane 96 (explore.md #10) counted 11 against 44 for Earth on the same grid, so this is still well short (PW-950's finding stands).
- **The shelf is missing at 1 Gyr:** 0.64% of the ocean is 0 to -200 m (Earth 7%, the 100 Myr world 4.2% only because its sea level was +312 m and flooded the platform). So the cliff-edged margin is the same at L8 here; this is model, not age.
- One continent holds 87% of the land. That is much less continent-scattered than the L7 seed-11 world (70%) and the 100 Myr one (47%); at 1 Gyr that is just where seed 11 ended up. Single seed: do not read it as a trend.
- Run size: 120 keyframes of 17 MB is why the run dir is 5.9 GB. Disk is fine (657 GB free on /data).

## Problems and what to know
- None crashed. The `simulate` process printed nothing to its log until the end (buffered), so the wait is blind apart from checkpoints.
- Peak RAM 30.2 GB is the final write of the run (mostly keyframe assembly), not the physics (10-16 GB). Two L8 runs at once would need ~60 GB at the end; plan for it.
- `make` for L8 would do the same sequence but cannot be pinned per stage; I ran the stages by hand.
- No code changes, no tickets, no scorecard run (a scorecard at L8 is not set up).

## Progress log
- 22:01 started run 6a6fd6 (`l8-earthlike-s11-1gyr`), pinned to cores 0-7, `--every 10 --checkpoint-every 100`, frozen code at main c943933a. RSS 6.7 GB at 90 s, 9.6 GB at 1 h.
- 22:53 100 Myr checkpoint written (52 min for the first 100 Myr, about 31 s/Myr). Frames are only written at the end of the run; the checkpoints in `runs/6a6fd6/state/` are the progress marker.
- 23:31 200 Myr, 23:52 300 Myr, 00:23 400 Myr, 00:41 500 Myr (checkpoint times). 100 Myr per 18-40 min. RSS 10-11.7 GB (one 18.6 GB sample around 00:40 when a checkpoint/keyframe was written). /tmp 86 GB free throughout.
- 00:59 600 Myr, 01:22 700 Myr, 01:55 800 Myr (the last 100 Myr took 33 min). RSS 12-15.5 GB, brief spikes at keyframe writes.
- 02:26 run finished: 5 h 25 min 42 s wall, peak RSS 30.2 GB (at the final write), run dir 5.9 GB, 120 keyframes.
- 02:27-02:37 `slice 6a6fd6 --at auto` -> world 928016: 9 min 52 s, peak RSS 19.7 GB, 422 MB.
- 02:41 started `timezoom 6a6fd6 --at 1000 --kyr 300` (the showcase norm), pinned to 8 cores.
