---
id: PW-163
title: "Clouds on temperature (PW-143 phase 2): replace evap_cool with cloud shading, or leave clouds diagnostic?"
type: task
status: done
parent: PW-013
subsystem: climate
effort: m
impact: low
found_by: clouds
blocked_by: []
relates: [PW-143]
refs: [planet/climate.py, tools/earth_check.py, "world dc3732"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-143 phase 1 added a diagnostic cloud cover (climate.clouds; cloud_jul/jan, sunshine_jul/jan
on worlds). Phase 2 would let clouds feed back on temperature: they shade by day and keep the
night warm, so cloudy places get a smaller seasonal range and less summer heat, and snow/ice
melt less under cloud. Tested offline on Earth (L6, Koppen group agreement now 70.69%, warm-month
MAE 2.49 C, cold-month MAE 3.42 C over land outside Antarctica):

- Stacked on today's temperatures, a land term t_warm -= a (cloud_summer - c_ref),
  t_cold += b (cloud_winter - c_ref): every setting made both errors worse
  (a=4,b=4,c_ref=0.5: 70.51%, MAE 2.63 / 3.67; a=6,b=6: 69.91%, 2.79 / 3.87). The model's
  temperatures were tuned on Earth with clouds implicit in them, and `evap_cool` (rainy summers
  1.5 C cooler, dry ones hotter) already does much of the same job through the rain.
- Replacing evap_cool's summer term with a cloud term is neutral: a=4, c_ref=0.4 gives 70.63%,
  MAE 2.52 / 3.42; a=4, b=2, c_ref=0.45 gives 70.86% but cold MAE 3.50.

Options:
- A: leave clouds diagnostic (now). No change to temperatures, Koppen or goldens.
- B: swap evap_cool for cloud shading (a ~4 C per unit of cloud above ~0.4 in summer, maybe a
  small winter term). Neutral on Earth, but more physical on other worlds: a dry but overcast
  coast (a stratocumulus coast) would stay cool, which evap_cool can't do. Needs the rain kernel's
  evap tcor (the rain kernel also feels evap_cool) to stay as is or move with it.
- C: a proper surface energy balance (shortwave under cloud, longwave back-radiation) for the
  seasonal swing and for ice-sheet melt (earth.ice_sheets, timezoom), with a retune of
  `continental`, `evap_cool` and the ice terms. Largest, and the only one likely to improve Earth.

Lean: A now; B only if generated worlds show cloudy coasts that are too hot in summer.

## Updates
- 2026-10-14: Status needs-decision -> done. Owner decision: keep clouds display-only for now; revisit with the PW-013 rain/ocean retune.
- 2026-10-14: Created from inbox draft draft-cloud-temperature-feedback.md (found by clouds).
