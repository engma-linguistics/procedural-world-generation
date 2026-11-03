---
id: PW-1408
title: "Runs made before PW-1390 replay from t=0: their checkpoints are in the old format"
type: task
status: done
parent: null
milestone: v2
subsystem: store
effort: xs
impact: low
found_by: lane 147
blocked_by: []
relates: [PW-1390, PW-1035]
refs: ["planet/store.py::read_checkpoint", "planet/store.py::unpack_state", "planet/timeline.py::replay", docs/review/speed/memory-fixes/round1.md]
created: 2026-11-03
updated: 2026-11-03
---

## Description
In plain words: PW-1390 changed how checkpoints are stored (the plates packed, not a full pickled copy).
Checkpoints written by older code no longer load; `timeline.replay` already catches that (PW-1035) and
replays from t=0, which gives the same world but slowly (an L7 1 Gyr run: ~35-50 min per slice instead of a
few). Nothing is wrong, but runs Daniel keeps will slice slowly until their checkpoints are re-saved.

What to do after the merge (no backward-compatibility code in planet/):
- [ ] list runs under runs/ with `state/*.ckpt` older than the merge;
- [ ] for the ones worth keeping, either delete them and re-simulate, or re-save the checkpoints with a one-off
  script outside planet/ (load each old checkpoint with the pre-merge code, `Simulation.from_state`, then
  `store.save_checkpoint` with the new code; check one slice matches its keyframe).

## Updates
- 2026-11-03: Status todo -> done. Lane 149: tools/resave_checkpoints.py built and verified on a fresh old-code run, but none of the 68 runs' 687 checkpoints is convertible: all lack state fields added since they were written, so they already replayed from t=0 before PW-1390. Nothing under runs/ touched. Follow-up PW-1410.
- 2026-11-03: Created from inbox draft draft-old-checkpoints-replay-from-zero.md (found by lane 147).
