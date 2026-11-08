# PW-1446 (b) scout 190: the crust cap is on the column's height

Scout 190, 2026-11-04, on main 879b0abb. Scripts beside this file: `scout3_world.py` (splits a stored world's high cells
into Airy + sediment lift + the rest, and a static re-cap), `scout3_decomp.py` (the same from a run checkpoint; the
10fd90 checkpoints are of older code and won't load, so it is kept for new runs), `scout3_earth.py` (Earth's L6/L7 cell
hypsometry), `scout3_hyps.py` (paired hypsometry of two judge arms). `tools/ice_diag.py` now records the bed's
hypsometry every 10 Myr (`hyps`), so a judge arm carries it.

## In plain words

- **The cause.** The model stops crust thickening at 80 km, which stands 7.0 km high. Sediment and plume swell then add
  up to another 1.0-1.3 km on top. On Earth, what stops a thickening crust is how high its column stands, not how thick
  it is. A plateau that is held up too high spreads and pulls apart under its own weight (Dewey 1988). Tibet's mantle
  uplift of up to 2 km turned it to east-west extension (England & Houseman 1989). So the extra buoyancy should thin the
  crust, not raise the ground.
- **The sediment part is not wrong.** It already floats the way it should: a km of sediment adds about 270 m, not
  1,000. Candidate 3 is already the code.
- **The change.** The crust cap becomes a height cap. A column's crust may be at most 80 km, less what its sediment and
  swell already lift it by (`isostasy.max_km`). Nothing below the cap changes. No taper, no new constant.
- **Hypsometry, 8 high-mountain draws, same draws on main.** The highest cell ever falls from a median 8,272 m to
  6,970 m. The share of samples with any cell above 7 km falls from 33% to 0. Cells above 6 km fall from 12 to 0, and
  land above 4 km from 1.44% to 0.93% (Earth: 1.5%). Earth's highest cell is 5,415 m at L6 and 5,878 m at L7.
- **Climate.** On the 8-draw screen: 0 hard failures, and every late climate inside -6..+5 C. On the full 36-draw judge:
  **1 hard failure** (one draw ends frozen; on main that same draw is a hot failure) and a spread of 1.80 C against the
  bar's 1.3-1.7. Soft passes are 29 against 31 (chance), and the late climate is +0.56 C warmer (inside chance).
  **It misses lane 181's bar**, so it is committed on the branch and not proposed for merge as is.

## 1. Diagnosis (written before any run)

### What the code does
`isostasy.elevation` gives continent `250 + 150 (thick - 35)` m (Airy, 150 m per km of crust), plus `sediment_lift`, plus
the datum (plume swell + flexure/sag - sea level). Crust is clipped to `MAX_KM` = 80 km in two places
(`crust.flow_and_orogeny` and `Simulation._write_back`). So a column at the cap stands at 7,000 m plus whatever its
sediment and swell add.

### Is the sediment lift itself wrong? No.
The sediment is part of `thick`, and `sediment_lift` adds only the buoyancy deficit of that sediment against crust
(`K_LAND (rho_cont - rho_sed(z))` integrated over the pile, with Athy compaction to 2.6 g/cm3 at depth). Together with the
150 m/km that the same km already gets as crust, a km of sediment stands `1000 (1 - rho_s / rho_m)` m: about 270 m at
2.4 g/cm3. That is exactly candidate 3 ("load sediment isostatically"), and it is already the code. Sediment on a thick
root does sink isostatically here. Candidate 3 is therefore not a change.

### What is wrong: the cap is on thickness, but what limits a thickened crust is its height
- A plateau or belt stops thickening because a high, isostatically held-up column spreads under its own weight: extension
  and collapse, driven by the gravitational body forces of isostatically compensated uplift (Dewey 1988, Tectonics 7(6),
  1123-1139, as summarised by the EGU Tectonics & Structural Geology "TS must-read" review: collapse needs "the
  isostatically compensated topography" to be "regionally high"; removal of the lithospheric root is a listed trigger,
  followed by "isostatic reequilibration, which reduces topography through extension").
- England & Houseman 1989 (JGR 94, 17561-17579, abstract): convective removal of Tibet's lower lithosphere raised the
  surface by "as much as 2 km" and its potential energy by 5-10 x 10^12 N/m, which is "sufficient for east-west
  extension ... to replace north-south compression". So thermal (mantle) uplift on a plateau at its limit is spent on
  thinning the crust, not on standing higher.
