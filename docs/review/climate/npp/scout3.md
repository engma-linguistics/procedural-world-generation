# Scout 217: the rainforest's upkeep (PW-1517) and the late warm shift (PW-1516), pass 1 of 3

**In plain words.** The ticket suspected that the rainforest tree spends too little on the upkeep of its wood and roots.
It does not. I read the one field study that measures every part of an Amazon forest's breathing separately (Chambers
et al. 2004, near Manaus). The model's wood and roots breathe out about as much as the measured trunks and roots there
(about 990 against 970 g C/m2/yr). What breathes too little is the leaves: about 575 against a measured 700-980. Raising
the wood's rate would overshoot the measured trunks and roots by about 30% and cut rainforest growth by a sixth, so
that is the wrong fix.

Raising the leaves' rate is the sourced direction, but it cannot be done alone. The model picks the number of leaf
layers that pays best. Dearer leaves make it keep fewer layers (LAI 4.6 falls to 4.1 or 3.7, where Amazon plots measure
4.7-5.1), so it fixes less carbon and grows less. To keep growth where it is, photosynthesis has to rise by 6-12%. The
measured cause of that extra photosynthesis is diffuse light. Under cloud, light comes from the whole sky and reaches
the shaded inner leaves, and Amazon towers fix 1.1 g C per MJ of absorbed light in the sunny dry season against 1.9
under the wet season's cloud (Yan et al. 2017). The model has no such effect. So the fix is one change in two parts:
a diffuse-light gain, which is a new mechanism, together with a measured leaf upkeep rate. Raising the efficiency
number instead would be a stand-in.

The headline number itself is less wrong than the ticket says. The model's rainforest turns 44.5% of the carbon it
fixes into growth (NPP/GPP 0.445). The three Amazon sites measured with the same method give 0.32, 0.34 and 0.49
(Malhi et al. 2009). The ~0.30 is the poor-soil old forest end of that range, and the authors say it is probably
underestimated. So the model sits inside the measured range, at its high end.

PW-1516 (the planets 0.8 C warmer late): I followed every road from the plants to CO2 in the code. All of them pass
through the weathering terms that scout 210b logged, and none of those moved. The one input that did move, the
volcanic outgassing (+2.8%, interval touching zero), cannot be reached by the plants except through the runs drifting
apart by chance. My verdict is chaos. 210b's runs are deleted, so the one check that would settle it, the
correlation of each pair's CO2 change with its outgassing change, is now built into `scout2b_mech.py` for the next
paired judge.

No coupled screen was run (reasons in section 5).

**Baselines.** "Main" is cb8374b0 / ca03c9e6: KN_RESP 0.15, TrBE eps 1.43, physics identical. Earth numbers are the
Earth L6 terrain (world 506694) on observed climate with soils on, the same setup as `npp_check.py` (scout 210's
screens). They come from `docs/review/climate/npp/scout3_probe.py` on the TrBE stand alone ("stand", where it is viable,
T > 22 C, P > 2000 mm, 674 cells, PAR 2992 MJ/m2/yr). The npp_check boxes are mixed cells. Measured numbers are named
by site. "Today's Earth" means the measured Amazon forests, as a plausibility check, not a target.

## 1. The measured carbon budget of an Amazon forest (read this session)

| source (read) | site | GPP | NPP | Ra leaf | Ra wood (stems) | Ra roots | Ra total | NPP/GPP |
|---|---|---|---|---|---|---|---|---|
| Chambers et al. 2004, Ecol Appl 14:S72, Table 2 (full text, eScholarship) | Manaus (ZF2), LAI 4.7 | ~3000 ("~30 Mg C/ha/yr", Reco taken as GPP) | 900 | **980** | **420** | **550** | 2100 (incl. understory 150) | 0.30 (above-ground; wood 0.43, leaf 0.25) |
| Malhi et al. 2009, GCB 15:1255 (abstract, via IPAM / search) | Manaus / Tapajos / Caxiuana | | 1010 / 1440 / 1000 | largest, most uncertain part | | | 1490-2140 | **0.34 / 0.49 / 0.32** |
| Malhi, Doughty & Galbraith 2011, Phil Trans B 366:3225 (PMC3179639) | Amazon review | ~3000 | NPP canopy 332, wood 380, fine root 272 (35-site mean) | | | | ~70% of GPP | "approximately 30 per cent", "likely to be underestimated ... missing components of NPP" |
| Atkin et al. 2015, New Phytol 206:614 (full text, USDA Treesearch copy) | 100 sites, 899 species | | | broadleaf tree outer-canopy Rdark at 25 C: 1.0 umol/m2/s at TWQ 20 C, **0.82 at TWQ 25 C** (Discussion, Table 6) | | | | |
| Yan et al. 2017, JGR Biogeosci 122:3014 (full text, White Rose eprint 124617) | K67 Tapajos | | | | | | | LUE 1.1 (Df 0.55, dry) to 1.9 g C/MJ (Df 0.9, wet); two-leaf sunlit 1.11 / shaded 4.35 g C/MJ, shaded scaled by (0.25 + 0.75 Df^1.8) |

