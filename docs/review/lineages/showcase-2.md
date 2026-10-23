# Lineages showcase 2: the dnd preset on four L7 worlds (lane 2, 2026-10-23)

Code at commit 0db5f2e (lane 2). Each world ran `planet lineages <world> --tree dnd --tries 2`, taking 130-190 s a try at L7. The screenshots show the globe at the present on the `peoples` layer, with the "Peoples' origins and tracks" overlay: rings mark origins, lines are centroid tracks.

| world | run | wish score | mixing (land share; corridors / closed) | empty continents | screenshot |
|---|---|---|---|---|---|
| 1144ce | 037790 | 0.64 | 36 Mkm² (22%; 42% / 16%) | none (the 36 Mkm² polar continent is 16% held) | showcase2_1144ce.png, showcase2_1144ce_overlay.png |
| 31926a | 06a854 | 0.56 | 28 Mkm² (17%; 31% / 11%) | none | showcase2_31926a.png |
| 91448a | 2dcc80 | 0.59 | 16 Mkm² (12%; 25% / 10%) | 25°S 111°W (5.3 Mkm²; humans landed 300 years ago, 3% held) | showcase2_91448a.png, showcase2_91448a_mix.png |
| 3e0b0a | dfcbd2 | 0.58 | 24 Mkm² (18%; 36% / 15%) | 52°N 145°W (40 Mkm², 4%: aarakocra only), 4°N 29°W (5.3 Mkm²) | showcase2_3e0b0a.png |

Wish scores:

| wish | 1144ce | 31926a | 91448a | 3e0b0a |
|---|---|---|---|---|
| aarakocra on islands | 0.89 | 0.66 | 0.55 | 0.96 |
| tortles on islands | 0.69 | 0.64 | 0.99 | 0.10 |
| goblins in jungle | 0.63 | 0.65 | 0.54 | 0.71 |
| orcs on steppe | 0.76 | 0.63 | 0.62 | 0.69 |
| halfling near human | 1.0 | 1.0 | 1.0 | 1.0 |
| hobgoblin near goblin | 0.09-0.36 | 0.09-0.36 | 0.09-0.36 | 0.09-0.36 |
| goblin near orc | 0.0 | 0.0 | 0.0 | 0.0 |

"Goblin near orc" fails everywhere: rainforest goblins and steppe orcs now hold distinct ranges. See inbox `draft-lineages-near-wishes-after-exclusion`. No lines were lost on any world.

## How plausible it looks
- **1144ce**: the best of the four.
  - Humans arose on the 52 Mkm² southern continent ~150 kyr ago. They sailed ~4.8 kyr ago to the 77 Mkm² continent (963 km of open sea) and to the 6.6 Mkm² one, and island-hopped.
  - Tortles swam 361 km to islands at 900 kyr and live scattered over 18 coastal patches.
  - Aarakocra have 13 patches including the island chain at 16-24°N 60°W.
  - The main mixing zone (26.6 Mkm², hobgoblins + humans + elves) sits on the southern continent's lowlands. The rest is lizardfolk/tortle/dragonborn coast near 6°S 152°E. The polar continent is mostly empty: it is cold.
- **31926a**: one supercontinent (170 Mkm²), only half held: its interior is too cold or dry for most of the preset.
  - The single large mixing zone (23 Mkm², 5 peoples) is the tropical west-coast lowland where most lines arose (origins within ~30° of each other). It reads as a crowded cradle rather than corridors, because the origins cluster there. A preset with wider niches would spread them.
  - Humans sailed 1745 km to the 6.9 Mkm² southern continent 2.6 kyr ago, a Polynesian-scale late voyage.
- **91448a**: distinct ranges, the clearest isolation.
  - Mixing covers only 12% of the land, mostly the human-halfling farmland at 26°N 10°W, which the preset asks for.
  - Aarakocra flew 2166 km to a 6.9 Mkm² continent 400 kyr ago and hold 78 patches. Tortles score 0.99 on islands.
  - Bugbears (cold forest, hardy) hold 48 Mkm², too much. That is the preset's niche, not the mechanism.
- **3e0b0a**: shows the crossings' honest limit.
  - The 40 Mkm² northern continent is only reached by aarakocra (overland at a low stand ~250 kyr ago, then confined to its coasts). Humans only sailed to one island, 1.5 kyr ago.
  - Tortles (0.38 Mkm², 3 patches) are boxed in by lizardfolk on the coast of their origin and score 0.10 on islands.
  - Plausible as a world with a "new world" still to be settled. Whether the owner wants that is the empty-continents draft.

## General
- Peoples now hold separate countries with mixing in the coastal and river lowlands. Lane 1 had mixed 38-45% of the land.
- Every people's story reads as game text (`run.txt` "Stories", and the panel when one is picked). Example (1144ce, humans): "Humans split from the hominid stem ~150 kyr ago in an isolated part of its parent's land, on the continent at 26°S 22°W (52 Mkm²). ~4.8 kyr ago it sailed to the continent at 17°S 174°E (77 Mkm²) over 963 km of open sea..."
- Rough edges:
  - "(inside the parent's range)" wording.
  - The stories list arrivals on tiny islands.
  - The many-patch counts come from the 25% presence fragments at L7.
