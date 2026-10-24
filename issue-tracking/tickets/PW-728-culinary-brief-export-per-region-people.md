---
id: PW-728
title: "Culinary brief: export per region, people and era (land, fuels, wild food, fish, salt, crops, animals, peoples, neighbours, substrate, trade reach, events, reputation) as JSON and Markdown"
type: story
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: culinary-intake
blocked_by: []
relates: [PW-722, PW-721, PW-719, PW-475]
refs: [docs/proposals/culinary-dnd-intake.md, planet/lineages/output.py]
created: 2026-10-24
updated: 2026-10-24
---

## Description
The interface between procgen_world and the owner's culinary-dnd repo. Proposal §7 has the schema sketch.

**CLI:** `planet brief RUN [--people ID…] [--region LAT LON --radius-km R] [--at KYR,…] [--format json|md] [--all]`.
- RUN is a peoples run.
- The default era slices are the present plus 0.5, 1, 2, 3, 6, 9 and 12 kyr ago, from the stored frames.
- `--all` writes one file per people and one per mixing zone to `briefs/<run>/`.

**Per region:**
- place, with the nearest highlight in place of a name;
- land: Köppen shares, biome, soil, fertility, rivers, harbour, growing and frost months;
- the bad years from the recent pass;
- fuels (PW-722), wild food (mast, game, honey, fungi), fish and salt (draft-salt-and-sea-food-goods);
- crops (PW-721) and animals (PW-719), each with dates and routes;
- peoples, by composition and group;
- substrate, neighbours and tiers (draft-contact-history-and-interfertility-tiers);
- trade reach (days by road and sea: a cost-distance over the travel and harbour layers);
- events and reputation (draft-reputation-and-exonyms);
- a `suggested` block of rule-based lines ("what ferments follows what's stored"), marked as overrulable.

**Per people:**
- the lineage chain, body, groups;
- homelands per era, migration, refuges, numbers;
- what the land gave it over time;
- the contact record and shared mixing zones;
- what neighbours call it and why;
- its stories.

v0 ships with what exists today: land, goods, peoples, composition, bodies, animals, dairy, land use, neighbours,
mixing zones, the bad years. Later fields are added as their tickets land, behind a `brief_version`.
- [ ] Deterministic.
- [ ] Run id, tree hash and seed in every file.
- [ ] A schema doc.
- [ ] A Markdown rendering readable on its own.

## Updates
- 2026-10-24: fun8: first cut shipped (brief_version 1): planet brief RUN [--region lat,lon[,r] | --people ID] [--era kyr] [--format md|json] [--out DIR --name N]; planet/lineages/brief.py; examples in docs/review/lineages/briefs/. Null by design: salt, trade_reach, reputation, substrate, honey, mast, fungi, tiers. Follow-ups: draft-brief-follow-ups-after-first-cut.
- 2026-10-24: Created from inbox draft draft-culinary-brief-export.md (found by culinary-intake).
