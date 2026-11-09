---
id: PW-1524
title: Regional pantheons (PW-1521) - five design choices before building
type: task
status: done
parent: PW-1308
milestone: null
subsystem: culture
effort: xs
impact: med
found_by: scout220
blocked_by: []
relates: [PW-1308, PW-1489, PW-1477, PW-986]
refs: [docs/review/culture/faiths/pantheon1.md, docs/review/culture/faiths/pantheon1/pantheons.py, planet/lineages/gods.py, "planet/lineages/gods.py::Pantheons.merge", planet/lineages/attitudes.py, "run 0141d1", "run 3e0eb4", "settlements.json who"]
created: 2026-11-08
updated: 2026-11-08
---

## Description

**In plain words.** Daniel asked (11-09, PW-1521) whether a D&D-style larger pantheon could grow in some regions. In that kind of
pantheon, each people keeps gods of its own, and the big domains (sea, sky, war, harvest) get gods that several peoples share. The scout
found that history built pantheons this way, by *matching* gods across peoples (the Romans' "Sulis Minerva" at Bath) in mixed trade
cities and multi-people empires under tolerant polytheists. The model already has most of the ingredients.

On 0141d1, 47 candidate pantheons already appear around mixed towns, with a median of 5 peoples and 4 shared domain gods. On 3e0eb4,
where Daniel's missionary dwarf faith holds 192 of 267 cultures, only 5 small ones appear. The full write-up, with sources and the
design, is docs/review/culture/faiths/pantheon1.md. Five choices need Daniel before a lane builds it.

If this is never decided, the build lane will guess at choices 1-3. Each guess changes what the viewer shows: a wrong reach rule gives one
pantheon over 70% of the land, which is the worldwide pantheon Daniel said he does not want.

**1. When two peoples' alike gods meet, what happens?**
- A: **Match them (lean).** Each keeps its own name and people, and both join a shared "seat": the sea god of the Luki pantheon,
  worshipped by dragonborn and leonin. This is reversible and keeps each people's flavour. It is the Sulis Minerva or honji suijaku
  pattern.
- B: Fuse them into one being, as cultures merging do today. It is simpler, but each people loses its version, and it cannot be undone.
- C: Match them, and sometimes also create a brand-new joint god, as Ptolemy's Serapis was made for Greeks and Egyptians. It is richer,
  and one more rule.

**2. How far does a pantheon reach?**
- A: The hub culture and its direct neighbours. On 0141d1: 47 overlapping pantheons over 58% of the land.
- B: **(lean)** Cultures within a fixed distance of the hub city (about 800-1500 km). A pantheon inside a bigger one's reach joins it,
  the way a city god sits under a capital's god (Nippur's Enlil under Babylon's Marduk).
- C: Let touching pantheons join freely. On 0141d1 this chains into one region of 114 cultures and 25 peoples, 70% of the land. That
  is effectively worldwide, which Daniel ruled out.

**3. How common should pantheons be on a polytheist world?**
- A: **Rare (lean).** Only towns that stay mixed for centuries, or empires over several peoples. About 2-8 per world, under a third of
  the land.
- B: Common: any mixed town. Most of the open land ends up in one pantheon or another.

**4. What does a faith that refuses other gods do?**
- A: **(lean)** Its cultures cannot join a pantheon, and a culture that converts to such a faith leaves its seats (the Meiji
  separation; the early Christians' refusal to sacrifice). If lane 219 (PW-1520) separates "exclusive" from "missionary", use exclusive.
- B: An exclusive faith can host a pantheon of lesser figures under its one god, like saints. This is more content, and later.

**5. War, harvest, smithing and ancestor gods never reach temple rank today.** Only a culture's single leading being individuates
fully, and those domains never lead. So the shared roster will be sea, sky, fire, forest, hunt, storm and river, never "the god of war".
- A: **(lean)** Let the second and third beings rise further with the faith techs (kingship, temples), so a war god or a harvest god can
  reach temple rank where war or farming dominates life. This is a small gods.py change and would be its own ticket.
- B: Leave it. The pantheons will be nature-heavy.

**My overall lean: 1A, 2B, 3A, 4A, 5A.** All of it is read-out only, like the minority faiths: the history and the majority faiths stay
as they are.

## Updates
- 2026-11-08: Status needs-decision -> done. Daniel ruled D68 11-08 (desk answers): 1 A+C (match, sometimes a new joint god), 2B, 3A, 4A, 5A, plus 'We need more domains in general I think.' Building in lane 236 (PW-1523), with more domains tied to world and culture drivers.
- 2026-11-08: Desk D68 (lean 1A 2B 3A 4A 5A).
- 2026-11-08: Created from inbox draft draft-regional-pantheons-design-choices.md (found by scout220).
