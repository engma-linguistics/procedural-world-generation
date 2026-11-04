# Crop origins and spread: round 1 sources (lane 157)

**In plain words.** I checked each row of the crop table in `planet/lineages/crop_defs.py` against published sources: Earth's first cultivation date (the "anchor", in thousands of years ago, ka) and its home region. **Most anchors are fine, within about 1 kyr. Three look wrong:** common beans (7.0, should be about 5.0), quinoa and amaranth (7.0, should be about 5.0) and the flax part of oil seeds (6.0, but flax is about 9.5). Two are borderline: tomatoes (5.0 against a single genetic estimate of about 7) and foxtail millet (10.0 holds only if the row also covers broomcorn millet).

Some rows I could not check this round: tropical spices, sap sugar and beet, cooking greens, onions and garlic, vanilla, oats and amaranth.

Up to seven foods should be added, staples first: soybean, date palm, cowpea, mung bean, Old World melons, breadfruit and coffee.

On spread, the most useful finding for the model is about who carries the crops:
- **Colonists** bring their whole crop kit to new land, including across thousands of km of open sea. Lapita settlers did this about 3 ka, Polynesians in 1.0–0.7 ka, and Austronesians in Madagascar and the Comoros in 1.3–1.0 ka.
- **Traders** bring single crops to land other peoples already hold. Those crops stay minor for centuries.
- Overland, farming spread at about 1 km a year.
- Crossing between winter-sown and summer-sown climates took Eurasian crops thousands of years.

**Method.** Every date below comes from a source I opened in this session, unless it is marked *unverified*. Most dates come from one figure: Larson et al. 2014, PNAS 111:6139, **Fig. 2** ("A chronological chart listing the regions where, and the time frames over which, key plants and animals were domesticated"). I read it from the eScholarship PDF (escholarship.org/content/qt6sd6f5bc/qt6sd6f5bc.pdf, page 3 of the article).

How to read Fig. 2:
- Grey dashes mean people were using the wild plant.
- Blue dashes mean people were cultivating it, but the plant had not yet changed shape.
- A red bar is the span over which the first domestic forms appear.
- A short red tick is "the latest time by which domestication occurred".

I read the bars off the time axis at about ±0.2 kyr. The table that would give exact numbers (Larson Table S1, in the supplement) would not open: PMC and PNAS both refused the request. Below, "L14 Fig 2, region X" means that figure.

---

## 1. Per-row audit

Verdicts:
- **OK**: within about 0.5 kyr.
- **fine**: within about 1.5 kyr.
- **WRONG**: off by more than 1.5 kyr, or the wrong crop sets the date.

"Region type" describes the climate the crop was first farmed in, not a continent.

