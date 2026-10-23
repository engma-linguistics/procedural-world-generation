---
title: "Cell composition is by presence (habitat held), not by head count; a dense people looks smaller than it is"
type: task
status: needs-decision
parent: PW-689
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: fun-composition
blocked_by: []
relates: [PW-689, PW-663, PW-701]
refs: [planet/lineages/compose.py]
---

## Description
The shares in `mix_lead_share` / `mix_second_share` / `mix_other_share` weigh each people by its presence in the cell (the share of the habitat it holds, with reach) times its cohabitation with the leader. They do not weigh by population (presence x density): farmers at 12 per km2 beside foragers at 2 would be ~6:1 by heads but 1:1 by presence. The lactase share (PW-701) is therefore also by presence.

Options:
- A (built): by presence. Reads as "who holds the ground".
- B: weight by presence x density, so shares are shares of the cell's people. Dense peoples dominate more; a hunter minority shrinks to the "other".
- C: both layers (ground and heads), the hover shows heads.

Lean: B for the hover and the body shares when the cuisine pass (PW-692) needs head counts; A stays for the colour layer.
