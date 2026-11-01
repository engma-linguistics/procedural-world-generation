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