- England & Houseman 1988 ("The mechanics of the Tibetan Plateau") frame the plateau's height as limited by the strength
  of the continental lithosphere (search result summary only, the paper was not read).
- Lower-crustal flow relaxes lateral pressure differences, which are set by surface height (Clark & Royden 2000, Geology
  28, 703-706; abstract and citing summaries only).

The model's cap is the stand-in for that limit, so it should be a cap on the column's height (its potential energy),
not on its thickness. At the cap, 1 km of sediment lift or swell is 6.7 km of crust too much: the crust should thin by
that, as Tibet's did. Today the sediment lift and swell instead stack on top of the 7.0 km cap height. On dba204
(`scout3_world.py`), cells > 6 km hold a median 2.5 km of cover (p90 8.3 km) and so 370 m of sediment lift (p90 810 m,
max 1,040), and the rest of their excess (swell + flexure/sag - sea level, net of the ice's load) is a median +70 m, p90
+490 m. The top ten cells: 80 km crust, 1.3-10.6 km cover, 230-960 m sediment lift and +320 to +720 m rest.

### The three candidates
| # | candidate | physics? | verdict |
|---|---|---|---|
| 1 | no lift above Airy at the cap | yes, if done as a cap on the column's height that thins the crust | **chosen**, as `isostasy.max_km` |
| 2 | taper both lifts as the crust nears `MAX_KM` | no: a taper is a shape picked to hide the step, with a free width | rejected |
| 3 | load sediment isostatically, (1 - rho_s/rho_m) | already the code (see above) | no change |

### The mechanism
`isostasy.max_km(cont, cover, extra)` = `MAX_KM - (sediment_lift + max(swell, 0)) / ISO_LAND` on continent (never below
the cover), `MAX_KM` at sea. Both caps use it. The crust beyond it is deleted as the cap already deleted it (booked as
`flow+cap` / `clip`). A continent then stands no higher than 80 km of plain crust would (7.0 km) plus flexure/sag and minus
the sea level. When a swell decays, the thinned plateau subsides below the cap, as a collapsed plateau would. Cells below
the cap are untouched, so a run is identical until a column first reaches it.

What it does not do: the cap height itself (7.0 km at 80 km) is above Earth's highest L7 cell (5,878 m). Static re-cap of
dba204 (crust thinned to the new cap, nothing else re-run): cells > 7 km 120 -> 28-112, highest 8,233 -> 7,000-7,820 m
(bounds: sediment lift only, or lift plus the positive rest), cells > 6 km 231 -> 231. Cells of 6-7 km sit just below the
cap and are not touched. So this removes the stacked overshoot, not the height of the cap.

## 2. Paired screen (8 L6 draws, 1 Gyr)

Draws: roll 0.0005 of `l6fix` (seeds 957317, 619496, 583167, 639472) and `l6c_0` (53669, 733847, 819014, 958504), so
all eight seeds. Six of the eight have a highest cell above 7 km in a third or more of samples on main, so they are
the high-mountain draws. Both arms ran exactly as `paired.sh` runs a draw (scratch `screen.sh`, 1 thread, 4 at once),
from frozen copies: `main` = main 879b0abb plus the `ice_diag` hypsometry record (c1ae3fda), `cap` = that plus the
change. The main arm reproduced lane 181's `kn` arm (main's physics) to the second decimal on every draw's late dT, so
the record changes nothing and `kn` is a valid baseline for the full judge.

### Hypsometry (`scout3_hyps.py`; bed, medians over 100-1000 Myr, sampled every 10 Myr)
Baselines: main is the same draw on current code. Earth is ETOPO1 cell means on the same grids (`scout3_earth.py`,
`data/earth/L6.npz` / `L7.npz`, the bed).

| | land > 2 / 3 / 4 km | cells > 5 / 6 / 7 km | highest cell (median) | highest ever | samples with a cell > 7 km |
|---|---|---|---|---|---|
| Earth L6 | 4.68 / 2.43 / 1.51% | 41 / 0 / 0 | 5,415 m | | |
| Earth L7 | 4.88 / 2.53 / 1.59% | 171 / 0 / 0 | 5,878 m | | |
| main, median of 8 draws | 8.52 / 3.72 / 1.44% | 67.5 / 12 / 0 | 6,509 m | 8,272 m | 33% |
| cap, median of 8 draws | 7.56 / 2.69 / 0.93% | 34 / 0 / 0 | 5,843 m | 6,970 m | 0% |

