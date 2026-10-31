---
title: "Portal arrivals as a random yearly trickle (compound Poisson) that averages to the set founders over a few kyr; pooled to viable size before founding"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: low
found_by: lane-85
blocked_by: [PW-1185]
relates: [PW-1150, PW-1185, PW-1191]
refs: [docs/review/peoples-events/design.md, planet/lineages/history/portals.py, planet/lineages/history/founding.py]
---

## Description
**In plain words.** Owner 10-31: keep a fixed arrival size for now. Later, arrivals should come at random, year by year, and average
out to the standard number over longer periods. Wandering portals come after the other numbers are sane. Sketch:
docs/review/peoples-events/design.md, section 4.

- **The stream.** Mean μ = founders / stream kyr. Each portal opens at Poisson times, λ per year. A batch is lognormal (sd 1 in log,
  judgement) with mean μ / λ / portals. Per step: count ~ Poisson(λ dt), total ~ gamma with that many batches' mean and variance.
- **How it averages out.** CV over a window T is about sqrt((1 + CV_b²) / (λ T)). At λ = 0.01/yr: ±170% per century, ±24% per 5 kyr.
- **Pooling.** Arrivals wait at their portal until they reach `viable_pop`, then `found_people` sets them down.
- **Determinism.** One generator per (seed, plane, portal).
- **Variant.** Bursty, with λ following the wandering thinnings' open and close (PW-1191).

- [ ] stream option beside today's waves (meta switch), default waves until D21 settles
- [ ] a test that the 50 kyr mean is within 5% of founders
