---
title: Squeezed peoples sit at the refuge floor (160 cells at L7) because their free habitat is in other patches they cannot reach overland; pick a mechanism (or accept)
type: task
status: needs-decision
parent: PW-692
subsystem: timezoom
effort: m
impact: med
found_by: fun-lane-30
blocked_by: []
relates: [PW-888, PW-887, PW-885]
refs: [planet/lineages/history.py, planet/lineages/spread.py, "worlds 2a7385 1df1c3 e71172 6909cb a12762 067778", "dnd 7000-7003"]
---

## Description
Found in PW-888's fifth pass (draft-small-landmass-founders-start-thin.md). Giants, drow, firbolgs, bugbears, sea elves, tritons, and on some rolls gnomes, dwarves and halflings, end at 150-165 cells: REFUGE_MKM2 (0.5 Mkm2) at L7, where displacement stops. Per-people pass rate at 300 cells: gnome 11/24, drow 1/24, fire giant 1/24, cloud/hill giant 6/24, sea elf 8/24, goliath 9/24, firbolg 11/24, triton 12/24. They have thousands of good cells and room >= EST on 20-80% of them, but more than 10 rings from their range (mostly more than 60): other ranges or forests across land they cannot hold. Near their range the room is ~0. The overland spread is a widest-path pressure that dies in K < 0.3 country, and there is no long-distance overland jump (only sea hops). Three local-contest mechanisms (habitat-pressure settling, time-integrated founder reach, home-ground territorial weighting) were measured over 24 rolls with no net change.
Options:
- A. Accept: small niche peoples hold one refuge each; the 300-cell bar is not for them (owner ruling on which peoples it covers).
- B. Overland jump dispersal: a people's frontier reaches a habitat patch it cannot walk to at rate x exp(-distance / L), as crossing.hop does over the sea (needs a rate and an L: new constants, owner's call). Hill peoples would then hold several ranges, not one.
- C. Scale the refuge floor with the people's own habitat (e.g. a share of its K >= 0.5 country) instead of a fixed 0.5 Mkm2.
Lean: B (it is the missing process), behind the 6 x 4 sweep.
- [ ] each people >= 300 cells on ~70% of rolls, or the exceptions ruled niche
