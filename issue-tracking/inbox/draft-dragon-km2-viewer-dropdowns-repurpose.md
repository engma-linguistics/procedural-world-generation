---
title: "The viewer's 'dragons / giants where peoples press them: one per km2' dropdowns no longer set any density: repurpose them as 'how hard peoples press dragons'?"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: viewer
effort: s
impact: med
found_by: fun-lane-63
blocked_by: []
relates: [PW-1068, PW-923, PW-957, PW-963]
refs: [viewer/lineages.html, planet/lineages/spec.py, planet/lineages/history/megafauna.py, planet/lineages/samples/dnd.toml]
---

## Description
**In plain words.** The peoples' pressure on dragons and giants changed (PW-1068). It used to push every dragon in peopled country
down to a fixed "one per 5,000 km2". Now the peoples kill a share of the dragons each year, set by how many people there are, how well
armed they are and whether they have herds to defend, against how slowly dragons breed. So the two dropdowns in the viewer's
lineages settings no longer do what their labels say: "dragons where peoples press them: one per km2" and the giants' one. They are
still read, but only as a "nominal" number. It sets how hard a dragon line competes with other lines and how many dragons a patch
needs to last. It no longer sets how many dragons live anywhere.

Options:
- **A.** Repurpose the two dropdowns as "how hard peoples press dragons (and giants)". The choice would multiply the kill
  (`megafauna.KILL_Q`): gentle x0.5, default x1, harsh x2 or x4. That way you keep a lever on how rare dragons are in peopled country.
  The nominal number stays as it is, out of sight.
- **B.** Remove the dropdowns, plus `meta.dragon_km2` and `meta.giant_km2` from the spec, the samples and the tests. The competition
  and viable-population checks would take a fixed nominal number.
- **C.** Leave the dropdowns as they are, with an honest tooltip ("affects competition only").

Coordinator's lean: **A**. It is the most useful to you, since you use the viewer, not the command line.
- [ ] owner picks A, B or C
- [ ] (A) a meta setting (e.g. `meta.persecution`) multiplies KILL_Q; the dropdown labels and tooltips say so in plain words; dnd.toml
  and seven_meals.toml comments follow
