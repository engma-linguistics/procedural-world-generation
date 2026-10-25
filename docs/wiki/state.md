# State

**Last updated: 2026-10-24.** Overwrite this page; never append (history is in git). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Lanes running
<!-- coordinator: fill in at each compaction or lane change -->
- Physics (Opus): v1-finish-13 continues v1-finish-12 in worktree agent-a509febb63d5ebd7d (branch worktree-agent-a509febb63d5ebd7d: PW-865 bar harness passrate4, plants light from climate sunshine be00f07; thermostat-off v11 physics bar 7/10, all checks 3/10). RULING (coordinator): drift sized to what the model lacks, option A with C checked (draft-drift-double-counts-degassing). Before that: v1-finish-12 on hold/v1-finish-11-balance (v1-finish-11 anchored the carbon balance at the end with GEOCARB III weathering laws and literature strength; full Gough alone failed the old <=40% icehouse cap 0/6; the star thermostat passed it only by riding its bound). RULING (owner, PW-865): option C, no icehouse cap, thermostat off. v1-finish-12 re-measures on the new bar (L6 18, L7 8, 2 Gyr 13) with finish diagnostics, then works the wet tropics and end-CO2 spread. Held: hold/v1-finish-10-anchor (inside 11), hold/pw798-ref-freeze.
- Fun (Sonnet): fun-lane-26 (PW-861 humans spread, 851 hybrid fertility, 855 dragons, 854 salt-seeking, 853 continent names). Fun lane 25 merged (6749aa4): Equal Earth overlays, wheel zoom, right-pane summaries and tooltip, workbench timeline, fuels layer, brief in viewer (PW-860, 843, 840, 841, 845, 837; follow-ups PW-863, 864). Fun lane 24 merged (de83743): half-elves through frontier contact and arrival on free land near the partner (PW-852; residual PW-861), fiend framing dropped and dnd tieflings as a 3 kyr human template (PW-858), ruminant diet data and the no-dairy brief line (PW-850/800), tracks overlay removed (PW-857), Results tab per world (PW-842), label depth (PW-839), Equal Earth default (PW-838; overlays missing, PW-860). Kept runs on 2a7385: dnd 62341d and seven_meals bbfba8. Next: the coordinator's pick from PW-840/841/843/845, 851, 855, 853, 854, 837, 861.
- Pick planet for seven_meals: 6fbc2c (peoples run 104de8, may be replaced by fun lane 22).

## v1
- Epic PW-244. Only the owner sign-off PW-780 is open (default `star_brightening` 0.45, a K-type star; provisional owner OK 2026-10-24). 2 open tickets in the v1 milestone.
- Icehouse bar loosened 2026-10-25 (PW-865): icehouse share is uncapped; snowball, hellhole and never-ice fail. The old bar on main's forward star was L6 13/18 and L7 7/8. Rule: ~70% pass, never-ice and always-icebox both fail ([glossary](glossary.md), [decisions](decisions.md)).
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
