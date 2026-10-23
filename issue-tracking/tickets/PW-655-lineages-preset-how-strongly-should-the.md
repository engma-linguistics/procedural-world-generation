---
id: PW-655
title: "Lineages preset: how strongly should the true giants be bound to their country? (pull 0.85, strict)"
type: task
status: done
parent: PW-103
milestone: v2
subsystem: timezoom
effort: xs
impact: low
found_by: lineages-preset-lane
blocked_by: []
relates: [PW-635]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/history.py, "run e8cc18"]
created: 2026-10-23
updated: 2026-10-23
---

## Description
The owner asked for the giants to prefer their country strongly: fire giants volcanoes, hill giants
rolling hills, cloud giants peaks, frost giants frost, storm giants storm coasts. The preset does this with
one `[[use]]` per giant (`by` = the line's id) at `pull = 0.85, strict = true`. Off its good, a giant keeps
0.15 of its habitat.

`strict` was needed. With the usual normalisation (mean 1 over the line's country), a rare good lifts its few
places, but the rest of the country keeps ~0.75 of its habitat. In that first pass, storm giants held
7.7 Mkm² in 22 patches on 1df1c3, and hill giants 3.8 Mkm² and frost giants 4.7 Mkm² on 3e9e7d.

With strict, L7, best of 2 (giants' present ranges, Mkm²):

| world | hill | cloud | storm | frost | fire |
|---|---|---|---|---|---|
| 1df1c3 (run e8cc18) | 0.47 | 0.97 | 0.13 | 3.68 | 0.01 |
| 3e9e7d (deleted run 86b68d) | 2.83 | 0.01 | 0.10 | 4.19 | 0.18 |

For scale, humans hold ~20 Mkm².

Options:
- **A (current):** keep 0.85 strict. The giants are rare. Some fall to a refuge of a few cells (fire 0.01 Mkm² on 1df1c3, cloud 0.01 on 3e9e7d).
- **B:** pull 0.7 strict. Somewhat larger ranges, fewer refuge-sized peoples.
- **C:** a per-line population-density or roaming-area knob, the owner's later idea. Rarity would come from density rather than from cutting the habitat. That is for the later lane.

Frost giants are the largest of the giants: polar land has few rivals.

## Updates
- 2026-10-23: Status needs-decision -> done. Resolved by PW-650's density knob: giants rare by numbers (hundreds to ~14k) without the strict 0.85 pull.
- 2026-10-23: Created from inbox draft draft-lineages-giant-land-use-strength.md (found by lineages-preset-lane).
