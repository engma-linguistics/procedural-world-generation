# Tech tree round 3: neighbour lags, state techs need towns, the sea peoples' branch (PW-1490, PW-1491; lane 207)

**Baseline.** The baseline is main at faa4fb8c (contact arms "BT"). Every number below comes from rebuilding the tree in memory over a
stored run's history. There are 8 draws per run (the run's seed plus the next 7) on 0141d1 and 3e0eb4 (D&D, both on world 899985) and
07c755 (Seven Meals, measured only, not tuned).

The two changed trees are:
- **arm S:** the baseline plus D60 B.
- **final:** arm S plus the sea branch.

Scripts:
- [round3/lag.py](round3/lag.py): rebuilds the tree; read-only on runs/.
- [round3/tables.py](round3/tables.py): the tables below.
- [round3/tail.py](round3/tail.py): what drives the slow tail.

## In plain words

- **Daniel's worry, measured.** The worry was a people in suitable land, surrounded by neighbours who have a tech, that goes hundreds
  of years or more without it.
  - **It almost never goes without it for good.** Take a people that has the land, the body and the prerequisites, and whose
    neighbour got a tech more than 2,000 years ago. Today it lacks that tech in 0-1% of cases, on all three runs.
  - **But "hundreds of years" is the norm, not the exception.** The median wait after the neighbour has it is about 400-700 years
    for a tech of 5,000-2,000 years ago. It is about 1,000-1,250 years before that. Even with the prerequisites in hand, only 0-5%
    are taken up within a century.
- **Why the waits are that long: it is mostly the model working as designed.**
  - A people "takes up" a tech when the front has crossed to the middle of its country, at about 1 km a year. That is the
    Neolithic farming front (Pinhasi et al. 2005).
  - A D&D people is a macro-people of 3-30 million km². Crossing half of one takes centuries to a couple of thousand years.
  - The slow tail sits with:
    - **older eras:** for techs ready over 20,000 years ago the median wait is about 2,600 years, because the steps are coarse and
      the borders short then;
    - **short borders:** under 300 km of shared border, the median is 1,000-1,500 years;
    - **bigger takers:** the wait grows with the taker's area.
  - Insularity matters little.
  - The slow tail is everyday stone-age techs among the giants, goblins and bugbears, not the ladder.
- **Compared with Earth** (sources fetched today, section 4): these are the same order as Earth's.
  - Iron took about 500 years from the Aegean to Ireland.
  - Paper took about 1,000 years from China to Spain, at 40-650 years a hop.
  - Writing reached the Indus and the Aegean 700-1,500 years after Mesopotamia.
  - Printing is the fast outlier: 205 cities in 50 years.
  - So the lags are not too short. The old problem was elsewhere: *everyone* ended up with *everything* (spread1).
- **D60 B is built** (arm S, on by default).
  - **The state techs** are writing, kingship, law, taxation, census, bureaucracy and coinage. A people invents, takes up, shares or
    inherits them only while it has a town of its own in the settlement ledger.
  - **Why that set.** These are the techs that only work inside a standing hierarchy with a centre: records, rulers, courts,
    taxes. The Atlas's "3+ levels of authority" (states) is the trait they stand for. The alphabet, paper and printing need writing,
    so they follow on their own.
  - **What it does not gate.** Chiefdoms and towns themselves are not gated. They are what a people has to build first.
  - **No number to tune.** The front still arrives as before. A people that founds a town takes up a tech already at its border at
    once.
