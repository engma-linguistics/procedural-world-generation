---
id: PW-102
title: Ice sheets stay put after their mountains move away (world-frame ice with height feedback)
type: task
status: todo
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
- 2026-10-14: Created.
