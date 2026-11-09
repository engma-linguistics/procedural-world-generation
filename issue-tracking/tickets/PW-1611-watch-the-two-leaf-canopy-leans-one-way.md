---
id: PW-1611
title: "Watch: the two-leaf canopy leans one way on the soft pass count and on glacial maxima"
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: s
impact: low
found_by: coordinator
blocked_by: []
relates: [PW-1518]
refs: [docs/review/climate/diffuse/screens.md, docs/review/climate/diffuse/out/judge_36draw.txt]
created: 2026-11-09
updated: 2026-11-09
---

## Description
**In plain words.** PW-1518's two-leaf canopy passed every bar, but the soft pass count leaned to main in every batch: pass 3 (24 L6 pairs) 19 vs 23, the 36-draw judge 30 vs 34 (discordant 6 vs 2, McNemar p 0.29; 8 draws shared between the two). Fails go both warm and cold, and no continuous measure moved (end T +0.38 C [-1.57, +1.70]). The judge also reports glacial maxima (land ice >= 25% at some moment) in 18 of 36 two-leaf draws against 13 of 36 on main.

**What misleads if never done.** Each batch alone reads as chance; together they might be a small loss of steadiness. The next physics judge that runs on main is the cheap place to see whether the lean persists: compare its soft count and glacial-maximum count against runner 252's main arm (00cfe6d3).
- [ ] the next 36-draw judge on main: soft pass and glacial-maximum counts against 00cfe6d3's 34/36 and 13/36

## Updates
- 2026-11-09: Created from inbox draft draft-two-leaf-pass-lean.md (found by coordinator).
