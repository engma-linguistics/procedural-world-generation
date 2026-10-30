# Peoples' numbers from demography (lane 76, 2026-10-30)

Research only. Nothing in the code was changed. The coordinator saved this from lane 76's report.

## In plain words
- **Births and deaths decide how fast a people grows, not how many it ends up with.** Once land is full, each people's births balance its deaths. Fast-breeding, short-lived goblins are not more numerous for it. Final numbers come from density (how many people a km² of their country feeds) and from how much country they hold. That is textbook ecology, and the model works the same way.
- **Fast breeding changes four things:**
  1. how fast a people spreads, though only with the square root of its growth rate;
  2. how fast it recovers after a war, a plague or an ice age;
  3. how much steady loss (raids, dragons, disease) it can take without collapsing;
  4. how small a group can survive.
- **On canon ages:** kobolds, goblins and orcs grow about 1.5–3× as fast as humans, dwarves and gnomes about ¼ as fast, elves about ⅐.
- **Demography will not make dwarves and elves common. It makes them rarer**, because slow peoples lose races for empty land and recover slowly. That fits canon (few long-lived, slow peoples), but not "mainline peoples are common".
- **Two things can make them common without a weight:**
  1. **Density by way of life**, the biggest lever and already a number in the tree. Elves are set at 1 person per km² against humans' 10. Lane 73 measured elves leading about 2–3% of cells while being only about 0.5% of people.
  2. **Arriving in force through portals.** Most of this is already built.
- **The portal idea is cheap and sound.** Portals exist (PW-697), and an arrival already founds at every portal it can live near; the D&D preset just has `portal_mode = "off"`. Turning portals on and adding one number per arrival ("founders") gives the "million through ten portals" case for about half a day of work.

## 1. Where demography enters today
Checked on main 5b808d91, and in lane 73's worktree at commits df15c4c5 and 03087601.

- **Population.** `peoples.population` = presence × `dens_at` × area. Density is a hand-set number per people, multiplied by land productivity (PW-974).
- **No growth equation.** `spread.spread` gives a reached cell its full room at once. Spread is `speed_kmyr` passes (default 0.5 km/yr), changed only by trait multipliers.
- **Competition.** `_compete` uses niche overlap, `ALPHA_CLOSED` and the density ratio (`invasion_weights`, `DENSITY_PUSH`).
- **Rates are uniform.** `TAU_KYR`, `MVP_TAU_KYR`, `JUMP_RATE` and lane 73's `SURGE_KYR` (4 kyr) are the same for every people.
- **`generation_yr` affects viability only.** It reaches:
  - `origins.origin_mvp`, and through it the landmass draw;
  - `dispersal.line_mvp`, which sets the small-patch fade and the founding sizes in `_jump` and `_polycentric`;
  - the techtree's learners factor.

  It never touches growth, density or competition. Counting viability in generations is the right, invariant-respecting form (Ginzburg et al. 2010).
- **Hand values disagree with canon:**
  - elves derive to about 200 years, not 50;
  - hobgoblins and bugbears inherit the goblinoid stem's 15, although canon makes them human-like;
  - kobolds are set at 25 (canon derives about 18);
  - halflings are set at 25 (canon derives about 41).
- **Lane 73's mainline flag** is at 0 (not the chosen design). At 0.6 it brought dwarves only to 0.6–0.9% and elves to 0.3–0.5%.

## 2. Canon numbers (5e)
Every row was read from `https://dnd5e.wikidot.com/lineage:<name>` on 2026-10-30. Each page quotes its book's Age trait.

| People | Adulthood | Lifespan | Book |
|---|---|---|---|
| Human | late teens | < a century | PHB |
| Dwarf | as humans; "young until 50" | ~350 average | PHB |
| Elf | physically as humans; claim adulthood ~100 | up to 750 | PHB (no separate drow or sea-elf trait) |
| Halfling | 20 | mid second century | PHB |
| Gnome | ~40 | ~350, some 500 (as paraphrased by the tool) | PHB |
| Half-elf | 20 | often > 180 | PHB |
| Half-orc | 14 | rarely > 75 | PHB |
| Dragonborn | 15 | ~80 | PHB |
| Tiefling | as humans | "a few years longer" | PHB |
| Orc | 12 (Wildemount 16) | 50 (Wildemount 80) | VGtM |
| Kobold | 6 | "up to 120 but rarely do so" | VGtM |
| Goblin | 8 | 60 | VGtM |
| Hobgoblin | as humans | as humans | VGtM |
| Bugbear | 16 | 80 | VGtM |
| Kenku | 12 | 60 | VGtM |
| Aarakocra | 3 | ~30 | EEPC |
| Tortle | 15 | average 50 | Tortle Package |
| Lizardfolk | 14 | rarely > 60 | VGtM |
| Firbolg | 30 | 500 | VGtM |
| Triton | 15 | 200 | VGtM |
| Leonin | as humans | as humans | MOoT |
| Tabaxi | — | as humans | VGtM |
| Goliath | late teens | < a century | EEPC |

