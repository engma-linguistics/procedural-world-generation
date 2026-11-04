# The peoples-mechanisms ledger, round 1 (lane 176, 2026-11-04)

## In plain words

The peoples history has grown about thirty separate rules for where a people lives and how many there are. This round lists all of
them, then switches each one off in turn and runs the history again to see what moves.

- **Three things did nothing at all, and they are gone.** The share bands (per-people targets for a share of the world, which no
  preset sets), the dwarves' disease resistance (a stored number that nothing reads, because the plague isn't built), and one dead
  constant. The history now runs bit for bit the same as before on both test worlds.
- **One try is noisy.** A do-nothing nudge (a timescale 1.0 -> 1.01 kyr) moved 13 points of share on the dnd tree. The dwarves
  jumped from 4% to 16% of all people, and the humans dropped from 38% to 30%. The dwarves on that world have two stable outcomes,
  and the nudge just tips them from one to the other. So a single run can't show that any rule moves shares by less than about
  13 points. It can show which rules move more than that, and which ones change range and density more than chance does.
- **Clearly stronger than chance:** the habitat-tier weight on the landmass draw (species-area), the fit-weighted contest, the
  room left for dragons, a squeezed people's integration, the three-site founding, and the base strength of competition in closed
  country. These are kept. The last three are flagged as fragile: small code, big effect, and in one case a 20% change in the knob
  moved more than chance did.
- **Near zero, but not zero:** forager-farmer trade, raid food for den peoples, and the late mixing ramp. They move totals by
  0.01-1% (trade, raids) or about 1 point of share (mixing). They are kept for now. The goldens would change if they went, and
  each has a design reason to stay.
- Hunts change no numbers by design (they log events for the map) and stay.

Sample: one try each of the lane 77 suite's base variants: dnd at seed 7 on world 4360a3 for every rule, and seven_meals at seed 7
on af2677 for the first few. Chance was measured on four runs (dnd and seven_meals, seeds 7 and 10, both worlds). Everything was
run on main at b53ccd24 (the retirements were checked to be bit-identical). The budget was 4 cores, so this is a screen, not a
verdict. Where a row says "within chance", it means the rule's effect is under the noise of one try, not that it does nothing.

## How it was measured

`tools/peoples_robust.py`'s `run_one` on its `base` variants, with each rule's constant set neutral through the suite's own
params override (every history module and `spread`). The ladder's trade and raid caps were set the same way on `lineages.ladder`.
The den trait was set to 0 in `spec.TRAITS`, and `meta.growth_rates` to false. For each people (groups rolled up, megafauna
apart), I compared its share of all people, its range (Mkm2 held) and its density with the same seed's base run. The "moved"
column is half the summed absolute share change: the share of all people that changed hands, in points. Range and density are the
median over peoples of the absolute change. The harness and outputs were in the lane's scratch directory and were deleted at the
end. To redo a row, run `uv run python tools/peoples_robust.py run --family base --trees dnd --seeds 7 --worlds 4360a3 --arms now
--params '<the row's override>' --tag <name>`.

**Chance (the floor).** `TAU_KYR` 1.0 -> 1.01, on 4 runs: mean |d share| 0.58 pt a people, worst single people 11.1 pt. On
dnd-s7@4360a3: 13.1 pt moved, range 7%, density 7% (the dwarves 4.4 -> 15.5%). On sm-s7@af2677: 4.4 pt, 1%, 4%. A second
do-nothing nudge, `FOUNDER_KM` 400 -> 401, left all 4 runs bit-identical. The founding blob is whole cells, so 1 km doesn't
change it, and that one is not a chaos probe. So on dnd-s7, read share moves under ~13 pt and range and density changes under
~7-10% as chance.

## The ledger

