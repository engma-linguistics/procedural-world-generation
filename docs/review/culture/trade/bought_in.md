# Bought-in foods in the culinary brief (PW-1505, design1.md step 4a; lane 235)

Design: [design1.md](design1.md) step 4a. (Not lane 224's [step4a.md](step4a.md), which is about craft goods; the step numbers drifted.)
Code: `planet/lineages/bought_in.py` (new), `planet/lineages/brief.py` (`Ctx.trade_flows`, `_trade_reach`, `_bought_in_md`;
`BRIEF_VERSION` 21), `planet/lineages/cuisine.py` (`sheet`, `bought_in`, and the staple, drink and fuel lines). Tests:
`tests/test_bought_in.py`. Harness: [bought_in/](bought_in/) (`setup.sh` builds a scratch data root of symlinks, `stats.py`,
`sample.py`). Screenshot: [the Culinary brief tab, desert humans of the south-east of Trojanel on 3e0eb4](bought_in_brief_3e0eb4.png).

**Baseline:** before this lane the brief's `trade_reach` was `null` and listed as "not modelled". No culture's brief said it bought
any food in. Every number below is new. Where a number is set against the real world, the comparison comes from this epic's
sourced review ([review1.md](review1.md), [step4b.md](step4b.md)), not from memory.

## In plain words

- **What it does.** A culture's cuisine sheet now has a **Bought in** line. It lists each food that reaches the culture from another
  culture, who sends it, how far it comes and by what road. Below the sheet, a **Bought-in food** section gives each food in full.
  The brief's JSON `trade_reach` holds the same rows. Both viewers show it, because both show the brief's text: the workbench's
  Culinary brief tab and the globe's "Culinary brief..." box. The trade tables under the brief were already there and are unchanged.
- **Where it comes from.** The trade model works out the exchange after the run (trade_flow.py; Daniel's D63: a read-out after the
  run). This step only reads it. It changes nothing in the history or in the exchange.
- **Foods counted:** grain, dried and salted fish, herd animals, salt, oil and wine, sugar, spices (with tea and cacao), seal and
  whale oil. Firewood and charcoal go on the fuel line.
- **The giver's own fields name the food.** "Oil and wine" from a giver that grows the vine is **wine**. From one that grows olives it
  is olive oil. "Spices" from a tea grower is **tea**. The drink line gains "wine bought in from ..." (or tea, cacao, date or palm
  wine) only where the culture does not grow that crop itself.
- **The road**, as a cook would say it:
  - by sea, by river, flown in (a flying people carried it);
  - by caravan (merchants over land: a third culture lies between and caravans or ships are known);
  - driven on the hoof (herd animals walk);
  - overland (a neighbour's market or barter);
  - as tribute (the culture takes it from peoples it rules, or a dragon's realm takes it from the peoples on its land).
- **The shares are rough.** "8%" means the giver meets the want of 8% of the culture's people for that food. It is not 8% of the
  diet: the exchange has no amounts eaten. The line also says how many go without, where 5% or more do. No sourced diet share was
  added. JUDGEMENT display cut-offs only: a giver is named from 1% of the people, and a food enters the staple, drink or fuel line
  from 5%.
- **Crops flyers bring** (Daniel's D65: flyers spread foods to new regions) are listed as "flown in by ...". These are crops the
  culture does not grow.

### Sample cultures (the present)

D&D showcase runs 3e0eb4 and a24559:
- **The desert humans of the south-east of Trojanel** (3e0eb4) buy salt from the fire giants of the south of Trojanel, **844 km by
  caravan**. It reaches 8% of their people; 71% go without. (The screenshot.)
- **The temperate dwarves of the west of Simath** (3e0eb4) buy chilies from the humans of the east of Trojanel, **3,529 km by sea**
  (29% of their people), and from the tritons of the east of Ratal, 4,010 km by sea.
- **The first dwarves of the east of Simath** (a24559) buy herd animals from the humans of Tobrosal, **3,204 km by sea** (8%; 34% go
  without). They buy chilies and tea, 5,038 km by sea.
- **The continental halflings of the north of Ratal** (a24559) buy salt from the first hill giants of the east of Ratal, **744 km
  by river**.
- **The orcs of the north of Tobrosal** (a24559) buy grain from the humans of Tobrosal, **176 km by river**. They buy wine and seed
  oil from the first sea elves of the south-west of Simath, next door.
- **The kobolds of Ratal (2)** (a24559) get chilies and tea flown in from the first halflings of the north-west of Ratal, 444 km.
  They get herd animals **driven on the hoof** 1,413 km.
- **The halflings of the north of Trojanel** (3e0eb4) buy wine and seed oil from the tabaxi of the east of Trojanel, 141 km by
  river. The aarakocra of the north of Trojanel fly in wheat, barley, lentils and peas, which these halflings do not grow.

Seven Meals runs 1e97dd and 07c755 (frozen: measured only, nothing tuned on them):
- **The half-orcs of the north of Thovalol** (1e97dd) buy wine from the first aarakocra of the east of Khika, **361 km by sea**.
  They take sap sugar as tribute from the humans of the north-west of Khika and of Thovalol, whom they rule.
- **The temperate kobolds of the north-west of Vazem** (1e97dd) buy salt from the first hill giants of the north of Vazem, **457 km
  by river** (17%; 54% go without). They buy chilies and cacao from the humans of the west of Vazem, 8,842 km by sea. Their drink
  line now ends "a cacao drink bought in from humans of the west of Vazem".
- **The gold dragons of the south-east of Lameth (4)** (1e97dd) take grain and herd animals as tribute from the hobgoblins, humans
  and leonin on their land. Their staple line now says so.

## Numbers on the stored L7 runs

Read-only, from a scratch data root of symlinks with its own `.godscache` (`bought_in/setup.sh`). The exchange docs were made once
per run on main's trade code (trade_flow VERSION 9), ~5 min each on 4 threads. All four runs have 26 eras from 12.5 kyr ago to now.
Shown here: the present and 5 kyr ago.

Cultures that trade (the ledger's trade mode), how many have at least one bought-in food (1% or more of their people supplied),
how many take some food as tribute, and how many have a crop flown in:

| run (tree) | era | trading cultures | with a bought-in food | take food as tribute | crops flown in |
|---|---|---|---|---|---|
| 3e0eb4 (D&D) | now | 224 | 189 | 72 | 36 |
| 3e0eb4 (D&D) | 5 kyr | 205 | 110 | 30 | 22 |
| a24559 (D&D) | now | 261 | 161 | 25 | 21 |
| a24559 (D&D) | 5 kyr | 243 | 58 | 14 | 14 |
| 1e97dd (Seven Meals) | now | 227 | 191 | 70 | 59 |
| 1e97dd (Seven Meals) | 5 kyr | 205 | 139 | 36 | 34 |
| 07c755 (Seven Meals) | now | 239 | 212 | 96 | 46 |
| 07c755 (Seven Meals) | 5 kyr | 190 | 125 | 34 | 21 |

How far each food comes at the present. Each giver row is weighted by its share times the taker's people. The table gives the
median km and, after the slash, the far tenth (p90):

| food | 3e0eb4 | a24559 | 1e97dd | 07c755 | sourced comparison |
|---|---|---|---|---|---|
| grain | 699 / 2,738 | 458 / 2,260 | 888 / 2,911 | 952 / 2,299 | ~100-200 km overland at most, thousands of km by water (review1.md section 6; Rome's grain from Africa and Egypt) |
| salt | 844 / 2,781 | 680 / 1,284 | 1,206 / 1,216 | 847 / 3,792 | Sahara 1,000+ km by camel (review1.md table, R§3-4) |
| wine (from vine growers) | 378 / 1,186 | 78 / 917 | 91 / 96 | 218 / 1,689 | (no sourced wine distance in this epic's review) |
| spices, tea, cacao | 5,141 / 8,607 | 5,473 / 9,024 | 2,541 / 5,189 | 2,213 / 4,687 | ~8,000 km, pepper Malabar to Rome (step4b.md, Pearson, Pliny) |
| herd animals | 1,897 / 3,628 | 2,961 / 3,840 | 423 / 2,034 | 608 / 1,949 | (PW-1532: horses' far haul still needs a source) |

The roads, as a share of the weight (the present): grain is 41-61% tribute, 22-29% river and 14-29% sea; overland and caravan are
under 2%. Salt goes by river, sea, caravan and overland, plus 13-66% tribute. Spices go 24-70% by sea. Herd animals are 8-48%
driven on the hoof, 3-30% by sea, and the rest tribute.

**Herders' grain** (cultures with 25% or more of their heads herding): at the present, 5 / 42 / 3 / 11 such cultures. People-weighted,
bought grain reaches 12% / 4% / 11% / 13% of their people. The ledger's grain lack is 17% / 42% / 16% / 17% (3e0eb4 / a24559 /
1e97dd / 07c755). So herders do buy grain on every run, with most of their lack left unmet on a24559. That matches PW-1511 (won't
do: the herders live far from the farmland).

## What makes sense and what does not

- **Inland salt makes sense.** It comes 700-1,200 km at the median, by river, caravan and overland, and most salt-buyers still go
  partly without. That is within the Sahara's 1,000+ km.
- **Spices make sense.** Their median is 2,200-5,500 km and their far tenth 4,700-9,000 km, mostly by sea. Pepper's ~8,000 km
  sets the far end. These are lane 226's numbers seen from the taker's side.
- **Wine stays near the vine.** Its median is 78-378 km, and its far tenth stays under ~1,700 km.
- **Salt fish never moves** (lane 244 since gave it a want: 43-74 cultures now buy it, [bought_in_244.md](bought_in_244.md)). Before it, no culture on any of the four runs buys dried or salted fish. The goods ledger writes no want for
  it (trade.py: "dried fish, obsidian and sea-mammal oil: no need written yet"). So "salt fish far inland" cannot appear. This is
  draft 1.
- **Grain goes too far by sea in the tail.** Some cultures get grain over 6,000-10,000 km of sea. Examples on 3e0eb4: the continental
  gnomes of the west of Simath, 6,296-7,997 km; the first kenku of the south of Simath, 10,604 km. Bulk goods pay freight alone at sea (trade_flow.HAND_KM
  leaves bulk out, a JUDGEMENT of lane 225). The longest sourced bulk route in the review is Rome's grain fleet, from Africa and Egypt.
  The far tenth (2,300-2,900 km) is near that, but the tail is not. This is draft 2. The shares in that tail are small (1-4% of a
  culture's people), so the brief names it but it does not dominate.
- **Tribute is a large share of food moved.** It is a ruler taking food from the cultures it rules (trade_flow.kind_of reads the
  polities), and a dragon's realm or a tribute giant taking from the peoples on its land. The brief says "takes as tribute" rather
  than "bought".

## Not done here

- Food words travelling with the food (PW-984) can now follow `trade_reach` (giver, km, road per food). Not started.
- The culinary side's own amounts (how much of the diet is bought) need the exchange to carry amounts. It carries shares of people
  supplied. Not attempted. No sourced diet share was added.
- `RIVER_COURSE` (lane 226's measured, left-off switch) would move some of the grain rows from river to sea or drop them. Nothing here
  depends on it.

## Tests

`tests/test_bought_in.py` (three new: foods, givers and roads; the giver's fields naming the crop good and the drink; the sheet's
lines). Run with the brief-, cuisine-, trade- and lineages-area files (`-n 2`, `-m "not slow"`): 279 passed.
