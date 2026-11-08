# Polities round 3: who rules a polity now, and confederations (PW-1451, PW-785, lane 178)

## In plain words

**A polity now names the people who rule it (PW-1451).** When another people takes a polity's capital, its name, card and legend
follow them from that century on. "Founded by" keeps the first people as history.

For example, on 3c1caf the old map showed three "cervid-folk" empires from 5.2 to 3.4 thousand years ago, but humans and half-orcs
held their capitals then. Take the first of them. Its card at 5,000 years ago now reads:
- **name:** South-east of Razukum (half-orcs);
- **its people:** the half-orcs hold its capital, since 5,200 years ago;
- **founded:** 8,200 years ago, by the cervid-kin;
- **held by** (in the details): the cervid-kin 8,200 years ago, then the humans 6,200 years ago, then the half-orcs 5,200 years ago;
- **capital:** a town of the half-orcs.

The legend's list of the biggest polities, the "taken from" and "conquests" rows, "conquered by" and the invasion read-out all
use the name the polity had at that moment. The map and the invasion read-out now agree. A polity's colour is its rulers' colour at
its peak. Names now use the people's own short name, the one the read-out uses: "(humans)", "(antelope-kin)", not "(human)" or
"(antelope-folk)".

**Why the antelope-kin had almost no states (PW-785).** The diagnosis is below. In short, it is density, not the tier rules or the
writing gate. Their towns never reach a city's size, and polities only saw towns.

**What I built: confederations.** A people with kings or law but no city may now band its villages and camps into a state, if two
things hold. First, there must be a city's worth of its own people (10,000) in its places within a state's reach. Second, a foreign
state, empire or dragon realm must have held land within that reach in the century before. This is Turchin 2009's "mirror empires":
large agrarian states push their neighbours to "band together" (`proposal.md` 2.1.2). The proposal names "dragon country" as one of
this world's frontiers. Nothing is forced. Any people on any tree qualifies the same way, and a preset whose peoples never meet a
foreign power never gets one.

**What it gives on Seven Meals (3c1caf).** The baseline is the same run on main today, with PW-1451's fix:
- **The antelope-kin** now rule 52 states and empires over the run, between 6,400 years ago and the present. One stands at the
  present: North of Razukum (antelope-kin) 16. It is an empire of 0.39 Mkm² and about 132,000 settled people, mostly human and
  tabaxi subjects. It was founded 200 years ago, on the same capital as their largest ever empire (1.21 Mkm², 1,300 years ago).
  Before this lane they had none.
- **The cervid-kin** have 47. The largest are 0.89 Mkm² empires: one 3,500 to 3,200 years ago (taken by a stronger neighbour), and
  one 1,200 to 1,100 years ago (its capital shrank). Before this lane they had none.
- **Not quite what you asked for:** two small cervid-kin confederations also stand at the present, both founded in the last
  century. So the cervid-kin empire is fallen, but the cervid-kin are not out of the game.

## Diagnosis: why the antelope-kin had so few polities

The baseline is 3c1caf (`v010-earthlike-a-seven-meals`) on main at cdff1a88, read with `planet/lineages/polities.py` as it is there.

**Tier thresholds and techs are not the cause.** The antelope-kin know every gate early:

| tech | known from |
|---|---|
| writing | 9,490 years ago |
| chiefdoms | 9,150 years ago |
| cities | 8,520 years ago |
| kingship | 8,220 years ago |
| bureaucracy | 7,380 years ago |
| law | 7,650 years ago |
| standing armies | 7,120 years ago |
| riding | 6,620 years ago |

This is earlier than the humans (kingship 8,520, law 7,380).

**The writing gate (D49) is not the cause.** They know writing themselves from 9,490 years ago.

**Density and where they live are the cause.**
- The preset gives the antelope-kin a density of 0.8 people per km². The humans have 10 and the cervid-kin 2.0. Their trait is
  "nomadic".
- At the present, the antelope-kin and their four groups number about 10.4 million (`meta.present`). Only 125,000 of them live in
  the settlement ledger's places. They hold 365 villages, the biggest of 792 people.
