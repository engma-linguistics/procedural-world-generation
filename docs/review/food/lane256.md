# Lane 256: the missing herd animals (PW-835) and food fit per body (PW-905)

Sources were fetched in this lane by two research passes (WebFetch/WebSearch). The quotes are as the fetch tool relayed them. Publisher
pages (nature.com, pnas.org, Cell, Springer) mostly refused automated fetches, so PMC copies, press summaries and Wikipedia stand in.
Each is marked. Anything not found is marked JUDGEMENT.

## 1. Herd animals (animal_defs.py)

| animal (bit) | anchor | where | wild range as coded | milked | source (fetched) |
|---|---|---|---|---|---|
| fowl (4) | **3.5 ka** (was 8) | Ban Non Wat, central Thailand | unchanged | no | Peters et al. 2022 PNAS, PMC9214543: "the first unambiguous domestic chicken bones are found at Neolithic Ban Non Wat in central Thailand" (1650-1250 BCE). Wikipedia's "8,000 years ago" is the old figure. |
| horse (0) | **4.2 ka** (was 5.5) | lower Volga-Don | unchanged | yes | Librado et al. 2021 Nature, PMC8550961: "the lower Volga-Don region, as the homeland of modern domestic horses", spreading "following about 2200 bc". Botai's ~3500 BC horses (milked, bridled) are not the ancestors of modern horses. |
| pig (7) | 10.5 ka | Near East (and East Asia ~8 ka) | forest and woodland edge, -4..34 C, 250-4500 mm, below ~3500 m (edges JUDGEMENT) | no | Frantz et al. 2019, PMC6717267: "pig domestication had begun by ∼10,500 y before the present (BP) in the Near East"; PMC6889691: "separately domesticated about 8 kya in East Asia". |
| reindeer (8) | 2 ka (**JUDGEMENT**) | Fennoscandia and western Russia | tundra and taiga, mean annual -22..4 C | yes (Sami, small herds) | PMC7366605: herding "certainly developed from the Late Iron Age (ca. 800–900 AD)"; some suggest ~1500 BC. 2 ka sits between the two. |
| camel (9) | 4.5 ka | Central Asia (Bactrian); SE Arabia (dromedary ~3 ka) | open dry land 10-600 mm, -6..36 C, below ~4200 m | yes | PMC6946651: "first domesticated in Central Asia before 4.45 thousand years ago"; Almathen et al. 2016 PNAS via phys.org: "the Southeast Arabian Peninsula as the region of first domestication". Wikipedia (Dromedary): southern limit ~550 mm/yr; Bactrian coat good from -30 to 50 C. |
| llama (10) | 6 ka | central Andean highlands | 2600-5600 m (core 3400-5000), -6..15 C, open | no (a llama gives ~60 ml at a time, Wikipedia) | Florida Museum, Origins of animal domestication in the Andes: "approximately 6000 years ago"; Wikipedia (Alpaca): 3500-5000 m. |
| buffalo (11) | 6.3 ka | western India (river type) | hot humid lowland 16-34 C, 700-5500 mm, wetland x1.0 else x0.7, below ~2000 m | yes (river type) | Wikipedia (Water buffalo): river type "probably domesticated about 6,300 years ago"; PMC8289072: swamp type "domesticated between 3–7,000 years ago", "both are well-adapted to a hot and humid climate", river type "prized for ... high-quality milk". |
| yak (12) | 7.3 ka | Qinghai-Tibet Plateau | 2500-5900 m (core 3200-5200), mean annual -14..9 C, open | yes | Qiu et al. 2015 Nat Commun, PMC4703879: "We date yak domestication to 7,300 years before present"; Wikipedia (Yak): pastures 3000-5000 m, heat exhaustion above ~15 C. The oldest bones are ~2.5 ka, and pastoralism starts ~4.5 ka, so 7.3 is the genomic date. |

Boats: pigs ride canoes like dogs and fowl (size 0). Lapita-associated settlers "introduced dogs (Canis familiaris), pigs (Sus sp.), and jungle fowl (Gallus gallus)" (PMC428491). Wikipedia (Chicken) says they "were carried with dogs and pigs during the Austronesian maritime migrations". This is patchier east of Near Oceania.

