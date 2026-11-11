---
title: Judge the shred gap (shred_km=15 with thin-margin dynamics) at L6 before flipping it on, with and without the thin-margin area fix
type: task
status: todo
parent: null
milestone: null
subsystem: tectonics
effort: m
impact: med
found_by: lane-302
blocked_by: []
relates: [PW-1295, PW-1314, PW-1318, PW-1315, PW-1316]
refs: [planet/tectonics/params.py::Params.shred_km, planet/tectonics/mantle.py::keel, planet/tectonics/crust.py::coherence, planet/tectonics/crust.py::thermostats, docs/review/tectonics/margin/pw1295-note.md, docs/review/tectonics/margin/flickdiag.py, docs/review/tectonics/margin/paired_margin.sh, tools/hard_bar.py]
---

## Description
In plain words: the continents' outermost cells flicker between continent and ocean floor because one 20 km bound
decides both ways. Lane 302 added a switch, `shred_km` (default 0 = off): with 15, a thin margin cell is turned into
ocean floor only below 15 km, and the plate model's keel drag, traction and mantle insulation see only crust of
20 km and up as continent (so the kept thin margins don't leave the young planet with fewer plates, PW-1318). On
test_envelopes' world over 20 seeds (L5, 400 Myr, pw1295-note.md section 6) it cures the flicker on every seed
(quick shreds 105 -> 1 median; with the sea-floor creep 289 -> 15), no world leaves the envelope band (0/20 on and
off), and the plate count is no longer lower (9/20). It is off because it also moves things: continental area +2.3
points (18/20), crust 1.9 km thinner (19/20), land -0.8 points, end T +1.9 C median (14/20, not significant at 20
seeds). The thinner crust and lower land are PW-1314's area-thermostat swing (the thermostat counts the kept thin
margin as continental area).

If never done: the flicker stays on main (small: ~13% of shreds come back within 10 Myr) and the sea-floor creep
(PW-1315) can't come back without its ~6x flicker at L6.

- [ ] paired L6 judge (paired_margin.sh, 18 draws x 2 rolls, as pw1295-note.md section 3) of `shred_km=15` against main
- [ ] the same with PW-1314 A on top (area thermostat counting only crust >= BECOMES_CONT_KM), to see whether it
  takes the land and thickness swing away; PW-1314 is a decision (A or accept), so bring both arms to it
- [ ] flip the default only if no hard failure and the soft pass level holds
