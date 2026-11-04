---
title: "Polities: the largest polity on Seven Meals is under Taagepera's 2.3 Mkm² floor (war v0 cannot chain conquests)"
type: task
status: todo
parent: PW-661
milestone: later
subsystem: culture
effort: m
impact: med
found_by: lane179
blocked_by: []
relates: [PW-1449, PW-1432]
refs: ["planet/lineages/polities.py::war_v0", "planet/lineages/polities.py::WIDE_BY", "planet/lineages/polities.py::STATE_MAX_KM", "planet/lineages/polities.py::derive", docs/review/culture/polities/round4.md, docs/review/culture/polities/round2.md, "docs/review/cultures-proposal/proposal.md#212-formation-growth-and-reach", "run 3c1caf", "run 07c755", "run a2b637"]
---

## Description
**In plain words.** Lane 179 (PW-1449) capped a city-state's reach at Spencer 2010's 250 km. That fixed the count of giant
polities. But now the biggest polity on the Seven Meals showcase (3c1caf) is 1.4 Mkm² at the present. Over the last 3,000 years
the biggest per century is 0.9-2.6 Mkm², about 1.6 in the median century. Taagepera 1997 (via `proposal.md` 2.1.2) says the
largest polity was never under 2.3 Mkm² after ~650 BC. Before lane 179 the run met that floor only because one capital's reach alone
was ~2 Mkm².

**What misleads if this is never done:** the size check in round 2 now fails on 3c1caf in most centuries. The Seven Meals world has
no empire on the scale of Rome or the Achaemenids, and a reader trusting "largest 2.3-5.5" from round 2 is wrong. (07c755 does
reach 4.2 Mkm², so it depends on the world.)

**Why:** war v0 takes a whole neighbour with WAR_P = 0.25 a century, needs 1.5x the strength, and only between polities that touch.
With 250 km states, states rarely touch, and most conquests are of one-cell chiefdoms. An empire would need 10-15 conquered states
within its ~2-century life (Arbesman's fall hazard). Raising WAR_P to 1.0 alone gives 0.59 Mkm² (round4.md table).

What I would try (one of):
- War that moves the frontier, not whole polities: a strong state takes its neighbours' border cells each century (Turchin et al.
  2013 conquer cell by cell at 100 km cells; their parameters are in the supplement, which nobody has read yet).
- Conquest that chains within a century: a winner that took a neighbour may attack the neighbour's neighbours in the same step.
- [ ] the largest polity on 3c1caf inside 2.3-5.5 Mkm² in most centuries of the last 3,000 years, with under ~8 over 1 Mkm²
