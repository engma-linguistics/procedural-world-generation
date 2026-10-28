# Megafauna references

These are the papers behind `docs/proposals/megafauna-scaling.md`, used for giant and dragon size, food and density. The PDFs stay local: they are gitignored (`docs/references/**/*.pdf`) because of copyright. This README is the index, and it is committed.

**Before citing a paper in code or a ticket, read it here, not from memory.** All the citations were checked against Crossref on 2026-10-28.

**Owner to fetch** (paywalled, or bot-blocked for agents). Fetch these into this folder and tick them off here. PW ticket: PW-962. The PMC items open fine in a browser.

## Have (local PDF)

| File | Citation | Used for |
|---|---|---|
| marshall2021_trex_abundance_science.abc8300.pdf | Marshall et al. 2021, Science 372:284, doi:10.1126/science.abc8300 | Damuth intercepts by physiology; ecological (age-weighted) mass |
| carbone_gittleman2002_carnivore_density_science.1067994.pdf | Carbone & Gittleman 2002, Science 295:2273, doi:10.1126/science.1067994 | carnivore density per prey biomass (Carnivora only) |
| carbone2007_costs_of_carnivory_plosbiol.pdf | Carbone, Teacher & Rowcliffe 2007, PLoS Biol 5:e22 | predators over ~21.5 kg must take large prey |
| field2013_bird_mass_skeletal_plosone.pdf | Field, Lynner, Brown & Darroch 2013, PLoS ONE 8:e82000 | body mass from the skeleton in flying birds |
| sato2009_soaring_seabirds_pterosaurs_plosone.pdf | Sato et al. 2009, PLoS ONE 4:e5400 | the size limit of soaring flight |
| witton2010_giant_pterosaurs_plosone.pdf | Witton & Habib 2010, PLoS ONE 5:e13982 | *Quetzalcoatlus* ~250 kg, ~10.5 m span (dragon wing-loading anchor) |

## Owner to fetch: free in PMC (open in a browser)

- [ ] McNab 2009, PNAS 106:12184, doi:10.1073/pnas.0904000106 (PMC2715483): varanid ~22% of mammal energy use
- [ ] Carbone, Turvey & Bielby 2011, Proc R Soc B 278:2682, doi:10.1098/rspb.2010.2497 (PMC3136829): intra-guild competition, T. rex
- [ ] Chatterjee, Templin & Campbell 2007, PNAS 104:12398, doi:10.1073/pnas.0702040104 (PMC1906724): *Argentavis* flight
- [ ] Ksepka 2014, PNAS 111:10624, doi:10.1073/pnas.1320297111 (PMC4115518): *Pelagornis sandersi* flight
- [ ] Hamilton, Milne, Walker & Brown 2007, PNAS 104:4765, doi:10.1073/pnas.0611197104 (PMC1810510): hunter-gatherer space use (giant forager baseline)

## Owner to fetch: paywalled (most wanted first)

- [ ] McNaughton, Oesterheld, Frank & Williams 1989, Nature 341:142-144, doi:10.1038/341142a0: herbivore biomass, consumption and secondary production against aboveground NPP. **The prey field's fit (planet/lineages/prey.py, PW-966) waits on its biomass regression**: until it is read here, prey is proportional to grazing NPP through one anchor.
- [ ] Coe, Cumming & Phillipson 1976, Oecologia 22:341-354, doi:10.1007/BF00345312: large African herbivore biomass against rainfall and primary production (the second candidate fit for PW-966).
- [ ] Sandom, Faurby, Sandel & Svenning 2014, Proc R Soc B 281:20133254, doi:10.1098/rspb.2013.3254: late-Quaternary megafauna extinctions linked to humans (PW-966 overkill).

- [ ] Nagy, Girard & Brown 1999, Annu Rev Nutr 19:247, doi:10.1146/annurev.nutr.19.1.247. Field metabolic rate per class. The slopes are confirmed from the abstract (reptiles 0.889, mammals 0.734, birds 0.681). **The intercepts used (4.82, 10.5, 0.196, kJ/day with M in g) are unverified.**
- [ ] Farlow 1993, Am J Sci 293:167-199, doi:10.2475/ajs.293.a.167: "On the rareness of big, fierce animals"
- [ ] Damuth 1987, Biol J Linn Soc 31:193-246, doi:10.1111/j.1095-8312.1987.tb01990.x: does it give reptile intercepts?
- [ ] Ripple et al. 2014, Science 343:1241484, doi:10.1126/science.1241484: large carnivores suppressed by people (the age of dragons)
- [ ] Jetz, Carbone, Fulford & Brown 2004, Science 306:266, doi:10.1126/science.1102138: home range and overlap scaling
- [ ] Grady et al. 2014, Science 344:1268, doi:10.1126/science.1253143: dinosaur mesothermy (plus the Myhrvold comment and reply, Science 348:982, 2015)
- [ ] Nagy 2005, J Exp Biol 208:1621, doi:10.1242/jeb.01553: field metabolic rate and body size, 229 species
- [ ] Damuth 1981, Nature 290:699, doi:10.1038/290699a0
- [ ] Greenewalt 1975, Trans Am Philos Soc 65(4):1-67, doi:10.2307/1006161: wing dimensions against mass in birds (the best raptor and flier allometry found; no good raptor-only paper turned up)
- [ ] Rayner 1988, Current Ornithology 5:1-66, doi:10.1007/978-1-4615-6787-5_1
- [ ] McMahon 1973, Science 179:1201, doi:10.1126/science.179.4079.1201: elastic similarity (giant robustness)
- [ ] Biewener 1989, Science 245:45, doi:10.1126/science.2740914
- [ ] Campione, Evans, Brown & Carrano 2014, Methods Ecol Evol 5:913, doi:10.1111/2041-210x.12226: body mass from limb bones in bipeds
- [ ] Binford 2001, *Constructing Frames of Reference* (UC Press), doi:10.1525/9780520925069: the hunter-gatherer density dataset (a book)
