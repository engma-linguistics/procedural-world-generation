---
id: PW-457
title: "Climate: eastern Canada gets 1.9x the observed summer rain and 0.5x the winter's, with summers +5.5 C (Labrador snowfall 236 vs 408 mm)"
type: task
status: done
parent: null
milestone: null
subsystem: climate
effort: m
impact: med
found_by: pw033
blocked_by: []
relates: [PW-033]
refs: [planet/climate.py, docs/review/audit/PW-033-diagnosis.md]
created: 2026-10-20
updated: 2026-10-22
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

## Updates
- 2026-10-22: Status todo -> done. 2026-10-22 stage 3 merged (lane A12): summer fetch from the arriving sea air on distance scales (fetch_km 1000, fetch_h 3500), per-time reach, PET-referenced energy split, mountain rule, humidity floor. Humid summers +5-6 -> +2-4 C; SH coastal range 1.29x (pass); dry-region summer rain down; r 0.620. W Europe / Fennoscandia summers worse via too-cold near-land NH SST (new ticket). Merged under the owner's principle.
- 2026-10-20: Created from inbox draft draft-east-canada-summer-rain-winter-dry.md (found by pw033).
