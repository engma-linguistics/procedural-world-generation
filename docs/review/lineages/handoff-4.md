# Lineages lane 4: handoff (2026-10-23)

Showcase and numbers: `showcase-4.md`. Design notes: `docs/proposals/lineages.md`, section "Lane 4 additions".

## Done
- **PW-613, lean B.** Contact hybrids linger once they have appeared (`History._hybrid`). They fade where their parents no longer meet, and live on as a small people of their own where the parents last met. Tested.
- **PW-614, lean B.** The preset's wish is now "hobgoblin near orc". Goblins keep the jungle wish.
- **Land use.** New module `planet/lineages/land.py`:
  - the world's goods (gameattrs, humanuse fertile and harbour, resources, coastform), worked out in memory when a world lacks them;
  - spec `[[use]]` (trait or place → good, weight) and `meta.land_pull`, in the editor too;
  - `History._land_mult`: normalised to a mean of 1 over the line's country, geology-only before 10 kyr, off in deep time. Tested;
  - a new trait `miner` (dwarves, gnomes).
- **Homeland notes** in each people's story and in `meta.present.homeland`. They name places by the nearest highlight feature, else by directions.
- **Showcase.** New runs 364010, 4e2000, 176619 and 345bb4. Lane 3's 3cf7fe, 2c70d9, 13cf30 and 5cdd4a were deleted, as were the L6 test runs.

## Next
- Inbox:
  - `draft-l7-worlds-have-no-grasses`: a vegetation bug upstream. The L7 worlds have 6 PFTs, so there is no pasture;
  - `draft-lineages-land-pull-strength`: needs a decision on the pull.
- Half-orcs on 3e0b0a never appeared, because their parents never met. A wish or an origin pull for contact hybrids' parents would be the next lever, if wanted.
- Worlds have no place names. The homeland notes would read better with them, through a naming lane.
