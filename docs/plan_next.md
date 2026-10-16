# Plan

*Updated 2026-10-14. Open work, known issues and decisions now live on the board in `issue-tracking/` (one file per ticket). This page is only the short roadmap.*

## Roadmap
**Done on 2026-10-14:** discrete volcanoes (PW-001), landform classes and their zoom synthesis (PW-005), boundary churn (PW-108), sea-level swings (PW-053), plate-count nudge (PW-024), clouds, ocean layers, seasonal layers.

**Status 2026-10-15:** V1 epic PW-244 sets the order from here (see docs/coordination.md). overnight batch and foundation round merged; see docs/coordination.md "Current state" for the next steps. **Order change (coordinator, 2026-10-15, after the owner asked whether the base layers are stable enough):** after the overnight batch (ice/isostasy, vegetation in zooms, vegetation-climate feedbacks, small tickets), run a **foundation round** before soils, resources, game attributes and the L8 run: PW-052, PW-191, PW-054, PW-046, then PW-171/170 and PW-055. Vegetation tuning is insulated (Earth-tuned, recomputed on whatever geography exists), so the vegetation steps in flight continue.

**Next, in order** (owner, 2026-10-14; superseded by the V1 epic order in docs/coordination.md, details on the board):
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
- The open work from the epics down: `board.py tree --open` (the 2026-10-14 backlog snapshot, docs/backlog.md, is at commit d8e959a).
- `docs/overview.md`: how each subsystem works.
- `docs/coordination.md`: worktrees, merging, the server, run costs, showcase recipes.
- `docs/proposals/`: design write-ups (vegetation).
- `docs/review/`: investigations and run reviews: the physics audit (`audit/`), the 2026-10-15 baselines and health sweeps, and image galleries linked from the overview.
- The old plan, with the full Known issues list as migrated, is at `git show bdc967f:docs/plan_next.md`.
