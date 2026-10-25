# Pre-v1 assumptions audit: final report

## Verdict

The physics core is sound. Tectonics, isostasy, routing, the climate kernel and the CO2 thermostat are crude but defensible, and most findings are wrong constants, stale docs or Earth-copied clocks rather than broken mechanisms. Two things are not sound yet. First, the evidence the owner is about to review is stale: `docs/overview.md` §3 still shows pre-PW-266 Earth numbers, and the reference worlds 2a7385 and 6fbc2c predate the PW-806 plant fix. Second, a few things would embarrass v1 in front of an amateur geologist or hydrologist:
- **Iron:** iron exists only on Archaean shields.
- **Shelves:** continental shelves are 2–8x rarer than on Earth (unverified).
- **Deserts:** on Earth's own terrain the model's Earth has almost no Sahara (B 20% vs 30%, land rain +41%).
- **Rivers:** rivers run 2–4x Earth's discharge, while the docs call the water balance Earth-like.
- **Volcanoes:** continental volcanoes stop at 3.5 km, though highlights promises Chimborazo (6.3 km).
- **Plates:** default worlds often show one plate covering half the planet.

Each has a cheap first step. None means v1 is "built on lies", but several calibrations (the 0.45 star rate, PCO2_BALANCE, the icehouse share) rest on weak or mislabelled pieces. Those pieces should be re-measured together, not one at a time.

## Ranked findings

