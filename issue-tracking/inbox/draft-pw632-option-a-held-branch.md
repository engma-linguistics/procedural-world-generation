---
title: "PW-632 option A measured: on the failing cold worlds the glacial's leftover ice is partly a held branch at I = 0 (seed 8 on step 2 keeps 51% for 120 kyr), so no faster-melting rule can meet the endings bar; only the marine fronts' loss moves it"
type: task
status: needs-decision
parent: PW-470
milestone: v1
subsystem: timezoom
effort: m
impact: high
found_by: base-climate-laneA19
blocked_by: []
relates: [PW-632, PW-627, PW-588, PW-385, PW-569, PW-623, PW-471]
refs: [docs/review/base-climate/laneA19/, docs/review/base-climate/stages.md, tests/test_timezoom_cycle.py]
---

## Description
Lane A19 worked PW-632 option A (find the termination physics that cold worlds lack). Branch
`worktree-agent-a818192c7d6091881` (main b289b95 + A18's branch), files in `docs/review/base-climate/laneA19/`.
Nothing under `planet/` is committed. The endings test (L4, 300 Myr, seeds 1-9, as A18's scan) still fails on step 1
(this branch) seeds 7 and 8 (extra / left 131.7 / 88.5, 70.5 / 43.9 m) and on step 2 seeds 1 and 8 (30.9 / 18.4,
80.8 / 49.0 m).

**What holds the ice** (`diag.py`, `diag2.py`):
- 55-70% of the leftover extra is grounded marine ice on beds pushed 650-700 m down, 2.3-2.5 km thick; the rest is
  land ice above its equilibrium line. Its warm month is -12 to -17 C against +3 to +10 C bare (off run).
- Of that ~20 C, the extra height is 8-11 C (1.2-1.7 km of surface, already isostatically lowered). Taking out the
  full climate's answer to the sheets (B) or the ice surface's local terms (C) warms it 2-5 C, but the leftover's
  smb stays near 0 (marine +0.04 to +0.25 m/yr): the height alone holds it.

**Slow or held?** (`hold.py`: I kept at 0 after the first ending, 120 kyr):
- Warm worlds lose their extra in 10-20 kyr.
- The failing worlds keep 17% (seeds 1 step 2, 7 step 1), 27% (8 step 1) and 51% (8 step 2) for good. The rest
  decays with e-folding ~30-40 kyr; the bar needs < 22 kyr.
- Seed 8 on step 2 can't pass by any rule that only speeds the decay: half its extra is a second stable state at
  I = 0.
- On these worlds the index-off run is itself an ice age: mean sea level -27 to -66 m. The test cools the run's
  moment by 4 C, and on a cold world that puts I = 0 inside the sheets' hysteresis window. Abe-Ouchi et al. 2013 and
  Ganopolski & Calov 2011 show the same: an ending needs a climate outside the multiple-equilibria range.

**Candidates measured** (fails -> passes among the four failing cases, `levers*.txt`, `sun1.txt`, `frontmelt1.txt`):

| candidate | passes |
|---|---|
| isostatic lag (`iso_tau` 1) | 1 |
| no shelves (`shelf_warm` -30) | 0 |
| no buttressing | 0 |
| sheet air from frozen summers (`sheet_air=cold`) | 0 |
| `surface_air=fetch` | 2 |
| `margin=ramp` | 2 |
| `front=ramp` | 0 |
| climate every 2.5 kyr (the blend's lag) | 1 |
| flow `enhancement` x2 | 0 |
| the orbit's sunshine change melting a melting surface directly (`sun_melt_probe.diff`, SUN_SURFACE 0.5, snow / ice albedo 0.75 / 0.45) | 1 |
| frontal melt by the sea's annual water above freezing (`front_melt_probe.diff`, 100-300 m/yr per C) | 1 (cold worlds' fronts sit in water at freezing) |
| proglacial lakes, glacial dust | already tried under PW-030, moved nothing |

Only two levers clear the held branch in `hold.py`, and both are calibrated constants:
- `calving` x4 passes 3 of 4 (seed 7 step 1 117 / 65) and leaves 0-8% held, but it costs Earth ~20 m of glacial
  (maxima -56..-74 m against -79..-98).
- `summer_damp` 0 passes 3 of 4 and leaves 2-22% held. This is PW-569's cold-surface question.

So the one physical lever with traction is the marine fronts' loss. That points to PW-385: the model's ocean has no
subsurface warm water, so a cold world's fronts feel no ocean warming at an ending. See the companion draft on
frontal melt.

**Options:**
- A2: build PW-385's subsurface water and a frontal melt at grounded marine fronts (ocean + timezoom, m-l), and
  re-test with this bar.
  - Uncertain: it must clear 51% held on seed 8 step 2 without moving Earth's dT-0 yardstick.
- B: PW-632's option B. The endings test's source is chosen by a rule that isn't its outcome (the coordinator's
  PW-623 idea: the run's moment nearest its own median dT, or an I = 0 that isn't itself an ice age). Owner's call;
  it unblocks PW-627's step 2.
- C: accept that on a planet whose interglacial is an ice age, a glacial's extra ice need not go in 15 kyr. That
  needs the test's set-up changed, which is B.
- Lean: B now, with A2 as the physics follow-up under PW-385, using this seed scan as its bar. No change to the test's
  assertions in either.
- [ ] owner picks A2 / B / C
