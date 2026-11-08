# Polities round 7: polities inside the history, design and a first cut (PW-1434; lane 183)

## In plain words

- **What this round is.** Until now the states were worked out after the peoples history had finished. A state could never push a
  people out, and the history's brakes guessed at states with three stand-ins. This round puts the polities inside the history, behind
  a switch that is off by default. On each century step the history seats chiefdoms, states and dragon realms from its own numbers. They
  claim land, fall and fight under polities v0's rules. The brakes then read the real states, and the peoples on conquered land fare by
  how the winner regards them: kept, thinned or expelled.
- **The catch, found while designing.** v0's states need three things that only exist after the history: the tech tree (who knows
  writing, kingship and law, and when), the settlement ledger (the towns) and the cultures. Inside the history none of these exists yet.
  This cut stands in for the towns with the history's own head counts (the ledger's own sizing rule, in short). For the tech gates it
  uses the era's tech level for farming peoples. A test harness can also lend it a finished run's tech calendar, and the runs below do
  that, so on and off use the same gates. A proper fix needs the tech tree to run inside the history. That is the real prerequisite for
  v4, and it has a draft.
- **Cost.** The live step takes 4-6 seconds in a whole L7 run (under 0.5% of it).
- **Results** (section 6; each against the same seed with the switch off). The peoples' shares move by under 2 points: no
  explosion. The live map is thinner than the read-out's: a third to a half of the ruled land, smaller states, fewer wars. The
  largest polity is no nearer Taagepera's floor (PW-1456 still needs war that moves the frontier). Scheduled invasions do not
  reach further (PW-1450): fewer polities touch. Most conquered peoples are kept, a few are thinned or expelled. With the switch
  off the history is bit for bit the same as before.

## 1. What the history needs from polities, each step

The history steps every century through the recent pass (the last 30 kyr). Polities matter only from the first step at which some
people may seat a chiefdom (in the dnd and seven_meals runs, the last 3-5 kyr). On those steps, before the peoples move:

| the history asks | v0 stand-in (history/rule.py) | live answer (history/polity_live.py) |
|---|---|---|
| who rules each cell | nobody: no states in the history | `owner` per cell: a polity, or -1 |
| pacification G (war-torn land) | 1 / (1 + STATE_Q x tech level x the people's farm share), everywhere | 1 / (1 + STATE_Q x tech level x PACIFY[tier]) on the cells a polity rules; 1 on unruled land |
| hostile frontier F (war-torn land, raids, culls) | hostile presence on the cell and its neighbours | the same sum, but a hostile people under the same ruler is a co-subject: it counts only on unruled land or across a polity's border |
| circumscription C (in-fighting) | free good land 0, other peoples' land SOCIAL_Q, unlivable 1 | as before, and land a foreign state or empire rules bars fully (STATE_BAR) |
| the loser's peoples | (nothing) | their presence on the taken land is cut once by the winner's tolerance (section 4) |

The brakes' formulas in counter.py do not change. Only the answers do. The step is one call, `rule.begin_step(step)`, placed just before
the history reads who holds what. With the switch off it does nothing, so the history is bit-identical (section 7).

**What a step does** (the order of `polities.derive`, so the two can be compared rule by rule):
0. falls: v0's hazard (Arbesman 2011's 0.46 per century), keyed on the seat's cell and founding year;
1. seats: a cell is a town seat when its central place is big enough. Sedentary heads are each people's heads x its farm share, once
   past its forager era. A town is SHARE[2] of the cell and its ring, at the best cell of that ring. A city is SHARE[3] of two rings, at
   the best cell of those (the ledger's numbers, `settlements.CONST`, without the site factor). The cell's lead people holds it. The
   gates are v0's: chiefdoms and writing (own, or a neighbour's) for a chiefdom; kingship or law and a city for a state; a hemmed-in
   people needs less (HEMMED_X x its circumscription); a sitting seat keeps its tier down to HOLD;
2. dragon realms: one per piece of a dragon people's range, at its core, claiming settled land within DRAGON_KM;
3. claims: v0's kernel (`polities._claim`), order and reach (`polities._reach`), provinces and the wide reach of conquerors;
4. war: `polities.war_v0` itself, unchanged, with the invasions you schedule;
5. tiers: an empire is a state whose subject peoples hold SUBJECT_SHARE of its sedentary heads (peoples, not cultures: the cultures are
   made after the run).

## 2. What the history lacks, and the stand-ins