- A state seat needs a city of 10,000 (`tiers.city_min`), or 5,000 if fully hemmed in. No antelope-kin town ever reached a city.
  The biggest was 7,925, 7,500 years ago. At most four of their towns were ever over 5,000, at one century.
- Their biggest place shrank from 4,457 (2,500 years ago) to 792 at the present. That is under even a town's 1,000, so at the
  present they do not even have a chiefdom.
- Their places hold 0.24-0.40 million people from 9,500 to 2,500 years ago, then 0.13 million at the present. The humans' places
  hold 3-27 million.

**The one "antelope-kin" state was not theirs.** It stood 1,500 years ago (South of Shakhitrem). The humans had taken its capital
200 years before; this is PW-1451's error. The same is true of all three "cervid-kin" states and empires. So on main, with the
names fixed, **the antelope-kin and the cervid-kin never rule a state on 3c1caf**. They have 205 and 51 chiefdoms.

**The cervid-kin**, for comparison: kingship 7,650 years ago, law 6,870, writing 8,520. Their biggest town ever was 6,145. They too
have nothing over a town at the present: 560 villages, the biggest of 1,251 people.

So the bar the antelope-kin fail is the town-size bar, and that bar is set by how thinly they live. There were two ways to answer
it:
- **Thicken their towns.** That is a history change (the settlement ledger, `ladder.py`). It is v4 and lane 176's files, and it is
  not done here.
- **Let a polity count a people spread out, not just its biggest town.** This is the confederation, at the polity level in
  `polities.py`, and it is what I built.

## The rule, exactly (step 1b of `derive`)

Each century step, for each people that knows `chiefdoms` and `kingship` or `law`:
1. **Candidate seats.** Its places of any size (chief or minority kind) are tried as seats: last century's seats first, then the
   biggest. At most CONFED_TRY = 6 are tried per people per step, a cost cap (judgement).
2. **Gates on each candidate.**
   - It must pass the same writing gate as any seat: its people's writing or a neighbour's (D49 untouched).
   - A fallen capital waits its COOL_STEPS, as any seat does.
   - A place inside the reach of an earlier candidate of the same people is skipped, so one people forms no overlapping
     confederations.
3. **Reach.** The reach is a state's reach for that people (STATE_KM, law, distance techs, riding, roads, boats), measured over
   peopled land.
