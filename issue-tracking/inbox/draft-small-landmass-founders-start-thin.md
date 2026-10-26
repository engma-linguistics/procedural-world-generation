---
title: Under the species-area origin draw (PW-888) some peoples now found on small landmasses and start thin: humans at 100 kyr ago, elves on 1df1c3
type: task
status: needs-decision
parent: PW-692
subsystem: timezoom
effort: s
impact: med
found_by: fun-lane-30
blocked_by: []
relates: [PW-888, PW-885]
refs: [planet/lineages/history.py, "world 2a7385", "world 1df1c3", "dnd tries 7000-7007"]
---

## Description
PW-888 draws each origin's landmass with probability (habitable cells)^0.3 (`history.SPECIES_AREA_Z`), so small landmasses and islands get a share; the founders must be viable (`tree.viable_pop`). Over 8 tries (7000-7007, dnd) this spreads the peoples, but some founders land on a small place and start thin:
- 2a7385, humans at 100 kyr ago: 22.1k, 5.3k, 25.6k, 15.9k, 4.2k, 0.3k, 2.9k, 3.5k cells (before: 3.6k, 24.5k, 18.6k, 16.6k, 17.7k, 3.5k, 3.5k, 24.4k); at the present 28.1k, 13.2k, 30.2k, 29.0k, 5.5k, 15.1k, 14.0k, 9.8k (before 8.7k, 30.5k, 29.8k, 29.4k, 26.7k, 7.2k, 6.7k, 32.6k). Mean at 100 kyr ago falls from 14.0k to 10.0k, the present mean from 21.5k to 18.1k (the old small-continent tries 7000, 7005 and 7006 do better now, the others worse).
- 1df1c3: humans at 100 kyr ago 3, 3 and 32 cells on tries 7001, 7006 and 7004 (2.7-6.7k on all eight before), present 12-26k (13-23k before); elves under 500 cells on 7004 (176) and 7007 (186): 6 of 8 at >= 500 (8 of 8 before).
Likely cause: a founder population at the viability floor (500 people) on a landmass of a few hundred km2 passes the filter but cannot grow. Options: A. accept (isolation, island peoples; the Holocene farmers still reach 12k+). B. raise the founder floor to a multiple of `viable_pop` (say 10x) so a landmass must hold a lasting population. C. weight the draw by (habitable area)^z only above a minimum landmass size and give smaller ones a fixed small share. Lean: B, behind the same 8-try sweep on both worlds.
- [ ] humans >= 1k cells at 100 kyr ago and elves >= 500 on 7 of 8 tries on both 2a7385 and 1df1c3, with no landmass under ~15% of the land holding most peoples
