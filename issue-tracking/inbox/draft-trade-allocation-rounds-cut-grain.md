---
title: "Trade step 2's allocation stops after 3 rounds and leaves 62-73% of the world's grain lack unmet; 8 rounds triples herders' grain on 3e0eb4"
type: task
status: needs-decision
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 216
blocked_by: []
relates: [PW-1515, PW-1511, PW-1503]
refs: [docs/review/culture/trade/step3b.md, "planet/lineages/trade_flow.py::ROUNDS", "planet/lineages/trade_flow.py::flows_at", "planet/lineages/trade_flow.py::_allocate", "run 0141d1", "run 3e0eb4", "run 07c755"]
---

## Description
In plain words: when a culture lacks grain, step 2 gives it grain from the best source in reach. If that source runs out, the culture looks
for the next best source, but only up to 3 times (`trade_flow.ROUNDS` = 3, written as "a compute bound", not a model number). On the three
judge runs 62-73% of the world's grain lack is still unmet in the last 3,000 years. With 8 rounds it is 44-62%, and herders get 1.5% /
11.3% / 9.6% of their grain need from others on 0141d1 / 3e0eb4 / 07c755, against 0.7% / 3.9% / 4.6% with 3 rounds (main cb8374b0,
lane 216's judge). Herders getting any grain: 10% / 54% / 23% → 15% / 54% / 44%.

If it is never done, every import number (food bought, herders' grain, food routes) is cut short by a compute limit rather than by distance
or supply, and the culinary brief will read those numbers as the world's.

Options:
- A: raise ROUNDS to 8. The derive takes 1.7-2.0 times as long (L7: ~2 min a D&D run, ~3 min Seven Meals, one thread).
- B: rounds until no taker finds more supply (the true allocation), with a cheaper walk (only from sources with supply left, only to
  takers still short); costlier to build, possibly cheaper to run.
- C: keep 3 and say in the brief that imports are a lower bound.

Lean: A now (it is a slam dunk in model terms; the cost is runtime), B if the server's first load gets too slow. Check the
step 2 judge (step2.md) still passes: fall-off distances per class, sea against land.
- [ ] the unmet grain share falls, and herders' grain met is measured before and after on the three judge runs
