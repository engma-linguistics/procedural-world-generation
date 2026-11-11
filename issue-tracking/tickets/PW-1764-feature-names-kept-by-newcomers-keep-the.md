---
id: PW-1764
title: Feature names kept by newcomers keep the namer's spelling instead of being re-heard (needs a public hearing call in planet/language)
type: task
status: todo
parent: null
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lane311
blocked_by: []
relates: []
refs: ["planet/lineages/featnames.py::walk", "planet/lineages/featnames.py::coin", "planet/language/names.py::_hear", "planet/language/names.py::_Pass.water_name", "run a24559 (copy)", docs/review/names/lane311.md]
created: 2026-11-11
updated: 2026-11-11
---

## Description
Lane 311 names peaks, ranges, capes, bays, islands and seas in planet/lineages/featnames.py, outside planet/language (owned by
another session). When a people of another language family takes over a feature and keeps its name (a substrate name, P2), the
name keeps the first namer's spelling: the adapter cannot re-hear it through the newcomers' sounds, because the only function
that does that, `names._hear` (profiles.hear_word, then the listener's repair), is private. Rivers and lakes are re-heard (the
language pass names them). On a24559 about a third of the coined feature names are substrate names.

What misleads if never done: a kept mountain or island name is spelled in sounds the people who say it now do not have, so the
local-name map mixes spellings of several languages in one region, and the 'kept as heard' layer looks the same as the original.

Try: expose a public `hear(form_ipa, listener_lect)` in planet/language (names.py or profiles.py) that returns ipa and the book
spelling, and call it from featnames.walk for the 'substrate' layer.
- [ ] a substrate peak's local name on a24559 uses only segments of the sayer's inventory

## Updates
- 2026-11-11: Created from inbox draft draft-feature-names-heard-by-newcomers.md (found by lane311).
