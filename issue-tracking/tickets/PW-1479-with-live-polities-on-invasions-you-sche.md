---
id: PW-1479
title: With live polities on, invasions you schedule still need a shared border (no war band, no expedition)
type: task
status: done
parent: null
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lane198
blocked_by: []
relates: [PW-1450, PW-1434, PW-1433]
refs: ["planet/lineages/history/polity_live.py::LivePolities", "planet/lineages/polities.py::_war_bands", "planet/lineages/polities.py::_expedition", "planet/lineages/polities.py::war_v0", planet/lineages/invasions.py, docs/review/culture/polities/invasions_reach.md, docs/review/culture/polities/round7.md]
created: 2026-11-04
updated: 2026-11-05
---

## Description
In plain words: lane 198 (PW-1450) made a strong invasion reach the victims in the polities read after the run: a war band if
the invaders have only chiefdoms, and an expedition across the gap (further for nomads and herders). The live polities inside the
history (POLITIES_LIVE, off by default) still run plain v0, because `polity_live.py` was being edited by lane 196 at the same time
and was left alone. With the switch on, a strong row there still acts only across a shared border.

What misleads if never done: when live polities are turned on (v4), the rows Daniel writes go back to mostly "it didn't" inside
the history (round7.md section 6: the dnd s10 orc and hobgoblin rows found no border in the history), while the read-out says they
happened. The two maps disagree about the same row.

What to do (about ten lines in `LivePolities` step 2-4):
- [ ] call `PO._war_bands(self, seats, self.inv_rows, ago, self.prev_cap, self.open_, self.anc)` before `by_key` (it needs
  `self.knows`, which LivePolities has);
- [ ] give the war step `ctx["expedition"]` as derive does (`PO._expedition` reads `R.lines`, `R.lidx`, `R.ekm` and the frame's
  `edz`, `sea`, `ice`: pass a small dict of the live arrays as F), and turn each `exped` log entry's `w`/`l` into record ids
  after the war call, as derive does;
- [ ] a test like tests/test_invasions.py's gap world, through LivePolities.

## Updates
- 2026-11-05: Status -> done. Lanes 201/201b/201c merged (docs/review/culture/polities/round10.md).
- 2026-11-04: Created from inbox draft draft-live-polities-invasions-reach.md (found by lane198).
