# v2 fun-polish lane 1 (2026-10-23): tin belts, coal speckle, zoom shore forms, game-layer sea

Tested on copies in a scratch store (`PLANET_DATA=.../scratchpad/polish/store`); the shared store was only read.
The `simulate`, climate, ocean, ice and tectonics outputs are unchanged. So are the world and zoom goldens and
the existing zoom layers. Full `pytest` passes.

## PW-616: Sn-W by mechanism (`planet/resources.py`)

Before: every exhumed granite cell got 0.55 (x1.4 where crust was once > 50 km), and every exhumed thick
orogen got up to 0.8. The new rule:
- **History** (two new per-cell records in `history()`):
  - `coll_thick`: the thickest crust the traced ground sat on while it was in a collision setting (fold-belt
    landform or orogen basement);
  - `granite_myr`: how long the ground has been granite at the surface without a break, up to now.
- **Tin granites**: granite x (0.04 + 0.86 x S-type) x (0.3 + 0.7 x roof).
  - S-type = ramp(coll_thick, 52, 62 km) x reduced source (1.0 within 2 cells of metasedimentary basement:
    orogen or sediment rock; else 0.6).
  - roof = exp(-granite_myr / 150 Myr): the greisens and cupolas are stripped within ~100-200 Myr of
    unroofing.
  - Arc (I-type) granites with no collision thickening get 0.04, since they carry porphyry Cu instead.
- **Melted collision belts** (the rock layer names their basement, not their plutons): orogen x exposed x
  S-type x window x incubation x 0.4.
  - window: the crust lost since its peak (~ exhumation) is 3-8 km (rising) to 12-20 km (falling); still
    0.25 under an intact plateau.
  - incubation = ramp(peak age, 5, 20 Myr): a thickened root takes 10-30 Myr to heat up to melting (England &
    Thompson 1984).
- The Earth fallback (no history) uses today's collision belts and crust, with the roof at 0.6.

| world | granite cells | sn_w >= 0.5: granite share | land % >= 0.5, before -> after | notable deposits world-wide (sum -ln(1-p)), before -> after |
|---|---|---|---|---|
| 1144ce L7 | 534 | 8% | 4.21 -> 0.06 | 3693 -> 272 |
| 119973 L6 | 151 | 23% | 3.99 -> 0.24 | 798 -> 103 |
| 81aced L6 | 172 | 12% | 5.18 -> 0.15 | 1092 -> 71 |
| 91448a L7 | 465 | 6% | 4.70 -> 0.05 | 4170 -> 158 |

Zooms (all deposits, small ones included):
- 72857c (1144ce): 286 -> 0. Its ground is a 67 km thick plateau that is still thickening, so its melts are
  still deep: lost 0 km, peak age ~0.
- 439e2a (31926a): 331 -> 105, about 30 of them notable. This one is a real melted belt: 80 -> 67 km, 24 Myr
  after its peak.

Placer tin follows, since it is computed from sn_w. Map: `sn_w_1144ce_before_after.png` and
`sn_w_119973_before_after.png` (top before, bottom after). Tin now sits in a few belts, not on every granite.

## PW-615: the coal speckle's spatial half (`planet/resources.py`)

After the column is rebuilt, `history()` filters the column summaries over each cell's neighbours on the
same present plate and crust (a plate boundary or a coast is a real edge). The filter is a per-lithology
vote: a cell keeps a unit (> 0.02 km) where most of its same-ground neighbourhood holds it. That removes lone
cells and fills lone gaps without spreading the unit's edge. A kept value moves halfway to the holders' mean,
and a filled gap takes that mean. Depths and burials follow the unit's own km. Oil, gas and salt use the same
filtered column.

Two alternatives were tried and dropped:
- A plain neighbour mean grew coal by 8-34%: thin seams spread over the 0.5 line.
- A median shrank coal by 45-52%: coal is often held by only 3 of 7 neighbours.

| world | coal land % >= 0.5, before -> after | isolated coal cells | patches |
|---|---|---|---|
| 1144ce L7 | 3.71 -> 3.41 | 17% -> 4% | 615 -> 187 |
| 119973 L6 | 2.69 -> 2.31 | 24% -> 2% | 137 -> 31 |
| 81aced L6 | 4.74 -> 4.44 | 17% -> 3% | 182 -> 54 |
| 91448a L7 | 1.34 -> 0.91 | 22% -> 3% | 392 -> 75 |

