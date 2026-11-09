# PW-054 scout 250, pass 2: dry hollows, limited to dry catchments

Branch `worktree-agent-adfa5180f5376146a` on main 4edd6cff. Pass 1: `scout247.md`. Scripts: `scout250/`
(read-only; nothing written to runs/ or worlds/). The code is `scout250/pass2.patch` (with a test), not applied on
the branch. "Inland" is health's `inland_pct` (% of ice-free land whose
water ends on land), frames after 50 Myr; "giant-lake frames" is health's `giant_lake_frames` check (% of
keyframes after the spin-up with a lake over 1 Mkm2), the measure pass 1's table used.

## In plain words
Pass 1's rule ("a hollow no river leaves stays closed, however shallow") also closed wet flat hollows and made
giant shallow lakes on Earth's terrain. Pass 2 keeps the rule only where the hollow's whole catchment is
dryland by the climate's own land evaporation, and only where the lake leaves part of the hollow's floor dry.
On Earth that removes the wet mistakes (the Sudd/White Nile, a 3 Mkm2 lake at L7; the Indus at L6): what the
rule still adds is desert (~200-270 mm of rain), about half of it real closed basins, and Earth at L7 gets
19.4% inland against the real 21.3%. It still counts some desert land inland that really drains to the sea
(Mesopotamia, the Thar, the Texas plains), so the "no more false positives than main" bar is missed by
1.3-1.8 points. On generated worlds (L6, 4 seeds) inland drainage goes from 7.2% to 12.4% (the same code on
Earth at L6: 13.9%), and at L7 (seed 11, against main run alongside) from 6.1% to 18.8% (Earth at L7: 19.4%).
Lakes grow from 0.72% to 1.07% of land at L6, and giant-lake frames double (L6 6.4% -> 12.8%; L7 0 -> 7%), but
109 of the 113 giant lakes of the L6 runs (42 of 43 at L7) sit in hollows deep and steep enough that main keeps
them too: the runs take other paths, and one draw per seed can't tell whether that is the rule or chance. The
rule also costs ~14% more run time at L7. Not a merge yet: one more pass to settle the giant lakes on forked
runs and to cut the cost.

## 1. The criterion
`hydrology._dry_hollows` (called from `_settle` when `lakes()` gets `pet_mm`):
1. Candidates: the closed hollows of the unfiltered ground (lake balance on it never reaches the rim), as in
   pass 1.
2. Their lakes and catchments are taken again on `_bed`'s ground with the candidates put back, so a shallow
   hollow upstream that `_bed` fills passes its river on into them.