| Row (anchor ka) | Earth origin | Best-supported date (ka) and source | Region type | Verdict |
|---|---|---|---|---|
| wheat and barley (10.5) | SW Asia (Fertile Crescent) | Wheat: cultivation without domestic traits from ~11, domestic traits 11–9. Barley: domestic traits ~10.5–9. L14 Fig 2, A | winter-rain, dry-summer foothills, semi-arid | OK |
| lentils and peas (10.0) | SW Asia | Lentil: domestic traits ~10.5–9. Pea: ~10–8.5. Chickpea: ~10.2–8.2. L14 Fig 2, A | same as wheat | OK |
| foxtail millet (10.0) | N China | Broomcorn ("common") millet in Cishan pits 10.3–8.7 cal ka; "After ca. 8,700 cal yr BP, the grain crops began to contain a small quantity of foxtail millet". Lu et al. 2009 PNAS 106:7367, abstract (PMC2678631). Latest-domestication ticks: broomcorn ~8.0, foxtail ~7.4 (L14 Fig 2, C) | semi-arid, summer-monsoon, cool-temperate loess | **fine only as "the northern millets"**. For foxtail alone use ~8.5. Suggest relabelling the row "foxtail and broomcorn millet" and keeping 10.0 |
| rice (9.0) | Yangtze, China (japonica) | Japonica: wild use from 10, cultivation without domestic traits ~7.9, domestic traits 7.5–5.0. Indica (S Asia): domestic traits 4.0–2.5. African rice: tick ~2.0. L14 Fig 2, B/C/E | warm, humid, subtropical wetland | fine (about 1 kyr early; it sits in the wild-use and early-cultivation phase) |
| sorghum and pearl millet (5.5) | Sahel and E Sudan | Sorghum at KG23, E Sudan, 3500–3000 BC (5.5–5.0 ka), "a snap shot from the middle of its domestication". Winchell et al. 2017 Curr. Anthropol., via ScienceDaily release 27 Sep 2017. Pearl millet in Mali ~2500 BC. Same release. L14: pearl millet domestic traits 4.5–3.5 | summer-rain, semi-arid tropical savanna | OK (sorghum sets the date) |
| maize (9.0) | Mesoamerica | Wild-use dashes 10–9, latest-domestication tick ~9.0. L14 Fig 2, G | warm, seasonally dry tropics; later highlands | OK |
| potatoes and other cool tubers (8.0) | high Andes, Lake Titicaca (3,800 m) | "The story of the potato begins about 8 000 years ago near Lake Titicaca". FAO, International Year of the Potato 2008 booklet, "Andean heritage" (fao.org/4/i0500e/i0500e02a.pdf). L14 Fig 2, H: white potato wild use 7.0–4.6, tick ~4.5 | cool tropical highland, short-day | fine (FAO). The domestic-form evidence is later (~4.5) |
| yams, taro and cassava (7.5) | **lumps three homelands**: New Guinea (taro, greater yam), S America (manioc), Africa (yams) | New Guinea: wild use 10–7, cultivation without domestic traits 7–4 (banana, taro, yam). Manioc: tick ~7.0. S American yam: ~5.5. L14 Fig 2, D/H. African yam not in L14 (*unverified*) | humid tropical lowland (wet-dry fringe for manioc) | fine. **7.0 best stands for the row** (New Guinea and manioc agree) |
| bananas and plantains (7.0) | New Guinea | Cultivation without domestic traits 7–4. L14 Fig 2, D | humid tropical lowland | OK |
| rye and oats (3.5) | Europe (rye began as a weed in wheat fields) | Rye is a "secondary domesticate"; "Substantial numbers of rye grains appear in the archaeological record only in the European Bronze Age", and it was a crop by the Iron Age. Schreiber et al. 2018 Evol. Appl. (PMC6304746), introduction. The source gives periods, not years. Oats *unverified* | cool-temperate, wet, short summers | fine (Bronze to Iron Age; the years are not in the source) |
| tree fruit and nuts (7.0) | SW Asia and E Mediterranean | Olive, grapevine and dates were domesticated in the Chalcolithic, fig in the Early Bronze Age. "Beginnings of fruit growing in the Old World – two generations later", Isr. J. Plant Sci. 62 (2015), abstract (cris.biu.ac.il). L14: date palm wild use 7–6, tick ~5.0; olive tick ~6.0. Apple: grafted only in the last 2–3 millennia (Spengler 2019 Front. Plant Sci., PMC6545323; *unverified*, from the search summary only) | Mediterranean, dry-summer, plus desert oases | fine. **6.0 is best**, and temperate fruit is much later |
| olives (6.5) | Levant | Wild use 10–6, tick ~6.0. L14 Fig 2, A. Chalcolithic (2015 reassessment above) | dry-summer Mediterranean | OK |
| grapes and vines (8.0) | S Caucasus and W Asia | "Early work asserted that V. vinifera originated ... ~8000 years ago during the Neolithic". The genome study puts the split at ~11,000 years ago (95% CI 10.5–12.5) in W Asia and the Caucasus. Dong et al. 2023 Science 379:892, introduction and results (KIT pdf) | dry-summer and continental uplands | OK (archaeological view; the genetic view is earlier) |
| oil seeds: sesame, flax, rape (6.0) | **lumps**: flax from SW Asia, sesame from S Asia, rape from Europe | Flax: wild use 12–9.5, latest-domestication tick ~9.5. L14 Fig 2, A. Sesame and rape *unverified* | flax: as wheat. Sesame: hot semi-arid | **WRONG if flax leads (9.5)**. Either split flax into the pulses/wheat package at ~9.5 or keep 6.0 for sesame (unchecked) |
| coconut and oil palm (4.5) | coconut: Island SE Asia/Pacific and S India margin (two origins). Oil palm: W Africa | Coconut: "two geographical origins": Gunn et al. 2011 PLoS ONE 6:e21143 (PMC3120816; search summary of the abstract, which gives no date). Oil palm: wild use from ~9.5, tick ~3.5. L14 Fig 2, E | humid tropical coast | fine (only oil palm is dated, ~3.5) |
| pepper, cinnamon, tropical spices (3.5) | S India and Sri Lanka, Island SE Asia | not checked this round (*unverified*) | humid tropical forest | — |
| chili-like capsicum (6.0) | S America (origin "Bolivia and southern Brazil") and Mesoamerica (*C. annuum*) | S America tick ~6.0; Mesoamerica tick ~3.0. L14 Fig 2, G/H. Origin: Nunn & Qian 2010 JEP 24(2):163, "Capsicum Peppers" p.171 | warm, seasonally dry tropics to mid-elevation | OK |
| sugar cane (8.0) | New Guinea | "domesticated from the wild species S. robustum around 8 000 years ago in New Guinea". CIRAD release 15 Oct 2025 on Garsmeur et al. 2025 Cell | humid tropical lowland | OK |
| sap sugar and beet (1.0) | NE N America (maple), Europe (beet sugar) | not checked (*unverified*) | cool-temperate forest | — |
| tea, coffee, infusions (3.0) | tea: SW China uplands. Coffee: Ethiopia, then Yemen | Tea: "tea was grown 2100 years ago", sample 255±80 BCE, first text 59 BCE. Lu et al. 2016 Sci. Rep. 6:18955 (PMC4704058), abstract and introduction. Coffee: mid-15th c. Yemen (popular histories only; *weak*) | humid subtropical uplands (tea); tropical highland (coffee) | fine for tea (2.2–2.5). **Coffee is ~0.55 and belongs in its own row** (see §2) |
| cooking greens: brassicas, leeks (5.0) | — | not checked (*unverified*) | — | — |
| onions and garlic (6.0) | — | not checked (*unverified*) | — | — |
| tomatoes and nightshade fruits (5.0) | wild cherry tomato in Ecuador and Peru; cultivated tomato in Mexico | "the origin of the common cultivated tomato, SLL, ∼7 ka in Mexico". Razifard et al. 2020 MBE 37:1118 (OUP press summary page). Genetics only: the seeds preserve poorly | warm, seasonally dry tropics and subtropics | **borderline WRONG: about 2 kyr late against the only estimate. Use ~7.0 (low confidence)** |
| squash and gourds (10.0) | Mesoamerica (*C. pepo*), S America (*C. moschata*) | *C. pepo* domestic traits 10.0–9.5; *moschata* tick ~10.0. L14 Fig 2, G/H. Text: loss of bitterness "by at least 9200 B.P., only 800 y later than the first evidence for its domestication" (L14 p.6141) | warm, seasonally dry tropics | OK |
| common beans (7.0) | Mesoamerica and Andes (two origins) | Latest-domestication ticks: Andes ~5.0, Mesoamerica ~3.0. Lima bean: cultivation without domestic traits ~8, tick ~6. L14 Fig 2, G/H | warm, seasonally dry tropics, mid-elevation | **WRONG: use 5.0** |
| cacao (5.3) | upper Amazon (SE Ecuador) | cacao use "between 5,300 and 2,100 years ago" at Santa Ana-La Florida. In Mesoamerica it appears only by 3,900 years ago. Zarrillo et al. 2018 Nat. Ecol. Evol., EurekAlert release 814842 | humid tropical montane forest foothills | OK |
| vanilla (1.0) | Mesoamerica | not checked (*unverified*) | humid tropical forest | — |
| peanuts (7.6) | S America (lowland foothills) | Cultivation without domestic traits ~8.4–6.4, tick ~5.0. L14 Fig 2, H | warm, seasonally dry tropics | OK (it sits in the cultivation window) |
| sweet potatoes (5.0) | tropical S America | tick ~5.0. L14 Fig 2, H | humid tropical lowland to mid-elevation | OK |
| quinoa and amaranth (7.0) | Lake Titicaca basin (quinoa) | Quinoa: wild use from ~5.0, tick ~3.5. L14 Fig 2, H. Amaranth *unverified* | high Andes, cold semi-arid | **WRONG: use 5.0** (4.0 if using the domestic forms) |
| avocados (5.5) | Mesoamerica | wild use 7.0–6.0, tick ~3.0. L14 Fig 2, G | seasonally dry tropical uplands | fine (inside the window; weakly pinned) |

