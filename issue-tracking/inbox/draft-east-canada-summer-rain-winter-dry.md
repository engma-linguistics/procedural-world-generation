---
title: "Climate: eastern Canada gets 1.9x the observed summer rain and 0.5x the winter's, with summers +5.5 C (Labrador snowfall 236 vs 408 mm)"
type: task
status: todo
parent: null
subsystem: climate
effort: m
impact: med
found_by: pw033
blocked_by: []
relates: [PW-033]
refs: [planet/climate.py, docs/review/audit/PW-033-diagnosis.md]
---

## Description
Earth L6 today, ice-free land (`scratchpad/pw033/probe1.py`, diagnosis section 1). The model's Apr-Sep :
Oct-Mar precipitation rates (mm/yr) against the observed:
- Labrador 50-60 N: 1762 : 368 (obs 906 : 662), July 17.9 C (obs 11.9).
- Hudson Bay lowlands: 1569 : 211 (obs 820 : 424), July 21.1 C (obs 15.4).
- Keewatin: 610 : 232 (obs 396 : 194), July 13.8 (obs 11.8).
So the snowfall Labrador gets is 236 mm w.e./yr against 408 on the observed climate, and the Hudson Bay
lowlands get 108 against 271. Real Labrador-Ungava was a core Laurentide inception area. The pattern looks
monsoon-like: a hot continental summer drawing in moist air, and too little winter storm-track snow. It
is not the ocean: the Labrador Sea is close to the observed temperature.
- [ ] Labrador's summer : winter precipitation ratio < ~2.5 and its July within ~3 C of the observed, with
  no loss on the Köppen scorecard
