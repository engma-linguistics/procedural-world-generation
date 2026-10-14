---
id: PW-015
title: Fix moisture transport in the rain model
type: story
status: todo
parent: PW-013
subsystem: climate
effort: l
impact: high
found_by: daniel
blocked_by: [PW-014]
relates: [PW-019]
refs: [planet/climate.py, tools/earth_check.py, tools/scorecard.py, "plan_next@bdc967f: Known issues → Climate"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Make the rain model carry vapour realistically between basins and inland, guided by the diagnosis.
Success: basin E−P contrast close to observed, and the regional misses that share this root improve.

Merged known issues (Earth on our climate):
- Sahel and East Africa too wet; Indian and Chinese monsoons too dry (from the v1 notes).
- River discharges miss because of rain: the Yangtze ends in a lake; the Lena, Mekong and Ganges are
  too small (dry China, Siberia, Indian monsoon); the Nile is 19× too big (wet Sahel). With observed
  rain, magnitudes are about right (`water`).
- The model's Ganges is ~3,700 m³/s against ~40,000, so no Earth delta comes out tide-dominated
  (`deltas`; morning decision 4).
- Also consider: rain doesn't see the overturning's ocean warming (one extra temperature pass, no rain
  recompute; morning decision 3b).

Check with `tools/earth_check.py` and the scorecard; don't chase parity.

## Updates
- 2026-10-14: Created from the rain/overturning epic. Merged: 'Older Earth errors' and 'Also noted: Earth climate errors' (v1), 'Discharge misses come from the rain model' (water), 'No Earth delta comes out tide-dominated' (deltas), morning decision 3(b).
