---
id: PW-628
title: "Soils vs SoilGrids stays at 45% after the salt and blown-sand fixes: what is left is classification convention"
type: task
status: done
parent: PW-184
milestone: v2
subsystem: surface
effort: m
impact: low
found_by: soilveg2
blocked_by: []
relates: [PW-330, PW-185]
refs: [planet/soils.py, tools/soil_check.py, docs/review/soilveg/earth_soils_pw330.png]
created: 2026-10-23
updated: 2026-10-29
---

## Description
PW-330 (soilveg lane 2): salt soils now only in the cell holding the salt lake or pan (5.0% of land -> 1.0%, SoilGrids 1.1%); blown sand only on flat ground (< 3 m/km: sand seas fill basins and plains, rolling ground keeps rock and pavement). Group shares moved toward Earth (desert 21.6 -> 17.9% vs 14.6, young 12.2 -> 14.6% vs 21.9, thin 6.5 -> 6.9% vs 8.2) but the 10-group agreement stayed at 45.0%: each fix gains about as many cells as it loses.
What remains has no model signal at L6 (observed climate; diagnostics in docs/review/soilveg/handoff-2.md):
- SoilGrids Cambisols under the model's frozen soils (3.3 Mkm2, mountain and Siberian permafrost): slope, age and depth don't separate them from SoilGrids' Cryosols;
- caliche (10.2% of land vs Calcisols 3.0%): hits 55% at mi 0.1-0.2, 36% at 0.3-0.35; the misses are Luvisols, Cambisols, Leptosols and Regosols spread over all ages and slopes. WRB keys a dry soil with a clay-illuviation (argic) horizon over its lime as a Luvisol, a history the model doesn't track;
- Cambisol vs Luvisol in temperate forest: W medians 3.4 vs 4.2, broad overlap.
Options: accept ~45% as plausible (group shares now within ~1.5x of Earth's except young and caliche), or add an argic-horizon age (clay illuviation needs ~1e4-1e5 yr of seasonal wetting) so dry-margin Luvisols and Calcisols separate. Owner's call whether that is worth it.

## Updates
- 2026-10-29: Removed docs/review/soilveg/earth_soils_pw330.png, docs/review/soilveg/handoff-2.md in cleanup; last present at 9861e2df.
- 2026-10-23: Status needs-decision -> done. Coordinator (owner delegates geophysics; Earth is a plausibility anchor): 45% group agreement with the documented reasons is plausible enough; no further soil tuning toward SoilGrids. Group shares moved toward Earth's in lane 2.
- 2026-10-23: Created from inbox draft draft-soil-agreement-remaining.md (found by soilveg2).
