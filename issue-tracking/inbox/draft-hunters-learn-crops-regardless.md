---
title: "Hunting kinds take up farming as fast as anyone: the crop front, not their leaning, decides (density ladder Q2 A)"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: lane 137 (density ladder check d)
blocked_by: []
relates: [PW-1275, PW-1350, PW-721]
refs: ["planet/lineages/crops.py::Crops.step (took_up: adopt >= 0.2 x prop)", "planet/lineages/animals.py::Stock._front", "planet/lineages/animals.py::Stock._propensity", "planet/lineages/crop_defs.py::_PROP", "planet/lineages/ladder.py::Ladder.tech", "planet/lineages/ladder.py::Ladder.line", planet/lineages/samples/dnd.toml, docs/review/peoples/density-ladder/build.md, docs/review/peoples/density-ladder/ladder.md, tools/peoples_robust.py]
---

## Description
In plain words: on the new density ladder a people farms all its farmable land as soon as it "knows" a crop. A people knows a crop once
the crop has spread over a fifth of its land, and crops spread over any peopled land at about 1 km a year whoever lives there. A
people's leaning to farm (its propensity: ~1 for farmers, 0.1 for hunters) is multiplied into both sides of the test
(`adopt = share x prop >= 0.2 x prop`), so it cancels out. So tabaxi, leonin, goliaths and bugbears become full farmers within a few
thousand years of a crop reaching their land; in the lane 137 D&D runs most tabaxi and goliaths live as plough or irrigation farmers
and over half of leonin farm (tables in build.md).

Is that sane? The land-decides ruling (Q2 A) is applied as ruled, but the "knows" switch is too easy: on Earth, foragers beside
farmers often stayed foragers for a long time, and a kind whose lore is hunting would be among the slowest to switch.

Options:
- (A) keep as is (knowing = farming: the ruling read literally);
- (B) delay knowing by the leaning: a people takes up a crop once the crop has stood on a fifth of its land for a time ~ LAG / propensity
  (farmers at once, hunters ~10x slower); the share that farms once it knows is still the land's (Q2 A);
- (C) scale the farmed share by the leaning (hunters farm a tenth of their farmable land): closer to Q2 B, which was not chosen.
Lean B: it keeps Q2 A and lets each kind's lore show as a delay, not a cap. Measure on the robust suite.
