# Polities v0, round 1 (PW-1431, lane 169)

## In plain words

Peoples runs now have a **Polities** layer on the globe (Peoples section, beside "demes"). It shows who rules where at the
century nearest the time slider: chiefdoms (one town and its cell, drawn pale), states, empires (states where another culture
holds a fifth or more of the people) and dragon realms (ruled by a dragon culture; dragons are sapient). Borders are drawn darker;
land no one rules is grey. The legend lists that century's counts and its ten biggest polities. Click (or hover) a cell and the
info box shows the polity's card: its name, tier, size and people, the culture that rules it, its subject cultures, when it was
founded, when it fell (and why) or "still stands", and its capital.

It is a **read-out**: it is worked out after the run from what the run stored (the towns of the settlement ledger, the tech tree,
the cultures and where each lives). It takes about 30 seconds the first time a run is opened in the layer, is kept under
`<data root>/.godscache` like the gods and taboos, and never writes into the run. Nothing re-runs the history. War (PW-1432) has a
marked place to plug in and move land between neighbouring polities.

**Is it plausible?** Mostly, with two clear gaps:
- Sizes and populations are in the right ranges. Chiefdoms hold a few thousand people in their towns and villages, and the
  biggest hold tens of thousands. States and empires hold tens of thousands to about 1.5 million. That matches the ladder in
  Johnson & Earle 2000 (via Grinin 2003, quoted in round 1 of the cultures proposal): simple chiefdoms in the thousands, complex
  chiefdoms in the tens of thousands, states in the hundreds of thousands or more. The largest polity at the present is 1.2-1.9
  million km². Taagepera 1997 (same source) says no polity was over 1.1 million km² before about 650 BC, and the largest was never
  under 2.3 million km² after it. So our biggest are a little small for a late-medieval world. That is expected before war, because
  no state conquers another yet.
- **Polities last too long.** Half our states last 600 years (D&D run) or 1,400 years (Seven Meals). Taagepera's median is 130
  years at half or more of peak size. v0 has no collapse: a polity falls only when its capital shrinks, empties or comes under a
  stronger neighbour. War v0 and a base fall hazard (Arbesman 2011, mean ~220 years, round 1 2.1.2) are the fix. Draft filed.
- **On the D&D run, rulers come late.** Your rule "a chiefdom needs writing" (P2, "nearly B") is kept. On a2b637 the humans have
  cities from 5,000 years ago but writing only from 1,100 years ago. So there are no chiefdoms or states until then, only dragon
  realms. On the Seven Meals showcase, writing comes earlier and states appear from 7,000 years ago. A decision draft gives the
  options and the numbers for each.

## The rule, step by step

