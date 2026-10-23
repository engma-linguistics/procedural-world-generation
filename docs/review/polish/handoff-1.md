# Polish lane: handoff 1 (2026-10-23)

Branch `worktree-agent-ab67a9e26ffa4d792`, on main b26d400. The write-up and numbers are in `polish-1.md`, in
this folder.

## Done
- PW-616: Sn-W by mechanism. Collision-melt (S-type) granites with their roof zones intact, plus melted
  collision belts within an exhumation window. Code: `resources.history()` (coll_thick, granite_myr) and
  `likelihoods()`.
- PW-615: a spatial vote filter over each column's same-plate, same-crust neighbours in `history()`. Isolated
  coal cells are down to 2-4%, and coal's share of land does not grow.
- PW-621: `planet/zoom_shoreforms.py`, called from `zoom_coast.build`.
  - The layer `shore_form`: spits, beach ridges, tidal flats and channels, drowned reefs.
  - Spit features; the spits are raised in the terrain only with `--terrain`.
  - Viewer: a "Shore forms" layer. Test: `tests/test_zoom_shoreforms.py`.
- PW-624: the sea is already masked on the game ramps (nothing to change).

## Not done
- PW-621: cliffs as terrain; channel networks at 1 km. See `draft-shoreforms-followups`.
- PW-624: the by-eye scale review against named Earth places.
- PW-616 follow-up: store the run's exhumation record (`draft-snw-melted-belt-proxy`).

## Scratch store
`/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/polish/store`
holds copies of worlds 1df1c3, afcee8, 1f0505, 3e9e7d, 1144ce, 119973 and 31926a, and their zooms. Several
zooms there now have the new resources and coast layers. The shared store was not written. The server on port
8799 was stopped.
