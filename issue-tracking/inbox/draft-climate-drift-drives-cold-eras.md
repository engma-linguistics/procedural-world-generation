---
title: "The run's climate drift (sd 3 C) makes the deep cold eras; PW-240's decision to narrow it (~2 C) was never applied"
type: task
status: needs-decision
parent: null
subsystem: climate
effort: xs
impact: med
found_by: icehouse-depth
blocked_by: []
relates: [PW-240, PW-364]
refs: [planet/tectonics/earth.py, planet/tectonics/params.py, docs/review/audit/icehouse-depth.md]
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
