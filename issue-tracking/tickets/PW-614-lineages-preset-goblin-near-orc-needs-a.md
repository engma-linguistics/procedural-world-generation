---
id: PW-614
title: "Lineages preset: 'goblin near orc' needs a shared country; the dnd niches have none"
type: task
status: needs-decision
parent: PW-103
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: lineages-lane-3
blocked_by: []
relates: [PW-604, PW-601]
refs: [planet/lineages/samples/dnd.toml, docs/review/lineages/showcase-3.md]
created: 2026-10-23
updated: 2026-10-23
---

## Description
With lane 3's near-wish pull (PW-604), the goblins' origin lands next to the orcs. Even so, "goblin near orc" scores 0.00-0.19 on three of the four L7 showcase worlds, against 0.70 on 3e0b0a and 1.00 on 119973.

The cause is the preset, not the mechanism:
- Goblins are rainforest people: 18-30 C, 1200-4000 mm.
- Orcs are cold-steppe people: 2-20 C, 200-900 mm.
- Over 400 kyr the two ranges drift to their own climates, and savanna peoples settle the land between.
- Where the pull did hold them together (3e0b0a), the goblins sat in a small non-jungle pocket (0.2 Mkm², jungle wish 0.0).

Options:
- A: keep the preset. The wish fails honestly on most worlds, as PW-601 lean A allows.
- B: change the wish to "hobgoblin near orc". Hobgoblins are savanna people, and savanna touches steppe.
- C: widen the goblins' rain range down to ~800 mm, so they can live in seasonal forest next to steppe.

Lean: B. It matches the usual D&D pairing of hobgoblin and orc armies, and geography meets it without forcing.

## Updates
- 2026-10-23: Created from inbox draft draft-lineages-goblin-orc-niches.md (found by lineages-lane-3).
- 2026-10-23: Lane 4 built lean B in planet/lineages/samples/dnd.toml: the wish is now 'hobgoblin near orc'; goblins keep the jungle wish. L7 showcase 4 (best of 2): 0.91 / 0.57 / 1.00 / 0.15 on 1144ce / 31926a / 91448a / 3e0b0a (lane 3's runs, recomputed: 0.50 / 0.00 / 1.00 / 0.78). Status left for the coordinator.
