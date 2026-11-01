# Megafauna references

These are the papers behind `docs/proposals/megafauna-scaling.md`, used for giant and dragon size, food and density. The PDFs stay local: they are gitignored (`docs/references/**/*.pdf`) because of copyright. This README is the index, and it is committed.

**Before citing a paper in code or a ticket, read it here, not from memory.** All the citations were checked against Crossref on 2026-10-28.

**Owner to fetch** (paywalled, or bot-blocked for agents). Fetch these into this folder and tick them off here. PW ticket: PW-962. The PMC items open fine in a browser.

## Have (local PDF)

| File | Citation | Used for |
|---|---|---|
| marshall2021_trex_abundance_science.abc8300.pdf | Marshall et al. 2021, Science 372:284, doi:10.1126/science.abc8300 | Damuth intercepts by physiology; ecological (age-weighted) mass |
| carbone_gittleman2002_carnivore_density_science.1067994.pdf | Carbone & Gittleman 2002, Science 295:2273, doi:10.1126/science.1067994 | carnivore density per prey biomass (Carnivora only) |
| carbone2007_costs_of_carnivory_plosbiol.pdf | Carbone, Teacher & Rowcliffe 2007, PLoS Biol 5:e22 | carnivores over a predicted 14.5 kg threshold (observed ~15-20 kg) gain more from large prey (read 2026-10-28; the earlier "~21.5 kg" is not in this paper) |
| field2013_bird_mass_skeletal_plosone.pdf | Field, Lynner, Brown & Darroch 2013, PLoS ONE 8:e82000 | body mass from the skeleton in flying birds |
| sato2009_soaring_seabirds_pterosaurs_plosone.pdf | Sato et al. 2009, PLoS ONE 4:e5400 | the size limit of soaring flight |
| witton2010_giant_pterosaurs_plosone.pdf | Witton & Habib 2010, PLoS ONE 5:e13982 | *Quetzalcoatlus* 200-250 kg, 10-11 m span (abstract; Table 2 uses 10.40 m at 250 kg, p. 7) (dragon wing-loading anchor) |
| carbone2011_intraguild_trex_procb.pdf | Carbone, Turvey & Bielby 2011, Proc R Soc B 278:2682, doi:10.1098/rspb.2010.2497 | intra-guild competition, T. rex |
| ksepka2014_pelagornis_flight_pnas.pdf | Ksepka 2014, PNAS 111:10624, doi:10.1073/pnas.1320297111 | *Pelagornis sandersi* flight, the largest volant bird |
| hamilton2009_population_stability_huntergatherers_pnas.pdf | Hamilton, Burger, DeLong, Walker, Moses & Brown 2009, PNAS 106:12255-12260, doi:10.1073/pnas.0905708106 (title: "Population stability, cooperation, and the invasibility of the human species") | hunter-gatherer density dependence; NOT the 2007 space-use paper listed below |
| alexander2007_argentavis_commentary_pnas.pdf | Alexander 2007, PNAS 104:12233-12234, doi:10.1073/pnas.0705515104, commentary "Ancient Argentavis soars again" | commentary on Chatterjee et al. 2007; NOT the paper itself |
| seymour2013_crocodile_power_gigantothermy_plosone.pdf | Seymour 2013, PLoS ONE 8:e69361 | aerobic and anaerobic power in large crocodiles vs mammals; dinosaur gigantothermy (bonus, not on the list) |
| nagy1999_field_metabolic_rate_annurevnutr.pdf | Nagy, Girard & Brown 1999, Annu Rev Nutr 19:247-277, doi:10.1146/annurev.nutr.19.1.247 | field metabolic rate: mammals 4.82 M^0.734, birds 10.5 M^0.681, reptiles 0.196 M^0.889 kJ/day, M in g (Table 2, p. 260; intercepts now confirmed); Komodo dragon 45.2 kg, 2,430 kJ/day (Table 1, p. 258); metabolizable energy per g dry diet (pp. 263-264) |
| nagy2005_fmr_body_size_jeb.pdf | Nagy 2005, J Exp Biol 208:1621-1625, doi:10.1242/jeb.01553 | restates the 1999 class fits (p. 1622); endotherms 8.53 M^0.676 |
| coe1976_african_herbivore_biomass_rainfall_oecologia.pdf | Coe, Cumming & Phillipson 1976, Oecologia 22:341-354, doi:10.1007/BF00345312 | log10 B = 1.094 log10 NAAP + 0.389 (B kg/km2 live, NAAP g dry/m2/yr, < 700 mm rain, N = 12; Fig. 3, p. 349); on rainfall 1.685 log10 P - 1.095 (Fig. 4, N = 20). Agrees with prey.py within 1.4x (PW-975) |
| sandom2014_megafauna_extinctions_humans_procb.pdf | Sandom, Faurby, Sandel & Svenning 2014, Proc R Soc B 281:20133254, doi:10.1098/rspb.2013.3254 | share of large-mammal species (>= 10 kg) lost per country: median ~0.02 where hominins evolved, ~0.23 archaic, ~0.46 where modern humans came first (Fig. 3, p. 5); species, not biomass (prey.OVERKILL; inbox draft) |
| farlow1993_rareness_big_fierce_animals_ajs.pdf | Farlow 1993, Am J Sci 293-A:167-199, doi:10.2475/ajs.293.a.167 | a scan with no text layer (read as page images). Prey turnover 0.94 M^-0.28/yr and 7 kJ per g live mass (p. 172); prey:predator 100:1-200:1 (p. 176); Damuth 1987 carnivores 3.89 M^-0.96 (p. 177); reptile density 66.07 M^-1.01, ectotherm intake 3.81 M^-0.16 (p. 187); Belovsky minimum populations (p. 175) |
| ripple2014_large_carnivores_science.pdf | Ripple et al. 2014, Science 343:1241484, doi:10.1126/science.1241484 | large carnivores' range loss: 17 of the 31 largest hold on average 47% of their historical range, tiger 18%, lion 17% (p. 1241484-2, Table 1); no density-against-potential figure (the "few percent" was wrongly cited to it) |
| riggio2013_savannah_africa_lion_view_biodivconserv.pdf | Riggio et al. 2013, Biodivers Conserv 22:17-35, doi:10.1007/s10531-012-0381-4 (CC-BY) | lion areas exclude land above 25 people per km2 (p. 21, rule 3), the density best matching land converted to crops, overlap peaking between 10 and 25 (p. 23); "Woodroffe (2000) estimated a mean human population density threshold at which lions went extinct of 26 people per km2" (p. 30); lion areas ~3.4 Mkm2, 25% of savannah Africa (p. 29). The persecution's extirpation threshold (history.megafauna.LOSS_KM2, lane 103) |
| cardillo2004_hpd_carnivore_extinction_plosbiol.pdf | Cardillo, Purvis, Sechrest, Gittleman, Bielby & Mace 2004, PLoS Biol 2:e197, doi:10.1371/journal.pbio.0020197 (open access; fetched 2026-10-30, fun lane 63) | carnivore extinction risk against human density: thresholds 2-100 people/km2 (Table 1, p. 0910); the share of range at >= 10/km2 the best predictor (Table 2 note, p. 0911); slow life history matters where people are dense, persecution named (Table 3, pp. 0911-0912); technology can outweigh numbers (p. 0911). The persecution kill's evidence (megafauna.kill, PW-1068) |
| jetz2004_animal_space_use_science.pdf | Jetz, Carbone, Fulford & Brown 2004, Science 306:266-268, doi:10.1126/science.1102138 | home range per individual: all mammals 6.69 ha M^1.07, carnivores 52.07 ha M^1.20 (M kg; Table 1, p. 268); overlap grows with size |
| burness2001_dinosaurs_dragons_dwarfs_pnas.pdf | Burness, Diamond & Flannery 2001, PNAS 98:14518-14523, doi:10.1073/pnas.251548698 (not on the list) | top species' mass against land area: endothermic herbivores 0.47 A^0.52, endothermic carnivores 0.05 A^0.47, ectothermic carnivores 0.25 A^0.47 kg (A km2; p. 14520) |

