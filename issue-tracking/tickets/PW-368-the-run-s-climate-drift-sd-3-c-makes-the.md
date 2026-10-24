---
id: PW-368
title: The run's climate drift (sd 3 C) makes the deep cold eras; PW-240's decision to narrow it (~2 C) was never applied
type: task
status: todo
parent: PW-649
milestone: later
subsystem: climate
effort: xs
impact: low
found_by: icehouse-depth
blocked_by: []
relates: [PW-240, PW-364, PW-584]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, docs/review/audit/icehouse-depth.md]
created: 2026-10-16
updated: 2026-10-23
---

## Description
PW-364's decomposition of the global temperature (`earth.global_temperature`: drift + CO2 + ice albedo)
over the deep cold eras (docs/review/audit/icehouse-depth.md):
- L5 envelope world (seed 1 + PW-338's patch, pre-PW-364 code), 300-320 Myr: dT -4.3 = drift -4.7, CO2
  -0.7, ice albedo -0.5 (later -1.4 at 10.8% ice, levelling off as designed). CO2 rises as the ice covers
  the weathering land (-1.9 -> -0.2: the thermostat works).
- The ice albedo is never more than ~1.5 C beyond Earth's; CO2 is clipped at +-1.5 (+-4.5 C).
So the depth of a cold era is set by the drift's excursions (an OU process, sd `climate_drift` 3 C over
40 Myr: a -4.7 C excursion is a 1.6 sd event, seen every few hundred Myr), then by the geography's ice
response (PW-364: steep on continents over both poles). PW-240's coordinator decision (2026-10-15) was
"narrow the run's climate drift (~2 C sd) first"; PW-240 was then closed when the audit made runs barely
glaciate, and `Params.climate_drift` is still 3.0.

Options:
- A. Leave it: the drift stands in for the carbon cycle's missing pieces; deep icehouses on favourable
  geographies are the price of Earth-like variability (Phanerozoic global T ~11-36 C, range 25 C).
- B. `climate_drift` 3 -> 2 C, as decided on PW-240 (health --quick's dT range per run is 8-19 C now;
  not measured with 2 C): fewer -4 C dips, so fewer deep icehouses on polar-continent geographies.
- C. Make the drift's cold side answer the ice (e.g. weathering under a growing sheet already stops; the
  drift has no such feedback). A design change.
Lean: A for now (the cold eras' depth follows geography soundly after PW-364); B if the owner finds
-300..-500 m icehouses too frequent in the viewer. A tuned parameter, so the owner's call.

## Updates
- 2026-10-24: Lane v1-finish-6 measured option B at L6 (18 seed-draws, 300-1000 Myr): climate_drift 2 C leaves the icehouse median at 46% and raises the deep-ice share (17% of updates below -150 m vs 12%); the pass-count change (5 -> 9 of 18) is within draw noise. Not applied; see draft-icehouse-bar-late-trend-after-pw750.md.
- 2026-10-23: Filed under the quality-pass epic PW-649 (parent PW-649, milestone later): shipped and judged good enough, residual kept for a later cleanup pass.
- 2026-10-23: PW-597 triage (2026-10-23): kept. PW-584 (time-zoom drift spread at I = 0) does not cover this: it concerns the 20 kyr sea-level drift of the time zoom over plausible worlds and a test bound, while this ticket is the run's own climate drift (sd 3 C) that makes the deep cold eras. PW-584 added to relates.
- 2026-10-16: Parked per owner (v1 reassessment 2026-10-16); impact set low so board next stops offering it.
- 2026-10-16: Status needs-decision -> todo. Owner 2026-10-16: parked as a someday task (climate_drift stays 3 C).
- 2026-10-16: Coordinator: after PW-364 the deepest era is -219 m with no frame below -250 m, so lean A (leave climate_drift at 3 C) for now; tuned knob, so the owner's call. Revisit when looking at showcase runs.
- 2026-10-16: Created from inbox draft draft-climate-drift-drives-cold-eras.md (found by icehouse-depth).
