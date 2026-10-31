# Why so many humans, and why no continental blocs (lane 84, 2026-10-31)

Investigation only: no model code was changed. Each number is one try per seed of the dnd preset, or a five-people cut of it, on
the quick world 4360a3 (L6). Three base runs were also made on af2677. A scratch probe ran the history in process and switched one
rule or number off at a time; nothing was saved under runs/. "Points" are the change in the humans' share of all people against the
base at the same seeds.

## In plain words

1. **Why so many humans.** Humans are about two thirds of all people. That is mostly because each human counts for more, not
   because they hold most of the land. They hold about a fifth of the land peoples hold, at about seven times everyone else's
   people per km². The causes, measured, largest first:
   - **Their density:** 10 people per km² (farmers 12), a farming number used from 200,000 years ago on. Elves have 1, orcs 1,
     dragonborn 2. At a third of it, humans drop from 67% to 35%.
   - **The contest's edges for an expanding, dense farming people:** all five together are worth 19 points.
     No one edge does it. Each alone moves the share by 4 points or less, because when one is off another carries the humans.
     The farmers' edge, the momentum and the expansive press together take 8 points; all five take 19, and the human range falls
     from 73 to 43 Mkm². Every one of them rewards a people that is spreading, dense and farming, and that is the humans.
   - **Their ways of life stack:** farmers, herders, seafarers and nomads are extra lines that hardly compete with the core humans,
     so a human square kilometre is filled about 1.3 times. Without them humans drop to 51%. This is most of the jump in human
     numbers when farming starts.
   - **Boats:** they take humans to every landmass. Without them humans drop to 58%.
   - **Density following the land's productivity** favours farmers: 6 points.
   - **Not causes on their own:** the momentum edge, the growth rates, frontier invasion with density push, and one-spot
     founding. Nor is a simple "fit decides" rule, because on today's niches humans fit every people's best country as well as that people
     does.
2. **Why no continental blocs.** The continents are blocky already: two or three peoples make 90% of a typical continent. But
   humans lead 6–9 of the 10 continents and are at least 5% of the people on all ten. The other blocs are always the same few
   (kobolds, kenku, gnomes, dragonborn) on the reptile stem's own continent.
   - Every mammal people starts on one cradle continent: orcs, dwarves, halflings, hobgoblins, goblins, bugbears, tabaxi and leonin,
     in 7–8 runs of 8.
   - Only humans leave it, by boat, and they win where they land.
   - Cut the humans down (density, groups, boats) and the blocs you describe appear: kobold, dragonborn, kenku, halfling, hobgoblin
     and orc continents.
3. **The human offshoots.** You are right about the effect, not the counting. The summaries already count farmers, herders and the
   rest as humans. But each offshoot is a full extra claim on the same land, and that inflates humans by ~16 points. They should be
   one species that splits its land between ways of life, the level the regional populations (demes) already describe.
4. **Brittle peoples.** On 4360a3 with fixed dates, hobgoblins, tabaxi, bugbears and goblins are steady: under 3× between 8
   seeds. Halflings flip, all or nothing, at 0.5% or 5–10%. On af2677 even plain seeds swing 40–600×. Lane 77's pooled table mixed
   both worlds and jittered dates. The tipping point is always a race:
   - Was the people born in a cut-off part of its stem's range, or teleported to the best spot when its parent was gone?
   - Do the humans' boats reach its continent before it fills? On af2677 they reach the biggest continent 30 kyr ago in one seed
     (humans 65%) and 3–6 kyr ago in the others (39–47%).
   - The contest is winner-takes-all, with a 0.5 M km² floor for the loser. So it lands either way, never in between.
5. **Dragons in farmed land.** They keep 9% of their numbers (median of 8 seeds). About 40% of the loss is food (the peoples'
   hunters and the overkill of the wild herds; livestock gives part back). About 60% is persecution. Where people are thickest (10 or
   more per km²), persecution is over 90% of the loss.
