---
id: PW-1425
title: "Hard bar: a world fails 'frozen over' when it ends or stays frozen, not when its worst moment in 884-1000 Myr crosses 40%"
type: task
status: done
parent: null
milestone: later
subsystem: climate
effort: s
impact: high
found_by: lane158
blocked_by: []
relates: [PW-1404, PW-994, PW-1261]
refs: [docs/review/climate/stability/round1.md, docs/review/climate/stability/tools/attractor.py, docs/review/climate/stability/tools/pulse.py, docs/review/climate/stability/tools/pulse_read.py, docs/review/climate/stability/tools/pulse_parts.py, tools/hard_bar.py, tools/judge.py, tools/ice_criteria.py]
created: 2026-11-03
updated: 2026-11-04
---

## Description
**In plain words.** The frozen-over check reads the single worst moment of a 116-Myr window. One cold test planet
(r0.001 l6c_p 957317, main 4abc1707) has five equally valid histories: lane 144's forked main and two do-nothing
re-runs, plus lane 158's two pushed runs. Two of the five peak above 40% land ice in the window and three don't. All
five are below 21% by 980-990 Myr, and none ends frozen. A -8 C push for 60 Myr was answered within ~10 Myr and
nothing locked in. The check is reading when the glacials fall, which the plates' chaos sets. It is not reading
whether the world is broken.

Baseline: the same planet's other histories on main 4abc1707.

Options:
- **A. Ends or stays frozen.** Hard failure = land ice >= 40% at the run's end with no finish moment passing for ice,
  or >= 40% held from some time to the end. The window's peak moves to the soft scorecard (with time at >= 40% and
  mean land ice). On the five histories: 0 of 5 fail (now 2 of 5).
- **A + recovery check.** As A, plus, for any draw that fails: a forked -8 C push for 60 Myr must return within
  ~20 Myr of its unpushed twin (pulse.py, ~1 run).
- **B. Keep the peak, judge against nulls** (PW-1404 option A).
- **C. Leave as is.**

Lean: A + recovery check, together with the yardstick fix (draft-climate-yardstick-one-constant). Without that fix,
cold-yardstick draws still sit near the line.
- [ ] Daniel's choice (a judging change)

## Updates
- 2026-11-04: Status todo -> done. Lane 170/170b merged (D47 C): paired 36 L6 draws vs main 1ecdad3a: 0 hard both, soft 30 vs 28 (p 0.79), late dT all inside -6..+5, spread sd 2.09 -> 1.73 C, cold tail p10 -1.55 -> -0.69, main's two hot outliers gone. YARDSTICK {6: 1.377, 7: 1.542}. docs/review/climate/stability/round3.md.
- 2026-11-03: Status needs-decision -> todo. Owner 11-03: D47 C, approved: frozen over = ends frozen or stays frozen to the end; 40% line unchanged.
- 2026-11-03: Milestones 11-03: v2 -> later: physics side track, ranked 1; gates no tag (D47, approved)
- 2026-11-03: Created from inbox draft draft-hard-bar-ends-frozen-not-peak.md (found by lane158).