Who tames each animal and who takes it up (the farm, herd and forage weights) is JUDGEMENT, following the existing rows. Pigs go to farmers and settled foragers, not nomads. The cold and dry herd animals go to herders, and reindeer also to hunters. Buffalo go to farmers and herders, plus a little plough land. Camels move fast over open land, as horses do, but slower (x1.3).

Format: `animal_known` and `animal_wild` are now uint16 (13 bits). The earlier stored runs still hold uint8 layers and read correctly, but they carry none of the new animals. A run gets the new animals only when it is re-run.

## 2. Food fit (food_fit.py)

Each food class gets a level for each body: thrives / tolerates / poorly suited / harmful. It is read from the body keys the presets already carry (milk, sweet, capsaicin, raw_meat, cellulose, gut, grain, bitter, toxic, diet). No new key is authored.

| claim | used for | source (fetched) |
|---|---|---|
| ~65% of adults malabsorb lactose; persistence is high in northern Europe and among pastoralists, and <=5% in East Asians; other mammals lose lactase after weaning | fresh milk | Wikipedia, Lactose intolerance and Lactase persistence |
| yogurt bacteria use up lactose; cheddar holds <1.5% of milk's lactose | soured dairy | Wikipedia, Lactose intolerance |
| "scavengers and carnivores have significantly higher stomach acidities compared to herbivores"; humans are near the carrion feeders | raw meat, high meat | Beasley et al. 2015 PLoS ONE, journals.plos.org/plosone/article?id=10.1371/journal.pone.0134116 |
| "cat Tas1r2 is an unexpressed pseudogene"; sweet is also lost in other exclusive meat eaters (sea lion, spotted hyena, Asian otter) | sweet | Li et al. 2005 PLoS Genetics; Jiang et al. 2012 PNAS, PMC3324019 |
| bird TRPV1 "does not respond to capsaicin"; capsaicin "offers protection from predatory mammals" | chili | Wikipedia, Capsaicin; Jordt & Julius 2002 (Duke scholars abstract) |
| an ADH4 change ~10 Myr ago let hominid ancestors oxidise ethanol well | alcohol (human-like) | phys.org summary of Carrigan et al. 2015 PNAS |
| ~50% of East Asians carry ALDH2*2 (the flush) | alcohol (noted, not used per people yet) | Wikipedia, ALDH2 |
| dogs and cats sicken on ethanol | alcohol (cat-, dog-, bird-like bodies) | Merck Veterinary Manual, Alcohols. **Search summary only**, not a fetched page. |
| dog half-lives: theobromine 17.5 h, caffeine 4.5 h; signs from 20 mg/kg | caffeine, cacao | Merck Veterinary Manual, Chocolate toxicosis |
| alliums: "Cats are the most susceptible species, followed by dogs"; Heinz body anaemia | alliums | Merck Veterinary Manual, Allium toxicosis |
| browsing cervids have proline-rich (tannin-binding) saliva. **Disputed**: the same 2020 study finds no browser/grazer difference across 28 African species | tannin (foregut bodies) | PMC7548203 |
| deer take birds now and then | meat for plant eaters ("poor", not "harmful") | Field & Stream (magazine, **weak**) |

Not found, so these rows are JUDGEMENT:
- human liking for chili is learned
- human caffeine tolerance
- birds' and reptiles' ethanol handling
- reptile sweet taste
- the grain, browse, tannin and high-meat levels for the human-like baseline

Grapes and raisins are toxic to dogs (Merck), but no body in the presets marks a canid. That row is left out.

Fantasy bodies are any body off the human-like baseline: another diet, gut, taste, cold blood or toxin. They get the nearest real animal's biology, and their line says JUDGEMENT. This covers lizardfolk, tortles, kobolds and the dragon kinds, which inherit the reptilian stem's body (dragons are sapient peoples; their fit is that of a reptile-bodied people). The cat peoples are covered too. Their poor alcohol fit agrees with the owner's canon (culinary-dnd master reference §7: the cat peoples "barely drink"). The aarakocra thrive on chili, which agrees with that canon's capsaicin-blind pepper breeding.

Where it shows:
- the cuisine sheet's "Body and food" line, and `sheet.food_fit` (levels, rows with basis and source, and the foods its own fields grow that do not suit it)
- the brief's Peoples section, as a "food fit" line under each people's body

The viewer's Culinary brief tab renders both from the markdown.