## Owner to fetch: free in PMC (open in a browser)

- [x] McNab 2009 (mcnab2009_dinosaur_energetics_pnas.pdf), PNAS 106:12184, doi:10.1073/pnas.0904000106 (PMC2715483): varanid ~22% of mammal energy use
- [x] Carbone, Turvey & Bielby 2011, Proc R Soc B 278:2682, doi:10.1098/rspb.2010.2497 (PMC3136829): intra-guild competition, T. rex
- [x] (chatterjee2007_argentavis_aerodynamics_pnas.pdf) Chatterjee, Templin & Campbell 2007, PNAS 104:12398, doi:10.1073/pnas.0702040104 (PMC1906724): *Argentavis* flight
- [x] Ksepka 2014, PNAS 111:10624, doi:10.1073/pnas.1320297111 (PMC4115518): *Pelagornis sandersi* flight
- [x] (hamilton2007_spaceuse_huntergatherers_pnas.pdf) Hamilton, Milne, Walker & Brown 2007, PNAS 104:4765, doi:10.1073/pnas.0611197104 (PMC1810510): hunter-gatherer space use (giant forager baseline)

## Owner to fetch: paywalled (most wanted first)

2026-10-29: the owner's batch is in (ticked). The unticked rest are not expected.

- [x] (mcnaughton1989_herbivore_biomass_productivity_nature.pdf) McNaughton, Oesterheld, Frank & Williams 1989, Nature 341:142-144, doi:10.1038/341142a0: herbivore biomass, consumption and secondary production against aboveground NPP. **Read (PW-975)**: log10 B = 1.52 log10 NAP - 4.79 (kJ/m2 and kJ/m2/yr; r2 0.579, d.f. 49) is prey.py's fit. The paper gives no kJ-to-mass conversions (cites "standard factors", refs 41-43), so prey.py's three conversion constants are unverified assumptions.
- [x] (coe1976_african_herbivore_biomass_rainfall_oecologia.pdf) Coe, Cumming & Phillipson 1976, Oecologia 22:341-354, doi:10.1007/BF00345312: large African herbivore biomass against rainfall and primary production (the second candidate fit for PW-966).
- [x] (sandom2014_megafauna_extinctions_humans_procb.pdf) Sandom, Faurby, Sandel & Svenning 2014, Proc R Soc B 281:20133254, doi:10.1098/rspb.2013.3254: late-Quaternary megafauna extinctions linked to humans (PW-966 overkill).

