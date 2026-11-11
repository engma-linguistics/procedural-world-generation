---
id: PW-1740
title: "Languages: living sound systems drift unnatural (15% lack /m/, aspirates 3% vs 19%, prenasals 46% vs 13%, /i/ the commonest vowel in half)"
type: story
status: todo
parent: PW-1736
milestone: v4
subsystem: culture
effort: l
impact: high
found_by: lang-assessment
blocked_by: []
relates: []
refs: [docs/review/language/assessment-2026-11-11.html, planet/language/data/sound_changes.tsv, "planet/language/inventory.py::draw_inventory", planet/language/lect.py, "planet/language/checks.py::living_segments", "run a24559", "run de1cc6"]
created: 2026-11-11
updated: 2026-11-11
---

## Description
In plain words: proto inventories match PHOIBLE, but after 20 kyr of sound change the living systems do not: aspirated series 3.2% of living human-voiced lects (protos 16%, PHOIBLE 19%), prenasals 46% (13%), trill 93% (47%), retroflex 45% (28%), ŋ 35% (64%), ɾ 7% (25%), ts 6% (22%); no /m/ in 15% (PHOIBLE 3.4%), no plain coronal stop 13%; one vowel carries > 40% of vowel tokens in half the lects and /i/ is the modal vowel in 314 of 621. Same on de1cc6 (prenasals 61%), so structural: the catalogue has sinks with no sources (nothing creates aspiration; m > n 447 firings; obstruent > sonorant folds). Do after lane 17 (PW-1692 weighted re-fire) is in.
- [ ] source rows for aspiration (e.g. from clusters, tonogenesis-side), ts (t > ts before high vowels), ɾ (intervocalic flapping), ŋ (nasal assimilation, final n > ŋ)
- [ ] fold guards: no obstruent > sonorant folds that empty a series; never lose the last labial nasal
- [ ] a core guarantee in the proto draw (inventory.py ~545-589)
- [ ] checks: series shares within ±2x of PHOIBLE in both directions; a vowel-token concentration check; BURST_X (lect.py ~32) founding bursts of 12-72 changes looked at
- [ ] pass on the multi-world matrix

## Updates
- 2026-11-11: Created.
