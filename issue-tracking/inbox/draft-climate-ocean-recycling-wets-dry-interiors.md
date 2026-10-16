---
title: "After PW-266 the dry interiors rain on themselves: Earth's Köppen-B land share fell from 29% to 20% (Kottek 30%), exact agreement 39% to 33%"
type: task
status: needs-decision
parent: PW-245
subsystem: climate
effort: m
impact: high
found_by: climate-ocean
blocked_by: []
relates: [PW-266, PW-026, PW-228, PW-290, PW-013]
refs: [planet/climate.py, docs/review/audit/fixes-climate-ocean.md]
---

## Description
PW-266 made the rain kernel give the air back what Budyko's water balance evaporates. Before, it used a flat 0.5 × warm × the local rain. The water books now close (the fresh-water mean is +0.1 cm/yr on Earth, against −3.2 before). But on dry land Budyko evaporates nearly all the rain, and the kernel rains much of that vapour out again where it rose. The dry interiors now recycle their own rain:

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

On generated planets (health --quick, 8 L6 seeds, 500 Myr), the median Köppen-B share fell from 30–45% to 24–31%. The scorecard's seeds 1 and 2 at 1000 Myr fell from 32/37% to 18.5/20.7%.

Some regions got better: Great Plains, W Siberia, SE China, SE USA and the Pampas. The deserts and steppes got wetter.

Before, the kernel's land evaporation was too low (41% vs 60%). That under-recycling hid the fact that the kernel rains out recycled vapour too readily over dry land. In reality, desert evaporation follows rare rain events, and the vapour is mixed up and carried off under the subsiding air. It doesn't fall again where it rose.

Options:
- A: keep it as is. The books close, the generated interiors are wetter (PW-026, PW-290), and Earth is off.
- B: sound, small. Put the recycled vapour into the air that moves on rather than into the local column. For example, add the land's evaporation to `moved` (after the cell's rain) instead of to `m` before it. The water then rains downwind (Earth's continental recycling length is ~500–2000 km). This might be the smallest physical change.
- C: re-tune the kernel's rain-out (bg, belt_dry, rh_c) on Earth to get the B share back. This is a re-tune for a score, so not recommended.
- D: revert PW-266 to the flat share, and keep the freshwater correction.

Lean: B, then re-measure earth_check and health. If B isn't enough, look at whether `belt_dry` should also damp the showers of locally recycled vapour.
