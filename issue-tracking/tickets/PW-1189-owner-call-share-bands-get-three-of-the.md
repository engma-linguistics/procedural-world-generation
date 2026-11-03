---
id: PW-1189
title: "Owner call: share bands get three of the even six into 12-22%, but humans and elves need more than a x4 nudge"
type: task
status: wontdo
parent: PW-917
milestone: v2
subsystem: highlights
effort: s
impact: med
found_by: lane78b
blocked_by: []
relates: [PW-1173, PW-1149, PW-1155]
refs: [planet/lineages/history/bands.py, tools/peoples_robust/trees/even_six.toml, "world 4360a3"]
created: 2026-10-30
updated: 2026-11-03
---

## In plain words
You wanted the six peoples of the even-six tree near-equal. Lane 78b gave five of them a target of 12-22% of all people (tieflings
can't take one: they are a share of the humans, not a people of their own). The run then raises or lowers each people's density and
tries again. After six tries, dragonborn, halflings and gnomes land inside their targets. Humans and elves don't. Humans need their
density cut below a quarter, and elves need theirs raised more than four times. A quarter and four times are the limits the targets
may push. Even at those limits, humans keep 24-28% and elves reach only 7-8%.

## Description
World 4360a3, L6, one try, even_six tree with `band_pct = [12, 22]` on human, elf, gnome, dragonborn and halfling (merged lane 78 +
main). Share of people:

| seed | rounds | human | halfling | dragonborn | gnome | elf | total miss |
|---|---|---|---|---|---|---|---|
| 7 | 0 (no bands) | 59.7 | 16.0 | 8.9 | 14.7 | 0.7 | 52 pts |
| 7 | 3 | 23.7 (x0.25) | 18.2 (x0.70) | 26.6 (x1.36) | 24.0 | 7.5 (x4) | 12.7 |
| 7 | 6 (stops at 4) | same round kept | | | | | 12.7 |
| 10 | 0 | 63.4 | 16.6 | 8.3 | 11.1 | 0.6 | 57 |
| 10 | 3 | 21.0 (x0.25) | 22.3 (x0.87) | 24.8 (x1.44) | 26.5 (x1.11) | 5.4 (x4) | 14.2 |
| 10 | 6 | 28.1 (x0.25) | 21.7 (x0.72) | 21.2 (x1.07) | 20.8 (x0.84) | 8.2 (x4) | 9.9 |

- Why bands are missed:
  - humans and elves are held at the knob's bound (BAND_KNOB x1/4..x4);
  - the shares are coupled: cutting the humans lifts every other people, so a people in its band one round leaves it the next;
  - 3 rounds (the default) are too few for 5 coupled peoples. 6 rounds helped seed 10 (miss 14 -> 10). Seed 7 stopped at round 4,
    with every unmet people already at its bound.
- Tieflings: a template overlay; the spec refuses `band_pct` on it. Their numbers follow the humans (1.1-2.3 M here).
- Options:
  - A. Accept: bands are a soft nudge, and this tree asks more than a x4 nudge. Report it as now.
  - B. Set the base densities by way of life first (PW-1149 option B, elves 3-5/km²), so the bands only have the last step to make.
  - C. Widen BAND_KNOB to x1/10..x10. That would likely meet all five, but by then the band is rewriting the people's ecology.
  - D. Raise the default `band_rounds` from 3 to 6. Each round costs one try.
- Lean: B, then D. C only if the owner wants the even split exactly.

## Updates
- 2026-11-03: Status needs-decision -> wontdo. Closed 11-03: superseded. Owner D31 (10-31) paused peoples-share tuning; densities by way of life (PW-1203 A, D20) replace the x4 band nudge, and band_pct is set by neither shipped preset (fresh-eyes review, R7: dead knob). A mechanism ledger (D44) decides whether to retire the code.
- 2026-10-30: Created from inbox draft draft-share-bands-cannot-even-out-the-six.md (found by lane78b).
