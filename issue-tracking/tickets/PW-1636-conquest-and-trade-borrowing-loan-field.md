---
id: PW-1636
title: "Conquest and trade borrowing: loan field profiles by contact kind, superstrate fix on shift, food and register doublets (cow/beef, wheat/flour)"
type: task
status: done
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
- 2026-11-10: Status todo -> done. Lane 13 (lang-lane13): P1 field profiles by contact kind (contact.py; elite = takeover + elite incursions + the rulers' speech after a shift; trade; city; flat), mean-normalised, crops x1 under trade, closed class x1; swamp-direction superstrate fix; P3 meat concepts (animal + MEAT compounds) and 12 trade/rule/law concepts by technology; P2 meat and product splits (data/splits.tsv) and a formal register (systems.registers.high); doublets in the sketch and demo page; checks 'loans follow the contact kind' (a24559: 1.78x) and 'doublets under elite rule' (77%). Trade numerals hook off (contact.TRADE_NUMERALS) pending desk card p.numerals. a24559: 190 meat + 159 product doublets in 170 languages, 1,052 formal synonyms; WOLD rho 0.403 -> 0.425, pronoun loans 0.082 -> 0.066, sisters 0.562 -> 0.531. Write-up: docs/review/language/for-daniel.md (Lane 13). Viewer/cuisine display and the broad trade label left as drafts.
- 2026-11-10: Created from inbox draft draft-conquest-borrowing.md (found by lang-coordinator).
