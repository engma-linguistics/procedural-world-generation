---
id: PW-1742
title: "Viewer: flag language isolates (where is this world's Basque?), relic isolates inside a big family's spread first"
type: story
status: todo
parent: PW-1736
milestone: v4
subsystem: viewer
effort: m
impact: med
found_by: lang-assessment
blocked_by: []
relates: []
refs: [docs/review/language/assessment-2026-11-11.html, planet/language/families.py, viewer/langview.js, viewer/langmap.js, "run a24559"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: Daniel 11-11: language isolates would be neat to flag in the viewer, 'where's my Basque equivalent on a given world'. An isolate is a living language with no demonstrable relatives, as the world's scholars see it (the scholars' tree, not the true tree: a Basque is an isolate because the comparative method finds nothing, whatever the deep truth). The interesting ones are relic isolates: an isolate whose neighbours mostly belong to one large family that spread later (Basque among Indo-European).
Caveat: today 175 of 264 true families are single-lect, and 549 of 579 languages are one lect, so a plain 'isolate' flag would light up most of the map. Rank instead: isolate status in the scholars' tree x how surrounded it is by one big family x age of its line, and flag the top few per world as 'relic isolates' (with a short why: 'last survivor of the X line; everyone around speaks Y-family languages since Z kyr'). Fewer, truer isolates also depend on families expanding (polities PW-1549).
- [ ] families.py exports per living language: scholars' isolate yes/no, relic score and its why
- [ ] viewer: an isolates filter/badge on the Families tab and map, the relic isolates listed first
- [ ] the finder (tools/language/find.py, language-finder skill) can answer 'isolates'

## Updates
- 2026-11-11: Created.
