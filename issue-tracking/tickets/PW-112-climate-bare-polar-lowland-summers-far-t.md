---
id: PW-112
title: "Climate: bare polar lowland summers far too warm (Antarctica's ground at +15 C)"
type: task
status: todo
parent: null
milestone: null
subsystem: climate
effort: m
impact: med
found_by: climfix
blocked_by: []
relates: [PW-102]
refs: [planet/climate.py, planet/tectonics/earth.py]
created: 2026-10-14
updated: 2026-10-16
---

## Description
With Earth's real ice (earth_data L6), climate.compute's bare-ground warmest month (its new 'ground'
output: the ice surface's temperature before the ice's own height and cooling) is +9.8 / +14.7 / +16.1 C
(p10/50/90) over Antarctica, whose bedrock sits near sea level. An ice-free polar lowland at 70-90 deg
should have summers around 0 to +5 C (Ellesmere, Peary Land). The model gets the ice sheets right only
through the 10 C ice_cooling and the 0.5 melt hold, i.e. by compensating a warm polar base.
Consequence: any ice rule judged on the ground (with less than full feedback) cannot keep Antarctica on
Earth geography. Applying the main-run ice rule repeatedly to Earth from the real ice: old rule 100 ->
36% of Antarctica after 4 climate steps; climfix's (feedback 0.75) 39%; with feedback 0.5, 2%. Generated
planets keep their polar sheets (L6 seed 21: 63% of polar land iced) because their ice sits higher.
Likely cause: temperature() (polar -10 C at sea level) plus seasons() summer swing over big polar land,
with evap_cool's desert term (+ for dry ground) adding more. Probe: earth_ice.py-style loop
(climate.compute on data/earth L6 with ice, then earth.ice_sheets, 4 iterations).
- [ ] Antarctica (and Greenland) hold their ice under the main-run rule on Earth geography

## Updates
- 2026-10-16: Status in-progress -> todo. Partly addressed by the polar bundle (frozen-sea summer air, carried sheet air). Remaining: Antarctic plateau ~10 C warm (PW-039).
- 2026-10-16: pw313: Earth's real ice-free polar lowlands were +1..+4 C too warm in summer from the frozen sea's summer air (draft-frozen-sea-summer-air; fixed to within 1 C, not merged: it dries the poles). Antarctica's bed (+13 C) has no Earth analogue; the observable error is the ice surface's air (draft-ice-sheet-air-carried). docs/review/audit/pw313-polar-summers.md.
- 2026-10-15: Status todo -> in-progress. Run-lane agent started (polar summers / Antarctica).
- 2026-10-14: Created from inbox draft draft-polar-bare-ground-too-warm.md (found by climfix).
