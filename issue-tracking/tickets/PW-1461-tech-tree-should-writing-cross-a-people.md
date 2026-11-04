---
id: PW-1461
title: "Tech tree: should writing cross a people's towns instead of its whole country?"
type: task
status: needs-decision
parent: null
milestone: later
subsystem: culture
effort: s
impact: med
found_by: lane-184
blocked_by: []
relates: [PW-1448]
refs: ["planet/lineages/techtree.py::contact_rate", "planet/lineages/techtree.py::build", planet/lineages/samples/techtree.toml, "planet/lineages/techspread.py::derive", docs/review/culture/writing/round1.md, "run a2b637", "run 0141d1", "run 07c755"]
created: 2026-11-04
updated: 2026-11-04
---

## Description
**In plain words.** A people learns writing from a neighbour when a "front" of the know-how has crossed half its country at about
1 km a year (the speed farming spread across Europe). That suits farming, which moved with farmers. Writing moved with scribes and
merchants between towns, so it crossed a big people's towns rather than its whole land. Today a huge people waits a long time at the
border even with a dozen writing neighbours. On the Seven Meals run 07c755 the humans held 36% of the settled people and were ready
for writing from 7,900 years ago. They bordered writers from 6,400 years ago but took writing only 4,300 years ago, 2,100 years
later. On a2b637 the dwarves hold 24% of the settled people. They have bordered writers for 1,300 years and still do not write. Under
D49 their cities can never be states. If this is never decided, worlds keep big peoples with cities and no states for one to two
thousand years after their neighbours write. The lean below would also make writing reach most towns faster than it did on Earth's
Bronze-Age edge, so this is a real trade-off, not a fix.

The numbers (docs/review/culture/writing/round1.md): from the first writing to half the settled people took 800 to 1,300 years on the
three showcase runs. Earth: near neighbours took writing within about 100 to 900 years of Uruk (Susa, Ebla). The edge (Anatolia,
Crete, Mycenae) took 1,400 to 2,000 years. So the model's median is Earth-like, and the slow part is the tail of big, inward-looking
peoples.

Options:
- **A: keep it.** The spread matches Earth's median, and the tail is luck plus insularity. A2b637's statelessness until 1,100 years
  ago comes mostly from writing being invented late (4,500 years after the first people was ready; Earth took 3,300). That is chance,
  not the contact rule.
- **B: town network.** For a tech that needs towns (writing, and the alphabet after it), the front crosses the width of the taker's
  town cells, not its whole range (`contact_rate` given the town footprint's area; techtree needs the settlement footprint per people
  over time, which output.save has). Big peoples with a few dense urban cores then take writing in centuries. This is a mechanism, but
  it changes how fast the techs spread, so it needs your say. It needs new peoples runs.
- **C: trade contact.** Two peoples whose towns trade (both have towns, and they share a border) pass urban techs at a trade speed
  (Jordan et al. 2016's 1.2 to 3.3 km a year along favoured corridors) instead of 1 km a year. This is closer to a dial: it is the
  same front, made faster.

**Lean: A for now, B if you want big urban peoples to stop waiting.** B keeps the rule "know-how crosses where its carriers live" and
needs no new numbers. C is a dial turn.

## Updates
- 2026-11-04: Lane 186 merged (switch off, identical): arms B/C/E/K measured (docs/review/culture/writing/round2.md). Medians, years to half: off 865, B 425, C 560, E 273, K 850; all inside Earth's 100-900. Lean E; it needs PW-1464 for new runs. Desk D53.
- 2026-11-04: Daniel 11-04: B or C, wary of the halfway time; experiment lane 186 tries B, C, E (rulers take it up) and K (kin share faster).
- 2026-11-04: Coordinator: desk D52. Lean B (writing crosses a people's towns, not its whole land) on Daniel's suspicion of a slow tail; it needs new peoples runs.
- 2026-11-04: Created from inbox draft draft-writing-crosses-town-network.md (found by lane-184).
