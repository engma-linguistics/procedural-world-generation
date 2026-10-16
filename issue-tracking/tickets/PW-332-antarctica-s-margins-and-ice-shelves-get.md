---
id: PW-332
title: "Antarctica's margins and ice shelves get 20-100 mm/yr of snow (obs ~100-500): the run's ice rule can't hold them"
type: task
status: blocked
parent: null
subsystem: climate
effort: m
impact: high
found_by: pw313
blocked_by: []
relates: [PW-313, PW-013, PW-308, PW-112]
refs: [planet/climate.py, tools/ice_probe.py, docs/review/audit/pw313-polar-summers.md]
created: 2026-10-16
updated: 2026-10-16
---

## Description
The PW-313 probe (`tools/ice_probe.py`, Earth L6 at dT 0 from the real ice) decays Antarctica to ~0.1% of the
surface. Making the Antarctic ice surface's summer match NCEP within 1-2 C at every bed height (a diagnostic:
stronger damping, full air-mass cover) still leaves it decaying to 1.7%. With the carried-sheet-air option
(draft-ice-sheet-air-carried, A) it decays to 1.2%.

The cells it loses are the Ross and Ronne shelves and WAIS margins (bed clamped at +1 m in the Earth source).
They sit at the observed summer temperature (-4.0 vs -4.7 C) and get 20-100 mm/yr of snow. Observed accumulation
there is ~100-250 mm on the shelves and 200-600 on WAIS and the coasts. earth_check: Antarctica 70-80S land
rain 200 mm against GPCP's 412. With Antarctic snowfall x2.5 (diagnostic) and option A, the probe holds at ~2.6%
(-50 m) over 8 updates. The snowfall alone (x2.5 with today's temperatures) doesn't hold (1.7%), and polar
snowfall x3 alone grows the ice to 5.9%.

For PW-013 (rain transport): the vapour reaching Antarctica's coasts from the Southern Ocean storm track (60-65S).
Since PW-308 the air takes up water through leads (`TUNE['leads']` 0.1), but the coast still gets a quarter to a
half of the observed snow. The frozen-sea summer air fix (draft-frozen-sea-summer-air) makes it ~15% drier still.
- [ ] Antarctica 70-80S land precipitation within ~30% of GPCP's 412 mm; ice-shelf/WAIS cells ≥ 100 mm
- [ ] PW-313 probe at dT 0 holds ~3% over 8 updates (with the temperature fixes) and grows toward ~-120 m at dT -6

## Updates
- 2026-10-16: Status in-progress -> blocked. Partly fixed in baabbba (vapour no longer rides the polar cell's equatorward surface drift; rain lift uses the ice surface): Antarctic land 70-80S 77 -> 158 mm (GPCP 210), Greenland 207 -> 304 (375). Margins still ~half of GPCP: storm-track moisture over 55-65S seas at 0.4 of GPCP, owned by PW-015 (merged draft there).
- 2026-10-16: Status todo -> in-progress. Polar bundle agent started.
- 2026-10-16: Created from inbox draft draft-antarctic-margin-snowfall.md (found by pw313).
