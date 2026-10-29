---
title: "Triple junctions split three ways too often: Burke & Dewey 1973 have one failed arm as the rule (32 of 40), our independent 0.3 per arm gives it 44%"
type: task
status: todo
parent: null
milestone: v2
subsystem: tectonics
effort: s
impact: low
found_by: papers-1029
blocked_by: []
relates: [PW-952]
refs: [planet/tectonics/events.py, planet/tectonics/params.py, docs/review/tectonics/rifts/rifts.md, docs/references/tectonics/burke_dewey1973_plume_triple_junctions_jgeol.pdf]
---

## Description
Burke & Dewey 1973 (J. Geol. 81:406-433) is now on file. Of their 45 selected plume-generated junctions (p. 426):
- 32 spread on two arms, and the third arm failed;
- 3 spread on all three arms;
- 5 failed on every arm beyond the rifting stage;
- 5 are too young to tell.

Their abstract (p. 406) and conclusion 1 (p. 429) call one failed arm "a normal course of events" and "commonly". Of the 40 mature junctions that is 80% two-way, 7.5% three-way and 12.5% none.

`events.triple_rift` fails each arm on its own with `aulacogen_odds` = 0.3. That gives 34% three-way splits (no arm failed), 44% two-way and 22% no split. So our three-way splits are about 4.5 times too common, and our two-way splits are about half as common as theirs. Their sample is selected (junctions recognisable in old rocks), so the shares are rough. They also list no single rifts and five possible four-armed junctions (p. 426).

Other points from the paper the model leaves out:
- Plumes rift continents "especially" where the lithosphere is at rest over the plume (p. 406, conclusions 1 and 8, p. 429). Plate speed plays no part in `triple_rift` today.
- Young rifts commonly reactivate old rifts and sutures (conclusion 7, p. 429).

Options. Each changes the plate breakups and needs paired L6 runs. No value has been changed.
- **A.** Pick the outcome directly: two-way 0.8, three-way 0.08, none 0.12 (the paper's mature shares).
- **B.** Keep independent arms but correlate them: one arm always fails unless a roll (~0.1) keeps all three.
- **C.** Leave it. Three-way splits are the feature the owner asked for in PW-952, and the paper's sample may under-count them.

Lean: B. It keeps the three-way feature, rarer, and matches the paper's rule of one failed arm. The expected effect is fewer three-piece splits per run (0-3 per 200 Myr today) and slightly larger largest plates. Check that PW-952's largest-plate gain (41 -> 26%) holds.
- [ ] outcome shares of `triple_rift` near the paper's (within the sample's roughness)
- [ ] largest plate share over 600-1000 Myr stays near PW-952's 26%; paired pass rate unchanged
