---
id: PW-1015
title: How big is a regional population (deme)? ~20, ~60 or ~150 human demes on b69f51
type: task
status: in-progress
parent: PW-981
milestone: v2
subsystem: peoples
effort: xs
impact: med
found_by: fun46-demes
blocked_by: []
relates: [PW-981, PW-856, PW-767]
refs: [planet/lineages/demes.py, "run b69f51"]
created: 2026-10-29
updated: 2026-10-30
---

## Description
In plain words: the demes pass cuts a long range into a chain of regional populations once it is wider than a set
travel distance. That distance decides how many "cultures in waiting" each people gets. Humans on b69f51 lead 34,603
cells today (~108 Mkm², mostly the one huge continent), and the three settings give:
- **~20 human demes** (split at 14,000 easy km, fuse under 8,000): 21 alive today. A typical one is ~1,200 cells
  (~3.7 Mkm²); they run from ~100 cells (an island) to ~3,900. Each large island still gets its own (the sea gap does not
  depend on this setting). Few cuts by distance (21 in 300 kyr), so most of the tree is gap splits (148) and fusions (107): the tree
  is mostly about who got cut off, not about drift across a plain.
- **~60 human demes** (now: 7,000 / 4,000): 55 alive. A typical one is ~580 cells (~1.8 Mkm²), from ~90 to ~1,150. The 2cb509 diaspora gets 13 at this
  setting.
- **~150 human demes** (3,500 / 2,000): 155 alive. A typical one is ~190 cells (~0.6 Mkm²), from ~40 to ~450. The tree
  churns: 647 cuts by distance and 381 demes that die out in 300 kyr, against 143 and 147 now. Many of those are
  short-lived bands at moving range edges.
One easy km is a km of coast or easy lowland; open lowland costs ~1.3 per km, desert or mountains 2-3. The count is
also the number of rows the workbench tree draws for humans, and later perhaps the number of languages or dialects.

Options:
- A: keep 7,000 (~60);
- B: 14,000 (~20): a clean tree, coarse cultures;
- C: 3,500 (~150): fine-grained, busy and churning;
- D: two levels: big demes (B) with sub-demes (A) inside, the tree drawing the big ones and the sub-demes on demand.
Lean: A now; D later, since languages want both levels (family and dialect).

## Updates
- 2026-10-30: Owner 10-30 D7: A now; D later, when languages arrive.
- 2026-10-29: Owner 10-29: agrees way of life should shape deme size. Mobile herders and seafarers reach further before splitting, so steppes stay whole and farming valleys fracture. Queue with the next demes work. Scale still to be picked from the maps (at least 2x). In the viewer, call them 'regional populations', not 'demes'.
- 2026-10-29: Status todo -> in-progress. Owner 10-29: Mongolia-sized is too big. At least double the count. Show maps or numbers at 2-5x the current count. Some regions should stay one people and others fracture a lot. Dialects come later via zooms. A small lane is making the comparison maps (docs/review/lineages/deme-scale/).
- 2026-10-29: Scale examples made: maps and tables for ~2x, 3x, 4x, 5x the 55 human demes on b69f51 (settings 4,300/2,450, 3,400/1,950, 2,850/1,630, 2,500/1,430) in docs/review/lineages/deme-scale/README.md. Median human deme 1.8 Mkm2 at 1x down to 0.38 at 5x; highland demes ~half the size of lowland, dry country only 15-25% smaller, islands small at every scale. `demes.derive` gained split_km/fuse_km keywords (defaults unchanged).
- 2026-10-29: Status needs-decision -> todo. Owner 10-29: ~60 human demes (regional-sized, about Mongolia) for now, not set in stone, and never continent-sized. This is going to be vibes-based: the owner wants to see examples and pick. Note for the language project: dialects at an England-size scale would be a finer level nested inside demes, not a smaller deme size.
- 2026-10-29: Created from inbox draft draft-demes-scale.md (found by fun46-demes).
