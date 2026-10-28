---
title: Megafauna body size and food as data (giants' recommended masses and food; dragons' length, mass, wingspan and food by age)
type: task
status: todo
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-724, PW-692]
refs: [docs/proposals/megafauna-scaling.md, planet/lineages/samples/dnd.toml, planet/lineages/spec.py]
---

## Description
Owner 2026-10-28 approved the giants' table and the interpolated dragon sizes in docs/proposals/megafauna-scaling.md. Put them on the lines as data that output and culinary code can read.

Giants (recommended masses):

| kind | height | mass | kcal/day | × human food |
|---|---|---|---|---|
| hill | 4.9 m | 2.2 t | 38k | 12 |
| stone | 5.5 m | 2.0 t | 35k | 12 |
| fire | 5.5 m | 3.3 t | 52k | 17 |
| frost | 6.4 m | 4.0 t | 60k | 20 |
| cloud | 7.3 m | 5.2 t | 73k | 24 |
| storm | 7.9 m | 7.3 t | 94k | 31 |

Food is Kleiber BMR × 1.7.

Dragons, by age:

| age | length | mass | wingspan | cattle/yr |
|---|---|---|---|---|
| 5 yr | 3 m | 60 kg | 6 m | 0.5 |
| 100 yr | 8 m | 1.2 t | ~19 m | 6 |
| 800 yr | 16 m | 9.8 t | 36-44 m | 40 |
| 1,500 yr | 22 m | 25 t | 49-64 m | 92 |
| 3,000 yr | 28 m | 52 t | 62-85 m | 176 |

How the dragon figures are built: reptile field metabolic rate (Nagy et al. 1999); a Komodo build lightened ×0.6; wingspan at *Quetzalcoatlus* wing loading.

- A `mass_kg` (or a size block) on the spec, with dragons reading the stage curve.
- Food per day derived from mass and `thermo` (mammal: Kleiber × 1.7; ecto: reptile field metabolic rate), not stored by hand.
- The brief can then say "a hill giant eats like twelve peasants" and "an adult red dragon takes about forty cattle a year".