Per draw, the highest cell ever falls from 7,307-8,510 m to 6,896-7,483 m. (The few above 7.0 km stand on sag uplift or a
sea level below the datum, which the cap does not include.) In 7 of 8 draws the share above 4 km falls; in 957317, main's
lowest-relief draw, it rises (0.25 to 1.00%) because that run's tectonics diverged. Land above 2 km stays at 1.5-1.8x
Earth's. That excess is mid-height ground, not the cap (scout 171's other half of PW-1446).

### Climate (`tools/judge.py paired`, `tools/hard_bar.py`, late = 600-1000 Myr)
- Hard bar: 0/8 on both arms (frozen over at the end, boiled, ocean loss, CO2 crash).
- Soft pass: main 8/8, cap 7/8. The one lost is 583167, whose end T is +7.4 C. Its late dT is +1.61 (main +1.82), so it
  is the end moment, not the late climate.
- Late dT: every draw is inside -6..+5 C on both arms (main -1.43..+2.82, cap -0.16..+4.17). Spread sd 1.44 (main) vs
  1.57 (cap).
- Paired, cap - main: late dT +1.92 C (95% CI -1.44..+3.27, 5 up / 3 down), end T +2.26 (CI -0.21..+5.48), late CO2
  index +0.17 (CI -0.13..+0.45). None of these moved by the judge's rule. Land share +0.8 points (CI +0.37..+1.26, 7/1)
  moved. Trees +5.0 points and land rain +71 mm/yr are near the edge.
- Reading: the sign is what PW-451 warns of (less high ground, a weaker weathering sink, a warmer climate), but on 8
  draws it is within chaos. The full judge decides it.

## 3. Full paired judge (36 L6 draws, 2 rolls x 18)

`cap` arm: `paired.sh` from the frozen copy (scratch `run_full.sh`, MAXSIM 5, THREADS 1), keeping the screen's 8.
Baseline `main`: lane 181's `kn` arm, copied (main's physics is unchanged since 98547e1e, and §2 showed it reproduces).

| | main | cap | lane 181's bar |
|---|---|---|---|
| hard failures (`tools/hard_bar.py`) | 0/36 | **1/36** (frozen over at the end) | 0 |
| soft pass | 31/36 | 29/36 (McNemar p 0.69: 4 lost, 2 gained) | within chance of main: yes |
| late dT range | -1.43..+4.35 | -2.14..+4.39 | inside -6..+5: yes |
| late dT spread (sd) | 1.25 | **1.80** | about 1.3-1.7: **no** |
| late dT, paired cap - main | | +0.56 C (CI -1.16..+1.70, 20/16) | |
| end T, paired | | +0.30 C (CI -0.62..+2.19) | |
| late CO2 index, paired | | +0.01 (CI -0.13..+0.24) | |
| land rain, paired | | +37 mm/yr (CI +1..+62, 24/12), the only measure that moved | |

The hard failure is r0.0005 `l6c_m` seed 958504: it ends at -8.0 C and is frozen over. On main the same draw fails
the soft bar the other way: it ends at +7.8 C. The other roll of that planet and offset passes on both arms (cap +0.2,
main +2.9). So it is a cold-tail chaos draw of the kind PW-1404 describes, not a sign that the cap cools worlds: the
paired late dT and CO2 both lean slightly warm. But the bar as written is 0 hard failures and an sd of 1.3-1.7, and
this arm misses both. Per the brief, I have not tuned anything.

Hypsometry over all 36 cap draws (main's 28 extra draws have no `hyps` record): median land > 2 / 3 / 4 km 7.24 /
2.85 / 0.97%, cells > 5 / 6 / 7 km 34 / 0 / 0, median highest cell 5,866 m, highest ever 7,001 m (median of draws).
That matches the screen. One sample stands out: r0.0005 `l6c_p` 619496 has a 10,576 m cell at 260 Myr, with the
continent's thickest crust at 71.7 km, so it is not a cap cell. It is probably a hotspot pile at sea (the PW-172
family). Main has no record of that draw to compare (draft on file).

