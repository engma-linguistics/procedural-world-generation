# State

**Last updated: 2026-10-24.** Overwrite this page; never append (history is in git). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Lanes running
<!-- coordinator: fill in at each compaction or lane change -->
- Physics (Opus): idle for the owner's clean benchmark (one L6 then one L7, scratchpad bench). PW-790 analysed (docs/review/base-climate/v2-climate-1/): outgassing decline is in the literature range; the water-world icebox comes from the CO2 references freezing at 300 Myr while land still emerges. RULING (coordinator): fix the freeze planet-relatively (PW-798, option A) before any +8 offset (PW-799, blocked). Next: PW-798, then PW-791 star thermostat.
- Fun (Sonnet): idle for the benchmark. PW-793 (no fiend dairy) and PW-794 (horse contact uptake, barriers) merged; riders test now reads "home" as every landmass the horse reached (both strict conditions kept). Next: PW-797 salt-miner dwarves, PW-800 follow-ups.
- Pick planet for seven_meals: 6fbc2c (peoples run 104de8, may be replaced by fun lane 22).

## v1
- Epic PW-244. Only the owner sign-off PW-780 is open (default `star_brightening` 0.45, a K-type star; provisional owner OK 2026-10-24). 2 open tickets in the v1 milestone.
- Strict icehouse bar: L6 13/18 seed-draws, L7 7/8. Rule: ~70% pass, never-ice and always-icebox both fail ([glossary](glossary.md), [decisions](decisions.md)).
- Showcase remake (PW-202) done; the 4 L6 + 4 L7 showcases below.

## v2 and later (board.py milestones, 2026-10-24)
| milestone | open | done |
|---|---|---|
| v1 | 2 | 104 |
| v2 | 162 | 115 |
| v3 | 17 | 2 |
| later | 72 | 2 |
| unscheduled | 44 | 274 |

v2 priorities: always one fun lane on peoples/lineages (PW-692 frames the end goal), then speed, resources (PW-155), zoom quality (PW-516). Roadmap: [plan_next.md](../plan_next.md).

## Current showcases
- Runs: 6c652c, d30069, 99dc70, feaade.
- Worlds: 6fbc2c, 067778, a12762, 6909cb.
- Peoples run 104de8 (`seven_meals` preset) on world 6fbc2c.
- Also kept: Earth world 577526 and the nine overturning reference worlds (119973 28442c 607540 81aced 7082f5 d14b89 a5a387 dad91b c00ebf), per PW-202.
- Viewer: http://127.0.0.1:8765/viewer/ (server notes in [coordination.md](../coordination.md)).

## Where to look next
- Open owner decisions: `board.py decisions`.
- Unmerged branches or held work: ask `git branch --no-merged main` and the lane tickets; not tracked here.
