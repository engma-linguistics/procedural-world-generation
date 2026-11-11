---
id: PW-1743
title: "Names on demand: a per-language name generator (20+ personal and settlement names) in the API and viewer"
type: story
status: todo
parent: PW-1736
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lang-assessment
blocked_by: []
relates: []
refs: [docs/review/language/assessment-2026-11-11.html, planet/language/personal.py, planet/langserve.py, viewer/langmore.js]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: for a campaign, names in bulk are the most-used language output, and a lect stores only 6 given and 2 full names. Generate more on demand from the lect's own naming tradition, words and grammar (deterministic per request seed), via langserve/API and a button in the viewer's Names tab: given names, full names with bynames, settlement names in the family's habit, with the Common's English alongside.
- [ ] /api endpoint + viewer button; 20 by default, more on request
- [ ] same tradition and spelling as the stored names

## Updates
- 2026-11-11: Created.
