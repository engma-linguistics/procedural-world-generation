---
id: PW-140
title: "Travel highlights from seasonal climate: beach destinations, ski country, mild winters"
type: task
status: done
parent: null
subsystem: highlights
effort: s
impact: med
found_by: daniel
blocked_by: []
relates: [PW-126]
refs: [planet/highlights.py]
created: 2026-10-14
updated: 2026-10-14
---

## Description
Owner: 'let's find somewhere nice to go during beach season, or somewhere tolerable in winter with good skiing.' Use the new July/January temperature and rain layers (PW-126) for highlight finders: beach destinations (warm, dry, sunny summer half-year on a coast; moderate wave power; warm sea), ski country (mountains with a snowy winter: below-freezing winter at altitude with good winter precipitation, reachable from valleys with a tolerable winter), mild-winter retreats (mild, dry winter half-year). Each with a one-line why in the highlight text, using the hemisphere's own summer/winter. Optionally a combined 'year-round resort town'.

## Updates
- 2026-10-14: Status todo -> done. highlights.py: beaches, ski_country, mild_winters, year_round from the July/January layers, each hemisphere's own season, a numeric why in title and blurb; skipped on worlds without the layers. 67317b: 4 beaches, 4 ski, 3 mild winters, 1 year-round resort. Viewer ?hl=N opens a highlight. Test: tests/test_highlights.py::test_travel.
- 2026-10-14: Created.
