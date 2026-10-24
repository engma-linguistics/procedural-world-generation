---
id: PW-703
title: Cell composition is by presence (habitat held), not by head count; a dense people looks smaller than it is
type: task
status: done
parent: PW-689
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-composition
blocked_by: []
relates: [PW-689, PW-663, PW-701]
refs: [planet/lineages/compose.py]
created: 2026-10-23
updated: 2026-10-23
---

## Description
The shares in `mix_lead_share` / `mix_second_share` / `mix_other_share` weigh each people by its presence in the cell (the share of the habitat it holds, with reach) times its cohabitation with the leader. They do not weigh by population (presence x density): farmers at 12 per km2 beside foragers at 2 would be ~6:1 by heads but 1:1 by presence. The lactase share (PW-701) is therefore also by presence.

Options:
- A (built): by presence. Reads as "who holds the ground".
- B: weight by presence x density, so shares are shares of the cell's people. Dense peoples dominate more; a hunter minority shrinks to the "other".
- C: both layers (ground and heads), the hover shows heads.

Lean: B for the hover and the body shares when the cuisine pass (PW-692) needs head counts; A stays for the colour layer.

## Updates
- 2026-10-23: Status todo -> done. Merged (fun lane 3, runs fa7183/18cf62).
- 2026-10-23: Built (fun lane 3): `compose.compose(..., dens=)` weights presence by density, so shares are shares of heads. Wish score and empty land unchanged (it is a reading); lead share mean 83.6 -> 81.4% (1df1c3), 83.7 -> 81.9% (3e9e7d); cells with a second people >= 10%: 53.0 -> 48.2% and 49.2 -> 37.1% (dense farmers swamp sparse neighbours). The leader stays the ground holder (draft draft-composition-leader-by-heads).
- 2026-10-23: Status needs-decision -> todo. Coordinator's call: yes, weight shares by head count (presence x density); the owner's '50% one people' reads as people, not area.
- 2026-10-23: Created from inbox draft draft-composition-by-numbers-not-presence.md (found by fun-composition).
