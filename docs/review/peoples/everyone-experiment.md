# Everyone: the kitchen-sink extinction experiment (lane 277)

An experiment that Daniel asked for on 2026-11-10: *"contrive every last damn playable species you can think of and make a reasonable-looking
phylogenetic tree for this far-too-busy world and see how badly it explodes or who goes extinct ... remove the 'if a people shrink too much
they get moved,' and instead allow playable races/species to go extinct under appropriate pressure."* None of it gets tuned or merged into
the defaults: main behaves exactly as before unless the switch is set.

## In plain words

- **The tree.** We built a 127-line family tree with 98 end peoples. It has every D&D people from the existing preset, plus about 55 more:
  - beast-folk: cats, hyenas, dogs, jackals, wolves, bears, otters, seals, bulls, antelope, deer, elephants, rhinos, hippos, rabbits, mice,
    moles, hedgehogs, bats, monkeys, owls, frogs, toads, snakes and mantises;
  - sea peoples: merfolk, fish-folk and shark-folk;
  - plant-folk and fungus-folk, the small fey, satyrs and centaurs;
  - elf, dwarf, gnome and halfling variants, ogres and trolls;
  - two astral peoples, an ooze people, two kinds of construct, and five "touched" overlays.
- **On main nobody can die out.** In the control run on world 4360a3, all 88 whole peoples are alive at the present. That includes **11 green
  dragons**, 142 silver dragons and 1,512 frost giants, each still counted as a living people with its own culture and gods. The floors keep
  them on the books.
- **With the floors off, 14 of 88 die out on that world**:
  - five beast-folk peoples: the tortles (1.6 Myr ago), hedgehog-folk, deer-folk, mole-folk and serpent-folk;
  - the aarakocra, the goblins and the ooze-folk;
  - the forest gnomes, only 4,000 years ago;
  - three dragon kinds: the silver, green and white dragons;
  - two splits that were stillborn: the mouse-folk and the river halflings.
- **Almost all extinctions are competition, not climate.** On almost every cell a dying people held, another people moved in on the next
  frame. Their land was never left empty.
- **The weirdest thing:** if the stems may die too, the **mammal root dies 1 Myr after it appears**. It is born into a world already full of
  older reptile, amphibian, fish, insect, plant and fungus roots. With it go humans, dwarves, goblins, orcs, giants, halflings and every
  hooved, rodent or insect-eating people. That world is run by mantis-folk, flower people, crow people, cats and dogs. On main the same root
  is saved by a refuge on the step it is born, so the whole mammal branch grows from a refuge pocket.
- **Who explodes when the floors go:**
  - the rabbit people: from 53 M to 179 M, the largest range on the world (31 Mkm²);
  - wolf-folk: from 2 M to 87 M;
  - bugbears: from 0.4 M to 48 M.
  - **Humans fall from 190 M to 67 M.** The baseline is the same world and tree with the floors on.
- **Cost:** an L6 world takes 11 to 14 minutes of history. With all the outputs it took about 28 minutes, against about 8 minutes for a
  dnd-sized tree. After that, the languages pass ran more than 35 minutes and was still going when we stopped it. Peak memory was 3.6–5.2 GB.
  The two L7 runs took 69 and 75 minutes with no languages pass and peaked at 12 GB. They lost 19 and 18 of 88 peoples (see "L7 runs" below).
- **At L7 it is the same story.** On the Earth-like world 70 of 88 peoples are alive and on the near-supercontinent 69. Between 6 and 7 of the
  dead on each world never held land at all (stillborn on their founding step), and for the rest another people took every dead people's last
  cells on the next frame. Who wins and who dies out changes a lot from world to world: the hare-folk win L6, are dead on one L7 world and
  111 M on the other; the same dragonborn are stillborn on one and 45 M on the other. Only the mole-folk, the green and white dragons,
  the river halflings and the forest gnomes die on all three worlds.

## The switch: what exactly it changes

