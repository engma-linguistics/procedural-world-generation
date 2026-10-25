---
id: PW-851
title: Hybrid fertility follows real divergence times (fertile to ~1-2 Myr, mostly sterile to ~4 Myr), not a quarter of them
type: task
status: done
parent: PW-692
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: owner-feedback-2026-10-25
blocked_by: []
relates: []
refs: []
created: 2026-10-25
updated: 2026-10-25
---

## Description
Owner feedback 2026-10-25 (feedback doc on world 2a7385): Owner: align hybrid timing to real-world approximations instead of the 1/4 initial guess.

## Updates
- 2026-10-25: Status todo -> done. Merged fun lane 26 (80c1df3).
- 2026-10-25: Created.
- 2026-10-25: fun lane 26. Tier limits now T1 < 1.1 Myr (fertile), T2 < 4 Myr (mostly sterile), T3 beyond (was 1 Myr / 40 Myr); `spec.fertility_at(d)` gives the share of hybrid matings bearing fertile young (1 under 1.1 Myr, 0.2 falling to 0.02 across T2, 0 beyond) and `Tree.fertility(a, b)` reads it from the lineages' own split dates ([[interfertile]] rows give their tier's nominal share; no common ancestor, e.g. arrivals, gives 1: the half-elf exemption). A contact hybrid's share of its hosts' people scales by it (`History._fertility`); the contact pairs carry `hybrid_fertility`. seven_meals: antelope-kin x cervid-kin (~25 Myr) become T3. Brief version 9. Tests: test_hybrid_fertility_follows_divergence_times, test_a_contact_hybrid_of_distant_parents_is_a_thinner_share.
