---
title: Fold the farmers' push into spec.WAY_PRESS and tune the herders' press on more worlds
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: low
found_by: fun14
blocked_by: []
relates: [PW-756, PW-723, PW-748]
refs: [planet/lineages/spec.py, planet/lineages/history.py, planet/lineages/animals.py]
---

## Description
PW-756 added `spec.WAY_PRESS` (way -> (good, share of the rivals' load felt there)), used in `History.run` for the `pastoral_nomad` way: the rivals' load on good
grazing land is felt at 0.6 in proportion to `Animals.herding(k)` (best adoption among animals that carry a herd, over `spec.HERD_FULL` = 0.5). The farmers' analogue
is still the hard-coded `"agricultural" in l.traits and step.ago <= FARM_KYR` x 0.5 on `tags["farmland"]`. Follow-ups:
- Refactor decision (flag for a yes): express the farmers' push as a `WAY_PRESS` row too (farmer / horticulturalist on `fertile`), one rule keyed on the way, not on a trait. It changes dnd and
  seven_meals outputs (the trait is also given to peoples with no `way`), so it needs a pass-rate comparison, not a drive-by.
- 0.6 and HERD_FULL 0.5 are first guesses measured on one world (1df1c3, tries 1): they triple the seven_meals antelope-kin (3.85 -> 11.7 Mkm2). Check other worlds and a few re-rolled draws before treating
  that as the effect (see the seed pass-rate note); steppe orcs and hill giants (dnd) are pastoral nomads too, numbers in the lane report.
- The owner welcomes baked-in aggressive tendencies as a data-driven trait: built as the `aggressive` trait (TRAITS push 0.7: rivals' load felt at 0.7 everywhere), given to the antelope- and cervid-kin in seven_meals. Value and which peoples carry it are first guesses; unify with WAY_PRESS if a refactor happens.
- `transhumant` and `agro_pastoral` get no press (they are tied to a home base and fields); decide if a smaller share belongs to them.
- Herding only reaches the antelope-kin in the last ~10 kyr on 1df1c3 (adoption 0.13 at 10 kyr ago, 0.43 at 2 kyr): the horse-taming people is on another continent. Whether
  the press should also come from the people's own tamed herd stock (caprine/cattle) earlier is a taming question (PW-718), not this rule's.
