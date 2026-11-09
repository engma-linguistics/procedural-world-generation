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
