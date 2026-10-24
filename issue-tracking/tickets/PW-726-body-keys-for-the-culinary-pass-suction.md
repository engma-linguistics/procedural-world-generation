---
id: PW-726
title: "Body keys for the culinary pass: suction, teeth, gut, salt craving, display organ and shed cycle, activity hours, ectothermy, fire use"
type: task
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: culinary-intake
blocked_by: []
relates: [PW-694, PW-701]
refs: [planet/lineages/spec.py, docs/proposals/culinary-dnd-intake.md]
created: 2026-10-24
updated: 2026-10-24
---

## Description
PW-694's body keys (sweet, milk, capsaicin, bitter, smell, diet, raw_meat, cellulose, toxic) miss most of the "one
physical fact" lines the culinary repo builds its entries on. Add the following keys, inherited key by key as now,
shown in the stories and exported in the culinary brief. Nothing in the simulation reads them, except
`fire = false`, which the fuels pass (PW-722) should honour.
- `suction`: none | poor | normal. Aarakocra: none. Dragonborn: poor.
- `teeth`: grinding | conical | dental_pad (ruminants: no upper incisors) | beak.
- `gut`: simple | hindgut | foregut. Foregut covers the ruminants, and hill giants' "ancestral fermenting gut".
- `salt`: normal | craving. Herbivores: craving.
- `display`: none | horns (permanent, growth rings) | antlers (shed yearly).
- `shed`: none | both | males. This is the antler calendar's "one clock or two".
- `hours`: diurnal | crepuscular | nocturnal. Warm-country giants, the ruminants.
- `thermo`: endo | ecto. Lizardfolk: "ectothermy as a desert superpower", the feast-and-fast rhythm.
- `fire`: true | false. Deep folk cook without fire: vents, brine, fermentation.

Preset values: `docs/proposals/culinary-dnd-intake.md` §4.3 for the antelope and cervid folk, and the culinary
fact sheets for the rest.
- [ ] Workbench dropdowns.
- [ ] Story sentences.
- [ ] Validated in `spec.parse_body`.

## Updates
- 2026-10-24: fun8: remade fantasy run 6ca7e0 on 1df1c3 (--tries 2) carries the new keys; examples in docs/review/lineages/briefs/ (people_triton shows 'cook without fire').
- 2026-10-24: fun8: nine body keys (suction teeth gut salt display shed hours thermo fire) validated in spec.parse_body, inherited key by key, in the story notes, the workbench dropdowns, the brief; fire=false honoured by fuels.py (It cooks without fire). Preset (dnd.toml) set where the analogue is clear: reptilian ecto, avian endo+beak+no suction, dragonborn poor suction, tortle beak, feline conical+crepuscular, hill giants foregut, triton and sea elves no fire. The ruminant folk (display, shed, salt) wait for the owner preset (PW-730).
- 2026-10-24: Created from inbox draft draft-body-keys-for-the-culinary-world.md (found by culinary-intake).
