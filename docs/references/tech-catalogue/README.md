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
