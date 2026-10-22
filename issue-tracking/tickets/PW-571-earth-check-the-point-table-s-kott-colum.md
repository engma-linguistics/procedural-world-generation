---
id: PW-571
title: "earth_check: the point table's Kott column and the region table's Kottek code read Am for nearly every place"
type: task
status: todo
parent: null
milestone: v2
subsystem: infra
effort: xs
impact: low
found_by: base-climate-review
blocked_by: []
relates: []
refs: [tools/earth_check.py]
created: 2026-10-22
updated: 2026-10-22
---

## Description
Seen with `tools/earth_check.py --level 6` on main 3798b6a:
- The point check's "Kott" column says "Am" for every city (and "Af" for Vostok).
- The region table's Kottek column says "Am 100%" for every region.
- The group shares and group-match percentages above them look right (Kottek B 30.1%, and so on).

The lookup in `analyse` seems to read the wrong array or id map. The points use `CODES.get(int(ok[ci]))` and the
regions use `top(np.maximum(ok, 0), rk)`.

Fix it, then check it against a few cities whose codes are known: Cairo BWh, London Cfb, Moscow Dfb.

## Updates
- 2026-10-22: Created from inbox draft draft-earth-check-kottek-column.md (found by base-climate-review).
