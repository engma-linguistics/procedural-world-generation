---
id: PW-1310
title: "Gods readout starts at the 300 kyr window: seed the oldest gods (dragons) from when each people learned ritual, and step finer than the frames"
type: task
status: todo
parent: PW-1308
milestone: later
subsystem: peoples
effort: m
impact: low
found_by: lane117
blocked_by: []
relates: [PW-1306, PW-986, PW-981]
refs: ["planet/lineages/gods.py::derive", "planet/lineages/gods.py::Pantheons.frame", "planet/lineages/cultures.py::derive", planet/lineages/demes.py, "run b4d502: gods.json cultures[].ritual_since_kyr", docs/review/religion/slice1.md]
created: 2026-11-02
updated: 2026-11-03
---

## Description
In plain words: Daniel's ruling is that dragons' gods are emergent and likely the oldest. In the first slice every culture's gods start at the first frame of the
demes window (300 kyr ago), so all founding gods are the same age. The peoples learned spirit ritual much earlier (b4d502: tortles, lizardfolk and giantkin ~910
kyr, hill giants and aarakocra 900, leonin 878, dragons 750), and `gods.json` records that per culture as `ritual_since_kyr`.

Options: (A) show `ritual_since_kyr` as the age of a founding culture's first gods (cheap, a label); (B) run the god pass over the deep keyframes too (the demes only
cover 300 kyr, so this needs deme-less peoples-level pantheons before the window); (C) leave it. Also: the stored frames are 0.5-4 kyr apart, while the doc's step is 25
yr; drift is scaled by the frame gap, which is fine for slow ritual change, but births and fusions inside a frame are not seen.
- [ ] choose A, B or C; if A, show the age in the viewer's gods column and the brief

## Updates
- 2026-11-03: Triage 11-03: v2 -> later: peoples refinement or later mechanism (tuning, follow-ups), not needed for a first culinary brief
- 2026-11-02: Created from inbox draft draft-gods-pre-window-seed.md (found by lane117).
