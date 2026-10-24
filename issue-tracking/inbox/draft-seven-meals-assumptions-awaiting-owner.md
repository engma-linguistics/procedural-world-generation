---
title: "seven_meals.toml assumes the leans on the open PW-734 questions (Q2 dates, Q7 sweet raptors, Q8 source of truth, Q9 marine, Q10 fantasy-only)"
type: task
status: needs-decision
parent: PW-692
milestone: v2
subsystem: timezoom
effort: xs
impact: med
found_by: fun13
blocked_by: []
relates: [PW-730, PW-734, PW-754]
refs: [planet/lineages/samples/seven_meals.toml, docs/proposals/culinary-dnd-intake.md]
---

## Description
The preset (PW-730) had to choose something where the owner has not answered. Each is one line to change in the file:
- **Q2 dates:** the split times are the culinary depths used as anchors (the tiers fall out of them). The run draws the rest. Nothing is authored exact.
- **Q7 aarakocra sweet:** `aarakocra` has `sweet = true` for all four ecotypes (lean A: the pepper joke needs the raptors). Option B: raptors don't, move the joke to the granivores.
- **Q8 source of truth:** the preset mirrors the culinary repo's tree and bodies (lean A) and the file says so; no check script exists. A script diffing the preset against a YAML export of `genetics.md` is the next step if the owner wants it.
- **Q9 marine:** the merfolk and the deep folk live on coasts and islands (`swims`, `coastal`), like dnd.toml's sea folk; the deep folk cook without fire. Real marine habitat (sea cells, the trench, the vents) is not built (lean A for merfolk and storm giants; B acceptable for the deep folk). Until then a "deep folk" range on a coast is a placeholder, not a claim.
- **Q10 fantasy-only:** the preset is fantasy; real mode keeps the lines marked `real = true` (the human line and the human groups).
Also decided in the preset and worth a glance: the memory length of the devil and demon rows (30 kyr; PW-754 option A) and the four antelope-kin groups (steppe and savanna males-only, dry-grass and mountain both sexes), where the intake had three.

Lean: keep all as written; the owner only needs to answer if one is wrong.