3. Kept only if the catchment (the hollow and all land draining into it) is dryland: catchment rain
   < `DRYLAND_AI` (0.65) x catchment potential evaporation, the climate's own land PET (`climate.water_balance`'s
   Oudin `pet`, the one `landform.aridity` uses), not the open-water evaporation pass 1 tried. 0.65 is the
   aridity index's drylands bound ("drylands are lands with an AI of less than 0.65"
   [earthmap.org, aridity index](https://help.earthmap.org/datasets/climate/aridity-index); that page's PET is MODIS's, not Oudin's: the bound is the index's, not a fit).
4. ...and only if its lake at balance leaves some of the hollow's floor dry (the lake stops short of the rim).
   A hollow its lake fills, most often a one-cell dip on a big river's course, is as likely to spill as not
   within a cell.
5. After the rivers settle (`closed_excess`'s rerouting: a spilling lake's river sent on into a lower closed
   basin, PW-122), each kept hollow's catchment is checked again on the final routing; a hollow the rivers made
   wet goes back to `_bed`'s rule (at most 3 rounds).
Kept hollows keep their own ground in the bed (no digging; pass 1's dig and this reset gave identical Earth
numbers). The run's erosion step passes the climate's `pet` too (`sim.pet`, a new state field), so runs and
worlds use one rule.

The sensitivity to the 0.65 bound is small (Earth L6 inland 14.8 / 14.4 / 13.9% at 0.65 / 0.5 / 0.3 before
steps 4-5): the catchment test is not a tuned clamp, it barely binds where the rule's gains are. Steps 2, 4 and 5
are what removed the wet false positives.

## 2. Earth (terrain + the model's climate, nothing imposed; `scout250/earth_dry.py`, `earth_added.py`)
"False +" = inland land outside HydroSHEDS's real closed basins, % of ice-free land.

| | L6 main | L6 pass 1 | L6 pass 2 | L7 main | L7 pass 1 | L7 pass 2 |
|---|---|---|---|---|---|---|
| inland % (HydroSHEDS real: 20.5 / 21.3) | 10.7 | 14.8 | **13.9** | 16.9 | 22.4 | **19.4** |
| share of real closed area found | 42% | 49% | 49% | 53% | 61% | 59% |
| false + | 2.1 | 4.8 | **3.9** | 5.5 | 9.5 | **6.8** |
| false +, mean rain mm | 589 | 441 | **496** | 480 | 705 | **432** |
| land added: % of land, real closed share, rain | - | 4.1, 36%, 245 mm | 3.2, 43%, 266 mm | - | 5.5, ~29%, ~890 mm | 2.5, 47%, 194 mm |
| lakes % of land, largest lake Mkm2 | 1.77, 0.24 | 1.83, 0.24 | 1.81, 0.24 | 2.71, 0.22 | 3.08, 0.34 | 2.71, 0.22 |

(Pass 1 columns from `scout247.md`; this script on the pass-1 rule gives the same at L6 and 22.2 / 9.2 / 714 mm at L7.) The rain bar (false positives under ~500 mm)
is met; the false-positive bar (at or below main's 2.1 / 5.5) is missed by 1.8 / 1.3 points. Where the added
land is (largest pieces; P/PET by the model's climate):
- L6: Sahara west (1.2 Mkm2, 67% real), Mesopotamia (1.1 Mkm2, 31% real; the model's Tigris-Euphrates catchment
  gets 149 mm, P/PET 0.14: the Zagros/Taurus snow is missing), Murray-Darling (0.5, 14%), Tibesti/Chad (0.4, 100%),
  Kansas (0.3, 0%), the Deccan (0.2, 0%; the model has it at P/PET 0.26).
- L7: Mesopotamia (0.66, 33%), the Niger's inland delta (0.49, 25%), the Western Australian interior (0.45, 97%),
  Tibesti (0.36, 100%), Salinas Grandes (0.2, 95%), Texas (0.17, 0%), the Thar (0.15, 4%), central Arabia (0.11, 69%).
The remaining false positives are deserts in the model's climate that HydroSHEDS drains to the sea through
channels finer than a cell or cut in wetter times (wadis); the Earth world has no `valley` memory, which in runs
keeps such outlets open, so the Earth check is if anything harsh on the rule there.

## 3. Generated worlds, L6 seeds 1 / 2 / 3199 / 77, 400 Myr (main = pass 1's runs on 19a9a4f5; no physics change since)

| | main | pass 2 |
|---|---|---|
| inland median, per seed | 5.1 / 7.2 / 8.2 / 8.2 | 9.2 / 11.0 / 15.8 / 13.6 |
| inland, mean of seeds | 7.2 | **12.4** |
| inland p10-p90, seed 3199 | 4.3-17.9 | 8.9-27.3 |
| lakes, % of land (mean) | 0.72 | 1.07 |
| largest lake, median Mkm2 (mean of seeds) | 0.20 | 0.28 |
| giant-lake frames %, per seed | 4.7 / 2.3 / 14.0 / 4.7 | 2.3 / 0.0 / 20.9 / 27.9 |
| giant-lake frames, mean | 6.4 | **12.8** |
| land %, crust volume end/start, peaks > 9.5 km | 32.6-33.5, 0.97-0.99, 0 | 32.0-33.0, 0.974-0.988, 0 |
| icehouse % (seed 1 / 2 / 3199 / 77) | 81 / 0 / - / - (pass 1) | 38 / 100 / 23 / 0 |

Are the giant lakes the rule's? `scout250/giant_hollow.py` takes each frame's largest lake over 1 Mkm2 and
measures the hollow under it (filled depth and rim-to-middle slope): of all 113 such frames of the four runs
(20 / 18 / 42 / 33, any time), 109 sit in a hollow `_bed` keeps without the rule (>= 20 m deep and >= 0.1 m/km);
only 4 (seed 1 t=24; seed 3199 t=192, 208; seed 77 t=260; 1.1-1.5 Mkm2, 64-96 m deep but flatter than
0.1 m/km) are hollows only the rule keeps. Those 4 are closed lakes under 740-1500 mm of rain on the lake: hot
hollows whose catchment the model's Oudin PET still counts dryland. Seed 77's late giants (2-3.4 Mkm2, ~400 mm of rain, 130-240 m deep) and seed 3199's (40-5000 m
deep) are ordinary deep hollows. So the rise is the runs diverging (the rule changes where the erosion step's
rivers end, so sediment and terrain go elsewhere) or chance, which one draw per seed can't separate (pass 1's
lesson: compare several re-rolled draws before calling a flip signal). Pass 1's v2 (the unrestricted rule) had
4.7 / 7.0 for seeds 77 / 3199 where this has 27.9 / 20.9, which points to chance.

## 4. L7, seed 11, 400 Myr (main 4edd6cff vs pass 2, run side by side)
| | main | pass 2 |
|---|---|---|
| inland median (p10-p90) | 6.1 (4.4-10.5) | **18.8** (11.9-31.6) |
| lakes, % of land (mean) | 1.35 | 1.57 |
| largest lake, median Mkm2 | 0.35 | 0.66 |
| giant-lake frames (health) / of frames after 50 Myr | 0.0 / 21.0% | 7.0 / 31.4% |
| giant lakes any time; in a hollow only the rule keeps | 32; 0 | 43; 1 (t=28, 1.9 Mkm2, 118 m, 0.097 m/km) |
| land %, crust volume end/start, peaks > 9.5 km, icehouse % | 34.0, 0.967, 0, 35 | 34.6, 0.982, 0, 0 |
| run time, side by side (4 threads each) | 1678 s | 1906 s (+14%) |

L7 closes the gap pass 1 found (stored L7 runs 4-6% against 16.9% for the same code on Earth at L7): 18.8% is
the same code's Earth number (19.4%) and under the real 21.3%. Main's L7 run has giant lakes too (32 frames,
mostly before the end of health's spin-up window): giant lakes are PW-300 / PW-430's and noisy per draw.

## 5. Recommendation
**Pass 3, not a merge.** The criterion does what pass 1 asked on Earth (the wet false positives and the Earth
giant lake are gone; what is added is desert and about half real), and it lifts generated inland drainage to the
same code's Earth number at both levels. Two things stand between it and a merge:
1. **Giant-lake frames doubled on single draws** (L6 6.4 -> 12.8%, L7 0 -> 7%), though almost all of them are in
   hollows main keeps too. Settle it on forks: take main's state at ~200 Myr for 3 seeds at L6 (and seed 11 at
   L7) and continue 200 Myr with main and with the rule from the same state, two re-rolled draws each; merge if
   giant-lake frames don't rise beyond the draw-to-draw spread.
2. **Cost: +14% run time at L7.** `_dry_hollows` runs two extra lake balances and floods per `_settle`, and
   `_settle` runs up to 3 times per `lakes()` (the carve tries) and up to 3 rounds each; work the dry mask out
   once per `lakes()` call (on the uncarved ground) and reuse it across the carve tries.
The Earth false-positive bar (at or below main's 2.1 / 5.5) is missed by 1.8 / 1.3 points, all desert (the
model's dry Mesopotamia and Deccan, the Thar, Texas), and Earth at L7 sits under the real share (19.4 vs 21.3):
in range for a plausibility anchor. Daniel may want to rule on that bar; I'd accept it. Scorecard and full judge:
not run (no merge recommended yet). `tests/test_golden.py` changes with the patch (expected).
