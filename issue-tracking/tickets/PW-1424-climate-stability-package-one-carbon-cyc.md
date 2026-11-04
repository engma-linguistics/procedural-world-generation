---
id: PW-1424
title: "Climate stability package: one carbon-cycle yardstick per grid level instead of each planet's dice roll, weathering on plant cover"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: climate
effort: m
impact: high
found_by: lane158
blocked_by: []
relates: [PW-1403, PW-1404, PW-1332, PW-1261, PW-994]
refs: [docs/review/climate/stability/round1.md, docs/review/climate/stability/tools/pin.py, docs/review/climate/stability/tools/pin_read.py, docs/review/climate/stability/tools/yard.py, docs/review/climate/stability/tools/decomp.py, docs/review/climate/stability/tools/share.py, docs/review/climate/stability/tools/probe.py, docs/review/base-climate/fork-judge/round1.md, "planet/tectonics/earth.py::global_temperature", "planet/tectonics/earth.py::plant_factor", "planet/tectonics/earth.py::REF_FREEZE", docs/review/base-climate/v1-finish-16/paired_fork.sh]
created: 2026-11-03
updated: 2026-11-03
---

## Description
**In plain words.** Each planet learns its "normal" volcanic CO2 output and its normal rock weathering in its first
300 Myr and keeps them as its yardstick. That yardstick is a dice roll: it varies about as much between re-runs of
one planet (sd 0.16) as between different planets (0.18). Each 0.1 of it moves the planet's whole later climate by
1.1 C. It is most of why re-runs of one planet disagree (2.0 C sd of the 600-1000 Myr mean on lane 140's 36 runs).
The thermostat itself is Earth-strength and quick, and nothing locks in when a planet is pushed
(round1 sections 1 and 4).

First check (round1 section 5): three of main's coldest test planets, continued from their 300-Myr states with the
yardstick pinned to the mean, ended +2.9 to +5.4 C warmer than their three unpinned histories. The forecast was
+2.8 to +5.1 C. Their worst hard-window land ice fell from 16-43% to 3-27%.

Baseline: main = lane 140's frozen main 4abc1707; comparisons are the same planet re-run.

Options:
- **A. One yardstick per grid level.** After the spin-up, set sink reference = source reference x exp(-Y_level). Y
  is the reference ensemble's mean y (1.316 at L6), re-fit by a probe tool whenever a change moves the
  weathering's or outgassing's size. Forecast on the 36 runs: late-climate sd across all runs 2.64 -> 1.32 C; between
  re-runs of one planet 2.0 -> 0.9 C; worst hard-window land ice 33.5 -> 26.6%. Makes the forked judge (PW-1403)
  unnecessary.
- **A + C.** As A, and at the same re-anchoring the weathering's plant factor reads plant cover, not NPP (PW-1332
  option B), so plant-growth fixes stop moving the climate by 3-5 C.
- **D. Strengthen the thermostat.** Not recommended. It is already between the classic models and the best current
  estimate for Earth (Krissansen-Totton & Catling 2017).
- **Leave as is.** Every judge keeps reading the yardstick's dice roll.

Lean: A + C, after the confirming experiment: pin.py on all 36 judge draws (two continuations each from the
300-Myr fork states). Pass if the between-re-run late dT sd falls to <= 1.2 C and the cold six's peak ice falls by
about the forecast.
- [ ] Daniel's choice
- [ ] confirming experiment (round1 section 7)

## Updates
- 2026-11-03: Lane 158 lean: yes (A + C). Confirming experiment (pin.py on all 36 draws x2) started as lane 160 before Daniel decides.
- 2026-11-03: Created from inbox draft draft-climate-yardstick-one-constant.md (found by lane158).