Effect at defaults is dnd-s7@4360a3 unless marked "sm" (seven_meals s7@af2677). Verdicts: **keep**, **retired**, **fragile**
(keep, but small code with a big or knife-edge effect: a candidate for prone-to-explode), **near-zero** (keep for now, round 2
candidate), **core** (no neutral setting: the rule is the model).

### Where a people starts

| mechanism (code) | what it does | knobs | read by | effect at defaults (off or neutral) | verdict |
|---|---|---|---|---|---|
| Landmass draw by species-area (`origins`, PW-888) | a root draws its landmass in proportion to (habitable area)^z | `SPECIES_AREA_Z` 0.3 | origins | z = 0: **28.2 pt** moved, humans 38 -> 52%, tabaxi 4 -> 12%; range 26%, density 47% | **fragile** (one exponent, the largest effect measured) |
| Origin viability (`origins`) | a daughter needs a range big enough to persist to the present | `ORIGIN_MVP_MULT` 8, `MVP_REF_GEN` 40, `PERSIST_EXP` 1 | origins | not switched (no neutral: it decides whether a split can found at all) | core |
| One-spot founding, stem ends empty (`origins._origin_split`, `_end_parent`, PW-1152/1181) | a split founds within `FOUNDER_KM` of one origin cell, and a dead stem's land lies empty | `FOUNDER_KM` 400 | origins, dispersal | 400 -> 401: bit-identical (whole cells) | core |
| Founding at a few places (`origins._found_spread`, D27) | founds at up to 3 sites within one jump of the first | `FOUND_SITES` 3, `FOUND_SPREAD` 1 | origins | 1 site: **17.0 pt**, halflings 7.8 -> 0.2%, elves 4.3 -> 9.2%; range 18%, density 29% | **fragile** (halflings near-vanish on a founding detail) |
| Start hints (`origins._start_hints`, PW-763) | authored near / far_from / lat_band / landmass multipliers on placement | `START_KM` 1500, `NEAR_ORIGIN` 2, `NEAR_ORIGIN_KM` 1000 | origins | `NEAR_ORIGIN` 0 is in the "wishes" row below | keep (authored) |
| Megafauna-stem founding (`origins._origin_off_megafauna`) | kobolds and dragonborn found like an arrival, not from the dragons' range | none | origins | not switched | core |
| Arrivals, portals, waves (`portals`, `founding`, PW-697/1150) | arrivals come through portals or at their best habitat | `PORTAL_*`, `ARRIVAL_ROOM`, `ARRIVAL_POCKET_RINGS`, `PARTNER_PULL`, `HYBRID_REACH_KM`, `SCATTER_KM` | origins | not switched (only in portal trees; the base presets use `portal_mode` off) | keep |
| Contact hybrids (`contact`, PW-613/852) | half-peoples where parents meet; linger where they no longer do | `LINGER_KYR` 10, `LINGER_MIN` 0.3, `HYBRID_FROM_KYR` 12 | contact, summary | not switched (authored lines) | keep |
| Groups, ways of life (`groups`, PW-665) | a group founds and diverges where its habitat beats its people's by a margin | `GROUP_MARGIN` 0.15 | groups, habitat | margin 100: **bit-identical** | keep, but see the draft: the margin never binds on dnd-s7 |

### How much a cell can hold for a people (K)

