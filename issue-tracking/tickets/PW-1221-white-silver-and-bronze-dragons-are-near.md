---
id: PW-1221
title: "White, silver and bronze dragons are nearly gone once the herds are fed only the above-ground NPP: cold, dry land holds 5-7x fewer grazers"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: lane-90
blocked_by: []
relates: [PW-1073, PW-1065]
refs: [planet/lineages/prey.py, planet/lineages/history/megafauna.py, planet/lineages/samples/dnd.toml, docs/review/dragon-food-chain/report.md]
created: 2026-10-31
updated: 2026-10-31
---

## Description
**In plain words.** The owner ruled that the grazing herds should be fed only the part of the plants that grows above ground, which is
what the herd formula was fitted on. In cold and dry country most of a plant's growth is roots, so the herds there shrink to a fifth or
less, and the dragons that live there have almost nothing to eat. White dragons fall from a few thousand on a world to a few dozen, and
on some worlds to a handful; silver and bronze fall nearly as far. The owner asked for white and silver dragons on cold, poor land,
"just fewer". They are now so few that a player would rarely meet one. Something has to give: accept it, or give the cold and coastal
dragons a food they really have.

Evidence (lane 90 report, six worlds at roll 7000, present day): white dragons 734-3,272 before, 3-82 after; silver 257-1,435 before,
6-317 after; bronze 292-1,985 before, 28-474 after. In white country on world 6909cb the median prey fell from 0.39 to 0.05 t/km2 (x0.14,
the above-ground share's f^1.52 at ~250 mm of rain); the cells the white dragons hold fell from 0.24 to 0.009 t/km2. Diagnosis traces on
6909cb (scratch, not committed): the old viable-population floor (line_mvp instead of LINKED_MVP) and no persecution each leave the white
dragons where they are (mean over the last 290 kyr 150 -> 177 and 151); feeding the dragons over the ancients' hunting range (HUNT_KM,
~173 km) instead of the food-weighted mean range (~77 km) raises it to ~225 and lowers the silver dragons. So it is the food itself.

Options:
- **A.** Accept: white, silver and bronze dragons are legendary rarities. Nothing to do.
- **B.** Sea food for the coast and ice kinds: real cold-country top predators live off the sea (seals, fish, seabirds), which the
  model does not count at all (the coast only carries the land's herds one ring out to sea). A marine-prey field from the ocean's
  productivity, read by kinds that hunt the sea (white, bronze, blue on the coast). Needs a source for marine mammal biomass by
  productivity. The sound fix; a new mechanism.
- **C.** Feed the dragons over their whole hunting range (HUNT_KM) instead of the food-weighted mean: helps the white dragons a little
  (~1.5x in one trace) and costs others; not a real cure.

Lean: B for v1 if the owner wants white dragons to be met in play; else A, with B in v2.

## Updates
- 2026-10-31: Created from inbox draft draft-cold-dragons-thin-after-above-ground-prey.md (found by lane-90).
