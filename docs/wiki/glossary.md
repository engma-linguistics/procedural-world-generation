# Glossary

Project vocabulary. Geology and climate terms: the glossary in [overview section 7](../overview.md). Mechanics of each item: the overview section or the ticket named.

## Stores and zooms
- **run**: a simulation of a planet over 0.5-2 Gyr (`planet simulate`), with keyframes and checkpoints. Id = 6 hex. Folder `runs/<id>/`.
- **world**: one moment of a run, sliced and finished (climate, rivers, lakes, biomes, waves, tides). `worlds/<id>.json`. Made by `planet slice` or `planet make`.
- **regional zoom** (zoom): a world refined to 1-4 km/px over a region (`zooms/<id>/`). A **fine zoom** nests inside one (tens of m/px; PW-129, PW-516).
- **time zoom**: 1 Myr of glacial cycles (ice ages) replayed from a run moment. A world's "now" is picked from it (PW-479, `--now interglacial`).
- **highlights**: detectors that pick interesting places and pre-make zooms (`planet highlights`).
- **L5 / L6 / L7 / L8**: icosphere grid level. L6 = 41k cells, ~110 km (quick tests, ~6 min per Gyr); L7 = 164k cells, ~55 km (showcases, 30-50 min per Gyr). Costs: the run-costs table in [coordination.md](../coordination.md).

## Peoples (`planet/lineages/`; the spec's docstring in `planet/lineages/spec.py` is the reference)
- **peoples run**: a lineage history computed on a finished world (and its time zoom); listed in the viewer's Peoples panel. Proposal: [lineages.md](../proposals/lineages.md); intake: [culinary-dnd-intake.md](../proposals/culinary-dnd-intake.md).
- **preset**: a TOML tree in `planet/lineages/samples/` (`dnd.toml`, `seven_meals.toml`).
- **line** (`[[lineage]]`): one node of the tree: `origin` root / split / arrival / hybrid / template / group, plus a time `at` (years before present).
- **people**: a living line, with niche, traits and range. The tree is a DAG; unset fields inherit from the first parent.
- **group** (culture): a way of life inside one people (`group_of`): steppe vs forest orcs. Not a split; mixes freely and rolls up into its people (PW-776; deeper culture is PW-661).
- **template**: an overlay on host peoples from `at` on (tieflings): a share of the hosts, spread from a few sites.
- **hybrid**: two parents. `contact = true` (default): exists only where both meet, in a shared cell or on a frontier (a cell of one beside a cell of the other, PW-852; half-elves), and an arrival whose hybrid is wanted lands about 600 km from the other parent; `linger = false`: gone once the parents part; `contact = false`: founds its own people.
- **arrival**: a line from outside the world (feywild, planes), at a `place` or its best habitat; optionally through portals (PW-697).
- **realm**: `land` (default), `coast` (shelf, tidal flats: merfolk) or `sea` (open water by depth band: storm giants) (PW-775).
- **way of life**: what a people or group does for a living (forage, farm, herd, sail...), expressed by `[[use]]` entries and the land goods it wants.
- **brief**: the generated per-people summary of a peoples run for the consumer (`planet/lineages/brief.py`); examples in `docs/review/lineages/briefs/`.
- **culinary-dnd**: the owner's north-star consumer repo (read-only here); PW-692 frames priorities.

## Bars and checks
- **icehouse**: share of a run's time under ice-age conditions. Reported, not capped (owner 2026-10-25, PW-865; it was ~40% before).
- **icehouse bar**: ~70% of seed-draws pass, not all (outlier worlds allowed; "not worse" means the pass share doesn't drop). Never-ice and always-icebox both fail for Earth-like worlds (PW-780; the star thermostat idea is PW-791).
- **strict bar**: the stricter pass criteria in PW-780's sign-off (numbers in [state.md](state.md)).
- **scorecard / earth_check**: `tools/scorecard.py` after model changes, `tools/earth_check.py` after climate changes. Earth is a plausibility anchor, never a parity target.
- **golden**: stored test outputs in `tests/golden/`; update with `--update-golden` only for purposeful changes.

## Process
- **lane**: one stream of work in its own worktree. One serial run-physics lane (anything that changes `simulate` outputs) plus parallel lanes (viewer, zoom, fun/peoples, docs...).
- **coordinator**: the main session that briefs lanes, merges, numbers drafts and answers the owner.
- **draft / inbox / intake**: subagents write `issue-tracking/inbox/draft-<slug>.md`; the coordinator runs `board.py intake` to number them. Subagents never assign PW- ids.
- **needs-decision**: ticket status for an owner judgement call; options and the coordinator's lean are in the Description (`board.py decisions`).
- **RULING**: the tag for an owner or coordinator ruling in ticket Updates, mirrored in [decisions.md](decisions.md).
- **fun lane**: the always-on v2 lane on peoples/lineage features.