| mechanism | what it does | knobs | read by | effect at defaults | verdict |
|---|---|---|---|---|---|
| Niche, body envelope, goods (`habitat`) | comfort range, body limits, the land's goods and [[use]] | `BODY_C` 8, `BODY_OCT`, `BODY_ELEV_M`, `HOLOCENE_KYR`; spec `limits` (ectotherms `cold_c = 1` in the trees) | everything | not switched | core |
| Learned country (`habitat._learn`, PW-1155) | a pressed people learns marginal country next to it | `LEARN`, `T_LEARN_KYR` 5, `FORGET_X` 10, `FULL_FROM` 0.5, `LEARN_GAIN` 0.6 | habitat, summary | off: 14.0 pt (within chance), but **range 23%, density 16%** (over chance); tabaxi 4 -> 11%. `LEARN_GAIN` x0.8: 13.1 pt, range 8% (chance) | keep |
| Carried knowledge (`habitat`, `CARRY`) | a learned biome opens the connected same biome | `CARRY` 0.9 | habitat | off: 14.8 pt, range 9%, density 6% (all chance) | keep (within chance on one try) |
| Wishes near/among (`habitat`, `model`, PW-889) | 'near' pulls habitat toward the partner and cuts competition; 'among' lets one live inside the other | `NEAR_RANGE` 0.5, `NEAR_KM` 300, `NEAR_TOLERANCE` 0.5, `AMONG_TOLERANCE` 0.7, `NEAR_ORIGIN` 2 | habitat, competition, summary (wish score) | all off: 8.3 pt, range 14%, density 12% (around chance) | keep (authored) |
| Megafauna habitat tiers (`habitat`, PW-924/1024) | dragons and giants in their own country, at half in tolerated country | `MEGAFAUNA_OFF` 0.1, `TOLERATE_K` 0.5, `EDGE_C/OCT/ELEV_M` | megafauna | not switched (megafauna only, §2.27) | keep |
| Brake: war-torn land (`counter`, D25 A) | dense, stateless peoples next to enemies lose capacity | `LAND_Q` 0.3, `H_MAX`, `WAR_Q`, `WAR_N0` 10, `WAR_EXT` 0.5, `STATE_Q` 3, `H_WAY`, `H_ERA`; `meta.war` | counter, summary (`lost`), suite | off: **19.5 pt**, humans 38 -> 23%, dwarves 4 -> 17%; range 7%, density 9% | keep (the share move is mostly the dwarf flip seen under chance) |
| Brake: in-fighting (`counter`, D31) | every people loses land to feuds by its circumscription and fill | `FEUD_CUT` 0.35, `SOCIAL_Q` 0.5; `meta.war` | counter, summary, suite | off: 11.7 pt, humans 38 -> 30%, density 22%. x0.8: 10.4 pt; x1.2: 3.0 pt (both within chance) | keep |
| Brake: raid losses (`counter`, `life_history.harsh_kept`) | a raider's canon losses scale on hostile borders | `RAID_Q` 1, `R_MAX` 3.6; `meta.raiders` | counter, suite | off: 5.3 pt, hobgoblins 14 -> 19%; range 6% (chance) | keep |
| Brake: culling wars (`counter`) | a crowded raider frontier is cut to 40% now and then; logs 'cull' | `CULL_FULL`, `CULL_F`, `CULL_P` 0.5, `CULL_D` 0.6, `CULL_AGAIN`, `RECOVER_YR`, `CULL_LOG_KYR`; `meta.raiders` | counter, events (viewer) | off: 6.0 pt, range 2%, density 3% (chance) | keep |
| Brake floors (`counter`, lane 101) | no brake below 5% of K, never under 0.24 on held cells | `COUNTER_FLOOR` 0.05, `BRAKE_HOLD` 0.24 | counter | not switched (a guard, not a rule) | keep |

### Who holds a contested cell

