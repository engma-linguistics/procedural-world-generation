---
title: "Tech tree firsts: a tie can credit a contact taker over the inventor"
type: task
status: todo
parent: PW-675
subsystem: timezoom
effort: xs
impact: low
found_by: techtree-views
blocked_by: []
relates: [PW-675]
refs: [planet/lineages/techtree.py, "run 3097e3", docs/review/techtree-views/]
---

## Description
`techtree.build` fills `firsts` by walking `known` in line order and replacing only on a strictly older date
(`v[0] > firsts[tid]["ago_kyr"]`). When an invention and a same-step contact land on the same grid step, whichever line
comes first in `meta.lineages` wins. In run 3097e3 (world 2a7385, D&D peoples), pottery's first is "firbolgs, 18.8 kyr
(contact)" although halflings invented it at the same 18.8 kyr and passed it on; the viewer's Firsts card and every
mockup in docs/review/techtree-views/ show the taker as the first.
Fix: on equal dates prefer `invented` (then `tamed`/kit) over `contact`/`shared`/`inherited`.
- [ ] firsts[tid].how is never contact/shared/inherited when an inventor holds the same date
