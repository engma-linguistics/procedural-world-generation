# PW-846 scout 171: are the mountains too low?

Scout 171, 2026-11-03. Read-only measurements on stored runs and Earth data. No simulation runs (§5 says why).

## In plain words

- **The mountains are not too low for the grid.** One L7 cell is about 60 km across, and the model stores one height per cell: the cell's average. Earth averaged the same way tops out at **5.9 km** (Tibet). Its 8.8 km summits sit inside cells whose average is about 4.4 to 5 km. The "tallest peak 5.7 km" on world 2a7385 is the same kind of number.
- **Proof:** I passed Earth's own heights through the world builder's sub-cell texture step (`timeline.texture`). Earth's "tallest peak" then comes out at **5.7 to 6.3 km** (8 seeds). So with today's code, Earth itself would show the 5.7 km that the ticket complains about.
- **On current code, L7 has more high ground than Earth.** Seven Earth-like L7 runs on code from 10-27 to 11-01 have 2.1 to 3.7% of land above 4 km (median over their frames), against Earth's 1.5%. They have 10 to 18% of land above 2 km, against Earth's 4.7%. They also have more separate high regions: 15 to 25 regions above 2 km and 7 to 11 above 3 km, against Earth's 11 and 2. The 2a7385 world came from an older run (6b48f5, code 2865ee1) at a low-relief moment: 0.2 to 0.7% above 4 km around 792 Myr.
- **What is really missing is the Andes kind of range.** On Earth, a quarter of the land above 3 km is the central Andes, a range on an ocean-continent margin. In the runs, only 8 to 10% of the land above 3 km lies near such a margin, and volcanic-arc rock is 1 to 4% of it. Almost all high ground is collision plateau, about 60% of it on craton rock.
- **The lever I'd try first is not a physics change.** Report and draw summits as the cell average plus Earth's measured sub-cell relief, so the world's highest peak reads 7 to 9 km where the cell average is 5 to 6 km. I found no tectonic lever that should push heights up. The physics follow-ups point the other way (an overshoot at the top end) or sideways (Andean margins). Both are below.

## 1. Earth: what the grid can show

Sources: ETOPO1 (Amante & Eakins 2009, NOAA NGDC), sampled at 1/6 degree, and its L6/L7 cell means as built by `tools/earth_data.py` (`data/earth/L6.npz`, `L7.npz`, `raw_etopo_bed.npz`, `raw_etopo_ice.npz`). Sub-cell relief comes from the HydroSHEDS v1 30-arcsecond DEM (Lehner, Verdin & Jarvis 2008, Eos 89(10)), `data/earth/raw_hydrosheds_dem_30s.zip`. Both citations are as recorded in `tools/earth_data.py`. "Ice-free land" leaves out cells with more than 10 m of ice, which is how the run frames' bare bed compares best.

Share of land above each height:

| Earth | > 1 km | > 2 km | > 3 km | > 4 km | highest cell |
|---|---|---|---|---|---|
| L6 cell means (120 km), ice-free land | 19.5% | 5.0% | 2.6% | 1.6% | 5415 m |
| L7 cell means (60 km), ice-free land | 19.7% | 5.2% | 2.7% | 1.7% | 5878 m |
| L7, bed under the ice, all land | 18.6% | 4.7% | 2.4% | 1.5% | 5878 m |
| ETOPO1 1/6 deg samples, ice-free land | 19.9% | 5.7% | 3.1% | 2.0% | 6527 m |

Sub-cell relief: within 0.5-degree blocks (~55 km, about one L7 cell) of the 1 km DEM, I compared the highest pixel with the block's mean land height (blocks at least 90% land):

| block mean | blocks | median (highest - mean) | p90 | highest pixel |
|---|---|---|---|---|
| 0-0.5 km | 33525 | 105 m | 549 m | 3727 m |
| 0.5-1 km | 11567 | 389 m | 1085 m | 4575 m |
| 1-2 km | 8604 | 622 m | 1408 m | 6098 m |
| 2-3 km | 2298 | 617 m | 1762 m | 7479 m |
| 3-4 km | 618 | 1143 m | 2008 m | 7528 m |
| 4-5 km | 734 | 941 m | 1732 m | 8247 m |
| 5-7 km | 233 | 816 m | 1276 m | 7883 m |