`planet lineages WORLD --set HOLD_OUT_REFUGE=false` sets the constant in `planet/lineages/history/params.py`. `--set` is new: it overrides any
`history.params` constant for one call. The default is `True`, which is main. When it is off, these change for every people:

1. **No refuge move** (`dispersal._hold_out`). A line given as living at the present is no longer put back into a refuge pocket when it falls
   under 3 cells or loses all its land.
2. **No BRAKE_HOLD floor** (`counter._brake`). War-torn land, raids, in-fighting and culls may now cut a people's habitat on its own cells
   below 0.24, so they can take the land outright. COUNTER_FLOOR (5% of K) stays, but at 5% a cell is below the presence threshold anyway, so
   it keeps no one alive.
3. **No refuge gate on displacement** (`competition._compete`). On main, displacement slows as a range shrinks toward REFUGE_MKM2 (0.5 Mkm²)
   and stops entirely below it. Off, a people held above its competitive room is displaced at the full rate however small it is. The Allee
   lapse (HOLD_MIN) may also take its last cells.
4. **The viable-population fade reaches the largest patch** (`dispersal._viable`). On main, the largest patch is always spared. Off, a people
   whose only or largest patch is under its viable number (`line_mvp`) fades too.
5. **No birth from a dead stem** (`origins._start_due`). A split whose stem has died out is never born ("unborn" event). On main it would be
   founded by the stem's last land.

`EXTINCT_STEMS` (default `False`) sets whether stems are spared. With it `False`, a stem that still has splits to come keeps all five floors
until its last split. That is the "peoples die, the family tree still happens" reading of Daniel's request, and all the runs below use it
except the one marked "stems die too". `True` lets stems die as well. Scripted extinctions (`extinct = "T"`) are unchanged.

## The tree (`planet/lineages/samples/everyone.toml`)

It is `dnd.toml` as of main plus a block of lane 277 additions at the end, with these changes:

- the troglodytes are no longer scripted to die out;
- dwarves, gnomes and halflings `persist` past their new variants, as the elves already did;
- the cats hang off a new feliform stem, so the hyena-folk are their cousins;
- the "devils" and "demons" exonyms are dropped. They keyed on horns and antlers, and this tree is full of horned and antlered peoples who
  are not fiends.

Habitats, bodies and ways of life come from the nearest real animal: Seven Meals' ruminant, antelope and cervid bodies for the hooved
peoples, a canid's grape, chocolate and onion toxicity for the dogs, hindguts for rabbits, elephants and rhinos, ectotherms for the
amphibians, fish, snakes and mantises. Where an existing preset entry already fitted, its numbers were used.

Trademarked creatures get plain stand-ins:
- serpent-folk for yuan-ti;
- astral raiders and monks for githyanki and githzerai;
- forgeborn for warforged;
- clockwork folk for autognomes;
- mantis-folk for thri-kreen;
- spore-folk for myconids;
- shark-folk and fish-folk for sahuagin and locathah;
- hare-folk, owl-folk and elephant-folk for harengon, owlin and loxodon;
- the dream-touched for kalashtar;
- ooze-folk for plasmoids.

Mind flayers are left out: they are parasites, not a people.

**Honest fudges (flagged):**

- **Constructs are not born.**
  - The forgeborn are a `split` of the dwarves at 2 kyr ("forged in the dwarf holds") and the clockwork folk a split of the gnomes at
    1.5 kyr. Both carry an `interfertile` tier 3 with their makers, so they have no hybrids.
  - The model still makes them eat and breed, and their numbers follow the density ladder like anyone else's.
- **The undead-adjacent and the shape-changers are overlays, not lineages.**
  - Dhampirs, the reborn, changelings, shifters and the dream-touched are `template` overlays on their host peoples, as tieflings are in
    dnd.toml.
  - Templates are overlays, so they cannot die out on their own; they go when their host does.