- **Fertility:** canon gives none for any people. A D&D Beyond snippet says *Volo's* has kobolds laying "up to six eggs a year", but that page could not be opened, so the figure is unverified.
- **Giants and dragons:** only secondhand figures were found; the Forgotten Realms Wiki returned HTTP 402.
- **Body weight:** only the kobold's was read (25–35 lb).

## 3. Rates
Real-world anchors (all read):
- **Foragers:** first birth at 19.5 yr, 3.69 yr between births (Robson & Wood 2008, *J Anat* 212:394, Table 2, PMC2409099).
- **Survival:** 57% survive to 15, and 64% of 15-year-olds reach 45, an adult mortality of about 1.5%/yr (Gurven & Kaplan 2007, *PDR* 33:321, p. 326).
- **Fertility (TFR):** foragers 5.6, horticulturalists 5.4, farmers 6.6; only farmers differ significantly (Bentley, Jasieńska & Goldberg 1993, *Curr Anthropol* 34:778, Table 1).
- **Maximum growth:** Rmax per generation does not depend on body size in mammals, at about 3.5; birds about 7.8 (Ginzburg, Burger & Damuth 2010, *Biol Lett* 6:850). So r_max ≈ ln(Rmax) / T.
- **Sustainable loss:** the share of a population that can be removed each year falls exponentially with age at first breeding (Hone, Duncan & Forsyth 2010, *J Appl Ecol*; abstract only).
- **Spread speed:** the Fisher–KPP front moves at U = 2√(νγ), independent of carrying capacity, with γ ≈ 0.02/yr typical and the Neolithic front at about 1 km/yr (Baggaley et al. 2012, arXiv:1203.4471).

**Method** (script: scratchpad l76/demog.py):
- Survival to adulthood is human, except for the harsh peoples.
- Adult mortality is the human hazard, stretched to the canon lifespan, and the fertile window is stretched the same way.
- T is the mean age of mothers.
- r_max = ln(Rmax) / T, with Rmax 3.5, or 7 for a "brood" class.

| People | T, yr (toml value) | r_max %/yr | × human | spread ×√ |
|---|---|---|---|---|
| Human-likes | 29 (25; hobgoblin 15) | 4.3 | 1.0 | 1.0 |
| Dragonborn / bugbear / half-orc / lizardfolk | 21–26 | 4.9–5.9 | 1.1–1.4 | 1.1–1.2 |
| Orc | 18 (25) | 6.9 (Rmax 7: 10.8) | 1.6 (2.5) | 1.3 (1.6) |
| Kobold, harsh (+5%/yr adult deaths, 25% reach adulthood) | 18 (25) | 6.8 (10.5) | 1.6 (2.4) | 1.3 (1.6) |
| Goblin, harsh | 15 (15) | 8.1 (12.5) | 1.9 (2.9) | 1.4 (1.7) |
| Aarakocra | 7 (25) | 17 | 4.0 | 2.0 |
| Halfling | 41; fertile 20–45: 32 (25) | 3.1 (3.9) | 0.71 (0.91) | 0.84 |
| Half-elf, triton | 43–44 | 2.9 | 0.66 | 0.81 |
| Dwarf | 114; fertile 50–100: 75 (40) | 1.1 (1.7) | 0.26 (0.39) | 0.51 |
| Gnome | 109; fertile 40–90: 65 (40) | 1.15 (1.9) | 0.27 (0.45) | 0.52 |
| Elf | 204; fertile 100–200: 149; breeding from physical maturity 20–120: 69 (50) | 0.61 / 0.84 / 1.8 | 0.14 / 0.20 / 0.42 | 0.38–0.65 |

- **Implied fertility.** If dwarves are to persist rather than explode, a dwarf woman bears about 6.6 children at about 24-year intervals; an elf, at about 39-year intervals. This is the fertility canon leaves out.
- **Steady losses.** At an extra 0.5%/yr of raiding or predation, an equilibrium people keeps N*/K = 1 − h/r of its numbers:
  - humans about 43%;
  - kobolds and goblins 65–70%;
  - dwarves, gnomes and elves 0.

  Slow peoples persist only where little kills them. This is the real-ecology form of "breed fast, survive worse".

