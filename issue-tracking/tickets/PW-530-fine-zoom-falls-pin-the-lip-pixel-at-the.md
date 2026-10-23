---
id: PW-530
title: Fine-zoom falls pin the lip pixel at the parent's lip height, so a horseshoe cannot recess the river's own crest
type: task
status: todo
parent: PW-516
milestone: v2
subsystem: zoom
effort: m
impact: low
found_by: pw522
blocked_by: []
relates: [PW-522, PW-516, PW-649]
refs: [planet/zoom_fine.py, planet/zoom_falls.py]
created: 2026-10-21
updated: 2026-10-23
---

## Description
PW-522's fine-zoom lip curves by holding the flanks' crest downstream (zoom_falls.horseshoe; lag 0 at
the river, up to 0.9 x the first tier at 1.3 x the gorge's half width). Niagara's centre is cut back
upstream of its flanks; here the river's pixels are pinned at the parent's lip height and position, so
the recess is only relative. A real recess needs the course above the lip to be re-laid (a notch cut
into the upstream channel and the parent's lip pixel moved back by the recess), with the upstream
course's bed lowered to meet it; that moves the parent's fall, so it needs a decision on how far a
fine zoom may move a parent's lip.
- [ ] move the lip up the course by the recess, with the bed above it graded into it

## Updates
- 2026-10-23: Filed under the quality-pass epic PW-649 (relates PW-649): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-21: Created from inbox draft draft-fine-fall-lip-notch.md (found by pw522).
