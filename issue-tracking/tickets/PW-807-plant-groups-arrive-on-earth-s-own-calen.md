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
refs: []
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
- 2026-10-24: Created.
