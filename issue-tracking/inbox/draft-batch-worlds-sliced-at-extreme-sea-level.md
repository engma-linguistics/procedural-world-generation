---
title: "`--at auto` slices worlds at extreme sea level: 4 of 8 v1 batch worlds sit at -269..-369 m"
type: task
status: todo
parent: null
milestone: v1
subsystem: highlights
effort: s
impact: med
found_by: pw548
blocked_by: []
relates: [PW-434, PW-202]
refs: [planet/highlights.py, docs/review/health/2026-10-21-batch/report.md, "worlds dad91b c00ebf 91448a 3e0b0a"]
---

## Description
`highlights.representative_time` (`--at auto`) picks the keyframe whose land %, largest landmass and landmass count are nearest the run's medians. It doesn't look at sea level. In the v1 8-planet batch four of the eight worlds were sliced while total sea level was below the -250 m band: dad91b -361.5 m, c00ebf -369.0 m, 91448a -287.1 m, 3e0b0a -268.9 m (run keyframes at the slice times; docs/review/health/2026-10-21-batch/report.md). Their coasts and zooms sit on exposed shelf, which is not the representative moment the recipe intends, and PW-202's showcase remake would repeat it.
Try: add sea level (and ice % / largest lake) to the distance that picks the time, or skip keyframes outside the health envelopes (-250..300 m, ice <= 10%, largest lake <= 1 Mkm2) when a keyframe inside them exists.
- [ ] `--at auto` avoids keyframes outside the sea-level envelope when any other keyframe qualifies
- [ ] re-measure the batch worlds' slice moments