| v0 reads | made | inside the history | this cut |
|---|---|---|---|
| tech dates (meta.techtree.known) | after the run, from the populations' whole series, contacts as intervals and the goods held at the present | not available: the tech tree looks at the whole run | `CALENDAR` (a harness lends a finished run's calendar) or `PROXY_LEV`: a farming people knows a social tech once the era's tech level passes a set point (judgement) |
| towns (settlements.json) | after the run, from the stored density and farm-share frames | the history's own heads per cell, every step | the ledger's central-place rule, in short, on the live heads |
| cultures | after the run, from the demes | not available | polities are by people; cards name cultures after the run |

The era proxy is coarse. Every farming people gets its gates at the same date, so it cannot make v0's "the humans never learned
writing" draw (round 6). It is there so the switch works on its own. It is not meant for a product. The real fix is to move the tech
tree inside the history (draft `draft-techtree-inside-the-history.md`): its keyed draws (round 6) already make it a pure function of
(seed, people, tech, step). It needs only what it reads to be available step by step: the populations so far, the contacts so far,
and the goods held by then.

## 3. The after-run read-out and the invasions

- `polities.derive` is unchanged. It still reads the ledger and the tech tree after the run, so the Polities layer, the cards, the
  names and the nudge checks work as before. With the switch on, the run also writes `polities_live.json` (format
  `procgen-polities-live/1`): per step the counts, the largest state and who rules it, the conquests and each people's fate; per polity
  a card (founded, tiers, peak, what it took and how it treated the peoples there); and the maps (packed cells, as v0 stores them).
  For now there are two maps. Making the read-out the live map (derive reading `polities_live.json` and keeping only the naming and
  the culture cards) waits for the tech tree inside the history. Without that, the live map's gates are a proxy.
- **Invasions you schedule** (invasions.py) go through the same `war_v0` hook. In the history they are an input to the run
  (`polity_live.INVASIONS`, rows as `invasions.clean` reads them), and each row's log has the same fields as the read-out's. A row
  written into authored.json after a run still changes only the read-out. Making it change the history means re-running, which
  belongs with the history zoom (proposal-r2 3.3, "the sim re-runs from just before to contrive it").

## 4. Kept, thinned or expelled

**Sourced:** proposal-r2 3.3 (owner's ruling P3 B): war is mostly a change of owner. The farmers keep farming. Losses and displacement
depend on the winner's tolerance of the subject's species or culture: tolerant winners cost little, intolerant ones expel, enslave or
exterminate a share. Attitudes (3.4) are not built, so tolerance comes from the one attitude the history already has: the tree's old
enmities (`StandIns.hostility`, 0..1, from the cohabitation wishes: an "apart" wish of weight w reads w).

**Judgement (labelled as such in the code):**
- `FATE_AT = (0.25, 0.6)`: hostility under 0.25, the people is kept; under 0.6, thinned; otherwise expelled. The winner's own people
  and its kin (groups, stems) are always kept.
- `FATE_CUT`: kept 0, thinned 0.25, expelled 0.8 of its presence on the taken cells, once, at the conquest. Thinned people regrow on
  their own land (their habitat is untouched). Expelled people lose the land when their presence falls under EST. Their numbers are not
  moved elsewhere in this cut. The history's spread refills free land.
- `FATE_MAX = 0.1`: no people loses more than 10% of its heads to conquests in one step. This is the guard against a chain of
  intolerant conquests ending a people in a century.

## 5. What could explode, and the guards

| risk | why | guard |
|---|---|---|
| a people driven out of existence | repeated expulsions by one intolerant conqueror | FATE_MAX per step; v0's fall hazard ends conquerors (mean ~220 years); thinned people regrow |
| the rich get richer | a conqueror's people refills the emptied land and grows stronger | strength still needs 1.5x (WAR_ODDS), WAR_P 0.25 a century; falls; watched in the runs (largest people's share) |
| stateless land gets more war-torn | the stand-in's G pacified every farming people everywhere; live G pacifies only ruled land | this is the intended change; measured as the shares' move against the switch-off run |
| seats flicker at the size line | live heads move every step | HOLD (0.8) for a sitting seat, as v0 |
| ties on flat country seat every cell | the "best of its ring" test with equal heads | a deterministic tie-break on the cell id |
| cost blows up | many seats, many Dijkstra claims | claims are v0's numba kernel; measured below |
| order dependence | the step runs once, before the peoples move; the draws are keyed (round 6) | no draw depends on loop order |

## 6. Results

