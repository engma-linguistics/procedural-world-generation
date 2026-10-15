# Plan

*Updated 2026-10-14. Open work, known issues and decisions now live on the board in `issue-tracking/` (one file per ticket). This page is only the short roadmap.*

## Roadmap
- **Discrete volcanoes (PW-001):** hotspot vents every ~50–100 km of plate motion and arc volcanoes as objects that ride their plate, carried into worlds and zooms (cones, eroded islands, atolls). Approved, at level 7.
- **Landform classes (PW-005):** 8–12 classes (great escarpment, caprock plateau, traps, fault-block rift, fold belt, shield, …) computed from each cell's history in the run, synthesised by the zoom. This is where coarse→fine variety and taller waterfalls come from.
- **Rain / moisture transport and the overturning follow-up (PW-013):** diagnose and fix vapour transport between basins, then remove the overturning spin-up rule; Antarctic bottom water; salinity memory in the time zoom.
- **World finishing pass (PW-090):** run the ~1 Myr glacial time zoom from a chosen world and keep its imprint (carved valleys, moraines, lakes, sea-level marks) as the world's last phase, plus finer features for real use (rivers, soils, coasts, resources, export for games). First step: PW-091.
- **Tectonics tuning:** the plate-count nudge (PW-024), fast sea-level swings (PW-053), low level-7 continents (PW-052), closed basins (PW-054).

Defaults: level 7 for showcases, level 6 for quick large-scale tests.

## The board
```sh
uv run python issue-tracking/board.py next --limit 15     # cheapest, most valuable first
uv run python issue-tracking/board.py decisions           # judgement calls for the owner
uv run python issue-tracking/board.py list --open --subsystem climate
uv run python issue-tracking/board.py tree --open
```
Conventions, the inbox for subagents, and effort/impact definitions: `issue-tracking/README.md`.

## Elsewhere
- `docs/backlog.md`: the open work from the epics down, with priorities and suggested batches (snapshot 2026-10-14).
- `docs/overview.md`: how each subsystem works.
- `docs/coordination.md`: worktrees, merging, the server, run costs, showcase recipes.
- `docs/proposals/`: design write-ups (glacial time zoom, ocean overturning, supercontinent cycle, the round 1–2 plan as written).
- `docs/review/`: investigations and run reviews; `docs/morning_report.md` is the record of the 2026-10-14 overnight session.
- The old plan, with the full Known issues list as migrated, is at `git show bdc967f:docs/plan_next.md`.
