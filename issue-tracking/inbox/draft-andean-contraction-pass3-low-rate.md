---
title: "Andes pass 3: screen the overriding-plate contraction (option A) at the long-term rate, share 0.1"
type: task
status: todo
parent: null
milestone: later
subsystem: tectonics
effort: m
impact: med
found_by: scout 237
blocked_by: []
relates: [PW-1497, PW-1509, PW-1293]
refs: [docs/review/tectonics/mountains/scout7.md, docs/review/tectonics/mountains/scout7_measure.py, docs/review/tectonics/mountains/scout6.md, "planet/tectonics/crust.py::andean_contraction", "planet/tectonics/crust.py::to_ocean", "planet/tectonics/plates.py::Plates.short_pool", "planet/tectonics/params.py::andean_shortening", "Medvedev et al. 2006 (The Andes, ch. 23)", "Gotberg, McQuarrie & Carlotto 2010 GSA Bull 122", "Schellart 2008 GSA Bull 120"]
---

## Description
In plain words: the overriding plate can now really contract at ocean-continent trenches (`andean_shortening`, off
by default; scout 237, PW-1497 strike 2). At the present central-Andes rate (share 0.4 of the plate's advance) it
puts Andes where Andes belong (22-25% of high ground at margins against main's 11-18%, Earth 25%; continental area
held far better than scout 209's arms) but makes 4-8x main's land above 3 km (10.6-12.3% against 1.4-2.7%, main on
the same 3 L6 seeds x 600 Myr). Earth's Andes shorten in bursts, so the long-term mean is several times lower; a
one-seed L5 sweep at share 0.1 lowered total high ground (1.7% against main's 2.9%) with 29% of it at margins.
If never done, PW-1497 stays open on a lead nobody tested: either margin ranges come cheaply at the long-term rate,
or the ticket should be parked for good.

Strike 3 of 3: if share 0.1 fails at L6, park PW-1497 (option B).
- [ ] L6 screens, share 0.1 and 0.05, seeds 1, 2, 6001 x 600 Myr, `scout7_measure.py`, against main's row in scout7.md
- [ ] pass bar: Andes share >= ~20%; land > 3 km near main's 1.4-2.7%; continental area within ~2 points of main
- [ ] if it passes: full judge (two-tier bar, hard failures 0), `tools/scorecard.py`, make the share the default
