---
title: "Demes: most gap splits and fusions are a range's narrow neck flickering between frames, not a real barrier"
type: task
status: todo
parent: PW-981
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: fun46-demes
blocked_by: []
relates: [PW-981, PW-902]
refs: [planet/lineages/demes.py, "run b69f51"]
---

## Description
In plain words: when a people's land is joined to a pocket by a strip one or two cells wide, and that strip changes hands
from frame to frame, the demes pass records the pocket splitting off, then fusing back, then splitting again. The tree
fills with short-lived branches that are bookkeeping noise, not populations that really parted.

On run b69f51 (300 kyr cut), 459 gap splits and 389 fusions for 809 demes. Of the 497 gap-split or fusion events of
60+ cells, only 49 had the sea moving within 3 cells of the demes involved (land bridges, rising sea); the rest are range
changes. Example: the humans at ~51°N 159°W on the large northern continent split off along a gap at 120 kyr, fused back at 68 kyr and
split again at 32 kyr; the ASCII maps show a 1-2 cell neck through another people's land, not a sea gap. Small peoples
churn most (leonin 62 demes, 28 died out; goliath 57; orcs 90).

What to try:
- hysteresis: count a gap split only after the pieces stay apart for 2 frames (or 2 kyr), and a fusion only after they
  stay joined as long;
- a neck tolerance: let a deme bridge up to 1-2 cells of another people's land (as it bridges SEA_KM of sea), so a
  minority strip does not cut it;
- then re-count events per deme and the share caused by the sea (the measure above).
- [ ] gap splits + fusions per deme on b69f51 at least halved, with the land-bridge cases kept
