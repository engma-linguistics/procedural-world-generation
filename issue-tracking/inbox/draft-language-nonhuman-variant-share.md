---
title: Non-human sound variants turn up in far too many proto-inventories (growls in 54% of bird and 78% of reptile languages)
type: task
status: todo
parent: null
subsystem: culture
effort: s
impact: med
found_by: lang-design review fixes (percepts/romanize/profiles)
blocked_by: []
relates: [PW-1423]
refs: [planet/language/inventory.py, planet/language/profiles.py, planet/language/data/voice_profiles.toml, docs/review/language/voice-profiles.md]
---

## Description
In plain words: when a species can make a growled, purred or two-voiced sound, the inventory draw adds such a variant of each of
its 30 commonest sonorants and vowels, each with a made-up frequency of 0.25 x the plain sound's share / the species' make cost
(`inventory._pool_for`, `NONHUMAN_SHARE`). Thirty chances add up: with today's profiles 54% of avian proto-inventories, 78% of
reptilian and 82% of tortle ones contain a growled sound, although the profiles call growl "possible but not the norm"
(avian harsh x3, reptilian x2). For humans (harsh made finite on 2026-11-03, contrastive in !Xóõ and Bai) the same mechanism
gave 14% at x8, so the human number was set to x30 (~2%) to compensate. If this is never fixed, fantasy languages will be full
of growls the profiles say are rare, and every make_cost on a non-human key will need a compensating fudge like the human x30.

Measured: 200 draws per profile, `np.random.default_rng(1)`, script in the lang-design report.

Fix to try: give the variants one share per species and key (e.g. a target share of inventories with any such sound,
falling with the make cost, spread over the 30 candidates) instead of a per-candidate share; then set human harsh back to the
reviewer's x8 and check the shares (birds and reptiles should be a minority, cats and dragons commoner).
- [ ] share of proto-inventories with a growled sound under ~40% for avian/reptilian profiles, ~1-3% for humans at harsh x8

## Updates
- 2026-11-03: Created.