The highest block mean is 5718 m. The highest 1 km pixel is 8247 m, which is Everest smoothed over 1 km. The 20 blocks with a pixel above 7 km have a median block mean of 4.9 km. So on Earth the named giants stand 2 to 4 km above their own 60 km average.

The world builder's texture adds at most about 180 m of noise plus 0.45 × 900 m of ridges (`timeline.texture`: `TEX_M`, `mountains * 900 * (rough - 0.45)`). That is roughly a third of Earth's p90 sub-cell relief on high ground. Earth's L7 grid through `texture()` gives a highest point of 5708 to 6292 m over seeds 1 to 8; at L6 it gives 5505 to 5829 m.

Ranges: connected regions of ice-free land above each height, counting regions of at least 50,000 km²:

| | > 1.5 km | > 2 km | > 3 km |
|---|---|---|---|
| Earth L6 | 18 | 11 | 2 (Tibet-Himalaya 2.95 M km², central Andes 0.89 M km²) |
| Earth L7 | 20 | 11 | 2 (3.0 M km² centred 34N 88E; 1.0 M km² centred 19S 70W) |

## 2. The runs

Scripts sit beside this file: `scout1_hyps.py` (hypsometry, crust tail, zones), `scout1_ranges.py`, `scout1_margins.py`, `scout1_tops.py`, `scout1_highrock.py` and `scout1_subcell.py` (Earth DEM). Run them with `PYTHONPATH=. uv run python docs/review/tectonics/mountains/scout1_X.py RUN_DIR...` (or `earth`). `scout1_hyps.py` samples about 50 frames per run, and these are medians over frames with t ≥ 100 Myr. Land means elevation > 0. "Zones" counts active collisions: connected groups of at least 3 cells along converging grid edges between continental crust on two different plates. A zone has about twice as many cells at L7, so compare zone counts within one level only.

