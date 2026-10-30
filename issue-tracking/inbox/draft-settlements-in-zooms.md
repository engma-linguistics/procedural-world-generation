---
title: "Settlements in a regional zoom: each ledger site placed at km scale on its own terrain (harbour, ford, river bend)"
type: task
status: todo
parent: null
milestone: v2
subsystem: zoom
effort: m
impact: med
found_by: fun-lane-60
blocked_by: []
relates: [PW-1011]
refs: [planet/lineages/settlements.py, planet/zoom, planet/humanuse.py]
---

## Description
In plain words. The settlement ledger (PW-1011) gives each site a cell (~110 km across at L6) and a seeded spot inside it, so on the globe a city's dot does not sit on its actual harbour or river. A regional zoom (1-4 km/px) has the human-use layers at km scale: harbours, navigable reaches, fords, passes, fresh water. It also already places villages inside zooms from its own rules (`zoom_peoples.py`).

What to try: when a zoom covers ledger sites, move each one to the best pixel of its cell inside the zoom, by the same site factor the ledger uses (harbour, navigable river, fresh water, fertile ground, a pass), and draw the ledger's sites, ruins included, on the zoom. The zoom's own villages should then fill in around the ledger's chief places instead of being placed independently.
- [ ] a zoom draws the ledger's sites of the cells it covers, each on its best pixel; ruins shown
