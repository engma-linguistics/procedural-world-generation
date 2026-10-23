# Lineages showcase 3: faster history, near wishes that hold (lane 3, 2026-10-23)

This uses the code at lane 3's head. Each world ran `planet lineages <world> --tree dnd --tries 2`. The screenshots show the flat map at the present on the `peoples` layer, with origins and tracks. Lane 2's showcase runs (037790, 06a854, 2dcc80, dfcbd2) were deleted. Their screenshots stay in `showcase-2.md`.

| world | run | wish score | mixing (land share; corridors / closed) | lost | empty continents | screenshot |
|---|---|---|---|---|---|---|
| 1144ce | 3cf7fe | 0.73 (lane 2: 0.64) | 35 Mkm² (21%; 42% / 17%) | half-elves | none | showcase3_1144ce.png, showcase3_1144ce_mix.png |
| 31926a | 2c70d9 | 0.56 (0.56) | 21 Mkm² (12%; 29% / 6%) | none | 43°S 172°E (6.9 Mkm²) | showcase3_31926a.png |
| 91448a | 13cf30 | 0.73 (0.59) | 17 Mkm² (12%; 22% / 12%) | none | 25°S 111°W (5.3 Mkm²) | showcase3_91448a.png |
| 3e0b0a | 5cdd4a | 0.62 (0.58) | 15 Mkm² (11%; 21% / 11%) | half-orcs | 40°S 69°W (27 Mkm²), 4°N 29°W (5.3 Mkm²) | showcase3_3e0b0a.png |

## Speed
On 1144ce (L7, one try), old and new code ran side by side on the same loaded machine: **265 s → 63 s**. Lane 2 measured 130–190 s a try. With 5 runs in parallel, a try now takes ~60 s at L7 and ~16 s at L6 (119973). The stored frame layers and the events are identical. In the final presence, 234 cells differ by at most 2e-16, from summation order. Where the time went, and the fixes:
- **The spread, 66 s → 11 s.** It now visits only the front: the neighbours of the cells that changed in the pass before. It used to sweep all 164k cells every pass. A test checks that it equals the full sweep.
- **Competition.** It is summed in numba over a line's rivals only, and only on the cells where the line can hold ground (K ≥ EST). The room anywhere else is never used.
- **Habitat.** It is worked out on the land cells only.
- **Neighbour reductions.** `ufunc.at` is replaced by `reduceat`, because `nbr_src` is sorted.
- **Island chains.** They are tagged only when a wish or a line names them.

What still costs time: the spread ~11 s, habitat ~10 s, frames ~6 s, crossings ~5 s and tags ~5 s. The rest is per-line array work over the full grid.

## Near wishes (PW-604)
How a "near" wish works now:
- **Habitat pull.** The wish pulls the habitat toward the other people's border, ×(1 + 0.5 w) just outside its range, e-folding over 300 km. It does not pull into that range: before, the wish doubled a's habitat inside b's range. Under lane 2's exclusion, that let the wisher displace the other.
- **Origin pull.** Whichever of the two arises second is pulled toward the other: ×(1 + 2 w), e-folding over 1000 km. Before, this pull reached one cell ring.
- **Tolerance.** The two compete half as hard with each other, so they can share a border without one excluding the other.
- **Score.** The share of a's range within 330 km of b. That is 3 cells at L6, as before. It used to be 3 cells at any level, which at L7 meant only 165 km.

