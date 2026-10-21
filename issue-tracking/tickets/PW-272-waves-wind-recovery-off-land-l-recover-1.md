---
id: PW-272
title: "Waves: wind recovery off land (L_RECOVER 1200 km) was doubled to fit the enclosed-sea rows"
type: task
status: done
parent: PW-245
milestone: v1
subsystem: coast
effort: s
impact: med
found_by: audit-coast-zoom
blocked_by: []
relates: [PW-075, PW-074]
refs: [planet/coast.py, tools/coast_check.py, docs/review/audit/coast-zoom.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`coast.py:129` `LAND_SLOW, L_RECOVER = 0.5, 1200.0`. Commit 4f11406 raised L_RECOVER from 600 to 1200 km, and
its only justification is coast_check (Gulf of Lion 16.8 -> ~10, Baltic 12.8 -> ~8.5, waves within 2x 26 -> 28).
The process it stands for, the marine internal boundary layer, brings an offshore wind up to speed within
~10-50 km. At 1200 km the wind is still ~30% slow 600 km off any upwind coast, so power drops over much of
every ocean near land, not only in enclosed seas. U_TRADE/U_STORM weren't refitted, and enclosed seas are
still ~2x high, so the real cause is elsewhere (see the gust-moment draft).

Options:
A. Set L_RECOVER to ~50 km and LAND_SLOW to ~0.3 (physical), fix the gust moment first, then refit U_TRADE/U_STORM
   once on the open-ocean rows of coast_check. Enclosed seas may then need a real fetch effect, not this knob.
B. Keep 1200 km as an explicit "enclosed-sea" fit constant and document it as such.
Lean: A. It's a bandaid, and it acts far outside the seas it was tuned for.

## Updates
- 2026-10-15: Status in-progress -> done. Done in the coast-zoom fix branch (merged d4e7c90); docs/review/audit/fixes-coast-zoom.md.
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Status needs-decision -> todo. Owner (2026-10-15): approved the lean.
- 2026-10-15: Created from inbox draft draft-audit-coast-zoom-land-wind-recovery.md (found by audit-coast-zoom).
