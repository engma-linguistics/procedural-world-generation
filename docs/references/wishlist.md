# Maybe Daniel can look these up someday

Books and papers we'd like to read but can't get: paywalled, print-only, or blocked for agents. None of these blocks anything. Each is
a stand-in or an "unverified" note in the code that a real source could replace. If you get one, drop the PDF into the topic folder
under `docs/references/` (PDFs are gitignored) and tick it here; an agent will read it and check our numbers against it (PW-938).

Ordered by how much a finding would change what the worlds show.

**2026-10-29:** the owner's 10-29 batch is ingested (ticked below; PDFs in docs/references/megafauna/ and docs/references/tectonics/). The
remaining unticked items are not expected.

## Most wanted

- [x] **McNaughton, Oesterheld, Frank & Williams 1989**, Nature 341:142-144, doi:10.1038/341142a0. Herbivore biomass against plant
  growth. Read (PW-975): prey.py uses its biomass fit. Its kJ-to-mass conversions are not in the paper;
  see the next item.
- [ ] **Standard energy conversion factors** (carbon to dry matter, kJ per g dry plant, kJ per g live herbivore), e.g. Golley 1961 Ecology 42:581 or Schroeder 1977 Oecologia 28:261 (McNaughton's refs 41-42). prey.py's C_FRAC 0.45, KJ_PER_G_DRY 17.5 and KJ_PER_G_LIVE 7.0 are unverified typical values (PW-975). 10-29: KJ_PER_G_LIVE 7 kJ/g is now confirmed by Farlow 1993 p. 172 (citing Peters 1983, p. 33); the other two are still open.
- [x] **Coe, Cumming & Phillipson 1976**, Oecologia 22:341-354, doi:10.1007/BF00345312. African herbivore biomass against rainfall,
  the second candidate fit for the same field. Read 10-29: log10 B = 1.094 log10 NAAP + 0.389 (kg/km2, g dry/m2/yr; Fig. 3 p. 349)
  matches prey.py within 1.4x (same at a steppe, lower at a rich savanna); no change.
- [ ] **Binford 2001**, *Constructing Frames of Reference* (University of California Press; a book, likely only in print or a
  library). Its hunter-gatherer tables would source the forager density behind the giants' natural density (meta.forager_km2, 0.1
  per km2, now a setting, PW-976), and could anchor people density per biome (PW-974).

## Megafauna: sizes, metabolism, density