**Set-up.** World 899985 (time zoom fc5311), copied into a scratch data root, at L7. One try per run, tree seeds 7 and 10 (dnd) and 7
(seven_meals). Each run used 4 threads, one at a time. **The baseline for every comparison is the same tree and seed on today's code
with the switch off** (main at 4b1da391, a frozen copy). The switch-off runs reproduce round 6's runs: dnd s7's shares are the same
as lane 182's to 0.1 point (humans 39.0, hobgoblins 11.8, halflings 11.1), with the same thin unlettered-humans draw (58 states now,
largest 0.82 Mkm²). The switch-on runs borrowed the tech calendar of their own seed's switch-off run (`CALENDAR`), so both arms have
the same gates. Both arms carry two strong invasion rows (dnd: orcs on humans 2,000-300 years ago, hobgoblins on elves 1,500-500;
seven_meals: antelope-kin on humans 2,000-300, hobgoblins on dwarves 1,500-500). In the off arm the rows act on the read-out only. In
the on arm they act in the history.

**Cost.** The live polity step took 4.2 s (dnd s7), 3.5 s (dnd s10) and 5.7 s (seven_meals) in total over each run: under 0.5% of a
23-33 minute L7 run. At L6 (dnd s7 on 4360a3, era proxy) it took 0.8 s. The whole runs took 1,642 / 1,979 s (dnd s7 off / on),
1,236 / 1,353 s (dnd s10) and 1,468 / 1,475 s (seven_meals). The spread is machine load, not the step.

**The peoples (share of all people at the present, %; groups rolled up):**

| run | off | on | largest move |
|---|---|---|---|
| dnd s7 | humans 39.0, hobgoblins 11.8, halflings 11.1, orcs 8.9, kenku 7.1, leonin 6.6 | 39.4, 11.3, 11.2, 8.9, 6.9, 6.8 | 0.5 pt |
| dnd s10 | humans 29.8, hobgoblins 20.8, leonin 16.8, elves 7.9, kenku 6.8, orcs 5.6, halflings 4.3 | 28.6, 21.3, 18.0, 8.0, 7.1, 6.1, 2.5 | 1.8 pt (halflings) |
| seven_meals s7 | humans 38.2, half-orcs 24.4, antelope-kin 18.3, tabaxi 3.4, dragonborn 3.2 | 39.5, 23.0, 18.6, 3.4, 2.7 | 1.4 pt |

All of these moves are inside one try's chance (lane 176 measured up to 13 points for a do-nothing nudge). Nothing exploded. The
halflings' 4.3 -> 2.5 on s10 is the largest move. They are the people lane 176 found "on a knife edge" on these worlds.

**States over time** (states and empires; "largest" is the largest state or empire, Mkm²; "ruled" is all land any polity rules):

| run | | 2,000 years ago | 1,000 | 500 | now | largest over the last 3,000 years | conquests |
|---|---|---|---|---|---|---|---|
| dnd s7 | off (read-out) | 0 states | 0 | 41, 0.35, ruled 11.2 | 58, 0.82, ruled 15.0 | 0.82 | 249 |
| dnd s7 | on (live) | 0 | 0 | 25, 0.18 (hobgoblins), ruled 3.4 | 43, 0.25 (hobgoblins), ruled 5.2 | 0.25 | 14 |
| dnd s10 | off | 32, 0.63, ruled 16.0 | 91, 1.35, ruled 29.5 | 159, 1.82 | 152, 1.58, ruled 40.7 | 2.01 | 1,269 |
| dnd s10 | on | 33, 0.18 (hobgoblins), ruled 4.9 | 65, 0.20 (leonin), ruled 10.1 | 75, 0.28 | 93, 0.19 (leonin), ruled 14.7 | 0.79 | 71 |
| seven_meals | off | 188, 2.38, ruled 48.4 | 212, 1.91, ruled 60.6 | 301, 1.22 | 272, 1.98, ruled 67.7 | 2.67 (3 of 31 centuries at or over 2.3) | 4,035 |
| seven_meals | on | 162, 0.82 (antelope-kin), ruled 24.1 | 190, 0.29, ruled 28.2 | 204, 1.16 (goblins) | 218, 1.46 (half-orcs), ruled 34.6 | 2.22 (0 of 31) | 463 |

(The read-out on the on-arm's own history: dnd s10 largest 3.60, seven_meals 3.77 Mkm², 5 of 31 centuries at or over 2.3. The history
moved a little, and the read-out's largest polity moves a lot with it, which is PW-1460's spread.)

