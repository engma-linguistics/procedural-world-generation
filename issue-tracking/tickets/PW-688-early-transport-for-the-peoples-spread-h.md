---
id: PW-688
title: "Early transport for the peoples' spread: horses (wild range, where and when domesticated) and boats on a rough real-world timeline"
type: story
status: in-progress
parent: PW-103
milestone: v2
subsystem: timezoom
effort: l
impact: high
found_by: daniel
blocked_by: []
relates: [PW-675, PW-683]
refs: []
created: 2026-10-23
updated: 2026-10-23
---

## Description
Owner (2026-10-24): before the tech epic (PW-675), give the spread a few early, basic ways to travel. Today: walking, rafting, canoes from 60 kyr (PW-677), boats from 6 kyr. Add: (1) horses: a wild-horse range from the world (open temperate grassland/steppe, as Equus on Earth), a domestication homeland and date (Earth anchor: the Pontic-Caspian steppe ~5.5 kyr ago), and riding spreading from there, speeding the spread over open land for peoples that take it up (herders, nomads, steppe orcs); (2) a boat ladder on a rough Earth timeline of when each came to be or could have: rafts, dugouts and skin boats, outriggers and sails (~5-3 kyr), planked seagoing ships, open-ocean voyaging (~3-1 kyr), each with its reach and who takes it up (sea share). 'Could have' matters: a fantasy people may get one earlier if its niche rewards it. Fauna is not simulated (PW-184), so the horse's range is derived from the land, with an optional evolutionary note in the story.

## Updates
- 2026-10-24: Part 2 built (branch fun6): craft ladder `animal_defs.craft_ladder` (canoe/outrigger 60 kyr 300 km; planked boat 6 kyr 800 km; sailing ship 3 kyr 2500 km) gating which animals cross the sea; in run.txt, events and stories. People's own crossings unchanged (draft draft-boats-for-peoples-follow-the-craft-ladder). Riding known over 71->35 and 126->63 Mkm2 (fantasy 1df1c3, 3e9e7d). Numbers: docs/proposals/lineages.md.
- 2026-10-23: Status todo -> in-progress. Part 1 horses merged (wild range, taming, riding front, carry). Part 2 boats remains; see PW-702.
- 2026-10-23: Part 1 (horses) built (branch horses-senses, planet/lineages/horses.py): wild range from the land, a drawn taming date (anchor 5.5 kyr) and homeland among herding peoples on the range, a riding front plus carry with peoples, speed x2.5 over open land at full adoption, herders' grazing capacity and land-use pasture up; layers horse_wild and horse_riding, globe layer 'horses', workbench block, stories. Boats (part 2) not started. Follow-up: draft-riding-carried-instantly-across-seas. Numbers in docs/proposals/lineages.md.
- 2026-10-23: Part of the domestication epic filed the same day (horses are its first animal).
- 2026-10-23: Created.