| run | level, seed, code | > 2 km | > 3 km | > 4 km | frame max | continent > 60 km | zones |
|---|---|---|---|---|---|---|---|
| **Earth L6** | | 5.0 | 2.6 | 1.6 | 5415 | | |
| cacfc8 | L6 s1 bfda8e67 | 5.9 | 1.9 | 0.54 | 5828 | 0.40% | 6 |
| 9496cb | L6 s2 bfda8e67 | 6.4 | 2.6 | 1.22 | 6700 | 0.96% | 6 |
| e37ccc | L6 s1 (10-28) | 9.6 | 3.1 | 0.98 | 6011 | 0.58% | 11 |
| c9e85b | L6 s2 (10-28) | 6.4 | 2.7 | 0.76 | 5593 | 0.42% | 7 |
| ea33de | L6 s6001 347b4374 | 9.5 | 3.6 | 0.84 | 5683 | 0.70% | 11 |
| f3e034 | L6 s5401 b8dcfb2d | 6.4 | 2.4 | 0.66 | 5748 | 0.43% | 8 |
| **Earth L7** | | 5.2 | 2.7 | 1.7 | 5878 | | |
| 6b48f5 (2a7385's run) | L7 s11 2865ee1 | 5.7 | 1.6 | 0.41 | 6865 | 0.30% | 8.5 |
| 2b53a0 gallery-stock-3 | L7 s203 deecf8af | 11.0 | 5.3 | 2.91 | 8345 | 2.46% | 9 |
| b92096 gallery 8 plates | L7 s211 deecf8af | 14.0 | 6.8 | 3.01 | 8305 | 1.98% | 8 |
| 85f322 gallery 16 plates | L7 s212 deecf8af | 9.7 | 4.5 | 2.09 | 8293 | 1.97% | 8 |
| a19366 v010-earthlike-a | L7 s11 e55316ad | 10.2 | 3.9 | 1.60 | 6729 | 1.19% | 20 |
| 10fd90 v010-earthlike-b | L7 s12 e55316ad | 13.3 | 6.4 | 2.47 | 8040 | 2.06% | 20 |
| fe954c v010-land-heavy | L7 s14 e55316ad | 11.7 | 6.8 | 3.66 | 8232 | 3.12% | 27 |
| c9f38c v010-cold | L7 s15 e55316ad | 18.3 | 8.6 | 3.65 | 6894 | 2.51% | 17 |
| 5aa5ff v010-hothouse | L7 s16 e55316ad | 5.4 | 1.7 | 0.55 | 6865 | 0.48% | 15 |
| f27dc1 v010-water-world | L7 s13 e55316ad | 13.6 | 3.9 | 0.94 | 5886 | 0.85% | 33 |

Ranges on L7 runs, using the same rule as the Earth table above. a19366 has 15 to 25 regions above 2 km and 7 to 11 above 3 km in most frames after 300 Myr. Its largest single region above 1.5 km is 7 to 17 M km², where Earth's is 5 M km². 6b48f5 at 792 Myr has 9 regions above 2 km and 5 above 3 km.

Per frame, high ground comes in episodes. In cacfc8 (L6 s1), land above 4 km goes 0 → 4.8% (160-200 Myr) → 0 (340-560) → 4.3% (640-680) → ~0.3% (840-960). Each spike follows a burst of active collision zones and decays over about 100-200 Myr. `scout1_hyps.py` prints the per-frame series.

What this rules in and out:

- **The 80 km crust cap (`isostasy.MAX_KM`)** does not limit the area of high ground: crust of 78 km or more is ≤ 0.04% of continent in all but one run (fe954c 0.21%). It does set the single highest cell, though. In every L7 run I checked, the top cell of most frames is at 80 km and stands 1.0-1.4 km above its own Airy height (median over frames; `250 + 150 × (80 - 35)` = 7000 m), with sediment lift and swell making up the difference. These are one-cell spikes of the PW-048/PW-172 family. Raising the cap would add spikes, not ranges.
- **The isostasy constant** (150 m per km beyond 35 km) puts 70 km crust at 5.5 km, which is about Tibet's height on Earth. That is not the limit.
- **Erosion** and crust flow do wear plateaus down over 100-200 Myr after a collision ends (the L6 episodes above). On current-code L7 that still leaves 1.5-2.5× Earth's area above 4 km, so neither is too strong at L7. I did not split the decay between erosion and flow; that needs a checkpoint budget (`sim.book`), which a lane can do.
- **Collision count late in a run (PW-827).** On current code (e55316ad, after PW-565/PW-952 rifting), active zones rise in late frames: a19366 17 → 24, fe954c 20 → 37. The older 6b48f5 has 8.5. Same seed 11, old code against new: land above 4 km is 0.41% (6b48f5) against 1.60% (a19366). That is one pair, and chaos alone could explain it, but it fits "more late collisions, more mountains". **The low relief behind the ticket looks like it came mostly from the old code plus a low moment.**
- **Grid level matters.** L6 has 0.5-1.2% of land above 4 km against L7's 1.6-3.7%, while Earth's share is the same at both levels (1.6/1.7%). Mountain building depends on resolution: the collision belt spreads over `6 × scale²` cells, the crust flow and the hillslope term are per km, and L6 cells halve a belt's peak. L6 runs can't judge this ticket.

## 3. What is actually off (after the presentation issue)

1. **Andes-type ranges are rare.** On Earth, the central Andes are 25% of the land above 3 km at L7 (1.0 of 4.0 M km²), all on an ocean-continent margin. In the runs, 8-10% of the land above 3 km lies within about 250 km of the continental side of a converging ocean-continent plate edge. That's 10fd90 9%, a19366 10%, c9f38c 8%, cacfc8 8%, ea33de 10%. Arc rock is only 1-4% of the land above 3 km. The model thickens a continent at a trench only by arc magmatism (`crust.arc_growth`, under the volume thermostat), less subduction erosion. It has no shortening of the overriding plate. Continent-continent collision is the only process that stacks crust (`plate_kernels.resolve` → `crust.stack_collisions`). On Earth, Andean-type relief needs that kind of shortening behind the arc. No local paper is in `docs/references` for this, so a lane should fetch one before choosing a rate.
2. **The top end overshoots at L7, on craton.** Single cells reach 8-9.5 km in most frames of the current-code runs: 45/61 frames above 7 km in 10fd90, 53/60 in fe954c, 48/60 in 2b53a0. Earth's highest 60 km cell is 5.9 km. Craton rock covers 54-68% of land above 4 km, about in proportion to its share of land (47-62%). A collision stacks crust onto craton but leaves its rock as craton (`flow_and_orogeny`: `rock != CRATON`), so it keeps craton's erodibility, 0.3 against orogen's 0.6. Zooms on 10fd90's world dba204 draw 12 km summits on craton rock. Zoom 7d6c4d has a mean land height of 6249 m and a highest point of 12188 m; zoom f4db12 reaches 11957 m. Earth's 1 km DEM tops out at 8.2 km.
3. **Too much ground between 1 and 3 km at L7.** Land above 1 km is 20-43% in the runs against Earth's 19.7%; above 2 km it is 2-3.5× Earth's share. The sim's uplands are broad plateaus: the largest region above 1.5 km is 7-17 M km², against Earth's 5 M km². This goes against the "too low" framing, so it is worth telling Daniel.

## 4. The one lever I'd try

**Summits from Earth's sub-cell relief, in the world, the highlights and the viewer, not in the run.** Give each high cell a summit height of cell mean + Δ. Fit Δ to the HydroSHEDS table above by cell mean and the cell's slope or landform: about +0.6 km median and +1.7 to 2 km at p90 for cells of 2-5 km. Report the highest summit as "highest peak". Either the texture's ridge amplitude follows the same Δ, or only the summit is carried as a separate value, so that lakes and drainage keep the cell means (PW-057's reason for the small texture). Then a 5.7 km cell reads as a 7 to 8 km peak, as an Earth cell of that mean does. The zoom already builds its own sub-cell relief, but it overshoots (§3.2), so it needs the same Earth table as a check.

