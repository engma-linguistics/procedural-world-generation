# Peoples on a refined L8 world (PW-1265, lane 266): what it needs, first path, where it stopped

## What `planet lineages` needs from the grid
- `recent.resolve(ref)`: a world finished from a glacial time zoom (meta `timezoom`, `timezoom_kyr`). A keyframe world
  (e.g. 783674, the source of the old refine fb5e11) cannot host peoples at all; so the L8 try refines a time-zoom world:
  899985 (Earth-like A, time zoom fc5311, L7 dnd try 0141d1). `planet refine` keeps the `timezoom` meta.
- `recent.Pass` built its grid from the time zoom's level (7) and read the world's layers (goods, flow, NPP, sites) on it:
  an L8 world's layers (655,362 cells) against an L7 grid (163,842) cannot work.
- The deep history (`history/steps.py`) reads the source run's keyframes (L7); the recent pass reads the time zoom's
  frames (L7) and runs ~15 full climates on the zoom's grid. Everything after the history (settlements, polities, demes,
  cultures, gods, brief) reads the peoples run's own saved frames and `meta.level`, so it follows the history's grid.

## Smallest sound path (this lane, code in recent.py / steps.py)
When the world is finer than its time zoom, the Pass runs on the world's grid and every L7 frame field is prolonged to it
(`recent.finer`: nest.step's two-parent mean; first parent for the climate class). The full climates stay on the zoom's
L7 grid (as `planet refine` does with `climate_level=7`) and only their rain is prolonged. At equal levels nothing changes.
This runs the whole history on L8, not the agreed split (deep on L7, settled window on L8): the split needs the History
state (per-people presence, K, learned country, demes, live polities and tech) regridded at the cut, which is not built.
Known cost of the shortcut: the deep dispersal advances a ring per hop, so its fronts move half as fast in km on L8
(draft-settled-window-grid-rings.md); coasts of the prolonged frames are the L7 ones while the world's layers are refined.

## Where it stopped (lane 266 hand-off at ~100 tool calls)
- Refine of 899985 to L8 in a scratch root: world 5d09cc, 6 min 28 s, peak 11.9 GB (scratchpad l266/root).
- L8 try (`planet lineages 5d09cc --tree dnd --tries 1`) and an L7 baseline on the same code (899985) were started and
  stopped in their first stage (the recent pass's full climates): no timing or map yet.
- The map script (lead people per land cell, towns and cities) works on 0141d1; it lives in the lane's scratch
  (`side.py`). Next: rerun both tries (expect L7 ~20 min of history for 0141d1's 1,233 s, L8 several times that) and
  draw the pair here.
