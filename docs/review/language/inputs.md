# Language engine inputs: what a stored peoples run holds (a24559)

Map of the data `planet/language/` reads, so builders need not open the files. All paths relative to the worktree. Example
values are from `runs/a24559` (dnd preset, world `dba204`, time zoom `56dee1`, L7 grid: 163,842 cells, `cell_size_km` 60,
cell area 3,113 km² = 4πR²/n). No design here: inputs only. "GAP" marks something the engine needs that is not stored.

## 0. Read this first: time, frames, staleness

- **Time axis**: every pass file uses **kyr ago, positive, larger = older** (`born_kyr`, `ended_kyr`, `ago_kyr`). run.json
  `frames[].t` is the same instant **negated** (`t = -ago`, kyr). `meta.time_unit` = `"kyr"`. The present is `ago = 0.0`
  (run.json frame 146, `t = 0.0`). `meta.now_kyr` = 202.0 is the time zoom's own clock, NOT "the present"; ignore it.
- **run.json frames**: 147 (`meta.frames`), from `t = -20202` (20.2 Myr) to 0; the deep ones are Myr apart, `t = -202.0`
  occurs twice (frames 42, 43: time zoom handover; demes.py takes the later).
- **demes.json / cultures.json frames**: 106, `from_kyr` 300.0 (`demes.WINDOW_KYR`). Spacing: 300, 250, 202, then **4 kyr**
  from 202 to 30 kyr ago (glacial zoom), then **0.5 kyr** from 30.0 to 0.0 (recent pass: 61 frames). So the last 20 kyr is
  41 frames 0.5 kyr apart. Map a demes frame to a run frame by matching `ago == -t` (take the later index on a repeat).
- **eraq / land-use inputs**: only frames with `ago <= 12.5` (26 frames, `meta.eraq.frames` = run frame indices 121..146).
- **a24559 is stale vs HEAD** (made at commit `38dc06c9`, `meta.code`): it still has **way-of-life groups** (`human_farmer`,
  `human_herder`, `human_nomad`, `human_seafarer`, `human_arctic`, `forest_orc`, `steppe_orc`, `hill_dwarf`) and the **city
  groups** `city_goblin`, `city_kobold`, all removed since (PW-1357, PW-1369; the current `samples/dnd.toml` has none). Its
  `gods.json` lacks `faiths` and `frames` (added by PW-1358; the server re-derives gods in memory, `server.gods_doc` 243). Its
  settlements still carry `quarters` (gone from `settlements._document` 705). Code against fields present in both, and do not
  key anything on group ids.
