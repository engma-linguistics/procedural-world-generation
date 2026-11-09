---
id: PW-1576
title: The rainforest keeps 4.3 leaf layers against 4.7-5.1 measured; a sunlit/shaded (two-leaf) light model would pay its deep leaves
type: task
status: todo
parent: null
milestone: later
subsystem: surface
effort: m
impact: low
found_by: scout232
blocked_by: []
relates: [PW-1518, PW-1517]
refs: ["planet/vegetation.py::_year", "planet/vegetation.py::DIFFUSE", "planet/climate.py::diffuse_fraction", "planet/climate.py::months", docs/review/climate/diffuse/diagnosis.md, docs/review/climate/diffuse/screens.md, docs/review/climate/diffuse/probe.py, "Yan et al. 2017 JGR Biogeosci 122:3014 eq. 5-11 (White Rose eprint 124617)", "Mercado et al. 2009 Nature 458:1014 (NORA 6771)", "world 506694 (Earth L6)"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: with the diffuse-light gain and the measured leaf upkeep (PW-1518, scout 232), the rainforest tree's
growth and breathing land in the measured ranges, but it keeps fewer leaf layers than before: LAI 4.28 on Earth's
observed climate (main before PW-1518: 4.58; measured 4.7 at Manaus, 5.1 +- 0.5 at Tapajos). The gain is big-leaf: it
pays every leaf alike, so it only partly undoes the dearer leaves. In a real canopy the extra carbon under diffuse light
goes to the shaded inner leaves, which is what makes deep leaves worth keeping.

What misleads if never done: any read-out of rainforest leaf area (and what depends on it: canopy interception,
browse, shade) is ~10-15% under the measured canopy, and a cloudier world's forests are not credited with deeper
canopies.

Also seen: the model's Df over the Amazon stand runs only 0.52-0.61 by month (K67 measured 0.55-0.9). The PAR's
clearness (0.25 + 0.5 x sunshine) never gets dark enough for 0.9, and two half-year clouds flatten the seasons. A
two-leaf model would feel this more than the big-leaf gain does.

- [ ] Yan's two-leaf split in `_year` (sunlit LAI 2 cos(theta)(1 - exp(-0.5 Omega L / cos(theta))), a monthly noon
      zenith from latitude and tilt), normalised so TrBE's canopy LUE at Df 0.55 and LAI ~4.6 is today's eps
- [ ] probe.py screens: LAI toward 4.7-5.1 with leaf upkeep, NPP, NPP/GPP and the wet box still in range

## Updates
- 2026-11-09: Created from inbox draft draft-two-leaf-rainforest-lai.md (found by scout232).
