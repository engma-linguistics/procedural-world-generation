# Claims ledger: Dragons and their food (index.html)

Round 2, 2026-10-29. One row per cited claim; the id matches an `<!-- Cn -->` comment beside the sentence in `sections/*.html`
(and so in `index.html`). Claims without a comment tag but with a citation in a table cell (Section 3's Table 1, Section 9.2's
Table 9) are listed under "Table citations" below. PDFs: `docs/references/megafauna/` (gitignored; read in the main checkout).
Page numbers are the journal's printed page numbers, checked against the PDF page. Farlow 1993 is a scan with no text layer and
was read as page images; every Farlow quote below was read on the image of its page in round 2.

**Section numbers in the claim rows and table-citation rows are the pre-restructure draft's** (see `changes-r2.md`): add one to
Sections 1-6 (results 4.x are now 5.x); old Section 7 is now 9.2, old Section 9 is 9.1, old Table 7 is Table 9. The run-derived
map below uses the published numbers.

Model code: main at b36c9581; the sweep ran from snapshot 8c7ce305 (main + the measuring script). `numbers.json` is written by
`dragon_numbers.py` from the sweep in `/home/daniel/personal/repos/procedural-world-generation/data/review-inputs/dragon-r2/`.
Every model number on the page is a `{{ expression }}` over `numbers.json` (or `charts/boxes.json`) in `sections/*.html`; the
expression beside each sentence is its source. Round-1 changes are marked **r2**.

## Cited claims

