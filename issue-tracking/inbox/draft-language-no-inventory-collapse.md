---
title: "Languages: no line collapses Hawaiian-style; the inventory-size anchor holds every line at its proto size whatever its rate"
type: task
status: needs-decision
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lang-rulings (2026-11-08)
blocked_by: []
relates: [PW-1539]
refs: [planet/language/lect.py, "planet/language/lect.py::Lect.rate_now", "planet/language/inventory.py::size_prior", docs/review/language/calibration.md, "run a24559", "scratch passes rulings/base, rulings/alone, rulings/bursts, rulings/final (deleted; numbers in calibration.md 'Rulings lane')"]
---

## Description
In plain words: Daniel ruled (PW-1539 E) that some lines should change much faster than others, so that now and then a
language wears its sounds down to a Hawaiian-sized set (8 consonants). The rate spread is in (lect.RATE_SIGMA 0.5, and a
x2 burst for 1 kyr after a shift or a founder split), but no language collapses: living lects under 10 consonants were
1 before, 1 with the spread alone, 0 and 1 in two passes with the bursts (a24559, about 620 living lects; the one
is a bronze-dragon lect drawn small; 5th percentile 13 consonants).

Why: a lect's rate sets how many sound changes it draws, not which. The inventory-size steer (`SIZE_K`, `SIZE_ANCHOR`
0.12 in lect.py) weights every rule toward keeping the line near its own proto size, so a fast line makes more changes
that cancel out: across the bursts pass the consonant count does not depend on rate at all (correlation -0.03; median
change against the proto 0 / -1 / -1 for rate under 0.7, 0.7-1.4, over 1.4).

**What misleads if never done:** the world has no small-inventory languages except those drawn small at the start, so
Polynesian-type histories (a founder population spreading over islands and losing contrasts) never happen, and the
rate ruling reads as done when it changed only the scholars' horizon.

Options: (a) accept: small inventories come only from small protos; (b) loosen the anchor during a burst (a founder or
shifted line re-anchors toward a smaller size: SIZE_ANCHOR x 3 while `burst_until` holds), so a founder line can drift
down and then holds its new size; (c) a founder-specific merger boost (mergers weighted up during a burst on an island
or coast founder). Lean: (b), one line, and it is what a founder effect is.

- [ ] decide (a), (b) or (c)
- [ ] if changed: count living lects under 10 consonants and re-run the inventory-size check
