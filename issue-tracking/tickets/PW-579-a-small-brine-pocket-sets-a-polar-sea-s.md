---
id: PW-579
title: A small brine pocket sets a polar sea's deep water and gates out the rest (dad91b's south 4.5 → 0.9 Sv)
type: task
status: done
parent: null
milestone: null
subsystem: ocean
effort: m
impact: med
found_by: laneA5 (stage 2b + PW-578, merge pass)
blocked_by: []
relates: [PW-578, PW-458, PW-346, PW-017]
refs: [planet/ocean.py, docs/review/base-climate/stages.md, "world dad91b"]
created: 2026-10-22
updated: 2026-10-22
---

## Description
The generated world dad91b still sinks in both hemispheres, but its south has fallen across the stages: stage 1
4.5 Sv, stage 2b 3.2, PW-578 0.89 (one site, 72.6S 67.8E, 0.43 Mkm2, drho 5.4 kg/m3). The other 8 worlds are 6.7–20
Sv in each hemisphere.

**Why (lane A5, dad91b re-climated on main 2684f2b against this branch):** its southern polar sea is small and
hemmed in (76% of the land poleward of 50S; 14.5 Mkm2 of sea there, 2.9 Mkm2 poleward of 70S).

| poleward of 60S | main (stage 1) | branch |
|---|---|---|
| sea-ice growth (m/yr) | 0.91 | 1.41 |
| winter density, area mean (kg/m3) | 1026.98 | 1026.97 |
| winter density, densest 10% | 1028.37 | 1029.20 |
| poleward of 70S: salinity / densest 10% | 34.60 / 1028.74 | 34.82 / 1029.85 |
| sinking (Sv) | 3.37 | 0.88 |

Stage 2's sea ice (more of it, and its brine) is working as designed: the bays beside the southern continent grow
~1.4 m of ice a year, export it, and keep the brine, so their water turns salty and dense (the polynya mechanism of
Antarctic shelf water). But in `ocean.overturning` the deep-water reference is the area mean of the densest
`moc_top` (10%) of the polar sea. So these few brine-dense cells raise the reference ~0.8 kg/m3, and the gate (water
within `moc_drho` of the reference minus `moc_mix`) shuts off the rest of the open polar sea, whose mean density
hasn't changed. The strength law is proportional to the sinking area, so the small pocket alone gives ~1 Sv.

This is not a numerical bug. It is a question about the mechanism:
- on Earth, Antarctic Bottom Water does form from small shelf polynyas, yet carries ~10 Sv. The dense shelf water
  cascades down the slope and entrains the water around it, so the flux isn't proportional to the area where it
  forms;
- in the model, a small dense pocket can only *lower* its hemisphere's sinking, by raising the bar for the open sea.

Earth's own south is also weak (2.4 Sv; PW-017).

Options:
- A: give a sinking site's flux an entrainment term (cascading shelf water draws in the ambient water), so a
  dense small site isn't area-limited;
- B: the deep-water reference as a mix of the whole sinking-capable polar sea rather than its densest 10% (a small
  pocket then dilutes into it instead of setting it);
- C: accept it: a hemmed-in polar sea with little open water makes little deep water.

Lean: A or B. Ocean / stage-1 code, so for the coordinator's ruling and the next ocean pass, not this merge.
- [ ] rule on A / B / C
- [ ] check Earth's Weddell and Ross under the chosen option (PW-017)

## Updates
- 2026-10-22: Status needs-decision -> done. 2026-10-22 merged (lane A10): entrainment, moc_entrain 1.5; reference = lighter of the old and the pocket/open-sea mix. Earth S 2.51 -> 5.94 Sv, N 14.4 Sv (92% open polar); Fennoscandia coldest month -6.0 (meets +-6). dad91b stays 2.5 Sv: its dense shelf water is behind straits (new ticket).
- 2026-10-22: Created from inbox draft draft-dad91b-southern-sinking-weakening.md (found by laneA5 (stage 2b + PW-578, merge pass)).
