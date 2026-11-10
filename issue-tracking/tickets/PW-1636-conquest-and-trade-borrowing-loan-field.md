---
id: PW-1636
title: "Conquest and trade borrowing: loan field profiles by contact kind, superstrate fix on shift, food and register doublets (cow/beef, wheat/flour)"
type: task
status: todo
parent: PW-767
milestone: v4
subsystem: culture
effort: m
impact: high
found_by: lang-coordinator
blocked_by: []
relates: [PW-1561, PW-1568]
refs: [docs/review/language/proposal-2026-11-10-paradigms-and-conquest.md, planet/language/history.py, planet/language/lexicon.py, "planet/language/faiths.py::learned_register", planet/language/checks.py, tools/language/sketch.py, "run a24559", "run de1cc6"]
created: 2026-11-10
updated: 2026-11-10
---

## Description
In plain words: Daniel asked 11-10 for Norman-conquest borrowing: when one people rules another, prestige words
(government, law, war, fine food) are borrowed heavily while basic words stay native, and a language can end up with
two words where it had one: the farmer's animal and the lord's meat (cow/beef, pig/pork), the ingredient and the
product (wheat/flour), plain and learned registers. Trade languages also lend business and counting words (Arabic into
Swahili). He called this super important to Seven Meals (the culinary pages). Today borrowing is blind to the kind of
contact, so a conquered language reads like a neighbour-influenced one, and every concept has one word.

Scope (proposal Part 2, coordinator settled D2.1 B and D2.2 B): P1 field profiles by contact kind (takeover/elite,
trade, neighbour, substrate), mean-normalised, with the swamp-direction superstrate fix on shift; P3 the new concepts
(animal vs meat, ingredient vs product, trade and business terms); P2 the doublet draw (meaning splits, food first)
and a high-register table reusing the faiths' learned-register shape; the sketch and demo show them. Trade numerals
wait for the desk card p.numerals. If never done, the culinary pages have no beef/pork-style histories and conquest
leaves no visible mark on a language.

## Updates
- 2026-11-10: Created from inbox draft draft-conquest-borrowing.md (found by lang-coordinator).