| mechanism | what it does | knobs | read by | effect at defaults | verdict |
|---|---|---|---|---|---|
| Lotka-Volterra contest, closed country (`competition`, `model`) | competition by niche overlap; closed country over 1, so the larger excludes | `ALPHA_CLOSED` 1.4, `TAU_KYR` 1 | competition | x0.8: **19.6 pt**, humans 38 -> 26%, range 23%. x1.2: 13.3 pt, range 17% | **fragile** (the base coefficient; 20% moves range 2-3x chance) |
| Fit decides the contest (`competition._fit_w`, D20) | rival's weight x clip(S_j / S_k, 1/3, 3) | `FIT_Q` 1, `BREADTH_Q` 0.5, `FIT_CLIP` 3; spec `contest` | competition | off: 15.2 pt, elves 4 -> 12%, halflings 8 -> 1%, density 75%; sm: **35.4 pt**, humans 9 -> 26%, a half-orc people revived | keep (designed to be strong; the strongest on seven_meals) |
| Coexistence cap (`spread.coexist_cap`, lane 73) | mutual invasibility: a newcomer can get into an incumbent's niche | `COEXIST` on | competition | off: 15.8 pt, hobgoblins 14 -> 25%, **range 26%**, density 16% | keep |
| One capacity per people (`model._kin`, PW-1205) | a people's groups share one K (alpha 1 among kin) | none | competition | not switched | core |
| Momentum edge (`pressure.surge`, lane 73) | a surging people feels rivals up to half less | `SURGE_Q` 0.5, `SURGE_KYR` 4, `SURGE_FULL` 2, `SURGE_LATE_FROM_KYR`; `meta.surge_early/late` | competition | off: 14.5 pt, humans 38 -> 26%, range 12%, density 13% (around chance) | keep |
| Expansive press (`pressure`, PW-869 successor) | an explorer holding little of its country presses harder | `EXPANSE_PRESS` 0.6, `EXPANSE_FROM/SPAN`, `EXPANSE_FILL` | competition | off: 7.3 pt, range 8% (chance) | keep |
| Integration under squeeze (`pressure`, PW-889) | a squeezed people shares a friendly neighbour's land | `INTEGRATE` 0.5, `SQUEEZE_FILL` 0.5 | competition | off: **21.6 pt**, humans 38 -> 20%, hobgoblins 14 -> 25%; range 8%, density 8% | keep (big share move; range and density at chance, so it redistributes heads more than land) |
| Late mixing (`competition`, `MIX_DROP`) | competition falls by 60% by the present in full corridors | `MIX_DROP` 0.6; `meta.mixing_start` | competition | off: **1.0 pt**, range 5%, density 2% (under chance) | **near-zero** (round 2: measure on more runs before retiring) |
| Hold lapse, Allee (`competition`, PW-920) | a people under 0.25 K on a cell leaves it | `HOLD_MIN` 0.25, `REFUGE_MKM2` 0.5 | competition | off: 16.8 pt (the dwarf flip), range 14%, density 8% | keep |
| Herders hold pasture (`competition`, `spec.WAY_PRESS`, PW-756) | nomads with herds press harder on good grazing | `WAY_PRESS`, `HERD_FULL` | competition | not switched | keep |
| Dragons take little room (`model`, PW-855) | a megafauna line's competition on peoples x0.1 | `MEGAFAUNA_PUSH` 0.1 | competition | 0: **20.3 pt**, hobgoblins 14 -> 27%, halflings 8 -> 0.6%; **range 38%**, density 27% | keep (a tenth of the dragons' push decides a lot: flagged with the halflings below) |

### How a people moves

