# V1 reassessment (2026-10-16)

*Read-and-plan review of PW-244 against the board as of commit 9a57727. No tickets changed. Section 5 is for the coordinator to apply.*

**Short version.** Nearly every physical system a v1 planet needs is in. What is missing is the **finishing and delivery layer**: glaciers that carve (PW-037 then PW-092), one command from seed to finished world (PW-248), export (PW-100), and a fine zoom that redraws everything it inherits (PW-392, PW-405). Rain (PW-015) is no longer a v1 blocker. It is calibration, gated on an Earth-analogue question (PW-352). The best move for the run lane is to finish PW-358, then **freeze run physics** and remake the showcases (PW-202). Everything else can then build on stable runs.

## 1. System inventory

| System | State | Notes (tickets) |
|---|---|---|
| Tectonics, mantle, volcanoes | **in** | Plates, collisions, rifts, discrete volcanoes and chains (PW-001). Open items are tuning: closed basins PW-054, escarpments PW-135, flicker PW-134/170. |
| Rock record, landform classes | **in** | Strata and 8–12 classes with zoom synthesis (PW-005). Tuning: PW-130, 136, 147, 165, 175. |
| Surface erosion, sediment | **in** | PW-049 and PW-243 are tuning. |
| Climate (temperature, wind, seasons, clouds) | **in** | Regional Earth misses (PW-352, 346, 112, 026, 039) are calibration. |
| Rain / moisture transport | **in, needs tuning** | Stage 1 (conservative transport) merged, so L6/L7 agree and the residue is ~0. Stages 2–3 are parked on PW-352 (PW-015 blocked). Generated planets are plausible (27.8% arid). |
| Ocean (currents, SST, salinity, overturning) | **in** | The overturning still starts by a spin-up rule (PW-016, waits on PW-015). This is a crutch, not a missing system. |
| Run ice / glaciation | **in** | PW-308 and PW-364 done; the deepest era is -219 m. Antarctic margins PW-313/332 are an Earth-analogue issue. |
| Glacial time zoom | **partial** | Ice, sea level, shelves (PW-367) and finished worlds (PW-091/193) work. **No glacial erosion or imprint (PW-037).** No terminations (PW-030). Start drift PW-295/241 is parked behind PW-366. |
| Hydrology, lakes, deltas | **in** | Giant closed lakes (PW-300) wait on PW-358, which is in progress. |
| Coast (waves, tides, delta type) | **in** | Coast forms (cliffs, beaches, barriers) PW-097 are zoom detail. |
| Coastal and shallow-sea life | **in** | PW-188, PW-326. |
| Soils | **in** | PW-185, PW-331. SoilGrids agreement PW-330 is calibration. Coal from peat in the run (PW-212) is small. |
| Vegetation | **in** | World, run, zoom and climate feedbacks are built. Not yet in the time zoom (PW-213). Game attributes PW-206 are parked. |
| Satellite view | **in** | PW-224 and PW-223 are polish. |
| Highlights | **in** | PW-079 is polish. |
| Regional zoom | **in** | Missing detail: glacial landforms PW-092, river planform/fans/terraces PW-094, sea-level marks PW-093, microclimate PW-101. |
| Fine zoom (50–100 m) | **in, partial** | PW-129 Python side and 3D tile merged (f3fc8cd, cb3c8a6), plus PW-390. **Glaciers, landform overlays and reefs are not redrawn (PW-392).** Rivers zigzag (PW-405). Volcano form PW-395. |
| Viewer / 3D | **in** | Globe and zoom 3D, fine tiles, replay. PW-316, 371 and 400–402 are polish. |
| Seed-to-world flow | **partial** | Every step exists, but there is no single `planet make` or "New planet" button (PW-248). |
| Export | **missing** | Only the zoom's `heightmap.png`. No tiles, splat maps or GeoJSON (PW-100). |
| Human-use layers | **missing** | Navigable rivers, harbours, passes, fertile land (PW-099). |
| Store / infra / health | **in** | Determinism, health sweeps (PW-246), audit (PW-245). Speed PW-247/252 open. |
| Resources, hazards | **missing** (out of V1 by decision) | PW-155, PW-098. |
| Weather, moons, species/time | **missing** (out of V1) | PW-156, PW-216, PW-103. Embedded run ice ages PW-104 also missing. |

