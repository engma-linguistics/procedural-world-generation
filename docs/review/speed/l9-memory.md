# Why L9 from scratch needs so much memory, and what runs on one core (2026-11-03)

Read-only investigation for Daniel's question (11-02). One L6 40 Myr memory count and one native climate update at L6/L7
were measured; L9 figures are estimates (x16 from L7 per-cell numbers). Scratch deleted.

## Short answer
About three quarters of the "bonkers" L9 memory is avoidable bookkeeping, not the planet:
- viewer keyframes held in RAM for the whole run, then all stacked again at the save (`planet/timeline.py:125,145,164`; PW-801);
- every plate carries a full-globe copy in 48 fixed slots (`planet/tectonics/plates.py:19,101-103`), ~90% of run state
  (8,237 B/cell, of which 7,392 B is plate slots; only 2.1% of slot-cells held crust in the L6 count);
- each checkpoint deep-copies the full state (`planet/tectonics/simulation.py:199`, from `planet/store.py:945`, every 100 Myr);
- the native climate update allocates ~9.7 kB/cell of numpy temporaries (L7 1.59 GB).
Check: the pieces add up to ~9.4 GB for an L7 1 Gyr run against PW-801's measured 9.94 GB.

With those fixed, L9 could fit in roughly 10-20 GB (estimate). Time is the real wall: the 2 Myr step is fixed at every level
(`planet/__main__.py:634`), but wind-carry (`climate.py:490`), the gyre solver (`climate.py:879`), rain (`climate.py:1572`,
33x per call L7->L8 in `pw252.md:100`) and sea-floor creep (`surface.py:465-466`) iterate more at finer levels: roughly 6-10x
per level, so an L9 Gyr is 1-2+ days (estimate).

## Table (time shares: L7 per-100 Myr stage table, docs/review/speed/pw252.md; memory: this count)

| Step | Time (L7) | Serial or parallel, why | Memory L7 / L9 | Cheaper alternative |
|---|---|---|---|---|
| Climate | 34% | Mixed. Gyre solver `_stommel` serial by method (sweep order, `climate.py:757`); leftover numpy single-threaded | 1.6 / ~25 GB scratch (finish window only; spin-up runs on the L6 grid, `params.py:98`) | keep L9 climate on the L7/L8 grid (as `planet refine` does); warm-start relaxations |
| Ice sheets | 21% | mass balance parallel; ring loops serial as written | small | ice on the coarse climate grid in spin-up |
| Vegetation | 13% | parallel per cell | 0.07 / 1.2 GB | float32 (changes outputs) |
| Tectonics | 10% | per-plate bookkeeping serial (last write wins, ordered sums for bit-identity) | **plate slots 1.2 / 19.4 GB** | alive-only slots (~3x) or sparse owned cells (~0.5 GB at L9) |
| Rivers, lakes | 10% | truly sequential as written (heap priority flood, union-find; `kernels.py:244,572`); parallel versions break ties differently | small | per-landmass parallel (unchecked idea); fewer settle passes |
| Ocean | 4% | small coarse grid | small | none needed |
| Keyframes | 3% | not CPU | **2.3 / ~38 GB per Gyr, doubled at the save** | stream frames to disk (PW-801); fewer frames |
| Checkpoints | - | deep copy on the main thread | 1.35 / ~22 GB, short-lived | shrink before copying (`store.shrink_state`) |
| Grid, basis, neighbours | setup | built once | 0.23 / ~3.6 GB | float32 basis; drop list-of-lists (`grid.py:209`) |
| Time steps | all | true dependency: each step needs the last | - | only separate seeds run side by side |

About half of the L7 step is still serial after PW-252 (`pw252.md:107`).

## Bottom line
- Today: L9 from scratch ~110-160 GB peak, 1-2+ days per Gyr (estimates).
- ~75 GB keyframes + save copy, ~19 GB empty plate slots, ~22 GB checkpoint copy: all avoidable with bit-identical outputs.
- Unavoidable world fields: ~1-2 kB/cell, ~3-5 GB at L9.
- Cheapest path: keep simulating at L7 and refine the finished moment (L9 refine measured 38 min, 38.8 GB peak,
  `docs/review/refine-l8/report.md:18`), or the land zoom (PW-1296/1299).
- The earlier "L9 from scratch" estimate was not found written down; the nearest is PW-801 (L7 9.94 GB) x16.
