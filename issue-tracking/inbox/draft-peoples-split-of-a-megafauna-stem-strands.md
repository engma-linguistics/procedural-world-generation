---
title: "Kobolds after one-spot founding: fixed in most draws, but a narrow non-seafaring people still strands on a crowded landmass in some (dnd3 seed 7: 0.4%)"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: highlights
effort: s
impact: med
found_by: lane83b
blocked_by: []
relates: [PW-1152, PW-1181, PW-1174, PW-1202, PW-920]
refs: [planet/lineages/history/origins.py, planet/lineages/history/dispersal.py, docs/review/peoples-d20/report.md, "world 4360a3"]
---

## Description
**In plain words:** since a new people starts at one spot (your ruling D20 (2)), the kobolds had nearly vanished: 0.05–5% of all
people in the full dnd tree, 0.3% in the three-people tree. Lane 83b fixed most of it (below). Over the suite's 14 full-tree runs they now hold 0.45–11% (median 2.8%).
But in some draws they still start on a landmass where others already hold most of their country, and since they can't sail they
stay there at 0.4%. That is the one call left: accept it, or give a narrow people some other way off its landmass.

What lane 83b changed (general rules, not kobold settings):
- A people split from a megafauna stem (kobolds and dragonborn, from the dragons) founds where its own country lies, on a landmass the
  dragons' range reaches, drawn by the founders its free room would carry. Before, the landmass was drawn by the dragons' worldwide range.
- Such a people takes no demography from the stem: the dragons' explore 0.3 and insularity 0.85 are numbers for solitary fliers.
- Land that only dragons or giants hold is free country to a people's pioneers and jumps. Before, a dragon's range barred them.
- A people that has filled the land it holds sends founders out, as a crowded one does. Before, only crowding by rivals did, so the
  kobolds, alone on their patch of broken country, never left it.

What is left (one try each):
- dnd3 (humans, goblins, kobolds), seed 7: kobolds 0.42%. They start on a landmass with about a fifth of their country, much of it
  already held by archaic humans. There is no free country of theirs left on that landmass to jump to, and they can't cross the sea
  (sea share 0.02, no boats).
- dnd3, seed 10: 1.4%. On world af2677: 1.8% and 21%.
- The three-people tree can't get back to its base of 79–82% humans. In the base the kobolds held 77 Mkm², the dragons' whole
  range, inherited. Their denning country (D20 (4): dense but narrow) is about 17–24 Mkm² of good land worldwide. At 4 /km²
  against humans at 10 over ~100 Mkm², even all of it would leave humans near 90%.

Options:
- A. Accept it: a narrow, non-seafaring people born on a crowded landmass stays small there. It is alive and holds its own mountains.
- B. Give the kobolds a little sea craft (sea_share 0.1, as gnomes and halflings have), so canoes from 60 kyr can take them to the
  next landmass.
- C. Read "dense but narrow" as density, not habitat: off broken country they would live thinly instead of hardly at all. They would
  hold more land and cross plains, but they would also contest the open country with everyone.

Lean: A. The suite's per-world swings are in docs/review/peoples-d20/report.md.
