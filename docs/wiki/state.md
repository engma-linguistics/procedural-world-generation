# State

**Last updated: 2026-10-28.** Overwrite this page; never append (history is in git). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Lanes running
<!-- coordinator: fill in at each compaction or lane change -->
- Physics: lane 19 geology tail merged (d7b8577e: PW-826/818/817 done, PW-827 metric; paired 29/36 vs main 29/36). PW-821 rain fix dropped (24/36 vs 29/36), blocked on PW-015. Gallery: 12 L7 worlds (docs/review/gallery/gallery.md), only 6/12 finish well (PW-948, lean cold): look into it before tagging v1. Next: PW-948, zoom tail, then tag v1.
- Fun: lane 39 tech tree v0 merged (8 tracks, 98 techs, Technology tab; output only, PW-946). Lane 38 megafauna coverage held on branch worktree-agent-a3512fd38525dbb67: coverage 48 -> 106/116 but peoples remnants 18 -> 24, per-people pass 75% -> 70%; awaiting the owner (giant density option?). Owner questions open: PW-945 dragon teachers, PW-947 language dates.
- Up to ~12 sims with >=40 GB free in /tmp.

## v1
- Epic PW-244. Only the owner sign-off PW-780 is open (default `star_brightening` 0.45, a K-type star; provisional owner OK 2026-10-24). 42 open tickets in the v1 milestone (workgroups A-D in the backlog doc https://claude.ai/artifact/8rxpMkD49iovLmeBzZmP4t).
- Icehouse bar loosened 2026-10-25 (PW-865): icehouse share is uncapped; snowball, hellhole and never-ice fail. The old bar on main's forward star was L6 13/18 and L7 7/8. Rule: ~70% pass, never-ice and always-icebox both fail ([glossary](glossary.md), [decisions](decisions.md)).
- Showcase remake (PW-202) done; the 4 L6 + 4 L7 showcases below.

## v2 and later (board.py milestones, 2026-10-26)
| milestone | open | done |
|---|---|---|
| v1 | 42 | 112 |
| v2 | 183 | 150 |
| v3 | 21 | 4 |
| later | 72 | 5 |
| unscheduled | 50 | 275 |

v2 priorities: always one fun lane on peoples/lineages (PW-692 frames the end goal), then speed, resources (PW-155), zoom quality (PW-516). Roadmap: [plan_next.md](../plan_next.md).

## Current showcases
- Owner feedback world (2026-10-24): world 2a7385 (seed 11 L7, run 6b48f5, time zoom f778ab, zooms 1ab4c4 91bf86 cd4341 80a169), peoples b69f51 (seven_meals) and 6b5d0e (dnd). Feedback doc: https://claude.ai/artifact/GMaU7W2PynuiY9z5o71kDA
- Runs: 6c652c, d30069, 99dc70, feaade.
- Worlds: 6fbc2c, 067778, a12762, 6909cb.
- Peoples run 104de8 (`seven_meals` preset) on world 6fbc2c.
- Also kept: Earth world 577526 and the nine overturning reference worlds (119973 28442c 607540 81aced 7082f5 d14b89 a5a387 dad91b c00ebf), per PW-202.
- Viewer: http://127.0.0.1:8765/viewer/ (server notes in [coordination.md](../coordination.md)).

## Where to look next
- Open owner decisions: `board.py decisions`.
- Unmerged branches or held work: ask `git branch --no-merged main` and the lane tickets; not tracked here.
