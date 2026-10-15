---
id: PW-284
title: "Flexural moat: a 15% share tuned on one L7 seed's closed-basin count, and only the moat half of flexure applied"
type: task
status: in-progress
parent: PW-245
subsystem: tectonics
effort: s
impact: med
found_by: audit-tectonics
blocked_by: []
relates: [PW-054, PW-242]
refs: [planet/tectonics/isostasy.py, planet/tectonics/params.py, docs/review/audit/tectonics.md]
created: 2026-10-15
updated: 2026-10-15
---

## Description
`isostasy.subsidence` (PW-054) takes the Airy root of thickened continent
(850 m per km beyond 35 km), blurs it over FLEX_KM = 150 km, and lowers the
continent wherever the blurred root is deeper than its own by
`flexure` x the difference (smoothly capped at MOAT_MAX = 2.5 km). Two
things make this a bandaid rather than an approximation of flexure:

1. **The share is a KPI knob.** Treated as flexure, the blurred root *is*
   the deflection, so the physical share is ~1. 0.15 has no physical
   derivation. Commit 1571042 picked it to hit a closed-basin share on a
   single L7 seed (3199): "inland drainage of arid land 35% -> 46%, 65% at
   0.3". The overview says the same: "0.15 was chosen so L7 doesn't
   overshoot: 0.3 gave 48%".
2. **Half the process.** Flexure moves the compensation sideways. The
   moat sinks *and* the belt stands higher by the same volume. Only the
   moat is applied ("the belts keep their Airy height"), so each moat is
   an extra, uncompensated depression. It is small globally (audit runs:
   mean -25 to -35 m over continental crust, about 0.4 points of land at
   L5/L6), but locally it is what makes the basins.

A full share would sink moats by up to the 2.5 km tanh cap and swamp L7.
That suggests the full flexure isn't what's missing; something else
(L7's finer drainage, sediment trapping) already makes L7 keep more
hollows than L6 (20% vs 9% before the moat). The 0.15 share hides that
level dependence instead of fixing it.

Options:
- (A) Keep it and document it honestly as a calibrated share
  (a "basin-making" knob), not as flexure.
- (B) Make it a sound approximation: use a share of 1, with FLEX_KM set
  from a realistic elastic thickness (alpha ~ 50-100 km for Te 20-40 km,
  i.e. a smaller blur), and apply both halves (deflection =
  smooth(root) - root everywhere, so the belt edges rise as much as the
  moats sink; total zero). Then recheck closed basins at L6 and L7 and,
  if L7 still overshoots, look for the level-dependent cause in
  hydrology/erosion rather than retuning the share.
- (C) Drop the moat and rely on thermal sag plus PW-242's back-arc and
  dynamic-topography basins.
Lean B: one formula, no tuned share. The blur width is the only
parameter, and it has a physical value.

## Updates
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Status needs-decision -> todo. Owner (2026-10-15): approved the lean.
- 2026-10-15: Created from inbox draft draft-audit-tectonics-flexure-share.md (found by audit-tectonics).
