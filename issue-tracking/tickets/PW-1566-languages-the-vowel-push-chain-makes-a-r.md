---
id: PW-1566
title: "Languages: the vowel push chain makes a raised e (i̞) in 6-11% of living lects (PHOIBLE 0.2%); one rulings pass failed the overused check on it"
type: task
status: todo
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lang-rulings (2026-11-08)
blocked_by: []
relates: [PW-1539]
refs: ["planet/language/rules.py::dispersion_rule", "planet/language/rules.py::pick_rule", planet/language/checks.py, docs/review/language/calibration.md, "run a24559", "scratch passes rulings/alone, rulings/bursts (deleted; numbers in calibration.md 'Rulings lane')"]
created: 2026-11-08
updated: 2026-11-09
---

## Description
In plain words: when a sound change would merge two vowels and is turned down, the vowel in the way is pushed one step
on (a push chain, as in the Great Vowel Shift). For e the step up is "half-way to i", a raised e written i̞, a vowel
almost no real language has as a phoneme (PHOIBLE 0.2%). The push fires in about one lect in six over a run, and the i̞
spreads to the daughters.

Measured on a24559: living lects with an i̞ vowel (any length or tone) 34 of 622 in the stored lang-lane output, 59 of 622
in the rulings bursts pass; in the rulings pass without bursts the plain i̞ reached 10.7% and failed the overused-segments
check (ratio 47x PHOIBLE). Lects whose own changes include `dispersion.push.e`: 180 of 1182 stored, 197 of 1183 bursts;
faster lines push more (rate over 1.25: 76 of 411 lects in the bursts pass against 22 of 231 before), so the rate spread
pushed it over the line in one variant. It is not new: it was under the 10% floor by luck.

**What misleads if never done:** the overused check fails on any seed or rate change that tips i̞ over 10%, and a
tenth of the world's languages carry an odd vowel only a push-chain artefact makes.

What I'd try: in `dispersion_rule`, move the pushed vowel to the nearest *common* vowel quality in that direction that the
lect lacks (e > i only when the lect has no i; else no push, or centralize to ɪ), rather than one height step; or let
cap_inventory fold a pushed vowel one axis from a commoner one as it does other rare new units.

- [ ] i̞ under ~1% of living lects; the overused check passes on two seeds

## Updates
- 2026-11-09: Fix merged dffed688: a pushed front/back vowel skips in-between heights; raised e (i̞) 10% -> 0 of languages on the a24559 pass. Close after one more seed.
- 2026-11-08: Created from inbox draft draft-language-push-chain-raised-e.md (found by lang-rulings (2026-11-08)).
