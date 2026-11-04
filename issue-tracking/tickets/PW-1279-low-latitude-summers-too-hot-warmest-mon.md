---
id: PW-1279
title: "Low-latitude summers too hot: warmest month 3-4 C above Earth's at the same annual mean"
type: task
status: done
parent: null
milestone: later
subsystem: climate
effort: m
impact: high
found_by: owner
blocked_by: []
relates: []
refs: []
created: 2026-11-01
updated: 2026-11-03
---

## Description
In plain words: the owner saw a hot July on world dba204 (Earth-like B finished, +0.3 C globally) and asked if it is aberrant. It is. Warmest-month mean on land against CRU (data/earth L7 obs_t_warm): 0-20 deg 30.5 vs 26.5 C at nearly the same annual mean (23.1 vs 23.7), 20-40 deg 28.5 vs 25.8 (annual 17.5 vs 16.9), 40-60 deg 15.8 vs 18.4 (annual -0.3 vs 3.0). Land with a warmest month at or above 30 C: 42% vs 14%; at or above 35 C: 19% vs 2%. So the seasonal swing over low-latitude land is about twice Earth's while mid-latitudes are cold. Part may be geography (dba204 has more tropical land), so check on Earth itself first (tools/earth_check.py warmest-month by latitude band), then diagnose: land heat capacity, soil moisture and evaporative cooling, cloud, monsoon. Diagnosis gate first.

## Updates
- 2026-11-03: Status needs-decision -> done. Scout 172 (docs/review/climate/summers/scout1.md): Earth analogue at L7 vs NCEP 1991-2020: warmest month 0-20 deg -1.6 C, 20-40 deg +0.4 C, 40-60 deg -0.1 C; land >=35 C 1.0% vs 1.9% observed (7.9% before PW-1326). Excess gone. Remaining SH 30-40 deg summer swing filed separately.
- 2026-11-03: Milestones 11-03: v2 -> later: physics side track, ranked 4; gates no tag (re-measure after PW-1326/1327 first)
- 2026-11-02: Status in-progress -> needs-decision. 11-02 lane 121: dba204's heat is mostly the finished frame's orbit at 0.25 C per W/m2 (PW-1325, lean A); Earth's 20-40 deg excess is the summer split (PW-1326/1327, one round later).
- 2026-11-02: Status todo -> in-progress. 11-02: lane 121, diagnosis first incl. PW-1322's observed-rain swap.
- 2026-11-01: Created.
