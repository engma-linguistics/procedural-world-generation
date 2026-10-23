---
id: PW-589
title: "The sea's summer air the fetch builds on is 2-6 C too cold off W Europe, Scandinavia and Alaska and 2-5 C too warm in the SH: the annual SST, not the swing"
type: task
status: done
parent: PW-470
milestone: v1
subsystem: ocean
effort: m
impact: high
found_by: base-climate-laneA12
blocked_by: []
relates: [PW-580, PW-573, PW-587]
refs: [planet/climate.py, planet/ocean.py, docs/review/base-climate/stages.md, docs/review/base-climate/laneA12/]
created: 2026-10-22
updated: 2026-10-22
---

## Description
Stage 3's fetch (lane A12, `_summer_fetch`) builds the land's summer from the sea air that arrives. So the summer
sea air's bias now reaches the land, which the land's full continental swing used to hide.

Earth L6, ocean cells with NCEP data. The diagnostic is `seadiag.py` in lane A12's scratch, numbers below. Columns:
the model's annual SST, its summer sea air, NCEP's warmest month and NCEP's annual mean.

| box | SST | summer air | NCEP warmest | NCEP mean |
|---|---|---|---|---|
| NE Atlantic 45–55N | 11.8 | 14.3 | 16.5 | 12.8 |
| Biscay–North Sea | 7.3 | 13.5 | 17.3 | 11.3 |
| Norwegian Sea 60–70N | 4.9 | 8.3 | 11.5 | 6.6 |
| Baltic | 0.1 | 3.2 | 17.2 | 6.4 |
| Gulf of Alaska | 3.6 | 6.4 | 12.6 | 6.8 |
| NE Pacific 40–50N | 9.1 | 11.3 | 16.3 | 11.7 |
| S Atlantic off Patagonia | 12.3 | 17.9 | 14.5 | 10.4 |
| Tasman | 19.6 | 23.1 | 18.2 | 15.2 |

- In the north the annual SST is 2.5–6 C too cold. In the south it is 2–4 C too warm.
- The Baltic is the worst case. Its winter freezing deficit (`_summer_half`) takes 6 C off a 9 C swing, so its summer
  air stays at 3 C (NCEP 17).
- Effect on land: W Europe's warmest month goes +0.4 → −2.1 with the fetch, Fennoscandia −5.2 → −5.7 and Alaska
  −2.8 → −5.2. The probe that swaps NCEP's sea air into the fetch alone (`laneA12/stage3_probe_fetch_obs_sea.txt`)
  gives back 0.5–1.4 C of that. The rest comes in through the reach and the coast mixing, which carry the same sea air.
- In the south, Tasmania's +6.2 is mostly the Tasman's warm air.

What to try: find why the near-land NH seas' annual SST is so cold. Candidates are the gyre's poleward heat, the
`_summer_half` deficit on enclosed seas, and the sea-ice lid. Stage 3 is complete without this. This is what keeps W
Europe and Fennoscandia under main's.
- [ ] NE Atlantic, North Sea and Gulf of Alaska summer sea air within 2 C of NCEP, without warming the Tasman further

## Updates
- 2026-10-22: Status todo -> done. 2026-10-22 merged (lane A13): the overturning's heat comes off the mean over each latitude's sea in both hemispheres (fold=True). Near-land SST rows within +-2 C 3/8 -> 5/8; Fennoscandia summer -5.7 -> -3.9, winter -6.0 -> -4.5; W Europe summer -2.1 -> -1.2 (bar +0.4 missed: the summer swing, new ticket); rain r 0.620.
- 2026-10-22: Created from inbox draft draft-near-land-sea-summer-air-cold-north-warm-south.md (found by base-climate-laneA12).
