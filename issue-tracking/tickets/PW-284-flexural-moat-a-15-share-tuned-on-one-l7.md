---
id: PW-284
title: "Flexural moat: a 15% share tuned on one L7 seed's closed-basin count, and only the moat half of flexure applied"
type: task
status: todo
parent: PW-245
milestone: v1
subsystem: tectonics
effort: s
impact: med
found_by: audit-tectonics
blocked_by: []
relates: [PW-054, PW-242]
refs: [planet/tectonics/isostasy.py, planet/tectonics/params.py, docs/review/audit/tectonics.md, planet/tectonics/crust.py, planet/tectonics/plate_kernels.py, "run:a1d3b9@900Myr"]
created: 2026-10-15
updated: 2026-10-16
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
- 2026-10-16: Status in-progress -> todo. Spike source fixed (collision belts straddle the suture: spikes >15 km over neighbours 59 -> 10). Sound flexure (alpha 66 km, Te 30 km) not landed: cells are as wide as alpha, so one-cell loads are held up (27 km peaks). Options and patch on the ticket; the 0.15 share documented as calibrated.
- 2026-10-16: Tectonics night lane (2026-10-16): spike source fixed: stacked crust and crust flow now cross collision boundaries (crust.inner_edges); spikes > 15 km above their continental neighbours, L6 seed 1 0-400 Myr samples every 20 Myr: 59 (44 on a converging boundary, at ~78 km) -> 10 (none > 20 km); health peaks mean-of-maxima 8.53 -> 8.03 km. Sound flexure (share 1, both halves, volume kept, alpha from Te 30 km = 66 km) still NOT viable: on cells as wide as alpha (L6 120 km, L7 60 km) every one-cell load is held up by most of its root, not just collision spikes: a moat beside a lifted cell fills with up to 18 km of sediment (cover counts as crust), becomes a one-cell load and rises in turn (checkerboard instability): L6 seed 1 max elevation 27 km by 140 Myr, 792 spikes. Driving crust flow by the flexed height (gravitational collapse, stable explicit cap) did not stop it at the rate law's speed. Patch: docs/review/audit/tectonics-night/flexure-attempt.patch. Options: (A) a cell-averaged plate response (the deflection of a load spread uniformly over a cell, so the grid scale is mostly compensated; derivable but needs care per level); (B) keep the 0.15 moat as an honest calibrated share (done: params note); (C) drop the moat. Lean B for now, A as a later m-l task.
- 2026-10-16: Status todo -> in-progress. Tectonics run-lane agent started.
- 2026-10-16: Status in-progress -> todo. Basins lane 2026-10-16: moat off -> inland 6.4 -> 3.7% (raw), giant lakes 8.8 -> 6.1% (within noise). Sound two-sided flexure lifts single-cell crust spikes absurdly: needs those smoothed in crust.py first. Stays todo.
- 2026-10-16: Correction to the entry above: of the deepest giant-lake pits checked, one (seed 77 @180 Myr, -200 m in a frame) is a moat beside a single-cell spike; the others are a thinned, sediment-filled cell (seed 3199 @272) and plain 36-38 km cells (seeds 505 @424, 42 @456). Not all are moat pits.
- 2026-10-16: Basins-lakes lane: stopped, not landed. Steps 1-2 don't single the moat out for giant lakes: flexure=0 (diagnostic, 8 L6 seeds x 500 Myr) gives giant-lake frames 8.8 -> 6.1% (seed noise ~+-2.5 points), but inland drainage 6.4 -> 3.7% (raw ends on land), so the moat is what makes most L6 closed basins. Giant lakes' cells have median dyn -10..-30 m (rims ~0), and the deepest pits in them (200-800 m) are moats beside single-cell crust spikes (e.g. a 60 km / 5.5 km cell next to 38 km neighbours). Sound two-sided flexure (share 1, volume kept, alpha from Te) still needs the load fixed first: an elastic plate holds a load narrower than its flexural width almost fully, so the grid-scale spikes would rise by nearly their whole root (the 2026-10-15 attempt: 14-40 km). Within isostasy.py the only spike-safe forms are a yield cap or an extra load smoothing, both knobs. What's needed: option A of the 2026-10-15 update in crust.py (collision stacking spreads stacked crust over the belt across both plates; crust_flow crosses the suture-to-be / acts at the grid scale) so that no single cell carries >~5 km more crust than its belt; then share 1, both halves, FLEX_KM from Te ~20-40 km (alpha ~50-100 km), recheck peaks (PW-172), inland share at L6/L7, giant lakes.
- 2026-10-16: Status todo -> in-progress. Run-lane agent started (basins and giant lakes).
- 2026-10-15: Status in-progress -> todo. Not landed: full flexure needs grid-scale crust spikes smoothed first (merged update above); stays todo.
- 2026-10-15: Merged inbox draft draft-tect-flexure-needs-smooth-crust.md ("PW-284 lean B not landed: full two-sided flexure lifts grid-scale crust spikes to 14-40 km", found by audit-fix-tectonics).
  PW-284's approved lean (share 1, both halves of the flexure, volume kept,
  FLEX_KM the only knob) was implemented as `dyn += root - smooth(root, km)`
  (smooth rescaled so the sum is exactly zero, no MOAT_MAX cap) and tested.
  It is not viable on today's crust field, so the code still has the 0.15
  moat-only share.
  
  Why: collision belts carry single-cell crust spikes (80 km cells next to
  40-48 km ones, at the plate boundary where stacking lands). An elastic
  plate holds a load narrower than its flexural width up almost in full, so
  the bulge half lifts each spike by nearly its whole Airy root (up to 38 km).
  - Static, on a1d3b9's 900 Myr state (L7): uplift max 36 km (FLEX_KM 150),
    34 (75), 31 (50); 33-156 cells above 9.5 km; moats to -26..-28 km in
    oceanic holes inside belts. Land 33.3% -> 27.5% (150), 31.2% (75).
  - Dynamic replays (L7, 900-930 Myr): max elevation 14 km (150 and 75 km),
    10.4 km at 50 km (dyn +2-3 km on belt cells).
  - L6 seed 1, 0-300 Myr with FLEX_KM 150: mean max elevation 40 km, dyn
    -19..+32 km, land 34.2% -> 28.7%.
  So the physics is right but the load field isn't: nature never makes a
  55-110 km wide, 45 km thick excess column, because the crust flows or
  collapses first. In the model, crust_flow (thickness-driven, flux-limited
  at 0.15, and only inside one plate's continent) doesn't remove spikes that
  stacking rebuilds every step at the boundary.
  
  Options:
  - (A) Fix the load first: make collision stacking and crust flow keep the
    belt smooth at the grid scale (spread stacked crust across the boundary
    to both plates' belts; let flow cross the suture-to-be; or drive flow by
    the flexed elevation). Then land full flexure as approved.
  - (B) Keep the moat-only form but call it what it is: a calibrated
    basin-making share (the audit's option A).
  - (C) Two-sided flexure on a load smoothed at the flexural width (the
    plate responds only to belt-scale loads; grid-scale relief is carried
    locally). Spike-safe, volume-kept, but the extra smoothing has no
    physical derivation.
  Lean A (effort m), then B's honest docstring until it lands.
- 2026-10-15: Status todo -> in-progress. Fix agent started (owner approved leans, 2026-10-15).
- 2026-10-15: Status needs-decision -> todo. Owner (2026-10-15): approved the lean.
- 2026-10-15: Created from inbox draft draft-audit-tectonics-flexure-share.md (found by audit-tectonics).
