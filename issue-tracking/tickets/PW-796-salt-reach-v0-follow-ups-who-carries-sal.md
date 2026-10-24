---
id: PW-796
title: Salt reach v0 follow-ups - who carries salt, mineral licks as sources, and the cap and discounts are untuned
type: task
status: todo
parent: PW-692
milestone: v3
subsystem: timezoom
effort: m
impact: low
found_by: fun21
blocked_by: []
relates: [PW-745, PW-732]
refs: [planet/lineages/salt_reach.py, planet/lineages/brief.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
fun21 added `salt_reach.py` and the brief's `salt.reach` (own / traded / cut-off shares, `poor` = a quarter of the land cut off). Light by design; left open:
- Trade goes along rivers (x0.5) and contact zones (x0.6) only, with a 450 km cost cap; nothing says who trades (no `trade_reach` between peoples, no
  boats over sea gaps, so an island people far from salt reads the same as an inland one). The numbers are first guesses, not tuned.
- `_salt_kind` and the sources include mineral licks (50-66% of nearest sources in the 104de8 briefs): those are for herds, not people's salt; whether they
  count as a human source is a judgement call (dropping them would raise the cut-off shares a lot).
- The contact zone uses the leading people per cell at the brief's era; the contacts record (`meta.contacts`, border length, kind) is not read.
- Still no salting works (cured fish needs salt and fish at one coast) and no `[[use]]` row reads salt.
- [ ] decide the licks; [ ] sea routes for trade; [ ] per-people trade partners in the brief's `trade_reach`

## Updates
- 2026-10-24: RULING (coordinator): mineral licks stay a human salt source (many were saline springs later boiled for salt, e.g. Big Bone Lick).
- 2026-10-24: Created from inbox draft draft-salt-reach-follow-ups.md (found by fun21).
