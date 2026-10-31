# The dragon food chain after the dragon-density paper's revisions (lane 90)

## In plain words

The dragon-density paper (docs/review/megafauna/dragon-density/) checked how the model works out how many dragons a world can feed,
and listed what was unsourced or wrong. The owner ruled on each point. This lane put those rulings into the code. Each step now has a
source with a page number, or is marked as a judgement.

The result is fewer dragons: about a fifth as many on a world today. A Sword Coast-sized region (3.9 million km²) holds about 120
dragons at the land's average density, down from about 460. Two changes do most of it:

- **Herds are fed only the plants that grow above ground.** The herd formula was fitted on above-ground growth, but it was being fed
  the whole plant, roots included. In dry and cold country most growth is roots, so the herds there shrink five- to sevenfold.
- **Each dragon now eats what a dinosaur-like animal of its size would.** Counting the bones it leaves and the food it cannot digest,
  a dragon needs about twice as much prey as before.

Some changes push the other way. Young dragons now eat inside the smaller predators' share. When people kill the wolves and leopards,
the dragons get the food those predators leave. Viability, persecution and the deep past were also reworked.

The dragon kinds now live where the DMG puts them. Red dragons are in hills and mountains, blue on coasts and in deserts, green in
forests, gold on grasslands, white in the arctic, silver on mountains. Each kind hunts up to about 170 km out of its own country.

One thing needs the owner. White, silver and bronze dragons live on cold, poor land, where the new herd numbers leave almost nothing to
eat. They are now very rare: a few dozen white dragons on a world, and none on one world. The owner asked for "fewer where it is
poor", and this is far fewer. The inbox draft "cold dragons thin after the above-ground prey" lays out the options. The lean is to give
the coast and ice dragons a sea food (seals, fish), which the model does not count at all yet.

The peoples are untouched. The dnd peoples' land shares on seeds 7, 10 and 13 move only within run-to-run noise.

## What changed, ruling by ruling

The effects are against round 3 of the paper, at a given place. They are factors on the dragons the food feeds, from the paper's own
`sensitivity.py`, which reads the revised chain.