## 2. Blocking v1 ("all major systems in, even if they need tuning")

1. **PW-358 → PW-300: finish, then freeze run physics** (s). Already in flight. Giant hyperarid lakes are the last visible plausibility defect in run frames. Freezing afterwards makes every later lane build on runs that stop changing.
2. **PW-202 showcase remake on the frozen code** (s, plus L7 compute). Old runs no longer replay after PW-187 and PW-015 stage 1. This is also V1's review gate.
3. **PW-037 glacial imprint in the time zoom** (l). This is the biggest missing system. It is the owner's stated "last phase" of a finished world (PW-090: glaciers that carve valleys). It is time-zoom only, so it does not touch run physics.
4. **PW-248 one command and one button, seed to finished world** (m). This is V1's own definition, and every piece already exists. It mostly orchestrates steps and adds sensible defaults.
5. **PW-092 glacial landforms in the zoom** (l, after PW-037). Fjords, U-valleys, cirques, moraines and hanging-valley falls. This is what makes the ice ages visible in the 3D views.
6. **PW-100 export, with PW-099's derived layers in its feature list** (m + s/m). Data usable outside the viewer is a V1 criterion, and nothing exists yet beyond one PNG.
7. **PW-392 + PW-405 fine-zoom completeness** (m + m). The fine zoom is the owner's favourite surface. It currently drops glaciers and overlays, and its rivers draw 90° switchbacks. Those are defects in a new system, not tuning.

*Borderline, recommended after the above but not blocking:* PW-213 vegetation in the time zoom (m). Finished worlds already get equilibrium vegetation. Migration and refugia matter mainly for PW-103.

## 3. Not blocking v1 (about 105 tickets, by group)

- **Earth-analogue climate and ocean calibration (~25):** PW-015 stages 2–3, 016, 017, 026, 038, 039, 041, 042, 112, 152, 162/232, 233, 290, 304, 324, 325, 346, 352, 353, 396, 397, 210/228. Earth is an analogue. Re-tune once, at the end (PW-244 item 9).
- **Tectonic and surface realism (~18):** PW-025, 047, 049, 051, 054, 056, 130, 132, 134–136, 147, 165, 170, 171, 175, 242, 243, 284, 289, 359. Closed basins (PW-054) is the most visible of these, but generated planets are plausible without Earth's 20%.
- **Ice and time-zoom tuning (~10):** PW-018, 030, 033, 115, 241, 295, 313, 332, 366, 368, 385, 398.
- **Zoom and fine-zoom polish (~15):** PW-093, 094, 097, 101, 118, 177, 370, 383, 391, 394, 395, 403, 404, plus 096 (loess, see section 5).
- **Viewer and perf polish (~12):** PW-223, 224, 316, 322, 371, 399–402, 247, 252, 259, 153, 348, 386.
- **Life and world calibration (~6):** PW-206, 207, 212, 329, 330, 347, 377.
- **Out of scope / someday (epics):** PW-155, 156, 098, 103, 104, 216–219.

## 4. Recommended order (next ~10 items)

| # | Run lane (serial) | Zoom lane | Viewer lane | World / infra lane |
|---|---|---|---|---|
| 1 | PW-358 finish, re-measure PW-300 | PW-405 fine river planform | PW-248 button half (with world lane) | PW-248 `planet make` CLI |
| 2 | **Freeze**; PW-202 L7 showcase remake + review | PW-392 fine-zoom glaciers, overlays, reefs | PW-399/401 fine-tile falls list, flights (s) | PW-037 glacial imprint (time zoom) |
| 3 | PW-252 numba fusion (bit-identical, safe under the freeze) | PW-092 glacial landforms (after PW-037) | Glacial landforms' look in 3D | PW-100 export + PW-099 layers |
| 4 | PW-212 coal from peat, then thaw for one calibration pass | PW-395 volcano form | PW-400 instanced trees (if wanted) | PW-213 vegetation in the time zoom |

PW-037 sits in the world lane because it runs in `timezoom.py`, not `simulate`. It must not share files with the zoom lane's PW-092 until PW-037 has defined the imprint layers. A second ice-age showcase is due after PW-092.