Units: g C/m2/yr (Mg C/ha/yr x 100). Chambers' components include growth respiration (they are measured CO2 effluxes).
Chambers' wood respiration per stem area: 0.6 umol/m2 stem/s, stem area index 1.7, "no relationship between Rw and stem
surface temperature". Leaf: 0.54 umol/m2 leaf/s averaged over 24 h on 20 canopy trees (daytime rates reduced 40%),
scaled by LAI 4.7 with no canopy depth profile. Not read: Malhi 2009's component table and Malhi 2015 (Wiley, 403),
Mercado et al. 2009 (Nature, login).

## 2. The model against it

TrBE stand, main (`scout3/main.txt`). The model's growth respiration is 25% of (GPP - maintenance) and has no tissue.
To compare it with the measured per-tissue effluxes I split it by Malhi 2011's mean NPP allocation (canopy 34%, wood +
fine root 66%).

| | model (main) | measured | ratio |
|---|---|---|---|
| GPP | 2827 | ~3000 (Manaus), 3144 (Tapajos tower, via scout 210) | 0.90-0.94 |
| NPP (stand) | 1259 | 900-1440 (Chambers, Malhi 2009) | in range |
| **wood + roots: rw maintenance 716 + 66% of growth** | **~993** | **970** (Chambers stems 420 + roots 550) | **1.02** |
| **leaves: rl maintenance 432 + 34% of growth** | **~575** | **980** as published (no depth profile); **~710** with the model's own KN 0.15 profile on Chambers' rate | **0.59-0.81** |
| Ra total | 1568 | 2100 (Chambers, incl. understory), 1490-2140 (Malhi 2009) | low end of range |
| NPP/GPP | 0.445 | 0.30 / 0.32 / 0.34 / 0.49 | inside, high end |
| LAI | 4.58 | 4.7 (Manaus, trees > 10 cm), 5.1 +- 0.5 (Tapajos) | slightly low |

