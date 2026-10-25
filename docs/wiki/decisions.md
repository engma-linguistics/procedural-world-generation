# Decisions (ruling log)

One line per ruling: date · topic · ruling · ticket. Newest first within a section. "Superseded" rows are kept so nobody re-litigates them.

**Convention:** write new rulings in the ticket's Updates as `RULING (owner): ...` or `RULING (coordinator): ...`, then add a line here. Rows below before 2026-10-25 were seeded by grepping "Owner 20xx" in ticket Updates; the ticket has the full text.

## Standing process rules (owner)
- 2026-10-25 · Framing (owner) · drop the 'fiend' angle: seven_meals' antelope-kin and cervid-kin are the closest equivalent to tieflings; dnd tieflings are a demonic/abyssal template on humans from a historical event in the last ~10 kyr; forage-led farming, grain in moderation, no dairy approved · PW-858, PW-850
- 2026-10-25 · Greenhouse gases (owner) · track CH4/N2O separately from CO2 (climate reads all, plants read CO2) - an important v1 thread · PW-859
- 2026-10-25 · Feedback (owner) · cultures/civs, not species, are the unit of the culinary book; settlements mostly one species outside cities (design talk pending) · PW-856
- 2026-10-25 · Fantasy realism (owner) · hybrids follow real divergence times; fiend-kin are ruminants, so grain only as real ruminants can take it (coordinator: in moderation) or via an evolved trait; mostly farmers · PW-850, PW-851
- 2026-10-25 · Finished worlds (owner) · end temperatures within what modern humans lived through (coordinator: true mean ~-6..+3 C vs pre-industrial) and interglacial land ice near Earth's, not none and not ice-age · PW-812
- 2026-10-25 · Plates (owner) · a half-planet plate is wrong: find the cause; largest plate a little above Earth's historical largest, by mechanism · PW-827
- 2026-10-25 · Dragons (owner) · dragons are reptiles: a deep reptile line, extant megafauna at giant-like density, chromatic/metallic by biome · PW-855
- 2026-10-25 · Scope (owner) · iron from bog ore/laterite in v1; ice ages keep modern timing, documented; other greenhouse gases as a CO2-equivalent; don't over-chase Earth's dryness · PW-817, PW-824, PW-828, PW-821
- 2026-10-20 · Pass bar · ~70% of seeds passing is enough; outlier worlds allowed; use 6-10 seeds when 4 is too few; "not worse" = pass share doesn't drop · PW-438
- 2026-10-22 · Regressions · as the sim gets more sound, individual regressions are expected and teach what else to fix; adopt the whole-history ice criteria · PW-560
- 2026-10-22 · Local optima · land a correct mechanism even if a fitted kernel (rain/Koppen) regresses; fix that next · PW-578
- 2026-10-16 · Chasing Earth · if an option batch misses the bar, step back to cruder approximations or a relaxed bar; don't chase Earth perfection · PW-015
- 2026-10-19 · Models and budgets · Haiku mechanical, Sonnet moderate, Opus ice-age physics; hand off at ~100 calls · see [playbook](coordinator-playbook.md)
- 2026-10-24 · Carbon balance (coordinator) · with the star anchored at the run end, the weathering balance is anchored there too (GEOCARB frame, planted land at today's Sun); thermostat stays opt-in unless the anchored system still fails · PW-809, PW-810
- 2026-10-24 · Calendar (owner) · default worlds are taken at the run end ("now") or its last few Myr (modern plants and people); earlier eras by age before now; sea algae >1 Ga, land plants 470-500 Ma, everything on the real calendar counted back from the end · PW-807
- 2026-10-24 · Star anchor (owner) · a run ends at the present Sun: brightening anchored at the run end (a 2 Gyr run starts ~15% dimmer); runs up to ~4 Gyr should stay habitable throughout, like Earth since life began; optional offset to look into the future · PW-791
- 2026-10-24 · Star and plants (owner) · 0.45 ok; prefer dialling the star (bounded, slow, both ways, PW-791, v1 default for Earth-likes) over bending other systems or setting CO2; tree cover 15-40% with a geography caveat (coordinator: diagnostic; wet-tropics >= ~20% the hard check); plants change only where the literature says they are too steep · PW-791, PW-806, PW-780
- 2026-10-24 · Plants (coordinator) · treeless star-warmed worlds: recalibrate the plants' CO2 and warming responses (PW-806, v1); v1 climate bar is 1 Gyr, the 2 Gyr late window goes with PW-791 after v1 · PW-806, PW-780
- 2026-10-24 · Scope · Earth-likes first: water, hothouse and molten worlds wait until after the v1.0 tag; exotic shapes (ringworld, discworld, gas-giant moon) are for a standalone release someday, outside the culinary-dnd end-to-end · PW-802
- 2026-10-24 · Climate (coordinator) · water-world icebox: fix the CO2 reference freeze planet-relatively before adding any preset warming offset · PW-798, PW-799
- 2026-10-24 · Wiki · lean coordinator wiki approved; the full human wiki is parked to late v2 · PW-786, PW-792
- standing · No temporary fixes · fold a stopgap into the owning ticket; don't merge partial fixes · PW-074 (cited)
- standing · Outputs · old runs/worlds/zooms freely deletable; `tools/cleanup_outputs.py` is fine for the coordinator · PW-202

## Ice ages, climate, star
- 2026-10-25 · Finish moment (owner) · taking the finished world at a human-habitable moment near the run end is choosing the right moment, not a kludge (Earth passes the finish checks only in its last few Myr); window set from measurement · PW-866
- 2026-10-25 · Carbon source (coordinator) · the climate drift stands only for what the model lacks (burial, ocean chemistry), sized from the literature, with outgassing no longer counted twice; check a C3-limit weathering floor (Pagani 2009) · draft on v1-finish-12
- 2026-10-25 · Icehouse bar (owner) · option C: keep the physics (end-anchored GEOCARB balance, literature weathering, star thermostat off); no cap on a run's icehouse share; snowball/always-icebox, hellhole and never-ice still fail at ~70% of draws passing; finish checks (true mean -6..+3 C, interglacial ice ~Earth's, wet-tropics trees) stay · PW-865
- 2026-10-24 · Star lever · for Earth-like worlds NO ice ages is a fail too; star brightening is the accepted per-world lever; 0.45 is the working default (provisional, phone) · PW-780
- 2026-10-24 · Star thermostat · opt-in per preset, causal, slow, bounded luminosity range · PW-791
- 2026-10-24 · pCO2 · coordinator's call: carry a real ppm from the stock first; if wildly off, take A for now · PW-646
- 2026-10-24 · Forest-to-tundra test · eligibility by a rule on the world · PW-645
- 2026-10-24 · Multi-seed time-zoom fixtures · L4 multi-seed tests at ~50% (lottery-proof) · PW-643
- 2026-10-24 · Flora timeline · compress it (C4 grasses/succulents at ~66% of run), serial physics lane · PW-636
- 2026-10-22 · v1 scope · sim-physics (ice, rain, winds, base climate, epic PW-470) stays under v1; v1 is an arbitrary point · PW-244
- 2026-10-22 · Start and CO2 · mature start, set-once reference; CO2 as a stock; accept ~0.35-0.5 C/C; default run 1 Gyr, 300 Myr warm-up kept · PW-576
- 2026-10-22 · Base-climate plan · order approved; lane A stages 1-3 serial, lane B stage 4 · PW-570
- 2026-10-22 · Weathering · smooth saturating law, no hard cutoff · PW-574
- 2026-10-21 · Sea-level band · leave the first ~100 Myr (warm-up) out · PW-549
- 2026-10-21 · Ice batch · park PW-460/459/464 batch; take PW-465 coast_loss with the cost cut if it holds; v2 starts with a holistic ice review · PW-526, PW-514
- 2026-10-20 · Run moments · v1 bar is "cycles at ~100 kyr without runaway"; coastal-ice physics post-v1 · PW-492
- 2026-10-20 · Ice-age physics · parked under epic PW-470; v1 uses the glacial-index kludge · PW-471 (**partly superseded** by the 2026-10-22 v1-scope row for sim-physics)
- 2026-10-16 · Time-zoom ice · PW-366 close enough unless cheap · PW-366; climate_drift stays 3 C · PW-368; marine-margin buttressing option A · PW-367
- 2026-10-15 · Rain · all six leans of the moisture proposal approved · PW-015
- 2026-10-15 · Sea level reference · A+B (model's own steady ocean, SEA_TECT_MAX ~400 m) · PW-293
- 2026-10-15 · Incision per grid level · leave it, the law is sound · PW-302; zoom creep step option C · PW-125; world land mask later · PW-307; soils: all 7 leans · PW-185

## Zoom, viewer, v1 scope
- 2026-10-21 · Fine zoom · waterfalls acceptable for v1, gorge straight stays, further fiddling v2; wanted form (amphitheatre lip, tiered face) is v2 · PW-517, PW-532, PW-516
- 2026-10-21 · Fine-zoom carving · slope-settling pass plus rock-dependent carving · PW-541
- 2026-10-21 · Moved to v2 · flexural moat, rain kernel vapour, glacial cooling, game-export presets · PW-284, PW-304, PW-538, PW-475
- 2026-10-21 · Showcase remake · when v1 is done, 4 random-seed L6 + 4 random-seed L7 (full chain), as one batch · PW-202
- 2026-10-16 · Nice-to-have, not v1 · river-through-time · PW-416

## Peoples, culture, culinary
- 2026-10-25 · Dispersal (coordinator) · humans should spread like the record (Sahul by sea >=50 kyr, through held country within 10-20 kyr): pioneer advantage plus an early boat rung, by mechanism · PW-869
- 2026-10-24 · Owner's world (seven_meals) · antelope-kin and cervid-kin can milk by default but are mostly farmers, **then reversed**: no dairying for the setting's tieflings · PW-784 (**superseded** by) PW-793
- 2026-10-24 · Folklore · two layers per row: current name fades, legend/folklore persists; parked under historical linguistics · PW-757, PW-767
- 2026-10-24 · Empires · present-day Empire (antelope-kin) and fallen Empire (cervid-kin) in seven_meals; needs polities or authored anchors · PW-785
- 2026-10-24 · Culture depth · only a very shallow pass in the workbench (groups by way of life); deeper culture under the civilization epic · PW-661, PW-776
- 2026-10-24 · Anchors · optional back-fill only; default is plausible simulation; tree roots placeable · PW-734, PW-763
- 2026-10-24 · Map ownership · procgen owns the map; no fitting worlds to the culinary repo's written geography · PW-733
- 2026-10-24 · Horses and mounts · peoples in sustained contact take them up fast, with real barriers · PW-794
- 2026-10-24 · Deposits · found, not given: a per-people known share · PW-713
- 2026-10-24 · Industrial fuels · animal oils yes; no industrial-revolution fuels yet · PW-766
- 2026-10-24 · Attitudes · "aggressive" is several stances; later; v0 placeholder stays · PW-768
- 2026-10-24 · Incursions · a ruling-minority fast rise counts; keep it light · PW-769
- 2026-10-24 · Demographics · giants far fewer with larger ranges; some peoples insular, some exploratory · PW-650
- 2026-10-20 · Fauna · post-v1; first version a lookup by biome/water body · PW-207
- 2026-10-20 · Rock · detailed rock knowledge post-v1, nothing slow · PW-474
