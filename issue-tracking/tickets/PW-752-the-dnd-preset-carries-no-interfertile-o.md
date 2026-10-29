---
id: PW-752
title: "The dnd preset carries no [[interfertile]] overrides: the half-elf exemption and the Fae arrivals need the owner's list"
type: task
status: todo
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
updated: 2026-10-29
---

## Description
**In plain words.** Which species pairs can have children together? The model decides from how long ago two lineages split: recently split pairs interbreed freely, older splits less or not at all (tiers set by `meta.tier_kyr`). D&D has hand-made exceptions, like half-elves, where by split age humans and elves would not interbreed.

How the owner can help:
1. List the pairs that should interbreed regardless of split age, and at what level (freely, or rare/sterile hybrids). E.g. human-elf (half-elves)? human-orc (half-orcs)? others?
2. Say whether that list belongs in the shared `dnd` preset or only in the owner's own `seven_meals` preset.

PW-727 adds tiers from split depth (`meta.tier_kyr`, default 10 kyr / 1 Myr / 40 Myr) and per-pair overrides as
`[[interfertile]] a = "x", b = "y", tier = 1` rows. Arrivals from outside the world are T3 with all, overlays are interfertile
with their hosts. The culinary canon's hand-marked exemptions (the half-elf, "humans and elves: T1"?) are not in `dnd.toml`:
which pairs are overridden, and whether a mode `real` run drops them, is the owner's call.
Options: (A) leave the preset to its split depths and add overrides only in the owner's own preset (`seven_meals`);
(B) put the half-elf pair rows into `dnd.toml` now. Lean: A, since the table is the owner's.

## Updates
- 2026-10-29: Status needs-decision -> todo. Owner 10-29: realistic genetics decides who can interbreed, and for how long after a split (viable, then absorbed into a parent, then sterile, then impossible). Exception: half-elves and half-orcs are always possible; they're central to the genre. Don't track minor hybrid populations (no half-tortle-half-lizardfolk cells): this serves D&D peoples as we know them.
- 2026-10-29: 2026-10-29: plain-language summary added at the top.
- 2026-10-24: Created from inbox draft draft-dnd-interfertility-overrides.md (found by fun11).
