---
id: PW-172
title: One-frame 11-18 km peaks are thick sediment-filled hotspot cells on ISO_VOLCANO isostasy
type: task
status: todo
parent: null
subsystem: tectonics
effort: s
impact: med
found_by: tectchurn
blocked_by: []
relates: [PW-048, PW-108]
refs: [planet/tectonics/isostasy.py, planet/tectonics/crust.py, "run:a01868@588Myr cell 1522", "run:a01868@968Myr cell 87076"]
created: 2026-10-14
updated: 2026-10-15
---

## Description
Diagnosis for PW-048 (single cells at 12+ km for one frame). L7 seed 21 run
a01868 (code 027bbe6) has two: t=588 cell 1522 at 11521 m with 45 km crust,
t=968 cell 87076 at 18154 m with 66 km crust (neighbours 0.5-2.6 km). Replayed
deterministically from the 500 Myr checkpoint, cell 1522:
- 582: continental, 26.9 km, cover 9.5 km;
- 584: flips to oceanic (a PW-108 sampling flip), 18 km, rock set to HOTSPOT
  by `crust.stretch` (`~cont & plume*dt > 0.2`), cover 7.7 km;
- 588: oceanic HOTSPOT, 45 km thick, cover 18 km (capped by burial), elevation
  = ocean depth + ISO_VOLCANO (350 m/km) x 38 km + 4.2 km sediment lift = 11.5 km.
So the amplifier is the volcano isostasy (350 m per km, meant for a narrow
pile held up by flexure) applied to tens of km of mostly sediment, and
`birth_and_cratons` never makes it continental: its `sedimented` test
(cover > half the excess thickness) fails because cover is capped at 18 km.
Options: (A) cap the thickness ISO_VOLCANO applies to (the flexural load a
plate can hold, ~Mauna Kea), the rest at ISO_SEA/ISO_LAND; (B) count buried
sediment (basement made from cover) in the `sedimented` test so the pile is
born continental; (C) don't mark HOTSPOT on cells that were continental a step
ago. Lean A+B. Coherence (PW-108 fix) removes some of the flips that start it.
- [ ] no frame of an L7 1 Gyr run above ~9.5 km (envelope test)

## Updates
- 2026-10-15: Tect2 (merged): options A+B; max 9.24 km to 700 Myr on L7 seed 3199. Close after one full 1 Gyr L7 run stays below ~9.5 km.
- 2026-10-14: Absorbs PW-048 (single-sample 12-13 km spikes; add the envelope test it asked for).
- 2026-10-14: Created from inbox draft draft-hotspot-pile-spikes.md (found by tectchurn).
