# Tech catalogue (2026-10-30, best knowledge, UNVERIFIED; state: INGESTED into techtree.toml, PW-1122)

Seven agents, one per group (food, fire, tools, shelter, travel, knowledge, war). Each listed real-world techs up to about 1700 CE, with:
- the earliest date;
- the independent origins (the "band");
- domains;
- needs.

The brief they followed is in BRIEF.md. Every `source` here comes from memory and is marked "(unverified)". The source hunt (PW-1113 / P4) replaces these with sources that have been read.

State at commit:
- 615 rows, 594 unique ids, 518 not yet in planet/lineages/samples/techtree.toml.
- 21 ids appear in two groups and need merging: adhesives, landscape_burning, lime_mortar, oil_press, smoking_drying, kilns, potters_wheel, glass, cheese, pickling, basketry, arrow_poison, ox_traction, qanat, grinding, windmill, megaliths, astrolabe, maps, standing_army, lighthouses.
- Unresolved needs: hide_tanning, metal_smelting, carpentry, mortar (x2), leatherwork.
- Rows marked `exists = true` reuse a techtree.toml id. When merging, keep the tree's own values unless the source hunt says otherwise.
- Ingested into planet/lineages/samples/techtree.toml by fun lane 69 (PW-1122); see the last section.

## Source hunt, pass 1 (2026-10-30): hunt/
Each file is a copy of its group with `verified`, `source_checked`, `hunt_note` and `earliest_kyr_checked` added on the rows checked.
The pass ran out of session web-search budget, so 190 of 615 rows were checked and 98 verified:

| group | rows | checked | verified |
|---|---|---|---|
| food | 136 | 45 | 36 |
| fire | 82 | 28 | 14 |
| tools | 86 | 15 | 2 |
| shelter | 67 | 26 | 15 |
| travel | 84 | 37 | 13 |
| knowledge | 90 | 21 | 9 |
| war | 70 | 18 | 9 |

Evidence grade: most `source_checked` entries rest on abstracts or search-result summaries, not full papers, and each entry says which. Treat `verified = true` as "a citable source agrees", not "read in full".
Pass 2 is to cover the unchecked rows, starting with tools/metallurgy, the `exists = true` anchors and the food chains.

## Ingested (PW-1122, fun lane 69, 2026-10-30)
The 594 ids became 547 techs in planet/lineages/samples/techtree.toml (102 before). Of the 594: 78 were already in the tree, 406
are new rows (at the end of the file, a section per track, in prerequisite order), 44 were merged into another row, 37 crop and
animal rows were folded into the history's own stocks, and 29 were dropped. The source files here are unchanged: the tree is now
the working copy.

Rules followed:
- Dates: the hunt's `earliest_kyr_checked` where `verified = true`, else the catalogue's own. For rows already in the tree, the
  tree's fields stay, except a verified hunted date (bread 14.4, ornament 142, cave_art 67.8, marks 77, writing 5.3, calendar
  9.5, mudbrick 10.3, villages 14.3, copper 6.95, wheel 5.5). Kept on purpose: temples 8 (11.6 is Göbekli Tepe: the megaliths
  row), cultivation 11.5 (the hunt keeps it), mines 40 (48 kyr is ochre mining).
- Sources: the hunt's `source_checked` where it verified the row, else the catalogue's, marked "(unverified)". A tree row keeps
  its own source unless that said unverified and the hunt verified the same date.
- `earth_origins` on every catalogue row: the number of independent origins (the hunt's `origins_checked` where it changed them;
  the most of any merged rows). No `rate` except pottery's (0.09, from its band of 7 origins; see the draft on floored techs).
- `pool`: the era's default ("all" in the stone age, "specialists" after), "all" for household food and ritual practices of any
  era and a few band techs (sea charts, skin boats, snow houses, horse archery...). Era: by date (stone age 7.2 kyr or older,
  bronze age to 3.4, classical to 1.6, medieval to 0.6, then renaissance), raised to the latest era of its needs.
- Domains: the catalogue's; the stray tags fire, social and communication became craft, know and know. The `build` track became
  shelter.