The top-leaf rate: rl 7.4 g C/m2 leaf/month at 20 C with Q10 2 is **0.33 umol/m2/s at 25 C** (acclimation shift
-0.2 C here, negligible). Measured: Chambers' 24-hour canopy-leaf mean **0.54**, which is x1.6 the model. Atkin's
outer-canopy dark rate at 25 C is **0.82** (TWQ 25 C), which is x2.5 the model. With leaf respiration inhibited about
30% in daylight (JULES's value, Clark et al. 2011, read by scout 210) over half the day, that is about 0.70, or x2.1.
So the leaf rate is low by x1.6 (the Amazon in-situ measurement) to x2.1 (the global outer-canopy trait database).
Chambers' number is the one measured in place in an Amazon canopy, so it is the one to take.

**Which term is off:** the leaf term (rl), by about x1.5-1.6 on the in-situ source. The wood-and-root term rw is
right to within a few percent of Chambers' trunks plus roots. `TrBR`, the temperate and boreal trees share LPJ's rl
values (6-7.4), so they are probably low against Atkin too. That is out of this ticket's scope, and noted as an
observation only.

## 3. Earth screens (TrBE stand and npp_check boxes, g C/m2/yr)

`scout3/run.sh`, one probe per variant (`scout3/*.txt`). The "x eps" columns change TrBE's efficiency only. They stand
in for the GPP a diffuse-light gain would add, and are not candidates themselves.

| | main | **rw x1.5** (the ticket's suspect) | rl x1.5 | rl x2.0 | rl x1.5 + eps x1.076 | rl x2.0 + eps x1.153 |
|---|---|---|---|---|---|---|
| LAI | 4.58 | 4.59 | **4.11** | **3.73** | 4.25 | 3.98 |
| GPP | 2827 | 2830 | 2772 | 2712 | 3002 | 3175 |
| NPP (stand) | 1259 | 1025 | 1109 | 970 | 1263 | 1276 |
| NPP/GPP | 0.445 | 0.362 | 0.400 | 0.357 | 0.421 | 0.402 |
| wood + roots respiration (with 66% of growth) | ~993 | **~1269** (Chambers 970: +31%) | ~947 | ~908 | ~987 | ~984 |
| leaves (with 34% of growth) | ~575 | ~536 | ~716 | ~835 | ~752 | ~915 |
| wet tropics box T18-32 P2500+ (MOD17 1011, field ~1160) | 1012 | 854 | 910 | 819 | 1015 | 1023 |
| T18-32 P1500-2500 (MOD17 920) | 905 | 787 | 834 | 772 | 910 | 919 |
| land NPP, Pg C/yr (MOD17 ~56) | 61.9 | 59.4 | 60.4 | 59.0 | 62.0 | 62.2 |
| forest, Mkm2 | 44.6 | 44.2 | 44.4 | 44.2 | 44.5 | 44.6 |

Reading it:
- **rw x1.5 is the wrong fix.** It reaches the ~0.36 NPP/GPP the ticket wanted, but it does so by making trunks and
  roots breathe 31% more than measured. Rainforest growth then falls to 854 in the wet tropics, 16% under the
  satellite figure.
- **rl alone costs leaves.** The LAI rule (`_year`: LAI maximises NPP net of leaf turnover) answers dearer leaves with
  fewer of them: 4.58 falls to 4.11 (x1.5) or 3.73 (x2.0), against the measured 4.7-5.1. GPP falls with it, and wet
  tropics NPP drops 10-19%.
- **To keep NPP, GPP must rise by 6% (rl x1.5) or 12% (rl x2.0) on main.** That means a canopy light-use efficiency of
  1.23 or 1.31 g C/MJ against today's 1.14. The resulting GPP of 3002 or 3175 sits around the Tapajos tower's 3144.
  On K67's range (1.1 at Df 0.55 up to 1.9 at Df 0.9; a straight line between Yan's two quoted ends, not their fitted
  slope), those efficiencies correspond to a diffuse share of about 0.61 or 0.64. Both are well inside the measured
  dry-to-wet span, so the needed lift is physically ordinary.
- **Even then NPP/GPP only reaches 0.40-0.42.** Getting to 0.30-0.34 at today's NPP would need GPP of about 3700-4200,
  beyond any tower. The model's 0.445 is a reasonable reading of the measured 0.32-0.49. Chasing 0.30 would be fitting
  to the poor-soil end of the range.

## 4. What would fix it (ranked)

1. **Recommended (next pass, if wanted): a diffuse-light gain, then TrBE rl x1.5.**
   - The model has monthly cloud (`climate.shade_from_hours` gives the shade the PAR already uses). Derive a diffuse
     fraction from it, as Yan et al. did from the sky clearness index.
   - Let the shaded part of the canopy use light more efficiently. Yan's two-leaf form: sunlit 1.11, shaded
     4.35 x (0.25 + 0.75 Df^1.8) g C/MJ. A simpler Df-linear canopy LUE pinned so that the dry-season floor stays at
     today's 1.14 would also do.
   - A two-leaf form also raises the value of deep, shaded leaves, so the optimal LAI should rise. That answers the LAI
     loss that rl x1.5 causes, where an efficiency scale-up does not.
   - Then rl x1.5 for TrBE, from Chambers' in-situ rate.
   - Order: Earth screens (npp_check, the wet-tropics boxes and LAI), then the 8-draw L6 screen, then the judge.
   - Open design question: should the gain apply to all trees? LUE rises with the diffuse fraction everywhere, but
     temperate NPP is fitted through EPS_SCALE. If it does, the temperate boxes have to be re-checked against MOD17.
2. **Not recommended: rl x1.5 + TrBE eps x1.076** (`scout3/rl1.5_eps1.076.txt`). It keeps NPP neutral on Earth and
   brings NPP/GPP to 0.42. But it is a stand-in for the missing mechanism: it undoes scout 210's reason for taking the
   dry-season efficiency floor, and the LAI still falls to 4.25. It is a temporary fix.
3. **Rejected: rw x1.5.** It overshoots measured stem and root respiration by about 30%, and NPP falls 16-19%.
4. **Also defensible: change nothing.** NPP/GPP 0.445 is inside the measured 0.32-0.49. PW-1517 is `impact: low`, and
   the owner's north star is "stable, not fiddly". If the diffuse-light gain is not wanted for its own sake (the wet
   season's higher Amazon photosynthesis is a real, documented effect), close PW-1517 as within range.

## 5. Why no coupled screen

The brief allowed 8 L6 draws for one kitchen-sink arm "if the diagnosis is clear". It is clear, but the only arm I
could build today is option 2, the efficiency stand-in. That arm would not be merged, and on Earth it is NPP-neutral
by construction, so a coupled screen of it would say little about option 1. I left the cores free. (Load average was
~42 on 48 cores during this pass.)

## 6. PW-1516: the path from plants to CO2

The CO2 stock (`planet/tectonics/earth.py::co2_stock`) settles each step where sink x co2_law(X) = source, both
measured against their references. Every way the plants reach it:

| path | where | 210b's paired change (late, median [95% CI]) |
|---|---|---|
| rooted cover -> weathering's plant factor | `earth.weathering`, `plant_factor(sim.cover_w)` | w_plant -0.0001 [-0.012, +0.012] |
| ground cover -> erosion supply (`k_mult`, the bare-ground erodibility) | `earth.py` ~l.1226, `sim.veg` | w_supply +2.0 [-5.0, +4.8] (of 170) |
| woody / deep cover -> Budyko w -> runoff; leaf albedo -> temperature | `climate.vegetation_feedbacks`, `albedo_warming` | w_q +12 [-23, +30] mm; w_temp +0.038 [-0.009, +0.075] |
| the references (learnt in the spin-up with the potential vegetation) | `earth.references`, `cover_pot` | sink/source ref (ln) -0.01 [-0.03, +0.05] |
| methane | `earth.ghg_conc` reads dT and runoff only | follows dT |
| NPP itself | not read by the carbon cycle since PW-1424 C | none |

- None of the plant paths moves beyond chance.
- The one that leans, w_temp (warmer weathering), points the wrong way to cause higher CO2: more weathering draws CO2
  down. It is a consequence of the warmth.
- The input that did move is the **volcanic source**: source_raw 2654 -> 2758, d +74 [-2, +263], 23/36 up. It is new
  ocean floor + arc growth + plume melt, times the drift noise. That noise comes from a per-step seeded generator
  (`default_rng([seed, step_no, 1])`), so it is not desynchronised by the plants.
- The plants reach the source only through the runs drifting apart (different erosion, different topography, different
  tectonic history). A 2.8% higher source needs about +0.05-0.1 e-folds of CO2 to balance, given the sink's sub-linear
  CO2 law, which is the size seen.
- The headline statistics are weak too: late dT median diff +0.77 [-0.26, +1.87], sign p 0.24. The +0.10 e-fold CO2
  (p 0.065) is one of ~15 paired measures 210b tested.

**Verdict: chaos.** No deterministic plant -> CO2 path exists outside the logged factors, and those are flat. Not fully
proven: 210b's runs were deleted with its worktree, so the per-pair correlation of the CO2 change with the source change
cannot be computed now. `scout2b_mech.py` now prints `d late CO2 vs d ln source_raw / sink_raw / w_*` (r per pair), so
the next paired judge of any plant change shows directly which side carries the CO2. If the source's r is high and the
plant factors' r near zero, close it then. My lean is to close PW-1516 as chaos now and lean on that line in the next
judge.

## Files
- `docs/review/climate/npp/scout3_probe.py`: the TrBE stand's respiration split on Earth's observed climate (flags
  --rl-x, --rw-x, --eps-x).
- `docs/review/climate/npp/scout3/run.sh`, `scout3/*.txt`: the six Earth screens.
- `docs/review/climate/npp/scout2b_mech.py`: + the per-pair CO2 vs source/sink correlation (PW-1516).
- Sources read: Chambers et al. 2004 (escholarship qt8mc3s8hp), Atkin et al. 2015 (USDA Treesearch 52124), Yan et al.
  2017 (White Rose 124617), Malhi et al. 2011 (PMC3179639), Malhi et al. 2009 (abstract only).
