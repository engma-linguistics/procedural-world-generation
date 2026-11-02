# PW-950 lane 100 handoff

Done (round 2, stopped by the stop rule): diagnosis.md, margindiag.py / earth_margin.py harnesses, `crust.necking`
(`neck_km`) and the continental-rise rule in `surface._offshore` (`rise`), both off by default (main's outputs and
goldens unchanged), plus `tests/test_rifts.py::test_necking_pays_for_the_margin_with_thinned_crust`. Results in
report.md: the cliff softens (next-cell share 23% -> 15% at L6, 20% -> 9% at L7) but the bands move little and the
ticket's checkboxes stay unmet; the 11-draw paired judge shows 3/11 CO2 dips under 100 ppm against 0/11 on main.

Next: draft-clinoform-front-has-no-foreset-slope (the shelf front is a one-cell wall), then a two-roll judge of
necking + rise (+ foreset) with the CO2 crash count deciding (draft-necking-margins-judge-co2-dips). Scratch runs were
deleted; re-run with the commands at the end of report.md.

## Round 3 (2026-11-01): status at handoff

main (v0.1.0) merged in (`b52ba525`). The diagnosis is written ([diagnosis-foreset.md](diagnosis-foreset.md)); no code,
no runs yet. Pick: marine slope diffusion of the sediment relief (Mitchell & Huthnance 2008, eq. 1-4). First step:
find and read a source for K and its depth decay. Then L6 screens on seeds 1 and 3 (main / round 2 / round 2 +
diffusion) with margindiag.py, and one full 18x2 paired judge at the end (`tools/hard_bar.py` replaced
docs/review/v1-cut/tally.py on main). Scratch for this round: `scratchpad/l100b/` (a real folder; never `scratchpad/root`).
Cap: 24 threads in total (lane 105's L8 run uses 8 cores).

## Round 3c (lane 100c, 2026-11-01)

Done: K sourced and the addendum written (diagnosis-foreset.md). `slope_k` sea-floor creep is in `surface._creep`
(off by default, goldens unchanged), with tests/test_sea_creep.py. L6 screens on seeds 1 and 3 over five arms are in
report.md, round 3. The paired 18x2 L6 judge of `neck_km=200 rise=1 slope_k=1000` against main ran from a frozen copy
at d43d24a1 through a margindiag variant of paired.sh (scratch `l100c/paired_m.sh`). Two roots (`judge_base/`,
`judge_on/`, arm `m` each, so `tools/hard_bar.py` reads them), copied into one root for pjudge.py.

Result (report.md, round 3): the margin numbers move most of the way to Earth on all 36 draws, with no hard failures.
But soft pass is 26/36 against 29/36, late dT is -2.2 C and land -2.9 points (both moved). So `slope_k` stays off.
Next: judge `slope_k=1000` alone and trace the land loss (draft-sea-creep-alone-judge). Scratch runs are deleted.
To redo them: `paired_margin.sh CODE OUT m 0.0005 0.001`, with `EXTRA="slope_k=1000"` for the on arm, one OUT root per
arm (hard_bar.py reads arm `m`). Then copy both into one root as base_/on_ for pjudge.py.

## Round 3d (lane 100d, 2026-11-01): diagnosis only (owner: proposals, no fixes, no judge)

[diagnosis-land.md](diagnosis-land.md), with [tracediag.py](tracediag.py) as the harness. Land loss: the creep drowns
continental crust (it strips the margins' cover, and rises born continental at 20 km count in the area thermostat).
It is not sea level. Cooling: the arc CO2 source follows the volume thermostat, which the creep drives up during the
spin-up while the source reference is learnt and down later. Early shelf collapse: the start-up continents' first
assembly removes highstand-flooded plains (36/36 draws). A judge of slope_k=300 alone was stopped at 29/36 paired
draws (land -1.6 moved; dT -0.9 and CO2 within the noise). No code changed. Next: decide
draft-arc-co2-follows-volume-thermostat and draft-sea-level-ignores-ocean-floor-sediment before any creep
defaults-on. Scratch runs deleted.

## Round 5 (lane 100e, 2026-11-01): fixes and judges

Done:
- **Sea level counts the ocean floor's sediment** (`earth.floor_sediment_water`, `sim.sea_sed` / `sed_water_ref`,
  diag `sea_sed`). The water the cover keeps out of oceanic cells is counted against the start, as `continent_water`
  counts the continents. Test: `tests/test_sea_level.py::test_sediment_moved_off_a_shelf_onto_the_ocean_floor_keeps_the_sea`.
  The goldens are updated. Judge 1 (72 paired draws) passes, see [deep-dive.md](deep-dive.md). It's a main change.
- **Candidate A (arc CO2 from the slab) is already the code** (PW-741). [note-arc-co2.md](note-arc-co2.md) has the
  trace. No change.
- **Candidate C** (`pile_area`, drowned sediment piles kept out of the area thermostat) was screened, didn't help, and
  was removed.
- **Deep dive** ([deep-dive.md](deep-dive.md)), per the owner's 11-01 widening. Area thermostat off: area holds near
  40%, but its judge failed (1 frozen over, pass 23 vs 27), so it stays on. The volume thermostat is load-bearing. The
  sediment-birth churn with the creep is the biggest late flux. The screen-only params (`area_gain`, `volume_gain`)
  were removed after their screens.
- Judge 2 (creep on top of the fix) fails: 2 frozen over, late dT -2.6 C, land -3.0. The creep stays off.
- tracediag.py now also logs the source's parts (ridge / arc / plume) and the slab (trench edges, convergence).
Next: draft-sediment-piles-born-continental (screen A on seeds 1 and 3 with the creep), then judge the creep again.
Scratch runs are deleted.

## Lane 112 (2026-11-01): PW-1292 option A

Done: sediment piles are born continental only where they touch their own plate's continent
(`crust.touches_own_continent` in `crust.birth_and_cratons`), with
`tests/test_churn.py::test_sediment_piles_are_born_continental_only_against_their_continent`. tracediag.py logs births
by kind and shreds of pile rock (`births`). [pw1292-note.md](pw1292-note.md) has the diagnosis, screens and the
36-draw paired judge (passes: 0 hard failures, 33/36 against 27/36, nothing moved). Isolated piles were only 2-12% of
pile births, so A barely changes the creep's churn. A screen of "3 continental neighbours" (A3) didn't either and ran
colder. The churn looks like a flicker at the shared 20 km birth and shred bound
(draft-margin-cells-flicker-at-the-20-km-bound). The creep-on-A judge wasn't run. Scratch runs are deleted.

## Lane 115 (2026-11-02): PW-1295, the flicker at the 20 km bound

Done: tracediag.py tags births, welds and shreds on the plate grid (`flick`). The flicker is confirmed (creep on:
~1150 shreds per 400 Myr within 10 Myr of a birth, at 19.3 km; ~900 re-births within 10 Myr of a shred; main
140-160 and 60-65). Screened S15 (shred only below 15 km), R25 (re-birth of a shred only at 25 km), both: S15 cures it
and needs no state. `crust.SHRED_KM = 15` is on, with
`tests/test_churn.py::test_a_margin_cell_thinned_just_below_the_birth_bound_is_not_shredded`; goldens updated.
Judge (36 draws, creep off): 0 hard failures, 32/36 against 33/36, climate unmoved, land -1.25 moved (the area
thermostat counts the kept thin margin). [pw1295-note.md](pw1295-note.md). Drafts:
draft-area-thermostat-counts-drowned-thin-margin, draft-sea-creep-still-cools-with-the-flicker-cured. Creep-on judge
not run (creep + S15 screens 3 C colder than S15). Scratch runs deleted.