- [x] Sandom, Faurby, Sandel & Svenning 2014, Proc R Soc B 281:20133254, doi:10.1098/rspb.2013.3254. Megafauna extinctions linked
  to people (the prey field's overkill rule). Read 10-29: it gives species lost (not biomass), ~0.02 / 0.23 / 0.46 by hominin history
  (Fig. 3 p. 5); OVERKILL 0.6 flat is a judgement (inbox draft).
- [x] Nagy, Girard & Brown 1999, Annu Rev Nutr 19:247, doi:10.1146/annurev.nutr.19.1.247. Field metabolic rate by class. Read 10-29:
  intercepts 4.82 / 10.5 / 0.196 confirmed (Table 2, p. 260).
- [x] Nagy 2005, J Exp Biol 208:1621, doi:10.1242/jeb.01553. The same, 229 species. Read 10-29: restates the 1999 fits (p. 1622).
- [x] Farlow 1993, Am J Sci 293:167-199, doi:10.2475/ajs.293.a.167. "On the rareness of big, fierce animals". Read 10-29 (a scan, read
  as images): prey turnover 0.94 M^-0.28/yr (p. 172) bounds OFFTAKE; 7 kJ/g live (p. 172); reptile density 66.07 M^-1.01 (p. 187).
- [ ] Damuth 1981, Nature 290:699, doi:10.1038/290699a0, and Damuth 1987, Biol J Linn Soc 31:193-246. Density against body mass
  (does 1987 give reptile intercepts?). 10-29, second-hand: Farlow 1993 p. 187 says 1987 gives reptile data but no reptile regression.
- [x] Ripple et al. 2014, Science 343:1241484. Large carnivores held down by people (the age of dragons). Read 10-29: gives range
  (47% of historical on average, Table 1), not "a few percent of potential"; the citation was wrong (inbox draft).
- [x] Jetz, Carbone, Fulford & Brown 2004, Science 306:266. Home-range size and overlap. Read 10-29: carnivore H = 52.07 ha M^1.20
  (Table 1, p. 268), ~52 km radius at 3.2 t, near FORAGE_KM 60.
- [ ] Grady et al. 2014, Science 344:1268, and the Myhrvold comment and reply (Science 348:982, 2015). Dinosaur mesothermy.
- [ ] Greenewalt 1975, Trans Am Philos Soc 65(4):1-67; Rayner 1988, Current Ornithology 5:1-66. Wing size against mass in birds.
- [ ] McMahon 1973, Science 179:1201; Biewener 1989, Science 245:45. How robust a giant's bones must be.
- [x] (fetched 10-30, fun lane 63; on file) Cardillo et al. 2004, "Human population density and extinction risk in the world's carnivores", PLoS Biol 2:e197 (cited as
  ref. 9 by Ripple et al. 2014, p. 1241484-9; to fetch). The candidate source for how the peoples' pressure on dragons should grow with
  people per km² (megafauna.PRESS_N0, PW-977 stage 3). Named on the dragon-density review (round 1); not yet cited anywhere.
- [ ] (10-30, fun lane 63: abstract only, Cambridge Core and Wiley paywalled; no open copy found; Anim Conserv 3(2):165-173 confirmed) Woodroffe 2000, "Predators and people: using human densities to interpret declines of large carnivores", Animal Conservation
  (volume and pages as a reviewer recalled them, from memory and unverified: 3:165-173). Human-density thresholds for large-carnivore
  persistence: the most direct candidate for PRESS_N0. To fetch; do not cite until read.
- [ ] A sourced above-ground share of grassland net primary production (root:shoot production), to turn the model's whole-plant
  herb-layer NPP into McNaughton et al. 1989's above-ground NAP before their fit (dragon-density review r2, inbox draft). McNaughton's
  own data are above-ground only (p. 142); the share is wanted per biome.
- [ ] A source for rural population densities of late-medieval farming country (people per km²), for the dragon-density page's
  "game present" table, which now borrows the model's own densities.
- [ ] Golley 1961, Ecology 42:581-584 (energy values of ecological materials), cited by McNaughton et al. 1989 for their conversion
  factors (ref. 41, p. 144). Would source prey.KJ_PER_G_DRY (17.5 kJ/g) and C_FRAC (0.45).

The megafauna folder's own index (docs/references/megafauna/README.md) has what we already hold.

## Technology tree dates

techtree.toml (planet/lineages/samples/) marks about 50 dates "unverified": textbook dates the author couldn't tie to a source it
was sure of, and journal references written from memory (PW-943). A general archaeology text would settle most of them at once:

- [ ] A recent world-prehistory textbook, e.g. Scarre (ed.), *The Human Past* (Thames & Hudson, 4th ed. 2018), for the textbook
  dates: ards, canals, iron, coinage, roads, the alphabet, temples, sails and so on.
- [ ] Schmandt-Besserat 1992, *Before Writing* (University of Texas Press). Tokens to writing.
- [ ] Wrangham 2009, *Catching Fire* (Basic Books). How early cooking began.
- [ ] Spot checks of the journal references, since their volume and page numbers were written from memory: Brooks et al. 2018,
  Clarkson et al. 2017, Hardy et al. 2020, Shahack-Gross et al. 2014, Rossel et al. 2008, Schmidt 2010, Geneste et al. 2010.

## Tectonics

- [x] Burke & Dewey 1973, J Geol 81:406-433. Plume-generated triple junctions (triple_rift, PW-952). Read 10-29: ~120 degrees
  confirmed; 32 of 40 mature junctions spread on two arms, 3 on three (p. 426), so our 0.3 per arm splits three ways too often (inbox draft).
- [x] McKenzie 1978, Earth Planet Sci Lett 40:25-32. Stretched margins thin and subside (the shelves work, PW-950). Read 10-29:
  tau 62.8 My and E0 3.2 km water-loaded (Table 1, p. 27) confirm SAG_TIME 63 and SAG_KM 2.2 air-loaded.

## Climate: moisture transport

- [ ] **A source on the transient eddies' poleward moisture flux** (v'q' by latitude, Sv or kg/m/s, and its split from the
  mean meridional circulation), e.g. Peixoto & Oort 1992, *Physics of Climate* (AIP), ch. 12, or a reanalysis study such as
  Trenberth & Stepaniak 2003 (J Climate). Lane 26b's poleward vapour drift (PW-998, docs/review/base-climate/coasts/README.md)
  uses u_e ~ 1 m/s x storminess from a back-of-envelope r x sigma_v x sigma_q / q ~ 0.5 x 6 m/s x 0.3 (all unverified).
  The claim that most of the observed transport at 30-40 deg is transient eddies is also unverified.

