---
id: PW-1024
title: "Rich temperate plains and lowland woods hold almost no dragons or giants: no kind's niche covers them; open niches should get filled"
type: task
status: done
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: med
found_by: coordinator
blocked_by: []
relates: [PW-990, PW-924]
refs: []
created: 2026-10-29
updated: 2026-10-30
---

## Description
**In plain words.** The richest grazing land in the model, cool-to-mild flat grassland and open woodland (Great Plains or Pontic steppe in Earth terms), has almost no dragons. That isn't because of the peoples: there is no pressure there. No dragon kind's climate niche covers it. Gold dragons need 16-32 C savanna, brass 18-40 C hot dry steppe, green 900 mm+ forest, copper hills, bronze coasts, silver and white cold mountains. A plain at 5-15 C with 400-900 mm of rain falls between them all. Hill giants need hills, so no giant takes it either. Peer review of the dragon paper (10-29): only 16% of rich empty cells hold any dragon, and 91% of the food there is in cells no kind occupies.

Options:
- A. Widen the existing kinds' climate ranges by hand (for example gold or brass down into cooler grassland).
- B. Ecological release: a kind may spread into neighbouring land outside its preferred niche where prey is plentiful and no rival kind holds it, at reduced density. Open niches fill on their own on any world and with any preset.
- C. Add a plains kind of dragon or giant to the presets.
Lean: B, maybe with C as a preset choice. B is the systemic fix and works for owner presets too.

Also check the 25 kyr -> present contraction of dragon range (46% -> 16% of rich empty cells occupied), which looks like a climate-driven range shift; find out why before building B.

## Updates
- 2026-10-30: Status todo -> done. Merged ac0cadae (lane 50): blue/gold/copper widened, tolerates tier, breaks tag, ecological release <=300 km; rich empty land with a dragon 52%->90% over 12 paired runs, per-people pass 67.0->67.8%.
- 2026-10-30: Fun lane 50 built A + B (docs/review/megafauna/open-niches/README.md). In plain words: rich land nobody holds now has dragons in 90% of it (was 52%), gold dragons live on open grassland in every run, and the peoples are unaffected. Diagnosis: the 46% -> 16% fall was mostly the counted set changing (peoples moved into the old one), plus brass habitat drying on the same cells, not range dynamics. The real gap was warm open grassland (Cwa/Cfa), not mainly cool plains. Half of 2a7385's case is a time-zoom rain mismatch (inbox draft). Built: blue (4-40 C, <=800 mm, desert + cold steppe BSk), gold (5-32 C, 400-1500 mm, savanna + open) and copper (5-30 C, hills + new 'breaks' tag) widened; a `tolerates` tier (TOLERATE_K 0.5, a 5 C / 0.5-octave / 1000 m margin) for green, silver, bronze, brass and white; ecological release (megafauna.release: up to 0.3 within 300 km of a kind's own country, prey above the median, no same-sort rival). Paired sweep (6 worlds x 7000-7001, base 29c38f8b): dragons +7%, giants +24%, per-people pass 67.0% -> 67.8%, remnants 44 -> 40. Merge may wait for the dragon-density paper.
- 2026-10-29: Status needs-decision -> todo. Owner 10-29: a mixture of A and B. In plain words: widen some kinds' climate ranges by hand where it suits them (A), and also let open niches fill on their own (B). The owner shared an outside note (another Claude's suggestion, not a sourced reference) on how D&D dragon kinds might fit cool continental plains Strong fits: blue (open dry shortgrass, storm country, lairs in loess bluffs); gold (cool open steppe, roaming over herders' country); copper (badlands, buttes and river breaks cutting through grassland). Accept it at the edges: green (forest-steppe, gallery forest, parkland); silver (lairs in distant mountains, ranging over the steppe); bronze (big rivers, steppe lakes, coasts); brass (hot dry margins, in summer); white (the harsh northern steppe, as winter visitors). Poor fits: red and black. Plan: (A) widen blue's rain/temperature range into dry continental grassland, gold's into cooler steppe, and add broken ground and badlands to copper's places; add a lower-suitability 'tolerates' tier for the edge fits. (B) ecological release for any kind, at reduced density, into neighbouring land no rival kind holds when prey is plentiful. Check the 25 kyr -> present range contraction first.
- 2026-10-29: Created.
