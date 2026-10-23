# Plan

*Updated 2026-10-23. The roadmap is the board in `issue-tracking/` (one file per ticket); this page only says where to look. History: the 2026-10-14 version is at `git show d32f7fa~1:docs/plan_next.md` (older still: `git show bdc967f:docs/plan_next.md`).*

## Milestones
- **v1** (epic PW-244): a reliable, finished, usable planet from a seed. `planet make` / the start screen, export, human-use layers, glacial imprint, fine-zoom redraws, then the showcase remake (PW-202) and the final calibration pass. `board.py milestones v1` lists what is open.
- **v2:** features before more physics fidelity. Mainly speed (PW-247/252), resources (PW-155 with PW-474), planet settings and phone layout (PW-481, PW-483), fine-zoom and zoom landform quality (PW-516 and the zoom tickets), and the base-climate and ocean follow-ups. `board.py milestones v2`.
- **later / parked:** ice ages done properly (epic PW-470; v1 uses the glacial index kludge PW-471), L8/L9 finish (PW-490), multiscale time (PW-103), weather (PW-156), moons and planet bodies (PW-216), weird worlds (PW-443).
- The base-climate v2 plan (overturning, sea's air, summer heat, thermostat; PW-570) is tracked in `docs/review/base-climate/stages.md`.

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
- `docs/coordination.md`: worktrees, merging, the server, run costs, showcase recipes, dated coordinator state.
- `docs/proposals/`: design write-ups.
- `docs/review/`: investigations kept for open tickets (physics audit in `audit/`, base-climate stages, ice v2, health sweep reports) and the images the overview links. Cleaned 2026-10-23: see `docs/cleanup-2026-10-23.md`.