## Sapience and language

For the sapiens-node dates (PW-971, docs/review/lineages/sapiens-dates.md). Reading these would settle the "unverified" marks there.

- [ ] Richter et al. 2017, Nature 546:293-296. The Irhoud dating companion to Hublin et al. 2017 (the 315 kyr figure; unverified, from memory).
- [ ] Roebroeks & Villa 2011, PNAS. When fire became habitual (regular use, not first signs); reference written from memory, unverified.
- [ ] Emery & Clayton 2004, Science 306:1903-1907, "The mentality of crows". The full corvid cognition review; reference from memory, unverified.
- [ ] Olkowicz et al. 2016, PNAS. Bird pallium neuron counts, for the avian stem; reference from memory, unverified.
- [ ] A big-cat cognition review (none found), for the feline stem.
- [ ] Hunt 1996, Nature, and Weir, Chappell & Kacelnik 2002, Science. New Caledonian crow hook-making and hook bending, for the bird stems'
  bare tools (techtree.toml `hooked_tools`, PW-987); references from memory, unverified.
- [ ] A review of tool use in living animals (stone hammers and anvils in chimpanzees and capuchins, probing sticks), for `found_tools`
  (PW-987); none chosen yet.
- [ ] The Dikika cut-mark dispute (a rebuttal to McPherron et al. 2010), no reference yet.
- [ ] Dediu & Levinson 2013 full text for the Neanderthal/sapiens split date they use.

## Peoples: the density ladder (PW-1275, lane 130; docs/review/peoples/density-ladder/ladder.md)

- [ ] **Zimmermann, Hilpert & Wendt 2009**, "Estimations of population density for selected periods between the Neolithic and AD
  1800", Human Biology 81(2-3):357-380. Open access on Wayne State Digital Commons (digitalcommons.wayne.edu, humbiol article 1060),
  but the site blocks agents; a browser download works. Its per-period table (Neolithic to 1800, central Europe) would firm up the
  ladder's bronze, iron, medieval and c. 1800 steps.
- [ ] **Boserup 1981**, *Population and Technology* (p. 23, the food-supply systems by density) and **Boserup 1965**: read only as
  quoted by Pingali & Binswanger 1983; that copy gives bush fallow 4-64 /km², the often-quoted figure is 4-16.
- [ ] **An early-modern densest-region source** (the Low Countries, Lombardy or the Yangzi delta c. 1500-1800, persons per km² of
  total land), for the renaissance top of the plough rung (ladder question 7).
- [ ] **Kalff, Downing & Smith 1985**, J. Arid Environments 9:173 (full text; abstract only read): density against rainfall in dry
  Kenya, the agro-pastoral rung's scaling.
- [ ] **Wang & Huang 1999**, Bull. Inst. Hist. Philology 70(2):363 (full text; abstract only): wet-rice densities and their area basis.