| mechanism | what it does | knobs | read by | effect at defaults | verdict |
|---|---|---|---|---|---|
| Spread and pioneers (`dispersal`, `spread`) | widest-path spread; the frontier carries pressure into empty country | `PIONEER_P` 1, `EXPLORE_MARGIN`, `CONVERGE` | dispersal | `PIONEER_P` 0: 6.7 pt, range 12% (around chance) | core (the spread itself) / keep |
| Crowding drives exploration (`dispersal`, PW-887) | a crowded people crosses water and enters poor country more | `CROWD_HOP` 2, `CROWD_ENTER` 0.5 | dispersal | off: 19.1 pt (the dwarf flip), range 9%, density 7% (chance) | keep |
| Sea crossings (`crossing`, `dispersal._sail`) | rafts, boats and craft by tech; hops and landings | `HOP_EVERY_KYR` 1, crossing modes, spec `sea_share` | dispersal, events | not switched | core |
| Jumps (`dispersal._jump`, PW-920) | a hemmed-in people founds far off on a fat-tailed kernel | `JUMP_RATE` 0.02, `JUMP_KM` 800, `JUMP_SWIM_KM`, `JUMP_SHAPE` 0.5, `JUMP_MAX`, `JUMP_HEMMED` 0.05 | dispersal, suite (`jumps`) | off: 15.9 pt, humans 38 -> 46%, **range 34%**, density 23% | keep |
| Small-patch fade (`dispersal._viable`) | a patch under the viable population fades | `MVP_TAU_KYR` 2, `MVP_EVERY_KYR` 1; `meta.viable_pop` | dispersal, suite (`faded`) | off: 16.4 pt, tabaxi 4 -> 11%, halflings 8 -> 0.8%; density 27% | keep |
| Refuge hold-out (`dispersal._hold_out`, PW-1184) | a people the tree says lives holds out in a refuge | none | dispersal | not switched (a guard) | core |
| Growth rates (`growth`, PW-1147) | r from canon ages scales spread, displacement, fade and jumps | `meta.growth_rates` (dnd on, seven_meals off) | dispersal, competition | off on dnd: 14.9 pt, hobgoblins 14 -> 21%, range 19%, density 14% | keep |

### How many live on a held cell

| mechanism | what it does | knobs | read by | effect at defaults | verdict |
|---|---|---|---|---|---|
| Density ladder (`ladder`, PW-1275) | density from way of life x tech x land x kind | `PEOPLE_PROD`, the rungs (`FORAGER`, `GARDEN`, `PLOUGH`, `IRR`, `NOMAD`...) | model (`dens_at`), brakes, megafauna, every output | off (one number per line): **43.3 pt**, humans 38 -> 11%, halflings 8 -> 0.3%; range 10% | core |
| Forager-farmer trade (`ladder`, PW-1386) | a forager people gets up to half its food from farmers near | `BARTER_CAP` 0.5, `BARTER_HALF`, `BARTER_REACH` | ladder | off: 0.0 pt; total people -0.01% | **near-zero** |
| Raid food (`ladder`) | a den people gets up to 30% of its food raiding | `RAID_CAP` 0.3, `RAID_HALF`, `RAID_REACH` | ladder | off: 0.0 pt; goblins -0.9%, kobolds -1.3% density | **near-zero** |
| Den ground (`dens`, `ladder`, PW-1382) | den peoples at half density off good den rock | spec trait `den` 0.5 | ladder | den 0: 14.7 pt (the dwarf flip), range 3%, density 10% | keep |

### Story only, and retired

| mechanism | what it does | knobs | read by | effect at defaults | verdict |
|---|---|---|---|---|---|
| Old enemies hunt (`hunts`, D26 B) | logs 'hunt' events on enemy borders, from its own generator | `HUNT_PER_KYR` 0.5 | events -> viewer map | 0: every people bit-identical; only the hunt events go | keep (story, by design) |
| Best of N tries (`tries`) | keeps the try with the best wish score, less `LOST_PENALTY` a lost line | `LOST_PENALTY` 0.05; CLI `--tries` | `planet lineages` | not switched (the suite runs one try) | keep |
| Share bands (`history/bands.py`, lane 78) | re-ran the best try nudging a people's density into a share target | `band_pct` per people, `meta.band_rounds`, `BAND_KNOB`, `BAND_INSIDE`, `SLOPE_CLIP`, `SECANT_MIN` | tries, output, viewer workbench | no preset or robust tree sets `band_pct`; the loop never ran | **retired** |
| Disease resistance (`spec.disease_resist`, D25) | 0..1 share of plague losses shrugged off (dwarves 0.75) | `disease_resist` | nothing (spec parse and to_raw only) | none | **retired** |
| `ECTO_COLD_C` (params) | documented the ectotherms' 1 C cold margin | `ECTO_COLD_C` 1 | nothing (the trees set `limits.cold_c = 1` themselves) | none | **retired** |

