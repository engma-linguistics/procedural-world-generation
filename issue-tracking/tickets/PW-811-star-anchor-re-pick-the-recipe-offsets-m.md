---
id: PW-811
title: "Star anchor: re-pick the recipe offsets measured on the old star (hothouse 5 -> 3, cold -6 kept, water world +8 proposed)"
type: task
status: todo
parent: null
milestone: v3
subsystem: climate
effort: s
impact: med
found_by: star-anchor-audit
blocked_by: []
relates: [PW-791, PW-799, PW-798, PW-790]
refs: [planet/make.py, README.md, docs/coordination.md, docs/review/base-climate/star-anchor-audit/]
created: 2026-10-24
updated: 2026-10-26
---

## Description
Audit items 8 and 9 (docs/review/base-climate/star-anchor-audit/README.md).

- **Hothouse** `climate_offset` 3 (planet/make.py:65; README.md:92; docs/coordination.md:60). 1fa0aeb changed it
  from 5 because the old star's late warming pushed it over the hellhole line (+12.9 / +10.9 C median). That is a
  direct old-star compensation. Re-pick it on the anchored star, starting from the star-off +5's character (+9.6
  median, under the line).
- **Cold** -6 (make.py:63): kept on the old star, 3 C less cold than star-off. Check that it still reads as a cold
  world with big sheets and isn't a frozen-solid icebox.
- **Water world** +8 (PW-799): this is two compensations stacked. One is PW-798's frozen-reference weathering
  surplus (sink/ref 1.2-1.3 with the star off, 1.5-2.7 with it on). The other is the old star. Don't land +8. Do
  PW-798 A first, then the anchor, and re-measure from offset 0.
- [ ] hothouse and cold re-checked at L6 (1 Gyr, 2 draws each), offsets updated in make.py, README and coordination.md
- [ ] water-world offset re-measured after PW-798 and the anchor

## Updates
- 2026-10-26: Parent PW-244 -> none. (PW-900 backlog reorg). Milestone v2 -> v3: other planet kind. (PW-900 backlog reorg).
- 2026-10-24: Created from inbox draft draft-recipe-offsets-after-anchor.md (found by star-anchor-audit).
