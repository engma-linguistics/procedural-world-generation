# v2 proposal: open work outside v1, at epic level

Prepared 2026-10-21 for the owner's morning review. Read-only: no ticket was edited. Board state from `board.py` on main (c3fbb00).

## Summary

- **Epics:** 17 proposed. 10 exist today and are not v1 (PW-013, 090, 103, 155, 156, 184, 216, 443, 470, 490). 7 are new (A to G below). PW-244 (v1) is not counted.
- **Scope:** 156 open non-epic tickets sit outside v1 (107 unscheduled, 49 v2, 3 later, and the epic children). Rough leaf effort is about 80 agent-days (xs 0.5 h, s 2 h, m 4 h, l 8 h, xl 40 h). PW-470 (ice ages) alone is about 21 of those.
- **v2 headline:**
  - Zoom and world features people can see first: river detail, sea-level marks, karst, escarpments, coasts (epics B, C).
  - Resources and detailed rock: PW-155 with PW-474 as the enabler (both already v2).
  - Planet settings and phone layout: PW-481 and PW-483 (already v2).
  - Speed pass: PW-247 with PW-252, the numba fuse (already v2).
  - Realism follow-ups: the rain subset of PW-013, closed basins (PW-054), L6/L7 consistency (PW-290), soils and vegetation (PW-184).
- **Moves out of v2:** the ice subtree (PW-470, 37 children) goes to later, as do PW-103, PW-490, PW-156 and PW-207. The owner wants features before ice quality, and these are post-v1 by the owner's own calls.
- **Proposed v2 leaf effort:** about 25 agent-days, plus PW-155 (xl, a multi-week project if taken whole).

---

## 1. PW-470 Ice ages done properly (existing, xl, high): LATER
Milestone is v2 on the epic and all 37 children today. Move the subtree to later: the owner parked it post-v1 on 2026-10-20 and wants features first.
- Key items: PW-030 sawtooth (l, high), PW-459 orbit response (l, high), PW-460 margin melt (l, high), PW-461 deglaciation (needs-decision), PW-464 cycle-average run ice (l, high), PW-469 window time zoom (m, high), PW-447 and PW-434 (needs-decision).
- Also unscheduled and related: PW-313 and PW-332 (Antarctic snow, blocked, m high; merge candidate), PW-421 (blocked, m high).
- Effort about 21 agent-days. Plus 30 smaller ice and time-zoom tasks.

## 2. PW-490 L8/L9 finish (existing, xl, med): LATER
Owner lists it post-v1. It is xl and needs the speed pass first. No children yet.

## 3. PW-103 Multiscale time (existing, xl, high): LATER
Deep time down to centuries is a new simulation scale. Not needed for a finished planet. Its v2 milestone is ahead of the owner's ordering.
- Children: PW-416 river through time (l, low, blocked). PW-207 fauna (s, low, v2 today; owner calls it post-v1, so later).

## 4. PW-155 Resources layer (existing, xl, med): v2
Owner excluded it from v1 and it is the strongest "fun feature" for v2. Resources are cheap per cell (labels), so most of the cost is at finish or zoom time.
- Take first: PW-098 resources and hazards (l, med, v2; sits under PW-090 today), PW-474 detailed rock (m, med, v2, the enabler).
- Caveat: xl. Plan it as a sub-project, not one ticket.

## 5. PW-156 Weather generator (existing, l, med): LATER
Owner note 2026-10-16: "very low priority, after v1". Its v2 milestone should move. PW-042 jet stream (m, low, unscheduled) belongs here.

## 6. PW-184 Life and the land surface (existing, xl, high): v2 (unscheduled today)
PW-244 gap (5) says the life layer must be complete for v1, so the owner needs to decide what soils is for v1 (see decisions).
- v2 items: PW-212 soils from peat (s, med), PW-330 SoilGrids match 44% to 50% (m, med), PW-329 soil memory (s, low), PW-206 vegetation game attributes (m, low, v2; see v1 flags), PW-347 boreal fire (s, low).
- Later: PW-377 Earth grassland NPP and fire (m, med, Earth-only).
- Gap: no open ticket covers coastal life. PW-097 (reefs, mangroves) in epic C is the closest.

