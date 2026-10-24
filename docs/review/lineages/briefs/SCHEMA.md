# Culinary brief schema (brief_version 3)

`planet brief RUN --region lat,lon[,km] | --people ID [--era KYR] [--format md|json]`, or `--all [--eras 0,0.5,...] --out DIR`
(one brief per people and group at each era slice, and per mixing zone at the present, into `DIR/<run>/`). The JSON is the
contract (`planet/lineages/brief.py`, `BRIEF_VERSION`); the Markdown is a reading of it. A key that is `null` is not built yet
(listed under `not_modelled`), never a zero.

"Era" column: **era** = read from the frame nearest the era asked; **present** = the run's last frame whatever the era;
**world** = the world's own slice moment (climate, soil, rivers, coast, goods, resources), not the era; **run** = a run-wide fact.

| Field | Meaning, unit | Source | Era |
|---|---|---|---|
| `brief_version`, `run`, `world`, `tree`, `mode`, `seed`, `code` | provenance: tree name@hash, `fantasy`/`real`, the try's seed, commit | run meta | run |
| `era_kyr`, `era_asked_kyr` | kyr ago of the frame used, and of the request | run frames | era |
| `place` | `lat`, `lon`, `radius_km`, `basis` (a circle, or a people's cells), `cells`, `land_cells`, `area_mkm2`, `land_mkm2`, `landmass` | grid | era |
| `land` | `koppen` shares, `temperature_c`, `precipitation_mm`, `tree_cover_pct`, `elevation_m`, `ice_share`; with a world also `biome`, `soil`, `fertile`, `rivers`, `coast`, `harbour_best`, `growing_months`, `frost_months_est`, `seasons`, `fire_months`, `flood_month`, `mud_months`, `resources` | frames; world layers | climate, tree cover, ice: era; the rest: world (flagged `world_layers_basis`) |
| `bad_years` | droughts and cold spells: `kind`, `kyr_ago`, `years`, `rain_x` or `temperature_c` | the recent pass's episodes | era (inside the recent window) |
| `fuels` | share of each fuel by heads (wood, charcoal, dung, peat, straw, grass, drift, coal, heath, oil, tallow, bone), `lead`, `basis` | `planet fuels` layers | present (flagged) |
| `wild_food` | `foraging`, `grazing`, `timber` goods (0..1 against the world's best), `game` and `wild_crops` range shares, `mast`/`honey`/`fungi` (null) | world goods; animal and crop wild ranges | world / era |
| `fish` | coast fish, fish mix sea/runs/lakes, `river_runs`, `lake_fish`, `sea_mammals` (0..1) | seafood.py goods | world |
| `salt` | `source_share_of_land` (rock, lake, spring, sea, lick), `km_to_salt` mean/p90/max, `nearest_source`, `unreached_share`, `within_100km_share`, `beyond_trade_km_share`, `plant_ash`, `poor` (mean beyond 300 km) | seafood.py (PW-732, PW-746) | world |
| `crops`, `animals` | stocks known in the region: `id`, `label`, `known_share`, `since_kyr` (when 10% of the land knew it), `route` (null), `origin` (first cultivation or taming: kyr ago, lat, lon, people), crops `kind` staple/cuisine | run layers `crop_known`, `animal_known` | era |
| `peoples` | `ways_of_life` (share of heads by way, PW-723, from the composition list), `groups` (at the present only: groups the composition folds into their people, with mean presence over the region, their way and dairy), `list` of `id`, `name`, `share`, `groups_of`, `way`, `body`, `dairy`; `peopled_cells`, `empty_share`, `others_together` | composition layers | era (a group has no frames of its own before the present: it reads its people's range) |
| `animal_foods` | `meat`, `eggs`, `dairy_animals`, `dairy_peoples` (`lactase_share`, `use`: fresh at or above 0.6, else soured and fermented) | animals known x peoples' bodies | era |
| `mixing_zones`, `neighbours`, `events` | where peoples meet; the peoples within `ring_km`; dated events in the window | run meta | present / era |
| `suggested` | `notes` (rule-based; the culinary side overrules), `drink` (null) | this brief only | as its inputs |
| `people` (with `--people`) | `lineage_chain`, `way`, `body`, `demography`, `present`, `homeland`, `story` | run meta | run / present |
| `substrate`, `trade_reach`, `reputation` | null: not modelled | | |
