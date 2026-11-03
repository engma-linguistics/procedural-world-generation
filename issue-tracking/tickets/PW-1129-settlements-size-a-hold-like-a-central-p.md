---
id: PW-1129
title: "Settlements: size a hold like a central place (a share of its hinterland), not by smooth saturation"
type: task
status: todo
parent: PW-1011
milestone: null
subsystem: culture
effort: s
impact: low
found_by: fun-lane-66
blocked_by: []
relates: [PW-1117]
refs: [planet/lineages/settlements.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
Fun lane 66 stopped the holds piling at 9,999 (PW-1117): a mining people's halls are HOLD_SHARE of its heads in the cell, now levelling off smoothly toward HOLD_MAX (80,000), and may be a city once the people has fortifications (or cities). That is a judgement fix, not a hierarchy: a chief city gathers SHARE[3] of two rings of hinterland. A hold could take the same hierarchy over its own people's cells in the hills. About 10 to 15 holds per run still sit within 2% of the town cap of 5,000 in the era before their people had fortifications or cities (peak, not now).
- [ ] holds sized by a hinterland share
- [ ] the HOLD_MAX and MINORITY_MAX constants dropped if the hierarchy replaces them

## Updates
- 2026-10-30: Created from inbox draft draft-hold-size-by-hierarchy.md (found by fun-lane-66).