4. **Heads.** Its own people in its places within that reach must number at least city_min x CONFED_HEADS_X (1.0, judgement: "a
   city's people, spread out"). An incumbent needs HOLD x that, as other seats do.
5. **Frontier.** At least one cell within that reach was held last century by a state, empire or dragon realm of another people
   (CONFED_AGAINST, judgement).
6. **Its own state rules first.** If its own city-state seat is within reach, that state rules there and no confederation forms.

A confederation is a state seat from then on:
- It claims after the states with cities, because its rank is its seat's own small size. With standing armies it claims before
  dragon realms, as any state does (O4).
- It can be an empire (subjects of 20% or more), it fights and falls like any state, and war counts its settled people.
- The record keeps `confed: [[kyr ago, heads], ...]`. The card adds a row: "confederation: no city of its own: ~N of the
  antelope-kin in villages and camps within its reach banded together beside a foreign state or dragon realm".

## Numbers

All read-only from `runs/` (L7). "Off" is the same code with CONFED = False. The off runs carry PW-1451's naming, which changes no
counts.

| run | states and empires over the run | at the present: states / empires | ruled at the present | over 1 Mkm² at the present | confederations over the run |
|---|---|---|---|---|---|
| 3c1caf off | 663 | 10 / 40 | 63.7 Mkm² | 25 | 0 |
| 3c1caf on | 1,223 | 13 / 53 | 75.3 Mkm² | 30 | 577 |
| a2b637 off (D&D) | 1,642 | 148 / 128 | 76.4 Mkm² | 14 | 0 |
| a2b637 on | 1,724 | 152 / 137 | 78.7 Mkm² | 14 | 85 |
| b4d502 off (D&D) | 164 | 9 / 10 | 26.8 Mkm² | 7 | 0 |
| b4d502 on | 319 | 14 / 20 | 38.4 Mkm² | 14 | 163 |

**What these show:**
- **The largest polity** does not move on any run: 2.86 Mkm² on 3c1caf, 1.80 on a2b637, and 1.95 to 1.98 on b4d502.
- **Lifetimes:** the median state still lasts 200 years from founding to fall on 3c1caf and a2b637, and 300 years on b4d502. At
  half its peak size or more, the median is 100 years on all three. Taagepera 1997's median is 130 years (round 2).
- **Confederations are short:** most hold one or two centuries. They form again and again in the same country. Steppe
  confederations re-forming under new leaders is a known pattern, but this is my judgement, not a sourced count.
- **Who forms them on D&D runs:**
  - a2b637: elves, drow, leonin, goliaths, hobgoblins and others, all within the last 900 years (writing comes late there).
  - b4d502: mostly humans in country with no city of theirs.
  - Neither run has antelope-kin or cervid-kin.
- **The cost:** more land is ruled, and more polities pass 1 Mkm². That makes PW-1449 ("about ten times history's" big polities)
  a little worse: 25 to 30 on 3c1caf, 7 to 14 on b4d502. Turchin 2009 puts over 90% of mega-empires in or next to the arid belt,
  which is where herder confederations sit. So these big polities are in character, but our count was already too high (PW-1449
  owns the reach).

**Which frontier counts (CONFED_AGAINST).** A decision draft is filed. If only states and empires count, with no dragon realms:

| | 3c1caf | b4d502 |
|---|---|---|
| states and empires over the run | 1,021 | 255 |
| ruled at the present | 67.1 Mkm² | 32.0 Mkm² |
| over 1 Mkm² at the present | 26 | 9 |
| antelope-kin | 24 empires, 5,700 to 1,300 years ago, none at the present (largest 0.63 Mkm²) | - |
| cervid-kin | 19, none at the present | - |

So the dragon realms are what give the antelope-kin a present-day empire on 3c1caf. Today the most populous antelope-kin country
holds 28,000-42,000 settled people within reach, and dragon realms border it. No state does.

## Robust when nudged (3c1caf, CONFED_HEADS_X ±10%)

| CONFED_HEADS_X | states and empires over the run | at the present | ruled at the present | antelope-kin (records, largest, standing now) | cervid-kin (records, largest, standing now) |
|---|---|---|---|---|---|
| 0.9 | 1,242 | 13 / 54 | 75.9 Mkm² | 52, 1.21 Mkm², 1 | 47, 0.89 Mkm², 2 |
| 1.0 | 1,223 | 13 / 53 | 75.3 Mkm² | 52, 1.21 Mkm², 1 | 47, 0.89 Mkm², 2 |
| 1.1 | 1,202 | 13 / 52 | 74.4 Mkm² | 51, 1.21 Mkm², 1 | 49, 0.89 Mkm², 2 |

- Every count moves by under 2%.
- The present-day antelope-kin empire stands in all three.
- The antelope-kin hold a confederation in 47 of the 64 centuries since 6,400 years ago. So one standing at the present is not a
  single lucky draw.

## What is not here

- **No forcing and no authored anchor.** If a run's antelope-kin never border a foreign power, or never gather 10,000 in their
  places, they get no empire. The back-fill anchor (`[[event]] kind = "polity"`, proposal 2.1.2) is still possible later, but it
  was not needed on 3c1caf.
- **The ledger still undercounts thinly spread peoples.** About 1.2% of the antelope-kin live in its places at the present.
  Polities read only the ledger, so a confederation's strength in war is its settled people, not its riders. War between
  confederations and states could weigh the whole people with polities inside the history (v4).
- **No new history.** history/, spread.py and ladder.py are untouched (lane 176).

## Files

- `planet/lineages/polities.py`:
  - `_confederations` (step 1b) and the constants CONFED, CONFED_HEADS_X, CONFED_TRY, CONFED_AGAINST;
  - `name_at`, `_at`, `_short`, and the records' `peoples`, `names`, `founded_by` and `confed`;
  - VERSION 4, so cached docs are remade.
- `planet/lineages/invasions.py`: the read-out names each side as it was called at the time.
- `viewer/globe/polities.js`: `nameAt`; the "its people", "held by" and "confederation" rows; "founded ... by"; the legend line.
- `tests/test_polities.py`: naming by the ruling people, and the confederation's gates.
