---
title: With live polities on, attitudes are walked twice (per people in the history, per culture in the religion read-out)
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lane201
blocked_by: []
relates: [PW-1481, PW-1465, PW-904, PW-1477]
refs: ["planet/lineages/history/polity_live.py::LivePolities._attitudes", "planet/lineages/history/polity_live.py::LivePolities._fates", "planet/lineages/attitudes.py::Attitudes", "planet/lineages/gods.py::Pantheons", docs/review/culture/polities/round10.md, docs/review/culture/attitudes/round1.md]
---

## Description
**In plain words.** Lane 201 (PW-1481) made conquest harshness read the winner's tolerance and aggression inside the history. The
history has no cultures, only peoples, so it keeps one `attitudes.Attitudes` per people (same temperament, same rules, stepped each
century from the live polities' wars, rule and contacts) and writes it to `polities_live.json` ("attitudes"). The religion read-out
(gods.py) still keeps its own `Attitudes` per culture after the run, from the read-out polities. With the switch on there are two
walks of the same rules on different grains and different luck.

**What misleads if never done.** With the switch on (v4), a people's card can say its rulers were tolerant (gods.py: a ruler's
tolerance sets how hard it pushes its faith) while the same people's conquests in the history expelled their subjects as an
intolerant winner would, or the reverse. Two numbers for one temperament, and Daniel cannot tell which one the history used.

**Options.**
- A. gods.py reads the history's per-people record when it exists: each culture's starting point and drift target take its
  people's live value at that time, plus the culture's own offset (cultures still differ; the people's history is one walk).
- B. The history steps cultures, not peoples: needs the cultures inside the history (they are made after the run today). Large.
- C. Keep both and label them: the read-out's per culture, the history's per people.
Lean: A, when the read-out becomes the live map (round7.md section 3: derive reading polities_live.json). Until then C is honest.
- [ ] one source for a people's temperament over time when the switch is on