- **Plant-folk and spore-folk need a food ladder.**
  - They are separate roots (15 and 12 Myr).
  - The model has no photosynthesis rung, so they "farm" and "forage".
- **Centaurs are fey**, a split of the arriving lesser fey. A horse-human chimera has no honest biological descent.
- **Deep splits are squeezed.** The roots may be no older than 20 Myr (the owner's ruling), so real splits that are 25–90 Myr deep sit inside
  the 10 Myr mammal root: moles against hedgehogs, elephants against rhinos, hyenas against cats.

The family tree (date = when the line arises):

- `reptilian` (20 Myr)
  - `draconic` (19.5 Myr): megafauna
    - `chromatic_dragon` (2.5 Myr): megafauna
      - `red_dragon` (750 kyr): megafauna
      - `blue_dragon` (750 kyr): megafauna
      - `green_dragon` (750 kyr): megafauna
      - `black_dragon` (750 kyr): megafauna
      - `white_dragon` (750 kyr): megafauna
    - `metallic_dragon` (2.5 Myr): megafauna
      - `gold_dragon` (750 kyr): megafauna
      - `silver_dragon` (750 kyr): megafauna
      - `bronze_dragon` (750 kyr): megafauna
      - `copper_dragon` (750 kyr): megafauna
      - `brass_dragon` (750 kyr): megafauna
    - `kobold` (350 kyr)
    - `dragonborn` (300 kyr)
  - `saurian` (19.5 Myr)
    - `troglodyte` (2.5 Myr)
    - `lizardfolk` (2.5 Myr)
    - `tortle` (4.2 Myr)
  - `serpentine` (15 Myr)
    - `serpent_folk` (1.2 Myr)
    - `naga_folk` (900 kyr)
- `mammalian` (10 Myr)
  - `goblinoid` (2.5 Myr)
    - `greater_goblinoid` (600 kyr)
      - `hobgoblin` (250 kyr)
      - `bugbear` (200 kyr)
    - `goblin` (400 kyr)
  - `hominid` (4 Myr)
    - `giantkin` (1.1 Myr)
      - `true_giant` (1 Myr): megafauna
        - `hill_giant` (900 kyr): megafauna
        - `sky_giant` (800 kyr): megafauna
          - `cloud_giant` (400 kyr): megafauna
          - `storm_giant` (300 kyr): megafauna
        - `elemental_giant` (700 kyr): megafauna
          - `frost_giant` (350 kyr): megafauna
          - `fire_giant` (250 kyr): megafauna
      - `goliath` (300 kyr)
      - `firbolg` (200 kyr)
      - `ogre` (600 kyr)
      - `troll_folk` (450 kyr)
    - `orc` (700 kyr)
    - `dwarf` (500 kyr): persists
      - `hill_dwarf` (150 kyr)
      - `grey_dwarf` (100 kyr)
      - `forgeborn` (2 kyr)
    - `archaic_human` (400 kyr)
      - `human` (200 kyr)
      - `halfling` (100 kyr): persists
        - `river_halfling` (40 kyr)
  - `feliform` (9 Myr)
    - `feline` (4 Myr)
      - `tabaxi` (1.2 Myr)
      - `leonin` (900 kyr)
    - `hyena_folk` (3 Myr)
  - `caniform` (9 Myr)
    - `canine` (4 Myr)
      - `dog_folk` (600 kyr)
      - `jackal_folk` (900 kyr)
      - `wolf_folk` (500 kyr)
    - `bear_folk` (3 Myr)
    - `otter_folk` (2.5 Myr)
    - `selkie` (2 Myr)
  - `pecoran` (8 Myr)
    - `bovid` (5 Myr)
      - `bull_folk` (1.5 Myr)
      - `antelope_folk` (2 Myr)
    - `cervid_folk` (3 Myr)
  - `elephant_folk` (8 Myr)
  - `rhino_folk` (7 Myr)
  - `hippo_folk` (6 Myr)
  - `glires` (8 Myr)
    - `harefolk` (2 Myr)
    - `mousefolk` (1.5 Myr)
  - `insectivoran` (8 Myr)
    - `mole_folk` (2 Myr)
    - `hedgehog_folk` (1.6 Myr)
  - `bat_folk` (7 Myr)
  - `simian_folk` (7 Myr)
  - `merfolk` (6 Myr)
- `elf` (25 kyr): persists, arrival from the feywild
  - `drow` (12 kyr)
  - `sea_elf` (8 kyr)
  - `wood_elf` (14 kyr)
  - `high_elf` (10 kyr)
  - `winter_elf` (9 kyr)
  - `shade_elf` (6 kyr)
- `gnome` (50 kyr): persists, arrival from the feywild
  - `forest_gnome` (30 kyr)
  - `deep_gnome` (20 kyr)
  - `clockwork_folk` (1.5 kyr)
- `triton` (6 kyr): arrival from the plane of water
- `avian` (6 Myr)
  - `aarakocra` (900 kyr)
  - `kenku` (400 kyr)
  - `owl_folk` (700 kyr)
- `feyfolk` (60 kyr): arrival from the feywild
  - `satyr` (45 kyr)
  - `centaur` (40 kyr)
  - `fairy` (35 kyr)
  - `brownie` (30 kyr)
- `astral_raiders` (8 kyr): arrival from the astral plane
  - `astral_monks` (6 kyr)
- `ooze_folk` (15 kyr): arrival from the elemental mire
- `amphibian` (18 Myr)
  - `frog_folk` (2 Myr)
  - `toad_folk` (1.6 Myr)
- `piscine` (18 Myr)
  - `fish_folk` (2 Myr)
  - `shark_folk` (1.4 Myr)
- `mantis_folk` (16 Myr)
- `plantfolk` (15 Myr)
  - `bark_folk` (3 Myr)
  - `bloom_folk` (1.5 Myr)
- `spore_folk` (12 Myr)
- overlays and mixed peoples: `half_elf` (hybrid of human + elf), `half_orc` (hybrid of human + orc), `tiefling` (template of human), `aasimar` (template of human + elf), `genasi` (template of human + dwarf), `changeling` (template of human), `shifter` (template of human + wolf_folk), `dhampir` (template of human + elf), `reborn` (template of human + dwarf + halfling), `dream_touched` (template of human)

## Runs

Every run is on a scratch data root, with the world and time-zoom data copied or file-linked. Nothing was written into the repo's runs/ or
worlds/. All runs use `--tree everyone --tries 1`.

| world | kind | run | switch | wall time | peak RSS |
|---|---|---|---|---|---|
| 4360a3 (L6) | fragmented: 10 landmasses over 1%, largest 29% | fe887b | control (main) | ~28 min to outputs; languages pass stopped after 38 more min | 5.2 GB |
| 4360a3 (L6) | | efe61b | peoples die | 19.7 min (history 679 s), stopped in the gods step | 3.6 GB |
| 4360a3 (L6) | | 592dd0 | stems die too (first cut of the switch) | 39 min, stopped in the languages pass (history 489 s) | 4.4 GB |
| 899985 (L7) | Earth-like (12 landmasses, largest 23%) | 0683e9 | peoples die | 75 min (history 3,097 s), no languages pass | 12.4 GB |
| 94cc8e (L7) | near-supercontinent (two masses, 44% + 41%) | 2e600c | peoples die | 69 min (history 2,889 s), no languages pass | 12.1 GB |

None of the stored worlds is an archipelago world. 899985 is the most broken-up L7 world with its time zoom still stored (12 landmasses over
1%, 150 islands), and 4360a3 is the L6 stand-in for that kind.

### 4360a3 (L6): whole peoples born and alive at the present

Of the 88 whole peoples, 16 are dragon or giant kinds and 72 are other peoples. The 10 overlays are not counted.

| run | born | alive now | died out | never born | heads at present |
|---|---|---|---|---|---|
| control (main) | 88 | 88 | 0 | 0 | 1.64 bn |
| peoples die | 88 | 74 | 14 | 0 | 1.57 bn |
| stems die too | 55 | 53 | 2 | 33 | 0.98 bn |

**Who died out, when, and who took the land** (peoples die, run efe61b). The takers are the peoples on the dead people's last cells at the
next stored frame (`takers.py`):

| people | died | peak | last land | taken by | why |
|---|---|---|---|---|---|
| tortles | 1.6 Myr ago | 3,460 (3.8 Myr ago) | 11 cells | fish-stem, bird-stem and frog-folk lines | crowded off the warm coasts by the other swimming lines in deep time |
| mouse-folk | 1.5 Myr ago, at birth | — | none | — | stillborn: founded beside the glires stem, displaced on the first step (the refuge gate had protected it) |
| hedgehog-folk | 800 kyr ago | 6,400 | 28 cells | hippo-folk, toad-folk, bat-folk | outcompeted in the warm lowlands |
| deer-folk | 700 kyr ago | 16,000 (at birth) | 6 cells | leonin, gold dragons | never got going; the cats took its last forest edge |
| aarakocra | 450 kyr ago | 11,600 | 32 cells | dwarves, the bird stem, sky giants | the mountains were full: dwarves and giants |
| silver dragons | 288 kyr ago | 13,900 | 259 cells | elemental giants, gold and red dragons | megafauna crowding plus the linked-population fade |
| green dragons | 284 kyr ago | 8,900 | 1,813 cells | bat-folk, wolf-folk, tabaxi, hippo-folk | the forests filled with peoples; in the control only 11 green dragons are left |
| mole-folk | 284 kyr ago | 5,100 | 17 cells | hare-folk, bull-folk, owl-folk | the hare-folk took the meadows |
| white dragons | 254 kyr ago | 44,000 | 2 cells | bat-folk, hill giants, copper dragons | squeezed out of the cold country |
| serpent-folk | 238 kyr ago | 161,000 | 11 cells | hippo-folk, hobgoblins, monkey-folk | outcompeted in the jungle |
| goblins | 238 kyr ago | 81,000 | 11 cells (the same ones) | hobgoblins, hippo-folk, monkey-folk | outcompeted by their own cousins, on the same step and cells as the serpent-folk |
| river halflings | 40 kyr ago, at birth | — | none | — | stillborn (control: founded on 0.15 Mkm² and still alive with 3,600) |
| ooze-folk | 10.7 kyr ago | 91,000 (on arrival) | 3 cells | bat-folk, tabaxi, hyena-folk | an arrival that never found free room |
| forest gnomes | 4 kyr ago | 129,000 | 1 cell | elves, tabaxi, bat-folk | the elves took the old woods back |

No people died for want of habitat alone: every dead people's last cells were held by someone else on the next frame (at most 35 cells were
left empty, by the green dragons). War, raids and culls did thin peoples (80 culls and 113 "troubles" were logged), but each extinction ends
in displacement by a rival. The model has no separate death by war.

