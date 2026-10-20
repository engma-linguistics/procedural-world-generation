---
id: PW-458
title: Earth's overturning sinks 4 Sv in Baffin Bay; the Norwegian Sea freezes and Fennoscandia's January is 18 C too cold
type: task
status: todo
parent: null
subsystem: ocean
effort: l
impact: high
found_by: pw033
blocked_by: []
relates: [PW-033, PW-018]
refs: [planet/ocean.py, planet/climate.py, docs/review/audit/PW-033-diagnosis.md]
created: 2026-10-20
updated: 2026-10-20
---

## Description
In `climate.compute` on Earth L6 today (`scratchpad/pw033/ocean.py`, diagnosis section 7):
- NH sinking is 4.1 Sv (real AMOC ~15-20), and its main sites are at 75 N, 63 W: northern Baffin Bay, not
  the Nordic, Labrador and Irminger seas.
- The overturning's SST warming (`moc_heat`) is +3.0 C in the Irminger Sea, +1.1 in the Labrador Sea, and
  -0.4 in the Norwegian Sea. The Norwegian Sea's SST is 0.5 C annual and -1.8 in January (real ~7-8, ice-free).
  The Barents Sea is frozen all year (real south ~2-5 C). The NAD at 45 N is 11.5 C (real ~13-15).
- On land: Fennoscandia Jul / Jan 9.3 / -26.7 C (obs 14.2 / -8.7), British Isles January -3.4 (obs +4.5),
  Fennoscandia precipitation 459 mm (obs 718). The North Atlantic Drift doesn't reach Norway.
- Labrador's +5.5 C summer bias is NOT from this: its sea is near the observed, and hosing the overturning
  off leaves it at 17.4 C.
- Response: at -3 C the sinking moves to Iceland-Irminger (6.5 Sv), at -6 C it collapses to 0.3 Sv, and
  0.3 Sv of hosing shuts it off.

Why it matters: the time zoom's Eurasian ice (Fennoscandia 1.5 Mkm2, Siberia 4 Mkm2 at the deepest glacial)
is largely this cold bias. On the observed baseline Fennoscandia's ice vanishes. Earth's LGM had warm,
seasonally open Nordic Seas feeding the Fennoscandian sheet (Hebbeln et al. 1994).
What to try: find why the inflow is routed into Baffin Bay (densest water there because of the freezing,
leads and ice export?) and why the surface currents carry no NAD past ~55 N toward the Norwegian Sea. Check
it against generated planets' overturning too.
- [ ] Earth's NH sinking in the Nordic, Labrador and Irminger seas, ~10+ Sv; the Norwegian Sea ice-free in
  winter; Fennoscandia's January within ~5 C of the observed

## Updates
- 2026-10-20: Created from inbox draft draft-north-atlantic-drift-missing.md (found by pw033).
