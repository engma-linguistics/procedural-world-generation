# Morning report (2026-10-14)

Viewer: http://127.0.0.1:8765/viewer/ (server running on main's latest code). Everything is committed locally on main; nothing is pushed.

**Also read:**
- `docs/morning_decisions.md`: 5 judgement calls for you.
- `docs/overview.md`: what the project is and how each part works. It was still being written at the time of this report.
- `docs/review/overnight_runs.md`: run numbers and the resolution comparison.

## What merged overnight
| Branch | What it does |
|---|---|
| `store` | One file per layer, so the viewer downloads ~4× less (57 MB instead of 252 MB for a default run view). Checkpoints every 100 Myr, so slicing at 900 Myr takes 4 s instead of 3.5 min. One set of layer names. `planet delete run:/world:/zoom:` and `--orphans`. Threaded server. **All old outputs were deleted and regenerated.** |
| `lakes` | Lakes on the run globe: fresh, salt and salt pan, with depth on hover. |
| `falls`, `falls2` | Real waterfalls in zooms: a hard-rock lip, a plunge pool, and a gorge cut back upstream. Glitch drops that bypassed the designed falls are fixed (67 → 17 across 76 zooms). |
| `ocean` | Overturning circulation: salinity from evaporation minus rain, runoff, sea-ice brine and meltwater. Sinking in the Nordic and Labrador seas; Norway's coastal sea goes 0.9 → ~5–6 °C. |
| `deltas` | Wave power and tidal range at every coast (new viewer layers). Zoom deltas take river, wave or tide shapes (Galloway). |
| `mantle` | Breakup fix, a mantle temperature field that drags plates (B′), plumes over warm mantle, lighter compacting sediment, and rift stress scaled with plate size. **Supercontinents now re-form 2–4 times per 2 Gyr.** |
| `l7jumps` | Fixes sudden 10–20-point land losses: subduction starting at an old continental margin used to split off a plate's whole ocean. |

Tests: 93 pass. Known issues were added to `docs/plan_next.md` for each merge.

## What to look at
**Showcase worlds** (level 6, final code). Each run has a world taken while its continents were spread out and one while they were gathered.

| Showcase | Run | Worlds |
|---|---|---|
| Earth-like A | 01b0f7 | 7c5adf, a873d4 |
| Earth-like B | 796a25 | 0433b2, dc3565 |
| Water world | f0a1b0 | 4adb0e, 717c6b |
| Land-heavy | 07fb28 | 6b749b, 607924 |
| Cold | 9abc92 | 04e7a7, a9cfd7 |
| Hothouse | 19385e | 28cfc4, 4d7207 |

Each world has highlights; open the Highlights section in the viewer.

**Supercontinent cycle:** run **6d9dcf** (seed 2, 2 Gyr). Play it, then look at world ffb5bd (assembled, 940 Myr) and 779b14 (dispersed).

**Waterfalls:** pick them from the zoom dropdown, or use `zoom.html?id=…`. Falls are listed under "biggest falls".

| Zoom | Falls |
|---|---|
| a85c5e | 128 m on a 251,000 m³/s river (more than the Amazon) with a 29 km gorge |
| ecbe17 | 177 m at 38,700 m³/s |
| 537a98 | 192 m at 10,400 m³/s |
| a767ae | 235 m at 7,000 m³/s |
| 09c897 | 350 m and 520 m on smaller rivers |

**Delta types**, all on world 0f7abd:
- 00975d: river-dominated, bird's foot;
- f81832: wave-dominated, arc with a lagoon;
- ce4b72: tide-dominated, funnels and tidal flats.

**Lakes on the run globe:** run 8dc2f2, elevation layer, around 180–360 Myr.

**Earth reference world:** 2f38e3. It now has the overturning ocean, plus the wave and tide layers.

**Level 7** (~30–45 min per Gyr): 0e4c66, 1ad733, f3f4ac, eef4a2, 958fd8, plus the resolution checks 1beb32 and fe7144. Each has a world with zooms. Behaviour matches level 6 closely: the same land %, landmass count and cycle timing. Of these, only fe7144 uses the final code; seed 13 on the final code was still running at the time of this report.

**Level 8:** 15b1b0 (seed 1, 1.2 Gyr, made before the final fixes). It took 4.1 h, uses 3.9 GB on disk, and frames are saved every 10 Myr. World aa1864 (800 Myr) has 5 zooms. It is slow to load in the viewer.

## Biggest open problems (details in Known issues)
1. **Fast sea-level swings are rarer but not gone.** E.g. fe7144: 40→30% land at ~1140 Myr, back to 34% by 1172. A smoothed response of ocean depth to plate reorganisations would fix it.
2. **Few closed basins.** Most generated worlds drain only 0–4% of their land inland (Earth ~20%).
3. **Plate count** median 6–7, dipping to 2–4 at times. Land runs high at 34–38%.
4. **Level-7 continents are ~300 m lower than level 6's.** Cause unknown.
5. **The rain model** is the root of several climate misses: Atlantic/Pacific salinity, a weak Ganges, and the monsoons.

## Process note
From ~06:10 to 07:30 nothing ran. The seed-13 level-7 verification run had failed at launch (zsh doesn't split `$x` into words), and my wait loop was waiting for a run that would never finish. It was restarted at 07:37.
