---
title: "Tech tree v0 is output only: let known techs feed back into the history (boats, densities, farming)"
type: story
status: todo
parent: PW-675
subsystem: timezoom
effort: l
impact: med
found_by: fun39-techtree
blocked_by: []
relates: [PW-913, PW-688, PW-869]
refs: [planet/lineages/techtree.py, planet/lineages/history/]
---

## Description
techtree.py runs after the peoples history, using what the history saved: lines, contacts, tamings, the present range and the world's goods. Nothing it decides changes the history. A people's sea reach does not wait for rafts or canoes, and its density does not rise with cultivation or towns. Crops and herds spread by their own fronts (crops.py, animals.py). The next step is to step the tree inside the history (History.run, one call per step) and read a few techs back: rafts and canoes for crossings (the craft list in animals.py already has dates), cultivation and towns for density, riding for speed.

A second gap: the land check reads only each people's present range. A line that is gone by the present is not checked at all, and a people's past range is not used. With the tree inside the history, the check would read the range at each step.
- [ ] tree stepped in History.run (same rules, same seeds)
- [ ] crossings read rafts / canoes / sails
- [ ] the land check reads the range at each step
