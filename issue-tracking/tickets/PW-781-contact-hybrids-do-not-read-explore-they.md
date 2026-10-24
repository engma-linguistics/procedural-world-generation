---
id: PW-781
title: Contact hybrids do not read explore (they spread nowhere); decide whether half-orcs/half-elves should wander
type: task
status: wontdo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun18
blocked_by: []
relates: [PW-758, PW-730]
refs: [planet/lineages/history.py, planet/lineages/samples/dnd.toml, planet/lineages/compose.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-758 leftover. A contact hybrid (`origin = "hybrid"`, `_hybrid` in history.py) is `min(parent A, parent B)` where the parents meet,
plus a fading linger; it never goes through the spread step, so `explore` (and `sea_share`, speed) have no effect on it. `insularity`
is real: `compose.cohabitation` reads every line's insularity. fun18 removed the cosmetic `explore` values from dnd's half_elf and
half_orc and kept `insularity = 0.3` (with a comment saying so). Options:
- A: leave it (hybrids are where parents meet; wandering would break the "occurs where the parents meet" rule).
- B: let a hybrid's presence leak a ring or two beyond the contact zone in proportion to `explore` (a small `spread` of `O`, within its
  own habitat K), so wanderers show up in neighbouring country. Cheap, but it is a new rule for what a contact hybrid is.
Lean A: the owner's canon says half-elves occur where the parents meet and form no community.

## Updates
- 2026-10-24: Status needs-decision -> wontdo. Coordinator: no wandering ring. Owner's rule (2026-10-24): half-folk stay with a parent group or strike out on their own; staying = contact hybrid, striking out = contact=false (a people of its own) in the preset.
- 2026-10-24: Created from inbox draft draft-hybrid-explore-unread.md (found by fun18).
