# Writing round 2: four ways for courts and kin to take writing sooner (D52, PW-1461; lane 186)

## In plain words

**Your question.** You asked whether there is a precedent for "ignore the villages, the king in the city over there will love
this". Yes. On Earth's Bronze-Age edge, courts took writing over the heads of their countryside:
- The Hittite kings probably brought scribes from northern Syria to Hattusa.
- The Yamato court in Japan learned to write from Korean and Chinese officials.
- In both places, and in Mycenaean Greece and among the Maya, writing then stayed in the palace for centuries.
- The carriers were merchants and scribes travelling at 20 to 30 km a day. A front of know-how moves at about 1 km a year.

On peoples: a shared language does make sharing easier, but as a bias, not a wall. Borrowing between strangers is common, and no
source puts a number on how much faster sharing runs inside a group. Section 1 has the sources.

**What I built.** One switch in the tech tree, `contact_arms`. It is off by default, and off is bit for bit today's tree: the whole
tech-tree doc is identical to main's on all three runs. It has four letters, each a mechanism:
- **B, town network.** A tech that needs towns crosses the width of the taker's towns, not its whole land.
- **C, trade contact.** Two peoples who both have towns pass urban techs at 2.2 km a year instead of 1. Jordan et al. 2016 measured
  1.2 to 3.3 km a year for pottery along favoured corridors.
- **E, elite uptake.** A people with chiefs, kings or towns takes writing (and the alphabet and written law) once the front reaches
  its nearest town, not its middle.
- **K, kin share.** A people does not hold back from its own kin: its parent, daughters and sister lines, split within the last
  15,000 years.

**What happened.** I measured each arm on the three showcase runs, over six draws of the tree's luck per run (the run's own and
five more), with nothing written into runs/. The baseline is main, switch off.
- **Off:** half the settled people know writing **865 years** after the first invention (median; 250 to 1,540).
- **B:** 425 years. **C:** 560. **E:** 270. **K:** 850, so K barely moves anything.
- Every arm keeps the half-way time inside the 100 to 900 years Earth's near neighbours took. Only "off" and K sit at the ~800
  years round 1 inferred for Earth's urban people, and that figure is itself a guess (section 4).
- The waits shrink. With B, C or E the median wait at a writing border falls from about 740 years to 310 to 430,
  and the slow big peoples' wait from about 400 years to 140 to 280. The
  dwarves of a2b637 wait a median 100 years under E against 620 now; in one draw in six they never write today.
- States come sooner where writing does. 4,000 years ago, 07c755 has 100 to 113 states and empires under B, C or E, against 62 now;
  0141d1 has 46 to 50 against 12. On a2b637 the first states come 600 to 900 years earlier. The present hardly changes.
- **Stable when nudged:** a ±20% nudge to B's or E's width moves the half-way time by 0 years in the median draw. C's speed moves
  it by about 70 to 100 years: C is half a dial.

**What is on by default: nothing.** No arm both keeps the half-way time near Earth's ~800 years and is clean:
- **E** is the history's answer to your question. It is a mechanism, it adds no number, and it holds when nudged. But it cuts the
  half-way time to about 270 years, and it needs to know where the towns are before the tree is built, which new runs cannot do
  yet (one draft).
- **C** is the gentlest speed-up (560 years) and works in new runs today. But it is a speed borrowed from pottery, and its number
  moves the result.
- **B** sits between them (425 years) and needs the towns, as E does.
- **K** does almost nothing. In these trees a people already shares everything with its own groups, and the big peoples have no
  recent kin. The dwarves split from the hominid stem 500,000 years ago.

**My lean: E,** if you accept a half-way time near Earth's near neighbours (Susa took 200 to 300 years, Egypt 0 to 200) rather than
round 1's 800. Otherwise C, at 2.2 km a year. This is a change to how fast the tech tree spreads, so it is your call.

## 1. History: did kings take writing over their villages' heads?

Found by web search in this lane (a helper agent read the pages; nothing is cited from memory). Strength is marked per claim.

