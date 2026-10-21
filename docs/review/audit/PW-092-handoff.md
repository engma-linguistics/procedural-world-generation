# PW-092 handoff: glacial landforms in the regional zoom (2026-10-21, agent pw092)

**Outcome:** regional zooms draw glacial landscapes from the finished world's imprint (`glacial_erosion`,
`glacial_till`, `ice_max`). 521 tests pass, no golden changed (worlds without an imprint get no glacial class).

## What was built
- `planet/zoom_glacial.py`: `Glaciated`, a `Synth` of `zoom_landforms` (class id `GLACIATED` = 20, registered at the
  bottom of zoom_landforms, which must be imported first). Its cells are the iced cells plus a ring (`Synth.select`).
  Hooks: `shape` (troughs, cirques, moraines, outwash, loess), `basins`/`lakes` (overdeepened troughs and moraine
  zone), `drown` (fjords), `overlay` (drumlins, kettles). See the module docstring and overview 11b.
- zoom_landforms: `Synth.select`/`cls`/`drown`, `Ctx.rec/order/q` (the remap's drainage), `Landforms.drown`/`glacial`,
  `glacial_layers()`, `ice_flow` derived per cell (surface slope of elevation + ice_max); the world needs no
  `landform` layer any more.
- zoom.py: `keep_` (closed basins kept) is computed after the remap; fjord drowning right after the landform pass
  (updates land/sea/active/outlet); layers `glacial_form`, `loess`; stats `glacial`.
- finish.py: `earth_rock` (moved from tools/earth_world.py): finished Earth worlds had no rock record, so no zoom could be made.
- tests/test_zoom_glacial.py.

## Showcase (store; world 577526 = f6e955 re-finished, same time zoom e9d59c at 420 kyr; f6e955 deleted)
Seed 1, 1000 km at 2 km/px unless noted.
| zoom | where | numbers |
|---|---|---|
| 66c45e | Norway 62N 7E | 14 fjords, mean 361 m / max 835 m deep, 3,640 km2 of fjord; trough floors lowered 244 m (p90) over 5,384 km of trunk; 80 trough lakes; 662 cirques; 96,000 km2 drumlin country |
| 0de6eb | Norway 61N 7E, 500 km at 1 km/px | 11 fjords (max 843 m), 51 trough lakes, 492 cirques |
| 4f65aa | Ungava (Canadian Shield) 62N 70W | 14 fjords (max 201 m), 33 lakes, 537 cirques, 82,000 km2 drumlins |
| 21703a | Baltic margin 57.5N 13E | 4 moraine belts, 5,964 km2 outwash, 23,376 km2 loess (max 12 m), 25 fjords, 75 trough lakes |
| b03a2b | Alps 46.5N 10E | nothing: parent erosion ~1 m |
| bf3c88 | Patagonia 47S 73W | 1 moraine belt, 1,500 km2 outwash, 4,800 km2 loess; no troughs (parent 4 m) |
The Canadian Shield around Hudson Bay is never iced in this time zoom (PW-033), hence Ungava. Cell means: Norway
inland bias -5.5 m, RMS 17.6 m (1 km zoom -8.4 / 20.6).

## Gaps (drafts in the inbox)
moraine-dammed lakes (0), fine zooms and Alps/Patagonia, trough calibration, Earth geology. PW-499 (flow
direction, wet_kyr) stands: the flow here is the slope of the thickest ice's surface.
