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
