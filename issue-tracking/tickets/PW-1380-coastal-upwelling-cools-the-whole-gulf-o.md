---
id: PW-1380
title: "Coastal upwelling cools the whole Gulf of Mexico 1.45 C (up to 6 C in the Bay of Campeche): Ekman drift away from a coast in a nearly enclosed sea"
type: task
status: todo
parent: null
milestone: v2
subsystem: ocean
effort: s
impact: low
found_by: lane134
blocked_by: []
relates: [PW-1362, PW-593]
refs: [docs/review/base-climate/rain-supply/round2.md, docs/review/base-climate/rain-supply/seaparts.py, "planet/climate.py::upwelling_cooling", "planet/climate.py::sea_surface"]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: the model cools much of the Gulf of Mexico by "upwelling", as if the trade winds pushed its
surface water out to sea. In a small, nearly enclosed sea the water has nowhere to go: it piles up against the
far shore.

Earth L6, Gulf box (18-30.5 N, 98-80 W):
- `upwelling_cooling` averages 1.45 C over the box;
- 82 of its 153 cells get over 0.5 C;
- it reaches 6.1 C in the Bay of Campeche (18.6 N, 92.5 W) and 4-4.5 C all along N Yucatan.

The Gulf's annual air is 22.8 against NCEP's 25.0, and this is most of that gap (PW-1362: the Gulf's summer
showers never fire).

The rule (`off = clip(ek . away, 0, 1.5)`) asks only whether the Ekman drift points away from the nearest land. Coastal
upwelling needs the offshore drift to leave, into an open ocean wider than the drift's reach. N Yucatan's
upwelling is real but local (not checked against data here).

What I'd try: scale `off` by how open the sea is downstream of the drift. For example, the distance to land along
ek over ~500-1000 km, or the share of open ocean within the Rossby radius in the drift's direction. Check that
Peru, California, Benguela and Canary keep their cooling.

The E Atlantic subtropics' annual mean is also 1.5 C cool (Canary current -0.74, latitude's t_sea 19.8 vs NCEP 21.3).
It's small and has two parts, so it's noted here, not ticketed.

- [ ] Gulf box upwelling under ~0.5 C mean, with the four big eastern-boundary upwellings unchanged (+-0.5 C)

## Updates
- 2026-11-02: Created from inbox draft draft-gulf-upwelling-box-wide.md (found by lane134).
