---
title: "Frozen-over spells start with CO2 falling about 8-fold in ~12 Myr, deep enough to reach LGM cold or colder"
type: task
status: todo
parent: null
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: lane71
blocked_by: []
relates: [PW-1142, PW-865]
refs: [planet/tectonics/earth.py, tools/ice_diag.py]
---

## Description
In plain words. Lane 71 followed each of main's four frozen-over worlds (lane 67's re-judge, L6, roll 0.0005) back
to what started its freeze. In three of the four, the ice is not outlasting a warm climate. The world gets
genuinely very cold, as cold as the Last Glacial Maximum or colder, after its CO2 falls fast. At that cold the
ice's own extent is 40%+ of the land even when grown from bare ground.

- 957317 l6c_p: from 756 to 768 Myr the CO2 index falls 1.73 -> -0.37 e-folds (about 8x). The volcanic source
  drops by a third (1.26 -> 0.86 of its baseline) while the land rises (30 -> 35%). The CO2 term goes from ~9 C to
  ~0 in 12 Myr. dT reaches -3.8 (true mean -6.2 C) and the land ice 41% at 776-792. From a pickled moment at 776,
  the ice rule grown from no ice at the same dT gives 41% (main) and 40% (lane 71's kitchen sink). So this freeze
  is the cold climate's own extent, not persistence. Its geography isn't unusually polar: land poleward of 60 deg
  is 19% (Earth 20%). But 45-60 deg holds 20% of its land (Earth 16%), wet (median 700 mm) and high (15% of land
  above 1500 m, Earth 8%).
- 583167 l6c_p: frozen 632-664 at dT -4.6..-6.3 (true -8 C). The CO2 index falls 1.3 -> -0.45 from 602 to 632.
- 819014 l6c_p: a long cold era from ~760 to the end at dT -5..-8.5 (true -8..-10 C), CO2 index -1 to -1.8.
- 619496 l6fix is the exception, a persistence/feedback case: the land ice goes 24% -> 45% at 402-426 with dT only
  -0.1..-1.8 (the albedo term reaches -1.7). That one is PW-1142's.

Question: are swings of 2 e-folds of CO2 in 12 Myr from a source dip plausible (the Cenozoic fell ~4-5x over
~50 Myr)? If not, the carbon cycle's response time or the source's volatility is the lever, not the ice.
- [ ] A written read of the source's variance per 10 Myr against Earth's record, sent to the coordinator
