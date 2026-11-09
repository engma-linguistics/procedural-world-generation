# PW-1518: diffuse light and the rainforest's leaf upkeep (scout 232)

**In plain words.** A leaf in full sun gets more light than it can use, so in a forest under a clear sky the top leaves
waste light and the inner leaves sit in shade. Under cloud the light comes from the whole sky, reaches the inner leaves,
and the forest fixes more carbon for each unit of light it catches. Our plants fix the same carbon per unit of light
whatever the sky, so the cloudy rainforest is short of photosynthesis. That shortfall is why its leaves' upkeep could
not be raised to the measured rate: dearer leaves without the extra light-use make the model keep fewer leaves and grow
less. This page says what is missing, lists the candidate mechanisms with the papers read for each, and the screens
come in [screens.md](screens.md).

## 1. What the model does today

- Light at the ground (`climate.months`, `_par`): PAR = 0.48 x top-of-atmosphere x (0.25 + 0.5 x sunshine share), the
  sunshine share from the light's cloud (`shade_jul`/`shade_jan`). So the sky's clearness index runs 0.725 (clear) to
  0.25 (overcast). There is no direct/diffuse split.
- Photosynthesis (`vegetation._year`): GPP per month = eps x FPAR x PAR x temperature and water factors, a big-leaf
  light-use efficiency (LUE) model, linear in PAR at any light level. eps is per PFT, scaled by EPS_SCALE 0.8 (fitted
  on Earth's land NPP). TrBE's eps 1.43 (1.14 g C/MJ) is scout 210's pick of the **dry-season** K67 value, the low end,
  because no diffuse gain is modelled.
- The leaf area (LAI) is the one that maximises the stand's net NPP (golden search, `_potential`): a leaf is kept when
  its extra GPP pays its respiration and turnover. A gain that scales all of GPP pays more for every leaf; a gain that
  goes to the shaded (deep) leaves pays most for the deep leaves, so it raises the optimal LAI more.

## 2. What the measurements say (sources fetched and read this session)

- **Yan et al. 2017**, JGR Biogeosci 122:3014, doi:10.1002/2017JG004008 (White Rose eprint 124617, full text read).
  - Monthly canopy LUE (GPP / (PAR x FPAR)) correlates linearly with the diffuse fraction Df at all four Amazon forest
    towers, R2 0.72-0.86 (section 4.2, Figure 2). At K67 Df runs 0.55 (dry season) to 0.9 (wet), LUE 1.1 to 1.9
    g C/MJ; with total light falling, GPP still rises ~34% dry to wet.
  - Df from the sky clearness index SI = Q/Q0 (eq. 13, He et al. 2013's fit):
    Df = 0.7527 + 3.8453 SI - 16.316 SI^2 + 18.962 SI^3 - 7.0802 SI^4, checked against measured monthly Df at three
    Amazon sites (R2 0.76-0.96, RMSE 0.06-0.07).
  - Two-leaf model (eq. 5-11): GPP = eps_sun APAR_sun + eps_shd (0.25 + 0.75 Df^1.8) APAR_shd, eps_sun 1.11,
    eps_shd 4.35 g C/MJ (calibrated at K67); sunlit LAI = 2 cos(theta) (1 - exp(-0.5 Omega LAI / cos(theta))),
    clumping Omega 0.8 for evergreen broadleaf, theta the monthly noon zenith angle.
  - Sensitivity: Df x1.1 gives GPP +14%, x0.9 gives -12% at K67 (section 4.5).
  - At pasture and savanna sites LUE relates to Df weakly (R2 0.25-0.42): water sets their seasons.
- **Mercado et al. 2009**, Nature 458:1014, doi:10.1038/nature07949 (NORA 6771 accepted version, full text read).
  - The mechanism: sunlit leaves are often light-saturated, so have low LUE; shade leaves are efficient but under-lit;
    diffuse light spreads the load. "Canopy photosynthesis tends to be significantly more light-use efficient under
    diffuse rather than direct sunlight."
  - The net effect of more cloud is a balance: less total PAR against more diffuse share. In JULES (multilayer,
    sunlit/shaded per layer) a temperate broadleaf forest's GPP peaks at Df ~0.4 and falls beyond as total light falls.
  - Global: diffuse-fraction changes raised the 1960-1999 land sink by ~24%.

What the papers do **not** settle: Yan's K67 LUE seasonality (x1.73 over Df 0.55 to 0.9) also carries the wet
season's new leaves (they cite Wu et al. 2016 on leaf age and leave it open), so the full slope is an upper bound for
the light effect alone. Mercado's GPP optimum near Df 0.4 says that, in a temperate forest, a cloudier month should not
out-grow a clear one: the gain must stay smaller than the light loss there.

## 3. Candidate mechanisms

| | mechanism | sources | what it should do here | risks |
|---|---|---|---|---|
| A | **Df-linear big-leaf LUE**: eps x (1 + k (Df - Df0)) above Df0, today's eps below (the clear-sky floor); Df from the model's own clearness via eq. 13; k from Yan's K67 span, Df0 = the Df the PFT's eps is for (TrBE: K67 dry season 0.55) | Yan 2017 Fig. 2 and eq. 13; Mercado 2009 (mechanism) | wet tropics GPP up by the cloud the model already has; NPP restored with rl x1.5; LAI rises a little (every leaf earns more) | slope partly leaf age (upper bound); must not make cloud beat sun in temperate forests (Mercado's optimum) |
| B | **Two-leaf sunlit/shaded LUE** (Yan eq. 5-11, normalised so that TrBE's canopy LUE at Df0 and LAI ~4.6 is today's eps) | Yan 2017 eq. 5-11; Mercado 2009 (JULES sunlit/shaded) | the gain goes to deep leaves, so the optimal LAI rises toward the measured 4.7-5.1 | more code in the hottest kernel (noon zenith per month); its calibration (eps_shd/eps_sun ~4) is one site's |
| C | **Change nothing, close as in range** (scout 217's option 4) | Malhi et al. 2009 (NPP/GPP 0.32-0.49), as scout 217 read it | none | leaves the leaf upkeep ~20-40% low and the cloudy-world bias |

The order: A first (one multiplicative term, cheap to screen, tells whether the model's own Df in the wet tropics gives a
gain of the needed size), then B only if A leaves the LAI short of the bar.

## 4. Bar (the ticket's)

Without the floor (i.e. with the diffuse gain carrying the wet season instead of taking the dry-season eps as the whole
story) and with TrBE rl x1.5 (Chambers et al. 2004's in-situ leaf rate): the TrBE stand's leaf respiration in Chambers'
710-980 g C/m2/yr, stand NPP in 900-1440, NPP/GPP in 0.32-0.49, wet-tropics box NPP near 1011-1160, LAI toward
4.7-5.1; the other boxes (seasonal tropics, temperate, boreal, land total) not worse against MOD17 than main.
