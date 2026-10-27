---
title: Peoples and civilization CLI runs should default to a favourite world
type: task
status: todo
parent: null
milestone: null
subsystem: viewer
effort: xs
impact: low
found_by: favourites
blocked_by: []
relates: []
refs: [planet/favourites.py, planet/__main__.py, docs/wiki/where-things-live.md, tests/test_favourites.py]
---

## Description
The owner can now star runs and worlds in the viewer (gallery cards, the run/world list, the peoples workbench world picker). They are stored server-side in `worlds/favourites/favourites.json` and listed by `uv run python -m planet favourites [--ids|--json] [--kind world]`; the workbench already defaults its world picker to the newest-sorted favourite. What is not done: the CLI commands that take a world (`planet lineages`, and the future civilization runs) still require an explicit world. The owner's intent is that favourites are the default worlds for those runs. Wire `favourites.listing("world")` in as the default when no world is given (and say which one was picked), and make lanes' test-world picking in `docs/coordination.md` / the playbook point at `planet favourites --ids --kind world`. Note a favourite world may lack a stored time zoom, which `planet lineages` needs; pick the first favourite that has one, as the workbench list does.
- [ ] `planet lineages` with no world uses the first runnable favourite and prints its id
- [ ] coordinator playbook mentions `planet favourites` for test-world choice