Notes on lumping:
- "Yams, taro and cassava" and "coconut and oil palm" each join crops from separate continents with different dates (7.0 / 7.0 / unknown, and coconut undated / 3.5).
- "Oil seeds" mixes a founder crop (flax ~9.5) with later ones.
- "Tea, coffee" mixes 2.5 ka and 0.55 ka.
- "Tree fruit and nuts" mixes Chalcolithic Mediterranean trees (~6) with temperate fruit (apple, grafted in the last 2–3 kyr; *unverified*).

---

## 2. Missing foods

Daniel's list is "chilies, potatoes, olives, and so on", with staples first. Chili, potato and olive are already rows. These are the most important absent foods I could date from an opened source. Staples come first.

| # | Proposed row | Origin | Climate type | First cultivation / domestication (ka), source |
|---|---|---|---|---|
| 1 | **soybean** (staple pulse, oil) | N China | summer-monsoon temperate | wild use from ~6.5, domestic traits 5.5–3.5. **Anchor ~5.0**. L14 Fig 2, C |
| 2 | **date palm** (staple of hot deserts) | Arabia and the Gulf / Africa | hot desert oasis, groundwater | wild use 7.0–6.0, tick ~5.0. L14 Fig 2, E. Chalcolithic per the 2015 reassessment. **Anchor ~6.0** |
| 3 | **cowpea and other African pulses** (savanna staple pulse) | W African savanna | summer-rain semi-arid tropics | ticks: cowpea ~3.7, hyacinth bean ~3.7. L14 Fig 2, E. **Anchor ~3.7** |
| 4 | **mung bean / Indian pulses** | S Asia | monsoon tropics | cultivation without domestic traits 4.4–3.5, domestic traits 3.5–3.0. L14 Fig 2, B. **Anchor ~4.0** |
| 5 | **melons and cucumbers (Old World cucurbits)** | E Asia (L14 lists melon under East Asia) | warm-summer temperate to subtropical | domestic traits 4.0–3.5. L14 Fig 2, C. **Anchor ~4.0** |
| 6 | **breadfruit** (Pacific tree staple) | Near Oceania | humid tropical islands | the word for breadfruit "was carried into Remote Oceania by the first Oceanic-speaking colonists" (Pawley, ANU Press, *New Perspectives in SE Asian and Pacific Prehistory* ch.17, citing Ross 2008). So it was a crop by ~3.1 ka. The domestication date is *unverified*. **Anchor ~3.5** (minimum) |
| 7 | **coffee** (own row, out of "tea, coffee") | Ethiopian highlands, then Yemen | tropical highland | mid-15th c. CE in Yemen (popular histories only, *weak*). **Anchor ~0.55** |

