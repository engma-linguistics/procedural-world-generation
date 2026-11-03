---
id: PW-758
title: A contact hybrid with no population of its own (linger = false) for the owner's half-elves, and culture-only groups
type: task
status: in-progress
parent: PW-692
milestone: v2
subsystem: culture
effort: s
impact: low
found_by: fun13
blocked_by: []
relates: [PW-730, PW-613]
refs: [planet/lineages/samples/seven_meals.toml, planet/lineages/history.py]
created: 2026-10-24
updated: 2026-10-24
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

## Updates
- 2026-10-24: Status todo -> in-progress. Merged c80c766: linger=false, half-elves in seven_meals. Left: niche=false 'same land as' groups; overlay hybrids don't read explore/insularity yet (dnd half_orc values cosmetic).
- 2026-10-24: fun16: `linger = false` built (spec + history._hybrid; test) and half_elf added to seven_meals.toml (run 4f82a4: 0.03 Mkm2, no lingers event). `niche = false` groups NOT built (still open). dnd.toml half_orc given explore 0.6 / insularity 0.3 (data only; overlays do not read them yet).
- 2026-10-24: Created from inbox draft draft-half-elf-no-population-switch.md (found by fun13).
- 2026-10-24: fun18: dnd half_elf/half_orc: the cosmetic `explore` removed (a contact hybrid never goes through the spread step); `insularity` kept, it is read by compose.cohabitation. Option to give hybrids a small ring of wandering left as draft-hybrid-explore-unread. `niche = false` groups still not built.
