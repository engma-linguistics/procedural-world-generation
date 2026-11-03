---
id: PW-1194
title: "Owner call: events from physics-placed chance; fast-breeder brake = raid losses + culling wars on top of land; dwarves' disease resistance"
type: task
status: done
parent: PW-917
milestone: v2
subsystem: timezoom
effort: xs
impact: high
found_by: lane-85
blocked_by: []
relates: [PW-1169, PW-1167, PW-1185]
refs: [docs/review/peoples-events/design.md]
created: 2026-10-31
updated: 2026-11-03
---

## Description
**In plain words.** Your 10-31 asks, designed in docs/review/peoples-events/design.md (no model change yet). Leans in brackets.

1. **Where do events come from?**
   - A. Pure dice.
   - B. Dice for when and how big, the planet for where: droughts where the climate is touchy, quakes on plate edges, eruptions at live
     volcanoes, plague in crowded towns.
   - C. Fully simulated.

   [B. Real megadroughts are mostly the climate's own noise.] A drought is a patch of the recent climate itself, so the rain you see
   and the peoples' hardship agree. You can also place one yourself in the viewer ("rough half-millennium for them, shame").
2. **Brake on fast breeders.**
   - A. Land only (the old lean).
   - B. Raid losses: kobolds' and goblins' heavy losses, the reason they breed fast, rise on hostile borders. Half again cuts a border
     to 65%, double to 31%. Elves and dwarves are untouched.
   - C. Culling wars: crowded raider borders get hunted down to 40% and bounce back. That's the same average dent for any people, so
     no slow people is wiped out.

   [A + B + C.] Pushback: kobolds alone in their own mountains have nobody to raid them; there only their density (D20) shrinks
   them.
3. **Dwarves resist disease:** `disease_resist` 0.5 halves their plague losses. They still carry plague to their neighbours.
   [Yes, at 0.5.]
4. **Portals later:** a random yearly trickle that averages to the set number over a few thousand years. [After D21 settles.]
5. **Still open from D22:** how far should the commonest people's share fall at the default dials? Your number.

Recorded: virgin-soil epidemics stay off (your 10-31 ruling). That belongs in PW-1167's Updates.

## Updates
- 2026-11-03: Status needs-decision -> done. Closed 11-03: answered by owner D25 (10-31, in its Updates) and built: dwarves disease_resist 0.75 (spec.py, dnd.toml), raid losses + culls + in-fighting (lane 97 and 101, overview 2.26). Events (PW-1193, PW-1167, PW-1169) and the portal trickle (PW-1195) stay as their own tickets.
- 2026-10-31: Daniel 10-31 (D25): 1=B; 2=A+B+C plus in-fighting within raider peoples; 3=dwarves disease resistance 0.75; 4=portal trickle later; 5=open, wants a breakdown with a graph of the commonest people's share under the dials.
- 2026-10-31: Created from inbox draft draft-owner-call-events-brakes-resistance.md (found by lane-85).
