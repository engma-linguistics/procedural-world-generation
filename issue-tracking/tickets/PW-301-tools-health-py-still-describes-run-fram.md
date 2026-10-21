---
id: PW-301
title: tools/health.py still describes run-frame lakes and downstream as a step stale (fixed by PW-239)
type: task
status: done
parent: null
milestone: null
subsystem: infra
effort: xs
impact: low
found_by: surface-hydro
blocked_by: []
relates: [PW-239, PW-246]
refs: [tools/health.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Since PW-239 a run frame's `downstream`, `flow`, `lake_kind` and `lake_depth` are worked out on the frame's own
terrain (output.water_now). tools/health.py still says otherwise in `real_hollows`' docstring, in the report's
caveat ("a keyframe's lakes and `downstream` come from the terrain before that step's erosion ... so
`inland_raw_pct` runs ~2-3x `inland_pct`") and in the `inland_pct` envelope note ("stale by a step"). After
PW-239 `inland_raw_pct` and `inland_pct` should agree, apart from ends under land ice (tests/test_health.py
test_frame_rivers_end_in_its_own_hollows). Update the text; `real_hollows` can stay as a check, or the two
measures can be merged into one.

## Updates
- 2026-10-15: Status todo -> done. Done: health.py text updated (envelope note, real_hollows docstring, report caveat).
- 2026-10-15: Created from inbox draft draft-health-caveat-after-pw239.md (found by surface-hydro).
