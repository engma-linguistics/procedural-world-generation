# procgen_world

Planets built by simulation: plate tectonics, climate, rivers and erosion over 0.5–2 Gyr (`planet simulate`) produce a **run**; any moment can be sliced into a **world** (climate, rivers, lakes, biomes, waves, tides); worlds can be refined into **regional zooms** (1–4 km/px) or a **glacial time zoom** (1 Myr of ice ages). A three.js viewer (`planet serve`, port 8765) shows them all. Python 3.12, numpy + numba, run everything with `uv run`.

- **How it works:** `docs/overview.md` (subsystems, pipeline, data model). CLI and calibration: `README.md`.
- **Roadmap:** `docs/plan_next.md`. Worktrees, merging, the server, run costs, showcase recipes: `docs/coordination.md`.

## Work tracking
All open work, known issues and decisions live in `issue-tracking/` (rules: `issue-tracking/README.md`).
- **Check the board before starting** on a subsystem: `uv run python issue-tracking/board.py list --open --subsystem X` (subsystems: tectonics surface climate ocean hydrology coast zoom timezoom highlights viewer store infra docs).
- **Subagents** report every remaining issue, follow-up or judgement call as an inbox draft (`issue-tracking/inbox/draft-<slug>.md`, template in the README), not as prose in the report. Never assign `PW-` ids in a worktree; the coordinator numbers drafts with `board.py intake` after merging.
- A hook runs `board.py check` after edits under `issue-tracking/`; fix what it reports.

## Rules
- Commit locally only; never push.
- Grid level: **7** for showcases, **6** for quick large-scale tests (~6 min per Gyr at L6, ~30–40 min per Gyr at L7).
- No backward compatibility: old runs, worlds and zooms can be deleted (`planet delete`) when a change breaks them; don't keep code paths for them.
- `uv run pytest -q` before committing anything under `planet/`. If outputs changed on purpose, `uv run pytest tests/test_golden.py --update-golden`.
- After model changes: `uv run python tools/scorecard.py`; after climate changes: `tools/earth_check.py`. Earth is a test analogue, never a parity target.
- Nudge systems rather than force them; ask about genuine judgement calls (as `needs-decision` tickets).
