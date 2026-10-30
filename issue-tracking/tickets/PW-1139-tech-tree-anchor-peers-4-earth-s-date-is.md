---
id: PW-1139
title: "Tech tree: anchor_peers = 4 (Earth's date is the first of four peoples' finds) is a judgement; confirm or pick another"
type: task
status: needs-decision
parent: PW-675
milestone: null
subsystem: timezoom
effort: xs
impact: low
found_by: fun-lane-70
blocked_by: []
relates: [PW-1137, PW-1124]
refs: [planet/lineages/techtree.py, planet/lineages/samples/techtree.toml]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words: the tree used to assume that Earth's first copper-smelters were a typical people, so every one of our peoples
was as quick as they were. Earth's first finder was really the quickest of several peoples who could have done it. Lane 70
now sets each Holocene tech's rate so the FIRST of four such peoples is as quick as Earth was. Four is my choice, not a
measured number, and you may want a different one.

What it does (fun lane 70, 4 runs x 2 draws, with contact as a 1 km/yr front):
| anchor_peers | finds per world / Earth origins (median) | copper finds (Earth 4) | world firsts vs Earth |
|---|---|---|---|
| 1 (the old rule) | 2.1x | 7.2 | copper 8.8 kyr (6.95), writing 8.7 (5.3), iron 7.9 (3.3): 1.4-4.6 kyr early |
| 4 (built) | 1.3x | 5.6 | copper 5.8, writing 4.1, iron 3.6, cities 6.1 (6), wheel 4.8 (5.5) |
| 10 | 0.9x | 3.0 | copper 5.5, writing 4.1, iron 1.9, cities 4.2: 1-2 kyr late |

Lane 64's earlier rejection of a k = 4 factor (writing's world first fell to 0.9 kyr) was with slow contact and the pure
k-times-longer form. Now the factor is the ramp's first-of-n (techtree.ramp_first) and packages travel by contact, and the
world firsts hold. The value sets one per-people number for every soft tech; there is no source for it.

Options: A keep 4. B tie it to something in the world (e.g. how many peoples are ready within a kyr of the world's first), so
a world of few big peoples is not held to Earth's many small ones. C 3 or 5, to tune the finds a little.
Lean: A for v1.

## Updates
- 2026-10-30: Created from inbox draft draft-techtree-anchor-peers-judgement.md (found by fun-lane-70).
