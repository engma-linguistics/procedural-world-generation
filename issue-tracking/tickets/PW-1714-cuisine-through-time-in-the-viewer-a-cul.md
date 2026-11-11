---
id: PW-1714
title: "Cuisine through time in the viewer: a culture's food sheet at three eras, with crops arriving, conquest doublets and dates in its own calendar"
type: story
status: done
parent: PW-692
milestone: v1.0
subsystem: viewer
effort: m
impact: med
found_by: plan-v1-lane
blocked_by: []
relates: [PW-742, PW-1644, PW-1391, PW-728]
refs: [docs/review/plan/milestones-to-v1.md, viewer/lineages.html, PW-742, PW-1644, PW-728]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: a culinary book is historical: what a people cooked before the plough, after the horse, under a conqueror. The brief already has era slices (PW-742), but the viewer's food sheet shows only one moment.

If it is never done, the owner sees only today's kitchen in the viewer. Change over time stays buried in JSON, and the conquest doublets (cow ~ beef, PW-1644) have nowhere to show.

- Add an era picker (three default slices from the brief) to the culture's food sheet.
- Mark what arrived or vanished between slices (a new crop, a lost herd animal, a new fuel) and why (the tech, the contact, the conquest).
- Show dates in "years ago", or in the culture's own calendar when one is chosen (v4 calendars).

Proposed for v0.6.0 (docs/review/plan/milestones-to-v1.md section 5, #3).

- [ ] On a Seven Meals culture, the food sheet switches between three eras and lists what changed and why

## Updates
- 2026-11-11: Status todo -> done. lane 309 merged
- 2026-11-11: Created from inbox draft draft-cuisine-through-time.md (found by plan-v1-lane).
