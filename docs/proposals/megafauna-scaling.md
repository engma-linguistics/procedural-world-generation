# Megafauna scaling: how big, how hungry, how many (giants and dragons)

Owner and a side session, 2026-10-28. The owner approved everything here. The tickets that carry it out are listed at the end. The numbers come from `docs/review/megafauna/scaling.py`. The papers are in `docs/references/megafauna/` (see its README).

## The equations

- **Damuth's law, in Marshall et al.'s form** (2021, Science 372:284): density = a·M^-0.75, with M in grams and density per km². log10 a depends on the metabolism class, in steps of 2.1× (checked against the paper: mesotherm log10 a = 2.99 in Table 1, slope -3/4 in Eq. 1, the 2.1× steps and the ~35× mammal herbivore step in the text, all Science p. 284; the mammal carnivore 2.67 and varanid 3.31 rows are 2.99 -/+ log10 2.1, derived, not printed; M in grams checked by 10^2.99 × (5.2e6 g)^-0.75 = 0.0090/km², the paper's median 0.0091):

  | class | log10 a |
  |---|---|
  | mammal carnivore | 2.67 |
  | Marshall's dinosaur "mesotherm" | 2.99 |
  | large varanid | 3.31 |
  | mammal herbivore (~35× mammal carnivores) | 4.21 |

  Scatter is ~240× across the 95% band (σ ≈ 0.61 in log10). (checked: Table 1, p. 284: 240× is the ratio of the 97.5% and 2.5% tails of the T. rex intercept, log10 a 1.80 to 4.18, which folds in the unknown physiology; the text, p. 284, gives 150× at ±1.96σ for flesh-eating mammals of one body mass, σ ≈ 0.55.) Apply the law to the **ecological mass**: the mean over the age structure, weighted by survivorship. Do not use the maximum size. (checked: p. 284; Marshall averages the postjuvenile cohorts only, weighted by cohort share from survivorship data.)
- **Carbone & Gittleman** (2002, Science 295:2273), Carnivora from 0.14 to 310 kg: carnivores per 10 t of prey = 89.1·M^-1.05; density per 100 km² = 197.6·M^-0.88 (M in kg). (checked: PDF p. 2, Science p. 2274; both fits N = 25, and Table 1 spans least weasel 0.14 kg to polar bear 310 kg.)
- **Field metabolic rate** (Nagy, Girard & Brown 1999), in kJ/day with M in grams:
  - mammals 4.82 M^0.734
  - birds 10.5 M^0.681
  - reptiles 0.196 M^0.889

  The reptile exponent is steeper. The reptile/mammal ratio is 0.23 at 70 kg (McNab's Komodo figure), 0.39 at 2 t and 0.55 at 20 t. At dragon size, "reptile" therefore buys only about 2× more animals than "mammal", which is roughly what Marshall's mesotherm intercept gives. **Dragons use log10 a = 2.99.**

## What was wrong before

`dnd.toml` and `megafauna.py` take the herbivore line at 20 t (0.05/km², which is correct). They then set an apex hunter "two to three orders lower", citing Carbone (mammals). Neither paper supports that. The mammal-carnivore line is only ~1.5 orders below the herbivore line, and reptile physiology then raises density again. The present 1 per 5,000 km² is the owner's pick from the PW-923 trial. It stays as the present-day value. It is explained by people pressure (below), not by the physics.

## Giants

**How the masses are built.** Height comes from the canonical D&D figures. Mass is isometric from a 1.78 m, 75 kg human, then multiplied by a build factor:

| kind | build factor |
|---|---|
| hill (portly) | 1.4 |
| stone (lean) | 0.9 |
| fire (stocky) | 1.5 |
| frost | 1.15 |
| cloud | 1.0 |
| storm | 1.1 |

The "robust" column uses mass ∝ height^3.3.

**How the food is worked out.** Food per day is Kleiber BMR × 1.7, a working human's activity level. The conversions:
- grain: 3,400 kcal/kg
- cattle: 625 Mcal edible per head
- fish: 1,200 kcal/kg

**Density baseline.** The forager-scaled column takes human foragers (~0.1/km² median) and scales them by M^-0.75.

| kind | height | iso | **recommended** | robust | kcal/day | × human | grain t/yr | cattle/yr | fish t/yr | forager-scaled | repo before lane 38 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hill | 16 ft / 4.9 m | 1.5 t | **2.2 t** | 2.9 t | 38k | 12 | 4.1 | 22 | 11.5 | 1/140 km² | 1/100 |
| stone | 18 ft / 5.5 m | 2.2 t | **2.0 t** | 2.8 t | 35k | 12 | 3.8 | 21 | 10.8 | 1/130 | (none) |
| fire | 18 ft / 5.5 m | 2.2 t | **3.3 t** | 4.6 t | 52k | 17 | 5.6 | 30 | 15.8 | 1/190 | 1/125 |
| frost | 21 ft / 6.4 m | 3.5 t | **4.0 t** | 5.9 t | 60k | 20 | 6.5 | 35 | 18.3 | 1/220 | 1/167 |
| cloud | 24 ft / 7.3 m | 5.2 t | **5.2 t** | 8.0 t | 73k | 24 | 7.8 | 43 | 22.2 | 1/270 | 1/200 |
| storm | 26 ft / 7.9 m | 6.6 t | **7.3 t** | 11 t | 94k | 31 | 10.1 | 55 | 28.6 | 1/345 | 1/200 |

- A storm giant's hip height (~4 m) equals T. rex's, and T. rex weighed ~7-9 t: think "T. rex mass on humanoid legs". A hill giant weighs about what Albertosaurus did.
- Food:
  - a hill giant eats like 12 peasants;
  - a steading of 10 taking tribute uses up a village of 100-150 people's surplus;
  - a storm giant needs about half a grey whale a year.
- Fun lane 38 (10-28) has since set every giant to `meta.giant_km2` = 5,000 km², 15-35× sparser than the forager-scaled figure. That is open for the owner as PW-963. Before lane 38, the repo's densities were 1.4-1.7× denser than the forager-scaled figure, which is well within the noise. A pure-carnivore giant on Carbone's line would be 1 per 400-1,300 km². The owner's 10-28 ruling ("giants lower, a user option") has room to go 2-3× lower and stay realistic.
- No age structure for giants (owner). Their demography is human-like.

## Dragons

### Size, wingspan and food by age

The growth model:
- growth goes on all life, reptile-style;
- body length (snout to tail) is interpolated through 0.8 m at hatching, 3 m at 5 yr, 8 m at 100, 16 m at 800, 22 m at 1,500 and 28 m at 3,000;
- mass is a Komodo build (70 kg at 2.6 m, ∝ L³), lightened ×0.6 for flight.

The wingspan columns hold the wing loading of *Quetzalcoatlus* (200-250 kg and a 10-11 m span, Witton & Habib 2010 abstract; their Table 2 uses 10.40 m at 250 kg, p. 7. Earlier text said "~10.5 m", the midpoint of 10-11 m). One scales the span ∝ M^(1/3), the other ∝ M^0.39 (the bird trend).

Food is reptile field metabolic rate. Cattle are counted as whole carcasses: 836 Mcal each, 85% of it assimilated.

| age | stage | length | mass | wingspan | kcal/day | cattle/yr |
|---|---|---|---|---|---|---|
| 5 yr | wyrmling (end) | 3.0 m | 60 kg | 6 m | 900 | 0.5 |
| 50 | young | 5.4 m | 370 kg | 12 m | 4,200 | 2 |
| 100 | young (end) | 8.0 m | 1.2 t | 18-20 m | 12,000 | 6 |
| 300 | adult | 10.3 m | 2.6 t | 23-26 m | 24,000 | 12 |
| 800 | adult (end) | 16.0 m | 9.8 t | 36-44 m | 77,000 | 40 |
| 1,200 | ancient | 19.4 m | 17.5 t | 43-55 m | 129,000 | 66 |
| 1,500 | ancient | 22.0 m | 25 t | 49-64 m | 180,000 | 92 |
| 2,000 | ancient | 24.0 m | 33 t | 54-71 m | 226,000 | 116 |
| 3,000 | ancient (oldest) | 28.0 m | 52 t | 62-85 m | 342,000 | 176 |

Real flight tops out near 250 kg (Witton & Habib 2010, abstract: 200-250 kg is the most reliable upper pterosaur estimate; the largest volant bird, *Pelagornis*, is 21.9-40.1 kg, Ksepka 2014, Fig. 2). Every adult dragon is far past that: this is "don't worry about it" physics. Ectotherm habits fit: feast and fast, one large kill every week or two.

### Age structure (the base case, owner-approved)

Annual mortality by stage:

| stage | ages | mortality per year |
|---|---|---|
| wyrmling | 0-5 | 20% |
| young | 6-100 | 1.5% |
| adult | 101-800 | 0.25% |
| ancient | 801+ | 0.4% |

The oldest age is 3,000 years.

| stage | share of individuals | share of biomass | share of food |
|---|---|---|---|
| wyrmling | 9% | 0.1% | 0.1% |
| young | 33% | 4% | 5% |
| adult | 51% | 62% | 64% |
| ancient | 7% | 34% | 31% |

- The ecological mass is 3.2 t.
- Ancients are rare in number but eat about a third of the food.
- The ancient count is very sensitive to adult mortality:
  - doubling every rate leaves 0.3% ancients;
  - halving every rate gives 26%.

  How dangerous the world is for an adult dragon is the real knob.
- **Generation time.** With breeding from age 100 and flat fecundity, it is ~430 yr. If fecundity rises with mass, it is ~700 yr. The repo uses 200 (PW-959).

### Natural density, people pressure and the age of dragons

Natural density uses Damuth at the 3.2 t ecological mass, with that food budget spread over every age:

| physiology | all dragons | ancients only |
|---|---|---|
| mesotherm (used) | 1 per 65 km² | 1 per 975 km² |
| mammal carnivore | 1 per 137 km² | 1 per 2,000 km² |

1 per 5,000 km² is 35-75× below that, outside the 95% band for any physiology. The resolution the owner accepted:
- real large carnivores in human-dominated land run at a few percent of their potential (tigers ~3-4% of their historical numbers; Ripple et al. 2014);
- so dragons sit near their natural density before peoples spread ("the age of dragons");
- they fall as peoples press them, to ~1 per 5,000 km² at the present in peopled country;
- country no people holds keeps skies closer to natural.

At 1 per 5,000 km² overall, the base case leaves about one ancient per 75,000 km² (about Scotland).

## Tickets

The tickets:

| Draft | Carries |
|---|---|
| PW-957 | the natural dragon density, suppressed by people pressure (the age of dragons) |
| PW-958 | dragon age structure, with counts reported by stage |
| PW-959 | revisit dragon generation time (~430 yr) |
| PW-960 | body size and food as data |
| PW-961 | what megafauna eat, in the culinary output |
| PW-962 | owner action: fetch the paywalled papers |
| PW-963 | giant density, reconcile (needs-decision) |

Updates were added to PW-923, PW-924, PW-936 and PW-937.
