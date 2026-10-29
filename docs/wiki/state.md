# State

**Last updated: 2026-10-28.** Overwrite this page; never append (history is in git). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Lanes running
<!-- coordinator: fill in at each compaction or lane change -->
- Physics (10-29): lanes 23-25 merged (weld ratchet PW-970; continents' sea water PW-980 part; sea bulk evaporation PW-015 with Earth B 27-28%; paired judge PW-994). Lane 26 running: dry subtropical coasts PW-998 with PW-026 (maritime air inland). Then the PW-980 remainder, PW-948 (needs the owner), showcase rebuild, tag v1.
- Fun (10-29): megafauna PW-958/959/977 stage 1 and sapiens dates PW-978/971 merged. Lane 45 running: people density PW-974 + PW-977 stage 2 (peoples' and predators' share of the food). Owner decisions open: PW-948, PW-990, PW-987, PW-988.
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
