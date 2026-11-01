---
title: "Cultures: drift rates by era, and merging side by side on a real shared border"
type: task
status: todo
parent: PW-670
subsystem: timezoom
effort: s
impact: low
found_by: lane108
blocked_by: []
relates: [PW-670]
refs: [planet/lineages/cultures.py, docs/review/emergent-cultures/design.md]
---

## Description
Two loose ends of round 2.
- The skill drift (TAU_LOSE 1 kyr, TAU_GAIN 3 kyr) is not scaled by era. Its grounding (Tasmania, the Torres and Banks
  Islands) is stone age, and no source read gives faster loss or uptake later. Larger, better-connected populations keep and
  gain skills faster (Henrich 2004; Kline & Boyd 2010). So the sounder next step is a pool-size term, not an era term.
- Merging side by side needs only one shared cell edge between two sister cultures. A minimum border would make "living
  side by side" mean what it says, for example a share of the smaller culture's edge, taken from the demes.json pairs.
