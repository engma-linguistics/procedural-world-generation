---
id: PW-807
title: Plant groups arrive on Earth's own calendar counted back from the run's end ('now'), with per-seed spread and a latest deadline
type: task
status: todo
parent: PW-244
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: owner-2026-10-24
blocked_by: []
relates: [PW-636]
refs: [planet/vegetation.py, planet/tectonics/earth.py, planet/highlights.py, planet/make.py, tests/test_vegetation.py, docs/review/base-climate/star-anchor-audit/]
created: 2026-10-24
updated: 2026-10-24
---

## Description
Owner 2026-10-24: a run's end is 'now' (see PW-791). Plant groups should arrive at their real ages before present, counted back from the run's end, not compressed into the run (vegetation.GROUPS fractions x FLORA_PACE, PW-636). A 500 Myr run starts with fewer groups still to come. A group whose real age is near the run's start may already exist or arrive early. Each group gets a per-seed spread and a latest 'forced by' age.
Rough real ages (Ma): land pioneers/mosses ~470; vascular marsh ~430; forests without flowers ~385 (seed plants ~360, conifers ~300); flowering trees ~130 (dominant ~100); grasses ~70 (widespread ~55); C4 grasses ~30 (spread ~8). Note: C3 photosynthesis itself is billions of years old; what arrives in the Paleozoic is plants on land.
Consequences to handle:
- Runs longer than ~500 Myr have bare continents for their first part (different erosion and weathering, no coal before ~360 Ma). That's physically right, but the CO2 calibration must be re-checked.
- 'planet slice --at auto' currently picks a representative moment after the last group arrives. On the real calendar that is the last ~10-30 Myr. Any earlier slice has no grasses, so no cereals. Owner question: should showcase worlds be taken at the run's end / last few Myr?
Supersedes PW-636's compression.

## Updates
- 2026-10-24: v1-finish-10: plant groups on Earth's calendar (vegetation.GROUPS windows in Ma before now: 500-470, 440-420, 395-375, 140-120, 75-60, 35-25), FLORA_PACE and plants_from removed, bare land before the pioneers; skeletal reefs 545-520 Ma (earth.REEF_BUILDERS_MA), microbial carbonate before. --at auto is now the run's end or its latest interglacial-like frame of the last 12 Myr; slice --ago MA added. Coastal layers not yet on the calendar: draft-coastal-reefs-on-the-calendar.md. docs/review/base-climate/v1-finish-10/README.md
- 2026-10-24: Merged inbox draft draft-flora-calendar-co2-and-auto-slice.md ("Plant calendar (PW-807) consequences: bare-land spin-up against the CO2 reference freeze, and slice --at auto's flora gate leaving only the last ~10-30 Myr", found by star-anchor-audit).
  Audit items 6 and 7 (docs/review/base-climate/star-anchor-audit/README.md).
  
  The compression to remove: `FLORA_PACE` 0.8, the `GROUPS` fractions of ~470 Myr, and `group_windows`' deadline
  D = end - max(16 Myr, 5%) (planet/vegetation.py:222-286). Also `plants_from` 0, `FLORA_END` 1000, and
  test_vegetation's group_windows test.
  
  Knock-ons to measure:
  - **CO2.** A run longer than ~470 Myr gets bare continents first: the weathering `plants` factor is 1.0 against up to
    1.75, and bare ground erodes up to 1.6x faster. On runs over ~770 Myr the reference freezes at 300 Myr on bare
    land, and the plants' arrival is then a lasting weathering surplus (cooling). The direction is physical (the
    Devonian drawdown), but its size on top of the anchored star's dim start is unmeasured. Measure it with the star
    zero-point decision. PW-798 A's "freeze once the start has settled" may need "once land plants exist".
  - **`--at auto`.** `highlights.representative_time` restricts to frames after the last group. On the real calendar
    that is ~30-8 Ma, which leaves 2-7 keyframes. The geographic-typicality medians and PW-700's warm-moment-of-the-era
    pick then mostly degenerate to the last frame. Owner question already in PW-807. One option: gate on flowering
    trees (~100 Ma) or grasses (~55 Ma), not C4 grasses.
  - [ ] CO2 reference vs plant arrival measured on a 1 Gyr L6 run
  - [ ] --at auto rule decided and test_highlights updated
- 2026-10-24: Owner 2026-10-24: (1) Showcase/default worlds are taken at the run's end ('now') or its last few Myr: the default use is a world with modern plants and people. A deliberate earlier era (e.g. a dinosaur-age TTRPG) is asked for by age, ideally 'Ma before now' (e.g. slice --ago 70). (2) Marine algae appear in water >1 Ga before now (Natural History Museum); land plants 470-500 Ma. Long runs should reflect life in the sea before land: whatever the model ties to marine life (reefs, carbon burial, plankton) follows the real calendar too, e.g. reef builders ~540 Ma onward, microbial mats/stromatolites earlier.
- 2026-10-24: Created.
