# Lane A22: why glacial cooling greened the low latitudes (PW-644)

Results are in `../stages.md`, in the section "PW-644: low CO2 is what shrinks a glacial's tropical forest
(lane A22)".

Branch `worktree-agent-ac50a7a56279c5017` contains:
- main 69db596;
- PW-643's harness (cherry-picked 8f090f8, its own commit, which can be dropped);
- the fix commit.

Main's tree for comparison was a `git archive main` export in this session's scratchpad, with the harness's
`tests/` and this lane's `tools/tz_earth.py` copied over it.

## Scripts
Run each from a tree root with `PYTHONPATH=.:tests:docs/review/base-climate/laneA22`.

- `lowlat.py [level] [dT] [co2]`: on Earth, the plants are grown on the start's climate and on a cooled one, and
  on swaps that separate the cooled temperature, the rain and the CO2. Each case is reported by |lat| belt:
  - rain, PET and P/PET;
  - tree area;
  - the forest, savanna-grass and desert areas;
  - F.

  Outputs:
  - `lowlat_{main,a22}_test.txt`: the forest test's setting (-4 C, index -1/3).
  - `lowlat_{main,a22}_glacial.txt`: the zoom's own glacial maximum on Earth (-6.22 C, index -1.04).
- `lowlat_split.py`: the cooled temperature split into the PET part and the part that acts inside the plants.
  It was run on main before the fix. The numbers are in `stages.md`.
- `fdiag.py`, `tcount.py`, `l5scan.py`, `fearth.py`: lane A21's scripts, unchanged apart from the paths.
  - `jobs.sh` writes `fdiag_a22*.json` and `tcount_a22*.txt` for seeds 1-24, on the harness's worlds and on the
    null draws at climate_offset +0.001 and -0.001 C.
  - `fdiag_main*.json` are copied from lane A21. Main's `planet/` has not changed since then.
  - `a22pool.py` writes `a22pool.txt`.
  - `l5scan_a22_eps{0,0.001}.txt` hold the cold-moment counts.
  - `fearth_a22_L{4,6}.txt` hold Earth's F decomposition.
- `co2range.py`: the runs' CO2 index in the store.
- `tz_earth_{main,a22}.txt/.json`: `tools/tz_earth.py --level 6`. It now also prints the forest share by latitude
  band at the interglacials and at the glacial maxima.
- `health/`: `tools/health.py --quick` on this branch. `health_main_report.md` is the same sweep on main's export.
