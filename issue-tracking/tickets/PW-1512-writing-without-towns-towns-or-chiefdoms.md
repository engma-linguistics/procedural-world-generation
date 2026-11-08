---
id: PW-1512
title: "Writing without towns: 'towns or chiefdoms' cannot read the chiefdoms tech (everyone has it); read a chief seat of its own?"
type: task
status: todo
parent: null
milestone: v4
subsystem: culture
effort: m
impact: med
found_by: lane208
blocked_by: []
relates: [PW-1495, PW-1490]
refs: ["planet/lineages/techtree.py::Calendar.settled", "planet/lineages/techtree.py::Calendar.can", "planet/lineages/techtree.py::Calendar.gated", "planet/lineages/techtree.py::Calendar.keeps", "planet/lineages/techspread.py::town_footprint", "planet/lineages/polities.py::derive", "planet/lineages/history/polity_live.py::LivePolities", docs/review/culture/techtree/round4.md, docs/review/culture/techtree/round4/chiefs.py, docs/review/culture/techtree/writing_without_towns.md, docs/review/culture/techtree/round3/lag.py, docs/review/culture/techtree/round3.md, "run 07c755", "run 0141d1", "run 3e0eb4"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
**In plain words.** You asked (11-07, back to your D60 B wording) that a people with "towns or chiefdoms of its own" may take up
writing and the other state techs. Inventing them still needs a town (D62 A). The record supports this: Germanic runes, Ogham in
Ireland and the Tuareg's Tifinagh were all taken up by peoples with chiefs and no towns (`writing_without_towns.md`).

Lane 208 measured the simplest reading: "holds the chiefdoms tech". It undoes the gate, because in the model nearly every people
knows chiefdoms by 500 years ago (96-100%). Measured against main e6cb463c (round4.md, 8 draws):
- Writing among peoples without a town: 6% → 89% (07c755), 33% → 89% (0141d1), 40% → 90% (3e0eb4).
- Writing among mobile peoples without a town (foragers, herders): 7% → 93% on 07c755.

So the variant was not merged. Main's rule (towns only) stands.

**What misleads if never decided:** chiefly peoples without towns (the model's runes-and-Tifinagh peoples) never write, though you
named them in the rule. Or, if the tech is read, nearly every band writes.

**Options.**
- **A. Keep towns only (main).** Simple. It misses the chiefdom readers that you asked for and the sources show.
- **B. The chiefdoms tech (measured).** It undoes the gate (above). Not recommended.
- **C. A chief seat of its own.** The people rules land as a chiefdom (or higher) in the polities:
  - Data: the live polities' records (switch on), or `polities.derive`'s chiefdom tier after the run.
  - It is added to the footprint `settled()` reads, for taking up only. That is the thing your wording names, and it uses no new
    number.
  - It needs the polity footprint wired into the calendar's `towns` input (or a sibling input), and a check that derive's
    chiefdoms are not themselves near-universal.

**Lean: C.** It is your wording, read literally, and the model already seats chiefdoms. Measure as round4.md does (writing at 0.5 kyr
ago, mobile peoples without towns), against main. Effort m: the read-out runs after the calendar, so the order needs care.

## Updates
- 2026-11-08: Status needs-decision -> todo. Coordinator: option C is Daniel's own 11-07 wording ('towns or chiefdoms'); no decision needed. Next culture lane builds it, checking derive's chiefdom tier is not near-universal.
- 2026-11-08: Created from inbox draft draft-chiefdom-seat-uptake.md (found by lane208).