| # | Ruling (owner) | What changed in the code | Source (page read) | Effect |
|---|---|---|---|---|
| 2 | Above-ground NPP into McNaughton's fit (PW-1073) | `prey.wild` feeds McNaughton et al. 1989's fit only the above-ground share of the grazing NPP, `prey.above(rain)` = 1 - (146 - 13.95 ln MAP)/100, clipped at 50-5,000 mm (no rain: 0.36) | Gherardi & Sala 2020, PNAS 117:20038, Fig. 3 legend (the fit) and text ("~70% in arid ecosystems to ~35% in humid", the below-ground share); Table 1 (grasslands 64%). The paper does not print the log base or the unit; ln with mm reproduces its 70% and 35% (a reading, marked) | prey x f^1.52: x0.16 at 250 mm, x0.35 at 1,000 mm, x0.46 at 2,000 mm. The largest single change: dry and cold land lose 5-7x of their herds |
| 3 | One stated intake law; 2.7 t labelled as the all-ages mean (PW-1066) | `dragon_ages.fmr_kcal`: Nagy et al. 1999's all-mammal field metabolic rate 4.82 M^0.734 kJ/day over `MESO_X` 2.1 (a mesotherm), the one law for every stage; the docstring states the all-ages mean (4.9 t of prey a year) and a dragon at the ecological mass (1.65 t: 8.5 t a year) | Nagy, Girard & Brown 1999, Annu Rev Nutr 19:247, Table 2 p. 260 eq. 1; Marshall et al. 2021, Science 372:284, p. 284 (a physiology "midway" between mammalian carnivores and large varanids, densities 2.1x a mammal's); McNab 2009 PNAS 106:12184, p. 12185 (varanids at 22%) | x0.90 against round 3's all-reptile line |
| 4 | Assimilation and carcass use (PW-1067) | `ASSIMILATED` 0.66, `CARCASS_USE` 0.78 (the midpoint of 65-91%: a judgement); one edible figure for peoples and dragons (`HEAD_KCAL` = `dragon_ages.edible_kcal()`) | Carbone et al. 2007, PLoS Biol 5:e22, p. 364 (0.66) and p. 367 (65-91% of a carcass) | x0.78 (assimilation 85% -> 66%) x0.78 (whole carcass -> 78%) |
| 5 | Offtake tied to herd production (PW-1072) | `OFFTAKE` = Farlow's turnover at the 0.5 t head (0.94 M^-0.28 = 0.165/yr) x the share of production predators kill (0.45: real communities at 100:1-200:1 against the 50:1 best case, over the carcass share): 7.5%/yr, was 10% unsourced | Farlow 1993, Am J Sci 293-A:167, eq. 6 p. 172 and p. 176; Coe, Cumming & Phillipson 1976, Oecologia 22:341, Table 1 pp. 344-345 (0.085-0.26/yr, a cross-check) | x0.75 |
| 8 | One metabolic exponent; young dragons eat in the smaller classes (PW-1071) | `GUILD_EXP` = the intake law's 0.734 (was a separate Kleiber 0.75); `dragon_share` adds the wyrmlings' and young's food (~24% of the dragons') inside the smaller classes' share: 21% of the guild's food, was 17% | Carbone, Turvey & Bielby 2011, Proc R Soc B 278:2682, p. 2683 (juvenile T. rex among its own competitors), Fig. 1 / Table 1 (the size classes) | x1.25 |
| 9 | Overkill by co-evolution time (PW-1000) | `prey.coevolved_loss`: the overkill (meta.overkill 0.6) x Sandom's species loss for how long small folk have lived there over 0.46, log-interpolated at 50 kyr / 1 Myr / 3 Myr (a judgement); the clock (`note_settled`) is each cell's first small folk, taken over the land within 300 km | Sandom et al. 2014, Proc R Soc B 281:20133254, Fig. 3 p. 5 and p. 2 (0.46 / 0.23 / 0.02 of species lost where modern humans came first / archaic hominins / hominins evolved) | none on newly reached land; land held over 1 Myr keeps about half its overkill, 3 Myr ~4%. In the dnd tree most land is reached late, so the effect is small |
| 11 | A deep-epoch food budget (PW-1062) | Before 300 kyr (other plates) the dragons' density is one planet figure from the same budget (`deep_budget`): the present's mean wild offtake after the step's mean overkill, less the peoples' mean take, plus stock, x the dragons' share | (the model's own chain; no new source) | the deep-time peak falls from 0.7-2.4 M dragons to ~0.4-0.5 M |
| 12 | Where the unused share goes; the smaller predators pressed too (PW-1070) | The guild takes (1 - dragon_share) of what the giants leave, x `guild_kept` (the peoples' kill against a wolf- to leopard-sized breeder, generation 7 yr: a judgement); what a pressed guild leaves, the dragons can take. The old "prey" mode's guild (ratio x the dragons' Carbone food) is gone: at the sourced intake it asked ~1.3x the whole offtake | Ripple et al. 2014, Science 343:1241484, Table 1 p. 1241484-2 (the 31 persecuted large carnivores include the gray wolf and the leopard) and p. 1241484-6 (empty forests; hunters first) | more food to dragons in peopled country, none where nobody hunts |
| 7 | A viable-population test for regional pockets (PW-1069) | Pockets within `metapop_km` are one population; a linked population under `LINKED_MVP` 1,000 fades unless it is the kind's largest (`linked_mvp`); each pocket in the summary carries `linked_pop` and `viable` | Marshall et al. 2021 p. 285 ("at least thousands"); Burness, Diamond & Flannery 2001, PNAS 98:14518, p. 14521 ("a few thousand to at least 10,000") | small: a trace with the old floor ends with the same white dragons (see below) |
| 1 (rest) | Persecution means from the peoples' own techs (PW-1177, partial) | Herds to defend count only once the history gives a people herds (`animals.herding`); riding from its stocks with speed > 1 (`MOUNTED_X` 0.5, a judgement); `KILL_Q` re-calibrated 0.0028 -> 0.00187 so dense renaissance farmers still keep 10% of their dragons. Weapons and metal still come from the era calendar | (the history's own animals pass; the calibration is the existing one, carried over) | the same kill on dense late farmers; less on early peoples without herds |
| 6 | Biomes: closer to A, fixed in general and widened (PW-1065) | dnd.toml: each dragon kind's habitat after the DMG's monsters-by-environment lists, each citing book and printed page; red 4-40 C with volcanoes, mountains and hills; blue desert and coast; green -4-30 C, 450-3,000 mm; black 2-34 C, 600-3,000 mm; white tolerates steppe, open and subarctic; gold grassland and forest; silver to 7,000 m with steppe, open and tundra; brass steppe and desert. Hunting: `release` lets a kind hunt `HUNT_KM` (~173 km, Jetz et al. 2004's carnivore home range at an ancient's mass) out of its own country whatever the prey | Dungeon Master's Guide (5e, 2014), Appendix B, pp. 302-305 (arctic p. 302; coastal p. 302; desert p. 302; forest pp. 302-303; grassland p. 303; hill p. 304; mountain p. 304; swamp p. 304; urban p. 305); Jetz et al. 2004, Science 306:266, Table 1 p. 268 | coverage of their own country rises for blue, gold, green and red; white and silver stay thin (food, below) |


Taken together, the factors per tonne of prey are 0.90 (intake) x 0.78 (assimilation) x 0.78 (carcass) x 0.75 (offtake) x 1.25
(young in the guild), about 0.51. The above-ground share then cuts the prey itself, by x0.16 to x0.46 depending on rain.

Also fixed on the way:
- **The overkill cache.** The overkill per cell was cached by step and ignored a change to `meta.overkill` (the viewer's setting). The
  cache key now includes it.
- **The giants' food.** The giants now read the same edible figure, `HEAD_KCAL`, as the peoples and dragons. They had been using the
  proposal's 625 Mcal, about 4% more food each. This commit (15d93b31) came after the sweep, so the sweep's giants are that 4% hungrier
  than the code's.

## Before and after

Both arms ran the paper's own probe, `docs/review/megafauna/probe.py`. Each covered six worlds (2a7385, 1df1c3, e71172, 6909cb, a12762,
067778) at roll 7000, with `--eras 31,29,25,10,5,0 --cells`, in three versions: the model as it stands ("on"), pressure off ("off") and
persecution off ("noper").

- **Before:** a snapshot of main 69ac92a5, whose planet/ is the same as 394a5ccd, this branch's base.
- **After:** this branch at 1532de63.

Both sets of numbers come from the paper's `dragon_numbers.py` at each checkout. The numbers are medians over the six worlds at the
present day. "Region" is the paper's Sword Coast-sized region (3.9 million km²), taken at the whole land's average density. The other
columns are dragons per 10,000 km².

**Table H1: dragons the yearly food would feed, if dragons lived in every land cell (before → after):**

| row | world | region | empty land | peopled | grassland | forest | desert |
|---|---|---|---|---|---|---|---|
| alone | 22,241,621 → 4,034,961 | 469,058 → 87,912 | 34 → 2.9 | 1,336 → 245 | 2,298 → 337 | 1,231 → 273 | 485 → 33 |
| rivals | 3,713,049 → 835,654 | 78,304 → 18,207 | 5.4 → 0.56 | 223 → 51 | 383 → 69 | 206 → 57 | 81 → 6.9 |
| hunt | 1,743,688 → 232,985 | 36,357 → 4,970 | 3.8 → 0.21 | 110 → 15 | 221 → 22 | 48 → 10 | 55 → 1.9 |
| overkill | 952,271 → 295,642 | 19,847 → 6,149 | 3.3 → 0.18 | 57 → 18 | 89 → 25 | 20 → 8.2 | 24 → 1.7 |

**Table H2: dragons the worlds hold now:**

| row | world | region | empty land | peopled | grassland | forest | desert |
|---|---|---|---|---|---|---|---|
| hunt | 106,765 → 5,968 | 2,326 → 123 | 1.4 → 0.062 | 6.2 → 0.38 | 14 → 0.67 | 0.35 → 0.05 | 2.4 → 0.22 |
| overkill | 32,922 → 7,388 | 679 → 152 | 1 → 0.071 | 1.7 → 0.45 | 2.3 → 0.73 | 0.14 → 0.054 | 0.67 → 0.42 |
| persecution | 19,751 → 3,566 | 431 → 74 | 1 → 0.071 | 0.86 → 0.21 | 1.5 → 0.38 | 0.056 → 0.015 | 0.62 → 0.21 |
| press_0.25 | 25,801 → 5,271 | 543 → 109 | 1 → 0.071 | 1.1 → 0.33 | 1.9 → 0.54 | 0.1 → 0.031 | 0.67 → 0.33 |
| press_4 | 11,544 → 2,088 | 252 → 43 | 1 → 0.071 | 0.47 → 0.11 | 0.77 → 0.22 | 0.019 → 0.0087 | 0.54 → 0.1 |

Notes on the tables:
- **Two rows swap order, in H1 and H2.** In "after", the "overkill" row is above the "hunt" row. "Hunt" comes from the pressure-off runs, where
  nobody kills the smaller predators. "Overkill" comes from the persecution-off runs, where the peoples still kill them (`guild_kept`),
  so the dragons take what that guild leaves (ruling #12).
- **Persecution takes a little more.** In H2, going from the overkill row to the persecution row now loses about half the dragons
  (7,388 → 3,566), where it lost 40% before (32,922 → 19,751). Herds now count only once the history gives a people herds. `KILL_Q`
  was re-calibrated so that dense renaissance farmers still keep 10% of their dragons. The world totals by arm (below) vary more
  from world to world.

**The Sword Coast-sized region over all land at the present.** These are means over the six worlds, with the range:
- **Before:** 461 dragons (166-951).
- **After:** 118 (19-385).
- **The largest kind's share:** a median of 0.41 before and 0.42 after.

**Deep time.** The deep-time peak of all dragons falls from 0.65-2.4 million to 0.25-0.53 million. It now comes from the planet-wide
deep budget (`deep_budget`, ruling #11), and it falls at 8-16 Myr ago rather than at the 300-400 kyr plate switch.

**Totals by arm.** All dragons on each world at the present, in the order 067778, 1df1c3, 2a7385, 6909cb, a12762, e71172:

| arm | before | after |
|---|---|---|
| on | 10,271; 29,326; 46,115; 24,913; 8,069; 15,086 | 2,946; 3,962; 18,585; 5,682; 917; 1,864 |
| persecution off | 32,073; 34,411; 93,474; 44,207; 19,365; 25,437 | 8,952; 5,543; 29,531; 10,246; 2,507; 2,668 |
| pressure off | 222,229; 84,012; 224,256; 102,787; 38,455; 115,633 | 5,634; 6,335; 20,041; 7,124; 2,672; 3,667 |

**By kind, at the present, on the six worlds:**

| kind | before: median count (range) | after | coverage of its country, median before → after |
|---|---|---|---|
| black dragon | 714 (0-5,981) | 134 (8-2,406) | 0.70 → 0.54 |
| blue dragon | 2,590 (119-20,803) | 238 (119-1,155) | 0.64 → 0.92 |
| brass dragon | 3,828 (1,074-19,658) | 1,495 (338-8,774) | 0.95 → 0.93 |
| bronze dragon | 387 (202-1,985) | 146 (28-474) | 0.88 → 0.85 |
| cloud giant | 176 (120-715) | 342 (123-788) | 0.57 → 0.61 |
| copper dragon | 848 (174-6,868) | 106 (52-586) | 0.40 → 0.36 |
| fire giant | 1,358 (442-4,545) | 2,038 (650-5,776) | 0.51 → 0.45 |
| frost giant | 942 (255-2,016) | 348 (84-1,300) | 0.47 → 0.54 |
| gold dragon | 870 (420-7,548) | 419 (50-4,983) | 0.81 → 0.98 |
| green dragon | 187 (34-539) | 24 (5-411) | 0.59 → 0.88 |
| hill giant | 31,135 (21,302-91,927) | 40,179 (32,208-122,368) | 0.78 → 0.73 |
| red dragon | 750 (287-1,969) | 133 (49-234) | 0.58 → 0.69 |
| silver dragon | 294 (77-1,435) | 20 (6-317) | 0.44 → 0.54 |
| storm giant | 5,496 (1,531-13,572) | 6,989 (2,705-18,473) | 0.96 → 0.96 |
| white dragon | 1,380 (70-3,272) | 26 (0-82) | 0.73 → 0.49 |


The giants rise slightly. Their density reads the land's productivity against its own median, not the absolute prey, and they eat
before the smaller predators and the dragons, so the drop in prey does not reach them.

## The cold dragons: a diagnosis

White, silver and bronze dragons fall much further than the rest. Four trace runs of world 6909cb tested three suspects: the new
viability floor, persecution and the hunting range. Each trace recorded every kind's count every 10 kyr; the script is scratch, not
committed. These are the white dragons' means over the last 290 kyr:

| trace | white dragons | silver dragons |
|---|---|---|
| as committed | 150 | 129 |
| the old viability floor (`line_mvp` instead of `LINKED_MVP` 1,000) | 177 | 111 |
| no persecution of the dragons | 151 | 130 |
| food gathered over the ancients' hunting range, ~173 km, not the food-weighted ~77 km | 225 | 77 |

None of the three explains the fall. The food does:
- **Their country lost most of its herds.** The median prey in white-dragon country on 6909cb fell from 0.39 to 0.05 t/km² (x0.14).
  That is the above-ground share at about 250 mm of rain, raised to McNaughton's 1.52.
- **The cells they hold are poorer still.** There the median prey fell from 0.24 to 0.009 t/km².

The draft "cold dragons thin after the above-ground prey" (needs-decision) asks the owner to choose:
- **A.** Accept them as rarities.
- **B.** Add a sea food for the coast and ice kinds.
- **C.** Widen the food reach, a weak lever.

## The peoples (lane 83's area, untouched)

These are `planet lineages 4360a3 --tree dnd.toml`, with the tree's `seed =` line set to 7, 10 and 13, before and after. Each people's
share is its land (Mkm², present) over all peoples' land, dragons and giants left out. Each run keeps the best of four tries, so a
point or two of drift is noise. The six l90 runs were deleted afterwards.

| people | s7 before → after | s10 before → after | s13 before → after |
|---|---|---|---|
| aarakocra | 1.2% → 1.2% | 1.2% → 1.0% | 0.9% → 1.1% |
| bugbears | 0.2% → 0.2% | 0.2% → 0.2% | 0.6% → 0.2% |
| dragonborn | 11.9% → 8.6% | 9.8% → 11.9% | 7.5% → 10.7% |
| drow | 0.2% → 0.2% | 0.2% → 0.2% | 0.1% → 0.2% |
| dwarves | 0.2% → 0.2% | 0.2% → 0.2% | 0.5% → 0.2% |
| elves (from the feywild) | 3.6% → 3.9% | 4.5% → 4.0% | 3.0% → 3.7% |
| firbolgs | 0.1% → 0.0% | 0.0% → 0.0% | 0.3% → 0.1% |
| gnomes (from the feywild) | 2.6% → 3.7% | 3.2% → 2.8% | 1.9% → 1.7% |
| goblins | 0.4% → 0.5% | 0.5% → 0.3% | 1.0% → 0.7% |
| goliaths | 0.2% → 0.2% | 0.2% → 0.2% | 0.2% → 0.2% |
| half-elves | 2.8% → 1.5% | 2.0% → 2.9% | 4.0% → 2.1% |
| half-orcs | 7.3% → 7.5% | 7.9% → 8.5% | 7.7% → 7.2% |
| halflings | 4.7% → 5.7% | 6.6% → 6.5% | 9.2% → 6.8% |
| hobgoblins | 4.6% → 3.8% | 3.8% → 2.8% | 5.7% → 3.5% |
| humans | 21.6% → 22.2% | 17.0% → 19.5% | 22.0% → 21.5% |
| kenku | 10.2% → 11.3% | 12.0% → 9.7% | 8.0% → 10.5% |
| kobolds | 10.9% → 11.6% | 13.3% → 12.4% | 8.7% → 11.7% |
| leonin | 3.2% → 2.3% | 1.8% → 2.0% | 4.6% → 3.1% |
| lizardfolk | 0.5% → 1.6% | 1.9% → 1.3% | 0.9% → 1.5% |
| orcs | 3.9% → 4.0% | 4.1% → 4.5% | 4.0% → 3.8% |
| sea elves | 0.9% → 0.9% | 0.9% → 0.7% | 0.6% → 0.8% |
| tabaxi | 6.4% → 6.2% | 5.5% → 5.3% | 5.7% → 6.1% |
| tortles | 1.4% → 1.7% | 2.1% → 1.9% | 1.5% → 1.3% |
| tritons (from the plane of water) | 1.3% → 1.3% | 1.4% → 1.2% | 1.3% → 1.5% |


## Hooks outside the megafauna code (flagged)

- **`history/model.py`.** After the step's kill, two calls feed the overkill's clock and the deep epoch's food budget:
  `MG.note_settled(self, self.p, step.ago)`, then, in the deep epoch, `MG.deep_budget(self, self.p, env["land"])`. They read the
  presences and do not change them.
- **`history/dispersal.py`, `_viable`.** A megafauna line's floor is `MG.linked_mvp(l)`. The peoples keep `line_mvp`, so their numbers
  do not change.

## Judgements made (marked in the code)

- **Carcass use 0.78.** The midpoint of Carbone 2007's 65-91%.
- **The co-evolution times.** 50 kyr / 1 Myr / 3 Myr, log-interpolated, for Sandom's three groups. The clock reads the land within
  300 km.
- **The smaller predators' generation, 7 yr**, for the peoples' kill on them.
- **`MOUNTED_X` 0.5.** Riding's share of the means.
- **The above-ground fit's units.** Gherardi & Sala print neither the log base nor the unit. ln with MAP in mm reproduces the paper's
  70% and 35%.
- **The "prey" setting's guild.** It is now the same as the food setting's; the old multiple starved the dragons at the sourced intake.
- **No rain field.** Without one, `prey.wild` uses 0.36, the humid end.

## Tests

- `uv run pytest -q -m 'not slow'`: 844 passed and 1 skipped. Three kernel-thread tests failed only because the run capped numba at one
  thread; they pass on their own (3 passed).
- The lineages, prey, niche-learning, viewer and golden tests, slow included: 148 passed.
- No golden files changed. The tests changed for the intended changes: the McNaughton and anchor tests now read the above-ground
  share, the release test reads the hunting range, the natural-settings and budget tests read `dragon_share`, and there is a new
  `test_food_chain_revisions_lane90`.
