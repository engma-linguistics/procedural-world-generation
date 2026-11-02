---
id: PW-1351
title: Halflings, gnomes and dwarves skip the era density cap and the land's productivity (no farm share)
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane130-density-ladder
blocked_by: []
relates: [PW-1275, PW-1203, PW-974]
refs: [planet/lineages/samples/dnd.toml, "planet/lineages/landuse.py::shares", "planet/lineages/history/growth.py::_set_era_density", "planet/lineages/history/growth.py::ERA_DENSITY", "planet/lineages/prey.py::people_fields", planet/lineages/history/model.py, docs/review/peoples/density-ladder/ladder.md, "planet/lineages/ladder.py::is_hold", "planet/lineages/ladder.py::Ladder.tech (TERRACE_LAG)", "planet/lineages/crop_defs.py::_EXCL", "planet/lineages/spec.py::WAYS", docs/review/peoples/density-ladder/build.md]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: three dense peoples get their full number everywhere and from the start, because the model does not see them as farmers.

Found while sourcing the density ladder (lane 130, `docs/review/peoples/density-ladder/ladder.md`, section "Where density lives now"). Read off `landuse.shares` on dnd.toml at 05f84f8d:
- **halfling**: density 12, traits `agricultural`, but `way` is inherited from its parent `archaic_human` as `forager`, so `shares` gives farm 0, forage 1. Result: a 12/km² people read as foragers (its productivity factor reads the foraging layer) and, with farm share 0, `growth._set_era_density` never caps it at the forager 0.35 or gardener 5 before it farms.
- **gnome** (12/km²; farm 0, forage 0.5) and **dwarf / hill_dwarf** (7 / 8; farm 0, herd 0, forage 0): same skip of the era cap; the dwarves read no productivity layer at all (`people_fields` leaves f = 1 when farm + herd + forage = 0), so a hold's density does not depend on the land it feeds from.

PW-1275 (the shared ladder) would replace all of this, so fix it there rather than separately (owner's no-stopgaps rule) unless PW-1275 slips: then give halflings `way = "farmer"` (or an explicit fertile use) and give gnomes and dwarves a farm/herd use so the cap and the productivity factor apply.
- [ ] halflings, gnomes, dwarves get a way of life whose density follows the era and the land
- [ ] check `shares` for every dnd people with density > 1 has farm or herd > 0

## Updates
- 2026-11-02: Owner 2026-11-02: halflings and gnomes absolutely can be farmers.
- 2026-11-02: Created from inbox draft draft-halflings-farm-as-foragers-at-12.md (found by lane130-density-ladder).