## What was retired, and why it is safe

- **Share bands** (`planet/lineages/history/bands.py`, 142 lines; `Lineage.band_pct`, `Tree.band_rounds`, `BAND_ROUNDS`,
  `spec.band_warnings`, the calibration loop in `tries.simulate`, `History(knobs=...)`, the report and output lines; the workbench's
  band column, band-rounds field and Share bands panel; two tests). Safe because neither dnd.toml, seven_meals.toml nor any
  `tools/peoples_robust/trees/*.toml` sets `band_pct`, so `B.banded(tree)` was empty and the loop was never entered. The only other
  path, `History.knobs`, was only ever filled by the bands. The owner's even-six goal (PW-1189, already wontdo) is reached by the
  mechanisms, which is the D20 and robust-presets direction ("nudge systems rather than force them"). PW-1190 (bands calibrate on the
  best try's seed) has nothing left to fix.
- **`disease_resist`** (the field, its parsing, the hybrid mean, `to_raw`, dnd's dwarves 0.75, and its test assertions). Safe
  because nothing in the history, the outputs or the viewer read it. The owner's ruling (D25, dwarves shrug off 75% of plague
  losses) is kept as a comment on the dwarves in dnd.toml. PW-1238 should now read "re-add `disease_resist` with the plague code
  (PW-1167)".
- **`params.ECTO_COLD_C`**: referenced nowhere. The ectotherm margin lives in the trees' `limits = { cold_c = 1 }`.

Check: `base` re-run on the new code is bit-identical to the old code on dnd-s7@4360a3 and sm-s7@af2677 (every people's share,
range, population, the brakes and the event counts). `uv run pytest -m 'not slow' -n 4` and the peoples-robust slow tests: see the
commit.

## Fragile: a lot for a few lines

These stay as they are. Retuning them is not this lane's job, and the owner's bar is "not prone to exploding when nudged".

1. **`SPECIES_AREA_Z`** (one exponent in `origins`): z 0.3 -> 0 moved 28 pt, the largest of any rule, with density changed 47%.
   Who lands on the big continent decides who ends up commonest. The next step is a ±20% screen on several seeds.
2. **`ALPHA_CLOSED`** (1.4, one constant): x0.8 moved 19.6 pt with range changed 23%, 3x chance. It is the only knob where a 20%
   nudge clearly beat chance on one try. x1.2 moved 13.3 pt with range 17%.
3. **`FOUND_SITES`** (3 -> 1) and **`MEGAFAUNA_PUSH`** (0.1 -> 0) both nearly erase the dnd halflings (7.8% -> 0.2% and 0.6%), and so
   do the fit contest off (0.9%) and the small-patch fade off (0.8%). The halflings sit on a knife edge on this world. That's a
   people that is fragile, not one rule.
4. **The dwarves are bistable on dnd-s7@4360a3:** about 4% or about 16% of all people. A do-nothing nudge flips them, and so do
   war-torn land off, hold lapse off, crowding off, carry off, den off and `LEARN_GAIN` x0.8. Most of the "pt moved" on dnd-s7 for
   those rules is this flip, not the rule. Inbox draft.

Within chance on one try, so not shown fragile: `FEUD_CUT` ±20% (10.4 and 3.0 pt), `LEARN_GAIN` x0.8 (13.1 pt; x1.2 5.8 pt).

## What round 2 should do

- Run the "within chance" and "near-zero" rows on 4-6 seeds and both trees, and judge by the mean, not by one try. Late mixing,
  trade and raid food are the retirement candidates. Their effect is real but small, and retiring them changes the goldens, so
  each needs a yes.
- Find out why `GROUP_MARGIN` x667 leaves dnd-s7 bit-identical (inbox draft).
- `tools/peoples_robust.py` couldn't measure `PEOPLE_PROD = False` (it read the ladder's density map). This lane fixed that guard.
