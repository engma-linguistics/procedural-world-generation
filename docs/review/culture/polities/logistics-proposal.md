# Logistics: how far a polity can campaign and how long it can besiege (proposal, lane 279)

Written proposal only. No model code was changed. Daniel's ask (2026-11-10): early small kingdoms invade each other over short
distances; as logistics capacity grows they reach further; over-extended powers get nipped at on their edges while a power that
settles down stays compact and strong; and the magic side of the tech tree needs something for food and water, which would
change campaigning and sieging a lot.

## 1. In plain words

Today a polity's war reach comes from a fixed budget (a state's 150 foot-km, up to 250, or an expedition's ~1,000 km, x2 for
herders) plus a few multipliers for riding, roads and sails. Nothing in it says how an army eats or drinks, and a war is a single
per-century coin flip with no siege in it.

The proposal gives each polity one number, its **logistics** (LOG), made from what its ruling people know: ways to keep food
(drying, salting, granaries), to carry it (pack animals, carts, ships), to keep count of it (writing, taxes, bureaucracy,
depots), and, on the fantasy side, to make or conjure it (purify water, preserve food by charm, conjure provisions, pocket
storage, divine provisioning). LOG does two jobs from the same number: it sets **how far an expedition can go**, and **how many days
an army can sit in front of a wall** against how many days the town inside can hold out.

Early on LOG is low: kingdoms raid the neighbour a few hundred km away and give up after a short siege. As LOG grows they march
further and sit longer. Past a point, the far provinces are thin (strength falls with supply distance from the capital), so
neighbours bite the edges. A state that stays inside its supply radius keeps full strength at every border, which is the "settling
down" Daniel described. Magic provisioning is just more LOG with a ceiling set by how many casters a polity has (decision 2).
Reach stays one budget: LOG scales the existing foot-km, it does not add a second ruler beside it.

## 2. Sources

What I could verify (search 2026-11-10, secondary summaries only; I could not read the books, so no page numbers or exact figures
are quoted as facts):

- **Engels, D. W. 1978.** *Alexander the Great and the Logistics of the Macedonian Army.* University of California Press.
  Summaries and reviews agree on the shape: pack animals eat much of what they carry, so they are the binding constraint (one
  summary says they could operate roughly 8-10 days without forage); a land army can itself carry only about a week to ten days of
  provisions, less in desert where water must be carried; an army lives off rivers, the sea and the towns it can reach. Exact
  figures (grain per soldier and per animal, days carried, km per day) were reported inconsistently by the sources I reached.
  **Unverified: the numbers below are judgement anchored on that shape; check them against the book before tuning.**
- **van Creveld, M. 1977.** *Supplying War: Logistics from Wallenstein to Patton.* Cambridge University Press (2nd ed. 2004). Verified
  thesis: before railways armies could mostly be fed only while moving, foraging and pillaging as they went; they needed continuous
  supply lines only if stopped and the local food and fodder ran out; horse-powered armies stripped country and pushed forward
  rather than back. This is the source for "sieges are where supply bites": a stationary force eats out its surroundings. Early
  modern scope, so it is a mechanism, not a calibration for the ancient world.
- **Roth, J. P. 1999.** *The Logistics of the Roman Army at War (264 BC - AD 235).* Brill. Named from memory as the standard Roman
  study (Roman reach rested on organised requisition, depots, river and sea transport, roads); **not verified in this search.**
- **Erdkamp, P. 1998.** *Hunger and the Sword: Warfare and Food Supply in Roman Republican Wars (264-30 BC).* Gieben. Named from
  memory as the companion study; **not verified here.**
- Already in the repo and reused, not new: ORBIS (Scheidel, Meeks and Weiland 2012) cost per km by mode in `trade_flow.py` (PACK = 1),
  and Spencer 2010 / Taagepera 1997 for administrative reach in `polities.py`.

Judgement, not sourced: every multiplier in section 3, the 10-day base, the siege-day scale and the magic factors.

## 3. Mechanism

### 3.1 One budget, two readings