## 4. What r does to shares
- **Final state.** In the Lotka-Volterra competition the model approximates, who excludes whom depends on K and the competition coefficients, not on r.
- **Timing.** Lane 73 found strong priority effects in the model, so timing matters. Fast breeders win the races for newly free land and the long contests; slow ones lose.
- **Continental spread** barely changes: elves, at 0.38 × 0.5 km/yr, still cross about 4,700 km in their 25 kyr. The effect bites in contests lasting centuries to millennia.
- **Net effect:** elves and dwarves end rarer; kobolds, goblins and orcs end commoner.
- **What makes slow peoples common**, most physical first:
  1. **Density (K)**, from way of life plus body size. Damuth's rule (density ∝ mass^-0.75) is already used for the giants via `FORAGER_KM2`. A kobold eats about ⅓ of what a human does.
  2. **Competitive ability in full land.** It is r/K-defensible, but it amounts to the mainline flag.
  3. **Arriving big and in many places.**
  4. **Low losses.**

## 5. Options (least forced first) and recommendation
- **A. Life history in the spec.** New fields `adult_yr`, `lifespan_yr`, `breeding` (slow / mammal / brood, i.e. Rmax 2 / 3.5 / 7) and an optional `fertile_yr`. `generation_yr` and r are derived from them. Effort: s–m.
- **B. r drives the uniform rates.** Effort: m.
  - `speed_kmyr` × √(r / r_human);
  - `TAU_KYR` scaled by the r of the people taking the land;
  - `MVP_TAU_KYR` and refuge recovery scaled by r;
  - `JUMP_RATE` × r / r_human;
  - keep `SURGE_KYR` in years; counted in generations, elves would get an edge of about 28 kyr.
- **C. A steady-loss term, N* = K(1 − h/r).** Counter-pressures (PW-917). Effort: l, later.
- **D. Density by way of life.** Elves as forest horticulturalists at 3–5/km², about three times their share; dwarves as mountain farmer-miners at 6–8/km². Effort: xs. Owner call.
- **E. Portal wave** (section 6). Effort: s–m.
- **F. Mainline flag.** Keep it at 0 unless D and E fall short.

**Recommendation:** A, then B, then E, with D as an owner call. Tell the owner plainly that A and B make elves and dwarves rarer, not commoner. If they should be common, D (plus E for elves and gnomes) is the honest lever, because it changes an ecological number rather than adding a weight.

**A sensible rethink of canon:**
- Keep the canon ages.
- Give long-lived peoples a fertile window much shorter than life, with children at long intervals: dwarves 50–100, gnomes 40–90, elves 100–200.
- Put kobolds and goblins in the brood class, with the harsh survival that "rarely do so" implies.
- Give halflings a human-like fertile window (20–45), which makes them nearly human-fast and fits their homely numerousness.

## 6. Portal arrival, costed
**Already exists:**
- `meta.portal_mode` (off | random | sites) and `meta.portals`, with portals at least 1,800 km apart.
- `_origin_new` seeds a new people at every portal it can live within 700 km of (else 2,500 km).
- At L7 (cells of about 3,100 km²), lane 73's main seed holds FOUNDER_KM 400 km, about 169 cells or 0.5 Mkm². That is about 0.3 M elves at density 1, or about 4 M gnomes.
- Each extra portal seeds 3 rings (about 37 cells, about 70 k elves).

So arrivals are not a "tiny group" in number. Their weakness is landing at one point in a full world.

**Needed:**
1. In dnd.toml, `portal_mode = "sites"` and `portals` set to about 6–10.
2. A per-arrival `founders` total, split across the portals. Each seed grows ring by ring over free room (lane 73's siting, inside each disc) until it carries its share, as `_jump` does for the viable number.
3. Optionally, a per-arrival portal count.

**Soundness:** yes. This is polycentric founding from outside the world. It needs one owner number per arrival, whose default reproduces today's founding size.

**With lane 73's momentum edge:** `surge` is a ratio of a people's mass to its lagged mass, so a big wave keeps the edge as long as a small one does (about 3 kyr to half). The two combine without change.

## 7. Not checked
- The Forgotten Realms Wiki (HTTP 402).
- Giant and dragon lifespans (secondhand only).
- Canon body weights other than the kobold's.
- Kobold egg counts.
- Charnov's numeric invariant.
- The equation in Hone et al. 2010 (abstract only).
- Kelly's *Lifeways*.
- No model runs: the effects above are reasoned from the code, not measured.
