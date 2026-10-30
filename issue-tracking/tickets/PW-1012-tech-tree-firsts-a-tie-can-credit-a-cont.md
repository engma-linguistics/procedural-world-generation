---
id: PW-1012
title: "Tech tree firsts: a tie can credit a contact taker over the inventor"
type: task
status: todo
parent: PW-675
milestone: null
subsystem: timezoom
effort: xs
impact: low
found_by: techtree-views
blocked_by: []
relates: [PW-675]
refs: [planet/lineages/techtree.py, "run 3097e3", docs/review/techtree-views/]
created: 2026-10-29
updated: 2026-10-29
---

## Description
`techtree.build` fills `firsts` by walking `known` in line order and replacing only on a strictly older date
(`v[0] > firsts[tid]["ago_kyr"]`). When an invention and a same-step contact land on the same grid step, whichever line
comes first in `meta.lineages` wins. In run 3097e3 (world 2a7385, D&D peoples), pottery's first is "firbolgs, 18.8 kyr
(contact)" although halflings invented it at the same 18.8 kyr and passed it on; the viewer's Firsts card and every
mockup in docs/review/techtree-views/ show the taker as the first.
Fix: on equal dates prefer `invented` (then `tamed`/kit) over `contact`/`shared`/`inherited`.
- [x] firsts[tid].how is never contact/shared/inherited when an inventor holds the same date

## Updates
- 2026-10-29: Fun lane 47: fixed. techtree.firsts_of picks the oldest date and, on a tie, the people that invented it (then tamed or kit) over a contact, shared or inherited taker; tests in tests/test_techtree.py. The stored runs 3097e3, ac4c06 and 2cb509 were rebuilt with planet techtree (their 'known' records came out identical; only 14, 15 and 21 firsts changed, e.g. pottery in 3097e3 is now halflings, invented, 18.8 kyr ago). The Technology tab reads the corrected firsts.
- 2026-10-29: Created from inbox draft draft-techtree-firsts-tie-prefers-taker.md (found by techtree-views).
