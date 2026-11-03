# Foragers who trade with farmer neighbours (PW-1386, round 1)

Lane 146, 2026-11-03. Baseline = main cfd7d1cf; after = this branch. The same 6 runs of `tools/peoples_robust.py` each (D&D preset,
family base, arm now, seeds 7/10/13, worlds 4360a3 and af2677, one try each, end of the history ~1500 AD). Table from `compare.py` here.

## In plain words

- **What changed.** A people that hunts and gathers and has taken up no crop now gets part of its food by trading with farming
  neighbours (meat, forest goods and work for grain or cassava), as the Mbuti, Efe and Aka do with the villages of the Congo forest.
  The more farmers within about a day's walk, the bigger the share, up to half its foraging food. Half of the food means twice as many
  people can live on the same land. Fishers on rich waters, herders, farming peoples, den peoples (they raid) and dwarven holds are
  left as they were.
- **The number comes from the sources.** Forest foragers living beside farmers get "about 50%" of their energy from farm food
  (Kitanishi 1995), over 60% of their food by weight among the Mbuti (Ichikawa 1983); single camps range 11-63%. Away from farmers the
  share falls to nothing (the Baka lived months on wild food alone, Yasuoka 2004). No source gives how the share rises with the
  farmers' density, so the half point (5 farmers per km2 nearby) is my judgement, as it is for the den peoples' raids.
- **What it does at the end of the history (~1500 AD)**, against the same 6 runs on main: the forager peoples' people rise 0-2%
  (4.6 to 15 million per run); traded farm food is 0.2-2.4% of their food; the total number of people rises 0.004-0.010%, and the
  largest people's share is unchanged (to 0.1 point) in every run. The suite's checks hold on the branch as on main: 0 failures, 0 crashes, 0 peoples extinct, none over 85%.
- **Why so small:** 37-48% of the forager peoples' people do live within reach of 5+ farmers per km2, but by 1500 AD most forager
  peoples left in the D&D preset are coastal fishers (tortles, tritons, sea elves, lizardfolk) or herders (leonin), and the trade
  tops up only the hunting-and-gathering part of their food, which on rich coasts is smaller than the fishing. Whether fishers and
  herders should trade too is a decision draft (`draft-barter-with-herders-and-fishers.md`; my lean: not until a source is read).

## What changed

