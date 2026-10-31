# Level-8 world (lane 86b)

## In plain words
There is a level-8 world you can open now. It has about 655,000 cells of 30 km (L7 has 164,000 cells of 60 km).
It is a **100 Myr** world, not a showcase: 1000 Myr would not fit overnight. Use it to judge resolution
(coasts, rivers, lakes, the globe's speed), not geography or climate realism.
The same seed (11) gives different continents here than the L7 seed-11 world, because the model changed since
that L7 world was made and this one is much younger. Do not compare the maps; compare the counts and the speed.

Open in your viewer (port 8765):
- World: http://localhost:8765/viewer/?world=a16f5a.json  (`l8-earthlike-a-s11-100myr @ 100 Myr`)
- Run (tectonics, 100 Myr): http://localhost:8765/viewer/?run=2c0c5d
- Four regional zooms of the world (largest river mouth, longest river, highest peak, delta): ids 652c1a, f04623, e3e8aa, 839e46
- L7 seed-11 for comparison: http://localhost:8765/viewer/?world=2a7385.json

Peoples on this world: see the last section (status).
- Also stored: 60 kyr glacial time zoom `37f146` (the peoples run starts from it), highlights (75 places) in `worlds/highlights/`.

## What it cost (L8 here vs L7)
All on the Threadripper at load 20-55, with other lanes running, so read these as upper-ish numbers.

| Stage | L8 (this world) | L7 (stored, for scale) |
|---|---|---|
| tectonics + climate run, 100 Myr | 132 min wall; 9-25 s/Myr until ~88 Myr, then ~8 min/Myr in the last ~10 Myr (full climate every 0.5 Myr). Peak RSS 10.7-15 GB. Run dir 1.7 GB | L7 ~50 min per Gyr |
| `slice` to a world (full climate, coast, resources) | 13.8 min, 17.7 GB RSS, world file 440 MB (420 MB on disk) | world 2a7385: 37 s (finished from a time zoom), file 113 MB |
| 60 kyr glacial time zoom | 39 min, 10.4 GB RSS (~10-20 s per kyr; the `make` estimate says 2.6 s) | 300 kyr, ~0.65 s per kyr assumed |
| highlights | 86 s | - |
| 4 regional zooms | 439 s together (~110 s each), 33 MB each | - |
| peoples (`lineages`, 1 try) | still running, see the end | 4 tries, 4 h 24 min wall, 11.2 GB RSS (run 57b95b) |

`planet make` itself was stopped after the simulation: its time zoom was set to 300 kyr and was at 30 kyr after 24 min, and I judged it
would not finish before you woke. In hindsight its pace (30 kyr per ~24 min, similar to the 60 kyr run here) means it would have finished in
about 4 h, so that call was too pessimistic. I sliced the finished run directly instead, so this world is the run's last frame (100 Myr, no ice-age finish).

## What looks different at L8 (world a16f5a vs the L7 seed-11 world 2a7385)
Numbers from the stored worlds. Cells are equal-area, so plain means are fair.

| | L8 100 Myr | L7 792 Myr + 300 kyr |
|---|---|---|
| cells / cell size | 655,362 / 30 km | 163,842 / 60 km |
| land (elevation above 0) | 34.0% | 36.1% |
| coast length (land cells touching ocean x cell size) | 12,680 cells, ~380,000 km | 4,905 cells, ~294,000 km |
| river cells with flow >= 300 (km of river) | 3,563 (~107,000 km) | 583 (~35,000 km) |
| lake cells (open / closed / salt pan lakes) | 1,913 (49 / 44 / 31) | 44 (14 / 4 / 7) |
| small islands | 50 | 7 |
| landmasses (named, over 0.1% of the surface) | 8 | 8 |
| mean temperature, all / land | 13.3 / 15.2 C | 19.5 / 14.4 C |
| mean rain, all / land | 950 / 1,212 mm | 1,215 / 1,234 mm |
| highest peak | 3,248 m | 5,730 m |
| mean land elevation | 362 m | 676 m |
| ice cover | 1.2% of cells | 1.8% |

The three that stand out:
1. **Lakes and rivers multiply.** About 4x the river cells at the same flow threshold (more than the 4x cell count would give on length alone, since
   the finer grid resolves small basins), and about 40x the lake cells (1,913 vs 44). Finer cells make pits that hold water.
2. **Coastline gets longer and ragged.** The coast gains ~30% in length (not 4x; the cell size halved but the coast is a length) and there are 50 small
   islands against 7.
3. **The world is cooler and lower.** 13.3 C against 19.5 C global mean and a 3,248 m peak against 5,730 m. This is mostly age, not resolution: it is a 100 Myr world
   (young mountains, one run from a supercontinent start, 22 plates still splitting) against a 792 Myr one. I cannot separate the two with a single pair.
   One oddity worth a look: `meta.sea_level_m` reads +311.6 m for this world (L7: -7.7 m). That field is the total sea level, not a change; I did not check what the +311 means.

Same seed, different continents: both are `--seed 11`, but physics changed since the L7 world was made (Oct 24), the L8 run is only 100 Myr, and the grid differs.
Do not read the map differences as a resolution effect.

## Peoples
Shares are the present area of each people in million km2 (the stored `meta.present.lines`).

L7 (run 57b95b, 4 tries): dragonborn 92, kobold 54, kenku 27, gnome 21, genasi 20, human farmer 17, human 17, lizardfolk 17 (full list in its run.json `meta.present.lines`).
L8 (run name `l86-l8-dnd-s11`): **not yet. It is running** (started 06:07, one try, 60 kyr time zoom as the present). Expect many hours: one L7 try took
roughly 66 min wall, and L8 has 4x the cells, so about 4-5 h, i.e. around 10:30-11:00. The run lands in the store by itself with its land use, fuels, demes,
settlements and tech tree (the lineages step does all of those; there is no separate `techtree` or `settlements` step to run). Its id will show in the viewer's run list, or `uv run python -m planet list`.
Link once done: http://localhost:8765/viewer/?run=<id>&layer=peoples (id from the list).

## Viewer verdict: the globe will not chug
Measured with `tools/viewer_perf_globe.py` against my own server (port 8791), real GPU, headless Chrome, while the machine was busy with the sim:

| | L8 a16f5a | L7 2a7385 |
|---|---|---|
| load to first globe drawn | 5.3 s | 1.6 s |
| wire (gzipped) | 97.9 MB (world 65.9 + grid 32.0) | 25.8 MB |
| world JSON text | 440 M chars, parse 1.0 s, fetch 3.3 s | 113 M chars, parse 0.27 s |
| JS heap after load / at end | 1.2 GB / 3.3 GB | 0.3 GB / - |
| triangles drawn | 3.93 M | 0.98 M |
| globe frame while turning | 16.7 ms median (60 fps), worst 250 ms once | 16.7 ms, worst 33 ms |
| layer switch to drawn | 73-158 ms | 37-68 ms |
| flat map / 3D relief toggle | 1.2 s / 1.2 s | 0.2 s |
| hover (pointermove) | 0.8 ms | 0.65 ms |

Server endpoints (gzip accepted, local): `worlds/a16f5a.json` 200, 66 MB on the wire, 23 ms (cached file); `runs/2c0c5d/run.json` 157 KB, 33 ms;
`api/cell` first call 5.3 s (loads the world server-side; L7 1.1 s), then 3 ms; `api/highlights?cached=1` 3 ms. Payload is about x4 and the load time x3.3: the
page opens in about 5 s, then turns at 60 fps.

Watch for two things:
- **The world file is 440 M characters.** Chrome's longest string is about 536 M. L8 is under it with ~20% to spare; L9 (2.6 M cells) cannot be a single JSON and would need a binary format.
- The page uses 1.2 GB of heap after load and 3.3 GB after switching around. Fine on a desktop with a GPU; a laptop with 8 GB would feel it.
Opening a peoples run or a time-zoom run at L8 loads layers per frame (tens of MB each) and was not measured, because the peoples run does not exist yet.

## Caveats
- 100 Myr, not a showcase. Plants and soils are less developed than at 800 Myr+; the climate mean is cool.
- The slice is the run's last keyframe, not an interglacial moment of a time zoom.
- Same seed does not mean same continents (see above).
