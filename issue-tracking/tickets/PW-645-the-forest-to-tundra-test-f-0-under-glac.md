---
id: PW-645
title: "The forest-to-tundra test (F < 0 under glacial cooling) holds on snowy worlds but not warm ones: main's own null draws give 16 of 24 on seeds 1-24 (bar 17), so A20's 12 and main's 20 are the spread's tails, not a physics signal"
type: task
status: todo
parent: PW-470
milestone: v1
subsystem: timezoom
effort: s
impact: high
found_by: base-climate-laneA21
blocked_by: []
relates: [PW-640, PW-643, PW-450, PW-592]
refs: [tests/test_timezoom.py, tests/seeds.py, docs/review/base-climate/laneA21/, docs/review/base-climate/stages.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
Lane A21 (`docs/review/base-climate/stages.md`, lane A21) asked why A20's shelf-air worlds failed
`test_glacial_cooling_turns_forest_to_tundra_and_cools_further` on 12 of 24 seeds, where main fails 4.

**It is the lottery, not the rule.** The forest test over many draws (bar 17 of 24):

| draw | main | A20 |
|---|---|---|
| seeds 1-24 | 20 | 12 |
| seeds 1-24, `climate_offset` +0.001 C (a null perturbation) | 16 | 16 |
| seeds 1-24, +0.002 / -0.001 C | 16 / 16 | |
| seeds 25-72 | 35 / 48 | 35 / 48 |

- Pooled over 240 worlds, the mean F is the same on both trees: -0.054 / -0.053 W/m2.
- Main's true pass rate is ~72%, so a 70% bar on 24 seeds is red on main itself in 3 of 4 draws.
- The endings test passes its bar on every draw (18-20 of 24).

**Why the premise is planet-dependent.** F sums two parts:
- the boreal forest's loss over lying snow (negative: -0.19 W/m2 on passing worlds, -0.09 on failing ones);
- a darkening below 40 deg on every world, about +0.13 W/m2. Trees and grass gain ground under -4 C and the lower
  CO2 index (see `draft-cooling-greens-the-low-latitudes.md`).

Warm worlds have little snow, and some worlds have little high-latitude land. On both, the second part wins. Pass
rate by the start's snow cover on open land:
- below 0.09: 15 / 50;
- 0.09-0.12: 42 / 71;
- 0.12-0.15: 59 / 67;
- above 0.15: 50 / 52.

By run dT: below +5 C, 144 / 172; above +5 C, 22 / 68. Earth passes easily: F -0.19 at L4 and -0.24 at L6,
snow 0.16.

**Options (owner):**
- A: keep the assertion. Make eligibility a rule on the world: snowy worlds (the start's snow cover on open land
  >= ~0.12, or run dT <= +5). On those worlds the premise is physics: about 90-96% pass. This adds a precondition
  and a new number.
- B: keep every world and set the bar from main's measured spread, at ~50-60% on 24, or use 48 seeds. PW-643's own
  lean is 50%.
- C: run the test on Earth's source (`timezoom.source_earth`) as the anchor, plus the multi-seed rate as a
  regression net.
- Lean: A, or C plus B. Either way, PW-640 (A20) is no longer a physics hold.
- [ ] A / B / C

## Updates
- 2026-10-23: Status needs-decision -> todo. Owner 2026-10-24: option A, eligibility by a rule on the world (rules needn't fire where their prerequisites aren't there).
- 2026-10-23: Created from inbox draft draft-forest-test-premise-is-planet-dependent.md (found by base-climate-laneA21).
