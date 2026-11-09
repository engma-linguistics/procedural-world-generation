# Polities round 14: the tech tree in the history is built; is the switch ready? (PW-1466, PW-1488; lane 234)

## In plain words (design)

- **The ticket is older than the work.** PW-1466 asks for the tech tree to run inside the history, so that the polities there read
  what their own people knew by then, not an era proxy (`PROXY_LEV`) or a calendar lent from another run (`CALENDAR`). That was built
  by lanes 192, 195 and 196 (rounds 8 and 9) and tightened by PW-1483. Both stand-ins are gone from the code (`grep` finds neither).
  This lane did not rebuild it; it checked it on today's code and measured whether the switch can go on.
- **How the gates are read during the history (what is built).** There is one tech tree, `techtree.Calendar`, with one set of rules.
  It is a step function: `advance(ago)` runs its own log-spaced steps down to a given time, and every invention draw is keyed on
  (seed, people, tech, step), so a step run early meets the same luck as one run after the history. `history/tech_live.LiveTech`
  feeds it, at the start of every history step (deep, glacial and recent), only what the history knows by then:
  - **populations so far:** each people's track up to the last stored frame (a line not yet started is not alive in the tree);
  - **contacts so far:** each pair's first contact, and the border it shares at its last stored touch; a front of know-how still on
    its way is re-timed when the border grows, never later (PW-1473);
  - **towns so far:** D52's town arms read the live polities' own central places of town size, counted each century (PW-1472);
  - **tamings so far**, and **the goods each people's land holds now**.
  The live polities ask `LivePolities.knows(people, tech, ago)`, which reads that calendar. At the end of the run `output.save`
  feeds the same calendar the whole run, runs the steps left (none) and writes it out as the run's tech tree, so the history's
  polities and every after-run read-out read one calendar. No rule of the tree is copied into the history.
- **What is left of PW-1466.** Its first box asks that the live calendar agree with the after-run tree within the spread of 12
  draws. Round 9 found 12 of 12 (seed 7) and 7 of 12 (seed 10) for writing, on older code. This round re-checks it on today's code
  (section 2). Its second box (the stand-ins go) is done.
- **What is still missing before the switch is the product.** With the switch on, a run has two polity maps: the live one
  (`polities_live.json`, the polities that fought inside the history and moved its peoples) and the read-out (`polities.derive`,
  which the viewer's Polities layer, the cards, the religion read-out and the nudge checks read). Round 7 (section 3) put off making
  the read-out read the live map until the gates were the run's own. They now are. That step is not built here (it is a read-out
  rewrite, not a gate); it is filed as a draft (section 5).
