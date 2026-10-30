---
id: PW-1023
title: "Technology map: a cell shows only its leading people's knowledge, so small or mixed peoples hardly show"
type: task
status: todo
parent: PW-913
milestone: v2
subsystem: viewer
effort: s
impact: med
found_by: fun-lane-47
blocked_by: []
relates: [PW-913]
refs: [viewer/index.html, "run 3097e3", docs/review/techtree-tab/3-map-at-an-event.png]
created: 2026-10-29
updated: 2026-10-29
---

## Description
In plain words: on the globe's "technology" layer each cell takes the colour of the one people that holds most of it (the run's `peoples` layer). A people that lives mixed in with a bigger neighbour, or holds few cells of its own, barely shows even when it is the one that invented the tech. In run 3097e3, halflings invented pottery 18.8 kyr ago, but at that moment almost no cell has halflings as its leading people, so the map at the invention shows the star over land that looks grey ("not yet").

What to try: colour a cell by any people there that knows the tech (the run has `mix_lead` / `mix_second` and their shares), lit by the share of the cell's people who know it; or tint the cell when its second people knows it. The hover card already says what the leading people knows.
- [ ] the inventor's own land is visibly lit at the moment of the invention, in run 3097e3 (pottery, halflings)

## Updates
- 2026-10-29: Created from inbox draft draft-techtab-map-leading-people-only.md (found by fun-lane-47).