Also worth knowing, though they need no new row:
- Chickpea (domestic traits 10.2–8.2) and broad bean (tick ~10.3) belong in "lentils and peas" (L14 Fig 2, A).
- Broomcorn millet (Lu 2009) belongs in the foxtail row.
- Fonio (tick ~2.5) and African rice (~2.0) are later African grains (L14 Fig 2, E).
- I did not open a source for citrus, mango, apple, fig (as its own row), finger millet, teff or buckwheat, so they stay *unverified*.

---

## 3. How foods spread on Earth, and what held them back

### (a) Ocean crossings

- **Americas and Afro-Eurasia were cut off until 1492.** Only one food crossed between them before then. Sweet potato reached Central Polynesia "by approximately A.D. 1200 to 1300", "most likely ... by Polynesian voyagers who reached South America" (Denham 2013, PNAS commentary on Roullier et al. 2013, PMC3568348). Sweet potato later reached Oceania twice more after European contact: from Mexico by Spanish galleon to the Philippines about AD 1500, and from the Caribbean by Portuguese traders via Europe in the 16th c. (same source, the "tripartite hypothesis").
  - Bottle gourd reached the Americas by about 10 ka, apparently by floating from Africa, not with people (Kistler et al. 2014 PNAS; *unverified*: the abstract would not open, so this is from the search summary only).
- **The Columbian exchange was fast** (Nunn & Qian 2010 JEP, p.171–172 and the "Sugar Cane" section):
  - Capsicum peppers: "By 1493 ... had arrived in Spain and Africa. They then reached the East Indies by 1540 and India by 1542", and paprika is recorded in Hungary by 1569.
  - Tomato: in European texts 1544, the Philippines 1564, fields in North Africa by 1671. In China it was not cultivated until the 20th c.
  - Sugar cane: carried to Hispaniola in 1493, sugar exported to Europe by 1516, from Brazil by 1526.
  - **So a trade network could move a crop across oceans and continents within 50 years, but a people's own choices could hold one back for centuries (tomato in China).**
  - Potato is the counter-example for day length. The Andean group "is adapted to short day conditions". The potato grown worldwide today came from Chilean cultivars that reached Europe in the 19th century (FAO 2008, potato booklet, varieties section).
