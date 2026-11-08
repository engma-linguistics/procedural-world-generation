---
id: PW-1492
title: Faith timeline says \"no followers left\" for faiths that still survive as minorities
type: task
status: todo
parent: null
milestone: v4
subsystem: culture
effort: s
impact: low
found_by: lane205
blocked_by: []
relates: [PW-1489, PW-1358]
refs: ["planet/lineages/gods.py::Pantheons._check_end", "planet/lineages/gods.py::faith_docs", viewer/religiontab.js, docs/review/culture/faiths/minorities1.md, "run 0141d1"]
created: 2026-11-07
updated: 2026-11-07
---

## Description
In plain words: a faith "ends" when no culture holds it as its main faith any more. Since PW-1489 a culture keeps its old faith as a
minority after converting, so an "ended" faith can still be held by, say, a fifth of some culture. The Religion tab's timeline still
shows "no followers left" for it. A reader will take that to mean the faith is gone, when it lives on as a minority (see the Minorities
view of run 0141d1).

What breaks if never done: the timeline and faith records state something false for every faith that ended while it still has minorities.

Fix: in `faith_docs`, add `minority_in` (the cultures holding it as a minority now, from `Pantheons.comp`). Have the timeline say "no
majority left; a minority in N cultures" when that list is not empty. Keep `ended_kyr` as it is (it drives the map and the counts).
- [ ] faith records carry the cultures where the faith is a minority now
- [ ] the timeline's end text says so

## Updates
- 2026-11-07: Created from inbox draft draft-faith-end-ignores-minorities.md (found by lane205).
