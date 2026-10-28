---
id: PW-731
title: "Reputation and exonyms: what each people calls its neighbours and why (devils, demons, giant-kin, sea elves), set by conquest and contact history, kept apart from what they are"
type: story
status: done
parent: PW-692
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: culinary-intake
blocked_by: []
relates: [PW-661, PW-103]
refs: [docs/proposals/culinary-dnd-intake.md, planet/lineages/history.py]
created: 2026-10-24
updated: 2026-10-28
---

## Description
The owner's change (proposal §4). In their world, the "infernal" and "abyssal" tieflings are antelope-like and
cervid peoples. Popular belief made them devils and demons ("devils who came down from the western steppe and took
over swathes of land"). The same mechanism covers the culinary repo's other outsider errors: "giant-kin" for goliaths,
"sea elves" for deep folk, one "goblinoid menace".

**Inputs per observer O and subject S:**
- the contact record (draft-contact-history-and-interfertility-tiers);
- events: authored `[[event]]` conquests and polities from the preset, and derived incursions (S's presence rising
  sharply in O's cells within a few centuries; riding fronts), each with a direction from O;
- S's visible body (the display keys of draft-body-keys-for-the-culinary-world, size, aquatic, arrival) matched
  against a small table of folk categories (devil: horns and hooves; demon: antlers; giant-kin: size; sea elf: aquatic
  people-shape; fae: arrival);
- the tier.

**Rules:**
- O names S by its best-fitting category unless contact is rich and peaceful.
- Valence from history: conquered by S → feared; ruled by S → resented; ruled S → despised; trade → exotic; barely
  met → edge monsters.
- A conquest's reputation fades with an e-folding of ~1.5 kyr (slower with writing, by era). Peace erodes it slowly.
- Lumping under one name where contact is thin.
- A people without contact borrows its best-connected neighbour's view.

**Outputs:**
- `meta.present.reputation[O][S] = {category, valence, basis, since, strength, lumped_with}`;
- a story sentence per notable row;
- brief rows showing what a people is next to what it is called.

v0 runs on the lineage history and event anchors; v1 reads PW-661's conquests and trade.

Judgement calls for the owner: the folk-category table, and the decay time.
- [ ] On the owner's preset, humans near the conquest call the antelope folk "devils" with a conquest basis, and
      humans who live among the cervid folk use an ordinary name.

## Updates
- 2026-10-28: Owner 2026-10-28: v0's body-based folk categories are pattern X7 ('appearance as observed') in Owner's Claude Doc 'Ethnonyms: A Taxonomy for Culture Generation' (https://claude.ai/artifact/GDbAyM2ZHRYuXKkeMes8vS; Claude Docs id 7b3b1078-417a-4f09-a04d-862b94bd6877); valences map onto its 'exonym by relationship' rule (war X5, trade X1, thin contact X2/X3/X8). Next steps: PW-972 and PW-767.
- 2026-10-24: Status todo -> done. Merged f721107: reputation.py, [[exonym]] rows, brief v5. Memory length PW-754.
- 2026-10-24: Created from inbox draft draft-reputation-and-exonyms.md (found by culinary-intake).
- 2026-10-24: fun12 (branch worktree-agent-a9e99f60fb4ba7931): v0 built on the contact record. `planet/lineages/reputation.py` -> `meta.present.reputation[observer][subject]` (category, name, valence feared/despised/edge/exotic/neighbour, basis, since_kyr, strength, lumped_with, borrowed_from, text); folk categories are `[[exonym]]` spec rows (generic table in dnd.toml, no owner story); brief_version 5 shows them beside what each people is (region `reputation`, `people.reputation`); schema doc updated. Conquest = substrate (S holds cells O held), fading with an e-folding of 1.5 kyr x era scale or a row's own `efold_kyr`. Not yet: authored conquests/polities and derived incursions (PW-661), so no "resented" valence; the owner's rows and decay are in draft-exonym-rows-and-memory-length.