## 7. PW-013 Rain and ocean fidelity (existing, xl, high): v2, owner decision first
Owner note 2026-10-16 demoted rain to the final v1 calibration pass, but PW-244 gap (3) still names it. Decide whether PW-015 and PW-016 are v1.
- v2: PW-015 moisture transport (l, high, blocked), PW-016 overturning spin-up rule (m, high), PW-019 patchy rain (m, med), PW-228 vegetation agreement gap is regional rain (l, med), PW-352 humid subtropical summers (m, med).
- Later: PW-017 Antarctic sinking (m, med), PW-232, PW-233, PW-353 (m, low).

## 8. PW-090 World finishing pass (existing, xl, high): keep as the v1 umbrella
It holds v1 children PW-037 (glacial imprint), PW-092 (zoom synthesis), PW-099 (human-use layers), PW-495, PW-497, PW-499. Keep it open until those close.
- Re-parent the unscheduled v2 children into epics B and C (owner edit, not made here): PW-093, PW-094, PW-096, PW-097, PW-101.
- PW-494 GLiM lithology (s, low, v2) moves to later.

## 9. PW-216 Moons and planet bodies (existing, xl, low): LATER (bottom)
Owner: bottom of the backlog.
- Children: PW-217 tidal friction (l, low), PW-218 configurable moons (m, low), PW-219 other planets (xl, low). PW-219 overlaps PW-481 planet form, so it is a merge candidate.

## 10. PW-443 Weird worlds (existing, xl, low): LATER, wontdo option
Owner: "way post-v1". No children and nothing depends on it. Closing it costs nothing, so it is the clearest wontdo option.

---

## A. Speed, pipeline and data (new): v2
Goal: an L7 planet in 30 to 40 minutes, repeatable and resumable runs, clean outputs.
- v2: PW-247 speed pass (l, high, v2 today), PW-252 fuse numpy glue into numba (l, high, v2), PW-386 moisture tool misroutes Atlantic rivers (xs, low).
- Later: PW-259 Stommel solver (m, low), PW-444 shared cell-area code (s, low), PW-500 cooperative job cancel (s, low), PW-322 layer compression (m, low), PW-153 ocean layers in keyframes (m, low).
- Moves to v1: PW-508 and PW-446 (see v1 section).

## B. Zoom landforms and rivers (new): v2 headline
Goal: zooms show landforms a reader recognises. This is the "fun features" core.
- v2: PW-094 river detail (l, med: meanders, oxbows, terraces, fans, floodplains), PW-093 sea-level marks (m, med), PW-130 karst (m, med), PW-135 escarpments (m, med), PW-136 exposed stratum (m, med), PW-101 microclimate (m, med), PW-419 coarse-zoom volcano cone (m, med), PW-165 fold strike (m, med).
- Smaller, v2 or later: PW-096 wind features, PW-118 calderas, PW-147 cuestas, PW-175 coastal plain dip, PW-177 dune fields, PW-383 forearc islands, PW-394, PW-420, PW-433 (later).
- Earth-only, later: PW-132 landform classes on the Earth reference.
- Leftovers from PW-005 (done): PW-130, 132, 135, 136, 147, 165, 175.
- Effort about 8 agent-days.

## C. Coasts and human use follow-ups (new): v2
Goal: coast and navigation detail for the v1 human-use layers.
- v2: PW-097 coast detail (l, med: reefs, atolls, mangroves, barriers, cliffs; this is the coastal-life gap), PW-074 wave power (m, med), PW-501 passes (s, low), PW-504 low-water navigability (s, low).
- Decision: PW-502 fjord harbours (s, med). It is a PW-099 gap, so v1 or v2 is the owner's call.
- Later: PW-076 tides (m, low, Earth-only Fundy and amphidromes).

## D. Fine-zoom quality (new): later, with one v2
Goal: fine-zoom artefacts.
- v2: PW-404 sawtoothed crests (m, med).
- Later: PW-370, PW-391, PW-403, PW-411 braided reaches, PW-413, PW-433 oxbows (all s or m, low).
- The v1 fine-zoom polish (PW-485 to 489, 488 at med) stays v1.

