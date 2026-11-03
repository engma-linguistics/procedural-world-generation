---
id: PW-990
title: "The dragon food cap (PW-977 stage 1) never binds at the default densities: what limits dragons is the pressed 1 per 5,000 km2 and the natural prey density, not food"
type: task
status: todo
parent: null
milestone: v2
subsystem: peoples
effort: s
impact: med
found_by: fun-lane-43
blocked_by: []
relates: [PW-977, PW-957, PW-973]
refs: [planet/lineages/history/megafauna.py, docs/review/megafauna/probe.py, docs/review/megafauna/age-of-dragons.html]
created: 2026-10-29
updated: 2026-10-29
---

## Description
**In plain words.** Stage 1 asks: does each place grow enough food for the dragons we put there? At default settings the answer is always yes, by about 10x, so the food check never changes anything.

Today the dragon count is set by two other rules:
1. A natural density from body size: big predators are rare, by a formula fitted to real carnivores.
2. Where peoples are strong, a fixed 1 dragon per 5,000 km2.

Both give far fewer dragons than the food could feed.

The question for the owner: should dragon numbers come *from* food, or from the body-size rule with food only as a ceiling?
- **A.** Keep the body-size rule and the 1 per 5,000; food stays a ceiling. It only bites on barren worlds or if dragons are set denser.
- **B.** Let food decide: dragons get what is left after peoples and other predators eat, and the body-size rule becomes a sanity check.
  - Catch: if dragons got all the leftovers, rich land would hold ~10x today's dragons. B only makes sense once the peoples' and other predators' share (stage 2) is in.
  - Real predator guilds take a small share: Farlow 1993 gives prey:predator ratios of 100-200:1.
- **C.** Tighten the food rules until the check bites. Not recommended; it's tuning without a reason.

Fun lane 43 built stage 1: per cell, all dragon kinds together are held to the food there (10%/yr of the wild herds plus 10%/yr of the herders' stock, both unverified), each dragon needing the younger schedule's 5.4 cattle (2.7 t) a year. On the 6 worlds x rolls 7000-7001 (and 7002-7003 for the default arm) it changes no count: present dragons per run are identical with the cap on and off on 4 of 4 checked runs, and the worst cell's need is 16% of its supply, the worst pocket's 8-16%. It bites only in cells whose food is exactly zero (barren desert, a few dozen cells), where the uncapped run had a handful of expected dragons.

Why: at 1 t/km2 of prey the food supports ~1 dragon per 27 km2 at 1 t/km2 of prey (2.7 t / 0.1 t/km2/yr), whereas the natural density (Carbone and Gittleman, ~1 per 270 km2 at 1 t/km2 at the younger eco mass) is ~10x below that and the pressed 1 per 5,000 km2 far below. The old section 5 ">100%" came from comparing an ancient's whole yearly kill with the stock in its range as if it ate only stock; with wild prey and stock eaten in proportion to what each supplies, the worst share of a pocket's stock taken is under 1%/yr.

Options:
- **A.** Leave stage 1 as a safeguard (it will bind in a hungrier setting: meta.dragon_km2 small, or the poor-prey worlds) and go on to stage 2 (peoples' and other predators' share), where the food will start to bind.
- **B.** Derive the natural density from the food too (dragons' share of the surplus / food per dragon) instead of Carbone, so food is the mechanism, not a check; Carbone then becomes a cross-check.
- **C.** Raise OFFTAKE-style shares, or lower the herders' tolerated loss, until the cap is a real limit (a tuning against nothing; not recommended).

Lean: A now, B with stage 2 (the budget is only a budget once hunters and herders draw on it too).

## Updates
- 2026-10-29: Merged B (fun lane 45b). Stays open for stage 3: persecution as a kill rate against slow breeding, softer pressure, a viewer control for dragon abundance.
- 2026-10-29: RULING (owner, 10-29): option B. Food decides how many dragons the land holds; persecution (stage 3) decides how many survive near peoples; the 1 per 5,000 km2 goes once that is literature-driven. No external target for dragon numbers.
- 2026-10-29: Option B built as the default (meta.megafauna_natural = "food"; "prey" = Carbone kept as a cross-check): the guild, dragons included, splits what the peoples and giants leave by Carbone, Turvey & Bielby 2011's size classes (dragons 17%), natural density = that / 2.7 t a year. At 1 t/km2 of prey: 1 per 159 km2 (Carbone 1 per 269; Jetz 2004 carnivore N^-1 at 1.65 t: 1 per 202; Farlow 1993 reptiles 66.07 M^-1.01: 1 per 27). Rich (7 t/km2) 1 per 23, poor (0.6) 1 per 265. Present dragons 62.6k per run vs 42.3k (main). Prey:dragon biomass ~96:1 in wild country (Farlow p. 176: 100:1-200:1 modern, 50:1 his best case).
- 2026-10-29: Owner 10-29: drop the Forgotten Realms target. Tune dragons to what the world can support, with pressure much softer: peoples have a real effect, growing with technology, but never species-ending. Rebuild the age-of-dragons review once the food and biomass work lands, for the owner to read.
- 2026-10-29: Owner 10-29: 'any settled people pushes it all the way' means pressure is tuned too high; a food-driven B with many more dragons may still be fine. Make dragon abundance easy for users to tune in the viewer, from 'How to Train Your Dragon, they're everywhere' to 'one left somewhere'. The owner's own target is roughly the dragon numbers by age class of the Forgotten Realms setting; it isn't the only option. Need a source for FR dragon counts (sourcebooks; not from memory).
- 2026-10-29: Status needs-decision -> todo. Owner 10-29: option B. Food sets how many dragons the land can hold (dragons' share of the surplus after peoples and other predators); peoples' persecution (societal pressure, like humans with wolves or tigers, not competition) sets how many survive near them. 1 per 5,000 km2 was a placeholder 'pulled out of thin air' and should retire. Coordinator plan: stage 3 replaces the fixed pressed endpoint with a persecution kill rate against the dragons' slow breeding (equilibrium = natural x (1 - kill/r_max)), the rate rising with people's density and means (weapons, organisation, PW-961). Tension to resolve: PRESS_N0 today lets a thin forager band press dragons ~2/3 of the way, while the PW-977 proposal said foragers can't kill dragons.
- 2026-10-29: 2026-10-29: plain-language summary added at the top; to discuss with the owner.
- 2026-10-29: Papers read 10-29 bearing on option B (density from food): Farlow 1993 (pp. 171-174) builds predator density exactly that way, predator density x mass x intake = prey density x mass x turnover (eqs. 1-5), with intake 48.87 M^-0.30 kg/kg/yr for endotherms (eq. 7, p. 172) and 3.81 M^-0.16 for reptiles (eq. 8, p. 187). His reptile density fit, 66.07 M^-1.01 per km2 (M kg, p. 187), gives ~1 per 50 km2 at 3.2 t, close to Marshall's mesotherm line (~1 per 65, all ages). Jetz et al. 2004 (Table 1, p. 268) puts a 3.2 t mammal carnivore's home range at ~8,400 km2 (~52 km radius), near FORAGE_KM = 60. Nothing here favours A over B; it shows B has a standard form.
- 2026-10-29: Created from inbox draft draft-dragon-food-cap-does-not-bind.md (found by fun-lane-43).
