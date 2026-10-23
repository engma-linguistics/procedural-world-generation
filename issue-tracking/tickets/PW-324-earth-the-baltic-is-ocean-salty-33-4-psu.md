---
id: PW-324
title: "Earth: the Baltic is ocean-salty (~33.4 psu; observed ~6-8)"
type: task
status: todo
parent: null
milestone: null
subsystem: ocean
effort: m
impact: low
found_by: coastal-life
blocked_by: []
relates: [PW-152]
refs: [planet/ocean.py, tools/coastal_check.py]
created: 2026-10-15
updated: 2026-10-23
---

## Description
On the L6 Earth world (`tools/earth_world.build(6)`, code of 2026-10-15) the Baltic proper's sea cells (55-60 N, 17-22 E) have a surface salinity of 33.4-33.6 psu; the real Baltic is brackish, ~6-8 psu in the proper and < 5 in the Bothnian Bay, because a big river and rain surplus is trapped behind the shallow Danish straits. The model's salinity barely departs from the open ocean there. Seen through coastal life (PW-188): kelp grows in the Baltic proper (it needs > ~15 psu, so none is observed), and reefs and seagrass would use the wrong salinity in any enclosed sea of a generated world. The mirror problem of PW-152 (Mediterranean and Red Sea too fresh): enclosed seas don't build up their own salinity anomaly.
- [ ] Baltic proper < 15 psu on the Earth world, Black Sea brackish (~18), without upsetting the open ocean

## Updates
- 2026-10-23: PW-597 triage (2026-10-23): kept, not wontdo. Enclosed seas don't build up their own salinity anomaly (mirror of PW-152), which would also hit generated worlds' coastal life; the Baltic is only the test case.
- 2026-10-15: Created from inbox draft draft-earth-baltic-too-salty.md (found by coastal-life).
