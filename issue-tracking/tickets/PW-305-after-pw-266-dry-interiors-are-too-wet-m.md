---
id: PW-305
title: "After PW-266 dry interiors are too wet: more recycled vapour feeds the showers over hot dry land (Earth's Köppen-B share of land 29% -> 20%, Kottek 30%; exact 39% -> 33%)"
type: task
status: wontdo
parent: PW-245
subsystem: climate
effort: m
impact: high
found_by: climate-ocean
blocked_by: []
relates: [PW-266, PW-026, PW-228, PW-290, PW-013]
refs: [planet/climate.py, docs/review/audit/fixes-climate-ocean.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
PW-266 made the rain kernel give the air back what Budyko's water balance evaporates. Before, it used a flat 0.5 × warm × the local rain. The water books now close (the fresh-water mean is +0.1 cm/yr on Earth, against −3.2 before). On dry land, Budyko evaporates 80–95% of the rain, while the old kernel gave back ~40%. So the deserts' air now carries about twice the vapour, and it rains much of it out again.

| earth_check (L6) | main | after PW-266 | observed |
|---|---|---|---|
| Köppen group / exact | 71.8 / 38.9% | 71.2 / 33.0% | |
| B share of land (excl. Antarctica) | 28.9% | 20.3% | 30.1% (Kottek) |
| land P mean / median, mm | 840 / 515 | 1008 / 737 | 791 / 546 (GPCC) |
| Australia interior | 463 | 837 | 291 |
| Gobi/Mongolia | 303 | 582 | 157 |
| Sahara | 205 | 328 | 35 |
| Great Plains | 264 | 640 | 550 |
| W Siberia | 271 | 557 | 503 |
| Pampas group match | 4.9% | 74.4% | |

Some regions got better (Great Plains, W Siberia, SE China, SE USA, Pampas); deserts and steppes got wetter. On generated planets (health --quick, 8 L6 seeds, 500 Myr), the median B share fell from 30–45% to 24–31%.

**Tried and ruled out (2026-10-15): option B, put the recycled vapour into the air that moves on rather than the local column.** Two forms:
- added to the cell's moved air after its rain;
- sent with its outflow to the downwind cells.

Neither changed anything (Earth land P 1008 → 998 / 986 mm, B share 20.3 → 20.5%, Australia interior 837 → 830 / 839). Deserts are many cells wide, so moving the vapour one cell downwind doesn't take it out of the desert. The first form is the local column one step later.

**Where the extra rain comes from (Earth, current code):** the desert rain is mostly showers, not large-scale rain.

| region | P before → now | showers' share of the rain |
|---|---|---|
| Australia interior | 470 → 850 | 0.70 → 0.79 |
| Sahara | 209 → 334 | 0.60 → 0.70 |
| Gobi | 303 → 562 | 0.94 → 0.93 |

The added vapour raises the moist static energy of the hot ground air (`mse_t + LQ·q`) above the air aloft. The kernel has no inversion over dry land apart from `cv_sink` in the subtropical belt. In reality, a deep dry convective layer mixes desert evaporation up and away, and the subsidence inversion caps the showers.

The old flat `et` (0.5 × warm) under-recycled dry land, and that hid how readily the kernel turns any vapour over hot dry land into showers. I found no small change that is a sound process statement. "belt_dry should damp showers of recycled vapour" doesn't work: the kernel has one vapour, not a tagged recycled one. And `cv_sink` already damps showers in the sinking belt.

Options:
- A: keep it as is. The books close; generated interiors are wetter (PW-026, PW-290 helped); Earth's deserts are too wet.
- C: re-tune the kernel's showers (cv_sink, cv_scale) on Earth to get the B share back. This is a score re-tune, so not recommended.
- D: revert PW-266 to the flat share and keep the freshwater correction. This brings back the hidden imbalance.
- E (heavier, sound): give the showers over land a boundary-layer depth. Dry, deeply mixed ground air (large `t_air` − dew point) spreads its vapour through a deeper layer, so the near-ground q that drives `inst` is diluted. Or tag the recycled vapour as a second tracer that mixes aloft. Either needs a careful pass on Earth.

Lean: needs the owner. A for now; E if the deserts matter before PW-013's rain pass.

## Updates
- 2026-10-15: Status needs-decision -> wontdo. Owner (2026-10-15): option A, keep PW-266 as merged; no temporary fixes. The dry-interior over-wetting (Earth Koppen exact 38.9 -> 33.0%, Sahara 328 mm vs 35, Australia 837 vs 291) belongs to PW-013's rain/moisture-transport rework. E1 prototype not merged (write-up docs/review/audit/pw305-prototype.md).
- 2026-10-15: Prototype (branch pw305-e1-mixed-layer, e104331, not merged; write-up docs/review/audit/pw305-prototype.md on the branch): E1, a dry-convective mixed layer (PET-AET heats the air; once deeper than the 2 km vapour scale height, the shower trigger sees 2 km/h of the vapour). Earth Koppen exact 33.0 -> 34.3%, B share 20.3 -> 21.9% (obs 30.1), Sahara 328 -> 294, Australia 837 -> 720 mm; Gobi and Sahel unchanged; books stay closed. A deeper steady-state layer restores the B share (30-33%) but dries SE China/SE USA (too-warm summers there): rejected. Owner to decide: merge E1 (modest, sound), or keep looking.
- 2026-10-15: Coordinator: prototype agent started on a branch (sound route E: boundary-layer dilution or recycled-vapour tracer); owner decides from its report.
- 2026-10-15: Created from inbox draft draft-climate-ocean-recycling-wets-dry-interiors.md (found by climate-ocean).
