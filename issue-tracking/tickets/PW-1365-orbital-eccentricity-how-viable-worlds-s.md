---
id: PW-1365
title: "Orbital eccentricity: how viable worlds stay across eccentricities, and what range the generator should allow"
type: task
status: done
parent: null
milestone: v2
subsystem: climate
effort: m
impact: med
found_by: owner
blocked_by: []
relates: [PW-1325, PW-443]
refs: [planet/orbit.py, docs/review/base-climate/summer-heat/diagnosis.md, "planet/climate.py::_summer_split", docs/review/climate/eccentricity/round1.md, "planet/icemass.py::cycle_dq", "planet/finish.py::orbit_dt", "planet/climate.py::_orbit", "planet/timezoom/params.py::TZParams", tools/hard_bar.py]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: owner 2026-11-02: the orbit's eccentricity drives seasonal swings (dba204's moment at 0.035 added up to ~+8 C to tropical July land before PW-1325). Investigate how worlds behave across eccentricities (Earth-like ~0-0.06 today, and well beyond): seasonal extremes, land >= 35 C or frozen, ice ages, the CO2 balance, habitability by biome and people; where viable turns unviable. Diagnose with the land's real seasonal response (after PW-1325 lands), on a few re-rolled L6 seeds and finished worlds; say what range the generator should draw from and whether weirder orbits belong to the post-v1 weird-worlds work (PW-443). Source the physics read (orbital forcing, habitability vs eccentricity); never from memory.

## Updates
- 2026-11-03: Status todo -> done. Lane 148 study merged (docs only): Earth's 0-0.06 safe; model gives way ~0.1 (run ice rule, two-month seasons); boils ~0.4. Decision on the desk as D46 (PW-1415, lean B now, D later). Follow-ups PW-1414, PW-1416.
- 2026-11-02: Created.
