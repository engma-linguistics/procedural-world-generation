---
id: PW-1477
title: "Faiths barely spread: conversion is a 30 kyr e-folding per contact, only from temple faiths; no evangelism, no forced conversion"
type: task
status: done
parent: null
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: owner
blocked_by: []
relates: [PW-904]
refs: []
created: 2026-11-04
updated: 2026-11-05
---

## Description
In plain words: Daniel's written faith didn't spread. Today (planet/lineages/gods.py) a faith converts a neighbouring culture only if its leading being is organised (CONVERT_MIN 0.45, temples) and 0.15 more so than the neighbour's, with chance 1 - exp(-dt / 30 kyr) per contact: thousands of times slower than the world religions spread (centuries). There is no evangelism (missionary faiths that spread faster) and no forced conversion by a conquering state. Needs: a sourced spread rate, a missionary trait on a faith, and conversion by rulers (states, PW-1434) read through attitudes (PW-904).

## Updates
- 2026-11-05: Status todo -> done. Lane 199 merged (attitudes v0 / faith spread; docs/review/culture/attitudes/round1.md). Rest: PW-1480 (grudges, xenophobia), PW-1481 (conquest reads attitudes), PW-1482 (how many world faiths, desk D57).
- 2026-11-04: Created.
