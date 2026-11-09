---
title: "Languages: after the concave L2 map no language reads as a lingua franca (90th percentile 0.35, none above 0.5)"
type: task
status: needs-decision
parent: PW-767
milestone: null
subsystem: culture
effort: s
impact: med
found_by: lang-rulings (2026-11-08)
blocked_by: []
relates: [PW-1542, PW-985]
refs: ["planet/language/inputs.py::l2_share", planet/language/inputs.py, "planet/language/grammar.py::social_factors", "planet/language/checks.py::hubs", docs/review/language/calibration.md, "run a24559", "scratch passes rulings/bursts, rulings/alone (deleted; numbers in calibration.md 'Rulings lane')"]
---

## Description
In plain words: every language carries a number for "how many adults learn it as a second language". Daniel ruled
(PW-1542 (b)) that it should rise steeply at first and then level off, with the median language near 0.25. That is
done, and the median is 0.25. But the inputs that feed it rarely exceed about 1.2, so the curve squeezes the whole world
into 0.13-0.35: no language is a contact hub any more. Real adult-learner shares are small for most languages and very
large for a few lingua francas (Swahili, Malay, Hausa: more L2 than L1 speakers; Lupyan & Dale 2010).

Measured on a24559 (bursts pass, 622 living lects): l2 quantiles 10/25/50/75/90% = 0.13 / 0.19 / 0.25 / 0.30 / 0.35, none
at the 0.7 ceiling (before: 0.24 / 0.39 / 0.54 / 0.69 / 0.70, 151 at the ceiling). The "hubs simpler" check still passes
(hub 19.2 against isolated 23.0), but its hubs are now the top quarter of a narrow band.

**What misleads if never done:** the simplification a contact language gets (fewer endings, more regular forms) now
reads about the same everywhere, so the pages and the synthesis numbers show no language shaped by heavy adult
learning, and the one social contrast Trudgill's account rests on is flattened.

Options: (a) keep (the median is right; hubs are a later polities question); (b) feed the curve a sharper input: the
other peoples' share of *speakers* rather than of cells (PW-1542's option a), plus mixed-city heads, so a true hub's
input reaches 2-3 and its l2 0.6+; (c) a two-part map: the concave curve up to the median, then linear toward L2_MAX for
the top decile. Lean: (b), it is the measured quantity the proxy stands in for.

- [ ] decide (a), (b) or (c)
- [ ] if changed: re-measure the l2 quantiles, the WALS 22A bins by L2 band and the hubs check
