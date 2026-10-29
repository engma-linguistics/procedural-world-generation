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
- 2026-10-27 (owner): the deep-time bar fails only a hellhouse; icebox and never-ice eras are reported, not failures. Pass = good finish moment + no hellhouse. The sim is suspect if nearly all worlds (>=80%) are iceboxes or nearly all hellhouses (fmtally prints it). Judge physics changes over two pooled offset rolls.
- 2026-10-26: v1 finished world = latest habitable moment within the last 10 Myr (PW-866); judged there, flagged if none passes.
- 2026-10-26 · Backlog workgroups (owner) · 19 workgroups as in the backlog doc; base climate (PW-570) on the physics lane early in v2; other planet kinds v3; phone viewing out of v2/v3 (PC only); progress bars added (PW-914) · PW-900
- 2026-10-26 · Run length (owner) · v1 is judged on 1 Gyr runs; 2 Gyr runs are a post-v1 stretch goal and, when they return, are judged on their last 1 Gyr only (early snowball-era ice allowed) · PW-894, PW-895
- 2026-10-25 · Non-CO2 greenhouse gases first (owner) · PW-859 goes to the top of the physics queue; the faint-young-Sun icebox is fixed by planet-side greenhouse (CO2 response, methane), not by bending the star curve · PW-859
- 2026-10-25 · Plume degassing (coordinator) · plumes and LIPs outgas CO2, sized from the literature · PW-875
- 2026-10-25 · Finish moment (owner) · taking the finished world at a human-habitable moment near the run end is choosing the right moment, not a kludge (Earth passes the finish checks only in its last few Myr); window set from measurement; approved plan: last ~10 Myr at a ~0.5 Myr climate step, pick the best candidate · PW-866
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
- 2026-10-27 (owner): dragon density default 1 per 5,000 km² (user option; 10k rarer, 1k far too many by default).
- 2026-10-27 (owner): gnomes arrive at 50 kyr (were 15 kyr, remnants into a full world). Half-elves (and hybrids generally) are exempt from the remnant check: few where parents rarely meet is fine, reported only. Low-density overlap of peoples is fine.
- 2026-10-27 (owner): polycentric origins: a split people arises in several patches of its country, only where its parent lived at the split (dwarves in ranges the hominid stem reached). Walker jump reach ~800 km; far jumps rarer (small scouting bands), shorter ones preferred.
- 2026-10-27: hybrid peoples only after the farming onset (visible kin, not smoothed-away ancestry); check little 2+-people land before 20 kyr. Dragons and giants are counted megafauna (Damuth densities, own country, many small pockets, exempt from the 300-cell target; frost giants and white dragons, fire giants and red dragons overlap); breeding stays a mystery. Gnomes are a normal people: insular, denser, less far-reaching than humans.
- 2026-10-27: root ancestor lines start on different landmasses; related peoples may cluster near their ancestor until the civ stage. Overland jump dispersal yes, reach scaled by mobility (fliers > sea peoples > aquatic furthest over water); peoples abandon unsuitable land and low-density land can be taken over fully (PW-888, PW-920).
- 2026-10-26 (PW-888 targets): test on 6 planets; every people needs a livable range (~300+ L7 cells; 100 too low) on ~70% of rolls; hybrids present where parents meet; no planet-wide dominant people assumed (e.g. never plan on 50%+ humans); regional and per-civ dominant peoples are expected and wanted; a planet-wide dominance lever comes later (PW-916); hard fail if a main people is still a remnant (<~100 cells) at the present (farming onset); deep-time bottlenecks (e.g. at 100 kyr ago) are fine if the people expands. Civ work will reshape ranges (displacement, refuges, ways of life).
- 2026-10-26 · Civilizations round 2 (owner) · peoples ranges follow the ice-age climate; mixing preset realistic by default; tech uneven between civs with distance-based catch-up and pockets that refuse it; grudges fade with mixing plus a stubbornness axis; refactor the peoples code first and again at epic closures; gods as a light placeholder layer in v2; a backlog reorganization into v2 workgroups next · PW-900..913
- 2026-10-26 · Civilizations design (owner) · cultures/settlements/polities built in steps; history zoom from a per-region farming onset at 25-yr steps; emergent first, anchors later (may be credited to gods); plague on every world, other templates at sim rates; attitudes = history + temperament, xenophobia by culture and species; tech stops ~mid-1400s by default with a visible tech tree; named individuals/writing/industry v3+. Open questions in the doc round 2 · PW-856
- 2026-10-25 · Origins and crowding (owner) · most species must not evolve on one small landmass (origins by habitable area, species-area); crowding raises the drive to explore; conflict and warfare go to the civilizations epic · PW-888, PW-887, PW-856
- 2026-10-25 · Contact fronts (coordinator) · a denser people takes a thinner one's cells along the contact line (modern-human vs Neanderthal replacement) · PW-887
- 2026-10-25 · Frontier invasion built (coordinator) · INVADE 0.5, floor 0.3, crowding x(1+2 crowd) on sea crossings; accepted although the PW-885 8k line is unmet: the small continent holds only ~4k suitable cells, so the niche, not exclusion, is the limit now. Hobgoblin thinning re-measured after PW-888 changes origins · PW-887, PW-885
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
- 2026-10-28: PW-821 rain fix (showers need humid air) tried and dropped for now: paired 2-roll L6, 24/36 vs main 29/36 finish passes, Earth rain corr 0.637 vs 0.648. Kept on branch worktree-agent-a27927a0e29b0cbdf; waits on PW-015 (ocean evaporation).
- 2026-10-28: tech tree v0 merged (fun lane 39): 8 tracks, 98 techs in planet/lineages/samples/techtree.toml; language arises per stem and never by contact; elders early, arrivals bring kits; Technology tab in the peoples workbench. Output only for now (PW-946).
- 2026-10-28 (owner): language is a later joint project; the tech tree's language rules are for review only. Ruling: almost any contact spreads language to genetically modern species on these timescales.
- 2026-10-28 (owner): giants get their own, lower density (user option like dragons'). Nomads, hill giants above all, overlap other peoples more, with occasional conflict. An occasional main people with a small range in one setting is realistic; avoid only the pattern.
- 2026-10-28 (owner): plates may split three ways (triple junctions); experiment away the stress-rift die-off (PW-565, now v1).
- 2026-10-28: zoom tail merged (7cb8ca12): deltas grow a bird's foot only when river-dominated into water several channel depths deep (Wright 1977; Coleman & Wright 1975), not a hand; zoom harbours need open sea; living reefs follow the reef builders' calendar.
- 2026-10-28 (owner, megafauna scaling side session): approved docs/proposals/megafauna-scaling.md. Giants' masses and food, recommended column: hill 2.2 t, about 12 humans' food; storm 7.3 t, about 31. Dragons' size, wingspan and food by age. Dragons use the base age structure: ancients ~7% of dragons, ~1/3 of their biomass. Dragon generation time to be revisited (~430 yr). Report dragons by stage; giants don't need it. 1/5,000 km² is the present-day dragon density in peopled country. Natural density (~1/65 km²) holds where no people presses them: "the age of dragons". Papers live in docs/references/ (PDFs local, README index). Tickets PW-957..963. Giant density vs lane 38's 5,000 is open (PW-963).
- 2026-10-28: megafauna merged (94c5a318): giants 1 per meta.giant_km2 (default 5,000 km2, select 1k/5k/10k); nomads compete at 1-0.5*mobility with settled peoples (Khazanov 1984). Remnants 18 -> 24 per 24 rolls, per-people pass 75% held; repeats on 1df1c3 (orcs) and 067778 in PW-964. Giant density reconcile PW-963 (side session).
- 2026-10-28 (owner): giant density, option C (PW-963). Natural density comes from mass and is approached where few small folk compete. Peoples push it down easily, to a sparse present-day default (1 per 2,000 km² in peopled country; meta.giant_km2 becomes this pressed value). This is the same mechanism as dragons (PW-957). Players should not meet far more giants than they expect, or flocks of dragons.
- 2026-10-28 (owner, megafauna side session):
  - People density = way-of-life factor × productivity (PW-833).
  - Prey is a static field from net primary production (NPP), with no predator-prey cycles. Livestock counts as prey. Wild megaherbivores persist in giant country hostile to small folk (PW-966).
  - Megafauna pressure is one suppression number: persecution, not hunting.
  - Losing megaherbivores never zeroes dragons; they turn to livestock, tribute and kobold thralls.
  - Natural dragon numbers are reviewed on maps against familiar areas before they are fixed (PW-967).
  - Sapience arises once per stem at a dated node. Non-sapient kin live on as wyverns, drakes and pseudodragons (PW-965).
  - Kinds outside the tree (trolls, ogres) are DM-scale and not tracked.
- 2026-10-28 (owner): don't track non-sapient kin (wyverns, ogres, trolls...). A line may end as 'continues as animals, untracked', distinct from extinction, likely the stem's end at its split (PW-965).
- 2026-10-28 (owner): v1 physics triage. The climate leftovers go to v2 under the ice-age epic PW-470; PW-815 (star brightening) and PW-895 (mantle heat) are decided by going live on the 2 Gyr ticket PW-894. v1 physics is now rifts (PW-565/952/827), PW-880, PW-819 and PW-948, then the showcase rebuild and the tag. Owner worry: the ice-age redo is a possible bottomless pit, so timebox it in v2.
- 2026-10-28 (owner): v1 bar = a passing world stands up to casual-to-moderate scrutiny as a plausible end point and path, with no further physics. Coordinator: PW-015 (moisture transport, deserts) and PW-950 (shelves) pulled into v1 as visible soundness gaps.
- 2026-10-28: rifts merged (PW-565/952): settle clock on the new plate only, stress opening ~sqrt(area), plume triple junctions (triple_odds 0.5, aulacogen_odds 0.3; Burke & Dewey 1973). Owner approved the examples. test_land_and_crust[2] xfail for 27-28 km until PW-970.
- 2026-10-28: PW-965 merged: a stem's sapient = 'T' node and animals = true end ('continues as animals, untracked', not extinct; the stem's last split). Node dates (draconic 4 Myr, feline 1.5, avian 1.2, goblinoid 1, hominid 1.8) are placeholders.
- 2026-10-28: megafauna natural density merged (fun lane 41): prey from grazing NPP (stand-in proportional fit until the papers are fetched), natural density in wild country pressed by peoples to dragon_km2/giant_km2; selectable megafauna_natural, dragon_ages, dragon_generation, all candidates until the owner reviews PW-967. Per-people pass 70% vs 71%; present dragons 7.0k -> 17.6k and giants 1.8k -> 6.7k per run (needs-decision).
- 2026-10-28 (owner): forager baseline for giants is a setting, meta.forager_km2 (default 0.1, select 0.03/0.05/0.1), until Binford 2001 can be checked (PW-976). Hard-to-get sources live in docs/references/wishlist.md.
- 2026-10-28: Owner: PW-958 younger age schedule is the default; PW-977 present dragon density becomes a food-budget equilibrium (supply from prey + stock, demand from peoples and other predators, persecution separate), built in stages after PW-975.
- 2026-10-28: The megafauna side session is closed; megafauna design continues in the main session. PW-973 closed into PW-977 and PW-975; PW-967 reviewed.
- 2026-10-28: Owner: PW-959 dragon generation ~430 yr default for now (flag if counts wobble). PW-947/PW-971: language only after a stem's sapiens node; only bare-bones tool use before it. Node dates get a sourced review doc first.
- 2026-10-28: Merged the sapiens node dates review doc (docs/review/lineages/sapiens-dates.md, PW-971/PW-978); owner gut call pending.
- 2026-10-28: Merged PW-975: prey field from McNaughton et al. 1989 (log B = 1.52 log NAP - 4.79); present dragons and giants about 40% lower.
- 2026-10-28: Merged lane 23 (PW-970): welds need an inlet on the plate's own grid and >=20 km surrounding crust (a sampling ratchet grew continents with thin crust). The xfail is gone. Pass 31/36 -> 28/36, all losses warm (PW-980, v1, with PW-880/PW-819 next). PW-950 shelves to v2 after one failed round (water-loaded isostasy deepens margins; suggestions in the ticket).
- 2026-10-28: Owner gut call on sapiens node dates (PW-978): a long tools-before-minds run like the real ~3 Myr; dragons ~5 Myr; giantkin split earlier (add intermediate splits if needed); spread the reptilian splits; goblinoids shorter than hominids. Owner called the machine quiet for a few hours; both lanes frozen (SIGSTOP).
- 2026-10-28 (owner): language project set up as children of PW-767, no code yet: demes/phylogeography first (PW-981), then proto-languages + sound change from ~20 kyr (PW-982), morphology as a cycle (PW-985), food loanwords (PW-984); first-principles phonology experiment (PW-983) alongside. Name glosses PW-972. Ethnonym taxonomy doc linked on PW-767.
