---
id: PW-1066
title: "Dragon intake: the 2.7 t a year is an all-ages mean on a reptile fit stretched 60-1,100x past its data; it behaves as a mesotherm's, and the page and code should say which law and why"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: s
impact: med
found_by: dragon-density-r2
blocked_by: []
relates: [PW-958, PW-977, PW-1019]
refs: [planet/lineages/dragon_ages.py, planet/lineages/history/megafauna.py, docs/review/megafauna/dragon-density/sensitivity.py]
created: 2026-10-30
updated: 2026-10-30
---

## Description
**In plain words.** How much a dragon eats sets how many dragons the land can feed, more than almost anything else. The model takes the
formula for how much energy reptiles burn, which was measured on animals up to 45 kg, and stretches it to dragons of up to 52 tonnes.
The yearly 2.7 tonnes of prey is the average over dragons of every age (a young dragon eats little), not what a 1.65-tonne dragon eats
(about 4 tonnes). Because the reptile formula rises faster with size than the mammal one, the model's big dragons end up eating like
something between a lizard and a mammal, which is roughly what papers on dinosaurs suggest. That is a defensible choice, but it is an
accident of the formula, not a decision anyone made.

Evidence:
- Nagy, Girard & Brown 1999, Table 2 (p. 261): all reptiles 0.196 M^0.889 kJ/day (M g), n = 55; largest reptile the 45.2 kg Komodo
  dragon (Table 1, p. 258). Outside the fitted masses "95% CI will be larger" (p. 262). Lizard (eq. 33) and Varanidae (eq. 36) fits give
  1.5x the food; Nagy et al. recommend "the equation that applies most specifically" (p. 262).
- Nagy 2005 (J Exp Biol 208:1621): a species' true rate can be "as low as 30% of predicted or as high as 170%" (p. 1622); the food
  equations leave out growth ("this additional food is not accounted for", p. 1624), and the model's dragons grow all their lives;
  reptile data cover the season "when these animals were abroad and active" (p. 1622), the model eats x 365.
- McNab 2009 (PNAS 106:12184): varanids at a flat 22% of mammals, 1.07 M^0.735 (p. 12185); dinosaurs at "31% of mammals" (p. 12187).
  The model's law gives 37% of a mammal at 1.65 t and 64% at 52 t, so in effect a mesotherm's.
- Marshall et al. 2021 (Science 372:284) assume "a physiology midway between that of mammalian carnivores and that of large varanid
  lizards" (p. 284).
- Survivorship-averaged over the same ages (sensitivity.py): McNab varanid x1.9 dragons; McNab 31%-of-mammal mesotherm x1.39; Nagy
  lizards x0.68, Varanidae x0.63; Nagy mammal x0.43; Nagy birds (the only on-file rate that includes flying animals) x0.43.

Direction and size on dragons: the law alone moves density between x0.43 and x1.9; adding growth and a year-round active rate lowers it.

Options:
- **A.** Keep the all-reptile fit; document it as the mesotherm-in-effect choice, with the all-ages mean labelled as such (no change to numbers).
- **B.** Adopt McNab's 31%-of-mammal mesotherm line explicitly (x1.39 dragons), matching Marshall's "midway" physiology.
- **C.** A flight term on top (the bird line as an upper bound), if dragons are meant to fly far daily.

Lean: A or B for the owner; the docstring in megafauna.py ("~0.55 of a mammal's at dragon size") should read 0.37 at 1.65 t.
- [ ] owner picks A/B/C
- [ ] fix the megafauna.py docstring ratio and dragon_ages.py's "Table 2, p. 260" (the reptile row is eq. 32 on p. 261)

## Updates
- 2026-10-30: Created from inbox draft draft-dragon-intake-law-and-label.md (found by dragon-density-r2).
