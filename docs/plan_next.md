# Plan

*Updated 2026-11-03. The roadmap is the board in `issue-tracking/` (one file per ticket); this page only says where to look. History: the 2026-10-14 version is at `git show d32f7fa~1:docs/plan_next.md` (older still: `git show bdc967f:docs/plan_next.md`).*

## Milestones
- **v1** (epic PW-244; done, tagged v0.1.0 on 2026-11-01): a reliable, finished, usable planet from a seed. `planet make` / the start screen, export, human-use layers, glacial imprint, fine-zoom redraws, then the showcase remake (PW-202) and the final calibration pass. `board.py milestones v1` lists what is open.
Milestone vN is tag v0.N.0; v1.0 (tag v1.0.0) is 1 December, after v5. Plan, must-haves and "done when" checks per milestone: `docs/review/board/milestones-v2-v5.md` (2026-11-03). Milestones hold non-physics must-haves only.
- **v2** (~10 Nov): faiths you write, a culture's food sheet (PW-1391), dates in years. `board.py milestones v2`.
- **v3** (~17 Nov): states and war v0 (PW-661), invasions you schedule (PW-756), the Seven Meals empires (PW-785).
- **v4** (~23 Nov): polities inside the history, war's toll on land (PW-1172), culture-founded calendars, a names slot for the languages work.
- **v5** (~28 Nov): the December campaign world, refined L7 to L9 (PW-1209), every Seven Meals people right.
- **v1.0** (1 Dec): freeze, checklist walk, tag.
- **Physics side track:** gates no tag; ranked tickets in `later` (D47 first: PW-1424, PW-1425), one 1-3 pass lane each.
- **later:** the backlog, including the old v3/v4 systems (weather, moons, weird worlds, technology epic, walkable setting PW-1199). Ice ages done properly (epic PW-470; v1 uses the glacial index kludge PW-471) and the base-climate v2 plan (PW-570, `docs/review/base-climate/stages.md`) wait there.

Defaults: level 7 for showcases, level 6 for quick large-scale tests.

## The board
```sh
uv run python issue-tracking/board.py next --limit 15     # cheapest, most valuable first
uv run python issue-tracking/board.py decisions           # judgement calls for the owner
uv run python issue-tracking/board.py milestones v2       # open tickets of a milestone
uv run python issue-tracking/board.py list --open --subsystem climate
uv run python issue-tracking/board.py tree --open
```
Conventions, the inbox for subagents, and effort/impact definitions: `issue-tracking/README.md`.

## Elsewhere
- `docs/overview.md`: how each subsystem works.
- `docs/coordination.md`: worktrees, merging, the server, run costs, showcase recipes.
- `docs/wiki/`: the coordinator wiki (start at `index.md`: current state, rulings, glossary, playbook).
- `docs/proposals/`: design write-ups.
- `docs/review/`: lane evidence kept while an open ticket, a core doc or code names it (physics audit in `audit/`, base-climate stages, health sweep reports, the images the overview links). Retention rule: `docs/coordination.md`, "docs/review retention".