## 5. Board changes recommended (not applied)

| Ticket | Current | Proposed | Reason |
|---|---|---|---|
| PW-129 | todo | done | Python side (f3fc8cd) and 3D tile (cb3c8a6) merged; follow-ups are numbered. |
| PW-393 | todo | done | "Fine zoom here" from the 2D page shipped in cb3c8a6. |
| PW-388 | needs-decision | done | The coordinator decided (B), and canopy displacement shipped in cb3c8a6. Option C is PW-400. |
| PW-290 | todo | re-measure → done | Stage 1 commit 1416523 names it, and coordination says L6/L7 now agree. |
| PW-304 | todo | rescope (land-books residue only, low) | The transport is conservative since stage 1 (merged draft). |
| PW-019 | todo | re-measure | Named in the stage 1 commit. Close if the lattice is gone. |
| PW-210 | todo | merge into PW-228 | Same 44% vegetation-agreement gap, same root (regional rain). |
| PW-162 | todo | merge into PW-232 | PW-232 is "the rest of PW-162". |
| PW-096 | todo (loess only) | merge into PW-037 | PW-037 already lists loess downwind of outwash. |
| PW-366, PW-368 | todo | wontdo (parked), or impact low with a "parked" update | Owner said "close enough" / someday. They look actionable on `board.py next`. |
| PW-295, PW-241 | blocked on PW-366 | impact low, keep blocked | They follow PW-366's parking. |
| PW-359 | todo | blocked by PW-358 | The coordinator's own park condition. |
| PW-206, PW-207 | todo | wontdo (parked) or leave low | Owner parked game attributes; PW-207 needs PW-103. |
| PW-104 | todo (PW-090) | impact low, note "not V1" | Time zoom → finished world covers the last phase; embedded episodes are a later run-lane cost. |
| PW-015, PW-016 | in PW-244 gap (3) | relate only, not a V1 gate | See section 6. |
| PW-037, PW-092, PW-248, PW-100, PW-099, PW-392, PW-405 | various | attach to PW-244 (relates/children) | The section 2 blockers. |
| PW-252, PW-259 | no parent | parent PW-247 | They are speed-pass work items. |
| PW-202 | todo | blocked_by PW-358 (soft) + impact high | It is the V1 review gate. Remaking before the freeze wastes L7 compute. |

## 6. PW-244 scope and acceptance: what should change

- **Items (2) and (4) are done** (PW-245, 246, 240, 308). Drop them from the gap list and keep the health sweep only as an acceptance check.
- **Push back on (3), "climate fidelity, mainly rain."** Stage 1 fixed the physics: the transport is now conservative and L6/L7 agree. What remains is that Earth's land runs too wet and its humid-subtropical summers too warm. That is Earth-analogue calibration, gated on PW-352, and the owner prefers features once results are close enough. Keep PW-015 parked and treat it as part of item (9). Do not let it hold V1.
- **Add the glacial imprint (PW-037/092).** PW-244 lists "the run's ice in cold eras" but not the carving the owner asked for in PW-090. Without it the time zoom's finished world is the same terrain with ice on top.
- **Raise the "browsable" bar to the fine zoom** (50 m, now built). Add PW-392/405 so the closest view is not the weakest.
- **(5) "Life layer complete": narrow it.** Soils and coastal life are done. Vegetation in the time zoom (PW-213) is a refinement that serves PW-103 more than V1. Make it optional for V1.
- **Make (6) speed measurable,** or it never closes. For example: "`planet make` at L6 in ≤ X min and at L7 in ≤ Y min on the Threadripper, outputs bit-identical." PW-252 (~45% of wall time in numpy glue) is the obvious first cut.
- **Make "reliably" concrete:** `planet make` succeeds on the 8 L6 and 3 L7 health seeds with no outlier class worse than the 2026-10-15 after-audit sweep, and with no frame lake over 1 Mkm² in hyperarid ground.
- **Export (8) should carry PW-099's derived layers** (passes, harbours, navigable rivers). They are cheap and they make the data usable for a game.
- **On "resources not V1": agree, with one caveat.** The strata already hold most of what a coarse resources layer needs, so PW-155 is the cheapest high-value post-V1 item for game use. Design PW-100's feature schema so resources can be added later without a format change.