**Who exploded** (peoples die, against control):

| people | control | peoples die | note |
|---|---|---|---|
| hare-folk | 53 M | 179 M, 31 Mkm² | the biggest range on the world: quick-breeding, hardy, cosmopolitan, open country |
| bloom-folk | 140 M | 187 M | the most numerous people: flower farmers |
| mantis-folk | 171 M | 173 M | the dry plains, both runs |
| hobgoblins | 121 M | 118 M | |
| wolf-folk | 2.1 M | 87 M | the green dragons' forests |
| humans | 190 M | 67 M | lost the temperate lowlands to the hare-folk and the hippo-folk |
| bugbears | 0.4 M | 48 M | |
| centaurs | 53 M | 12 M | |

### 4360a3: the "stems die too" world (run 592dd0)

Run 592dd0 is the first cut of the switch, before stems were spared. It is the same as `HOLD_OUT_REFUGE=false EXTINCT_STEMS=true`.

- The mammal root died out 9 Myr ago, on its first step after its founding step.
- 33 peoples were never born: 45 "unborn" events, stems included.
- The caniforms and feliforms were born on that same last step (both split at 9 Myr). So the cats (tabaxi, leonin), the hyena-folk, dogs,
  jackals, bears, otters and seals are the only mammals in the world. The wolf-folk died at 296 kyr.
