# Tech catalogue (2026-10-30, best knowledge, UNVERIFIED)

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
- Not yet in the tree. Folding these rows into techtree.toml comes after lane 64's invention-model rework, which owns that file.

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