Confidence: **high** that the ticket's main complaint is the cell-mean presentation. The Earth-through-`texture()` test leaves little room for doubt. **Medium** that current-code L7 has enough high ground: 7 Earth-like runs agree, but they are 3 code versions and a few seeds each. **Medium-low** on the cause of the Andean gap. The mechanism is missing in the code, but its share of Earth's high ground is one planet's number.

## 5. Why no test runs

The brief allowed 1-3 L6 runs only if the diagnosis pointed to one clear lever. It doesn't point to any tectonic lever toward higher mountains, and L6 can't judge this ticket (§2, grid level). The presentation lever needs no simulation: the Earth check above already exercises it. A shortening run (§3.1) would need a new mechanism, which is a lane's job, not a scout's.

## 6. What a full lane would need

- **Presentation lane** (zoom/highlights; effort m): fit Δ(mean, slope) on HydroSHEDS at L7 and L6, apply it to the highest-peak highlight and the viewer's peak labels, and check it on the Earth world (the highest peak should read about 7.5 to 8.5 km). Judge: Earth through the pipeline, plus the L7 showcases. No runs.
- **Overshoot / craton lane** (tectonics; effort m): judge on L7 only, against Earth L7's hypsometry (> 2 / 3 / 4 km of 5.2 / 2.7 / 1.7%, highest cell 5.9 km), measured as the per-frame median over 3-4 seeds × 1 Gyr at L7 (about 40 min each). Candidates: make stacked craton orogen rock (or reduce thickening on the craton side), and stop single cells at the cap standing above their Airy height. Risk: weathering CO₂ draw-down falls with less high ground (PW-451), so global temperature will move. Check that with the two-tier bar, not the hypsometry seeds.
- **Andean margins lane** (tectonics; effort l): overriding-plate shortening at ocean-continent trenches, at a rate tied to convergence, from a sourced Andes shortening budget. Judge: the share of land above 3 km near ocean-continent margins (Earth 25%), together with the overshoot judge so that total high ground doesn't rise further. Risk: the volume thermostat (PW-1293) reacts, and arc CO₂ outgassing is tied to `arc_nom`.
- **Measurement method** for any lane: per frame, land = elevation > 0; shares above 1/2/3/4 km; frame max; continent > 60 km and ≥ 78 km; collision zones as defined in §2; ranges as connected land above 1.5/2/3 km of at least 50,000 km²; for margins, a 4-cell (L7) or 2-cell (L6) dilation of the continental side of converging ocean-continent edges.