- **Its effect, at 0.5 kyr ago** (the closest date to Earth's 1500 CE):
  - **Writing and kingship:** held by 72% of peoples with hands on 0141d1 and 3e0eb4, and 44% on 07c755. The baseline was 94-97%.
  - **Farming:** 96-97% on every run, unchanged.
  - **Fast techs** (farming, copper, bronze, iron, towns, cities, pottery, plough) are identical to the baseline in every draw.
  - **Who now lacks writing:** peoples without towns of their own (foragers, herders, groups and small peoples). Their wait is
    3,500-4,700 years and mostly "never".
  - **Settled peoples** keep their old pace: median 523 years on 0141d1 (baseline 456), 465 on 07c755 and 467 on 3e0eb4.
  - **What it does not do:** it does not create long lags for settled peoples in suitable land, with one wrinkle. On the D&D runs,
    11-15% of the settled cases still lack a state tech today, against 7% before. About a third of those had towns that later
    shrank away, so the gate rightly closed again. The rest are downstream state techs (law, coinage) whose givers are now fewer.
    That is the draft below.
  - **Side effect:** printing at 0.5 kyr ago fell from 72% to 7% of peoples on 0141d1 (median of draws), because it needs writing's
    whole chain. It still reaches 62% on 3e0eb4 and 28% on 07c755.
- **The Ethnographic Atlas and our present-day finish.**
  - **Its period.** The Atlas describes each society at the earliest good description of it. That is 1900-1950 for 69% of
    societies, the 19th century for 25%, before 1800 for 3%, after 1950 for 2% (Kirby et al. 2016). Its "present" is therefore
    roughly 1850-1950, later than our finish's era cap (renaissance) but close enough to use as a loose guide for the periphery.
  - **By culture count:** states are 11% of its cultures. We now have 44-72% of peoples with kingship, down from 94-97%. Ours is
    still higher, as it should be: a D&D people is a macro-people, not an ethnic group.
  - **By population:** writing and kingship cover 98-99% of the D&D population and 58% of Seven Meals'.
  - **Not a target.** We did not tune toward the Atlas.
- **The sea peoples' branch (PW-1491).**
  - **What it is:** 16 techs: reef and shelf foraging, shell, bone and coral tools, kelp cord, vent cooking (the sea's fire),
    shellfish beds and kelp gardens (the sea's farming), reef villages, pearl and nacre crafts, coral-lime building, vent ores,
    vent smelting, vent-cast copper and bronze, reef towns, shell and knot-cord records, tide councils, and an incised-shell
    script.
  - **Where the goods come from:** the world's own data, read in new sea goods:
    - the shelf, by depth;
    - reefs, kelp and seagrass, by the world's cover layers;
    - vents, by the sea-floor sulphides the resources model already puts on today's spreading ridges.

    These are real tectonic ridges, not a proxy.
  - **Who gets it:**
    - sea peoples: the merfolk and storm giants, plus the coastal swimmers (tritons, sea elves, deep folk);
    - land peoples: pearl and nacre crafts only, by trade.
  - **Merfolk** (07c755) now climb to reef towns in 6 of 8 draws. Vent smelting comes in 3 of 8, records and script in 1 of 8.
  - **Years behind on the world clock** shrink only a little, because the branch is small next to the ~500 land techs:
    - merfolk: 23,300 to 19,100;
    - storm giants: 11,400 to 10,600 on 07c755, and 11,800 to 11,700 on 0141d1 and 3e0eb4, where their country has fewer vents.
  - **Seven Meals** has merfolk, deep folk and storm giants. The branch applies to them as data, and nothing was tuned.

## 1. Neighbour lag (PW-1490)

**Definition.**
- **The cases:** each living people with hands, and each tech its land and body allow (goods held or the tech traded, the grip,
  not one single crop or beast, spread > 0).
- **Exposure:** the first date a neighbour in contact held the tech while the people was alive.
- **Lag:** the exposure date minus the people's own date for the tech. If it still lacks the tech, the lag runs to today ("never").
- **Ready:** the later of exposure and the date it held all the tech's needs.
- **Kinds:**
  - farming: cultivation, herding, plough, irrigation, storage, grinding;
  - metal: native copper to steel;
  - admin: the state set plus the alphabet.
- **Pooling:** cases are pooled over the 8 draws.

**Lag from ready, baseline (main)**: the median lag of the taken cases / the share at 1,000 yr or more / the share never taken.

| kind | era of ready | 0141d1 | 3e0eb4 | 07c755 |
|---|---|---|---|---|
| farming | > 5 kyr ago | 1,161 / 58% / 0% | 1,119 / 53% / 0% | 1,044 / 54% / 0% |
| farming | 5-2 kyr ago | 422 / 9% / 0% | 538 / 7% / 0% | 241 / 0% / 0% |
| metal | > 5 kyr ago | 840 / 40% / 0% | 754 / 37% / 0% | 591 / 19% / 0% |
| metal | 5-2 kyr ago | 542 / 19% / 0% | 518 / 13% / 0% | 425 / 11% / 0% |
| metal | last 2 kyr | 481 / 11% / 20% | 392 / 8% / 14% | 363 / 0% / 0% |
| admin | > 5 kyr ago | 755 / 35% / 0% | 630 / 20% / 0% | 527 / 9% / 0% |
| admin | 5-2 kyr ago | 523 / 18% / 0% | 448 / 12% / 0% | 440 / 9% / 0% |
| admin | last 2 kyr | 404 / 12% / 27% | 379 / 13% / 13% | 351 / 8% / 8% |
| all techs | > 5 kyr ago | 1,247 / 61% / 0% | 1,171 / 58% / 0% | 1,014 / 51% / 0% |
| all techs | 5-2 kyr ago | 694 / 30% / 1% | 633 / 24% / 1% | 520 / 17% / 0% |
| all techs | last 2 kyr | 461 / 15% / 32% | 431 / 11% / 31% | 405 / 9% / 17% |

- "Never" in the last 2 kyr is censored: the front is still on its way.
- Taken within 100 years: 0-8% in every row.
- Counted from exposure instead of from ready, the waits are longer: the "all techs" median is 1,300 / 817 / 641 years on 0141d1.
  The extra time is the prerequisite cascade.

**What drives the tail** (0141d1; taken cases, lag from ready; tail.py; 07c755 is alike):

| driver | bin | median lag (yr) | lag of 1,000 yr or more |
|---|---|---|---|
| ready date | 0-2 kyr ago | 458 | 12% |
| ready date | 2-5 | 698 | 30% |
| ready date | 5-10 | 911 | 44% |
| ready date | 10-20 | 1,169 | 61% |
| ready date | > 20 | 2,692 | 91% |
| border with the first holder | < 300 km | 1,035-1,215 | 51-61% |
| border with the first holder | > 1,500 km | 820 | 40% |
| taker's range | < 1 Mkm² | 626 | 21% |
| taker's range | 3-30 Mkm² | 860 | 43% |

**The cause in the model.** The lag is techtree.contact_rate: the front crosses half the taker's width at 1 km/yr, times the border
share and openness. Deep-time steps are also coarse: the steps are log-spaced, so 20 kyr ago one step is about 600 years.

**The peoples in the tail** are hill, cloud and frost giants, bugbears, goblins, goliaths, firbolgs and kenku. 69% of the cases have
no set way of life, and 76% have no towns at the ready date.

**The techs in the tail** are the stone-age everyday kit: oil lamps, tailored clothing, digging sticks, microliths, grave goods.

So no subsystem is stuck. The tail is big peoples on short borders in deep time.

## 2. D60 B: state techs need towns of one's own (arm S)

**What it does.**
- `state = true` marks writing, kingship, law, taxation, census, bureaucracy and coinage in techtree.toml. The arm is on by default:
  contact_arms "BST".
- `Calendar.settled(people, ago)` asks whether the people has at least one town cell in the town footprint:
  - after the run, the footprint is the settlement ledger's (techspread.town_footprint);
  - inside the history, it is the live polities' seats (tech_live).
- With no footprint at all, the people's way of life decides: not forager, fisher-forager, hunter, pastoral nomad, nomadic, sea
  nomad or transhumant.
- The gate applies to inventing, taking up, sharing within a people and inheriting at a split.
- `output.save` already builds the tree twice for the town arms. The ledger reads none of the state techs, so it settles after one
  round.

**Share of today's peoples with hands holding the tech at 0.5 kyr ago** (median of 8 draws; [min-max]):

| tech | 0141d1 base | 0141d1 S | 3e0eb4 base | 3e0eb4 S | 07c755 base | 07c755 S |
|---|---|---|---|---|---|---|
| cultivation | 97% | 97% | 97% | 97% | 96% | 96% |
| copper | 97% | 97% | 93% | 93% | 90% | 90% |
| iron | 90% [3-97] | 90% [3-97] | 86% | 86% | 90% | 90% |
| towns | 97% | 97% | 97% | 97% | 94% | 94% |
| cities | 97% | 97% | 97% | 97% | 94% | 94% |
| writing | 97% [21-97] | 72% [17-72] | 97% | 72% [69-76] | 94% | 44% [42-44] |
| kingship | 97% | 72% | 97% | 72% | 94% | 44% |
| law | 97% | 62% | 95% | 60% | 93% | 42% |
| coinage | 48% | 16% | 78% | 41% | 88% | 39% |
| printing | 72% [0-97] | 7% [0-66] | 76% | 62% | 92% | 28% |

Every tech without the flag, and not downstream of one, is identical draw for draw.

**Admin techs, lag from ready (or from the first town, if later)**: the median / 90th percentile / never.

| taker | 0141d1 base | 0141d1 S | 3e0eb4 S | 07c755 S |
|---|---|---|---|---|
| settled | 456 / 1,155 / 7% | 523 / 1,467 / 15% | 467 / 1,691 / 11% | 465 / 1,060 / 1% |
| not settled | 551 / 1,223 / 5% | 3,500 / 5,340 / 88% | 3,796 / 5,171 / 87% | 4,710 / 5,452 / 100% |

**At the present, against the Atlas** (share of peoples with hands / share of population):

| | 0141d1 | 3e0eb4 | 07c755 | Atlas (cultures) |
|---|---|---|---|---|
| cultivation | 97% / 100% | 97% / 100% | 96% / 100% | 80% (EA028 ≠ 1) |
| copper (any metal) | 97% / 100% | 93% / 100% | 90% / 99% | 46.5% (EA055) |
| kingship (states) | 72% / 98% | 72% / 99% | 44% / 58% | 11% (EA033 = 4-5) |
| writing | 72% / 98% | 72% / 99% | 44% / 58% | (no Atlas variable) |
| a town of its own now | 62% | 48% | 44% | |

The Atlas shares are spread1's, computed from the D-PLACE files.

## 3. The sea peoples' branch (PW-1491)

**Goods** (land.SEA_GOODS, sea cells, carried to the coast's land cells):

| good | how it is made | kind |
|---|---|---|
| shelf | depth 0-200 m full, gone by 400 m | area |
| reef | reef cover / 5% | point |
| kelp_beds | max(kelp, seagrass) cover / 10% | point |
| vents | res_vms at sea: resources.py puts 0.6 on every sea cell at today's divergent plate boundary | point |

These are world layers, not a proxy. A sea people's country held none of the old goods. Now on 07c755 the merfolk hold kelp beds,
reef, shelf and vents, and the storm giants kelp beds, shelf and vents.

**The techs** (all fantasy, `sea = true`; dates are the nearest land analogue's, named in each `source`):

```
sea_foraging -> shell_tools, kelp_cordage, vent_cooking, shellfish_beds
shellfish_beds -> kelp_gardens, reef_villages
shell_tools + shellfish_beds -> pearl_crafts (traded to land peoples)
reef_villages + shell_tools -> coral_lime
vent_cooking + shell_tools -> vent_ores -> vent_smelting -> vent_bronze
reef_villages + kelp_gardens + coral_lime -> reef_towns -> shell_tallies -> tide_councils, shell_script
```

**Who may hold them.** A sea people (techtree.is_sea): realm coast or sea, or swims and coastal. A land people may take only
pearl_crafts, by contact.

The incised-shell script is gated by the sea people's own reef towns, not by arm S: the settlement ledger builds no places at sea.

**Before and after** (years behind the world clock, spread1's measure; median of 8 draws):

| run | people | techs held, base | techs held, final | behind, base (yr) | behind, final (yr) | sea techs held (median) |
|---|---|---|---|---|---|---|
| 07c755 | merfolk | 79 | 90 | 23,300 | 19,126 | 11 of 16 (reef towns 6 of 8 draws) |
| 07c755 | storm giant | 106 | 117 | 11,357 | 10,635 | 11 of 16 |
| 07c755 | deep folk | 422 | 426 | 3,229 | 3,115 | 11 of 16 |
| 0141d1 | storm giant | 102 | 108 | 11,773 | 11,700 | 5 of 16 (fewer vents and kelp) |
| 3e0eb4 | storm giant | 102 | 106 | 11,773 | 11,700 | |
| 0141d1 | triton / sea elf | 380 / 390 | 379 / 384 | 2,467 / 2,104 | 2,511 / 2,140 | ~6 of 16 |

The tritons and sea elves are coastal land peoples and hold the land ladder too. Their small moves are draw scatter and arm S.

## 4. Sources (fetched 2026-11-07)

- **Ethnographic Atlas period.** Kirby et al. 2016, "D-PLACE", PLoS ONE 11(7): e0158391
  (journals.plos.org/plosone/article?id=10.1371/journal.pone.0158391): "The 'focal year', i.e., the time period to which the cultural
  data refer is before 1800 for 3% of societies, in the 19th century for 25%, between 1900 and 1950 for 69%, and after 1950 for 2%".
- **How the Atlas codes each society.** Giuliano and Nunn 2018, Econ. Hist. Dev. Regions 33(1)
  (nathannunn.sites.olt.ubc.ca/files/2022/07/nathannunn_Ancestral-Characteristics.pdf): "coded for the earliest period for which
  satisfactory ethnographic data are available".
- **Iron in the Near East.** Erb-Satullo 2019, J. Archaeol. Res. 27:557-607: smelted iron in Anatolia "beginning a little after 2000
  BC" through "widespread adoption by circa 600 BC"; "the centuries-long adoption process following the first appearance in a
  region".
- **Iron in Europe.** Wikipedia (secondary), "Iron Age Europe": "Iron working was introduced to Europe in the late 11th century BC";
  "the Iron Age of Prehistoric Ireland begins around 500 BC".
- **Paper.** British Association of Paper Historians, "Early history of paper" (baph.org.uk): AD 105 (Ts'ai Lun, by tradition),
  Samarkand 751, a Baghdad factory in 793, Xativa "poss 1056", Genoa 1255. Also Bloom 1999, Aramco World 50(3): "the first Spanish
  paper mill is documented at Jativa in 1056".
- **Printing.** Dittmar 2011, QJE 126(3):1133-1172 (people.bu.edu/chamley/764-23/Dittmar.pdf): "205 unique cities that adopted the
  printing press 1450–1500"; "Distance from Mainz was strongly and significantly associated with early adoption".
- **Writing.** Wikipedia (secondary), "History of writing": Mesopotamia c. 3400-3100 BC, Egypt c. 3250 BC, the Indus c. 2600 BC,
  Linear A c. 1800 BC.
- **Farming front.** Pinhasi, Fort and Ammerman 2005, PLoS Biol 3(12): e410: "The average rate of the Neolithic spread over Europe is
  0.6–1.3 km/y (95% confidence interval)."
- **Not found:** a quantitative source saying states spread more slowly than farming. Nothing above relies on one.
