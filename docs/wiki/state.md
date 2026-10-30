# State

**Last updated: 2026-10-30.** Overwrite this page; never append (history is in git). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Lanes running
<!-- coordinator: fill in at each compaction or lane change -->
- Physics (10-29): lanes 23-25 merged (weld ratchet PW-970; continents' sea water PW-980 part; sea bulk evaporation PW-015 with Earth B 27-28%; paired judge PW-994). Lane 26 running: dry subtropical coasts PW-998 with PW-026 (maritime air inland). Then the PW-980 remainder, PW-948 (needs the owner), showcase rebuild, tag v1.
- Fun (10-29): megafauna PW-958/959/977 stage 1 and sapiens dates PW-978/971 merged. Lane 45 running: people density PW-974 + PW-977 stage 2 (peoples' and predators' share of the food). Owner decisions open: PW-948, PW-990, PW-987, PW-988.
- Fun lane 66 (10-30, branch worktree-agent-a6adfb4eb11252857): settlement size classes now follow the holder's techs (stages villages, towns, cities, cities+roads; town 1,000 or 2,000, city 10,000, city caps from Reba 2016's tables; village and town bands UNVERIFIED pending Fletcher 1995) and second peoples' places churn far less (PW-1114, PW-1117; overview 2.25). PW-1116 (mine count) still waits on the owner.
- Fun lane 68 (10-30): PW-1116 done on its branch: mines go to the cell's most mining-inclined people even as a minority (affinity from traits and kin), one mining district per ring of cells; ~2,200 mines a run became 260-370, humans 95% -> 42-80%; overview 2.25. Rebuilt techtree and settlements on all seven runs with a settlements doc (488d7e 6128a3 114231 570701 6553f1 8d6884 e368d1).
- Up to ~12 sims with >=40 GB free in /tmp.

## v1
- Epic PW-244. PW-780 signed off. 15 open tickets in the v1 milestone (10-29): physics PW-998/026/015/821/969/980; release checks PW-825/932; docs PW-814/816; provenance PW-938/939/940/942. Older backlog grouping (workgroups A-D in the backlog doc https://claude.ai/artifact/8rxpMkD49iovLmeBzZmP4t).
- Icehouse bar loosened 2026-10-25 (PW-865): icehouse share is uncapped; snowball, hellhole and never-ice fail. The old bar on main's forward star was L6 13/18 and L7 7/8. Rule: ~70% pass; since 2026-10-30 only hellhouse and "frozen over" (40%+ of land under ice) fail, and the judges report icehouse, glacial maximum and frozen over (PW-1091; [glossary](glossary.md), [decisions](decisions.md)).
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
- planet/lineages/techtree.py + samples/techtree.toml: 547 techs since fun lane 69 (PW-1122, 10-30): the 594-id catalogue (docs/references/tech-catalogue/, README lists what was merged and dropped) folded in, with `earth_origins` per row, the history's crops and herd animals as techs (crop_wheat, animal_cattle...: wine waits for the vine, the plough for cattle) and `needs_any` (riding: a mount). 4 D&D runs x 2 draws: world firsts farming ~12.5 kyr (history), copper ~6.3, writing ~5.6, cities ~6.4; a living people knows ~250 of 547 now; finds per world ~2.7x Earth's origins (copper ~12 vs 4: better needs did not fix it, needs-decision draft); settlements unchanged in kind (488d7e: 114 -> 113 cities, towns 3,032 -> 3,513). Pottery has a band-justified rate (0.09). Build ~22 s a run.
- The hazard per people, per tech, per kyr: rate x kind rate_x (gnomes 1.5) x culture-domain match (cap 1.5) x S(pool) x ramp.
  - S = ln(pool / 300) / ln(1e5 / 300), Henrich's log with a threshold.
  - pool: the population at the time (from the tracks) x the learners factor (generation / 25 yr, capped at 20: dragons 17, elves 2, dwarves 1.6). For bronze-age-on techs it is x the specialist ladder (0.2% to 10%, a judgement after Childe) x a density term (a judgement after Bettencourt).
  - Domains: the catalogue's eight tags. Aggressive peoples take war techs up by contact x2.
- Band: dates at or before 11.6 kyr (and techs Earth got more than 10 kyr after their prerequisites) are hard floors. Younger techs are soft: their rate is set so the first of anchor_peers = 4 peoples of 10 M meets Earth's lag after the prerequisites (techtree.anchor_check, lane 70). A floored tech with 2+ dated Earth origins (`origins_kyr`) waits after its floor as the median origin did (band_wait, PW-1138; pottery's hand rate is now the rule). late_rate is gone.
- Fun lane 70 (10-30, PW-1137/1138 on its branch): contact is a front at 1 km/yr (Pinhasi et al. 2005; Jordan et al. 2016 for pottery) that reaches the taker's middle after a per-pair delay and then hands over whatever the taker can use, so packages travel together; inventing no longer goes first within a step. 4 runs x 2 draws: finds/origins median 2.75x -> 1.3x (copper 11.8 -> 5.6, writing 7.2 -> 2.5, towns 15 -> 6), world firsts copper 5.8 kyr, writing 4.1, iron 3.6, cities 6.1; living peoples knowing copper/writing/cities ~50% -> ~70%, beer 0% -> 73%.
- Evidence: docs/references/techtree/README.md. Open: drafts for a planet-own glacial gate, the risk effect, contact pools, specialists from the settlement ledger (PW-946); lane 69's drafts: finds vs origins (PW-1124 follow-up), floored techs' slow track rate, ending the history when cultures settle (owner idea), missing pigs/camelids/reindeer, dogs counting as herding, the tree view's size, build time.

## Current showcases
- Owner feedback world (2026-10-24): world 2a7385 (seed 11 L7, run 6b48f5, time zoom f778ab, zooms 1ab4c4 91bf86 cd4341 80a169), peoples b69f51 (seven_meals) and 6b5d0e (dnd). Feedback doc: https://claude.ai/artifact/GMaU7W2PynuiY9z5o71kDA
- Runs: 6c652c, d30069, 99dc70, feaade.
- Worlds: 6fbc2c, 067778, a12762, 6909cb.
- Peoples run 104de8 (`seven_meals` preset) on world 6fbc2c.
- Also kept: Earth world 577526 and the nine overturning reference worlds (119973 28442c 607540 81aced 7082f5 d14b89 a5a387 dad91b c00ebf), per PW-202.
- Viewer defaults (2026-10-30, lane 65): family-hue peoples colours, the current ramps, the docked legend and the grouped "Colour by" picker (globe and zoom) are the only behaviour; the `?palette=`, `?ramps=`, `?legend=` and `?picker=` switches are gone (PW-1032/1027/1029/1026). Screenshots: docs/review/viewer-defaults-10-30/.
- Viewer: http://127.0.0.1:8765/viewer/ (server notes in [coordination.md](../coordination.md)).

## Where to look next
- Open owner decisions: `board.py decisions`.
- Unmerged branches or held work: ask `git branch --no-merged main` and the lane tickets; not tracked here.
