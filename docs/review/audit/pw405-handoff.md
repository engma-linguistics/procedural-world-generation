# PW-405 handoff: fine-zoom river planform

Status: implemented and committed on branch `worktree-agent-a77223c7eaa43cc01`. Tests pass (`uv run pytest -q`). Not merged.

## What changed (planet/zoom_fine.py)
- `_courses`: builds each parent river course, main stem by main stem.
  - Smoothing: SMOOTH_PX = 1 parent px. This removes the D8 steps that caused the switchbacks.
  - Wander: WANDER_PX = 0.15 parent px, at about 4 parent px.
  - Each reach is classed as alluvial single-thread, braided or bedrock.
  - Alluvial single-thread reaches get a sine-generated meander train (MEANDER_WL = 11 w, MEANDER_OMEGA = 1.2 rad).
  - The meander swing is limited by the valley floor's half width and the valley's bend over one wavelength.
  - Meanders are drawn only where this zoom resolves them (MEANDER_PX 15-24 px) and a fine parent did not.
  - Tributaries end on their main river's drawn course.
- `_river_phase`: the meander phase, run down the whole parent network so that sibling zooms agree.
- The noise warp of the courses is gone. The categorical warp stays.
- Inflow: water that already passed through the built area is now subtracted by discharge. The old yes/no check lost a whole river once the parent box grew from +-2 to +-5 px.
- `planform()`: the switchback / sinuosity metric. Its output is in stats as `river_planform` (with `classes_km` and `switchback_px`).

## Pitfalls found on the way
- Never Gaussian-smooth the cumulative phase across a jump in Q: it winds the phase into a comb. Now:
  - the phase increments are evened per link;
  - no meanders across a link whose wavelength jumps (`lam_lo`);
  - the swing is never smoothed into a reach that doesn't allow it.
- The parent's `bed_p` sits a few m below its ground at the end of long courses (1 cm/link minimum fall). Valley floors are therefore measured from the ground at the course, not from the bed.

## Verification (scratch, not in repo)
`/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/pw405/`:
- `store_before` and `store_after`: regenerated showcase fine zooms plus lowland test zooms.
- `metrics.txt`: before/after metric table.
- `img/*_{before,after}_{overview,detail}.png`: plan-view images.
- Scripts: `regen.py`, `cmp.py`, `render405.py`.

## Next
Inbox drafts, all to be numbered by the coordinator:
- floodplains in the fine pass (the main limit on lowland meanders now);
- braided threads;
- small D8 streams.

PW-395, PW-404, PW-391 and PW-392 come after this. PW-391 (inflow) touches the same q_in block.
