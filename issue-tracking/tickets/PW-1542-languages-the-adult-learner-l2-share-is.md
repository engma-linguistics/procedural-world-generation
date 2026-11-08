---
id: PW-1542
title: "Languages: the adult-learner (L2) share is a co-presence proxy; a third of living lects sit at its 0.7 ceiling"
type: task
status: todo
parent: PW-767
milestone: null
subsystem: culture
effort: m
impact: med
found_by: lang-synth (synthesis lane, 2026-11-08)
blocked_by: []
relates: [PW-985]
refs: ["planet/language/inputs.py::l2_share", "planet/language/grammar.py::social_factors", docs/review/language/calibration.md, "run a24559"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: every language carries a number for "how many adults learn it as a second language", which makes it
simpler (fewer endings, more regular). We do not measure learners; we estimate the number from how much other peoples
live on the same land. That estimate is high almost everywhere: half the living languages are above 0.54 and a third sit
at the cap of 0.7, so a remote valley people next to one neighbour reads like a trade city. The synthesis lane softened
how hard the number bites (so languages are no longer mostly isolating), but the number itself still blurs the
difference between a real contact hub and an ordinary border language.

Measured on a24559 (polish pass 1, 624 living lects): l2 quantiles 10/25/50/75/90% = 0.22 / 0.38 / 0.54 / 0.69 / 0.70;
196 of 624 at exactly 0.7 (`L2_MAX`). Real-world adult-L2 shares are small for most languages and large for a few lingua
francas (Lupyan & Dale 2010; Bentz & Winter 2013).

**What misleads if never done:** the "hubs simpler" check picks its hubs as the top quarter by this proxy, which is
mostly a tie at 0.7; and every L2-driven rate (grammar loss, regularization, typology drift x(1 + l2)) acts on most of
the world as if it were a contact hub. Synthesis numbers (WALS 22A) and simplification stories in the history read
from it.

Options: (a) scale the co-presence by the other people's share of speakers rather than of cells, so a small neighbour
adds little; (b) a concave map (e.g. l2 = L2_MAX x (1 - exp(-k x share))) with k fitted so the median sits near 0.2-0.3;
(c) leave it and keep the softer grammar response (current). Your call; (b) is the cheapest. Any change needs the
synthesis bins and the hubs check re-measured (`scratchpad synth/fullan.py`).

- [ ] decide the shape of the L2 proxy
- [ ] re-measure WALS 22A bins and hub/isolated complexity after the change

## Updates
- 2026-11-08: Created from inbox draft draft-language-l2-proxy-ceiling.md (found by lang-synth (synthesis lane, 2026-11-08)).
- 2026-11-08: RULING (owner, Language Desk 11-08): option (b), a concave map with the median near 0.25; re-measure synthesis bins and hubs.
