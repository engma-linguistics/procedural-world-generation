---
id: PW-1125
title: "Tech tree: open the farming gate on the planet's own climate, not on Earth's 11.6 kyr"
type: task
status: todo
parent: PW-675
milestone: null
subsystem: culture
effort: m
impact: med
found_by: fun-lane-64
blocked_by: []
relates: [PW-946, PW-470]
refs: [planet/lineages/techtree.py, planet/lineages/samples/techtree.toml, docs/references/techtree/README.md]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words: farming and the techs that grow out of it cannot start before 11.6 kyr ago on any planet. That is the end of Earth's
last ice age, not this planet's.

Lane 64 (invention model v1) keeps every tech dated 11.6 kyr or older as a hard floor (`gate_kyr`). It also measures the anchor lag
of the Holocene techs from that date. Richerson, Boyd & Bettinger 2001 (American Antiquity 66:387) argue farming was impossible under
glacial climates (dry, low CO2, very variable) and compulsory once the Holocene began. So the gate is a climate gate. On a planet with
other glacial timing, it should open when that planet's climate becomes stable and warm enough. Today the history saves no per-step
climate-stability signal that the tree could read.

What to try:
- Have the history save, per step, a stability measure of the climate (for example the variability of temperature or rain over the
  last few kyr, and the glacial state from the ice-age model).
- Make gate_kyr per run: the time that measure last crossed a threshold, else 11.6.
- Then the farming techs (cultivation, herding, storage) and everything after them follow this planet's Holocene.

- [ ] a saved climate-stability signal
- [ ] gate_kyr read from it per run, with 11.6 as the fallback

## Updates
- 2026-10-30: Created from inbox draft draft-techtree-planet-glacial-gate.md (found by fun-lane-64).
