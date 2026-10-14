---
id: PW-102
title: Ice sheets stay put after their mountains move away (world-frame ice with height feedback)
type: task
status: done
parent: null
subsystem: climate
effort: m
impact: med
found_by: daniel
blocked_by: []
relates: []
refs: ["run:428083@596Myr(8.8,155.2)", "run:428083@624Myr(7.8,156.6)", planet/tectonics/earth.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner noticed (Current code L7 Earth-like seed 21, run 428083): at t=596 a ~800 m ice cap sits on a 4641 m mountain near (8.8, 155.2); by t=624 the mountain has moved east but the ice is still in roughly the same place, ~1000 m thick over ground at 3743 m (7.8, 156.6).

Likely mechanism (earth.py ~L104-116): ice is a world-frame per-cell field recomputed every climate step from t_warm < ice_summer_temp, but the climate sees elevation + ice (surface), so an existing sheet keeps its own surface cold (height/mass-balance feedback) and re-qualifies itself; the thickness rule (300 + 2700*(1-exp(-d/600 km)) from the sheet edge) ignores snowfall, so even a tropical cap gets ~1 km.

Partly physical: real ice sheets do have height-feedback hysteresis (Greenland might not regrow if melted). But real tropical ice caps are thin (Quelccaya ~200 m) and ice responds in ~10 kyr, far below the 4 Myr step, so a cap should follow its mountain. Fix ideas: inception judged on bedrock elevation and survival on ice surface with only a partial feedback; thickness limited by accumulation (precip) and size; or move ice with the plate between climate steps and let mass balance decide. Related: main-run ice rule leaves polar deserts bare (search 'ice rule').

## Updates
- 2026-10-14: Status todo -> done. Fixed in d38bc09 (climfix). Ice is judged on the bare ground minus its own cooling (none in the tropics, scaled by how much nearby land is iced) and 3/4 of its height, needs snow beyond its degree-day melt, and is a Nye profile thick. L7 seed 21 run 5ec775 (vs 428083, 100-1000 Myr): tropical ice cells on bedrock <2500 m 44.9 -> 3.8 per frame. Caps track their highs: run:5ec775@420-512Myr the ice centroid moves (4.2,31.0) -> (-1.0,34.4) within 0.1-0.3 deg of the >3.5 km ground's and goes at 516 Myr once the bedrock under it falls to ~4.2 km; run:5ec775@200-280Myr likewise around (2.5,-131). The new rule on 428083's own terrain: at 624 Myr the stranded cap near (8.1,156.6) (98 cells, bedrock median 3156 m) goes; at 1000 Myr near (2,-38.5) cells on bedrock <2500 m 14 -> 0, cell 140015 (3.59,-39.94) bare. Follow-ups in inbox (amount of ice: needs-decision; bare polar ground too warm).
- 2026-10-14: Created.
