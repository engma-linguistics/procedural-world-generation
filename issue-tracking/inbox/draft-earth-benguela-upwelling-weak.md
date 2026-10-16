---
title: "Earth: Benguela upwelling missing at the Cape (summer sea ~23 C off Cape Town; observed ~15-18)"
type: task
status: todo
parent: null
subsystem: ocean
effort: s
impact: low
found_by: coastal-life
blocked_by: []
relates: []
refs: [planet/climate.py, tools/coastal_check.py]
---

## Description
On the L6 Earth world the sea cells off Cape Town and the Cape west coast (32-35 S, 16-19 E) have a warmest-month SST of ~23 C and `upwelling` (climate.upwelling_cooling, now a world layer) of 0-0.6 C; the Benguela upwelling keeps that coast at ~15-18 C in summer (13-15 C at Cape Columbine). California (1-3 C of model upwelling) and Peru do get theirs. So the Cape gets no kelp in coastal life (PW-188; observed: the Cape's Ecklonia kelp forests), and its climate is too warm and wet. Probably the Cape's offshore Ekman component of the model's south-easterly is weak, or the cell sits where `lat_ok` and the coast's orientation meet badly; worth a look at the wind and `away` vectors there.
- [ ] Cape west coast summer SST <= 19 C on the Earth world, other upwelling coasts unchanged
