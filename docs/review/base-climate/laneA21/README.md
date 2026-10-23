# Lane A21: why A20's worlds failed the forest-to-tundra test (PW-640, PW-643)

Results are in `../stages.md`, section "PW-640: the forest test's 12 of 24 is the worlds' lottery (lane A21)".
The branch is main 1fc1f9d, plus PW-643's harness (cherry-picked 8f090f8), plus A20's branch (a1462d3, the
shelf-air rule) merged. No `planet/` change. Main's tree is a `git archive main` export in this session's
scratchpad, with the harness's `tests/` copied over it.

Every script runs from a tree root with `PYTHONPATH=.:tests:docs/review/base-climate/laneA21`. They import
`planet` before numpy (lane A16's trap).

- `fdiag.py CACHE OUT [a-b]`: on each L4 300 Myr world, the forest test's numbers with F split up:
  - snow-free against snowy albedo;
  - cells that lost trees, gained them, or neither;
  - |lat| below 40 and above it.
  Beside them it records the world's own numbers: land fraction and latitudes, ice, shelves, sea level, CO2, the
  start's land air, SST, sea ice and snow, and tree area by belt. `PW_EPS=x` builds the runs with
  `climate_offset = x` C. That is a null perturbation: the same physics, another chaotic draw.
- `fdiag.sh`, `fdiag2.sh`: the jobs (4-6 workers each, at most 12 at once). Their outputs are `fdiag_<tag>.json`:
  - `main`, `a20`: seeds 1-24, the harness's worlds;
  - `main_eps`, `main_eps2`, `main_epsm`: main's null draws at +0.001, +0.002 and -0.001 C;
  - `a20_eps`: A20's null draw at +0.001 C;
  - `main_25_72`, `a20_25_72`: 48 more seeds on each tree.
- `ftable.py` writes `ftable_all.txt` (per-seed and mean tables). `fpool.py` writes `fpool.txt`: every draw
  pooled, with the correlations, F's parts on passing and failing worlds, and the two populations compared.
- `tcount.py`, `tcount.sh` write `tcount_<tag>.txt`: the tests' own `_forest_case` and `_endings_case`
  (`seeds.check_rate`'s tables) on the cached sources.
- `l5scan.py`, `l5scan.sh` write `l5scan_{main,a20}_eps0.001.txt`: the cold-moment tests' counts (plausible
  seeds of 25-50, sheeted, speeds, index 0) on a null draw of each tree.
- `fearth.py` writes `fearth_L4.txt` and `fearth_L6.txt`: `fdiag.case` on Earth (`timezoom.source_earth`).
