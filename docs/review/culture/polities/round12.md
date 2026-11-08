# Polities round 12: where the expelled go, and submit or resist (PW-1496, D61 C; lane 208)

**Baseline:** main at e6cb463c on the same world (899985, L7), the dnd tree, tree seeds 7, 10 and 3, round 10's six strong invasion
rows, and polities in the history switched on. The script is `round12/live_run.py`, round 11's with a new run tag. Each pair below is
the same seed on main and on the branch.

## In plain words

- **What changed.** When a conqueror would thin, drive out or destroy a people on the land it took, the history now does this:
  - **It first asks whether that people submits.** (Daniel's 11-07 addition to D61, Genghis Khan's terms: "submit and you are
    spared, resist and you are destroyed".)
    - A people less warlike than the winner yields. It keeps its land and heads.
    - A people at least as warlike resists, and meets the harsh fate.
  - **If it resists and is driven out, the winner's own aggression decides what happens to it** (D61 C):
    - A martial winner (aggression 0.5 or more, the model's own value for a martial people) **razes**: that share is lost.
    - A less martial winner **drives them out**. The share moves to the same people's nearest land the winner does not rule,
      spread by how densely the people already lives there. It is lost only if the people has no such land.
  - "Thinned" is unchanged: war deaths, a loss.
- **What came of it.** Heads lost to conquest over the last 2,000 years, main → branch:
  - seed 7: 0.15 M → 0.10 M
  - seed 10: 5.2 M → 0.58 M
  - seed 3: 20.0 M → 0.94 M
- **Most of the drop is submission.**
  - On the branch, 9, 52 and 60 peoples per seed (seeds 7, 10, 3) submitted that main had thinned or expelled.
  - Among peoples a winner would have treated harshly, 69%, 68% and 59% submitted on the branch (seeds 7, 10, 3).
- **Moving is the rest.**
  - On seed 3, 23 peoples were driven out by plain, intolerant winners.
  - 8.3 M heads moved to their own people's other land. Only 66 thousand were lost, where the expelled had nowhere to go.
- **Razing still happens.** On seed 10, 17 peoples who resisted martial winners (the orcs and leonins of round 11) were razed: 0.40 M
  heads.
- **The present population barely moves:** 856.0 / 856.0 M (seed 7), 930.7 / 928.0 M (seed 10) and 1,007.8 / 1,013.6 M (seed 3),
  main / branch. The peoples' shares move by 0.3 points at most.
- **With the switch off, the output is byte-identical to main** (seed 7: every layer and every JSON value; only timings, ids, names
  and the code hash differ).
- **Caveat: submission is now the common case.** Under a martial winner, most peoples are plain (aggression about 0.3) and so
  submit. That makes razing rarer than round 11's D59 C made it: the martial winners' expulsions on seed 10 fell from 48 to 17.
  Real submission was not always honoured, and the Mongols destroyed cities that submitted and later revolted. An inbox draft
  takes this up (section 4).

## 1. The rule

`polity_live.LivePolities._fates` and `_refuge`.

1. The winner's harshness to each people on the taken land reads kept, thinned or expelled, as in round 11 (FATE_AT, TOL_X,
   AGG_HARSH).
2. **Submit or resist (new).** If the fate is not "kept", the people submits when its own aggression (`attitudes.Attitudes`, stepped
   each century) is below the winner's. It is then kept and recorded as "submitted".
   - Otherwise it resists and meets the fate.
   - There is no new number: the two peoples' own attitudes decide.
3. **The martial mark (D61 C).** If a resister is expelled by a winner of aggression AGG_MID (0.5) or more, the fate is "razed".
   - AGG_MID is the aggression `attitudes` gives a martial people: AGG_BASE 0.3 + AGG_CONTEST 0.4 × (contest 1.5 − 1). FATE_CUT
     already scales by it.
   - Round 11's `measure.py` buckets "martial" from 0.45 for display only. The rule uses 0.5.
4. **The cut** is the existing one (FATE_CUT × aggression / AGG_MID, FATE_MAX per people per step).
   - Thinned and razed: lost, as before.
   - Expelled: the heads that left the taken cells move, including those on cells that fell below EST. `_refuge` handles the move:
     - It searches outward from the taken cells, ring by ring, to the people's first cells off the taken land and off the winner's
       land (the winner's land after the step's wars).
     - It takes the connected patch, or patches, it reaches there.
     - It scales the people's presence on that patch up evenly, by its existing density, never above full presence (1).
     - What does not fit, or what has nowhere to go, is lost.
   - Only lost heads count toward FATE_MAX.
5. A fate is recorded as `[fate, heads lost, heads moved]`.

## 2. Fates and heads, by seed (history, switch on; main e6cb463c / branch)

`round12/measure.py`. "Harsh" means thinned, expelled or razed. On the branch, submitted peoples are ones the winner would have
treated harshly.

| seed | run | kept | submitted | thinned | expelled (moved) | razed | heads lost | heads moved |
|---|---|---|---|---|---|---|---|---|
| 7 | main cd0cd8 | 184 | - | 12 | 0 | - | 151,592 | - |
| 7 | branch ad6dfd | 184 | 9 | 4 | 0 | 0 | 104,673 | 0 |
| 10 | main 9573c1 | 172 | - | 25 | 53 | - | 5,199,993 | - |
| 10 | branch 3888f9 | 175 | 52 | 7 | 1 | 17 | 578,717 | 13,905 |
| 3 | main d5685f | 352 | - | 58 | 72 | - | 19,980,411 | - |
| 3 | branch 8100b3 | 365 | 60 | 18 | 23 | 0 | 941,806 | 8,267,399 |

- **Heads lost by fate, branch.**
  - seed 7: thinned 0.10 M.
  - seed 10: thinned 0.18 M, razed 0.40 M.
  - seed 3: thinned 0.88 M, expelled with nowhere to go 0.07 M.
- **Heads lost by fate, main.**
  - seed 10: thinned 1.77 M, expelled 3.43 M.
  - seed 3: thinned 4.89 M, expelled 15.09 M.
- **What C alone would have done to main's expulsions** (split at the martial mark by the winner's aggression at the conquest):
  - seed 10: 48 by martial winners (3.36 M, razed), 5 by plain ones (0.07 M, moved).
  - seed 3: 7 martial (1.89 M, razed), 65 plain (13.2 M, moved).
  - So C without submission would have kept seed 10 a razing seed and turned seed 3 into a refugee seed.
