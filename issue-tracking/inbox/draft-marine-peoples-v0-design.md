---
title: "Marine peoples v0: design note for PW-729 (coast realm first, sea realm second)"
type: task
status: todo
parent: PW-729
milestone: v2
subsystem: timezoom
effort: l
impact: med
found_by: fun16
blocked_by: []
relates: [PW-729, PW-770]
refs: [planet/lineages/history.py, planet/lineages/spread.py, planet/lineages/landuse.py, planet/lineages/contacts.py, planet/lineages/output.py]
---

## Description
fun16 did not build PW-729 (budget went to PW-763/758); a v0 cut that keeps the land peoples' numbers unchanged, in two
steps, each a separate small merge:

1. **`realm = "coast"` (merfolk, storm giants' shore end; no new grid):** capacity() already builds K on the land cells only
   (`_land_view`, `out[li] = ...`). A coast line's K is built on "interface cells" instead: land cells with `tags["coast"]`
   plus the sea cells within one ring of land (shelf, tidal flat; `coastal.py` has the tide range). Needs: a `tags["shore"]`
   mask in `_tags` (sea cells adjacent to land), a realm switch in `capacity()` that picks `li` from `land | shore`, and
   spread() already walks sea cells for swimmers (cost factor), so a coast line only needs `sea` allowed at cost 1 on `shore`.
   Competition stays within `realm` groups (an `_realm_alpha` mask zeroing alpha across realms, so merfolk and land peoples
   do not compete, they only share cells: that is the "contact on the shared coast").
2. **`realm = "sea"` (storm giants offshore, deep folk stay authored):** K on sea cells by depth band, water temperature
   (ocean.py surface temperature), upwelling/reef/kelp tags where ocean.py has them; presence arrays are already per cell, so
   the main work is in the consumers: Contacts (land adjacency graph), `_frame` (peoples layer assumes land: add a sea draw,
   hatch), landuse (population on a sea cell must not feed cropland/pasture), reputation/brief (no land use for them), the
   viewer's peoples layer (legend at sea). Deep folk keep authored facts (no fire, vents, brine).

Cost: step 1 is a small constant over the K build; step 2 adds the ocean cells (about 2/3 of the grid) to the spread passes of
sea lines only (few lines), so well under +10% at L7. Acceptance: land peoples' areas and populations byte-identical when no
line has a realm; golden unchanged.