- **PW-1488 (two attitude walks).** Its natural fix (option A: the religion read-out takes each people's temperament from the
  history's record) belongs with the step above: while the read-out draws its own polities, it has its own wars and rule to step
  attitudes on, so borrowing the history's values would mix two maps. Left with a note on the ticket (section 4).

## 1. Set-up

- World 899985 (L7, time zoom fc5311), copied with its source run into the lane's scratch data root; the dnd tree, one try per run,
  no invasion rows, `polity_live.REVOLT` at its default (off).
- Switch **off** = main at 8dd14a77 (this branch has no code change). Switch **on** = the same code with `POLITIES_LIVE = True`.
- Seeds 7, 10 and 3, each on and off; the PW-1460 nudge (halflings among humans, wish weight 0.8 -> 0.9) on seeds 7 and 10, on and off.
- Measured by `round14/measure.py` (states, largest polity, writing, the nudge pairs) and `round9/check.py` (the calendar spread).

Runs (scratch data root, gone after the lane): seed 7 on 746ed2, off 0a1c30; seed 10 on 097927, off 7de58b; nudge seed 7 on
f5e523, off 19e53f. Seed 3 and the seed 10 nudge were dropped: the machine ran at load 45-220 all night (another session), and
each L7 run took 63-158 min. The lane 77 stress suite (tools/peoples_robust.py, 94 variants per arm) was not run, for the same
reason. Outputs: `round14/measure_out.txt`, `round14/check_746ed2.txt`; runner `round14/live_run.py`.

## 2. PW-1466 box 1 on today's code: the live calendar against the after-run tree

Seed 7 (run 746ed2), the live calendar against 12 draws of the after-run tree over the same history (`round9/check.py`):
writing 12/12 in the spread, law 12/12, cities 11/12, kingship 8/12. Over 9 watched techs x 12 peoples the live date is a median
168 years later than the after-run tree's own draw (mean 193, mean size of the move 219). **Writing passes as round 9 found; the
live tree still runs a little late**, most on kingship. Seed 10 was not checked (budget).

## 3. Switch on against off (main 8dd14a77; same world, tree, seed)

"Live" = the polities inside the history (on runs only); "read-out" = `polities.derive` after the run (both). Largest = the largest
state or empire per century over the last 3,000 years; Taagepera's floor (PW-1456) is 2.3 Mkm².

| run | source | first state | states 2,000 / 1,000 / 0 ya | largest: median, peak, now (Mkm²) | centuries >= 2.3 |
|---|---|---|---|---|---|
| s7 off | read-out | 4,100 ya | 50 / 89 / 122 | 0.46, 2.33, 1.15 | 1/31 |
| s7 on | **live** | **2,600 ya** | 35 / 64 / 85 | **0.18, 0.64, 0.19** | 0/31 |
| s7 on | read-out | 3,800 ya | 37 / 87 / 124 | 0.42, 1.56, 1.39 | 0/31 |
| s10 off | read-out | 4,600 ya | 114 / 145 / 177 | 1.12, 1.58, 1.46 | 0/31 |
| s10 on | **live** | **4,100 ya** | 95 / 97 / 116 | **0.71, 1.66, 0.34** | 0/31 |
| s10 on | read-out | 4,100 ya | 105 / 127 / 164 | 1.13, 1.90, 1.90 | 0/31 |
| nudge s7 off | read-out | 4,100 ya | 63 / 95 / 116 | 1.24, 3.12, 3.12 | 4/31 |
| nudge s7 on | **live** | 3,800 ya | 55 / 70 / 81 | 0.34, 1.83, 0.28 | 0/31 |

- **Peoples' shares today** move under 0.6 points between on and off on every pair (s7 humans 39.6 off, 40.2 on).
- **Writing** (12 largest peoples all write on every run): median 3,936 ya off, 3,796 on (s7); 4,710 off, 5,061 on (s10).
- **The live polities are smaller and fewer than the read-out's**, on the same run: the largest live state is a median 0.18 Mkm²
  (s7) and 0.71 (s10) against the read-out's 0.42 and 1.13, and it never reaches the 2.3 floor. The read-out misses it too
  (PW-1456 is open either way), but the live map misses it by more.

**Steadiness under a nudge (PW-1460's measure; round6.md section 2; halflings among humans 0.8 -> 0.9, seed 7):**

| pair | 1,000 ya: top 10 kept, same ruler | now: top 10 kept, same ruler |
|---|---|---|
| on, live | 5/10, 4/10; 21% | 1/10, 0/10; 14% |
| on, read-out | 6/10, 4/10; 22% | 5/10, 2/10; 16% |
| off, read-out (main) | 6/10, 4/10; 19% | 1/10, 2/10; 20% |
| reference, s7 vs s10 (on, live) | 1/10, 0/10; 6% | 2/10, 2/10; 8% |

Caveat: this nudge moved the peoples far more than round 6's did (humans 39.6 -> 23.5% off, 40.2 -> 23.1% on; round 6 had 39.0
-> 43.1). The nudged tree was loaded from a file path, not by name; whether anything keys on the tree's name was not checked. The
nudge rows are therefore a harder test than round 6's, and on and off saw the same nudge.

## 4. Verdict

**The switch stays off; no flip draft.** The numbers do not clearly support it: the live polities are about half the read-out's
size and further from Taagepera's floor; a nudge keeps the live map's states 1,000 years ago about as well as main's read-out,
but at the present 1/10 and 0/10 against main's 1/10 and 2/10 (no better); and with the switch on the viewer would still show the
read-out's map, not the live one (draft: the read-out should draw the live map). What would make the case: the live map in the
read-out, the largest live polity brought to the read-out's size (PW-1456 applies to both), and a nudge re-check on 2 seeds.

PW-1488 stays as it is (ticket update): its option A needs the read-out to draw the live map first.
