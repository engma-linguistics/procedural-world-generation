---
id: PW-730
title: "The owner's world as a lineages preset (seven_meals.toml): the culinary repo's tree, groups, bodies and wishes beside dnd.toml"
type: story
status: todo
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: culinary-intake
blocked_by: []
relates: [PW-103, PW-694, PW-613]
refs: [docs/proposals/culinary-dnd-intake.md, planet/lineages/samples/dnd.toml, "culinary-dnd docs/genetics.md"]
created: 2026-10-24
updated: 2026-10-24
---

## Description
The owner's culinary-dnd repo has ruled a lineage tree for their own world (`docs/genetics.md`,
`docs/decisions/2026-09-24-lineages.md`). It is different from `dnd.toml`, which stays as the traditional D&D
template. The differences:
- one tree of life;
- bugbears split before goblins and hobgoblins;
- goliaths are a sister of humans, not giant-kin;
- halflings and dwarves split ~1–1.5 Myr ago;
- cats, the aquatic clade and the new ruminant branch are deep branches;
- elves and gnomes are separate Fae arrivals;
- kenku are a curse overlay on aarakocra;
- half-elves form no population;
- the tieflings are replaced by antelope and cervid peoples (proposal §4).

Build `planet/lineages/samples/seven_meals.toml` to the table in `docs/proposals/culinary-dnd-intake.md` §2.1 and
§4.4. It includes:
- groups: Arha and Anja orcs; the human forager, grain-belt, Jangwa cattle, seafarer and arctic groups; the four
  aarakocra ecotypes; the lizardfolk desert and delta groups; the antelope and cervid groups;
- bodies, including the culinary corrections: Arha milk ~0.1 (fermenters), aarakocra sweet = true, the ruminant
  bodies;
- the canon's adjacency as wishes;
- the cut lines (drow, sea elves, tritons, firbolgs, aasimar, genasi, troglodytes, the tiefling template) left out.

Small spec items that come with it:
- [ ] `linger = false` on a contact hybrid: no people of its own where the parents last met (half-elves: "no
      population, no cline, no community anywhere"; PW-613 otherwise makes one).
- [ ] A template whose share grows where its bearers and hosts cohabit ("the curse always takes": kenku).
- [ ] A culture-only group (`niche = false`): listed and rolled up, but takes no land of its own (Inheritance and
      Ephemeral elves in one forest).
- [ ] `[[event]]` anchors parsed and stored (polity, conquest), to be read by the reputation pass
      (draft-reputation-and-exonyms).

Builds on the proposal's leans for Q3–Q5 (a deep ruminant branch; a conquest from the steppe; antlers by group).
Measure on two L7 worlds, with four tries' means.
- [ ] Every living line holds land.
- [ ] Wish score mean reported.
- [ ] `dnd.toml` runs byte-identical.

## Updates
- 2026-10-24: fun13: seven_meals.toml built (62 lines, 20 wishes, tiers match genetics.md, deep ruminant fiends, horns/antlers by variant via new body key `display_sex`, `[[event]]` conquests, devil/demon rows). Run e63bfd on world 1df1c3 (--tries 1): wish 0.635, every living line holds land. Not done: half-elf `linger = false`, culture-only groups, kenku growing share (drafts filed); the "measure on two L7 worlds, four tries" boxes are open (one world, one try only). dnd.toml untouched.
- 2026-10-24: Unblocked by PW-734 answers 1/3/4/5: deep fiend branch, antelope-kin invaders, horns/antlers by variant following real species.
- 2026-10-24: Created from inbox draft draft-owner-world-lineages-preset.md (found by culinary-intake).
