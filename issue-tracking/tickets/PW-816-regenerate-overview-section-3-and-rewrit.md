---
id: PW-816
title: Regenerate overview section 3 and rewrite section 2.6 (stale Earth numbers, wrong CO2 text); fix decisions.md:33 and README's biome line
type: task
status: done
parent: PW-244
milestone: v1
subsystem: docs
effort: s
impact: high
found_by: assumptions-audit
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-10-31
---

## Description
From the pre-v1 assumptions audit (docs/review/assumptions-audit/README.md, findings.json): Regenerate overview section 3 and rewrite section 2.6 (stale Earth numbers, wrong CO2 text); fix decisions.md:33 and README's biome line.

## Updates
- 2026-10-31: Done (lane 88, docs). Overview §3 regenerated on 2026-10-31 from `tools/earth_check.py --level 6`, `overturning_report.py --earth`, `coast_check.py` and `veg_check.py` (on a scratch Earth world from `earth_world.py`), `tools/scorecard.py --seeds 1 2 --myr 1000`, and the pytest count (854 tests, 838 not slow); the stale glacial time-zoom depth table (deleted worlds, old physics) and the "every number checked" header claim are gone. §2.6's global-temperature paragraph is rewritten from earth.py (REF_FREEZE and the frozen references, the tanh CO2_MAX, the CO2 stock and CO2_TAU, the source and sink laws, the ice albedo, other greenhouse gases, the star). decisions.md's "saturating law" row is marked superseded by PW-576 C. README's biome line now says worlds group the vegetation types and only the zoom uses the Whittaker lookup; README's and overview's stale waves-and-tides claims were corrected (the tool no longer scores them: inbox draft draft-waves-tides-check-tool). Cell-size convention not done: inbox draft draft-cell-size-convention.
- 2026-10-25: Owner: fix the model's river discharge (via PW-821), not only the docs; the docs regenerate after.
- 2026-10-24: Created.
