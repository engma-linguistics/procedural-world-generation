---
title: "test_store::test_run_lakes depends on chance: lakes of 0-4 cells on 2.5k cells; PW-582's slope current moves the first one from step 1 to step 25"
type: task
status: needs-decision
parent: null
milestone: null
subsystem: infra
effort: s
impact: med
found_by: base-climate-laneA7
blocked_by: []
relates: [PW-582]
refs: [tests/test_store.py, tests/conftest.py]
---

## Description
`test_run_lakes` steps the 300 Myr L4 fixture (`sim4`) on until a snapshot has lakes, at most 20 steps. With lane A7's
PW-582 attempt 1 (the inflow follows the polar seas' slope) it fails: no lakes within 20 steps.

Counted over 60 further steps (`scratchpad/laneA7/lakes.py`):
- with the slope current: lakes in 11 of 60 frames, the first at step 25;
- without it: 24 of 60, the first at step 1.

Every lake is 1-4 cells. So whether the test passes is chance in a chaotic run, not a property of the lakes code, and
the climate change only nudges which steps get lakes. The test checks the lake layers' encoding (`lake_kind`,
`lake_depth` on wet land only), which doesn't need a chaotic run.

- [ ] rule: give the test a deterministic lake (a fixture or a forced basin), or step further. Either is a test
  change, so it is for the coordinator. PW-582 can't merge while it fails.
