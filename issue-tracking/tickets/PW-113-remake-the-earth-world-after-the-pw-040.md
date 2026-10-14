---
id: PW-113
title: Remake the Earth world after the PW-040 observation fix
type: task
status: done
parent: null
subsystem: docs
effort: xs
impact: low
found_by: climfix
blocked_by: []
relates: [PW-040]
refs: [tools/earth_world.py, tools/earth_data.py, "world 2f38e3"]
created: 2026-10-14
updated: 2026-10-14
---

## Description
PW-040 (climfix) changed how tools/earth_data.py maps the observed NCEP temperatures (sea-level
reduced, bilinear, back to the cell's height; CACHE_VERSION 4). World 2f38e3 still holds the old
observed layers (and the old ice cooling), so its temperature-difference view still speckles. After
merging, rerun `uv run python tools/earth_world.py` and repoint references to 2f38e3 (docs/overview.md
caption, viewer bookmarks) if the id changes.

## Updates
- 2026-10-14: Status todo -> done. Remade: world f8a740; old 2f38e3 deleted.
- 2026-10-14: Created from inbox draft draft-remake-earth-world.md (found by climfix).
