---
id: PW-209
title: Take mangrove forest and salt marsh from PW-188's coastal layers in the vegetation classifier
type: task
status: todo
parent: null
subsystem: coast
effort: xs
impact: low
found_by: veg
blocked_by: []
relates: [PW-188, PW-187]
refs: [planet/vegetation.py]
created: 2026-10-15
updated: 2026-10-15
---

## Description
Owner decision 7B moved mangroves and salt marsh to PW-188. The named types 55 (mangrove forest) and 56 (salt marsh) are in `vegetation.TYPES` and the legend, but `vegetation.classify` never assigns them: rule 2 of the proposal's classification ("coastal: mangrove or salt marsh over 30% of the cell") needs PW-188's layers. When PW-188 lands, add the rule after the ice/lake rules (`put(mangrove_share >= 0.3, T["mangrove forest"])`, same for salt marsh) and pass the layers into `vegetation.model`; gate mangroves with plant group 4 and salt marsh with group 5 (`vegetation.GROUPS`).

## Updates
- 2026-10-15: Created from inbox draft draft-veg-mangrove-classifier.md (found by veg).
