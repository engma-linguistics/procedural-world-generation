---
id: PW-742
title: "Culinary brief follow-ups: --all files, default era slices, group ranges per era, route and per-cell fields, schema doc"
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun8
blocked_by: []
relates: [PW-728, PW-726]
refs: [planet/lineages/brief.py, docs/review/lineages/briefs/, docs/proposals/culinary-dnd-intake.md]
created: 2026-10-24
updated: 2026-10-24
---

## Description
`planet brief RUN [--region lat,lon[,r] | --people ID] [--era kyr] [--format md|json] [--out DIR --name N]` ships
(PW-728 first cut, `brief_version` 1). Left for the full ticket, found while building it:
- `--all` (one file per people and per mixing zone into `briefs/<run>/`) and the default era slices (present, 0.5, 1,
  2, 3, 6, 9, 12 kyr): the builder takes one era per call. A `Ctx` opens a run once, so the loop is cheap.
- Groups (steppe orcs, forest orcs, human farmers) have no cells of their own in the run's frames (`peoples*`, `mix_*`
  hold the people, `presence_present.bin` has every line but only at the present). A group's brief at an earlier era
  falls back to its people's range. Store a per-line presence layer for the recent frames, or the groups' share of
  each cell, to give groups their own ranges and shares.
- `since_kyr` of crops and animals is when the region first reached 10% of its land with the stock known; `route`
  (road, wing, sea) is null because the spread does not record how each cell was reached.
- The fuels are the run's present only; the other eras print the present's fuels flagged as such. A fuel layer per
  frame (or a cheaper recompute from the frame's tree cover, herds and crops) gives them per era.
- The world's own layers (soil, biome, rivers, coast, growing months) are those of the world's slice moment, not the
  era (flagged in the JSON as `world_layers_basis`). The time zoom's frames give only the climate class, temperature,
  rain, tree cover and ice per era.
- The neighbours' `tier` (interfertility) and `since_kyr` are null until the contact record exists.
- Null by design until built: salt (a deposit likelihood is under `land.resources`), `trade_reach`, `reputation`,
  `substrate`, honey, mast, fungi, the shelf.
- [ ] a schema doc (field, unit, source, era-dependence) beside the examples

## Updates
- 2026-10-24: Built on branch fun10: `planet brief RUN --all [--eras ...] --out DIR` (people and group briefs per default era slice 0, 0.5, 1, 2, 3, 6, 9, 12 kyr, plus mixing zones), brief_version 3 (ways of life, mineral licks), schema doc docs/review/lineages/briefs/SCHEMA.md. Still open: per-era group ranges (a group falls back to its people's range before the present), fuels per era, route.
- 2026-10-24: Created from inbox draft draft-brief-follow-ups-after-first-cut.md (found by fun8).