**Yes, courts took writing across land, and it stayed in the palace for centuries.**
- **Hittites (moderate).** Hittite cuneiform looks like the hand of 17th-century BCE Alalakh (northern Syria), and the Hittite kings
  may have brought "Syrian scribes to transfer their activities to Hattusa" soon after 1650 BCE (Britannica, *Anatolian languages:
  early research*, https://www.britannica.com/topic/Anatolian-languages/Early-research). Tekin also names northern Syria the most
  likely source (https://dergipark.org.tr/en/download/article-file/782413). Popova finds the Old Babylonian texts do not bridge
  Alalakh VII and Hittite writing (https://tronsky.iling.spb.ru/en/xix-ovpopova.html?en). The Old Assyrian merchants' tablets at
  Kanesh came first, but I found no reliable source that they were the route. So: a court imported scribes, people and all.
  How long the Anatolian countryside stayed unlettered was not found (thin).
- **Mycenaean Linear B (moderate, from secondary pages).** Use was "mostly confined to administrative contexts, mainly at Mycenaean
  palatial sites". Handwriting studies count about 45 scribes at Pylos and 66 at Knossos. The script vanished with the palaces.
  (https://wikiwand.com/en/Linear_B)
- **Japan (moderate on the outline, thin on dates).** The first documents were written by Korean and Chinese officials at the Yamato
  court; elites took writing up in the 5th century CE and wider reading began only in the 7th
  (https://samurai-archives.com/wiki/Writing; the Wani story is semi-legendary, https://wikiwand.com/en/Wani_(scholar)).
- **Maya (moderate, popular source).** Scribes "trained and worked within the royal court"; literacy was "almost certainly limited"
  (https://www.worldhistory.org/article/655/maya-writing/).
- Not found in this pass: Ebla, proto-Elamite, Egypt, Ugarit, Meroitic, and counter-examples such as runes or ogham (a script that
  spread outside any court).

**How fast does a court-to-court route run?** Assur to Kanesh is about 1,100 km (the STRADA project,
https://cordis.europa.eu/project/id/101263289), and a donkey caravan took roughly 6 to 8 weeks (a merchant's account tablet,
1888-1876 BCE, via a secondary site, https://www.ancient-history-sites.com/?p=149038; thin on the time). That is travel at 20-30 km a
day: far faster than any front. Land diffusion of a technology is slower by three orders of magnitude: pottery's fronts ran at
0.32-0.80 km a year, and a constant-speed front explains only 9-19% of the variance (Silva & Steele 2014, *Radiocarbon* 56(2):723-732,
https://eprints.bournemouth.ac.uk/32039/; strong).

**Re-checking Jordan et al. 2016** (*Antiquity* 90(351):590-603, doi 10.15184/aqy.2016.68). The abstract gives no speeds. The
supplement (S0003598X16000685sup001.pdf at cambridge.org) gives "the speed along the Mediterranean corridor ranges from 1.46 to 5.51
km/yr" for the North-Africa-derived wave, with a table average near 3.3 (the table was garbled; moderate), and an off-corridor speed
"consistent with the 0.5 km/yr value" of Davison et al. 2006. Lane 70 had read the accepted manuscript's Table 1
(docs/references/techtree/README.md): 1.2 km a year in favoured habitat against 0.2 elsewhere (Asian zone), 3.3 against 0.5 (African
zone). So round 1's "1.2-3.3 km a year" stands, and the supplement's corridor fits run a little higher (1.5-5.5). All of it is
pottery among foragers, not writing among towns: borrowed for C as the nearest measured "favoured corridor" speed.

**Do techs move faster within a people than between strangers? A bias, not a wall (moderate).**
- Shennan, Crema & Kerig 2015 (*Evolution and Human Behavior*): a shared language "eases cultural interaction, and favours a
  homophilic positive feedback process", making clusters with sharp edges
  (https://discovery.ucl.ac.uk/id/eprint/1450105/2/1-s2.0-S1090513814001251-main.pdf; read as a snippet).
- Rogers, *Diffusion of Innovations*: likeness eases communication, but "the very nature of diffusion demands that at least some
  degree of heterophily be present" (https://web.stanford.edu/class/symbsys205/eisenberg-rogers.html; secondary summary).
- Against: Turkmen and Iranian weaving borrowed across groups (Tehrani, Collard & Shennan 2010,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC2677599); Central African foragers share music words widely across groups
  (https://carta.anthropogeny.org/node/329987); Neolithic Mediterranean ornaments span the whole farmer network while pottery
  decoration marks group borders (Rigaud et al. 2018).
- No source gave a number for "how much faster within a group". So a kin bonus is defensible only as mild and trait-dependent.

**The answer to Daniel's question.** Yes: "ignore the villages, the king in the city over there will love this" is how writing
moved on Earth's Bronze-Age edge. Courts brought scribes or script across land (Hattusa from Syria, Yamato from Korea and China), and
writing then stayed in the palace for centuries (Linear B, the Maya, early Japan). The carriers moved at travel speed, not at a
front's. Kin sharing is real but soft, and borrowing between strangers is common.

## 2. The arms

`planet/lineages/techtree.py` (ARM_DEFAULTS and `build`'s `towns` and `arms`). The switch is `contact_arms`, a string of letters,
set in the tree's `[defaults]` or passed to `build`/`rebuild`. With it empty (the default), the code takes none of the new branches.
`same.py` (below) compared the full tech-tree doc of main's `techtree.py` with this lane's, off and with `arms=""`, on 07c755,
a2b637 and 0141d1: identical, byte for byte.

| arm | what changes | which techs | new number |
|---|---|---|---|
| B, town network | the front's width is sqrt(the taker's town cells x cell area), capped at its range's width | needs towns or cities | none |
| C, trade contact | the front runs at `arm_trade_km_yr` (2.2) when giver and taker both know towns | needs towns or cities | 2.2 km/yr |
| E, elite uptake | a taker knowing chiefdoms, kingship or towns, with town cells: the width is its town spacing, sqrt(range / town cells) | writing, alphabet, law (`ARM_ADMIN`, or `admin = true`) | none |
| K, kin share | between kin, the taker's insularity does not apply (openness 1) | all that pass by contact | `arm_kin_kyr` 15 |

- **Kin**, for K (`techtree.kin_pairs`): a line and its parent (a split, a hybrid's parents, a group's people), and two daughters of one
  parent, when the daughter began within `arm_kin_kyr`. "Language family" depth is the judgement behind 15 kyr. Older splits, such
  as the dwarves from the hominid stem 500,000 years ago, are strangers. Cultures and languages are made after the tree, so they
  cannot be used here.
- **The draws stay keyed** as lane 182 made them: the pair's front is still `-log1p(-keyed(seed, "front", giver, taker))`. Only the
  rate it is divided by changes. For a tech an arm touches, the front's arrival is recomputed each step and never moves later. A
  front that gains a road speeds up from where it is.
- **The town footprint** for B and E: `techspread.town_footprint(run)` counts the cells where each people holds a place of town size,
  at every ledger century. `techtree.rebuild` reads it when B or E is on. `output.save` builds the tree before the ledger, so a new
  run has no footprint: B and E then warn and do nothing. The draft `draft-techtree-town-arms-need-the-ledger-first.md` covers that
  case.
- **B and E differ by density.** B crosses the summed width of the towns, so few towns cross fast. E crosses the spacing between
  them, so many towns cross fast. The humans of 07c755 have about 2,700 town cells of 3,100 km2 each. B's width is then about
  2,900 km against 7,000 km for their whole land; E's is about 140 km.

## 3. The measures

**Set-up.**
- Each of 07c755, a2b637 and 0141d1 is rebuilt in memory with `techtree.rebuild(run, T, arms, seed)`. The draws are the run's own
  tree seed and 101 to 105, so six per arm per run. (For "off", one draw per run was lost to a job-file slip, so it has five.)
- The measures are lane 184's `techspread.derive(run, "writing", tt)`:
  - **half** and **nine in ten**: the years from the first invention to half, and to nine-tenths, of the settled people.
  - **wait**: the median, over peoples that took writing by contact, of (the earlier of ready and in touch with a writer) minus
    the date they took it.
  - **tail**: the same wait for the slow people of round 1. That is the humans on 07c755 and 0141d1 (36% and 38% of the settled
    people) and the dwarves on a2b637 (24%). It is negative when the people found writing before touching a writer.
- Values are the median over draws, with the range in brackets.
- The tech tree's time steps near 4,000 to 5,000 years ago are about 100 to 150 years wide, so differences under ~150 years are one
  step.

**All three runs, 15 to 18 draws:**

| arm | half | nine in ten | wait at the border | tail people's wait |
|---|---|---|---|---|
| **off (main)** | **865** (252-1,540) | 1,403 (752-2,865), 2 draws never | 741 (527-1,067) | 395 (-196-1,867), 2 never |
| B | 425 (153-740) | 663 (353-1,265) | 313 (218-518) | 248 (-196-842) |
| C | 560 (153-1,040) | 836 (452-1,365), 1 never | 428 (320-726) | 283 (-196-986) |
| E | 273 (118-740) | 444 (218-940) | 357 (151-440) | 144 (-196-527) |
| K | 850 (252-1,540) | 1,295 (752-2,865), 2 never | 723 (527-1,284) | 364 (-196-1,614), 2 never |
| B+C | 318 (153-740) | 460 (203-940) | 208 (151-351) | 181 (-196-564) |
| E+K | 255 (118-740) | 444 (218-940) | 345 (137-440) | 144 (-196-527) |
| **Earth** (round 1) | ~800 for urban people (an inference); near neighbours 100-900 | over 3,000 to most of the Old World's states | — | the Bronze-Age edge: 1,400-2,000 after Uruk |

**Per run, half / tail people's wait (years):**

| arm | 07c755 | a2b637 | 0141d1 |
|---|---|---|---|
| off | 825 / 0 (humans) | 890 / 618, 1 never (dwarves) | 1,140 / 409, 1 never (humans) |
| B | 444 / 109 | 366 / 293 | 414 / 269 |
| C | 508 / 109 | 540 / 390 | 671 / 400 |
| E | 380 / 109 | 208 / 103 | 333 / 154 |
| K | 658 / 109 | 865 / 506, 1 never | 1,225 / 663, 1 never |

**The two slow peoples of round 1, on the runs' own draw.**
- **Humans of 07c755.** In the stored tree they waited 2,100 years. With today's keyed tree (lane 182) they wait 320 years, under
  every arm: they take writing from their own seafarer group, which got it first. So that tail was a draw, not the rule.
- **Dwarves of a2b637.** In the stored tree they never wrote. With today's tree they take writing 2,255 years ago, 860 years after
  first touching a writer. They take it 2,797 years ago under B and E (318 years), 2,603 under C (512), and 2,255 under K (no
  change, since they have no kin).

**D49's states, from polities derived in memory.** This is the runs' own draw only. Each arm's tree was put into a scratch copy of
the run, and `polities.derive` was run with the authored invasions. States and empires are counted together.

| run | arm | first state (years ago) | states + empires 4,000 years ago | now (chiefdoms / states / empires / dragon realms) |
|---|---|---|---|---|
| 07c755 | off | 4,300 | 62 | 2,810 / 57 / 210 / 17 |
| | B | 4,400 | 109 | 2,791 / 54 / 214 / 17 |
| | C | 4,400 | 113 | 2,809 / 57 / 211 / 17 |
| | E | 4,400 | 101 | 2,777 / 56 / 217 / 17 |
| | K | 4,300 | 62 | as off |
| a2b637 | off | 2,000 | 0 (first writing 3,115) | 2,175 / 142 / 153 / 19 |
| | B | 2,900 | 0 | 1,885 / 133 / 148 / 20 |
| | C | 2,600 | 0 | 1,951 / 133 / 146 / 20 |
| | E | 2,600 | 0 | 1,966 / 135 / 145 / 20 |
| | K | 2,000 | 0 | as off |
| 0141d1 | off | 4,600 | 12 | 3,379 / 76 / 156 / 11 |
| | B | 4,600 | 47 | 3,161 / 76 / 156 / 10 |
| | C | 4,600 | 50 | 3,141 / 72 / 154 / 11 |
| | E | 4,600 | 46 | 3,380 / 73 / 156 / 11 |
| | K | 4,600 | 12 | 3,198 / 77 / 155 / 11 |

What D49 does under the arms:
- The first state anywhere does not move on the two runs where its own people invented writing.
- On a2b637 the states come 600 to 900 years sooner. There writing was invented late, and the gate waited on the spread.
- 4,000 years ago there are about twice as many states and empires on 07c755, and four times as many on 0141d1.
- The present hardly moves: a few percent fewer chiefdoms, and the same states and empires to within ~5%.

## 4. Is the half-way time still Earth's?

Round 1's Earth figures:
- near neighbours took writing within 100 to 900 years of Uruk;
- the Bronze-Age edge took 1,400 to 2,000 years;
- half the urban people had it within ~800 years, which is an inference.

The ~800 is the weak one. If most city-dwellers of 2500 BCE lived in Mesopotamia, Egypt and the Indus, then the half-way point
depends on Egypt (0 to 200 years after Uruk, possibly independent) and the Indus (~700). It could be as early as 200 to 300 years.
So:
- **Every arm's median sits inside the near-neighbour band (100 to 900).**
- **Off (865) and K (850)** match round 1's ~800 inference.
- **C (560)** is the closest of the speed-ups; at 1.76 km a year it gives 630.
- **B (425) and E (273)** sit nearer the Susa and Egypt end.
- **Nine in ten** is already faster in the model than on Earth (round 1). Every speed-up widens that gap. The reason is that on
  Earth the edge peoples were not yet ready (no towns), while in the model nearly every taker is ready before the first invention.
  That is a property of the needs and the histories, not of these arms.

One reading caveat. `techspread` counts a people's whole settled population once the people knows writing. Under E that means
"its court writes", which is what D49's gate needs, but it is not literacy. Earth's figures are about societies with writing too,
so the comparison is like for like.

## 5. Nudge check (±20% on what each arm brings)

For each draw (6 per run, 18 in all), the nudged arm is compared with the same arm unnudged:

| arm, nudge | half (median) | change in half: median, largest | change in the tail people's date: median, largest |
|---|---|---|---|
| B, width x 0.8 | 425 | 0, 100 | 0, 163 |
| B, width x 1.2 | 425 | 0, 0 | 0, 81 |
| E, width x 0.8 | 255 | 0, 200 | 0, 169 |
| E, width x 1.2 | 273 | 0, 100 | 0, 76 |
| E+K, width x 0.8 | 253 | 0, 200 | 0, 169 |
| E+K, width x 1.2 | 255 | 0, 0 | 0, 31 |
| C, 1.76 km/yr | 630 | 0, 200 | 0, 218 |
| C, 2.64 km/yr | 521 | 0, 200 | 32, 174 |
| K, 12 kyr | 850 | 0, 0 | 0, 0 |
| K, 18 kyr | 850 | 0, 0 | 0, 0 |

- **B, E and K hold.** The median draw does not move, and the largest move is one or two time steps.
- **C's speed shifts the median half-way time** from 560 to 630 or 521: about 70 to 100 years per 20%. That is a dial showing
  through.
- **K's kin depth changes nothing** between 12 and 18 kyr: every kin pair in these trees is younger than 12 kyr (hybrids, elf
  daughters, groups).

## 6. Recommendation for D52

Nothing is on by default. The switch stays off, and new runs are unchanged. Changing how fast the tree spreads is Daniel's call, and
no arm both keeps round 1's ~800-year half-way time and is a pure mechanism that works in new runs today.

| option | half-way | for | against |
|---|---|---|---|
| A, keep (off) | 865 | matches the ~800 inference | big peoples can wait 600-1,900 years beside writers, or never |
| **E, elite uptake** (lean) | 273 | the history's answer: courts take writing across land; no new number; holds when nudged; is what D49's state gate needs | half-way near the fast end of Earth's band; needs the ledger before the tree (draft) |
| C, trade contact | 560 | gentlest speed-up; works in new runs today | a speed borrowed from pottery; its number moves the result ~70-100 years per 20% |
| B, town network | 425 | a mechanism; holds when nudged | needs the ledger, as E does; less grounded than E in the sources |
| K, kin share | 850 | real, as a soft bias | does almost nothing here: a people already shares with its groups, and the big peoples have no young kin |

**Lean: E.** It is Daniel's own picture ("the king in the nice city way over there") and the sources back it. Its cost is a
half-way time nearer Susa's 200 to 300 years than round 1's 800. If he wants the half-way time to stay near 800, take C at 2.2, or A.
Either way, E or B needs the tree rebuilt after the ledger in `output.save` (the draft), and then new peoples runs.

## Reproduce

Scratch scripts, deleted at the end of the lane:
- `measure.py RUN ARMS [seed=N] [key=value] [--polities]`: rebuilds the tree in memory with `techtree.rebuild(run, T, arms, seed)`,
  reads `techspread.derive(run, "writing", tt)` and, with `--polities`, writes the tree into a scratch copy of the run's run.json and
  runs `polities.derive(copy, invasions=gods.read_authored(run)["invasions"])`.
- `same.py`: main's `techtree.py` (git show main:) against this lane's, off, the whole doc compared on the three runs.
- 306 sweep jobs, 3 at a time on one thread each: 7 arms and 10 nudges x 6 draws x 3 runs, about 22 s each, plus 21 polities runs
  of about 3 minutes.