- `planet/lineages/ladder.py`: a **forager people** (one that has taken up no crop; not a den people, who raid instead, and not a hold)
  gets a share b of its foraging food from farmers within reach: its foraging rung becomes forager / (1 - b), with
  b = BARTER_CAP x F / (F + BARTER_HALF), F the farmers' people per km2 averaged over BARTER_REACH rings of neighbours
  (`Ladder.farmers_near`, the den peoples' `settled_near` counting farmers only). BARTER_CAP 0.5, BARTER_HALF 5 /km2, BARTER_REACH 1.
  Mechanically the den peoples' raiding share (RAID_*), on the forager rung only.
- What it leaves alone: fishing on rich waters (where fish lead, the cell keeps its own number), the rich-land and herding choices of
  PW-1385 (they read the land's own wild, never the bartered top-up), peoples that farm (their foraging fringe gets no trade from their
  own fields), den peoples and holds. With no farmers near, the numbers are the same to the bit (the test checks it).
- `Ladder.barter` holds the bartered part of each cell's food per line; `tools/peoples_robust.py::forage_land` now reports per people
  `forager_pop` and `traded_pop`. `ranges.py::FIXED` lists the three constants (not drawn: below).
- One small fix on the way: the farmers-near map is kept between the ladder's full refreshes, so a forager line whose tech moves in
  between (a herd animal) keeps its trade. The den peoples' raids have the same gap; that is a draft (it changes their numbers).

## Which foragers: any forager people, not only forest ones

All the cases read are rainforest foragers (Mbuti, Efe, Aka, Baka), and the "wild yam question" debate is about the rainforest. But the
mechanism the sources describe (meat, honey, forest goods and farm labour for farm food) needs farmers next door, not a forest, and a
forest-only rule would need a biome read in the ladder for a difference no source measures. So the share goes to any forager people,
and rises only where farmers are near; in the runs (below) it falls mostly where the forager peoples meet farming kinds. Herders as
trading partners and fishers trading fish are left out (no source read): draft `draft-barter-with-herders-and-fishers.md`.

## The sources

Every number was read in the paper linked; page numbers are the printed ones.

- **Ichikawa, M. 1983.** An examination of the hunting-dependent life of the Mbuti Pygmies, eastern Zaire. *African Study Monographs*
  4: 55-76 ([Kyoto repository](https://repository.kulib.kyoto-u.ac.jp/dspace/handle/2433/68001)). p. 55: the Mbuti "provide the
  agriculturalists with meat from the forest and manpower for agricultural works in exchange for metal works and farm foods ... Today,
  they depend for more than 60 % of total food weight on farm products, such as cassavas and plantains". p. 63: one gutted blue duiker
  (2-3.5 kg) "was exchanged for 15 kg of cassava. In this case 2,500 to 4,000 Cal of meat were exchanged for 12,000 Cal of cassava":
  the trade multiplies the hunters' calories three- to fourfold.
- **Kitanishi, K. 1995.** Seasonal changes in the subsistence activities and food intake of the Aka hunter-gatherers in northeastern
  Congo. *African Study Monographs* 16(2): 73-118 ([Kyoto repository PDF](https://repository.kulib.kyoto-u.ac.jp/server/api/core/bitstreams/a4f96cca-d6dd-4d06-8741-3feb5e9498ff/content)).
  - p. 106: in the forest camp at Linganga-Makaou "Agricultural food accounted for only 18% by weight, or 22% by energy. In contrast,
    agricultural food accounted for about 50% of total energy intake for other hunter-gatherers".
  - Table 11, p. 107, percent of energy in the forest camp from agricultural food (oil palm apart): Mbuti 11.0 (early rainy season,
    the honey season, Ichikawa 1981) and 63.3 (dry season, Ichikawa 1986); Efe 40.7 (+9.6 oil palm; Bailey & Peacock 1988) and 33.9
    (+3.3; Sawada 1990); Aka 11.1 (+11.1).
  - Table 5, p. 89: the Aka group spent 42.6% of person-days in the forest camp and 51.6% in the village camp, where (p. 107) they
    "provide agricultural work to the villagers, and mainly eat agricultural food". So even this least farm-fed group eats farm food
    for a good part of the year.
  - p. 107, Bahuchet (1988) as reported: for the Aka of Lobaye "agricultural food also accounted for about a half of total food intake
    (agricultural food 55%, wild food 45%)" (frequency in meals); and dependence on farm food "is related to the distance from the
    village to the camp": camps 5-8 hours' walk away ate more wild food, camps 3-4 hours away more oil palm and cassava leaves.
    (Secondary: Bahuchet 1988 itself was not read.)
  - p. 109: where the villagers hunt with guns themselves, the Aka "cannot obtain much agricultural food from the exchange of meat"
    (Tanno 1991, as reported): the share depends on what the farmers want.
- **Yasuoka, H. 2004.** Long-term foraging expedition and subsistence of the Baka in northwestern Congo Basin. *Asian and African Area
  Studies* 4(1) ([Kyoto repository PDF](https://repository.kulib.kyoto-u.ac.jp/server/api/core/bitstreams/99b16542-9610-4450-8694-f258925fadcf/content)),
  English abstract p. 36: on a two-and-a-half-month expedition (molongo) "the Baka subsisted solely on wild food resources, wild yams in
  particular, although it was during the dry season". So the share goes to 0 away from farmers; foraging alone feeds them.

**What the sources give, and what they do not.** The cap is sourced: the farm-food share of forest foragers who live beside farmers is
"about 50%" of energy (Kitanishi), 55% of meal items (Bahuchet), over 60% by weight (Ichikawa); single camps range 11-63%. BARTER_CAP
0.5 takes the "about 50%". **No source read relates the share to the farmers' density.** The one relation is distance (Bahuchet via
Kitanishi), qualitative. So BARTER_HALF (5 farmers per km2 within reach, as RAID_HALF: a gardening-village country) and BARTER_REACH
(one ring: a day's walk to the village is within one ~60 km cell's neighbours) are judgements, labelled as such in the code.
Not read (paywalled or no open copy found): Bailey & Peacock 1988, Bailey et al. 1989 (*American Anthropologist* 91: 59-82),
Hart & Hart 1986, Headland & Reid 1989 (*Current Anthropology* 30: 43-66), the *Human Ecology* 19(2) 1991 forum, and Agta numbers
(the Agta profile read, [dice.missouri.edu](https://dice.missouri.edu/assets/docs/austronesia/agta.pdf), says only that they "mainly
depend on trade for carbohydrates", with no share). Draft `draft-barter-source-the-density-relation.md`.

**Why a cap, and why density = forager / (1 - b).** As for the raids: the wild part of the diet is what the land feeds, and the traded
part comes on top of it, so a people getting half its food by trade can be twice as dense on the same forest. Ichikawa's arithmetic (one
duiker's 2,500-4,000 kcal for 12,000 kcal of cassava) shows trade can do more than that per hunter; the cap keeps the observed share,
not the most trade could give. Not drawn under `meta.draw_ranges`: the 11-63% is the spread of shares observed at given camps and
seasons, not a range for the most a people gets.

## Measured

**Baseline:** the same 6 runs on main cfd7d1cf (its code exported to scratch, with only the forager-people count added to the tool:
the branch's `ladder.barters` written out, no crops and not a den people or hold; no trade, so its traded share is 0). **After:** this
branch. `uv run python tools/peoples_robust.py run --out DIR --family base --trees dnd --seeds 7,10,13 --arms now` (both worlds),
`compare.py MAIN_DIR BRANCH_DIR`. Forager peoples' people = all the people of peoples that have taken up no crop (not den peoples or
holds), on whatever rung; traded share = the people their traded farm food feeds over their people.

| run | all people (main -> branch) | forager peoples' people | traded share of their food | people on a wild rung (all peoples) | top people's share |
|---|---|---|---|---|---|
| 4360a3 s7 | 1.07e9 -> 1.07e9 (1.000) | 1.39e7 -> 1.40e7 (1.01) | 0% -> 0.7% | 3.85e7 -> 3.86e7 (1.00) | 27.7% -> 27.7% |
| 4360a3 s10 | 1.09e9 -> 1.09e9 (1.000) | 5.74e6 -> 5.83e6 (1.02) | 0% -> 1.6% | 4.09e7 -> 4.10e7 (1.00) | 24.4% -> 24.4% |
| 4360a3 s13 | 1.32e9 -> 1.32e9 (1.000) | 5.40e6 -> 5.53e6 (1.02) | 0% -> 2.4% | 3.44e7 -> 3.45e7 (1.00) | 41.7% -> 41.7% |
| af2677 s7 | 6.98e8 -> 6.98e8 (1.000) | 1.51e7 -> 1.51e7 (1.00) | 0% -> 0.2% | 2.53e7 -> 2.53e7 (1.00) | 22.9% -> 22.9% |
| af2677 s10 | 1.26e9 -> 1.26e9 (1.000) | 4.57e6 -> 4.65e6 (1.02) | 0% -> 1.8% | 3.07e7 -> 3.08e7 (1.00) | 26.5% -> 26.5% |
| af2677 s13 | 9.93e8 -> 9.93e8 (1.000) | 1.49e7 -> 1.49e7 (1.01) | 0% -> 0.6% | 2.38e7 -> 2.39e7 (1.00) | 20.5% -> 20.5% |

Per people (branch, traded share of its food): lizardfolk 0.9-4.2%, tortles 1.0-2.8%, tritons 0.6-3.3%, aarakocra 0.5-1.9%, sea elves
0-1.8%; leonin 0.0% (7.6-10 million people, almost all herding: the trade reaches only the foraging part). One small case, tabaxi on
af2677 seed 7 (7,600 -> 9,500 people), gets 19.7%.

**Invariants** (`peoples_robust.py report`): main 6 runs, branch 6 runs, each 0 failing, 0 crashes, 0 peoples extinct, 0 over 85%;
the top people and its share the same in every run (largest 41.7%, humans on 4360a3 seed 13).

**Who is near farmers** (a re-run of 4 of the branch runs, seeds 7 and 13, with the tool also counting the forager peoples' people within
reach of 1+ and 5+ farmers per km2; the re-runs gave the same total people to the last digit): 37-48% of forager peoples' people live
within reach of 5+ farmers per km2. The traded share stays at 0.1-2.3% because in most of those cells fishing out-feeds hunting and
gathering, and the trade tops up only the latter (a cell keeps max(fishing, foraging / (1 - b))), or the people herds there.

**Not isolated:** one try per run; at these sizes (forager peoples ~1% of all people) the history barely moves, so the differences are
the trade itself rather than a different history (total people within 0.01% in all six).

## Tests

`tests/test_lineages.py::test_foragers_trade_with_farmer_neighbours`: with no farmers near the forager line's density is the same to
the bit as without trade; at BARTER_HALF the forager cells stand at forager / (1 - BARTER_CAP/2) and their bartered share is
BARTER_CAP/2; fishing-led cells keep their own number and no bartered share; with very many farmers near the share approaches but
stays under the cap; a people that knows crops and a den people never barter; `farmers_near` is 0 with nobody present.
Not-slow lineages + robust + golden tests: 139 passed (the golden test passes without an update). Full suite (`uv run pytest -q -n 4`): 957 passed, 2 skipped.
