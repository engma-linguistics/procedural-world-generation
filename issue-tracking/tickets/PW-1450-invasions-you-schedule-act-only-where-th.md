---
id: PW-1450
title: Invasions you schedule act only where the invaders' state already borders the victims, so most rows read 'it didn't'
type: task
status: todo
parent: null
milestone: v4
subsystem: peoples
effort: m
impact: med
found_by: lane177
blocked_by: []
relates: [PW-1433, PW-1432]
refs: [planet/lineages/invasions.py, "planet/lineages/polities.py::war_v0", viewer/invasiontab.js, "run a2b637", "run 3c1caf", docs/review/culture/polities/round2.md]
created: 2026-11-04
updated: 2026-11-04
---

## Description
In plain words: v0 of invasions you schedule (PW-1433) only raises war's chance between polities that already touch. A strong row
nearly always happens when the invaders have a state bordering the victims in its window (7 of 7 such rows did, on a2b637 and
3c1caf), but few rows get that far: of 30 strong one-century rows between six D&D peoples on a2b637, 5 had such a border; of 42 on
3c1caf (Seven Meals), 2. On 3c1caf the owner's own example, "the antelope-kin come down on the humans", can never happen: the
antelope-kin rule a state in one century only (1,500 years ago), and that state is new then, so it does not attack yet.

What misleads if never done: Daniel writes the invasions his campaign needs and most read "it didn't" (with a true reason), so the
feature looks broken for the common case of a people far away or without a state.

Options:
- A. Leave it to v4 (polities inside the history: a scheduled invasion can then move people and found the state it needs).
- B. A strong row lets the invaders' nearest state reach the victims across one unruled gap (an expedition: claim a corridor of
  cells to the victims' nearest polity before the war step).
- C. A strong row seats a state for the invaders at their largest town in the window if they have only chiefdoms (a "war band"),
  then war proceeds as now.
Lean: A for real campaigns, with B as a cheap v3 nudge if Daniel finds the read-outs too often negative.

## Updates
- 2026-11-04: Status needs-decision -> todo. Daniel 11-04: D50 B and C. Plus whatever accounts for highly mobile peoples (Mongol-horde analogues): mounted/nomadic peoples should reach and strike far beyond one border gap.
- 2026-11-04: Status todo -> needs-decision. Reopened (coordinator, 11-04): lane 183's live polities (PW-1434, switch off) did not make rows reach further: dnd s10's orc and hobgoblin rows found no border in the history; Seven Meals' antelope-kin row conquered 3.1 Mkm2 against 10.8 in the read-out (round7.md section 6). A alone is not enough; back on the desk as D50 with B and C.
- 2026-11-04: Status needs-decision -> todo. Daniel 11-04 (D50): A. Wait for v4: polities inside the history (PW-1434, lane 183) should give invaders reach.
- 2026-11-04: Coordinator: milestone v4, with polities inside the history; desk card D50 asks Daniel whether a strong row should reach further sooner.
- 2026-11-04: Created from inbox draft draft-invasions-need-a-shared-border.md (found by lane177).
