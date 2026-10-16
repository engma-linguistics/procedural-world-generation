# Physics audit (PW-245): coordinator's ranking

Five agents that didn't write the code audited one area each on 2026-10-15: [tectonics](tectonics.md), [surface and hydrology](surface-hydro.md), [climate and ocean](climate-ocean.md), [ice, time zoom and vegetation](ice-veg.md), [coast and zoom synthesis](coast-zoom.md). Each report has the full findings and an appendix inventory of every clamp, cap, fudge and constant (~285 items in all) with a verdict.

Grading follows the owner's calibration: this is a fun tool, so approximations are expected. A **sound approximation** is a recognised simplification with a physical basis, even if crude. A **bandaid** forces an answer, hides a process error, or only works on Earth. Fixes should be the simplest sound approximation, not a heavier model.

## The short answer
- **No Earth-, region- or latitude-keyed code acts on generated planets.** Earth-only branches (anchor, Eemian, observed fields) only touch the Earth source.
- **Conservation holds where checked:** the crust budget closes exactly; sediment volume per step to 4e-16; zoom water balance; salt; the time zoom's ice and sea-level budget to 1e-6.
- **Tests weren't loosened to pass.** Every widened bound has a stated physical reason or was a unit change.
- **There are a handful of genuine metric-chasing bandaids** (tier A), each traced to a commit that picked a value for a score. There are also several unsound approximations or bugs that shape outputs (tier B). Most of the inventory (~190 of ~285) was judged sound.

The coordinator spot-checked the tier A history claims (d909b83, 4f11406, 1571042, earth.py's sea-level reference). All four are as reported.

## Tier A: bandaids that hit a metric for the wrong reason
| Ticket | What | Evidence | Decision? |
|---|---|---|---|
| PW-288 | Sea level is measured against a reference that relearns the ocean's depth over ≤300 Myr, so a persistently young ocean (plates too fast, ~6–6.6 vs Earth ~4–5 cm/yr) never floods the continents. | L6 seed 21: +200..+370 m from a fixed reference vs −99..+184 m shown; false lowstands too. Ties to PW-051. | needs-decision (lean: fixed reference + look at plate speeds) |
| PW-265 | Overturning heat is a net source: `moc_zonal = 0` adds the inflow's warmth on top of `t_eq`, which was already fitted to Earth's sea including overturning. | d909b83 chose 0 because Köppen scored 70.69% vs 70.50%. +0.52 °C ocean mean, +0.98 °C poleward of 45°. | needs-decision (lean: `moc_zonal = 1`) |
| PW-272 | Wind recovery off land doubled 600 → 1200 km to fit the enclosed-sea rows of coast_check; the real process recovers in tens of km, and it weakens open-ocean waves near land too. | 4f11406. | needs-decision (lean: ~50 km after fixing PW-270) |
| PW-284 | Flexural moat share 0.15 picked on one L7 seed's closed-basin count; only the moat half of the flexure is applied (volume not conserved). | 1571042. Relates PW-054/243. | needs-decision (lean: full flexure, width the only knob) |
| PW-286 | Rifted-margin thickness is steered by the global continental-area error (a controller, not a process). | crust.py:307. Relates PW-046. | — |
| PW-278 | `WEATHER_K` raised in PW-235 to shorten cold eras; its runoff term counts rain that is already in the erosion rate it multiplies. | Clean value 0.09 vs 0.12. | xs |

Already-known bandaids that the audits confirmed are bandaids: the 10 °C ice-surface cooling (PW-112, and PW-277's two ice climates), the time zoom's `LOCAL` snow-damping floor (PW-275, PW-240), and vegetation `GRAZE` (PW-207).

## Tier B: unsound approximations or bugs that shape outputs
| Ticket | What | Likely effect |
|---|---|---|
| PW-282 | The run's hillslope term is one-sided relief × 4κ/d²: it doubles per grid level instead of being level-consistent. | Probably part of PW-243 (L7 has 2× L6's closed basins). |
| PW-276 | Run ice uses a Nye profile stacked on each cell's own bed, so caps on high ranges reach 9 km surfaces. | Cause of PW-226's −105..−111 °C. |
| PW-266 | The rain kernel recycles 41% of land rain, but the water balance evaporates 60%; the gap is quietly taken off in `ocean.freshwater`. | Likely part of PW-026/228 (dry interiors). |
| PW-280 | Closed lakes keep their rivers' entire sediment load with no room cap, piling it up to 1.2 km above the lake surface. | Closed-basin shapes; 2% of all deposition. |
| PW-269 | Delta plain radius is 3–5× below its own docstring's calibration. | Cause of PW-061's small zoom deltas. |
| PW-270 | The wave gust factor (derived for power ∝ U⁵) is applied to U. | Fetch- and duration-limited seas 1.5–1.6× too strong (PW-074/075). |
| PW-268 | Zooms don't keep their coarse cell means: valley carving lowers land 60–90 m and trenches lose ~3 km. | Most of the zoom's 516 m error. |
| PW-275 | A new ice cap starts under a stricter rule in the run than in the time zoom. | Part of the time zoom drifting icier than its run (PW-240). |

## Tier C: small and low (mostly xs)
PW-264 (CO2 thermostat compares rates, not a stock; needs-decision), PW-267, PW-271, PW-273, PW-274, PW-277, PW-279 (needs-decision), PW-281 (needs-decision), PW-283 (missing sediment-budget test), PW-285, PW-287.

## Suggested fix order
Several fixes move the same KPIs (sea level, land %, temperature, closed basins), so fix the processes first and retune after. Re-run `tools/health.py` and the scorecard after each batch.
1. **Bugs and xs with no judgement call:** PW-269, PW-274, PW-267, PW-283, PW-285, PW-287, PW-271, PW-273.
2. **Conservation and level consistency:** PW-265, PW-266, PW-280, PW-282 (then re-measure PW-243 and PW-054).
3. **Ice:** PW-276, PW-275, PW-277 (then PW-240 and PW-226).
4. **Tectonics:** PW-288 together with a look at plate speeds, then PW-284 and PW-286 (then PW-046 and PW-051).
5. **Waves:** PW-270, then PW-272.
