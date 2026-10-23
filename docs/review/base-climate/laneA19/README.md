# Lane A19: PW-632 option A (why cold worlds' glacial endings are slow)

Results are in `../stages.md`, section "PW-632 option A: what holds a cold world's glacial ice (lane A19)".
Base: main b289b95 + lane A18's branch (5d12daf), merged as cdec55d. Since A18's base main changed no run code (the
soils lane's crown fire is off in runs, `crown=False`), so A18's pickled sources stand; the time zoom's plants do take
crown fire, which moves extra / left by up to ~2 m. The step-2 tree is a detached worktree at cdec55d with
`../laneA17/step2_stable_summer.diff` applied (`$S2WT`, default `<scratch>/a19_s2`). Sources: A18's pickles
`<scratch>/a18_src_{s1,s2}[_SEED].pkl` (L4, 300 Myr, seeds 1-9; `../laneA18/xzoom.py dump` remakes them).

Scripts (run from a tree's root with `PYTHONPATH=.:tests`; all import `planet` before numpy, lane A16's trap):
- `scan.py SRC.pkl [k=v ...]`: the endings test's numbers on SRC with TZParams overrides, the extra ice by latitude at
  the ending and 15 kyr on, the index-on run's flows (Gt/yr).
- `diag.py SRC.pkl [k=v ...]`: the extra ice split by what holds it (land above / below its equilibrium line, marine
  grounded), with surface, thickness, smb, warm month, bed depression; the marine ice at fronts / behind shelves.
- `diag2.py SRC.pkl`: 15 kyr after the ending, the leftover's warm month and smb (A) as run, (B) with the index-off
  run's climate fields (the full climate's answer to the sheets taken out), (C) without the ice surface's local terms.
- `hold.py SRC.pkl [k=v ...]`: the index-on run with I held at 0 after its first ending, 120 kyr on: is the leftover
  slow or held?
- `batch.sh SCRIPT < jobs`: jobs of `TREE SRC [k=v ...]` (s1 = this tree, s2 = `$S2WT`), 8 at once.

Outputs: `base_scan.txt` (seeds 1-9 both trees), `levers1.txt` / `levers2.txt` (TZParams levers on the four failing
worlds), `sun1.txt` (the insolation-melt probe), `frontmelt1.txt` (the frontal-melt probe), `diag2_base.txt`,
`hold_base.txt`, `hold_levers.txt`, `pytest_endings_s{1,2}.txt` (the real test on each tree), `tz_earth_*.txt`.
Probe diffs (relative to cdec55d, not merged): `sun_melt_probe.diff` (the orbit's sunshine change melts a melting
surface directly), `front_melt_probe.diff` (a marine front's retreat by its sea's annual water above freezing).
