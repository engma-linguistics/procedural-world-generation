---
title: "Star anchor: re-pick star_brightening (0.45 was tuned on the old from-age-0 curve; anchored it gives +7.6 C per Gyr raw, full Gough +16.9) and remove star_age"
type: task
status: needs-decision
parent: PW-244
milestone: v1
subsystem: climate
effort: s
impact: high
found_by: star-anchor-audit
blocked_by: []
relates: [PW-791, PW-780, PW-789, PW-761]
refs: [planet/tectonics/params.py, planet/tectonics/earth.py, docs/review/base-climate/star-anchor-audit/]
---

## Description
Audit items 3 and 12 (docs/review/base-climate/star-anchor-audit/README.md).

`star_brightening` 0.45 is a compensation by its own write-up (v1-finish-7): "a chosen star". It was the only rate
that flattened PW-708's late weatherability cooling at L6 without the Sun-like overshoot (1.0 gave 16/18 never-ice).
It was picked on Gough's curve from star age 0.

Anchored at the run's end, Gough is steeper:

| run length | 0.45, old | 0.45, anchored | 1.0, old | 1.0, anchored |
|---|---|---|---|---|
| 1 Gyr | +5.6 C | +7.6 C | +12.8 C | +16.9 C |
| 2 Gyr | +11.5 C | +15.2 C | +27.5 C | +33.7 C |

Raw forcing at 0.81 C per W/m2.

Two owner rulings of 2026-10-24 now conflict:
- "0.45 ok" (provisional, by phone);
- the anchor: "full Gough unless evidence says otherwise".

PW-807 also moves the plants' weathering factor late, which changes the trend the rate was cancelling.

Options:
- A. Full Gough, as the anchor ruling says, with PW-791's thermostat expected to carry it.
- B. Keep 0.45, a K star. It is ~35% stronger than before at 1 Gyr.
- C. Re-measure 0.45 and one lower rate (e.g. 0.3) on the anchored code, with the 18 L6 seed-draws and 8 L7
  seed-draws on the unchanged bar, and pick the rate.

Lean C. Measure the anchored star alone before deciding on the thermostat, as PW-791 says. Remove `star_age` either
way (no backward compatibility): the anchor plus the ruled optional "future offset" replace it.
- [ ] rate re-picked with numbers; owner told of the conflict between the two rulings
- [ ] star_age removed; params comment rewritten