**What this says.**
- **The live polities are about a third to a half of the read-out's in ruled land, and smaller.** There are three reasons, and none
  is a bug in the rules they share. (1) The live seats count central places only. The ledger also has villages, minorities' places,
  mines and the site factor (harbours, rivers, passes), which make more and bigger towns. (2) Confederations (v0 step 1b) are not in
  this cut. On seven_meals they are a large part of the read-out's states (round 3). (3) The live strength is the polity's sedentary
  heads, against the read-out's settled people. That ratio drives war the same way, but fewer polities touch.
- **The largest polity is further from Taagepera's floor, not nearer** (PW-1456): at most 2.22 Mkm² on seven_meals against 2.67 for
  the read-out. Running war inside the history does not by itself chain conquests: the war step is the same war_v0. The conqueror's
  people does refill expelled land, but the expulsions are few (below). PW-1456's mechanism (war that moves the frontier, or chains
  within a century) is still needed, and it now has the right place to go (one call in `_step`).
- **The fates.** Over all three runs: 1,487 peoples-on-taken-land kept, 66 thinned (590,000 heads), 10 expelled (596,000 heads,
  nearly all on dnd s10). Most conquests are between peoples with no old enmity, so the farmers keep farming, as ruled (P3 B).
- **The brakes read the live polities.** With the switch on, pacification falls only on ruled land (a third to a half of the
  read-out's ruled land), so stateless land is more war-torn than under the stand-in. The shares moved by under 2 points, which says
  the brakes' land cut is small next to the peoples' own spread at these levels.

**Scheduled invasions (PW-1450): they do not reach further.** On seven_meals the antelope-kin row acted in the history: 47 conquests
of human and half-orc polities, 2,000-300 years ago, 3.1 Mkm² in all. The read-out off the same row had 620 conquests of mostly one-cell
chiefdoms, 10.8 Mkm². The hobgoblins-on-dwarves row never found a border in either arm. On dnd s10 the read-out's orc and hobgoblin
rows both happened. In the history neither did (the invaders had a state in 11 of their window's centuries and no border with the
victims). The live map has fewer, more separate polities, so the shared-border condition bites harder. Options B and C of PW-1450 (an
expedition across one unruled gap, or a war band seated for the invaders) are still the owner's call (desk card D50). Option A, "leave
it to v4", is not enough by itself.

## 7. Bit-identity with the switch off

As lane 180 did: the dnd-s7@4360a3 history (L6, one try), hashed at its end. The hash covers every line's presence `h.p`, the brakes'
`lost` shares, every event and the present summary's lines. Old code is a `git archive` of main at 4b1da391. New is this branch with
the switch off. Both ran in the same scratch data root, with 4 threads.

| run | sha256 | events |
|---|---|---|
| old code | 7ef6487c10b61adff966df4341ed4dda495781a490466c283c3160fe0c780865 | 1,464 |
| new code, switch off | the same: 7ef6487c10b61adff966df4341ed4dda495781a490466c283c3160fe0c780865 | 1,464 |
| new code, switch on (era proxy) | c2a1869a... (differs, as it should) | 1,464 |

The three L7 switch-off runs ran on the old code, so they are the baseline by construction. The goldens (`tests/test_golden.py`) cover
the sim and climate, not peoples, and are unchanged. The robust suite reads the history only, which is bit-identical with the switch
off.

## Status

**Done (this round):** the design; `planet/lineages/history/polity_live.py` (LivePolities, a StandIns subclass swapped in by
`params.POLITIES_LIVE`); the one-line step hook in `model.run` (`rule.begin_step`, a no-op for the stand-ins); `polities_live.json` written
beside the read-out when the switch is on; two tests; three L7 pairs and the L6 probe.

**Not in this cut, in the order I would take them:**
1. The tech tree inside the history (draft `draft-techtree-inside-the-history.md`). This is the real blocker for switching on by default.
2. Confederations (v0 step 1b) in the live step, and the ledger's villages and site factor in the live seats. Without them the live map
   is thinner than the read-out.
3. PW-1456's frontier war, in `_step` (the live step is where it belongs now).
4. The viewer: the Polities layer reads `polities_live.json` when it exists; the state card's kept / thinned / expelled lines (v4
   done-when 2).
5. The fates' numbers (draft `draft-conquered-peoples-tolerance.md`, needs-decision).

**Verdict on the design:** it holds. It is cheap (seconds per run), it reuses v0's rules unchanged, and it does not explode: shares
move by under 2 points, and with the switch off nothing changes. It is not yet a better map than the read-out, because its inputs (the
gates, the towns) are thinner. That is the work above, not a flaw in the seam.
