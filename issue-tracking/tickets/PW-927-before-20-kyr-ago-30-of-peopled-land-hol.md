---
id: PW-927
title: Before 20 kyr ago ~30% of peopled land holds 2+ peoples (COMPOSITION_TWO_PCT), not "small, contact zones only"
type: task
status: todo
parent: PW-692
milestone: later
subsystem: peoples
effort: m
impact: med
found_by: fun-lane-35
blocked_by: []
relates: [PW-920, PW-888]
refs: [planet/lineages/compose.py, planet/lineages/history/frame.py, planet/lineages/history/model.py]
created: 2026-10-27
updated: 2026-11-03
---

## Description
Coordinator ruling (fun lane 35): before 20 kyr ago contact leaves ancestry traces but little land has 2+ peoples. Measured over 6 planets x 4 rolls (dnd, 7000-7003), the frame stat two_plus_pct averaged over frames before 20 kyr ago is 29.8% on main (per-roll means 16-44%, frame max 71%) and 32.8% after fun lane 35 (16-50%, max 73%). Hybrids are not the cause: none exists before 12 kyr now (HYBRID_FROM_KYR). The cause is co-held cells. Where niche overlap alpha is under 1 (unlike ways of life: fliers, hill and forest peoples, feline vs hominid), two peoples both hold the cell at p >= EST. compose() then counts the second at EARLY = 0.2 x density, which is over 10% wherever densities are close.
Options:
- A. Read "2+ peoples" as the composition stat with a deep-time cohabitation lower than EARLY (e.g. EARLY ramped from ~0.05 before 20 kyr ago to 0.2 at the mixing start).
- B. Raise deep-time competition (closed-country terr) so unlike-way peoples split ground more.
- C. Accept: unlike ways of life sharing a landscape at low density is realistic, so the bar should apply to like-way peoples only.
Lean A: it is a reporting and mixing rule, and B would shrink ranges again.
- [ ] two_plus_pct before 20 kyr ago under ~10% on the 6 x 4 sweep, or the bar restated

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: peoples refinement or later mechanism (tuning, follow-ups), not needed for a first culinary brief
- 2026-10-29: Status needs-decision -> todo. Owner 10-29: option C. Unlike ways of life sharing a landscape at low density is fine; the 'small, contact zones only' bar applies to like-way peoples only. Restate the bar and measure two_plus_pct for like-way pairs.
- 2026-10-27: Created from inbox draft draft-deep-time-two-plus-share-high.md (found by fun-lane-35).
