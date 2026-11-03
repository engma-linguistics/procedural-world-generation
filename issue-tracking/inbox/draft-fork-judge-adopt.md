---
title: "Use the forked paired judge (shared 300 Myr spin-up)? Built and exact, but it does not calm the hard bar's cold tail"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: infra
effort: xs
impact: med
found_by: lane144
blocked_by: []
relates: [PW-994, PW-1261, PW-558, PW-559]
refs: [docs/review/base-climate/fork-judge/round1.md, docs/review/base-climate/v1-finish-16/paired_fork.sh, docs/review/base-climate/v1-finish-16/fork.py, tests/test_fork_judge.py, docs/review/vegetation/herb-roots/round1.md]
---

## Description
**In plain words.** Lane 140d found that each test planet's carbon-cycle yardstick, learnt in its first 300 Myr, is
close to a random draw, so re-running a planet to judge a change also redraws the yardstick (draft
`draft-sink-reference-warm-spinup-lead.md`, option B). Lane 144 built a judge that runs each planet once to 300 Myr,
saves it, and continues both the current code and the candidate from that same saved planet. It is exact (the
current code continued from the save is the same run, bit for bit) and a little cheaper than the current judge. On
main's six coldest test planets it does not make the last ~120 Myr's ice any less random. A do-nothing change still
moves peak land ice by 3-23 points (3-27 without the fork), and one do-nothing run put 2 of the 6 over the 40% line.
What it does remove is a bias: re-runs of planets picked for being cold no longer come back warmer on average
(11 of 12 warmer without the fork, 6 of 12 with it).

Numbers (round1.md section 2; lane 140's frozen main 4abc1707, its six coldest draws, two no-physics nudges each):
- Hard-window peak land ice, |do-nothing minus main|: forked mean 10.7 (median 6.4) points against unforked 9.6 (6.5).
- Late (600-1000 Myr) dT, rms paired difference: forked 2.66 C against unforked 3.28 C (-19%, 12 pairs a side).
- hard_bar: forked do-nothing arms 0/6 and 2/6 frozen over in the window; unforked 0/6 and 0/6.
- The nudge's effect has grown to the full spread by ~600 Myr (rms dT difference 3.6-4.5 C at 500-600 Myr), long
  before the hard window opens at 884, so the window's ice is set by when the glacial eras fall, which the fork
  does not share.

Options:
- **A. Keep paired.sh as the merge judge; use the fork for targeted screens on selected draws** (cold-tail screens like
  lane 140b/c/d's), where its unbiased baseline matters, and as a cheaper way to tighten the continuous measures
  when wanted. Report a change's effect on the yardstick beside it (`CAND_SPIN=1`, `fork.py yard`).
- **B. Make the fork the merge judge.** ~15% cheaper per draw (half, with an existing main arm), narrower late-dT
  intervals, yardstick-free. Blind to a change's effect on the spin-up and the yardstick (must be reported apart),
  and no better on the hard bar.
- **C. Not adopt.** Leave the harness in review as is.
Lean: A. Nothing in the existing judge, its thresholds or pass rules changed.

- [ ] Daniel's choice
