---
id: PW-172
title: One-frame 11-18 km peaks are thick sediment-filled hotspot cells on ISO_VOLCANO isostasy
type: task
status: done
parent: null
milestone: null
subsystem: tectonics
effort: s
impact: med
found_by: tectchurn
blocked_by: []
relates: [PW-048, PW-108]
refs: [planet/tectonics/isostasy.py, planet/tectonics/crust.py, "run:a01868@588Myr cell 1522", "run:a01868@968Myr cell 87076", docs/review/health/2026-10-15/report.md, "run:550a5a@148Myr(5.73,162.02)", "run:550a5a@640Myr(-0.89,117.67)", "run:a1d3b9@944Myr(-41.03,-9.32)", "run:9068cb@512Myr(2.65,-124.10)"]
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
- 2026-10-15: Status todo -> done. Fixed in a06369c (merged 4ce7706): the 10.6 km one-frame peaks were 80 km belt cells next to an opening edge, stretched as rifting every step while stacking rebuilt them; stacked crust is no longer stretched. a1d3b9 900-950 Myr peaks 10.0 -> 8.6 km; health --quick highest peak 9.3 -> 8.4 km.
- 2026-10-15: Health run 6114bd deleted as a bit-identical duplicate of a1d3b9 (same seed/level/code); use a1d3b9 for the 944/964/968 Myr spikes.
- 2026-10-15: Merged inbox draft draft-health-pw172-spikes.md ("PW-172 update: one-frame 9.7-10.6 km single-cell spikes on 80 km crust in all 3 L7 seeds (health sweep)", found by health-sweep).
  Update for PW-172. PW-246 health sweep (2026-10-15, main 6926583, 1 Gyr, keyframes every 4 Myr):
  keyframes with a peak above 9.5 km: L7 seed 21 (run 550a5a) 4, seed 3199 (6114bd) 3, seed 11
  (9068cb) 3; L6 seeds 21, 3199 and 2 one each (the other 5 L6 seeds none). Most are single cells
  standing far above their neighbours for one keyframe, all continental with crust at 75-80 km:
  | run | Myr | at | peak | neighbours (median) | frame before / after |
  |---|---|---|---|---|---|
  | 550a5a (L7 s21) | 148 | (5.73, 162.02) | 10534 | 2269 | 5864 / 2976 |
  | 550a5a | 640 | (-0.89, 117.67) | 10350 | 995 | 5646 / 66 |
  | 550a5a | 800 | (-43.47, 41.80) | 10142 | 911 | 1549 / 892 |
  | 6114bd (L7 s3199) | 944 | (-41.03, -9.32) | 10616 | 2208 | -332 / 4133 |
  | 9068cb (L7 s11) | 436 | (4.45, 115.21) | 9677 | 308 | -5579 / 198 |
  | 9068cb | 512 | (2.65, -124.10) | 9815 | -87 | 22 / 111 |
  | 9068cb | 640 | (63.16, -28.06) | 9947 | 692 | 6844 / 980 |
  | ce9950 (L6 s2, deleted) | 668 | (8.92, -142.86) | 10186 | 589 | 1215 / 1403 |
  The rest (6114bd 964/968, 550a5a 880, L6 s21 @792, L6 s3199 @180) are 9.6-9.7 km tops of 5-7 km
  plateaus: plausible. 6114bd reproduces the coordinator's a1d3b9 exactly (944/964/968 Myr, 10.6 km).
  The spikes jump from near sea level (or below) to ~10 km and back within 8 Myr, as PW-172 describes
  (ISO_VOLCANO isostasy on thick sediment-filled cells); the crust at the 80 km mark in every case
  suggests a thickness cap is involved too. L6 runs are deleted; seed 2 reproduces (deterministic).
  - [ ] no single-cell one-frame peaks above 9.5 km in `tools/health.py` (peak_frames 0 at L7)
- 2026-10-15: Tect2 (merged): options A+B; max 9.24 km to 700 Myr on L7 seed 3199. Close after one full 1 Gyr L7 run stays below ~9.5 km.
- 2026-10-14: Absorbs PW-048 (single-sample 12-13 km spikes; add the envelope test it asked for).
- 2026-10-14: Created from inbox draft draft-hotspot-pile-spikes.md (found by tectchurn).
