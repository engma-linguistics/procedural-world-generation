# Fine zooms write all the layers their parent has (PW-1679, lane 285)

Lane 285, 2026-11-10. Code: `planet/zoom/fine_layers.py` (new), called from `fine.build`; `humanuse.analyse_zoom` gained a `parts`
argument (regional zooms unchanged: all parts). World dba204, section 2a4463 (4,000 km at 2 km/px), the same three spots as lane
284's `lod-rungs.md` (mountain, coast; the river plain was not rebuilt). Every build below is the CLI in a private data root
(`PLANET_DATA` with read-only links to the owner's worlds and section 2a4463), one at a time, `/usr/bin/time -v`, 8 threads asked,
machine load 8-14 (a busy machine: times differ by 10-30% from run to run, see the baseline pair).

## In plain words

A rung (the fine pass: 500 km at 0.5 km, then 30 km at 25 m) used to write 48 layers where its section writes 71. It now writes 73
(the section's 71 plus `floor_m` and `valley_floor`, which only the fine pass makes), so every overlay the viewer offers on a
section is there on a rung: fuel, foraging, grazing, timber, fertile, travel, passes, sightlines, harbours, shore and glacial
forms. A rung costs about 5.6 to 13.6 s more and the same memory: 500 km rung 32.6 s to 46.2 s (10.4 GB both), 30 km rung 37.0 s
to 42.5 s (11.8 to 11.9 GB), on the same machine one after the other, against the 2x ceiling the ticket set. Where a rung meets its
parent, the new layers agree on the average; the largest step is walking time, which reads slower on finer ground (see Seams).

## The 25 layers: what each needs, and how a rung gets it

Inputs are the rung's own finished layers (ground, water, discharge, receivers, climate, plant fractions, soils); nothing new is
asked of the parent except the inherited ones.

| Layers | Needs | Scale-dependent? | On a rung |
|---|---|---|---|
| travel, sightline, grazing, foraging, timber, fuel, building, mud_months, fire_months, green_months, hazards (11, `gameattrs.py`) | plant fractions, canopy, NPP, soils, month-by-month climate, slope (`np.gradient` at the pixel, in m) | no thresholds in pixels; slope is a physical one | **computed at the pixels** |
| fertile, fertile_score (`humanuse`) | soil fertility and depth, moisture, growing months, slope, river distance (km) | the river-irrigation distance is `max(2 res, 2 km)`: already km | **computed at the pixels** |
| river_nav (`humanuse`) | receivers, discharge, ground, frozen months, falls | gradient measured over `NAV_RUN_KM` = 8 km of river (320 hops at 25 m: 6 s at most) | **computed at the pixels**; falls from the rung's own fall list |
| coast_type, nav_hazard, shore_form (`zoom.coast`) | water, wave power, tide, coastal life, rock, world coast classes | windows already in km (`RISE_KM`, `REEF_KM`, `SHOAL_KM`) | **computed at the pixels** (built in memory, not as a second pass) |
| harbour | sea within 3 pixels of land, fetch over `HARBOUR_FETCH_KM` = 50 km, depth within 6 km, river mouths | **yes**: the 3-pixel coast band is 75 m at 25 m; the depth search is 240 hops | **computed on a work grid** of about 0.5 km per pixel (block means of the rung), then each fine sea pixel takes its block's class |
| fresh_water, fresh_km, spring | rivers, lakes, wetland, rain, relief within 12 km, reach classes 3 / 10 / 30 km | **yes**: distances are km but the search iterates in pixels (1,200 px reach at 25 m) | **work grid**, then `fresh_km` is bilinear from it and 0 on a fine pixel that is itself a source; the class is re-cut from the km with the regional thresholds |
| pass, pass_height | drainage basins of 2,000 km2 and 150 km2, saddle 150 m above floors within 20 km | **yes**, and a 30 km window holds no 2,000 km2 basin | window of 100 km or more: **work grid** (0.5 km at the 500 km rung: the regional zoom's own scale), one mark on the fine pixel at the work pixel's centre. Narrower window: **inherited** (below) |
| barrier_island | the section's islands, lagoons and inlets, drawn into its terrain | a property of the coast at the section's scale | **inherited**: nearest parent pixel's class, kept only where the rung's own water agrees (island on land; lagoon and inlet on sea) |
| glacial_form | the section's ice history (troughs, cirques) | a property of the region | **inherited**: nearest parent pixel's class, on land only; present only where the parent has it (like `landform` and `cloud_*`) |
| (pass, small window) | the parent's pass pixels | point features of the parent's scale | **inherited**: each parent pass pixel puts its class and height on the one rung pixel nearest its centre, so a pass is still a mark and not a 2 km square |

No threshold was changed. The work grid is a block mean (water: majority; discharge: block maximum; wetland: majority; receivers:
the block's outlet pixel followed down the pixels' own channel until it leaves the block, `fine_layers.coarse_receiver`), so a rule
written in km reads km at any pixel size. At 0.5 km or coarser the work grid is the rung itself and the code path is the regional
zoom's, unchanged.

Also in the tests' scope: `fine.save` now stores the coast layers with `zoom.coast`'s specs and writes the coast legends and
`coast` block into `zoom.json`, as `coast.add_to_zoom` does for a regional zoom.

## Seams: the rung's edge against its parent

Method (script in the lane's scratch, not committed): each rung pixel is mapped to its parent pixel; over the outer 1 parent pixel
(4 px for the 500 km rung, 20 px for the 30 km rung, "edge") and over everything inside it ("interior"), the rung's mean inside
each parent pixel is compared with the parent's value. Scalars: signed mean and mean absolute difference, max absolute difference,
and the parent's standard deviation over the edge pixels for scale. Classes: share of rung pixels with the parent's class.
Chains: 44d6d6 is the 500 km rung of 2a4463; 01f501 the 30 km rung of 44d6d6 (mountain, centre 35.36, 135.52 then 34.5337, 133.6395);
61b06a and 7aff6b the same for the coast spot (37.93, 126.86 then 37.7917, 127.3750).

### Mountain, 44d6d6 against 2a4463 (parent pixel 2 km, 1,694 edge pixels)

| Layer | Edge: mean / mean abs / max abs | Parent std at the edge | Interior: mean / mean abs |
|---|---|---|---|
| travel (x open ground, 0 to 12.5) | +0.34 / 0.41 / 7.75 | 0.70 | +1.85 / 1.90 |
| sightline (m) | +24 / 335 / 4,957 | 1,720 | +70 / 239 |
| grazing (0 to 5) | +0.02 / 0.30 / 3.1 | 1.20 | -0.04 / 0.25 |
| foraging | -0.01 / 0.21 / 2.2 | 0.84 | -0.03 / 0.25 |
| timber | -0.06 / 0.32 / 3.8 | 1.46 | 0.00 / 0.32 |
| fuel | -0.02 / 0.38 / 4.3 | 1.64 | -0.02 / 0.38 |
| building | -0.24 / 0.39 / 3.3 | 1.03 | -0.51 / 0.73 |
| mud_months | +0.45 / 0.65 / 6.0 | 1.47 | +0.08 / 0.56 |
| fresh_km (km) | +1.49 / 2.97 / 28.4 | 5.57 | -0.58 / 1.29 |
| fertile class equal | 56% (85% either nonzero) | | 50% |
| fresh_water class equal | 71% | | 82% |

### Mountain, 01f501 against 44d6d6 (parent pixel 0.5 km, 336 edge pixels)

| Layer | Edge: mean / mean abs / max abs | Parent std at the edge | Interior: mean / mean abs |
|---|---|---|---|
| travel | +1.58 / 2.01 / 7.19 | 3.68 | +3.28 / 3.48 |
| sightline (m) | +181 / 371 / 4,097 | 1,955 | +104 / 336 |
| grazing | +0.09 / 0.33 / 2.3 | 0.91 | +0.07 / 0.26 |
| foraging | -0.05 / 0.30 / 2.95 | 1.01 | 0.00 / 0.20 |
| timber | -0.24 / 0.36 / 4.1 | 1.27 | -0.09 / 0.24 |
| fuel | -0.17 / 0.42 / 3.6 | 1.46 | -0.04 / 0.34 |
| building | -0.47 / 0.56 / 2.9 | 1.25 | -0.93 / 0.97 |
| mud_months | +0.45 / 0.65 / 3.5 | 1.22 | +0.43 / 0.57 |
| fresh_km | +1.49 / 1.54 / 8.5 | 5.45 | -0.88 / 1.75 |
| fertile class equal | 85% | | 80% |
| fresh_water class equal | 86% | | 80% |

### Coast, 61b06a against 2a4463 (1,728 edge pixels) and 7aff6b against 61b06a (468)

| Layer | 61b06a edge: mean / mean abs | 7aff6b edge: mean / mean abs |
|---|---|---|
| travel | +0.11 / 0.18 | +0.16 / 0.20 |
| grazing | -0.11 / 0.15 | -0.19 / 0.23 |
| timber | +0.01 / 0.11 | -0.01 / 0.02 |
| fuel | +0.02 / 0.11 | +0.17 / 0.20 |
| fresh_km (km) | +1.28 / 2.72 | +0.64 / 0.84 |
| coast_type class equal | 98.9% | 91.0% |
| harbour class equal | 99.9% | 97.2% |
| fresh_water class equal | 79.5% | 97.3% |

All class layers on the barrier, shore-form, nav-hazard and pass lists are 99.7% to 100% equal on the edge (they are 0 almost
everywhere).

Reading it:
- **Means agree.** The signed edge difference of every game layer is within 0.5 of a 0-to-5 scale (9%), fresh_km within 1.5 km
  (parent std 5.5 to 12.7 km), and the mean absolute difference is the detail the finer ground adds below the parent's pixel,
  as in lane 284's height seams.
- **Travel is the one that steps.** Its edge difference is +0.34 and +1.58 (scale 0 to 12.5; parent std 0.70 and 3.68) and +1.85 and
  +3.28 inside: the slope that Tobler's function reads is steeper at 25 m than at 0.5 km on the same mountain. That is
  physical (walking responds to slope over tens of metres), so it was kept; it is filed as a decision (draft
  `draft-fine-travel-slope-scale`). The coast chain, flat country, differs by 0.1 to 0.3.
- **fertile_score numbers are not trustworthy on any zoom**: the layer saturates at a raw 255 (57.4% of section 2a4463's pixels),
  so the fertile *class* comparison above is the one to read. Filed as `draft-zoom-fertile-score-saturates`; the bug is in the
  shared regional path, not in this lane's.
- Max absolute differences (4,100 to 5,000 for sightline, 2 to 8 for travel) are single pixels where a ridge crest or a
  hollow flips the sightline between 0 and the 5 km horizon cap.

## Cost: each rung against the same rung on main

Main = HEAD at the start of the lane (`git archive HEAD` into the scratch), run in its own data root so the two never touched each
other's zooms; each pair ran back to back. The first main run (b1a) compiled numba kernels from a cold cache and is not used.

| Rung | Code | Run | Wall time | Peak RAM | Layers | Time in the new layers |
|---|---|---|---|---|---|---|
| 500 km @ 0.5 km, mountain (44d6d6) | main | b1b | 32.6 s | 10.42 GB | 48 | |
| | this lane | n1 | 46.2 s | 10.41 GB | 73 | 13.6 s |
| 30 km @ 25 m, mountain (01f501) | main | b2 | 37.0 s | 11.84 GB | 48 | |
| | this lane | n2 | 42.5 s | 11.91 GB | 73 | 5.6 s |
| 500 km, coast (61b06a) | this lane | c1 | 40.8 s | 8.20 GB | 73 | not logged |
| 30 km, coast (7aff6b) | this lane | c2 | 37.1 s | 8.03 GB | 73 | not logged |

Lane 284's runs of the same ids (44d6d6 53.2 s / 10.6 GB, 01f501 40.4 s / 11.8 GB, 61b06a 34.3 s / 8.2 GB, 7aff6b 36.1 s / 8.0 GB)
sit inside the same spread as the pairs above, so the cost is +14 s (+42%) at the 500 km rung and +5.5 s (+15%) at the 30 km
rung, memory unchanged. Disk (`du -shL`): 500 km rung 92 MB to 134 MB (44d6d6, main vs this lane), 30 km rung 128 MB to 189 MB (01f501).
The 500 km
rung pays more because everything runs at the pixels on 1 M of them (the work grid is the rung itself at 0.5 km: this is the
regional zoom's own cost for these layers); the 25 m rung runs the slow, hop-based searches on a 60 x 60 grid instead. The run
ids above are scratch (deleted with the lane); the zoom ids 44d6d6, 01f501, 61b06a, 7aff6b are the ones lane 284 named, and are
rebuilt by the commands in `lod-rungs.md` against a copy of dba204's data.

## Tests

`tests/test_zoom_fine.py`: `test_fine_zoom_carries_the_regional_layer_set` (the 24 always-present layers are on a fine zoom, a
fine zoom of it keeps every one, shapes finite, each has a spec to save with), `test_fine_layers_agree_with_the_parent_at_the_seam`
(the outer-parent-pixel means of eight scalar layers within 15% of their range, mean absolute within 30%, on the synthetic fine of
fine chain, which exercises the work grid: 25 m inside 100 m), `test_fine_zoom_inherits_the_parents_regional_forms` (glacial_form,
barrier class, a pass as one mark). `tests/test_fine_layers.py`: the coarse receivers follow the channel; the work factor is in km.

## Left open

- Landform overlays and reef forms are still not redrawn on a rung (lane 284, unchanged).
- Two drafts: the fertile_score encoding and the slope scale of travel (above).