## E. Viewer and phone (new): v2 for the owner items
Goal: a usable viewer on phones, and the leftover polish.
- v2: PW-483 phone layout (m, low; owner post-v1), PW-400 instanced trees in the zoom 3D view (m, med), PW-507 navigator leftovers (s, low), PW-417 retire flicker switches (xs; owner confirmed PW-415 resolved, so check whether it is already done).
- Later: PW-506 2D map overlays, PW-223 and PW-224 satellite clouds and colours, PW-316 60 fps replay, PW-371 cache order, PW-399, PW-401, PW-402, PW-410.
- Unscheduled, PW-481 planet form (l, med, v2) sits loose under PW-244.

## F. Plates, basins and lakes (new): v2 for five
Goal: generated worlds keep closed basins and tidy plate boundaries.
- v2: PW-054 closed basins lost over time (l, high), PW-243 closed-basin share doubles from L6 to L7 (m, med), PW-430 giant closed lakes made in a step (m, med), PW-134 per-cell flicker (m, med), PW-171 continental pits (m, med).
- Later: PW-170 collision churn, PW-359 hollow volume (m, med), PW-025, PW-047, PW-051, PW-056, PW-242, PW-289, PW-431 (s, low).
- Merge: PW-432 into PW-054 (see close list).

## G. Earth-match climate and ocean (new): later, three v2
Goal: physical realism, checked on Earth as a test analogue (not a parity target).
- v2: PW-026 winter maritime air inland (m, high), PW-458 Baffin Bay overturning (l, high), PW-290 L6 vs L7 aridity on the same seed (m, med; the showcase level).
- Later: PW-038, PW-039, PW-041, PW-112, PW-346 (polar and ocean Earth misses), PW-396, PW-397, PW-414, PW-457, PW-153.
- Drop candidates: PW-152, PW-324, PW-325 (Earth-only, nothing for generated worlds), PW-368 (owner parked it as someday).

---

## v1 flags (existing v1 items and moves into v1)

Moves into v1 (rare; real bugs in v1 features):
- PW-508 (m, med): a make-job restart starts the tectonic simulation over. Reliability of the v1 one-button flow (PW-248).
- PW-446 (s, med): the cached mantle basis differs from a fresh build (up to 0.063), changing runs. Breaks repeatability for the v1 health sweep (PW-246).
- PW-348 (xs, low): land under 0.5 m is stored as sea elevation but carries soil and vegetation. Data bug in v1 export (PW-100).
- PW-503 (s, low): human-use on a zoom builds edge lists for every pixel. Memory and time at 4096 x 4096 in a v1 feature (PW-099).
- Fold, don't move: PW-498 (time zooms made before carving can't finish) into PW-202, the v1 showcase remake.

Existing v1 items to re-check:
- PW-284 flexural moat: a 15% share tuned on one L7 seed's closed-basin count. This is metric-chasing; re-check against the audit rule before v1 freezes.
- PW-304 rain kernel vapour not mass-conservative (~0.6 m/yr residue on test planets). A real bug in v1 rain. Keep v1, prioritise.
- PW-475 game export depends on PW-206 (v2 today). PW-244 says game attributes are not v1, so either move PW-206 into v1 or move PW-475 out.

---

## Owner decisions for the morning
1. **Rain in v1?** PW-244 gap (3) says rain, but the 2026-10-16 update says final calibration only. Which of PW-015 and PW-016 is v1?
2. **Soils in v1?** PW-244 gap (5) requires the life layer. Does soils (PW-212, PW-330) go to v1, or is it v2 with the coastal-life work (PW-097)?
3. **PW-206 vs PW-475.** Game attributes are not v1 but game export is. Pick one.
4. **Ice subtree to later.** Confirm PW-470 and its 37 children move from v2 to later.
5. **Wontdo.** PW-443 (weird worlds), PW-368 (parked drift), and the Earth-only misses PW-152, PW-324, PW-325.

## Close, merge and supersede candidates
- PW-432 into PW-054: it is evidence for PW-054, not separate work.
- PW-498 into PW-202 (v1).
- PW-033 into PW-448: both are the Earth time-zoom glacial depth gap.
- PW-332 into PW-313: both are the Antarctic snow gap.
- PW-115 superseded by PW-460: both are margin melt, and PW-460 is the fix.
- PW-219 into PW-481 (planet form) if the planet-settings work covers other sizes.
- PW-421: close after the PW-366 re-measure (owner's decision A on 2026-10-16).
- PW-417: close if the owner's Chrome test is done (PW-415 resolved on 2026-10-16).
- PW-368: wontdo (owner parked it on 2026-10-16).
