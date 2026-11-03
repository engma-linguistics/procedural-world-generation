# State

**Last updated: 2026-11-03** (main 8f7db3e4, housekeeping pass after the fresh-eyes review). Overwrite this page; never append (the history is in the repo log). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Release
- **v0.1.0 tagged 2026-11-01** (the v1 milestone, epic PW-244). The physics is good enough to fool a layman and impress a
  climatologist or geologist; the peoples ship as a preview.
- Final tally (lane 102, `docs/review/v1-cut/final-tally.md`, `tools/hard_bar.py`): 42 draws, 0 hard failures (frozen over,
  boiled, ocean loss, CO2 crash under D32 B, below the plants' compensation point). Soft pass L6 29/36, L7 5/6.
- Bars: hard failures must be 0; the soft scorecard is fine at ~60-70% (L7 60% OK for v1; 70%+ is v2, PW-1009). Only "frozen
  over" (40%+ of land under ice) and hellhouse fail; icehouse and glacial maximum (25% of land, the USGS LGM figure) are reported.
- Next tag: v0.2.0 for the v2 milestone.

## Lanes running (11-03)
- **Lane 141**: rich wild land resists farming, per-person returns sourced from PNW and California (PW-1385 A; the crowding look-around is PW-1388, the forager-farmer trade top-up PW-1386 comes after it).
- **Lane 142**: the North Atlantic is too warm, the ice sheets' lost snow (PW-1381, the next physics fix).
- **Lane 140c**: herb-roots cold-tail screen, a per-part screen of the 2 draws that froze over (PW-1261; lane 140 failed the hard bar, strike 1, not merged).
- Merged since 11-01 (details in [decisions.md](decisions.md)): land zoom sections with seams and rivers (lanes 116, 122, 127-129; a 1 km section 2 h 48 m / 110 GB became 16 min / 86 GB), speed parts 1-2 (PW-252, -11.6% then 15-25% more), the density ladder and no groups (lanes 136+137; D&D humans 56% -> 17% of people), religion slices 1-2 (gods, faiths, 13 taboo kinds, the Religion tab), the orbit fix for finished worlds (PW-1325), the rain's second pass on the overturning's sea (PW-1364, lane 134), hunters learn crops slower (PW-1373 B, lane 139).
- Docs-only lanes merged as diagnoses: 119, 120, 121, 123, 125, 131, 132, 135, 138 (rain inland and coasts, summer heat, plant check, spin-up audit). Three strikes in a row sends a target to the back of the line (rain kernel PW-1363, creep PW-1315, margin flicker PW-1295).
- **Waiting on Daniel**: D44, the fresh-eyes review (food first, PW-1391; PW-1332 B; fewer tickets; a mechanism ledger; which world the book is written on). The faith-spread rule is kept for now (PW-1366). Open calls: `board.py decisions`.
- Next physics: PW-1381, then PW-1332 (grass NPP against weathering) with PW-1261 and PW-1331. Next peoples: PW-1385, then cultures prep (PW-1280, PW-1281, PW-1283) toward lects v0 and polities v0, unless D44 puts the per-culture brief (PW-1391) first.
- Housekeeping 11-03: subsystems `peoples`, `culture`, `food` added to the board (most of the 266 open `timezoom` tickets were peoples work; about 50 genuine time-zoom tickets remain); the open v2 children of the parked ice-age epic PW-470 went to `later` except PW-467; the Earth-only regional residuals and the dragon tail were parked.
- Up to ~12 sims with >=40 GB free in /tmp; in the daytime all lanes together stay within 32 cores and ~90 GB. `scratchpad/root` holds symlinks into the main runs/ and zooms/: never write into it.

## Milestones (2026-11-03)
| milestone | open | done |
|---|---|---|
| v1 | 0 | 157 |
| v2 | 374 | 245 |
| v3 | 24 | 4 |
| v4 | 1 | 0 |
| later | 149 | 5 |
| unscheduled | 134 | 302 |

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
- Since 11-01: density from one sourced ladder of way of life x tech x land productivity (PW-1275), peoples have no groups (PW-1357), faiths as records with 13 taboo kinds (PW-1306, PW-1311), hunters learn crops slowly and farm-or-forage per cell is next (PW-1373, PW-1385). The brief is still per people, not per culture (PW-1391).

## Where to look next
- Open owner decisions: `board.py decisions`.
- Unmerged branches or held work: `git branch --no-merged main` and the lane tickets.
