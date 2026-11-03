---
id: PW-1183
title: Portal arrivals skip the free-room siting, so the gnomes shrink 10-60x when portals are on
type: task
status: todo
parent: null
milestone: v2
subsystem: peoples
effort: s
impact: med
found_by: lane77
blocked_by: []
relates: [PW-697, PW-1150]
refs: [planet/lineages/history/origins.py, tools/peoples_robust.py]
created: 2026-10-30
updated: 2026-10-31
---

## In plain words
When arrivals come through portals (portal_mode = sites), the gnomes end up far smaller than without portals: 0.07-0.34% of people
instead of 2.3-4.5% on world 4360a3. Without portals an arriving people is set down where it has free room. Through a portal it
is set down at its best habitat near the portal, even if other peoples already fill that country.

## Description
origins._origin_new: lane 73's arrival siting (free room = K less the rivals' load, smoothed over ARRIVAL_POCKET_RINGS, landmass by
founders) applies only when portal_mode is off. The portal branch then picks argmax(K x noise) within PORTAL_KM of each portal, on
the bare habitat. Suite (lane 77, dnd, seed 7/10, gnome share off / 1 portal / 3 portals): 4360a3 s7 4.5% / 0.34% / 1.9%; s10 2.3% /
0.073% / 0.065%; af2677 s7 5.6% / 1.1% / 5.7%. Elves and tritons move less (their country is emptier).
Fix: inside the portal branch, score the cells within PORTAL_KM (and PORTAL_FAR_KM) by the same free-room pocket as without portals.
Lane 78 builds wandering portals: whoever touches the portal block first should fold this in.

## Updates
- 2026-10-31: Milestone v1 -> v2 (v1 cut plan, docs/review/v1-cut/plan.md): not a tag blocker; v1 tags the planet, peoples ship as a preview.
- 2026-10-30: Created from inbox draft draft-portal-arrivals-skip-free-room-siting.md (found by lane77).