6. **War.** There is none. Peoples only compete for room; nothing kills anybody. So nothing gives "too many goblins, hunt them down
   locally, they bounce back". The model has that exact rule for dragons, a kill weighed against how fast they breed. Run between
   hostile peoples, it would make goblins bounce back, but it would not brake them; it would thin elves (lane 82's finding).

**Top three changes** (proposals, taken onto the board as PW-1202 to PW-1207; lane 83 is reworking the contest, founding and density code):
1. A people's ways of life share one capacity per cell (PW-1205).
2. Density follows the way of life a people actually lives, era by era: forager humans until they farm, and any people that farms
   at farmers' numbers (PW-1203, the general form of D20 lever 3).
3. Peoples born apart (splits founded across landmasses, as roots are) and a home-ground edge, so continents get their own owners
   (PW-1202). With it, a cost of being a generalist in the contest; otherwise D20's "fit decides" has nothing to act on
   (PW-1204).

## 1. Why humans hold 53–94%

### Land against density (base, seed 7)

| people | nominal density /km² | realised /km² of its range | range Mkm² | share of held range | share of people |
|---|---|---|---|---|---|
| human | 10 (farmers 12) | 9.78 | 62.9 | 21% | 65% |
| kobold | 4 | 2.31 | 43.8 | 15% | 11% |
| kenku | 3 | 1.72 | 39.4 | 13% | 7.2% |
| gnome | 12 | 3.75 | 14.1 | 4.7% | 5.6% |
| dragonborn | 2 | 0.91 | 43.1 | 14% | 4.2% |
| hobgoblin | 4 | 1.09 | 15.0 | 5.0% | 1.7% |
| orc | 1 | 0.88 | 16.4 | 5.5% | 1.5% |
| elf | 1 | 0.31 | 16.0 | 5.3% | 0.5% |
| dwarf | 4 | 1.87 | 1.0 | 0.3% | 0.2% |

Humans hold 36% of the land and 21% of all held range, but 65% of the people: 9.8 per km² against 1.4 for all the rest.
- Keeping every presence as it is but giving all peoples one density would put humans at 35%.
- Humans realise ~98% of their nominal density; the others 30–60%. The gap is the stacked groups (section 3) and rivals thinning
  the others.

### Ablations, dnd (seeds 7, 10, 13)

| arm | what it switches off | human (mean) | kobold (mean) | halfling (mean) | elf (mean) | dwarf (mean) | orc (mean) | hobgoblin (mean) | human change vs base, same seeds (points) | human range Mkm² |
|---|---|---|---|---|---|---|---|---|---|---|
| base (n=3) | nothing (today's main) | 66.9% | 9.57% | 3.72% | 0.45% | 0.184% | 1.46% | 1.58% | +0.0 (+0, +0, +0) | 73 |
| hdens (n=3) | human and human-group density x0.3 | 34.5% | 17.5% | 9.75% | 0.72% | 0.336% | 3.17% | 5.2% | -32.4 (-32, -32, -33) | 82 |
| nogroups (n=3) | the five human groups (farmers, herders, seafarers, nomads, arctic) | 50.9% | 14.6% | 4.98% | 0.561% | 0.224% | 2.38% | 3.51% | -15.9 (-14, -12, -22) | 68 |
| nosea (n=3) | human boats (sea share 0.05, no seafaring trait, humans and groups) | 58.4% | 12.1% | 4.18% | 0.482% | 0.201% | 1.37% | 2.12% | -8.5 (-10, -5, -10) | 46 |
| noprod (n=3) | density following the land's productivity (flat map) | 60.9% | 11.6% | 4.62% | 0.536% | 0.217% | 1.38% | 1.99% | -5.9 (-7, -5, -6) | 72 |
| nofarm (n=3) | the farmers' edge (rival load x0.5 on farmland, double speed) | 63.8% | 10.6% | 3.66% | 0.485% | 0.198% | 1.62% | 1.95% | -3.1 (+3, -3, -9) | 67 |
| fit (n=3) | adds a 'fit decides' rule: rival load x (K_j/K_k), clipped 0.25-4 | 66.4% | 8.77% | 6.2% | 0.422% | 0.206% | 1.8% | 2.28% | -0.5 (+3, -1, -3) | 75 |
| noinv (n=3) | frontier invasion and density push (INVADE 0, DENSITY_PUSH 0) | 71% | 7.69% | 2.73% | 0.707% | 0.145% | 1.7% | 2.3% | +4.2 (+7, +8, -3) | 81 |
| edges (n=3) | all five contest edges together: invasion, density push, farmers' edge, expansive press, surge | 48.1% | 13.9% | 4.46% | 0.0755% | 0.191% | 1.97% | 2.86% | -18.8 (-12, -19, -26) | 43 |
| nosurge (n=3) | the surge momentum | 70.1% | 10% | 5.03% | 0.394% | 0.191% | 1.13% | 1.71% | +3.2 (+1, +7, +2) | 81 |
| nogrowth (n=3) | lane 78's growth-rate eras (flat rate) | 69.3% | 7.5% | 3.94% | 0.455% | 0.197% | 1.22% | 1.48% | +2.4 (+10, -2, -1) | 80 |
| local (n=3) | one-spot (local) founding for every split | 70.9% | 0.155% | 6.86% | 0.391% | 0.176% | 0.906% | 1.48% | +4.0 (+9, +5, -2) | 85 |
| sink (n=3) | density x0.3, no groups, no boats, and the fit rule, together | 9.04% | 23.8% | 9.62% | 0.92% | 0.519% | 4.26% | 9.13% | -57.8 (-56, -56, -62) | 29 |

The contest's edges, in combinations (same seeds):

| arm | what it switches off | human (mean) | kobold (mean) | kenku (mean) | dragonborn (mean) | elf (mean) | human change vs base, same seeds (points) | human range Mkm² |
|---|---|---|---|---|---|---|---|---|
| noinv (n=3) | frontier invasion and density push (INVADE 0, DENSITY_PUSH 0) | 71% | 7.69% | 6.72% | 3.68% | 0.707% | +4.2 (+7, +8, -3) | 81 |
| farmsurge (n=3) | the farmers' edge and the surge together | 63.7% | 11.7% | 6.97% | 3.31% | 0.485% | -3.1 (-3, -3, -4) | 71 |
| noexp (n=3) | the expansive press (EXPANSE_PRESS 0) | 67.1% | 10.6% | 5.86% | 3.01% | 0.0146% | +0.2 (+1, +6, -7) | 74 |
| invexp (n=3) | frontier invasion, density push and the expansive press | 65.6% | 12.2% | 7.6% | 4.14% | 0.0921% | -1.3 (+5, +6, -15) | 65 |
| fsexp (n=3) | the farmers' edge, the surge and the expansive press | 58.6% | 14.1% | 8.46% | 4.53% | 0.0175% | -8.3 (-3, -5, -17) | 54 |
| edges (n=3) | all five contest edges together: invasion, density push, farmers' edge, expansive press, surge | 48.1% | 13.9% | 16.1% | 8.1% | 0.0755% | -18.8 (-12, -19, -26) | 43 |

The edges substitute for each other: off one at a time, none moves the human share by more than 4 points; off together, 19.
The expansive press alone is worth nothing to the humans, but without it the elves fall from 0.45% to 0.01%: it was added for them
(PW-869).

Over time (seed 7):
- The human share is 24% at 104 kyr and 37–39% from 44 to 9.5 kyr. It jumps to 56% by 7 kyr and ends at 63–65%.
- Human numbers double, from 212 M to 417 M, between 9.5 and 7 kyr. That is when the farmer group (density 12, from 9 kyr) appears
  on top of the core humans.
- Without the groups the same step goes from 37% to 35%.

### Ablations, five peoples (humans, elves, dwarves, halflings, orcs; seeds 7, 10, 13, 21, 34)

| arm | what it switches off | human (mean) | elf (mean) | dwarf (mean) | halfling (mean) | orc (mean) | human change vs base, same seeds (points) | human range Mkm² |
|---|---|---|---|---|---|---|---|---|
| base (n=5) | nothing (today's main) | 83.2% | 1.36% | 0.994% | 13.8% | 0.669% | +0.0 (+0, +0, +0, +0, +0) | 107 |
| hdens (n=5) | human and human-group density x0.3 | 58.1% | 3.3% | 3.02% | 33.8% | 1.77% | -25.1 (-27, -26, -26, -23, -24) | 108 |
| nogroups (n=5) | the five human groups (farmers, herders, seafarers, nomads, arctic) | 73.9% | 2.3% | 2.06% | 20.4% | 1.27% | -9.2 (-11, -11, -11, -6, -7) | 94 |
| nosea (n=5) | human boats (sea share 0.05, no seafaring trait, humans and groups) | 64.9% | 4.91% | 1.74% | 27.4% | 1.08% | -18.3 (-21, -20, -19, -15, -16) | 40 |
| noprod (n=5) | density following the land's productivity (flat map) | 79.8% | 1.92% | 1.18% | 16.5% | 0.604% | -3.4 (-4, -3, -3, -3, -4) | 105 |
| nofarm (n=5) | the farmers' edge (rival load x0.5 on farmland, double speed) | 81.2% | 1.95% | 1.15% | 14.9% | 0.756% | -1.9 (-4, -2, -2, -1, +0) | 97 |
| nosurge (n=5) | the surge momentum | 82.9% | 1.68% | 1.18% | 13.5% | 0.658% | -0.2 (+1, -1, -1, +1, -1) | 105 |
| nogrowth (n=5) | lane 78's growth-rate eras (flat rate) | 83.8% | 1.71% | 1.21% | 12.7% | 0.624% | +0.6 (+4, -1, -1, +0, +1) | 105 |
| fit (n=5) | adds a 'fit decides' rule: rival load x (K_j/K_k), clipped 0.25-4 | 83% | 1.46% | 1.03% | 13.8% | 0.715% | -0.1 (-2, -1, -1, +3, +0) | 110 |
| noinv (n=5) | frontier invasion and density push (INVADE 0, DENSITY_PUSH 0) | 82.6% | 2.01% | 0.823% | 13.7% | 0.932% | -0.6 (+0, -0, -0, +0, -2) | 100 |
| edges (n=5) | all five contest edges together: invasion, density push, farmers' edge, expansive press, surge | 77% | 2.29% | 1.38% | 18.5% | 0.873% | -6.2 (-10, -4, -7, -5, -4) | 85 |
| local (n=5) | one-spot (local) founding for every split | 88.4% | 1.57% | 1.07% | 8.21% | 0.79% | +5.2 (+15, +8, -1, +4, +0) | 105 |
| sink (n=5) | density x0.3, no groups, no boats, and the fit rule, together | 21.1% | 9.34% | 6.06% | 59.5% | 4% | -62.1 (-65, -65, -60, -59, -61) | 35 |

Small rosters go higher because fewer peoples have taken the land before humans land on it.
- In this cut humans hold 107 M km², 61% of the land, against 73 in full dnd. Without boats they hold 40, and the share falls 18 points.
- The halflings are the humans' twin: same stem, a niche inside the humans', density 12. Slow the humans (`sink`) and the halflings
  take the human slot, at 60%.
- Whoever is the dense, broad, lowland people with boats ends up on top.
- Lane 77 found that a fifth of the density left humans at 98% in its five_peoples tree (humans, lizardfolk, goblins, aarakocra,
  gnomes). In this cut, a third of the density takes them from 83% to 58% with the same range. The density lever works through the
  count once rivals of comparable reach exist.

Mechanism, file:line:
- **Density** is one number per line for the whole run.
  - `History.dens` (model.py:102), times a static productivity field (model.py:113-116, prey.py:121-140).
  - `population` = presence × density × area (peoples.py:88-95). dnd.toml:704 has humans at 10, :721 farmers at 12.
  - Lane 78's eras change growth rates, never density (growth.py:31-46).
- **Expansive press** (pressure.py:11-18, applied at competition.py:67-68): a people with explore ≥ 0.4 feels up to
  EXPANSE_PRESS = 60% less competition until it holds half of the country it could hold (K ≥ 0.3).
  - Humans' country is so large that the discount fades only late. Off alone it is worth +0.2 points to them (table above).
  - The discount is 30% for humans (explore 0.55) and 60% for seafarers (0.8), nomads and arctic hunters (0.7).
- **Groups** barely compete with their people: GROUP_KIN 0.5, no closed-country term (model.py:90-96).
- **Sea:** humans have sea share 0.6, seafarers 0.85 (dnd.toml:706, :769). Long crossings land on any landmass the people does not
  yet hold, wherever it has room (crossing.py:196, dispersal.py:130-149).
- **Farmers** get the rival load ×0.5 on farmland after FARM_KYR (competition.py:59-60), and double speed (dispersal.py:90).
- **Fit:**
  - On the present climate of 4360a3, `habitat.capacity` gives humans K ≥ 0.5 on 54% of land and ≥ 0.9 on 39%.
  - In each people's own best country (its K ≥ 0.7), the humans' median K is 0.97 for elves, and 1.00 for orcs, hobgoblins,
    halflings, dragonborn, gnomes and leonin. It is 0.92 for kenku, 0.94 for bugbears, 0.87 for tabaxi and 0.82 for kobolds.
  - Only dwarves and goliaths have country humans fit badly (0.40). So a K-ratio fit rule changes nothing (`fit` arm).

What would change it:
- density by way of life and era;
- one capacity per people across its groups;
- contest edges that do not all reward the same people: today the farmers' edge, the momentum, the expansive press, invasion and
  density push all favour a spreading, dense farming people, and each stands in for the others;
- a generalist cost, or fit by preference, in the contest;
- later or costlier deep-sea crossings.

Share bands can finish the job afterwards.

## 2. Why no continental blocs

The table is per landmass of 1 Mkm² or more that holds people. The mix distance is half the summed differences between a
continent's people shares and the world's, weighted by people: 0 means the continent looks like the world, 1 means it has no
people in common with it. Medians over the runs.

| arm (world) | runs | humans' share of people | continents >= 1 Mkm² | led by humans | peoples making 90% of a continent | mix distance from the world | leaders seen (non-human) |
|---|---|---|---|---|---|---|---|
| base (4360a3) | 8 | 68% | 10 | 6–9 | 2 | 0.29 | dragonborn, gnome, kenku, kobold |
| base (af2677) | 3 | 47% | 6 | 3–4 | 3 | 0.33 | dragonborn, gnome, halfling, hobgoblin, kobold |
| no human boats | 3 | 58% | 9 | 3–4 | 3 | 0.40 | dragonborn, gnome, hobgoblin, kenku, kobold |
| no human groups | 3 | 51% | 9 | 7–7 | 3 | 0.38 | gnome, kobold |
| human density x0.3 | 3 | 33% | 10 | 6–8 | 3 | 0.40 | gnome, halfling, kobold |
| all four (sink) | 3 | 9% | 9 | 0–1 | 3 | 0.48 | dragonborn, halfling, hobgoblin, kenku, kobold |

Per people, base on 4360a3, 8 seeds (medians):

| people | continents where it is ≥ 5% of the people | share of its people on its main continent | continents it leads | born on the cradle continent | landmasses ever reached |
|---|---|---|---|---|---|
| human | 10 | 30% | 8 | 5/8 | 32 |
| kobold | 3 | 54% | 1 | 1/8 | 8 |
| kenku | 3 | 59% | 0 | 2/8 | 10 |
| gnome | 2 | 86% | 0 | 1/8 | 4 |
| dragonborn | 3 | 39% | 0 | 1/8 | 16 |
| hobgoblin | 1 | 92% | 0 | 7/8 | 3 |
| orc | 0 | 58% | 0 | 8/8 | 8 |
| halfling | 2 | 63% | 0 | 8/8 | 4 |
| tabaxi | 0 | 50% | 0 | 8/8 | 4 |
| elf | 0 | 85% | 0 | 1/8 | 8 |
| dwarf | 0 | 100% | 0 | 8/8 | 2 |
| goblin | 0 | 100% | 0 | 7/8 | 2 |
| bugbear | 0 | 100% | 0 | 8/8 | 1 |
| leonin | 0 | 89% | 0 | 8/8 | 4 |

"Cradle" is the 22 Mkm² continent where the mammalian stem arises (landmass rank 2).

When humans first reach each continent (base, 4360a3): the cradle 200 kyr ago, the largest continent (54 Mkm²) 58–88 kyr ago. The
reptile-held continents (41, 13 and 10 Mkm²) are reached only 1–4 kyr ago, and humans are still 3–24% there by the present.

What prevents blocs, in order:
1. **One cradle.**
   - A split is founded inside, at the edge of or beside its parent's range (origins.py:265-321). Founders carried across the sea
     weigh 0.6 × K × the crossing's reach and rarely win.
   - The split does draw its landmass first (`_by_landmass`, origins.py:302), but only among the landmasses its score reaches,
     and the far ones are weighted down by that reach. So the parent's own continent nearly always wins.
   - So the whole mammal radiation starts on one continent.
   - The only rule that puts peoples apart is the root rule: a root avoids the other roots' landmasses (origins.py:149-158). That
     rule is why a reptile and avian continent exists at all.
2. **Only humans leave.** Sea share 0.6 and the seafarer group carry humans to 32 landmasses, all ten continents. The others (sea
   share 0.05–0.3) mostly stay where they were born.
3. **They win where they land:**
   - the density, the stacked groups and the contest's edges for a spreading, dense farming people (section 1);
   - a niche as good as anyone's;
   - losers keep the 0.5 M km² refuge floor (competition.py:89-93, REFUGE_MKM2), not a continent.
4. **Inherited stem ranges** (origins.py:412-444, `_end_parent`). They put kobolds, kenku and dragonborn on ~3 continents each. That
   is why the non-human blocs are always the same four peoples.

The contest itself makes blocs, not mixtures: ALPHA_CLOSED 1.4 excludes in closed country, and two or three peoples make 90% of a
continent. The problem is who wins, not mixing.

What would produce blocs:
- sister peoples born on different continents (split founding by landmass, as roots are);
- a home-ground edge, so a landing makes a coastal enclave instead of a takeover;
- open-sea crossings only late, if those two are not enough.

The `sink` arm previews it. With the humans cut down, the continents belong to kobold, kenku, dragonborn, halfling, hobgoblin and orc
blocs (mix distance 0.48, against 0.29).

## 3. The human offshoots

- **How the tree builds them.**
  - They are `origin = "group"`, `group_of = "human"` (dnd.toml:714-788).
  - A group starts where its own habitat beats its people's by 15% and takes half the people's presence there (groups.py:12-51).
    It keeps arising the same way in new cells (groups.py:53-67).
  - It is its own line, with its own comfort range, density, sea share and contest coefficients against the other peoples.
- **How shares are counted.** Every summary rolls a group into its people (`tree.people_of`, `History.whole` and `fold`,
  peoples.py:46-75; `bands.shares`). The offshoots are not counted as separate peoples.
- **Where the inflation comes from.** Within a people the lines compete at GROUP_KIN 0.5 × their overlap, with no closed-country term
  (model.py:90-96). So they coexist near full.
  - Full dnd, seed 7: the human lines' presences sum to 1.01 per human cell on average, against a capped whole of 0.78. 89% of human
    cells hold two or more human lines.
  - Five-people cut: 1.26 against 0.90.
  - Population counts each line at its own density.
- **Do they change the contest?** Yes.
  - Herders, nomads, seafarers and arctic hunters carry humans into steppe, desert, coast and tundra on their own niches.
  - The seafarers (sea share 0.85, explore 0.8) make about half the human landings: 24–27 long crossings each for core humans and
    seafarers in a run.
  - Groups off: humans go from 67% to 51% (dnd) and 83% to 74% (five peoples). The human range moves less, from 73 to 68 Mkm².
- **Should they be plain humans at the species level?** Yes: one capacity per cell, split between ways of life.
  - The groups would still decide where farmers, herders and seafarers live.
  - The regional and ethnic level already exists as demes (demes.py, output only). That is where "the farmers of the river plain"
    and "the steppe nomads" belong as populations.

## 4. Brittle peoples

Lane 77's own runs (scratch l77/suite, range arm, the model before lane 78), split by world and family. 0.01% is the suite's floor.

| people | 4360a3 seeds | 4360a3 jittered dates | af2677 seeds | af2677 jittered dates | pooled |
|---|---|---|---|---|---|
| hobgoblin | 1.1–1.8% (1.7x) | 1.7–6.0% (3.6x) | 1.4–13.9% (9.8x) | 0.04–9.9% (265x) | 509x |
| tabaxi | 0.94–1.24% (1.3x) | 0.90–1.63% (1.8x) | 0.014–0.025% (1.7x) | 0.013–0.53% (41x) | 125x |
| bugbear | 0.01–0.017% (1.7x) | 0.01–0.09% (9x) | 0.01–0.45% (45x) | 0.01–0.64% (64x) | 64x |
| halfling | 0.39–5.5% (14x) | 0.40–8.4% (21x) | 11–17% (1.5x) | 5.2–8.9% (1.7x) | 54x |
| goblin | 0.09–0.16% (1.8x) | 0.11–0.25% (2.2x) | 0.48–0.85% (1.8x) | 0.44–3.5% (8x) | 49x |

Today's main, dnd, plain seeds:

| people | 4360a3, 8 seeds: min–max (swing) | af2677, 3 seeds: min–max (swing) | what decides it |
|---|---|---|---|
| hobgoblin | 1.14–1.88% (1.7x) | 0.032–9.35% (291.8x) | af2677: founded inside the parent's range (7–9%) or at its edge (0.03%), and whether humans reach the big continent before ~6 kyr ago |
| tabaxi | 0.748–1.13% (1.5x) | 0.0162–0.638% (39.3x) | the world: their rainforest is free on 4360a3, taken on af2677 |
| bugbear | 0.00548–0.0145% (2.6x) | 0.00889–0.587% (66.1x) | pinned at the 0.5 Mkm² refuge floor unless an isolated part of the stem's range is free (af2677 s13: 0.59%) |
| halfling | 0.538–10% (18.6x) | 0.017–10% (589.1x) | founding spot: an isolated part of the archaic-human range (or 'parent gone', a teleport) gives 5–10%, the edge next to humans 0.02–0.6% |
| goblin | 0.128–0.225% (1.8x) | 0.97–1.3% (1.3x) | near the floor on 4360a3; on af2677 'parent gone' founding (best habitat anywhere) gives ~1% |

The sensitivities:
- **Founding spot.**
  - A split's cell is drawn from its parent's range, an isolated part weighted ×3 and the edge ×1.5, times a heavy-tailed noise
    (origins.py:273-303).
  - Born in a part of the stem's range cut off from the main one, a people takes that whole part (range founding, origins.py:314-317)
    and fills it before the humans come.
  - Born at the edge next to the humans, it is pinned at the floor.
  - "Parent gone" sends a split to its best habitat anywhere in the world (origins.py:271-272, 383-388, PW-1184). On af2677 that is
    where the halflings' and goblins' best results come from.
- **The humans' landing date.** Crossings are a Poisson draw per kyr, with rate × exp(−gap / L) (crossing.py:178-215). A people
  that fills a continent before the boats arrive keeps much of it. One that does not, loses it within a few kyr.
- **Winner takes all, with a floor.**
  - Halflings, hobgoblins and bugbears live inside the humans' niche (halflings 9–22 °C against 6–26 °C, both temperate lowland;
    halflings are siblings of humans, kin 1.0).
  - In closed country such pairs exclude: alpha_eff > 1 (model.py:77-83, ALPHA_CLOSED).
  - The loser sits at the 0.5 M km² refuge floor (bugbears in every seed on 4360a3).
  - So shares are bimodal. Density then multiplies the winner's land: halflings at 12 per km² turn one landmass into 10% of the
    world's people.
- **The world.** Tabaxi are ~1% on 4360a3 in every seed. On af2677 their rainforest is taken in 2 of 3 seeds. That is geography.

What would change it:
- one-spot founding near the parent's last land (PW-1181, PW-1184), which ends the "isolated part" and "parent gone" lotteries;
- a generalist cost, so a specialist keeps its own country against the humans whoever came first;
- the suite reporting each people's swing per world and per family (PW-1207).

## 5. Dragons in farmed land

Dragons are counted at the present. Each dragon-held cell is compared with what the same dragons would number with no peoples:
- *food alone*: the peoples' effect on the food (overkill of the wild herds, the hunters' take, the livestock added), with no killing;
- *persecution alone*: the kill, with the food as if no peoples were there.

The loss is split by averaging the two orders (Shapley). Base, 8 seeds. "Peopled" is where the peoples' pressure on the herds is
at least half (as the megafauna summary counts it); farmland is the history's farmland tag.

| land | dragons kept, of the no-peoples number (median; min–max) | kept under food alone | kept under persecution alone | share of the loss: food | share of the loss: persecution |
|---|---|---|---|---|---|
| all peopled land | 12.4% (8.5–13.8%) | 52% | 41% | 44% (35–60%) | 56% |
| peopled farmland | 9.2% (6.6–11.5%) | 52% | 37% | 42% (22–59%) | 58% |
| 10+ people per km² | 4.2% (3.4–4.7%) | 88% | 5% | 7% (2–11%) | 93% |

The food budget in peopled farmland (seed 7, per km² a year; the figure with no peoples in brackets):
- the wild herds' sustainable offtake is 0.118 t (0.276);
- the peoples' hunters take 0.096 t of it;
- the herders' stock adds 0.12–0.17 t at the tolerable loss share;
- the smaller predators take 5/6 of what is left;
- the dragons' food is 0.023–0.030 t (0.045).

So hunting and overkill nearly empty the wild offtake, and the livestock gives back about half. That rests on STOCK_TOLERABLE = 0.1,
marked unverified in megafauna.py. In the densest land the kill dominates: its effort grows with people per km² × their means × the
era (megafauna.py:273-281; the share kept by age class, :232-271).

Mechanism: dragon density = natural(food) × kept(kill) × the food cap (megafauna.py:419-428). Food comes from `budget`
(megafauna.py:317-357). The "~9%" on the desk matches: 9.2% kept in peopled farmland, 6.6–11.5% over 8 seeds.

## 6. War

There is no war, raiding or killing between peoples anywhere in planet/lineages. settlements.py:41 says so: "Not modelled in v0:
war and raids". Peoples interact only through the competition for room (competition.py:24-99):
- the niche overlap, with the closed-country term: the larger excludes where it passes 1;
- frontier invasion: the denser presses at its front;
- displacement toward the room left, over TAU_KYR;
- the HOLD_MIN lapse;

and otherwise only through hybrids and contacts. So "war" today means "the denser, better-placed people takes the land". It favours
the humans, and nothing ever thins a people that has become too many.

The "too many goblins, hunted down locally, they bounce back" story exists as a rule for dragons and giants (megafauna.py `kill`,
`kept`). The share kept is 1 / (1 + effort × vulnerability / r), so fast breeders keep more and refill. Between hostile peoples the
same form gives exactly the bounce-back. Lane 82's finding (PW-1169) still holds: deaths brake slow breeders, not goblins. The brake
on fast breeders has to be land, as in PW-1172's lost-land term. Proposal: PW-1206.

## Proposals on the board

- PW-1205 (needs-decision): one capacity per people across its ways of life.
- PW-1203 (needs-decision): density by way of life and era.
- PW-1204 (needs-decision): a fit rule needs a generalist cost.
- PW-1202 (needs-decision): splits founded across landmasses, a home-ground edge, late deep-sea craft.
- PW-1207: the suite's swing per world and family.
- PW-1206 (needs-decision): the dragons' kill rule between hostile peoples.
## Method and caveats

- **Runs.** One try per seed: no best-of-4 and no share bands, so numbers differ from the desk's by a few points. World 4360a3 at L6,
  plus three base runs on af2677. Two worlds are not a sample of worlds.
- **The arms are crude.** ×0.3 density is a big cut, and `nosea` also removes the seafarers' boats. They rank causes; they do not
  calibrate fixes.
- **Effects do not add.** `edges` (all contest edges together) does far more than its parts one at a time. In `sink` (density,
  groups, boats and fit together) the halflings or kobolds take the human slot.
- **Tools.** The scratch probe and its analysis scripts are not committed (scratchpad l84/).
  - `probe.py` runs `History` in process and saves per-cell population per people, with groups rolled up.
  - It patches `_load` for the fit arm, and records each people's first arrival on each present landmass.
  - It also records the group stacking and the dragon decomposition at the present.
