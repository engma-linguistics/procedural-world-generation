---
title: "World faiths: how far should missionary faiths merge a world? (Seven Meals: three faiths hold 87% of cultures today, main 34%)"
type: task
status: needs-decision
parent: null
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane199
blocked_by: []
relates: [PW-1477, PW-904]
refs: ["planet/lineages/gods.py::MISSION_P", "planet/lineages/gods.py::MISSION_IND", "planet/lineages/gods.py::ETHNIC_RULE", "planet/lineages/gods.py::Pantheons._links", docs/review/culture/attitudes/round1.md, "run 07c755 (seven_meals)", "run 3e0eb4 (dnd)", "run 0141d1 (dnd)"]
---

## Description
**In plain words.** Lane 199 made faiths spread at real speeds (PW-1477): missionaries in a century or two per neighbour, rulers
pushing their faith within a generation (harsh) to millennia (tolerant). A faith the world makes turns missionary with an even chance
(MISSION_P 0.5, a judgement) once its god becomes a moralizing high god. What that does to a whole world depends on how many faiths
turn missionary:
- dnd 0141d1, none did: the largest faith holds 13% of cultures today (main: 11%);
- dnd 3e0eb4, none did, but your written dwarf faith is missionary: the largest (yours) holds 31% (main: 14%);
- Seven Meals 07c755 (frozen, only measured), five did: the three largest hold 87% of the cultures today (main: 34%), the largest 43%
  (main: 22%), 21 faiths left (main: 84).
None sweeps the world in centuries; Seven Meals' largest went from 17% to 43% over 2,000 years. Earth after ~2,000 years of
missionary faiths has a few world faiths holding most people, so neither result is wrong. It is a taste call.

**What misleads if never decided.** A world where most peoples share three faiths reads very differently in the culinary briefs
(shared taboos and feasts) from one with dozens of local faiths, and that is set by one unsourced 0.5.

**Options.**
- A. Keep as is (MISSION_P 0.5): worlds range from many local faiths to a few world faiths, by luck and tree.
- B. Fewer world faiths: MISSION_P 0.25, so most high-god faiths stay ethnic. Seven Meals would likely keep more faiths (not measured).
- C. Make it a run choice beside the gods mode (a "world faiths" dial: few / some / many) shown in the viewer, default A.
Lean: A, with C later if you find yourself wanting to steer it. The spread is a mechanism with sourced speeds; how often a faith
turns missionary is the one free number.