- The present belongs to:
  - mantis-folk (219 M);
  - bloom-folk (193 M);
  - the kenku crow-folk (108 M);
  - the elves (64 M; they arrive from the feywild, so they owe the mammal root nothing);
  - tabaxi (61 M);
  - dragonborn (50 M);
  - dog-folk (46 M).
- With no dwarves, the deep gnomes hold the underdark alone.
- The green dragons die here too, 14.5 kyr ago.

## L7 runs

Two detached runs, each without the languages pass (`docs/review/peoples/everyone/run_nolang.py`, `languages=False`, 4 threads each), both with the
floors off and stems spared. No L7 control was run (the machine was at load 60+), so "exploded" below means the largest peoples, not a change
against main.

| world | run | born | alive at present | died out | never born | wall time | peak RSS |
|---|---|---|---|---|---|---|---|
| 899985, Earth-like | 0683e9 | 88 | 70 | 18 | 0 | 75 min | 12.4 GB |
| 94cc8e, near-supercontinent | 2e600c | 88 | 69 | 19 | 0 | 69 min | 12.1 GB |

That is 20% and 22% of the peoples gone, against 16% at L6 (74 of 88 alive). Both L7 worlds lost the mole-folk, the red, green and white dragons,
the river halflings and the forest gnomes. L6 lost all of those but the red dragons.

