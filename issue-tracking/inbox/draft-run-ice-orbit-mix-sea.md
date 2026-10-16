---
title: "Run ice: the cycle-averaged balance still mixes the orbital response with the sea counted as land"
type: task
status: todo
parent: null
subsystem: climate
effort: xs
impact: low
found_by: tzbatch-2026-10-16
blocked_by: []
relates: [PW-114, PW-190]
refs: [planet/tectonics/earth.py, planet/icemass.py, planet/timezoom.py]
---

## Description
PW-114 (tzbatch) fixed the time zoom's orbital response over bright ice (`timezoom.orbit_k`): the air over
a sheet brings the response of the land, sea and ice around it, each at its own share (sea 0.3 of the
land's, bright ice 0.2), where before the absorbed shares were mixed with the open sea counted as fully
absorbing (1) and then scaled by the land's `insol_k`. Greenland's ice went from ~0.7 to ~0.35 of the land's
response, Antarctica's from ~0.42 to ~0.23.

The run's ice (`earth.ice_sheets`) averages `icemass.balance` over the cycle's orbits with the old mix:
`absorb = climate.smooth_big(g, 1 - clip(old / SNOW_H) * (1 - ICE_ABSORB), ABSORB_KM)` (sea cells 1).
So the run's coastal ice still feels ~2x the time zoom's orbital swing, and its cycle-average melt penalty
is a little larger than the time zoom's: a small inconsistency in PW-190's shared rule (the run's sheets a
little smaller near the coast than the time zoom's balance, PW-241/PW-295's direction). Not changed in the
tzbatch branch (planet/tectonics/ was another agent's lane).

Fix: in `earth.ice_sheets`, mix the shares with the sea at its own, `np.where(land, 1 - clip(old / SNOW_H)
* (1 - ICE_ABSORB), INSOL_SEA)`, before `smooth_big`, and blend as `orbit_k` does (`absorb = (1 - b) + b x
mix` with b the cell's brightness), or call a shared helper. One line; then re-measure `tools/ice_probe.py
0 -6` and the time zoom drift (PW-295).
