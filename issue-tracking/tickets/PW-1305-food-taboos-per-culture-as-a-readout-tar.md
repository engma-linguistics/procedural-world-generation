---
id: PW-1305
title: "Food taboos per culture as a readout: target, scope and origin (practical, symbolic, divine, identity, purity)"
type: story
status: todo
parent: PW-1308
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: religion-doc-chat
blocked_by: []
relates: [PW-719, PW-692]
refs: [planet/lineages/brief.py, planet/lineages/animal_defs.py]
created: 2026-11-02
updated: 2026-11-02
---

## Description
In plain words: each culture gets a few foods it won't eat, or that only some people may eat, with a reason the sim can point
to. This feeds the culinary book straight away (PW-692). brief.py already notes an unconsulted canid taboo (PW-719).

Settled in the religion doc (https://claude.ai/artifact/Tk4g2nkJPQpTJgeDXo6KoP (Claude Docs id d890d9ce-3695-47c4-add1-a21c3c1a3bf2)), section 6 plus Daniel's comment on cleanliness:
- Fields: target (species, part or season), scope (everyone, priests, pregnant women, a lineage), origin.
- Origins the sim can seed:
  - Totem: a species heavily relied on, or feared.
  - Identity: a neighbour's staple, refused (links to reputation grudges).
  - Practical: seasonal poison or parasites, only if ever modelled.
  - Divine: a god's domain.
  - Purity: Douglas 1966, on Leviticus. Animals that straddle the culture's own categories (habitat, diet and body from
    animal_defs) become "unclean". The number of rules scales with the culture's purity weight on the moral ledger. Ritual
    slaughter and blood rules are a possible later field.
- The explanation, consequence and enforcement are writer's material, not computed.

## Updates
- 2026-11-02: Created from inbox draft draft-food-taboos.md (found by religion-doc-chat).
