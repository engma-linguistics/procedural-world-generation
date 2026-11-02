---
id: PW-1347
title: Congo basin loses its low cloud under the land stratus stability gate (sky 60% vs 70-80, sunshine 0.57 vs CRU 0.45)
type: task
status: todo
parent: null
milestone: v2
subsystem: climate
effort: m
impact: low
found_by: lane126
blocked_by: []
relates: [PW-1334, PW-232, PW-228]
refs: ["planet/climate.py::_layer_gate", "planet/climate.py::clouds", "planet/climate.py::_season_inputs", "tools/earth_check.py::CLOUD_REGIONS", docs/review/base-climate/tropical-cloud/round1.md, docs/review/base-climate/tropical-cloud/screen.py, docs/review/base-climate/tropical-cloud/ec.sh, data/earth/clouds_L7.npz, "Klein & Hartmann 1993 (J. Climate 6:1587)", "Eastman & Warren 2014 (J. Climate 27:2386)"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: after lane 126's fix for the tropics' too-thick cloud, Earth's Congo basin is now too sunny. Its cloud
falls from 71% to 60% (earth_check range 70-80) and its sunshine rises to 0.57 against CRU's 0.45.

Why: the land's humidity layer cloud (`cloud_rh`) now needs stable air (`_layer_gate`: the air aloft `t_ref` less the
surface air, from -2 C, full at +4 C). Over the Congo the model's air is as warm as the air aloft, so the gate keeps
under half the layer. The real Congo / Gabon dry season (JJA) is known for a deck of low stratiform cloud. Its likely
source is cool, stable air from the SE Atlantic, but I did not read a source for that. The model's `t_ref` in the deep
tropics is the warmest sea's (weak-gradient), so it can't see a cool-season inversion over the Congo.

Try: read a source on the Congo / southern West Africa low cloud (e.g. the DACCIWA work) first. Then either a cool-sea
inversion that reaches over the coast (as `cloud_coast` drifts the Sc deck), or let the gate use the upwind sea's
stability. Check the Congo and Amazon rows and the three warm rain bands in round1.md's screen.
- [ ] Congo sky in 70-80% and the warm-land shade bands still within ~0.05 of observed

## Updates
- 2026-11-02: Created from inbox draft draft-congo-low-cloud-under-stability-gate.md (found by lane126).
