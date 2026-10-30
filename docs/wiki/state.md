# State

**Last updated: 2026-10-28.** Overwrite this page; never append (history is in git). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Lanes running
<!-- coordinator: fill in at each compaction or lane change -->
- Physics (10-29): lanes 23-25 merged (weld ratchet PW-970; continents' sea water PW-980 part; sea bulk evaporation PW-015 with Earth B 27-28%; paired judge PW-994). Lane 26 running: dry subtropical coasts PW-998 with PW-026 (maritime air inland). Then the PW-980 remainder, PW-948 (needs the owner), showcase rebuild, tag v1.
- Fun (10-29): megafauna PW-958/959/977 stage 1 and sapiens dates PW-978/971 merged. Lane 45 running: people density PW-974 + PW-977 stage 2 (peoples' and predators' share of the food). Owner decisions open: PW-948, PW-990, PW-987, PW-988.
- Up to ~12 sims with >=40 GB free in /tmp.

## v1
- Epic PW-244. PW-780 signed off. 15 open tickets in the v1 milestone (10-29): physics PW-998/026/015/821/969/980; release checks PW-825/932; docs PW-814/816; provenance PW-938/939/940/942. Older backlog grouping (workgroups A-D in the backlog doc https://claude.ai/artifact/8rxpMkD49iovLmeBzZmP4t).
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

## Tech tree (PW-675; v1 invention model, lane 64, 2026-10-30)
- planet/lineages/techtree.py + samples/techtree.toml: about 100 techs, still a prototype list (the 594-row catalogue in docs/references/tech-catalogue/ is not yet ingested: draft-techtree-catalogue-ingest-v1).
- The hazard per people, per tech, per kyr: rate x kind rate_x (gnomes 1.5) x culture-domain match (cap 1.5) x S(pool) x ramp.
  - S = ln(pool / 300) / ln(1e5 / 300), Henrich's log with a threshold.
  - pool: the population at the time (from the tracks) x the learners factor (generation / 25 yr, capped at 20: dragons 17, elves 2, dwarves 1.6). For bronze-age-on techs it is x the specialist ladder (0.2% to 10%, a judgement after Childe) x a density term (a judgement after Bettencourt).
  - Domains: the catalogue's eight tags. Aggressive peoples take war techs up by contact x2.
- Band: dates at or before 11.6 kyr (and techs Earth got more than 10 kyr after their prerequisites) are hard floors. Younger techs are soft: their rate is set so a 10 M people meets Earth's lag after the prerequisites (techtree.anchor_check: towns, copper, writing, iron within ~20%). late_rate is gone.
- Evidence: docs/references/techtree/README.md. Open: drafts for a planet-own glacial gate, the risk effect, contact pools, specialists from the settlement ledger (PW-946), and too many independent copper finds.

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
