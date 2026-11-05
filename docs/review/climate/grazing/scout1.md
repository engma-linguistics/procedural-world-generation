# Grazing herds after the grass-roots fix: scout 202, pass 1 (diagnosis gate), 2026-11-05

**In plain words.** When lane 185 (PW-1261) made grass roots pay their upkeep, grass on Earth's real climate came
down to what field plots measure, and the model's wild herds fell with it: in the 550-700 mm rain band of warm
African grassland from 4.10 to 3.07 tonnes of grazers per km2 (baseline: the code before PW-1261, same world, same
observed climate). The six African parks Coe et al. counted in that band hold 3.8-4.4. So the model now sits about
three quarters of the park figure. That is still inside the spread of the real data: the parks scatter by a factor
of about 1.4-1.5 around their own rainfall line, and 3.07 is 1.1-1.4 of those spreads below it. And the parks are
the rich-soil end of Africa: at the same rain, poor soils carry far fewer grazers (Fritz & Duncan 1994 put it at
about 20 times). A model that knows only rain should land below the rich-soil parks, not on them.
**Recommendation: no change.** The drop is the right consequence of the grass being fixed; it does not need undoing.

Baselines throughout: "before" is main before the PW-1261 merge (lane 181's KN code), "after" is current main
(lane 185's C1), both on Earth L6 world 506694 with the observed climate, numbers from
`docs/review/climate/npp/round3.md` section 1 (lane 185's `npp_check.py` run). Statistics in this folder's
`coe_stats.py` (run: `uv run python docs/review/climate/grazing/coe_stats.py`). No model runs in this pass.

## 1. Where herd biomass comes from in the model
- `planet/gameattrs.py` (grazing block, ~line 169): grazing NPP = (herb NPP + 0.3 x shrub NPP as browse) x
  (0.4 + 0.6 x open months / 12). Tree NPP feeds no herds at all (the "forests hold no game" half of PW-836).
- `planet/lineages/prey.py::wild`: that NPP, cut to its above-ground share by Gherardi & Sala 2020
  (`above`: 0.44 at 626 mm), converted to kJ (C_FRAC 0.45, 17.5 kJ/g dry), then McNaughton et al. 1989's
  cross-ecosystem fit, log10 B = 1.52 log10 NAP - 4.79 (PDF p. 142-143, on file), and back to live weight
  (7 kJ/g, Farlow 1993). Overkill, refuges and livestock then act on this `wild` field (`prey.field`).
- So the herds are a power law of the herb layer's above-ground NPP, with exponent 1.52.

## 2. Why the grass fix lowered the herds
Nothing in the herd code changed. Lane 185's herb above-ground NPP in the 550-700 mm band went 711 -> 588 g
dry/m2/yr (x 0.827; round3.md). Through the 1.52 exponent: 0.827^1.52 = 0.75, and 4.10 x 0.75 = 3.07, exactly the
reported figure. The same holds in every band (1.28 -> 0.96, 2.57 -> 1.89, 5.44 -> 4.10: all x 0.74-0.75).

The old 4.10 matched the parks only because the grass was over-growing: 711 g against Deshmukh 1984's 512 and
Yang et al. 2020's 397 at 626 mm (round3.md). Now the grass is at 1.15x Deshmukh and 1.5x Yang, and the herds are at
what McNaughton's fit gives for that grass. The "gap" is not a bug in the grass fix; it is where the herd fit's
cross-ecosystem line meets field-true African grass.

Why Coe's own fit would say more: Coe et al. regress herds on above-ground production *predicted* from rain by
Rosenzweig 1968 (p. 345, AE = rain under 700 mm), which at 626 mm is 960 g dry/m2/yr (`coe_stats.py`), 1.9x
Deshmukh's measured peak biomass and 2.4x Yang's. Their fit's intercept is calibrated to that inflated production,
so it cannot be fed field-true grass production (the model's) and be expected to give their parks. McNaughton
et al. note the same direction in their data: on consumption against production, "forests fell below the line and
grasslands above" (p. 143), and the upper end is "heavily influenced ... by a prevalence of data from African game
parks, known to support among the highest levels of herbivory yet quantified" (p. 143).

## 3. What the model should be judged against
**The 4.0-4.4 figure, verified.** Coe, Cumming & Phillipson 1976 (Oecologia 22:341, on file, Table 1, pp. 344-345):
Tsavo East north of the Voi 4,033 kg/km2 and south of it 4,388, both at 553 mm. Correct as quoted, but the band
holds six wildlife areas, not two:

| area (Coe Table 1) | rain, mm | biomass, t/km2 |
|---|---|---|
| Tsavo E, N of Voi | 553 | 4.03 |
| Tsavo E, S of Voi | 553 | 4.39 |
| Sengwa, Rhodesia | 597 | 4.32 |
| Ruaha, Tanzania | 625 | 3.91 |
| Kruger, southern | 650 | 3.78 |
| Mfolosi, S. Africa | 650 | 4.39 |
| (neighbours: Willem Pretorius 520 mm 3.34; pastoral Samburu district 500 mm 6.51, Kaputei 710 mm 7.88) | | |

**The scatter.** Re-fitting Coe's Table 1 in log-log (my fit; the paper's Fig. 2a gives slope 1.552, intercept
-0.52 for the 30 areas; mine gives 1.559, -0.642: the slope reproduces, the intercept does not quite, so I use my
fits only for their scatter):

| fit | n | residual sd | fit at 626 mm | before (4.10): z | after (3.07): z |
|---|---|---|---|---|---|
| all 30 areas | 30 | 0.181 dex (x1.52) | 5.23 | -0.58 | -1.28 |
| wildlife areas | 24 | 0.174 dex (x1.49) | 4.82 | -0.41 | -1.13 |
| wildlife, rain < 700 mm | 13 | 0.151 dex (x1.42) | 4.57 | -0.31 | -1.14 |
| linear, wildlife < 700 mm (the paper's p. 348 form) | 13 | 858 kg/km2 | 4.25 | | -1.37 |

Across all four bands (all-30 fit, before / after): 328 mm -0.96 / -1.65, 468 mm -0.62 / -1.35, 626 mm -0.58 /
-1.28, 804 mm -0.84 / -1.52. So: after PW-1261 the model sits a steady 0.5-0.66x (-0.18 to -0.30 dex) below the fitted lines
in every band (0.74x of the six parks' mean in the 550-700 band), 1.0-1.65 residual sd low; inside a 2-sd envelope everywhere, but below all six parks in the
550-700 band.

**Why the parks are a ceiling, not a centre.**
- Coe et al. took their censuses "primarily from the east African plains and lightly wooded savannas where large
  mammals are more easily counted than in the more extensive savanna woodlands of west central and southern
  Africa" (p. 342): protected, open, well-counted country.
- East 1984 (Afr J Ecol 22:245, doi:10.1111/j.1365-2028.1984.tb00700.x; abstract read via OpenAlex 2026-11-05)
  places Coe's rainfall correlation in "arid/eutrophic savannas", and finds that on "soils of low nutrient status"
  the main herbivore biomass "tends to decline at higher levels of rainfall", with moist/dystrophic savanna
  species' biomasses "usually low".
- Fritz & Duncan 1994 (Proc R Soc B 256:77-82, doi:10.1098/rspb.1994.0052; abstract read via OpenAlex 2026-11-05):
  rainfall dominates, but "for a given level of rainfall, on rich soils (high nutrient availability) the biomass of
  large ungulates is about 20 times as great as on poor soils"; rain plus soil class explains 87% of the variance.
  The full paper (its fitted coefficients) is paywalled; not read.
- The model's 550-700 mm African cells (lane 185's mask: lon -20..52, lat -35..20, T > 18 C, potveg savanna/grass
  groups) include dystrophic woodland as well as eutrophic plains, and the model has no soil-nutrient term in the
  herds. Its band median should therefore sit below a sample of eutrophic parks. 0.74x of them is a plausible place.

Not used: Hempson, Archibald & Bond 2015 (Science 350:1056) mapped herbivore biomass across sub-Saharan Africa
~1000 years ago, which would be the right all-soils yardstick, but its abstract gives no numbers and the paper was not
read. If a later pass needs a continental yardstick, that is the paper to get.

## 4. Candidate fixes (none recommended now)
- **A. No change (recommended).** 3.07 is within the observed scatter for its rain (z -1.1 to -1.4), and the
  observed sample is the rich-soil end. Earth is a plausibility anchor; stop once in range. Effect: none. The
  steady offset should be recorded on PW-1261 as "in range, accepted", so the next reader does not chase it.
- **B. A soil-nutrient factor on the herds** (East 1984; Fritz & Duncan 1994): scale `prey.wild` by the world's
  `soil_fertility` layer (humanuse already reads it), up on eutrophic ground, down on leached ground. This is the
  sourced form of PW-836's "forage quality" and the most physical of the three. Expected effect: eutrophic
  semi-arid plains up (towards Coe's parks), wet dystrophic woodland down; the band median could go either way.
  Needs Fritz & Duncan's coefficients (paper not read) and a check that the model's soil fertility separates
  Bell's eutrophic and dystrophic savannas. Not a pass-1 job, and it widens the herds' spread rather than shifting
  the centre. Fits PW-836's scope; no new ticket.
- **C. A grassland offset on McNaughton's line** (his p. 143: grasslands sit above the pooled fit), e.g. refit
  the intercept on Coe's parks with field-true grass production. Expected: about +0.13 dex (the parks' mean 4.14 over 3.07), herds back to ~4.1 at 626 mm.
  Rejected: it is an Africa-park fit dressed as a grassland term (PW-1261's own option C, "not general"), it
  re-tunes to the eutrophic ceiling, and it would undo by hand what the grass fix correctly did.
- (Browse from tree foliage, PW-836's "forests hold no game": McNaughton's foliage fit, log C = 2.04 log NFP - 4.80,
  p. 143, brings forests into line. It would add herds in wooded savanna and forest, a structural change for
  PW-836 or PW-207, not a fix for this band.)

## 5. Verdict
No experiment run: no candidate is both clearly sound and needed. Recommendation: **no change**; close the
"herds 0.75x Coe" open item on PW-1261 as in range; keep B as the sourced scope for PW-836 when that ticket's
turn comes.
