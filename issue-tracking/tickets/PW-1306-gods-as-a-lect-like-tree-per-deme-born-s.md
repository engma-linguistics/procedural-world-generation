---
id: PW-1306
title: Gods as a lect-like tree per deme (born, split, merge, drift, fade) with an individuation slider and a gods-mode switch, as a readout
type: story
status: todo
parent: PW-1308
milestone: v2
subsystem: timezoom
effort: l
impact: high
found_by: religion-doc-chat
blocked_by: []
relates: [PW-907, PW-981, PW-986, PW-711]
refs: [planet/lineages/demes.py, planet/lineages/cultures.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: each people's gods are tracked like their languages. A god is born when something matters to a group for long
enough. It is copied when the group splits, so the copies drift into cousins (Zeus and Jupiter from one sky father). It fuses
with a neighbour's god on conquest or long contact, shifts as the land changes (an inland sea god becomes a rain god, slowly), and
fades when its worshippers die out.

Design, settled in the religion doc (https://claude.ai/artifact/Tk4g2nkJPQpTJgeDXo6KoP (Claude Docs id d890d9ce-3695-47c4-add1-a21c3c1a3bf2)), section 2-3 of "Claude's take, round 1":
- Each being: a weight vector over about 20 domains (sky, sea, rain, flood, herd, smithing, death...). Each history step
  nudges it toward what the deme's land and way of life make salient now. The decay of old domains is slower than lect drift,
  because ritual is conservative. 3-15 beings per deme, updated every 25-year step.
- Individuation per being (0 = a spirit bound to one place or feature, 1 = a named person-god). It rises with the faith nodes the
  people holds (see the faith tech-nodes story). A spirit bound to a feature hangs on the hydrology or relief feature.
- meta gods_mode: faith_made (default) | belief_only | absolute. faith_made: no worshippers, no god (no pre-sapient gods).
  The history is identical across modes; only the readout wording and the spell-granting flag change. No feedback in v2.
- Under the parent epic (religion draft). Names wait for PW-986 (cognate god names from the lect tree).
- Daniel uses the viewer, not the CLI: the culture card needs a gods panel, and the mode needs a world-creation control (relates PW-711).

## Updates
- 2026-11-02: Supersedes PW-907 (folded in): read PW-907's 11-02 rulings before building.
- 2026-11-02: Created from inbox draft draft-gods-tree-individuation.md (found by religion-doc-chat).
