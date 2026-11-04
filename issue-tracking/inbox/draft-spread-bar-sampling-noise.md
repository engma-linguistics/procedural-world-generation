---
title: The late-dT spread bar reads one 36-draw sample of a 400 Myr mean; re-judge before chasing it
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: med
found_by: scout193
blocked_by: []
relates: [PW-1446, PW-1404]
refs: [docs/review/tectonics/mountains/scout4.md, docs/review/tectonics/mountains/scout4_coupling.py, docs/review/tectonics/mountains/scout4_persist.py, docs/review/tectonics/mountains/scout3.md, docs/review/climate/npp/round2.md, tools/judge.py, "branch held/scout190-max-km"]
---

## Description
In plain words: the merge bar for climate changes says the late-climate spread between 36 planets should be about
1.3-1.7 C. Scout 190's mountain-height cap read 1.80 against main's 1.25 and was held. Scout 193 (scout4.md §4) found
that in every 133 Myr slice of the late window the two arms have the same spread (2-3 C, none of the differences
significant, main wider in one). The whole difference comes from whether a planet that is warm in one slice stays warm
in the next. That correlation is +0.3 on the cap and −0.1 to −0.3 on main across 36 chaotic draws, about a 2σ effect.
No part of the carbon loop differs measurably between the arms.

What misleads if it is never done: a sound physics change (the height cap) is held, and later ones may be tuned to
pass a statistic whose own sampling noise is about as large as the effect being judged. Main itself sits below the band
(1.25).

Do: re-judge main and the cap on a second, independent 36-draw roll set, or with the forked judge (forked main as the
baseline, since forking narrows the spread by about 19%, lane 144). Read whether the cap's excess holds. Do not change
the bar in this ticket.
