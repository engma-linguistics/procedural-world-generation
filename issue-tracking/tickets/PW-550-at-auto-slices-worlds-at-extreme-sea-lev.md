---
id: PW-550
title: "`--at auto` slices worlds at extreme sea level: 4 of 8 v1 batch worlds sit at -269..-369 m"
type: task
status: done
parent: null
milestone: v1
subsystem: highlights
effort: s
impact: med
found_by: pw548
blocked_by: []
relates: [PW-434, PW-202]
refs: [planet/highlights.py, docs/review/health/2026-10-21-batch/report.md, "worlds dad91b c00ebf 91448a 3e0b0a"]
created: 2026-10-21
updated: 2026-10-21
---

## Description
`highlights.representative_time` (`--at auto`) picks the keyframe whose land %, largest landmass and landmass count are nearest the run's medians. It doesn't look at sea level. In the v1 8-planet batch four of the eight worlds were sliced while total sea level was below the -250 m band: dad91b -361.5 m, c00ebf -369.0 m, 91448a -287.1 m, 3e0b0a -268.9 m (run keyframes at the slice times; docs/review/health/2026-10-21-batch/report.md). Their coasts and zooms sit on exposed shelf, which is not the representative moment the recipe intends, and PW-202's showcase remake would repeat it.
Try: add sea level (and ice % / largest lake) to the distance that picks the time, or skip keyframes outside the health envelopes (-250..300 m, ice <= 10%, largest lake <= 1 Mkm2) when a keyframe inside them exists.
- [x] `--at auto` prefers (planet-relative; see update) -- was: avoids keyframes outside the sea-level envelope when any other keyframe qualifies
- [x] re-measure the batch worlds' slice moments

## Updates
- 2026-10-21: Created from inbox draft draft-batch-worlds-sliced-at-extreme-sea-level.md (found by pw548).
- 2026-10-21: Done. `highlights.representative_time` now adds the frame's total sea level (`sea_level_m`) as a fourth term of the distance to the run's post-300 Myr medians (scale = IQR, floored at 40 m), so it is planet-relative and a nudge: when no frame near the run's typical level fits the other criteria, the nearest overall is taken and `--at auto` prints a NOTE with the pick's sea level beside the run median. Runs without `sea_level_m` skip the term. Re-picked on the batch runs (old t / sea -> new t / sea; run median): 9b685e 860/-362 -> 880/-209 (-214); 0ecb0d 692/+29 -> 576/-228 (-246); 865ea0 892/-182 unchanged (-191); 3ff3f3 552/-369 -> 884/-227 (-224); 1112ef 712/+154 -> 796/-160 (-214); 6a0029 788/-287 unchanged (-248); 396621 672/-269 unchanged (-217); f9e085 748/-45 -> 772/-111 (-130). Two of the four worst (dad91b, c00ebf) now sit at the run median; 91448a and 3e0b0a stay at -287/-269 because their medians are -248/-217: the whole run is low, which is PW-434 (cold-era sea level), not a picker problem. Worlds were not re-sliced.
