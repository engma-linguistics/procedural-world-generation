---
id: PW-752
title: "The dnd preset carries no [[interfertile]] overrides: the half-elf exemption and the Fae arrivals need the owner's list"
type: task
status: needs-decision
parent: PW-692
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun11
blocked_by: []
relates: [PW-727, PW-734]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/spec.py, docs/proposals/culinary-dnd-intake.md]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-727 adds tiers from split depth (`meta.tier_kyr`, default 10 kyr / 1 Myr / 40 Myr) and per-pair overrides as
`[[interfertile]] a = "x", b = "y", tier = 1` rows. Arrivals from outside the world are T3 with all, overlays are interfertile
with their hosts. The culinary canon's hand-marked exemptions (the half-elf, "humans and elves: T1"?) are not in `dnd.toml`:
which pairs are overridden, and whether a mode `real` run drops them, is the owner's call.
Options: (A) leave the preset to its split depths and add overrides only in the owner's own preset (`seven_meals`);
(B) put the half-elf pair rows into `dnd.toml` now. Lean: A, since the table is the owner's.

## Updates
- 2026-10-24: Created from inbox draft draft-dnd-interfertility-overrides.md (found by fun11).
