---
id: PW-751
title: The contact record is read at the stored epochs, from the wholes' presence; border, corridor kind and substrate are coarse
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun11
blocked_by: []
relates: [PW-727, PW-701]
refs: [planet/lineages/contacts.py, planet/lineages/history.py, docs/review/lineages/briefs/SCHEMA.md]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-727 is built as output only (contacts.py), so its limits are known and listed here for a later pass:
- Contacts are read at the stored epochs only (`meta.every`), so `first_contact_kyr` is the first stored epoch with touching ranges,
  and `years_in_contact` credits each epoch with half the gap to its neighbours. In the deep and glacial epochs the gaps are
  thousands of years. A finer record would read the presence every step (cost: ~190 pair sweeps per step).
- The border is the count of cells of one people touching the other's range outside it (the longer side) x the cell size, not a length along a line; the corridor `kind` is the commonest of
  coast / river / open lowland / closed / mixed on the cells next to the border (crossing.corridor values and tags), not the
  river or coast named.
- Substrate is "the people holding a cell with presence >= 25% before the present one, until the old one holds none of it",
  read at the stored epochs. A cell held back and forth keeps only the last other holder. The brief gives it over the people's
  whole range, not the region only.
- The cline (`contacts.cline`: 300 km, rate 0.5 per ring, T0/T1 borders only) is an output smoothing of `body_<trait>`; it is not
  fed back into the history and its width is not calibrated against anything.
- [ ] decide whether the brief should give the substrate for the region's cells only (needs the per-cell previous holder stored as a layer)
- [ ] store `contacts` per epoch as a layer if the viewer wants to draw the haloclines over time

## Updates
- 2026-10-24: Created from inbox draft draft-contact-record-resolution.md (found by fun11).
