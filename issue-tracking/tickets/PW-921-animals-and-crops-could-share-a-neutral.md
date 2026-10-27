---
id: PW-921
title: Animals and Crops could share a neutral base class instead of Crops subclassing Animals
type: task
status: todo
parent: null
milestone: null
subsystem: timezoom
effort: s
impact: low
found_by: pw901-history-split
blocked_by: []
relates: [PW-901]
refs: [planet/lineages/animals.py, planet/lineages/crops.py, planet/lineages/crop_defs.py]
created: 2026-10-27
updated: 2026-10-27
---

## Description
`Crops` is `class Crops(Animals)` and reuses `Stock`. It overrides `_make`, `step`,
`speed_mult`, `k_mult`, `frame_layers` and `summary`, and adds `know` and `present_cells`; what
it keeps from `Animals` is `__init__` and the stock list. A crop is not an animal, and the
inheritance means changes to `Animals` (herding, sea crossings) can reach `Crops` by accident.
This is optional tidiness, not a bug: the two classes behave correctly today.

Option: extract a small base (for example `Domesticates`) holding the shared constructor, the
`stocks` list and the hook signatures `_make`, `step`, `speed_mult`, `k_mult`, `frame_layers`
and `summary`, and make `Animals` and `Crops` both subclass it. `Stock` keeps its shape. It must
be bit-identical: check with the same probe as PW-901 (hash frames, presence, populations,
events, run.json, run.txt and briefs for two worlds, two trees, two seeds, base vs new) and
`uv run pytest -q` without golden updates. Worth doing only if a third domesticate kind (fungi,
say) is planned, or when next editing either class; otherwise leave it.
- [ ] `Crops` no longer inherits from `Animals`
- [ ] outputs bit-identical on the probe matrix; no golden updated

## Updates
- 2026-10-27: Created from inbox draft draft-animals-crops-base-class.md (found by pw901-history-split).
