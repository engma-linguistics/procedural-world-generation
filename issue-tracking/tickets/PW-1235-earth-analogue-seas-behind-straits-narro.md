---
id: PW-1235
title: "Earth analogue: seas behind straits narrower than a cell (Puget Sound, Maracaibo, Ob gulf, Amazon mouth) become land pockets"
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: s
impact: low
found_by: lane98
blocked_by: []
relates: [PW-1229, PW-386]
refs: [planet/geo.py, tools/earth_data.py, docs/review/v1-cut/inland-pits.md]
created: 2026-10-31
updated: 2026-10-31
---

## Description
In plain words: the new sea rule (PW-1229) counts water as sea only if the grid can see it reach the ocean, or
if it is big (≥ 0.3 Mkm²) or one low cell away. On real Earth at L7, a few genuine seas join the ocean through
channels narrower than a cell and are now land: Puget Sound and the Salish Sea (5 cells, −104 m), Lake Maracaibo
(4), the St Lawrence estuary (2), Cook Inlet (1), the Ob gulf (11), the Amazon's mouth cell (1, −1 m) and a few
Arctic coastal cells. On generated worlds this is the intended rule. On Earth it is a small regridding cost:
the earth_check numbers barely move (Köppen group 71 → 70%). The one large effect was a correction (PW-386:
the Amazon and Ob had been ending in those one-cell "seas" in the moisture budget).

What I'd try if it matters: earth_data could mark cells that HydroSHEDS or ETOPO shows as joined to the
ocean at full resolution, and pass that to `is_land` as a seed of known sea. Only the Earth analogue has
that information, so generated worlds would be unaffected.
- [ ] decide whether the Earth analogue needs known-sea seeds (owner's earth-as-anchor rule says probably not)

## Updates
- 2026-10-31: Created from inbox draft draft-subcell-straits-earth.md (found by lane98).