Best of 2 tries, before (lane 2's mechanism, same seeds) → after:

| wish | 1144ce | 31926a | 91448a | 3e0b0a | 119973 (L6) |
|---|---|---|---|---|---|
| goblin near orc | 0.00 → 0.11 | 0.00 → 0.00 | 0.00 → 0.19 | 0.00 → 0.70 | 0.00 → 1.00 |
| hobgoblin near goblin | 0.33 → 1.00 | 0.14 → 0.26 | 0.09 → 1.00 | 0.36 → 0.54 | 0.05 → 0.96 |
| halfling near human | 1.00 → 1.00 | 1.00 → 1.00 | 1.00 → 1.00 | 1.00 → 1.00 | 1.00 → 1.00 |
| aarakocra on islands | 0.89 → 0.90 | 0.66 → 0.53 | 0.55 → 0.43 | 0.96 → 0.90 | 0.85 → 0.85 |
| tortles on islands | 0.69 → 0.72 | 0.64 → 0.64 | 0.99 → 0.99 | 0.10 → 0.44 | 0.00 → 0.00 |
| lizardfolk apart from tortles | 0.69 → 0.54 | 0.74 → 0.64 | 0.74 → 0.75 | 0.73 → 0.39 | 0.85 → 0.85 |
| lizardfolk apart from aarakocra | 1.00 → 1.00 | 0.81 → 1.00 | 1.00 → 1.00 | 1.00 → 0.94 | 0.96 → 0.96 |
| goblins in jungle | 0.62 → 0.70 | 0.65 → 0.61 | 0.54 → 0.56 | 0.71 → 0.00 | 0.00 → 0.00 |
| orcs on steppe | 0.76 → 0.66 | 0.63 → 0.63 | 0.62 → 0.62 | 0.69 → 0.34 | 0.85 → 0.83 |
| **overall** | 0.64 → 0.73 | 0.56 → 0.56 | 0.59 → 0.73 | 0.58 → 0.62 | 0.49 → 0.74 |
| goblin area (Mkm²) | 2.4 → 4.0 | 2.7 → 2.0 | 0.4 → 0.5 | 1.1 → 0.2 | 0.3 → 4.3 |
| mixing, land share | 22% → 21% | 17% → 12% | 12% → 12% | 18% → 11% | 25% → 21% |

On 119973, goblins went from a 0.3 Mkm² remnant to 4.3 Mkm² bordering orcs, hobgoblins and humans. Both near wishes are met there.

### What the wish can't do
"Goblin near orc" stays low on three of the four L7 worlds:
- The goblins' origin now lands next to the orcs. On 3e0b0a both arise within ~400 km of each other, and on 1144ce ~2000 km apart instead of across the continent.
- But the preset's rainforest goblins (18–30 °C, ≥ 1200 mm) and cold-steppe orcs (2–20 °C, ≤ 900 mm) have no shared country. Over 400 kyr the ranges drift apart to their own climates, and savanna peoples (hobgoblins, humans, tabaxi) fill the land between.
- On 3e0b0a the pull held the goblins at the orcs' side (0.70), but in a small non-jungle pocket (0.2 Mkm², jungle wish 0.0). That is the trade-off of one wish against another.

Hobgoblins are savanna people, and savanna does touch steppe, so "hobgoblin near orc" would be met by geography. See the inbox draft `draft-lineages-goblin-orc-niches`.

## Corridors (PW-602)
Exposed continental shelf at a glacial low stand (land then, sea now) is now a 0.7 contact corridor in glacial and recent epochs: the flat coastal plains of Doggerland, Beringia and Sunda. The present-day river field has no rivers there. This acts only in the past, so mixing at the present barely moves. The values for plains (0.5) and rivers (0.9) are unchanged: the maps give no clear reason to change them, and it stays the owner's call.

## How it looks
- **1144ce** (showcase3_1144ce.png). The southern continent is a patchwork: hobgoblins, humans, tabaxi, goblins and halflings, with orcs and halflings in the far south. Goblins (4.0 Mkm²) sit in the central lowland between hobgoblins and humans. The orcs are on the southern steppe, ~1500 km off. Dragonborn hold the arid east and northeast (62 Mkm²). The half-elves are lost because humans and elves no longer meet at the present in either try.
- **31926a**. One crowded tropical cradle (19 Mkm², 6 peoples), as in lane 2. Goblins live with lizardfolk and tabaxi in the coastal jungle. The few orcs (2.2 Mkm²) are far south.
- **91448a**. Hobgoblins border the goblin jungle (1.00). The human-halfling farmland at 26°N 10°W is the main mixing zone.
- **3e0b0a**. Goblins, hobgoblins, bugbears and orcs share one southern upland near 10°S 107°E: goblin-orc 0.70. The 40°S 69°W continent (27 Mkm²) is empty in this run, and the half-orcs are lost.

## Rough edges
- Contact hybrids (half-elf, half-orc) can be lost when their parents' ranges stop touching. Best of N now prefers a try that keeps every living line (−0.05 per line lost), but here both tries lost the same one. See the inbox draft `draft-lineages-contact-hybrids-lost`.
