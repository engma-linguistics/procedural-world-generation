---
title: "Tech tree: taming dogs counts as herding, so herding's world first is ~14 kyr (Earth 11) and the plough and cheese chains start early"
type: task
status: todo
parent: PW-675
milestone: null
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-69
blocked_by: []
relates: [PW-1122]
refs: [planet/lineages/techtree.py, planet/lineages/samples/techtree.toml]
---

## Description
In plain words: when the history tames any animal, the tech tree gives that people "herding". Dogs are tamed first (~15 kyr), so
herding's world first is ~14.3 kyr in all 4 D&D runs (Earth: ~11 kyr, sheep and goats), and herding is "found" 14-24 times a
world (most of them the dog). Everything after herding (milking, cheese, the plough) then starts early where the history gives a
people dogs. Since PW-1122 the dog stock is its own tech (`dogs`, stock "animals:dog").

Fix: in techtree.build, skip the generic "animals" stock (herding) for the dog stock (or give each stock a flag in animal_defs:
herd = false for dogs). Check: herding's world first and finds per world before/after on the four runs; settlements unchanged
(they read villages, towns, cities).