| # | Domain | Finding | Kind | Sev | Action |
|---|---|---|---|---|---|
| 1 | life | Owner's feedback/reference worlds (2a7385, 6fbc2c) predate PW-806: 2–16% trees, dung-heavy fuels | stale output | high | Banner the feedback doc now; remake both worlds after the star anchor lands; re-run peoples and fuels |
| 2 | docs | overview.md says "every number checked" but §3 has B 31%, 842 mm (now 20.3%, 1118 mm); §2.6 CO2 text is wrong (REF_FREEZE, tanh CO2_MAX=6) | doc-mismatch | high | Regenerate §3 from a fresh earth_check, scorecard and pytest; rewrite §2.6 from earth.py |
| 3 | tectonics/peoples | "Iron" = BIF on cratons ≥1.8 Gyr only; no bog iron, laterite or ironstone | false-fact | high | Add pre-industrial iron sources from existing layers; keep BIF as the industrial grade |
| 4 | tectonics | Shelves 0.6–1.4% of ocean vs Earth 5.8%; submerged continent sits at −0.7 to −1.6 km | unverified | high | Hypsometry check in scorecard; test clinoform progradation; fix water-loaded isostasy |
| 5 | climate | 3 °C drift is a temperature term, so the thermostat answers it with low CO2: warm eras are CO2-starved (pCO2 <180 ppm 7–32% of the time) | unverified | high | Move the drift onto the carbon source; measure corr(T, ln pCO2) together with PW-812/815 |
| 6 | water/peoples | Fish runs, salt licks, salt rivers, lake fisheries, predator-free islands and reach are set in cell units, so L6 and L7 give different foods | kludge | high | Convert to m³/s, km² and km; add an L6/L7 agreement test |
| 7 | water | Rivers 2–4x observed, land R/P 0.49 vs 0.38; overview calls it Earth-like | doc-mismatch | high | Don't retune; fix the doc; report discharge ratios in scorecard; note it on PW-015 |
| 8 | climate/framing | Model Earth: B 20% vs 30%, hot desert 3–5%, rainforest 2–3%; no v1 check; PW-228/290 have no milestone | known limit | med | State it as a v1 limitation, or move PW-228's dryness part into v1; add hot-desert share to earth_check |
| 9 | framing | `global_temp_c = 14.5 + dT` overstates the real mean by ~20% of dT; realised sensitivity ~2.4 °C/doubling | false-fact | med | Report the area-weighted mean; rename dT "profile offset" |
| 10 | climate | Earth anchor 577526 predates ~15 climate commits; PW-808's diagnosis was drawn from it | stale output | med | Rebuild the Earth world; re-check PW-808 numbers on it |
| 11 | climate | Ice-age bar "~100 kyr cycles" is met by construction; glacial cooling ranges 0.5–10.4 °C | kludge | med | Say "scripted" honestly; floor the cooling before v1; move the 100/405 kyr periods to TZParams |
| 12 | framing | Scorecard and earth_check run at L6 on 2 seeds; v1 is L7 | unsupported | med | One L7 earth_check before the tag; re-measure PW-290 in pairs; ≥6 seeds or Earth-only |
| 13 | life/peoples | Farming, "Holocene" and domestication dates follow Earth's clock, not the world's last deglaciation (41a7a4's interglacial is ~0 kyr old) | kludge | med | Key epochs to the world's termination; gate farming on a known staple |
| 14 | tectonics | Weathering sink ignores rock type and never saturates; decisions.md:33 records a "saturating law" that was never built | doc-mismatch | med | Fix the decisions row now; re-weigh the sink by lithology with the PCO2_BALANCE work |
| 15 | tectonics | Continental volcano summits capped at 3500 m above sea level | false-fact | med | Cap relief above the floor (~4.5–5 km) instead |
| 16 | tectonics | Late-run plates: largest covers 40–68% (Earth ~20%); PW-565 is v2; summary "plates" count is wrong | owner-belief | med | Re-rank PW-565 or accept it on record; add a plate-size metric; fix world.py:316 |
| 17 | climate | Time-zoom co2_share 0.5 gives LGM pCO2 0.47x (Earth 0.68x), ~130 ppm | false-fact | med | Express as a glacial pCO2 ratio ~0.68 |
| 18 | life | PW-806 acclimation gives an LGM wetter in trees than today; parameters at the top of the literature; marked done with its in-run check unmet | kludge | med | Add an ordered LGM < Holocene ≤ today test; gate on PW-808 |
| 19 | water | No wetland evaporation; the Sudd treated as an "artefact" and drained by MIN_SLOPE | owner-belief | med | Charge flooded share open-water ET; revisit MIN_SLOPE |
| 20 | water | Lakes 0.07–0.25% of land on most L7 worlds vs ~0.7% resolvable on Earth | kludge | med | Report lake share per level; evidence onto PW-054 |
| 21 | peoples | Density ignores productivity: 14 M tundra herders, 107 M foragers | false-fact | med | Scale density by absolute NPP and goods, by way of life |
| 22 | peoples | `milks = max(herd, lac)` gives foragers "dairy herds" | false-fact | med | Drop lac from milks; let lactase rise under dairying |
| 23 | life/peoples | No pig, reindeer, camel, llama, buffalo or yak; tundra "pastoral nomads" herd only dogs; brief promises salt pork | gap | med | Add pig first, then reindeer and camel; make the brief text conditional |
| 24 | life | Grazing ignores forage quality: wet tall grass is the best pasture; forests hold no game | unsupported | med | Forage-quality ramp; forest-game term |
| 25 | life | Plant weathering factor (≤1.75x, scaled by NPP) cites GEOCARB (~4x, scaled by roots) | doc-mismatch | med | Fix the comment, or tie it to rooting; measure with the star zero point |

**Low, tidy-up items:**
- Inherited crust ages ignore run length: >1.6 Gyr runs end older than the Sun. Fold into PW-813.
- Breakup rule forbids India-sized pieces.
- Coal gated on veg>0.5 rather than woody swamp floras. Fold into PW-807.
- BQART glacial factor 5x too weak (coast.py:621).
- Stream-power 2^(level−5) factor undocumented.
- Discharge assumes equal-area cells.
- Kelp, reefs, seals and meandering rivers ungated in time.
- No groundwater or wells.
- Pre-grass niches fall back to moss, with no ferns or cycads.
- Two documented placeholders, GRAZE and crown fire off in runs: record both as v1 approximations.
- Crops read only annual means.
- PCO2_REF 350 is really ~300 at equilibrium.
- Sea-level ice/basin terms use inconsistent isostasy.
- Ice-albedo comment claims the LGM anchor; it gives about half.
- Global rain pinned at 1000 mm: label it "enforced".
- Chicken and horse dates.
- Livestock boat ladder.
- Salt-trade cap.
- `meta.era` documented as unread but read.
- Bird taste and smell defaults.

**Fine, briefly:** the oceanic 4.2 km volcano cap, half-space cooling for young floor, the routing on observed rain (Amazon 1.03x with GPCC), the 3%/K rain scaling (upper end but defensible), and GRAZE as a tracked placeholder.

## Where the owner may be off

- **"Iron comes from old shields."** Before about 1850, almost all iron came from bog ore, laterite and ironstone, which occur on young land nearly everywhere. Banded iron formations needed industrial processing. *Source:* Buchwald 2005, *Iron and Steel in Ancient Times*; Pleiner 2000.
- **"The Sudd is an artefact basin."** It is a real wetland that evaporates about half the White Nile's inflow, and the Inner Niger Delta loses about 40% of its inflow. The model lacks the process; the basin isn't wrong. *Sources:* UNEP Sudd hotspot page; Mahé et al. (IAHS).
- **"The hellhole lines mark molten worlds."** Earth's own Eocene (~+10–16 °C) and PETM (~+17 °C) were forested, with crocodiles in the Arctic, and Earth's mean ranged 11–36 °C over 485 Myr. The line is also in dT units, about 20% above the real mean. A strict bar is defensible for "Earth-like", but call it "hotter than Earth's record", not "molten". *Sources:* Inglis et al. 2020, *Clim. Past* 16; Judd et al. 2024, *Science*.
- **"Ice ages work: 100 kyr cycles pass."** The period is scripted, and Earth itself ran on 41 kyr cycles before ~1 Ma. *Source:* Lisiecki & Raymo 2005.
- **"Default worlds at the run end are representative."** For tectonics they are the most sclerotic phase: Earth's largest plate covers ~20%, the model's often 50%+. *Source:* Bird 2003.
- **"About half of LGM cooling was CO2."** That half is all greenhouse gases together; CO2 alone is about a third. *Sources:* Köhler et al. 2010; Hansen et al. 2008.
- **"3 °C per doubling, as on Earth."** Because of the dT labelling, the model realises ~2.4 °C.
- **"Chickens 8 ka, horses 5.5 ka."** The evidence now gives ~3.5 ka for chickens (on rice and millet farms) and ~4.2 ka for the horse that spread across Eurasia. *Sources:* Peters et al. 2022, *PNAS*; Librado et al. 2021, *Nature*.
- **Rulings that are canon, not factual errors.** Ruminant fiends as grain farmers, and "no offspring" at 1 Myr of divergence, are deliberate canon. Real ruminants get acidosis from grain, and mules come from ~4 Myr of divergence. Just record both in decisions.md as fantasy rules.

## Proposed tickets

The peoples layer (lineages) has no subsystem of its own in the allowed list, so those tickets are filed under the nearest one.

- Banner and remake reference worlds 2a7385/6fbc2c after the star anchor | docs | v1 | Re-run peoples and fuels on current plants before the feedback review relies on them.
- Regenerate overview §3 and rewrite §2.6 | docs | v1 | Replace stale Earth numbers and CO2 text with generated, dated output; fix decisions.md:33 and README's biome line.
- Pre-industrial iron deposits | tectonics | v1 | Add bog iron, lateritic ferricrete and ironstone, and map "iron" to their max with bif_fe.
- Shelf hypsometry metric and progradation test | surface | v1 | Measure shelf share against Earth and test clinoform fill plus water-loaded isostasy.
- Climate drift as carbon-cycle noise | climate | v1 (needs-decision) | Move the OU drift onto outgassing so warm eras carry high CO2; measure with PW-812/815.
- Physical units for culinary water thresholds | hydrology | v1 | Convert seafood, salt_reach, coastform and compose thresholds to m³/s, km² and km; add an L6/L7 test.
- Declare Earth dryness a v1 limitation and track it | climate | v1 | Add hot-desert and B share to earth_check; put PW-228's dryness part in v1 or rule it out.
- Real global mean temperature label | climate | v1 | Report the area-weighted mean and restate the hellhole and HOT lines in that unit.
- Rebuild the Earth anchor world | climate | v1 | Replace 577526 and re-check PW-808's numbers on the new world.
- Honest ice-age bar and cooling floor | timezoom | v1 | Label the period as scripted and floor glacial cooling so icehouse moments never get ~0.5 °C.
- L7 Earth check and multi-seed scorecard | infra | v1 | Run earth_check at L7 once, re-measure PW-290 in pairs, and use ≥6 seeds.
- Volcano relief cap | tectonics | v1 | Replace the 3500 m absolute continental cap with a relief cap.
- Plate-size diagnostic and PW-565 re-rank | tectonics | v1 | Add a largest-plate share metric, fix the plates count, and decide on PW-565.
- Time-zoom glacial pCO2 ratio | timezoom | v1 | Set the glacial CO2 drop to ~0.68x at Earth's cooling.
- Lithology-weighted weathering sink | tectonics | v2 (needs-decision) | Weight supply by silicate share and retry saturation, together with PCO2_BALANCE.
- Wetland evaporation | hydrology | v2 (needs-decision) | Charge flooded cells open-water ET and revisit MIN_SLOPE.
- Deglaciation-keyed peoples calendar | highlights (lineages) | v2 | Anchor HOLOCENE_KYR, FARM_KYR and domestications to the world's termination.
- Productivity-scaled population density | highlights (lineages) | v2 | Density per unit absolute NPP, by way of life.
- Dairy from herds, not lactase | highlights (lineages) | v2 | Drop lac from milks and let lactase evolve under dairying.
- Pig, reindeer, camel, llama rows and updated dates | highlights (lineages) | v2 | Add the missing herd animals and fix the fowl and horse anchors.
- Forage quality in grazing | climate | v2 | Penalise wet tall C4 grass and add forest game.
- PW-806 ordering test | climate | v1 | LGM < Holocene ≤ today for tropical forest, gated on PW-808.