---
id: PW-1635
title: "Question words: 'who' built as 'what person' (fix the old-who + person bug) and 'when' gets its own time ending (D1, option A)"
type: task
status: done
parent: PW-767
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lang-coordinator
blocked_by: []
relates: []
refs: [docs/review/language/proposal-2026-11-10-paradigms-and-conquest.md, planet/language/lexsys.py, planet/language/lexicon.py, tools/language/sketch.py, "run a24559"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: the 11-10 proposal (Part 1) found that question words are built from a shared stem in many languages
(English wh-), and that our engine builds 'who' as 'old who + person' when it compounds, which is a bug. Option A,
which all three answers to the desk card p.qscope include, is: build WHO as WHAT + PERSON where a language derives it,
and give WHEN its own time ending instead of borrowing another's. If never done, some languages show a doubled
'who-person' word on their pages. The full grid (options B/C) waits for Daniel's answer on the Language Desk.

## Updates
- 2026-11-10: Status todo -> done. Lane 12: option A. lexicon.reinforce_parts builds a WHAT_X question word (WHO) renewed by a noun as WHAT + noun ('what person'), in core_repair and the function-word reinforcement; WHEN gets a 'time' affix (AFFIX_MEANINGS, source TIME; derivations.tsv 'time WHAT WHEN'), no longer the 'place' affix. a24559: WHO as old-who + person 0.034 -> 0, WHO on WHAT 0 -> 0.076, WHEN on WHAT 0.15 -> 0.19, WHERE = WHEN homophones 1 of 620. Options B/C wait on Daniel.
- 2026-11-10: Created from inbox draft draft-question-word-repair.md (found by lang-coordinator).
