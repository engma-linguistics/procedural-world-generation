---
id: PW-702
title: Riding is carried to any patch of a riding people at once, even across the sea; tie it to boats and add mounts for the big and the winged
type: task
status: todo
parent: PW-688
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: horses-senses
blocked_by: []
relates: [PW-688, PW-691, PW-695]
refs: [planet/lineages/horses.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Horses part 1 (planet/lineages/horses.py) spreads riding as a front over peopled land, and `Horses._carry` (every 0.5 kyr) gives riding to any patch of a people that already rides over >= 30% of its land (propensity >= 0.3), so patches settled over the sea ride at once. On 1df1c3 that took riding to 109 Mkm2 of the 159 Mkm2 land (all four continents) within ~1.5 kyr of the taming's arrival. Without `_carry` the front stopped at the sea (35 Mkm2).
Follow-ups:
- A horse crossing the sea needs boats big enough (the boat ladder, PW-688 part 2): carry only for lines whose sea share is >= ~0.2 and only after the 'planked ships' step, or by a probability per crossing.
- Fantasy mounts (PW-695 mode): propensity is 0 for fliers, swimmers, cave dwellers and sparse giants; in fantasy mode other peoples could ride other beasts (the same mechanism with a different animal).
- Taming more than once exists (AGAIN_RATE 0.06 /kyr per landmass with herders on wild range) but with `_carry` it almost never fires on 1df1c3 because riding arrives first; check on worlds with a separate steppe continent.

## Updates
- 2026-10-23: Created from inbox draft draft-riding-carried-instantly-across-seas.md (found by horses-senses).
