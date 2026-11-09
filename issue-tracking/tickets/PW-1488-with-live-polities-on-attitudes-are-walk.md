---
id: PW-1488
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
created: 2026-11-05
updated: 2026-11-09
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

## Updates
- 2026-11-09: Lane 238 (round15.md section 4): unblocked by PW-1575 (the read-out now draws the live map), not done: option A needs calls first (the history samples each people's axes only every 0.5 kyr; it has no town term and counts peoples not cultures for contact): keep gods.py's own contact/town terms on top of the people's value or not, and record the history's walk per century?
- 2026-11-09: Lane 234: left as option C until the read-out draws the live map (new read-out-reads-live-map ticket); then option A.
- 2026-11-08: Lane 234 (round14.md section 4): left as is. Option A only makes sense once the read-out draws the live map (lane 234 draft 'the read-out should draw the live map'): until then gods.py has its own rulers and wars from polities.derive, and seeding its cultures from the history's per-people walk would mix two maps. Interim is option C in effect: polities_live.json labels its walk 'keyed_by: people (line index; the history has no cultures)', gods.py's is per culture. When the read-out reads the live map, gods.py should take each culture's start and drift from its people's live record (A) and drop its own conquest/rule memories.
- 2026-11-05: Created from inbox draft draft-two-attitude-walks-with-live-polities.md (found by lane201).
