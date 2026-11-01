---
id: PW-1240
title: "Owner call: the D25 brakes at x1 cut kobolds and goblins hard (mostly through in-fighting) and leave the humans untouched, so the commonest people grows"
type: task
status: needs-decision
parent: PW-917
milestone: v2
subsystem: timezoom
effort: s
impact: high
found_by: lane97
blocked_by: []
relates: [PW-1165, PW-1172, PW-1218]
refs: [planet/lineages/history/counter.py, planet/lineages/history/params.py, docs/review/peoples-brakes/report.md]
created: 2026-10-31
updated: 2026-10-31
---

## Description
**In plain words.** The brakes you asked for in D25 are built and on by default. At the default strength they do what they say: the
kobolds and goblins lose about a third of their land, the elves and other farmers a few percent to war, the humans almost nothing.
But the room the raiders lose goes mostly to the humans, so the commonest people gets bigger, not smaller. In the three-people tree
(humans, kobolds, goblins) the runs with more than 85% humans went back from 1 of 4 (after D27) to 4 of 4. The full numbers, charts
and maps are in docs/review/peoples-brakes/report.md.

What does the work: the in-fighting term. Kobold and goblin peoples almost never have free good country next door, so their
"hemmed-in" share sits near 1 and in-fighting takes about 35% of their land everywhere (raids on hostile borders take 1-4%, culls
about 2%, war 0-1%). That makes in-fighting close to a flat cut on the raiders, not one that rises with their crowding.

The dial sweep (report, "The dial sweep") adds two findings:
- Any raiders' setting above x0 puts the three-people tree back above 85% humans (x0.5 too).
- At x4 the kobolds and goblins die out (in every three-people try, and the goblins in 3 of 4 full-tree tries), although
  COUNTER_FLOOR (5% of habitat) was meant to stop any brake ending a people: a floor on K does not hold a people whose growth on that
  5% is below its losses. Either the floor should hold numbers (a minimum presence where the people lives) or x4 should leave the dial.

Judgement calls in it (all in params.py, explained in history.counter):
- FEUD_Q 0.5: in-fighting at full hemming raises the raiders' losses by half (R 1.5). Mechanism sourced (Chagnon on fission,
  Carneiro on circumscription), size not.
- RAID_Q 1.0: a full hostile border doubles them (lane 85's R_FRONT 2). Not sourced.
- The culls' numbers (lane 85's design: 80% full, 30% hostile frontier, chance 0.5 a step, cut to 40%). Not sourced.
- War-torn land: lane 82's LAND_Q 0.3, H_MAX 1%/yr, STATE_Q 3. The violent-death rates per way of life are sourced (lane 82's table).

Options:
- A. Keep x1 as the default and let the raiders' dial be the lever (the sweep in the report shows x0 to x4).
- B. Make in-fighting rise with the raiders' own crowding only (hemmed-in share above a threshold), so a lone people with room is
  braked less; keep the rest.
- C. Lower the default raiders' dial to x0.5.
- D. Add a brake on the leader too: crowding war for any dense people (PW-1172's war deaths through the life tables), so the people
  that holds the most land pays the most. This is the only option that lowers the commonest share directly.
Lean: B now, D with PW-1172. The question of what the commonest share should be is in the report's last section.

## Updates
- 2026-10-31: Lane 101: B done for every people, humans included (Daniel D31), sourced to Carneiro 2012, Chagnon 2014, Walker and Hill 2014; the floor holds numbers (BRAKE_HOLD 0.24 on held cells). D (war-deaths leader brake) built, measured at 0-0.2%, dropped on Daniel's ruling and parked with PW-1172. Suite: commonest dnd 64/37%, fails 7 of 82 (4 dnd3, 3 Seven Meals half-orcs never founded), no people lost to a brake. Sizes parked in draft-in-fighting-judgements-for-polities.md.
- 2026-10-31: Coordinator: B (in-fighting rises with the raiders' own crowding) plus D (a leader brake via PW-1172 war deaths) plus a floor that holds numbers go to lane 101. Daniel's target for the commonest share (PW-1241) sets the judge.
- 2026-10-31: Created from inbox draft draft-peoples-brakes-sizes-and-the-leader.md (found by lane97).
