# Trade step 4b: what bounds a sea haul (lane 225; the inbox draft on the long-haul network's size after PW-1529)

Step 4a: [step4a.md](step4a.md). Code: `planet/lineages/trade_flow.py` (`HANDS`, `HAND_KM`, in `_Frame.cost`; doc version 8). Test:
`tests/test_trade_routes.py::test_a_sea_km_costs_a_share_of_value_for_the_hands`. Judge: step 4a's ([step4a/judge.py](step4a/judge.py)),
unchanged, with `NOCOST=1` (the land nudge only, as in step 4a), one judge at a time on 4 cores.

**Baseline everywhere: main fe063817** (lane 224 merged), judged on the same machine in the same hour with `HANDS = False`, which is
main's code exactly. Runs 0141d1, 3e0eb4 (D&D) and 07c755 (Seven Meals), L7, 26 frames from 12.5 kyr ago. The main numbers below match
step4a.md's to the km, so the judge reproduces lane 224's.

## In plain words

- **The problem.** In main, goods sail anywhere: spices a median ~8,000-11,800 km, cloth 6,500-7,700 km on two runs, horses 4,900-6,200 km,
  the far tenth of most goods' flows 3,500-15,000 km, nearly all by sea. A ship's freight is 1/28 of a donkey's per km (ORBIS), and the
  fall-off lengths were set from overland hauls, so a dear good's budget was ~150,000 km by ship.
- **What really bounded a long sea haul (section 1).** Not freight. The price chains show it: pepper cost 1-2 g of silver a kilo where it
  grew, 10-14 at Alexandria and 20-30 in Europe (Pearson); Indian wares sold in Rome at "a hundred times their prime cost" (Pliny). Over
  Malabar to Alexandria that is about one e-fold of value every ~2,900 km, almost none of it freight. The cargo passed from merchant to
  merchant at each emporium, each paid for a season of capital, the voyage's risk and his margin. On land the model already charges
  these hands: the fall-off lengths come from whole overland markups, and every culture's border takes a toll. At sea there is no border,
  so a 10,000 km voyage paid one harbour due and nothing else.
- **The mechanism (built).** A km at sea now also costs a share of the cargo's value: its value e-folds every **3,000 km** at sea for
  middling and dear goods (JUDGEMENT within the sourced 1,800-8,300 km), on top of the freight. Bulk goods (grain, timber, firewood,
  stone, dried fish) keep freight alone: their sourced sea cost is freight (wheat ~1.3% of value per 100 Roman miles by sea), which ORBIS
  already gives, and they went port to port in one hull.
