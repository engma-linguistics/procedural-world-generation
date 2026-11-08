---
id: PW-1149
title: "Owner call: make mainline peoples common through their density and way of life, not a commonness weight"
type: task
status: blocked
parent: null
milestone: later
subsystem: highlights
effort: xs
impact: high
found_by: lane76
blocked_by: [PW-1155]
relates: [PW-917, PW-650, PW-974]
refs: [planet/lineages/samples/dnd.toml, planet/lineages/history/params.py]
created: 2026-10-30
updated: 2026-11-03
---

## In plain words
You asked whether peoples' numbers could come from births and deaths instead of a "how common" weight. Mostly they can't. Births
and deaths decide how fast a people grows and recovers. How many there end up being is set by how many people their land feeds
per square kilometre, and by how much land they hold. Slow-breeding elves and dwarves come out rarer from demography, not
commoner. What can make them common is the density number each people already has in the tree, chosen by way of life. Elves are
set at 1 person per km² against humans' 10.

## Description
Lane 73 measured world 4360a3, seeds 7 and 10. Elves lead ~2–3% of cells but are only ~0.5% of people. Even with the mainline
competition cut at 0.6, dwarves reach 0.6–0.9% and elves 0.3–0.5%. In Lotka-Volterra competition the end state depends on
carrying capacity and competition, not on growth rate. So the density number is the lever.

Options:
- A. Leave densities as they are and accept that elves and dwarves are rare (canon-consistent for long-lived, slow peoples).
- B. Set densities by way of life:
  - elves as forest horticulturalists, 3–5/km² (about ×3 their share);
  - dwarves as mountain farmer-miners, 6–8 (hill dwarves are already 6);
  - gnomes stay at 12;
  - optionally scale by body size (Damuth's rule, density ∝ mass^-0.75, as the giants already use), so small folk such as
    kobolds (25–35 lb, VGtM), halflings and gnomes pack denser.
- C. B plus the mainline flag (lane 73's MAINLINE_Q, now 0) as a stated design dial for what B leaves short.

Lean: B, measured after the portal-arrival and life-history drafts land. C only if B falls short of what you want.

## Updates
- 2026-11-03: Milestones 11-03: v2 -> later: dnd-only owner call; Seven Meals is the December world
- 2026-10-30: Status needs-decision -> blocked. Owner 10-30: niche learning (peoples learn new country) comes first and may supersede the density rethink; revisit after it lands.
- 2026-10-30: Created from inbox draft draft-mainline-peoples-density-rethink.md (found by lane76).
