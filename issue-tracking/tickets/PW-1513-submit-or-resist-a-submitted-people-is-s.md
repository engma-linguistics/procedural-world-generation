---
id: PW-1513
title: "Submit or resist: a submitted people is spared for good; should revolt (Herat) or a broken promise (Merv) bring the harsh fate back?"
type: task
status: needs-decision
parent: PW-661
milestone: v4
subsystem: peoples
effort: s
impact: med
found_by: lane208
blocked_by: []
relates: [PW-1496, PW-1487, PW-1481]
refs: ["planet/lineages/history/polity_live.py::LivePolities._fates", "planet/lineages/history/polity_live.py::LivePolities._refuge", "planet/lineages/attitudes.py::Attitudes", docs/review/culture/polities/round12.md, docs/review/culture/polities/round12/measure.py, docs/review/culture/polities/round12/live_run.py, docs/review/culture/polities/round11.md, "world 899985"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
**In plain words.** Since lane 208 (your D61 addition), a people that a conqueror would thin, drive out or raze first chooses:
- **It submits** if it is less warlike than the winner, and is then kept.
- **It resists** if it is at least as warlike, and meets the harsh fate.

Submission is now the common case: 59-69% of the peoples a winner would have treated harshly submitted, on seeds 7, 10 and 3 against
main (round12.md section 2). The reason is that most peoples are plain (aggression about 0.3) and conquerors tend to be warlike. So
razing became rare. On seed 10 the martial winners' expulsions fell from 48 (main) to 17 razings.

In the record, submission was not always the end of it:
- **Herat** was spared at its first surrender, then rebelled and was massacred in 1222.
- **Merv** surrendered on a promise that Tolui broke.

In the model, a submitted people is kept once and never revisited.

**What misleads if never decided:** a v4 history where nearly every conquest is a peaceful change of masters. The "Genghis Khan"
pole of D54 then shows up only against warlike peoples. A reader would take the conqueror's terror to be milder than D59 C meant.

**Options.**
- **A. Keep as built.** Submission is final. Simple, and the counts in round12.md stand.
- **B. Revolt.** A submitted people that later raises a faction against the same ruler (the brakes already split factions off) meets
  the harsh fate it escaped, at the winner's attitudes then. No new number: the existing faction split is the trigger. Herat.
- **C. Terms kept by tolerance.** An intolerant winner (tolerance under 0.5, the scale's middle) breaks its terms: a submitting people
  meets the fate anyway, but the cut is halved for "no resistance". This needs a new number (the half), so it is weaker.

**Lean: B.** It uses a mechanism already in the model, keeps submission as the first answer, and gives razings a cause the reader can
follow ("they rose against the khan"). Effort is small: a lookup of the submitted peoples per ruler, read when a faction splits off.
- [ ] Daniel picks; then measure on seeds 7, 10, 3 (round12/measure.py) against the round 12 runs.

## Updates
- 2026-11-08: Desk D67 updated with lane 215's measured B (REVOLT switch, off): 4/6, 7/13, 9/21 submitted pairs later rose; heads lost 0.10->0.11, 0.58->2.14, 0.94->1.00 M (seeds 7/10/3).
- 2026-11-08: Lane 215: option B built as a switch, polity_live.REVOLT, default OFF (docs/review/culture/polities/round13.md). No faction-split event exists in the history, so a rising is read from the polities: a submitted people seats its own polity on a cell its ruler held last century while that ruler still stands; the same ruler's next taking finds it unable to submit (fate at the winner's attitudes then); no new number. Seeds 7/10/3, switch off (= main 96dd22aa) -> on: submitted pairs that later rose 4 of 6 / 7 of 13 / 9 of 21; retaken 3 / 14 / 9; heads lost 0.10 -> 0.11 M, 0.58 -> 2.14 M, 0.94 -> 1.00 M; razed 0 -> 0, 17 -> 21, 0 -> 0; heads moved 0 -> 0, 0.014 -> 0.041 M, 8.27 -> 8.27 M. Seed 10's orcs razed risen humans (1.12 M in one retaking); seed 3's tolerant humans kept 5 of 9 risers. Present population unchanged. Flip REVOLT to True if Daniel picks B.
- 2026-11-08: Desk D67 (lean B: revolt brings the harsh fate back; no new number).
- 2026-11-08: Created from inbox draft draft-submission-revocable.md (found by lane208).