Oil, gas and salt also moved: on 1144ce oil went 1.37 -> 1.02, gas 1.49 -> 1.15 and salt 1.63 -> 1.59; on
119973 oil went 1.65 -> 1.26, gas 2.65 -> 2.26 and salt 0.36 -> 0.26. Map: `coal_1144ce_before_after.png`
and `coal_119973_before_after.png`. The history pass got no slower: 6-8 s at L7, 1.5 s at L6.

## PW-621: zoom shore forms (`planet/zoom_shoreforms.py`, called by `zoom_coast.build`)

`planet coast zoom:<id>` now also writes a `shore_form` layer and adds spit features to `coast.features`.
Nothing that existed changes, and the terrain changes only with `--terrain`, which raises the spits like the
barrier islands. The legend is `shore_form`, and the viewer has a "Shore forms" layer and a hover row. The cost
is about 0.2-0.5 s per zoom.
- **Longshore drift** (CERC: Q ~ P sin 2θ). The zoom stores no wave direction, so the waves run with the
  world's annual wind at the pixel's cell. The shore normal comes from a smoothed land mask (4 km). Offshore
  winds move nothing.
- **Sand supply**: river mouths (sqrt Q) plus retreating soft bluffs (rise >= 15 m on rock that is not hard,
  x waves), summed over 30 km up the drift.
- **Spits** grow from shore pixels where the coast falls away ahead along the drift: a headland's lee, a bay
  or estuary mouth.
  - They run over water shallower than 20 m, 6 km x sqrt(supply) long (at most 40 km).
  - The last quarter is bent up to 70° landward (a recurved hook).
  - They stand >= 20 km apart, the best drift x supply first.
  - Each feature carries its length, drift bearing and kW/m.
- **Beach-ridge plains**: low land (< 8 m) behind beach shores near a big sand supply, 3 km x sqrt(supply)
  wide.
- **Tidal flats and channels** form on tide-dominated shores: tide >= 2 m and >= 2 x Hs (Davis & Hayes 1984).
  - The flat runs out over floor shallower than 25 m, 2 km per m of tide.
  - The marsh behind it is the land below half the range.
  - The channels are the flat's own D8 drainage, where >= 40 km² drains through.
- **Drowned reefs**: in reef waters (the coldest month's SST >= 18 °C), the first pixels deeper than the
  time zoom's lowstand drop (`meta.sea_level_change_m`), seaward of floor shallower than it.

| zoom | spits (km) | beach ridges km² | tidal flats / channels km² | drowned reefs km² (lowstand) |
|---|---|---|---|---|
| 9d7c44 (119973, 500 km) | 10 (99) | 297 | 0 / 0 | 614 (35 m) |
| 368c45 (1df1c3, 1000 km) | 20 (160) | 1540 | 84 / 0 | 1100 (119 m) |
| bc40a3 (3e9e7d, 1000 km) | 9 (68) | 484 | 17100 / 1532 | 1852 (23 m) |
| 3a852a (1f0505, 1000 km) | 2 (6) | 128 | 0 / 0 | 1836 (42 m) |

On 9d7c44 (10°N, trade winds) the spits all point west, downwind of the easterlies, from the headlands' lee.
Images (relief, shore forms on top: yellow spits, tan ridges, grey flats, blue channels, magenta drowned reefs):
- `zoom_9d7c44_spits.png`
- `zoom_368c45_ridges_spits_reefs.png`
- `zoom_bc40a3_tidal_flats_reefs.png`
- `viewer_9d7c44_shore_forms.png` (the viewer layer and its legend)

Limits (inbox draft `draft-shoreforms-followups`):
- At 2 km/px the flats are a 2-4 px fringe and the channels are short stubs. Dendritic networks need 1 km or
  fine zooms, and the near-shore bathymetry is too coarse.
- The wave direction is the wind's; swell from distant storms would need `coast.py`'s rays to keep their
  direction.
- Drowned reefs use the single lowstand in `meta.sea_level_change_m`, not the time zoom's full curve.
- Cliffs as terrain and raised reef terraces are not built.

## PW-624: the quick items

- **Sea on the zoom's game ramps**: already masked. zoom.html's `RAMPS` branch draws every sea pixel with the
  sea's depth ramp (`if (wet === 1) ...`, since ca5fafc on 2026-10-15), and travel and sightline are RAMPS
  layers. `viewer_368c45_travel_sea_masked.png` shows the travel layer with a depth-shaded sea. Nothing to
  change. The ticket's checkbox can be ticked by the coordinator.
- **The by-eye scale review against named Earth places** was not done in this lane (not cheap: it needs the
  Earth world's game layers sampled at named places). It stays on the ticket.
