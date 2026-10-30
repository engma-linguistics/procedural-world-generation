---
id: PW-1041
title: "Tech-tree kind rules name D&D line ids: in Seven Meals the giants aren't an elder kind, and the edge_folk rule matches nothing"
type: task
status: done
parent: null
milestone: null
subsystem: timezoom
effort: xs
impact: med
found_by: code-audit-2026-10
blocked_by: []
relates: [PW-946, PW-943]
refs: [planet/lineages/samples/techtree.toml, planet/lineages/techtree.py, planet/lineages/samples/seven_meals.toml, docs/review/code-audit-2026-10/index.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words. The tech tree's "who starts with what" rules are tied to the exact names of peoples in the D&D preset. Your own Seven Meals world calls its giants `giant`, not `true_giant`, so its giants silently don't count as an elder kind, and one rule (edge_folk) refers to something that isn't a people at all, so it never applies. Any custom tree silently loses all these rules.

From the lineages audit (probed there): techtree.toml:59-87 `[[kind]] of = "draconic" | "kobold" | "dragonborn" | "true_giant" | "elf" | "gnome" | "triton" | "edge_folk" | "dwarf"`; `edge_folk` is an `[[exonym]]` id in both presets; seven_meals has `giant` and no `triton`.

Fix now: techtree warns on an `of` that matches no line, and `of` accepts a list (`["true_giant", "giant"]`). Better later (owner call): put kind facts (elder, hands, kit, rate_x) on the lineage rows themselves.

Source: codebase audit 2026-10-29 (docs/review/code-audit-2026-10/index.html).

## Updates
- 2026-10-29: Status todo -> done. Fix lane 49: a [[kind]] of may be one id or a list (techtree.load normalises to a list; _kind maps each id); techtree.build warns 'tech tree [[kind]] rules name no line of this tree: ...' for each rule none of whose ids is a line of the tree. Seven Meals' giant is clearly the D&D true_giant's counterpart (the giants stem, steadings, generation 65 yr, megafauna), so the rule is now of = ["true_giant", "giant"] (elder). The D&D tree's outputs are unchanged (it has no 'giant' line). edge_folk (an exonym, not a line) left as is: intent unclear, needs-decision inbox draft. The warning also fires for Seven Meals' missing triton and saurian lines, correctly. Test: test_techtree.test_kind_rules_take_several_ids_and_warn_on_none.
- 2026-10-29: Created from inbox draft draft-techtree-kind-rules-match-preset-ids.md (found by code-audit-2026-10).