| id | claim on the page (shortened) | paper, location | what the paper says there | how the model uses it |
|---|---|---|---|---|
| C1 | Grazing NPP becomes herbivore biomass by log10 B = 1.52 log10 NAP − 4.79 (51 points, r² = 0.579) | McNaughton et al. 1989, p. 143 | "Herbivore biomass (B) was related (coefficient of determination r2 = 0.579, P < 0.00001, degrees of freedom (d.f.) = 49) to net primary productivity (NAP) by log B = 1.52 (log NAP) − 4.79"; slope "significantly greater than 1" | **Adapted**: same fit in `prey.wild`, fed the model's grazing NPP (C24) |
| C2 | The paper converts masses "using standard conversion factors" without giving them; cites Golley 1961, Schroeder 1977, Whitfield 1977 | McNaughton et al. 1989, pp. 142–143 (**r2**: was p. 143) | the sentence runs across the page break; refs 41–43 | **Differs**: model adds `prey.C_FRAC` 0.45 and `KJ_PER_G_DRY` 17.5 (unsourced), `KJ_PER_G_LIVE` 7.0 (C6) |
| C3 | Coe et al.'s fit, log10 B = 1.094 log10 NAAP + 0.389 (r = 0.966; B large herbivores kg/km² live weight; NAAP g dry/m²/yr predicted from rainfall by Rosenzweig 1968; 12 areas under 700 mm), gives 0.8 / 1.9 / 4.9 t/km² | Coe, Cumming & Phillipson 1976, Fig. 3, p. 349; p. 347 (NAAP from rainfall) | Fig. 3: "y = 1.094 (± 0.206) x + 0.389 (± 0.571), r = 0.966, P < 0.001, N = 12" (**r2**: r now quoted; read on the page) | **Not used**; cross-check |
| C4 | McNaughton's NSP fit against the biomass fit gives 1.1 / 0.77 / 0.54 × standing biomass a year; a ratio of two fits to different data, both including insects, so a weak bound | McNaughton et al. 1989, p. 143 | "net secondary productivity (NSP) was related (r2 = 0.364, P < 0.0001, d.f. = 34) to NAP by log NSP = 1.10 (log NAP) − 3.27" | **Differs**: flat `OFFTAKE` 0.1 (**r2**: caveat added per reviewer) |
| C5 | Prey turnover 0.94 M^−0.28 a year: 0.26 / 0.16 / 0.14 at 100 / 500 / 1,000 kg | Farlow 1993, eq. 6, p. 172 | "Prey turnover rate = 0.94 * mass^(−0.28)", mass in kg, rate in yr⁻¹ | **Differs**: one number, 0.1 |
| C6 | 7 kJ per g live animal | Farlow 1993, p. 172 | "the energy content of animal tissue approximates 7 * 10^6 joules/kg live mass" | **Identical**: `KJ_PER_G_LIVE`, `CATTLE_MCAL` 836 |
| C7 | Reptile FMR 0.196 M^0.889 kJ/day (M g), all reptiles, n = 55 | Nagy, Girard & Brown 1999, Table 2, eq. 32, p. 261 (**r2**: page narrowed) | Table 2 row "All reptiles 0.196 0.889 55" | **Adapted**: `dragon_ages.fmr_kcal`, extrapolated to every age (C27, C28) |
| C8 | Size classes 20.6 kg (79.9%), 58.3 (19.0%), 1,123 (0.9%), 5,347 (0.1%), the guild's *predicted* shares of individuals | Carbone, Turvey & Bielby 2011, Table 1, p. 2683 | "mass categories, kg (with estimated %)" | **Identical**: `GUILD_CLASSES` (**r2**: "predicted") |
| C9 | The shares come from Carbone & Gittleman's mammalian line 1.97 M^−0.88 per km² (197.6 M^−0.88 per 100 km², their Fig. 2B), summed over each class's species | Carbone et al. 2011, p. 2685 (**r2**: was p. 2684) | "Estimates of carnivorous theropod dinosaur abundances were derived from mammalian carnivore data [47], where e = 1.97 and f = −0.88" | Context for C8 |
| C10 | The M^0.75 weighting has a source: carnivores per unit of prey production expected as M^−0.75, fitted −0.66 (CL −0.48 to −0.85), "not significantly different from −0.75" | Carbone & Gittleman 2002, p. 2274; note 10, p. 2275 (**r2**: was "Kleiber, not from the paper") | as quoted | **Adapted**: `GUILD_KLEIBER` 0.75 → apex share 16.8% |
| C11 | Carnivores per 10,000 kg prey = 89.1 M^−1.05 (N = 25, R² = 0.83): 1 per 269 km² at 1 t/km² for a 1.65 t carnivore; fit's heaviest species 310 kg; prey = main prey species (≥ 70% of diet) | Carbone & Gittleman 2002, p. 2274; Table 1; note 21, p. 2275 | as quoted | **Cross-check** (`natural = "prey"` mode) |
| C12 | "about 90 kilograms" is the fit's value at 1 kg; at 1.65 t the fit gives 62 kg per 10,000 kg of prey, the model's dragons 104 kg (1.7×) | Carbone & Gittleman 2002, p. 2273 (abstract) | "10,000 kilograms of prey supports about 90 kilograms of a given species of carnivore" | **r2**: compared against the fit at 1.65 t, not the constant (reviewer `carbone` item 1) |
| C13 | Mammalian carnivores N⁻¹ = 34.43 ha × M^0.86 (n = 38): 1 per 202 km²; crosses the model at 0.79 t/km² | Jetz et al. 2004, Table 1, p. 268 | Table 1 row Carn, N⁻¹ | **Not used**; cross-check |
| C14 | Carnivore home range 52.07 ha × M^1.20 (n = 70): 3,800 km² at 1.65 t, a 35 km radius disc; the model's 60 km reach ≈ 11,300 km² | Jetz et al. 2004, Table 1, p. 268 | Table 1 row Carn, H | **Differs**: `FORAGE_KM` 60 (**r2**: "radius" made explicit) |
| C15 | Reptile density 66.07 M^−1.01 per km², Damuth's data with Komodo dragon data added: 1 per 27 km² at 1.65 t; largest reptile > 2 orders lighter | Farlow 1993, p. 187 | as quoted (**r2**: "Komodo dragon data added", reviewer `farlow` item 6) | **Not used**; cross-check |
| C16 | Mammal communities "usually somewhere between 200:1 and 100:1", "can get as low as 45:1"; 50:1 and 10:1 are best-case minima; model 127:1 (96:1 at eco mass) | Farlow 1993, p. 176; pp. 171–172; p. 187 | as quoted; p. 187 "a limiting, extreme case" | Comparison (our arithmetic) |
| C17 | Round 1's reading reversed: reptile-like food needs + a high ratio ⇒ populations held "considerably smaller than their food requirements alone would have dictated" | Farlow 1993, p. 190 | "If the ornithischian:tyrannosaur ratio was high as suggested by Brinkman's (1990) study, and if we want to argue that tyrannosaurs were more reptile-like than mammal-like or bird-like in their food requirements, we must then conclude that tyrannosaur populations were regulated by some factor(s) that kept them considerably smaller than their food requirements alone would have dictated." (read on the page image) | **r2**: argument reversed (reviewer `farlow` item 1; owner note 3) |
| C18 | Smaller predators share the prey production; Farlow's own correction halves the apex predator (50:1 → 100:1), milder than the model's 16.8% | Farlow 1993, p. 176 | "It is unrealistic to suppose that an ecological community that included dinosaur-sized carnivorous mammals would not also include smaller predators…" | Support for the split's existence, not its size (**r2**: Farlow's milder correction added) |
| C19 | Overkill: species lost depends on co-evolution, medians ~2% / ~23% / ~46%; "universally low extinctions in sub-Saharan Africa (maximum 13%)"; species, not biomass | Sandom et al. 2014, Fig. 3, p. 5; p. 6 | Fig. 3 box plot; p. 6 as quoted | **Differs**: flat `prey.OVERKILL` 0.6 |
| C20 | Ripple: "17 of the 31" with estimates hold on average 47% of historical range; pumas tolerate more human land use than wolves | Ripple et al. 2014, p. 1241484-1; p. 1241484-6 | "Estimates of range contractions for 17 of the 31 species revealed that they currently occupy on average only 47%…"; "pumas are able to persist in areas with much higher levels of human land use than are gray wolves" | **Differs**: `PRESS_N0`, `meta.dragon_km2` unsourced (**r2**: "17 of 31" wording) |
| C21 | Farlow's food budget form: predator density × mass × intake = prey density × mass × turnover | Farlow 1993, eqs. 3–5, p. 172 | "Equation 4.—(Predator density) * (average predator mass) * (predator mass-specific food consumption rate) = (prey density) * (average prey mass) * (prey turnover rate)" | **Adapted** |
| C22 | Hamilton 2007: all foragers exponent 0.70; C0 is ln(km²); Table 1 prints 4.44, Fig. 1 prints 4.14; groups of 25–1,000 at 0.03–0.09 (4.44) or 0.04–0.13 (4.14) people/km² | Hamilton et al. 2007, Table 1, p. 4767; Fig. 1, p. 4766 | Table 1 All foragers β_N = 0.70, C0 = 4.44; Fig. 1 fit ln A = 0.70 ln N + 4.14 | Reading (**r2**: unit settled, both constants given) |
| C23 | Whole guild ≈ 46:1 (all ages), 35:1 (eco mass) | our arithmetic on C8, C16 | Σ n·M under 1 t / ≥ 1 t = 1.78 | **r2**: eco-mass figure added (reviewer `carbone` item 6) |
| C24 | McNaughton's NAP is above-ground only; the model's NPP is whole-plant; 2× input → 2^1.52 = 2.9× biomass | McNaughton et al. 1989, p. 142; Fig. 1 caption | "Only processes occurring above ground were included"; "net above-ground primary productivity" | **Differs**: whole-plant herb NPP + 30% shrub browse (vegetation's grazing NPP). New in r2 |
| C25 | McNaughton's B includes insects | McNaughton et al. 1989, p. 143 | "dominance by heterotherm herbivores in forests and homeotherms in grasslands" | **Differs**: read as big game. New |
| C26 | Coe: production 0.085–0.26 of biomass a year across 24 areas (median 0.20), from assumed P/B 0.05 / 0.20 / 0.35 | Coe et al. 1976, Table 1, pp. 344–345; pp. 343–344 | Table 1 biomass and production columns (transcribed in `sensitivity.py` `COE_B`, `COE_P`) | Bound on `OFFTAKE`. New |
| C27 | 2.7 t is the all-ages mean (a single ~1.0 t reptile's rate); a 1.65 t dragon kills 4.1 t; adults and ancients eat 84% of the food | model arithmetic (Nagy eq. 32) | — | **r2**: mass framing fixed (reviewer `nagy` item 1; owner note 3) |
| C28 | The fit's largest reptile is the 45.2 kg Komodo dragon; outside the masses the 95% interval "will be larger" | Nagy et al. 1999, Table 1, p. 258; p. 262 | Table 1 row Varanus komodoensis 45,200 g; p. 262 as quoted | New |
| C29 | A species' FMR can be "as low as 30% of predicted or as high as 170%"; food equations leave out growth | Nagy 2005, p. 1622; p. 1624 | as quoted; growth not counted | New |
| C30 | Varanids 1.07 M^0.735 kJ/day (2.2–45.2 kg), 22% of mammals; dinosaurs "31% of mammals" | McNab 2009, p. 12185; p. 12187 | as quoted | New (sensitivity rows) |
| C31 | Marshall's "ecological body mass" (survivorship-weighted, post-juvenile); "midway" physiology | Marshall et al. 2021, p. 284 | "physiology midway between that of mammalian carnivores and that of large varanid lizards" | `chain.eco_mass_kg` is this measure. New |
| C32 | One-at-a-time factors and joint cases | our arithmetic, `sensitivity.py` | — | New (Section 2) |
| C33 | Farlow's ectotherm intake (eq. 8, 3.81 M^−0.16 kg/kg/yr) gives 1.9 t/yr at 1.65 t, endotherm (eq. 7, 48.87 M^−0.30) 8.7 t; model 4.1 t at that mass | Farlow 1993, eq. 7, p. 172; eq. 8, p. 187 | equations as printed | Cross-check. New |
| C34 | Damuth's law a M^−0.75 (M g), log10 a = 2.99 (95%: 1.80–4.18): 1 per 47 km² at 1.65 t (1 per 730 to 1 per 3.0); model matches at 3.4 t/km² | Marshall et al. 2021, Table 1, p. 284 | Table 1 intercepts | `megafauna.LOG_A["mesotherm"]` = 2.99 (the `mesotherm` mode). New |
| C35 | Top species' mass vs land area: endothermic carnivore 0.05 A^0.47, ectothermic 0.25 A^0.47 kg → 63 / 310 kg on 3.88 M km²; dinosaurs ~12× heavier for the same area → ~3.8 t | Burness et al. 2001, p. 14520 (fits); p. 14523 (dinosaur offset) | as printed | Comparison (our arithmetic). New |
| C36 | Big-theropod fauna ratios 10:1 (Judith River articulated) to Brinkman's mean 115:1; "could have been as low as 10:1 or as high as 100:1" | Farlow 1993, p. 189; p. 190 | as quoted (page images) | Comparison. New |
| C37 | ~20,000 post-juvenile *T. rex* on 2.3 ± 0.88 M km² (95%: 1,300–328,000); "the loose consensus that at least thousands of individuals are needed for long-term persistence" | Marshall et al. 2021, p. 285; Table 2 | as quoted | Viability comparison. New |
| C38 | MVP: "frequent estimates are a few thousand to at least 10,000 individuals" | Burness et al. 2001, p. 14521 | as quoted | Viability comparison. New |
| C39 | A 200 kg crocodile produces "only 14% of that for a mammal"; crocodiles "lack not only the absolute power for exercise, but also the endurance" | Seymour 2013, abstract, p. 1 (e69361) | as quoted | Argument on flight and intake. New |
| C40 | Hamilton 2009 forager densities (groups of 25–1,000) ~0.03–0.11 people/km² | Hamilton et al. 2009, Fig. 2, p. 12257 | Fig. 2 fit 0.72x + 0.61 (log10 area against log10 N; our arithmetic for densities) | Reading. New |

## Table citations (no comment tag)

| where | claim | paper, location |
|---|---|---|
| Table 1, Section 7 | Assimilation 0.66 | Carbone, Teacher & Rowcliffe 2007, p. 364 |
| Table 1, Section 7 | "only a proportion of large-vertebrate prey are consumed (65%–91% depending on their mass)" | Carbone et al. 2007, p. 367 |
| Table 1, Section 7 | Exponent 0.79 across carnivores; 0.6 within large-prey hunters | Carbone et al. 2007, Table 1 and p. 364 |
| Table 1 | Nagy's food conversion 16.8 kJ/g dry matter, 30% dry matter → 5.04 kJ/g fresh | Nagy et al. 1999, pp. 263–264 |
| Table 1 | All lizards 0.190 M^0.916 (eq. 33), Varanidae 0.208 M^0.915 (eq. 36); mammals 4.82 M^0.734, birds 10.5 M^0.681 | Nagy et al. 1999, p. 261; Table 2, p. 260 |
| Section 7 item 8 | Juvenile *T. rex* "relatively abundant"; the classes use adult masses | Carbone et al. 2011, p. 2683 |
| Section 4.4 | "We might expect ectothermic theropods to obtain higher densities for a given density of prey/carcasses" | Carbone et al. 2011, p. 2687 |
| Section 4.4 | Home ranges overlap, so area per animal is far below home range | Jetz et al. 2004, p. 268 |

## Unsourced constants named on the page

`planet/lineages/history/megafauna.py`: `OFFTAKE` 0.1, `STOCK_TOLERABLE` 0.1, `PERSON_KCAL_YR` (2,200 kcal/day), `WILD_MEAT` (0.5, 0.05),
`HEAD_KCAL` 625,000, `PRESS_N0` 0.05, `FORAGE_KM` 60; `meta.dragon_km2` 5,000; `planet/lineages/prey.py`: `OVERKILL` 0.6, `C_FRAC` 0.45,
`KJ_PER_G_DRY` 17.5; `planet/lineages/dragon_ages.py`: `ASSIMILATED` 0.85. (`GUILD_KLEIBER` 0.75 now has a source, C10.)

## Run-derived numbers

All are `{{ … }}` expressions in `sections/*.html` over `numbers.json`; the main keys:

| on the page | numbers.json |
|---|---|
| Table 2, Figure 2 | `on.eras.{25,10,0}.{class}.per_1000km2`, `.land_share`, `.per_1000km2_runs_min/max`; `off.eras.0.*`; `paired.0.{class}.{median,min,max}` |
| Section 4 area divergence | `paired.0.{class}.area_on_over_off_{min,max}` |
| Table 3 | `channels_7000.0.{class}.{on,noper,off,noper_peoples_share}` |
| Figure 3, Section 5.2 | `on.eras.{25,0}.{class}.shares` (`guild` = smaller predators, `food` = dragons' share, `dragons_need` = eaten) |
| Section 5.3, Table 4, Figure 4 points | `cells.on.0.none_now`, `cells.on.0.rich_poor`, `cells.on.0.binned` |
| Section 5.4 lines | `literature.*` |
| Section 5.5, Figure 5 | `steps.{on,off}.{30,300}_summary`, `steps.on.peak`, `step30_eras`, `series` |
| Tables 5 and 6 | `cells.{on,noper,off}.0.biome_situation` (best guess: `build_page.gpv`) |
| Tables 7, 8 | `sword_coast.counts`, `sword_coast.formula`, `sword_coast.largest_kind_share`; `charts/boxes.json` |
| Table 1, Figure 1 | `sensitivity.rows`, `sensitivity.combined`, `sensitivity.coe_pb` |

## Code map (repo-side only; the published page carries no code names or ticket ids)

| on the page | code | ticket / draft |
|---|---|---|
| McNaughton fit, unit factors (0.45, 17.5, 7 kJ/g) | `planet/lineages/prey.py`: `wild`, `C_FRAC`, `KJ_PER_G_DRY`, `KJ_PER_G_LIVE` | PW-966; `draft-prey-fit-fed-whole-plant-npp.md` |
| Grazing NPP fed to the fit (herb NPP + 30% shrub browse, open-months factor) | vegetation's `grazing_npp` game attribute (`planet/gameattrs.py`), read in `planet/lineages/recent.py` | same draft |
| Overkill 60%, refuges (tundra, mountain) | `prey.OVERKILL`, `prey.REFUGE`, `prey.field` | PW-1000 |
| 10% offtake, 10% stock | `planet/lineages/history/megafauna.py`: `OFFTAKE`, `STOCK_TOLERABLE` | PW-991; `draft-offtake-from-prey-production.md` |
| Peoples' game (2,200 kcal/day, 50% / 5%, 625,000 kcal a head) | `PERSON_KCAL_YR`, `WILD_MEAT`, `HEAD_KCAL` | PW-1018, PW-1019 |
| Guild split | `GUILD_CLASSES`, `GUILD_APEX_KG`, `GUILD_KLEIBER`, `guild_ratio()` | PW-1019; `draft-guild-weighting-exponent-and-young-dragons.md` |
| Dragon intake (reptile FMR, 85%, 836 Mcal carcass; "younger" age schedule) | `planet/lineages/dragon_ages.py`: `fmr_kcal`, `ASSIMILATED`, `CATTLE_MCAL` | `draft-dragon-intake-law-and-label.md`, `draft-dragon-kill-conversion-assimilation-carcass.md` |
| Food budget (peoples, giants, guild, 60 km reach) | `megafauna.budget`, `BUDGET`, `FOOD_CAP`, `FORAGE_KM` | PW-977 stage 2; `draft-food-budget-uneaten-share-and-unpressed-small-predators.md` |
| Pressure 1 − exp(−N/0.05), toward 1 per 5,000 km² | `megafauna.pressure`, `PRESS_N0`, `_pressed`; endpoint `meta.dragon_km2` | PW-977 stage 3, PW-1001; `draft-dragon-pressure-source.md` |
| Habitat, occupancy, viability, 7,500 km linking | `SUITABLE`, `LINK_KM`, `SCATTER_LINKS`, `metapop_km`, `History._viable`, `History.line_mvp` | PW-924, PW-936; `draft-dragon-habitat-coverage-rich-land.md`, `draft-dragon-viability-at-regional-counts.md` |
| Natural-density modes (food default; prey; mesotherm; mammal) | `NATURAL`, `LOG_A` (Marshall intercepts) | PW-990 |
| Deep-epoch flat density | `megafauna` deep-epoch rule | `draft-deep-epoch-dragon-budget.md` |
| 30 kyr step | glacial / recent pass hand-over (`planet/lineages/history/steps.py`, `RecentParams.kyr`) | `draft-dragon-count-step-at-recent-pass.md` |
| Dense hunter peoples; people density from productivity | dnd tree line densities; `prey.GRAZE_REF` = 279 | PW-1018, PW-1020 |
| "The setting's roster" | the dnd tree; "global grid of ~3,113 km² cells" = grid level 7 | — |
| Viewer layer (not on the page) | — | `draft-viewer-dragon-density-layer.md` |

## Reproducing the page

- Inputs (persistent, outside the repo): `/home/daniel/personal/repos/procedural-world-generation/data/review-inputs/dragon-r2/`.
  `run.sh` runs `jobs.txt` (54 jobs, 6 at a time) through `job.sh`, which exports the model at commit 8c7ce305 (main b36c9581 +
  `probe.py`'s round-2 options) and runs `docs/review/megafauna/probe.py WORLD ROLL OUT.json --eras 31,29,25,10,0 --cells DIR`, with
  `--no-press` (pressure off) or `--no-persecute` (persecution off). Each output records `rev`.
- Numbers: `PYTHONPATH=. uv run python docs/review/megafauna/dragon-density/dragon_numbers.py DIR docs/review/megafauna/dragon-density/numbers.json` (imports `sensitivity.py`, analytic).
- Charts: `PYTHONPATH=. uv run --with matplotlib python docs/review/megafauna/dragon-density/charts.py docs/review/megafauna/dragon-density/numbers.json DIR docs/review/megafauna/dragon-density/charts` (light and dark copies; `charts/boxes.json`).
- Page: `uv run python docs/review/megafauna/dragon-density/build_page.py` fills every `{{ … }}` in `page.tmpl.html` and `sections/*.html` (plain, abstract, then `NN-*.html` in order).
- Check: `uv run --with playwright python <check script>` at 1200 and 390 px, light and dark, on `file://` (no server needed).
