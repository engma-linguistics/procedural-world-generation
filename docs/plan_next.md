# Plan

*Updated 2026-10-14. Open work, known issues and decisions now live on the board in `issue-tracking/` (one file per ticket). This page is only the short roadmap.*

## Roadmap
**Done on 2026-10-14:** discrete volcanoes (PW-001), landform classes and their zoom synthesis (PW-005), boundary churn (PW-108), sea-level swings (PW-053), plate-count nudge (PW-024), clouds, ocean layers, seasonal layers.

**Next, in order** (owner, 2026-10-14; details in `docs/backlog.md`):
1. **Glacial isostasy (PW-189):** ice sheets press the crust down and it rebounds after they melt.
2. **Life and the land surface (PW-184):** soils (PW-185) and a vegetation proposal for owner review (PW-186) in parallel, then the vegetation model (PW-187) and coastal life (PW-188).
3. **Tectonics leftovers:** L7 continents too thin and low, retuning targets (PW-052, after PW-169); interior closed basins (PW-054); late plate collapse at L7 (PW-191); ice volume too large (PW-190).
4. **World finishing pass (PW-090),** starting with PW-091 (time zoom from a chosen world becomes the finished world); **rain and ocean (PW-013)** in parallel.
5. **Later:** weather generator (PW-156), resources (PW-155), multiscale time with species, fantasy races and civilisation at the very end (PW-103).

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
