---
id: PW-464
title: "Run ice as the cycle's time mean: the mean of each cycle state's own extent (orbit x the cycle's global swing), with only the persistent ice carried between steps"
type: task
status: todo
parent: PW-470
milestone: v2
subsystem: tectonics
effort: l
impact: high
found_by: pw462
blocked_by: []
relates: [PW-462, PW-461, PW-460, PW-459, PW-436, PW-452, PW-104]
refs: [planet/tectonics/earth.py, planet/icemass.py, planet/timezoom/forcing.py, docs/review/audit/ice-framing-deep-dive.md]
created: 2026-10-20
updated: 2026-10-23
---

## Description
Today `earth.ice_sheets` returns *one* fixed point under the balance averaged over 8 orbital states
(`icemass.cycle_dq`), carried from the old ice. Measured (PW-462 deep dive, section 2), that is an edge of the
cycle, not its mean: on main's L5 consistency moment (seed 1 @ 300, -4 C) the run's ice is -19 m, each orbital
state's own equilibrium -21..-230 m (mean -83 m), and the default forced zoom's time mean -87 m (total), with
the run at the zoom's interglacial maximum. Averaging the *balance* lets a cell keep ice only if it survives
the warmest states too, so the run holds roughly the interglacial extent. On deep moments the opposite edge
shows (seed 2 @ 580: the zoom only loses ice, PW-436). On a deep moment (L6 seed 11 @ 400 in memory,
-252 m) the 8 states agree with the run within 13 m, so this rule changes nothing there; that gap is the
budget's (draft-run-ice-marine-budget.md). On Earth (L6, dT 0) the rule gives -58.8 m (about today's real
ice, right for an interglacial) and the orbit-only states average only -67.8 m, against a Pleistocene mean
of ~-115 m: the states need the cycle's global swing (item 1) to give Earth its glacials.

Proposal (PW-461 option B(1), extended):
1. **States.** The cycle's states are the orbit's (cycle_dq, per hemisphere) *and* the cycle's global swing:
   with honest orbital sensitivity (PW-459's ~0.08 C per W/m2) the orbit alone barely moves the extent
   (branch 246ef40: all 8 states within -340..-371 m on the same moment), because real glacial cycles are the
   feedbacks' (CO2, ice albedo) paced by the orbit. So each state also carries a global offset dT_s from the
   time zoom's own rules: CO2 `co2_cool` per 120 m of the state's extra ice (clipped as `Forcing`) plus the
   albedo change of its extra area, solved with the state's extent (2-3 iterations), around the step's mean dT.
2. **Extent per state, no memory between states:** each state's fixed point (the existing passes, one
   climate_step per pass instead of 8: about the same cost as today's averaged pass), seeded from the
   *persistent* ice below, so a state can't keep ice only because another state grew it.
3. **Persistent ice** = the warmest state's extent (per hemisphere: precession is anti-phased), carried as the
   old ice into the next climate step. Only ice that survives an interglacial keeps the run's hysteresis
   (Antarctica through 34 Myr is real); the glacial sheets are rebuilt each step.
4. **Stored ice** = the time mean thickness over the states (weights: the share of time the orbit spends near
   each, or uniform), plus `ice_ig` (persistent) and `ice_glacial` (coldest state) per keyframe for the
   viewer, the time zoom's interglacial footprint and the phase picker. Sea level from the mean volume; the
   ice albedo from the time-mean iced *area* (not the union); the weathering mask weighted by each cell's iced
   share of time.
5. Then re-apply PW-460's margin and PW-459's seasonal k (branch 246ef40) on top, together with the marine
   budget (draft-run-ice-marine-budget.md), and run the 10-seed cold-era check and the tz_mean table.

Risks, honestly: (a) a state's equilibrium assumes the sheet reaches it, but sheets take ~50-100 kyr to grow
and a precession half-cycle is ~11 kyr; on the one moment measured the mean of the equilibria matched the
zoom's mean within 4 m, but that may be luck (the zoom's own CO2/albedo feedbacks add ice). If it doesn't hold
on the L6 moments, weight the cold states by a growth-time factor measured against the zoom (one number, tested
by draft-tz-mean-matches-run-check.md), or fall back to option B(3). (b) On main this makes moderately cold
moments *icier* (-19 -> ~-85 m on the L5 moment), so the 10-seed bars may get worse before PW-460/459 and the
marine budget rebalance them; the bars become cycle means (draft-cold-era-bars-as-cycle-mean.md).
- [ ] tz_mean: |zoom mean - run| <= max(15 m, 0.25 x swing) on >= 4 of 5 moments
- [ ] 10-seed cold-era check >= 7/10 with the bars as cycle means
- [ ] cost of a climate update's ice <= 2x today's

## Updates
- 2026-10-23: Milestone v1 -> v2 (owner approved shrinking v1 to its real gates, 2026-10-24; docs/review/board/triage-2026-10-24.md).
- 2026-10-20: Created from inbox draft draft-run-ice-cycle-mean.md (found by pw462).
