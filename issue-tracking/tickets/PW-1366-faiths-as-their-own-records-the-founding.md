---
id: PW-1366
title: "Faiths as their own records: the founding, schism and conversion rule (judgement call)"
type: task
status: todo
parent: PW-1308
milestone: later
subsystem: culture
effort: s
impact: med
found_by: lane133
blocked_by: []
relates: [PW-1358, PW-1306, PW-1311]
refs: ["planet/lineages/gods.py::Pantheons._schisms", "planet/lineages/gods.py::Pantheons._conversions", "planet/lineages/gods.py::contacts", "planet/lineages/gods.py::faith_docs", "planet/lineages/gods.py::FAITH_RULE", planet/lineages/faithmap.py, viewer/religiontab.js, tests/test_gods.py, docs/review/religion/slice2.md, docs/review/religion/stats-round1.md, tools/religion_stats.py, "run b4d502", "run a24559", "run 3c1caf"]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: until now a "religion" was simply a culture's set of gods. Daniel asked that faiths be records of their own, able to spread to
other cultures or die out while their culture lives. Lane 133 added the smallest rule that does it (readout only, the history is untouched):

1. **Founded**: a culture that gets gods by itself (it learns spirit ritual and no parent culture had gods) founds a faith; its "core" is the
   culture's most salient domain then (sea, sky, forest...).
2. **Inherited**: a daughter culture keeps its parent's faith; when two cultures merge, the survivor keeps its own.
3. **Schism**: a culture whose most devoted god has had another top domain than its faith's core for **20 kyr** (SCHISM_KYR) breaks away as a
   new faith ("the forest schism of ..."). A faith's last culture does not break away; the faith's core moves instead (logged as a change).
4. **Conversion**: two cultures that share or border cells in a frame, of different faiths: if the neighbour's leading god is at least
   **0.45** individuated (temples) and **0.15** more than its own, the culture converts with chance 1 - exp(-dt / **30 kyr**) per frame, taking
   a copy of that god and keeping its own (syncretism). A converted culture does not break away by drift (otherwise its old gods win back
   within 20 kyr and every conversion undoes itself, seen in the first test).
5. A faith with no cultures left ends: "no followers left" when they all converted or broke away, else "its cultures ended".

Run b4d502 (rebuilt tech tree): 205 faiths ever, 95-97 living for 298 living cultures; 101 founded, 104 schisms, 13-20 conversions, 4 faiths
ended with no followers left. Biggest faiths hold 30-55 cultures of several peoples (a stem's faith inherited down the culture tree).

Options:
- A (done): as above.
- B: conversion also from equal individuation by population or prestige (needs a population per culture, not in cultures.json now).
- C: schism on a slower clock or only on daughter splits (fewer, larger faiths).
Lean A for v2; revisit the three numbers after Daniel has seen the map.

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: languages, polities, religion and owner's-world empires wait until food is done (fresh-eyes review, D44)
- 2026-11-02: Status needs-decision -> todo. Daniel 11-02: keep the rule as built (A); no hurry. Revisit the three numbers together once he has looked at the map and timeline.
- 2026-11-02: Created from inbox draft draft-faith-spread-rule-call.md (found by lane133).
