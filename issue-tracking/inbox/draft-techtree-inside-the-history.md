---
title: "Polities in the history need the tech tree in the history: today their gates are an era proxy or a borrowed calendar"
type: task
status: todo
parent: PW-661
milestone: v4
subsystem: peoples
effort: l
impact: high
found_by: lane183
blocked_by: []
relates: [PW-1434, PW-1460]
refs: [planet/lineages/history/polity_live.py, "planet/lineages/techtree.py::build", "planet/lineages/output.py::save", docs/review/culture/polities/round7.md]
---

## Description
**In plain words.** States need their people to know chiefdoms, writing, kingship and law. The tech tree that says who knows what, and
when, is made after the peoples history ends, from the whole run (each people's population series, its contacts summed over the run,
the goods it holds at the present). So the polities that now run inside the history (PW-1434, lane 183, behind a switch) cannot read
it. They use one of two stand-ins:
- an era proxy (`polity_live.PROXY_LEV`): every farming people gets each gate at the same date, once the era's tech level passes a set
  point;
- a calendar lent from an earlier run (`polity_live.CALENDAR`), which the round 7 runs used so that on and off had the same gates.
  This is a test harness, not a product.

**What breaks if never done.** The live polities cannot become the polities. The era proxy cannot make the differences between peoples
that v0 shows (round 6: the 1-in-12 draw in which the humans never write, so their states never form). A lent calendar needs a second
run. v4's done-when 1 ("states grow, fight and fall" on Seven Meals, the antelope-kin's conquests) would be shown on gates that are not
the run's own.

**Try.** Make `techtree.build` a step function the history calls each century of the recent pass. Its keyed draws (PW-1459) already
make each invention test a function of (seed, people, tech, step). What must change is what it reads: the populations so far (not the
saved whole series), the contacts so far (not intervals with a median border over the whole run), and the goods held by then (not at
the present). Then `polity_live.knows` reads the live calendar, and the after-run tech tree is the same calendar written out.
- [ ] the tech tree runs inside the history; with polities off, the calendar matches today's within the 12-seed spread (round 6)
- [ ] polity_live reads it; CALENDAR and PROXY_LEV go
