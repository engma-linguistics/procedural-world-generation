---
id: PW-1326
title: "Summer split heats dry sunny land into a fixed 1500 m layer with no long-wave loss: subtropics +2.1 C, 8% of land >= 35 C (obs 2%)"
type: task
status: done
parent: null
milestone: v2
subsystem: climate
effort: s
impact: high
found_by: lane121
blocked_by: []
relates: [PW-1279, PW-015]
refs: [docs/review/base-climate/summer-heat/diagnosis.md, docs/review/base-climate/summer-heat/candidates.patch, docs/review/base-climate/summer-heat/diag.py, docs/review/base-climate/summer-heat/summ.py, docs/review/base-climate/summer-heat/screen.sh, docs/review/base-climate/summer-heat/ec.sh, docs/review/base-climate/summer-heat/seeds.sh, docs/review/base-climate/summer-heat/simtune.py, docs/review/base-climate/summer-heat/runs_measure.py, docs/review/base-climate/rain-inland/withtune.py, "planet/climate.py::_summer_split", "docs/review/base-climate/summer-heat/candidates.patch", "planet/climate.py::compute", "planet/climate.py::open_water_evap", tools/earth_check.py, data/earth/L7.npz, "Ryder et al. 2015 (ACPD 15:199 / ACP 15:8479)", "Allen et al. 1998 (FAO-56, eq. 39)"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: on Earth, the model's subtropical summers are too hot (+2.1 C at 20-40 deg). 8% of land gets a
warmest month of 35 C or more, against the observed 2%. The cause is one step: how much the summer air warms
over sunny, dry ground. It puts all of the ground's spare heat into a fixed 1500 m of air for a day. Real desert air
mixes 4-6 km deep, and clear skies also lose more heat as long-wave.

Lane 121 screened two sourced fixes (diagnosis.md section 4, both in candidates.patch as TUNE knobs, off):
- C, `split_bl_max` 4: the layer deepens as sqrt(H / H_ref) up to 6 km. Ryder et al. 2015 (Fennec): the Saharan
  layer commonly reaches 5-6 km, with weak entrainment.
- B, `split_lw` 1: FAO-56 eq. 39's long-wave loss changes with the sunshine.

Earth L7, B+C:
- 20-40 deg +2.1 -> +0.4 C; land >= 35 C 7.9% -> 0.7% (C alone 1.5%).
- Sahara +4.7 -> +0.7.
- Köppen B 25.0 -> 24.6 (the wrong way, Kottek 30.1). Arabia -2.6, India -1.5, US Southwest -5.3.
- The humid coasts barely move: they need their rain (PW-015).

Options:
- A. Merge C alone (closest on the >= 35 C tail), after the 36-world judge.
- B. Merge B+C (the larger subtropical fix, but it overshoots the tail and costs more in Arabia, India and the US SW).
- C. Fold it into a round with the overcast-tropics split fix (draft-summer-split-overcast-tropics). That fix moves
  the split's reference onto CRU's sunshine scale, which changes what H_ref is.

Lean: C. Both drafts change the same reference, so re-anchor the reference once and screen B+C on it. Merging C
alone now would be a partial fix (memory: no temporary fixes).

- [ ] judge (36 worlds) on the chosen arm, after the owner's go

## Updates
- 2026-11-02: Status needs-decision -> done. Lane 126 (merged fdc631a4) folded B+C in with the cloud gate and sunshine re-anchor, as planned on the desk's D41 card: Earth warmest month at 20-40 deg +2.1 -> +0.4 C; land >=35 C 7.9% -> 0.9%; Sahara +4.7 -> +0.8. Costs: US SW -5.2 C, Arabia -2.5, India -1.2. L6 judge 32/36 vs 32/36.
- 2026-11-02: Created from inbox draft draft-summer-split-deep-dry-boundary-layer.md (found by lane121).
