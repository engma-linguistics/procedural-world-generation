---
id: PW-1090
title: "Coasts package (PW-998 rounds 1-3) judge: finish A vs D and check whether it cools generated worlds into iceboxes"
type: task
status: done
parent: PW-013
milestone: v1
subsystem: climate
effort: m
impact: med
found_by: lane26b
blocked_by: []
relates: [PW-998, PW-026]
refs: [planet/climate.py, docs/review/base-climate/coasts/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
Lane 26b's paired judge of the coasts package was paused for the speed lane: A = db7a178a against D = e0158fa2
(rounds 1-3). It stopped at A 34/36, D 13/36, in lane 26b's scratchpad `judge/`. To finish: SIGCONT the paired.sh
trees (or re-run paired.sh for D into the same root; done draws are skipped), then
`pjudge.py <root> A D --table`.

Preview (incomplete):
- A vs D, 11 pairs: pass 8/11 against 5/11, icebox 1 against 6; arid % -4.9 [-7.3, -1.0].
- A vs round 1 alone (B), 15 pairs: icebox 2 against 5.
- Earth L6 gains: SE USA 40 -> 48% of GPCC (round 1 -> 3), Pampas 31 -> 43%, corr 0.704 -> 0.722, exact
  37.1 -> 38.4, B 26.4 -> 25.2.

Hypotheses and probes for the iceboxes: the coasts README's last handoff. If the package fails, split it round-wise,
starting with round 1's 15 B runs.

## Updates
- 2026-10-30: Status todo -> done. Superseded: the coasts judge ran on lane 28b (vs F, 18 L6): passes 13/18 vs 14/18, iceboxes 8 vs 5; merged 53807d76.
- 2026-10-30: Created from inbox draft draft-coasts-package-judge-icebox.md (found by lane26b).
