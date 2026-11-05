---
id: PW-1471
title: "Humans alone (humans_only tree) never take up writing and rarely found chiefdoms: every urban step came by contact"
type: task
status: done
parent: null
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lane-192
blocked_by: []
relates: [PW-1466, PW-1461, PW-1448]
refs: [tools/peoples_robust/trees/humans_only.toml, planet/lineages/samples/techtree.toml, "planet/lineages/techtree.py::rate_of", "planet/lineages/techtree.py::band_wait", "planet/lineages/techtree.py::rebuild", docs/review/culture/polities/round8.md, "world 899985 (time zoom fc5311) L7, seed 7: scratch runs humans-only and dnd with polities in the history on (deleted)", "run 0141d1"]
created: 2026-11-04
updated: 2026-11-05
---

## Description
**In plain words.** On a world where the humans are the only people (the robustness tree `humans_only.toml`), they never learn to
write, so under D49 they can never have a state. In most draws they never found a chiefdom either, and in three draws of eight
they never even build huts, so they never live in villages or towns. The same world and seed with the whole D&D cast gives the
humans huts from the orcs (by way of their archaic ancestors), villages from the leonin, and towns and chiefdoms from the gnomes,
and they invent writing themselves 3,600 years ago (run 0141d1). So in the dnd tree every urban step the humans take comes by
contact. Alone, they have nobody to learn from, and the tree's own invention rates are too slow to make up for it.

The numbers (world 899985, L7, seed 7, polities in the history switched on; the tree re-drawn over the same history with
`techtree.rebuild(run, seed=s)` for 8 draws of its luck). The baseline is the same world and seed with the dnd tree:
- huts: never in 3 of 8 draws (huts' rate is 0.0043 a kyr after its 400 kyr floor: a median wait of about 160 kyr, with two dated
  origins, 400 and 23 kyr);
- villages: in 5 of 8, 2,600 to 9,400 years ago; towns in 5 of 8, 600 to 6,000 years ago;
- chiefdoms: in 2 of 8 (3,300 and 9,400 years ago); proto-writing and writing: in 0 of 8;
- states: none possible in any draw (D49: a state needs its own writing).

**What breaks if never done.** A world with one people, or with one isolated people on its own continent, can never have states,
and the brief and the polities say "no states" for a reason that is a rate, not the world. Earth invented writing at least three
or four times independently (Mesopotamia, China, Mesoamerica, probably Egypt), each without a writing neighbour. The model's humans
alone never manage it once in 8 draws.

**Options.**
- **A: keep it.** One people alone is an edge case; the robustness suite reports it and nothing else needs it.
- **B: give the urban chain a floor-and-wait, like the stone-age gated techs.** Tokens, proto-writing and writing get their rates
  from Earth's independent origins (band_wait, as pottery's), so a big settled people alone invents them in a few thousand years
  after towns. Huts' rate gets the same treatment from its two dated origins.
- **C: let a people learn from its own regions.** The tree treats a people as one learner; a huge people (here 145 Mkm2, 1.4 billion)
  spread over many continents is many peoples in all but name. The demes (demes.py) could be the learners. This is the larger,
  more faithful fix and touches the whole tree.

**Lean: B.** It is a rate fix sourced from Earth's own independent origins, and it leaves contact as the faster road where there is
one. C is right in the long run but is a project.
- [ ] on humans_only, 899985 seed 7, over 8 draws of the tree's luck: writing in most draws, states possible
- [ ] the dnd showcase's writing dates move by less than the 12-seed spread (round 6)

## Updates
- 2026-11-05: Status -> done. Lanes 200/200b merged (docs/review/culture/techtree/round2.md).
- 2026-11-04: Status needs-decision -> todo. Daniel 11-04 (D55): fix it. Climbing the tech tree must happen no slower than a given rate, not only by catching up with neighbours; independent re-invention should happen but never be forced. Local groups should each be learners: all humans on all continents as one learner 'sounds very wrong'. So B (own-invention rates from Earth's independent origins) and C (regional learners, demes) both, C as the structural fix.
- 2026-11-04: Created from inbox draft draft-humans-alone-never-write.md (found by lane-192).
