---
title: Weathering is kinetically limited on every cell; slow-eroding land should be supply-limited
type: task
status: todo
parent: null
milestone: later
subsystem: climate
effort: l
impact: med
found_by: scout193
blocked_by: []
relates: [PW-1446, PW-451]
refs: [planet/tectonics/earth.py::weathering, planet/tectonics/earth.py::climate_coef, docs/review/tectonics/mountains/scout4.md, "West, Galy & Bickle 2005, EPSL 235: 211-228"]
---

## Description
In plain words: in the model, every patch of eroding land answers a warmer climate equally hard (the sink is erosion
supply × a climate factor × a plant factor, `earth.weathering`). On Earth, only fast-eroding ground does. Slow-eroding
lowlands with deep soils are limited by how much fresh rock reaches the surface, so warming hardly speeds them up.
West, Galy & Bickle 2005 (abstract; §4, p. 223): "At lower erosion rates mineral supply limits weathering. At higher
erosion rates there is abundant material but kinetic and therefore climatic factors limit weathering", and the
long-term feedback "takes place in more rapidly eroding terrains".

What misleads if it is never done: the CO2 thermostat is stronger than physics allows on low-relief planets, and it
cannot weaken when mountains are lowered (PW-1446 scout 193 found this by construction). Planets without big mountain
belts get a climate steadier than they should. Fixing it is expected to widen the spread between planets, not narrow
it, so it is a soundness item for after v1, not a fix for the spread bar.
