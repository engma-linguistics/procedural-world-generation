---
id: PW-1191
title: "Owner call: should the elves and gnomes come through wandering thinnings instead of fixed portals?"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: highlights
effort: xs
impact: low
found_by: lane78
blocked_by: []
relates: [PW-1150, PW-697]
refs: [planet/lineages/history/portals.py, planet/lineages/samples/dnd.toml]
created: 2026-10-30
updated: 2026-11-03
---

## In plain words
The peoples workbench now has a fourth way for arrivals from other planes to come in: "wandering thinnings".

How a thinning works:
- A thinning is a weak spot between the realms. It drifts slowly over the world, the way a hotspot volcano stays put while the plates slide over it.
- It stays open for a few thousand years. While it stands over land a people can live on, that people comes through in waves. Then it closes, and another opens somewhere else.
- Elves, gnomes and others from the same plane share its thinnings.

The D&D preset still uses fixed portals at interesting sites: 8 of them, with a million elves in two waves. That is the setting the coordinator asked for.

Your call: switch the Feywild peoples to wandering thinnings, or keep the fixed portals?

## Description
- Setting: `meta.portal_mode = "wandering"`.
- Knobs:
  - `portals`: thinnings open at once;
  - `portal_open_kyr`: mean opening, default 5 kyr;
  - `portal_drift_kmkyr`: default 100 km/kyr;
  - `wave_kyr`: years between an arrival's waves.
- Each arrival also has a `plane`.
- Both drift defaults are judgement calls, not measured.
- Not yet measured on a 4360a3 run in wandering mode. Only the unit test (tests/test_lineages.py::test_wandering_thinnings_drift_open_and_close) covers it.
- [ ] owner picks fixed or wandering for the preset
- [ ] if wandering: screen elves', gnomes' and tritons' shares on a few rolls

## Updates
- 2026-11-03: Re-checked 11-03: owner D21 (10-31) said wandering portals come later, but no ruling picks fixed or wandering for the preset. Left open (belongs with PW-1195).
- 2026-10-30: Created from inbox draft draft-wandering-portals-for-the-feywild.md (found by lane78).
