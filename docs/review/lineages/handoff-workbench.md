# Handoff: peoples workbench lane (PW-650), 2026-10-24

Branch `worktree-agent-a7e2c1259d4f34bcf`, based on main 139296c. The design and the numbers are in
docs/proposals/lineages.md ("Workbench lane" and "Next: groups within a people") and in the PW-650 update.

## Done
- **Demography knobs per people** (spec.DEMOGRAPHY; defaults from traits):
  - `density` / `band_km2`: numbers, a viable population per patch (`meta.viable_pop`), and a mild density push;
  - `explore`: marginal land, long crossings;
  - `sea_share`: boats via spec.BOATS, short hops;
  - `insularity`: mixing, leaving home.
- **Folded in:**
  - the `seafaring` trait's `late_sea` knob became the sea share;
  - the `insular` / `cosmopolitan` `mix` knobs became insularity;
  - `speed_kmyr` is the expansion rate (alias `expansion_kmyr`).
- **Outputs:** populations (per people, landmass, frame); per landmass `discovered`, `settled_by`, `arrivals`, `population`; `meta.present.ascii`.
- **Workbench page:** `viewer/lineages.html`, five tabs. The per-people side panel shows only that people's wishes (owner bug note); the Wishes tab has a people filter. `?sel=<id>` opens a line.
- **Preset:** giants sparse and insular, pull 0.7 not strict (PW-655 → option C); the rest per the owner.
- **Runs kept:** 37e9da (1df1c3), 33b1c3 (3e9e7d). Deleted: 50fe0f, 676ab1, 9fc91a, c7f2d9, ff42c4.
- **No server change.** The 8791 test server is stopped.

## Open
- Groups within a people (owner, 2026-10-24): designed only; draft-peoples-groups.
- draft-peoples-density-push (needs-decision); draft-peoples-fire-giants-refuge.
- Seed variance is large: halflings ranged 1–10 Mkm² between try seeds before and after the lane. Compare like with like (same try seed) when tuning.
- The workbench's per-people wish list is read-only. It links to the filtered Wishes tab for editing.
