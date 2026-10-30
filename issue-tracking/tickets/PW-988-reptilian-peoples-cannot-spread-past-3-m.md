---
id: PW-988
title: Reptilian peoples cannot spread past 3 Myr without relaxing a test and an owner ruling
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-44
blocked_by: []
relates: [PW-978, PW-851]
refs: [planet/lineages/samples/dnd.toml, tests/test_lineages.py]
created: 2026-10-29
updated: 2026-10-29
---

## Description
Owner 10-28 (PW-978): the kobolds, troglodytes, lizardfolk, tortles and dragonborn split from their stems at about the same time; spread them out. dnd.toml now has tortle 3 Myr, troglodyte 2.6, lizardfolk 2.3, kobold 2 and dragonborn 0.3 (seven_meals: tortle 3, lizardfolk 2.5, kobold 2, dragonborn 1.3). That is as wide as it goes: `test_dragons_are_a_deep_extant_reptile_line_with_kinds_by_biome` asserts the lizardfolk and tortles split at 3 Myr or later than that (`ago_kyr <= 3000`), and the file header records the earlier ruling that named peoples are fully realized within ~3 Myr. I did not touch the threshold.

Options: (A) leave it (0.3-1 Myr between splits). (B) Allow the tortles deeper (say 5 Myr, "a far deeper branch"; seven_meals already calls them that) and raise the test's bound to match; they stay T3 to the dragons either way. (C) Also push the dragonborn up to ~1 Myr in dnd.toml (T2 to the dragons from 1.1 Myr). Lean: B, since the tortles are the slow, deep, ocean-going branch, and nothing else depends on their date.

## Updates
- 2026-10-29: Fun lane 48: restructured dnd.toml. New saurian stem off the reptilian root at 19.5 Myr (beside the dragons), sapiens node 4.5 Myr (after the dragons' 5 Myr, so they stay the elder line); tortles split from it at 4.2 Myr, then lizardfolk and troglodytes from each other at 2.5 Myr (the stem ends there). Kobolds 2 Myr and dragonborn 300 kyr unchanged. The hand-written T3 rows are gone: by split depth tortles are T3 to both, lizardfolk-troglodytes T2 (mostly sterile hybrids). Test: the 3 Myr cap became 'split after the dragons' sapiens node', plus a check of the branch's shape. seven_meals left alone (no troglodytes; inbox draft draft-seven-meals-saurian-branch.md). Checked on run 46bc09 (world 2a7385, its time zoom f778ab), Tree tab.
- 2026-10-29: Status needs-decision -> todo. Owner 10-29: restructure rather than just spread the dates. Troglodytes, tortles and lizardfolk become their own branch off the reptilian line, and troglodytes split from the other two later. Kobolds and dragonborn stay as they are. The test's 3 Myr bound is a placeholder like the rest of the timeline, so change it to fit; the coordinator may choose the dates.
- 2026-10-29: Created from inbox draft draft-reptilian-splits-capped-at-3-myr.md (found by fun-lane-44).
