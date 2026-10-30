---
id: PW-1123
title: "Tech tree: let neighbours in contact add to a people's pool of learners (Kline & Boyd 2010; Henrich's effective size)"
type: task
status: todo
parent: PW-675
milestone: null
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-64
blocked_by: []
relates: []
refs: [planet/lineages/techtree.py, docs/references/techtree/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In the v1 invention model, a people's pool of learners is its own population (x specialists x learners). Contact acts only through
diffusion: a known tech passes over a border. Henrich 2004 and his reply to Vaesen et al. 2016 say what matters is the effective,
interacting pool. Kline & Boyd 2010 found that contact matters more for small Oceanic populations. So a small people well connected
to big neighbours should invent somewhat more than the same people alone, not only copy.

What to try: pool_eff = N + c x sum over neighbours in contact of (their N x border weight), with c small (say 0.1 to 0.25, a
judgement) and only on the "all" pool. Check that firbolgs and goliaths beside big peoples invent a little more, and that the big
peoples barely change (log form).
- [ ] contact pool term, off by default until checked
- [ ] firsts table before and after on two runs

## Updates
- 2026-10-30: Created from inbox draft draft-techtree-contact-pools.md (found by fun-lane-64).