## 3b. Re-roll of the hard failure (coordinator's request)

r0.0005 `l6c_m` seed 958504 was re-run on both arms at the README's rolls 3 and 4 (0.0015, 0.002), from the same
frozen code (main c1ae3fda, fix 59d774f3, physics identical to the judged 3235e2b1), 1 thread, 4 at once.

**The re-rolls are not new draws.** `l6c_m`'s offset is -0.001, so rolls 0.0015 and 0.002 give offsets 0.0005 and
0.001. Those are exactly `l6c_0`'s rolls 1 and 2 for the same seed, and the runs reproduce them to the last digit (fix
+0.4 / -0.2 end T, main +4.6 / +2.7). So for `l6c_m` the README's 4-roll scheme collides with `l6c_0`.
(For `l6c_m`, rolls 0.0015 and 0.002 add no new runs; `l6c_p`'s go to 0.0025 and 0.003 and are new.) Seed 958504 has only four distinct runs in the set, at offsets -0.0005, 0,
+0.0005 and +0.001:

| offset | main late dT / end T / pass | fix late dT / end T / pass | fix - main late dT |
|---|---|---|---|
| -0.0005 (l6c_m r1) | +2.65 / +7.8 / fail (hot) | -2.14 / -8.0 / **fail, frozen over** | -4.79 |
| 0 (l6c_m r2) | +3.08 / +2.9 / pass | -1.20 / +0.2 / pass | -4.28 |
| +0.0005 (l6c_0 r1) | +1.69 / +4.6 / pass | +2.24 / +0.4 / pass | +0.55 |
| +0.001 (l6c_0 r2) | +0.98 / +2.7 / pass | -0.05 / -0.2 / pass | -1.03 |

- **Is the frozen end chaos or a lean?** Both, at different levels. The frozen end itself is the tail: the fix passes
  the other three runs of that planet, and the frozen one sits next to main's hottest fail. But this planet leans cold
  under the fix: 3 of 4 offsets are cooler (median -2.6 C), while the 36-draw arm as a whole leans +0.56 C warm. On this
  seed, removing the high plateau's top seems to push the carbon cycle toward its cold tail. On the other seeds it does
  not, so this is per-planet chaos in the response's sign, not a set-wide cooling.
- **Spread.** The fix arm's late-dT sd is 1.80 over the 36. Without the frozen draw it is 1.71, and with that planet's
  two `l6c_m` rolls pooled into their mean it is 1.74. Leaving out any single draw gives at least 1.71. So the frozen
  draw adds about 0.1. The rest is a broad widening, not one draw: the fix has 10 draws below 0 C late dT against main's
  5, and 9 above +3.0 against 3. Main's sd is 1.25 (1.24 pooled the same way). Pooled over all 38 runs, counting the
  duplicates, the fix's sd is 1.78.
- Pass count with the re-rolls: main 33/38, fix 31/38. Hard failures stay main 0, fix 1.

## 4. Tests

Not-slow suite on the branch (`-n 4`, NUMBA_NUM_THREADS=4): 1012 passed, 1 skipped, goldens included and unmoved. The tectonics-area tests (isostasy, crust, rifts, tectonics, ice_diag: 21) passed before the screen. `scorecard.py` and `earth_check.py` were not run, because the judge failed the bar (brief step 4).

## Status

Scout done, 1 pass. The change, `isostasy.max_km`, is the physics and does what PW-1446 (b) asks: the top cell goes
from 8.3 km to 7.0 km, no frame has a cell above 7 km, and land above 4 km falls from 1.44% to 0.93%, against Earth's
1.5%. It fails lane 181's merge bar on two counts: one hard failure (a chaos cold-tail draw whose main pair is a hot
fail) and an sd of 1.80. It is committed on this branch, not merged. Re-roll (§3b): the frozen end is the tail of a planet the
fix pushes cold on 3 of 4 offsets. The sd stays at 1.71 or above without it, so the spread miss is the arm's, not one
draw's. The README's rolls 3-4 duplicate `l6c_0`'s runs for `l6c_m` draws, so they add no new runs there. Not done: the cap height itself (7.0 km at 80 km) is above Earth's
5.4-5.9 km highest cell, and land above 2 km stays at about 1.5x Earth's. Both are other halves of PW-1446, not this
change.
