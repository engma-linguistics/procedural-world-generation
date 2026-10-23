# Lane A16: PW-596 option A re-measured on the PW-576 base

The results are in `../stages.md`, section "PW-596 option A on the PW-576 base (lane A16)".

The scripts take a second checkout of main as `$MAINWT` (default: the session scratch `mainwt`, a detached worktree
at 2180b8e with `data/earth` symlinked).

- `tools.sh SUFFIX`: earth_check, climate_bias and the overturning (Earth + 9 worlds). Outputs `*_branch.txt`;
  they are identical to `../laneA15/*_after.txt`.
- `pytest_branch.txt`: the tail of the branch's `pytest -q`.
- `health_main.md`, `health_branch.md`: `tools/health.py --quick` reports (main 2180b8e, branch).
- `coldscan.sh` / `coldscan.py`: the cold_moment fixture's precondition and sheet share for every seed.
  Outputs `coldscan_{main,branch}.txt` (25-35) and `coldscan_*_36-50.txt`. These scripts import `planet` before
  numpy: the other order changes the run.
- `xcold.sh` / `xcold.py`: the run's ice rule (`_cold`) on a fixed world with each tree's climate, and the
  `belt1` / `col1` toggles. Output `xcold.txt`.
- `xzoom.sh` / `xzoom.py`: the icehouse test (glacial extra / left) on sim4's source from each tree with each
  tree's climate. The numbers are in `stages.md`. Its dump imports numpy first, but its own-tree numbers equal the
  test's printout (main 93.0 / 15.3, branch 49.9 / -0.5).
- `rundt.sh` / `rundt.py`: one run's dT under 6 hash seeds. It is independent of the hash seed.
