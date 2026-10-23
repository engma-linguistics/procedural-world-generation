# Handoff: thermostat lane 1024, after steps 1-2 (step 3 in progress)

Branch `worktree-agent-aacd696776c504933`. Steps 1 (PW-680, cde32c2) and 2 (PW-636, a99cd2c) are committed and green
(README.md). Step 3 (PW-681 + PW-653) is measured in part; nothing for it is built. The first agent handed off at
its tool-call / context budget.

## Set-up a new agent needs
- **Mantle bases.** Every tree must hold the main checkout's `planet/tectonics/__pycache__/mantle_basis_*.npy` (copy
  them in before the first run), or it may run other worlds from the same code (draft
  `draft-mantle-basis-cache-picks-the-world.md`). The worktree and every scratch tree below have them.
- **Scratch trees** (session scratch `t1024/`, `/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/t1024/`;
  each with the store links and the bases): `tree_m0` (52f25a9, merge-1024's main), `tree_s2` (feec571, + A22/A23),
  `tree_s3` (c13b567, + A20 shelf air), `main_tree` (main 12b2b02 = merge-1024 step 4, PW-627), `pace2_tree` (main +
  PW-636 = this branch's physics), `fix_tree` (a copy of pace2_tree for a step-3 experiment, unchanged so far).
- **Scripts here:** `sweeps.sh` (health `--quick` per tree, 24-core cap), `hpair.py` (pooled health with SEs, paired by
  seed), `diag.sh` (ice_diag 1 Gyr L6 on the 10 thermostat seeds; `SCRIPT=srcsplit.py` logs the source's parts),
  `decomp.py` (the CO2 answer split into sink fb - source fb, with the sink's parts), `curves.py` / `icecurve.py`
  (ice against dT, pooled / per seed with SEs), `srcparts.py` (the source's parts on the drift), `static.py` +
  `mkmoment.py` (the climate's own sink sensitivity on fixed geography), `bedtol.py`, `lagcheck.py` (step 1).
- CPU: keep to ~24 cores (health `W=6 TH=3` while ~8 cores of ice_diag run; pytest `-n 4`, `PW_SEED_WORKERS=3`).

## Step 3 so far

**Thermostat at 3 C per doubling (PW-653), ice_diag on the 10 seeds** (`t1024/diag_<tree>/summary.txt`):

| tree | CO2 answer (trends out) median, in band | sink's own fb | source fb | sink parts: area / supply / temp / plants |
|---|---|---|---|---|
| s3 (c13b567, before PW-627) | +0.42, 5/10 | +0.59 | +0.15 | +0.04 / +0.21 / +0.41 / -0.10 |
| s4 (main, PW-627) | +0.24, 2/10 | +0.43 | +0.17 | +0.05 / +0.09 / +0.34 / -0.07 |

- A23 expected the sink fb to go 0.39 -> ~0.51-0.56 at 3 C per doubling: s3 has it (0.59); main has 0.43. Per seed,
  s3 0.60 +- 0.04 (mean +- SE) against s4 0.43 +- 0.02: ~3.8 SE apart; most of it is the supply part (0.23 vs 0.09,
  ~2.6 SE) and some the temperature part (0.42 vs 0.36, ~1.3 SE).
- **Not the climate model:** on fixed geography (`static.py`: Earth L6 and three L5 moments, the s3 and s4 climate
  code side by side) the sink proxy's sensitivity is the same to 1% (Earth +0.074 / +0.073 per C; land T +0.78 /
  +0.77 C per C). So PW-627 does not change the climate's own sink sensitivity; the in-run difference is the runs'
  (erosion supply, ice) or chaos. The in-run g (~0.04-0.055 per C) is ~60% of the static one (~0.074): worth a look.
- **The source answers the drift positively** on both trees (median +0.15 / +0.17 C/C; 20 seed-runs: mean +0.13 +-
  0.07). That is a warm-reinforcing source, against the thermostat. The volcanic source is ~95% arc growth (L4 seed 1:
  92%; L6 seeds 1 and 2 of `diag_pace2_tree_src`: 95%), and the arc growth carries the continental-volume thermostat's
  gain (`crust.thermostats`, median x2.2, 5-95% x1.45-3.3). Hypothesis tested: erosion -> volume deficit -> gain ->
  CO2. On the 4 seeds done on PW-636's tree (`step3/srcparts_4seeds.txt`: 1, 2, 5, 7) the gain's own answer on the
  drift is ~0 (-0.05..0.00), so **not confirmed**; and there the source's answer is *negative* on all 4 (median
  -0.17), so its sign moves with the worlds: chance so far, as stage 4 found. The other 6 seeds are not run
  (`SCRIPT=srcsplit.py SUFFIX=_src diag.sh pace2_tree "11 13 21 42 99 3199"`, then `srcparts.py`). Even if the gain doesn't answer the climate,
  the CO2 source is set by a bookkeeping thermostat's gain x2.2: a candidate for a sound mechanism (outgassing from
  the subduction flux, not from the volume thermostat's correction), but it needs its own measurement first.
- **Ice against dT** (`curves.py`, `icecurve.py`): s4 holds a little more ice at a given dT (mean ice SL at dT -1..+1:
  -59 +- 8 against -46 +- 8 m; icehouse share there 63 vs 64%): within the noise. The deep eras on s4 come with a
  milder drift (-0.8 against -3.0 C) and a CO2 term below its reference (-0.6 C, low source x0.85) where s3's had
  +1.0 C: the deep eras are where the source runs low. Earth plausibility: s4's ice SL at dT 0..+1 is -57 m (Earth
  ~-65 m) and at dT -5..-6 -209 m (LGM-like ~-190 m): plausible on both trees.

**PW-681, the third seed set (201-216, health --quick; `step3/health_s3_201.md`, `step3/health_s4_201.md`):**

| tree | pooled % kf < -150 m (+- SE) | seeds > 10% | old bar F | new bar F | icehouse % median / mean |
|---|---|---|---|---|---|
| s3 (A20 shelf air) | 11.0 +- 4.4 | 5 | 0 | 6 | 36.2 / 41.5 +- 8.5 |
| s4 (PW-627, main) | 9.8 +- 4.0 | 4 | 1 | 6 | 44.1 / 44.5 +- 8.1 |

s4 - s3: deep share -1.2 +- 5.9 points, icehouse +2.9 +- 10.1. **PW-627's step does not deepen the icehouses on a
fresh seed set**: merge-1024's 101-108 jump (7.3 -> 20.1%) looks like those 8 worlds' draw. m0, s2 and pace2 are
still to run (the sweep was stopped at the hand-off; its empty run folders were removed):
`W=6 TH=3 bash sweeps.sh 201 "201 ... 216" tree_m0 tree_s2 pace2_tree` (each ~20 min). Then
`hpair.py m0=... s2=... s3=... s4=... s5=...` and the verdict (chaos or signal per step, with SEs; merge-1024's
101-108 and default sets add 16 more seeds per tree for m0..s4: `merge-1024/<step>/health_*.md`, same code).

## What's left
1. Finish the 201-216 sweeps and the 6 srcsplit seeds; verdict on PW-681 (record on PW-681 and PW-653).
2. Decide the cause: if the sink fb drop (s3 -> s4) holds up, find where the supply part lost its answer (erosion's
   response to runoff in the run vs static); if the source's positive answer holds up, whether it is the arc gain.
   A sound fix is built only if the cause is clear (owner's rules; ~5 attempts). Otherwise a needs-decision draft with
   the options.
3. Record the thermostat numbers in `docs/review/base-climate/thermostat.md` (PW-653's checkbox).
4. Merge main before the final report; delete own store runs (`health ... seed 2xx` runs are deleted by health.py
   itself; the scratch trees are scratch).
