---
id: PW-1649
title: Tech tree has no food, water or supply techs on the arcane side (and no field rations or depots)
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane279
blocked_by: []
relates: [PW-1449, PW-1478, PW-1108]
refs: [docs/review/culture/polities/logistics-proposal.md, planet/lineages/samples/techtree.toml, "planet/lineages/trade_flow.py::has_pack", planet/lineages/polities.py, planet/lineages/invasions.py]
created: 2026-11-10
updated: 2026-11-10
---

## In plain words
Magic in the tech tree can bond beasts, ward with runes and enchant arms, but it cannot feed an army or clean its water. If it never
does, wizards and clerics are invisible to every campaign and siege, and the new supply numbers will only ever read mundane tech.
On the mundane side there is no field ration or army depot node either.

## Description
Add nodes, gated as in `logistics-proposal.md` section 3.2: `water_purifying` (druidcraft + boiling_pots), `preservation_charm`
(druidcraft or runes + smoking_drying), `conjured_provisions` (arcane_schools), `pocket_storage` (enchanting), `divine_provisioning`
(divine_magic, gods-gated), plus mundane `waterskins`, `field_rations`, `army_depots`. Generic names only. Nothing reads them until the
logistics scalar lands (sibling draft); they change no output.
- [ ] nodes added with gate, tier, domains, fantasy mode and source text; tech tree builds without warnings
- [ ] `uv run pytest -q` passes; showcase trees rebuilt
- [ ] if never done: fantasy worlds look identical to mundane ones in war reach and siege

## Updates
- 2026-11-10: Owner 11-10 caution: magical warfare must not become a rabbit hole. Build ordinary supply (carry, store, organise) first; the magic side is optional. At the first hint of odd behaviour that can't be quickly brought to semi-reasonable, drop the magic part and park it in later. No 'realism' tuning of magic warfare.
- 2026-11-10: Owner 11-10 D74 C (casters limit only strong spells) plus a world dial for how magical the world is (none to high fantasy) that sets how many strong casters a people has, like generals in an army. D73 C: magical supply needs magical/alchemical resources and trade goods.
- 2026-11-10: Created from inbox draft draft-arcane-provisioning-techs.md (found by lane279).
