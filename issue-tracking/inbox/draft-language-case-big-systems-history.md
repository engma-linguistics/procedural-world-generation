---
title: "Languages: big case systems (6+) wear away in the full history, not in the gram cycle: 26% of living lects against WALS 32%"
type: task
status: todo
parent: PW-767
subsystem: culture
effort: m
impact: low
found_by: language lane 10 (PW-1605)
blocked_by: []
relates: [PW-1605, PW-1586]
refs: ["planet/language/grammar.py::step", "planet/language/grammar.py::_check_lost", "planet/language/history.py::areal_step", "planet/language/history.py::AREAL_WEIGHT", "planet/language/lect.py::Lect.step", "planet/language/grammar.py::social_factors", "run a24559", "run de1cc6", docs/review/language/calibration.md]
---

## Description
In plain words: real languages with six or more noun cases are about a third of the world's languages (WALS 49A: 32%).
Our proto-languages start near that (about 40% of a24559's protos are born with 6+ cases), and a test bench that runs
the grammar alone, or a whole language with its sound changes, keeps them there over 20,000 years (lane 10 harness:
400 human protos, 800 generations: 6+ 33-35% with or without sound change). But in the full world history the share
falls in the first 6,000 years (living lects' ancestry in a24559: protos with 5+ bound cases 42% at 20 kyr, 25% at
14 kyr, 18-22% after) and ends at 23-26% of living languages (a24559 lane 9 23.5%, lane 10 26.3%; de1cc6 lane 9 18.9%).
Humans are lowest (a24559 lane 9: 6+ 12% of 99 human lects; other peoples 31%), but the human lects descend from a
handful of protos.

So what wears them away is something only the history has: contact (areal typology copying, AREAL_WEIGHT case 0.2;
loans), language shift and its L2 learners over time (the harness draws today's l2 per lect, not its history), koine
levelling, founder bursts (rate_now), or the shown typology a calque writes. Next step: run the lane 10 harness with
each of these switched on in turn (a small history, or replay one lineage's l2 and contacts from the snapshots), then
nudge the one that drains the big systems.

The 2-5 middle band stays high (28% against WALS 20%), mostly 3 and 4 cases (7.9% and 5.0% against 3% each): the
worn-down big systems pass through it.

**What misleads if never done:** the language page's WALS 49A comparison shows big case systems a fifth too rare and
small ones a third too common; a reader takes the world's grammar as poorer in case than real languages.
- [ ] the history step that drains 6+ named, with a harness measurement
- [ ] 6+ within ~4 points of 32% and 2-5 within ~5 of 20% in a full a24559 pass, none + borderline kept near 47%