**Stillbirths.** 6 of 18 extinctions on the Earth-like world and 7 of 19 on the supercontinent never held land in a stored frame: the
people was founded and gone on the same step.
- Earth-like: spore-folk (12 Myr), monkey-folk (7 Myr), hippo-folk (6 Myr), gold dragons, wolf-folk and kobolds. Monkey-folk and hippo-folk
  are whole mammal lines that never got going.
- Supercontinent: mantis-folk (16 Myr), otter-folk, green, black and silver dragons, frost giants and dragonborn.
- The same people is often stillborn in one world and thriving in the other: dragonborn are dead at birth on the supercontinent and number
  45 M on the Earth-like world; mantis-folk are dead at birth on the supercontinent and number 148 M on the Earth-like world; wolf-folk are
  stillborn on the Earth-like world and number 14 M on the supercontinent.
- Even with the refuge off, the `refuge` event still fires once on each world: the mammalian stem is held out in a refuge on its first step
  (9.3 Myr and 10 Myr ago). The stem is spared by `EXTINCT_STEMS=False`; this was the one refuge left on the books.

### 899985 (L7, Earth-like): who died, when, who took the land

| people | died | peak | last land | taken by |
|---|---|---|---|---|
| spore-folk, monkey-folk, hippo-folk | 12, 7, 6 Myr ago, at birth | none | none | stillborn |
| gold dragons, wolf-folk, kobolds | 750, 500, 350 kyr ago, at birth | none | none | stillborn |
| bear-folk | 600 kyr ago | 6,500 | 46 cells | the bird stem, elemental giants, dog-folk |
| mole-folk | 284 kyr ago | 7,200 | 110 cells | hare-folk, mouse-folk, bat-folk |
| red dragons | 276 kyr ago | 8,200 | 36 cells | frog-folk, bat-folk |
| green dragons | 266 kyr ago | 21,000 (17.8 Mkm2) | 22 cells | owl-folk, hill giants, copper dragons |
| elephant-folk | 232 kyr ago | 31,000 | 6 cells | hare-folk, mouse-folk, bat-folk |
| white dragons | 172 kyr ago | 21,000 (11.9 Mkm2) | 7 cells | silver dragons, dwarves, frost giants |
| firbolgs | 88 kyr ago | 80,000 | 1 cell | cloud giants, grey dwarves |
| river halflings | 34 kyr ago | 6,000 | 27 cells | owl-folk, humans, halflings |
| goblins | 25.7 kyr ago | 153,000 | 2 cells | bark-folk, hobgoblins |
| forest gnomes | 17.9 kyr ago | 43,000 | 4 cells | elves, deep gnomes |
| brownies | 11.4 kyr ago | 37,000 | 3 cells | bark-folk, cloud giants, fairies |
| winter elves | 6.8 kyr ago | 32,000 | 5 cells | owl-folk, ogres, wood elves |

