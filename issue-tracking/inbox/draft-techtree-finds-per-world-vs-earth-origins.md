---
title: "Tech tree: peoples find each tech ~2.7x as often as Earth's independent origins (copper ~12 a world vs 4); better needs do not fix it"
type: task
status: needs-decision
parent: PW-675
milestone: null
subsystem: timezoom
effort: s
impact: low
found_by: fun-lane-69
blocked_by: []
relates: [PW-1124, PW-1122]
refs: [planet/lineages/techtree.py, planet/lineages/samples/techtree.toml, docs/references/tech-catalogue/]
---

## Description
In plain words: when a few peoples have what it takes to invent something, each of them invents it itself before a neighbour
can show them. On Earth copper smelting was found in about four places (the Balkans, Iran, Peru, west Mexico); in our worlds it
is found about twelve times. The same holds across the whole tree: half the techs are found 2.7 times as often as Earth's listed
origins or more.

Numbers (fun lane 69, PW-1122 ingested, runs 488d7e 6128a3 114231 570701 x 2 draws; a group's finds count as its people's):
| tech | Earth's origins | finds per world | world first, kyr |
|---|---|---|---|
| copper | 4 | 7-16 (mean 11.8) | 6.3 |
| writing | 5 | 5-9 (7.3) | 5.6 |
| cities | 6 | 6-12 (8.9) | 6.4 |
| the wheel | 3 | 5-8 (5.5) | 5.7 |
| bronze | 5 | 3-4 (3.5) | 5.2 |
| iron | 1 | 4-9 (6.4) | 4.7 |
| pottery | 7 | 2-7 (4.1) | 18.5 |
| kilns | 2 | 5-11 (8.8) | 7.8 |
| plough | 3 | 6-10 (7.6) | 7.9 |
| the bow | 1 (not in the catalogue's list) | 1-3 (2.1) | 53 |
Over the 481 techs with an origins count: median finds / origins 2.75; 44% above 3x. (The catalogue lists one origin for many
rows it was unsure of, which inflates the ratio; copper, writing and cities have good counts.)

Why needs alone cannot do it: a soft (Holocene) tech's rate is set so that a 10 M people takes as long after its prerequisites
as Earth's FIRST finder did (copper: ~1 kyr after kilns). Contact passes a tech at ~0.05-0.15 per kyr. So any people that gets
the prerequisites (mostly by contact, at about the same time as its neighbours) invents copper within ~1 kyr, ten times faster
than a neighbour can show it. Lane 69 tried the real preconditions (native copper working, hot kilns and towns: copper now needs
native_copper, kilns, towns): the finds stayed at ~12, because those spread or are found the same way. Needs change who is
ready, not how many of the ready find it themselves.

Options:
- A: accept it. The owner's 10-30 ruling allows rough near-simultaneity, and a fantasy world's peoples are fewer and bigger than
  Earth's; 2-3x is "several places within a few kyr".
- B: a per-tech correction from the origins count only: Earth's date is the first of k candidates, k ~ (peoples ready on Earth)
  / (origins), so each people's rate is lower by ~k; keep the anchor for the world first by checking the first of the ready
  set, not one isolated people (anchor_check would build a world of N anchor peoples). Lane 64 rejected a global k = 4 because it
  compounded down the chain; a per-tech k from the catalogue, checked on the world first, would not compound the same way.
- C: faster contact for know-how next door (raise contact_rate for techs whose prerequisites the taker already has): the first
  finder's neighbours learn it before they find it. Changes every tech's spread.
- D: check finds against origins in tests (a band per tech) and fix outliers one by one.
Lean: A for v1 (dates are fine), B as a v2 experiment with the world-first check.