Keep the existing currency: **foot-km** (km on foot over flat ground). It is read twice today:

- *Rule reach* `polities._reach()`: STATE_KM x LAW_X x DISTANCE_X, capped at STATE_MAX_KM unless conquest or confederation.
- *Campaign reach* `invasions.campaign_budget()`: max(CAMPAIGN_KM, EXTENT_X x radius) x mobility.

Proposal: add a dimensionless **LOG** (about 0.4 for a bare chiefdom, 1.0 for an iron-age kingdom, 2 to 3 for a late medieval state
with ships, roads and depots, more with magic) and make it the single place the supply techs act:

- Campaign reach = campaign_budget x LOG / LOG_REF, where LOG_REF is the LOG of the tech level D56 was set against (the "from that
  part of the continent" ~1,000 km). D56's number is preserved there; earlier states fall below it.
- Rule reach is **unchanged** in the first steps, so goldens and the history stay byte-stable. `DISTANCE_TECHS` (bureaucracy,
  postal_relay, milestones_waystations) keep doubling rule reach; they also count once in LOG's administration group, so that is the
  same techs read for supply, not a second budget. Riding, roads and sails keep their per-km cost discounts (RIDE_X, ROAD_X, SAIL_X)
  and LOG does **not** count them again. This avoids a double count (see PW-1457 on touchy multipliers).

### 3.2 LOG from three groups

LOG = BASE x CARRY x STORE x ADMIN, each group the product of its techs' factors, each group capped so no one runs away. BASE is a
bare chiefdom's supply, about 10 days of carried food (Engels reviews: a week to ten days), scaled so LOG = 1 sits at LOG_REF.

| Tech (id) | Group | Gate (needs) | Tier | Domains | Adds (judgement) |
|---|---|---|---|---|---|
| smoking_drying (exists) | STORE | cooking | stone | food | x1.15 |
| salting (exists) | STORE | | stone/bronze | food | x1.15 |
| storage, raised_granary (exist) | STORE | containers | stone | food | x1.15 (depots at home) |
| fermentation, cellaring (exist) | STORE | | | food | x1.05 each |
| **waterskins** (new; containers already exist, this is the carried-water node) | CARRY | containers | stone | food, move | x1.1; arid ground only (water is the binding term in desert) |
| pack_animals (exists; `has_pack`) | CARRY | herding | bronze | move, trade | x1.3 (animals eat part of their own load, so far below ORBIS's cost ratio) |
| wheel + ox_traction (exist) | CARRY | | bronze | move | x1.2 on flat ground, 1.0 in hills |
| **field_rations** (hardtack, pemmican, travel bread; new) | STORE | smoking_drying, grinding | bronze | food, war | x1.2 |
| sails, plank_boats, harbours (exist) | none | | | | SAIL_X already makes the sea cheap; instead **coastal supply**: no supply-distance loss along a held coast or river |
| taxation, census, writing (exist) | ADMIN | | | trade, war | x1.1 each (requisition needs lists) |
| bureaucracy, postal_relay, milestones_waystations, caravanserais (exist) | ADMIN | | | | x1.2 each; the DISTANCE_TECHS, counted once here |
| **army_depots** (magazines on the route; new) | ADMIN | taxation, storage, roads | classical | war, trade | x1.3 |

Fantasy side (mode "fantasy", track "arcane"; generic names, no rulebook text):

| New arcane tech | Gate (needs) | Tier | Domains | Group | Adds |
|---|---|---|---|---|---|
| **water_purifying** (clean or draw drinking water by working) | druidcraft, boiling_pots | stone/bronze, after druidcraft (30 kyr) and pots | food, ritual | CARRY | x1.2 on water-limited ground, 1.1 elsewhere; also a camp-disease hook |
| **preservation_charm** (food keeps for weeks) | druidcraft or runes, smoking_drying | bronze | food, ritual | STORE | x1.3, stacks with mundane keeping |
| **conjured_provisions** (small daily food and water by casting) | arcane_schools | medieval, where arcane_schools sits (~1.5 kyr) | food, know | CARRY, cast-limited | up to x1.8 |
| **pocket_storage** (extradimensional pack or hold) | enchanting | renaissance (~1.2 kyr) | craft, food, move | CARRY, cast-limited | up to x1.5 |
| **divine_provisioning** (clerics feed an army) | divine_magic (gods-gated as it is) | bronze, low rate | ritual, food | STORE, cast-limited | up to x1.5 |
| beast_bond (exists) | | | food, move | CARRY | x1.1 (hardier pack beasts) |

Gates keep the tree's shape: the early ones hang off druidcraft, the strong ones off the schools and the enchanting node, the divine
one off divine_magic so it exists only when gods do. Tiers should follow the gate's existing `earliest_kyr`.

### 3.3 Magic is bounded by who can cast it

Mundane factors apply to the whole army. The cast-limited ones scale with `casters`: the trained share of the ruling people (set by
arcane_schools and the kind's magic trait) against army size (settled people x a levy fraction). Each cast-limited factor is
`1 + (F - 1) x min(1, casters / casters_needed)`. A small polity with one college feeds a small elite column; a large one with
many colleges and clerics can feed a host. This is decision 2; the lean is a ceiling so magic never beats the mundane stack by
more than ~1.5x.

### 3.4 Supply distance and siege

- **Supply distance** d_s: foot-km from the army's base (own capital, nearest depot, or held port) along cheapest cost, using the
  Dijkstra `invasions.expedition` already runs. Strength at a front falls with d_s:
  `strength(d_s) = strength x exp(-d_s / (LOG x L0))`, L0 a judgement scale in foot-km (start near 400). A held river or coast
  resets d_s (Engels's emphasis on sea and rivers). Mobile and foraging peoples use a flatter curve (van Creveld: moving armies
  live off the country), tied to `invasions.mobility`.
- **Siege.** A walled town (fortifications, castle) holds D_def days: its stores (the defender's STORE group, times its people over
  its garrison). The attacker lasts D_att = D0 x LOG x falloff(d_s), shorter the longer it sits unless fed by sea or river (van
  Creveld: a stationary army eats out its district). If D_att < D_def the attacker withdraws and that front's war for the century
  fails; otherwise the town falls or is sacked (hook into the settlement sack/raze/walled model, PW-1108). Unwalled: no siege.
  Magic cuts both ways: purify and preserve lengthen the defender, conjure and pocket lengthen the attacker, so it is not a one-way
  boost. Siege day counts are new output; today `war_v0` is one coin flip per century.

### 3.5 The pattern, step by step

1. **Early (LOG 0.4-0.7).** Supply radius of a few hundred foot-km. A neighbour 100-250 km away is raidable, one 600 km away is not.
   The expedition search already reports "more than N km"; the same hook gives the honest reason "out of supply". Any stone wall
   beats a short-supplied army, so raids loot open towns, as now.
2. **Growing LOG.** Granaries, pack animals, carts, then depots double radius and siege endurance. Campaigns reach 500-1,000 km
   (D56 at iron-age tech). Walled towns now fall to long sieges.
3. **Over-extension.** A state that conquered a province 800 km out holds it at strength(d_s) with d_s large. A neighbour whose border
   lies near its own capital outguns the thin edge: in `war_v0` a front cell is compared at local strength, so a strong neighbour
   takes the weak edge rather than the whole polity (partial conquest, decision 4). Far conquered provinces also free themselves
   more readily: the Falls step (FALL_PER_CENTURY) gets a term rising with d_s / reach.
4. **Settling down.** A polity inside its LOG radius has full strength at every border and no thin edge, so it keeps its cells
   even against a larger neighbour. Nothing is scripted; it falls out of the falloff.

## 4. What to measure

All on the same commit and seeds, flag on against off (a `LOGISTICS_ON` switch; off must be byte-identical to main), over at least
five re-rolled draws (a single-world swap is not proof):

1. **Campaign distance by era.** For every expedition, war and invasion row: median and 90th percentile of foot-km and km, by
   century bucket and tech tier. Expect it to rise with era, early median under ~300 km, iron-age 90th percentile near D56's
   1,000 km, and the rows that happen on main (15/30 on a2b637) still happening at iron age.
2. **Siege lengths.** Days of D_def and D_att by wall tier; share of attacks that are sieges and share that succeed, by era, magic
   on and off. Expect sieges rare and failing early, success rising with LOG.
3. **Over-extension.** Per state, its largest d_s / LOG against the share of its cells lost to neighbours within a century. A
   positive relation is the goal; a flat one means the falloff is too weak.
4. **Settle-down effect.** Lifetime and land held of polities with low against high max d_s / LOG at equal size.
5. **Magic against mundane.** Share of campaigns where a cast-limited factor changed the outcome; LOG with and without arcane techs
   on a2b637; zero change on a no-magic tree.
6. **Regression guards.** The giants check (PW-1449: largest polity near Taagepera's floor, 1.40 Mkm2 on 3c1caf) moves by no more than
   noise; rule reach byte-stable; `tests/test_golden.py` unchanged until wiring is on.

The harness is a short script beside `invasions_reach_score.py` that reads polities and invasion rows.

## 5. Decisions for Daniel

1. **How strong is magical provisioning against the mundane stack?** A: same scale as mundane (each arcane tech about x1.2-1.5).
   B: strong (conjure and pocket let an army ignore distance for a while). C: modest ceiling (arcane adds at most ~1.5x on top of
   mundane). Lean C: wizards matter and fantasy worlds look different, but the over-extension pattern you want survives.
2. **Is magic logistics limited by caster numbers?** A: no, a flat factor for any polity that knows the tech. B: yes, scaled by
   trained casters against army size. C: yes for the strong ones (conjured_provisions, pocket_storage, divine_provisioning), flat
   for water purifying and preservation charms. Lean C: cheap spells are everyday; feeding a host needs colleges and clerics.
3. **What does LOG = 1 mean?** A: D56's ~1,000 km at iron-age tech, so early states fall below and later ones above. B: the
   ceiling for everyone, so every era's campaigns shrink. Lean A. Changes how many authored invasion rows reach.
4. **Edge bites or all-or-nothing war?** Today a winner takes the whole neighbour. A: add partial conquest, so a strong neighbour
   takes only the cells where it is locally stronger. B: keep all-or-nothing; over-extension then shows only as faster falls and
   freed provinces. Lean A, since your ask rests on it, but it changes every history and is the biggest step.

## 6. Build plan

Lane 278 is finishing states inside the history (live polities). **both** = works on the after-the-run read-out and carries to the
live history; **live** = needs 278.

1. **Tech nodes (both).** Add waterskins, field_rations, army_depots and the five arcane nodes to
   `planet/lineages/samples/techtree.toml`; tech tree warns on bad ids; `uv run pytest -q`; rebuild showcase trees. Effort s. No
   output changes.
2. **`logistics.py` (both).** Pure `log_of(knows, ago, casters)` returning LOG and its groups, unit-tested on three tech sets (bare
   chiefdom, iron-age kingdom, medieval with arcane). Effort s.
3. **Campaign reach (both).** `campaign_budget` takes LOG / LOG_REF; the expedition "why not" says "out of supply"; flag off by
   default. Effort s-m. Measures 1 and 6.
4. **Supply-distance falloff (both for the read-out; live for the history).** Front-cell strength in `war_v0`; nomad curve.
   Effort m. Measures 3 and 4.
5. **Siege model (both).** D_def, D_att, the sack/raze hook (PW-1108); siege days in the polity doc. Effort m. Measure 2.
6. **Partial conquest (decision 4 A; live).** Edge bites in war and a distance term in falls. Effort l. Matters most in the history,
   so gated on 278.
7. **Live wiring (live).** `history/polity_live.py` reads the same LOG (the PW-1479 pattern). Effort m, after 278.
8. **Measure and tune (both).** The script in section 4, five re-rolled draws, one sweep. Effort m.

Steps 1-3 and 5 can start now; 6 and 7 wait for 278.
