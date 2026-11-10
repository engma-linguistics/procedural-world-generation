# Glossary

Project vocabulary. Geology and climate terms: the glossary in [overview section 7](../overview.md). Mechanics of each item: the overview section or the ticket named.

## Stores and zooms
- **run**: a simulation of a planet over 0.5-2 Gyr (`planet simulate`), with keyframes and checkpoints. Id = 6 hex. Folder `runs/<id>/`.
- **world**: one moment of a run, sliced and finished (climate, rivers, lakes, biomes, waves, tides). `worlds/<id>.json`. Made by `planet slice` or `planet make`.
- **regional zoom** (zoom): a world refined to 1-4 km/px over a region (`zooms/<id>/`). A **fine zoom** nests inside one (tens of m/px; PW-129, PW-516).
- **time zoom**: 2 Myr of glacial cycles (PW-1661; was 1 Myr) (ice ages) replayed from a run moment. A world's "now" is picked from it (PW-479, `--now interglacial`).
- **highlights**: detectors that pick interesting places and pre-make zooms (`planet highlights`).
- **L5 / L6 / L7 / L8**: icosphere grid level. L6 = 41k cells, ~110 km (quick tests, ~6 min per Gyr); L7 = 164k cells, ~55 km (showcases, 35-40 min per Gyr quiet, ~50 under load). Costs: the run-costs table in [coordination.md](../coordination.md).

## Peoples (`planet/lineages/`; the spec's docstring in `planet/lineages/spec.py` is the reference)
- **peoples run**: a lineage history computed on a finished world (and its time zoom); listed in the viewer's Peoples panel. Proposal: [lineages.md](../proposals/lineages.md); intake: [culinary-dnd-intake.md](../proposals/culinary-dnd-intake.md).
- **preset**: a TOML tree in `planet/lineages/samples/` (`dnd.toml`, `seven_meals.toml`).
- **tech tree** (PW-675 v0): `planet/lineages/samples/techtree.toml` read by `lineages/techtree.py` after a peoples run: tracks, techs with needs, land goods and a real-world earliest date (sources in the file and in [the review](../review/techtree/techtree.md)). **kit**: what an arrival (gnomes, elves) brings; **elder kind**: dragons and true giants, who may reach a tech before its ordinary earliest date. Viewer: the Technology tab of `lineages.html`; `planet techtree RUN` adds it to a stored run.
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
- **icehouse**: permanent polar ice sheets (Earth today): ice holding at least 20 m of sea level. A run's icehouse share is reported, not capped (owner 2026-10-25, PW-865; it was ~40% before).
- **glacial maximum**: an ice-age peak, roughly Earth at its coldest (the Last Glacial Maximum, ~25% of land under ice). Reported (owner 2026-10-30, PW-1091).
- **frozen over**: 40% or more of the LAND under ice. A fail for an Earth-like world when the world ENDS frozen: at or above 40% at the run's end (so also when it stays frozen to the end) with no finish-window moment passing the finish's land-ice check (owner 11-03, D47, PW-1425). A frozen moment that recovers is reported, not a failure: the peak in the hard-bar window (the star's forcing within 2 C of the finish's and the run's last 300 Myr, whichever is narrower, `tools/ice_criteria.py` `hard_window`, PW-1142) as `frozen_peak`, and a spell under the dim young star (a dim-era icehouse, like Earth's Cryogenian) as `frozen_over_any`. The only ice term that fails a world (PW-1091). Replaces "icebox", which read ice volume (sea level) only.
- **icehouse bar**: ~70% of seed-draws pass, not all (outlier worlds allowed; "not worse" means the pass share doesn't drop). Hellhouse and frozen over fail; never-ice is reported (PW-780, PW-1091; the star thermostat idea is PW-791).
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
