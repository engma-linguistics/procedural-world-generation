---
title: Reptilian peoples cannot spread past 3 Myr without relaxing a test and an owner ruling
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-44
blocked_by: []
relates: [PW-978, PW-851]
refs: [planet/lineages/samples/dnd.toml, tests/test_lineages.py]
---

## Description
Owner 10-28 (PW-978): the kobolds, troglodytes, lizardfolk, tortles and dragonborn split from their stems at about the same time; spread them out. dnd.toml now has tortle 3 Myr, troglodyte 2.6, lizardfolk 2.3, kobold 2 and dragonborn 0.3 (seven_meals: tortle 3, lizardfolk 2.5, kobold 2, dragonborn 1.3). That is as wide as it goes: `test_dragons_are_a_deep_extant_reptile_line_with_kinds_by_biome` asserts the lizardfolk and tortles split at 3 Myr or later than that (`ago_kyr <= 3000`), and the file header records the earlier ruling that named peoples are fully realized within ~3 Myr. I did not touch the threshold.

Options: (A) leave it (0.3-1 Myr between splits). (B) Allow the tortles deeper (say 5 Myr, "a far deeper branch"; seven_meals already calls them that) and raise the test's bound to match; they stay T3 to the dragons either way. (C) Also push the dragonborn up to ~1 Myr in dnd.toml (T2 to the dragons from 1.1 Myr). Lean: B, since the tortles are the slow, deep, ocean-going branch, and nothing else depends on their date.
