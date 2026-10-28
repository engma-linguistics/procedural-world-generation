---
id: PW-821
title: "Model Earth too wet in the subtropics (B climates 20% vs 30%, hot desert 3-5%): add hot-desert and B share to earth_check; declare it a v1 limitation or pull PW-228's dryness part into v1"
type: task
status: blocked
parent: PW-470
milestone: v2
subsystem: climate
effort: s
impact: med
found_by: assumptions-audit
blocked_by: [PW-015]
relates: []
refs: []
created: 2026-10-24
updated: 2026-10-28
---

## Description
From the pre-v1 assumptions audit (docs/review/assumptions-audit/README.md, findings.json): Model Earth too wet in the subtropics (B climates 20% vs 30%, hot desert 3-5%): add hot-desert and B share to earth_check; declare it a v1 limitation or pull PW-228's dryness part into v1.

## Updates
- 2026-10-28: Status todo -> blocked. Paired 2-roll L6 set (36 per arm, new bar): rain fix 24/36 vs main 29/36 finish-moment passes, icebox 7 vs 7, no hellhouse; Earth log-rain corr 0.637 vs 0.648, Tibet drier. No gain, so not merged. Kept on branch worktree-agent-a27927a0e29b0cbdf for the record; fold into PW-015 (ocean evaporation, the root cause, v2).
- 2026-10-25: Owner 2026-10-25: 'if they're broken, we fix em' - rivers (PW-816's 2-4x discharge) and land dryness get fixed in the model, without chasing forever; physics lane queue after the carbon work.
- 2026-10-25: Owner: don't chase it to the ends of the earth; model as best we can at our cell size and fix systems where we can. Coordinator: one bounded v1 attempt on the shared root (land evaporation/runoff, also behind PW-816's 2-4x rivers), then document the limit.
- 2026-10-24: Created.
