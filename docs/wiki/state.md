# State

**Last updated: 2026-11-10 ~03:00** (main after runner 252). Overwrite this page; never append (the history is in the repo log). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Release
- **v0.1.0 tagged 2026-11-01** (the v1 milestone, epic PW-244). Hard failures 0 over 42 draws; soft pass L6 29/36, L7 5/6
  (`docs/review/v1-cut/final-tally.md`, `tools/hard_bar.py`). Bars: hard failures 0; soft scorecard ~60-70%.
- **Plan (Daniel 11-03):** v1.0 tagged 1 Dec 2026, when he starts building a Seven Meals campaign world in the viewer. Milestone
  vN = tag v0.N.0: v2 kit (target 10 Nov), v3 states/war/invasions (17 Nov), v4 history that moves, calendars, names slot (23 Nov),
  v5 December world and refine (28 Nov). `docs/review/board/milestones-v2-v5.md`, `december-plan.md`. North star: "reasonably
  stable and not prone to exploding when nudged"; lanes file at most 3 drafts; the backlog is `later`.
- **v0.2.0** waits on Daniel's look. v2 open: PW-728, 856, 1308 (epics/briefs nearly done), PW-1312, PW-1444 (showcase re-runs).
- Physics is a side track: 1-3 passes per scout lane, regional metrics (not global dT), tickets in `later` ranked "physics side track".

## Lanes running (11-10 ~11:50)

As of 2026-11-10 evening. Running: 275b (Andes gate, fork queue then judge), 278 (states in the history: five pairs on fix 9306190c, then the flip), 280 (2 Myr time zoom, v1.0). Done today: 276 (v0.3.0 close-out, merged), 277b (everyone experiment, docs only on main).
v0.3.0 tagged (suite 2033 passed); server restarted. Waiting on Daniel: D73-D76 (supply), D77 (extinction).

## Milestones (2026-11-09)
| milestone | open | done |
|---|---|---|
| v1 | 0 | 157 |
| v2 | 4 | 275 |
| v3 | 3 | 15 |
| v4 | 17 | 53 |
| v5 | 17 | 8 |
| later | 546 | 33 |
| unscheduled | 161 | 322 |

Standing priorities: always one fun lane on peoples/lineages (PW-692 frames the end goal; cultures, languages and polities next per
the proposal), physics lanes take the most useful physics ticket, then speed, resources (PW-155), zoom quality (PW-516).
Roadmap: [plan_next.md](../plan_next.md).

## Current showcases (v0.1.0, lane 110: `docs/review/v010-showcases/notes.md`)
All at L7, `--every 4`, built on main e55316ad.

| Recipe | Run | World | Notes |
|---|---|---|---|
| Earth-like A (seed 11, 1 Gyr) | a19366 | 9459ad | time zoom fc5311, finished world 899985; peoples **07c755 (seven_meals), 0141d1 (dnd)** on current code; old b4d502, 3c1caf kept |
| Earth-like B (seed 12, 1.5 Gyr) | 10fd90 | 848662 | time zoom 56dee1, finished world dba204; peoples **3e0eb4 (dnd)**; old a24559 kept (Daniel's language run reads it) |
| Water world (seed 13, 2 Gyr) | f27dc1 | b76c8e | icehouse; soft fail (post-v1 kind) |
| Land-heavy (seed 14, 1 Gyr) | fe954c | 036772 | |
| Cold (seed 15, 1 Gyr) | c9f38c | 0c14eb | icehouse, -6.4 C (as meant) |
| Hothouse (seed 16, 1 Gyr) | 5aa5ff | f9c12a | only +3.5 C: the recipe is weak |

Each world has six highlight zooms (ids in the notes). Also kept: the L8 worlds a16f5a (direct) and fb5e11 (refined from L7
783674, run b13ee9; zoom 361209); the older showcases and owner runs (cc22df 622c00 and the protected list in the coordinator
memory) until Daniel has seen the new set; Earth world 577526 and the nine overturning reference worlds (PW-202).

## Peoples model (v0.1.0 preview)
- Lineages, demes (overlapping per people since lane 109, PW-1259), emergent cultures (PW-670: era-scaled time apart, cohesion by
  kind), in-fighting for every people (D31 A: the commonest people under 50% usually, never over 70% with 5+ peoples), dragons
  round 2 (lion-line persecution, local extirpation, `dragon_abundance` dial), tech tree (PW-675), settlements and mines.
- Peoples-share tuning is paused until war and polities exist (Daniel 10-31).
- Since 11-01: density from one sourced ladder of way of life x tech x land productivity (PW-1275), peoples have no groups (PW-1357), faiths as records with 13 taboo kinds (PW-1306, PW-1311), hunters learn crops slowly and farm-or-forage per cell is next (PW-1373, PW-1385). The brief is still per people, not per culture (PW-1391).

## Where to look next
- Open owner decisions: `board.py decisions`.
- Unmerged branches or held work: `git branch --no-merged main` and the lane tickets.
