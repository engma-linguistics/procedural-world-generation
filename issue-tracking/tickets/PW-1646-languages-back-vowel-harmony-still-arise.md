---
id: PW-1646
title: "Languages: back vowel harmony still arises in about half of all lines within 2,500 years"
type: task
status: done
parent: PW-767
milestone: v4
subsystem: peoples
effort: xs
impact: med
found_by: lang-lane14
blocked_by: []
relates: [PW-1642, PW-1641]
refs: ["planet/language/rules.py::_demo", harmony.back, tools/language/real_inventory.py, tools/language/data/real_inventory_baseline.json, "planet/language/lect.py::LINE_FAMILY_SIGMA"]
created: 2026-11-10
updated: 2026-11-11
---

## Description
In plain words: Turkish-style vowel harmony (suffix vowels agree with the root's first vowel) is a family trait in the real
world (Uralic, Turkic, Mongolic, Tungusic) and rarely arises from scratch. In the engine it is an ordinary
naturalness-3 row whose input is in nearly every language, so it fired in 76% of the real-language benchmark's
daughters in 2.5 kyr before lane 14 and still 54% after the stronger line tendencies (PW-1642). Every other drift
signature went under the benchmark's 80% mark; this one is the largest left. If never done, about half of all
languages in a world look harmonic within a few millennia, and harmony stops marking a family.

Try: naturalness 3 -> 2 for harmony.back (a judgement on the catalogue, like S124 paragoge's), or make it a candidate
only for signature changes (lect.maybe_signature) so it marks branches; judge with `real_inventory.py --check`
(the harm column) and a full a24559 pass.
- [ ] harmony.back fires in under 25% of benchmark daughters; families with it keep it

## Updates
- 2026-11-10: Created from inbox draft draft-back-harmony-too-common.md (found by lang-lane14).
- 2026-11-11: Done in lane 17 (21bbe7a6): harmony.back naturalness 3 -> 2 plus weight-scaled wave adoption; benchmark daughters with back harmony 51% -> 16% (target < 25%); full passes, living lects with it in their own span a24559 51% -> 32%, de1cc6 49% -> 29%.
