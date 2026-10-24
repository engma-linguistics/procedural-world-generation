---
title: A contact hybrid with no population of its own (linger = false) for the owner's half-elves, and culture-only groups
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun13
blocked_by: []
relates: [PW-730, PW-613]
refs: [planet/lineages/samples/seven_meals.toml, planet/lineages/history.py]
---

## Description
Two small spec items of PW-730 that `seven_meals.toml` could not use, so it leaves them out and says so in its header:
- **Half-elves** (the canon's one exemption: "occurs; forms no population, no cline, no community"). A `contact = true` hybrid is an
  overlay where its parents meet, but PW-613 lets it linger and make a small people where they last met. Needs `linger = false` on a
  hybrid. The preset omits half-elves until then.
- **Culture-only groups** (Inheritance and Ephemeral elves share one forest). The groups model needs a niche difference to separate a
  group; `niche = false` would list the group and roll it up into its people without land of its own. The preset has one elf line.
- [ ] `linger = false`: no `_linger` cells and no 'lingers' event for that hybrid
- [ ] `niche = false` groups listed in the summaries and the brief as "same land as", taking no land
- [ ] add both lines back to `seven_meals.toml` when built
