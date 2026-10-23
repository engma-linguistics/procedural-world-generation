---
title: "Peoples preset: fire giants hold only a refuge (~50 giants) on 1df1c3 and 3e9e7d"
type: task
status: todo
parent: PW-649
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: peoples-workbench-lane
blocked_by: []
relates: [PW-650, PW-655]
refs: [planet/lineages/samples/dnd.toml, "run 37e9da (1df1c3)", "run 33b1c3 (3e9e7d)"]
---

## Description
The workbench lane made the true giants rare through density (0.005–0.01 /km²) and the viable-population
rule, in place of the strict 0.85 pull (PW-655).

On the final runs, most giants hold one land of a few hundred to a few thousand giants:

| world (run) | hill | cloud | storm | frost | fire |
|---|---|---|---|---|---|
| 1df1c3 (37e9da) | 1,251 | 819 | 233 | 8,731 | 53 |
| 3e9e7d (33b1c3) | 597 | 560 | 247 | 13,915 | 54 |

The fire giants are the exception: 0.02–0.04 Mkm² and ~50 giants on both worlds. That is the refuge the
history keeps for a living line, not a land of their own. Their niche is narrow: 12–34 °C, the volcanic tag
and the volcanic good. Their habitat lies where denser peoples compete, and the viable-population rule fades
every separate volcanic patch but one.

Things to try, in order:
1. Widen their comfort range, or let `hardy` widen it.
2. Drop `prefers = ["volcanic"]` and keep only the volcanic good (pull 0.7). The tag cuts K to 0.4 off volcanic ground.
3. Exempt patches that hold a line's favoured good from the viable-population rule. This is a bigger change and needs an owner nod.

- [ ] fire giants hold ≥ 0.1 Mkm² and a few hundred on both showcase worlds without the strict pull
