# State

**Last updated: 2026-11-04** (main 940c338b, after lane 175). Overwrite this page; never append (the history is in the repo log). Refresh the counts with `uv run python issue-tracking/board.py milestones`.

## Release
- **v0.1.0 tagged 2026-11-01** (the v1 milestone, epic PW-244). Hard failures 0 over 42 draws; soft pass L6 29/36, L7 5/6
  (`docs/review/v1-cut/final-tally.md`, `tools/hard_bar.py`). Bars: hard failures 0; soft scorecard ~60-70%.
- **Plan (Daniel 11-03):** v1.0 tagged 1 Dec 2026, when he starts building a Seven Meals campaign world in the viewer. Milestone
  vN = tag v0.N.0: v2 kit (target 10 Nov), v3 states/war/invasions (17 Nov), v4 history that moves, calendars, names slot (23 Nov),
  v5 December world and refine (28 Nov). `docs/review/board/milestones-v2-v5.md`, `december-plan.md`. North star: "reasonably
  stable and not prone to exploding when nudged"; lanes file at most 3 drafts; the backlog is `later`.
- **v0.2.0** waits on Daniel's look. v2 open: PW-728, 856, 1308 (epics/briefs nearly done), PW-1312, PW-1444 (showcase re-runs).
- Physics is a side track: 1-3 passes per scout lane, regional metrics (not global dT), tickets in `later` ranked "physics side track".

## Lanes running (11-04)
- **Lane 170**: D47 C (one carbon yardstick per grid level, weathering on plant cover, frozen-over read at the end); paired judge
  and Earth check before merge. The NPP lever (branch `scout-173-npp`, 19512a3a) waits for it.
- **Lane 176**: the peoples mechanisms ledger (docs plus tests; touches history/, spread.py, ladder.py).
- **Lane 177**: invasions you schedule (PW-1433), polity level, rows in runs/<id>/authored.json; must not touch history/.
- Peoples runs must start from a finished world id, never a time zoom id (no world means no goods, settlements or polities).
- **Languages merged 11-08** (lang-design folded into main, worktrees removed): `planet languages <run>` writes
  languages.json + sidecars; viewer `planet langserve`; guide docs/review/language/ (for-daniel.md, sketches, calibration).
  Leftovers are the language tickets taken in at the merge. Never delete runs a24559, b4d502, 3c1caf (a24559 is the language run).
  11-08 later: owner rulings + syrinx two-voice tone merged (3fb356ff). Open language calls live on the separate Language Desk
  (https://claude.ai/artifact/HYNL244a8zVvfSGFWK5Fgw, db 'answers'), not the Owner's Desk. 11-09: PW-1551 lane merged (dffed688: one sound-change draw, naturalness on a log scale, caps removed; elves long-generation; founder size drift); a24559 language files rebuilt in place. 11-09 morning: lane 4 merged (PW-1557 sonorant codas, PW-1569 case by WALS bins + local series, PW-1570 short function words/pronouns + wear, PW-1571 PRE_FUSE suffixing preference) plus river floors in m3/s (PW-820 units); a24559 rebuilt. Lane 5 merged 11-09 (PW-1545 done, PW-1537 part; 1612db8f), a24559 rebuilt. Lane 6 merged 11-09 (PW-1592 done, PW-1537 mostly; growl envelope and fable-check fixes; PW-1595 left). a24559 rebuilt (pronoun loans at the 0.08 cap, sisters 0.51: watch). Lane 7 merged 11-09 (b50a316c; PW-1546 + PW-1579 done, PW-1586 partial; PW-1600..1602 taken in, PW-1602 spelling looks on the Language Desk as built=A). a24559 rebuilt (616 living; pronoun loans 0.075, sisters 0.535). Lane 8 running: PW-1586 (case seeded at birth) + PW-1600 (joint alignment/number draws) + PW-1595. PW-1549 waits for the other terminal's polities work.
- Merged 11-03/04 (details in [decisions.md](decisions.md)): board triage (v2 382 -> 12), milestones v2-v5, crops cross the sea
  only with colonists or ocean ships, years-ago dates (NumFmt), stable culture uids, cuisine sheet per culture, written faiths and a
  gods disk cache, the workbench tree, polities v0 and war v0 (Polities globe layer, `/api/polities`), summit heights (PW-846),
  scouts 171-173 (summer excess gone, mountains are cell averages, NPP lever held), keyframe streaming (PW-801).
- **Waiting on Daniel**: D49 (PW-1448, writing gate; lean B), the v0.2.0 tag.

## Milestones (2026-11-04)
| milestone | open | done |
|---|---|---|
| v1 | 0 | 157 |
| v2 | 5 | 272 |
| v3 | 7 | 7 |
| v4 | 9 | 1 |
| v5 | 17 | 0 |
| later | 527 | 8 |
| unscheduled | 136 | 303 |

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
