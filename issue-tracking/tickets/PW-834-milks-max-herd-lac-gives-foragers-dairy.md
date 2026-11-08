---
id: PW-834
title: "milks = max(herd, lac) gives foragers dairy herds: drop lac from milks; let lactase rise under dairying"
type: task
status: done
parent: PW-692
milestone: v2
subsystem: food
effort: s
impact: med
found_by: assumptions-audit
blocked_by: []
relates: []
refs: []
created: 2026-10-24
updated: 2026-11-03
---

## Description
From the pre-v1 assumptions audit (docs/review/assumptions-audit/README.md, findings.json): milks = max(herd, lac) gives foragers dairy herds: drop lac from milks; let lactase rise under dairying.

## Updates
- 2026-11-03: Status todo -> done. Lane 164: animals.summary milks = herd (lactase no longer makes a dairy people); the cuisine sheet's dairy rule (cuisine.py::dairy_of) needs herding >= 10% of heads, milking known, a dairy animal on the land and body.milks, and lets lactase rise with years of dairying (PW-1372).
- 2026-10-24: Created.
