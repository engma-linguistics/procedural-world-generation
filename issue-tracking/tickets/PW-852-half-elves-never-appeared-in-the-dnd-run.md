---
id: PW-852
title: Half-elves never appeared in the dnd run though elves and humans meet; they should appear soon after elves arrive
type: task
status: done
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Owner: 'about ten months after the first elves show up'. Cause being checked.

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 24 (de83743).
- 2026-10-25: fun-lane-24: diagnosis (probe of the dnd tree on time zoom f778ab): humans and elves never came within three cells of each other (human ~10k cells, elf ~4k, overlap 0, near 0 at every frame). Two causes. (1) The arrival's pull toward the other parent was x(0.2 + 3-cell dilation), beaten by the heavy-tailed origin noise (over 163k cells the best cell's luck is hundreds of times a typical one). (2) A contact hybrid needed both parents above EST in the same cell, but in closed country a rival excludes the other (ALPHA_CLOSED), so two ranges on one continent only touch. Fix in history.py: an arrival whose hybrid is wanted comes down within HYBRID_REACH_KM (600 km) of the other parent's range, on land where it can really live (K >= half its best), the nearest portal first with portals; contact is a frontier (History._meeting: both hold a cell, or one holds it and the other the cell beside it). Tests in tests/test_lineages.py: frontier touch (exact cells), arrival within reach over 12 seeds, an end-to-end hybrid appearing within 3 kyr of its own date. Result on time zoom f778ab: see the final run in the lane report.
- 2026-10-25: Owner: humans spread like a gas; on a continent shared for ~6 kyr with elves who'd been expanding ~20 kyr, they should meet within hundreds to low thousands of years and mix. Something is wrong: investigate the overlap (EST threshold, exclusion, human spread on continent 0) and fix.
- 2026-10-25: Diagnosis: contact hybrids are born only where both parents share cells; elves arrived ~25 kyr ago on continent 0 while humans lived on continent 1 and only reached continent 0 ~5.9 kyr ago, with no human-elf mixing zone. Working as written; the owner wants half-elves soon after the elves arrive, so the Fae arrival should favour land near humans or hybrids should form at sea/coast contact.
- 2026-10-25: Created.
