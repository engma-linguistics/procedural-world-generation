# State

**Last updated: 2026-10-24.** Overwrite this page; never append (history is in git). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Lanes running
<!-- coordinator: fill in at each compaction or lane change -->
- Physics (Opus): v1-finish-16 merged (PW-866): the finished world is the latest moment in the run's last 10 Myr (0.5 Myr steps) that passes the finish checks; run.json meta.finish_moment; viewer and --at auto open there. Bar + checks at the moment: L6 1 Gyr 15/18, L7 7/8 (end-only 10/18, 5/8): v1 physics bar met. Earth group 71%. PW-895 held. Next: coupling tail PW-878/872/879/876/874/877/883/884/871, PW-915 step-length audit, PW-821/816, geology and zoom tails, then tag v1. Fun lane 31 (PW-888 founder floor in area) running. Up to ~12 sims with >=40 GB free.
- Civilizations design (PW-856): owner answered both rounds 2026-10-26 (tickets PW-900..913). Backlog workgroups approved (PW-900). Next fun lane: PW-901 peoples refactor after fun lane 30 merges.
- Fun (Sonnet): fun lane 29 merged (6e66244): PW-887 frontier invasion (a thinner rival's cells at a people's front weigh exp(-0.5 ln density ratio), floor 0.3; Banks 2008, Kolodny & Feldman 2017) and the crowding drive (sea-crossing x(1+2 crowd) within the craft ladder; entry into poor country). Small-continent humans now fill their ~4k suitable cells by 100 kyr ago (the PW-885 8k line is the sea-limited niche); elves >=500 on 8/8, half-elves 8/8; hobgoblins thin to 80-140 cells on the small-continent tries (PW-889, re-measure after PW-888). Kept on 2a7385: fl29-dnd acd1e5, fl29-seven_meals ff49f2. Earlier kept: fl28 099362/89098b, fl27 bbfeb6/620278, fl26 97d5ba/3d951f. Next: PW-888 origins by habitable landmass area, then PW-868, 870, then civilizations once the owner answers the doc.
- Pick planet for seven_meals: 6fbc2c (peoples run 104de8, may be replaced by fun lane 22).

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
