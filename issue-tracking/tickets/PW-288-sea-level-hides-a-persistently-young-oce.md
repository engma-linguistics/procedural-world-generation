---
id: PW-288
title: "Sea level hides a persistently young ocean: the basin term is measured against a baseline that learns it away"
type: task
status: done
parent: PW-245
milestone: v1
subsystem: tectonics
effort: s
impact: high
found_by: audit-tectonics
blocked_by: []
relates: [PW-051, PW-053]
refs: [planet/tectonics/earth.py, planet/tectonics/isostasy.py, docs/review/audit/tectonics.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`earth.global_temperature` sets the ocean-basin part of sea level as
`SEA_TECT_MAX x tanh(0.5 x (depth_ridge - depth_ref) / SEA_TECT_MAX)`.
`depth_ridge` is the mean sea-floor depth smoothed over `ridge_time`
(30 Myr, fine). `depth_ref` is a baseline that *learns* `depth_ridge`
over min(300, 10 + t) Myr. Three parts of this:

1. **The learning baseline is a bandaid.** A lasting change in basin
   volume (an ocean that stays old for 200 Myr, PW-051; a long fast-ridge
   era) is learned away: sea level drifts back to 0 while the floor stays
   as deep as it was. Physically, sea level follows the basins' volume
   against a fixed reference (the starting ocean, which setup already
   makes a steady-state one with mean age 60 Myr, PW-053). The baseline
   was added "so only real changes in spreading move the sea", but a lasting
   change *is* a real change. PW-051 reports the term sitting on its clip
   in stagnant few-plate phases, and the baseline is what eventually
   hides it.
2. **x0.5 for water loading should be ~0.69.** Extra water on the floor
   pushes it down by rho_w / (rho_m - rho_w) of its depth, so the sea
   rises by (rho_m - rho_w) / rho_m = 2.27 / 3.3 = 0.69 of the change in
   floor depth (before flooding the shelves widens the sea).
3. The tanh limit of +-250 m is a soft clamp. It is fine as a
   stability limiter if it rarely binds. With a fixed reference it would
   bind in old-ocean eras, which tells us something (PW-051).

Measured (audit probes, L6 seed 21 0-1000 Myr and L5 seed 1 0-400 Myr):
the model's ocean stays far younger than the steady-state ocean it starts
from (L6 mean age 40.6 Myr over the Gyr; start 55, Earth ~64; L5 40 Myr).
Against the fixed starting floor with x0.69, the basin term would be +200
to +370 m for nearly the whole Gyr at L6 (up to +557 m after the first
breakup). The model gives -99 to +184 m (mean +13). The baseline also
makes spurious lowstands: at L5 t=204 Myr the floor's mean age equals the
start's (61 Myr), yet sea_tect is -116 m. So the stable sea level and land
share are partly held by this term cancelling the young ocean. The likely
process cause is fast spreading (mean cell speed 6.0-6.6 cm/yr vs Earth
~4-5). Seeds differ (scorecard L6 seeds 1/2 end at 95/63 Myr); on an
old-ocean seed the baseline hides a lowstand instead. The mean floor depth
ranges ~1000 m over each run. (Its depth law,
half-space cooling to a 6400 m floor at 119 Myr, is a sound
approximation of plate-model flattening and consistent with the 35 km /
+250 m continental datum. It is ~0.5-0.8 km deeper than GDH1 at 100-150
Myr, so it makes sea level ~30% more sensitive to ocean age than GDH1
would. Reported, not a fix.)

Options:
- (A) Keep as is (it keeps sea level in a comfortable band; land share
  stays stable).
- (B) Fixed reference (the starting ocean's mean depth, as now at t=0),
  factor 0.69, tanh kept as a wide limiter (e.g. +-400 m). Expect the sea
  ~+300 m on runs like seed 21 and several points less land, until the
  young-ocean cause (plate speeds / spreading) is found and fixed. Old-ocean
  eras then lower the sea, as they should (PW-051).
- (C) Like B, but also take the flattening at ~5.6 km from GDH1
  (`5651 - 2473 e^-0.0278 t` beyond 20 Myr), with the continental datum
  rechecked so continents and old ocean stay in isostatic balance.
Lean B, landed together with a look at why the ocean is so young (plate
speeds, ridge lengths), so land share doesn't just drop. C only if B's
old-ocean lowstands look too deep.

## Updates
- 2026-10-15: Status in-progress -> done. Done in the tectonics fix branch (merged 4ce7706); see docs/review/audit/fixes-tectonics.md.
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Status needs-decision -> todo. Owner (2026-10-15): approved the lean.
- 2026-10-15: Created from inbox draft draft-audit-tectonics-sea-level-baseline.md (found by audit-tectonics).
