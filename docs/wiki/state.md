# State

**Last updated: 2026-11-01.** Overwrite this page; never append (history is in git). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Release
- **v0.1.0 tagged 2026-11-01** (the v1 milestone, epic PW-244). The physics is good enough to fool a layman and impress a
  climatologist or geologist; the peoples ship as a preview.
- Final tally (lane 102, `docs/review/v1-cut/final-tally.md`, `tools/hard_bar.py`): 42 draws, 0 hard failures (frozen over,
  boiled, ocean loss, CO2 crash under D32 B, below the plants' compensation point). Soft pass L6 29/36, L7 5/6.
- Bars: hard failures must be 0; the soft scorecard is fine at ~60-70% (L7 60% OK for v1; 70%+ is v2, PW-1009). Only "frozen
  over" (40%+ of land under ice) and hellhouse fail; icehouse and glacial maximum (25% of land, the USGS LGM figure) are reported.
- Next tag: v0.2.0 for the v2 milestone.

## Lanes running
<!-- coordinator: fill in at each compaction or lane change -->
- L8 1 Gyr world done (lane 105): run 6a6fd6, finished world 0af5ae, slice 928016, time zoom 7d803e; `docs/review/l8-world/gyr-notes.md`. Shelf still 0.6-1.2% of ocean.
- Lane 100 merged 11-01 (sea level counts ocean-floor sediment; creep/necking/rise off). Lane 112 running: PW-1292 A (sediment piles become continent only against continental crust), then creep re-judged.
- Lane 113 running: richer ticket refs (paper/doc/function forms, check validation, demo backfill on PW-1158 and lane 100 tickets).
- Waiting on Daniel: only his thoughts in the religion doc (https://claude.ai/artifact/Tk4g2nkJPQpTJgeDXo6KoP). Cultures r2 answered (owner-notes-r2.md).
- Next: cultures prep lanes (PW-1280, PW-1254 rulings, PW-1281, PW-1283), then lects v0 + polities v0, PW-908; sources reads PW-1275, PW-1285; D34 B all-biome productivity; refine refactor; PW-1198.
- Up to ~12 sims with >=40 GB free in /tmp. `scratchpad/root` holds symlinks into the main runs/ and zooms/: never write into it.

## Milestones (2026-11-01)
| milestone | open | done |
|---|---|---|
| v1 | 0 | 157 |
| v2 | 384 | 200 |
| v3 | 23 | 4 |
| v4 | 1 | 0 |
| later | 80 | 5 |
| unscheduled | 121 | 297 |

v2 priorities: always one fun lane on peoples/lineages (PW-692 frames the end goal; cultures, languages and polities next per
the proposal), physics lanes take the most useful physics ticket, then speed, resources (PW-155), zoom quality (PW-516).
Roadmap: [plan_next.md](../plan_next.md).

## Current showcases (v0.1.0, lane 110: `docs/review/v010-showcases/notes.md`)
All at L7, `--every 4`, built on main e55316ad.

| Recipe | Run | World | Notes |
|---|---|---|---|
| Earth-like A (seed 11, 1 Gyr) | a19366 | 9459ad | time zoom fc5311, finished world 899985; peoples b4d502 (dnd), 3c1caf (seven_meals) |
| Earth-like B (seed 12, 1.5 Gyr) | 10fd90 | 848662 | time zoom 56dee1, finished world dba204; peoples a24559 (dnd) |
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

## Where to look next
- Open owner decisions: `board.py decisions`.
- Unmerged branches or held work: `git branch --no-merged main` and the lane tickets.
