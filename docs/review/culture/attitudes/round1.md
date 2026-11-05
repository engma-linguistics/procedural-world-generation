# Attitudes v0 and faith spread, round 1 (lane 199: PW-904 v0, PW-1477)

## In plain words

**Why your faith did not spread.** On run 3e0eb4 you wrote "Test Religionism" for the dwarves, 4,000 years ago, ticked "spreads". Today's
code (main) founds it in "first dwarves of the west of Simath" and it never wins a single neighbour: the read-out says "no neighbour of
another faith at least 0.15 less organised took it up". Two things stopped it. A faith could only convert a neighbour whose own gods were
clearly less organised, and even then only with an e-folding time of **30,000 years** per border. Real faiths spread in centuries. There
was no such thing as a missionary faith, and no ruler ever pushed his faith on his subjects.

**What changed.**
- **Three ways to convert, each with a real time scale.** A culture takes another faith (1) from a **missionary** neighbour in a century or
  two (early Christianity grew about 40% a decade, Stark 1996), (2) from an **ordinary** neighbour with temples over a millennium or two,
  or (3) from its **rulers**: within a generation under a harsh ruler (Charlemagne's Saxons, 32 years; Lithuania, 26 years), over two or
  three centuries under a middling one (Islam in Iran: about 40% Muslim two centuries after the conquest, 80% after three to four;
  Bulliet 1979), hardly at all under a tolerant one (Cyrus returning the gods of Babylon to their temples).
- **Missionary faiths.** Your "spreads" checkbox now has a second one: "missionary" (both on by default, so your dwarf faith is missionary).
  Faiths the world makes itself become missionary with an even chance once their leading god is a moralizing high god.
- **Attitudes.** Every culture has a **tolerance** and an **aggression** (0 to 1). They start from its people's traits in the tree:
  insular peoples are less tolerant, cosmopolitan ones more, martial and herding peoples more aggressive. Each culture then has its own
  lasting offset and wanders over centuries, pushed by its history. Conquest raises aggression. Ruling many peoples makes a ruler a
  little more tolerant. Wide contact raises tolerance and isolation lowers it. So cultures of one people differ, and any era can have its
  Genghis Khan and its Cyrus. A ruler's tolerance sets how hard it pushes its faith.
  You can see both numbers on each culture's card in the Religion tab (taboos view).

**The result.** On the same run, with the same history, your dwarf faith now holds **84 cultures** today. It got there by **22
conversions by its missionaries and 63 under rulers of its faith**; on main it held 1 culture today and had won none. It
reached its 2nd culture in 51 years, its 5th in 145, its 10th in 725 and its 20th in 924. It does **not** sweep the world: today it holds 31% of the
cultures. On run 0141d1 with no faith written in, the largest faith holds 13% of the cultures today, against 11% on main.

**The worry.** On the Seven Meals tree (frozen: measured, not tuned), five faiths turned missionary by themselves. Three of them now hold
87% of the cultures between them (main: 34%), and the largest holds 43% (main: 22%). That looks like Earth's handful of world faiths, but
it is a judgement call how much merging you want, so it is a needs-decision draft. It is not a sweep in centuries: the largest
faith went from 17% to 43% over the last 2,000 years.

## What was there (main, before)

`planet/lineages/gods.py` (PW-1358): a culture in contact with a culture of another faith converts if that neighbour's leading god is at
least 0.45 individuated (temples) and 0.15 more than its own, with chance 1 - exp(-dt / 30 kyr) per frame. At most one hop per frame: the
frames are 0.5 kyr apart near the present and up to 50 kyr apart 300 kyr ago. Polities existed only in their read-out
(`polities.py`); nothing linked them to faiths. No culture had a temperament beyond its people's insularity, which sets cohabitation and
tech openness.

## What is built

### Attitudes v0 (`planet/lineages/attitudes.py`, PW-904 v0)

Two axes only. A third, trade-mindedness, was not added: openness to trade is already the tree's insularity (techtree's openness
`1 - 0.7 insularity`, compose's cohabitation). The traits checked first were nomadic, aggressive, martial (demography contest), insular
and cosmopolitan; they are the seeds:

| | formula (JUDGEMENT) | humans | elves | dwarves | orcs | dragons |
|---|---|---|---|---|---|---|
| tolerance | 0.8 - 0.6 insularity (+0.1 cosmopolitan) | 0.72 | 0.38 | 0.35 | 0.50 | 0.29 |
| aggression | 0.3 (+0.2 aggressive, +0.4 (contest - 1), +0.1 nomadic or pastoral) | 0.30 | 0.30 | 0.50 | 0.40 | 0.30 |

(Insularity and contest from the dnd tree; the run's meta lineages.) The dnd tree has no `aggressive` people, so orcs are only
aggressive through `nomadic`. Making orcs aggressive in D&D's sense would mean a tree edit, which changes the history (`aggressive`
pushes the spread); left for a tree pass.

Each culture: a seeded lasting offset (sd 0.1); a daughter starts from its parent's values. An Ornstein-Uhlenbeck walk about a point
(e-folding 0.5 kyr, spread 0.1), which its history moves. Conquest (its state took land by war) adds +0.15 aggression. Ruling 5 or more
subject cultures adds +0.05 tolerance. Living under a foreign ruler takes 0.05 off aggression. Contact moves tolerance between -0.05 alone
and +0.05 with 6 or more cultures in touch. A missionary faith takes 0.05 off tolerance. All memories fade over 0.5 kyr. Every number is a
JUDGEMENT, labelled in the code.

Spread over cultures (all cultures ever, at their last value): 3e0eb4 tolerance 10/50/90th percentile 0.24 / 0.49 / 0.80, aggression
0.12 / 0.30 / 0.51; Seven Meals 07c755 tolerance 0.35 / 0.53 / 0.70, aggression 0.09 / 0.29 / 0.48 (values from the r6 measure,
before the last rule change, which did not touch attitudes).

It is a read-out like the gods: stepped inside `gods.replay`, written to `gods.json` as `attitudes` (per culture: people, now, track).
The peoples history is untouched.

### Faith spread (`gods.py`, PW-1477)

A culture converts as a whole. Every way it could convert now is a **link** with a hazard rate, and the conversions between two frames
are drawn as events in continuous time (Gillespie: the wait to the next is exponential in the sum of the rates, the links are worked out
again after each). So the rates hold whatever the frame spacing, and a faith can cross several cultures within one 0.5 kyr frame if the
rates say so. The links:

| link | condition | mean wait of one link |
|---|---|---|
| ordinary neighbour | its leading god >= 0.45 (temples) and >= 0.15 above the taker's | TAU_CONVERT 2 kyr (was 30) |
| missionary neighbour | the taker's faith is not missionary; its leading god >= 0.2 (burial) and >= 0.05 above the taker's | TAU_MISSION 0.2 kyr |
| ruler | a state, empire or dragon realm whose ruling culture holds the faith; the subject lives in it | TAU_FORCED^(1-t) x TAU_TOLERANT^t, t = the ruler's tolerance: 30 years at t = 0, 0.25 kyr at 0.5, 2 kyr at 1; x10 slower when the ruler's faith is not missionary |

A neighbour's link is weighted by the share of the taker's border facing it (grid edges to cells it does not hold, the sea included;
a shared cell counts as six edges). It is also weighted by the taker's receptiveness, its tolerance / 0.5: tolerant cultures take new
faiths readily, insular ones resist. A ruler's link is weighted by the share of the subject culture's land the polity holds, and the ruler
does not ask. The polities are read from `polities.derive` (with your scheduled invasions), one century step at a time
(`gods.rule_table`); `derive` runs it when the run has settlements (69 s on 3e0eb4), and the server reuses its cached polities doc.

Two guards, each found by a measure:
- **No ping-pong.** Round r3 on Seven Meals had 1,001 neighbour conversions in 12.5 kyr. Small cultures between two organised faiths
  flipped back and forth. The fix is to remember the church that converted a culture: a later faith must clear the gap over that
  church's leading god, not the convert's own (`held`). The convert's own god keeps its own individuation, so a convert is not at once
  a strong source. In round r5 converts were given the converter's individuation, and Seven Meals' largest faith reached 93% of cultures
  in about 1.5 kyr: a front.
- **Not before its founding.** A faith founded in a frame cannot convert, or be converted from, earlier in that frame's interval
  (round r1 had a written faith converting 199 cultures before its own founding date).

Missionary faiths: one you write is missionary when "spreads" and "missionary" are both ticked (saved files from before have no
`missionary` key: then it is missionary if it spreads). A faith the world makes turns missionary with chance 0.5 (one seeded draw per
faith, independent of every other draw), the first time one of its cultures' leading god reaches 0.7. That is past kingship's ceiling
of 0.6, so it means the moralizing high god.

## Sources (the time scales)

All fetched on 2026-11-04 by a research subagent of this lane; quotes as returned by the fetch.
- **Stark 1996.** Rodney Stark, *The Rise of Christianity: A Sociologist Reconsiders History*, Princeton University Press, 1996. Growth "of
  40 percent per decade": 1,000 Christians in AD 40, 6.3 million (10.5% of the Roman Empire) in 300, 33.9 million (56.5%) in 350. Table
  reproduced at https://www.psephizo.com/life-ministry/how-fast-should-the-church-grow/ (a secondary source; Stark's pages not checked).
  At 40% a decade a population goes from 1% to a majority in about 116 years: that is the per-link scale of TAU_MISSION (0.2 kyr mean
  wait, with a link to a fully receptive culture twice as fast).
- **Fousek et al. 2018.** J. Fousek, V. Kaše, A. Mertel, E. Výtvarová, A. Chalupa, "Spatial constraints on the diffusion of religious
  innovations: The case of early Christianity in the Roman Empire", *PLoS ONE* 13(12): e0208744, 2018,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC6306252/. A "conservative" 34.2% per decade; the spread "closely follows a gravity-guided
  diffusion". It is the reason the neighbour links are weighted by contact (border share).
- **Bulliet 1979.** Richard W. Bulliet, *Conversion to Islam in the Medieval Period: An Essay in Quantitative History*, Harvard University
  Press, 1979. Via https://en.wikipedia.org/wiki/Islamization_of_Iran: Muslims "from approximately 40% in the mid-9th century to nearly
  80% by the end of the 11th century" (Iran conquered in the 640s-650s: about two centuries to 40%, three to four to 80%). Islamic rule
  taxed unbelievers but mostly did not force conversion: the middle of the ruler scale (tolerance ~0.5-0.6: 0.25-0.4 kyr).
- **Forced conversion.** Saxon Wars 772-804, "32 years of campaigns"; the Capitulatio de partibus Saxoniae: a Saxon who "shall have wished
  to remain a pagan, let him be punished by death" (https://en.wikipedia.org/wiki/Saxon_Wars, citing Munro, *Selections from the Laws of
  Charles the Great*). Lithuania: Jogaila's baptism agreed 1385, Christianisation from 1387, "Samogitia was the last ethnic region ... in
  1413" (https://en.wikipedia.org/wiki/Christianization_of_Lithuania): about 26 years. Castile 1502 rescinded tolerance of Islam,
  Aragon 1526 convert-or-leave, expulsions 1609-1614 (https://en.wikipedia.org/wiki/Morisco). These set TAU_FORCED = 0.03 kyr.
- **Tolerant rulers.** The Cyrus Cylinder: "I returned the images of the gods ... to their places"
  (https://en.wikipedia.org/wiki/Cyrus_Cylinder; the page notes Kuhrt and Grabbe doubt an empire-wide policy). Ghazan
  (https://en.wikipedia.org/wiki/Ghazan): "The Mongols were traditionally tolerant of multiple religions"; Ghazan himself converted to
  Islam in 1295, the ruler taking a faith rather than imposing one. Ashoka's Rock Edict 12 (Hultzsch 1925, via
  https://en.wikipedia.org/wiki/Edicts_of_Ashoka): "concord is meritorious". These set the tolerant end (TAU_TOLERANT 2 kyr, JUDGEMENT:
  no number exists for "never") and ETHNIC_RULE (a polytheist ruler restores its subjects' gods rather than replacing them).
- **Buddhism** (https://en.wikipedia.org/wiki/Spread_of_Buddhism): into Han China along the Silk Road "beginning in the 1st or 2nd
  century CE", first documented translation 148 CE, Tibet established in the 8th century. Centuries per region, along trade routes;
  consistent with the missionary scale; not used for a number (the page's dates for wide adoption were not verifiable).
- Not found: any km-per-year rate for a world religion. Whitehouse et al. 2019 (*Nature*, moralizing gods) was retracted (2021) and
  is not used.

## Measures

Method: `gods.inputs` once per run, then `gods.replay` with main's code (`git archive main planet`) and this branch's, the same
inputs, the run's own authored faiths. "Share" = the share of the cultures alive at that time held by the largest faith (top 1) and
the three largest (top 3), over cultures with gods. Runs: dnd 3e0eb4 (world dba204, with Daniel's dwarf faith) and 0141d1 (world
899985, no written faith); Seven Meals 07c755 (world 899985, frozen tree: measured only). Scripts: lane scratch `measure.py`.

### Share of cultures in the largest faiths (baseline: main on the same run)

| run | kyr ago | faiths main | faiths now | top 1 main | top 1 now | top 3 main | top 3 now |
|---|---|---|---|---|---|---|---|
| 0141d1 (dnd, nothing written) | 4 | 94 | 93 | 7.7% | 7.3% | 20.7% | 20.3% |
| | 2 | 92 | 91 | 11.1% | 11.1% | 25.9% | 26.3% |
| | 0 | 89 | 89 | 11.1% | 13.3% | 26.9% | 29.4% |
| 3e0eb4 (dnd, Daniel's dwarf faith) | 4 | 79 | 77 | 9.9% | 10.7% | 24.4% | 24.8% |
| | 2 | 80 | 73 | 11.9% | 14.9% | 26.8% | 31.4% |
| | 0 | 79 | 62 | 13.9% | 31.5% | 28.5% | 48.3% |
| 07c755 (Seven Meals, nothing written) | 4 | 95 | 94 | 12.4% | 13.3% | 22.2% | 21.8% |
| | 2 | 88 | 72 | 20.6% | 16.7% | 31.3% | 35.3% |
| | 0 | 84 | 21 | 22.4% | 43.0% | 34.2% | 87.1% |

Conversions in the 300 kyr window. 0141d1: main 31, all neighbours; now 36 (22 rulers, 14 neighbours). 3e0eb4: main 35; now 122 (90 rulers,
22 missionaries, 10 neighbours). 07c755: main 57; now 373 (155 rulers, 154 missionaries, 64 neighbours), with 5 missionary faiths.

### A written missionary faith (baseline: main on the same run, same faith)

| faith | run | founded | cultures today, main | cultures today, now | how | 2nd / 5th / 10th / 20th culture |
|---|---|---|---|---|---|---|
| Daniel's "Test Religionism" (dwarves) | 3e0eb4 | 4 kyr ago | 1 (0 won) | 84 (85 won) | 22 missionaries, 63 rulers | 51 / 145 / 725 / 924 years |
| test faith "Sun" (humans, missionary), written for this measure | 0141d1 | 3 kyr ago | 4 (1 won) | 35 (32 won) | 23 missionaries, 9 rulers | 274 / 440 / 692 / 2,100 years |
| test faith "Tree" (elves, spreads, not missionary) | 0141d1 | 3 kyr ago | 2 (0 won) | 3 (1 won) | 1 neighbour, after 2.1 kyr | - |

(Test faiths: lane scratch only, never saved into a run. On 3e0eb4 the same human test faith was converted away by the dwarf faith's rulers in its first frame: a written faith can lose its founder.)

### Against the sourced rates

- Missionary: the dwarf faith's 2nd to 5th culture took about 95 years and the 5th to 10th about 580 years. Stark's Christianity
  took about 310 years to go from a sect to a majority of an empire of tens of "cultures". So this is slower than Stark's
  Christianity, as it should be without Roman roads and a unifying state (Fousek's gravity model: contact speeds it).
- Rulers: the measured ruler conversions follow the formula, since the rate is the formula times the land share. The test
  `test_a_harsh_ruler_converts_its_subjects_far_faster_than_a_tolerant_one` checks a whole subject culture under a ruler at
  tolerance 0: median wait under 0.2 kyr (sourced: a generation). Under a tolerant one, more than 0.2 kyr. A ruler whose faith is not
  missionary takes more than twice as long as a harsh missionary one.
- Not explosive: no faith takes more than half the cultures within 2 kyr on any of the runs above. The largest jump is Seven Meals'
  largest faith, 17% to 43% over the last 2 kyr.

### Robustness trees (tools/peoples_robust/trees, world 899985, seed 11, one try each; baseline: main's read-out of the same run)

Two fresh peoples runs (scratch only, deleted after): humans_only (run db9823) and no_dragons (run b6013c). The same two test faiths were
written in, 3 kyr ago, to see a missionary faith on each.

| tree | kyr ago | faiths main | faiths now | top 1 main | top 1 now | top 3 main | top 3 now | test missionary faith today (main / now) |
|---|---|---|---|---|---|---|---|---|
| humans_only | 4 | 28 | 28 | 28.6% | 28.6% | 53.2% | 53.2% | 1 / 1 culture |
| | 0 | 31 | 31 | 23.2% | 23.2% | 50.0% | 50.0% | |
| no_dragons | 4 | 71 | 71 | 10.8% | 10.8% | 25.0% | 25.0% | 6 / 71 cultures |
| | 2 | 76 | 70 | 8.9% | 9.4% | 21.4% | 25.0% | |
| | 0 | 80 | 58 | 9.3% | 34.6% | 22.4% | 48.3% | |

- humans_only: identical to main. No conversions at all, because the humans have no states (round 8 of the polities: they never get
  towns in this draw). Their gods stop at burial's 0.2, so even the missionary test faith has no less organised neighbour to win. A
  missionary faith needs a gap in organisation; on a world where everyone is equally organised it does not spread.
- no_dragons: the missionary test faith takes 71 cultures (35%) in 3 kyr, 47 by missionaries and 24 under rulers. It reaches its 10th
  culture in 132 years, because the humans' first culture holds many small neighbours inside its range (a shared cell faces fully).
  That is fast but stops well short of the world. With no faith written in, the tree has no missionary faith of its own here.

## Changes outside the gods

- `gods.json` changes for every run, written faiths or not. It gains the `attitudes` section, rulers' conversions and the new rates.
  The faiths of runs with no written faith differ from main (0141d1: 91 faiths today on main, 89 now).
  The peoples history is byte-identical (nothing in `history/` was touched), and so are `cultures.json`, `polities` and the briefs' non-religion parts.
- `gods.derive` runs `polities.derive` (69 s on 3e0eb4) when the run has settlements. `output.py` calls it at the end of a peoples
  run, so a peoples run is about a minute longer.
- Server: the gods cache is keyed on the scheduled invasions too (they change who rules, so whose faith is pushed).
- Viewer: the faith form has the "missionary" checkbox; the result column says how a faith spread (missionaries, rulers,
  neighbours); the culture card shows tolerance and aggression.

## Not done (drafts)

- Grudges between named peoples, xenophobia by species, forgiveness, stubbornness: `draft-attitudes-grudges-xenophobia-forgiveness.md`.
- PW-1465 (conqueror harshness) reading tolerance: not wired. The fates are in `history/polity_live.py` (lane 196's file) and
  attitudes are an after-run read-out: `draft-conqueror-harshness-reads-attitudes.md`.
- How much merging into world faiths Daniel wants (the Seven Meals result): `draft-world-faiths-how-much-merging.md` (needs-decision).
