# State

**Last updated: 2026-10-24.** Overwrite this page; never append (history is in git). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Lanes running
<!-- coordinator: fill in at each compaction or lane change -->
- Physics (Opus): v1-finish-11 on top of hold/v1-finish-10-anchor (star anchored, full Gough, real plant calendar, drift on outgassing; failed the bar 0/6 ICEBOX because the carbon balance was frozen at 300 Myr). RULING (coordinator): anchor the carbon balance at the end (GEOCARB frame) and check the weathering feedback strength against the literature; end pCO2 ~180-600 ppm is a diagnostic. Audit done (PW-816..836).
- Fun (Sonnet): fun-lane-25 (viewer: PW-860 Equal Earth overlays, 843 wheel zoom, 840 right pane, 841 workbench, 845 fuels, 837 brief in viewer). Fun lane 24 merged (de83743): half-elves through frontier contact and arrival on free land near the partner (PW-852; residual PW-861), fiend framing dropped and dnd tieflings as a 3 kyr human template (PW-858), ruminant diet data and the no-dairy brief line (PW-850/800), tracks overlay removed (PW-857), Results tab per world (PW-842), label depth (PW-839), Equal Earth default (PW-838; overlays missing, PW-860). Kept runs on 2a7385: dnd 62341d and seven_meals bbfba8. Next: the coordinator's pick from PW-840/841/843/845, 851, 855, 853, 854, 837, 861.
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
- Owner feedback world (2026-10-24): world 2a7385 (seed 11 L7, run 6b48f5, time zoom f778ab, zooms 1ab4c4 91bf86 cd4341 80a169), peoples b69f51 (seven_meals) and 6b5d0e (dnd). Feedback doc: https://claude.ai/artifact/GMaU7W2PynuiY9z5o71kDA
- Runs: 6c652c, d30069, 99dc70, feaade.
- Worlds: 6fbc2c, 067778, a12762, 6909cb.
- Peoples run 104de8 (`seven_meals` preset) on world 6fbc2c.
- Also kept: Earth world 577526 and the nine overturning reference worlds (119973 28442c 607540 81aced 7082f5 d14b89 a5a387 dad91b c00ebf), per PW-202.
- Viewer: http://127.0.0.1:8765/viewer/ (server notes in [coordination.md](../coordination.md)).

## Where to look next
- Open owner decisions: `board.py decisions`.
- Unmerged branches or held work: ask `git branch --no-merged main` and the lane tickets; not tracked here.
