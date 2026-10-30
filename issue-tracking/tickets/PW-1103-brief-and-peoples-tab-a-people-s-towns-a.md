---
id: PW-1103
title: "Brief and Peoples tab: a people's towns and cities, its ruins and the city quarters, from the settlement ledger"
type: task
status: todo
parent: PW-856
milestone: v2
subsystem: timezoom
effort: s
impact: high
found_by: fun-lane-60
blocked_by: []
relates: [PW-1011, PW-910, PW-889]
refs: [planet/lineages/settlements.py, planet/lineages/brief.py, viewer/lineages.html]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. The settlement ledger (PW-1011 v0, `settlements.json` in a peoples run) records every village, town and city of the last ~12 kyr:
- who founded it and who holds it now;
- its size over time;
- when and why it was left (sea, ice, drought, a river moving, driven out, its people left);
- who lives in it, with the city-minority quarters (city kobolds 2%, city goblins 3%).

It shows on the globe, but the culinary brief and the workbench's Peoples tab don't read it yet. The book's city chapter (quarters, diaspora, the docksides) needs it in the brief.

What to add:
- a "Towns and cities" block in the brief per people and per region: the largest places and who lives in them, the minority quarters, the famous ruins and what ended them, the towns taken from another people;
- a line per people in the workbench ("4 cities, 52 towns, 300 villages; 40 ruins; held 120 kenku towns since ~3.7 kyr").
- [ ] brief block and Peoples-tab line from settlements.json

## Updates
- 2026-10-30: Created from inbox draft draft-settlements-in-the-brief.md (found by fun-lane-60).