Every dead people's last cells were held by someone else on the next frame, and no cell was left empty.

Biggest at the present: humans 292 M (48 Mkm2), hyena-folk 170 M, mantis-folk 148 M, hare-folk 111 M, dwarves 64 M, bloom-folk 64 M,
antelope-folk 62 M, grey dwarves 59 M, ogres 50 M and dragonborn 45 M. The widest ranges belong to small peoples: owl-folk 4 M on 41 Mkm2,
mouse-folk 19 M on 29 Mkm2.

### 94cc8e (L7, near-supercontinent): who died, when, who took the land

| people | died | peak | last land | taken by |
|---|---|---|---|---|
| mantis-folk, otter-folk | 16 Myr, 2.5 Myr ago, at birth | none | none | stillborn |
| green, black and silver dragons, frost giants, dragonborn | 750 to 300 kyr ago, at birth | none | none | stillborn |
| troglodytes | 1.4 Myr ago | 19,000 | 22 cells | the bird stem, toad-folk, rhino-folk |
| frog-folk | 298 kyr ago | 498,000 (9.9 Mkm2) | 3,165 cells | bat-folk, hippo-folk, deer-folk, mouse-folk |
| goblins | 298 kyr ago | 21,000 | 372 cells | monkey-folk, bat-folk, bark-folk |
| serpent-folk | 298 kyr ago | 103,000 | 1,009 cells | monkey-folk, bat-folk, bark-folk |
| red dragons | 270 kyr ago | 13,600 | 645 cells | spore-folk, bark-folk, gold dragons |
| white dragons | 250 kyr ago | 21,700 (14.2 Mkm2) | 18 cells | owl-folk, copper dragons, spore-folk |
| hare-folk | 218 kyr ago | 42,600 | 44 cells | wolf-folk, owl-folk, seal-folk |
| mole-folk | 194 kyr ago | 143,000 | 2 cells | bat-folk, deer-folk, fish-folk |
| hedgehog-folk | 25.5 kyr ago | 545,000 | 2 cells | mouse-folk, copper and gold dragons, humans |
| river halflings | 23.5 kyr ago | 192,000 | 8 cells | hippo-folk, deer-folk, fairies |
| forest gnomes | 20.6 kyr ago | 60,000 | 1 cell | spore-folk, owl-folk, elves |
| drow | 11.4 kyr ago | 23,000 | 5 cells | tabaxi, shark-folk, bronze dragons |

Again, almost every cell was taken by a rival on the next frame (at most 2 cells empty, from the red and white dragons). Three peoples
(frog-folk, goblins, serpent-folk) die on the same step, 298 kyr ago, and the same few peoples (bat-folk, monkey-folk, bark-folk) take their land.

Biggest at the present: humans 130 M (58 Mkm2), bloom-folk 114 M, antelope-folk 99 M, hyena-folk 93 M, hobgoblins 82 M, orcs 46 M and
monkey-folk 33 M. Widest ranges: bat-folk 1.5 M on 40 Mkm2, toad-folk 1.9 M on 26 Mkm2, mouse-folk 3.5 M on 22 Mkm2.

