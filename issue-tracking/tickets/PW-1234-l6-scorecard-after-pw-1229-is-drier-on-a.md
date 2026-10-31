---
id: PW-1234
title: L6 scorecard after PW-1229 is drier on average (dry 18.8 → 22.9%, NPP 412 → 364); re-rolled draws needed to call it chaos or a shift
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: lane98
blocked_by: []
relates: [PW-1229]
refs: [tools/scorecard.py, docs/review/v1-cut/inland-pits.md, docs/review/v1-cut/scorecard_L6.txt]
created: 2026-10-31
updated: 2026-10-31
---

## Description
In plain words: after lane 98 made cut-off pits land (PW-1229), the six L6 scorecard worlds (seeds 1–6,
1000 Myr) came out different from the baseline, as expected when the run's physics changes at all.
On average they were drier (dry land 18.8 → 22.9%), with less plant growth (NPP 412 → 364) and fewer trees
(41.2 → 35.8%). Per seed it goes both ways: seed 2 18.5 → 18.2% dry, seed 3 19.7 → 27.8%. No hard failure.

On identical terrain (the same keyframe sliced with old and new code) the new rule moves the dry share by
at most 0.12 points and NPP by under 1%. So the move comes through the runs' different paths, not the
climate step. One draw can't separate a distribution shift from chaos. My own `planet simulate` runs of
seeds 1 and 2 with the new code disagree with the scorecard's (30.5% and 14.7% dry).

What to do: run two or three re-rolled seed sets (e.g. seeds 7–12, 13–18) on main before and after the
merge and compare the means and spreads. If the drying holds, look for the run-side mechanism (the run's
erosion or lakes now filling pits that used to be sea).
- [ ] dry/NPP/trees means over ≥ 3 seed sets, old vs new, within their spread (or a mechanism found)

## Updates
- 2026-10-31: Created from inbox draft draft-scorecard-shift-after-pw1229.md (found by lane98).