- **Lapita colonists carried their whole crop kit across open sea.**
  - Lapita settled Reefs-Santa Cruz, Vanuatu, Fiji and Tonga in **3100–2850 BP**, across island groups "separated by hundreds of kilometres".
  - The plant remains and the word evidence show "the greater yam, Colocasia taro, two kinds of Musa bananas" and the main tree crops (breadfruit included) arriving with the first settlers, with pigs and chickens.
  - Contact between the island groups lapsed within 100–300 years (Pawley, ANU Press ch.17).
  - I found no sourced value this round for the longest single open-water gap (e.g. Vanuatu to Fiji).
- **The long pause.** "Migration into eastern Polynesia began after a 1,800-y pause since the first settlement of Samoa, ∼800 B.C." Then came two fast pulses: the Society Islands in AD ~1025–1120, and all remaining East Polynesia (Hawaii, New Zealand, Rapa Nui) in AD ~1190–1290. The second pulse began 70–265 years after the first. (Wilmshurst et al. 2011 PNAS 108:1815, abstract and results, PMC3033267.)
- **Indian Ocean: colonists versus traders** (Crowther et al. 2016 PNAS, "Ancient crops provide first archaeological signature of the westward Austronesian expansion", UCL author manuscript; Fuller and Boivin are co-authors):
  - **Madagascar** lies 500 km from Africa and 6,000 km from SE Asia. It was settled by Austronesian speakers in the 1st millennium CE, about the 7th–8th c. on linguistic grounds.
  - On the **Comoros and Madagascar** (colonists), the earliest crop remains (8th–10th c. CE) are dominated by Asian crops. Rice makes up "approximately 70–100%". The authors call this "consistent with patterns observed when crops move through human colonization". Their comparisons are Neolithic Europe, where "the first crops are entirely Near Eastern", and Japan, where wet rice arrived with immigrants after 2.8 ka.
  - On the **East African mainland coast** (traders reaching land held by other peoples), Asian crops "were absent or rare and mainly identified at major trading ports ... (approximately 8%)". "Significant quantities (>10%) of Asian crops do not appear at any eastern African site until the 11th century CE". "Exotic crops introduced to a region as new plants usually featured as a minor component ... for centuries and, in some cases, millennia after arrival".
  - The other direction: "African millets and sorghum appear in Indus sites" in 2500–1500 BC, "in the context of a network of resource movement across the Indian Ocean" (Liu et al. 2019 QSR 206:21, §3.3). The sources I opened do not say whether this went coast by coast or across open sea; that stays *unverified*.
  - **Answer to the key question:** crops went across long open sea (Madagascar is 6,000 km from SE Asia; Polynesia is thousands of km) **with colonists settling new land**, from Lapita (~3.1 ka) on. Traders also moved crops by sea, to the coast of East Africa and, from about 4 ka, to India, but those crops reached land held by others and stayed minor for centuries.

### (b) Climate and day length

- **Maize spread north slowly.** It reached the US Southwest "no later than about 2100 cal. B.C." (~4.1 ka), against Oaxaca at ~4300 cal BC. That is about 2,800 km in about 2,200 years: "about 1.3 km per year, or one degree of latitude ... every 92 years". It spread by "group-to-group diffusion" among foragers, not with migrating farmers (Merrill et al. 2009 PNAS 106:21019, PMC2795521). The paper does not discuss day length.
  - The eastern North America date and a sourced statement on photoperiod are *unverified* this round.
