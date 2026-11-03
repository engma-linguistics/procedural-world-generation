---
id: PW-1193
title: "Events system: one seeded schedule per kind (drought, eruption, quake, plague, cull), placed by the planet's physics, coupled through climate / K / the log, shown in the viewer"
type: task
status: todo
parent: PW-917
milestone: v2
subsystem: peoples
effort: l
impact: high
found_by: lane-85
blocked_by: [PW-1165]
relates: [PW-1165, PW-1166, PW-1167, PW-1171, PW-1172, PW-1108, PW-756]
refs: [docs/review/peoples-events/design.md, planet/lineages/history/events.py, planet/lineages/recent.py, planet/lineages/reputation.py, planet/lineages/settlements.py]
created: 2026-10-31
updated: 2026-10-31
---

## Description
**In plain words.** The owner asked for droughts, earthquakes and epidemics that come by chance but still change the world. A drought
should reshape the local climate for centuries, so the peoples and the climate agree. Design: docs/review/peoples-events/design.md,
section 1.
- **When and how big:** the dice. **Where:** the planet's physics (touchy climate, plate edges, live volcanoes, crowded towns).
- **Each event couples through exactly one of three channels:** the recent pass's climate fields (an `Episode`), lane 82's K cut
  (`kept` / `d`), or the event log alone.

Work:
- **Schedules.** One generator per kind, `default_rng((seed, EVENT_SALT[kind], try))`, drawn before the run. Placement reads the state
  at that step. Climate events keep the recent pass's own seed. `meta.events_seed` rerolls only the luck.
- **Eruptions** from the world's live volcanoes, at VEI 6 every 50–100 yr and VEI 7 every 500–1,000 yr (Wikipedia "Volcanic
  explosivity index", read). The effect is a local ash K-dent (size UNVERIFIED, judgement 300 km, 1 step), and for VEI 7 a 1-step
  cold Episode.
- **Earthquakes** on converging `plate_boundary` cells, at ~13.8 M7–7.9 and ~1.2 M8+ a year worldwide (USGS 2000–2021 table, read).
  Log only, plus a settlement fall reason "earthquake" (PW-1108).
- **Authored events.** `RecentParams.authored` holds climate episodes (re-saving the recent run, cheaply, with the cached climate).
  `[[event]]` gets the kinds drought, plague and cull, each with a place and a span (`reputation.parse_events`).
- **Viewer.** An events track on the slider and footprints on the map, with click-through text. The peoples tab gets "lost to" bars.
  Controls: bad years, plagues early/late, how hard peoples hunt raiders early/late, reroll the luck, and "place a drought here".
- **Owner ruling 10-31:** virgin-soil epidemics stay off.

- [ ] per-kind schedules, deterministic; adding a people leaves the climate schedule unchanged (test)
- [ ] eruption and quake placement from the world's tables
- [ ] authored drought / plague / cull
- [ ] viewer track, footprints, lost-to bars, controls
- [ ] judged on tools/peoples_robust.py, arms off / default

## Updates
- 2026-10-31: Created from inbox draft draft-events-system-schedule-and-viewer.md (found by lane-85).