- [x] (nagy1999_field_metabolic_rate_annurevnutr.pdf) Nagy, Girard & Brown 1999, Annu Rev Nutr 19:247, doi:10.1146/annurev.nutr.19.1.247. Field metabolic rate per class. **Read 10-29:** slopes and intercepts (4.82, 10.5, 0.196, kJ/day with M in g) confirmed, Table 2, p. 260.
- [x] (farlow1993_rareness_big_fierce_animals_ajs.pdf) Farlow 1993, Am J Sci 293:167-199, doi:10.2475/ajs.293.a.167: "On the rareness of big, fierce animals"
- [ ] Damuth 1987, Biol J Linn Soc 31:193-246, doi:10.1111/j.1095-8312.1987.tb01990.x: does it give reptile intercepts? (Farlow 1993, p. 187: it gives reptile data but no regression.)
- [x] (ripple2014_large_carnivores_science.pdf) Ripple et al. 2014, Science 343:1241484, doi:10.1126/science.1241484: large carnivores suppressed by people (the age of dragons)
- [x] (jetz2004_animal_space_use_science.pdf) Jetz, Carbone, Fulford & Brown 2004, Science 306:266, doi:10.1126/science.1102138: home range and overlap scaling
- [ ] Grady et al. 2014, Science 344:1268, doi:10.1126/science.1253143: dinosaur mesothermy (plus the Myhrvold comment and reply, Science 348:982, 2015)
- [x] (nagy2005_fmr_body_size_jeb.pdf) Nagy 2005, J Exp Biol 208:1621, doi:10.1242/jeb.01553: field metabolic rate and body size, 229 species
- [ ] Damuth 1981, Nature 290:699, doi:10.1038/290699a0
- [ ] Greenewalt 1975, Trans Am Philos Soc 65(4):1-67, doi:10.2307/1006161: wing dimensions against mass in birds (the best raptor and flier allometry found; no good raptor-only paper turned up)
- [ ] Rayner 1988, Current Ornithology 5:1-66, doi:10.1007/978-1-4615-6787-5_1
- [ ] McMahon 1973, Science 179:1201, doi:10.1126/science.179.4079.1201: elastic similarity (giant robustness)
- [ ] Biewener 1989, Science 245:45, doi:10.1126/science.2740914
- [ ] Campione, Evans, Brown & Carrano 2014, Methods Ecol Evol 5:913, doi:10.1111/2041-210x.12226: body mass from limb bones in bipeds
- [ ] Binford 2001, *Constructing Frames of Reference* (UC Press), doi:10.1525/9780520925069: the hunter-gatherer density dataset (a book)