### What the two L7 worlds say

- **Who explodes is a matter of luck, not role.** The rabbit people, which won the L6 world, are dead on the supercontinent and 111 M on the
  Earth-like world. Hyena-folk are 93 to 170 M on both L7 worlds and mantis-folk 148 M on one. Humans are the most numerous people on both L7 worlds (292 M and 130 M).
- **Who dies out is also luck.** Only the mole-folk, the green and white dragons, the river halflings and the forest gnomes are lost on all three worlds.
  The chromatic dragons die almost everywhere; the late halfling and gnome splits die on their first competition.
- **Tiny peoples with huge ranges** (bat-folk, owl-folk, toad-folk, mouse-folk, hill giants, copper dragons) hold the patchwork between the great
  powers: a few millions of people over 20 to 40 Mkm2.
- **Cost.** L7 with 88 whole peoples took 69 to 75 minutes with no languages pass and peaked at 12 GB, the same as the dnd tree at L7. So
  the larger tree costs time, not memory (history alone took 2,900 to 3,100 s).

## Weirdest outcomes

1. **A world with no mammals except cats and dogs** ("stems die too"). Mantis-folk and flower people are the great powers. The kenku
   crow-folk are the third-largest people. The elves are the only humanoid-looking people, because they came from another plane.
2. **The rabbits win.** Without the floors, the hare-folk become the widest-ranging people on the world and push the humans off half their
   lowlands.
3. **Eleven green dragons.** On main, the floors keep a dragon kind of 11 animals as a living people with a culture, gods and a brief.
4. **The goblins and the serpent-folk die on the same step, on the same 11 cells**, squeezed between hobgoblins, hippo-folk and monkey-folk.
5. **The forest gnomes die 4,000 years ago**, retaken by the elves who came through the same portals.
6. **Stillborn peoples.** The mouse-folk and the river halflings are founded, then displaced on their first step. On main a newborn people
   is immune to displacement until it grows past 0.5 Mkm², because founders get less land than the refuge gate's own size.

## What broke or was slow

- **No crashes** in the history, the cultures, demes, settlements, gods or taboos at L6 with 88 whole peoples, 16 of them megafauna, and 10
  overlays.
  - One warning, from the tech tree: its `[[kind]]` rule names `edge_folk`, a line this tree does not have. It is harmless.
  - `planet lineages --set` did not exist before; it has been added.
- **The languages pass scales badly with the number of peoples.** At L6 the history took 11–14 min, and all outputs up to taboos about
  28 min. The languages pass ran more than 35 minutes after that and had not finished when we stopped it. The dnd tree's full run is about
  8 min at L6. The L7 runs skip that pass.
- **Memory is fine.** The L6 runs peaked at 3.6–5.2 GB (dnd L7 peaks at about 12 GB).
- **The history is faster with fewer peoples alive.** Peoples die: 679 s. Control: 835 s. Stems die too: 489 s.
- **Deep time assumes few roots.** Stems compete as single peoples in closed country, so a root that arrives late is crushed at birth (draft
  `late-root-crushed-at-birth`). The dnd tree, with three roots, never shows it.
- **The floors keep zombie peoples and hide stillbirths** (draft `zombie-peoples-under-the-floors`).
- **The tries score is meaningless for this tree.** The wish score fell to 0.247 in "stems die too", because most of the wishes name unborn
  peoples. LOST_PENALTY scoring with `--tries` above 1 would be dominated by extinctions.

## Reproduce

```
uv run python -m planet lineages 4360a3 --tree everyone --tries 1 --set HOLD_OUT_REFUGE=false          # peoples die
uv run python -m planet lineages 4360a3 --tree everyone --tries 1 --set HOLD_OUT_REFUGE=false EXTINCT_STEMS=true   # stems too
uv run python -m planet lineages 4360a3 --tree everyone --tries 1                                       # control
```
