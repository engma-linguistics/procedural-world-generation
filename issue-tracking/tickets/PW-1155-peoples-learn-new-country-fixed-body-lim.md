---
id: PW-1155
title: "Peoples learn new country: fixed body limits, widening cultural preference (niche learning)"
type: task
status: in-progress
parent: PW-917
milestone: v1
subsystem: timezoom
effort: m
impact: high
found_by: coordinator
blocked_by: []
relates: [PW-1149, PW-1152, PW-1151, PW-981]
refs: [planet/lineages/history/habitat.py, planet/lineages/spread.py, planet/lineages/history/model.py, planet/lineages/samples/dnd.toml]
created: 2026-10-30
updated: 2026-10-30
---

## Description
In plain words. Today each kind of people has one fixed habitat for the whole history, so the kind with the broadest habitat (humans) wins nearly everywhere. Real peoples learn new country: humans reached the Arctic and the high plateaus by learning, over thousands of years. The owner wants every people able to do the same, slowly and at its frontier. That gives regional subgroups (desert aarakocra, plains gnomes, tundra elves) for the demes and the culinary work.

Design intent (owner 2026-10-30):
- **Body limits (tolerance)** are fixed per kind: tortles dislike the frozen north, merfolk need water, giants and dragons mostly keep to their lane.
- **Cultural preference** widens with time held at a range edge: first accept, then prefer. It is slow, and driven by pressure at the frontier, so a forest people stays mostly in forest for a long time.
- It must not homogenise the world. Judge it on the lane 77 peoples stress suite: shares, even_six, menagerie, no collapse.

Supersedes the density rethink (PW-1149) and the mainline flag as the main lever for "mainline peoples are common".

- [x] tolerance vs preference split in the spec and habitat
- [x] frontier learning over time; learned preference recorded per cell or deme for the demes pass
- [x] judged on the stress suite; even_six and human share reported

## Updates
- 2026-10-30: Lane 79 built it (params.LEARN on). Spec has `limits` (the soft body envelope) and `never` (hard limits). Each people
  and cell keeps a learned acceptance L, with K = K0 + 0.6 L (T - K0). T_LEARN_KYR is 5, sourced from the Andes, Tibet and Arctic
  peopling. Learning is gated by pressure and by the cell being empty, and carries within a biome class. On learned country the
  way-of-life competition discount fades (competition hook). Output: the peoples_learned layer, stats.learned, deme labels
  "adapted" and split_adapted demes. MAINLINE_Q and `mainline` were removed. Results on 4360a3, off -> on: dnd humans
  73/69/73% -> 66/60/70% (seeds 7/10/13); homogenisation 0.63-0.67 -> 0.63-0.70; menagerie 51/52 alive both ways; even_six
  humans 72 -> 68%, elves 0.2 -> 0.9-1.1%. Follow-ups are in inbox drafts.
- 2026-10-30: Created from inbox draft draft-niche-learning.md (found by coordinator).