- **Do not re-run `planet demes a24559` casually**: it rewrites demes.json in place (runs/ is a symlink to the owner's data)
  and current demes.py may renumber deme ids, breaking cultures.json, gods.json and any languages.json keyed on them.

## 1. demes.json (the deme tree)

Writer: `planet/lineages/demes.py::_document` (915-976), written by `write` (1003-1024). Top level
(`demes.py:966`): `{"format": "procgen-demes/1", "from_kyr": 300.0, "frames": [106 floats, kyr ago, descending],
"demes": [871], "events": [1059], "pairs": [3000]}`. Summary copy in run.json `meta.demes` (count, alive, by_people,
constants, `generated_in_s` 58.5, `occupied_from` "presence").

**Deme record** (id = list index; trimmed real example):
```json
{"id": 0, "people": "tortle", "n": 1, "name": "tortle 1 (the south of Simath)", "short": "tortle 1",
 "place": "the south of Simath", "lat": 13.5, "lon": -126.0, "parent": null, "parent_people": null,
 "born_kyr": 300.0, "how": "first", "settled_kyr": null, "ended_kyr": null, "end": null, "into": null,
 "adapted": null, "learned_share": 0.022, "peak_cells": 351, "peak_kyr": 300.0, "cells_now": 134,
 "series": [[300.0, 351], [190.0, 209], ..., [0.0, 134]], "color": "#3824db"}
```
- `people`: lineage id (run.json `meta.lineages[].id`). Only **whole peoples** are cut (`demes.peoples_of` 783): no groups,
  no overlays (`half_elf`, `half_orc`, `genasi`, `tiefling`, `aasimar` have **no demes**), no templates. Stems that were alive
  in the window do have demes (`archaic_human` 1, `giantkin` 10, `elemental_giant` 4, `greater_goblinoid` 2).
- `parent` (deme id or null), `parent_people` (that deme's people). `how` (how it was born): `first` 110, `split_adapted`
  413, `split_distance` 158, `split_gap` 127, `crossing` 42, `from_people` 21. `n`: 1-based index within its people.
- `lat`/`lon`: centroid **at its peak**, replaced by the present centroid if alive (`demes.py:404-412`). `place`: "the
  <part> of <landmass called>" (`_place` 897), from `meta.present.landmasses`.
- `born_kyr`/`ended_kyr`: kyr ago; `ended_kyr` null = alive now. `end`: null | `fused` (199) | `extinct` (99); `into`: the
  deme it fused into (same people in all 199 cases).
- `settled_kyr`: for a piece cut off by a gap, when its land was first settled (540 non-null).
- `adapted`: biome class of learned country (PW-1155) or null: temperate 182, desert 58, continental 52, steppe 43, subarctic
  33, high mountain 16, savanna 15, tropical wet 14, polar 6. `learned_share`: share of its cells on learned country.
- `series`: `[[ago_kyr, cells], ...]` **thinned to 24 points** (`SERIES_KEEP`); `peak_cells`, `peak_kyr`, `cells_now`.
  Units are **cells**, not people (see GAP below). For every frame use `layers/demes_all.bin` (below).

**Events** (sorted oldest first): `{"ago_kyr", "kind", "deme", "other", "lat", "lon", "cells", "confirmed_kyr"?, "text"}`.
For splits/crossing/from_people `deme` = the new deme, `other` = its parent; for `fusion` `deme` = the one that kept its id,
`other` = the one absorbed ("dragonborn 14 took in dragonborn 18"); `extinct` has `other` null. `confirmed_kyr` (739 events):
the frame at which a gap split or fusion had held `PERSIST` = 4 frames; `ago_kyr` is backdated to when it began. Kinds:
split_adapted 413, fusion 199, split_distance 158, split_gap 127, extinct 99, crossing 42, from_people 21.

**Pairs** (deme contact over time, `_contacts` 758, `_document` 938-950): `{"a", "b", "same_people", "first_kyr",
"last_kyr", "frames", "peak", "border_now", "shared_now", "series": [[ago_kyr, border, shared], ...]}` (series thinned to 24).
- `border`: number of **land cell edges** where neighbouring cells' **leading** peoples are demes a and b. `shared`: number of
  **cells both demes live in** (co-presence from the presence table). Both are counts, no km. `peak` = max(border + shared).
- Only the top `PAIRS_KEEP` = 3000 pairs by `peak * frames` are kept: 2827 between peoples, only **173 same-people** (touching
  sister demes tend to fuse). 1955 pairs are in contact at the present (`last_kyr` 0). `frames`: frames in contact (max 106).

**Per-frame cells of every deme**: `layers/demes_all.bin` (`<u2`), aligned entry-for-entry with the presence table
(run.json `meta.presence`, read with `planet/lineages/output.py::read_presence` 221 or `read_presence_frame` 234):
for run frame `f`, line index `k`, entries `offsets[f,k]:offsets[f,k+1]` of `cells` (`<u4` here), `share` (uint8, % of the
cell's habitat that people holds, >= 12) and `demes_all` (deme id, 65535 none or a frame before 300 kyr). Verified: summing
present-frame human entries by deme reproduces `cells_now`. `layers/demes.bin` (uint16, (147, n)): the deme of each cell's
**leading** people only. The brief and cultures code show the read pattern (`brief.py::Ctx.overlap` 143, `_cultures` 1163).

**Counts (a24559)**
- 871 demes; **573 alive at the present**; **452 alive at 20.0 kyr ago**. Every present deme traces back to one of 395
  distinct 20-kyr ancestors. 262 demes were born and 141 ended in the last 20 kyr.
- Alive now by top stem: mammalian 247, reptilian 228, avian 50, arrivals elf 23 (elf 20, drow 2, sea elf 1), gnome 17,
  triton 8. **Humans: 92 alive of 113** (31,548 cells now). Dragons (10 kinds) 165 alive, true giants 45, kobolds 52,
  dragonborn 49, halflings 27, kenku 26, aarakocra 24, elves 20.
- Alive now per people: human 92, kobold 52, dragonborn 49, halfling 27, kenku 26, aarakocra 24, elf 20, gnome 17, silver
  dragon 16, firbolg 16, hobgoblin 15, blue 14, gold 14, bronze 12, white 12, orc 12, hill giant 11, brass 11, copper 11,
  storm giant 11, green 10, red 10, cloud giant 10, tabaxi 9, dwarf 9, goliath 9, triton 8, tortle 7, fire giant 7,
  leonin 6, black 6, frost giant 6, lizardfolk 4, goblin 4, bugbear 3, drow 2, sea elf 1. Troglodytes extinct (60 kyr).

**Quirks**
- **No deme is a true root**: all 110 parentless demes are `how = "first"` at **300 kyr** (the window start). Deeper ancestry
  is only at people level (run.json `meta.lineages[].parents`, section 2).
- **Arrivals get a wrong deme parent**: a new people's first demes take the deme of its tree parent, "else the deme that
  led most of those cells" (`demes.py` docstring; `_from_people` 615). Arrivals have no tree parent, so `gnome` demes have
  parents of `kobold`, `dragonborn`, `goliath`, `hill_giant`, `kenku` (50 kyr); `elf` of `hill_giant`, `gnome`, `goliath`,
  `dragonborn`, `kenku`, `green_dragon` (25 kyr); `triton` of `bronze_dragon` (6 kyr). Of the 21 `from_people` demes only
  these are real descent: fire_giant<-elemental_giant, hobgoblin/bugbear<-greater_goblinoid, firbolg<-giantkin,
  human/halfling<-archaic_human, drow/sea_elf<-elf. Treat `run.json lineage.origin == "arrival"` as "no deme parent".
- No zero-cell living demes (min `cells_now` 2, max 4,271). Demes overlap freely (several peoples per cell).
- A deme's `lat/lon` is a single point; its cells per frame come only from demes_all.

## 2. run.json: the lineage spec and peoples

`meta.lineages` (69 entries, writer `output.py:139-150`) is the resolved per-line record; `meta.tree` is the raw tree
(`spec.to_raw`, keys `meta`, `lineage`[69], `exonym`, `event`, `interfertile`, `wish`, `use`).

**Line record keys**: `index` (the uint8 id used in every layer), `id`, `name`, `origin` (root | split | arrival | hybrid |
template | group), `parents` [ids], `ago_kyr` (birth), `sapient_kyr`, `group_of`, `groups` [ids], `cities`, `extinct_kyr`,
`overlay`, `realm` (land | coast | sea; note tritons are stored `land`, storm giants `coast`), `traits`, `color`, `leaf`,
`started_kyr`, `ended_kyr`, `origin_place` {cell, lat, lon, ago_kyr, epoch, why}, `track` (centroid path, `[ago, lat, lon,
.., ..]`), `reached` {landmass rank: {ago_kyr, how, gap_km?}}, `crossings`, `story` (prose), `demography` {density
(people/km² mean over its present land), explore, sea_share, insularity, contest}, `speed_kmyr`, `body`, `way`,
`generation_yr`, `life_history` {adult_yr, lifespan_yr, stage_end, fertile, breeding, survival, by_era{era:{T, r, R0..}}},
`life_eras` {forager | horticulturalist | agrarian: kyr ago it entered}, `waves`, `faded_patches`.

**Tree** (origin, parents, born kyr ago): reptilian root 20000 -> draconic 19500 (sapient 5000) -> {chromatic_dragon,
metallic_dragon} 2500 -> 10 dragon kinds 750; draconic -> kobold 350, dragonborn 300. reptilian -> saurian 19500 (sapient
4500) -> tortle 4200, lizardfolk 2500, troglodyte 2500 (extinct 60). mammalian root 10000 -> feline 4000 (sapient 2000) ->
tabaxi 1200, leonin 900; hominid 4000 (sapient 1600) -> giantkin 1100 -> true_giant 1000 -> hill_giant 900, sky_giant 800
(-> cloud 400, storm 300), elemental_giant 700 (-> frost 350, fire 250); giantkin -> goliath 300, firbolg 200; hominid -> orc
700, dwarf 500, archaic_human 400 -> human 200, halfling 100; mammalian -> goblinoid 2500 (sapient 1200) -> goblin 400,
greater_goblinoid 600 -> hobgoblin 250, bugbear 200. avian root 6000 (sapient 2000) -> aarakocra 900, kenku 400. Arrivals:
gnome 50, elf 25 (-> drow 12, sea_elf 8), triton 6. Hybrids (overlay): half_elf, half_orc 10. Templates (overlay): genasi 4,
tiefling 3, aasimar 2. Groups (stale, section 0): human_arctic 30, forest_orc/steppe_orc/human_farmer 9, hill_dwarf 8,
human_herder 8, human_seafarer 6, city_goblin/city_kobold 5, human_nomad 5. `sapient_kyr` is a marker only (PW-965).

**Body inheritance** (`spec.py:952-954`): `bgiven = parse_body(r.get("body"), lid)`; `body = {**base.body, **bgiven}` where
`base` is the **first parent** (else `BODY_DEFAULT`, `spec.py:241`). `parse_body` (255-287) only validates the keys given:
bools (or a 0..1 share for population-frequency traits like `milk`), `fire`/`milks` strict bool, `toxic` list of
`TOXINS`, the rest one of `BODY_CHOICES`. Keys: sweet, milk, milks, capsaicin, bitter, smell, diet, raw_meat, cellulose,
toxic, suction, teeth, gut, salt, display, shed, display_sex, hours, thermo, fire, grain. The stored line `body` is resolved
(all keys); `meta.tree.lineage[].body` holds only what each line gave. `way` inherits the same way (`spec.py:997`); `realm`
from a split's parent; `LIFE_KEYS` (adult_yr, lifespan_yr, breeding, fertile_yr, survival, mortality, `spec.py:763`) by
splits and groups. There is no "stem"/"kind" key: a stem is any non-leaf line; `kind` in dnd.toml is the density-ladder
kind factor inside `demography` (PW-1275), and `cohesion` (dragons 0.9) is read by cultures.py.

**generation_yr** stored = `History.gen_yr(l)` (`history/peoples.py:37`): a flying megafauna (dragons) from
`dragon_ages.generation_yr` (mode `line` here: the line's own 430), else `life_history.generation_yr` (123): **T of the
forager life table where the line has canon ages** (`adult_yr`, `lifespan_yr`), else the line's `generation_yr` (default
`spec.GENERATION_YR` 25). Values (yr; generations in 20 kyr): tortle 23.5 (851), lizardfolk 21.3 (940), troglodyte 25,
tabaxi 27.7 (722), **aarakocra 5.8 (3,437)** (tree says 25; brood breeding, adult at 3 yr), leonin 27.7, 10 dragons **430
(47)**, hill/cloud/storm/frost/fire giant 65 (308), orc 18.0 (1,109), dwarf 70.8 (283), goblin 13.1 (1,528), kenku 19.3
(1,038), **kobold 11.7 (1,712)**, dragonborn 24.7 (810), goliath 27.7, hobgoblin 27.7, bugbear 25.7 (778), firbolg 83.7
(239), human 27.7 (722), halfling 30.1 (665), gnome 60.3 (332), **elf/drow/sea elf 144.9 (138)**, triton 37.2 (538),
half_elf 41.0, half_orc 23.1, genasi/tiefling/aasimar 25.0.

**Populations**: `meta.present.lines[id]` = {area_mkm2, patches, largest_patch_share, centroid, neighbours, population
(heads now, e.g. human 128,705,455), density, band_km2, by_landmass {rank: heads}}. `meta.present.landmasses[]` =
{rank, kind, area_mkm2, lat, lon, name, called, discovered, settled_by, arrivals[], population{id: heads}}. Groups are
counted apart from their people there (human 34.2 M on Simath, human_farmer another 34.5 M).

**Way of life**: per line `way` (spec.WAYS: forager, fisher_forager, horticulturalist, farmer, pastoral_nomad, transhumant,
agro_pastoral, sea_nomad); most peoples have `null` (from traits). Set in a24559: human farmer, halfling forager,
archaic_human forager, hill_giant pastoral_nomad, hobgoblin agro_pastoral, elf/drow/sea_elf horticulturalist, and the groups
(human_herder transhumant, human_nomad/steppe_orc pastoral_nomad, human_seafarer fisher_forager, ...). `traits` carry niche:
flies, swims, coastal, mountain, subterranean, miner, hunter, nomadic, seafaring, agricultural, insular, cosmopolitan,
denning, sea_hunter, hardy. Per cell: `groups_best` layer (the group with most presence, (147, n) uint8) and
`groups_best_pct`; per culture `traits.ways_now` (section 4). On HEAD the ways come from the density ladder (`ladder.py`),
not groups.

## 3. Shift triggers: substrate, incursions, conquests, reputation

All **people-level**, in run.json `meta.contacts` (writer `contacts.py::Contacts.summary` 191-225) and
`meta.present.reputation` (`reputation.build` 225, called at `output.py:152`). Nothing at deme level. GAP: no polities, no
"who ruled whom" (reputation docstring: "Not yet read: polities (PW-661)").

- `meta.contacts.pairs` (808, people pairs incl. stems): `{"a", "b", "tier" (T0..T3), "stage" (viable | absorbed | sterile |
  impossible), "hybrid_fertility", "mixed_people" (e.g. human+elf -> "half_elf"), "split_kyr", "first_contact_kyr",
  "years_in_contact" (yr), "in_contact_now", "border_km_now", "border_km_peak", "mixed_pct_now", "kind" (e.g. "closed
  country"), "series": [[ago_kyr, border_km, mixed_pct], ...]}`. human/elf: first 25 kyr, 25,250 yr, border 56,190 km, 32.3%.
- `meta.contacts.substrate` {people: {cells, first_here_share, held_before: [{id, cells, share, held_until_kyr}] (top 6)}}:
  who held the people's present cells before, and until when.
- `meta.contacts.incursions` (180 kept, `INCURSION_KEEP` 200; all within the last 98 kyr, most < 6 kyr):
  ```json
  {"by": "goblin", "over": "human", "kind": "displacement", "ago_kyr": 1.17, "span_kyr": 0.5, "cells": 38,
   "mkm2": 0.118, "gain": 0.102, "local_share": 0.447, "lat": -3.87, "lon": 93.88, "from_deg": 334}
  ```
  `kind`: `settled_among` 148 (the newcomer rises among a host that still leads; `from_deg` null) or `displacement` 32 (the
  old people lose the cells). `gain`: share of the taker's own range; `local_share`: of the loser's land within 1000 km.
  `by`/`over` may be groups or overlays (`half_elf` over `human` 0.59 kyr). Map to demes by the `lat/lon` and the frame at
  `ago_kyr` (demes_all of `by` and `over` there).
- Authored conquests: `meta.tree.event` = `[]` in a24559 (`reputation.parse_events`: {kind, by, over, at, strength}).
- **Reputation / exonym v0**: `meta.present.reputation` = {"params", "rows": {observer: {subject: row}}}, 36 observers.
  Row: `{"category": "goblin_menace" | null, "name": "the goblin menace", "valence": feared | despised | exotic | edge |
  neighbour, "basis": "incursion (derived): goblin settled among tabaxi on 197 cells in 2 kyr (92% of tabaxi's land
  nearby), from the west", "since_kyr": 1.47, "strength": 0.542, "lumped_with": [], "tier": "T3", "from_dir": "west",
  "borrowed_from"?, "text"}`. Valences: exotic 576, neighbour 394, edge 78, feared 21, despised 17. `neighbour` -> `name` is
  the subject's own label ("humans call aarakocra by their own name"); otherwise the label of the best-matching
  `meta.tree.exonym` row: devil, demon, giant_kin, sea_elves, fae ("the fair folk"), goblin_menace, raiders, lesser_folk,
  strangers ("foreigners"), edge_folk. Names are English labels; no generated words yet.
- Site level: settlements `holders` (section 5) record every change of hands of a site (who held it from when); `why` =
  "driven out by the <people>" when abandoned after a change of holder. The nearest stored thing to a local takeover.

## 4. cultures.json

Writer: `cultures.py::document` (381-463), `write` (520-546). Top: `{"format", "from_kyr": 300.0, "frames": [106],
"cultures": [773], "merges": [375], "deme_culture": [871]}`. `deme_culture[deme_id]` = culture id (-1 none). Most cultures
are one deme (743 of 773); a culture is a run of demes along the deme tree. 305 alive now. `how`: adapted 413, apart 318,
founding 42.
```json
{"id": 98, "people": "human", "n": 1, "name": "first humans of the west of Simath", "how": "founding", "parent": 60,
 "parent_people": "archaic_human", "born_kyr": 198.0, "cohesion": 0.0, "ended_kyr": null, "end": null, "into": null,
 "demes": [177], "adapted": null, "founded_by": null, "place": "the west of Simath", "lat": 45.6, "lon": 166.1,
 "country_now": "temperate", "cells_now": 762, "cells_held_now": 1321, "area_mkm2": 4.112, "peak_cells": 1112,
 "last_seen_kyr": 0.0, "traits": {"body": [], "cultural": ["agricultural", "seafaring", "cosmopolitan"],
 "sea_craft": {"start": 0.6, "now": 0.647, "fit_now": 0.651, "verdict": "kept"}, "open_country": {...},
 "ways_start": {"human": 1.0}, "ways_now": {"human_herder": 0.324, "human_farmer": 0.251, ...}},
 "changes": ["took up the ways of the human herders"], "series": [[198.0, 143, 0.6, 0.0], ...], "color": "#ff0064"}
```
- `series`: `[ago_kyr, cells, sea_craft, open_country]`, thinned to 24. `end`: null | merged | died out; `into` culture id.
- `merges`: `{"ago_kyr", "culture", "into", "why": contact | states, "area_mkm2", "contact_kyr", "text"}` (344 contact, 31
  states: one state's reach, `REACH_MKM2` law 5, cities 1).
- `name` is an English placeholder (brief header says "placeholder names"). No prestige, no population, no city field:
  GAP. Proxies: `cells_held_now`, `area_mkm2`, the people's density, settlements on its cells, techtree known (`cities`,
  `writing`, `law`).

## 5. settlements.json (34 MB; sampled)

Writer: `settlements.py::_document` (705-770), `write` (773). Top: `{"format": "procgen-settlements/1", "from_kyr": 12.5,
"step_kyr": 0.1, "constants", "tiers": {village_min 120, town_min_by_stage, city_min 10000, city_cap_by_stage, stages},
"sites": [47137]}`. Sites since 12.5 kyr ago only, on a 0.1 kyr step. **No names, no deme id, no culture id, no trade
links** (brief `trade_reach` is null; "Not modelled in v0: war and raids"). Deme/culture of a site: its `cell` at the frame
via demes_all + presence for the holder's line index.
```json
{"id": 39591, "kind": "chief", "cell": ..., "lat": ..., "lon": ..., "place": "the north-west of Ratal",
 "tier_peak": "city", "tier_now": "city", "founded_kyr": ..., "founded_by": ..., "holder": "human",
 "holders": [[1.0, "human"], [0.2, "halfling"]], "abandoned_kyr": null, "why": null, "ruin_of": null,
 "resettled_as": null, "pop_now": 15281, "peak_pop": ..., "peak_kyr": ..., "who": {"halfling": 51, "human": 48},
 "who_when": "now", "quarters": [{"group": "city_kobold", "people": "kobold", "pct": 2.0}],
 "series": [[7.5, 600], [7.3, 794], ...], "bands": [[7.5, 1000.0, 10000.0]]}
```
- `kind`: minority 23,622 (a second people's own place), chief 21,985, pit 1,512, mine 18. `tier_now`: village 29,282,
  ruin 8,821, merged 5,165, town 2,953, pit 807, city 94, mine 15. `holders`: `[[from_kyr_ago, people], ...]`; 7,741 sites
  changed hands at least once. `who`: % of heads by people (towns draw from one ring, cities two), `who_when` "now" or "at
  its height" (ruins). `series`: `[ago_kyr, pop]` (unthinned, 0.1-0.2 kyr). `why`: "its people left" 5,384, "merged into the main
  place" 5,165, "the river moved away" 1,024, drought 794, **"driven out by the <people>"** (names the newcomer: humans 700,
  goblins 314, halflings 238, elves 154, ...), "the ice came" 2.
- **City mixing**: of 32,329 live places, 16,912 have 2+ peoples in `who`; of 94 cities, 61 are mixed (31 with 3 peoples,
  2 with 4). Largest mixed: human/halfling cities of ~15 k in the north of Ratal. Mining/minority sites are mostly one people.

## 6. gods.json

Writer: `gods.py::derive` (491-612), written by `taboos.write_religion` (276-286). Domains (`gods.DOMAINS`, `GROUPS` 49):
water [sea, river, rain, flood], sky [sky, sun, storm], land [mountain, fire, forest, desert], life [herd, hunt, harvest,
fertility], human [hearth, smithing, death, war, ancestors]. Top: `{"format": "procgen-gods/1", "gods_mode":
"faith_made", "from_kyr", "domains", "groups", "constants", "beings": [4253], "events": [3614], "cultures": {culture id
string: {name, people, beings, living, ritual_since_kyr}}, "summary"}` (+ `faiths`, `frames` on HEAD only).
- Being: `{"id": 373, "label": "god of sky and storm", "born_kyr": 198.0, "culture": 98, "how": founded | born | split,
  "parent": 180, "fused": [1813, 4105], "top": [["sky", 0.557], ["storm", 0.335], ["sun", 0.108]], "individuation": 0.597,
  "devotion": 1.0, "bound_to": null, "high": true, "status": living | merged | faded, "ended_kyr", "end", "into",
  "grants_spells": true, "first_domain": "sky", "history": [[ago_kyr, individuation, lead domain], ...]}`.
- Gods map to **cultures** (`culture` id), hence to demes via `cultures[].demes`; 1,791 living. Labels are domain phrases;
  `gods.py:22` "Names wait for PW-986". Events: merge 1764, birth 959, split 692, carry 137, fade 62.
- taboos.json (`taboos.py::write` 267): `{"cultures": {id: {name, people, purity_weight, taboos: [{target, label, scope,
  origin: symbolic | identity | divine | purity, why, god?}]}}}` for the 305 live cultures. Targets are food kinds (swine,
  carrion_birds, bats, hares, snakes, insects, roots, waterfowl, ...). `taboo_defs.KINDS` includes `speech` ("names and
  words not spoken: of the dead, of rulers..."), not yet emitted in a24559.

## 7. Crops, animals, fuels: concepts and spread history

**Ids** (`crop_defs.TABLE`, bit = TABLE index): wheat (wheat and barley) 0, pulses 1, foxtail_millet 2, rice 3, sorghum 4,
maize 5, potato 6, roots 7, banana 8, rye 9, stonegrain 10 (fantasy), emberpod 11 (fantasy), tree_fruit 12, olive 13, vine 14,
oil_seeds 15, coconut 16, spice_tree 17, chili 18, cane 19, sap_sugar 20, tea 21, greens 22, alliums 23, nightshade_fruit 24,
squash 25, beans 26, cacao 27, vanilla 28, peanut 29, sweet_potato 30, pseudograin 31, avocado 32. a24559 stores 31 stocks
(no stonegrain/emberpod); always use the stock's `bit`. Animals (`animal_defs.TABLE`): horse 0, dog 1, caprine (sheep and
goats) 2, cattle 3, fowl 4, great_elk 5 and riding_lizard 6 (fantasy, absent from a24559's 5 stocks). Fuels
(`fuels.FUELS`): wood, charcoal, dung, peat, straw, grass, drift, coal, heath, oil, tallow, bone; per people
`meta.fuels.summary.by_line[id]` = {people, <fuel>: share, lead, lead_share, sentence "It cooks over driftwood-and-seaweed
fires."}; `meta.fuels.phrases`. Other concept sources: `land.GOODS` (34 goods: harbour, salt, fish, shellfish, seals...),
body keys, the taboo targets, `meta.animals.craft` (boats: raft or dugout 100 kyr, canoe or outrigger 60, planked boat 6,
sailing ship ...), `meta.animals.dairy` per people, techtree techs (section 9).

**Stored spread record** (people- and landmass-level; writer `animals.py::Stock.summary` 250-271, crops subclass it):
`meta.crops.stocks[id]` / `meta.animals.stocks[id]` =
```json
{"label": "wheat and barley", "bit": 0, "deed": "first cultivated", "date_drawn_kyr": 11.175, "anchor_kyr": 10.5,
 "tamed": [{"ago_kyr": 11.1, "lat": 43.7, "lon": 153.1, "landmass": 0, "landmass_name": "the continent of Simath (84 Mkm²)",
            "line": "human", "people": "humans", "country": "wild country", "first": true, "wild_mkm2": 20.45},
           {"ago_kyr": 8.7, "line": "hobgoblin", "first": false, ...}, {"ago_kyr": 5.7, "line": "human_farmer", ...}],
 "reached_kyr": {"the continent of Simath (84 Mkm²)": 11.1, "the continent of Ratal (24 Mkm²)": 5.7, ...},
 "crossings": [{"ago_kyr": 7.7, "landmass": 17, "landmass_name": ..., "craft": "canoe or outrigger", "gap_km": 180}, ...],
 "took_up_kyr": {"leonin": 8.5, "bugbear": 8.5, ..., "human": 4.9}, "adoption": {people: share}, "users_share": {...},
 "propensity": {line: x}, "wild_mkm2", "known_mkm2", "grown_mkm2", "route_file": "layers/route_wheat.bin"}
```
`tamed` = independent origins (several per crop; `first` marks the earliest). `took_up_kyr` = when each **people** first
took it up. No per-deme or hop-by-hop record is stored.
**Recomputable per deme**: layer `crop_known` ((147, n) **uint64** bit flags, bit = crop bit, "the front of the knowledge
spreads over peopled land and by canoe and boat") and `animal_known` ((147, n) uint8). A deme's arrival time for crop c =
the first frame where any of its cells (demes_all) has bit c set; the donor = the neighbouring/co-present deme that had it
the frame before (pairs, or the cell graph). Resolution 0.5 kyr (recent frames). `layers/route_<id>.bin` (present only,
uint8 per cell): 0 not known, 1 origin, 2 road (land front), 3 sea (boat). `crop_wild` / `animal_wild`: wild ranges.

## 8. Landscape for place, river and lake names

- **World layers** (`worlds/dba204.json` `layers`, plain lists of 163,842, same grid; `world` id in `meta.world`):
  `flow` (accumulated discharge, m³/s, 0..1785; 1,250 cells > 100, 131 > 1000), `downstream` (cell index of the next cell
  down, -1 at sinks/sea), `lake` (0/1), `lake_kind` (0..3), `lake_level` (m), `river_nav` (0 none, 1 small boats, 2
  barges, 3 sea-going), `harbour` (0..3), `coast_type` (0..11: ice front, fjord, delta, mangrove, ...), `pass` (0..3),
  `landform` (0..12: sea, hills, shield, fold belt, rift, ...), `biome` (0..15), `elevation`, `fresh_water`, plus soils,
  resources (`res_*`), vegetation. Legends in the world's `legend` (human_use, landforms, coast, biomes, koppen).
- **No river or lake ids anywhere**. Derivable: trace `downstream` to each mouth (one river = cells draining to one mouth;
  tributaries by flow). `planet/highlights.py` already has `_rivers` (448), `_river_course` (483: farthest source to the
  sea), `_basin_cells` (496), `lakes` (631): lake = connected `lake` cells. The history keeps the world's **present** rivers
  through time (settlements docstring), so rivers are fixed; lakes and coasts move with sea level and ice (run layers
  `elevation`, `ice` per frame).
- **Existing names**: landmass names from `planet/names.py::landmass_name(seed, rank)` (crc32 of the world seed; CV
  syllables: "Simath", "Trojanel", "Ratal", "Tobrosal"...), stored in `meta.present.landmasses[].called` and the world
  `summary.landmasses`; owner overrides via `POST /api/names`. Landmarks for place phrases: `land.landmarks(world)` (331,
  highlight kinds `LANDMARKS` 326: mountain_range, plateau, great_forest, desert, wetland, lake, inland_sea, largest_river,
  fjords, rift, ice_sheet ...) and `land.place_of` (364). Deme `place` uses only the landmass ("the south of Simath").
- **Per deme, cheap**: its cells at a frame (demes_all) x the world layers give river cells crossed, lake cells, coast cells
  (`coast_type` > 0), peaks (`elevation`), passes, harbours. `land.goods(world)` (157, disk-cached) gives 0..1 per cell
  per good (hills, peaks, volcanic, frost, harbour, fish, salt...). The run's per-frame `climate`, `tree_cover`,
  `precipitation`, `temperature` and `peoples_learned` give the country a deme lived in then.

## 9. CLI, pass wiring, seeds, tests

- **CLI** is `planet/__main__.py` (no cli.py). `planet demes RUN...` -> `cmd_demes` (358): `d = S.find_run(ref)`,
  `DM.write(d, report=False)`, print. Parser block 814-817 (`sub.add_parser("demes", ...)`, `runs` nargs "+",
  `set_defaults(func=cmd_demes)`). Siblings follow the same shape: `cultures` (367, `--out`, `--redemes`), `religion`
  (378, `--out`, `--mode`), `settlements` (390, `--set KEY=VALUE`), `brief` (403).
- **Pass order in `output.save`** (82-195): reputation (152) and techtree (154) into `meta`, then landuse and fuels (with a
  world), `DM.write` (186), `CU.write` (187), `TB.write_religion` (gods then taboos, 190) if cultures.json exists,
  `ST.write` (192). A language pass would slot after religion/settlements and be re-runnable alone like `planet religion`.
- **Pass shape** (copy cultures/taboos): `derive(run_dir) -> {"doc", "summary"}` read-only, then `write(run_dir,
  out_dir=None)` with `S.write_atomic(run_dir / "x.json", json.dumps(doc, separators=(",", ":")))` and `S.update_meta(run_dir,
  fn)` (store.py 208: locked read-modify-write of run.json) for `meta.<x>` summary; optional `lines_for_report` appended to
  run.txt. `--out DIR` writes `DIR/<run id>/x.json` and leaves the run untouched (use this while developing on a24559).
  Readers: `T.load_frames(run_dir, names)` (timeline.py 233, memory-mapped), `T.frame(run, arr, name, i)` (240, decoded),
  `S.read_layers`, `shared_grid(level)` (grid: `n`, `centers`, `nbr_off`/`nbr_idx` CSR, `components`).
- **Seeds**: `meta.seed` = 12 (the world/sim seed), `meta.try_seed` = 7002 (the peoples try), `meta.tree.meta.seed` = 7,
  `meta.recent.seed` = 95173. Convention: `np.random.default_rng((seed, <ticket number>, ...))` per item; gods use
  `meta.seed` (`gods.py:216, 534`), taboos `meta.seed` per culture (`taboos.py:217, 241`), settlements `meta.try_seed`
  (`settlements.py:349, 385`). Deterministic: same run gives the same output.
- **Tests**: `tests/test_<module>.py`, synthetic inputs on small grids (`shared_grid(5)`, hand-made LINES dicts:
  `tests/test_demes.py`, `test_cultures.py`, `test_gods.py`); none read a stored run. `pyproject.toml` addopts `-n 16 --dist
  loadscope` (xdist); marker `slow` registered in `tests/conftest.py:26`; lanes run `uv run pytest -q -m "not slow"` plus
  their area tests. Fixture `data_root` (conftest 56) gives a temp store root for tests that write runs. Golden files
  (`tests/golden/`) cover only the sim and climate (`test_golden.py`, `--update-golden`). JS tabs are tested by running the
  file under node with stubbed DOM/fetch (`tests/test_religiontab_js.py`, skipped without node).

## 10. The brief (`planet/lineages/brief.py`)

- `BRIEF_VERSION` = 16 (40; bump with a note when adding a section). `build(run_ref, region=(lat, lon, km) | None,
  people=id | None, era_kyr=0.0, ctx=None) -> dict` (248). `Ctx(run_ref)` (97) opens the run once: `meta`, `lines`, `idx`
  {id: index}, `g`, `ts`, `arr` (layers incl. demes), `world` layers, `goods`, lazy `cultures()`, `religion()` (gods.json,
  taboos.json), `overlap()` (presence + demes_all), `frame_at(era)`, `f(name, i)`.
- Region = cell mask `sel` (`region_of_people` 211 for a people: its cells at the era frame). Sections are assigned in
  order (291-313): land, bad_years, fuels, wild_food, fish, salt, crops, animals, peoples, cultures, sea_peoples, megafauna,
  megafauna_ages, animal_foods, mixing_zones, substrate, neighbours, mining, settlements, trade_reach (None), events,
  reputation, suggested; then `people` (`_people` 1209: lineage chain, body, way, demography, present, homeland, story,
  reputation calls/called_by, contacts) when `people=` is given; `not_modelled` (null-keyed list).
- Per-culture data arrives via `_cultures` (1163): the cultures on the region's land at the era (top `CULTURES_TOP` 6, by
  deme cells through `deme_culture`), each `{id, name, people, how, since_kyr, land_share, sea_craft, changes, gods?,
  taboos?}`. A language section fits either per culture here (its demes are known) or as `brief["languages"]` after
  `cultures` with the people's endonym/exonyms beside `reputation`; `markdown` (1274) renders "## Cultures here" at 1342
  and "### Names (PW-731)" at 1422 (the exonym lines). `all_briefs` (1433) writes one brief per people x `DEFAULT_ERAS`
  (0, 0.5, 1, 2, 3, 6, 9, 12 kyr) plus mixing zones. Served by `GET /api/brief` (`server.brief` 182).

## 11. The workbench (`viewer/lineages.html`, 1,227 lines)

- Server: `planet serve` (`server.serve` 754), **127.0.0.1:8765**, viewer at `/viewer/`; data root = `store.root()` (set
  by `--data`/`$PLANET_DATA`, else the repo, whose runs/ worlds/ zooms/ grids/ are symlinks). Static files: `GET
  /runs/<id>/<file>` straight from the run dir, so a `languages.json` is fetchable as `../runs/${id}/languages.json` with no
  route. Routes worth copying: `/api/cultures` (212: file if present, else derived in memory, cached by run mtime), `/api/gods`
  (312), `/api/taboos`, `/api/presence?run=&frame=` (binary frame of presence + demes_all), `/api/brief`. Lineage editor
  routes under `lineages_api` (671).
- Tabs: `<nav id="tabs">` buttons with `data-tab` (104-114: tree, cultures, peoples, places, wishes, results, tech,
  religion) and `<section class="tab" id="tab-<name>">` (117-124). `showTab(t)` (283) toggles; the redraw dispatch (306-312)
  calls `drawX()`; `location.hash` `#<tab>/<view>` keeps the view. Footer help per tab in the `FOOT` map (258-280).
- Run loading: `showResult(id)` (1169) fetches `../runs/${id}/run.json` -> global `result = {id, ...run.meta}`, and
  `result.demesDoc` from `meta.demes.file`. The Tree tab's `#tlView` select offers "species" and "species + regional
  populations" (the deme tree from `result.demesDoc`). Cultures tab (`drawCultures` 1002) lazily fetches `/api/cultures`
  into `result.culturesDoc` and `/api/gods` into `result.godsDoc`, with `.busy` guards and redraw on arrival.
- New tab pattern = `religiontab.js` / `techtab.js`: a classic script (IIFE) loaded after `numfmt.js` (127-129), injects
  its own CSS, exposes `window.ReligionTab = {draw(el, result)}` (238), sub-views with `setView` + `history.replaceState`
  (237). `drawReligion()` (1083) is the host stub: "pick a run" message when `result` is null, else `ReligionTab.draw(el,
  result)`. Helpers: `esc`, `$`, `NumFmt.kyr` (numfmt.js), `HOW_COL`, CSS vars `--line --panel --muted --text --acc`.

## 12. Machine and timing

- Machine: 48 cores, 183 GB RAM (owner cap by day: all lanes <= 32 cores, ~90 GB; /tmp is RAM).
- Stored timings: whole peoples run 1,464 s; `planet demes` **58.5 s** (cutting 106 frames); cultures 6.1 s; gods 12.3 s;
  taboos 0.1 s; settlements 26.9 s. Presence table 18.4 M entries (92 MB) over 147 frames; demes_all the same count of u2.
- Loop sizes over the last 20 kyr: 452 demes at 20 kyr, 573 now, 262 born on the way; 41 frames at 0.5 kyr. Generations
  per lineage in 20 kyr range from 47 (dragons) and 138 (elves) through ~720 (humans) to 1,712 (kobolds) and 3,437
  (aarakocra). Deme-generations: **~378,000** (sum over every deme of its lifetime within the last 20 kyr / gen_yr; dominated by
  kobolds, aarakocra, kenku, dragonborn, humans), so per-generation work must be vectorised or batched per frame interval.

## GAPs the engine must derive (nothing stored)

1. **Deme population**: only cells. Proxy: per frame, sum over its demes_all entries of `share/100 x cell area (3,113 km²) x
   density`, with density = `meta.lineages[].demography.density` (present mean) or, for <= 12.5 kyr, `eraq_dens`
   (all peoples/km², `2**(q * PEOPLE_SCALE) - 1`, `landuse.inputs_from` 157) split by the presence shares.
2. **Bilingualism / L2 share**: none. Proxies: pair `shared` cells / the smaller deme's cells; presence shares on shared
   cells; people-level `mixed_pct_now`; settlement `who` mixes.
3. **Language-shift events at deme level**: only people-level incursions (lat/lon + time) and site `holders`; no polity,
   ruler or elite. Arrival demes' parents are wrong (section 1).
4. **Full-resolution deme series**: thinned to 24 points; recompute per frame from demes_all.
5. **Crop/animal arrival per deme and donor**: recompute from `crop_known` / `animal_known` x demes_all.
6. **River and lake identities**: derive from `downstream`, `flow`, `lake` (highlights helpers).
7. **Prestige, cities per culture, trade**: none; proxies from settlements on the culture's cells, techtree `known`
   (`meta.techtree.known[people][tech] = [kyr_ago, how, from]`, e.g. `writing`, `cities`, `law`, `roads`), area.
8. **Hybrids, templates and groups** have no demes or cultures; groups vanish on HEAD.
9. **Names**: deme, culture and god names are English placeholders; only landmasses have generated names.
