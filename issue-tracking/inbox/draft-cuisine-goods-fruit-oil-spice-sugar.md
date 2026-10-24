---
title: Crops table lacks the non-staple cuisine plants (tree fruit, olives and vines, oil seeds, spices, sugar, tea and coffee, cooking greens)
type: story
status: todo
parent: PW-692
milestone: v3
subsystem: timezoom
effort: m
impact: med
found_by: fun7
blocked_by: []
relates: [PW-721, PW-692, PW-719]
refs: [planet/lineages/crop_defs.py, planet/lineages/crops.py]
---

## Description
`crop_defs.TABLE` has ten real staples (wheat and barley, lentils and peas, foxtail millet, rice, sorghum and pearl millet,
maize, potato-like tubers, yams/taro/cassava, bananas, rye and oats) and two rare fantasy rows. The culinary pass
(PW-692) will also want, as rows of the same shape (a wild range, anchor, who, spread, effect), the plants that flavour
and fatten the plate and bring trade: tree fruit and nuts, olive and grape, oil seeds (sesame, flax, oil palm), spices
(pepper, cinnamon, chilli-like; capsaicin ties to the senses epic), sugar cane, tea and coffee, brassicas and alliums.
They add little to `farm` capacity (small `k`, `weight` 0), mostly to a per-cell "crops known" list and later to trade.
Rows can be added without code changes beyond the table, up to 16 crops in the uint16 bit-flag layers (widen the layers
past that).
- [ ] fruit/oil/spice/sugar rows with wild ranges from climate, soils and (for vines/olives) dry summers

## Updates
