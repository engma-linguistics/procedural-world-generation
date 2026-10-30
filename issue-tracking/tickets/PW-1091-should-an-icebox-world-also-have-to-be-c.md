---
id: PW-1091
title: Should an \"icebox\" world also have to be cold? The flag reads ice volume (sea level) only, and flags Earth-warm worlds
type: task
status: needs-decision
parent: null
milestone: v1
subsystem: climate
effort: s
impact: med
found_by: lane28
blocked_by: []
relates: [PW-998, PW-1050, PW-865]
refs: [docs/review/base-climate/v1-finish-12/passrate4.py, docs/review/base-climate/v1-finish-16/pjudge.py, tools/ice_criteria.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Every judge reports how many worlds are "iceboxes". At the moment that
label only looks at how much ice the land holds, measured as how far it lowers the sea.
A world counts as an icebox from 300 Myr on if either:
- the ice holds at least 20 m of sea level for 90% of the time; or
- the ice holds more than 150 m for 30% of the time.

It never asks whether the world is actually cold. A warm world with big ice sheets on
polar or high land gets the same label as a frozen one.

The icebox label doesn't fail a world: since the owner's ruling of 2026-10-27, only a
hellhouse does. But it feeds the set-level sanity check (80% iceboxes means the sim is
wrong), and it's what lanes and the coordinator read as "too icy". The coasts judge (10-30)
went from 5 to 8 iceboxes of 18, and that was nearly treated as a reason not to merge.

What the icebox worlds look like (L6, 18 draws per arm, roll 0.0005; the median over each
run's climate updates from 300 Myr):

| arm | iceboxes | their median global temperature (cell mean) | the other draws' | their median dT |
|---|---|---|---|---|
| main before PW-1050 (3a58e00d) | 3 | 12.7 C | 14.7 C | +0.23 C |
| main with PW-1050 (F) | 5 | 11.8 C | 15.8 C | -0.92 C |
| with the coasts package (now main) | 8 | 12.8 C | 15.2 C | +0.47 C |

For scale, the judges' finish check takes Earth's pre-industrial mean as 13.8 C and accepts
-6 to +3 C around it. Of the 8 coasts iceboxes, 6 have a dT median above zero; their median
global temperatures run from 10.7 to 14.1 C. In all three arms only main's 819014 (7.0 C,
dT -6.1) is clearly a cold world; F's two coldest (53669 and 619496, dT about -2 C) are
mildly cool. The rest are Earth-warm worlds with large sheets. That is a plausible outcome when there's high polar land and a lot of polar snow,
which the Earth check now says the coasts package gets about right (60-80 N land rain within
3% of GPCC).

The question for the owner: should "icebox" also need the world to be cold? For example,
the sea-level test AND a global mean below pre-industrial by some margin (say dT median
< -2 C, or a global mean T < ~11 C). Then the label would mean "a cold, frozen world" rather
than "a world with big ice sheets".
- **Yes:** the icebox count would track climate, and the 80% sanity check would catch a
  sim that runs cold, not one that grows realistic sheets. With one illustrative cut (dT
  median < -1.5 C, not tuned) the counts would be 1, 2 and 0 out of 18.
- **No (keep it as is):** "icebox" stays a pure ice-volume label. Then a separate cold-world
  count is worth reporting next to it, and the coordinator should read the icebox count as
  "lots of ice", not "too cold".
- **Either way:** it's a label and a sanity check, not a pass/fail, so no world's pass
  changes. It only changes what the judges tell us.

Judgement call, so asking rather than changing passrate4.judge. If a cold criterion is
wanted, pick the margin (dT or absolute T) and the window (300 Myr to end, as now).

- [ ] Owner: icebox = ice volume only (as now), or ice volume AND globally cold (which margin)?
- [ ] If changed: passrate4.judge and pjudge/fmtally updated together, with a cold-world count reported either way

## Updates
- 2026-10-30: Owner 10-30: 'frozen over' means roughly 40%+ of LAND under ice. Coordinator note: Earth's Last Glacial Maximum is commonly put at roughly a quarter of land under ice (to be verified from a source), so by that bar no Pleistocene ice age qualifies. Proposal for owner: three terms, icehouse (permanent polar sheets, Earth today), glacial maximum, frozen-over (>=40% land); then the judges report all three. Discussion with owner pending.
- 2026-10-30: Created from inbox draft draft-icebox-flag-needs-global-cold.md (found by lane28).
