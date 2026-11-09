---
id: PW-1436
title: "Names slot: every culture, faith, state and place carries a name field for the languages work"
type: task
status: done
parent: null
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: coordinator
blocked_by: []
relates: []
refs: []
created: 2026-11-03
updated: 2026-11-09
---

## Description
In plain words: the brief and viewer read one name field; Daniel's language worktree fills it when it lands; PW-1249 gloss names are the fallback. Plan: docs/review/board/milestones-v2-v5.md.

## Updates
- 2026-11-09: Status todo -> done. Lane 255: planet/lineages/nameslot.py. Each culture, faith, state and place has one name (plus gloss_name and name_from). The languages fill it where the run has languages.json: a culture gets its largest living deme's endonym, a place its settlement name, a state its capital's name, and a faith 'the sky faith of <culture>'. PW-1249 gloss names are the fallback. Filled at read-out in /api/cultures, /api/gods, /api/polities and the brief's Ctx. a24559: 301 of 305 living cultures named from the language, 0 repeats; 1e97dd: 267 of 269. Viewer: Cultures tab name column (gloss in grey beside a language name), and the brief, faith and state cards read the same field. Follow-up draft: old capitals have no language name.
- 2026-11-03: Created.
