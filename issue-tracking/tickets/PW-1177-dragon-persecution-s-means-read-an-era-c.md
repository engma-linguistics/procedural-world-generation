---
id: PW-1177
title: "Dragon persecution's 'means' read an era calendar, not the peoples' own techs: feed megafauna.means from known weapons, metal and horses"
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-63
blocked_by: []
relates: [PW-1068, PW-946, PW-961, PW-977]
refs: [planet/lineages/history/megafauna.py, planet/lineages/techtree.py]
created: 2026-10-30
updated: 2026-10-31
---

## Description
**In plain words.** How hard a people hunts dragons now rises with "the era" in a fixed calendar. The present is the tree's `meta.era`
(renaissance by default). Earlier eras are counted back on Earth-like spans: renaissance 0.35 kyr, medieval 1.0, classical 1.3,
bronze 2.0, and stone age before that (`megafauna.tech_level`, `ERA_KYR`). This is a proxy, the same weakness as the tech tree's
bands. Every people gets the same tech level at the same moment, whatever it actually knows. A stone-age people beside a bronze-age
one presses dragons just as hard as its neighbour.

The fix is to feed the tech level per line from each people's real known techs, once techs can feed back into the history. The
level sets which age classes of dragons a people can reach (`megafauna.vulnerability`: wyrmlings always, the young a little more
with tech, adults and ancients only at high tech; bronze age 0.15, owner 10-30):
- weapons and metal (bronze, iron: reach);
- horses and mounted hunting (reach over open country);
- organised states and bounties (the motive and organisation part).
Today the tech tree (`techtree.py`) is computed after the history, so this waits on lane 64's rework, or a pass that runs techs
alongside the history (PW-946).

`means()` (motive: herds to defend; organisation: bands against settled folk) and `vulnerability(level)` are the two places to
change, per line, at a time. Keep KILL_Q's
calibration (dense renaissance farmers keep ~10% of their dragons) or re-calibrate it on the tech-fed means.
- [ ] the tech level (`vulnerability`) and `means()` read each line's known techs at the step, not the era calendar
- [ ] the calendar proxy (`tech_level`, `ERA_LEVEL`, `ERA_KYR`) retires

## Updates
- 2026-10-31: Lane 90 (partial): means read the history's herds (animals.herding) and riding (stocks with speed > 1, MOUNTED_X 0.5); KILL_Q re-calibrated 0.0028 -> 0.00187 to keep the dense-farmer anchor. Weapons and metal still from the era calendar until PW-946. docs/review/dragon-food-chain/report.md
- 2026-10-30: Created from inbox draft draft-dragon-persecution-means-from-real-techs.md (found by fun-lane-63).