- **What it does** (median km of each good's flows between cultures, main → now, 0141d1 / 3e0eb4 / 07c755):
  - cloth 7,737 → 339 / 216 → 153 / 6,518 → 155; the far tenth 11,896 → 2,041 / 5,019 → 1,768 / 12,940 → 2,399;
  - horses 5,213 → 2,814 / 4,922 → 1,717 / 6,210 → 1,561; far tenth ~11,000-17,000 → ~4,200-4,700;
  - spices 11,757 → 6,918 / 11,551 → 8,160 / 8,094 → 5,187; far tenth ~18,000-20,000 → 9,700-14,600;
  - silk, dyes, silver, gold, incense: far tenth now 2,000-3,800 km (main 2,800-15,000);
  - grain: unchanged (1,011 / 736 / 1,157).
  Every middling and dear good except spices now has its far tenth at 1,100-4,700 km ("a few thousand", the sourced range), and
  sea's share of their flows falls from about two thirds to between a tenth and a half.
- **The long-haul network thins by a sixth to a third:** 1,546 / 1,472 / 1,467 stretches an era (main 1,841 / 1,805 / 2,308); at the
  present 2,642 / 2,783 / 1,631 (main 4,971 / 3,851 / 3,595). Sea's share of it falls from 0.62-0.76 to 0.36-0.40. More of it now runs
  overland, so more towns are trading towns (301 / 520 / 476 at the present, main 216 / 303 / 252).
- **The bars hold.** Land-nudge steadiness 0.78 / 0.79 / 0.75 (main 0.80 / 0.78 / 0.75; the 07c755 worst frame 0.64, main 0.55).
  Herders' grain met 0.0302 / 0.1264 / 0.1227 (main 0.0300 / 0.1266 / 0.1196: the same or better). The derive takes 64 / 55 / 83 s,
  under main's 94 / 127 / 205 s (fewer goods walk to the far side of the world).
- **What is still too far (two drafts).** Dear goods now take the rivers instead: spices' flows are mostly river hauls (0.50-0.83 of them),
  and spices' far tenth stays at 9,700-14,600 km, past the sourced ~8,000 km of pepper to Rome. And horses and herd animals still go
  ~1,500-2,800 km by median, half by ship, though a horse walks itself overland and is dear to ship.

## 1. Literature: what bounded sea reach

Every source below was fetched for this lane (11-08). Distances marked [est.] are this lane's own route estimates; no source gives them.

**Price chains along long sea hauls.**
- **Pepper, 15th century.** Pearson (1987, *The Portuguese in India*, New Cambridge History of India I.1, p. 41, as quoted in the World
  History Encyclopedia's [spice trade article](https://www.worldhistory.org/article/1777/the-spice-trade--the-age-of-exploration/)): the
  price of a kilo of pepper "as it changed hands" was "1 or 2 grammes of silver at the production point", "10 to 14 in Alexandria, 14 to
  18 in Venice, and 20 to 30 in the consumer countries of Europe".
  - Malabar to Alexandria: x8 (1.5 → 12) over ~6,000 km [est.: Calicut-Aden ~3,300 by sea, on by the Red Sea to Suez or Tor, overland
    to Cairo, down the Nile], through several hands and the Mamluk duties: **one e-fold of value per ~2,900 km**.
  - Alexandria to Venice: x1.33 over ~2,400 km by sea [est.], one leg in (this lane's reading) one merchant's hands: **~8,300 km**.
  - Venice to the consumer lands: x1.56 over ~1,000 km overland [est.]: ~2,300 km (the model's dear-good fall-off on land is 1,200
    pack-km plus tolls, the same order).
  - The Journal of Economic History's "Pepper prices before Da Gama" ([Cambridge](https://core-prod.cambridgecore.org/core/journals/journal-of-economic-history/article/pepper-prices-before-da-gama/6C850DB458DB453869EB8F41791F02BF))
    gives Venice's wholesale series (40-50 ducats a cargo in the 15th century); Pearson's own caution (a [Taylor & Francis chapter](https://www.taylorfrancis.com/chapters/mono/10.4324/9781315242637-11/pepper-prices-da-gama-pearson))
    is that the sultan's sales to Venice are a poor guide to Alexandria's market price. So the chain is an order of magnitude, not a fit.
- **Indian wares in Rome, 1st century.** Pliny, *Natural History* 6.26 (6.101), Bostock's translation
  ([Perseus](http://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.02.0137:book=6:chapter=26)): India's wares "are sold among
  us at fully one hundred times their prime cost" (a polemic against luxury; the 25% Red Sea *tetarte* is inside it). The same chapter
  gives the route and its seasons: Juliopolis to Coptos up the Nile 308 miles in 12 days, Coptos to Berenice 257 miles in 12 days by
  camel, sail "at midsummer" and "in about thirty days arrive at Ocelis", then "in forty days" with the Hippalus wind to Muziris; back from
  India in December or by mid-January, so that "they can go and return in the same year". Muziris to Rome ~8,200 km [est.]: x100 is
  **one e-fold per ~1,800 km**, and one round trip a year.
- **The price of capital and risk alone.** Demosthenes 35.10 (Against Lacritus, [Perseus](http://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.01.0076:speech=35:section=10)):
  a sea loan on 3,000 jars of Mendaean wine, Athens to Mende or Scione, to the Bosporus, and back to Athens, "at the rate of two hundred
  and twenty-five drachmae on the thousand; but, if they should sail out from Pontus to Hieron after the rising of Arcturus, at three
  hundred on the thousand". The round trip is ~3,600 km [est.], so the lender's price of a season's capital and the sea's risk is **one
  e-fold per ~17,700 km**; late in the season it rises by a third.
- **Relays on the land routes.** review1.md (sources fetched for that review): the Silk Road ran in relays with ~2,500 km legs; one 7th-century
  partnership went ~2,500 km west of Chang'an. Zhao 2015 (step4a.md): Chinese porcelain reached the Swahili coast "primarily ...
  indirectly".
- **Bulk by sea.** review1.md section 6: wheat by land over 100 Roman miles cost ~55% of its value, by sea 1.3% (Duncan-Jones);
  Rome imported 150,000-272,000 t of grain a year. The model's bulk sea cost is ~1.8% per 100 Roman miles: freight alone already fits.
- **Horses by sea.** Yule's notes to Marco Polo, vol. 2 ([Digital Silk Road, Toyo Bunko copy, p. 405](https://dsr.nii.ac.jp/toyobunko/III-2-F-c-30/V-2/page-hr/0405.html.en)):
  Wassaf prices the horses shipped to Ma'bar (south-east India) from the Gulf at "220 dinars of red gold" each, 2,200,000 dinars a year in
  all (so ~10,000 horses), and the horses kept there "become weak, slow, useless", "a constant necessity of getting new horses annually".
  Kish or Hormuz to Ma'bar is ~3,000-3,500 km by sea [est.]. Horses overland: the Tea Horse Road (Sichuan-Tibet section "more than a
  thousand kilometres", step4a.md), the Nogai's 20,000-80,000 horses a year to Russia (review1.md).

**Not used, and why.** Sea losses as a rate: no fetched source gives ships lost per voyage-km (the sea loan's premium is the priced form of
it). A time cost alone (capital per day in transit): at the sea loan's rate it bounds hauls at ~17,700 km per e-fold, an order of
magnitude too weak to explain the price chains, so time alone is not the mechanism. Kessler & Temin's wheat prices falling with distance
from Rome: the fetched text ([Temin 2011, AEA](https://www.aeaweb.org/conference/2011/retrieve.php?pdfid=219)) states the pattern but
gives no coefficient.

**What the model takes.**
1. What a dear good lost on a long sea haul was its merchants' hands: a season of capital, the risk and a margin per stage, x1.3 for one
   hand on a short leg, x8 over a relayed ocean crossing. That is a share of value per km, not freight, the same kind of loss as a toll.
2. The relayed rate, ~2,900 km per e-fold (Pearson), lies between Pliny's polemical ~1,800 and the one-hand leg's ~8,300. **HAND_KM =
   3,000 km** (JUDGEMENT within that range).
3. On land these hands are already in the model: the fall-off lengths are whole overland markups (Kanesh's tin, Cato's mill), and every
   border crossed takes its toll, rivers included, since a river runs through the cultures' land. So the charge is at sea only.
4. Bulk goods went port to port in one hull, and their sourced sea cost is freight, which the model already meets: no charge (section 3
   measures the alternative).

## 2. Plausibility ranges (set before measuring)

From the brief and section 1, per class, for the median and the far tenth (p90) of each good's flows between cultures:

| class | median | far tenth | sources |
|---|---|---|---|
| bulk (grain, timber, stone) | overland 100-200 km; by water hundreds of km | by water up to ~2,000-3,000 km (Egypt or the Pontus to Rome or Athens, one hull) | review1.md section 6 |
| middling (cloth, glass, porcelain, salt, wine, herds) | a few hundred km | ~1,000-2,000 km, some further by sea via emporia | obsidian's 700-800 km tail; step4a.md section 1 |
| precious (silk, dyes, silver, gold, gems, incense, arms) | ~1,000 km | a few thousand km, relayed | Kanesh 1,200 km; Silk Road 2,500 km legs |
| spices | a few thousand km | ~8,000 km (pepper Malabar to Rome) | Pliny, Pearson |
| horses | mostly overland, ~1,000 km | the sea long case ~3,000-3,500 km (Gulf to Ma'bar) | Tea Horse Road, Nogai, Wassaf |

## 3. Results

Main fe063817 against this lane, and two variants measured on the way: A charges every class 3,000 km (bulk too); B charges bulk the
sea loan's 17,700 km. 0141d1 / 3e0eb4 / 07c755 in each cell.

| measure | main fe063817 | A: 3,000 km, every class | B: bulk 17,700 (sea loan) | this lane (bulk none) |
|---|---|---|---|---|
| long-haul stretches an era (mean) | 1,841 / 1,805 / 2,308 | 1,379 / 1,344 / 1,381 | 1,464 / 1,407 / 1,412 | 1,546 / 1,472 / 1,467 |
| long-haul stretches at the present | 4,971 / 3,851 / 3,595 | 2,147 / 2,438 / 1,564 | 2,375 / 2,616 / 1,555 | 2,642 / 2,783 / 1,631 |
| sea share of long-haul stretches | 0.69 / 0.62 / 0.76 | 0.31 / 0.29 / 0.30 | 0.36 / 0.34 / 0.33 | 0.40 / 0.38 / 0.36 |
| all routes, stretches an era | 2,477 / 2,479 / 2,994 | 1,988 / 2,016 / 2,049 | 2,076 / 2,078 / 2,088 | 2,162 / 2,143 / 2,144 |
| land nudge, all routes (worst frame) | 0.798 (0.712) / 0.778 (0.722) / 0.746 (0.549) | 0.785 (0.72) / 0.768 (0.729) / 0.747 (0.644) | 0.775 (0.713) / 0.786 (0.733) / 0.751 (0.651) | 0.782 (0.67) / 0.788 (0.738) / 0.75 (0.642) |
| land nudge, long-haul | 0.825 / 0.826 / 0.748 | 0.829 / 0.813 / 0.788 | 0.803 / 0.839 / 0.777 | 0.807 / 0.84 / 0.785 |
| land nudge, local | 0.684 / 0.648 / 0.694 | 0.675 / 0.652 / 0.702 | 0.679 / 0.655 / 0.701 | 0.681 / 0.653 / 0.695 |
| land nudge, towns | 0.756 / 0.683 / 0.755 | 0.796 / 0.722 / 0.782 | 0.79 / 0.717 / 0.77 | 0.791 / 0.717 / 0.768 |
| herders' grain met (mean share of lack) | 0.0300 / 0.1266 / 0.1196 | 0.0176 / 0.1262 / 0.1047 | 0.0267 / 0.1263 / 0.1213 | 0.0302 / 0.1264 / 0.1227 |
| herders with any grain | 0.318 / 0.535 / 0.543 | 0.197 / 0.535 / 0.429 | 0.284 / 0.535 / 0.529 | 0.320 / 0.535 / 0.543 |
| grain unmet (all eras) | 0.536 / 0.488 / 0.349 | 0.564 / 0.507 / 0.395 | 0.542 / 0.493 / 0.361 | 0.535 / 0.487 / 0.348 |
| trading towns at the present | 216 / 303 / 252 | 294 / 529 / 504 | 300 / 511 / 481 | 301 / 520 / 476 |
| merchant quarters at the present | 144 / 214 / 267 | 240 / 486 / 629 | 239 / 474 / 599 | 237 / 484 / 599 |
| derive s | 94 / 127 / 205 | 57 / 62 / 73 | 65 / 54 / 90 | 64 / 55 / 83 |

- Variants A and B both cut herders' grain on 0141d1 (0.0300 → 0.0176 and 0.0267), a bar the brief keeps: herders there got part of
  their grain by long sea hauls. With bulk on freight alone, grain is as in main.
- A first try also charged rivers (3e0eb4 only): it cut more (1,139 long-haul stretches an era) but cut herders' grain (0.1266 → 0.1083),
  since grain goes by river; the land model already charges a river haul's tolls at each border, so it was dropped.
- 3e0eb4's herders' grain is 0.1264 against 0.1266 (two in ten thousand): the same within the run's noise; the share with any grain is
  equal.

**Each good's reach** (people-weighted km of its flows between cultures, tribute left out; main fe063817 → this lane):

| good | class | median km (0141d1 / 3e0eb4 / 07c755) | far tenth (p90) km | by sea (share of flows) |
|---|---|---|---|---|
| grain | bulk | 1,014 → 1,011 / 732 → 736 / 1,154 → 1,157 | 4,489 → 4,586 / 3,682 → 3,727 / 4,377 → 4,368 | 0.44 → 0.44 / 0.24 → 0.24 / 0.61 → 0.60 |
| timber | bulk | 760 → 779 / 148 → 152 / 1,950 → 1,975 | 7,019 → 7,099 / 2,976 → 2,922 / 4,608 → 4,587 | 0.39 → 0.39 / 0.21 → 0.21 / 0.50 → 0.50 |
| firewood | bulk | 494 → 482 / 116 → 115 / 1,281 → 1,212 | 7,212 → 7,141 / 2,768 → 2,855 / 4,286 → 4,417 | 0.39 → 0.38 / 0.24 → 0.23 / 0.44 → 0.43 |
| stone | bulk | 198 → 202 / 523 → 523 / 139 → 116 | 728 → 728 / 1,635 → 1,634 / 929 → 929 | 0.36 → 0.36 / 0.30 → 0.30 / 0.11 → 0.11 |
| salt | middling | 1,053 → 885 / 1,165 → 905 / 913 → 792 | 2,599 → 1,761 / 3,799 → 2,273 / 3,181 → 2,437 | 0.46 → 0.24 / 0.52 → 0.22 / 0.52 → 0.27 |
| livestock | middling | 3,470 → 2,227 / 1,584 → 1,437 / 5,059 → 1,677 | 7,425 → 4,718 / 8,973 → 3,810 / 16,635 → 3,917 | 0.81 → 0.43 / 0.38 → 0.20 / 0.82 → 0.42 |
| oil_wine | middling | 1,569 → 1,004 / 556 → 540 / 535 → 410 | 7,530 → 3,176 / 3,670 → 2,845 / 7,819 → 4,297 | 0.59 → 0.35 / 0.38 → 0.21 / 0.70 → 0.44 |
| cloth | middling | 7,737 → 339 / 216 → 153 / 6,518 → 155 | 11,896 → 2,041 / 5,019 → 1,768 / 12,940 → 2,399 | 0.81 → 0.11 / 0.26 → 0.09 / 0.67 → 0.13 |
| glass | middling | 258 → 63 / 2,984 → 1,631 / 15 → 10 | 5,723 → 1,542 / 6,750 → 4,056 / 1,735 → 1,438 | 0.28 → 0.07 / 0.62 → 0.12 / 0.11 → 0.02 |
| porcelain | middling | 0 → 0 / - / 15 → 9 | 4,849 → 384 / - / 1,724 → 1,148 | 0.24 → 0.06 / - / 0.13 → 0.02 |
| horses | middling | 5,213 → 2,814 / 4,922 → 1,717 / 6,210 → 1,561 | 11,215 → 4,702 / 12,907 → 4,221 / 17,043 → 4,259 | 0.89 → 0.55 / 0.67 → 0.31 / 0.81 → 0.45 |
| spices | precious | 11,757 → 6,918 / 11,551 → 8,160 / 8,094 → 5,187 | 19,729 → 11,288 / 17,630 → 14,611 / 18,736 → 9,675 | 0.90 → 0.36 / 0.92 → 0.16 / 0.91 → 0.49 |
| gold | precious | 1,012 → 889 / 2,503 → 1,431 / 1,458 → 1,080 | 5,095 → 2,684 / 8,603 → 3,696 / 5,900 → 3,050 | 0.41 → 0.06 / 0.53 → 0.12 / 0.46 → 0.03 |
| silver | precious | 920 → 796 / 1,215 → 1,040 / 2,772 → 1,094 | 2,842 → 2,178 / 4,084 → 3,415 / 10,006 → 3,209 | 0.29 → 0.08 / 0.36 → 0.19 / 0.67 → 0.11 |
| gems | precious | 1,967 → 1,533 / 376 → 377 / 2,282 → 1,606 | 4,851 → 3,389 / 1,728 → 1,534 / 6,091 → 4,719 | 0.65 → 0.38 / 0.17 → 0.07 / 0.63 → 0.17 |
| incense | precious | 2,026 → 1,533 / 1,712 → 1,819 / 2,246 → 1,999 | 4,815 → 3,539 / 5,566 → 3,804 / 5,769 → 3,857 | 0.75 → 0.21 / 0.39 → 0.28 / 0.72 → 0.14 |
| silk | precious | 812 → 365 / 319 → 277 / 534 → 127 | 9,206 → 2,190 / 3,696 → 1,984 / 8,729 → 2,281 | 0.47 → 0.14 / 0.20 → 0.01 / 0.44 → 0.14 |
| dyes | precious | 1,295 → 472 / 260 → 255 / 479 → 181 | 15,092 → 2,248 / 3,549 → 2,169 / 9,542 → 2,400 | 0.56 → 0.11 / 0.18 → 0.02 / 0.46 → 0.14 |
| arms | precious | 106 → 66 / 24 → 40 / 0 → 9 | 7,527 → 2,197 / 546 → 584 / 88 → 168 | 0.28 → 0.21 / 0.03 → 0.01 / 0.02 → 0.00 |
| ornaments | precious | 2,964 → 2,041 / 1,800 → 1,047 / 3,010 → 2,750 | 6,701 → 4,570 / 5,535 → 4,501 / 8,601 → 6,709 | 0.73 → 0.20 / 0.56 → 0.11 / 0.82 → 0.26 |

**Against the ranges (section 2).**
- Bulk: unchanged by design. The medians (100-2,000 km) are mostly river and sea hauls; the far tenth (up to ~7,000 km for timber and
  firewood on 0141d1) is past the ~2,000-3,000 km of the sourced one-hull grain voyages. Not this lane's lever (the bar kept herders'
  grain as main's); noted, not drafted.
- Middling: cloth, glass and porcelain now in range (medians 0-340 km except glass on 3e0eb4, 1,631; far tenth 380-4,100). Salt and
  wine within ~1,000 by median. **Herds and horses still long** (medians 1,400-2,800 km, far tenth ~3,800-4,700, a third to a half by
  sea): draft.
- Precious: in range: medians 9-2,750 km, the far tenth 170-4,700 km (ornaments 6,700 on 07c755).
- Spices: medians 5,200-8,200 km, far tenth 9,700-14,600: past the sourced ~8,000 km, now mostly by river (0.50-0.83 of the flows):
  draft.

## 4. What changed in the code

- `trade_flow.py` (doc version 8): `HANDS` (False: main's freight alone at sea) and `HAND_KM` ({"middling": 3000, "precious": 3000};
  bulk none). In `_Frame.cost`, a sea edge (mode 2, coast and open sea, canoes included) costs `hop x L / HAND_KM[class]` more, so the
  supply after `x` km at sea is multiplied by `exp(-x / HAND_KM)` whatever the class's fall-off length. The doc's constants list them.
  The module docstring says so.
- Test: `test_a_sea_km_costs_a_share_of_value_for_the_hands` (the charge per sea edge is the hop over HAND_KM in value terms for each
  class, bulk and land and river edges unchanged).

## 5. Status

- The inbox draft (the long-haul network's size after a sourced port cost; ruling: a model problem, option C out) is **closed by this
  lane** and deleted: a sourced mechanism (the hands at sea) thins the long-haul layer by 16-36% an era and brings cloth, silk, dyes,
  silver, gold and incense into their sourced ranges.
- Bars: land-nudge steadiness 0.78 / 0.79 / 0.75 (>= 0.7 on all three, main 0.80 / 0.78 / 0.75); herders' grain the same as main or
  better; derive time 0.4-0.7 of main's.
- Drafts (inbox): river hauls carry dear goods past their sourced reach; herds and horses go by sea as cheaply as cloth.
