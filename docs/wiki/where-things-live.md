# Where things live

Code map by file: [overview section 6](../overview.md). This page is the operational map.

## Data stores (repo root, git-ignored; worktrees symlink them to the main checkout)
| Store | Contents | Delete with |
|---|---|---|
| `runs/<id>/` | simulation runs: keyframes, layers, checkpoints, time zooms (also runs) | `uv run python -m planet delete run:<id>` |
| `worlds/<id>.json` + `worlds/layers/<id>/` | finished worlds (header + one binary file per layer) | `delete world:<id>` |
| `zooms/<id>/` | regional and fine zooms | `delete zoom:<id>` |
| `worlds/favourites/favourites.json` | the owner's starred runs and worlds (viewer stars; `planet favourites [--ids] [--kind world]` lists them for agents; `GET/POST /api/favourites`); a star goes when its item is deleted | unstar in the viewer |
| `grids/` | cached icosphere grids | rebuilt on demand |
| `data/` | symlinked input data (Earth reference data) | |

`--orphans` deletes things whose parent is gone. Bulk cleanup: `uv run python tools/cleanup_outputs.py` (lists), `--yes` (deletes everything not referenced by an open ticket, not younger than 12 h, not the Earth world). Outputs are freely deletable ([decisions](decisions.md)).

## Docs
- `docs/overview.md`: how it works. `docs/coordination.md`: worktrees, merging, costs, recipes. `docs/plan_next.md`: roadmap pointer.
- `docs/proposals/`: design write-ups (lineages, resources, soils, vegetation, culinary-dnd intake).
- `docs/review/`: lane evidence, under `docs/review/<topic>/`, kept only while an open ticket, a core doc or code points at it; deleted when its tickets close (the history has it). `board.py review` lists what keeps each file; `board.py check` warns about the rest. Rule: [coordination.md](../coordination.md), "docs/review retention".
- `docs/scorecard.jsonl`: scorecard history (written by `tools/scorecard.py`).
- `docs/wiki/`: this folder.

## Tools and checks
- `tools/scorecard.py` (~11 min; after model changes), `tools/earth_check.py` (after climate changes), `tools/health.py` (multi-seed sweep; `--quick` ~6 min), `tools/cleanup_outputs.py`.
- Tests: lanes run `uv run pytest -q -m 'not slow'`; the full `uv run pytest -q` (13–22 min under load) runs at merge. Goldens in `tests/golden/`.

## Server
- `planet serve --no-open` on port **8765**, viewer at http://127.0.0.1:8765/viewer/. Restart only after `planet/server.py` or `planet/api.py` change; recipe in [coordination.md](../coordination.md). Subagents never touch it.

## Peoples presets
- `planet/lineages/history/` (PW-901): the peoples simulation as a package, `History` built from mixins by concern; see its `__init__` docstring. Older tickets still cite `history.py`: look in the module for the concern (origins.py, dispersal.py, contact.py, ...).
- `planet/lineages/samples/dnd.toml` (stock D&D tree), `planet/lineages/samples/seven_meals.toml` (the owner's world). Spec reference: docstring of `planet/lineages/spec.py`. The editor is `viewer/lineages.html`.

## Board
- Tickets `issue-tracking/tickets/PW-NNN-*.md`, drafts `issue-tracking/inbox/`, CLI `issue-tracking/board.py`, rules [issue-tracking/README.md](../../issue-tracking/README.md). Starting points: `board.py next`, `decisions`, `milestones`, `list --open --subsystem X`.
- Consumer repo: culinary-dnd at `~/personal/repos/culinary-dnd`, read-only.