- **Who razes on the branch.** All 17 razings are on seed 10, by intolerant martial winners (round 11's orcs and leonins) against
  peoples at least as warlike.
- **Conquests** are about the same:
  - seed 7: 94 wars and 23 invasions on both.
  - seed 10: 207/208 wars, 41/41 invasions.
  - seed 3: 251/250 wars, 30/25 invasions.
  - Fewer heads lost changes later strengths a little, so the runs drift apart.

## 3. Population, shares, states (main / branch)

| seed | present population | top shares % | states at 0 kyr ago | largest at 0 kyr ago |
|---|---|---|---|---|
| 7 | 856.0 / 856.0 M | human 41.1/41.1, hobgoblin 13.4/13.4, halfling 9.0/9.0, orc 8.7/8.7 | 84 / 84 | 1.009 / 1.009 Mkm² orc |
| 10 | 930.7 / 928.0 M | human 62.6/62.8, halfling 12.3/12.3, hobgoblin 5.5/5.2, elf 4.7/4.7, orc 2.7/2.8 | 115 / 118 | 0.342 / 0.342 hobgoblin |
| 3 | 1,007.8 / 1,013.6 M | human 60.6/60.9, hobgoblin 8.8/8.7, orc 6.6/6.6, elf 4.4/4.4 | 118 / 116 | 1.308 dwarf / 0.921 hobgoblin |

- The first writing, kingship, law and cities are unchanged on every seed.
- **Rows that took land:**
  - seed 7: orc_human and human_kenku, the same on both.
  - seed 10: four rows on both. orc_human took 0.47 Mkm² on the branch, against 0.24 on main.
  - seed 3: orc_human took 1.08 against 0.77 Mkm²; dwarf_hob took 0.63 against 0.95 Mkm².

**Reading.**
- On main, the expelled vanished. 15 M heads on seed 3 is about 1.5% of the present population, all gone.
- On the branch, they mostly either never left (submitted) or became refugees on their own people's land.
- The world's totals hardly change, because the history regrows the losses within centuries.
- What changes is the record: who was razed, who fled, who yielded. That is what the v4 card will show.

## 4. Sources for submit or resist, and what it leaves out

- **Terms.** Envoys carried terms that amounted to "submit or die", with "no third course of action". "Those who did resist would be
  destroyed"; "the more determined the resistance, the greater the level of destruction" (Timothy May, *The Mongols*, chapter on
  policies:
  [Cambridge abstract](https://www.cambridge.org/core/books/abs/mongols/policies/3B748706C27DD1F207482C79E0F17784)).
- **Practice.** "Genghis Khan and his generals preferred to offer their enemies a chance to surrender without resistance." Those who
  submitted became tributary vassals, and "populations resisting were usually annihilated"
  ([Destruction under the Mongol Empire](https://en.wikipedia.org/wiki/Destruction_under_the_Mongol_Empire)).
- **Submitted:**
  - The Uyghur Idiqut sent an embassy, and Uyghuria joined as the fifth ulus in 1211
    ([Barchuq Art Tegin](https://en.wikipedia.org/wiki/Barchuq_Art_Tegin)).
  - Galicia and Volhynia submitted to Batu's suzerainty and paid tribute
    ([Siege of Kiev](https://en.wikipedia.org/wiki/Siege_of_Kiev_(1240))).
- **Resisted:**
  - Kiev killed the envoys, and most of its population was massacred.
  - Baghdad refused Hülegü's demand to "peacefully submit" in 1258
    ([Siege of Baghdad](https://en.wikipedia.org/wiki/Siege_of_Baghdad_(1258))).
  - Gurganj was taken "fighting block for block".
  - Nishapur was razed after the khan's son-in-law was killed there
    ([Mongol invasion of Khwarazmia](https://en.wikipedia.org/wiki/Mongol_invasion_of_Khwarazmia)).
- **Not always honoured** (same page):
  - Merv surrendered on a promise that Tolui broke.
  - Herat was spared at its first surrender, then rebelled and was massacred in 1222.
- **What the model leaves out:**
  - A submitted people is kept once. It cannot later revolt and be punished.
  - A winner never breaks its terms.
  - The draft `draft-submission-revocable.md` asks whether that matters.
- **Choice of mechanism.** The rule is "less warlike than the winner yields". The alternatives (the brief's list) were rejected:
  - Relative strength: the loser has already lost the war, so it says nothing more.
  - Distance to the winner's core: no source ties it to surrender.
  - The victim's aggression against the winner's is the one input both sides already carry.

## 5. Checks

- **Switch off.** Seed 7 on main (ef0265) and on the branch code before the arm S change (899e29) give the same bytes:
  - every layer, settlements.json, cultures.json and demes.json;
  - run.json, gods.json and taboos.json, apart from generated_in_s, created, name, id, tree_file and planet_src_sha.
  - Note: lane 208's second change, arm S's chiefdom uptake (techtree round 4), does change switch-off output, through the tech
    calendar. That is that change's own effect, measured in `../techtree/round4.md`. The task 1 runs used the polity code without
    it.
- **Tests.** In `tests/test_lineages.py`, a new test covers moved, razed, nowhere-to-go, thinned and submitted. Two fate tests now
  read "razed" for a martial winner and set the kobolds' aggression to resist. The not-slow and area suites are listed in the
  lane's report.
- **Bug found while running.** A taken cell without the people's presence gave a NaN in the moved share. Fixed in 07b35329; seed 3 on
  the branch was re-run with the fix.

## Files

- `round12/live_run.py`: the runs.
- `round12/measure.py`: the tables in sections 2 and 3.
- The runs were in a scratch data root and are gone after the lane: main cd0cd8, 9573c1, d5685f; branch ad6dfd, 3888f9, 8100b3;
  switch off ef0265 (main) and 899e29 (branch).