One rule per century step (`planet/lineages/polities.py`, the module docstring has the full text):
1. **Seats.** A living town of the ledger becomes a chiefdom seat if its people know `chiefdoms` and writing, or live beside a
   people who know writing (round 2's lenience). It becomes a state seat if its people also know `kingship` or `law` and it is a
   city. A hemmed-in town needs to be less big (Carneiro 2012). There is one seat per cell, the biggest town.
2. **Dragon seats.** Each living dragon culture whose kind knows `hoards` (hoards and tribute) has a seat at its densest cell.
3. **Claims.** Seats claim the peopled land within their reach, strongest first. The order is: states with standing armies (your
   O4, "until technology outstrips it"), then dragon realms, then other states, then chiefdoms. Within each class the biggest go
   first, and last century's capital counts 1.5 times its size. Claimed land is a border to everyone else. A seat inside someone
   else's claim is just one of that polity's towns.
4. **War** would go here (`polities.WAR`, default: no change). A polity whose capital is taken falls.

Reach is a travel budget measured in km walked on flat ground:
- **Chiefdom:** 27.5 km (Spencer 2010, sourced). That is less than a cell at L7.
- **State:** 150 km, the middle of Spencer's 50-250 km.
- **Extras (all judgement calls):** written law adds a third. Bureaucracy or relay posts double it ("government at a distance",
  Taagepera). Riding and roads each make a km cost two thirds. A 1,000 m climb doubles a km's cost. The sea needs boats, and is
  cheaper by sail.
- **Dragon realm:** 250 km of flight, ignoring sea and slope (judgement, O4). It needs settled subjects within reach.

Every number in the module is labelled "sourced" or "judgement" (a test checks this).

## Numbers

Read-only from `runs/`. "Settled people" is everyone in the ledger's towns and villages inside the polity. Areas use L7 cells of
~3,113 km².

**a2b637**, D&D peoples on dba204 (made today on current code):

| when | chiefdoms | states | empires | dragon realms | largest |
|---|---|---|---|---|---|
| 10,000 years ago | 0 | 0 | 0 | 2 | gold dragons' realm, 0.06 Mkm² |
| 6,000 years ago | 0 | 0 | 0 | 13 | copper dragons' realm, 0.18 Mkm² |
| 2,000 years ago | 0 | 0 | 0 | 21 | copper dragons' realm, 0.19 Mkm² |
| 1,000 years ago | 1,405 | 80 | 130 | 24 | Trojanel (human) empire, 0.54 Mkm², ~640 k people |
| the present | 934 | 167 | 177 | 24 | Trojanel (human) empire, 1.23 Mkm², ~1.5 M people |

At the present:
- **Chiefdoms:** median 4,600 people (830-28,000).
- **States:** median 100,000 people and 56,000 km².
- **Empires:** median 154,000 people and 121,000 km².
- **Dragon realms:** median 32,000 subjects; the largest is 0.19 Mkm².
- **Land ruled:** 81 Mkm², about half the land.

**3c1caf**, `v010-earthlike-a-seven-meals` (made 2026-11-01). No new D&D or Seven Meals peoples showcase existed yet today; only
the v010 time zooms (fc5311, 56dee1) had been re-run.

| when | chiefdoms | states | empires | dragon realms | largest |
|---|---|---|---|---|---|
| 9,000 years ago | 86 | 0 | 0 | 13 | green dragons' realm, 0.17 Mkm² |
| 7,000 years ago | 1,043 | 1 | 1 | 14 | North of Shakhitrem (orc) empire, 0.32 Mkm² |
| 5,000 years ago | 1,335 | 0 | 4 | 18 | South of Shakhitrem (hobgoblin) empire, 0.66 Mkm² |
| 3,000 years ago | 737 | 14 | 15 | 15 | West of Hizam (human) empire, 1.94 Mkm² |
| 1,000 years ago | 1,079 | 24 | 28 | 18 | West of Hizam (human) 2, 1.95 Mkm² |
| the present | 1,191 | 12 | 55 | 20 | South of Talatos (human) 5 empire, 1.95 Mkm², ~1.4 M people |

At the present:
- **Chiefdoms:** median 2,300 people.
- **States and empires:** median about 450,000 people and 0.9-1.2 Mkm².
- **Dragon realms:** median 13,000 subjects.
- **Land ruled:** 70 Mkm².

**Against history (baselines all from Taagepera 1997 and Johnson & Earle 2000, as quoted in round 1, `proposal.md` 2.1.2):**
- **Size ladder:** in range on both runs (see above).
- **Largest polity:** Seven Meals' 1.9 Mkm² at 3,000 years ago is over Taagepera's pre-650 BC bar of 1.1 Mm². Its humans have the
  distance techs by then, and Taagepera ties the jump to government at a distance, not a date, so this is not wrong on its face.
  The present's 1.2-1.9 Mkm² is under his post-650 BC floor of 2.3 Mm²: no conquest yet.
- **Lifetimes:** too long (see above). Only a fall hazard and war will fix this.

**Robust when nudged** (3c1caf, counts at each 2,000 years):
- **State reach ±10%:** the largest polity moves ±20% (1.62 / 1.95 / 2.36 Mkm² at the present), and the counts move by less than
  10%.
- **Hemmed-in factor (0.5 to 0.4), incumbency (1.5 to 1.25):** no change at all.
- **Dragon flight (250 to 200 km):** dragon realms shrink, and a few more chiefdoms appear.

No step explodes.

## What is not in v0

- **War:** no conquest, no change of owner, no deaths. PW-1432 plugs in at `polities.WAR`, with `polities.borders` listing who
  touches whom.
- **Falls:** no collapse hazard (draft). No authored nudges (PW-785 back-fills Seven Meals' empires).
- **Names:** a polity's name is its capital's region and ruling people ("Luki (human) 4" is the fourth so named). Real names come
  with PW-856's names slot.
- **Rulers:** the ruling culture is the capital's people's culture on its cell. Hybrid peoples whose demes belong to a parent's
  culture show that culture as ruler: for example, a half-orc town ruled by "humans of ...".
- **Slider:** the globe's time slider moves by stored frames (500 years apart in these runs). The layer shows the century step
  nearest each frame, and the server holds every century.

## Files

- `planet/lineages/polities.py`: the read-out (`derive`, `summary`, `step_view`, `report`, the war seam `WAR` and `borders`).
- `planet/server.py`: `GET /api/polities?run=<id>[&ago=<kyr>]`, `polities_doc` (disk cache, never the run folder).
- `planet/lineages/cultures.py`: `culture_uid` and `uids()`. Every culture is keyed by its stable uid, and the uid is rebuilt
  for a cultures.json made before PW-1283 (a2b637's has none).
- `viewer/globe/polities.js`: the layer, its legend and the card. It is wired in `layers.js` and `describe.js`.
- `tests/test_polities.py`.
