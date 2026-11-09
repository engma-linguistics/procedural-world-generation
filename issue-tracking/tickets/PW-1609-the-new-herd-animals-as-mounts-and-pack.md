---
id: PW-1609
title: "The new herd animals as mounts and pack animals: camels, yaks and reindeer for riding, camels and llamas for caravans"
type: task
status: todo
parent: PW-1498
milestone: later
subsystem: peoples
effort: s
impact: low
found_by: lane256
blocked_by: []
relates: [PW-835]
refs: [planet/lineages/samples/techtree.toml, "planet/lineages/trade.py::GOODS", planet/lineages/animal_defs.py]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: lane 256 added pigs, reindeer, camels, llamas and alpacas, water buffalo and yaks as herd animals. They feed and milk
(the brief's meat and dairy lists, the cuisine sheet), but they do nothing else yet:
- The `riding` tech (techtree.toml, needs_any) needs a horse or a fantasy mount. Camels, yaks and reindeer are ridden on Earth but do not unlock it.
- The trade ledger (trade.py) counts horses as a good, but camel or llama caravans add nothing to reach.
- Water buffalo add a little plough land (crop_land 0.15), but no ox-traction tech names them.

What breaks if never done: a desert or plateau people with camels or yaks has no mounts or pack trains in its story or trade. That would be
a visible gap once trade routes reach the culinary book. Needs a source per use (camel caravans, the llama caravans of the Andes) before
any number is set.

## Updates
- 2026-11-09: Created from inbox draft draft-pack-and-riding-herds.md (found by lane256).