- **Diamond's axis claim.** Laitin, Moortgat & Robinson 2012 (PNAS 109:10263, PMC3387047) restate it: plants and animals "have evolved to survive within specific seasonal regimes" that vary with latitude, so farming spreads more easily east–west. Their test supports the axis effect only through linguistic diversity (north–south countries keep more indigenous languages, r = 0.13 on its own). It does not measure crop spread. **Treat the axis claim as plausible but untested for crops.**
- **Winter-sown and summer-sown crops took millennia to swap.** Liu et al. 2019 (§4.2–4.3):
  - 5000–2500 BC: crops spread only within "familiar environmental niches".
  - 2500–1500 BC: "the predominantly winter sown crops wheat and barley spread to east China, where ... broomcorn, foxtail millet and rice are mostly sown in the spring and summer". Conversely, the spring-sown millets spread to SW Asia and Europe.
  - Changes in flowering time helped wheat and barley reach the northern latitudes of Europe and the high altitudes of Asia.
  - For the model: **a crop moving into a different season regime should be slowed far more than one moving within the same regime.**

### (c) Keeping

- The sources show perishable produce limiting trade, not the crop itself. Ripe tomatoes "can become putrid within days in hot climates", and only canning (mechanised about 1900) made them a global trade good (Nunn & Qian p.172).
- The vegetatively propagated crops (yams, taro, banana) did cross the longest seas, with colonists (Lapita, Madagascar). So tubers and cuttings travelling in a canoe were not a hard limit for settlers. Crowther et al. also note these crops leave few charred remains ("archaeologically invisible").
- **I found no source comparing how fast tuber or cutting crops spread overland against seed crops.** That stays an open question.

### (d) Overland spread speeds

- Neolithic farming from the "northern Levantine/Mesopotamian area" into Europe spread at **0.6–1.3 km/yr** (95% CI), starting 10,000–11,500 cal BP (Pinhasi, Fort & Ammerman 2005 PLoS Biol 3:e410, abstract and results).
- Maize moved northward at about **1.3 km/yr** (Merrill 2009, above).
- **Trans-Eurasian exchange** (Liu et al. 2019 §3.2–3.3):
  - Wheat and barley reached E Kazakhstan and the upper Ganges by 2500 BC, and the Altai at c. 3000–1500 cal BC.
  - Wheat reached Shandong (E China) at c. 2500–2000 cal BC. The larger overland movements came after 2000 BC.
  - Broomcorn millet reached E Kazakhstan in the late 3rd millennium BC. The oldest direct date in Europe is c. 1600 BC (Hungary). Older indirect dates are doubted.
  - That puts **about 5–6 kyr between the founder crops and the exchange** across about 4,000+ km of steppe and mountain corridors.
- Bantu expansion speed: *unverified* this round (no source opened).

---

## Numbers the model can use

1. Corrected anchors: common beans **5.0** (L14 Fig 2 H); quinoa and amaranth **5.0** (L14 Fig 2 H); flax **9.5** if it leads oil seeds (L14 Fig 2 A); tomato **~7.0**, low confidence (Razifard 2020); tea **~2.5** (Lu 2016); coffee **0.55**, weak; best single value for the root-crops row **7.0** (L14 Fig 2 D/H).
2. New rows: soybean 5.0, date palm 6.0, cowpea 3.7, mung bean 4.0, melons 4.0 (all L14 Fig 2); breadfruit at least 3.1 (Pawley); coffee 0.55 (weak).
3. Neolithic farming front overland: **0.6–1.3 km/yr** (Pinhasi 2005).
4. Maize northward by forager-to-forager handoff: **1.3 km/yr, ~92 yr per degree of latitude** (Merrill 2009).
5. Columbian-exchange spread through trade networks: chili from Spain to India in **≤50 yr** (1493 → 1542); tomato from Europe to the Philippines in **20 yr**, but not farmed in China for about 400 yr (Nunn & Qian 2010).
6. Colonists bring their crop kit across open sea, up to **6,000 km** (Madagascar) and across Remote Oceania, at **3100–2850 BP** (Lapita) and **AD 1025–1290** (East Polynesia). Colonists' crop share at first settlement is **~70–100%** of crop remains (Crowther 2016; Pawley; Wilmshurst 2011).
7. Traded crops on land already held by others make up **about 8%** of remains at ports, take **centuries or millennia** to become major, and pass 10% of remains at no East African site before the 11th century CE, some centuries after the first finds (Crowther 2016).
8. Long pause before the next push into remote ocean: **1,800 yr** after the West Polynesia settlement (Wilmshurst 2011).
9. Crossing between winter- and summer-sown regimes took Eurasian crops **about 5–6 kyr** after domestication; within-niche spread came first (Liu 2019).
10. Exactly one pre-1492 crop crossed between the Americas and the Old World by people: sweet potato, AD 1200–1300, carried by Polynesians (Denham 2013).
