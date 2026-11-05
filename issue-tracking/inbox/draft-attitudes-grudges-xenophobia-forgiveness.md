---
title: "Attitudes v1: grudges between named peoples, xenophobia by species (difference x unfamiliarity), forgiveness and a stubbornness axis"
type: story
status: todo
parent: PW-856
milestone: later
subsystem: culture
effort: m
impact: med
found_by: lane199
blocked_by: []
relates: [PW-904, PW-1465, PW-1477]
refs: [planet/lineages/attitudes.py, "planet/lineages/attitudes.py::Attitudes", "planet/lineages/attitudes.py::temperament", "planet/lineages/gods.py::Pantheons._links", planet/lineages/compose.py, docs/review/culture/attitudes/round1.md, docs/review/cultures-proposal/proposal-r2.md]
---

## Description
**In plain words.** Lane 199 built attitudes v0 (PW-904): each culture now has a general **tolerance** and **aggression**, seeded from
its people's traits and moved by its own history (conquest, rule, contact, faith), drifting over centuries. What is not built is the
rest of PW-904's title: feelings about *particular* others. A culture does not yet hold a grudge against the people that conquered
it, fear a species it has never met (xenophobia as difference x unfamiliarity), forgive over time (faster with intermarriage, a shared
faith or language), or differ in how stubbornly it holds on to all of that.

**What misleads if never done.** The tolerance number reads as "how this culture treats outsiders", but it treats every outsider the
same: a culture conquered by orcs is as open to orcs as to its oldest friends. Harsh conquest (PW-1465) and forced conversion
(PW-1477) both read this one number, so the "Genghis Khan vs Cyrus" contrast is per ruler, never per pair.

Sketch (from the v0 code): a per-pair memory in `Attitudes` (culture -> other people -> grudge 0..1), raised by conquest and
expulsion events (polities `took`, PW-1465 fates), decaying with a per-culture stubbornness; xenophobia = body-plan distance x
(1 - contact years); the pair value lowers the tolerance used in `_links` for that pair only. The tree's old enmities (the `apart`
wishes) are a seed.
- [ ] per-pair grudge memory with a fading rate set by a stubbornness axis
- [ ] species xenophobia from difference and unfamiliarity
- [ ] PW-1465 and PW-1477 read the pair value instead of the general tolerance