- Land: the free-text `env` mapped to land.GOODS (timber, frost, salt, coal, the ores, volcanic, coast -> harbour/fish/shellfish
  any, mountain -> hills/peaks any, clay -> pottery's stand-in); stone only for building techs (knapping stone is everywhere);
  ore only for the smelting rows (worked metal travels); products (hides, wool, fibre, bone) and climates without a good
  (desert, wetland, grass) left out.
- Needs: the catalogue's, resolved through the merges, with about 140 replaced. Rows Earth got more than 10 kyr after their
  prerequisites (floored by lag_max_kyr) got their real Holocene precondition instead (calendar needs villages, coal needs
  kilns and mines, soap needs fat rendering, weaving needs villages, the composite bow needs herds and glue...); 10 forager
  techs stay floored on purpose (storage, sledges, quarrying, paddles, snowshoes, bone skates, the sling, honey hunting). Rows
  dated before a need were given needs that match their date (faience before glazes, balance scale before weights...).
- Food chains to the history's stocks: wine needs the vine, chicha maize, rice wine rice, palm wine the coconut and oil palm,
  nixtamalisation maize, sugar the cane, olive oil the olive, maple syrup sap sugar; the plough needs oxen (cattle), milking
  (cheese, butter, fermented milk) a milk beast (`needs_any`), riding a mount (horse, great elk, riding lizard).

Merged (catalogue id -> kept id): adhesives -> birch_tar (renamed "adhesives (birch tar, compound glues)", 200 kyr verified);
hunting_spear -> thrusting_spear; spear_thrower -> atlatl; beer_brewing -> beer; winemaking -> wine; slash_burn -> slash_and_burn;
sauce_garum -> fish_sauce; storage_pits -> storage; storehouses -> raised_granary; cellars_ice -> ice_house; pot_boiling ->
boiling_pots; stone_boiling -> earth_oven; hearth_house -> fire_hearth; heat_treatment -> heat_treating_stone; glass_blowing ->
glassblowing; cast_iron_kiln -> cast_iron; hide_tanning, leatherwork -> tanning; dyeing -> dyes; pressed_oil_lamp -> oil_lamps;
brick_kiln -> fired_brick; butter_churning -> ghee_butter; salt_pans, salt_boiling -> salting; music_flute -> music;
cuneiform_scribal -> schools; woodblock_printing -> printing; barter_network -> trade; harbour_works -> harbours; waterwheel ->
watermill (renamed "water mills"; windmill is its own row); log_rafts -> rafts; dugouts -> canoes; windbreaks -> huts;
metal_smelting -> copper; carpentry -> carpentry_joints; mortar -> lime_mortar; llama_packs, camel_packs, donkey_caravans ->
pack_animals; camel_riding -> riding; camel_cavalry -> cavalry; camel_saddle -> saddles; pontoon_bridge -> pontoon_bridges;
stone_arch_bridge -> stone_arch_bridges; mortar_pestle -> grinding; spoked_wheel_chariot -> war_chariot; antler_working ->
bone_tools; pit_firing -> pottery; canals_ditches -> irrigation. The 21 two-group ids kept one row each (the verified one, or the
one whose needs fit its date).

Folded into the history's stocks (techs crop_<id> and animal_<id>, stock = "crops:<id>", known only from the history's tamings and
take-ups; 39 techs, one per stock in crop_defs and animal_defs): wheat, barley -> crop_wheat; lentil_pea_chickpea -> pulses;
flax, sesame -> oil_seeds; rye_oats -> rye; rice, african_rice -> rice; millet -> foxtail_millet; maize; squash; common_bean ->
beans; potato; manioc, yam, taro -> roots; sweet_potato; sorghum, pearl_millet -> sorghum; banana; sugarcane -> cane; olive;
grape -> vine; fig, apple, peach, citrus -> tree_fruit; chili; cacao; tea, coffee -> tea; quinoa -> pseudograin; goat, sheep ->
animal_caprine; cattle; chicken -> fowl; horse. The dog stock is the tree's own `dogs`.

Dropped (29): institutions or rows with no real date: kinship_exchange, oaths_ordeal, midwifery (a placeholder date), hygiene,
pilgrimage_festival, slavery_corvee, bone_setting (50 kyr not confirmed); species the history has no stock for (see the inbox draft
on missing animals): pig, donkey, dromedary, bactrian_camel, llama_alpaca, guinea_pig, reindeer, yak, water_buffalo, cat, rabbit,
soybean, teff_enset, eastern_agricultural_complex, date_palm; folded without a row of their own: zebu (cattle), waterfowl,
turkey, pigeon_dovecote (fowl); and the rows that hung on missing animals: elephant_riding, war_elephants, reindeer_draught.
